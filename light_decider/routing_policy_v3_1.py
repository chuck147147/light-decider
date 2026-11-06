from __future__ import annotations

import re
from collections.abc import Mapping, Sequence


POLICY_VERSION = "v3.1"


LEGAL_TOPICS = (
    "遗产",
    "继承",
    "遗嘱",
    "所有权",
    "产权",
    "房产",
    "土地权",
    "赔偿",
    "起诉",
    "违法",
    "合同纠纷",
)
PERSONAL_REFERENCES = ("我", "我们", "我的", "我家")
OUTCOME_TERMS = ("能", "可以", "可不可以", "是否", "有权", "拿到", "取得", "获得")
QUESTION_MARKS = ("吗", "么", "是否", "能否", "可否", "?", "？")

UNRESOLVED_REFERENT_PREFIXES = (
    "这人",
    "这个人",
    "那人",
    "那个人",
    "这位",
    "那位",
    "他",
    "她",
    "它",
    "这件事",
    "刚才那个",
    "上次那个",
    "之前那个",
    "上面那个",
    "刚才说的",
    "之前说的",
    "上面说的",
)

# Narrow object-action patterns avoid treating generic phrases such as
# "这个 Python 报错怎么排查" as unresolved references, while still blocking
# multi-clause dispatch when an action targets an unnamed "that/another" item.
UNRESOLVED_OBJECT_ACTION_PREFIXES = (
    "先把那个",
    "再把那个",
    "然后把那个",
    "把那个",
    "先把它",
    "再把它",
    "然后把它",
    "把它",
    "把那份",
    "把这份",
    "把那几项",
    "把第二份",
    "把第二个",
    "把有问题的几条",
    "把之前说的",
    "把刚才说的",
    "把上次说的",
    "照旧版本恢复",
    "按旧版本恢复",
    "恢复到旧版本",
    "剩余的也处理",
    "剩下的也处理",
    "剩余部分也处理",
    "剩下部分也处理",
    "剩余的也一起处理",
    "剩下的也一起处理",
    "剩余部分也一起处理",
    "剩下部分也一起处理",
    "剩余的也做掉",
    "剩下的也做掉",
    "先删掉另一个",
    "再删掉另一个",
    "然后删掉另一个",
    "删掉另一个",
    "先删除另一个",
    "再删除另一个",
    "然后删除另一个",
    "删除另一个",
    "还是改成那个",
    "改成那个",
    "换成那个",
    "帮我把上次那个",
    "把上次那个",
)

