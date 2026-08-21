"""`pipeline.run_cycle` -- the section 37 test matrix: EMPTY CATALOG, ONE/MULTIPLE MOCK STRATEGY,
INELIGIBLE STRATEGY, NO SIGNAL, MULTIPLE SIGNALS/CONFLICT, EV REJECTION, RISK REJECTION, INVALID MARKET
STATE, INVALID STRATEGY OUTPUT, BROKER DISABLED, DEDUP, RESTART, FAIL-CLOSED, SHADOW LEDGER,
CONFIG/FINGERPRINT. Uses the REAL N1/Router-produced MarketState fixture (`real_trend_up_market_state`)
and the REAL, reused Risk Engine (`risk_manager_live.evaluate_trade_proposal`) -- nothing about Risk or
MarketState is mocked; only the Strategy layer is (deliberately, section 11's own MOCK strategies)."""

from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import Any

import pytest

from ai_trader.new_brain_live.market_state import MarketState, market_state_identity
from ai_trader.new_brain_live.strategy_platform import reason_codes as rc
from ai_trader.new_brain_live.strategy_platform.catalog import EMPTY_CATALOG, StrategyStatus
from ai_trader.new_brain_live.strategy_platform.ev_engine import MockEVDecisionEngine
from ai_trader.new_brain_live.strategy_platform.mock_strategies import (
    MockAlwaysNoTrade,
    MockConflictA,
    MockConflictB,
    MockLongOnFixedFixture,
    MockShortOnFixedFixture,
)
from ai_trader.new_brain_live.strategy_platform.pipeline import POLICY_PENDING_VALIDATED_STRATEGY_PORTFOLIO, run_cycle
from ai_trader.new_brain_live.strategy_platform.risk_execution_adapter import RiskExecutionDeps
from ai_trader.new_brain_live.strategy_platform.shadow_ledger import ShadowLedger
from ai_trader.new_brain_live.strategy_platform.strategy_protocol import StrategyEvaluationInput
from ai_trader.new_brain_live.strategy_platform.tests._fixtures import catalog_of, make_risk_execution_deps, real_trend_up_market_state
from ai_trader.new_brain_live.strategy_platform.trade_hypothesis import TradeHypothesis
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.risk_manager.types import RiskContext
from ai_trader.signal_engine.types import Direction


def _ledger(tmp_path: Path, name: str = "state.db") -> tuple[ShadowLedger, SqliteStateStore]:
    store = SqliteStateStore(tmp_path / name)
    return ShadowLedger(store), store


def _deps() -> RiskExecutionDeps:
    return RiskExecutionDeps(**make_risk_execution_deps())  # type: ignore[arg-type]


def test_empty_catalog_produces_no_trade_not_error(tmp_path: Path) -> None:
    market_state = real_trend_up_market_state()
    ledger, store = _ledger(tmp_path)
    result = run_cycle(
        market_state=market_state, catalog=EMPTY_CATALOG, ev_engine=MockEVDecisionEngine(),
        risk_execution_deps=_deps(), ledger=ledger,
    )
    assert result.record.final_decision == "NO_TRADE"
    assert result.record.final_reason_codes == (rc.NO_VALIDATED_STRATEGY,)
    assert result.record.hypothetical_order_intent is None
    store.close()


def test_ineligible_strategy_wrong_regime_produces_no_trade(tmp_path: Path) -> None:
    market_state = real_trend_up_market_state()  # resolves TREND_UP
    catalog = catalog_of(MockLongOnFixedFixture(), context_eligibility=("RANGE",))  # never matches TREND_UP
    ledger, store = _ledger(tmp_path)
    result = run_cycle(
        market_state=market_state, catalog=catalog, ev_engine=MockEVDecisionEngine(), risk_execution_deps=_deps(),
        ledger=ledger,
    )
    assert result.record.final_decision == "NO_TRADE"
    assert result.record.final_reason_codes == (rc.NO_ELIGIBLE_STRATEGY,)
    store.close()


def test_regime_independent_strategy_is_always_eligible(tmp_path: Path) -> None:
    market_state = real_trend_up_market_state()
    catalog = catalog_of(MockAlwaysNoTrade(), context_eligibility=None)  # REGIME_INDEPENDENT
    ledger, store = _ledger(tmp_path)
    result = run_cycle(
        market_state=market_state, catalog=catalog, ev_engine=MockEVDecisionEngine(), risk_execution_deps=_deps(),
        ledger=ledger,
    )
    assert result.router_outcome is not None
    assert len(result.router_outcome.eligible) == 1
    store.close()


