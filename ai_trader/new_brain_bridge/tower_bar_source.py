"""Read-only, point-in-time fetch of the last N CLOSED M15/M5 bars for a `ve_tower` N3/N4 request --
CEO Phase 2 step 5 ("wire bridge.py to the real tower"). The genuine gap this closes: `bridge.py`'s own
`RawAxesBuilder` accumulates exactly ONE timeframe's bars (whatever `timeframe=` the caller passes for
N1), but `ve_tower` needs M15 (N3) and M5 (N4) SIMULTANEOUSLY, regardless of what timeframe N1 itself
runs on -- no such dual-timeframe source existed anywhere in this repo before this file.

**Deliberately NOT `LiveBarFeed`** (`live_signal_source/bar_feed.py`, "Piesa 1"): that class owns
watermark/dedup/backfill state for INCREMENTAL polling of ONE timeframe over a process's whole lifetime.
This is a stateless snapshot -- "give me the last N closed bars of M15/M5 right now" -- for a single
decision. Reuses `MT5Gateway.copy_rates_from` directly and the SAME broker-offset correction +
still-forming-bar filter `bar_feed.py` already established (`make_broker_offset`, `_read_field`) rather
than re-deriving either -- a caller already running a `LiveBarFeed` for its own N1 timeframe should reuse
its `broker_offset` callable here too, so both fetches agree on the same broker/UTC correction.

**Gap DETECTION (not recovery), added 2026-08-16 for test 05** (`test_e2e_readiness.py`, Mandate B point
5: "a detected gap is visible in whatever context N1 consumes"): `detect_gaps` reuses `bar_feed.py`'s own
`classify_gap` on WHATEVER window this module fetched -- a gap in the M15/M5 window this file hands to
`ve_tower` must be visible to the caller (bridge.py surfaces it on the Tower `NodeTrace`), never silently
absorbed the way a plain OHLC array would hide it. This is deliberately NOT the same as `LiveBarFeed`'s
own gap detection (which compares against a persisted watermark across POLLS, for recovery/backfill
purposes) -- this is a single, one-shot check WITHIN the fetched window itself, every time it's fetched."""

from __future__ import annotations

from ai_trader.execution_engine.adapters.mt5_gateway import MT5Gateway
from ai_trader.live_signal_source.bar_feed import _read_field
from ai_trader.live_signal_source.gap_classification import classify_gap
from ai_trader.live_signal_source.types import BarFeedError, GapRecord

MT5_TIMEFRAME_H1 = 16385
"""The REAL `MetaTrader5.TIMEFRAME_H1` value -- empirically verified (2026-08-17, RT-TOWER-0008), NOT the
naive `60` (minutes) a reader might guess: MT5's own enum only encodes M1-M30 as their literal minute
count; H1 and above use a `0x4000`-flagged encoding (`16385 = 0x4001`). Getting this wrong would silently
fetch the wrong timeframe (or fail) rather than raise -- verified against the actual installed
`MetaTrader5` package before being written here, not assumed."""
MT5_TIMEFRAME_M15 = 15
MT5_TIMEFRAME_M5 = 5
BAR_SECONDS_H1 = 3600
BAR_SECONDS_M15 = 900
BAR_SECONDS_M5 = 300


def fetch_closed_bars(
    gateway: MT5Gateway, *, symbol: str, mt5_timeframe: int, bar_seconds: int, count: int,
    now: int, broker_offset_seconds: int = 0,
) -> tuple[dict[str, object], ...]:
    """Up to `count` most-recently-CLOSED bars (oldest first) as `{"time": int, "open": float,
    "high": float, "low": float, "close": float}` dicts -- exactly the wire shape
    `ve_tower_worker.decision.real_decision` requires. Never includes the currently-forming bar.

    `broker_offset_seconds` is `broker_epoch - true_utc_epoch` (see `bar_feed.make_broker_offset`) --
    `0` (the default) means MT5 timestamps are already true UTC. Raises `BarFeedError` on a genuine
    gateway failure (`None` result, a rate missing an OHLC field) -- fail-closed, never a partial or
    fabricated bar."""
    rates = gateway.copy_rates_from(symbol, mt5_timeframe, now + broker_offset_seconds, count)
    if rates is None:
        raise BarFeedError(
            f"fetch_closed_bars: copy_rates_from({symbol!r}, timeframe={mt5_timeframe}) returned None"
        )

    bars: list[dict[str, object]] = []
    for rate in rates:
        ts_open = _read_field(rate, "time")
        open_ = _read_field(rate, "open")
        high = _read_field(rate, "high")
        low = _read_field(rate, "low")
        close = _read_field(rate, "close")
        if ts_open is None or open_ is None or high is None or low is None or close is None:
            raise BarFeedError(
                f"fetch_closed_bars: copy_rates_from({symbol!r}, timeframe={mt5_timeframe}) returned a "
                f"rate missing an OHLC field"
            )
        ts_open = int(ts_open) - broker_offset_seconds
        ts_close = ts_open + bar_seconds
        if ts_close > now:
            continue  # still forming -- never included, matching LiveBarFeed.poll()'s own rule
        bars.append({
            "time": ts_open, "open": float(open_), "high": float(high),
            "low": float(low), "close": float(close),
        })

    bars.sort(key=lambda b: b["time"])  # type: ignore[arg-type,return-value]
    return tuple(bars)


