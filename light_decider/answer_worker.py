from __future__ import annotations

import json
import os
import threading
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit, urlunsplit
from typing import Any


SYSTEM_PROMPT = "直接回答用户的问题，不提路由、不解释自己是执行层。"
DEFAULT_BASE_URL = "http://localhost:11434/v1"
DEFAULT_MODEL = "qwen2.5:7b-instruct"
DEFAULT_TIMEOUT_SECONDS = 120
DEFAULT_NUM_CTX = 4096
DEFAULT_KEEP_ALIVE = "60s"
_SERIAL_REQUEST_LOCK = threading.Lock()


class AnswerWorkerFailure(RuntimeError):
    def __init__(self, message: str, *, model: str, attempts: int, elapsed_seconds: float) -> None:
        super().__init__(message)
        self.model = model
        self.attempts = attempts
        self.elapsed_seconds = elapsed_seconds


class AnswerWorker:
    """Serial local answer worker using Ollama's native chat endpoint."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        model: str | None = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.base_url = (base_url or os.environ.get("LIGHT_DECIDER_ANSWER_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.model = model or os.environ.get("LIGHT_DECIDER_ANSWER_MODEL") or DEFAULT_MODEL
        self.timeout_seconds = timeout_seconds

    @property
    def native_chat_url(self) -> str:
        parts = urlsplit(self.base_url)
        path = parts.path.rstrip("/")
        if path.endswith("/v1"):
            path = path[:-3]
        elif path.endswith("/v1/chat/completions"):
            path = path[: -len("/v1/chat/completions")]
        return urlunsplit((parts.scheme, parts.netloc, f"{path}/api/chat", "", ""))

    def _request_once(self, request_text: str) -> tuple[str, dict[str, int | None] | None]:
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request_text},
            ],
            "stream": False,
            "options": {"temperature": 0.2, "num_ctx": DEFAULT_NUM_CTX},
            "keep_alive": DEFAULT_KEEP_ALIVE,
        }
        request = urllib.request.Request(
            self.native_chat_url,
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace").strip()
            raise RuntimeError(f"HTTP {error.code}: {detail or error.reason}") from error
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            raise RuntimeError(f"{type(error).__name__}: {error}") from error
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise RuntimeError(f"响应不是有效 JSON：{error}") from error

        try:
            content = payload["message"]["content"]
        except (KeyError, TypeError) as error:
            raise RuntimeError("响应缺少 message.content。") from error
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("模型返回了空回答。")

        prompt_tokens = _optional_int(payload.get("prompt_eval_count"))
        completion_tokens = _optional_int(payload.get("eval_count"))
        usage = None
        if prompt_tokens is not None or completion_tokens is not None:
            usage = {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
                if prompt_tokens is not None and completion_tokens is not None
                else None,
            }
        return content.strip(), usage

    def answer(self, request_text: str) -> dict[str, Any]:
        started = time.perf_counter()
        errors: list[str] = []
        with _SERIAL_REQUEST_LOCK:
            for attempt in range(1, 3):
                try:
                    text, usage = self._request_once(request_text)
                    return {
                        "model": self.model,
                        "elapsed_seconds": round(time.perf_counter() - started, 3),
                        "text": text,
                        "usage": usage,
                        "attempts": attempt,
                    }
                except Exception as error:
                    errors.append(f"第 {attempt} 次：{error}")
        elapsed = round(time.perf_counter() - started, 3)
        raise AnswerWorkerFailure(
            "Answer Worker 调用失败，已达到最多两次尝试；" + "；".join(errors),
            model=self.model,
            attempts=2,
            elapsed_seconds=elapsed,
        )


def _optional_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None
