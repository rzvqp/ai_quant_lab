"""N1 incremental integration -- CEO's 7 mandatory tests (2026-08-18), against the REAL installed
`ve_n1_replay` 0.1.1 artifact via a genuine subprocess call to `.ai_trader_n1_venv` (AI-Trader-exclusive
since the environment split, `N1_ALPHA_AI_TRADER_RUNTIME_ISOLATION_COMPLETE`, 2026-08-21) -- never
mocked. This is
the whole point: proving the Red-Team-cleared engine actually resolves the `N1_HYDRATION_CONDITIONAL`
blocker end-to-end through the real isolation boundary this package builds, not merely that the client
code compiles."""

from __future__ import annotations

import dataclasses
import inspect
import time
from pathlib import Path
from typing import Any

import ve_brain  # type: ignore[import-untyped]

from ai_trader.live_signal_source.bar_feed import LiveBarFeed
from ai_trader.live_signal_source.types import Bar
from ai_trader.new_brain_bridge.bridge import TowerDependencies
from ai_trader.new_brain_bridge.tests.conftest import bos_bull_bars
from ai_trader.new_brain_bridge.tests.test_bridge_tower_wiring import (
    _COMPLETE_N2_OUTPUT,
    _COMPLETE_N3_OUTPUT,
    _COMPLETE_N4_OUTPUT,
    _FakeTimeframeAwareGateway,
    _FakeWorker,
    _client_for,
    _closed_rates,
)
from ai_trader.new_brain_live import n1_incremental
from ai_trader.new_brain_live.dual_clock.m5_decision_loop import M5DecisionLoop
from ai_trader.new_brain_live.dual_clock.upstream_context import CachedUpstreamContext, UpstreamContextStore
from ai_trader.new_brain_live.n1_incremental import (
    artifact_pin,
    client as client_module,
    context_refresh_loop_incremental,
    hydrate,
    snapshot_store as snapshot_store_module,
)
from ai_trader.new_brain_live.n1_incremental.client import N1IncrementalClient, N1IncrementalWorkerError
from ai_trader.new_brain_live.n1_incremental.context_refresh_loop_incremental import IncrementalContextRefreshLoop
from ai_trader.new_brain_live.n1_incremental.snapshot_store import N1IncrementalSnapshotStore
from ai_trader.new_brain_live.tests._fixtures import SYMBOL, FakeNewBrainLiveGateway
from ai_trader.persistent_state.store import SqliteStateStore

_BAR_SECONDS = 900
_MT5_TIMEFRAME = 15
_COMMIT = artifact_pin.PINNED_DELIVERY_COMMIT


def _client(**overrides: Any) -> N1IncrementalClient:
    kwargs: dict[str, Any] = {
        "symbol": SYMBOL, "timeframe": "M15", "bar_interval_seconds": _BAR_SECONDS,
        "implementation_commit": _COMMIT,
    }
    kwargs.update(overrides)
    return N1IncrementalClient(**kwargs)


def _calm_bars_after(*, count: int, start_index: int, start_price: float) -> list[Bar]:
    bars: list[Bar] = []
    price = start_price
    for i in range(count):
        idx = start_index + i
        o = price
        h = o + 0.4
        low_ = o - 0.4
        c = o + 0.02
        bars.append(Bar(
            symbol=SYMBOL, ts_open=idx * _BAR_SECONDS, ts_close=(idx + 1) * _BAR_SECONDS,
            open=o, high=h, low=low_, close=c, volume=100.0,
        ))
        price = c
    return bars


def _far_history(*, calm_count: int) -> tuple[Bar, ...]:
    """A confirmed `bos_bull` break (idx 14) followed by `calm_count` calm bars with no further break."""
    bos = bos_bull_bars(SYMBOL)
    calm = _calm_bars_after(count=calm_count, start_index=len(bos), start_price=bos[-1].close)
    return tuple(bos) + tuple(calm)


# ═══ 1 — trend started over 5300 bars ago survives restart ═══

