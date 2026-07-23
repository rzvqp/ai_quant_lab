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

**Superseded by the position-scoped layer below (Architectural Decision Package, Decisions 1-3)**: the
"disclosed, accepted limitation" this docstring originally described here -- multiple partial fills
sharing one `client_order_id`, with only the first resolution succeeding -- was reviewed by the CEO and
found to conflict with confirmed production semantics (partial exits are economically DISTINCT events,
never duplicates of one fact). `client_order_id`-keyed `CorrelationMap`/`PendingCapture` below is NOT
removed -- the Lifecycle Specification proved it remains the correct, reliable bridge from one decision to
that SAME decision's own opening fill (Lifecycle Specification I5) -- but it is no longer used as the
correlation key for anything AFTER the opening fill. `PositionCorrelationMap`/`PendingPosition` (this
module, appended below) own everything from the opening fill onward: interim realizations for every
partial that does not zero the position, exactly one terminal `Outcome` for the fill that does, and
correct compound handling of a flip (one decision that simultaneously closes one economic position and
opens another). See `LEARNING_FEEDBACK_ARCHITECTURAL_DECISION_PACKAGE.md` for the full reasoning.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, replace

from ai_trader.context_memory.contracts import (
    EdgeEvidenceId,
    InterimRealizationId,
    Observation,
    ObservationId,
    OperationalMetadataId,
    PositionOutcomeId,
)
from ai_trader.context_memory.enums import OutcomeKind
from ai_trader.context_memory.repository import ContextMemoryRepository
from ai_trader.learning_feedback.adapters import (
    build_operational_metadata,
    build_portfolio_interim_realization,
    build_portfolio_outcome,
    build_portfolio_position_outcome,
    build_strategy_interim_realization,
    build_strategy_outcome,
    build_strategy_position_outcome,
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

    def discard(self, run_id: str, client_order_id: str) -> PendingCapture | None:
        """Retire an entry with NO resolution ever produced for it -- Sprint 2 Blocker 3: an order that
        was allowed but never reached a fill (cancelled, expired, or a rejection not caught synchronously
        at ``execute()`` time) must not persist forever. Same run-mismatch/unknown-key semantics as
        :meth:`pop_for_resolution`; retires every alias of a multi-id (bracket) entry together. Never
        produces an Outcome -- purely bookkeeping cleanup."""
        return self.pop_for_resolution(run_id, client_order_id)

    def drain_pending(self) -> tuple[PendingCapture, ...]:
        """Every entry still pending, retired with no resolution ever produced -- end-of-run sweep
        (Sprint 2 Blocker 3), mirroring :meth:`PositionCorrelationMap.drain_pending` exactly. Guarantees
        `pending_count() == 0` after this call. Idempotent: a second call returns an empty tuple, since
        every entry is retired (not merely read) the first time."""
        drained = tuple({id(v): v for v in self._pending.values()}.values())
        for entry in drained:
            for coid in entry.client_order_ids:
                self._pending.pop(coid, None)
                self._resolved_client_order_ids.add(coid)
        return drained


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


# ---------------------------------------------------------------------------------------------------
# Position-scoped correlation (Architectural Decision Package, Decisions 1-3)
#
# `client_order_id`/`CorrelationMap` above remain exactly as built in Phase E -- proven (Lifecycle
# Specification I5) to reliably bridge one decision to that SAME decision's own opening fill, never to a
# later, independent closing order. `PositionCorrelationMap` below owns everything from the opening fill
# onward, keyed by the run-scoped, position-identity `position_key` string
# (`ai_trader.learning_feedback.position_registry.make_position_key`) -- proven the only identifier that
# survives every closing mechanism (Lifecycle Specification §6/§7): ordinary exit, time-stop, trailing-
# stop, bracket, liquidation, and (per Decision 2) a flip's own compound close-old/open-new event.
# ---------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class PendingPosition:
    """Everything needed to resolve the position identified by `position_key`, once its owning fill(s)
    are observed -- the position-scoped analogue of `PendingCapture`, minted either by promoting a
    decision-time `PendingCapture` at the moment its opening fill is observed (`promote_opening_fill`), or
    by deriving one directly from the OLD position's own entry at flip time (`register_flip_position`,
    Decision 2 -- a flip's new position has no decision of its own).

    `accumulated_partials`/`interim_realization_ids` (Learning/Research Feedback Sprint 2, Blocker 2,
    CEO-ratified): the COMPLETE, in-order ledger of every partial (`TradeRecord`/leg) and every already-
    produced `InterimRealizationId` contributed by this position's own lifecycle so far -- accumulated
    via `PositionCorrelationMap.accumulate`, consumed once, at terminal capture time, to build the ONE
    canonical `PositionOutcome` for this position (never a research metric -- pure Level-1 arithmetic
    over this exact ledger)."""

    run_id: str
    position_key: str
    strategy_id: str
    symbol: str
    outcome_kind: OutcomeKind
    observation_id: ObservationId
    cost_model_ref: str
    decision_as_of: int
    accumulated_partials: tuple[TradeRecord, ...] = ()
    interim_realization_ids: tuple[InterimRealizationId, ...] = ()


class PositionCorrelationMap:
    """Run-scoped, in-memory-only, position-keyed correlation state -- never persisted, mirroring
    `CorrelationMap`'s own conventions exactly (bound to one `run_id`, fail-closed on mismatch/duplicate).
    Unlike `CorrelationMap`, `get`/peek does NOT retire an entry -- an interim realization must be able to
    read a still-open position's own pending entry repeatedly, across many partial exits, without ever
    treating that read as "the" resolution (Decision 3: only the fill that brings a position to zero size
    retires its entry, via `retire`)."""

    def __init__(self, run_id: str) -> None:
        self._run_id = run_id
        self._pending: dict[str, PendingPosition] = {}
        self._resolved_position_keys: set[str] = set()

    @property
    def run_id(self) -> str:
        return self._run_id

    def register(self, entry: PendingPosition) -> None:
        """Raises `CorrelationRunMismatchError`/`DuplicateDecisionCaptureError` -- callers in this module
        always catch these at the public function boundary; a direct caller (e.g. a test) sees them
        raised."""
        if entry.run_id != self._run_id:
            raise CorrelationRunMismatchError(
                f"PositionCorrelationMap bound to run_id={self._run_id!r} cannot register an entry for "
                f"run_id={entry.run_id!r}"
            )
        if entry.position_key in self._pending or entry.position_key in self._resolved_position_keys:
            raise DuplicateDecisionCaptureError(
                f"position_key={entry.position_key!r} is already pending or already resolved for "
                f"run_id={self._run_id!r}"
            )
        self._pending[entry.position_key] = entry

    def get(self, position_key: str) -> PendingPosition | None:
        """A non-retiring peek -- safe to call once per interim realization against a still-open
        position, any number of times."""
        return self._pending.get(position_key)

    def accumulate(
        self, run_id: str, position_key: str, trade: TradeRecord,
        interim_realization_id: InterimRealizationId | None = None,
    ) -> PendingPosition | None:
        """Append `trade` (and, if produced, its own `interim_realization_id`) to the still-pending
        entry's own ledger -- Sprint 2 Blocker 2: every interim/terminal capture call accumulates its own
        partial here FIRST, so a `PositionOutcome` can later be built from the COMPLETE ledger, not just
        the terminal partial alone. Does NOT retire the entry (mirrors `get`'s own non-destructive
        semantics) -- `retire` is still the only way an entry stops being pending. Returns the entry
        AFTER accumulation, or `None` for an unknown/already-resolved `position_key` (same miss
        semantics as `get`)."""
        if run_id != self._run_id:
            raise CorrelationRunMismatchError(
                f"PositionCorrelationMap bound to run_id={self._run_id!r} cannot accumulate onto an "
                f"entry for run_id={run_id!r}"
            )
        entry = self._pending.get(position_key)
        if entry is None:
            return None
        new_interim_ids = (
            entry.interim_realization_ids + (interim_realization_id,)
            if interim_realization_id is not None else entry.interim_realization_ids
        )
        updated = replace(
            entry, accumulated_partials=entry.accumulated_partials + (trade,),
            interim_realization_ids=new_interim_ids,
        )
        self._pending[position_key] = updated
        return updated

    def retire(self, run_id: str, position_key: str) -> PendingPosition | None:
        """Pop and permanently retire `position_key` -- called exactly once, for the fill that brings a
        position to zero size (a plain close, or the closing half of a flip). Returns `None` for BOTH an
        unknown key and an already-retired one, exactly like `CorrelationMap.pop_for_resolution`."""
        if run_id != self._run_id:
            raise CorrelationRunMismatchError(
                f"PositionCorrelationMap bound to run_id={self._run_id!r} cannot retire an entry for "
                f"run_id={run_id!r}"
            )
        entry = self._pending.pop(position_key, None)
        if entry is None:
            return None
        self._resolved_position_keys.add(position_key)
        return entry

    def is_pending(self, position_key: str) -> bool:
        return position_key in self._pending

    def is_resolved(self, position_key: str) -> bool:
        return position_key in self._resolved_position_keys

    def pending_count(self) -> int:
        return len(self._pending)

    def drain_pending(self) -> tuple[PendingPosition, ...]:
        """Every entry still open, retired with NO Outcome ever produced for it -- end-of-run disposition
        for a `HOLD_AND_MARK` position (Decision 3): the position's fate in this run is genuinely
        unresolved, never fabricated. Idempotent: calling this twice returns an empty tuple the second
        time, since every entry is retired (not merely read) the first time."""
        drained = tuple(self._pending.values())
        for entry in drained:
            self._resolved_position_keys.add(entry.position_key)
        self._pending.clear()
        return drained


def promote_opening_fill(
    correlation: CorrelationMap, position_map: PositionCorrelationMap, run_id: str, client_order_id: str,
    position_key: str, expected_outcome_kind: OutcomeKind,
) -> bool:
    """Bridge a decision-time `PendingCapture` (registered under `client_order_id`, Phase E's own
    mechanism) into the position-scoped `PositionCorrelationMap`, at the moment the registry (Decision 1)
    observes this exact fill's own opening bar. Never raises: returns `False` (drop+log) if the
    `client_order_id` candidate is unknown/already consumed, or if its own `outcome_kind` does not match
    `expected_outcome_kind` (defense-in-depth kind isolation, mirroring the existing resolution
    functions)."""
    try:
        candidate = correlation.pop_for_resolution(run_id, client_order_id)
        if candidate is None:
            _LOGGER.info(
                "learning_feedback: no pending decision-time correlation for run_id=%s client_order_id=%s "
                "-- cannot promote to position_key=%s", run_id, client_order_id, position_key,
            )
            return False
        if candidate.outcome_kind is not expected_outcome_kind:
            _LOGGER.warning(
                "learning_feedback: pending entry for client_order_id=%s is kind=%s, not %s -- dropped "
                "(kind isolation)", client_order_id, candidate.outcome_kind, expected_outcome_kind,
            )
            return False
        position_map.register(PendingPosition(
            run_id=run_id, position_key=position_key, strategy_id=candidate.strategy_id,
            symbol=candidate.symbol, outcome_kind=candidate.outcome_kind,
            observation_id=candidate.observation_id, cost_model_ref=candidate.cost_model_ref,
            decision_as_of=candidate.decision_as_of,
        ))
        return True
    except Exception:
        _LOGGER.exception(
            "learning_feedback: failed to promote opening fill client_order_id=%s to position_key=%s",
            client_order_id, position_key,
        )
        return False


def register_shadow_position(position_map: PositionCorrelationMap, entry: PendingPosition) -> bool:
    """Register a `PendingPosition` for a Shadow strategy DIRECTLY, at decision time -- Sprint 2 Blocker
    1 (`LEARNING_FEEDBACK_NEXT_SPRINT_DESIGN.md`, Option A). Unlike the real-portfolio side (which must
    bridge a `client_order_id` candidate to a `position_key` once the opening fill is observed, via
    `promote_opening_fill`), Shadow's own `position_id` is already deterministically known at decision
    time (`ShadowEvidenceEngine`'s own `position_id` formula, minted before the virtual entry order is
    even known to have filled) -- no two-stage promotion is needed. Never raises; returns `False` (log)
    on any registration failure (e.g. a duplicate `position_key`, which should not happen by
    construction since Shadow's own `position_id` formula is unique per decision)."""
    try:
        position_map.register(entry)
        return True
    except Exception:
        _LOGGER.exception(
            "learning_feedback: failed to register shadow position position_key=%s", entry.position_key,
        )
        return False


def register_flip_position(
    position_map: PositionCorrelationMap, run_id: str, old_position_key: str, new_position_key: str,
    new_strategy_id: str,
) -> bool:
    """Derive a fresh `PendingPosition` for the newly-opened side of a flip directly from the OLD
    position's own still-pending entry (Decision 2: a flip's new position is caused by the SAME decision
    that closes the old one -- there is no independent decision to bridge from). MUST be called BEFORE
    the old entry is retired via `capture_portfolio_terminal`/`capture_strategy_terminal` (both peek via
    `get`-then-`retire`, never destructively before this runs). Never raises."""
    try:
        old_entry = position_map.get(old_position_key)
        if old_entry is None:
            _LOGGER.warning(
                "learning_feedback: no pending entry for old_position_key=%s -- cannot derive flip "
                "registration for new_position_key=%s", old_position_key, new_position_key,
            )
            return False
        position_map.register(PendingPosition(
            run_id=run_id, position_key=new_position_key, strategy_id=new_strategy_id,
            symbol=old_entry.symbol, outcome_kind=old_entry.outcome_kind,
            observation_id=old_entry.observation_id, cost_model_ref=old_entry.cost_model_ref,
            decision_as_of=old_entry.decision_as_of,
        ))
        return True
    except Exception:
        _LOGGER.exception(
            "learning_feedback: failed to register flip position new_position_key=%s from "
            "old_position_key=%s", new_position_key, old_position_key,
        )
        return False


def capture_portfolio_terminal(
    repository: ContextMemoryRepository, position_map: PositionCorrelationMap, run_id: str,
    position_key: str, trade: TradeRecord, observation_as_of: int,
) -> EdgeEvidenceId | None:
    """Resolve the real-portfolio position identified by `position_key` into a terminal Portfolio Outcome
    -- called exactly once, for the fill that brings that position to zero size (Decision 3). Retires
    `position_key` via `PositionCorrelationMap.retire`; every subsequent call for the same key is treated
    as an unknown/duplicate key and dropped, identically to `capture_portfolio_resolution`.

    **Sprint 2, Blocker 2** (CEO-ratified, additive): also builds and appends the ONE canonical
    `PositionOutcome` for this position's own complete lifecycle, aggregated from every accumulated
    partial (`PositionCorrelationMap.accumulate`). Return type is UNCHANGED (still the terminal Outcome's
    own `EdgeEvidenceId`) -- `PositionOutcome`'s own id is not returned, only persisted, preserving full
    backward compatibility with every existing caller/test of this function."""
    try:
        accumulated = position_map.accumulate(run_id, position_key, trade)
        if accumulated is None:
            _LOGGER.info(
                "learning_feedback: no pending position correlation for run_id=%s position_key=%s -- "
                "dropped", run_id, position_key,
            )
            return None
        entry = position_map.retire(run_id, position_key)
        if entry is None:  # pragma: no cover -- defensive only; accumulate() just confirmed it exists.
            return None
        if entry.outcome_kind is not OutcomeKind.PORTFOLIO:
            _LOGGER.warning(
                "learning_feedback: pending position entry for position_key=%s is kind=%s, not "
                "PORTFOLIO -- dropped (kind isolation)", position_key, entry.outcome_kind,
            )
            return None
        outcome = build_portfolio_outcome(trade, entry.observation_id, observation_as_of, entry.cost_model_ref)
        if outcome is None:
            return None
        outcome_id = repository.append_outcome(outcome)
        position_outcome = build_portfolio_position_outcome(
            entry.accumulated_partials, position_key, entry.observation_id, entry.cost_model_ref,
            outcome_id, entry.interim_realization_ids,
        )
        if position_outcome is not None:
            repository.append_position_outcome(position_outcome)
        return outcome_id
    except Exception:
        _LOGGER.exception("learning_feedback: failed to capture Portfolio terminal resolution")
        return None


def capture_portfolio_interim(
    repository: ContextMemoryRepository, position_map: PositionCorrelationMap, run_id: str,
    position_key: str, trade: TradeRecord, observation_as_of: int,
) -> InterimRealizationId | None:
    """Capture one non-terminal, diagnostic-only realization for a real-portfolio partial exit that does
    NOT bring `position_key` to zero size (Decision 3) -- PEEKS the pending entry via `PositionCorrelation
    Map.get`, never retires it. May be called any number of times for the same still-open `position_key`.

    **Sprint 2, Blocker 2**: also accumulates `trade` (and, if produced, this realization's own id) onto
    the pending entry's own ledger, so the eventual terminal `PositionOutcome` can aggregate across every
    partial, not just the terminal one."""
    try:
        if run_id != position_map.run_id:
            _LOGGER.warning(
                "learning_feedback: run_id=%s does not match PositionCorrelationMap's own run_id=%s -- "
                "dropped", run_id, position_map.run_id,
            )
            return None
        entry = position_map.get(position_key)
        if entry is None:
            _LOGGER.info(
                "learning_feedback: no pending position correlation for run_id=%s position_key=%s -- "
                "dropped", run_id, position_key,
            )
            return None
        if entry.outcome_kind is not OutcomeKind.PORTFOLIO:
            _LOGGER.warning(
                "learning_feedback: pending position entry for position_key=%s is kind=%s, not "
                "PORTFOLIO -- dropped (kind isolation)", position_key, entry.outcome_kind,
            )
            return None
        realization = build_portfolio_interim_realization(
            trade, position_key, entry.observation_id, observation_as_of, entry.cost_model_ref,
        )
        if realization is None:
            position_map.accumulate(run_id, position_key, trade)
            return None
        realization_id = repository.append_interim_realization(realization)
        position_map.accumulate(run_id, position_key, trade, interim_realization_id=realization_id)
        return realization_id
    except Exception:
        _LOGGER.exception("learning_feedback: failed to capture Portfolio interim realization")
        return None


def capture_strategy_terminal(
    repository: ContextMemoryRepository, position_map: PositionCorrelationMap, run_id: str,
    position_key: str, position: ShadowPositionRecord, closing_leg: TradeRecord, observation_as_of: int,
) -> EdgeEvidenceId | None:
    """Resolve the Shadow position identified by `position_key` into a terminal Strategy Outcome -- the
    Shadow-side mirror of `capture_portfolio_terminal`. Shadow already tracks its own stable
    `position_id` (Lifecycle Specification §3B, already correct) -- `position_key` here is expected to be
    that SAME string, passed straight through by the caller, not re-derived by this module.

    **Sprint 2, Blocker 2**: mirrors `capture_portfolio_terminal`'s own `PositionOutcome` aggregation,
    for `OutcomeKind.STRATEGY`. Return type unchanged."""
    try:
        accumulated = position_map.accumulate(run_id, position_key, closing_leg)
        if accumulated is None:
            _LOGGER.info(
                "learning_feedback: no pending position correlation for run_id=%s position_key=%s -- "
                "dropped", run_id, position_key,
            )
            return None
        entry = position_map.retire(run_id, position_key)
        if entry is None:  # pragma: no cover -- defensive only; accumulate() just confirmed it exists.
            return None
        if entry.outcome_kind is not OutcomeKind.STRATEGY:
            _LOGGER.warning(
                "learning_feedback: pending position entry for position_key=%s is kind=%s, not STRATEGY "
                "-- dropped (kind isolation)", position_key, entry.outcome_kind,
            )
            return None
        outcome = build_strategy_outcome(
            position, closing_leg, entry.observation_id, observation_as_of, entry.cost_model_ref,
        )
        if outcome is None:
            return None
        outcome_id = repository.append_outcome(outcome)
        position_outcome = build_strategy_position_outcome(
            entry.accumulated_partials, position_key, entry.observation_id, entry.cost_model_ref,
            outcome_id, entry.interim_realization_ids,
        )
        if position_outcome is not None:
            repository.append_position_outcome(position_outcome)
        return outcome_id
    except Exception:
        _LOGGER.exception("learning_feedback: failed to capture Strategy terminal resolution")
        return None


def capture_strategy_interim(
    repository: ContextMemoryRepository, position_map: PositionCorrelationMap, run_id: str,
    position_key: str, closing_leg: TradeRecord, observation_as_of: int,
) -> InterimRealizationId | None:
    """Capture one non-terminal, diagnostic-only realization for a Shadow partial exit leg that does NOT
    bring `position_key` to zero size -- the Shadow-side mirror of `capture_portfolio_interim`, including
    the same Sprint 2 Blocker 2 accumulation."""
    try:
        if run_id != position_map.run_id:
            _LOGGER.warning(
                "learning_feedback: run_id=%s does not match PositionCorrelationMap's own run_id=%s -- "
                "dropped", run_id, position_map.run_id,
            )
            return None
        entry = position_map.get(position_key)
        if entry is None:
            _LOGGER.info(
                "learning_feedback: no pending position correlation for run_id=%s position_key=%s -- "
                "dropped", run_id, position_key,
            )
            return None
        if entry.outcome_kind is not OutcomeKind.STRATEGY:
            _LOGGER.warning(
                "learning_feedback: pending position entry for position_key=%s is kind=%s, not STRATEGY "
                "-- dropped (kind isolation)", position_key, entry.outcome_kind,
            )
            return None
        realization = build_strategy_interim_realization(
            closing_leg, position_key, entry.observation_id, observation_as_of, entry.cost_model_ref,
        )
        if realization is None:
            position_map.accumulate(run_id, position_key, closing_leg)
            return None
        realization_id = repository.append_interim_realization(realization)
        position_map.accumulate(run_id, position_key, closing_leg, interim_realization_id=realization_id)
        return realization_id
    except Exception:
        _LOGGER.exception("learning_feedback: failed to capture Strategy interim realization")
        return None
