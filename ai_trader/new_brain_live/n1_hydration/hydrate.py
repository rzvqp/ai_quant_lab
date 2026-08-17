"""`hydrate_n1` -- the CEO's own 6-step recipe (RT-N1-HYDRATION-0001):

1. check for a compatible persisted snapshot
2. if present, restore it and process only the bars missing since its own watermark
3. if absent (or rejected), read the required closed M15 history from MT5
4. process every bar chronologically through the REAL `RawAxesBuilder`
5. save snapshot + watermark + identity
6. hand back a watermark such that live decisions start only from the next NEW bar

**Reuses `LiveBarFeed` for every MT5 interaction and closed-bar determination -- never a duplicated
`copy_rates_from` parser.** `LiveBarFeed.poll()` already correctly excludes any bar not yet closed (`ts_
close > now: continue`) and returns bars oldest-first; hydration constructs a bare, `state_store=None`
`LiveBarFeed` (so it never touches or corrupts any REAL persisted watermark) purely as a closed-bar
fetcher, then explicitly filters for `ts_open > watermark` itself -- an explicit, auditable "only the
missing bars" step, not a MT5 API range query this repo has no other precedent for.

**Zero path to a trade, by construction.** This module imports `RawAxesBuilder`, `LiveBarFeed`,
`SqliteStateStore`, and this package's own `identity`/`snapshot` modules -- nothing from `ve_brain`'s
Router/DecisionRequest/decide_n6, `risk_gate`, `execution_shadow`, or any broker-adjacent module. Warmup
bars are fed to `RawAxesBuilder.observe()` and nothing else; there is no code path here that could ever
reach a candidate, a risk decision, or `order_send`."""

from __future__ import annotations

import dataclasses

from ai_trader.execution_engine.adapters.mt5_gateway import MT5Gateway
from ai_trader.live_signal_source.bar_feed import LiveBarFeed, watermark_key
from ai_trader.live_signal_source.types import Bar
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder
from ai_trader.new_brain_live.n1_hydration.identity import (
    N1SnapshotIdentity,
    current_identity_for,
    identity_matches_for_restore,
    required_bar_count,
)
from ai_trader.new_brain_live.n1_hydration.snapshot import N1Snapshot, N1SnapshotStore
from ai_trader.persistent_state.store import SqliteStateStore

_M15_TIMEFRAME_MT5 = 15
_M15_BAR_SECONDS = 900
_FETCH_MARGIN_BARS = 20  # small slack over the exact requirement, so a partial/short MT5 window never
                          # under-fetches by one due to weekend/holiday gaps in the trailing count


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class HydrationResult:
    axes_builder: RawAxesBuilder
    watermark_ts_open: int
    identity: N1SnapshotIdentity
    restored_from_snapshot: bool
    rejection_reason: str | None
    bars_replayed_from_snapshot: int
    bars_replayed_new: int


def _fetch_closed_bars(
    *, gateway: MT5Gateway, symbol: str, count: int, timeframe_mt5: int = _M15_TIMEFRAME_MT5,
    bar_seconds: int = _M15_BAR_SECONDS,
) -> tuple[Bar, ...]:
    """A bare, ephemeral `LiveBarFeed` used ONLY as a closed-bar fetcher (`state_store=None` -- it never
    reads or writes any real persisted watermark, so it cannot corrupt or be corrupted by the real
    decision-loop feed's own dedup state)."""
    feed = LiveBarFeed(gateway, symbol, timeframe_mt5, bar_seconds, lookback_count=count, state_store=None)
    return feed.poll()


def _trailing_window(bars: tuple[Bar, ...], *, max_bars: int) -> tuple[Bar, ...]:
    """Bounded-snapshot trim (see `snapshot.py`'s own docstring for why) -- keeps at most the trailing
    `max_bars`, oldest-first order preserved."""
    return bars[-max_bars:] if len(bars) > max_bars else bars


def hydrate_n1(
    *, symbol: str, gateway: MT5Gateway, state_store: SqliteStateStore,
    timeframe_mt5: int = _M15_TIMEFRAME_MT5, bar_seconds: int = _M15_BAR_SECONDS,
) -> HydrationResult:
    required = required_bar_count()
    store = N1SnapshotStore(state_store)
    snapshot = store.latest()

    rejection_reason: str | None = None
    restored_bars: tuple[Bar, ...] = ()
    if snapshot is not None:
        if identity_matches_for_restore(snapshot.identity, symbol=symbol, timeframe="M15"):
            restored_bars = snapshot.bars
        else:
            rejection_reason = "IDENTITY_MISMATCH"
            snapshot = None

    axes_builder = RawAxesBuilder(symbol)

    if snapshot is not None:
        for bar in restored_bars:
            axes_builder.observe(bar)
        watermark = restored_bars[-1].ts_open if restored_bars else None
        fetched = _fetch_closed_bars(
            gateway=gateway, symbol=symbol, count=required + _FETCH_MARGIN_BARS,
            timeframe_mt5=timeframe_mt5, bar_seconds=bar_seconds,
        )
        missing = tuple(b for b in fetched if watermark is None or b.ts_open > watermark)
        for bar in missing:
            axes_builder.observe(bar)
        all_bars = restored_bars + missing
        restored_from_snapshot = True
        bars_from_snapshot = len(restored_bars)
        bars_new = len(missing)
    else:
        fetched = _fetch_closed_bars(
            gateway=gateway, symbol=symbol, count=required + _FETCH_MARGIN_BARS,
            timeframe_mt5=timeframe_mt5, bar_seconds=bar_seconds,
        )
        for bar in fetched:
            axes_builder.observe(bar)
        all_bars = fetched
        restored_from_snapshot = False
        bars_from_snapshot = 0
        bars_new = len(fetched)

    if not all_bars:
        raise RuntimeError(
            f"hydrate_n1({symbol!r}): no closed bars available from MT5 -- cannot hydrate N1 state"
        )

    snapshot_bars = _trailing_window(all_bars, max_bars=required)
    new_identity = current_identity_for(symbol=symbol, timeframe="M15", bars=snapshot_bars)
    store.record(N1Snapshot(identity=new_identity, bars=snapshot_bars))

    final_watermark = all_bars[-1].ts_open
    state_store.set_value(watermark_key(symbol, timeframe_mt5), float(final_watermark))

    return HydrationResult(
        axes_builder=axes_builder, watermark_ts_open=final_watermark, identity=new_identity,
        restored_from_snapshot=restored_from_snapshot, rejection_reason=rejection_reason,
        bars_replayed_from_snapshot=bars_from_snapshot, bars_replayed_new=bars_new,
    )
