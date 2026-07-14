"""Lifecycle Controller (``STRATEGY_MANAGER_STATE_MACHINE.md``).

Owns every registered strategy's operational lifecycle state and enforces the state machine's legal
transitions (T1-T15). Never mutates a strategy's contract (architecture §7 invariant 1) — only the
Manager's own derived, operational classification (state-machine §"a derived, operational view").

**Composing the T-numbered edges into single calls.** The state-machine diagram enumerates
individual legal edges (e.g. T6 EXPLORATORY->CANDIDATE, T7 CANDIDATE->VALIDATED). This module
computes, in one step, the highest tier a contract's *own declared* ``lifecycle.maturity``
legitimately supports — gate-checking VALIDATED (matched-null + walk-forward PASS) and PROMOTED
(additionally global-FDR PASS + holdout-confirmed), exactly as §4 describes ("the guard on T7/T8
fails and the Manager holds the strategy at the highest state the ladder actually supports") — and
applies that as the target of a single :func:`admit`/:func:`reload_transition` call, rather than
requiring the caller to walk T4->T6->T7->T8 one edge at a time. This is a composition of the
documented guards, not a new rule: EXPLORATORY and CANDIDATE have no gate beyond "the contract says
so" (T4/T6 guards), so they are reachable directly; VALIDATED/PROMOTED still require their stated
evidence gates regardless of how many hops away the contract claims to be.
"""

from __future__ import annotations

from ai_trader.strategy_manager.contract import Contract, ContractStatus, HoldoutStatus, Maturity, TestStatus
from ai_trader.strategy_manager.loader import LoadOutcome
from ai_trader.strategy_manager.types import ACTIVATABLE_LIFECYCLES, CompatibilityResult, Health, Lifecycle

#: Lifecycles from which `disable()` is legal (state-machine §3: "any active/experimental").
_DISABLEABLE: frozenset[Lifecycle] = ACTIVATABLE_LIFECYCLES | {Lifecycle.EXPERIMENTAL}


def initial_lifecycle(outcome: LoadOutcome, compatibility: CompatibilityResult) -> Lifecycle:
    """T1/T2/T3: the lifecycle a freshly loaded (or reloaded-from-scratch) entry starts at, BEFORE
    any admission decision. Always ``EXPERIMENTAL`` for a valid, compatible, ``IMPLEMENTED``
    contract — "the post-load resting state of a valid contract"
    (``STRATEGY_MANAGER_STATE_MACHINE.md`` §1) — regardless of its declared maturity; reaching a
    higher tier always requires an explicit :func:`admit` or :func:`reload_transition` call.
    """
    if outcome.contract is None:
        return Lifecycle.INVALID  # T1 (schema-invalid) / CORRUPTED (no better bucket exists)
    if outcome.contract.lifecycle.status == ContractStatus.NOT_IMPLEMENTED:
        return Lifecycle.NOT_IMPLEMENTED  # T2
    if not compatibility.compatible:
        return Lifecycle.INVALID  # T15: quarantine; Health.INCOMPATIBLE carries the specific reason
    if outcome.contract.lifecycle.status == ContractStatus.INVALID:
        return Lifecycle.INVALID
    return Lifecycle.EXPERIMENTAL  # T3


def target_maturity_tier(contract: Contract) -> tuple[Lifecycle, bool]:
    """The highest :class:`Lifecycle` tier ``contract``'s declared ``lifecycle.maturity`` actually
    supports, gate-checking VALIDATED/PROMOTED (T7/T8 guards).

    Returns:
        ``(tier, gate_held)`` — ``gate_held`` is ``True`` iff the contract claims a maturity higher
        than the ladder can currently support (the guard failed and the Manager held it at a lower
        tier, per §4's "raising a health warning").
    """
    maturity = contract.lifecycle.maturity
    if maturity is Maturity.RETIRED:
        return Lifecycle.RETIRED, False
    if maturity is Maturity.EXPLORATORY:
        return Lifecycle.EXPLORATORY, False
    if maturity is Maturity.CANDIDATE:
        return Lifecycle.CANDIDATE, False

    validated_gate = (
        contract.evidence.matched_null_status.status is TestStatus.PASS
        and contract.evidence.walk_forward_status is TestStatus.PASS
    )
    if maturity is Maturity.VALIDATED:
        return (Lifecycle.VALIDATED, False) if validated_gate else (Lifecycle.CANDIDATE, True)

    # maturity is Maturity.PROMOTED
    promoted_gate = (
        validated_gate
        and contract.evidence.global_fdr_status is TestStatus.PASS
        and contract.provenance.holdout_status is HoldoutStatus.OPENED
    )
    if promoted_gate:
        return Lifecycle.PROMOTED, False
    if validated_gate:
        return Lifecycle.VALIDATED, True
    return Lifecycle.CANDIDATE, True


