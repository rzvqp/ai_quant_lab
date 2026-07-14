"""Pre-Trade Filters (``RISK_MANAGER_ARCHITECTURE.md`` §4/§5 stage 3, ``RISK_POLICY.md`` §5/§6):
per-opportunity market-condition gates read from :class:`~ai_trader.risk_manager.types.RiskContext`.
Every filter is a pure, deterministic comparison against fixed ``RiskConfig`` thresholds. A symbol
with no configured threshold (missing ``reference_spread``/``liquidity_floor`` entry) or no supplied
:class:`~ai_trader.risk_manager.types.SymbolRiskSnapshot` at all is treated as UNVERIFIABLE and
denied -- the fail-safe default is "cannot confirm safe," never "assume safe."
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ai_trader.market_scanner.types import DataQualityLevel
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.types import DeniedReason, RiskContext, SymbolRiskSnapshot


@dataclass(frozen=True, slots=True)
class FilterResult:
    passed: bool
    reason: DeniedReason | None = None


def check_data_quality(symbol: str, context: RiskContext, config: RiskConfig) -> FilterResult:
    snapshot = context.for_symbol(symbol)
    dq = snapshot.data_quality
    if dq in (DataQualityLevel.STALE, DataQualityLevel.INSUFFICIENT) or context.data_quality in (
        DataQualityLevel.STALE, DataQualityLevel.INSUFFICIENT,
    ):
        return FilterResult(False, DeniedReason(code="DATA_DEGRADED", observed=dq.value))
    return FilterResult(True)


def check_volatility(symbol: str, snapshot: SymbolRiskSnapshot, config: RiskConfig) -> FilterResult:
    """``RISK_POLICY.md`` §5: "deny if ATR/price is outside [0.25x, 4x] its rolling median" -- read
    as ``current_atr / atr_rolling_median`` outside ``[volatility_ratio_min, volatility_ratio_max]``.
    Missing/non-positive ATR data cannot be verified -> denied."""
    lim = config.filters
    if snapshot.atr is None or snapshot.atr_rolling_median is None or snapshot.atr_rolling_median <= 0:
        return FilterResult(False, DeniedReason(code="FILTER_VOLATILITY", detail="atr data unavailable"))
    ratio = snapshot.atr / snapshot.atr_rolling_median
    if ratio < lim.volatility_ratio_min or ratio > lim.volatility_ratio_max:
        return FilterResult(False, DeniedReason(
            code="FILTER_VOLATILITY", observed=ratio, limit=f"[{lim.volatility_ratio_min},{lim.volatility_ratio_max}]",
        ))
    return FilterResult(True)


def check_spread(symbol: str, snapshot: SymbolRiskSnapshot, config: RiskConfig) -> FilterResult:
    lim = config.filters
    reference = lim.reference_spread.get(symbol)
    if snapshot.current_spread is None or reference is None or reference <= 0:
        return FilterResult(False, DeniedReason(code="FILTER_SPREAD", detail="no spread threshold configured"))
    max_allowed = reference * lim.spread_multiplier_max
    if snapshot.current_spread > max_allowed:
        return FilterResult(False, DeniedReason(code="FILTER_SPREAD", observed=snapshot.current_spread, limit=max_allowed))
    return FilterResult(True)


def check_liquidity(symbol: str, snapshot: SymbolRiskSnapshot, config: RiskConfig) -> FilterResult:
    lim = config.filters
    floor = lim.liquidity_floor.get(symbol)
    if snapshot.liquidity_proxy is None or floor is None:
        return FilterResult(False, DeniedReason(code="FILTER_LIQUIDITY", detail="no liquidity threshold configured"))
    if snapshot.liquidity_proxy < floor:
        return FilterResult(False, DeniedReason(code="FILTER_LIQUIDITY", observed=snapshot.liquidity_proxy, limit=floor))
    return FilterResult(True)


def check_news(symbol: str, snapshot: SymbolRiskSnapshot, config: RiskConfig) -> FilterResult:
    minutes = snapshot.minutes_to_high_impact_event
    blackout = config.portfolio_limits.event_blackout_minutes
    if minutes is not None and minutes <= blackout:
        return FilterResult(False, DeniedReason(code="FILTER_NEWS", observed=minutes, limit=blackout))
    return FilterResult(True)


def check_weekend(symbol: str, snapshot: SymbolRiskSnapshot, config: RiskConfig) -> FilterResult:
    if snapshot.is_past_friday_cutoff:
        return FilterResult(False, DeniedReason(code="RULE_WEEKEND"))
    return FilterResult(True)


def check_gap(symbol: str, snapshot: SymbolRiskSnapshot, config: RiskConfig) -> FilterResult:
    if snapshot.is_weekend_gap:
        bars = snapshot.bars_since_gap
        if bars is None or bars < config.filters.gap_bars_threshold:
            return FilterResult(False, DeniedReason(
                code="RULE_GAP", observed=bars, limit=config.filters.gap_bars_threshold,
            ))
    return FilterResult(True)


SymbolCheckFn = Callable[[str, SymbolRiskSnapshot, RiskConfig], FilterResult]

#: The fixed evaluation order, matching ``RISK_POLICY.md`` §5's table: Volatility, Spread, Liquidity,
#: News, then Data-quality, then the weekend/gap rules -- NOT data-quality first. Since the pipeline
#: stops at the first failure, this order determines which single reason code surfaces when multiple
#: filters would fail simultaneously, so it must match the policy document's own table order exactly.
_FILTER_ORDER: tuple[str, ...] = (
    "FILTER_VOLATILITY", "FILTER_SPREAD", "FILTER_LIQUIDITY", "FILTER_NEWS",
    "DATA_DEGRADED", "RULE_WEEKEND", "RULE_GAP",
)

#: Every filter except ``DATA_DEGRADED``, which is dispatched separately in :func:`run_pre_trade_filters`
#: since it alone needs the full :class:`~ai_trader.risk_manager.types.RiskContext` (for the batch-level
#: ``context.data_quality``), not just the per-symbol :class:`SymbolRiskSnapshot`.
_SYMBOL_FILTERS: dict[str, SymbolCheckFn] = {
    "FILTER_VOLATILITY": check_volatility,
    "FILTER_SPREAD": check_spread,
    "FILTER_LIQUIDITY": check_liquidity,
    "FILTER_NEWS": check_news,
    "RULE_WEEKEND": check_weekend,
    "RULE_GAP": check_gap,
}


def run_pre_trade_filters(
    symbol: str, context: RiskContext, config: RiskConfig,
) -> list[tuple[str, FilterResult]]:
    """Run every filter in the fixed order, returning ``(rule_name, FilterResult)`` for EACH
    (never short-circuits) -- the caller decides how much of the audit trail to keep; the pipeline
    stops at the first failure but the whole ordered list is available for a full audit if needed."""
    snapshot = context.for_symbol(symbol)
    results: list[tuple[str, FilterResult]] = []
    for rule_name in _FILTER_ORDER:
        if rule_name == "DATA_DEGRADED":
            results.append((rule_name, check_data_quality(symbol, context, config)))
        else:
            results.append((rule_name, _SYMBOL_FILTERS[rule_name](symbol, snapshot, config)))
    return results