COMPARISON_CUES = (
    "比较",
    "对比",
    "优缺点",
    "区别",
    "差异",
    "取舍",
    "哪个好",
    "哪个更",
)
EXPLANATION_CUES = (
    "解释",
    "说明",
    "介绍",
    "讲解",
    "讲清楚",
    "讲重点",
    "讲原理",
    "分析",
    "先讲",
    "先说",
    "说说",
    "告诉我",
    "只分析",
    "只解释",
)
NEGATED_EXPLANATION_CUE_PATTERN = re.compile(
    r"(?:没有|没|未|尚未|并未|缺少|缺乏|不需要|无需)[^，。；;！？!?]{0,8}"
    r"(?:解释|说明|介绍|讲解|讲清楚|讲重点|讲原理|分析|先讲|先说|说说|告诉我|只分析|只解释)"
)
REPORTING_REQUIREMENT_PATTERN = re.compile(
    r"(?:交接(?:里|中)?|handoff).{0,24}"
    r"(?:告诉我|写明|注明|说明|列出).{0,28}"
    r"(?:最终|采用|选用|默认|理由|样式|规则|参数|方案)",
    re.IGNORECASE,
)
SELF_CONTAINED_CONCEPT_PATTERNS = (
    re.compile(r"\b[A-Z][A-Za-z0-9]*(?:[-/][A-Za-z0-9]+)*\b"),
)
SELF_CONTAINED_CONCEPT_CUES = (
    "是什么",
    "能解决什么问题",
    "有什么作用",
    "怎么工作",
    "如何工作",
    "主要区别",
    "有什么区别",
    "有什么差异",
)
IMPLEMENTATION_REQUEST_PATTERNS = (
    re.compile(r"^(?:从零|从头)(?:开始)?(?:做|写|搭建|创建|实现|开发|构建).{0,80}"),
    re.compile(r"^(?:做|写|新写|新建|创建|新增|实现|搭建).{0,36}(?:页|接口|工具|工作板|白板|功能|报表|模块|服务|程序|提醒|CLI|子命令|命令|徽章)"),
    re.compile(r"^(?:在|给|为).{0,40}(?:加一个|加个|加|添加|新增|增加|实现|创建|做邮件提醒|做提醒|改成|改为)"),
    re.compile(r"(?:^|[，,。；;])\s*(?:在|给|为).{0,48}(?:加一个|加个|加|添加|新增|增加|实现|创建|做邮件提醒|做提醒|改成|改为)"),
    re.compile(r"^把.{0,80}(?:转成|转为|转换为|解析|导入|读取)"),
    re.compile(r"(?:按|照)(?:这个|该|此|上述).{0,20}(?:需求|方案).{0,12}(?:实现|修改|调整|接入|新增|修复)"),
)
EXPLICIT_CHOICE_QUESTION_PATTERN = re.compile(
    r"(?:还是|二选一|选哪个|选哪一个|选择哪一种|选择哪一个|A\s*/\s*B).{0,48}"
    r"(?:吗|么|要不要|哪个|哪种|选择|\?|？)?",
    re.IGNORECASE,
)
CHOICE_ALTERNATIVE_PATTERN = re.compile(r"([^，。；！？?]{1,24})(?:还是|或者)([^，。；！？?]{1,24})")
HIGH_RISK_MARKERS = {
    "payment": (
        "支付", "付款", "扣款", "退款", "收款", "收款账户", "结算", "托管款", "充值", "账单",
        "换绑账户", "银行账户", "payment", "payout", "billing", "refund",
    ),
    "permission": (
        "权限", "授权", "访问控制", "访问", "角色", "mfa", "财务人员", "审计员", "外部审计",
        "客户资料", "客户数据", "工资报表", "薪酬报表", "合同历史", "合同记录", "谁能查看",
        "permission", "authorization", "access control",
    ),
    "deduplication": (
        "幂等", "去重", "重复提交", "重复事件", "防重", "重放", "dedup", "idempotency", "replay",
    ),
    "rate_limiting": (
        "限流", "频率限制", "请求频率", "发送限制", "配额", "超量", "超限", "每分钟", "每小时",
        "429", "burst", "rate limit", "rate-limit",
    ),
}
LOCALE_PARSING_CUES = ("解析", "转成数值", "转为数字", "导入", "小数", "金额", "浓度", "日期", "时间", "locale")
EXPLICIT_DEFAULT_AUTHORITY_CUES = (
    "你看着办", "按惯例", "按常见做法", "按常见习惯", "由你按常见习惯", "由你按惯例",
    "由你决定", "由你选择", "交给你决定", "你来定", "自行选择", "不用追问",
)
UNRESOLVED_POLICY_TERMS = ("没定", "未定", "待定", "需要确定", "要确定", "也要确定", "还要确定", "尚未决定")
POLICY_QUESTION_PATTERN = re.compile(r"(?:是否|能否|可否|要不要|多久|多长时间|多少|几次|哪个|哪种|怎么办|如何处理|怎么处理)")
EXECUTION_CUES = (
    "修改",
    "改成",
    "改为",
    "改好",
    "调整",
    "更新",
    "修复",
    "修好",
    "新增",
    "添加",
    "加",
    "加上",
    "补上",
    "补充",
    "接入",
    "实现",
    "训练",
    "运行",
    "执行",
    "生成",
    "导出",
    "部署",
    "重构",
    "替换",
    "删除",
    "创建",
    "写一个",
    "写入",
)
EXECUTION_TARGET_CUES = (
    "代码",
    "项目",
    "仓库",
    "脚本",
    "文件",
    "模块",
    "接口",
    "程序",
    "应用",
    "页面",
    "请求",
    "功能",
    "模型",
    "配置",
    "按钮",
    "导出",
    "数据",
)
ASSERTIVE_REQUIREMENT_CUES = (
    "都要能",
    "都得能",
    "必须能",
    "需要能",
    "要能",
    "必须支持",
    "需要支持",
    "要支持",
    "必须兼容",
    "需要兼容",
    "最多",
    "要留着",
    "需要留着",
)
REQUIREMENT_CAPABILITY_CUES = (
    "解析",
    "读取",
    "导入",
    "导出",
    "保存",
    "处理",
    "识别",
    "兼容",
    "保留",
    "显示",
    "生成",
    "返回",
    "重试",
    "附上",
    "留着",
    "等待",
)
REQUIREMENT_TARGET_CUES = (
    "列",
    "字段",
    "文件",
    "格式",
    "数据",
    "配置",
    "接口",
    "请求",
    "项目",
    "页面",
    "脚本",
    "程序",
    "表格",
    "记录",
    "结果",
    "日志",
    "服务",
    "状态码",
    "文件名",
    "429",
)
REQUIREMENT_QUESTION_CUES = (
    "吗",
    "么",
    "怎么",
    "如何",
    "哪些",
    "什么",
    "为什么",
    "是否",
    "要不要",
    "?",
    "？",
)
NON_EXECUTION_CUES = (
    "只解释",
    "只分析",
    "只讨论",
    "只想了解",
    "不用改",
    "不要改",
    "不要修改",
    "暂时不改",
    "先不改",
    "不需要实现",
)
HYPOTHETICAL_QUERY_CUES = (
    "会不会",
    "有什么影响",
    "有没有影响",
    "是否应该",
    "该不该",
    "值不值得",
    "是否值得",
)
HYPOTHETICAL_SCENARIO_PREFIXES = ("如果", "假如", "假设")
HYPOTHETICAL_CONSEQUENCE_CUES = (
    "会带来哪些风险",
    "会带来什么风险",
    "会有什么风险",
    "会造成什么影响",
    "会带来什么影响",
    "会有哪些后果",
    "可能出现哪些问题",
)
WORKSPACE_NO_EDIT_CUES = (
    "先别改项目",
    "先别修改项目",
    "不要改项目",
    "不要修改项目",
    "先别改仓库",
    "先别修改仓库",
    "暂时别动项目",
    "先不要改旧版流程",
    "先不要修改旧版流程",
    "不要改旧版流程",
    "不要修改旧版流程",
)
EXPLANATION_ONLY_CUES = ("只需要解释", "只解释一下", "只想听解释")


def _has_explanation_cue(text: str) -> bool:
    """Ignore reporting requirements and negated mentions; neither asks for an explanation."""
    positive_text = REPORTING_REQUIREMENT_PATTERN.sub(" ", text)
    positive_text = NEGATED_EXPLANATION_CUE_PATTERN.sub(" ", positive_text)
    return any(cue in positive_text for cue in EXPLANATION_CUES)


