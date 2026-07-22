"""Decision-time / resolution-time capture orchestration -- Learning/Research Feedback Phase E.

**UNWIRED.** Nothing in this module is called from `harness.py` or anywhere else in production code.
Every public function is defense-in-depth wrapped: it NEVER lets an exception escape, and NEVER
fabricates a record when its own required inputs are missing or inconsistent -- on any failure it logs
and returns `None` (or `False`), exactly mirroring Shadow Evidence's own established convention
(Implementation Plan §11).

**Correlation model (CEO decision, correcting the Implementation Plan's own original `(strategy_id,
symbol, entry_as_of)` key)**: `entry_as_of` is not known at decision time -- it is the FILL bar's own
`as_of`, generally a LATER bar than the decision bar (confirmed: market orders never fill on their own
signal bar; limit/stop orders can stay WORKING for many bars). Correlation is keyed by `client_order_id`
instead -- deterministically built at decision time (`f"{prefix}-{decision_id}"`,
`execution_engine/builder.py`) and carried forward unchanged onto `TradeRecord.client_order_id`/
`ShadowTradeLegRecord.leg.client_order_id` at resolution time.

**Run isolation**: `client_order_id` alone is NOT globally unique across separate runs --
`RiskDecision.decision_id` (`f"{strategy_id}|{symbol}|{as_of}"`, `risk_manager/assembler.py`) carries no
run-specific component, so two separate runs over the same historical window can produce the identical
`client_order_id` string. Every correlation-map operation is therefore keyed by the explicit compound
`(run_id, client_order_id)`, never `client_order_id` alone; a `CorrelationMap` instance is bound to
exactly one `run_id` at construction and rejects any operation for a different one.

**Bracket orders** (`Constraints.stop`/`Constraints.target` present) build up to THREE distinct
`client_order_id`s from one decision (`execution_simulator.py`: parent `f"{prefix}-{decision_id}"`, plus
`f"{parent}-TP"`/`f"{parent}-SL"` children, mutually exclusive via OCO cancellation) -- a
`PendingCapture` may be registered under multiple alias ids for exactly this case; resolving via ANY
alias retires ALL of them together, so a cancelled OCO sibling can never later be mistaken for a fresh,
unrelated order.

**Disclosed, accepted limitation**: partial fills of one order share the SAME `client_order_id` and can
produce MULTIPLE `TradeRecord`s. Only the FIRST resolution attempt for a given `client_order_id` succeeds
-- every subsequent one (a later partial against the same id) is treated as a duplicate resolution and
dropped, per the CEO's own explicit "duplicate terminal resolution" fail-closed requirement. This means a
multi-partial close is captured as ONE Outcome (from the first partial only), not one per partial -- a
known, disclosed scope limit of this phase, not a silent gap.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from ai_trader.context_memory.contracts import (
    EdgeEvidenceId,
    Observation,
    ObservationId,
    OperationalMetadataId,
)
from ai_trader.context_memory.enums import OutcomeKind
from ai_trader.context_memory.repository import ContextMemoryRepository
from ai_trader.learning_feedback.adapters import (
    build_operational_metadata,
    build_portfolio_outcome,
    build_strategy_outcome,
)
from ai_trader.risk_manager.types import RiskDecision
from ai_trader.shadow_evidence.types import ShadowPositionRecord
from ai_trader.simulation.portfolio_simulator import TradeRecord

_LOGGER = logging.getLogger(__name__)


class CorrelationError(Exception):
    """Base class for correlation-map invariant violations -- always caught at the public function
    boundary in this module, never allowed to escape a capture call."""


class CorrelationRunMismatchError(CorrelationError):
    """Raised when an operation's own `run_id` does not match the `CorrelationMap`'s bound `run_id` --
    separate runs must never share pending correlation state (CEO decision)."""


class DuplicateDecisionCaptureError(CorrelationError):
    """Raised when `register_decision` is given a `client_order_id` that is already pending OR already
    resolved for this run -- no silent overwrite of conflicting state (CEO decision)."""


@dataclass(frozen=True)
class PendingCapture:
    """Everything needed, at resolution time, to build the correct Outcome and locate the correct
    Observation -- recorded once, at decision time, per CEO's own required lifecycle fields."""

    run_id: str
    client_order_ids: tuple[str, ...]  # 1 (plain order) or 3 (bracket: parent, parent-TP, parent-SL)
    strategy_id: str
    symbol: str
    decision_id: str
    decision_as_of: int
    outcome_kind: OutcomeKind
    observation_id: ObservationId
    cost_model_ref: str

    def __post_init__(self) -> None:
        if not self.client_order_ids:
            raise ValueError("PendingCapture.client_order_ids must be non-empty")


