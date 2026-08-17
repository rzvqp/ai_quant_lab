"""RT-TIME-0001 section A ("REQUEST-SCOPED TIME FIX") decisive tests -- proves
`TowerDependencies.now` (captured once at process start, the exact defect `LIVE_SHADOW_TIMEFRAME_AUDIT.md`
found) is gone, and that bar-fetch data selection is anchored to `event_as_of`/`data_cutoff` (the bar
actually being evaluated), never to `wall_clock_now` and never to a value frozen at construction time.

Tests `_query_tower_chain` directly (a private helper, same convention `test_bridge_tower_wiring.py`
already establishes by importing `_fp`/`_side_provenance` directly) -- this is the exact function the
frozen-`now` defect lived in, so unit-level precision here is more decisive than routing everything
through `evaluate_bar`. Reuses `test_bridge_tower_wiring.py`'s own `_FakeWorker`/`_client_for`/
`_default_gateway`/`_COMPLETE_N*_OUTPUT` fixtures -- a genuine `TowerClient` speaking the real wire
protocol, not a duck-typed double."""

from __future__ import annotations

from typing import Callable

import pytest

from ai_trader.new_brain_bridge.bridge import TowerDependencies, _ChainQueryResult, _query_tower_chain
from ai_trader.new_brain_bridge.tests.test_bridge_tower_wiring import (
    _COMPLETE_N2_OUTPUT,
    _COMPLETE_N3_OUTPUT,
    _COMPLETE_N4_OUTPUT,
    _FakeTimeframeAwareGateway,
    _FakeWorker,
    _client_for,
    _closed_rates,
    _default_gateway,
)
from ai_trader.new_brain_bridge.wall_clock import ClockRollbackError, MonotonicWallClock

_SYMBOL = "XAUUSD"
_EVENT_AS_OF = 478 * 900  # matches `test_bridge_tower_wiring._LAST_BAR_TS_CLOSE`


def _tower(
    gateway: _FakeTimeframeAwareGateway, worker: _FakeWorker, *, wall_clock_provider: Callable[[], float],
) -> TowerDependencies:
    return TowerDependencies(
        client=_client_for(worker), gateway=gateway,  # type: ignore[arg-type]
        wall_clock_provider=wall_clock_provider,
    )


def _call(tower: TowerDependencies, *, event_as_of: int, data_cutoff: int | None = None) -> _ChainQueryResult:
    return _query_tower_chain(
        tower, market_event_id=f"{_SYMBOL}:M15:{event_as_of}", trace_id="trace-1", symbol=_SYMBOL,
        event_as_of=event_as_of, data_cutoff=data_cutoff if data_cutoff is not None else event_as_of,
        configuration_fingerprint="cfg-1", n1_fingerprint="n1-fp",
        regime_axes_status=("available", "available", "available", "available"),
        strategy_id="trend_pullback", strategy_version="v1", side=1,
    )


def _successful_worker() -> _FakeWorker:
    return _FakeWorker(n2_output=_COMPLETE_N2_OUTPUT, n3_output=_COMPLETE_N3_OUTPUT, n4_output=_COMPLETE_N4_OUTPUT)


# ── 1/2/3: process uptime (10min / 30min / 2h) never artificially staleness -- the core proof this ──
#           whole remediation exists for: `wall_clock_now` advancing far past `event_as_of` must NEVER
#           make the bar fetch itself look stale, because the fetch is anchored to `event_as_of`, not to
#           `wall_clock_now` and not to a value frozen at construction time.


@pytest.mark.parametrize("uptime_seconds", [10 * 60, 30 * 60, 2 * 3600], ids=["10min", "30min", "2h"])
def test_process_uptime_never_artificially_stales_the_fetch(uptime_seconds: int) -> None:
    worker = _successful_worker()
    try:
        gateway = _default_gateway(now=_EVENT_AS_OF)  # bars genuinely fresh AS OF the event
        tower = _tower(gateway, worker, wall_clock_provider=lambda: _EVENT_AS_OF + uptime_seconds)

        result = _call(tower, event_as_of=_EVENT_AS_OF)

        assert result.bias_available is True
        assert result.market_map_available is True
        assert result.confirmation_available is True
        assert not any("STALE" in code for code in result.reason_codes)
        assert result.staleness_reason_h1 is not None and result.staleness_reason_h1.startswith("OK:")
        assert result.staleness_reason_m15 is not None and result.staleness_reason_m15.startswith("OK:")
        assert result.staleness_reason_m5 is not None and result.staleness_reason_m5.startswith("OK:")
        assert result.wall_clock_now == _EVENT_AS_OF + uptime_seconds
        assert result.data_cutoff == _EVENT_AS_OF  # NEVER the advanced wall clock
    finally:
        worker.stop()


