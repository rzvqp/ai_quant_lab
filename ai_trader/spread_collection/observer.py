"""`SpreadCollector` -- builds one `SpreadObservation` per closed bar (CEO instruction, 2026-08-04).
Same recompute-from-scratch, single-continuous-block accumulation pattern every recognition rule in this
project already uses (`pdh_pdl_demo.recognition_rule.PdhPdlRecognitionRule`) -- reused here for the level-
touch marker only, never for a trading decision. No stop/target/candidate is ever constructed; this class
has no concept of direction, sizing, or a "policy."

**Fail-closed on a missing tick**: if the live tick can't be read for a bar, that bar produces NO
observation (never a fabricated bid/ask) -- `collect(bar)` returns `None`, matching this project's own
established "never invent a value that couldn't actually be read" convention.

**Backfilled bars, added 2026-08-10** (CEO: "Spread-ul NU se backfilleaza -- nu exista retroactiv"): a
bar recovered by `LiveBarFeed`'s gap-catch-up range fetch (`Bar.is_backfilled=True`) still gets its OHLC
folded into the running arrays -- level-touch/ATR continuity needs the real price path, and that part
CAN be reconstructed from history -- but `collect()` never attempts a tick read or records a
`SpreadObservation` for it, the same fail-closed `None` return as a missing tick, since a spread read
hours or days late has no meaning."""

from __future__ import annotations

from ai_trader.live_signal_source.types import Bar
from ai_trader.pdh_pdl_demo.day_index import day_boundary_start_utc
from ai_trader.pdh_pdl_demo.types import LiveTickReader
from ai_trader.spread_collection.journal import SpreadObservationLog
from ai_trader.spread_collection.types import SpreadObservation
from ai_trader.spread_collection.vendor_bridge import (
    Block,
    atr14,
    compute_prior_day_levels,
    detect_level_touches,
    sessions,
)


class SpreadCollector:
    """Records into `journal` itself (same self-contained-observer pattern
    `structural_observer.observer.StructuralObserver` already established) -- `collect()`'s return value
    is informational/for tests, not how recording happens."""

    def __init__(self, symbol: str, tick_reader: LiveTickReader, journal: SpreadObservationLog) -> None:
        self._symbol = symbol
        self._tick_reader = tick_reader
        self._journal = journal
        self._highs: list[float] = []
        self._lows: list[float] = []
        self._closes: list[float] = []
        self._day_index: list[int] = []

    @property
    def current_bar_count(self) -> int:
        return len(self._closes)

    def collect(self, bar: Bar) -> SpreadObservation | None:
        idx = len(self._closes)
        self._highs.append(bar.high)
        self._lows.append(bar.low)
        self._closes.append(bar.close)
        self._day_index.append(day_boundary_start_utc(bar.ts_open))

        if bar.is_backfilled:
            return None

        tick = self._tick_reader.read(self._symbol)
        if tick is None:
            return None

        block = Block(0, len(self._closes))
        levels = compute_prior_day_levels(self._highs, self._lows, self._day_index, [block])
        touches = detect_level_touches(self._highs, self._lows, levels, self._day_index, [block])
        fresh_touch = next((t for t in touches if t.touch_idx == idx), None)

        atr_array = atr14(self._highs, self._lows, self._closes)
        atr_at_idx = atr_array[idx]
        atr_value = None if atr_at_idx is None or _is_nan(atr_at_idx) else float(atr_at_idx)

        session = str(sessions([bar.ts_open])[0])

        observation = SpreadObservation(
            symbol=self._symbol, as_of=bar.ts_close, bid=float(tick.bid), ask=float(tick.ask),
            spread=float(tick.ask - tick.bid), session=session, atr=atr_value,
            day_boundary_label=self._day_index[idx], is_level_touch=fresh_touch is not None,
            touch_level_kind=fresh_touch.level.kind.value if fresh_touch is not None else None,
        )
        self._journal.record(observation)
        return observation


def _is_nan(value: float) -> bool:
    return value != value
