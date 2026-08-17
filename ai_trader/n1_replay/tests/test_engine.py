"""`N1ReplayEngine` tests -- RT-N1-REPLAY-0001 section 3 mandatory scenarios (all except the real-data
Live Shadow parity test, which lives in `test_live_parity.py` since it needs a real MT5 terminal)."""

from __future__ import annotations

import dataclasses

import pytest
import ve_brain  # type: ignore[import-untyped]

from ai_trader.live_signal_source.types import Bar
from ai_trader.n1_replay import (
    BarNotClosedError,
    DuplicateBarError,
    FutureBarError,
    IncompatibleSnapshotError,
    N1ReplayEngine,
    NonFiniteAxesInputError,
    OutOfOrderBarError,
    StaleStateError,
)
from ai_trader.n1_replay.fixtures.canonical_bars import (
    CANONICAL_BAR_INTERVAL_SECONDS,
    CANONICAL_SYMBOL,
    CANONICAL_TIMEFRAME,
    CANONICAL_TREND_UP_BARS,
    modified_close_variant,
)
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder
from ai_trader.new_brain_bridge.tests.conftest import BOS_BULL_CONFIRMED_AT_INDEX, CALM_PREFIX_BARS

_FAR_FUTURE_CLOCK = 10**10


def _engine(**overrides: object) -> N1ReplayEngine:
    kwargs: dict[str, object] = dict(
        symbol=CANONICAL_SYMBOL, timeframe=CANONICAL_TIMEFRAME,
        bar_interval_seconds=CANONICAL_BAR_INTERVAL_SECONDS, implementation_commit="TEST_COMMIT",
        clock=lambda: _FAR_FUTURE_CLOCK,
    )
    kwargs.update(overrides)
    return N1ReplayEngine(**kwargs)  # type: ignore[arg-type]


def _simple_bars(
    count: int, *, start_ts_open: int = 0, price: float = 2400.0, symbol: str = CANONICAL_SYMBOL,
) -> tuple[Bar, ...]:
    bars = []
    ts = start_ts_open
    for _ in range(count):
        bars.append(Bar(
            symbol=symbol, ts_open=ts, ts_close=ts + CANONICAL_BAR_INTERVAL_SECONDS,
            open=price, high=price + 1.0, low=price - 1.0, close=price + 0.3, volume=100.0,
        ))
        ts += CANONICAL_BAR_INTERVAL_SECONDS
        price += 0.3
    return tuple(bars)


# ── 1/2: live vs replay -- RawAxes and Router identical (unit-level: compare against the raw
#         primitives directly, mirroring bridge.py's own exact recipe; the real end-to-end proof
#         against the actually-running LIVE_SHADOW process is test_live_parity.py) ──────────────────


def test_live_vs_replay_raw_axes_identical() -> None:
    reference_builder = RawAxesBuilder(CANONICAL_SYMBOL)
    reference_axes = None
    for bar in CANONICAL_TREND_UP_BARS:
        reference_axes = reference_builder.observe(bar)

    engine = _engine()
    result = engine.replay(CANONICAL_TREND_UP_BARS)[-1]

    assert result.raw_axes == reference_axes


def test_live_vs_replay_router_identical() -> None:
    reference_builder = RawAxesBuilder(CANONICAL_SYMBOL)
    reference_axes = None
    for bar in CANONICAL_TREND_UP_BARS:
        reference_axes = reference_builder.observe(bar)
    market_event_id = f"{CANONICAL_SYMBOL}:{CANONICAL_TIMEFRAME}:{CANONICAL_TREND_UP_BARS[-1].ts_close}"
    reference_router = ve_brain.StrategyRouter(ve_brain.CANONICAL_STRATEGIES)
    reference_decisions = reference_router.eligible(reference_axes, market_event_id, None, 1.0)

    engine = _engine()
    result = engine.replay(CANONICAL_TREND_UP_BARS)[-1]

    assert result.eligibility_decisions == reference_decisions


# ── 3: same bars -> identical fingerprint ─────────────────────────────────────────────────────────


def test_same_bars_produce_identical_fingerprints() -> None:
    results_a = _engine().replay(CANONICAL_TREND_UP_BARS)
    results_b = _engine().replay(CANONICAL_TREND_UP_BARS)
    assert [r.output_fingerprint for r in results_a] == [r.output_fingerprint for r in results_b]
    assert [r.n1_output_fingerprint for r in results_a] == [r.n1_output_fingerprint for r in results_b]


# ── 4: a modified bar -> a different fingerprint ──────────────────────────────────────────────────


