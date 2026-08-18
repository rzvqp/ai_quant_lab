"""`hydrate_n1_incremental` -- CEO steps 1-2 ("citește istoricul real din MT5 până la ultima bară
închisă; construiește sau restaurează starea N1 canonică"). Cold-starts against a generously deep MT5
history (comfortably exceeding the CEO's own ">5.300 bare" decisive-test horizon) when no compatible
snapshot exists, or restores + catches up only the missing bars when one does -- reusing `LiveBarFeed`
for every MT5 interaction and closed/future-bar filtering, exactly like `n1_hydration.hydrate`'s own
established pattern, never a duplicated `copy_rates_from` parser.

Seeds the SAME `IncrementalContextRefreshLoop` watermark key the live M15 refresh loop will use
afterward (`watermark_key(symbol, mt5_timeframe, suffix="n1_incremental_context")`), so the very first
bar that loop's own `LiveBarFeed.poll()` ever returns is the first genuinely NEW one after hydration --
zero duplicate processing across the hydration-to-live-loop handoff."""

from __future__ import annotations

import dataclasses
import time
from typing import Callable

from ai_trader.execution_engine.adapters.mt5_gateway import MT5Gateway
from ai_trader.live_signal_source.bar_feed import LiveBarFeed, watermark_key
from ai_trader.live_signal_source.types import Bar
from ai_trader.new_brain_live.dual_clock.upstream_context import UpstreamContextStore
from ai_trader.new_brain_live.n1_incremental.client import N1IncrementalClient, N1IncrementalWorkerError
from ai_trader.new_brain_live.n1_incremental.context_refresh_loop_incremental import _to_cached_upstream_context, _atr_and_last_close
from ai_trader.new_brain_live.n1_incremental.snapshot_store import N1IncrementalSnapshotStore, StoredN1IncrementalSnapshot
from ai_trader.persistent_state.store import SqliteStateStore

_M15_TIMEFRAME_MT5 = 15
_M15_BAR_SECONDS = 900
_CONTEXT_WATERMARK_SUFFIX = "n1_incremental_context"
_DEFAULT_COLD_START_BAR_COUNT = 6000
"""Comfortably exceeds the CEO's own decisive-test horizon (">5.300 bare în urmă") -- a genuine, disclosed
choice, not derived from a formula the way `n1_hydration.identity.required_bar_count()` is, because the
incremental engine's own structural dependency is not bounded by any of this repo's own constants at all;
this is simply "as much real history as is reasonable to fetch once at cold start.\""""


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class IncrementalHydrationResult:
    restored_from_snapshot: bool
    rejection_reason: str | None
    bars_processed: int
    context_recorded: bool
    watermark_ts_open: int | None


def _fetch_closed_bars(
    *, gateway: MT5Gateway, symbol: str, count: int, timeframe_mt5: int = _M15_TIMEFRAME_MT5,
    bar_seconds: int = _M15_BAR_SECONDS,
) -> tuple[Bar, ...]:
    feed = LiveBarFeed(gateway, symbol, timeframe_mt5, bar_seconds, lookback_count=count, state_store=None)
    return feed.poll()


