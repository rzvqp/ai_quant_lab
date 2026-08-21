"""S5 canonical onboarding integration -- mandate `AI-TRADER-S5-CANONICAL-ONBOARDING-001`, sections 5-18.

Generic fail-closed coverage (wrong fingerprint/version/status, NaN/inf, expired hypothesis, missing
ve_brain, mock/real ambiguity, etc.) is ALREADY exhaustively proven, generically, in
`test_real_ev_engine.py` (section 14 of the prior mandate) -- this file does not re-derive that; it
proves S5's OWN real identity flows correctly through that already-proven machinery, plus what is
S5-specific: catalog admission with S5's real provenance, the honest `MISSING_PROBABILITY_INPUTS`
terminal state (see `s5_opening_range_breakout.py`'s own docstring for why), restart/dedup for S5
specifically, and legacy-path isolation."""

from __future__ import annotations

import dataclasses
from pathlib import Path

from ai_trader.new_brain_live.strategy_platform import pipeline
from ai_trader.new_brain_live.strategy_platform import reason_codes as rc
from ai_trader.new_brain_live.strategy_platform.catalog import CatalogEntry, StrategyCatalog, StrategyStatus
from ai_trader.new_brain_live.strategy_platform.ev_engine import NO_TRADE
from ai_trader.new_brain_live.strategy_platform.real_ev_engine import REAL_EV_ENGINE_VERSION, CostModel, RealEVDecisionEngine
from ai_trader.new_brain_live.strategy_platform.risk_execution_adapter import RiskExecutionDeps, evaluate_and_attempt
from ai_trader.new_brain_live.strategy_platform.router import StrategyRouter
from ai_trader.new_brain_live.strategy_platform.s5_opening_range_breakout import (
    CONFIG_FINGERPRINT,
    ENTRY_WINDOW_FIRST_BIS,
    STRATEGY_ID,
    STRATEGY_VERSION,
    S5OpeningRangeBreakoutLong,
    catalog_entry_for_s5,
)
from ai_trader.new_brain_live.strategy_platform.shadow_ledger import ShadowLedger
from ai_trader.new_brain_live.strategy_platform.tests._fixtures import make_risk_execution_deps
from ai_trader.new_brain_live.strategy_platform.tests.test_s5_opening_range_breakout import (
    _evaluation_input,
    _fixture,
    _session_bar,
)
from ai_trader.persistent_state.store import SqliteStateStore

_COST = CostModel(cost_model_id="s5-onboarding-test-cost-v1", full_spread_price=0.05, entry_slippage_price=0.02, exit_slippage_price=0.02)


def _ledger(tmp_path: Path, name: str = "s5_ledger.db") -> tuple[ShadowLedger, SqliteStateStore]:
    store = SqliteStateStore(tmp_path / name)
    return ShadowLedger(store), store


def _deps() -> RiskExecutionDeps:
    return RiskExecutionDeps(**make_risk_execution_deps())  # type: ignore[arg-type]


def _s5_breakout_fixture() -> tuple[S5OpeningRangeBreakoutLong, object]:
    breakout_bar = _session_bar(ENTRY_WINDOW_FIRST_BIS + 1, close=2052.0)
    strategy, market_state = _fixture(extra_bars=[breakout_bar])
    return strategy, market_state


# ═══ 1 — catalog admission with real provenance ═══

def test_s5_catalog_entry_admits_with_real_provenance() -> None:
    strategy = S5OpeningRangeBreakoutLong()
    entry = catalog_entry_for_s5(strategy)
    catalog = StrategyCatalog(entries=(entry,))
    assert catalog.lookup(STRATEGY_ID, STRATEGY_VERSION) is entry
    assert entry.status is StrategyStatus.VALIDATED


# ═══ 2 — real EV authority reached, never mock (section 8) ═══