def test_no_signal_produces_no_trade(tmp_path: Path) -> None:
    market_state = real_trend_up_market_state()
    catalog = catalog_of(MockAlwaysNoTrade(), context_eligibility=("TREND_UP",))
    ledger, store = _ledger(tmp_path)
    result = run_cycle(
        market_state=market_state, catalog=catalog, ev_engine=MockEVDecisionEngine(), risk_execution_deps=_deps(),
        ledger=ledger,
    )
    assert result.record.final_decision == "NO_TRADE"
    assert result.record.final_reason_codes == (rc.NO_STRATEGY_SIGNAL,)
    store.close()


def test_one_mock_strategy_reaches_broker_disabled_with_hypothetical_order_intent(tmp_path: Path) -> None:
    market_state = real_trend_up_market_state()
    catalog = catalog_of(MockLongOnFixedFixture(), context_eligibility=("TREND_UP",))
    ledger, store = _ledger(tmp_path)
    result = run_cycle(
        market_state=market_state, catalog=catalog, ev_engine=MockEVDecisionEngine(), risk_execution_deps=_deps(),
        ledger=ledger,
    )
    assert result.record.final_decision == "NO_TRADE"  # broker structurally disabled, always
    assert result.record.final_reason_codes == (rc.BROKER_DISABLED,)
    assert result.record.hypothetical_order_intent is not None
    assert result.record.hypothetical_order_intent.startswith("MOCK_LONG_ON_FIXED_FIXTURE|")
    assert "BLOCKED_AT_GATE" in result.record.broker_submission_state
    store.close()


def test_multiple_mock_strategies_all_no_signal_or_ineligible_combine_cleanly(tmp_path: Path) -> None:
    market_state = real_trend_up_market_state()
    catalog = catalog_of(
        MockAlwaysNoTrade(), MockLongOnFixedFixture(), context_eligibility=None,
    )
    ledger, store = _ledger(tmp_path)
    result = run_cycle(
        market_state=market_state, catalog=catalog, ev_engine=MockEVDecisionEngine(), risk_execution_deps=_deps(),
        ledger=ledger,
    )
    assert result.router_outcome is not None
    assert len(result.router_outcome.eligible) == 2
    assert len(result.router_outcome.hypotheses) == 1  # only the LONG fixture signals
    store.close()


def test_conflicting_signals_block_via_conflict_policy_never_pick_a_winner(tmp_path: Path) -> None:
    market_state = real_trend_up_market_state()
    catalog = catalog_of(MockConflictA(), MockConflictB(), context_eligibility=None)
    ledger, store = _ledger(tmp_path)
    result = run_cycle(
        market_state=market_state, catalog=catalog, ev_engine=MockEVDecisionEngine(), risk_execution_deps=_deps(),
        ledger=ledger,
    )
    assert result.record.final_decision == "NO_TRADE"
    assert result.record.final_reason_codes == (rc.CONFLICT_POLICY_BLOCK, POLICY_PENDING_VALIDATED_STRATEGY_PORTFOLIO)
    assert result.record.hypothetical_order_intent is None, "must never arbitrarily pick a winner"
    assert len(result.record.ev_decisions) == 2
    store.close()


def test_ev_rejection_produces_no_trade(tmp_path: Path) -> None:
    """A strategy that DOES signal but with no `mock_decision: TRADE` in its expected_edge -- EV
    rejects, never reaches Risk."""

    @dataclasses.dataclass(frozen=True, slots=True)
    class _SignalsButNoEdge:
        strategy_id: str = "TEST_SIGNALS_NO_EDGE"
        strategy_version: str = "v1"

        def evaluate(self, evaluation_input: StrategyEvaluationInput) -> TradeHypothesis | None:
            state = evaluation_input.market_state
            entry = state.entry_price if state.entry_price is not None else 100.0
            return TradeHypothesis(
                strategy_id=self.strategy_id, strategy_version=self.strategy_version, instrument=state.symbol,
                direction=Direction.LONG, signal_timestamp=state.market_timestamp,
                eligible_entry_timestamp=state.market_timestamp, entry_type="MARKET", intended_entry=entry,
                invalidation=entry - 1.0, exit_specification="none", max_hold=1, expected_edge=None,
                reason_codes=("TEST",), market_state_identity=market_state_identity(state),
                strategy_config_fingerprint="test-v1", research_validation_identity=None, provenance="test",
            )

    market_state = real_trend_up_market_state()
    catalog = catalog_of(_SignalsButNoEdge(), context_eligibility=None)
    ledger, store = _ledger(tmp_path)
    result = run_cycle(
        market_state=market_state, catalog=catalog, ev_engine=MockEVDecisionEngine(), risk_execution_deps=_deps(),
        ledger=ledger,
    )
    assert result.record.final_decision == "NO_TRADE"
    assert result.record.final_reason_codes == (rc.EV_BELOW_THRESHOLD,)
    store.close()


