"""Pure aggregation functions -- compute the `ExposureSnapshot` a `PortfolioDecision` is based on.
Never mutates `PortfolioState`; never touches wall-clock; the pending trade is always included in every
aggregate (Portfolio Manager evaluates the book AS IT WOULD BE if this trade were admitted, not the book
as it is today)."""

from __future__ import annotations

from ai_trader.portfolio_manager_live.types import ExposureSnapshot, PortfolioAuthorizationRequest, PortfolioManagerConfig
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.types import OpenPosition, PortfolioState
from ai_trader.signal_engine.types import Direction


def build_exposure_snapshot(
    request: PortfolioAuthorizationRequest, portfolio: PortfolioState, config: PortfolioManagerConfig,
) -> ExposureSnapshot:
    per_symbol: dict[str, float] = {}
    per_direction: dict[str, float] = {}
    per_strategy: dict[str, float] = {}
    per_asset_class: dict[str, float] = {}

    def _add(bucket: dict[str, float], key: str, amount: float) -> None:
        bucket[key] = bucket.get(key, 0.0) + amount

    for position in portfolio.open_positions:
        _add(per_symbol, position.symbol, position.risk_pct)
        _add(per_direction, position.direction.value, position.risk_pct)
        _add(per_strategy, position.strategy_id, position.risk_pct)
        _add(per_asset_class, config.asset_class_for(position.symbol), position.risk_pct)

    _add(per_symbol, request.symbol, request.approved_risk_pct)
    _add(per_direction, request.direction.value, request.approved_risk_pct)
    _add(per_strategy, request.strategy_id, request.approved_risk_pct)
    _add(per_asset_class, config.asset_class_for(request.symbol), request.approved_risk_pct)

    total_exposure_pct = portfolio.portfolio_risk_pct + request.approved_risk_pct
    portfolio_heat_pct = total_exposure_pct  # PORTFOLIO_MANAGER_PHASE4_DESIGN.md §3: same formula as
    # total exposure, evaluated against a SEPARATE, distinctly-named ceiling -- not a fabricated
    # alternative metric.

    return ExposureSnapshot(
        total_exposure_pct=total_exposure_pct,
        per_symbol_exposure_pct=per_symbol,
        per_direction_exposure_pct=per_direction,
        per_strategy_exposure_pct=per_strategy,
        per_asset_class_exposure_pct=per_asset_class,
        pending_session_heat_pct=request.approved_risk_pct,
        portfolio_heat_pct=portfolio_heat_pct,
        reserved_capital_pct=config.reserved_capital_pct,
        available_capital_pct=1.0 - config.reserved_capital_pct,
    )


_OPPOSITE_DIRECTION = {Direction.LONG: Direction.SHORT, Direction.SHORT: Direction.LONG}


def find_long_short_conflicts(
    request: PortfolioAuthorizationRequest, portfolio: PortfolioState, risk_config: RiskConfig,
) -> tuple[OpenPosition, ...]:
    """Any existing open position sharing a SYMBOL or CORRELATION GROUP (via the reused
    `RiskConfig.correlation_group_for`) with `request`, whose direction OPPOSES `request.direction`."""
    opposite = _OPPOSITE_DIRECTION.get(request.direction)
    if opposite is None:
        return ()
    request_group = risk_config.correlation_group_for(request.symbol)
    conflicts = [
        position for position in portfolio.open_positions
        if position.direction is opposite
        and (
            position.symbol == request.symbol
            or risk_config.correlation_group_for(position.symbol) == request_group
        )
    ]
    return tuple(conflicts)
