"""ADVERSARIAL TEST -- DOCUMENTS A CONFIRMED BLOCKER, NOT A PASSING GUARANTEE.

CEO instruction (2026-08-18), following VE's own code-level demonstration at checkpoint `e90bad7`:
`expansion`/`is_displacement` are bounded (trailing `ATR_WINDOW`), `compression`/`is_compressed` is
bounded (trailing `COMPRESSION_WINDOW`), but `structure`/`direction` are genuinely UNBOUNDED --
`RawAxesBuilder.observe()` always runs `detect_breaks`/`detect_swings` over `Block(0, len(self._closes))`,
the FULL accumulated history, and reports whichever break has the highest index ever seen. If the only
break in a symbol's real history is older than `identity.required_bar_count()` bars back, a bounded
snapshot (`snapshot.py`'s own disclosed trailing-window design) genuinely LOSES it on restore -- the
restored builder reports `UNCERTAIN` where a continuous, never-restarted run would have correctly kept
reporting the real, still-active TREND_UP/TREND_DOWN regime.

**"UNCERTAIN rămâne permis" does NOT license this.** That instruction means a genuinely undecidable
regime is an acceptable OUTPUT. It does not mean hydration may manufacture undecidability by discarding
real history a continuous run would still have. This test proves the two diverge for a real, constructed
scenario -- not a contrived edge case.

**Per the CEO's own instruction: if bounded restore differs from continuous full-history, KEEP this test
as evidence of the blocker. Do not loosen the assertion to make it pass.** The test below asserts the
DIVERGENCE explicitly (continuous keeps the regime; bounded-restore loses it) -- if a future change to
`snapshot.py`/`hydrate.py` ever closes this gap (unbounded incremental state, or a `ve_n1_replay`-produced
compatible snapshot, or a demonstrated-equivalent replay -- per the CEO's three listed remediation paths),
THIS test should start failing on its current assertions, and that failure is the correct signal to update
it, not evidence of a new bug.

**Commit C's status is `N1_STARTUP_HYDRATION_CONDITIONAL`, not `..._READY`, because of this file.**
`hydrate_n1` must not feed live decisions until one of the three CEO-listed remediations lands."""

from __future__ import annotations

import dataclasses
from pathlib import Path

import ve_brain  # type: ignore[import-untyped]

from ai_trader.live_signal_source.types import Bar
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder
from ai_trader.new_brain_bridge.tests.conftest import bos_bull_bars
from ai_trader.new_brain_live.n1_hydration.hydrate import hydrate_n1
from ai_trader.new_brain_live.n1_hydration.identity import required_bar_count
from ai_trader.new_brain_live.tests._fixtures import SYMBOL, FakeNewBrainLiveGateway
from ai_trader.persistent_state.store import SqliteStateStore

_BAR_SECONDS = 900


@dataclasses.dataclass
class _RawRate:
    time: int
    open: float
    high: float
    low: float
    close: float
    tick_volume: float = 100.0


def _calm_bars_after(*, count: int, start_index: int, start_price: float) -> list[Bar]:
    """The SAME calm-bar recipe `conftest.trend_up_regime_bars`'s own `CALM_PREFIX_BARS` generator uses
    (tiny fixed increments) -- already independently verified elsewhere in this repo to produce no new
    swing/break on its own. Appended AFTER the BOS sequence here (not before, as `trend_up_regime_bars`
    does) so the confirmed break is the OLD end of the history, not the recent end."""
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


def _far_future_history() -> tuple[Bar, ...]:
    """A confirmed `bos_bull` break (per `conftest.py`'s own hand-verified fixture, idx 14 of 18) followed
    by 500 calm bars with no further break -- comfortably more than `required_bar_count()` bars past the
    only break in this history's entire lifetime."""
    bos = bos_bull_bars(SYMBOL)
    calm = _calm_bars_after(count=500, start_index=len(bos), start_price=bos[-1].close)
    return tuple(bos) + tuple(calm)


def _to_raw_rate(bar: Bar) -> _RawRate:
    return _RawRate(time=bar.ts_open, open=bar.open, high=bar.high, low=bar.low, close=bar.close)