def hydrate_n1_incremental(
    *, symbol: str, gateway: MT5Gateway, state_store: SqliteStateStore,
    context_store: UpstreamContextStore, client: N1IncrementalClient,
    cold_start_bar_count: int = _DEFAULT_COLD_START_BAR_COUNT,
    wall_clock: Callable[[], float] = time.time, atr_lookback_bars: int = 20,
) -> IncrementalHydrationResult:
    snapshot_store = N1IncrementalSnapshotStore(state_store)
    prior = snapshot_store.latest()

    if prior is not None and prior.symbol == symbol and prior.timeframe == "M15":
        fetched = _fetch_closed_bars(gateway=gateway, symbol=symbol, count=cold_start_bar_count)
        missing = tuple(b for b in fetched if b.ts_open > prior.last_bar_ts_open)
        try:
            response = client.observe(
                bars=missing, restore_snapshot_blob=prior.snapshot_blob, wall_clock_now=wall_clock(),
            )
        except N1IncrementalWorkerError as exc:
            return IncrementalHydrationResult(
                restored_from_snapshot=False, rejection_reason=f"WorkerError: {exc}", bars_processed=0,
                context_recorded=False, watermark_ts_open=None,
            )
        # A rejected restore still returns `rejected=False` with a well-formed but INCOMPLETE-history
        # result (bars replayed against a fresh, empty engine) -- `restore_rejected_reason` is the signal
        # that actually matters here, not `response.rejected` alone (see `IncrementalContextRefreshLoop
        # .tick`'s own identical guard for the full explanation).
        if response.rejected or response.restore_rejected_reason is not None:
            # Fail-closed rebuild, not a silent accept -- fall through to the cold path below.
            prior = None
        else:
            watermark = missing[-1].ts_open if missing else prior.last_bar_ts_open
            context_recorded = False
            if response.result is not None and response.snapshot_blob is not None:
                atr, entry_price = _atr_and_last_close(fetched[-atr_lookback_bars:])
                context_store.record(_to_cached_upstream_context(response.result, atr=atr, entry_price=entry_price))
                snapshot_store.record(StoredN1IncrementalSnapshot(
                    snapshot_blob=response.snapshot_blob, identity_fingerprint=response.identity_fingerprint or "",
                    symbol=symbol, timeframe="M15", last_bar_ts_open=watermark,
                    last_bar_ts_close=watermark + _M15_BAR_SECONDS,
                ))
                context_recorded = True
            state_store.set_value(watermark_key(symbol, _M15_TIMEFRAME_MT5, suffix=_CONTEXT_WATERMARK_SUFFIX), float(watermark))
            return IncrementalHydrationResult(
                restored_from_snapshot=True, rejection_reason=response.rejection_reason,
                bars_processed=response.bars_processed, context_recorded=context_recorded,
                watermark_ts_open=watermark,
            )

    fetched = _fetch_closed_bars(gateway=gateway, symbol=symbol, count=cold_start_bar_count)
    if not fetched:
        return IncrementalHydrationResult(
            restored_from_snapshot=False, rejection_reason="NO_CLOSED_BARS_AVAILABLE", bars_processed=0,
            context_recorded=False, watermark_ts_open=None,
        )
    try:
        response = client.observe(bars=fetched, restore_snapshot_blob=None, wall_clock_now=wall_clock())
    except N1IncrementalWorkerError as exc:
        return IncrementalHydrationResult(
            restored_from_snapshot=False, rejection_reason=f"WorkerError: {exc}", bars_processed=0,
            context_recorded=False, watermark_ts_open=None,
        )
    if response.rejected or response.result is None or response.snapshot_blob is None:
        return IncrementalHydrationResult(
            restored_from_snapshot=False, rejection_reason=response.rejection_reason,
            bars_processed=response.bars_processed, context_recorded=False, watermark_ts_open=None,
        )

    watermark = fetched[-1].ts_open
    atr, entry_price = _atr_and_last_close(fetched[-atr_lookback_bars:])
    context_store.record(_to_cached_upstream_context(response.result, atr=atr, entry_price=entry_price))
    snapshot_store.record(StoredN1IncrementalSnapshot(
        snapshot_blob=response.snapshot_blob, identity_fingerprint=response.identity_fingerprint or "",
        symbol=symbol, timeframe="M15", last_bar_ts_open=watermark, last_bar_ts_close=watermark + _M15_BAR_SECONDS,
    ))
    state_store.set_value(watermark_key(symbol, _M15_TIMEFRAME_MT5, suffix=_CONTEXT_WATERMARK_SUFFIX), float(watermark))
    return IncrementalHydrationResult(
        restored_from_snapshot=False, rejection_reason=None, bars_processed=response.bars_processed,
        context_recorded=True, watermark_ts_open=watermark,
    )
