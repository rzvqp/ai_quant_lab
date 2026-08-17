"""Official N1 replay fixtures -- REUSES the existing, independently-verified canonical bar
sequences from `ai_trader.new_brain_bridge.tests.conftest` (already adopted throughout
`test_bridge_tower_wiring.py`/`test_e2e_readiness.py`), never a new hand-invented sequence. Per the
CEO's own directive ("Nu recrea și nu simplifica algoritmul"), the point of an "official fixture" is
that its regime outcome was already verified against the REAL vendored detectors before being
adopted -- inventing a second, parallel bar sequence here would just be a second unverified guess.

`CANONICAL_TREND_UP_BARS` is confirmed (by that module's own test coverage) to leave the LAST bar
reading `structure="strong"`, `direction="up"`, `applicable_regimes == {TREND_UP}` -- i.e. this is the
one official fixture that exercises a fully-resolved (non-`UNCERTAIN`) regime end-to-end, including a
genuine `StrategyRouter` NORMAL-eligible path."""

from __future__ import annotations

from ai_trader.live_signal_source.types import Bar
from ai_trader.new_brain_bridge.tests.conftest import bos_bull_bars, trend_up_regime_bars

CANONICAL_SYMBOL = "XAUUSD"
CANONICAL_TIMEFRAME = "M15"
CANONICAL_BAR_INTERVAL_SECONDS = 900

#: 460-bar calm prefix + `bos_bull_bars()`, re-timestamped -- see `trend_up_regime_bars` docstring.
CANONICAL_TREND_UP_BARS: tuple[Bar, ...] = tuple(trend_up_regime_bars(CANONICAL_SYMBOL))

#: The 18-bar BOS_BULL sequence alone (no calm prefix) -- short, deterministic, useful for tests that
#: don't need a fully-resolved regime, only a genuine, non-trivial structural signal in few bars.
CANONICAL_BOS_BULL_BARS: tuple[Bar, ...] = tuple(bos_bull_bars(CANONICAL_SYMBOL))


def modified_close_variant(bars: tuple[Bar, ...], *, index: int, delta: float) -> tuple[Bar, ...]:
    """Returns a copy of `bars` with bar `index`'s `close` shifted by `delta` (and every bar from
    `index` onward re-referencing the SAME `ts_open`/`ts_close`/other fields -- only content changes,
    never identity). Used by the "a modified bar produces a different fingerprint" test: no existing
    fixture in this codebase captures a deliberately-mutated variant of an official sequence, so this
    is new, but it is a pure transformation of the reused official data, not a new invented sequence."""
    out = list(bars)
    original = out[index]
    out[index] = Bar(
        symbol=original.symbol, ts_open=original.ts_open, ts_close=original.ts_close,
        open=original.open, high=original.high, low=original.low, close=original.close + delta,
        volume=original.volume, is_backfilled=original.is_backfilled,
    )
    return tuple(out)