def test_trend_started_over_5300_bars_ago_survives_restart() -> None:
    history = _far_history(calm_count=5310)  # 18 + 5310 = 5328; break sits 5328-14=5314 bars before the end
    assert len(history) - 14 > 5300, "fixture regression: must comfortably exceed the CEO's 5300-bar horizon"

    warmup, tail = history[:-1], history[-1]
    client = _client()

    # Cold hydration over everything except the very last bar.
    cold = client.observe(bars=warmup, restore_snapshot_blob=None, wall_clock_now=time.time())
    assert not cold.rejected
    assert cold.snapshot_blob is not None

    # "Restart": a FRESH client call restoring from that snapshot, observing only the one remaining bar.
    restarted = client.observe(bars=(tail,), restore_snapshot_blob=cold.snapshot_blob, wall_clock_now=time.time())
    assert restarted.restored_from_snapshot is True
    assert not restarted.rejected
    assert restarted.result is not None
    assert restarted.result.raw_axes.structure == "strong"
    assert restarted.result.raw_axes.direction == "up"
    assert "TREND_UP" in restarted.result.applicable_regimes


# ═══ 2 — cold start == continuous run (chunk-invariant) ═══

def test_cold_start_equals_continuous_run_chunked() -> None:
    history = _far_history(calm_count=200)
    client = _client()

    one_shot = client.observe(bars=history, restore_snapshot_blob=None, wall_clock_now=time.time())
    assert not one_shot.rejected
    assert one_shot.result is not None

    midpoint = len(history) // 2
    first_chunk = client.observe(bars=history[:midpoint], restore_snapshot_blob=None, wall_clock_now=time.time())
    assert not first_chunk.rejected
    second_chunk = client.observe(
        bars=history[midpoint:], restore_snapshot_blob=first_chunk.snapshot_blob, wall_clock_now=time.time(),
    )
    assert not second_chunk.rejected
    assert second_chunk.result is not None

    assert one_shot.result.raw_axes == second_chunk.result.raw_axes
    assert one_shot.result.applicable_regimes == second_chunk.result.applicable_regimes
    assert one_shot.result.n1_output_fingerprint == second_chunk.result.n1_output_fingerprint


# ═══ 3 — CONTEXT_FROM_FUTURE refused before the tower, for an incrementally-produced context ═══

def _tower_for(worker: _FakeWorker, *, now: int) -> TowerDependencies:
    gateway = _FakeTimeframeAwareGateway(
        h1_rates=_closed_rates(count=150, step=3600, now=now, start_price=1990.0),
        m15_rates=_closed_rates(count=150, step=900, now=now, start_price=2000.0),
        m5_rates=_closed_rates(count=150, step=300, now=now, start_price=2010.0),
    )
    return TowerDependencies(client=_client_for(worker), gateway=gateway)  # type: ignore[arg-type]


