"""Shadow Evidence data contracts -- Phase 6.10 Implementation Checkpoints 1A + 1B + 1C + 2
(``PHASE_6_10_SHADOW_EVIDENCE_ARCHITECTURE_DESIGN.md`` §9, revised after its own adversarial review,
§17). Frozen data shapes; no Strategy Health classification logic anywhere in this module.
``ShadowRejectionRecord`` was added in Checkpoint 1B (the read-only pipeline tap that produces DENY
events); Checkpoint 1C (:mod:`ai_trader.shadow_evidence.engine`) populates ``ShadowPositionRecord``/
``ShadowTradeLegRecord`` and sets ``ShadowOpportunityRecord.resulting_position_id`` for the first time.
Checkpoint 2 adds ``ShadowStrategySummary`` -- generic, per-strategy STATISTICS (win rate, expectancy,
drawdown, etc., reusing :mod:`ai_trader.strategy_health.metrics`'s own frozen, unmodified computation),
explicitly NOT Health SCORING or CLASSIFICATION (``strategy_health.scoring``/``classifier``/
``evaluator`` and ``HealthState``/``WindowScore`` are never imported or produced by this package) --
the CEO's own explicit "no Health/Edge Health" instruction (Checkpoint 2, 2026-07-18) draws this line
precisely: statistics is one lifecycle stage earlier than health (`PHASE_6_10_EDGE_PORTFOLIO_DIRECTION.md`
§5's own 7-stage table), and only that earlier stage is in scope here.

Reuses existing repository types wherever a genuine match exists, per the adversarial review's own
data-contract finding (Design §17.1, Q8): ``Direction``/``SignalState`` from
:mod:`ai_trader.signal_engine.types`, ``Recommendation`` from :mod:`ai_trader.scoring_engine.types`,
``TradeRecord`` from :mod:`ai_trader.simulation.portfolio_simulator` (embedded, not duplicated), and
``WindowMetrics`` from :mod:`ai_trader.strategy_health.types` (embedded, not duplicated, Checkpoint 2).
"""

from __future__ import annotations

from dataclasses import dataclass

from ai_trader.scoring_engine.types import Recommendation
from ai_trader.signal_engine.types import Direction, SignalState
from ai_trader.simulation.portfolio_simulator import TradeRecord
from ai_trader.strategy_health.types import WindowMetrics


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
    resulting_position_id: str | None  # set iff the ALLOW's virtual entry order actually filled (1C)

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
        # An ALLOW decision does NOT require resulting_position_id to be set: Checkpoint 1C submits
        # every ALLOW's virtual entry order, but the order can still genuinely fail to fill (e.g. a
        # real INSUFFICIENT_MARGIN/QTY_OUT_OF_BOUNDS rejection from ExecutionSimulator, empirically
        # rare but not impossible) -- an honest ALLOW-with-no-position, never fabricated. The only
        # enforced direction is the one above: a DENY must NEVER carry a position id.


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
    dedicated, per-strategy shadow ``RiskManager`` denies an opportunity. Checkpoint 1B's own shadow
    risk evaluation always used a structurally empty per-strategy ``PortfolioState`` (no virtual
    position ever existed), so ``LIMIT_MAX_PER_SYMBOL``/``LIMIT_MAX_POSITIONS``/cooldown denials were
    impossible there by construction. Checkpoint 1C changes this deliberately: shadow risk evaluation
    now projects THIS strategy's own real, evolving shadow ``PortfolioState`` (Design §17.1 finding
    H1's own correction), so ``denied_reason_code`` CAN legitimately be ``LIMIT_MAX_PER_SYMBOL`` (a
    same-strategy re-entry attempt while a shadow position is already open) or a cooldown-after-loss
    denial -- exactly mirroring the isolated-slot precedent (Design §8), never a shared-slot denial
    against the REAL competitive portfolio, which this record never sees or influences.

    Checkpoint 3 adds one more possible ``denied_reason_code``: ``SHADOW_ENTRY_ALREADY_PENDING`` -- a
    shadow-internal, never-a-genuine-RiskManager decision, produced when a strategy's own entry order
    is a LIMIT-priced bracket still awaiting a fill and a NEW ALLOW arrives for the same symbol before
    it resolves (``RiskManager.evaluate()`` only sees open positions, never pending orders, so it would
    otherwise happily ALLOW a second, structurally incompatible entry -- engine.py's own module
    docstring explains why). Found empirically at 43-strategy validation scale, not visible at N<=4."""

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


@dataclass(frozen=True, slots=True)
class ShadowStrategySummary:
    """One strategy's aggregated shadow STATISTICS over one rolling window (Checkpoint 2, Design §9's
    own revised definition, adversarial-review finding Q8). ``window_metrics`` is a genuine
    ``strategy_health.types.WindowMetrics``, computed by that module's own frozen, unmodified
    ``compute_window_metrics()`` over this strategy's shadow-sourced ``ClosedTrade`` stream (each
    ``ShadowTradeLegRecord.leg`` adapted via ``strategy_health.types.from_trade_record``, unmodified)
    -- NOT reinvented scoring math. This is deliberately a thin wrapper, not a parallel metrics schema:
    every actual number in ``window_metrics`` comes from code this package does not own or modify.

    ``source`` is the ONE label distinguishing this from a competitive-sourced ``WindowMetrics`` --
    always ``"shadow"`` here, never silently merged with a competitive stream by any downstream
    consumer. This type carries NO classification (no ``HealthState``, no percentile/PCA score) --
    that is Strategy Health's own, separate, still-unselected integration policy (Design §11),
    untouched by this type or by anything in :mod:`ai_trader.shadow_evidence`."""

    strategy_id: str
    source: str
    window_metrics: WindowMetrics
    n_opportunities: int
    n_shadow_denied_by_reason: dict[str, int]

    def __post_init__(self) -> None:
        if self.source != "shadow":
            raise ValueError(f"ShadowStrategySummary.source must be 'shadow', got {self.source!r}")
        if self.n_opportunities < 0:
            raise ValueError("ShadowStrategySummary.n_opportunities must be >= 0")
