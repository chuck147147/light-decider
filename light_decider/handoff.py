from __future__ import annotations

from collections.abc import Mapping, Sequence


def format_codex_handoff(
    text: str,
    context: Sequence[Mapping[str, str]] | None = None,
    *,
    action: str = "codex",
    declared_defaults: Sequence[Mapping[str, str]] | None = None,
    check_first_targets: Sequence[str] | None = None,
) -> str:
    """Package a Codex-bound request without inventing or rewriting requirements."""
    sections = ["## 用户当前请求（原文）", text.strip()]
    relevant_context: list[str] = []
    for message in context or ():
        content = message.get("text", "")
        if not isinstance(content, str) or not content.strip():
            continue
        role = message.get("role", "unknown")
        role = role.strip() if isinstance(role, str) else "unknown"
        relevant_context.append(f"- {role or 'unknown'}：{content.strip()}")

    if relevant_context:
        sections.extend(["## 相关对话上下文", "\n".join(relevant_context)])

    if action == "codex+declare_default" and declared_defaults:
        default_lines = []
        for item in declared_defaults:
            default_lines.extend(
                [
                    f"- 采用默认：{item.get('value', '').strip()}",
                    f"  理由：{item.get('reason', '').strip()}",
                ]
            )
        sections.extend(
            [
                "## 本次采用的默认",
                "\n".join(default_lines),
                "开始前检查相关实现、配置或文档是否有直接冲突的约定；发现冲突时转按 `codex+check_first` 核对。若查不到一致方案或冲突无法兼容，停止并向用户澄清。",
            ]
        )

    if action == "codex+check_first":
        targets = list(check_first_targets or ()) or [
            "相关模块的现有实现与配置",
            "相关文档、API/数据约定",
            "覆盖该行为的测试",
        ]
        sections.extend(
            [
                "## 执行前先检查",
                "检查以下位置：\n" + "\n".join(f"- {target}" for target in targets),
                "若查不到可直接沿用的一致约定，或发现相互冲突的约定，先停止并向用户澄清，再继续实现。",
            ]
        )

    sections.extend(["## 处理要求", "保留用户原意，不要补造需求。若缺少完成任务所必需的信息，先向用户澄清。"])
    return "\n\n".join(sections)
