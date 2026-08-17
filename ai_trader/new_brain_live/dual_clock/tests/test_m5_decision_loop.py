"""`M5DecisionLoop` decisive tests -- RT-TIME-0001 section B. Fakes only (no real MT5 terminal, no real
tower worker beyond the same in-process `_FakeWorker` `test_bridge_tower_wiring.py` already established
and proved speaks the real wire protocol); LIVE_SHADOW is never touched by anything in this file.

Reuses real fixtures rather than reimplementing them: `trend_up_regime_bars` (a real, already-verified
TREND_UP-resolving bar sequence) for the "genuinely eligible" path, and `_FakeWorker`/`_client_for`/
`_FakeTimeframeAwareGateway`/`_closed_rates`/`_COMPLETE_N2/N3/N4_OUTPUT` (the same in-process fake tower
worker `test_bridge_tower_wiring.py` uses for `evaluate_bar` itself) for the M5-triggered tower call --
so these tests prove the M5 path reaches the SAME real machinery `evaluate_bar` does, not a parallel
double that could silently drift."""

from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import Any

import ve_brain  # type: ignore[import-untyped]

from ai_trader.live_signal_source.bar_feed import LiveBarFeed
from ai_trader.mandate2_readiness.broker_gate import BrokerOrderSubmissionGate
from ai_trader.new_brain_bridge.authority import DecisionAuthority
from ai_trader.new_brain_bridge.bridge import TowerDependencies
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder
from ai_trader.new_brain_bridge.telemetry import NewBrainTelemetryLog
from ai_trader.new_brain_bridge.tests.conftest import CALM_PREFIX_BARS, trend_up_regime_bars
from ai_trader.new_brain_bridge.tests.test_bridge_tower_wiring import (
    _COMPLETE_N2_OUTPUT,
    _COMPLETE_N3_OUTPUT,
    _COMPLETE_N4_OUTPUT,
    _FakeTimeframeAwareGateway,
    _FakeWorker,
    _client_for,
    _closed_rates,
)
from ai_trader.new_brain_live.deps import NewBrainLiveDepsFactory
from ai_trader.new_brain_live.dual_clock.context_refresh_loop import ContextRefreshLoop
from ai_trader.new_brain_live.dual_clock.m5_decision_loop import M5DecisionLoop
from ai_trader.new_brain_live.dual_clock.upstream_context import CachedUpstreamContext, UpstreamContextStore, build_context
from ai_trader.new_brain_live.live_shadow_journal import LiveShadowCategory, LiveShadowJournal
from ai_trader.new_brain_live.tests._fixtures import SYMBOL, FakeNewBrainLiveGateway
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.risk_manager_live.circuit_breaker import persist_circuit_state
from ai_trader.risk_manager_live.types import TradingCircuitState
from ai_trader.risk_manager.types import EngineState

_M15_TIMEFRAME = 15
_M5_TIMEFRAME = 5
_M5_BAR_SECONDS = 300


@dataclasses.dataclass
class _RawRate:
    time: int
    open: float
    high: float
    low: float
    close: float
    tick_volume: float = 100.0


def _real_eligible_context() -> tuple[CachedUpstreamContext, int]:
    """The SAME real recipe `build_context` (and, underneath it, `bridge.evaluate_bar`) uses, fed the
    real `trend_up_regime_bars()` fixture -- independently verified elsewhere to resolve `trend_pullback`
    into an eligible TREND_UP decision. Returns the context plus its own `market_timestamp` (the M15
    bar's `ts_close` it was built from), so callers can place M5 bars precisely relative to it."""
    bars = trend_up_regime_bars(SYMBOL)
    builder = RawAxesBuilder(SYMBOL)
    for bar in bars[:-1]:
        builder.observe(bar)
    last_bar = bars[-1]
    context = build_context(symbol=SYMBOL, timeframe="M15", bar=last_bar, axes_builder=builder)
    assert any(d.eligible for d in context.eligibility_decisions), (  # type: ignore[attr-defined]
        "fixture regression: trend_up_regime_bars() must still resolve at least one eligible strategy"
    )
    return context, last_bar.ts_close


