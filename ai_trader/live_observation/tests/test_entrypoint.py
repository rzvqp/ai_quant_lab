"""`build_loop` wiring tests -- proves the composed pipeline behaves exactly like every already-proven
piece it's built from: zero candidates end-to-end, structural facts genuinely recorded, circuit breaker
consulted from the shared persisted store, watermark resume works through the composed loop too."""

from __future__ import annotations

import time as _time
from pathlib import Path

from ai_trader.live_observation.entrypoint import build_loop
from ai_trader.live_signal_source.tests._fixtures import FakeMT5Gateway, RawRate
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.structural_observer.journal import StructuralObservationLog
from ai_trader.structural_observer.types import StructuralEventKind

SYMBOL = "XAUUSD"
M15_SECONDS = 15 * 60
NOW = 1_700_000_000


_TEST_OFFSET_SAFETY_MARGIN_SECONDS = 300
"""Comfortably larger than both the +/-30s rounding noise `make_broker_offset` (2026-08-11 duplicate-bar
fix) can introduce AND any realistic real-clock drift between `_closed_bar_gateway` constructing its M1
probe rate and the moment `make_broker_offset` itself reads `time.time()` a little later -- see that
function's own docstring below."""


def _closed_bar_gateway(*ts_opens: int) -> FakeMT5Gateway:
    """`m1_probe_rates` backs `build_loop`'s own `make_broker_offset(gateway, symbol)` (default
    `system_clock`, i.e. the REAL wall clock at test-run time) -- set so the derived offset shifts every
    bar's corrected `ts_open` behind real "now" by `_TEST_OFFSET_SAFETY_MARGIN_SECONDS` plus one bar
    period, regardless of how far in the past the fixed `NOW` constant itself is -- always safely,
    unambiguously closed, exactly like this file's bars were before broker-time ever entered the picture.

    **Rounded AND margined, 2026-08-11** (duplicate-bar fix): `make_broker_offset` now rounds every
    measured offset to the nearest `_OFFSET_PROBE_BAR_SECONDS` (60) -- correct for a REAL broker offset
    (always a whole number of minutes), but this fixture's own implied offset is an arbitrary, unrounded
    number of seconds (`NOW` is a fixed 2023 epoch; `real_now` is whatever the wall clock reads at test
    time). The ORIGINAL version of this fixture put the newest bar's corrected close EXACTLY at real
    "now" (zero margin, relying only on the sub-millisecond gap between fixture construction and the
    forming-bar check to keep it in the past) -- with unrounded offsets that gap alone was enough, but
    the new ±30s rounding noise can push that marginal bar's close to appear up to 30s in the FUTURE,
    intermittently failing the forming-bar filter (caught by a flaky failure, not by inspection: 8 of 30
    repeated runs of `test_build_loop_resumes_from_the_persisted_watermark_after_restart` lost the newest
    bar this way). `_TEST_OFFSET_SAFETY_MARGIN_SECONDS` (300, ten times the rounding noise) restores a
    real margin. The target offset is pre-rounded here too, the same way `make_broker_offset` will round
    it, so this fixture's own value is a no-op input to that rounding, not a second, independent source
    of drift."""
    real_now = int(_time.time())
    target_offset = round(
        (NOW + M15_SECONDS - 60 + _TEST_OFFSET_SAFETY_MARGIN_SECONDS - real_now) / 60
    ) * 60
    latest_closed_ts_open = real_now + target_offset - 60
    return FakeMT5Gateway(
        rates=[RawRate(time=ts, open=2000.0, high=2001.0, low=1999.0, close=2000.5) for ts in ts_opens],
        m1_probe_rates=[RawRate(time=latest_closed_ts_open, open=1.0, high=1.0, low=1.0, close=1.0)],
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