def test_s5_hypothesis_reaches_real_ev_authority_honest_missing_probability_inputs(tmp_path: Path) -> None:
    """The decisive proof: S5's own real identity flows through `RealEVDecisionEngine` (never
    `MockEVDecisionEngine`), the ledger correctly records `real-ev-engine-v1`, and the terminal state is
    the HONEST `MISSING_PROBABILITY_INPUTS` -- not a fabricated TRADE_DECISION, not a silent skip."""
    strategy, market_state = _s5_breakout_fixture()
    hypothesis = strategy.evaluate(_evaluation_input(market_state))  # type: ignore[arg-type]
    assert hypothesis is not None
    assert hypothesis.expected_edge is None  # honestly disclosed -- no accessible probability evidence

    entry = catalog_entry_for_s5(strategy)
    catalog = StrategyCatalog(entries=(entry,))
    engine = RealEVDecisionEngine(catalog=catalog, market_state=market_state, cost_model=_COST)  # type: ignore[arg-type]
    ledger, store = _ledger(tmp_path)
    result = pipeline.run_cycle(
        market_state=market_state, catalog=catalog, ev_engine=engine, risk_execution_deps=_deps(),  # type: ignore[arg-type]
        ledger=ledger, router=StrategyRouter(),
    )
    assert result.record.final_decision == "NO_TRADE"
    assert result.record.ev_decisions == ((STRATEGY_ID, NO_TRADE),)
    assert result.record.fingerprints.ev_engine_version == REAL_EV_ENGINE_VERSION
    assert result.record.hypothetical_order_intent is None  # never reached Risk -- EV itself said NO_TRADE
    store.close()


# ═══ 3 — S5-specific fail-closed matrix (section 15) ═══

def test_wrong_s5_fingerprint_fails_closed(tmp_path: Path) -> None:
    strategy, market_state = _s5_breakout_fixture()
    hypothesis = strategy.evaluate(_evaluation_input(market_state))  # type: ignore[arg-type]
    assert hypothesis is not None
    tampered = dataclasses.replace(hypothesis, strategy_config_fingerprint="TAMPERED-NOT-THE-REAL-S5-CONFIG")

    entry = catalog_entry_for_s5(strategy)
    catalog = StrategyCatalog(entries=(entry,))
    engine = RealEVDecisionEngine(catalog=catalog, market_state=market_state, cost_model=_COST)  # type: ignore[arg-type]
    decision = engine.decide(tampered)
    assert decision.decision == NO_TRADE
    assert decision.reason_codes == (rc.STRATEGY_POLICY_MISMATCH,)


def test_wrong_s5_version_fails_closed_unknown_strategy() -> None:
    strategy, market_state = _s5_breakout_fixture()
    hypothesis = strategy.evaluate(_evaluation_input(market_state))  # type: ignore[arg-type]
    assert hypothesis is not None
    tampered = dataclasses.replace(hypothesis, strategy_version="not_the_real_representative")

    entry = catalog_entry_for_s5(strategy)  # catalog still keyed on the REAL version
    catalog = StrategyCatalog(entries=(entry,))
    engine = RealEVDecisionEngine(catalog=catalog, market_state=market_state, cost_model=_COST)  # type: ignore[arg-type]
    decision = engine.decide(tampered)
    assert decision.decision == NO_TRADE
    assert decision.reason_codes == (rc.UNKNOWN_STRATEGY,)


def test_wrong_status_not_validated_fails_closed() -> None:
    strategy, market_state = _s5_breakout_fixture()
    hypothesis = strategy.evaluate(_evaluation_input(market_state))  # type: ignore[arg-type]
    assert hypothesis is not None

    research_only_entry = CatalogEntry(
        strategy_id=STRATEGY_ID, strategy_version=STRATEGY_VERSION, status=StrategyStatus.RESEARCH_ONLY,
        enabled=True, allowed_instruments=("XAUUSD",), allowed_directions=("LONG",), context_eligibility=None,
        implementation_fingerprint="s5-impl-v1", config_fingerprint=CONFIG_FINGERPRINT,
        validation_provenance="research-only, not yet validated", risk_contract_reference="risk_manager_live-v1",
        rollback_identity="s5-rollback-v1", strategy=strategy,
    )
    catalog = StrategyCatalog(entries=(research_only_entry,))
    engine = RealEVDecisionEngine(catalog=catalog, market_state=market_state, cost_model=_COST)  # type: ignore[arg-type]
    decision = engine.decide(hypothesis)
    assert decision.decision == NO_TRADE
    assert decision.reason_codes == (rc.NO_ELIGIBLE_STRATEGY,)