def _manual_ineligible_context(*, market_timestamp: int) -> CachedUpstreamContext:
    """Hand-built, all-strategies-INELIGIBLE context -- the same kind of white-box fixture
    `test_entrypoint.py`'s own `_no_trade_outcome()`/`_trade_outcome()` already establishes as this
    project's convention for isolating one module's branching logic from another's (Router's real
    regime-resolution is already exhaustively tested elsewhere)."""
    market_event_id = f"{SYMBOL}:M15:{market_timestamp}"
    axes = ve_brain.RawAxes(
        is_compressed=True, is_displacement=False, direction=None, structure=None,
        volatility_state="normal", n1_contract_version=ve_brain.N1_CONTRACT_VERSION,
        raw_axis_schema_version=ve_brain.RAW_AXIS_SCHEMA_VERSION,
    )
    decisions = tuple(
        ve_brain.EligibilityDecision(
            strategy_id=canon.strategy_id, strategy_version=canon.strategy_version,
            market_event_id=market_event_id, regime_fingerprint="uncertain-fp",
            router_version=ve_brain.ROUTER_VERSION, eligible=False, mode=ve_brain.RoutingMode.INELIGIBLE,
            matched_regimes=(), reason_codes=("UNCERTAIN_REGIME",),
        )
        for canon in ve_brain.CANONICAL_STRATEGIES
    )
    context = CachedUpstreamContext(
        context_id="", symbol=SYMBOL, timeframe="M15", market_event_id=market_event_id,
        market_timestamp=market_timestamp, n1_output_fp="manual-uncertain-fp",
        regime_axes_status=("unavailable", "unavailable", "unavailable", "unavailable"),
        router_bias_direction=None, confidence=1.0, axes=axes, eligibility_decisions=decisions,
        atr=2.0, entry_price=2400.0,
    )
    return context


def _m5_rate(*, ts_close: int, price: float = 2400.0) -> _RawRate:
    return _RawRate(time=ts_close - _M5_BAR_SECONDS, open=price, high=price + 0.3, low=price - 0.3, close=price + 0.05)


def _make_loop(
    tmp_path: Path, *, context: CachedUpstreamContext | None, m5_bar_ts_close: int,
    tower: TowerDependencies, authority: DecisionAuthority | None = DecisionAuthority.NEW_BRAIN,
    gate: BrokerOrderSubmissionGate = BrokerOrderSubmissionGate(),
) -> tuple[M5DecisionLoop, LiveShadowJournal, NewBrainTelemetryLog, SqliteStateStore, UpstreamContextStore]:
    m5_gateway = FakeNewBrainLiveGateway(rates=(_m5_rate(ts_close=m5_bar_ts_close),))
    state_store = SqliteStateStore(tmp_path / "state.db")
    persist_circuit_state(
        state_store, TradingCircuitState(state=EngineState.READY, reason_code="OK", since=m5_bar_ts_close),
        m5_bar_ts_close,
    )
    feed = LiveBarFeed(m5_gateway, SYMBOL, _M5_TIMEFRAME, _M5_BAR_SECONDS, state_store=state_store)
    context_store = UpstreamContextStore(state_store)
    if context is not None:
        context_store.record(context)
    deps_factory = NewBrainLiveDepsFactory(SYMBOL, m5_gateway, tmp_path)
    telemetry_log = NewBrainTelemetryLog(state_store)
    shadow_journal = LiveShadowJournal(state_store)

    loop = M5DecisionLoop(
        feed=feed, context_store=context_store, tower=tower, deps_factory=deps_factory,
        state_store=state_store, telemetry_log=telemetry_log, shadow_journal=shadow_journal,
        authority_check=None if authority is None else (lambda: authority), gate=gate,
    )
    return loop, shadow_journal, telemetry_log, state_store, context_store