def test_risk_rejection_produces_no_trade(tmp_path: Path) -> None:
    """Empty `RiskContext.per_symbol` -> `SymbolRiskSnapshot(data_quality=INSUFFICIENT)` (the type's own
    documented fail-safe default) -> the real risk engine denies on insufficient data quality."""
    market_state = real_trend_up_market_state()
    catalog = catalog_of(MockLongOnFixedFixture(), context_eligibility=("TREND_UP",))
    ledger, store = _ledger(tmp_path)
    deps_kwargs = make_risk_execution_deps()
    deps_kwargs["risk_context"] = RiskContext(as_of=1_700_000_000, per_symbol={})
    result = run_cycle(
        market_state=market_state, catalog=catalog, ev_engine=MockEVDecisionEngine(),
        risk_execution_deps=RiskExecutionDeps(**deps_kwargs),  # type: ignore[arg-type]
        ledger=ledger,
    )
    assert result.record.final_decision == "NO_TRADE"
    assert result.record.final_reason_codes == (rc.RISK_REJECTED,)
    assert result.record.hypothetical_order_intent is not None
    store.close()


def test_invalid_market_state_fails_closed(tmp_path: Path) -> None:
    market_state = real_trend_up_market_state()
    invalid = dataclasses.replace(market_state, entry_price=None)
    catalog = catalog_of(MockLongOnFixedFixture(), context_eligibility=None)
    ledger, store = _ledger(tmp_path)
    result = run_cycle(
        market_state=invalid, catalog=catalog, ev_engine=MockEVDecisionEngine(), risk_execution_deps=_deps(),
        ledger=ledger,
    )
    assert result.record.final_decision == "NO_TRADE"
    assert result.record.final_reason_codes == (rc.MARKET_STATE_INVALID,)
    store.close()


def test_invalid_strategy_output_fails_closed_per_strategy_not_the_whole_cycle(tmp_path: Path) -> None:
    """One strategy raising must not crash the cycle, and must not silently vanish either -- it is
    recorded as INTEGRITY_FAILURE (when it's the only strategy) while the OTHER strategy's honest
    signal still flows through normally."""

    @dataclasses.dataclass(frozen=True, slots=True)
    class _RaisesOnEvaluate:
        strategy_id: str = "TEST_RAISES"
        strategy_version: str = "v1"

        def evaluate(self, evaluation_input: StrategyEvaluationInput) -> TradeHypothesis | None:
            raise RuntimeError("simulated strategy bug")

    market_state = real_trend_up_market_state()

    # Solo: the only eligible strategy raises -> INTEGRITY_FAILURE, not a crash.
    solo_catalog = catalog_of(_RaisesOnEvaluate(), context_eligibility=None)
    ledger, store = _ledger(tmp_path)
    result = run_cycle(
        market_state=market_state, catalog=solo_catalog, ev_engine=MockEVDecisionEngine(),
        risk_execution_deps=_deps(), ledger=ledger,
    )
    assert result.record.final_decision == "NO_TRADE"
    assert result.record.final_reason_codes == (rc.INTEGRITY_FAILURE,)
    assert result.record.invalid_output == (("TEST_RAISES", "RuntimeError: simulated strategy bug"),)
    store.close()

    # Alongside a healthy strategy: the healthy one's hypothesis still reaches EV/Risk/Execution.
    ledger2, store2 = _ledger(tmp_path, "state2.db")
    mixed_catalog = catalog_of(_RaisesOnEvaluate(), MockLongOnFixedFixture(), context_eligibility=None)
    result2 = run_cycle(
        market_state=market_state, catalog=mixed_catalog, ev_engine=MockEVDecisionEngine(),
        risk_execution_deps=_deps(), ledger=ledger2,
    )
    assert result2.router_outcome is not None
    assert result2.router_outcome.invalid_output == (("TEST_RAISES", "RuntimeError: simulated strategy bug"),)
    assert len(result2.router_outcome.hypotheses) == 1
    assert result2.record.final_reason_codes == (rc.BROKER_DISABLED,)  # the healthy strategy still ran end to end
    store2.close()


