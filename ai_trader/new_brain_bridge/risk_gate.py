"""`submit_new_brain_candidate` -- Mandate 2 continuation, section 2 (CEO, 2026-08-14): "Accepta NUMAI
iesirea validata si complet trasabila a N6. Orice lipsa de: event identity, strategy identity,
eligibility, configuration fingerprint, catalog sau version provenance, EV provenance -> NO_TRADE. Nu
fallback." This is the ONLY entrypoint through which a `NewBrainOutcome` may reach the live Risk Manager
(`risk_manager_live.engine.evaluate_trade_proposal`) -- that function itself is NEVER modified (frozen,
reused verbatim, exactly like every other consumer of the `ai_trader/risk_manager/` package).

**Every rejection here is a real, distinct, checked fact about `outcome`'s own identity** -- not a
single opaque "provenance invalid" catch-all:
1. N6 produced no actionable decision (`NO_TRADE`, or no `DecisionRequest` was ever built) -- nothing to
   submit; not a provenance failure, a "there is no candidate" fact.
2. `outcome.provenance` is `None` -- `bridge.py` itself only sets it for `TRADE`/`SHADOW_TRADE_CANDIDATE`.
3. `verify_decision_provenance` itself rejects (wrong `source`, or any of `trace_id`/`catalog_hash`/
   `configuration_fingerprint` empty) -- `ve_brain`'s own single-value allowlist.
4. The provenance's own `trace_id`/`catalog_hash` don't match `outcome.event_identity`'s -- proves the
   provenance object actually BELONGS to this event, not merely that some valid-looking provenance
   exists (a forged/mismatched-but-internally-valid `DecisionProvenance` would pass step 3 alone).
5. The provenance's `configuration_fingerprint` doesn't match what N6 itself returned on `outcome
   .decision` -- proves the provenance describes THIS decision, not a stale or substituted one.

Every one of these produces a `LiveRiskDecision(approved=False, ...)` with an explicit, distinct reason
code -- never a silent skip, never a fallback to any other decision source."""

from __future__ import annotations

from ai_trader.mandate2_readiness.decision_provenance import UntrustedDecisionSourceError, verify_decision_provenance
from ai_trader.new_brain_bridge.bridge import NewBrainOutcome
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.types import PortfolioState, RiskContext
from ai_trader.risk_manager_live.engine import evaluate_trade_proposal
from ai_trader.risk_manager_live.types import AccountState, InstrumentSpecification, LiveRiskDecision, TradeProposal
from ai_trader.signal_engine.types import Direction

NO_ACTIONABLE_N6_DECISION = "NO_ACTIONABLE_N6_DECISION"
MISSING_DECISION_PROVENANCE = "MISSING_DECISION_PROVENANCE"
UNTRUSTED_DECISION_SOURCE = "UNTRUSTED_DECISION_SOURCE"
PROVENANCE_EVENT_IDENTITY_MISMATCH = "PROVENANCE_EVENT_IDENTITY_MISMATCH"
PROVENANCE_DECISION_FINGERPRINT_MISMATCH = "PROVENANCE_DECISION_FINGERPRINT_MISMATCH"


def _deny(reason_code: str) -> LiveRiskDecision:
    return LiveRiskDecision(
        approved=False, reason_codes=(reason_code,), requested_risk=None, approved_risk=None,
        calculated_volume=None, monetary_risk=None, stop_distance=None, margin_estimate=None,
        warnings=(), calculation_trace=(),
    )


def submit_new_brain_candidate(
    outcome: NewBrainOutcome, *, account: AccountState, portfolio: PortfolioState,
    instrument: InstrumentSpecification, risk_context: RiskContext, risk_config: RiskConfig | None = None,
) -> LiveRiskDecision:
    """The provenance-gated bridge from a `NewBrainOutcome` to the live Risk Manager. Approval here
    does NOT mean a trade executes -- it means Risk Manager's own sizing/limits/guards evaluation may
    now run; `execution_shadow.py` still sits between any approval and the broker."""
    decision = outcome.decision
    if decision is None or decision.decision not in ("TRADE", "SHADOW_TRADE_CANDIDATE"):
        return _deny(NO_ACTIONABLE_N6_DECISION)

    if outcome.provenance is None:
        return _deny(MISSING_DECISION_PROVENANCE)

    try:
        verify_decision_provenance(outcome.provenance)
    except UntrustedDecisionSourceError:
        return _deny(UNTRUSTED_DECISION_SOURCE)

    if (outcome.provenance.trace_id != outcome.event_identity.trace_id
            or outcome.provenance.catalog_hash != outcome.event_identity.catalog_hash):
        return _deny(PROVENANCE_EVENT_IDENTITY_MISMATCH)

    if outcome.provenance.configuration_fingerprint != decision.configuration_fingerprint:
        return _deny(PROVENANCE_DECISION_FINGERPRINT_MISMATCH)

    if outcome.entry_price is None or outcome.stop_price is None:
        return _deny(NO_ACTIONABLE_N6_DECISION)  # geometry absent -- structurally shouldn't happen if
        # `decision` is TRADE/SHADOW_TRADE_CANDIDATE (bridge.py always sets both together), but this
        # function never assumes that invariant holds without checking it itself.

    proposal = TradeProposal(
        proposal_id=outcome.event_identity.trace_id, correlation_id=outcome.event_identity.trace_id,
        strategy_id=outcome.strategy_id, symbol=outcome.event_identity.symbol, direction=Direction.LONG,
        entry=outcome.entry_price, stop=outcome.stop_price, target=outcome.target_price,
        as_of=outcome.event_identity.market_timestamp, confidence_quality=None,
    )
    return evaluate_trade_proposal(proposal, account, portfolio, instrument, risk_context, risk_config)