class TransitionOutcome:
    """The result of one lifecycle-mutating operation, before the caller (the Manager) wraps it
    into a :class:`~ai_trader.strategy_manager.types.LifecycleResult` with the strategy id."""

    __slots__ = ("ok", "from_state", "to_state", "reason", "gate_held")

    def __init__(
        self, ok: bool, from_state: Lifecycle | None, to_state: Lifecycle | None, reason: str,
        gate_held: bool = False,
    ) -> None:
        self.ok = ok
        self.from_state = from_state
        self.to_state = to_state
        self.reason = reason
        self.gate_held = gate_held


def admit(current: Lifecycle, contract: Contract | None) -> TransitionOutcome:
    """T4: admit an ``EXPERIMENTAL`` strategy into the live active set, landing at the highest tier
    its contract supports (see module docstring)."""
    if current is not Lifecycle.EXPERIMENTAL:
        return TransitionOutcome(False, current, current, f"cannot activate from lifecycle {current.value} (only EXPERIMENTAL is admissible)")
    if contract is None:
        return TransitionOutcome(False, current, current, "no contract available to determine target maturity")
    target, gate_held = target_maturity_tier(contract)
    if target not in ACTIVATABLE_LIFECYCLES:
        return TransitionOutcome(False, current, current, f"contract maturity {contract.lifecycle.maturity.value} is not activatable")
    reason = "admitted" if not gate_held else (
        f"admitted at {target.value}; contract claims {contract.lifecycle.maturity.value} but its "
        "validation gate is not satisfied -- held at the highest state the ladder supports"
    )
    return TransitionOutcome(True, current, target, reason, gate_held)


def withdraw_admit(current: Lifecycle) -> TransitionOutcome:
    """T5: withdraw live admission, back to sandbox-only ``EXPERIMENTAL``."""
    if current not in ACTIVATABLE_LIFECYCLES:
        return TransitionOutcome(False, current, current, f"cannot withdraw admission from lifecycle {current.value} (not in the live active set)")
    return TransitionOutcome(True, current, Lifecycle.EXPERIMENTAL, "withdrawn from the live active set")


def reload_transition(current: Lifecycle, contract: Contract | None, compatibility: CompatibilityResult) -> TransitionOutcome:
    """T6-T9 (and re-derived T1/T2/T15): re-evaluate an existing entry's lifecycle against its
    (possibly changed) contract. Only meaningful for entries already at or above ``EXPERIMENTAL``
    (i.e. previously loaded successfully) — a strategy resting at ``EXPERIMENTAL`` (never admitted)
    simply gets a fresh :func:`initial_lifecycle` outcome; an already-active strategy is re-targeted
    to whatever tier the new contract supports, up OR down (T9), never silently staying stale.

    ``DISABLED`` is a special case: it is an operator kill-switch overlay (T10), and the state
    machine's only documented way OUT of it is ``enable()`` (T11) — an unrelated content reload
    (e.g. a routine evidence-field update) must never silently clear it. A disabled strategy's
    underlying contract/compatibility are still refreshed by the caller so a later ``enable()``
    re-validates against current data, but the lifecycle itself stays ``DISABLED`` here regardless
    of what the new contract says.

    Check order matters and mirrors :func:`initial_lifecycle` exactly: ``NOT_IMPLEMENTED`` status is
    checked BEFORE compatibility (a stub's ``required_data`` may not yet be satisfiable by the
    Scanner — that must still resolve to ``NOT_IMPLEMENTED``, not a misleading ``INVALID``/
    ``INCOMPATIBLE``).
    """
    if current is Lifecycle.DISABLED:
        return TransitionOutcome(
            True, current, Lifecycle.DISABLED,
            "reload while disabled: contract/compatibility refreshed, remains disabled until enable()",
        )
    if contract is None:
        return TransitionOutcome(True, current, Lifecycle.INVALID, "reload failed: no valid contract")
    if contract.lifecycle.status == ContractStatus.NOT_IMPLEMENTED:
        return TransitionOutcome(True, current, Lifecycle.NOT_IMPLEMENTED, "reloaded contract now NOT_IMPLEMENTED")
    if not compatibility.compatible:
        reason = "reload incompatible: " + "; ".join(compatibility.reasons)
        return TransitionOutcome(True, current, Lifecycle.INVALID, reason)
    if contract.lifecycle.status == ContractStatus.INVALID:
        return TransitionOutcome(True, current, Lifecycle.INVALID, "reloaded contract status=INVALID")
    if current not in ACTIVATABLE_LIFECYCLES:
        # was EXPERIMENTAL/INVALID/NOT_IMPLEMENTED -- a successful reload just re-derives the initial
        # resting state; admission remains a separate, explicit `admit()` call (T3, not T6-T9).
        return TransitionOutcome(True, current, Lifecycle.EXPERIMENTAL, "reloaded: valid + compatible, resting at EXPERIMENTAL pending admission")
    target, gate_held = target_maturity_tier(contract)
    if target not in ACTIVATABLE_LIFECYCLES:
        # contract's own maturity dropped to something no longer active-eligible (e.g. RETIRED).
        return TransitionOutcome(True, current, target, f"reload lowered maturity to {contract.lifecycle.maturity.value}; no longer active")
    direction = "raised" if target != current else "unchanged"
    reason = f"reload {direction} maturity to {target.value}" + (
        f" (contract claims {contract.lifecycle.maturity.value}; gate not satisfied, held at {target.value})" if gate_held else ""
    )
    return TransitionOutcome(True, current, target, reason, gate_held)