class CorrelationMap:
    """Run-scoped, in-memory-only correlation state -- never persisted, matching Context Memory's own
    schema having no knowledge of this map's existence (Implementation Plan §5). Bound to exactly one
    `run_id` at construction; every operation validates its own `run_id` argument against it."""

    def __init__(self, run_id: str) -> None:
        self._run_id = run_id
        self._pending: dict[str, PendingCapture] = {}
        self._resolved_client_order_ids: set[str] = set()

    @property
    def run_id(self) -> str:
        return self._run_id

    def register_decision(self, entry: PendingCapture) -> None:
        """Raises :class:`CorrelationRunMismatchError`/:class:`DuplicateDecisionCaptureError` on any
        invariant violation -- callers in this module always catch these at the public function
        boundary; a direct caller (e.g. a test) sees them raised."""
        if entry.run_id != self._run_id:
            raise CorrelationRunMismatchError(
                f"CorrelationMap bound to run_id={self._run_id!r} cannot register an entry for "
                f"run_id={entry.run_id!r}"
            )
        for coid in entry.client_order_ids:
            if coid in self._pending or coid in self._resolved_client_order_ids:
                raise DuplicateDecisionCaptureError(
                    f"client_order_id={coid!r} is already pending or already resolved for "
                    f"run_id={self._run_id!r}"
                )
        for coid in entry.client_order_ids:
            self._pending[coid] = entry

    def pop_for_resolution(self, run_id: str, client_order_id: str) -> PendingCapture | None:
        """Returns `None` for BOTH a genuinely unknown key (never registered) and an already-resolved
        one (duplicate resolution attempt) -- callers distinguish these, if needed, via
        :meth:`is_resolved`/:meth:`is_pending`; the resolution OUTCOME (drop, never double-write) is
        identical either way, per the CEO's own fail-closed requirement. Resolving via any ONE alias in
        a multi-id `PendingCapture` (bracket TP/SL) retires ALL of that entry's own aliases together."""
        if run_id != self._run_id:
            raise CorrelationRunMismatchError(
                f"CorrelationMap bound to run_id={self._run_id!r} cannot resolve an entry for "
                f"run_id={run_id!r}"
            )
        entry = self._pending.get(client_order_id)
        if entry is None:
            return None
        for coid in entry.client_order_ids:
            self._pending.pop(coid, None)
            self._resolved_client_order_ids.add(coid)
        return entry

    def is_pending(self, client_order_id: str) -> bool:
        return client_order_id in self._pending

    def is_resolved(self, client_order_id: str) -> bool:
        return client_order_id in self._resolved_client_order_ids

    def pending_count(self) -> int:
        """Distinct pending entries (not distinct alias keys -- a 3-alias bracket entry counts once)."""
        return len({id(v) for v in self._pending.values()})


# ---------------------------------------------------------------------------------------------------
# Decision-time capture
# ---------------------------------------------------------------------------------------------------


def capture_decision_observation(
    repository: ContextMemoryRepository, observation: Observation,
) -> ObservationId | None:
    """Append one bar's own already-built `Observation` (idempotent, content-addressed -- inherited
    from the repository, not reimplemented here). Never raises: returns `None` and logs on any
    unexpected failure, per Implementation Plan §11's defense-in-depth convention."""
    try:
        return repository.append_observation(observation)
    except Exception:
        _LOGGER.exception("learning_feedback: failed to append decision-time Observation")
        return None


