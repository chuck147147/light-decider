from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


_TEMPLATES: dict[str, dict[str, object]] = {
    "explicit_key_choice_question": {
        "missing_points": ["原请求列出的关键选项尚未确定"],
        "question": "请从原请求列出的方案中选一个；如果选择取决于适用条件或优先级，也请一并说明。",
    },
    "unresolved_policy_parameter_before_implementation": {
        "missing_points": ["会改变业务结果的规则、参数或优先顺序"],
        "question": "请补充这项功能要遵循的关键规则或参数；如果有多个方案，请指出采用哪一个及其适用条件。",
    },
    "payment_account_change_controls_missing": {
        "missing_points": ["账户换绑前的身份核验、审批或复核要求"],
        "question": "请明确账户换绑前必须执行哪些身份核验、审批或复核步骤。",
    },
    "rate_limit_threshold_or_window_missing": {
        "missing_points": ["限流计数口径、阈值和时间窗口"],
        "question": "请明确限流按什么对象计数、允许的次数以及对应时间窗口。",
    },
    "locale_sensitive_value_format_ambiguous": {
        "missing_points": ["输入值适用的地区或明确格式"],
        "question": "请明确输入值应按哪个地区或哪种格式解析；如果无法判断，请说明是否拒绝歧义输入。",
    },
    "reminder_cadence_missing": {
        "missing_points": ["重复提醒的频率和停止条件"],
        "question": "请明确重复提醒的间隔，以及满足什么条件后停止提醒。",
    },
    "concurrent_edit_conflict_policy_missing": {
        "missing_points": ["并发修改冲突时的处理规则"],
        "question": "多人同时修改时发生冲突应如何处理，例如优先保留哪一方或是否交由用户选择？",
    },
    "contract_history_access_or_retention_policy_missing": {
        "missing_points": ["可查看合同历史的角色和历史保留期限"],
        "question": "请明确哪些角色可以查看合同历史，以及历史记录需要保留多久。",
    },
    "external_auditor_scope_mapping_missing": {
        "missing_points": ["外部审计可访问材料的范围映射规则"],
        "question": "请明确哪些材料属于外部审计范围，以及如何把业务材料映射到该范围。",
    },
    "referent_missing_without_context": {
        "missing_points": ["请求中未指明的对象或指代"],
        "question": "请指出请求里“这个/那个/之前提到的”具体指哪一项，或补充相关上下文。",
    },
    "personal_legal_outcome_without_context": {
        "missing_points": ["判断个人法律结果所需的地区、时间和关键事实"],
        "question": "要判断这件事还需要哪些适用地区、时间和相关事实？请只补充你愿意提供且与问题直接相关的信息。",
    },
    "conflicting_execution_constraints": {
        "missing_points": ["相互冲突的执行要求应以哪一项为优先"],
        "question": "这几项要求彼此冲突。请说明哪一项优先，或指出可以放宽的限制。",
    },
}

_FALLBACK = {
    "missing_points": ["处理对象、触发条件或预期操作中尚未明确的部分"],
    "question": "请指出希望系统在什么情况下，对哪个对象执行什么操作；如果缺的是参数，请给出取值或范围。",
}


def _candidate_reasons(route_result: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    clauses = route_result.get("clause_analysis", ())
    if isinstance(clauses, Sequence) and not isinstance(clauses, (str, bytes)):
        for clause in clauses:
            if not isinstance(clause, Mapping) or clause.get("action") != "clarify":
                continue
            for key in ("policy_override", "reason"):
                value = clause.get(key)
                if isinstance(value, str) and value:
                    reasons.append(value)
    for key in ("policy_override", "reason"):
        value = route_result.get(key)
        if isinstance(value, str) and value:
            reasons.append(value)
    return list(dict.fromkeys(reasons))


def build_question_package(
    route_result: Mapping[str, Any],
    request_text: str,
) -> dict[str, object]:
    """Return a question and missing-point list, preferring router-provided data."""
    supplied = route_result.get("question")
    if isinstance(supplied, Mapping):
        question = supplied.get("question")
        missing = supplied.get("missing_points", ())
        if isinstance(question, str) and question.strip():
            points = [str(item).strip() for item in missing if str(item).strip()] if isinstance(missing, Sequence) and not isinstance(missing, (str, bytes)) else []
            return {
                "question": question.strip(),
                "missing_points": points or ["路由器标记为待澄清的信息"],
                "template_reason": "router_question_package",
            }
    elif isinstance(supplied, str) and supplied.strip():
        return {
            "question": supplied.strip(),
            "missing_points": ["路由器标记为待澄清的信息"],
            "template_reason": "router_question_string",
        }

    for reason in _candidate_reasons(route_result):
        template = _TEMPLATES.get(reason)
        if template:
            return {**template, "template_reason": reason}

    return {**_FALLBACK, "template_reason": "generic_clarification"}