def test_s5_disabled_entry_fails_closed() -> None:
    strategy, market_state = _s5_breakout_fixture()
    hypothesis = strategy.evaluate(_evaluation_input(market_state))  # type: ignore[arg-type]
    assert hypothesis is not None
    entry = catalog_entry_for_s5(strategy, enabled=False)
    catalog = StrategyCatalog(entries=(entry,))
    # A disabled entry is excluded from the Router entirely (StrategyCatalog.enabled_entries()) -- but
    # RealEVDecisionEngine ALSO independently checks entry.enabled if somehow reached directly:
    engine = RealEVDecisionEngine(catalog=catalog, market_state=market_state, cost_model=_COST)  # type: ignore[arg-type]
    decision = engine.decide(hypothesis)
    assert decision.decision == NO_TRADE
    assert decision.reason_codes == (rc.STRATEGY_DISABLED,)

    outcome = StrategyRouter().route(catalog=catalog, market_state=market_state)  # type: ignore[arg-type]
    assert outcome.eligible == () and outcome.hypotheses == ()


def test_s5_wrong_market_state_identity_fails_closed() -> None:
    strategy, market_state = _s5_breakout_fixture()
    hypothesis = strategy.evaluate(_evaluation_input(market_state))  # type: ignore[arg-type]
    assert hypothesis is not None
    tampered = dataclasses.replace(hypothesis, market_state_identity="not-the-real-market-state-id")
    entry = catalog_entry_for_s5(strategy)
    catalog = StrategyCatalog(entries=(entry,))
    engine = RealEVDecisionEngine(catalog=catalog, market_state=market_state, cost_model=_COST)  # type: ignore[arg-type]
    decision = engine.decide(tampered)
    assert decision.decision == NO_TRADE
    assert decision.reason_codes == (rc.MARKET_STATE_MISMATCH,)


def test_s5_expired_hypothesis_fails_closed() -> None:
    strategy, market_state = _s5_breakout_fixture()
    hypothesis = strategy.evaluate(_evaluation_input(market_state))  # type: ignore[arg-type]
    assert hypothesis is not None
    expired = dataclasses.replace(hypothesis, eligible_entry_timestamp=hypothesis.eligible_entry_timestamp + 10_000_000)
    entry = catalog_entry_for_s5(strategy)
    catalog = StrategyCatalog(entries=(entry,))
    engine = RealEVDecisionEngine(catalog=catalog, market_state=market_state, cost_model=_COST)  # type: ignore[arg-type]
    decision = engine.decide(expired)
    assert decision.decision == NO_TRADE
    assert decision.reason_codes == (rc.SCHEMA_VALIDATION_FAILED,)


