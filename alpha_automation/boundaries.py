"""Scientific-boundary guardrail -- pure stdlib.

Alpha's charter forbids it from producing strategy claims, profitability claims, validation
verdicts, or causal claims. This module scans Alpha's machine-readable output for language
that would violate that boundary. A hit is treated by the adapter as a validation failure
(the response is rejected and re-requested), so a boundary breach can never be silently
persisted or frozen.

The list is deliberately conservative -- it targets phrases that clearly assert tradability,
profitability, statistical validation, or causation, not ordinary descriptive market language
(a bare word like "entry" or "stop" is NOT matched; only claim-shaped phrases are).
"""

from __future__ import annotations

import re
from typing import List

# Each entry is a lowercase substring or regex fragment that signals a boundary breach.
FORBIDDEN_PATTERNS: List[str] = [
    # profitability / performance claims
    r"profitab\w*",
    r"\bpnl\b",
    r"sharpe",
    r"\bwin[\s\-]?rate\b",
    r"\bexpectancy\b",
    r"profit factor",
    r"\broi\b",
    r"annualized return",
    # strategy / execution claims
    r"trading strateg\w*",
    r"take[\s\-]?profit",
    r"stop[\s\-]?loss",
    r"risk[\s/\-]?reward",
    r"position siz\w*",
    r"\bbuy signal\b",
    r"\bsell signal\b",
    r"entry rule",
    r"exit rule",
    r"execution rule",
    # validation verdicts (Alpha only produces candidates, never validates)
    r"validated edge",
    r"is validated",
    r"statistically validated",
    r"\bbacktest\w* prov\w*",
    r"proven strateg\w*",
    r"confirmed edge",
    # causal over-claims
    r"proves that",
    r"is caused by",
    r"\bguarantee\w*",
    # Strategy Tester as edge evidence / parameter optimization (TVRE charter, CEO 2026-07-22)
    r"strategy tester",
    r"backtest\w* result\w*",
    r"optimiz\w* (the )?param\w*",
    r"parameter optimiz\w*",
    r"best[\s\-]?performing param\w*",
    r"curve[\s\-]?fit\w*",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in FORBIDDEN_PATTERNS]


def forbidden_language(text: str) -> List[str]:
    """Return the list of forbidden phrases found in `text` (empty list == clean)."""
    if not text:
        return []
    hits: List[str] = []
    for pat in _COMPILED:
        m = pat.search(text)
        if m:
            hits.append(m.group(0))
    return hits


def scan_response(obj: dict) -> List[str]:
    """Scan all free-text fields of an Alpha response for boundary breaches."""
    fields = (
        "summary",
        "observation",
        "why_attracted_attention",
        "why_may_repeat",
        "why_investigate",
        "scope_caveats",
    )
    hits: List[str] = []
    for f in fields:
        v = obj.get(f)
        if isinstance(v, str):
            hits.extend(forbidden_language(v))
    return sorted(set(hits))
