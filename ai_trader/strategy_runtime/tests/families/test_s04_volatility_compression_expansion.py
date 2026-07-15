"""Unit tests for S4 -- Volatility Compression Expansion: hand-constructed bar sequences plus
hand-constructed ``feature_history`` (the Phase 6.8 Wave B historical-features window), no live
data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s04_volatility_compression_expansion import (
    S04VolatilityCompressionExpansion,
)

CONTRACT_PATH = (
    Path(__file__).resolve().parents[4]
    / "knowledge" / "strategies" / "S04_volatility_compression_expansion" / "strategy.json"
)


def make_evaluator() -> S04VolatilityCompressionExpansion:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S04VolatilityCompressionExpansion("S4", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def flat_bars(n: int, price: float) -> list[dict]:  # type: ignore[type-arg]
    return [bar(1000 + i * 900, price, price + 0.1, price - 0.1, price) for i in range(n)]


def make_context(
    bars: list[dict], compress_flags: list[bool | None], atr: float | None = 1.0  # type: ignore[type-arg]
) -> dict:  # type: ignore[type-arg]
    history = [{"compress": f} if f is not None else None for f in compress_flags]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"m_atr": atr}, "bars": bars, "feature_history": history}},
    }


class TestNoSetup:
    def test_missing_atr_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(5, 2000.0)
        ctx = make_context(bars, [False] * 5, atr=None)
        assert ev.evaluate(ctx).setup_forming is False

    def test_insufficient_compress_history_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(2, 2000.0)
        ctx = make_context(bars, [False, False])
        assert ev.evaluate(ctx).setup_forming is False

    def test_no_prior_compression_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(4, 2000.0)
        bars.append(bar(bars[-1]["ts_close"] + 900, 2000.0, 2012.0, 1998.0, 2011.0))  # big expansion
        history = [False, False, False, False, True]
        ctx = make_context(bars, history, atr=1.0)
        assert ev.evaluate(ctx).setup_forming is False

    def test_no_expansion_bar_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(6, 2000.0)  # every bar's range is 0.2, well under 1.5*atr
        history = [False, False, False, True, False, False]
        ctx = make_context(bars, history, atr=1.0)
        assert ev.evaluate(ctx).setup_forming is False


class TestActionable:
    def test_expansion_after_prior_compression_is_actionable_long(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(4, 2000.0)
        bars.append(bar(bars[-1]["ts_close"] + 900, 2000.0, 2012.0, 1998.0, 2011.0))  # bullish expansion
        history = [False, False, False, True, False]  # n=1 ago compressed, satisfies min_compress=1
        ctx = make_context(bars, history, atr=1.0)
        result = ev.evaluate(ctx)
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.entry == 2011.0
        assert result.stop is not None and result.stop < result.entry
        assert result.target is None  # trailing-exit only, no fixed price target
        assert result.risk_R is None
        assert ev.trailing_stop_atr_mult == 1.5

    def test_expansion_after_prior_compression_is_actionable_short(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(4, 2000.0)
        bars.append(bar(bars[-1]["ts_close"] + 900, 2000.0, 2002.0, 1988.0, 1989.0))  # bearish expansion
        history = [False, False, True, False, False]  # n=2 ago compressed, satisfies min_compress=1
        ctx = make_context(bars, history, atr=1.0)
        result = ev.evaluate(ctx)
        assert result.setup_forming and result.present
        assert result.direction == "SHORT"
        assert result.entry == 1989.0
        assert result.stop is not None and result.stop > result.entry
