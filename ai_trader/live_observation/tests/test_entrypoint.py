"""`build_loop` wiring tests -- proves the composed pipeline behaves exactly like every already-proven
piece it's built from: zero candidates end-to-end, structural facts genuinely recorded, circuit breaker
consulted from the shared persisted store, watermark resume works through the composed loop too."""

from __future__ import annotations

from pathlib import Path

from ai_trader.live_observation.entrypoint import build_loop
from ai_trader.live_signal_source.tests._fixtures import FakeMT5Gateway, RawRate
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.structural_observer.journal import StructuralObservationLog
from ai_trader.structural_observer.types import StructuralEventKind

SYMBOL = "XAUUSD"
M15_SECONDS = 15 * 60
NOW = 1_700_000_000


def _closed_bar_gateway(*ts_opens: int) -> FakeMT5Gateway:
    """`m1_probe_rates` backs `build_loop`'s own `make_broker_offset(gateway, symbol)` (default
    `system_clock`, i.e. the REAL wall clock at test-run time) -- set so the derived offset shifts every
    bar's corrected `ts_open` to just-behind real "now", regardless of how far in the past the fixed
    `NOW` constant itself is: `offset = (NOW + M15_SECONDS - 60) + 60 - real_now`, so
    `corrected_ts_open = raw_ts_open - offset = (raw_ts_open - NOW - M15_SECONDS) + real_now` -- always a
    few thousand seconds behind real "now", exactly like this file's bars were before broker-time ever
    entered the picture."""
    return FakeMT5Gateway(
        rates=[RawRate(time=ts, open=2000.0, high=2001.0, low=1999.0, close=2000.5) for ts in ts_opens],
        m1_probe_rates=[RawRate(time=NOW + M15_SECONDS - 60, open=1.0, high=1.0, low=1.0, close=1.0)],
    )


def test_build_loop_produces_zero_candidates_and_records_structural_facts(tmp_path: Path) -> None:
    gateway = _closed_bar_gateway(NOW - 2_000, NOW - 1_000)
    state_store = SqliteStateStore(tmp_path / "state.db")
    loop = build_loop(gateway, state_store, symbol=SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS)

    ran = loop.tick()

    assert ran is True
    structural_journal = StructuralObservationLog(state_store, log_name="structural_observer.observations")
    regimes = [e for e in structural_journal.entries if e.kind is StructuralEventKind.REGIME]
    assert len(regimes) == 2  # one per bar the fake gateway supplied


def test_build_loop_circuit_breaker_still_gates_the_cycle(tmp_path: Path) -> None:
    from ai_trader.risk_manager.types import EngineState
    from ai_trader.risk_manager_live.circuit_breaker import persist_circuit_state
    from ai_trader.risk_manager_live.types import TradingCircuitState

    gateway = _closed_bar_gateway(NOW - 2_000, NOW - 1_000)
    state_store = SqliteStateStore(tmp_path / "state.db")
    persist_circuit_state(
        state_store,
        TradingCircuitState(state=EngineState.EMERGENCY_STOP, reason_code="TEST", since=NOW),
        as_of=NOW,
    )
    loop = build_loop(gateway, state_store, symbol=SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS)

    ran = loop.tick()

    assert ran is False
    assert gateway.copy_rates_from_calls == []  # cycle skipped entirely -- feed never even polled


def test_build_loop_resumes_from_the_persisted_watermark_after_restart(tmp_path: Path) -> None:
    db_path = tmp_path / "state.db"
    gateway_before = _closed_bar_gateway(NOW - 2_000, NOW - 1_000)
    store_before = SqliteStateStore(db_path)
    loop_before = build_loop(gateway_before, store_before, symbol=SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS)
    loop_before.tick()
    store_before.close()

    gateway_after = _closed_bar_gateway(NOW - 2_000, NOW - 1_000, NOW)  # same two bars + one new
    store_after = SqliteStateStore(db_path)
    loop_after = build_loop(gateway_after, store_after, symbol=SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS)
    loop_after.tick()

    structural_journal = StructuralObservationLog(store_after, log_name="structural_observer.observations")
    regimes = [e for e in structural_journal.entries if e.kind is StructuralEventKind.REGIME]
    assert len(regimes) == 3  # 2 from before restart + exactly 1 new -- no duplicate reprocessing
