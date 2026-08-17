"""`NewBrainLiveLoop` tests -- orchestration logic only, with fakes: `safe_evaluate_bar` and
`submit_new_brain_candidate` are monkeypatched at their `entrypoint` module-level names (matching
`test_probability_source.py`'s own established monkeypatch convention) so these tests isolate the LOOP's
own decisions (circuit breaker, authority demotion, journaling, broker-gate-blocked classification) from
`evaluate_bar`'s/the real Risk Manager's own internal correctness, which are already exhaustively tested
elsewhere. No real MT5 terminal, no real tower worker."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import ve_brain  # type: ignore[import-untyped]

from ai_trader.live_signal_source.bar_feed import LiveBarFeed
from ai_trader.live_signal_source.types import Bar
from ai_trader.mandate2_readiness.decision_provenance import NEW_BRAIN_SOURCE, DecisionProvenance
from ai_trader.mandate2_readiness.event_identity import EventIdentity
from ai_trader.new_brain_bridge.authority import DecisionAuthority
from ai_trader.new_brain_bridge.bridge import NewBrainOutcome
from ai_trader.new_brain_bridge.fail_safe import BrainUnavailableOutcome
from ai_trader.new_brain_live import entrypoint as entrypoint_module
from ai_trader.new_brain_live.deps import NewBrainLiveDepsFactory
from ai_trader.new_brain_live.entrypoint import NewBrainLiveLoop
from ai_trader.new_brain_live.live_shadow_journal import LiveShadowCategory, LiveShadowJournal
from ai_trader.new_brain_live.tests._fixtures import SYMBOL, FakeNewBrainLiveGateway
from ai_trader.new_brain_bridge.telemetry import NewBrainTelemetryLog
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.risk_manager.types import EngineState
from ai_trader.risk_manager_live.circuit_breaker import persist_circuit_state
from ai_trader.risk_manager_live.types import LiveRiskDecision, TradingCircuitState

AS_OF = 1_700_000_000


@dataclass
class _RawRate:
    time: int
    open: float
    high: float
    low: float
    close: float
    tick_volume: float = 100.0


def _real_closed_rate() -> _RawRate:
    """One real, safely-in-the-past closed M15 bar (`AS_OF` is far behind real system time) --
    `LiveBarFeed.poll()`'s own `now = self._clock()` (real `time.time()` by default) will treat it as
    genuinely closed."""
    return _RawRate(time=AS_OF - 900, open=2400.0, high=2401.0, low=2399.0, close=2400.5)


def _event_identity(trace_id: str) -> EventIdentity:
    return EventIdentity(
        trace_id=trace_id, market_event_id=f"{SYMBOL}:M15:{AS_OF}", symbol=SYMBOL, timeframe="M15",
        bar_id=f"{SYMBOL}:M15:{AS_OF}", market_timestamp=AS_OF, received_timestamp=AS_OF,
        brain_version=ve_brain.VE_BRAIN_VERSION, catalog_hash=ve_brain.CANONICAL_CATALOG_HASH,
        configuration_fingerprint="cfg-test",
    )


def _no_trade_outcome() -> NewBrainOutcome:
    return NewBrainOutcome(
        event_identity=_event_identity("t-no-trade"), strategy_id="trend_pullback", strategy_version="v1",
        node_traces=(), decision=None, provenance=None, entry_price=None, stop_price=None, target_price=None,
    )


def _trade_outcome(trace_id: str = "t-trade") -> NewBrainOutcome:
    decision = ve_brain.DecisionResponse(
        contract_id=ve_brain.OUTPUT_CONTRACT_ID, decision="TRADE", expected_value_net=0.5,
        expected_reward=1.0, expected_loss=0.3, estimated_cost=0.02, probability_assumptions={},
        strategy_id="trend_pullback", configuration_fingerprint="cfg-test",
        reason_codes=(ve_brain.ReasonCode.TRADE_VALIDATED_EDGE.value,), engine_version=ve_brain.ENGINE_VERSION,
    )
    provenance = DecisionProvenance(
        source=NEW_BRAIN_SOURCE, trace_id=trace_id, catalog_hash=ve_brain.CANONICAL_CATALOG_HASH,
        configuration_fingerprint="cfg-test",
    )
    return NewBrainOutcome(
        event_identity=_event_identity(trace_id), strategy_id="trend_pullback", strategy_version="v1",
        node_traces=(), decision=decision, provenance=provenance, entry_price=2400.0, stop_price=2390.0,
        target_price=2420.0,
    )


def _make_loop(
    tmp_path: Path, *, outcomes: Any, authority: DecisionAuthority | None = DecisionAuthority.NEW_BRAIN,
) -> tuple[NewBrainLiveLoop, LiveShadowJournal, SqliteStateStore]:
    gateway = FakeNewBrainLiveGateway(rates=(_real_closed_rate(),))
    state_store = SqliteStateStore(tmp_path / "state.db")
    persist_circuit_state(state_store, TradingCircuitState(state=EngineState.READY, reason_code="OK", since=AS_OF), AS_OF)
    feed = LiveBarFeed(gateway, SYMBOL, 15, 900, state_store=state_store)
    from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder

    axes_builder = RawAxesBuilder(SYMBOL)
    deps_factory = NewBrainLiveDepsFactory(SYMBOL, gateway, tmp_path)
    telemetry_log = NewBrainTelemetryLog(state_store)
    shadow_journal = LiveShadowJournal(state_store)

    def _fake_safe_evaluate_bar(bar: Bar, *, timeframe: str, axes_builder: Any, tower: Any = None) -> Any:
        return outcomes

    entrypoint_module.safe_evaluate_bar = _fake_safe_evaluate_bar  # type: ignore[attr-defined]

    loop = NewBrainLiveLoop(
        feed=feed, axes_builder=axes_builder, tower=None, deps_factory=deps_factory,  # type: ignore[arg-type]
        state_store=state_store, telemetry_log=telemetry_log, shadow_journal=shadow_journal,
        authority_check=None if authority is None else (lambda: authority),
    )
    return loop, shadow_journal, state_store


def test_circuit_breaker_not_ready_skips_the_cycle(tmp_path: Path, monkeypatch: Any) -> None:
    loop, journal, store = _make_loop(tmp_path, outcomes=(_no_trade_outcome(),))
    persist_circuit_state(store, TradingCircuitState(state=EngineState.SUSPENDED, reason_code="TEST", since=AS_OF), AS_OF)
    ran = loop.tick()
    assert ran is False
    assert journal.entries == ()
    store.close()


def test_no_trade_outcome_is_journaled_and_never_reaches_risk_manager(tmp_path: Path, monkeypatch: Any) -> None:
    loop, journal, store = _make_loop(tmp_path, outcomes=(_no_trade_outcome(),))

    def _fail_if_called(*args: Any, **kwargs: Any) -> LiveRiskDecision:
        raise AssertionError("submit_new_brain_candidate must never be called for a NO_TRADE outcome")

    monkeypatch.setattr(entrypoint_module, "submit_new_brain_candidate", _fail_if_called)
    ran = loop.tick()
    assert ran is True
    assert len(journal.entries) == 1
    assert journal.entries[0].category is LiveShadowCategory.LIVE_SHADOW_NO_TRADE
    store.close()


def test_brain_unavailable_outcome_never_crashes_the_loop(tmp_path: Path) -> None:
    unavailable = BrainUnavailableOutcome(
        symbol=SYMBOL, timeframe="M15", bar_ts_close=AS_OF, reason="BRAIN_UNAVAILABLE", error="boom",
    )
    loop, journal, store = _make_loop(tmp_path, outcomes=unavailable)
    ran = loop.tick()
    assert ran is True  # the cycle itself completed; the bar's own processing degraded, not the loop
    assert journal.entries == ()
    store.close()


def test_legacy_authority_never_reaches_risk_manager(tmp_path: Path, monkeypatch: Any) -> None:
    """CEO section 3: a process without NEW_BRAIN authority is `LEGACY_SHADOW_TELEMETRY` -- it observes
    but never submits."""
    loop, journal, store = _make_loop(tmp_path, outcomes=(_trade_outcome(),), authority=DecisionAuthority.LEGACY)

    def _fail_if_called(*args: Any, **kwargs: Any) -> LiveRiskDecision:
        raise AssertionError("submit_new_brain_candidate must never be called without NEW_BRAIN authority")

    monkeypatch.setattr(entrypoint_module, "submit_new_brain_candidate", _fail_if_called)
    ran = loop.tick()
    assert ran is True
    assert len(journal.entries) == 1
    assert journal.entries[0].category is LiveShadowCategory.LIVE_SHADOW_EVENT
    assert journal.entries[0].terminal_reason_code == "LEGACY_SHADOW_TELEMETRY_AUTHORITY_NOT_NEW_BRAIN"
    store.close()


def test_approved_candidate_reaches_broker_gate_and_is_blocked(tmp_path: Path, monkeypatch: Any) -> None:
    loop, journal, store = _make_loop(tmp_path, outcomes=(_trade_outcome(),), authority=DecisionAuthority.NEW_BRAIN)

    from ai_trader.risk_manager_live.types import CalculationTraceStep

    approved = LiveRiskDecision(
        approved=True, reason_codes=(), requested_risk=10.0, approved_risk=10.0, calculated_volume=0.01,
        monetary_risk=10.0, stop_distance=10.0, margin_estimate=5.0, warnings=(),
        calculation_trace=(CalculationTraceStep(stage="test", passed=True),),
    )
    monkeypatch.setattr(entrypoint_module, "submit_new_brain_candidate", lambda *a, **k: approved)

    ran = loop.tick()
    assert ran is True
    assert len(journal.entries) == 1
    record = journal.entries[0]
    assert record.category is LiveShadowCategory.LIVE_SHADOW_BLOCKED_AT_BROKER
    assert record.reached_broker_gate is True
    assert record.broker_blocked is True
    assert record.order_send_calls == 0
    assert record.orders_created == 0
    assert record.positions_created == 0
    store.close()


def test_denied_candidate_is_not_blocked_at_broker_because_it_never_reaches_the_gate(
    tmp_path: Path, monkeypatch: Any,
) -> None:
    loop, journal, store = _make_loop(tmp_path, outcomes=(_trade_outcome(),), authority=DecisionAuthority.NEW_BRAIN)

    denied = LiveRiskDecision(
        approved=False, reason_codes=("RISK_LIMIT_EXCEEDED",), requested_risk=None, approved_risk=None,
        calculated_volume=None, monetary_risk=None, stop_distance=None, margin_estimate=None, warnings=(),
        calculation_trace=(),
    )
    monkeypatch.setattr(entrypoint_module, "submit_new_brain_candidate", lambda *a, **k: denied)

    ran = loop.tick()
    assert ran is True
    record = journal.entries[0]
    assert record.category is LiveShadowCategory.LIVE_SHADOW_CANDIDATE
    assert record.reached_broker_gate is False
    store.close()


def test_broker_gate_default_is_never_enabled(tmp_path: Path, monkeypatch: Any) -> None:
    """Structural proof, not just a convention: the loop's own default `gate` parameter is a fresh,
    default-closed `BrokerOrderSubmissionGate`."""
    loop, _journal, store = _make_loop(tmp_path, outcomes=(_no_trade_outcome(),))
    assert loop._gate.enabled is False  # noqa: SLF001 -- deliberate internal-state check
    store.close()


def test_clean_stop_exits_run_forever(tmp_path: Path) -> None:
    loop, _journal, store = _make_loop(tmp_path, outcomes=(_no_trade_outcome(),))
    call_count = 0

    def _sleep(seconds: float) -> None:
        nonlocal call_count
        call_count += 1
        if call_count >= 2:
            loop.stop()

    loop.run_forever(sleep=_sleep, install_signal_handlers=False)
    assert loop.stop_requested is True
    assert call_count >= 2
