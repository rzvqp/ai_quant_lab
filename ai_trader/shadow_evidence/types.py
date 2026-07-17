"""Shadow Evidence data contracts -- Phase 6.10 Implementation Checkpoints 1A + 1B
(``PHASE_6_10_SHADOW_EVIDENCE_ARCHITECTURE_DESIGN.md`` §9, revised after its own adversarial review,
§17). Structural only: frozen data shapes with no execution behavior and no Strategy Health
classification logic. ``ShadowRejectionRecord`` was added in Checkpoint 1B (the read-only pipeline tap
that actually produces DENY events); ``ShadowStrategySummary`` remains deferred -- it is
Strategy-Health-adjacent, out of scope per the CEO's own explicit "no Health classification logic"
instruction.

Reuses existing repository types wherever a genuine match exists, per the adversarial review's own
data-contract finding (Design §17.1, Q8): ``Direction``/``SignalState`` from
:mod:`ai_trader.signal_engine.types`, ``Recommendation`` from :mod:`ai_trader.scoring_engine.types`,
and ``TradeRecord`` from :mod:`ai_trader.simulation.portfolio_simulator` (embedded, not duplicated).
"""

from __future__ import annotations

from dataclasses import dataclass

from ai_trader.scoring_engine.types import Recommendation
from ai_trader.signal_engine.types import Direction, SignalState
from ai_trader.simulation.portfolio_simulator import TradeRecord


@dataclass(frozen=True, slots=True)
class ShadowOpportunityRecord:
    """One bar's already-computed signal + score, tagged with the shadow-only risk decision
    (Design §9). Not a duplicate of ``StrategySignal``/``OpportunityScore`` -- their read-only union at
    one point in time, persisted because the live batch objects are not themselves retained bar to
    bar. ``resulting_position_id`` is set exactly once, at virtual-entry time, and must never be
    re-set on a later partial exit (Design §5's identity invariant)."""

    opportunity_id: str
    strategy_id: str
    symbol: str
    as_of: int
    direction: Direction
    signal_state: SignalState
    score_recommendation: Recommendation
    shadow_risk_decision: str  # "ALLOW" | "DENY" -- the one field with no upstream equivalent
    shadow_denied_reason: str | None
    resulting_position_id: str | None  # set only once virtual execution exists (not this checkpoint)

    def __post_init__(self) -> None:
        if self.shadow_risk_decision not in ("ALLOW", "DENY"):
            raise ValueError(
                f"ShadowOpportunityRecord.shadow_risk_decision must be 'ALLOW' or 'DENY', "
                f"got {self.shadow_risk_decision!r}"
            )
        if self.shadow_risk_decision == "DENY" and self.resulting_position_id is not None:
            raise ValueError(
                "ShadowOpportunityRecord: a DENY decision must not carry a resulting_position_id"
            )
        # NOTE (relaxed during Checkpoint 1B, corrected from Checkpoint 1A's own first pass): an
        # ALLOW decision does NOT require resulting_position_id to be set. Checkpoint 1B is a
        # read-only pipeline tap with no virtual execution/positions (explicit CEO scope) -- an ALLOW
        # opportunity legitimately has resulting_position_id=None here. Only a later checkpoint that
        # implements virtual execution would populate it. The only enforced direction is the one
        # above: a DENY must NEVER carry a position id, in any checkpoint.


@dataclass(frozen=True, slots=True)
class ShadowPositionRecord:
    """One logical shadow position, spanning one or more ``ShadowTradeLegRecord`` legs (Design §5/§9).
    No existing repository type represents this concept -- confirmed during the adversarial review
    (Design §17.1, Q8) to be genuinely new, not duplicative."""

    position_id: str
    strategy_id: str
    symbol: str
    direction: Direction
    entry_as_of: int
    entry_price: float
    entry_opportunity_id: str
    status: str  # "OPEN" | "CLOSED"
    full_exit_as_of: int | None  # MAX(leg.exit_as_of); None while OPEN
    n_legs: int
    aggregate_net_pnl: float | None  # None while OPEN
    aggregate_holding_bars_full: int | None  # bars from entry_as_of to full_exit_as_of

    def __post_init__(self) -> None:
        if self.status not in ("OPEN", "CLOSED"):
            raise ValueError(f"ShadowPositionRecord.status must be 'OPEN' or 'CLOSED', got {self.status!r}")
        if self.status == "OPEN" and self.full_exit_as_of is not None:
            raise ValueError("ShadowPositionRecord: an OPEN position must not carry full_exit_as_of")
        if self.status == "CLOSED" and self.full_exit_as_of is None:
            raise ValueError("ShadowPositionRecord: a CLOSED position must carry full_exit_as_of")
        if self.n_legs < 0:
            raise ValueError("ShadowPositionRecord.n_legs must be >= 0")
        if self.status == "CLOSED" and self.n_legs < 1:
            raise ValueError("ShadowPositionRecord: a CLOSED position must have n_legs >= 1")


@dataclass(frozen=True, slots=True)
class ShadowRejectionRecord:
    """One shadow DENY event -- created alongside a ``ShadowOpportunityRecord`` whenever the
    dedicated, per-strategy shadow ``RiskManager`` denies an opportunity (Checkpoint 1B). Since the
    shadow risk evaluation always uses a structurally empty per-strategy ``PortfolioState`` (no
    virtual position ever exists in this checkpoint), ``denied_reason_code`` can never be
    ``LIMIT_MAX_PER_SYMBOL``/``LIMIT_MAX_POSITIONS`` against a shadow position -- only a genuine
    market/policy-driven denial (spread/liquidity/volatility filters, etc.) is possible here by
    construction. This is an expected, honest property of a pipeline stage that has not yet modeled
    positions -- not a bug to be masked."""

    rejection_id: str
    strategy_id: str
    symbol: str
    as_of: int
    direction: Direction
    denied_reason_code: str
    denied_detail: str | None


@dataclass(frozen=True, slots=True)
class ShadowTradeLegRecord:
    """One shadow fill/exit leg. Reuses ``TradeRecord`` verbatim (embedded, not duplicated) plus
    exactly the 2 additive fields the Shadow Evidence design requires: ``position_id`` (the FK a
    partial-exit's second leg shares with its first, never inferred post-hoc -- Design §5) and
    ``exit_reason`` (set directly by whichever mechanism closed this leg, never inferred from a
    ``client_order_id`` string, unlike the diagnostic's own necessary workaround)."""

    leg: TradeRecord
    position_id: str
    exit_reason: str