def test_dedup_restart_replay_never_reprocesses_the_same_market_state(tmp_path: Path) -> None:
    """Simulates a restart: a SECOND `ShadowLedger` opened against the SAME state file (mirroring how
    `SqliteStateStore` is reopened after a real process restart) must see the SAME single record, never
    a duplicate, never a second Risk/Execution attempt."""
    market_state = real_trend_up_market_state()
    catalog = catalog_of(MockLongOnFixedFixture(), context_eligibility=("TREND_UP",))
    db_path = tmp_path / "restart.db"

    store1 = SqliteStateStore(db_path)
    ledger1 = ShadowLedger(store1)
    first = run_cycle(
        market_state=market_state, catalog=catalog, ev_engine=MockEVDecisionEngine(), risk_execution_deps=_deps(),
        ledger=ledger1,
    )
    assert first.duplicate is False
    store1.close()

    # "Restart" -- a fresh store/ledger against the same file.
    store2 = SqliteStateStore(db_path)
    ledger2 = ShadowLedger(store2)
    assert len(ledger2.entries) == 1
    second = run_cycle(
        market_state=market_state, catalog=catalog, ev_engine=MockEVDecisionEngine(), risk_execution_deps=_deps(),
        ledger=ledger2,
    )
    assert second.duplicate is True
    assert second.record == first.record
    assert len(ledger2.entries) == 1, "a restart replay must never append a second, duplicate record"
    store2.close()


def test_shadow_ledger_record_reconstructs_the_whole_cycle(tmp_path: Path) -> None:
    market_state = real_trend_up_market_state()
    catalog = catalog_of(MockLongOnFixedFixture(), context_eligibility=("TREND_UP",))
    ledger, store = _ledger(tmp_path)
    result = run_cycle(
        market_state=market_state, catalog=catalog, ev_engine=MockEVDecisionEngine(), risk_execution_deps=_deps(),
        ledger=ledger,
    )
    record = result.record
    assert record.market_timestamp == market_state.market_timestamp
    assert record.market_state_identity == market_state_identity(market_state)
    assert record.eligible_strategy_ids == ("MOCK_LONG_ON_FIXED_FIXTURE",)
    assert record.fingerprints.market_intelligence_fingerprint == market_state.n1_output_fp
    assert record.fingerprints.catalog_version
    assert record.fingerprints.ev_engine_version
    assert record.fingerprints.risk_engine_version
    assert record.fingerprints.execution_adapter_version
    store.close()


def test_zero_validated_strategies_is_acceptable_not_an_error(tmp_path: Path) -> None:
    """Section 45's own explicit acceptance: catalog entries exist but none are VALIDATED (all
    MOCK_TEST_ONLY) -- still functions correctly, never crashes, never fabricates a trade."""
    market_state = real_trend_up_market_state()
    catalog = catalog_of(MockLongOnFixedFixture(), status=StrategyStatus.MOCK_TEST_ONLY, context_eligibility=None)
    assert all(e.status is not StrategyStatus.VALIDATED for e in catalog.entries)
    ledger, store = _ledger(tmp_path)
    result = run_cycle(
        market_state=market_state, catalog=catalog, ev_engine=MockEVDecisionEngine(), risk_execution_deps=_deps(),
        ledger=ledger,
    )
    assert result.record.final_decision == "NO_TRADE"  # broker disabled regardless of validation status
    store.close()


def test_deterministic_replay_same_inputs_produce_byte_identical_decision(tmp_path: Path) -> None:
    """Section 25: fixed MarketState + catalog + configs -> deterministic decision output. Two
    INDEPENDENT ledgers (not a restart of the same one) processing the identical MarketState/catalog
    must reach byte-identical ShadowLedgerRecords, field for field."""
    market_state = real_trend_up_market_state()
    catalog = catalog_of(MockLongOnFixedFixture(), context_eligibility=("TREND_UP",))

    ledger_a, store_a = _ledger(tmp_path, "replay_a.db")
    result_a = run_cycle(
        market_state=market_state, catalog=catalog, ev_engine=MockEVDecisionEngine(), risk_execution_deps=_deps(),
        ledger=ledger_a,
    )
    store_a.close()

    ledger_b, store_b = _ledger(tmp_path, "replay_b.db")
    result_b = run_cycle(
        market_state=market_state, catalog=catalog, ev_engine=MockEVDecisionEngine(), risk_execution_deps=_deps(),
        ledger=ledger_b,
    )
    store_b.close()

    assert result_a.record == result_b.record