# ── 4: fake clock advanced WITHOUT reconstructing TowerDependencies ──────────────────────────────────


def test_fake_clock_advances_without_reconstructing_tower_dependencies() -> None:
    """The SAME `TowerDependencies` instance (never rebuilt, exactly like the real long-running process
    never rebuilds it either) sees `wall_clock_now` genuinely advance across two calls -- proving the
    fix is a live, per-call read, not something that only works if you happen to reconstruct the object."""
    worker = _successful_worker()
    try:
        gateway = _default_gateway(now=_EVENT_AS_OF)
        clock_value = [_EVENT_AS_OF]
        tower = _tower(gateway, worker, wall_clock_provider=lambda: clock_value[0])

        first = _call(tower, event_as_of=_EVENT_AS_OF)
        assert first.wall_clock_now == _EVENT_AS_OF

        clock_value[0] = _EVENT_AS_OF + 3600  # advance, no new TowerDependencies constructed
        second = _call(tower, event_as_of=_EVENT_AS_OF)
        assert second.wall_clock_now == _EVENT_AS_OF + 3600
        assert second.data_cutoff == first.data_cutoff == _EVENT_AS_OF  # data anchor unaffected
    finally:
        worker.stop()


# ── 5: historical catch-up -- zero lookahead ──────────────────────────────────────────────────────────


def test_historical_catchup_never_sees_bars_after_its_own_event_as_of() -> None:
    """An OLD event, processed long after the fact (wall clock far ahead) -- the fetch must still be
    anchored to THAT event's own `event_as_of`, never to "now", proving a catch-up sweep can never look
    ahead of the specific bar it is currently replaying."""
    worker = _successful_worker()
    old_event_as_of = 100 * 900
    try:
        gateway = _default_gateway(now=old_event_as_of)
        tower = _tower(gateway, worker, wall_clock_provider=lambda: old_event_as_of + 30 * 24 * 3600)  # 30 days later

        _call(tower, event_as_of=old_event_as_of)

        assert gateway.copy_rates_from_calls, "expected the gateway to be queried"
        for _symbol, _timeframe, date_from, _count in gateway.copy_rates_from_calls:
            assert date_from == old_event_as_of, (
                f"bar fetch anchor {date_from} must equal the event's own as_of {old_event_as_of}, "
                "never wall-clock 'now'"
            )
    finally:
        worker.stop()


# ── 6: different event_as_of -> bars and identity both advance ──────────────────────────────────────


def test_different_event_as_of_advances_both_the_fetch_anchor_and_the_identity() -> None:
    worker = _successful_worker()
    try:
        event_a = 200 * 900
        event_b = 201 * 900
        gateway = _FakeTimeframeAwareGateway(
            h1_rates=_closed_rates(count=150, step=3600, now=event_b, start_price=1990.0),
            m15_rates=_closed_rates(count=150, step=900, now=event_b, start_price=2000.0),
            m5_rates=_closed_rates(count=150, step=300, now=event_b, start_price=2010.0),
        )
        tower = _tower(gateway, worker, wall_clock_provider=lambda: event_b + 60)

        result_a = _call(tower, event_as_of=event_a)
        result_b = _call(tower, event_as_of=event_b)

        assert result_a.event_as_of == event_a
        assert result_b.event_as_of == event_b
        assert result_a.data_cutoff != result_b.data_cutoff
        anchors = [call[2] for call in gateway.copy_rates_from_calls]
        assert event_a in anchors and event_b in anchors
    finally:
        worker.stop()


# ── 7: future bar -> refused, before any data fetch ───────────────────────────────────────────────────


