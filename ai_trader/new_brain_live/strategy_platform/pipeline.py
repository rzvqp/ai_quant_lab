"""The orchestrating evaluation cycle (AI Trader New Brain Architecture mandate, section 3): MarketState
-> Strategy Catalog -> Strategy Router -> Strategy Evaluation -> EV/Decision Engine -> Risk Engine ->
Execution Adapter -> Shadow Ledger. `NO VALID STRATEGY` or `NO VALID EDGE` -> `NO_TRADE`, a first-class
outcome, never an error, fallback, or fabricated trade (section 26, fail-closed).

**Real `TRADE` is structurally impossible in this delivery.** `BROKER_ORDER_SUBMISSION` stays globally
DISABLED (section 19); `RiskExecutionDeps.gate` always raises before any real order. `final_decision`
therefore always resolves to `"NO_TRADE"` here -- honestly reflecting reality, not fabricated, ready to
flip the moment (and only if) a future, explicit, CEO-authorized gate ever changes that.

**Conflict policy (section 16)**: when more than one hypothesis reaches `TRADE_DECISION` on the SAME
MarketState, this pipeline does NOT invent a profit-maximizing arbitration rule -- it refuses ALL of
them (`CONFLICT_POLICY_BLOCK`), explicitly `POLICY_PENDING_VALIDATED_STRATEGY_PORTFOLIO`, until a real,
ratified conflict-resolution rule exists."""

from __future__ import annotations

import dataclasses

from ai_trader.new_brain_live.market_state import MARKET_STATE_SCHEMA_VERSION, MarketState, market_state_identity
from ai_trader.new_brain_live.strategy_platform import reason_codes as rc
from ai_trader.new_brain_live.strategy_platform.catalog import StrategyCatalog
from ai_trader.new_brain_live.strategy_platform.dedup import already_processed
from ai_trader.new_brain_live.strategy_platform.ev_engine import (
    MOCK_EV_ENGINE_VERSION, TRADE_DECISION, EVDecision, EVDecisionEngine,
)
from ai_trader.new_brain_live.strategy_platform.risk_execution_adapter import RiskExecutionDeps, evaluate_and_attempt
from ai_trader.new_brain_live.strategy_platform.router import RouterOutcome, StrategyRouter
from ai_trader.new_brain_live.strategy_platform.shadow_ledger import ShadowLedger, ShadowLedgerRecord, StrategyPlatformFingerprints

POLICY_PENDING_VALIDATED_STRATEGY_PORTFOLIO = "POLICY_PENDING_VALIDATED_STRATEGY_PORTFOLIO"

CATALOG_VERSION = "strategy-catalog-v1"
#: Fallback ONLY for the no-EV-engine-yet code paths below (an invalid MarketState, dedup replay, empty
#: catalog, no eligible strategy, no hypotheses) -- these never touch `ev_engine` at all, so there is no
#: "actual engine" to name; MOCK_EV_ENGINE_VERSION is a reasonable, disclosed placeholder for a field that
#: genuinely doesn't apply to that record. Once an `EVDecisionEngine` IS invoked (a cycle that reaches
#: `ev_engine.decide`), its own `engine_version` is used instead -- see `_fingerprints`'s `ev_engine` arg.
EV_ENGINE_VERSION = MOCK_EV_ENGINE_VERSION
RISK_ENGINE_VERSION = "risk_manager_live-v1"
EXECUTION_ADAPTER_VERSION = "execution_shadow-v1"


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class CycleResult:
    record: ShadowLedgerRecord
    router_outcome: RouterOutcome | None
    ev_decisions: tuple[EVDecision, ...]
    duplicate: bool


def _fingerprints(market_state: MarketState, *, ev_engine_version: str = EV_ENGINE_VERSION) -> StrategyPlatformFingerprints:
    """`ev_engine_version` defaults to the Mock placeholder for the no-EV-engine-invoked code paths (see
    the module constant's own comment); every call site AFTER `ev_engine.decide(...)` has actually run
    passes the real engine's own `ev_engine.engine_version` explicitly (mandate VE-AI-TRADER-GENERIC-EV-
    AUTHORITY-001 section 10 -- the ledger must never claim an engine other than the one that really ran).
    """
    return StrategyPlatformFingerprints(
        market_intelligence_fingerprint=market_state.n1_output_fp,
        market_state_schema_version=MARKET_STATE_SCHEMA_VERSION, catalog_version=CATALOG_VERSION,
        ev_engine_version=ev_engine_version, risk_engine_version=RISK_ENGINE_VERSION,
        execution_adapter_version=EXECUTION_ADAPTER_VERSION,
    )


