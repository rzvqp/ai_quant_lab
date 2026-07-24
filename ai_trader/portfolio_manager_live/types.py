"""Types owned by Portfolio Manager (Phase 4). Reuses `risk_manager.types.PortfolioState`/`OpenPosition`
(the book) and `risk_manager_live.types.CalculationTraceStep` (the same audit-trace shape Phase 2 already
established) unmodified -- only the genuinely missing pieces live here."""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_trader.signal_engine.types import Direction


@dataclass(frozen=True, slots=True)
class PortfolioAuthorizationRequest:
    """Built by a caller (the future Execution Orchestrator, Phase 9, or a test/manual caller this
    phase) from an already-APPROVED `risk_manager_live.LiveRiskDecision` plus its originating
    `TradeProposal` -- mirrors `order_manager.ApprovedTradeIntent`'s own bridge pattern. `session` has no
    existing detector anywhere in the repo (disclosed, `PORTFOLIO_MANAGER_PHASE4_DESIGN.md` §3) -- the
    caller supplies it directly."""

    proposal_id: str
    correlation_id: str
    strategy_id: str
    symbol: str
    direction: Direction
    session: str
    monetary_risk: float
    approved_risk_pct: float  # LiveRiskDecision.approved_risk -- the risk_pct this trade would add
    as_of: int

    def __post_init__(self) -> None:
        if not self.proposal_id:
            raise ValueError("PortfolioAuthorizationRequest.proposal_id must be non-empty")
        if not self.correlation_id:
            raise ValueError("PortfolioAuthorizationRequest.correlation_id must be non-empty")
        if not self.strategy_id:
            raise ValueError("PortfolioAuthorizationRequest.strategy_id must be non-empty")
        if not self.symbol:
            raise ValueError("PortfolioAuthorizationRequest.symbol must be non-empty")
        if not self.session:
            raise ValueError("PortfolioAuthorizationRequest.session must be non-empty")
        if not isinstance(self.direction, Direction):
            raise TypeError(f"PortfolioAuthorizationRequest.direction must be a Direction, got {self.direction!r}")
        if self.approved_risk_pct <= 0:
            raise ValueError(f"PortfolioAuthorizationRequest.approved_risk_pct must be > 0, got {self.approved_risk_pct!r}")


@dataclass(frozen=True, slots=True)
class PortfolioDailyState:
    """Caller-owned, caller-persisted -- Portfolio Manager is a pure function and holds no state itself
    (same discipline as every prior module: no wall-clock, no hidden state). A future Execution
    Orchestrator (Phase 9) owns tracking and resetting this daily."""

    as_of: int
    trades_opened_today: int = 0
    daily_heat_used_pct: float = 0.0
    session_heat_used_pct: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.trades_opened_today < 0:
            raise ValueError("PortfolioDailyState.trades_opened_today must be >= 0")
        if self.daily_heat_used_pct < 0:
            raise ValueError("PortfolioDailyState.daily_heat_used_pct must be >= 0")


@dataclass(frozen=True, slots=True)
class ExposureSnapshot:
    """The aggregated view Portfolio Manager's decision was based on -- always attached to the
    decision for audit, whether ALLOW or DENY."""

    total_exposure_pct: float
    per_symbol_exposure_pct: dict[str, float]
    per_direction_exposure_pct: dict[str, float]
    per_strategy_exposure_pct: dict[str, float]
    per_asset_class_exposure_pct: dict[str, float]
    pending_session_heat_pct: float
    portfolio_heat_pct: float
    reserved_capital_pct: float
    available_capital_pct: float


@dataclass(frozen=True, slots=True)
class CalculationTraceStep:
    """Same shape as `risk_manager_live.types.CalculationTraceStep` -- redeclared here (not imported)
    only to keep this package's own static import-independence test simple; field-for-field identical,
    not a divergent design."""

    stage: str
    passed: bool
    detail: str | None = None
    observed: float | str | bool | None = None
    limit: float | str | bool | None = None


@dataclass(frozen=True, slots=True)
class PortfolioDecision:
    approved: bool
    reason_codes: tuple[str, ...]
    exposure_snapshot: ExposureSnapshot | None
    warnings: tuple[str, ...]
    calculation_trace: tuple[CalculationTraceStep, ...]

    def __post_init__(self) -> None:
        if self.approved and not self.calculation_trace:
            raise ValueError("PortfolioDecision: an approved decision must carry a non-empty calculation_trace")
        if not self.approved and not self.reason_codes:
            raise ValueError("PortfolioDecision: a denied decision must carry at least one reason code")


@dataclass(frozen=True, slots=True)
class PortfolioManagerConfig:
    max_total_exposure_pct: float = 0.30
    max_direction_exposure_pct: float = 0.20
    max_strategy_exposure_pct: float = 0.15
    max_session_exposure_pct: float = 0.15
    max_asset_class_exposure_pct: float = 0.25
    max_portfolio_heat_pct: float = 0.30
    reserved_capital_pct: float = 0.10
    max_trades_per_day: int = 20
    max_daily_heat_pct: float = 0.20
    allow_long_short_conflict: bool = False
    asset_class_map: dict[str, str] = field(default_factory=dict)

    def asset_class_for(self, symbol: str) -> str:
        return self.asset_class_map.get(symbol, "UNCLASSIFIED")

    def __post_init__(self) -> None:
        if not (0.0 <= self.reserved_capital_pct < 1.0):
            raise ValueError("PortfolioManagerConfig.reserved_capital_pct must be in [0, 1)")
        if self.max_trades_per_day < 0:
            raise ValueError("PortfolioManagerConfig.max_trades_per_day must be >= 0")