def _is_self_contained_concept_question(text: str) -> bool:
    normalized = text.strip()
    has_named_concept = any(pattern.search(normalized) for pattern in SELF_CONTAINED_CONCEPT_PATTERNS)
    has_question_cue = any(cue in normalized for cue in SELF_CONTAINED_CONCEPT_CUES)
    has_question_mark = any(mark in normalized for mark in ("?", "？", "吗", "么"))
    return has_named_concept and has_question_cue and has_question_mark
DIRECT_TEXT_TRANSFORMATION_CUES = (
    "翻译成",
    "翻成",
    "译成",
    "压缩成",
    "缩成",
    "总结成",
    "概括成",
    "精简成",
)
WORKSPACE_ARTIFACT_CUES = ("仓库", "项目", "README", "文件", "文档", "页面", "脚本", "代码")
OFFER_CUES = (
    "要不要",
    "需要我",
    "我可以",
    "我会",
    "我能",
    "我建议",
    "是否要我",
    "可以帮你",
    "接下来我",
    "下一步我",
)
CHOICE_CUES = (
    "还是",
    "或者",
    "也可以",
    "你想先",
    "哪一个",
    "哪个方案",
    "选哪个",
    "哪一种",
)
VAGUE_SELECTION_CUES = (
    "就那个",
    "还是那个",
    "之前说过",
    "之前说的",
    "我之前说的",
    "刚才提到",
    "上次那个",
    "我说的那个",
    "按我说的",
    "那个就行",
    "那个就好",
    "那个吧",
    "看起来更合适",
    "更合适的那个",
    "更好的那个",
    "更稳妥的那个",
)
OPTION_NUMBER_CHARACTERS = "一二三四1234"
CURRENT_OPTION_PATTERNS = (
    re.compile(rf"(?:用|选|选择|采用|按|就按)第?([{OPTION_NUMBER_CHARACTERS}])(?:种|个|项|方案)?"),
    re.compile(rf"(?:用|选|选择|采用|按|就按)(?:方案|选项)([{OPTION_NUMBER_CHARACTERS}])"),
)
CONTEXT_OPTION_PATTERN = re.compile(
    rf"(?:方案|选项)([{OPTION_NUMBER_CHARACTERS}])|第([{OPTION_NUMBER_CHARACTERS}])(?:种|个|项)"
)
AFFIRMATION_PATTERN = re.compile(
    r"^(?:好|好的|行|可以|可以的|嗯|没问题|继续(?:吧)?|照做|按这个来|就这样(?:做(?:吧)?)?|开始吧)"
    r"(?:\s|[，,。；;]|$)"
)
EXPLICIT_EXECUTION_PATTERNS = (
    re.compile(r"(?:请|帮我|替我|直接).{0,18}(?:修改|改成|改为|改好|调整|修复|修好|新增|添加|加上|接入|实现|训练|运行|执行|生成|导出|部署|重构|替换|删除|创建|写一个|写入|更新(?:为|成|到|一下))"),
    re.compile(r"(?:把|将).{0,18}(?:改成|改为|改好|调整|修复|修好|新增|添加|加上|接入|实现|训练|运行|生成|导出|部署|替换|删除|创建|写入|更新(?:为|成|到|一下))"),
    re.compile(r"(?:按|照)(?:这个|该|此|方案|上述).{0,20}(?:修改|更新|修复|实现|接入|补充|添加|新增|删除|替换|调整)"),
    re.compile(r"(?:开始|现在|直接)(?:修改|改|修复|训练|运行|执行|部署|实现|新增|添加|调整)"),
)
STRONG_IMPLEMENTATION_PATTERNS = (
    re.compile(r"(?:把|将).{0,20}(?:改成|改为|调整|修复|修好|新增|添加|接入|实现|替换|删除|更新(?:为|成|到|一下)|写入)"),
    re.compile(r"(?:按|照)(?:这个|该|此|方案|上述).{0,20}(?:修改|更新|修复|实现|接入|补充|添加|新增|删除|替换|调整)"),
)
DIRECT_EXECUTION_REQUEST_PATTERNS = (
    re.compile(r"(?:请|帮我|替我|我想让你|现在就|立即|直接).{0,24}(?:修改|改成|改为|调整|修复|修好|新增|添加|加上|接入|实现|训练|运行|执行|生成|导出|部署|上线|发布|重构|替换|删除|创建|写入|更新)"),
)


def _has_context(context: Sequence[Mapping[str, str]] | None) -> bool:
    return any(
        isinstance(message.get("text"), str) and message["text"].strip()
        for message in context or ()
    )


def clarification_override_reason(
    text: str,
    context: Sequence[Mapping[str, str]] | None = None,
) -> str | None:
    """Flag personal legal-outcome questions when no conversation context is supplied."""
    if _has_context(context):
        return None

    normalized = text.strip()
    if not normalized:
        return None
    is_personal = any(term in normalized for term in PERSONAL_REFERENCES)
    is_legal = any(term in normalized for term in LEGAL_TOPICS)
    asks_outcome = any(term in normalized for term in OUTCOME_TERMS)
    is_question = any(mark in normalized for mark in QUESTION_MARKS)
    if is_personal and is_legal and asks_outcome and is_question:
        return "personal_legal_outcome_without_context"
    return None