def _no_trade_record(market_state: MarketState, *, reason: str) -> ShadowLedgerRecord:
    return ShadowLedgerRecord(
        market_timestamp=market_state.market_timestamp, market_state_identity=market_state_identity(market_state),
        eligible_strategy_ids=(), ineligible=(), hypothesis_dedup_keys=(), ev_decisions=(),
        final_decision="NO_TRADE", final_reason_codes=(reason,), hypothetical_order_intent=None,
        broker_submission_state="DISABLED_NEVER_REACHED", fingerprints=_fingerprints(market_state),
    )


def run_cycle(
    *, market_state: MarketState, catalog: StrategyCatalog, ev_engine: EVDecisionEngine,
    risk_execution_deps: RiskExecutionDeps, ledger: ShadowLedger, router: StrategyRouter | None = None,
    tower_context: object | None = None,
) -> CycleResult:
    ms_id = market_state_identity(market_state)

    # Fail-closed (section 26): an invalid MarketState never reaches the Router at all.
    if market_state.atr is None or market_state.entry_price is None:
        record = _no_trade_record(market_state, reason=rc.MARKET_STATE_INVALID)
        ledger.record(record)
        return CycleResult(record=record, router_outcome=None, ev_decisions=(), duplicate=False)

    # Restart-safe dedup (section 23): re-processing the same MarketState never re-records or
    # re-attempts execution -- the existing ledger entry IS the answer.
    if already_processed(ledger, market_state_identity=ms_id):
        existing = next(e for e in ledger.entries if e.market_state_identity == ms_id)
        return CycleResult(record=existing, router_outcome=None, ev_decisions=(), duplicate=True)

    if not catalog.enabled_entries():
        record = _no_trade_record(market_state, reason=rc.NO_VALIDATED_STRATEGY)
        ledger.record(record)
        return CycleResult(record=record, router_outcome=None, ev_decisions=(), duplicate=False)

    active_router = router if router is not None else StrategyRouter()
    outcome = active_router.route(catalog=catalog, market_state=market_state, tower_context=tower_context)

    if not outcome.eligible:
        record = _no_trade_record(market_state, reason=rc.NO_ELIGIBLE_STRATEGY)
        ledger.record(record)
        return CycleResult(record=record, router_outcome=outcome, ev_decisions=(), duplicate=False)

    ineligible_pairs = tuple((r.entry.strategy_id, r.reason_codes[0]) for r in outcome.ineligible)
    eligible_ids = tuple(r.entry.strategy_id for r in outcome.eligible)

    if not outcome.hypotheses:
        # section 37 "INVALID STRATEGY OUTPUT": a strategy that raised/malformed its own hypothesis is
        # distinguished from an honest NO_SIGNAL -- both fail closed to NO_TRADE, but with a more
        # informative reason when integrity (not just absence of a signal) is the actual cause.
        reason = rc.INTEGRITY_FAILURE if outcome.invalid_output else rc.NO_STRATEGY_SIGNAL
        record = ShadowLedgerRecord(
            market_timestamp=market_state.market_timestamp, market_state_identity=ms_id,
            eligible_strategy_ids=eligible_ids, ineligible=ineligible_pairs, invalid_output=outcome.invalid_output,
            hypothesis_dedup_keys=(), ev_decisions=(), final_decision="NO_TRADE", final_reason_codes=(reason,),
            hypothetical_order_intent=None, broker_submission_state="DISABLED_NEVER_REACHED",
            fingerprints=_fingerprints(market_state),
        )
        ledger.record(record)
        return CycleResult(record=record, router_outcome=outcome, ev_decisions=(), duplicate=False)

    ev_decisions = tuple(ev_engine.decide(h) for h in outcome.hypotheses)
    trade_decisions = tuple(d for d in ev_decisions if d.decision == TRADE_DECISION)
    dedup_keys = tuple("|".join(h.dedup_key) for h in outcome.hypotheses)

    if not trade_decisions:
        record = ShadowLedgerRecord(
            market_timestamp=market_state.market_timestamp, market_state_identity=ms_id,
            eligible_strategy_ids=eligible_ids, ineligible=ineligible_pairs, invalid_output=outcome.invalid_output,
            hypothesis_dedup_keys=dedup_keys,
            ev_decisions=tuple((d.hypothesis.strategy_id, d.decision, d.evidence_fingerprint) for d in ev_decisions),
            final_decision="NO_TRADE", final_reason_codes=(rc.EV_BELOW_THRESHOLD,),
            hypothetical_order_intent=None, broker_submission_state="DISABLED_NEVER_REACHED",
            fingerprints=_fingerprints(market_state, ev_engine_version=ev_engine.engine_version),
        )
        ledger.record(record)
        return CycleResult(record=record, router_outcome=outcome, ev_decisions=ev_decisions, duplicate=False)

    if len(trade_decisions) > 1:
        record = ShadowLedgerRecord(
            market_timestamp=market_state.market_timestamp, market_state_identity=ms_id,
            eligible_strategy_ids=eligible_ids, ineligible=ineligible_pairs, invalid_output=outcome.invalid_output,
            hypothesis_dedup_keys=dedup_keys,
            ev_decisions=tuple((d.hypothesis.strategy_id, d.decision, d.evidence_fingerprint) for d in ev_decisions),
            final_decision="NO_TRADE", final_reason_codes=(rc.CONFLICT_POLICY_BLOCK, POLICY_PENDING_VALIDATED_STRATEGY_PORTFOLIO),
            hypothetical_order_intent=None, broker_submission_state="DISABLED_NEVER_REACHED",
            fingerprints=_fingerprints(market_state, ev_engine_version=ev_engine.engine_version),
        )
        ledger.record(record)
        return CycleResult(record=record, router_outcome=outcome, ev_decisions=ev_decisions, duplicate=False)

    winning = trade_decisions[0]
    h = winning.hypothesis
    order_intent = f"{h.strategy_id}|{h.instrument}|{h.direction.value}|{h.intended_entry}|{h.invalidation}"

    risk_execution_outcome = evaluate_and_attempt(winning, deps=risk_execution_deps)
    if not risk_execution_outcome.risk_decision.approved:
        record = ShadowLedgerRecord(
            market_timestamp=market_state.market_timestamp, market_state_identity=ms_id,
            eligible_strategy_ids=eligible_ids, ineligible=ineligible_pairs, invalid_output=outcome.invalid_output,
            hypothesis_dedup_keys=dedup_keys,
            ev_decisions=tuple((d.hypothesis.strategy_id, d.decision, d.evidence_fingerprint) for d in ev_decisions),
            final_decision="NO_TRADE", final_reason_codes=(rc.RISK_REJECTED,), hypothetical_order_intent=order_intent,
            broker_submission_state="DISABLED_NEVER_REACHED",
            fingerprints=_fingerprints(market_state, ev_engine_version=ev_engine.engine_version),
        )
        ledger.record(record)
        return CycleResult(record=record, router_outcome=outcome, ev_decisions=ev_decisions, duplicate=False)

    shadow_result = risk_execution_outcome.shadow_result
    assert shadow_result is not None  # risk approved -> execution was attempted, by evaluate_and_attempt's own contract
    broker_state = f"BLOCKED_AT_GATE:{shadow_result.reason}" if shadow_result.blocked else "UNEXPECTED_NOT_BLOCKED"
    final_reason = rc.BROKER_DISABLED if shadow_result.blocked else "UNEXPECTED_NOT_BLOCKED"
    record = ShadowLedgerRecord(
        market_timestamp=market_state.market_timestamp, market_state_identity=ms_id,
        eligible_strategy_ids=eligible_ids, ineligible=ineligible_pairs, invalid_output=outcome.invalid_output,
        hypothesis_dedup_keys=dedup_keys,
        ev_decisions=tuple((d.hypothesis.strategy_id, d.decision, d.evidence_fingerprint) for d in ev_decisions),
        final_decision="NO_TRADE", final_reason_codes=(final_reason,), hypothetical_order_intent=order_intent,
        broker_submission_state=broker_state,
        fingerprints=_fingerprints(market_state, ev_engine_version=ev_engine.engine_version),
    )
    ledger.record(record)
    return CycleResult(record=record, router_outcome=outcome, ev_decisions=ev_decisions, duplicate=False)
