"""Unit tests for S25 -- Volatility-Regime Onset: hand-constructed bar sequences plus
hand-constructed ``feature_history`` (the Phase 6.8 Wave B historical-features window), no live
data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s25_volatility_regime_onset import (
    S25VolatilityRegimeOnset,
)

CONTRACT_PATH = (
    Path(__file__).resolve().parents[4]
    / "knowledge" / "strategies" / "S25_volatility_regime_onset" / "strategy.json"
)


def make_evaluator() -> S25VolatilityRegimeOnset:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S25VolatilityRegimeOnset("S25", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def flat_bars(n: int, price: float) -> list[dict]:  # type: ignore[type-arg]
    return [bar(1000 + i * 900, price, price + 0.1, price - 0.1, price) for i in range(n)]


def make_context(
    bars: list[dict], atr_history: list[float | None], atr_ma_history: list[float | None],  # type: ignore[type-arg]
    atr: float | None, atr_ma: float | None, sma: float | None = 2000.0,
    rmin20: float | None = 1990.0, rmax20: float | None = 2010.0,
) -> dict:  # type: ignore[type-arg]
    history = [
        {"m_atr": a, "atr_ma": am} if a is not None and am is not None else None
        for a, am in zip(atr_history, atr_ma_history)
    ]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {
            "M15": {
                "features": {"m_atr": atr, "atr_ma": atr_ma, "m_sma": sma, "rmin20": rmin20, "rmax20": rmax20},
                "bars": bars, "feature_history": history,
            }
        },
    }


class TestNoSetup:
    def test_missing_atr_ma_history_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(2, 2000.0)
        ctx = make_context(bars, [None, 1.5], [None, 1.0], atr=1.0, atr_ma=1.5)
        assert ev.evaluate(ctx).setup_forming is False

    def test_no_contraction_onset_when_already_low_vol_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(2, 2000.0)
        # both now and before are low-vol (atr < atr_ma) -- no transition
        ctx = make_context(bars, [1.0, 1.0], [1.5, 1.5], atr=1.0, atr_ma=1.5)
        assert ev.evaluate(ctx).setup_forming is False

    def test_expand_onset_is_not_contract_mode_no_setup(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(2, 2000.0)
        # before: low-vol (1.0<1.5); now: high-vol (2.0>1.5) -- this is an EXPAND onset, not contract
        ctx = make_context(bars, [1.0, 2.0], [1.5, 1.5], atr=2.0, atr_ma=1.5)
        assert ev.evaluate(ctx).setup_forming is False


class TestActionable:
    def test_contract_onset_below_sma_is_actionable_long(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(2, 1985.0)
        # before: high-vol (2.0>1.5); now: low-vol (1.0<1.5) -- CONTRACT onset
        ctx = make_context(bars, [2.0, 1.0], [1.5, 1.5], atr=1.0, atr_ma=1.5, sma=2000.0, rmin20=1980.0, rmax20=2010.0)
        result = ev.evaluate(ctx)
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"  # close (1985) < sma (2000) -- revert UP toward the mean
        assert result.entry == 1985.0
        assert result.stop is not None and result.stop < result.entry
        assert result.target is None  # time-exit only, no fixed price target
        assert result.risk_R is None
        assert ev.time_stop_bars == 24

    def test_contract_onset_above_sma_is_actionable_short(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(2, 2015.0)
        ctx = make_context(bars, [2.0, 1.0], [1.5, 1.5], atr=1.0, atr_ma=1.5, sma=2000.0, rmin20=1980.0, rmax20=2020.0)
        result = ev.evaluate(ctx)
        assert result.setup_forming and result.present
        assert result.direction == "SHORT"  # close (2015) > sma (2000) -- revert DOWN toward the mean
        assert result.entry == 2015.0
        assert result.stop is not None and result.stop > result.entry