def capture_operational_metadata(
    repository: ContextMemoryRepository, decision: RiskDecision, policy_state: str | None,
    observation_id: ObservationId,
) -> OperationalMetadataId | None:
    """Build (Phase D `build_operational_metadata`, consumed unmodified) and append one
    `OperationalMetadata` row. Never raises."""
    try:
        metadata = build_operational_metadata(decision, policy_state, observation_id)
        return repository.append_operational_metadata(metadata)
    except Exception:
        _LOGGER.exception("learning_feedback: failed to capture OperationalMetadata")
        return None


def register_pending_correlation(correlation: CorrelationMap, entry: PendingCapture) -> bool:
    """Register `entry` for later resolution. Returns `False` (never raises) on any
    :class:`CorrelationError` or unexpected failure -- a duplicate/mismatched registration is REJECTED,
    not silently accepted, but the rejection itself never escapes as an exception."""
    try:
        correlation.register_decision(entry)
        return True
    except Exception:
        _LOGGER.exception(
            "learning_feedback: failed to register pending correlation for client_order_ids=%s",
            entry.client_order_ids,
        )
        return False


# ---------------------------------------------------------------------------------------------------
# Resolution-time capture
# ---------------------------------------------------------------------------------------------------


def capture_strategy_resolution(
    repository: ContextMemoryRepository, correlation: CorrelationMap, run_id: str, client_order_id: str,
    position: ShadowPositionRecord, closing_leg: TradeRecord, observation_as_of: int,
) -> EdgeEvidenceId | None:
    """Resolve a closed Shadow position into a Strategy Outcome (Phase D `build_strategy_outcome`,
    consumed unmodified). Returns `None` -- never raises -- for: no matching pending entry (unknown or
    already-resolved `client_order_id`, both drop+log); a pending entry whose own `outcome_kind` is not
    STRATEGY (kind isolation, defense-in-depth on top of the SHADOW-CID/CID prefix separation that
    already keeps these namespaces disjoint); or `build_strategy_outcome` itself returning `None`
    (position not yet resolvable)."""
    try:
        entry = correlation.pop_for_resolution(run_id, client_order_id)
        if entry is None:
            _LOGGER.info(
                "learning_feedback: no pending correlation for run_id=%s client_order_id=%s -- dropped",
                run_id, client_order_id,
            )
            return None
        if entry.outcome_kind is not OutcomeKind.STRATEGY:
            _LOGGER.warning(
                "learning_feedback: pending entry for client_order_id=%s is kind=%s, not STRATEGY -- "
                "dropped (kind isolation)", client_order_id, entry.outcome_kind,
            )
            return None
        outcome = build_strategy_outcome(
            position, closing_leg, entry.observation_id, observation_as_of, entry.cost_model_ref,
        )
        if outcome is None:
            return None
        return repository.append_outcome(outcome)
    except Exception:
        _LOGGER.exception("learning_feedback: failed to capture Strategy resolution")
        return None


def capture_portfolio_resolution(
    repository: ContextMemoryRepository, correlation: CorrelationMap, run_id: str, client_order_id: str,
    trade: TradeRecord, observation_as_of: int,
) -> EdgeEvidenceId | None:
    """Resolve a closed real trade into a Portfolio Outcome (Phase D `build_portfolio_outcome`,
    consumed unmodified). Same miss/kind-isolation/adapter-`None` handling as
    :func:`capture_strategy_resolution`, mirrored for `OutcomeKind.PORTFOLIO`."""
    try:
        entry = correlation.pop_for_resolution(run_id, client_order_id)
        if entry is None:
            _LOGGER.info(
                "learning_feedback: no pending correlation for run_id=%s client_order_id=%s -- dropped",
                run_id, client_order_id,
            )
            return None
        if entry.outcome_kind is not OutcomeKind.PORTFOLIO:
            _LOGGER.warning(
                "learning_feedback: pending entry for client_order_id=%s is kind=%s, not PORTFOLIO -- "
                "dropped (kind isolation)", client_order_id, entry.outcome_kind,
            )
            return None
        outcome = build_portfolio_outcome(trade, entry.observation_id, observation_as_of, entry.cost_model_ref)
        if outcome is None:
            return None
        return repository.append_outcome(outcome)
    except Exception:
        _LOGGER.exception("learning_feedback: failed to capture Portfolio resolution")
        return None