def test_modified_bar_produces_different_fingerprint() -> None:
    """Perturbing the BOS_BULL confirmation bar's close (the bar `detect_breaks` reports the actual
    structure break at, per `conftest.py`'s own verified docstring) changes `direction`/`structure`,
    hence the fingerprint. Confirmed empirically (not merely assumed) before being adopted here."""
    modified_index = CALM_PREFIX_BARS + BOS_BULL_CONFIRMED_AT_INDEX
    modified_bars = modified_close_variant(CANONICAL_TREND_UP_BARS, index=modified_index, delta=-50.0)

    baseline = _engine().replay(CANONICAL_TREND_UP_BARS)[-1]
    modified = _engine().replay(modified_bars)[-1]

    assert modified.n1_output_fingerprint != baseline.n1_output_fingerprint
    assert modified.output_fingerprint != baseline.output_fingerprint


# ── 5: duplicate bar -> deterministic dedup (this engine's chosen behavior, not a refusal) ─────────


def test_exact_duplicate_bar_is_deterministically_deduplicated() -> None:
    bars = _simple_bars(5)
    engine = _engine()
    engine.replay(bars)
    before = engine.bars_observed

    result_again = engine.observe_closed_bar(bars[-1])  # exact same Bar object/content, re-observed

    assert engine.bars_observed == before  # not double-counted
    assert result_again.n1_output_fingerprint == engine._last_result.n1_output_fingerprint  # type: ignore[union-attr]


def test_conflicting_duplicate_bar_is_refused() -> None:
    bars = _simple_bars(5)
    engine = _engine()
    engine.replay(bars)
    conflicting = dataclasses.replace(bars[-1], close=bars[-1].close + 100.0)

    with pytest.raises(DuplicateBarError):
        engine.observe_closed_bar(conflicting)


# ── 6: not-yet-closed bar -> refused ──────────────────────────────────────────────────────────────


def test_unclosed_bar_is_refused() -> None:
    engine = _engine(clock=lambda: 100)  # wall clock far behind the bar's own ts_close
    forming_bar = _simple_bars(1, start_ts_open=1000)[0]
    with pytest.raises(BarNotClosedError):
        engine.observe_closed_bar(forming_bar)


# ── 7: wrong temporal order -> refused ────────────────────────────────────────────────────────────


def test_out_of_order_bar_is_refused() -> None:
    bars = _simple_bars(5)
    engine = _engine()
    engine.replay(bars)
    earlier_bar = _simple_bars(1, start_ts_open=bars[0].ts_open - CANONICAL_BAR_INTERVAL_SECONDS)[0]
    with pytest.raises(OutOfOrderBarError):
        engine.observe_closed_bar(earlier_bar)


# ── 8: future bar (beyond the requested replay horizon) -> refused ───────────────────────────────


def test_future_bar_beyond_as_of_horizon_is_refused() -> None:
    bars = _simple_bars(3)
    engine = _engine()
    horizon = bars[1].ts_close  # bound the replay to only the first two bars
    with pytest.raises(FutureBarError):
        engine.replay(bars, as_of=horizon)


def test_bars_within_as_of_horizon_are_accepted() -> None:
    bars = _simple_bars(3)
    engine = _engine()
    horizon = bars[-1].ts_close
    results = engine.replay(bars, as_of=horizon)
    assert len(results) == 3


# ── 9: restart + restore -> identical result ──────────────────────────────────────────────────────


def test_restart_and_restore_produces_identical_results() -> None:
    continuous = _engine()
    continuous_results = continuous.replay(CANONICAL_TREND_UP_BARS)

    split_point = 300
    before_restart = _engine()
    before_restart.replay(CANONICAL_TREND_UP_BARS[:split_point])
    snapshot = before_restart.snapshot()

    # simulate a full restart: a brand-new engine instance, identity built the same way
    after_restart = _engine()
    after_restart.restore(snapshot)
    remaining_results = after_restart.replay(CANONICAL_TREND_UP_BARS[split_point:])

    assert remaining_results[-1].n1_output_fingerprint == continuous_results[-1].n1_output_fingerprint
    assert remaining_results[-1].raw_axes == continuous_results[-1].raw_axes
    assert remaining_results[-1].eligibility_decisions == continuous_results[-1].eligibility_decisions
    assert after_restart.bars_observed == continuous.bars_observed


# ── 10: incompatible snapshot -> fail-closed, state unchanged ────────────────────────────────────