def fetch_tower_bar_windows(
    gateway: MT5Gateway, *, symbol: str, now: int, broker_offset_seconds: int = 0,
    m15_count: int = 150, m5_count: int = 150,
) -> tuple[tuple[dict[str, object], ...], tuple[dict[str, object], ...]]:
    """`(m15_closed_bars, m5_closed_bars)`, both as of the SAME `now`/`broker_offset_seconds`. Kept for
    callers that only need N3/N4's own two timeframes; `fetch_tower_chain_bar_windows` below is the
    RT-TOWER-0008 (2026-08-17) superset that also fetches H1 for the chain's own N2 (bias) node."""
    m15 = fetch_closed_bars(
        gateway, symbol=symbol, mt5_timeframe=MT5_TIMEFRAME_M15, bar_seconds=BAR_SECONDS_M15,
        count=m15_count, now=now, broker_offset_seconds=broker_offset_seconds,
    )
    m5 = fetch_closed_bars(
        gateway, symbol=symbol, mt5_timeframe=MT5_TIMEFRAME_M5, bar_seconds=BAR_SECONDS_M5,
        count=m5_count, now=now, broker_offset_seconds=broker_offset_seconds,
    )
    return m15, m5


def fetch_tower_chain_bar_windows(
    gateway: MT5Gateway, *, symbol: str, now: int, broker_offset_seconds: int = 0,
    h1_count: int = 150, m15_count: int = 150, m5_count: int = 150,
) -> tuple[tuple[dict[str, object], ...], tuple[dict[str, object], ...], tuple[dict[str, object], ...]]:
    """`(h1_closed_bars, m15_closed_bars, m5_closed_bars)`, all as of the SAME `now`/
    `broker_offset_seconds` -- the exact triple `ve_tower.ChainRequest` needs (RT-TOWER-0008, 2026-08-17:
    N2/bias now runs on H1, a REAL, chain-internal producer -- see `ve_tower.N2_EXPECTED_TIMEFRAME`)."""
    h1 = fetch_closed_bars(
        gateway, symbol=symbol, mt5_timeframe=MT5_TIMEFRAME_H1, bar_seconds=BAR_SECONDS_H1,
        count=h1_count, now=now, broker_offset_seconds=broker_offset_seconds,
    )
    m15, m5 = fetch_tower_bar_windows(
        gateway, symbol=symbol, now=now, broker_offset_seconds=broker_offset_seconds,
        m15_count=m15_count, m5_count=m5_count,
    )
    return h1, m15, m5


def detect_gaps(bars: tuple[dict[str, object], ...], *, symbol: str, bar_seconds: int) -> tuple[GapRecord, ...]:
    """Every place two consecutive bars in `bars` (already sorted oldest-first, as `fetch_closed_bars`
    always returns them) are not exactly `bar_seconds` apart -- classified via the SAME `classify_gap`
    `LiveBarFeed.poll()` itself uses, so a gap inside a tower window is labeled identically to how the
    same real event would be labeled if `LiveBarFeed` had seen it. Never filled, never estimated -- only
    reported, matching this codebase's own "golul se raporteaza, nu se umple" convention."""
    gaps: list[GapRecord] = []
    previous_time: int | None = None
    for bar in bars:
        ts_open = bar["time"]
        assert isinstance(ts_open, int)
        if previous_time is not None and ts_open != previous_time + bar_seconds:
            gaps.append(GapRecord(
                symbol=symbol, gap_start=previous_time, gap_end=ts_open,
                duration_seconds=ts_open - previous_time, classification=classify_gap(previous_time, ts_open),
                bars_backfilled=0, backfill_capped=False,
            ))
        previous_time = ts_open
    return tuple(gaps)