def test_future_event_as_of_is_refused_before_any_fetch() -> None:
    worker = _successful_worker()
    try:
        gateway = _default_gateway(now=_EVENT_AS_OF)
        tower = _tower(gateway, worker, wall_clock_provider=lambda: _EVENT_AS_OF - 3600)  # wall clock BEHIND the event

        result = _call(tower, event_as_of=_EVENT_AS_OF)

        assert result.bias_available is False
        assert result.market_map_available is False
        assert result.confirmation_available is False
        assert any("FUTURE_EVENT_REJECTED" in code for code in result.reason_codes)
        assert not gateway.copy_rates_from_calls, "must refuse BEFORE ever touching the gateway"
    finally:
        worker.stop()


# ── 8: clock rollback -> fail-closed ──────────────────────────────────────────────────────────────────


def test_wall_clock_rollback_is_fail_closed() -> None:
    worker = _successful_worker()
    try:
        gateway = _default_gateway(now=_EVENT_AS_OF)
        raw_values = iter([_EVENT_AS_OF + 100, _EVENT_AS_OF + 50])  # second read goes BACKWARD
        clock = MonotonicWallClock(raw_clock=lambda: next(raw_values))
        tower = _tower(gateway, worker, wall_clock_provider=clock)

        first = _call(tower, event_as_of=_EVENT_AS_OF)
        assert first.bias_available is True  # first read succeeds normally

        second = _call(tower, event_as_of=_EVENT_AS_OF)
        assert second.bias_available is False
        assert second.market_map_available is False
        assert any("WALL_CLOCK_ROLLBACK_DETECTED" in code for code in second.reason_codes)
    finally:
        worker.stop()


def test_monotonic_wall_clock_raises_directly_on_rollback() -> None:
    raw_values = iter([100.0, 50.0])
    clock = MonotonicWallClock(raw_clock=lambda: next(raw_values))
    assert clock() == 100
    with pytest.raises(ClockRollbackError):
        clock()


# ── 9: genuine staleness -> honestly reported, not hidden ─────────────────────────────────────────────


def test_genuinely_stale_data_is_reported_not_hidden() -> None:
    """A REAL gap (the gateway's own bars end long before `event_as_of`, e.g. a genuinely broken feed)
    must still show up as stale in the bridge-side diagnostic fields -- the fix must never overcorrect
    into masking real staleness, only artificial staleness."""
    worker = _successful_worker()
    try:
        stale_gateway_now = _EVENT_AS_OF - 4000  # bars are ~1h+ old relative to the event
        gateway = _default_gateway(now=stale_gateway_now)
        tower = _tower(gateway, worker, wall_clock_provider=lambda: _EVENT_AS_OF + 60)

        result = _call(tower, event_as_of=_EVENT_AS_OF)

        assert result.staleness_reason_m5 is not None and result.staleness_reason_m5.startswith("STALE:")
        assert result.staleness_reason_m15 is not None and result.staleness_reason_m15.startswith("STALE:")
    finally:
        worker.stop()


# ── 10: restart -> identical continuation, zero duplication ──────────────────────────────────────────


def test_restart_produces_identical_fetch_anchor_for_the_same_event() -> None:
    """Two INDEPENDENT `TowerDependencies` instances (simulating two different process starts) asked to
    evaluate the SAME `event_as_of` must anchor their bar fetch IDENTICALLY -- the result depends only on
    the event, never on which process instance (or its own wall-clock history) happened to handle it."""
    worker_1, worker_2 = _successful_worker(), _successful_worker()
    try:
        gateway_1 = _default_gateway(now=_EVENT_AS_OF)
        gateway_2 = _default_gateway(now=_EVENT_AS_OF)
        tower_1 = _tower(gateway_1, worker_1, wall_clock_provider=lambda: _EVENT_AS_OF + 5)
        tower_2 = _tower(gateway_2, worker_2, wall_clock_provider=lambda: _EVENT_AS_OF + 999_999)  # very different uptime

        result_1 = _call(tower_1, event_as_of=_EVENT_AS_OF)
        result_2 = _call(tower_2, event_as_of=_EVENT_AS_OF)

        assert result_1.data_cutoff == result_2.data_cutoff == _EVENT_AS_OF
        anchors_1 = sorted(call[2] for call in gateway_1.copy_rates_from_calls)
        anchors_2 = sorted(call[2] for call in gateway_2.copy_rates_from_calls)
        assert anchors_1 == anchors_2, "restart must reproduce the identical fetch anchor for the same event"
    finally:
        worker_1.stop()
        worker_2.stop()
