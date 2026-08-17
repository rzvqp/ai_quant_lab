"""Fixture-uri de bare pentru paritate/teste. Constantele BOS_BULL + logica de generare sunt COPIATE ca DATE din
`new_brain_bridge/tests/conftest.py` @21ae632 (deja verificate contra detectorilor reali) — VE decision (b): date, NU
algoritm, ca să nu depindem de un modul `tests/` la runtime. Reflectarea pentru TREND_DOWN e o transformare de date."""

from __future__ import annotations

from ve_n1_replay import Bar

SYMBOL = "XAUUSD"
BOS_BULL_HIGHS = [10, 11, 12, 13, 10, 9, 8, 12, 16, 12, 9, 8, 7, 11, 20, 14, 10, 9]
BOS_BULL_LOWS = [9, 10, 11, 12, 9, 8, 7, 11, 15, 11, 8, 7, 6, 10, 19, 13, 9, 8]
BOS_BULL_CLOSES = [h - 1 for h in BOS_BULL_HIGHS]
BOS_BULL_OPENS = [low_ + 0.5 for low_ in BOS_BULL_LOWS]
CALM_PREFIX_BARS = 460


def bos_bull_bars(symbol: str = SYMBOL) -> list[Bar]:
    return [Bar(symbol=symbol, ts_open=i * 900, ts_close=(i + 1) * 900, open=BOS_BULL_OPENS[i],
                high=BOS_BULL_HIGHS[i], low=BOS_BULL_LOWS[i], close=BOS_BULL_CLOSES[i], volume=100.0)
            for i in range(len(BOS_BULL_HIGHS))]


def trend_up_regime_bars(symbol: str = SYMBOL) -> list[Bar]:
    bars: list[Bar] = []
    price = 2400.0
    for i in range(CALM_PREFIX_BARS):
        o = price; h = o + 0.4; low_ = o - 0.4; c = o + 0.02
        bars.append(Bar(symbol=symbol, ts_open=i * 900, ts_close=(i + 1) * 900, open=o, high=h, low=low_, close=c,
                        volume=100.0))
        price = c
    for i, b in enumerate(bos_bull_bars(symbol)):
        off = CALM_PREFIX_BARS + i
        bars.append(Bar(symbol=symbol, ts_open=off * 900, ts_close=(off + 1) * 900, open=b.open, high=b.high,
                        low=b.low, close=b.close, volume=b.volume))
    return bars


def uncertain_regime_bars(symbol: str = SYMBOL, n: int = 60) -> list[Bar]:
    """Numai prefix calm (fără structură) ⇒ UNCERTAIN."""
    bars: list[Bar] = []
    price = 2400.0
    for i in range(n):
        o = price
        bars.append(Bar(symbol=symbol, ts_open=i * 900, ts_close=(i + 1) * 900, open=o, high=o + 0.4, low=o - 0.4,
                        close=o + 0.02, volume=100.0))
        price = o + 0.02
    return bars


def trend_down_regime_bars(symbol: str = SYMBOL) -> list[Bar]:
    """Reflectare verticală (în jurul lui 26) a secvenței BOS_BULL ⇒ BOS_BEAR/jos, cu prefix calm descendent."""
    bars: list[Bar] = []
    price = 2400.0
    for i in range(CALM_PREFIX_BARS):
        o = price
        bars.append(Bar(symbol=symbol, ts_open=i * 900, ts_close=(i + 1) * 900, open=o, high=o + 0.4, low=o - 0.4,
                        close=o - 0.02, volume=100.0))
        price = o - 0.02
    for i in range(len(BOS_BULL_HIGHS)):
        off = CALM_PREFIX_BARS + i
        h = 26.0 - BOS_BULL_LOWS[i]; low_ = 26.0 - BOS_BULL_HIGHS[i]
        c = 26.0 - BOS_BULL_CLOSES[i]; o = 26.0 - BOS_BULL_OPENS[i]
        bars.append(Bar(symbol=symbol, ts_open=off * 900, ts_close=(off + 1) * 900, open=o, high=h, low=low_,
                        close=c, volume=100.0))
    return bars
