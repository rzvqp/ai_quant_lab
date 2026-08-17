"""Real-data live-vs-replay parity test (RT-N1-REPLAY-0001 section 3's own explicit requirement:
"Folosește și bare reale deja journaled în Live Shadow pentru testul de paritate"). Never runs as part
of standard regression -- requires a real MT5 terminal AND the actually-running LIVE_SHADOW process's
persisted telemetry, matching the established `MT5_REAL_TERMINAL_TEST=1` gating convention
(`ai_trader/execution_engine/adapters/tests/test_mt5_real_terminal_integration.py`).

**Read-only, twice over**: reads `new_brain_live_state/xauusd_m15.db` (the SAME db LIVE_SHADOW itself
writes to) via a fresh, independent `SqliteStateStore` connection -- never writes to it, never touches
`decision_authority`, never calls `set_authority`. Reads real MT5 bars via `copy_rates_range` -- no
`order_send`, no position/order calls. Does not access SEALED data (this reads live operational
telemetry, not any research/holdout dataset).

**Why matching is done by CONTENT/POSITION rather than exact timestamp equality**: `make_broker_offset`
is deliberately re-measured fresh on every call (never cached, per its own docstring) and can drift by
about a minute between two calls made minutes apart -- reproducing LIVE_SHADOW's own exact historical
label assignment after the fact is not reliable. What IS reliable: `n1_output_fingerprint` depends only
on the ORDERED SEQUENCE of real OHLC values fed into a fresh `RawAxesBuilder` (see `bridge.py`'s own
`n1_output_fp` formula -- it never references a bar's timestamp), so matching real bars to the
journaled window by nearest `ts_open` and taking the following contiguous run is sufficient for an
exact fingerprint comparison, without needing byte-exact timestamp reproduction."""

from __future__ import annotations

import os

import pytest

from ai_trader.n1_replay import N1ReplayEngine
from ai_trader.n1_replay.fixtures.canonical_bars import CANONICAL_BAR_INTERVAL_SECONDS as BAR_INTERVAL_SECONDS
from ai_trader.n1_replay.fixtures.canonical_bars import CANONICAL_SYMBOL as SYMBOL
from ai_trader.n1_replay.fixtures.canonical_bars import CANONICAL_TIMEFRAME as TIMEFRAME
from ai_trader.new_brain_live.entrypoint import DEFAULT_DB_PATH  # test-only import -- never in package source

pytestmark = pytest.mark.skipif(
    os.environ.get("MT5_REAL_TERMINAL_TEST") != "1",
    reason="Real MT5 terminal + running LIVE_SHADOW telemetry required -- set MT5_REAL_TERMINAL_TEST=1 "
    "to run explicitly. Never runs as part of standard regression.",
)


def test_replay_matches_live_shadow_journaled_n1_output() -> None:
    from ai_trader.live_signal_source.bar_feed import make_broker_offset
    from ai_trader.live_signal_source.types import Bar
    from ai_trader.mt5_pnl_source.gateway import RealMT5HistoryGateway
    from ai_trader.new_brain_bridge.telemetry import NewBrainTelemetryLog
    from ai_trader.persistent_state.store import SqliteStateStore
    import MetaTrader5 as mt5  # type: ignore[import-untyped]

    if not DEFAULT_DB_PATH.exists():
        pytest.skip("new_brain_live_state/xauusd_m15.db does not exist -- LIVE_SHADOW has not run yet")

    store = SqliteStateStore(DEFAULT_DB_PATH)
    try:
        log = NewBrainTelemetryLog(store)
        seen: dict[int, str] = {}
        for record in log.entries:
            ts = record.event_identity.market_timestamp
            n1_trace = next((t for t in record.node_traces if t.node_name == "N1"), None)
            if ts not in seen and n1_trace is not None:
                seen[ts] = n1_trace.output
    finally:
        store.close()

    if len(seen) < 3:
        pytest.skip(f"only {len(seen)} distinct journaled N1 events -- too few for a meaningful parity check")

    live_pairs = sorted(seen.items())

    gateway = RealMT5HistoryGateway()
    assert gateway.initialize(), f"MT5 initialize() failed: {gateway.last_error()!r}"
    try:
        offset = make_broker_offset(gateway, SYMBOL)()
        first_ts_open = live_pairs[0][0] - BAR_INTERVAL_SECONDS
        last_ts_close = live_pairs[-1][0]
        pad = 3 * BAR_INTERVAL_SECONDS
        rates = gateway.copy_rates_range(
            SYMBOL, mt5.TIMEFRAME_M15, first_ts_open - pad + offset, last_ts_close + pad + offset,
        )
    finally:
        gateway.shutdown()

    assert rates is not None and len(rates) > 0, "no real bars returned for the journaled window"
    corrected = sorted((int(r["time"]) - offset, r) for r in rates)
    start_idx = min(range(len(corrected)), key=lambda i: abs(corrected[i][0] - first_ts_open))
    window = corrected[start_idx:start_idx + len(live_pairs)]
    assert len(window) == len(live_pairs), "not enough contiguous real bars covering the journaled window"

    bars = tuple(
        Bar(
            symbol=SYMBOL, ts_open=ts_open, ts_close=ts_open + BAR_INTERVAL_SECONDS,
            open=float(rate["open"]), high=float(rate["high"]), low=float(rate["low"]),
            close=float(rate["close"]), volume=float(rate["tick_volume"]),
        )
        for ts_open, rate in window
    )

    engine = N1ReplayEngine(
        symbol=SYMBOL, timeframe=TIMEFRAME, bar_interval_seconds=BAR_INTERVAL_SECONDS,
        implementation_commit="TEST_LIVE_PARITY", clock=lambda: 10**10,
    )
    replayed = [result.n1_output_fingerprint for result in engine.replay(bars)]
    expected = [output for _, output in live_pairs]

    assert replayed == expected, (
        f"replay produced {replayed} but LIVE_SHADOW's own journal recorded {expected} for the same "
        "real, already-processed bars"
    )
