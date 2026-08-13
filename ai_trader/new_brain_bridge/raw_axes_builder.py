"""`RawAxesBuilder` -- turns real, accumulated live OHLC into `ve_brain.RawAxes` (N1's contract). Step 5
of the CEO's 12-step list: "feed live -> normalizare -> bara inchisa -> N1 RawAxes."

**Why this doesn't reuse `market_intelligence.expansion`/`market_intelligence.structure`**: both are fed
`market_context`, and BOTH live entrypoints (`pdh_pdl_demo/entrypoint.py:107`,
`multi_policy_live/entrypoint.py:238`) build that context as `build_market_context(symbol, ts_close,
[bar])` -- a SINGLE-bar list. `analyze_expansion` reads `m15_features` (always `{}` on the live path, by
`build_market_context`'s own docstring) -> always `UNKNOWN`. `analyze_structure` reads real bars, but a
length-1 trailing window cannot satisfy its own fractal swing detector (`fractal_bars=3` each side) --
also structurally dead on the live path today, just for a different reason (window size, not empty
features). Neither path is a genuine source of live structural signal; wiring N1 from either would
silently produce `UNCERTAIN` on every single event, indistinguishable from "not wired at all."

**What this DOES reuse**: the exact same vendored, frozen, already-live detectors
`structural_observer.vendor_bridge` uses -- `detect_swings`/`label_structure`/`detect_breaks` for
structure/direction, `compression`/`expansion` for the compression/displacement axes -- fed this
builder's OWN accumulated OHLC arrays (mirroring `StructuralObserver`'s own accumulation pattern, since
process memory isn't shared with the separate `live_observation` process). Nothing here is a new
detector; this file is glue, not a new signal.

**The structure/direction mapping below is a genuine, disclosed judgment call**, not something already
coded anywhere: `BreakKind` (`bos_bull`/`bos_bear`/`choch_bull`/`choch_bear`) has no existing mapping to
`RawAxes`'s `direction`/`structure` vocabulary. BOS (a confirmed continuation break) maps to the
CONFIRMED end of each axis (`structure="strong"`, `direction="up"/"down"`); CHoCH (an early reversal
signal, not yet confirmed by a following break) maps to the WEAKER end (`structure="weak"`,
`direction="weak_up"/"weak_down"`) -- both ends already exist in `ve_brain`'s own vocabulary
(`_STRUCT_TREND = {"weak", "strong"}`), so this reuses the target vocabulary's own confidence gradient
rather than inventing a new one.

**No synthesized RANGE/neutral label.** When no break exists yet in the accumulated history, this
returns `structure=None, direction=None` (-> `SemanticRegime.UNCERTAIN`) rather than fabricating a
"ranging" state -- consistent with `ve_brain`'s OWN CEO decision that RANGE is retired and never
produced (`RANGE_STRATEGY_ROUTING="DISABLED"`, `version.py`). Absence of a recent break is exactly the
"not identifiable yet" case N1 is supposed to report honestly, not paper over."""

from __future__ import annotations

import ve_brain  # type: ignore[import-untyped]  # external VE artifact, no py.typed marker -- never modified

from ai_trader.live_signal_source.types import Bar
from ai_trader.structural_observer.vendor_bridge import (
    Block,
    atr14,
    compression,
    detect_breaks,
    detect_swings,
    expansion,
    label_structure,
)

_BREAK_KIND_TO_STRUCTURE_DIRECTION: dict[str, tuple[str, str]] = {
    "bos_bull": ("strong", "up"),
    "bos_bear": ("strong", "down"),
    "choch_bull": ("weak", "weak_up"),
    "choch_bear": ("weak", "weak_down"),
}


class RawAxesBuilder:
    """One instance per (symbol, timeframe) live stream -- accumulates every closed bar it is given and
    derives the CURRENT `RawAxes` reading from the full accumulated history on each call. Never resets;
    matches `StructuralObserver`'s own "single continuous block, growing, never reset" convention for the
    same underlying detectors."""

    def __init__(self, symbol: str) -> None:
        self._symbol = symbol
        self._opens: list[float] = []
        self._highs: list[float] = []
        self._lows: list[float] = []
        self._closes: list[float] = []

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def bars_observed(self) -> int:
        return len(self._closes)

    @property
    def last_close(self) -> float | None:
        return self._closes[-1] if self._closes else None

    def atr14(self) -> float | None:
        """The same vendored ATR14 `expansion()` itself uses internally (`market_state.atr14`), read
        for the LAST accumulated bar. `None` for the first 14 bars (insufficient trailing window --
        the vendored function's own NaN sentinel, translated to `None` at this boundary rather than
        leaking a float NaN to callers, matching this repo's own `getattr`-boundary convention)."""
        if not self._closes:
            return None
        values = atr14(self._highs, self._lows, self._closes)
        last = values[-1]
        return last if last == last else None  # NaN != NaN

    def observe(self, bar: Bar) -> ve_brain.RawAxes:
        """Feeds one newly-closed bar (never a forming bar -- `LiveBarFeed` already guarantees this) and
        returns the axes reading as of that bar."""
        if bar.symbol != self._symbol:
            raise ValueError(f"RawAxesBuilder for {self._symbol!r} received a bar for {bar.symbol!r}")

        self._opens.append(bar.open)
        self._highs.append(bar.high)
        self._lows.append(bar.low)
        self._closes.append(bar.close)

        block = Block(0, len(self._closes))
        swings = label_structure(detect_swings(self._highs, self._lows, [block]))
        breaks = detect_breaks(self._closes, swings, [block])
        structure, direction = _structure_and_direction(breaks)

        exp = expansion(self._opens, self._highs, self._lows, self._closes)
        comp, valid = compression(self._highs, self._lows)
        last = len(self._closes) - 1
        is_displacement = bool(exp[last])
        is_compressed = bool(comp[last]) if valid[last] else None

        return ve_brain.RawAxes(
            is_compressed=is_compressed, is_displacement=is_displacement,
            direction=direction, structure=structure,
        )


def _structure_and_direction(breaks: object) -> tuple[str | None, str | None]:
    breaks_list = list(breaks)  # type: ignore[call-overload]
    if not breaks_list:
        return None, None
    latest = max(breaks_list, key=lambda b: int(b.idx))
    mapped = _BREAK_KIND_TO_STRUCTURE_DIRECTION.get(str(latest.kind.value))
    if mapped is None:
        return None, None
    return mapped