def _tower_for(worker: _FakeWorker, *, now: int) -> TowerDependencies:
    gateway = _FakeTimeframeAwareGateway(
        h1_rates=_closed_rates(count=150, step=3600, now=now, start_price=1990.0),
        m15_rates=_closed_rates(count=150, step=900, now=now, start_price=2000.0),
        m5_rates=_closed_rates(count=150, step=300, now=now, start_price=2010.0),
    )
    return TowerDependencies(client=_client_for(worker), gateway=gateway)  # type: ignore[arg-type]


def test_missing_context_is_no_trade_for_every_strategy_and_never_touches_tower(tmp_path: Path) -> None:
    worker = _FakeWorker(n2_output=_COMPLETE_N2_OUTPUT, n3_output=_COMPLETE_N3_OUTPUT, n4_output=_COMPLETE_N4_OUTPUT)
    try:
        m5_ts = 1_000_000
        tower = _tower_for(worker, now=m5_ts)
        loop, journal, _telemetry, store, _ctx_store = _make_loop(
            tmp_path, context=None, m5_bar_ts_close=m5_ts, tower=tower,
        )
        ran = loop.tick()
        assert ran is True
        assert loop.events_processed == len(ve_brain.CANONICAL_STRATEGIES)
        assert len(journal.entries) == len(ve_brain.CANONICAL_STRATEGIES)
        assert all(e.category is LiveShadowCategory.LIVE_SHADOW_NO_TRADE for e in journal.entries)
        assert all(e.terminal_reason_code == "CONTEXT_STALE" for e in journal.entries)
        assert worker.connection_count == 0, "tower must never be contacted with no cached context"
        store.close()
    finally:
        worker.stop()


def test_context_older_than_staleness_threshold_is_no_trade(tmp_path: Path) -> None:
    context, market_ts = _real_eligible_context()
    worker = _FakeWorker(n2_output=_COMPLETE_N2_OUTPUT, n3_output=_COMPLETE_N3_OUTPUT, n4_output=_COMPLETE_N4_OUTPUT)
    try:
        m5_ts = market_ts + (2 * 900) + 1  # one second past the default 2-M15-bar staleness window
        tower = _tower_for(worker, now=m5_ts)
        loop, journal, _telemetry, store, _ctx_store = _make_loop(
            tmp_path, context=context, m5_bar_ts_close=m5_ts, tower=tower,
        )
        loop.tick()
        assert all(e.terminal_reason_code == "CONTEXT_STALE" for e in journal.entries)
        assert worker.connection_count == 0
        store.close()
    finally:
        worker.stop()


def test_context_from_the_future_is_rejected_not_silently_accepted(tmp_path: Path) -> None:
    """RT-TIME-0001's own zero-lookahead requirement: a cached M15 context whose own `market_timestamp`
    is AFTER the M5 bar being evaluated must never be used -- this is the fail-closed branch added
    directly in response to reading `_process_m5_bar`'s original staleness check, which only bounded
    context age from above (too old) and would have silently treated a negative age as valid."""
    context, market_ts = _real_eligible_context()
    worker = _FakeWorker(n2_output=_COMPLETE_N2_OUTPUT, n3_output=_COMPLETE_N3_OUTPUT, n4_output=_COMPLETE_N4_OUTPUT)
    try:
        m5_ts = market_ts - _M5_BAR_SECONDS  # the M5 bar closes BEFORE the cached M15 context's own close
        tower = _tower_for(worker, now=market_ts)
        loop, journal, _telemetry, store, _ctx_store = _make_loop(
            tmp_path, context=context, m5_bar_ts_close=m5_ts, tower=tower,
        )
        loop.tick()
        assert len(journal.entries) == len(ve_brain.CANONICAL_STRATEGIES)
        assert all(e.category is LiveShadowCategory.LIVE_SHADOW_NO_TRADE for e in journal.entries)
        assert all(e.terminal_reason_code == "CONTEXT_FROM_FUTURE" for e in journal.entries)
        assert worker.connection_count == 0, "a from-the-future context must never reach the tower"
        store.close()
    finally:
        worker.stop()


