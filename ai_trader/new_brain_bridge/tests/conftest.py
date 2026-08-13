"""Shared fixtures for `new_brain_bridge` tests -- one hand-verified OHLC sequence that produces a
genuine, confirmed `bos_bull` structure break through the REAL vendored detectors (`structural_observer
.vendor_bridge.detect_swings`/`label_structure`/`detect_breaks`), not asserted from a mental model of
the algorithm. Verified directly against the vendored functions before being adopted here: two swing
highs (idx 3 @ 13, UNCLASSIFIED as the first-of-kind; idx 8 @ 16, labeled HH since 16 > 13) plus one
swing low (idx 12 @ 6, labeled LL), then a close at idx 14 (19) that clears the HH reference (16) --
`detect_breaks` reports exactly one `BOS_BULL` at idx 14, reference price 16."""

from __future__ import annotations

from ai_trader.live_signal_source.types import Bar

BOS_BULL_HIGHS = [10, 11, 12, 13, 10, 9, 8, 12, 16, 12, 9, 8, 7, 11, 20, 14, 10, 9]
BOS_BULL_LOWS = [9, 10, 11, 12, 9, 8, 7, 11, 15, 11, 8, 7, 6, 10, 19, 13, 9, 8]
BOS_BULL_CLOSES = [h - 1 for h in BOS_BULL_HIGHS]
BOS_BULL_OPENS = [low_ + 0.5 for low_ in BOS_BULL_LOWS]
#: 0-indexed position at which `detect_breaks` reports the confirmed BOS_BULL (verified above).
BOS_BULL_CONFIRMED_AT_INDEX = 14


def bos_bull_bars(symbol: str = "XAUUSD") -> list[Bar]:
    return [
        Bar(symbol=symbol, ts_open=i * 900, ts_close=(i + 1) * 900, open=BOS_BULL_OPENS[i],
            high=BOS_BULL_HIGHS[i], low=BOS_BULL_LOWS[i], close=BOS_BULL_CLOSES[i], volume=100.0)
        for i in range(len(BOS_BULL_HIGHS))
    ]


#: `compression()`'s own trailing window (`market_state.COMPRESSION_WINDOW`) is 460 bars -- until that
#: many bars accumulate, `is_compressed` is honestly `None`, and `applicable_regimes` treats ANY `None`
#: axis (not just structure/direction) as `UNCERTAIN`. A calm 460-bar prefix, independently verified
#: below to land on a real, defined `TREND_UP` regime once the BOS sequence is appended, is the ONLY way
#: to exercise a genuine `StrategyRouter` NORMAL-eligible path with all four axes resolved.
CALM_PREFIX_BARS = 460


def trend_up_regime_bars(symbol: str = "XAUUSD") -> list[Bar]:
    """460 calm bars (to clear the compression window) followed by `bos_bull_bars()`, re-timestamped to
    continue immediately after. Independently verified (this module's own test coverage) to leave the
    LAST bar reading `structure="strong"`, `direction="up"`, `applicable_regimes=={TREND_UP}` -- not
    merely hoped for."""
    bars: list[Bar] = []
    price = 2400.0
    for i in range(CALM_PREFIX_BARS):
        o = price
        h = o + 0.4
        low_ = o - 0.4
        c = o + 0.02
        bars.append(Bar(symbol=symbol, ts_open=i * 900, ts_close=(i + 1) * 900, open=o, high=h,
                         low=low_, close=c, volume=100.0))
        price = c

    for i, b in enumerate(bos_bull_bars(symbol)):
        offset = CALM_PREFIX_BARS + i
        bars.append(Bar(symbol=symbol, ts_open=offset * 900, ts_close=(offset + 1) * 900, open=b.open,
                         high=b.high, low=b.low, close=b.close, volume=b.volume))
    return bars
