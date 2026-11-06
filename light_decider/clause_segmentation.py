from __future__ import annotations

import re


_SENTENCE_BOUNDARY = re.compile(r"[。！？!?；;\n]+")
# Avoid treating the “并” inside compounds such as “合并规则” as a connector.
_CLAUSE_CONNECTOR = re.compile(
    r"(?=然后|接着|随后|另外|同时|顺便|而且|还要|(?<!合)并(?!行|非|不|发))|(?<=[，,])(?=再)"
)
_EDGE_PUNCTUATION = " \t\r\n,，;；"


def split_request_clauses(text: str) -> list[str]:
    """Split an utterance at strong punctuation and common task-level connectors.

    Commas alone are kept intact because they often introduce conditions,
    examples, or negation that modifies the same request.
    """
    normalized = text.strip()
    if not normalized:
        return []

    clauses: list[str] = []
    for sentence in _SENTENCE_BOUNDARY.split(normalized):
        for candidate in _CLAUSE_CONNECTOR.split(sentence):
            clause = candidate.strip(_EDGE_PUNCTUATION)
            if clause:
                clauses.append(clause)

    # Preserve the original sentence and punctuation when no real split occurred.
    return clauses if len(clauses) > 1 else [normalized]