def test_bounded_snapshot_restore_loses_structure_older_than_the_window_BLOCKER(tmp_path: Path) -> None:
    history = _far_future_history()
    bos_break_index = 14  # BOS_BULL_CONFIRMED_AT_INDEX, per conftest.py's own hand-verified fixture
    assert len(history) - bos_break_index > required_bar_count(), (
        "fixture regression: the break must sit more than required_bar_count() bars before the end, "
        "or the bounded snapshot's trailing window would include it and this test would prove nothing"
    )

    # ── Reference: a continuous, never-restarted run over the FULL real history ──
    continuous = RawAxesBuilder(SYMBOL)
    continuous_axes = None
    for bar in history:
        continuous_axes = continuous.observe(bar)
    assert continuous_axes is not None
    continuous_regimes = ve_brain.applicable_regimes(continuous_axes)
    continuous_router = ve_brain.StrategyRouter(ve_brain.CANONICAL_STRATEGIES).eligible(
        continuous_axes, f"{SYMBOL}:M15:{history[-1].ts_close}", None, 1.0,
    )

    # ── Bounded path: cold hydration (correct -- fetches and replays every bar), THEN a SECOND
    # hydration that restores from the bounded snapshot the first one persisted, with no new bars ──
    state_store = SqliteStateStore(tmp_path / "state.db")
    rates = tuple(_to_raw_rate(b) for b in history)
    first = hydrate_n1(symbol=SYMBOL, gateway=FakeNewBrainLiveGateway(rates=rates), state_store=state_store)
    assert first.restored_from_snapshot is False
    assert first.bars_replayed_new == len(history)

    second = hydrate_n1(symbol=SYMBOL, gateway=FakeNewBrainLiveGateway(rates=rates), state_store=state_store)
    assert second.restored_from_snapshot is True
    assert second.bars_replayed_new == 0
    assert second.bars_replayed_from_snapshot == required_bar_count(), (
        "the snapshot must be bounded to exactly required_bar_count() bars -- confirms the BOS bars "
        "(indices 0-17 of this fixture) are genuinely excluded from what was restored"
    )

    probe = Bar(
        symbol=SYMBOL, ts_open=history[-1].ts_close, ts_close=history[-1].ts_close + _BAR_SECONDS,
        open=2500.0, high=2500.4, low=2499.6, close=2500.02, volume=100.0,
    )
    restored_axes = second.axes_builder.observe(probe)
    restored_regimes = ve_brain.applicable_regimes(restored_axes)
    restored_router = ve_brain.StrategyRouter(ve_brain.CANONICAL_STRATEGIES).eligible(
        restored_axes, f"{SYMBOL}:M15:{probe.ts_close}", None, 1.0,
    )

    # ── THE BLOCKER, asserted explicitly: the continuous run keeps the real structure/direction; the
    # bounded restore has genuinely lost it. Do NOT relax these to make the test green -- a future fix
    # closing this gap should make BOTH sides equal, at which point every assertion below should be
    # inverted to prove equivalence instead. ──
    assert continuous_axes.structure is not None, "fixture regression: the continuous run must see the real break"
    assert continuous_axes.direction is not None
    assert restored_axes.structure is None, (
        "BLOCKER NOT REPRODUCED: bounded restore unexpectedly kept structure -- if a real fix landed, "
        "invert this assertion; if not, the fixture window sizing regressed"
    )
    assert restored_axes.direction is None
    assert continuous_axes.structure != restored_axes.structure
    assert continuous_axes.direction != restored_axes.direction
    assert continuous_regimes != restored_regimes
    continuous_eligible_ids = {d.strategy_id for d in continuous_router if d.eligible}
    restored_eligible_ids = {d.strategy_id for d in restored_router if d.eligible}
    assert continuous_eligible_ids != restored_eligible_ids, (
        "the Router verdict itself must differ -- a strategy eligible under the real (continuous) "
        "structure reading must not remain eligible under the bounded-restore UNCERTAIN reading"
    )
    state_store.close()
