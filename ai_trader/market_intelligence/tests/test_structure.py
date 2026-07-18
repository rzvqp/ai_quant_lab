"""Unit tests for :mod:`ai_trader.market_intelligence.structure`. Uses ``fractal_bars=1`` (the
module's own exposed parameter) throughout -- the SAME algorithm as the default, just needing far
fewer hand-constructed bars per confirmed swing (1 bar on each side instead of 3), which keeps these
fixtures small and hand-verifiable.
"""

from __future__ import annotations

from ai_trader.market_intelligence.structure import analyze_structure
from ai_trader.market_intelligence.types import StructureState


def _bar(ts: int, high: float, low: float, close: float | None = None) -> dict[str, object]:
    return {"ts_open": ts - 900, "ts_close": ts, "open": low, "high": high, "low": low, "close": close if close is not None else high, "volume": 100.0}


def _context(bars: list[dict[str, object]]) -> dict[str, object]:
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "timeframes": {"M15": {"bars": bars, "features": {}, "feature_history": []}},
        "data_quality": {"level": "OK"},
    }


def test_structure_bullish_bos() -> None:
    # Two ascending swing lows (1990 -> 1995) and two ascending swing highs (2010 -> 2020) --
    # bullish prevailing structure -- then the final bar closes above the most recent swing high
    # (2020), a continuation break: BULLISH_BOS.
    bars = [
        _bar(0, high=2000, low=2000),                      # idx0
        _bar(900, high=2000, low=1990),                     # idx1: swing low #1 (1990)
        _bar(1800, high=2000, low=2000),                    # idx2
        _bar(2700, high=2010, low=2000),                    # idx3: swing high #1 (2010)
        _bar(3600, high=2000, low=2000),                    # idx4
        _bar(4500, high=2000, low=1995),                    # idx5: swing low #2 (1995, higher-low)
        _bar(5400, high=2000, low=2000),                    # idx6
        _bar(6300, high=2020, low=2000),                    # idx7: swing high #2 (2020, higher-high)
        _bar(7200, high=2000, low=2000),                    # idx8: confirms idx7
        _bar(8100, high=2030, low=2020, close=2025),        # idx9: current bar, closes above 2020
    ]
    reading = analyze_structure(_context(bars), fractal_bars=1)
    assert reading.state is StructureState.BULLISH_BOS
    assert reading.last_swing_high is not None and reading.last_swing_high.price == 2020
    assert reading.last_swing_low is not None and reading.last_swing_low.price == 1995


def test_structure_bullish_choch() -> None:
    # Two descending swing lows (1980 -> 1970) and two descending swing highs (2040 -> 2030) --
    # bearish prevailing structure -- then the final bar closes ABOVE the most recent swing high
    # (2030), the OPPOSITE direction to the prevailing structure: BULLISH_CHOCH.
    bars = [
        _bar(0, high=2000, low=2000),
        _bar(900, high=2000, low=1980),                     # idx1: swing low #1 (1980)
        _bar(1800, high=2000, low=2000),
        _bar(2700, high=2040, low=2000),                     # idx3: swing high #1 (2040)
        _bar(3600, high=2000, low=2000),
        _bar(4500, high=2000, low=1970),                     # idx5: swing low #2 (1970, lower-low)
        _bar(5400, high=2000, low=2000),
        _bar(6300, high=2030, low=2000),                     # idx7: swing high #2 (2030, lower-high)
        _bar(7200, high=2000, low=2000),
        _bar(8100, high=2040, low=2030, close=2035),         # idx9: closes above 2030
    ]
    reading = analyze_structure(_context(bars), fractal_bars=1)
    assert reading.state is StructureState.BULLISH_CHOCH


def test_structure_ranging_when_no_break() -> None:
    bars = [
        _bar(0, high=2000, low=2000),
        _bar(900, high=2000, low=1990),
        _bar(1800, high=2000, low=2000),
        _bar(2700, high=2010, low=2000),
        _bar(3600, high=2000, low=2000),
        _bar(4500, high=2000, low=1995),
        _bar(5400, high=2000, low=2000),
        _bar(6300, high=2020, low=2000),
        _bar(7200, high=2000, low=2000),
        _bar(8100, high=2005, low=1998, close=2002),  # stays comfortably inside [1995, 2020]
    ]
    reading = analyze_structure(_context(bars), fractal_bars=1)
    assert reading.state is StructureState.RANGING