def test_context_from_future_refused_before_tower_for_incremental_context(tmp_path: Path) -> None:
    history = _far_history(calm_count=20)
    real_client = _client()
    result = real_client.observe(bars=history, restore_snapshot_blob=None, wall_clock_now=time.time())
    assert not result.rejected and result.result is not None

    market_ts = history[-1].ts_close
    context = context_refresh_loop_incremental._to_cached_upstream_context(result.result, atr=2.0, entry_price=2400.0)
    assert context.market_timestamp == market_ts

    worker = _FakeWorker(n2_output=_COMPLETE_N2_OUTPUT, n3_output=_COMPLETE_N3_OUTPUT, n4_output=_COMPLETE_N4_OUTPUT)
    try:
        m5_ts = market_ts - 300  # the M5 bar closes BEFORE the incremental context's own M15 close
        tower = _tower_for(worker, now=market_ts)
        m5_gateway = FakeNewBrainLiveGateway(rates=())
        state_store = SqliteStateStore(tmp_path / "state.db")
        from ai_trader.risk_manager_live.circuit_breaker import persist_circuit_state
        from ai_trader.risk_manager_live.types import TradingCircuitState
        from ai_trader.risk_manager.types import EngineState
        persist_circuit_state(state_store, TradingCircuitState(state=EngineState.READY, reason_code="OK", since=m5_ts), m5_ts)

        feed = LiveBarFeed(
            FakeNewBrainLiveGateway(rates=(_raw_rate(ts_close=m5_ts),)), SYMBOL, 5, 300, state_store=state_store,
        )
        ctx_store = UpstreamContextStore(state_store)
        ctx_store.record(context)
        from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder
        from ai_trader.new_brain_live.deps import NewBrainLiveDepsFactory
        from ai_trader.new_brain_bridge.telemetry import NewBrainTelemetryLog
        from ai_trader.new_brain_live.live_shadow_journal import LiveShadowCategory, LiveShadowJournal

        deps_factory = NewBrainLiveDepsFactory(SYMBOL, m5_gateway, tmp_path)
        telemetry_log = NewBrainTelemetryLog(state_store)
        shadow_journal = LiveShadowJournal(state_store)
        loop = M5DecisionLoop(
            feed=feed, context_store=ctx_store, tower=tower, deps_factory=deps_factory, state_store=state_store,
            telemetry_log=telemetry_log, shadow_journal=shadow_journal,
        )
        loop.tick()
        assert worker.connection_count == 0, "a from-the-future context must never reach the tower"
        assert len(shadow_journal.entries) == len(ve_brain.CANONICAL_STRATEGIES)
        assert all(e.terminal_reason_code == "CONTEXT_FROM_FUTURE" for e in shadow_journal.entries)
        state_store.close()
    finally:
        worker.stop()


@dataclasses.dataclass
class _RawRate:
    time: int
    open: float
    high: float
    low: float
    close: float
    tick_volume: float = 100.0


def _raw_rate(*, ts_close: int, price: float = 2400.0) -> _RawRate:
    return _RawRate(time=ts_close - 300, open=price, high=price + 0.3, low=price - 0.3, close=price + 0.05)


# ═══ 4 — request-scoped time, never a frozen "now" ═══

def test_request_scoped_time_not_frozen() -> None:
    history = _far_history(calm_count=5)
    fresh = time.time()
    old_bar_close = int(fresh) - 10_000_000  # bars anchored far in the past relative to `fresh`
    aged_bars = tuple(
        dataclasses.replace(b, ts_open=b.ts_open + old_bar_close, ts_close=b.ts_close + old_bar_close)
        for b in history
    )

    client = _client(max_staleness_seconds=3600.0)
    stale_call = client.observe(bars=aged_bars, restore_snapshot_blob=None, wall_clock_now=fresh)
    assert stale_call.rejected is True
    assert stale_call.rejection_reason is not None and "StaleStateError" in stale_call.rejection_reason

    fresh_wall_clock = aged_bars[-1].ts_close + 10  # freshly computed relative to the bars' OWN clock
    fresh_call = client.observe(bars=aged_bars, restore_snapshot_blob=None, wall_clock_now=fresh_wall_clock)
    assert fresh_call.rejected is False, (
        "a freshly-computed wall_clock_now (not the cached value from the first call) must succeed -- "
        "proves wall_clock_now is genuinely read per-call, never frozen at client construction"
    )


# ═══ 5 — dedup and journal/watermark continuity ═══

def test_dedup_and_watermark_continuity_across_ticks(tmp_path: Path) -> None:
    history = _far_history(calm_count=5)
    state_store = SqliteStateStore(tmp_path / "state.db")
    gateway = FakeNewBrainLiveGateway(rates=tuple(
        _RawRate(time=b.ts_open, open=b.open, high=b.high, low=b.low, close=b.close) for b in history
    ))
    feed = LiveBarFeed(gateway, SYMBOL, _MT5_TIMEFRAME, _BAR_SECONDS, state_store=state_store, watermark_key_suffix="test")
    context_store = UpstreamContextStore(state_store)
    snap_store = N1IncrementalSnapshotStore(state_store)
    loop = IncrementalContextRefreshLoop(
        feed=feed, client=_client(), context_store=context_store, snapshot_store=snap_store,
    )

    first_count = loop.tick()
    assert first_count == len(history)
    first_context = context_store.latest()
    first_snapshot = snap_store.latest()
    assert first_context is not None and first_snapshot is not None

    second_count = loop.tick()
    assert second_count == 0, "no new bars -- must process nothing"
    assert context_store.latest() == first_context
    assert snap_store.latest() == first_snapshot
    state_store.close()