def disable(current: Lifecycle) -> TransitionOutcome:
    """T10: operational kill-switch overlay, from any disable-eligible state."""
    if current not in _DISABLEABLE:
        return TransitionOutcome(False, current, current, f"cannot disable from lifecycle {current.value}")
    return TransitionOutcome(True, current, Lifecycle.DISABLED, "disabled")


def enable(current: Lifecycle, prior: Lifecycle | None, contract: Contract | None, compatibility: CompatibilityResult) -> TransitionOutcome:
    """T11: re-enable a ``DISABLED`` strategy, restoring its prior state -- but only after
    re-validating (``enable`` re-validates before restoring, ``STRATEGY_MANAGER_API.md`` §4)."""
    if current is not Lifecycle.DISABLED:
        return TransitionOutcome(False, current, current, f"cannot enable from lifecycle {current.value} (not DISABLED)")
    if contract is None or not compatibility.compatible:
        return TransitionOutcome(False, current, current, "re-validation failed: no longer a valid, compatible contract")
    restored = prior if prior is not None else Lifecycle.EXPERIMENTAL
    return TransitionOutcome(True, current, restored, f"re-enabled, restored to {restored.value}")


def retire(current: Lifecycle) -> TransitionOutcome:
    """T12: terminal withdrawal within the interface MAJOR, legal from ANY state per the
    transition table (``STRATEGY_MANAGER_STATE_MACHINE.md`` §3, T12: "from: any"). Idempotent
    (retiring an already-RETIRED strategy is a no-op success, ``STRATEGY_MANAGER_API.md`` §4).
    Includes ``INVALID``/``NOT_IMPLEMENTED``: an operator must be able to permanently withdraw a
    strategy that is broken or abandoned, not leave it stuck in limbo forever."""
    if current is Lifecycle.RETIRED:
        return TransitionOutcome(True, current, current, "already retired (idempotent)")
    return TransitionOutcome(True, current, Lifecycle.RETIRED, "retired")


def is_health_incompatible_bucket(target_lifecycle: Lifecycle, contract_ok: bool, compatibility_ok: bool) -> Health | None:
    """Map a T1/T15 quarantine outcome to its specific :class:`Health` reason, when the base
    lifecycle landed on ``INVALID`` for a reason other than schema failure. Returns ``None`` when
    the caller should keep whatever base ``Health`` the Loader/Compatibility Checker already
    assigned (schema failure -> ``INVALID``, parse failure -> ``CORRUPTED``)."""
    if target_lifecycle is Lifecycle.INVALID and contract_ok and not compatibility_ok:
        return Health.INCOMPATIBLE
    return None