def test_structure_unknown_with_insufficient_bars() -> None:
    bars = [_bar(0, high=2000, low=2000), _bar(900, high=2001, low=1999)]
    reading = analyze_structure(_context(bars), fractal_bars=3)
    assert reading.state is StructureState.UNKNOWN
    assert reading.last_swing_high is None
    assert reading.last_swing_low is None


def test_structure_bearish_bos() -> None:
    # Mirror image of the bullish BOS case: two descending swing highs and two descending swing lows
    # (bearish prevailing structure), then the final bar closes BELOW the most recent swing low -- a
    # continuation break in the SAME (bearish) direction: BEARISH_BOS.
    bars = [
        _bar(0, high=2000, low=2000),
        _bar(900, high=2020, low=2000),                      # idx1: swing high #1 (2020)
        _bar(1800, high=2000, low=2000),
        _bar(2700, high=2000, low=1990),                      # idx3: swing low #1 (1990)
        _bar(3600, high=2000, low=2000),
        _bar(4500, high=2010, low=2000),                      # idx5: swing high #2 (2010, lower-high)
        _bar(5400, high=2000, low=2000),
        _bar(6300, high=2000, low=1980),                      # idx7: swing low #2 (1980, lower-low)
        _bar(7200, high=2000, low=2000),                      # idx8: confirms idx7
        _bar(8100, high=1985, low=1970, close=1975),          # idx9: current bar, closes below 1980
    ]
    reading = analyze_structure(_context(bars), fractal_bars=1)
    assert reading.state is StructureState.BEARISH_BOS


def test_structure_unclear_prevailing_when_fewer_than_two_swings() -> None:
    # Only ONE confirmed swing high AND ONE confirmed swing low exist -- _prevailing_structure's own
    # "fewer than two of either kind" branch -- so any break is classified as CHOCH (never BOS,
    # since UNCLEAR never equals "BULLISH"/"BEARISH").
    bars = [
        _bar(0, high=2000, low=2000),
        _bar(900, high=2000, low=1990),                        # idx1: the only swing low
        _bar(1800, high=2000, low=2000),
        _bar(2700, high=2010, low=2000),                        # idx3: the only swing high
        _bar(3600, high=2000, low=2000),
        _bar(4500, high=2020, low=2010, close=2015),            # idx5: current bar, breaks above 2010
    ]
    reading = analyze_structure(_context(bars), fractal_bars=1)
    assert reading.state is StructureState.BULLISH_CHOCH


def test_structure_unclear_prevailing_when_highs_and_lows_disagree() -> None:
    # Higher-high (2010 -> 2020) but LOWER-low (1990 -> 1980) -- a genuinely mixed/expanding market,
    # neither cleanly bullish nor bearish. _prevailing_structure's own "highs and lows disagree"
    # branch -- any break is classified as CHOCH, never BOS.
    bars = [
        _bar(0, high=2000, low=2000),
        _bar(900, high=2000, low=1990),                        # idx1: swing low #1 (1990)
        _bar(1800, high=2000, low=2000),
        _bar(2700, high=2010, low=2000),                        # idx3: swing high #1 (2010)
        _bar(3600, high=2000, low=2000),
        _bar(4500, high=2000, low=1980),                        # idx5: swing low #2 (1980, LOWER-low)
        _bar(5400, high=2000, low=2000),
        _bar(6300, high=2020, low=2000),                        # idx7: swing high #2 (2020, higher-high)
        _bar(7200, high=2000, low=2000),                        # idx8: confirms idx7
        _bar(8100, high=2030, low=2020, close=2025),            # idx9: breaks above 2020
    ]
    reading = analyze_structure(_context(bars), fractal_bars=1)
    assert reading.state is StructureState.BULLISH_CHOCH


def test_structure_is_deterministic() -> None:
    bars = [
        _bar(0, high=2000, low=2000),
        _bar(900, high=2000, low=1990),
        _bar(1800, high=2000, low=2000),
        _bar(2700, high=2010, low=2000),
        _bar(3600, high=2000, low=2000),
        _bar(4500, high=2000, low=1995),
        _bar(5400, high=2000, low=2000),
        _bar(6300, high=2020, low=2000),
        _bar(7200, high=2000, low=2000),
        _bar(8100, high=2030, low=2020, close=2025),
    ]
    ctx = _context(bars)
    assert analyze_structure(ctx, fractal_bars=1) == analyze_structure(ctx, fractal_bars=1)