def test_router_ineligible_strategy_is_no_trade_and_never_touches_tower(tmp_path: Path) -> None:
    market_ts = 500_000
    context = _manual_ineligible_context(market_timestamp=market_ts)
    worker = _FakeWorker(n2_output=_COMPLETE_N2_OUTPUT, n3_output=_COMPLETE_N3_OUTPUT, n4_output=_COMPLETE_N4_OUTPUT)
    try:
        m5_ts = market_ts + _M5_BAR_SECONDS
        tower = _tower_for(worker, now=m5_ts)
        loop, journal, _telemetry, store, _ctx_store = _make_loop(
            tmp_path, context=context, m5_bar_ts_close=m5_ts, tower=tower,
        )
        loop.tick()
        assert len(journal.entries) == len(ve_brain.CANONICAL_STRATEGIES)
        assert all(e.category is LiveShadowCategory.LIVE_SHADOW_NO_TRADE for e in journal.entries)
        assert all(e.terminal_reason_code == "NO_DECISION" for e in journal.entries)
        assert worker.connection_count == 0, "an ineligible strategy must never reach the tower"
        store.close()
    finally:
        worker.stop()


def test_eligible_context_reaches_the_real_tower_chain_with_real_n2_n3_n4_traces(tmp_path: Path) -> None:
    """The decisive chain-binding proof: an M5-triggered evaluation of a genuinely eligible strategy
    reaches `bridge.query_tower_chain` -- the SAME function `evaluate_bar` uses -- and the resulting
    telemetry carries real TowerN2/TowerN3/TowerN4 traces sourced from the real (fake-server) wire
    response, not a fabricated or cached substitute."""
    context, market_ts = _real_eligible_context()
    worker = _FakeWorker(n2_output=_COMPLETE_N2_OUTPUT, n3_output=_COMPLETE_N3_OUTPUT, n4_output=_COMPLETE_N4_OUTPUT)
    try:
        m5_ts = market_ts + _M5_BAR_SECONDS
        tower = _tower_for(worker, now=m5_ts)
        loop, journal, telemetry, store, _ctx_store = _make_loop(
            tmp_path, context=context, m5_bar_ts_close=m5_ts, tower=tower,
        )
        loop.tick()

        assert worker.connection_count == 1, "expected exactly one real tower connection for the eligible strategy"
        node_names_seen = {t.node_name for record in telemetry.entries for t in record.node_traces}
        assert {"N1", "Router", "TowerN2", "TowerN3", "TowerN4", "CostModel", "EV", "N6"} <= node_names_seen
        eligible_outcomes = [
            record for record in telemetry.entries
            if any(t.node_name == "TowerN2" for t in record.node_traces)
        ]
        assert eligible_outcomes, "expected at least one outcome to have actually reached the tower nodes"
        n2_trace = next(t for t in eligible_outcomes[0].node_traces if t.node_name == "TowerN2")
        n3_trace = next(t for t in eligible_outcomes[0].node_traces if t.node_name == "TowerN3")
        n4_trace = next(t for t in eligible_outcomes[0].node_traces if t.node_name == "TowerN4")
        assert n2_trace.input_fingerprint == "n2-node-input-fp"
        assert n3_trace.input_fingerprint == "n3-node-input-fp"
        assert n4_trace.input_fingerprint == "n4-node-input-fp"
        assert len({n2_trace.input_fingerprint, n3_trace.input_fingerprint, n4_trace.input_fingerprint}) == 3
        # every M5 event_identity/market_event_id must be M5-precision, distinct from the M15 context's own
        assert eligible_outcomes[0].event_identity.timeframe == "M5"
        assert eligible_outcomes[0].event_identity.market_event_id != context.market_event_id
        assert journal.entries, "the M5 evaluation must be journaled regardless of the final decision"
        store.close()
    finally:
        worker.stop()


