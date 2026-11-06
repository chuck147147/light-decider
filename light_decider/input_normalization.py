from __future__ import annotations

import re
from collections.abc import Mapping, Sequence


_FENCED_CODE_BLOCK = re.compile(
    r"(?m)(?P<prefix>^|\n)[ \t]{0,3}(?P<fence>`{3,}|~{3,})[^\r\n]*\r?\n"
    r".*?^[ \t]{0,3}(?P=fence)[ \t]*\r?(?=\n|$)",
    re.DOTALL,
)
_TRAILING_HORIZONTAL_SPACE = re.compile(r"[ \t]+\n")
_EXCESS_NEWLINES = re.compile(r"\n{3,}")


def strip_fenced_code_blocks(text: str) -> tuple[str, bool]:
    """Remove Markdown fenced code before intent classification, preserving prose."""
    if not text:
        return "", False
    matches = list(_FENCED_CODE_BLOCK.finditer(text))
    if not matches:
        return text.strip(), False

    cleaned = _FENCED_CODE_BLOCK.sub(lambda match: match.group("prefix"), text)
    cleaned = _TRAILING_HORIZONTAL_SPACE.sub("\n", cleaned)
    cleaned = _EXCESS_NEWLINES.sub("\n\n", cleaned).strip()
    return cleaned, True


def strip_code_from_context(
    context: Sequence[Mapping[str, str]] | None,
) -> tuple[list[dict[str, str]], bool]:
    """Keep conversational prose while removing fenced code from model context."""
    cleaned: list[dict[str, str]] = []
    removed_any = False
    for message in context or ():
        content = message.get("text", "")
        role = message.get("role", "unknown")
        if not isinstance(content, str):
            continue
        normalized, removed = strip_fenced_code_blocks(content)
        removed_any = removed_any or removed
        if normalized:
            cleaned.append({"role": role if isinstance(role, str) else "unknown", "text": normalized})
    return cleaned, removed_any
