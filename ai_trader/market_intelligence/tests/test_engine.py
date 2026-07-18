"""Unit tests for :mod:`ai_trader.market_intelligence.engine` -- the public
``build_market_intelligence()`` entry point. Real-data integration coverage lives in
``ai_trader/market_intelligence/tests/test_integration.py``.
"""

from __future__ import annotations

from ai_trader.market_intelligence.engine import build_market_intelligence
from ai_trader.market_intelligence.tests._fixtures import make_context


def test_build_market_intelligence_with_full_data() -> None:
    ctx = make_context(
        m15_features={
            "m_trend_up": True, "m_ema20": 2010.0, "m_ema50": 2000.0,
            "h1_trend_up": True, "h4_trend_up": True, "d1_trend_up": False,
            "m_rsi": 65.0, "roc3": 0.01, "h1_rsi": 55.0, "h4_rsi": 45.0, "d1_rsi": 60.0,
            "m_atr": 1.0, "atr_ma": 1.0, "m_volrank": 0.6,
            "compress": False, "disp": False,
            "session": "LONDON", "bar_in_sess": 5, "or_high": 2015.0, "or_low": 2005.0, "vwap": 2008.0, "gap": 0.5,
        },
        m15_bars=[{"ts_open": 0, "ts_close": 1, "open": 2000, "high": 2012, "low": 1998, "close": 2010.0, "volume": 1200}],
    )
    snapshot = build_market_intelligence(ctx)

    assert snapshot.symbol == "XAUUSD"
    assert set(snapshot.trend) == {"M15", "H1", "H4", "D1"}
    assert set(snapshot.momentum) == {"M15", "H1", "H4", "D1"}
    assert snapshot.structure.timeframe == "M15"
    assert snapshot.volatility.regime is not None
    assert snapshot.liquidity.state is not None
    assert snapshot.expansion.state is not None
    assert snapshot.session.session_name == "LONDON"
    assert snapshot.multi_timeframe_agreement.agreement_score is not None
    assert snapshot.confidence.score is not None


def test_build_market_intelligence_with_no_data_is_honest_not_fabricated() -> None:
    # Every dimension must degrade to UNKNOWN/None gracefully -- never raise, never fabricate.
    ctx = make_context(m15_features={}, m15_bars=[])
    snapshot = build_market_intelligence(ctx)
    assert snapshot.trend["M15"].direction.value == "UNKNOWN"
    assert snapshot.volatility.regime.value == "UNKNOWN"
    assert snapshot.structure.state.value == "UNKNOWN"
    assert snapshot.confidence.score is not None  # data_quality_ok=True (default "OK"), still computes


def test_build_market_intelligence_is_deterministic() -> None:
    ctx = make_context(m15_features={"m_trend_up": True, "m_rsi": 55.0, "m_atr": 1.0, "atr_ma": 1.0})
    assert build_market_intelligence(ctx) == build_market_intelligence(ctx)


def test_build_market_intelligence_never_mutates_the_input_context() -> None:
    ctx = make_context(m15_features={"m_trend_up": True})
    import copy
    before = copy.deepcopy(ctx)
    build_market_intelligence(ctx)
    assert ctx == before
