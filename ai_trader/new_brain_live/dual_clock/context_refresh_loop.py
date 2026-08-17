"""`ContextRefreshLoop` -- the ONE place N1/Router are computed for the M5 dual-clock path (RT-TIME-0001
section B). Owns its OWN `RawAxesBuilder` and its OWN `LiveBarFeed` (M15, `watermark_key_suffix=
"dual_clock_context"` -- a genuinely separate persisted watermark from the main M15 decision loop's own,
the CEO's own explicitly-named "N1/context watermark"). Never shares a `RawAxesBuilder` instance with the
main loop: two independent accumulators observing the identical real M15 bar stream produce identical
`RawAxes` (a pure function of accumulated history), so there is no correctness cost to this separation --
only the structural guarantee that this refresh path can run without ever mutating the main loop's own
state."""

from __future__ import annotations

from typing import Callable

import ve_brain  # type: ignore[import-untyped]

from ai_trader.live_signal_source.bar_feed import LiveBarFeed
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder
from ai_trader.new_brain_live.dual_clock.upstream_context import UpstreamContextStore, build_context

_TIMEFRAME = "M15"
_WATERMARK_SUFFIX = "dual_clock_context"


class ContextRefreshLoop:
    def __init__(
        self, *, feed: LiveBarFeed, axes_builder: RawAxesBuilder, context_store: UpstreamContextStore,
        catalog: tuple[ve_brain.StrategyContract, ...] = ve_brain.CANONICAL_STRATEGIES,
        router_bias_direction: str | None = None, confidence: float = 1.0,
    ) -> None:
        self._feed = feed
        self._axes_builder = axes_builder
        self._context_store = context_store
        self._catalog = catalog
        self._router_bias_direction = router_bias_direction
        self._confidence = confidence

    def tick(self) -> int:
        """Returns the number of M15 bars consumed this tick (0 when nothing new closed)."""
        bars = self._feed.poll()
        for bar in bars:
            context = build_context(
                symbol=self._axes_builder.symbol, timeframe=_TIMEFRAME, bar=bar,
                axes_builder=self._axes_builder, catalog=self._catalog,
                router_bias_direction=self._router_bias_direction, confidence=self._confidence,
            )
            self._context_store.record(context)
        return len(bars)
