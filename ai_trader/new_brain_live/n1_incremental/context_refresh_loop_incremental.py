"""`IncrementalContextRefreshLoop` -- CEO step 3 ("M15 actualizează N1/Router/contextul"), using the
isolated, Red-Team-cleared incremental engine instead of `dual_clock.upstream_context.build_context`'s
own bounded `RawAxesBuilder`. Produces the EXACT SAME `dual_clock.upstream_context.CachedUpstreamContext`
type Commit B already established -- `M5DecisionLoop` needs ZERO changes to consume a context built this
way: it already only ever reads `UpstreamContextStore.latest()`, never cares how that context was
computed.

Zero-lookahead / stale / rejected handling: a `rejected=True` worker response (identity mismatch,
`StaleStateError`, `FutureBarError`, `OutOfOrderBarError`, `DuplicateBarError`) means the context store is
NOT updated -- the previous (still valid, or naturally aging into staleness) context is left in place,
so `M5DecisionLoop`'s own existing `CONTEXT_STALE`/`CONTEXT_FROM_FUTURE` checks take over automatically.
This file never fabricates a context on a rejected response."""

from __future__ import annotations

import hashlib
import time
from typing import Callable

from ai_trader.live_signal_source.bar_feed import LiveBarFeed
from ai_trader.live_signal_source.types import Bar
from ai_trader.new_brain_live.dual_clock.upstream_context import CachedUpstreamContext, UpstreamContextStore
from ai_trader.new_brain_live.n1_incremental.client import N1IncrementalClient, N1IncrementalWorkerError
from ai_trader.new_brain_live.n1_incremental.snapshot_store import (
    N1IncrementalSnapshotStore,
    StoredN1IncrementalSnapshot,
)
from ai_trader.structural_observer.vendor_bridge import atr14

_TIMEFRAME = "M15"


def _fp(*parts: str) -> str:
    """Local copy of the same sha256-truncate-16 convention already established in `bridge._fp`/
    `dual_clock.upstream_context._fp`/`n1_hydration.identity._fp` -- kept local rather than importing a
    private helper across package boundaries, matching those files' own stated precedent."""
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]


def _atr_and_last_close(bars: tuple[Bar, ...]) -> tuple[float | None, float | None]:
    """ATR14/last-close are genuinely BOUNDED (trailing 14 bars) -- computed locally in the main process
    from the same real bar stream, via the same vendored `atr14()` every other N1 path in this repo
    already uses (`RawAxesBuilder.atr14()`), rather than round-tripping through the isolated worker for a
    value that has no unbounded-history dependency at all."""
    if not bars:
        return None, None
    closes = [b.close for b in bars]
    highs = [b.high for b in bars]
    lows = [b.low for b in bars]
    values = atr14(highs, lows, closes)
    last = values[-1]
    atr = last if last == last else None  # NaN != NaN
    return atr, closes[-1]


def _to_cached_upstream_context(result: object, *, atr: float | None, entry_price: float | None) -> CachedUpstreamContext:
    bar = result.last_closed_bar  # type: ignore[attr-defined]
    market_event_id = f"{bar.symbol}:{_TIMEFRAME}:{bar.ts_close}"
    regime_axes_status = result.regime_axes_status  # type: ignore[attr-defined]
    eligibility_decisions = result.eligibility_decisions  # type: ignore[attr-defined]
    n1_output_fp = result.n1_output_fingerprint  # type: ignore[attr-defined]
    context_id = _fp(
        bar.symbol, _TIMEFRAME, market_event_id, str(bar.ts_close), n1_output_fp,
        ",".join(regime_axes_status),
        ",".join(f"{d.strategy_id}:{d.eligible}:{d.mode.value}" for d in eligibility_decisions),
    )
    return CachedUpstreamContext(
        context_id=context_id, symbol=bar.symbol, timeframe=_TIMEFRAME, market_event_id=market_event_id,
        market_timestamp=bar.ts_close, n1_output_fp=n1_output_fp, regime_axes_status=regime_axes_status,
        router_bias_direction=None, confidence=1.0, axes=result.raw_axes,  # type: ignore[attr-defined]
        eligibility_decisions=eligibility_decisions, atr=atr, entry_price=entry_price,
    )


class IncrementalContextRefreshLoop:
    def __init__(
        self, *, feed: LiveBarFeed, client: N1IncrementalClient, context_store: UpstreamContextStore,
        snapshot_store: N1IncrementalSnapshotStore, atr_lookback_bars: int = 20,
        wall_clock: Callable[[], float] = time.time,
    ) -> None:
        self._feed = feed
        self._client = client
        self._context_store = context_store
        self._snapshot_store = snapshot_store
        self._atr_lookback_bars = atr_lookback_bars
        self._wall_clock = wall_clock
        self._recent_bars: list[Bar] = []  # bounded, trailing window, for the local ATR14 computation only

    def tick(self) -> int:
        """Returns the number of new M15 bars actually accepted into the incremental context (0 if
        nothing new closed, or if the worker rejected the batch -- context store left untouched either
        way)."""
        bars = self._feed.poll()
        if not bars:
            return 0

        self._recent_bars.extend(bars)
        if len(self._recent_bars) > self._atr_lookback_bars:
            self._recent_bars = self._recent_bars[-self._atr_lookback_bars:]

        prior = self._snapshot_store.latest()
        restore_blob = prior.snapshot_blob if prior is not None else None

        try:
            response = self._client.observe(
                bars=bars, restore_snapshot_blob=restore_blob, wall_clock_now=self._wall_clock(),
            )
        except N1IncrementalWorkerError:
            # Worker unavailable/crashed/timed out -- fail closed exactly like a rejected response: the
            # context store is left untouched, never fabricated from a failed call.
            return 0

        # `restore_blob is not None` means we HAD prior canonical state to continue from. If the worker
        # rejected that restore (identity mismatch), it still runs the given `bars` against a FRESH,
        # empty engine and reports `rejected=False` -- a well-formed but INCOMPLETE-history result, not a
        # crash. Using it here would silently produce a context built on none of the real prior history,
        # exactly the "worker/snapshot/identity mismatch" case the CEO's own mandate requires NO_TRADE
        # for. `response.rejected` alone does not catch this -- `restore_rejected_reason` does.
        restore_was_rejected = restore_blob is not None and response.restore_rejected_reason is not None
        if response.rejected or restore_was_rejected or response.result is None or response.snapshot_blob is None:
            return 0

        atr, entry_price = _atr_and_last_close(tuple(self._recent_bars))
        context = _to_cached_upstream_context(response.result, atr=atr, entry_price=entry_price)
        self._context_store.record(context)
        self._snapshot_store.record(StoredN1IncrementalSnapshot(
            snapshot_blob=response.snapshot_blob, identity_fingerprint=response.identity_fingerprint or "",
            symbol=context.symbol, timeframe=context.timeframe, last_bar_ts_open=bars[-1].ts_open,
            last_bar_ts_close=bars[-1].ts_close,
        ))
        return response.bars_processed
