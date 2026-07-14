"""Configuration objects for the Risk Manager.

Every default value below is transcribed verbatim from ``RISK_POLICY.md`` / ``POSITION_SIZING.md``
(explicitly labeled there as "conservative placeholders for design review, not tuned values" --
``RISK_POLICY.md`` §0). A handful of structural fields (``correlation_groups``, per-symbol
``reference_spread``/``liquidity_floor``, the quality->factor mapping) fill gaps the policy names but
does not fully specify a mechanism for -- each is documented at its point of use.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_trader.scoring_engine.types import Quality

RISK_ENGINE_VERSION = "1.0.0"
RISK_SCHEMA_VERSION = "1.0.0"
RISK_POLICY_VERSION = "1.0.0"

DEFAULT_SUPPORTED_SCORING_SCHEMA_MAJOR = 1
DEFAULT_SUPPORTED_INTERFACE_MAJOR = 1

#: ``POSITION_SIZING.md`` §2: "quality_factor in [0.5, 1.0] mapped from total_score bands (POOR/WEAK
#: -> 0.5 ... STRONG -> 1.0)". The model names the two endpoints only; MODERATE is the documented
#: linear interpolation between them, PREMIUM stays capped at the same ceiling as STRONG (the spec
#: gives no reason a strictly-higher band should exceed the [0.5, 1.0] range it itself fixes).
QUALITY_FACTOR: dict[Quality, float] = {
    Quality.POOR: 0.5,
    Quality.WEAK: 0.5,
    Quality.MODERATE: 0.75,
    Quality.STRONG: 1.0,
    Quality.PREMIUM: 1.0,
}


@dataclass(frozen=True, slots=True)
class PortfolioLimits:
    """``RISK_POLICY.md`` §2."""

    max_positions: int = 5
    max_per_symbol: int = 1
    max_correlated: int = 2
    max_exposure_pct: float = 0.30
    max_leverage: float = 3.0
    max_overnight_exposure_pct: float = 0.15
    event_blackout_minutes: float = 15.0


@dataclass(frozen=True, slots=True)
class LossDrawdownLimits:
    """``RISK_POLICY.md`` §3/§9."""

    max_daily_loss_pct: float = 0.03
    max_weekly_loss_pct: float = 0.06
    max_drawdown_pct: float = 0.12
    drawdown_reset_threshold_pct: float = 0.08


@dataclass(frozen=True, slots=True)
class CooldownLimits:
    """``RISK_POLICY.md`` §4.

    ``per_strategy_cooldown_bars``: ``RISK_POLICY.md`` names ``COOLDOWN_STRATEGY`` as "honor the
    strategy contract's ``execution.cooldown``" -- but the Risk Manager has no access to a strategy's
    contract (forbidden dependency: Strategy Library/Signal Engine, architecture §13), and
    ``OpportunityScore`` does not carry the contract's cooldown either. Resolved the same way as
    ``correlation_groups``: an operator-configured ``strategy_id -> cooldown bars`` mapping, letting
    the rule be enforced without the Risk Manager reaching into forbidden territory. A strategy absent
    from this mapping has no configured cooldown (0 bars) -- the safe default of "no unconfigured
    restriction", not a silent assumption of safety. PER_STRATEGY scope only in v1 (matches Strategy
    Manager's own ``CooldownScope.PER_STRATEGY``); PER_DIRECTION scope is a disclosed, not-yet-
    implemented gap (see the validation report).
    """

    after_loss_bars: int = 4
    consecutive_loss_count: int = 3
    consecutive_loss_cooldown_minutes: float = 60.0
    per_strategy_cooldown_bars: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class PreTradeFilterLimits:
    """``RISK_POLICY.md`` §5. ``reference_spread``/``liquidity_floor`` are per-symbol THRESHOLDS
    (fixed assumptions), distinct from :class:`~ai_trader.risk_manager.types.SymbolRiskSnapshot`'s
    ``current_spread``/``liquidity_proxy`` (live observed facts) -- a symbol absent from either dict
    has no configured threshold and is treated as worst-case (filter denies), never silently passed.
    """

    volatility_ratio_min: float = 0.25
    volatility_ratio_max: float = 4.0
    spread_multiplier_max: float = 3.0
    reference_spread: dict[str, float] = field(default_factory=dict)
    liquidity_floor: dict[str, float] = field(default_factory=dict)
    gap_bars_threshold: int = 3


#: ``RISK_POLICY.md`` §7.
DEFAULT_MIN_TOTAL_SCORE = 25
DEFAULT_ALLOWED_RECOMMENDATIONS: frozenset[str] = frozenset({
    "STRONG_OPPORTUNITY", "MODERATE_OPPORTUNITY", "WEAK_OPPORTUNITY",
})


@dataclass(frozen=True, slots=True)
class ConstraintDefaults:
    """IMPLEMENTATION CHOICE: ``RISK_MANAGER_ARCHITECTURE.md`` names the Constraint Builder's outputs
    ("max hold, expiry, slippage cap, session window") without fixing numeric defaults for any of
    them. Conservative, documented placeholders, matching ``RISK_POLICY.md`` §0's own framing for
    every other v1 default ("conservative placeholders for design review, not tuned values").
    ``valid_for_bars`` is stored on the emitted ``constraints.valid_until`` field as a bar COUNT (an
    integer), not a timestamp -- ``RISK_SCHEMA.json`` allows either ``string`` or ``integer`` for that
    field and does not fix which convention a producer uses; v1 uses a bar count since the Risk
    Manager has no wall-clock in its logic to convert it to an absolute timestamp itself.
    """

    max_hold_bars: int = 200
    max_slippage_pct: float = 0.001
    valid_for_bars: int = 5


@dataclass(frozen=True, slots=True)
class SizingLimits:
    """``POSITION_SIZING.md`` §2/§6."""

    risk_per_trade_pct: float = 0.005
    max_position_notional_pct: float = 0.20
    min_allocation_risk_pct: float = 0.001
    point_value: dict[str, float] = field(default_factory=dict)  # symbol -> currency per price unit; default 1.0


@dataclass(slots=True)
class RiskConfig:
    """Immutable-by-convention configuration for one :class:`~ai_trader.risk_manager.engine.RiskManager`
    instance.

    Attributes:
        correlation_groups: symbol -> correlation-group id (``RISK_POLICY.md`` §2's "groups by
            mechanism class / instrument correlation" -- the Risk Manager has no access to a
            strategy's contract (forbidden dependency, architecture §13), so grouping is instead a
            fixed, operator-configured symbol->group mapping. A symbol absent from this dict is its
            own singleton group (i.e. `LIMIT_MAX_CORRELATED` is a no-op for it unless configured) --
            the safe, conservative default when no grouping has been declared.
    """

    portfolio_limits: PortfolioLimits = field(default_factory=PortfolioLimits)
    loss_drawdown: LossDrawdownLimits = field(default_factory=LossDrawdownLimits)
    cooldowns: CooldownLimits = field(default_factory=CooldownLimits)
    filters: PreTradeFilterLimits = field(default_factory=PreTradeFilterLimits)
    sizing: SizingLimits = field(default_factory=SizingLimits)
    constraints: ConstraintDefaults = field(default_factory=ConstraintDefaults)
    correlation_groups: dict[str, str] = field(default_factory=dict)
    min_total_score: int = DEFAULT_MIN_TOTAL_SCORE
    allowed_recommendations: frozenset[str] = DEFAULT_ALLOWED_RECOMMENDATIONS
    supported_scoring_schema_major: int = DEFAULT_SUPPORTED_SCORING_SCHEMA_MAJOR
    supported_interface_major: int = DEFAULT_SUPPORTED_INTERFACE_MAJOR
    risk_engine_version: str = RISK_ENGINE_VERSION
    risk_schema_version: str = RISK_SCHEMA_VERSION
    risk_policy_version: str = RISK_POLICY_VERSION

    def __post_init__(self) -> None:
        if self.supported_scoring_schema_major < 1:
            raise ValueError("RiskConfig.supported_scoring_schema_major must be >= 1")
        if self.supported_interface_major < 1:
            raise ValueError("RiskConfig.supported_interface_major must be >= 1")

    def point_value_for(self, symbol: str) -> float:
        return self.sizing.point_value.get(symbol, 1.0)

    def correlation_group_for(self, symbol: str) -> str:
        return self.correlation_groups.get(symbol, symbol)

    def quality_factor_for(self, quality: Quality) -> float:
        return QUALITY_FACTOR.get(quality, 0.5)