def test_legacy_authority_never_reaches_the_tower(tmp_path: Path) -> None:
    """CEO's own rule, mirrored from the M15 loop: a process without NEW_BRAIN authority demotes to
    LEGACY_SHADOW_TELEMETRY and must never contact the tower, even for a genuinely eligible strategy."""
    context, market_ts = _real_eligible_context()
    worker = _FakeWorker(n2_output=_COMPLETE_N2_OUTPUT, n3_output=_COMPLETE_N3_OUTPUT, n4_output=_COMPLETE_N4_OUTPUT)
    try:
        m5_ts = market_ts + _M5_BAR_SECONDS
        tower = _tower_for(worker, now=m5_ts)
        loop, journal, _telemetry, store, _ctx_store = _make_loop(
            tmp_path, context=context, m5_bar_ts_close=m5_ts, tower=tower, authority=DecisionAuthority.LEGACY,
        )
        loop.tick()
        assert worker.connection_count == 0, "LEGACY authority must never reach the tower"
        legacy_entries = [e for e in journal.entries if e.category is LiveShadowCategory.LIVE_SHADOW_EVENT]
        assert legacy_entries, "expected at least one LEGACY_SHADOW_TELEMETRY entry for the eligible strategy"
        assert legacy_entries[0].terminal_reason_code == "LEGACY_SHADOW_TELEMETRY_AUTHORITY_NOT_NEW_BRAIN"
        store.close()
    finally:
        worker.stop()


def test_broker_gate_default_is_never_enabled(tmp_path: Path) -> None:
    """Structural proof, mirroring `test_entrypoint.py`'s own equivalent: the M5 loop's default `gate`
    parameter is a fresh, default-closed `BrokerOrderSubmissionGate` -- never silently enabled."""
    worker = _FakeWorker(n2_output=None, n3_output=None, n4_output=None)
    try:
        loop, _journal, _telemetry, store, _ctx_store = _make_loop(
            tmp_path, context=None, m5_bar_ts_close=1_000_000, tower=_tower_for(worker, now=1_000_000),
        )
        assert loop._gate.enabled is False  # noqa: SLF001 -- deliberate internal-state check
        store.close()
    finally:
        worker.stop()


def test_reached_broker_gate_candidate_is_blocked_with_zero_order_send_calls(tmp_path: Path) -> None:
    """If N6 ever produces a real trade candidate for an M5-triggered event, `attempt_shadow_execution`'s
    own default-disabled gate must block it before any broker call -- `order_send_calls`/`orders_created`/
    `positions_created` must all read 0 in the journaled record whenever the candidate reached the gate."""
    context, market_ts = _real_eligible_context()
    worker = _FakeWorker(n2_output=_COMPLETE_N2_OUTPUT, n3_output=_COMPLETE_N3_OUTPUT, n4_output=_COMPLETE_N4_OUTPUT)
    try:
        m5_ts = market_ts + _M5_BAR_SECONDS
        tower = _tower_for(worker, now=m5_ts)
        loop, journal, _telemetry, store, _ctx_store = _make_loop(
            tmp_path, context=context, m5_bar_ts_close=m5_ts, tower=tower,
        )
        loop.tick()
        gated_entries = [e for e in journal.entries if e.reached_broker_gate is not None]
        for entry in gated_entries:
            assert entry.order_send_calls == 0
            assert entry.orders_created == 0
            assert entry.positions_created == 0
            if entry.reached_broker_gate:
                assert entry.broker_blocked is True, "the default-disabled gate must block, never pass through"
        store.close()
    finally:
        worker.stop()


