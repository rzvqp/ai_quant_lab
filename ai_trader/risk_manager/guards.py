"""Loss & Drawdown Guards + Cooldowns (``RISK_MANAGER_ARCHITECTURE.md`` §4/§5 stages 5-6,
``RISK_POLICY.md`` §3/§4). Loss/drawdown guards additionally signal a GLOBAL state escalation
(``RISK_POLICY.md`` §3's "escalation" column) -- the caller (:mod:`ai_trader.risk_manager.engine`)
applies that escalation to the engine's own state, this module only reports what escalation (if any)
a breach implies, staying a pure function of its inputs.
"""

from __future__ import annotations

from dataclasses import dataclass

from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.types import DeniedReason, EngineState, PortfolioState


@dataclass(frozen=True, slots=True)
class GuardResult:
    passed: bool
    reason: DeniedReason | None = None
    escalate_to: EngineState | None = None


def check_daily_loss(portfolio: PortfolioState, config: RiskConfig) -> GuardResult:
    observed = portfolio.daily_pnl_pct
    limit = -config.loss_drawdown.max_daily_loss_pct
    if observed <= limit:
        return GuardResult(
            False, DeniedReason(code="LOSS_DAILY", observed=observed, limit=limit), EngineState.SUSPENDED,
        )
    return GuardResult(True)


def check_weekly_loss(portfolio: PortfolioState, config: RiskConfig) -> GuardResult:
    observed = portfolio.weekly_pnl_pct
    limit = -config.loss_drawdown.max_weekly_loss_pct
    if observed <= limit:
        return GuardResult(
            False, DeniedReason(code="LOSS_WEEKLY", observed=observed, limit=limit), EngineState.SUSPENDED,
        )
    return GuardResult(True)


def check_max_drawdown(portfolio: PortfolioState, config: RiskConfig) -> GuardResult:
    observed = portfolio.drawdown_pct
    limit = config.loss_drawdown.max_drawdown_pct
    if observed >= limit:
        return GuardResult(
            False, DeniedReason(code="DRAWDOWN_MAX", observed=observed, limit=limit), EngineState.SUSPENDED,
        )
    return GuardResult(True)


def check_cooldown_after_loss(symbol: str, portfolio: PortfolioState, config: RiskConfig) -> GuardResult:
    threshold = config.cooldowns.after_loss_bars
    for closed in portfolio.recent_closed_positions:
        if closed.symbol == symbol and closed.was_loss and closed.bars_since_close < threshold:
            return GuardResult(False, DeniedReason(
                code="COOLDOWN_AFTER_LOSS", observed=closed.bars_since_close, limit=threshold,
            ))
    return GuardResult(True)


def check_cooldown_consecutive(portfolio: PortfolioState, config: RiskConfig) -> GuardResult:
    if portfolio.consecutive_losses < config.cooldowns.consecutive_loss_count:
        return GuardResult(True)
    minutes = portfolio.minutes_since_last_loss
    threshold = config.cooldowns.consecutive_loss_cooldown_minutes
    if minutes is None or minutes < threshold:
        return GuardResult(False, DeniedReason(
            code="COOLDOWN_CONSECUTIVE", observed=minutes, limit=threshold,
        ))
    return GuardResult(True)


def check_cooldown_strategy(strategy_id: str, portfolio: PortfolioState, config: RiskConfig) -> GuardResult:
    threshold = config.cooldowns.per_strategy_cooldown_bars.get(strategy_id, 0)
    if threshold <= 0:
        return GuardResult(True)
    for closed in portfolio.recent_closed_positions:
        if closed.strategy_id == strategy_id and closed.bars_since_close < threshold:
            return GuardResult(False, DeniedReason(
                code="COOLDOWN_STRATEGY", observed=closed.bars_since_close, limit=threshold,
            ))
    return GuardResult(True)


def run_loss_drawdown_guards(portfolio: PortfolioState, config: RiskConfig) -> list[tuple[str, GuardResult]]:
    """``RISK_POLICY.md`` §3's fixed table order."""
    return [
        ("LOSS_DAILY", check_daily_loss(portfolio, config)),
        ("LOSS_WEEKLY", check_weekly_loss(portfolio, config)),
        ("DRAWDOWN_MAX", check_max_drawdown(portfolio, config)),
    ]


def run_cooldowns(symbol: str, strategy_id: str, portfolio: PortfolioState, config: RiskConfig) -> list[tuple[str, GuardResult]]:
    """``RISK_POLICY.md`` §4's fixed table order."""
    return [
        ("COOLDOWN_AFTER_LOSS", check_cooldown_after_loss(symbol, portfolio, config)),
        ("COOLDOWN_CONSECUTIVE", check_cooldown_consecutive(portfolio, config)),
        ("COOLDOWN_STRATEGY", check_cooldown_strategy(strategy_id, portfolio, config)),
    ]
