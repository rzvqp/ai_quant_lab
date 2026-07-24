"""`evaluate_portfolio_authorization` -- Portfolio Manager's single public entry point. Pure function: no
state, no I/O, no MT5 terminal API import (verified by `tests/test_import_independence.py`). Gates an
already-Risk-Manager-APPROVED trade at the aggregate-book level (CEO rule 8: no module may bypass Risk
Manager or Portfolio Manager). Every check runs to completion -- never short-circuited -- for a complete
audit trail (same discipline as `risk_manager_live.engine`)."""

from __future__ import annotations

from ai_trader.portfolio_manager_live import reason_codes as rc
from ai_trader.portfolio_manager_live.aggregation import build_exposure_snapshot, find_long_short_conflicts
from ai_trader.portfolio_manager_live.types import (
    CalculationTraceStep,
    PortfolioAuthorizationRequest,
    PortfolioDailyState,
    PortfolioDecision,
    PortfolioManagerConfig,
)
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.types import PortfolioState


def _deny(reason_codes: list[str], trace: list[CalculationTraceStep], warnings: list[str] | None = None) -> PortfolioDecision:
    return PortfolioDecision(
        approved=False, reason_codes=tuple(reason_codes), exposure_snapshot=None,
        warnings=tuple(warnings or ()), calculation_trace=tuple(trace),
    )


def evaluate_portfolio_authorization(
    request: PortfolioAuthorizationRequest, portfolio: PortfolioState, daily_state: PortfolioDailyState,
    risk_config: RiskConfig, config: PortfolioManagerConfig | None = None,
) -> PortfolioDecision:
    resolved_config = config if config is not None else PortfolioManagerConfig()
    trace: list[CalculationTraceStep] = []
    reason_codes: list[str] = []

    try:
        snapshot = build_exposure_snapshot(request, portfolio, resolved_config)
        conflicts = find_long_short_conflicts(request, portfolio, risk_config)
    except Exception as exc:  # noqa: BLE001 -- fail-closed: any aggregation failure denies, never raises,
        # matching every prior module's own exception-safety discipline at its public boundary.
        trace.append(CalculationTraceStep("AGGREGATION", False, detail=f"unexpected exception: {exc}"))
        return _deny([rc.PORTFOLIO_STATE_UNAVAILABLE], trace)

    total_ok = snapshot.total_exposure_pct <= resolved_config.max_total_exposure_pct
    trace.append(CalculationTraceStep(
        "TOTAL_EXPOSURE", total_ok, observed=snapshot.total_exposure_pct,
        limit=resolved_config.max_total_exposure_pct,
    ))
    if not total_ok:
        reason_codes.append(rc.PORTFOLIO_TOTAL_EXPOSURE)

    reserved_ok = snapshot.total_exposure_pct <= snapshot.available_capital_pct
    trace.append(CalculationTraceStep(
        "RESERVED_CAPITAL", reserved_ok, observed=snapshot.total_exposure_pct,
        limit=snapshot.available_capital_pct,
    ))
    if not reserved_ok:
        reason_codes.append(rc.PORTFOLIO_RESERVED_CAPITAL)

    direction_exposure = snapshot.per_direction_exposure_pct.get(request.direction.value, 0.0)
    direction_ok = direction_exposure <= resolved_config.max_direction_exposure_pct
    trace.append(CalculationTraceStep(
        "DIRECTION_EXPOSURE", direction_ok, observed=direction_exposure,
        limit=resolved_config.max_direction_exposure_pct,
    ))
    if not direction_ok:
        reason_codes.append(rc.PORTFOLIO_DIRECTION_EXPOSURE)

    strategy_exposure = snapshot.per_strategy_exposure_pct.get(request.strategy_id, 0.0)
    strategy_ok = strategy_exposure <= resolved_config.max_strategy_exposure_pct
    trace.append(CalculationTraceStep(
        "STRATEGY_EXPOSURE", strategy_ok, observed=strategy_exposure,
        limit=resolved_config.max_strategy_exposure_pct,
    ))
    if not strategy_ok:
        reason_codes.append(rc.PORTFOLIO_STRATEGY_EXPOSURE)

    session_used = daily_state.session_heat_used_pct.get(request.session, 0.0)
    session_exposure = session_used + request.approved_risk_pct
    session_ok = session_exposure <= resolved_config.max_session_exposure_pct
    trace.append(CalculationTraceStep(
        "SESSION_EXPOSURE", session_ok, observed=session_exposure,
        limit=resolved_config.max_session_exposure_pct,
    ))
    if not session_ok:
        reason_codes.append(rc.PORTFOLIO_SESSION_EXPOSURE)

    asset_class = resolved_config.asset_class_for(request.symbol)
    asset_class_exposure = snapshot.per_asset_class_exposure_pct.get(asset_class, 0.0)
    asset_class_ok = asset_class_exposure <= resolved_config.max_asset_class_exposure_pct
    trace.append(CalculationTraceStep(
        "ASSET_CLASS_EXPOSURE", asset_class_ok, observed=asset_class_exposure,
        limit=resolved_config.max_asset_class_exposure_pct,
    ))
    if not asset_class_ok:
        reason_codes.append(rc.PORTFOLIO_ASSET_CLASS_EXPOSURE)

    conflict_ok = resolved_config.allow_long_short_conflict or not conflicts
    trace.append(CalculationTraceStep(
        "LONG_SHORT_CONFLICT", conflict_ok,
        detail=None if conflict_ok else f"{len(conflicts)} opposing-direction position(s) in the same symbol/correlation group",
        observed=len(conflicts),
    ))
    if not conflict_ok:
        reason_codes.append(rc.PORTFOLIO_LONG_SHORT_CONFLICT)

    heat_ok = snapshot.portfolio_heat_pct <= resolved_config.max_portfolio_heat_pct
    trace.append(CalculationTraceStep(
        "PORTFOLIO_HEAT", heat_ok, observed=snapshot.portfolio_heat_pct,
        limit=resolved_config.max_portfolio_heat_pct,
    ))
    if not heat_ok:
        reason_codes.append(rc.PORTFOLIO_HEAT)

    trade_count_ok = daily_state.trades_opened_today < resolved_config.max_trades_per_day
    trace.append(CalculationTraceStep(
        "DAILY_TRADE_COUNT", trade_count_ok, observed=daily_state.trades_opened_today,
        limit=resolved_config.max_trades_per_day,
    ))
    if not trade_count_ok:
        reason_codes.append(rc.PORTFOLIO_DAILY_TRADE_COUNT)

    daily_heat = daily_state.daily_heat_used_pct + request.approved_risk_pct
    daily_heat_ok = daily_heat <= resolved_config.max_daily_heat_pct
    trace.append(CalculationTraceStep(
        "DAILY_HEAT", daily_heat_ok, observed=daily_heat, limit=resolved_config.max_daily_heat_pct,
    ))
    if not daily_heat_ok:
        reason_codes.append(rc.PORTFOLIO_DAILY_HEAT)

    if reason_codes:
        return PortfolioDecision(
            approved=False, reason_codes=tuple(reason_codes), exposure_snapshot=snapshot,
            warnings=(), calculation_trace=tuple(trace),
        )

    return PortfolioDecision(
        approved=True, reason_codes=(), exposure_snapshot=snapshot, warnings=(), calculation_trace=tuple(trace),
    )