def test_broker_never_reachable_for_s5_even_when_ev_and_risk_would_approve(tmp_path: Path) -> None:
    """Wiring-only proof, NOT a claim about S5's real edge (`expected_edge` here is a synthetic,
    well-formed test payload attached via `dataclasses.replace` to an already-produced real hypothesis --
    the SAME technique the fingerprint/version/market-state-mismatch tests above already use to construct
    adversarial variants; `S5OpeningRangeBreakoutLong.evaluate` itself is never modified and never
    produces this payload on its own, exactly per `s5_opening_range_breakout.py`'s own honest disclosure).
    Even when EV reaches TRADE_DECISION and Risk approves, `BrokerOrderSubmissionGate` stays structurally
    disabled for S5's own real `CatalogEntry` -- mirrors `test_real_ev_engine.py`'s generic future-fixture
    proof, applied here to S5's identity specifically."""
    strategy, market_state = _s5_breakout_fixture()
    hypothesis = strategy.evaluate(_evaluation_input(market_state))  # type: ignore[arg-type]
    assert hypothesis is not None
    wiring_only_edge: dict[str, float | str | None] = {
        "edge_schema": "real-ev-expected-edge-v1", "n": 200.0, "n_target": 110.0, "n_horizon": 60.0,
        "sum_horizon_r": 6.0, "credibility": 0.80,
    }
    test_only_hypothesis = dataclasses.replace(hypothesis, expected_edge=wiring_only_edge)

    entry = catalog_entry_for_s5(strategy)
    catalog = StrategyCatalog(entries=(entry,))
    engine = RealEVDecisionEngine(catalog=catalog, market_state=market_state, cost_model=_COST)  # type: ignore[arg-type]
    decision = engine.decide(test_only_hypothesis)
    assert decision.decision == "TRADE_DECISION"  # proves the wiring CAN carry a positive decision

    # pipeline.run_cycle would re-derive the hypothesis fresh from strategy.evaluate() (honestly
    # expected_edge=None again) -- to prove the Risk+Execution wiring specifically for a TRADE_DECISION
    # on S5's real identity, call evaluate_and_attempt directly with the (test-only) TRADE_DECISION above.
    deps = _deps()
    assert deps.gate.enabled is False
    outcome = evaluate_and_attempt(decision, deps=deps)
    assert outcome.risk_decision.approved is True
    assert outcome.shadow_result is not None
    assert outcome.shadow_result.blocked is True
    assert outcome.shadow_result.reached_broker_gate is True


# ═══ 4 — restart / dedup (section 16) ═══

def test_s5_restart_dedup_never_reprocesses(tmp_path: Path) -> None:
    strategy, market_state = _s5_breakout_fixture()
    entry = catalog_entry_for_s5(strategy)
    catalog = StrategyCatalog(entries=(entry,))
    db_path = tmp_path / "s5_restart.db"

    store1 = SqliteStateStore(db_path)
    ledger1 = ShadowLedger(store1)
    engine1 = RealEVDecisionEngine(catalog=catalog, market_state=market_state, cost_model=_COST)  # type: ignore[arg-type]
    first = pipeline.run_cycle(
        market_state=market_state, catalog=catalog, ev_engine=engine1, risk_execution_deps=_deps(),  # type: ignore[arg-type]
        ledger=ledger1, router=StrategyRouter(),
    )
    assert first.duplicate is False
    store1.close()

    store2 = SqliteStateStore(db_path)
    ledger2 = ShadowLedger(store2)
    assert len(ledger2.entries) == 1
    engine2 = RealEVDecisionEngine(catalog=catalog, market_state=market_state, cost_model=_COST)  # type: ignore[arg-type]
    second = pipeline.run_cycle(
        market_state=market_state, catalog=catalog, ev_engine=engine2, risk_execution_deps=_deps(),  # type: ignore[arg-type]
        ledger=ledger2, router=StrategyRouter(),
    )
    assert second.duplicate is True
    assert second.record == first.record
    assert len(ledger2.entries) == 1
    store2.close()


# ═══ 5 — legacy isolation (section 17) ═══

def test_s5_never_referenced_by_legacy_execution_paths() -> None:
    import ai_trader.multi_policy_live.orchestration as multi_policy_orchestration
    import ai_trader.pdh_pdl_demo.orchestration as pdh_pdl_orchestration

    for module in (pdh_pdl_orchestration, multi_policy_orchestration):
        source = Path(module.__file__).read_text(encoding="utf-8")  # type: ignore[arg-type]
        assert STRATEGY_ID not in source
        assert "s5_opening_range_breakout" not in source
        assert "S5OpeningRangeBreakoutLong" not in source
