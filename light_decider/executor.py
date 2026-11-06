from __future__ import annotations

import json
import hashlib
import os
import shutil
import subprocess
import tempfile
import time
import uuid
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from .answer_worker import AnswerWorker, AnswerWorkerFailure
from .question import build_question_package


RouteFunction = Callable[[str, list[dict[str, str]] | None], dict[str, Any]]
InputFunction = Callable[[str], str]
OutputFunction = Callable[[str], None]


class JsonlThreadStore:
    """Persist one current snapshot per thread_id in a JSONL file."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def upsert(self, thread: Mapping[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        thread_id = str(thread["thread_id"])
        records: list[dict[str, Any]] = []
        replaced = False
        if self.path.exists():
            for line_number, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), start=1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as error:
                    raise ValueError(f"Invalid thread JSONL at line {line_number}: {error}") from error
                if not isinstance(record, dict):
                    raise ValueError(f"Thread JSONL line {line_number} must contain an object.")
                if str(record.get("thread_id")) == thread_id:
                    if not replaced:
                        records.append(dict(thread))
                        replaced = True
                else:
                    records.append(record)
        if not replaced:
            records.append(dict(thread))

        payload = "".join(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n" for record in records)
        handle, temporary_name = tempfile.mkstemp(prefix=f".{self.path.name}.", suffix=".tmp", dir=self.path.parent)
        try:
            with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary_name, self.path)
        except Exception:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
            raise


def _route_snapshot(route_result: Mapping[str, Any], request_text: str, stage: str) -> dict[str, Any]:
    return {
        "stage": stage,
        "request_text": request_text,
        "action": route_result.get("action"),
        "reason": route_result.get("reason"),
        "policy_override": route_result.get("policy_override"),
        "suggested_route": route_result.get("suggested_route"),
        "scores": route_result.get("scores"),
        "high_risk_domains": route_result.get("high_risk_domains", []),
    }


def _dry_run_package(
    action: str,
    request_text: str,
    context: list[dict[str, str]],
    route_result: Mapping[str, Any],
    thread_id: str,
) -> dict[str, Any]:
    if action.startswith("codex"):
        package_type = "codex_handoff"
        payload: Any = route_result.get("codex_handoff") or {
            "request_text": request_text,
            "context": context,
            "action": action,
        }
    elif action == "decide":
        package_type = "assistant_response_request"
        payload = {"request_text": request_text, "context": context}
    else:
        package_type = "unrouted"
        payload = {"request_text": request_text, "context": context}
    return {
        "type": package_type,
        "thread_id": thread_id,
        "action": action,
        "payload": payload,
        "dry_run": True,
        "automatic_dispatch_allowed": False,
    }


def _is_abort(answer: str) -> bool:
    normalized = answer.strip().casefold()
    return not normalized or normalized in {"quit", "/quit"}


def _run_answer_worker(
    thread: dict[str, Any],
    request_text: str,
    answer_worker: AnswerWorker,
    thread_store: JsonlThreadStore | None,
    output_fn: OutputFunction,
) -> dict[str, Any]:
    thread["status"] = "answering"
    thread["dry_run"] = False
    if thread_store:
        thread_store.upsert(thread)
    try:
        answer = answer_worker.answer(request_text)
    except AnswerWorkerFailure as error:
        thread["status"] = "answer_failed"
        thread["answer"] = {
            "model": error.model,
            "elapsed_seconds": error.elapsed_seconds,
            "text": None,
            "usage": None,
            "attempts": error.attempts,
            "error": str(error),
        }
        thread["final_output"] = None
        thread["execution_package"] = {
            "type": "answer_failed",
            "thread_id": thread["thread_id"],
            "action": "decide",
            "error": str(error),
            "attempts": error.attempts,
            "dry_run": False,
            "automatic_dispatch_allowed": False,
        }
        if thread_store:
            thread_store.upsert(thread)
        output_fn(f"Answer Worker 失败：{error}")
        output_fn("本地模型不可用，已转人工")
        return thread

    thread["status"] = "answered"
    thread["answer"] = answer
    thread["final_output"] = answer["text"]
    thread["execution_package"] = {
        "type": "local_answer",
        "thread_id": thread["thread_id"],
        "action": "decide",
        "payload": answer["text"],
        "dry_run": False,
        "automatic_dispatch_allowed": False,
    }
    if thread_store:
        thread_store.upsert(thread)
    output_fn(answer["text"])
    return thread


def _payload_as_prompt(payload: Any) -> str:
    if isinstance(payload, str):
        return payload
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _decode_process_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _snapshot_files(directory: Path) -> dict[str, dict[str, Any]]:
    files: dict[str, dict[str, Any]] = {}
    for current, dir_names, file_names in os.walk(directory, followlinks=False):
        current_path = Path(current)
        dir_names[:] = [name for name in dir_names if not (current_path / name).is_symlink()]
        for name in file_names:
            path = current_path / name
            relative = path.relative_to(directory).as_posix()
            if path.is_symlink():
                files[relative] = {"type": "symlink", "target": os.readlink(path)}
                continue
            digest = hashlib.sha256()
            size_bytes = 0
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
                    size_bytes += len(chunk)
            files[relative] = {"type": "file", "sha256": digest.hexdigest(), "size_bytes": size_bytes}
    return files


def _file_changes(
    before: Mapping[str, Mapping[str, Any]], after: Mapping[str, Mapping[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    modified = sorted(name for name in set(before) & set(after) if before[name] != after[name])
    return {
        "added": [{"path": name, **dict(after[name])} for name in added],
        "modified": [{"path": name, **dict(after[name])} for name in modified],
        "removed": [{"path": name, **dict(before[name])} for name in removed],
    }


class CodexDispatcher:
    """Run a confirmed Codex CLI task with workspace-write limited to its work directory."""

    def __init__(self, *, timeout_seconds: float = 600) -> None:
        self.project_root = Path(__file__).resolve().parents[1]
        self.timeout_seconds = timeout_seconds

    def workdir_for(self, thread_id: str) -> Path:
        configured = os.environ.get("LIGHT_DECIDER_CODEX_WORKDIR", "").strip()
        if configured:
            candidate = Path(configured).expanduser()
            if not candidate.is_absolute():
                candidate = self.project_root / candidate
        else:
            safe_thread_id = "".join(
                character if character.isalnum() or character in "-_." else "_" for character in thread_id
            ).strip(".") or str(uuid.uuid4())
            candidate = self.project_root / "workspace" / "codex_runs" / safe_thread_id

        workdir = candidate.resolve()
        if workdir == self.project_root:
            raise ValueError("LIGHT_DECIDER_CODEX_WORKDIR 不能指向项目根目录。")
        workdir.mkdir(parents=True, exist_ok=True)
        if not workdir.is_dir():
            raise NotADirectoryError(f"Codex 工作目录不是文件夹：{workdir}")
        return workdir

    def command_for(self, workdir: Path, last_message_path: Path) -> list[str]:
        codex = shutil.which("codex")
        if codex is None:
            raise FileNotFoundError("找不到 Codex CLI（codex）。")
        return [
            codex,
            "exec",
            "--sandbox",
            "workspace-write",
            "--config",
            "sandbox_workspace_write.exclude_slash_tmp=true",
            "--config",
            "sandbox_workspace_write.exclude_tmpdir_env_var=true",
            "--config",
            "sandbox_workspace_write.writable_roots=[]",
            "--skip-git-repo-check",
            "--ephemeral",
            "--color",
            "never",
            "--output-last-message",
            str(last_message_path),
            "-C",
            str(workdir),
            "-",
        ]

    def run(self, task_prompt: str, workdir: Path) -> dict[str, Any]:
        last_message_path = workdir / f".light_decider_codex_output_{uuid.uuid4().hex}.tmp"
        try:
            command = self.command_for(workdir, last_message_path)
        except Exception as error:
            return {
                "command": None,
                "command_line": None,
                "exit_code": None,
                "elapsed_seconds": 0.0,
                "final_output": str(error),
                "stdout": "",
                "stderr": "",
                "error": str(error),
                "timed_out": False,
                "files": {"added": [], "modified": [], "removed": []},
            }

        before = _snapshot_files(workdir)
        started = time.perf_counter()
        try:
            completed = subprocess.run(
                command,
                input=task_prompt,
                cwd=workdir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout_seconds,
                check=False,
            )
            elapsed = round(time.perf_counter() - started, 3)
            stdout = completed.stdout or ""
            stderr = completed.stderr or ""
            final_output = (
                last_message_path.read_text(encoding="utf-8", errors="replace")
                if last_message_path.exists()
                else stdout.strip()
            )
            result = {
                "command": command,
                "command_line": subprocess.list2cmdline(command),
                "exit_code": completed.returncode,
                "elapsed_seconds": elapsed,
                "final_output": final_output,
                "stdout": stdout,
                "stderr": stderr,
                "error": None if completed.returncode == 0 else f"Codex CLI exited with code {completed.returncode}.",
                "timed_out": False,
            }
        except subprocess.TimeoutExpired as error:
            elapsed = round(time.perf_counter() - started, 3)
            stdout = _decode_process_output(error.stdout)
            stderr = _decode_process_output(error.stderr)
            final_output = (
                last_message_path.read_text(encoding="utf-8", errors="replace")
                if last_message_path.exists()
                else stdout.strip()
            )
            result = {
                "command": command,
                "command_line": subprocess.list2cmdline(command),
                "exit_code": None,
                "elapsed_seconds": elapsed,
                "final_output": final_output,
                "stdout": stdout,
                "stderr": stderr,
                "error": f"Codex CLI timed out after {self.timeout_seconds:g} seconds.",
                "timed_out": True,
            }
        except Exception as error:
            elapsed = round(time.perf_counter() - started, 3)
            result = {
                "command": command,
                "command_line": subprocess.list2cmdline(command),
                "exit_code": None,
                "elapsed_seconds": elapsed,
                "final_output": str(error),
                "stdout": "",
                "stderr": "",
                "error": str(error),
                "timed_out": False,
            }
        finally:
            last_message_path.unlink(missing_ok=True)

        after = _snapshot_files(workdir)
        result["files"] = _file_changes(before, after)
        return result


def _run_codex_handoff(
    thread: dict[str, Any],
    request_text: str,
    context: list[dict[str, str]],
    route_result: Mapping[str, Any],
    dispatcher: CodexDispatcher,
    input_fn: InputFunction,
    output_fn: OutputFunction,
    thread_store: JsonlThreadStore | None,
) -> dict[str, Any]:
    action = str(route_result.get("action", ""))
    package = _dry_run_package(action, request_text, context, route_result, str(thread["thread_id"]))
    payload_text = _payload_as_prompt(package["payload"])
    thread["execution_package"] = package
    thread["final_route_result"] = dict(route_result)

    try:
        workdir = dispatcher.workdir_for(str(thread["thread_id"]))
        before_confirmation = _snapshot_files(workdir)
    except Exception as error:
        thread["status"] = "dispatch_failed"
        thread["dispatch_decision"] = {"confirmed_by_user": False, "error": str(error)}
        thread["final_output"] = str(error)
        if thread_store:
            thread_store.upsert(thread)
        output_fn(f"Codex 派发失败：{error}")
        return thread

    thread["codex_workdir"] = str(workdir)
    thread["status"] = "awaiting_dispatch_confirmation"
    if thread_store:
        thread_store.upsert(thread)
    output_fn("Codex handoff payload：\n" + payload_text)
    try:
        confirmation = input_fn("确认派发给 Codex？(y/N) ")
    except (EOFError, KeyboardInterrupt):
        confirmation = ""

    if confirmation.strip().casefold() != "y":
        thread["status"] = "dispatch_declined"
        thread["dispatch_decision"] = {
            "confirmed_by_user": False,
            "response": confirmation.strip(),
            "command_invoked": False,
            "workdir_files_before": before_confirmation,
            "files": {"added": [], "modified": [], "removed": []},
        }
        thread["final_output"] = "用户拒绝派发；Codex CLI 未调用。"
        if thread_store:
            thread_store.upsert(thread)
        output_fn("已拒绝派发，未调用 Codex。")
        return thread

    task_prompt = (
        "执行下面完整的 Codex handoff payload。所有新建或修改的文件只能放在当前工作目录内；"
        "实现请求应在该目录中生成对应源码文件。\n\n"
        "--- handoff payload begin ---\n"
        + payload_text
        + "\n--- handoff payload end ---"
    )
    if action == "codex+check_first":
        task_prompt += (
            "\n\n本次执行约束：只检查当前工作目录内的项目文件和约定。"
            "如果目录为空，或找不到现有项目及其约定，请报告检查范围和缺失项后停止；不要创建或修改实现文件。"
        )

    thread["status"] = "dispatched"
    thread["dry_run"] = False
    package["dry_run"] = False
    thread["dispatch_decision"] = {"confirmed_by_user": True, "response": confirmation.strip()}
    if thread_store:
        thread_store.upsert(thread)

    result = dispatcher.run(task_prompt, workdir)
    dispatch_event = {
        "confirmed_by_user": True,
        "command": result["command"],
        "command_line": result["command_line"],
        "prompt_transport": "stdin",
        "prompt_sha256": hashlib.sha256(task_prompt.encode("utf-8")).hexdigest(),
        "sandbox": "workspace-write",
        "working_directory": str(workdir),
        "exit_code": result["exit_code"],
        "elapsed_seconds": result["elapsed_seconds"],
        "final_output": result["final_output"],
        "stdout": result["stdout"],
        "stderr": result["stderr"],
        "error": result["error"],
        "timed_out": result["timed_out"],
        "files": result["files"],
    }
    thread["dispatch_event"] = dispatch_event
    thread["final_output"] = result["final_output"]
    thread["workspace_file_changes"] = result["files"]
    thread["status"] = "completed" if result["exit_code"] == 0 else "dispatch_failed"
    if thread_store:
        thread_store.upsert(thread)
    if result["final_output"]:
        output_fn("Codex 最终输出：\n" + result["final_output"])
    if result["exit_code"] != 0:
        output_fn(f"Codex 派发失败：{result['error'] or '未知错误'}")
    return thread


def run_execution(
    request_text: str,
    context: list[dict[str, str]] | None,
    route_request: RouteFunction,
    *,
    input_fn: InputFunction = input,
    output_fn: OutputFunction = print,
    thread_store: JsonlThreadStore | None = None,
    answer_worker: AnswerWorker | None = None,
    question_worker: AnswerWorker | None = None,
    codex_dispatcher: CodexDispatcher | None = None,
    thread_id: str | None = None,
    max_clarification_rounds: int = 2,
) -> dict[str, Any]:
    """Route a request and execute the clarify loop as a dry-run only."""
    original_request = request_text.strip()
    if not original_request:
        raise ValueError("request_text must not be empty")
    if max_clarification_rounds != 2:
        raise ValueError("The clarification loop is fixed at a maximum of two rounds.")

    stable_thread_id = thread_id or str(uuid.uuid4())
    safe_context = list(context or [])
    current_request = original_request
    route_result = route_request(current_request, safe_context)
    thread: dict[str, Any] = {
        "schema_version": "light_decider_thread_v1",
        "thread_id": stable_thread_id,
        "original_request": original_request,
        "context": safe_context,
        "clarification_rounds": [],
        "route_history": [_route_snapshot(route_result, current_request, "initial")],
        "current_request": current_request,
        "current_action": route_result.get("action"),
        "status": "routing",
        "execution_package": None,
        "dry_run": True,
        "automatic_dispatch_allowed": False,
    }
    if thread_store:
        thread_store.upsert(thread)

    if route_result.get("action") != "clarify":
        if route_result.get("action") == "decide" and answer_worker is not None:
            thread["current_action"] = "decide"
            thread["final_route_result"] = route_result
            return _run_answer_worker(thread, current_request, answer_worker, thread_store, output_fn)
        if str(route_result.get("action", "")).startswith("codex") and codex_dispatcher is not None:
            return _run_codex_handoff(
                thread,
                current_request,
                safe_context,
                route_result,
                codex_dispatcher,
                input_fn,
                output_fn,
                thread_store,
            )
        thread["status"] = "routed"
        thread["execution_package"] = _dry_run_package(
            str(route_result.get("action", "")), current_request, safe_context, route_result, stable_thread_id
        )
        thread["final_route_result"] = route_result
        if thread_store:
            thread_store.upsert(thread)
        return thread

    for round_number in range(1, max_clarification_rounds + 1):
        question_package = build_question_package(route_result, current_request)
        if question_package.get("template_reason") == "generic_clarification" and question_worker is not None:
            try:
                generated_question = question_worker.clarification_question(current_request, safe_context)
                question_package["question"] = generated_question["question"]
                question_package["missing_points"] = generated_question["missing_points"]
                question_package["template_reason"] = "local_model_targeted_clarification"
            except AnswerWorkerFailure as error:
                question_package["question"] = (
                    "我还无法从当前请求中确定具体缺项。请直接指出尚未决定的行为、参数或候选方案。"
                )
                question_package["missing_points"] = ["本地模型未能识别具体缺项"]
                question_package["generation_error"] = str(error)
        thread["status"] = "awaiting_user"
        thread["pending_question"] = question_package
        thread["current_action"] = "clarify"
        if thread_store:
            thread_store.upsert(thread)

        output_fn(f"需要补充：{question_package['question']}")
        try:
            answer = input_fn("补充答复（空行或 quit 中止）> ")
        except (EOFError, KeyboardInterrupt):
            answer = ""

        if _is_abort(answer):
            thread["status"] = "aborted_by_user"
            thread["pending_question"] = None
            thread["execution_package"] = {
                "type": "aborted",
                "thread_id": stable_thread_id,
                "dry_run": True,
                "automatic_dispatch_allowed": False,
            }
            if thread_store:
                thread_store.upsert(thread)
            output_fn("已中止澄清回路。")
            return thread

        round_entry = {
            "round": round_number,
            "question": str(question_package["question"]),
            "missing_points": question_package.get("missing_points", []),
            "answer": answer.strip(),
        }
        thread["clarification_rounds"].append(round_entry)
        thread["clarification_round"] = {
            "question": round_entry["question"],
            "answer": round_entry["answer"],
        }
        current_request = original_request + "".join(
            f"\n补充：{entry['answer']}" for entry in thread["clarification_rounds"]
        )
        round_entry["enhanced_request"] = current_request
        thread["current_request"] = current_request
        thread["pending_question"] = None
        thread["status"] = "routing"
        if thread_store:
            # Persist the answer on the same thread before the router is called.
            thread_store.upsert(thread)
        route_result = route_request(current_request, safe_context)
        round_entry["reroute_action"] = route_result.get("action")
        round_entry["reroute_reason"] = route_result.get("reason")
        thread["current_action"] = route_result.get("action")
        thread["route_history"].append(
            _route_snapshot(route_result, current_request, f"after_clarification_{round_number}")
        )

        if route_result.get("action") != "clarify":
            if route_result.get("action") == "decide" and answer_worker is not None:
                thread["final_route_result"] = route_result
                return _run_answer_worker(thread, current_request, answer_worker, thread_store, output_fn)
            if str(route_result.get("action", "")).startswith("codex") and codex_dispatcher is not None:
                return _run_codex_handoff(
                    thread,
                    current_request,
                    safe_context,
                    route_result,
                    codex_dispatcher,
                    input_fn,
                    output_fn,
                    thread_store,
                )
            thread["status"] = "routed"
            thread["final_route_result"] = route_result
            thread["execution_package"] = _dry_run_package(
                str(route_result.get("action", "")), current_request, safe_context, route_result, stable_thread_id
            )
            if thread_store:
                thread_store.upsert(thread)
            output_fn(f"澄清完成，最终动作：{route_result.get('action')}（dry-run，未派发）")
            return thread

        if thread_store:
            thread_store.upsert(thread)

        if round_number == max_clarification_rounds:
            thread["status"] = "routed_to_human"
            thread["final_route_result"] = route_result
            thread["execution_package"] = {
                "type": "human_review",
                "thread_id": stable_thread_id,
                "request_text": current_request,
                "clarification_rounds": thread["clarification_rounds"],
                "reason": "clarification_round_limit_reached",
                "dry_run": True,
                "automatic_dispatch_allowed": False,
            }
            if thread_store:
                thread_store.upsert(thread)
            output_fn("转人工")
            return thread

    raise AssertionError("Clarification loop exited without a terminal state.")


def _load_router(model_path: Path, strip_fenced_code: bool) -> RouteFunction:
    if model_path.suffix.lower() == ".joblib":
        if strip_fenced_code:
            raise ValueError("--strip-fenced-code 需要语义模型目录。")
        from .predict import load_artifact, suggest_route as suggest_light_route

        artifact = load_artifact(model_path)

        def route_request(text: str, context: list[dict[str, str]] | None) -> dict[str, Any]:
            return suggest_light_route(artifact, text, context)

        return route_request

    from .semantic_runtime import SemanticIntentModel, suggest_route as suggest_semantic_route

    model = SemanticIntentModel(model_path)

    def route_request(text: str, context: list[dict[str, str]] | None) -> dict[str, Any]:
        return suggest_semantic_route(
            model,
            text,
            context,
            ignore_fenced_code_for_routing=strip_fenced_code,
        )

    return route_request


def _parse_context(raw_context: str) -> list[dict[str, str]]:
    try:
        context = json.loads(raw_context)
    except json.JSONDecodeError as error:
        raise ValueError(f"上下文 JSON 格式错误：{error}") from error
    if not isinstance(context, list) or any(
        not isinstance(message, dict) or not isinstance(message.get("text"), str)
        for message in context
    ):
        raise ValueError('上下文必须是 JSON 数组，例如：[{"role":"assistant","text":"之前的方案"}]')
    if any("role" in message and not isinstance(message["role"], str) for message in context):
        raise ValueError("上下文中的 role 必须是字符串。")
    return context


def _interactive_context() -> list[dict[str, str]] | None:
    raw = input("上下文 JSON（不需要就直接回车）> ").strip()
    try:
        return _parse_context(raw or "[]")
    except ValueError as error:
        print(error)
        return None


def _cli_progress_output(message: str) -> None:
    """Print only interaction that must happen before execution completes."""
    if message.startswith(("需要补充：", "Codex handoff payload：")):
        print(message)


def _print_cli_result(thread: Mapping[str, Any]) -> None:
    route_result = thread.get("final_route_result")
    if not isinstance(route_result, Mapping):
        history = thread.get("route_history") or []
        route_result = history[-1] if history and isinstance(history[-1], Mapping) else {}
    action = route_result.get("action") or thread.get("current_action") or "unknown"
    print(f"判断：{action}")

    status = thread.get("status")
    if status == "routed_to_human":
        output = "转人工"
    elif status == "aborted_by_user":
        output = "已中止澄清回路。"
    elif status == "answer_failed":
        output = "本地模型不可用，已转人工"
    else:
        output = thread.get("final_output")

    if output is None:
        package = thread.get("execution_package") or {}
        if str(action).startswith("codex") and package.get("type") == "codex_handoff":
            output = _payload_as_prompt(package.get("payload"))
        elif thread.get("dry_run"):
            output = "dry-run：未执行。"

    if output is not None:
        print("输出：")
        print(output)


def main(argv: Sequence[str] | None = None) -> None:
    import argparse
    import sys

    from .predict import DEFAULT_MODEL_PATH

    arguments = list(sys.argv[1:] if argv is None else argv)
    execution_switches = {"--execute", "--execute-dry-run"}
    if not execution_switches.intersection(arguments):
        # Preserve the original router CLI byte-for-byte when the new switch is absent.
        from try_router_semantic import main as original_router_main

        original_router_main(default_model=DEFAULT_MODEL_PATH)
        return

    parser = argparse.ArgumentParser(description="light_decider 执行层；Codex CLI 派发必须经用户确认。")
    parser.add_argument("--execute", action="store_true", help="启用本地 Answer Worker，并允许用户确认后调用 Codex CLI。")
    parser.add_argument("--execute-dry-run", action="store_true", help="只启用执行层 dry-run 与 clarify 回路。")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--strip-fenced-code", action="store_true")
    parser.add_argument("--text", help="单次请求；未传时进入交互模式。")
    parser.add_argument("--context", default="[]", help="JSON 对话上下文数组。")
    parser.add_argument("--thread-log", type=Path, default=Path(__file__).resolve().parents[1] / "logs" / "executor_threads.jsonl")
    args = parser.parse_args(arguments)
    if args.execute and args.execute_dry_run:
        parser.error("--execute 与 --execute-dry-run 不能同时使用。")

    if args.text is not None and not args.text.strip():
        parser.error("--text 不能为空。")
    try:
        context = _parse_context(args.context)
        route_request = _load_router(args.model, args.strip_fenced_code)
    except (ValueError, FileNotFoundError) as error:
        parser.error(str(error))

    store = JsonlThreadStore(args.thread_log)
    question_worker = AnswerWorker()
    answer_worker = question_worker if args.execute else None
    codex_dispatcher = CodexDispatcher() if args.execute else None
    if args.text is not None:
        thread = run_execution(
            args.text,
            context,
            route_request,
            output_fn=_cli_progress_output,
            thread_store=store,
            answer_worker=answer_worker,
            question_worker=question_worker,
            codex_dispatcher=codex_dispatcher,
        )
        _print_cli_result(thread)
        return

    print("输入 /exit 结束。")
    while True:
        try:
            request = input("\n当前消息> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n结束测试。")
            break
        if request.casefold() in {"/exit", "/quit", "exit", "quit"}:
            print("结束测试。")
            break
        if not request:
            continue
        context = _interactive_context()
        if context is None:
            continue
        thread = run_execution(
            request,
            context,
            route_request,
            output_fn=_cli_progress_output,
            thread_store=store,
            answer_worker=answer_worker,
            question_worker=question_worker,
            codex_dispatcher=codex_dispatcher,
        )
        _print_cli_result(thread)


if __name__ == "__main__":
    main()
