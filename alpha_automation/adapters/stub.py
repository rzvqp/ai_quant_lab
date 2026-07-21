"""Deterministic stub adapter -- for dry-run smoke tests and unit tests.

Given a task it returns a valid, boundary-clean AlphaResponse. The outcome is a deterministic
function of the task_id, weighted so that "no candidate" (NEGATIVE) is by far the most common
result -- matching the real world where most investigations find nothing. Tests can predict the
outcome via `StubAdapter.planned_outcome(task_id)`.

The stub never invents strategy/profit/validation/causal language, so it always passes the
scientific-boundary scan.
"""

from __future__ import annotations

import hashlib

from .base import AlphaAdapter, AlphaContext


def _bucket(task_id: str) -> int:
    return int.from_bytes(hashlib.sha256(task_id.encode("utf-8")).digest()[:4], "big") % 100


class StubAdapter(AlphaAdapter):
    name = "stub"

    def __init__(self, master_seed: int = 0):
        self.master_seed = int(master_seed)

    @staticmethod
    def planned_outcome(task_id: str) -> str:
        b = _bucket(task_id)
        if b < 70:
            return "NEGATIVE"
        if b < 90:
            return "TENTATIVE"
        return "CANDIDATE_PROPOSED"

    def _invoke(self, context: AlphaContext) -> dict:
        tid = context.task_id
        outcome = self.planned_outcome(tid)
        lens = context.perspective.get("lens", "behaviour")
        tf = (context.window or {}).get("timeframe", "H1")

        base_gate = {
            "novel": False,
            "evidence_supported": True,
            "reproducible_or_concrete": True,
            "descriptive_not_causal": True,
            "not_noise": True,
            "not_strategy_or_profit_claim": True,
        }

        if outcome == "NEGATIVE":
            return {
                "task_id": tid,
                "finding_type": "NEGATIVE",
                "summary": f"No distinguishable {lens} effect in the examined {tf} window.",
                "observation": (
                    "Across the sampled window the conditioned subset did not behave "
                    "measurably differently from the ambient distribution. Clean null."),
                "evidence": [{"what": "conditioned vs ambient subsets overlapped", "count": 0}],
                "confidence": "Medium",
                "gate": {**base_gate},
                "scope_caveats": "Single instrument, single window, descriptive scan only.",
            }

        if outcome == "TENTATIVE":
            return {
                "task_id": tid,
                "finding_type": "TENTATIVE",
                "summary": f"Possible weak {lens} regularity in {tf}; not robust enough to freeze.",
                "observation": (
                    "A faint recurring pattern appeared in the sampled window but was not "
                    "consistent across the whole range. Recorded as a tentative observation only."),
                "evidence": [{"what": "pattern present in part of the window", "count": 3}],
                "why_may_repeat": "The regularity aligns with a session boundary, but weakly.",
                "confidence": "Low",
                "gate": {**base_gate, "reproducible_or_concrete": False},
                "scope_caveats": "Not reproducible across the full window; do not over-read.",
            }

        # CANDIDATE_PROPOSED
        return {
            "task_id": tid,
            "finding_type": "CANDIDATE_PROPOSED",
            "summary": f"Recurring descriptive {lens} regularity worth further investigation ({tf}).",
            "observation": (
                "A concrete, repeatable descriptive pattern was observed consistently across the "
                "sampled window. It is described here purely as an observation for the laboratory."),
            "evidence": [
                {"what": "pattern recurred across the sampled window", "count": 12},
                {"what": "absent in the contrasting subset", "count": 0},
            ],
            "why_attracted_attention": "It recurred consistently and stood out from the ambient behaviour.",
            "why_may_repeat": "It coincides with a structural feature of the session, descriptively.",
            "why_investigate": "It is concrete and reproducible enough to justify laboratory attention.",
            "confidence": "Medium",
            "gate": {
                "novel": True,
                "evidence_supported": True,
                "reproducible_or_concrete": True,
                "descriptive_not_causal": True,
                "not_noise": True,
                "not_strategy_or_profit_claim": True,
            },
            "self_reported_related": [],
            "scope_caveats": "Descriptive observation only; not a tradability or performance claim; not yet reviewed.",
        }
