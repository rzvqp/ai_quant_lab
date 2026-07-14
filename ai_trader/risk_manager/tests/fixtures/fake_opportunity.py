"""Convenience builders for real, schema-valid ``OpportunityScore`` objects (built through the REAL
Signal Engine + Scoring Engine pipelines, not hand-constructed dicts) plus ``PortfolioState``/
``RiskContext`` builders for Risk Manager tests.
"""

from __future__ import annotations

from typing import Any

from ai_trader.risk_manager.types import (
    ClosedPosition,
    OpenPosition,
    PortfolioState,
    RiskContext,
    SymbolRiskSnapshot,
)
from ai_trader.scoring_engine.config import ScoringConfig
from ai_trader.scoring_engine.engine import ScoringEngine
from ai_trader.scoring_engine.types import OpportunityScore
from ai_trader.signal_engine import assembler as se_assembler
from ai_trader.signal_engine import pipeline as se_pipeline
from ai_trader.signal_engine.config import EngineConfig
from ai_trader.signal_engine.tests.fixtures.fake_strategy import make_context, make_fake_handle
from ai_trader.signal_engine.types import StrategySignal


def make_signal(
    strategy_id: str = "S1", symbol: str = "XAUUSD",
    generate_signal_response: dict[str, Any] | None = None,
    detect_response: dict[str, Any] | None = None,
) -> StrategySignal:
    handle, api = make_fake_handle(strategy_id=strategy_id)
    if generate_signal_response is not None:
        api.generate_signal_response = generate_signal_response
    if detect_response is not None:
        api.detect_response = detect_response
    context = make_context(symbol=symbol)
    outcome = se_pipeline.run_pipeline(context, handle, trader_state=None)
    return se_assembler.assemble_signal(
        strategy_id=handle.id, contract=handle.contract, outcome=outcome, context=context,
        evaluation_time_ms=1.0, config=EngineConfig(), now_ts=context["meta"]["as_of"],
    )


def make_opportunity(
    strategy_id: str = "S1", symbol: str = "XAUUSD", direction: str = "LONG",
    entry: float = 100.0, stop: float = 99.0, target: float = 102.0, strength: float = 0.9,
    rank: int | None = None,
) -> OpportunityScore:
    """Build a real ``OpportunityScore`` -- an actionable BUY/SELL by default -- by running the
    actual Signal Engine + Scoring Engine pipelines end-to-end."""
    signal = make_signal(strategy_id=strategy_id, symbol=symbol, generate_signal_response={
        "present": True, "direction": direction, "entry": entry, "stop": stop, "target": target,
        "strength": strength, "confidence": "HIGH", "required_confirmations_met": True, "regime": (
            "TREND_UP" if direction == "LONG" else "TREND_DOWN"
        ),
    })
    engine = ScoringEngine(ScoringConfig())
    engine.configure(manager=None)
    score = engine.score_signal(signal)
    if rank is not None:
        from dataclasses import replace
        score = replace(score, rank=rank)
    return score


def make_below_floor_opportunity(strategy_id: str = "S1", symbol: str = "XAUUSD", rank: int | None = None) -> OpportunityScore:
    """A real, actionable (BUY) opportunity with its ``total_score``/``recommendation`` forced below
    the Risk Manager's default floor via ``dataclasses.replace`` -- for testing the Risk Manager's OWN
    ``RECOMMENDATION_FLOOR``/``MIN_SCORE`` gate logic in isolation.

    Tuning ``signal_strength`` alone cannot reliably produce a below-floor score through the real
    Scoring Engine: with no Strategy Manager configured (its own ``EVIDENCE_MISSING`` fallback),
    ``risk_penalty``/``regime_alignment`` default to a NEUTRAL 0.5 rather than 0, which keeps
    ``total_score`` structurally above the default floor of 25 for every ``signal_strength`` in
    [0,1] under the current default ``ScoringConfig`` -- a genuine floor of the Scoring Engine's own
    formula under those specific inputs, not a Risk Manager concern. Forcing the two fields directly
    tests exactly what the Risk Manager gate itself checks, without depending on that cross-engine
    arithmetic coincidence.
    """
    from dataclasses import replace

    from ai_trader.scoring_engine.types import Recommendation

    score = make_opportunity(strategy_id=strategy_id, symbol=symbol, strength=0.9, rank=rank)
    return replace(score, total_score=10, recommendation=Recommendation.SKIP)


def make_portfolio(
    equity: float = 100_000.0,
    equity_high_water_mark: float | None = None,
    open_positions: tuple[OpenPosition, ...] = (),
    recent_closed_positions: tuple[ClosedPosition, ...] = (),
    realized_pnl_pct_daily: float = 0.0,
    unrealized_pnl_pct_daily: float = 0.0,
    realized_pnl_pct_weekly: float = 0.0,
    unrealized_pnl_pct_weekly: float = 0.0,
    gross_notional: float = 0.0,
    consecutive_losses: int = 0,
    minutes_since_last_loss: float | None = None,
    is_stale: bool = False,
    as_of: int = 1_700_000_000,
) -> PortfolioState:
    return PortfolioState(
        as_of=as_of, equity=equity,
        equity_high_water_mark=equity_high_water_mark if equity_high_water_mark is not None else equity,
        open_positions=open_positions, recent_closed_positions=recent_closed_positions,
        realized_pnl_pct_daily=realized_pnl_pct_daily, unrealized_pnl_pct_daily=unrealized_pnl_pct_daily,
        realized_pnl_pct_weekly=realized_pnl_pct_weekly, unrealized_pnl_pct_weekly=unrealized_pnl_pct_weekly,
        gross_notional=gross_notional, consecutive_losses=consecutive_losses,
        minutes_since_last_loss=minutes_since_last_loss, is_stale=is_stale,
    )


def make_risk_context(
    symbol: str = "XAUUSD", as_of: int = 1_700_000_000, **snapshot_kwargs: Any,
) -> RiskContext:
    defaults: dict[str, Any] = {
        "atr": 1.0, "atr_rolling_median": 1.0, "current_spread": 0.2, "liquidity_proxy": 1000.0,
    }
    defaults.update(snapshot_kwargs)
    return RiskContext(as_of=as_of, per_symbol={symbol: SymbolRiskSnapshot(**defaults)})
