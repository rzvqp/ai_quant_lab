"""Types owned by Order Manager (Phase 3). Everything reusable from `ai_trader/execution_engine/`
(`OrderRequest`, `OrderState`, `BrokerCapabilities`, ...) is imported and used unmodified elsewhere in
this package -- nothing here duplicates it. Only the genuinely missing pieces live here: the bridge from
a live Risk Manager decision to an order-ready intent, and the dry-run-aware result wrapper.
"""

from __future__ import annotations

from dataclasses import dataclass

from ai_trader.execution_engine.types import OrderState
from ai_trader.signal_engine.types import Direction


@dataclass(frozen=True, slots=True)
class ApprovedTradeIntent:
    """Built by a caller (the future Execution Orchestrator, Phase 9, or a test/manual caller this
    phase) from an already-APPROVED `risk_manager_live.LiveRiskDecision` plus the originating
    `TradeProposal` and `InstrumentSpecification` -- Order Manager itself never re-decides risk, it only
    turns an approval into a broker-ready order. Scope: OPEN intents only (a `TradeProposal` always
    carries a concrete `entry`/`stop`) -- CLOSE/REDUCE/flatten flows already exist, unmodified, via
    `execution_engine.builder.build_flatten_order`; Order Manager does not duplicate that path.

    `magic_number`/`comment`/`correlation_id` have no home on the frozen, reused `OrderRequest` -- they
    stay here and in the audit journal. Phase 10's real MT5 payload construction (a raw dict, not an
    `OrderRequest`) is the correct, later place to map `magic_number`/`comment` onto MT5's own
    `order_send()` parameters.
    """

    proposal_id: str
    correlation_id: str
    strategy_id: str
    symbol: str
    direction: Direction
    entry: float
    stop: float
    target: float | None
    as_of: int
    volume: float  # lots, already risk-approved AND already volume-step-rounded (risk_manager_live Phase 2)
    monetary_risk: float
    magic_number: int
    comment: str

    def __post_init__(self) -> None:
        if not self.proposal_id:
            raise ValueError("ApprovedTradeIntent.proposal_id must be non-empty")
        if not self.correlation_id:
            raise ValueError("ApprovedTradeIntent.correlation_id must be non-empty")
        if not self.strategy_id:
            raise ValueError("ApprovedTradeIntent.strategy_id must be non-empty")
        if not self.symbol:
            raise ValueError("ApprovedTradeIntent.symbol must be non-empty")
        if not isinstance(self.direction, Direction):
            raise TypeError(f"ApprovedTradeIntent.direction must be a Direction, got {self.direction!r}")
        if self.volume <= 0:
            raise ValueError(f"ApprovedTradeIntent.volume must be > 0, got {self.volume!r}")
        if not self.comment:
            raise ValueError("ApprovedTradeIntent.comment must be non-empty")


@dataclass(frozen=True, slots=True)
class OrderExecutionResult:
    """Order Manager's own outcome wrapper -- distinct from `execution_engine.types.ExecutionResult`
    because it must carry `dry_run` and a link back into the audit journal, neither of which the reused
    type has any concept of.

    `dry_run` reflects which adapter actually ran the order, not a phase-hardcoded constant (Phase 10
    fix, CEO-authorized 2026-07-25): `order_manager.dry_run_adapter.DryRunBrokerAdapter` always yields
    `dry_run=True` (unchanged -- every Phase 3 caller/test continues to see exactly that); a real
    (even demo) adapter yields `dry_run=False`. `process_approved_intent` itself never chooses which
    adapter runs -- the caller supplies it (`BrokerAdapter`, the general protocol) -- so this type
    cannot silently mislabel a real send as a dry run or vice versa; the caller's own adapter choice is
    the single source of truth, carried straight through."""

    order_request_id: str
    client_order_id: str
    state: OrderState
    dry_run: bool
    filled_qty: float = 0.0
    avg_price: float | None = None
    reasons: tuple[str, ...] = ()
    audit_event_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class OrderManagerConfig:
    """Order Manager's own configuration -- version/prefix strings reused verbatim from
    `execution_engine.config` where a concept already exists there (never re-pinned to a different
    value); new fields only for what Order Manager itself owns."""

    client_order_id_prefix: str = "OM-CID"
    order_request_id_prefix: str = "OM-REQ"
    risk_lineage_ref: str = "1.0.0"
    #: `ORDER_SCHEMA.json` requires `refs.risk_schema_version`/`risk_policy_version` to match
    #: `^\d+\.\d+\.\d+$` -- a semver value, not a free-form lineage string. This order's approving
    #: decision came from the LIVE Risk Manager (Phase 2), not the batch RISK_SCHEMA.json pipeline
    #: `execution_engine.builder.build_order` was designed for; that lineage is recorded in the audit
    #: journal (`ORDER_BUILT`/`INTENT_RECEIVED` events), not squeezed into this schema-constrained field.