def referent_override_reason(
    text: str,
    context: Sequence[Mapping[str, str]] | None = None,
    *,
    parent_request_text: str | None = None,
) -> str | None:
    """Flag clear references to missing people, objects, or prior messages."""
    if _has_context(context):
        return None
    if parent_request_text and _is_self_contained_concept_question(parent_request_text):
        return None
    normalized = text.strip().lstrip("\"'“‘（(")
    wrappers = ("麻烦你", "麻烦", "请你", "请", "帮我", "替我", "直接")
    while True:
        wrapper = next((item for item in wrappers if normalized.startswith(item)), None)
        if wrapper is None:
            break
        normalized = normalized[len(wrapper):].lstrip(" \t，,：:")
    unresolved_prefixes = (*UNRESOLVED_REFERENT_PREFIXES, *UNRESOLVED_OBJECT_ACTION_PREFIXES)
    if any(normalized.startswith(prefix) for prefix in unresolved_prefixes):
        return "referent_missing_without_context"
    return None


def _option_route_from_context(text: str, assistant_text: str) -> str | None:
    selected = next(
        (match.group(1) for pattern in CURRENT_OPTION_PATTERNS if (match := pattern.search(text))),
        None,
    )
    if selected is None:
        return None

    markers = list(CONTEXT_OPTION_PATTERN.finditer(assistant_text))
    for index, marker in enumerate(markers):
        number = marker.group(1) or marker.group(2)
        if number != selected:
            continue
        end = markers[index + 1].start() if index + 1 < len(markers) else len(assistant_text)
        segment = assistant_text[marker.end():end]
        segment = re.split(r"[。！？!?；;\n]", segment, maxsplit=1)[0]
        has_execution = (
            any(cue in segment for cue in EXECUTION_CUES)
            and any(cue in segment for cue in EXECUTION_TARGET_CUES)
        )
        has_explanation = _has_explanation_cue(segment)
        if has_execution:
            return "codex"
        if has_explanation:
            return "decide"
    return None


def intent_override_reason(
    text: str,
    context: Sequence[Mapping[str, str]] | None = None,
) -> tuple[str, str] | None:
    """Apply narrow advice/explanation and pending-action context overrides."""
    normalized = text.strip()
    if not normalized:
        return None

    has_explicit_execution = any(pattern.search(normalized) for pattern in EXPLICIT_EXECUTION_PATTERNS)
    has_direct_action_request = any(pattern.search(normalized) for pattern in DIRECT_EXECUTION_REQUEST_PATTERNS)
    has_explanation_request = _has_explanation_cue(normalized)
    asks_explanation = has_explanation_request and any(cue in normalized for cue in REQUIREMENT_QUESTION_CUES)
    has_non_execution_request = any(cue in normalized for cue in NON_EXECUTION_CUES)
    has_hypothetical_query = any(cue in normalized for cue in HYPOTHETICAL_QUERY_CUES)
    has_strong_implementation = any(pattern.search(normalized) for pattern in STRONG_IMPLEMENTATION_PATTERNS)

    has_workspace_freeze = any(cue in normalized for cue in WORKSPACE_NO_EDIT_CUES)
    has_explanation_only = any(cue in normalized for cue in EXPLANATION_ONLY_CUES)
    if (has_workspace_freeze or has_explanation_only) and has_direct_action_request:
        return "clarify", "conflicting_execution_constraints"

    is_hypothetical_outcome_question = (
        normalized.startswith(HYPOTHETICAL_SCENARIO_PREFIXES)
        and any(cue in normalized for cue in HYPOTHETICAL_CONSEQUENCE_CUES)
        and not has_direct_action_request
    )
    if is_hypothetical_outcome_question:
        return "decide", "hypothetical_change_question"

    is_direct_text_transformation = (
        any(cue in normalized for cue in DIRECT_TEXT_TRANSFORMATION_CUES)
        and not any(cue in normalized for cue in WORKSPACE_ARTIFACT_CUES)
        and not has_explicit_execution
    )
    if is_direct_text_transformation:
        return "decide", "direct_text_transformation"

    if has_strong_implementation and not asks_explanation and not has_non_execution_request and not has_hypothetical_query:
        return "codex", "explicit_implementation_request"

    if has_explanation_request and (not has_explicit_execution or asks_explanation):
        return "decide", "explicit_explanation_request"

    has_comparison_request = any(cue in normalized for cue in COMPARISON_CUES)
    if has_comparison_request and not has_explicit_execution:
        return "decide", "comparison_without_execution_request"

    has_assertive_requirement = any(cue in normalized for cue in ASSERTIVE_REQUIREMENT_CUES)
    is_technical_requirement = (
        has_assertive_requirement
        and any(cue in normalized for cue in REQUIREMENT_CAPABILITY_CUES)
        and any(cue in normalized for cue in REQUIREMENT_TARGET_CUES)
    )
    is_question_or_discussion = (
        any(cue in normalized for cue in REQUIREMENT_QUESTION_CUES)
        or any(cue in normalized for cue in NON_EXECUTION_CUES)
    )
    if is_technical_requirement and not is_question_or_discussion:
        return "codex", "assertive_technical_requirement"

    if not context:
        return None

    last_assistant = next(
        (
            message.get("text", "").strip()
            for message in reversed(context)
            if message.get("role") == "assistant" and message.get("text", "").strip()
        ),
        "",
    )
    if not last_assistant:
        return None

    selected_option_route = _option_route_from_context(normalized, last_assistant)
    if selected_option_route is not None:
        return selected_option_route, "selected_contextual_option"

    asks_choice = any(cue in last_assistant for cue in CHOICE_CUES)
    vague_selection = any(cue in normalized for cue in VAGUE_SELECTION_CUES)
    if asks_choice and vague_selection:
        return "clarify", "ambiguous_pending_choice"

    if not AFFIRMATION_PATTERN.match(normalized):
        return None

    offered_execution = (
        any(cue in last_assistant for cue in OFFER_CUES)
        and any(cue in last_assistant for cue in EXECUTION_CUES)
        and any(cue in last_assistant for cue in EXECUTION_TARGET_CUES)
    )
    offered_explanation = _has_explanation_cue(last_assistant)

    # When the assistant offered two kinds of help and explicitly asked which
    # one the user wants, a bare "好" does not select an option.
    if offered_execution and not offered_explanation:
        return "codex", "confirmed_pending_code_action"
    if offered_explanation and not offered_execution:
        return "decide", "confirmed_pending_explanation"
    if offered_execution and offered_explanation and any(cue in last_assistant for cue in CHOICE_CUES):
        return "clarify", "ambiguous_pending_choice"
    return None


