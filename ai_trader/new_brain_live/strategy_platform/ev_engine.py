"""EV / Decision Engine (AI Trader New Brain Architecture mandate, section 15). Consumes zero, one, or
multiple `TradeHypothesis`, produces `TRADE_DECISION` or `NO_TRADE` per hypothesis, based only on
ratified decision rules -- never an ad-hoc ranking formula invented in this mandate.

**The real, disclosed mismatch (section 15's own explicit instruction: report a mismatch rather than
inventing around it)**: the only ratified EV/decision authority in this repository today is
`ve_brain.decide_n6`, and it resolves every candidate against its own internal, sealed catalog of
exactly 4 strategies (`ve_brain.n6._SEALED_CATALOG`) -- verified, adversarially, to reject ANY other
`strategy_id` with `UNKNOWN_STRATEGY` regardless of eligibility/N3/N4/probability_inputs
(`INTEGRATION_BLOCKED_VE_BRAIN_STRATEGY_CATALOG.md`, `ai-trader-three-strategies` branch, 2026-08-18).
A real, ratified `EVDecisionEngine` implementation for strategies admitted through THIS catalog (i.e.
anything other than the 4 pre-existing canonical strategies) is therefore BLOCKED pending either a new
`ve_brain` release that accepts external strategies, or a separate, explicitly CEO/Statistician/Red-Team
-ratified decision-rule authority for this new catalog. This is reported, not silently routed around.

**What ships today**: `MockEVDecisionEngine` -- a deterministic, explicitly-labeled, engineering-only
pass-through used SOLELY to test the Catalog/Router/EV/Risk/Execution/Shadow-Ledger pipeline mechanics
with `MOCK_TEST_ONLY` strategies (section 11). It computes no real expected value, ranks nothing, and
must never be reachable by anything other than a `MOCK_TEST_ONLY` catalog entry (enforced by
`pipeline.py`, not merely this module)."""

from __future__ import annotations

import dataclasses
from typing import Protocol

from ai_trader.new_brain_live.strategy_platform import reason_codes as rc
from ai_trader.new_brain_live.strategy_platform.trade_hypothesis import TradeHypothesis

TRADE_DECISION = "TRADE_DECISION"
NO_TRADE = "NO_TRADE"


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class EVDecision:
    hypothesis: TradeHypothesis
    decision: str  # TRADE_DECISION | NO_TRADE
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.decision not in (TRADE_DECISION, NO_TRADE):
            raise ValueError(f"EVDecision.decision must be TRADE_DECISION or NO_TRADE, got {self.decision!r}")
        if self.decision == NO_TRADE and not self.reason_codes:
            raise ValueError("EVDecision: NO_TRADE must carry at least one reason code")


class EVDecisionEngine(Protocol):
    def decide(self, hypothesis: TradeHypothesis) -> EVDecision:
        ...


class MockEVDecisionEngine:
    """Deterministic, test-only. Reads a single, explicitly-named key from the hypothesis's own
    `expected_edge` dict (`"mock_decision"`, one of `"TRADE"`/`"NO_TRADE"`) -- NOT a computed edge, NOT
    a ranking, a plain labeled echo so mock strategies can drive both branches of the pipeline
    deterministically for testing. Missing or any other value fails closed to NO_TRADE."""

    def decide(self, hypothesis: TradeHypothesis) -> EVDecision:
        edge = hypothesis.expected_edge or {}
        mock_decision = edge.get("mock_decision")
        if mock_decision == "TRADE":
            return EVDecision(hypothesis=hypothesis, decision=TRADE_DECISION, reason_codes=("MOCK_TRADE_FIXTURE",))
        return EVDecision(hypothesis=hypothesis, decision=NO_TRADE, reason_codes=(rc.EV_BELOW_THRESHOLD,))
