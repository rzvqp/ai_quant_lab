"""Configuration for the Execution Engine.

``EXECUTION_ENGINE_ARCHITECTURE.md``/``ORDER_LIFECYCLE.md`` name several mechanisms without fixing
every numeric/policy detail (retry bounds, tick/lot rounding direction, the exact "entry price ≈
current market" threshold for Market-vs-Limit selection). Every such gap is filled here with an
explicit, documented, conservative default and marked IMPLEMENTATION CHOICE -- the same discipline
followed by every prior module's own ``config.py``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_trader.execution_engine.types import TimeInForce

EXECUTION_ENGINE_VERSION = "1.0.0"
ORDER_SCHEMA_VERSION = "1.0.0"
BROKER_ADAPTER_CONTRACT_VERSION = "1.0.0"
DEFAULT_SUPPORTED_RISK_SCHEMA_MAJOR = 1


@dataclass(frozen=True, slots=True)
class OrderTypeMappingPolicy:
    """``ORDER_LIFECYCLE.md`` §6's default ``RiskDecision`` -> order-type mapping.

    IMPLEMENTATION CHOICE: the policy prose describes selecting MARKET when the decision's entry
    price is "≈ current market", but the Execution Engine has no live quote feed input in v1 (Market
    Scanner access is explicitly forbidden, architecture §13) -- there is no reference price to compare
    against. The safe, fully deterministic default is therefore a **marketable LIMIT at the decision's
    own entry price** for every opening order with a specified entry (never worse than the approved
    entry, matches "or a marketable Limit" from the same sentence), falling back to MARKET only when
    the decision carries no entry price at all (nothing to limit against). Protective ``stop``/
    ``target`` attach as a BRACKET's child legs whenever either is present, per the architecture's
    "attached as a Bracket ... so the position is protected on fill." Reduce-only (closing/flatten)
    orders default to a plain, non-bracketed order at the given TIF -- a closing order does not need
    its own protective bracket.
    """

    open_time_in_force: TimeInForce = TimeInForce.GTC
    close_time_in_force: TimeInForce = TimeInForce.IOC


@dataclass(frozen=True, slots=True)
class RoundingPolicy:
    """``EXECUTION_ENGINE_ARCHITECTURE.md`` §8: prices/quantities are rounded to
    ``tick_size``/``lot_step`` "per policy" (the exact rounding rule is left to the implementer).
    IMPLEMENTATION CHOICE: round-half-up, for consistency with the Scoring Engine's own documented
    half-up rounding choice elsewhere in this codebase (not safety-critical here -- tick/lot
    increments are small and the direction of rounding does not change which side of the market the
    order rests on)."""

    round_prices: bool = True
    round_quantity: bool = True


@dataclass(frozen=True, slots=True)
class QuantityLimitPolicy:
    """``EXECUTION_ENGINE_ARCHITECTURE.md`` §8: "minimum quantity: qty >= min_qty (else REJECTED)";
    "maximum quantity: qty <= max_qty (clamp per policy or reject)". IMPLEMENTATION CHOICE: clamp DOWN
    to ``max_qty`` (never up -- clamping down can never exceed what the ``RiskDecision`` authorized,
    satisfying the hard boundary "never resize a position beyond the approved RiskDecision"; only
    reject if the clamped quantity would then fall below ``min_qty``, mirroring the Risk Manager's own
    notional-cap-then-below-min interaction precedent)."""

    clamp_to_max_qty: bool = True


@dataclass(frozen=True, slots=True)
class ExecConfig:
    """Configuration for one :class:`~ai_trader.execution_engine.engine.ExecutionEngine` instance."""

    order_mapping: OrderTypeMappingPolicy = field(default_factory=OrderTypeMappingPolicy)
    rounding: RoundingPolicy = field(default_factory=RoundingPolicy)
    quantity_limits: QuantityLimitPolicy = field(default_factory=QuantityLimitPolicy)
    client_order_id_prefix: str = "CID"
    order_request_id_prefix: str = "REQ"
    #: IMPLEMENTATION CHOICE: ``emergency_flatten``'s synthesized closing orders have no source
    #: ``RiskDecision`` to read ``max_slippage`` from (a flatten is a direct command, not a per-
    #: opportunity risk decision, ``EXECUTION_API.md`` §3) -- a conservative, documented placeholder,
    #: matching every prior module's own "conservative placeholder for design review" precedent for
    #: undocumented numeric defaults.
    flatten_max_slippage: float = 0.01
    supported_risk_schema_major: int = DEFAULT_SUPPORTED_RISK_SCHEMA_MAJOR
    execution_engine_version: str = EXECUTION_ENGINE_VERSION
    order_schema_version: str = ORDER_SCHEMA_VERSION
    broker_adapter_contract_version: str = BROKER_ADAPTER_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if self.supported_risk_schema_major < 1:
            raise ValueError("ExecConfig.supported_risk_schema_major must be >= 1")