def test_incompatible_snapshot_symbol_is_refused_and_state_unchanged() -> None:
    engine = _engine()
    engine.replay(CANONICAL_TREND_UP_BARS[:10])
    bars_before = engine.bars_observed

    other_symbol_engine = _engine(symbol="EURUSD")
    other_symbol_engine.replay(_simple_bars(3, symbol="EURUSD"))
    mismatched_snapshot = other_symbol_engine.snapshot()

    with pytest.raises(IncompatibleSnapshotError):
        engine.restore(mismatched_snapshot)
    assert engine.bars_observed == bars_before  # unchanged after the refused restore


# ── 11/12/13: single-field identity mismatches (contract / router / detector pin) are each caught ──


def test_snapshot_with_different_n1_contract_version_is_refused() -> None:
    engine = _engine()
    snapshot = engine.snapshot()
    tampered_identity = dataclasses.replace(snapshot.identity, n1_contract_version="n1-some-other-v9")
    tampered_snapshot = dataclasses.replace(snapshot, identity=tampered_identity)
    with pytest.raises(IncompatibleSnapshotError):
        engine.restore(tampered_snapshot)


def test_snapshot_with_different_router_version_is_refused() -> None:
    engine = _engine()
    snapshot = engine.snapshot()
    tampered_identity = dataclasses.replace(snapshot.identity, router_version="router-v99")
    tampered_snapshot = dataclasses.replace(snapshot, identity=tampered_identity)
    with pytest.raises(IncompatibleSnapshotError):
        engine.restore(tampered_snapshot)


def test_snapshot_with_different_detector_configuration_fingerprint_is_refused() -> None:
    engine = _engine()
    snapshot = engine.snapshot()
    tampered_identity = dataclasses.replace(
        snapshot.identity, detector_configuration_fingerprint="0000000000000000",
    )
    tampered_snapshot = dataclasses.replace(snapshot, identity=tampered_identity)
    with pytest.raises(IncompatibleSnapshotError):
        engine.restore(tampered_snapshot)


# ── 14: stale state -> refused ────────────────────────────────────────────────────────────────────


def test_stale_state_is_refused() -> None:
    engine = _engine(max_staleness_seconds=60.0)
    bars = _simple_bars(2)
    engine.replay(bars)
    far_future_now = bars[-1].ts_close + 3600
    with pytest.raises(StaleStateError):
        engine.assert_not_stale(now=far_future_now)


def test_fresh_state_is_not_stale() -> None:
    engine = _engine(max_staleness_seconds=3600.0)
    bars = _simple_bars(2)
    engine.replay(bars)
    engine.assert_not_stale(now=bars[-1].ts_close + 60)  # does not raise


def test_pure_historical_replay_is_never_flagged_stale_without_a_configured_threshold() -> None:
    """`max_staleness_seconds=None` (the default) -- a caller replaying an old fixture must never be
    refused merely because the fixture is old; staleness is opt-in, live-monitoring-only."""
    engine = _engine()  # max_staleness_seconds defaults to None
    engine.replay(CANONICAL_TREND_UP_BARS)
    engine.assert_not_stale(now=_FAR_FUTURE_CLOCK)  # does not raise


# ── 15: NaN/Inf -> refused ────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("bad_value", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_ohlc_is_refused(bad_value: float) -> None:
    engine = _engine()
    bad_bar = Bar(
        symbol=CANONICAL_SYMBOL, ts_open=0, ts_close=CANONICAL_BAR_INTERVAL_SECONDS, open=2400.0,
        high=2401.0, low=bad_value, close=2400.5, volume=100.0,
    )
    with pytest.raises(NonFiniteAxesInputError):
        engine.observe_closed_bar(bad_bar)


def test_non_finite_volume_is_refused() -> None:
    engine = _engine()
    bad_bar = Bar(
        symbol=CANONICAL_SYMBOL, ts_open=0, ts_close=CANONICAL_BAR_INTERVAL_SECONDS, open=2400.0,
        high=2401.0, low=2399.0, close=2400.5, volume=float("nan"),
    )
    with pytest.raises(NonFiniteAxesInputError):
        engine.observe_closed_bar(bad_bar)


# ── reset() ────────────────────────────────────────────────────────────────────────────────────────


def test_reset_returns_to_zero_bars_with_the_same_identity() -> None:
    engine = _engine()
    engine.replay(CANONICAL_TREND_UP_BARS[:50])
    identity_before = engine.identity

    engine.reset()

    assert engine.bars_observed == 0
    assert engine.last_closed_bar is None
    assert engine.identity is identity_before  # identity is a property of configuration, not history
