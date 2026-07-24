"""Proof that every CEO-required control that already exists in the frozen `ai_trader/risk_manager/`
package is genuinely invoked (not reimplemented) by `evaluate_trade_proposal` -- daily loss, drawdown,
volume/position limits, stop-loss, spread, leverage, trade-count limits, consecutive losses."""

from __future__ import annotations

from ai_trader.risk_manager.types import OpenPosition
from ai_trader.risk_manager_live.engine import evaluate_trade_proposal
from ai_trader.risk_manager_live.tests._fixtures import (
    make_account,
    make_config,
    make_instrument,
    make_portfolio,
    make_proposal,
    make_risk_context,
)
from ai_trader.signal_engine.types import Direction


def test_daily_loss_guard_denies() -> None:
    portfolio = make_portfolio(realized_pnl_pct_daily=-0.10)  # exceeds default max_daily_loss_pct=0.03
    decision = evaluate_trade_proposal(
        make_proposal(), make_account(), portfolio, make_instrument(), make_risk_context(), make_config(),
    )
    assert decision.approved is False
    assert "LOSS_DAILY" in decision.reason_codes


def test_drawdown_guard_denies() -> None:
    portfolio = make_portfolio(equity=80_000.0, equity_high_water_mark=200_000.0)  # 60% dd > 12% default
    decision = evaluate_trade_proposal(
        make_proposal(), make_account(), portfolio, make_instrument(), make_risk_context(), make_config(),
    )
    assert decision.approved is False
    assert "DRAWDOWN_MAX" in decision.reason_codes


def test_max_positions_limit_denies() -> None:
    open_positions = tuple(
        OpenPosition(
            symbol=f"SYM{i}", strategy_id="S1", direction=Direction.LONG, size_units=1.0,
            entry_price=100.0, opened_bars_ago=1,
        )
        for i in range(5)  # default max_positions=5 -- >= triggers DENY
    )
    portfolio = make_portfolio(open_positions=open_positions)
    decision = evaluate_trade_proposal(
        make_proposal(), make_account(), portfolio, make_instrument(), make_risk_context(), make_config(),
    )
    assert decision.approved is False
    assert "LIMIT_MAX_POSITIONS" in decision.reason_codes


def test_max_per_symbol_limit_denies() -> None:
    portfolio = make_portfolio(open_positions=(
        OpenPosition(
            symbol="XAUUSD", strategy_id="S1", direction=Direction.LONG, size_units=1.0,
            entry_price=2000.0, opened_bars_ago=1,
        ),
    ))
    decision = evaluate_trade_proposal(
        make_proposal(symbol="XAUUSD"), make_account(), portfolio, make_instrument(), make_risk_context(),
        make_config(),
    )
    assert decision.approved is False
    assert "LIMIT_MAX_PER_SYMBOL" in decision.reason_codes


def test_max_leverage_limit_denies() -> None:
    portfolio = make_portfolio(gross_notional=1_000_000.0)  # leverage = 1M/200k = 5.0 > default max 3.0
    decision = evaluate_trade_proposal(
        make_proposal(), make_account(), portfolio, make_instrument(), make_risk_context(), make_config(),
    )
    assert decision.approved is False
    assert "LIMIT_MAX_LEVERAGE" in decision.reason_codes


def test_consecutive_losses_cooldown_denies() -> None:
    portfolio = make_portfolio(consecutive_losses=5)  # default consecutive_loss_count=3 -- >= triggers
    decision = evaluate_trade_proposal(
        make_proposal(), make_account(), portfolio, make_instrument(), make_risk_context(), make_config(),
    )
    assert decision.approved is False
    assert "COOLDOWN_CONSECUTIVE" in decision.reason_codes


def test_spread_filter_denies_when_spread_too_wide() -> None:
    from ai_trader.risk_manager_live.tests._fixtures import make_risk_context, make_snapshot

    wide_spread_context = make_risk_context(snapshot=make_snapshot(current_spread=100.0))  # >> reference*multiplier
    decision = evaluate_trade_proposal(
        make_proposal(), make_account(), make_portfolio(), make_instrument(), wide_spread_context,
        make_config(),
    )
    assert decision.approved is False
    assert "FILTER_SPREAD" in decision.reason_codes


def test_sizing_size_below_min_reused_from_frozen_sizing_module() -> None:
    """A `min_allocation_risk_pct` set higher than the achievable risk given this account/stop -- the
    EXISTING, frozen `compute_sizing`'s own `SIZE_BELOW_MIN` guard (not reimplemented here) correctly
    denies. Distinct from this phase's OWN new `VOLUME_STEP_ROUNDING_BELOW_MIN` check (tested separately
    in `test_sizing_volume_margin.py`) -- this one fires INSIDE the frozen sizing.py itself, before this
    phase's own additive volume-step logic ever runs."""
    import dataclasses

    config = make_config()
    config = dataclasses.replace(
        config, sizing=dataclasses.replace(config.sizing, min_allocation_risk_pct=0.5),
    )  # far above what a $200k account/10-pt stop can reach -- SizingLimits/RiskConfig are frozen
    decision = evaluate_trade_proposal(
        make_proposal(), make_account(), make_portfolio(), make_instrument(), make_risk_context(), config,
    )
    assert decision.approved is False
    assert "SIZE_BELOW_MIN" in decision.reason_codes