def test_second_tick_with_no_new_bar_produces_zero_new_evaluations(tmp_path: Path) -> None:
    """`LiveBarFeed`'s own watermark dedup -- proven elsewhere in isolation -- must genuinely prevent the
    M5 loop from re-evaluating the same closed bar twice, including across a fresh `tick()` call."""
    worker = _FakeWorker(n2_output=None, n3_output=None, n4_output=None)
    try:
        m5_ts = 900_000
        tower = _tower_for(worker, now=m5_ts)
        context = _manual_ineligible_context(market_timestamp=m5_ts - _M5_BAR_SECONDS)
        loop, journal, _telemetry, store, _ctx_store = _make_loop(
            tmp_path, context=context, m5_bar_ts_close=m5_ts, tower=tower,
        )
        loop.tick()
        first_count = loop.events_processed
        first_journal_len = len(journal.entries)
        assert first_count > 0

        loop.tick()  # same underlying gateway rates, nothing new closed
        assert loop.events_processed == first_count, "a second tick with no new bar must process nothing new"
        assert len(journal.entries) == first_journal_len
        store.close()
    finally:
        worker.stop()


def test_context_refresh_loop_and_main_m15_loop_use_independent_watermarks(tmp_path: Path) -> None:
    """The CEO's explicit "N1/context watermark" requirement: `ContextRefreshLoop`'s own `LiveBarFeed`
    (built with `watermark_key_suffix="dual_clock_context"`) must never share dedup state with a SEPARATE
    `LiveBarFeed` polling the identical `(symbol, mt5_timeframe=15)` pair -- representing the main M15
    decision loop's own, pre-existing watermark."""
    bars = trend_up_regime_bars(SYMBOL)
    last_bar = bars[-1]
    m15_gateway = FakeNewBrainLiveGateway(rates=(
        _RawRate(time=last_bar.ts_open, open=last_bar.open, high=last_bar.high, low=last_bar.low, close=last_bar.close),
    ))
    state_store = SqliteStateStore(tmp_path / "state.db")

    main_loop_feed = LiveBarFeed(m15_gateway, SYMBOL, _M15_TIMEFRAME, 900, state_store=state_store)
    context_feed = LiveBarFeed(
        m15_gateway, SYMBOL, _M15_TIMEFRAME, 900, state_store=state_store, watermark_key_suffix="dual_clock_context",
    )

    context_store = UpstreamContextStore(state_store)
    axes_builder = RawAxesBuilder(SYMBOL)
    for bar in bars[:-1]:
        axes_builder.observe(bar)
    refresh_loop = ContextRefreshLoop(feed=context_feed, axes_builder=axes_builder, context_store=context_store)

    consumed = refresh_loop.tick()
    assert consumed == 1
    context = context_store.latest()
    assert context is not None
    assert context.market_timestamp == last_bar.ts_close

    # The main M15 loop's own, SEPARATE feed must still see the same bar as unconsumed -- proof the two
    # watermarks never collided.
    still_pending = main_loop_feed.poll()
    assert len(still_pending) == 1
    assert still_pending[0].ts_close == last_bar.ts_close
    state_store.close()


def test_upstream_context_serialization_round_trip(tmp_path: Path) -> None:
    context, _market_ts = _real_eligible_context()
    state_store = SqliteStateStore(tmp_path / "state.db")
    store = UpstreamContextStore(state_store)
    store.record(context)
    restored = store.latest()
    assert restored is not None
    assert restored.context_id == context.context_id
    assert restored.context_id != ""
    assert restored.market_timestamp == context.market_timestamp
    assert restored.n1_output_fp == context.n1_output_fp
    assert restored.atr == context.atr
    assert restored.entry_price == context.entry_price
    assert len(restored.eligibility_decisions) == len(context.eligibility_decisions)
    original_by_id = {d.strategy_id: d for d in context.eligibility_decisions}  # type: ignore[attr-defined]
    for restored_decision in restored.eligibility_decisions:
        original = original_by_id[restored_decision.strategy_id]  # type: ignore[attr-defined]
        assert restored_decision.eligible == original.eligible  # type: ignore[attr-defined]
        assert restored_decision.mode == original.mode  # type: ignore[attr-defined]
        assert restored_decision.reason_codes == original.reason_codes  # type: ignore[attr-defined]
    state_store.close()