# ═══ 6 — worker/snapshot/identity mismatch -> NO_TRADE (context left untouched) ═══

def test_identity_mismatch_leaves_context_store_untouched(tmp_path: Path) -> None:
    history = _far_history(calm_count=5)
    state_store = SqliteStateStore(tmp_path / "state.db")
    gateway = FakeNewBrainLiveGateway(rates=tuple(
        _RawRate(time=b.ts_open, open=b.open, high=b.high, low=b.low, close=b.close) for b in history
    ))
    feed = LiveBarFeed(gateway, SYMBOL, _MT5_TIMEFRAME, _BAR_SECONDS, state_store=state_store)
    context_store = UpstreamContextStore(state_store)
    snap_store = N1IncrementalSnapshotStore(state_store)

    client_a = _client(implementation_commit="commit-a")
    loop_a = IncrementalContextRefreshLoop(feed=feed, client=client_a, context_store=context_store, snapshot_store=snap_store)
    loop_a.tick()
    assert context_store.latest() is not None
    context_after_a = context_store.latest()

    future_bars = _calm_bars_after(count=1, start_index=len(history), start_price=history[-1].close)
    gateway._rates = gateway._rates + tuple(
        _RawRate(time=b.ts_open, open=b.open, high=b.high, low=b.low, close=b.close) for b in future_bars
    )
    client_b = _client(implementation_commit="commit-b-different")  # identity mismatch on restore
    loop_b = IncrementalContextRefreshLoop(feed=feed, client=client_b, context_store=context_store, snapshot_store=snap_store)
    consumed = loop_b.tick()
    assert consumed == 0, "an identity-mismatched restore must be rejected, never silently accepted"
    assert context_store.latest() == context_after_a, "context store must be left untouched on rejection"
    state_store.close()


# ═══ 7 — broker gate blocked, order_send never reachable (structural) ═══

def _source_excluding_docstrings(source: str) -> str:
    import ast

    tree = ast.parse(source)
    lines = source.splitlines()
    keep = [True] * len(lines)
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            start = node.lineno - 1
            end = (node.end_lineno or node.lineno) - 1
            for i in range(start, end + 1):
                keep[i] = False
    return "\n".join(line for line, k in zip(lines, keep) if k)


def test_n1_incremental_never_references_broker_or_decision_modules() -> None:
    """`worker_script.py` is read directly from disk, NEVER imported here -- it is not importable in the
    main venv at all (`ve_n1_replay` is deliberately absent from it), which is itself the isolation
    guarantee this test exists to check."""
    forbidden = (
        "decide_n6", "DecisionRequest", "risk_gate", "execution_shadow",
        "BrokerOrderSubmissionGate", "order_send", "submit_new_brain_candidate",
    )
    worker_script_path = Path(__file__).resolve().parent.parent / "worker_script.py"
    sources = [
        inspect.getsource(m) for m in (
            client_module, hydrate, context_refresh_loop_incremental, snapshot_store_module,
            artifact_pin, n1_incremental,
        )
    ]
    sources.append(worker_script_path.read_text(encoding="utf-8"))
    for source in sources:
        code_only = _source_excluding_docstrings(source)
        for name in forbidden:
            assert name not in code_only, f"forbidden reference {name!r} found"


def test_artifact_pin_matches_ceo_authorized_values() -> None:
    result = artifact_pin.verify_pin()
    assert result.ok, result.reason
    assert result.recorded_sha256 == artifact_pin.PINNED_WHEEL_SHA256
    assert artifact_pin.PINNED_WHEEL_SHA256 == "2cff7e7be1f9401c10753f751a1189a512f5be39946dfada4260b9c5e1cd29ab"
    assert artifact_pin.PINNED_DELIVERY_COMMIT == "e118c33"
    assert artifact_pin.PINNED_RT_PASS_COMMIT == "6230ee5"