def is_implementation_request(text: str, suggested_route: str | None = None) -> bool:
    normalized = text.strip()
    if not normalized or any(cue in normalized for cue in NON_EXECUTION_CUES):
        return False
    explicit_implementation = any(
        pattern.search(normalized)
        for pattern in (*EXPLICIT_EXECUTION_PATTERNS, *STRONG_IMPLEMENTATION_PATTERNS, *IMPLEMENTATION_REQUEST_PATTERNS)
    )
    is_comparison_question = (
        any(cue in normalized for cue in COMPARISON_CUES)
        and any(mark in normalized for mark in ("?", "？", "吗", "么", "是否", "要不要"))
        and not explicit_implementation
    )
    if is_comparison_question:
        return False
    if any(pattern.search(normalized) for pattern in EXPLICIT_EXECUTION_PATTERNS):
        return True
    if any(pattern.search(normalized) for pattern in DIRECT_EXECUTION_REQUEST_PATTERNS):
        return True
    if any(pattern.search(normalized) for pattern in STRONG_IMPLEMENTATION_PATTERNS):
        return True
    if any(pattern.search(normalized) for pattern in IMPLEMENTATION_REQUEST_PATTERNS):
        return True
    return False


def detect_high_risk_domains(
    text: str,
    context: Sequence[Mapping[str, str]] | None = None,
) -> list[str]:
    combined = "\n".join(
        [text, *(item.get("text", "") for item in context or () if isinstance(item.get("text"), str))]
    )
    normalized = combined.casefold()
    domains = [
        domain
        for domain, markers in HIGH_RISK_MARKERS.items()
        if any(marker.casefold() in normalized for marker in markers)
    ]

    comma_decimal = re.search(r"\d+,\d+\s*(?:mg|ml|g|kg|%|元|美元|eur|usd|m[a-z/]+)?", normalized)
    dot_decimal = re.search(r"\d+\.\d+\s*(?:mg|ml|g|kg|%|元|美元|eur|usd|m[a-z/]+)?", normalized)
    ambiguous_date = re.search(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", normalized)
    locale_terms = ("地区格式", "地区设置", "小数点", "千位分隔", "日期格式", "locale", "本地格式")
    parsing_terms = (*LOCALE_PARSING_CUES, "格式转换", "数值字段", "解析函数")
    if (
        (comma_decimal and dot_decimal)
        or ambiguous_date
        or (any(cue in normalized for cue in locale_terms) and any(cue in normalized for cue in parsing_terms))
    ):
        domains.append("locale_sensitive_parsing")

    return sorted(set(domains))


def explicit_choice_question_reason(
    text: str,
    *,
    parent_request_text: str | None = None,
    suggested_route: str | None = None,
) -> str | None:
    request = parent_request_text or text
    if not is_implementation_request(request, suggested_route):
        return None
    has_alternatives = bool(CHOICE_ALTERNATIVE_PATTERN.search(request))
    has_direct_choice_cue = any(cue in request for cue in ("二选一", "选哪个", "选哪一个", "选择哪一种", "选择哪一个"))
    has_question_form = any(mark in request for mark in QUESTION_MARKS) or any(
        cue in request for cue in ("哪个", "哪种", "要不要", "是否选择")
    )
    if (has_alternatives and has_question_form) or has_direct_choice_cue:
        return "explicit_key_choice_question"
    return None


def existing_project_check_targets(text: str, suggested_route: str | None = None) -> list[str]:
    if not is_implementation_request(text, suggested_route):
        return []
    normalized = text.casefold()
    existing_cues = (
        "现有", "目前", "当前", "沿用", "旧版流程", "旧版系统", "旧版接口", "旧版服务", "存量", "迁移", "保持原", "不改变现有",
        "按项目惯例", "按当前约定", "遵循现有", "当前项目约定", "已有实现",
    )
    if not any(cue in normalized for cue in existing_cues):
        return []

    targets = ["相关模块的现有实现与配置", "相关文档、API/数据约定", "覆盖该行为的测试"]
    if any(cue in normalized for cue in ("迁移", "存量", "旧版")):
        targets.insert(0, "迁移脚本、历史数据处理和兼容性测试")
    if any(cue in normalized for cue in ("接口", "openapi", "api")):
        targets.insert(0, "接口定义、生成器配置和 schema")
    if any(cue in normalized for cue in ("队列", "暂停", "恢复", "状态")):
        targets.insert(0, "队列状态模型、持久化路径和恢复逻辑")
    return list(dict.fromkeys(targets))


def critical_missing_spec_override_reason(
    text: str,
    high_risk_domains: Sequence[str],
    *,
    suggested_route: str | None = None,
    parent_request_text: str | None = None,
) -> str | None:
    request = parent_request_text or text
    normalized = request.casefold()
    if not is_implementation_request(request, suggested_route):
        return None

    if "payment" in high_risk_domains and any(cue in normalized for cue in ("账户换绑", "收款账户", "银行账户换绑")):
        has_verification_policy = any(
            cue in normalized for cue in ("双人复核", "二次验证", "身份核验", "人工审核", "审批", "旧账户验证", "验证旧账户")
        )
        if not has_verification_policy:
            return "payment_account_change_controls_missing"

    if "rate_limiting" in high_risk_domains and any(cue in normalized for cue in ("限流", "发送限制", "请求限制", "频率限制")):
        has_count = bool(re.search(r"\d+\s*(?:次|封|条|个请求|请求)", normalized))
        has_window = bool(re.search(r"(?:每|/\s*)\s*\d*\s*(?:秒|分钟|小时|天)", normalized))
        if not has_count or not has_window:
            return "rate_limit_threshold_or_window_missing"

    if "locale_sensitive_parsing" in high_risk_domains:
        ambiguous_decimal = bool(
            re.search(r"\d+,\d+", normalized)
            and re.search(r"\d+\.\d+", normalized)
        )
        ambiguous_date = bool(re.search(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", normalized))
        has_explicit_locale = any(cue in normalized for cue in ("locale", "地区设置为", "明确格式为", "日期格式为"))
        if (ambiguous_decimal or ambiguous_date) and not has_explicit_locale:
            return "locale_sensitive_value_format_ambiguous"

    if any(cue in normalized for cue in ("校准", "校准证书")) and any(cue in normalized for cue in ("提醒", "通知")):
        requires_repeat = any(cue in normalized for cue in ("过期后", "继续提醒", "持续提醒"))
        has_cadence = any(cue in normalized for cue in ("每天", "每周", "每隔", "间隔", "频率")) or bool(
            re.search(r"每\s*\d+\s*(?:天|周|小时|分钟)", normalized)
        )
        if requires_repeat and not has_cadence:
            return "reminder_cadence_missing"

    if any(cue in normalized for cue in ("离线编辑", "协作白板", "多人同时编辑", "同时修改")) and any(
        cue in normalized for cue in ("合并", "冲突")
    ):
        has_conflict_policy = any(
            cue in normalized
            for cue in ("最后写入", "版本优先", "人工选择", "冲突时", "保留双方", "合并策略", "冲突规则")
        )
        if not has_conflict_policy:
            return "concurrent_edit_conflict_policy_missing"

    if "permission" in high_risk_domains and any(cue in normalized for cue in ("合同审阅", "合同历史", "合同修订")):
        asks_unset_access = any(cue in normalized for cue in ("谁能查看", "哪些人能看", "查看历史"))
        asks_unset_retention = any(cue in normalized for cue in ("保留多久", "保存多久", "留存多久"))
        has_access_rule = any(cue in normalized for cue in ("只有法务", "仅限法务", "仅限管理员", "合同管理员"))
        has_retention_value = bool(re.search(r"\d+\s*(?:年|个月|月|天)", normalized))
        if (asks_unset_access and not has_access_rule) or (asks_unset_retention and not has_retention_value):
            return "contract_history_access_or_retention_policy_missing"

    if "permission" in high_risk_domains and any(cue in normalized for cue in ("外部审计", "审计顾问")):
        if any(cue in normalized for cue in ("客户支持附件", "客户资料", "客户数据")) and any(
            cue in normalized for cue in ("相关材料", "有关的材料", "相关附件")
        ):
            return "external_auditor_scope_mapping_missing"

    return None


def unresolved_policy_parameter_override_reason(
    text: str,
    *,
    suggested_route: str | None = None,
    parent_request_text: str | None = None,
) -> str | None:
    """Catch unresolved behavioral choices before an implementation cue can force Codex."""
    request = parent_request_text or text
    if not is_implementation_request(request, suggested_route):
        return None

    normalized = request.casefold()
    if any(term in normalized for term in UNRESOLVED_POLICY_TERMS):
        return "unresolved_policy_parameter_before_implementation"

    # Several open questions in one implementation request usually indicate that
    # core behavior is still being chosen. A single capability question such as
    # “Can you implement this?” does not meet this rule.
    question_clauses = re.split(r"[，,。；;\n]", normalized)
    open_parameter_questions = sum(
        len(POLICY_QUESTION_PATTERN.findall(clause))
        for clause in question_clauses
        if clause.strip()
    )
    if open_parameter_questions >= 2:
        return "unresolved_policy_parameter_before_implementation"
    return None


def safe_default_for_request(
    text: str,
    high_risk_domains: Sequence[str],
) -> dict[str, str] | None:
    normalized = text.casefold()
    user_authorized = any(cue in normalized for cue in EXPLICIT_DEFAULT_AUTHORITY_CUES) or bool(
        re.search(r"按(?:常见|平台|后台|跨平台).{0,12}(?:样式|习惯|做法|规范).{0,12}(?:处理|选择|选一个|采用)?", normalized)
    )
    # User authorization cannot make an otherwise high-risk default safe.
    if high_risk_domains:
        return None

    if user_authorized and any(cue in normalized for cue in ("空列表", "空状态", "帮助图标")):
        return {
            "value": "采用轻量空状态提示：帮助图标配一句简短引导文案；优先沿用相邻管理页的样式，找不到既有样式时使用常规次级文字样式和一致间距。",
            "reason": "用户明确授权按常见后台样式决定；该视觉细节可逆，且不改变数据、权限或业务政策。",
        }

    if user_authorized and any(cue in normalized for cue in ("快捷键", "键位")) and any(
        cue in normalized for cue in ("侧栏", "边栏")
    ):
        return {
            "value": "侧栏切换使用 Windows/Linux 的 Ctrl+B 和 macOS 的 Command+B。",
            "reason": "用户明确授权按常见跨平台习惯选择；实施前检查该快捷键是否与现有编辑操作冲突。",
        }

    if user_authorized and any(cue in normalized for cue in ("toast", "提示时长", "成功提示", "非阻断提示")):
        return {
            "value": "采用非阻断提示，显示 3 秒后自动关闭，并提供手动关闭；关闭提示不撤销已完成的业务操作。",
            "reason": "用户明确授权选择常见做法；提示时长和关闭方式可逆，且不会改变业务结果。",
        }

    if user_authorized and any(cue in normalized for cue in ("默认顺序", "默认排序", "默认顺序", "排序")):
        return {
            "value": "首次打开时按名称升序；用户可随时切换排序，且排序不改动源数据。",
            "reason": "用户明确授权选择低风险默认；该排序可逆，只影响显示顺序。",
        }

    if user_authorized and any(cue in normalized for cue in ("seed", "随机种子", "测试颜色", "测试样本")):
        return {
            "value": "未提供 seed 时使用固定值 42，并在结果中记录最终 seed；同一 seed 保持可复现。",
            "reason": "用户明确授权选择测试默认；固定 seed 仅影响本地测试样本，可随时更换，不改变业务数据。",
        }

    if user_authorized and any(cue in normalized for cue in ("样式", "颜色", "间距", "字号", "圆角", "图标", "布局")):
        return {
            "value": "优先沿用同类界面的样式 token；找不到既有样式时使用中性次级样式、8 px 间距和 4 px 圆角，并保持可由主题配置覆盖。",
            "reason": "用户明确授权选择低风险展示细节；默认只影响可逆的视觉呈现，不改变数据或业务政策。",
        }

    if any(cue in normalized for cue in ("完成的事项", "完成的任务", "已完成事项")) and any(
        cue in normalized for cue in ("离开主列表", "从主列表移出", "不显示在主列表")
    ) and not any(cue in normalized for cue in ("删除", "归档", "保留历史", "保留搜索", "还是", "或者")):
        return {
            "value": "将完成项归档并从主列表隐藏，保留可搜索的历史记录，不做永久删除。",
            "reason": "请求没有提出删除或归档选项；归档是可逆做法，保留已有记录并满足从主列表移出的要求。",
        }

    if any(cue in normalized for cue in ("同分", "平分", "排序相同")) and any(cue in normalized for cue in ("搜索", "排序", "结果列表")):
        return {
            "value": "用稳定且不可变的记录 ID 升序作为次级排序键。",
            "reason": "该次级键只确定并列项顺序，不改变匹配结果，并能保证结果稳定。",
        }

    if any(cue in normalized for cue in ("半成品", "不留下不完整", "导出失败")) and any(
        cue in normalized for cue in ("文件", "导出")
    ):
        return {
            "value": "先写入同目录临时文件，成功后原子替换目标；失败时保留旧文件并清理临时文件。",
            "reason": "该做法避免不完整内容覆盖已存在的完整文件。",
        }

    return None


def _apply_route_override(
    action: str,
    proposed_action: str,
    rule_name: str,
    high_risk_domains: Sequence[str],
) -> tuple[str, dict[str, object]]:
    event: dict[str, object] = {
        "rule_name": rule_name,
        "before": action,
        "after": action,
        "proposed_action": proposed_action,
        "applied": True,
    }
    if proposed_action == "decide" and high_risk_domains:
        event["applied"] = False
        event["blocked_reason"] = "high_risk_override_cannot_route_to_decide"
        return action, event
    event["after"] = proposed_action
    return proposed_action, event


def apply_routing_policy(
    suggested_route: str,
    text: str,
    context: Sequence[Mapping[str, str]] | None = None,
    *,
    parent_request_text: str | None = None,
    initial_override_reason: str | None = None,
) -> dict[str, object]:
    """Apply deterministic policy to a model argmax and return an auditable route."""
    parent_text = parent_request_text or text
    high_risk_domains = detect_high_risk_domains(parent_text, context)
    action = suggested_route
    reason = "highest_model_score"
    policy_override: str | None = None
    override_log: list[dict[str, object]] = []
    implementation_request = is_implementation_request(parent_text, suggested_route)
    declared_default: dict[str, str] | None = None
    check_first_targets: list[str] = []

    if initial_override_reason:
        action, event = _apply_route_override(
            action, "clarify", initial_override_reason, high_risk_domains
        )
        override_log.append(event)
        policy_override = initial_override_reason
        reason = initial_override_reason if event["applied"] else str(event["blocked_reason"])
    else:
        clarification_rules = [
            clarification_override_reason(text, context),
            referent_override_reason(text, context, parent_request_text=parent_text),
            explicit_choice_question_reason(
                text,
                parent_request_text=parent_text,
                suggested_route=suggested_route,
            ),
        ]

        rule_name = next((item for item in clarification_rules if item), None)
        if rule_name:
            action, event = _apply_route_override(action, "clarify", rule_name, high_risk_domains)
            override_log.append(event)
            policy_override = rule_name
            reason = rule_name if event["applied"] else str(event["blocked_reason"])
        else:
            # Resolve missing critical choices before any implementation override
            # or project-convention route can turn an unresolved request into work.
            missing_spec_rule = critical_missing_spec_override_reason(
                text,
                high_risk_domains,
                suggested_route=suggested_route,
                parent_request_text=parent_text,
            ) or unresolved_policy_parameter_override_reason(
                text,
                suggested_route=suggested_route,
                parent_request_text=parent_text,
            )
            if missing_spec_rule:
                action, event = _apply_route_override(
                    action, "clarify", missing_spec_rule, high_risk_domains
                )
                override_log.append(event)
                policy_override = missing_spec_rule
                reason = missing_spec_rule if event["applied"] else str(event["blocked_reason"])
            else:
                check_first_targets = existing_project_check_targets(parent_text, suggested_route)
                if check_first_targets:
                    action, event = _apply_route_override(
                        action, "codex+check_first", "existing_project_convention_check", high_risk_domains
                    )
                    override_log.append(event)
                    policy_override = "existing_project_convention_check"
                    reason = "existing_project_convention_check"
                else:
                    intent_override = intent_override_reason(text, context)
                    if intent_override is not None:
                        proposed_action, rule_name = intent_override
                        action, event = _apply_route_override(
                            action, proposed_action, rule_name, high_risk_domains
                        )
                        override_log.append(event)
                        policy_override = rule_name
                        reason = rule_name if event["applied"] else str(event["blocked_reason"])
                    elif implementation_request and action != "codex":
                        action, event = _apply_route_override(
                            action, "codex", "explicit_implementation_request", high_risk_domains
                        )
                        override_log.append(event)
                        policy_override = "explicit_implementation_request"
                        reason = "explicit_implementation_request" if event["applied"] else str(event["blocked_reason"])

                    if action == "codex":
                        declared_default = safe_default_for_request(parent_text, high_risk_domains)
                        if declared_default:
                            action, event = _apply_route_override(
                                action, "codex+declare_default", "safe_default_declared", high_risk_domains
                            )
                            override_log.append(event)
                            policy_override = "safe_default_declared"
                            reason = "safe_default_declared"

    return {
        "action": action,
        "reason": reason,
        "policy_override": policy_override,
        "override_log": override_log,
        "high_risk_domains": high_risk_domains,
        "declared_default": declared_default,
        "check_first_targets": check_first_targets,
    }


ACTION_PRIORITY = {
    "decide": 0,
    "codex": 1,
    "codex+declare_default": 2,
    "codex+check_first": 3,
    "clarify": 4,
}


def aggregate_policy_results(
    whole_result: Mapping[str, object],
    clause_results: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    """Aggregate a whole-request policy result and its clause-level results."""
    results: list[Mapping[str, object]] = [whole_result, *clause_results]
    action = max(
        (str(result.get("action", "clarify")) for result in results),
        key=lambda route: ACTION_PRIORITY.get(route, ACTION_PRIORITY["clarify"]),
    )

    override_log: list[dict[str, object]] = []
    for scope_index, result in enumerate(results):
        events = result.get("override_log", ())
        if not isinstance(events, Sequence) or isinstance(events, (str, bytes)):
            continue
        scope = "whole_request" if scope_index == 0 else f"clause_{scope_index}"
        for event in events:
            if isinstance(event, Mapping):
                override_log.append({**event, "scope": scope})

    whole_action = str(whole_result.get("action", "clarify"))
    if action != whole_action:
        override_log.append(
            {
                "rule_name": "multi_clause_aggregate",
                "before": whole_action,
                "after": action,
                "proposed_action": action,
                "applied": True,
                "scope": "request_aggregate",
            }
        )

    high_risk_domains = sorted(
        {
            str(domain)
            for result in results
            for domain in result.get("high_risk_domains", ())
        }
    )
    declared_defaults: list[dict[str, str]] = []
    seen_defaults: set[tuple[str, str]] = set()
    for scope_index, result in enumerate(results):
        default = result.get("declared_default")
        if isinstance(default, Mapping):
            value = str(default.get("value", ""))
            reason_text = str(default.get("reason", ""))
            if (value, reason_text) not in seen_defaults:
                declared_defaults.append(
                    {
                        "value": value,
                        "reason": reason_text,
                        "scope": "whole_request" if scope_index == 0 else f"clause_{scope_index}",
                    }
                )
                seen_defaults.add((value, reason_text))

    check_first_targets = list(
        dict.fromkeys(
            str(target)
            for result in results
            for target in result.get("check_first_targets", ())
        )
    )
    policy_override = (
        "multi_clause_aggregate"
        if action != whole_action
        else whole_result.get("policy_override")
    )
    reason = "multi_clause_aggregate" if action != whole_action else whole_result.get("reason", "highest_model_score")

    return {
        "action": action,
        "reason": reason,
        "policy_override": policy_override,
        "override_log": override_log,
        "high_risk_domains": high_risk_domains,
        "declared_defaults": declared_defaults,
        "check_first_targets": check_first_targets,
    }


