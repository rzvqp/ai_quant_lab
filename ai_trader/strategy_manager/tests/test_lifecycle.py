"""Tests for :mod:`ai_trader.strategy_manager.lifecycle` — the state machine
(``STRATEGY_MANAGER_STATE_MACHINE.md``)."""

from __future__ import annotations

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_manager.lifecycle import (
    admit,
    disable,
    enable,
    initial_lifecycle,
    is_health_incompatible_bucket,
    reload_transition,
    retire,
    target_maturity_tier,
    withdraw_admit,
)
from ai_trader.strategy_manager.loader import LoadOutcome
from ai_trader.strategy_manager.tests.fixtures.contracts import (
    PROMOTED_GATE_OVERRIDES,
    VALIDATED_GATE_OVERRIDES,
    make_contract_dict,
)
from ai_trader.strategy_manager.types import CompatibilityResult, ContractRef, Health, Lifecycle

COMPATIBLE = CompatibilityResult(True, True, True, True, True)
INCOMPATIBLE = CompatibilityResult(False, True, True, True, False, reasons=["missing_timeframe:D1"])


def _outcome(contract_dict: dict | None, health: Health = Health.LOADED) -> LoadOutcome:
    contract = parse_contract(contract_dict) if contract_dict is not None else None
    return LoadOutcome("path", contract.identity.id if contract else None, None, contract, ContractRef(), health)


class TestInitialLifecycle:
    def test_corrupted_or_no_contract_is_invalid(self) -> None:
        assert initial_lifecycle(_outcome(None, Health.CORRUPTED), COMPATIBLE) is Lifecycle.INVALID

    def test_schema_invalid_is_invalid(self) -> None:
        assert initial_lifecycle(_outcome(None, Health.INVALID), COMPATIBLE) is Lifecycle.INVALID

    def test_not_implemented_status(self) -> None:
        outcome = _outcome(make_contract_dict(status="NOT_IMPLEMENTED"))
        assert initial_lifecycle(outcome, COMPATIBLE) is Lifecycle.NOT_IMPLEMENTED

    def test_incompatible_is_invalid(self) -> None:
        outcome = _outcome(make_contract_dict())
        assert initial_lifecycle(outcome, INCOMPATIBLE) is Lifecycle.INVALID

    def test_contract_status_invalid(self) -> None:
        outcome = _outcome(make_contract_dict(status="INVALID"))
        assert initial_lifecycle(outcome, COMPATIBLE) is Lifecycle.INVALID

    def test_valid_compatible_implemented_is_experimental(self) -> None:
        outcome = _outcome(make_contract_dict(status="IMPLEMENTED", maturity="CANDIDATE"))
        # regardless of declared maturity -- EXPERIMENTAL is always the initial resting state
        assert initial_lifecycle(outcome, COMPATIBLE) is Lifecycle.EXPERIMENTAL


class TestTargetMaturityTier:
    def test_exploratory(self) -> None:
        contract = parse_contract(make_contract_dict(maturity="EXPLORATORY"))
        assert target_maturity_tier(contract) == (Lifecycle.EXPLORATORY, False)

    def test_candidate(self) -> None:
        contract = parse_contract(make_contract_dict(maturity="CANDIDATE"))
        assert target_maturity_tier(contract) == (Lifecycle.CANDIDATE, False)

    def test_retired(self) -> None:
        contract = parse_contract(make_contract_dict(maturity="RETIRED"))
        assert target_maturity_tier(contract) == (Lifecycle.RETIRED, False)

    def test_validated_gate_satisfied(self) -> None:
        contract = parse_contract(make_contract_dict(**VALIDATED_GATE_OVERRIDES))
        assert target_maturity_tier(contract) == (Lifecycle.VALIDATED, False)

    def test_validated_gate_not_satisfied_holds_at_candidate(self) -> None:
        contract = parse_contract(make_contract_dict(maturity="VALIDATED"))  # gates still NOT_RUN
        tier, gate_held = target_maturity_tier(contract)
        assert tier is Lifecycle.CANDIDATE
        assert gate_held is True

    def test_promoted_gate_satisfied(self) -> None:
        contract = parse_contract(make_contract_dict(**PROMOTED_GATE_OVERRIDES))
        assert target_maturity_tier(contract) == (Lifecycle.PROMOTED, False)

    def test_promoted_without_holdout_opened_holds_at_validated(self) -> None:
        overrides = dict(PROMOTED_GATE_OVERRIDES)
        overrides["holdout_status"] = "SEALED"  # the real, current, project-wide state
        contract = parse_contract(make_contract_dict(**overrides))
        tier, gate_held = target_maturity_tier(contract)
        assert tier is Lifecycle.VALIDATED
        assert gate_held is True

    def test_promoted_without_any_gate_holds_at_candidate(self) -> None:
        contract = parse_contract(make_contract_dict(maturity="PROMOTED"))  # nothing run
        tier, gate_held = target_maturity_tier(contract)
        assert tier is Lifecycle.CANDIDATE
        assert gate_held is True


class TestAdmit:
    def test_admits_experimental_to_exploratory(self) -> None:
        contract = parse_contract(make_contract_dict(maturity="EXPLORATORY"))
        outcome = admit(Lifecycle.EXPERIMENTAL, contract)
        assert outcome.ok
        assert outcome.to_state is Lifecycle.EXPLORATORY
        assert not outcome.gate_held

    def test_admits_directly_to_candidate_when_contract_says_so(self) -> None:
        contract = parse_contract(make_contract_dict(maturity="CANDIDATE"))
        outcome = admit(Lifecycle.EXPERIMENTAL, contract)
        assert outcome.to_state is Lifecycle.CANDIDATE

    def test_rejects_from_non_experimental(self) -> None:
        contract = parse_contract(make_contract_dict())
        outcome = admit(Lifecycle.EXPLORATORY, contract)
        assert not outcome.ok
        assert outcome.to_state is Lifecycle.EXPLORATORY  # unchanged

    def test_rejects_without_contract(self) -> None:
        outcome = admit(Lifecycle.EXPERIMENTAL, None)
        assert not outcome.ok

    def test_rejects_retired_contract(self) -> None:
        contract = parse_contract(make_contract_dict(maturity="RETIRED"))
        outcome = admit(Lifecycle.EXPERIMENTAL, contract)
        assert not outcome.ok

    def test_gate_held_note_present_in_reason(self) -> None:
        contract = parse_contract(make_contract_dict(maturity="VALIDATED"))
        outcome = admit(Lifecycle.EXPERIMENTAL, contract)
        assert outcome.ok
        assert outcome.to_state is Lifecycle.CANDIDATE
        assert outcome.gate_held
        assert "gate is not satisfied" in outcome.reason


class TestWithdrawAdmit:
    def test_withdraws_from_active_tier(self) -> None:
        outcome = withdraw_admit(Lifecycle.EXPLORATORY)
        assert outcome.ok
        assert outcome.to_state is Lifecycle.EXPERIMENTAL

    def test_rejects_from_experimental(self) -> None:
        outcome = withdraw_admit(Lifecycle.EXPERIMENTAL)
        assert not outcome.ok


class TestReloadTransition:
    def test_no_contract_goes_invalid(self) -> None:
        outcome = reload_transition(Lifecycle.EXPLORATORY, None, INCOMPATIBLE)
        assert outcome.ok
        assert outcome.to_state is Lifecycle.INVALID

    def test_incompatible_goes_invalid(self) -> None:
        contract = parse_contract(make_contract_dict())
        outcome = reload_transition(Lifecycle.EXPLORATORY, contract, INCOMPATIBLE)
        assert outcome.to_state is Lifecycle.INVALID

    def test_reloaded_contract_status_now_invalid(self) -> None:
        contract = parse_contract(make_contract_dict(status="INVALID"))
        outcome = reload_transition(Lifecycle.EXPERIMENTAL, contract, COMPATIBLE)
        assert outcome.ok
        assert outcome.to_state is Lifecycle.INVALID
        assert "status=INVALID" in outcome.reason

    def test_now_not_implemented(self) -> None:
        contract = parse_contract(make_contract_dict(status="NOT_IMPLEMENTED"))
        outcome = reload_transition(Lifecycle.EXPERIMENTAL, contract, COMPATIBLE)
        assert outcome.to_state is Lifecycle.NOT_IMPLEMENTED

    def test_not_implemented_checked_before_compatibility(self) -> None:
        # A stub's required_data may not yet be satisfiable by the Scanner -- that must still
        # resolve to NOT_IMPLEMENTED, not a misleading INVALID/INCOMPATIBLE (matches
        # initial_lifecycle()'s check order exactly: NOT_IMPLEMENTED status wins regardless).
        contract = parse_contract(make_contract_dict(status="NOT_IMPLEMENTED"))
        outcome = reload_transition(Lifecycle.NOT_IMPLEMENTED, contract, INCOMPATIBLE)
        assert outcome.to_state is Lifecycle.NOT_IMPLEMENTED

    def test_disabled_is_never_cleared_by_reload(self) -> None:
        # DISABLED is an operator kill-switch overlay -- an unrelated content reload (even one that
        # raises maturity or would otherwise change the tier) must never silently clear it. Only
        # enable() (T11) may.
        contract = parse_contract(make_contract_dict(maturity="CANDIDATE"))
        outcome = reload_transition(Lifecycle.DISABLED, contract, COMPATIBLE)
        assert outcome.ok
        assert outcome.to_state is Lifecycle.DISABLED

    def test_disabled_stays_disabled_even_if_new_contract_is_incompatible(self) -> None:
        outcome = reload_transition(Lifecycle.DISABLED, None, INCOMPATIBLE)
        assert outcome.to_state is Lifecycle.DISABLED

    def test_from_experimental_stays_experimental_pending_admission(self) -> None:
        contract = parse_contract(make_contract_dict(maturity="CANDIDATE"))
        outcome = reload_transition(Lifecycle.EXPERIMENTAL, contract, COMPATIBLE)
        assert outcome.to_state is Lifecycle.EXPERIMENTAL

    def test_from_invalid_recovers_via_reload(self) -> None:
        contract = parse_contract(make_contract_dict())
        outcome = reload_transition(Lifecycle.INVALID, contract, COMPATIBLE)
        assert outcome.to_state is Lifecycle.EXPERIMENTAL

    def test_raises_maturity_when_active(self) -> None:
        contract = parse_contract(make_contract_dict(maturity="CANDIDATE"))
        outcome = reload_transition(Lifecycle.EXPLORATORY, contract, COMPATIBLE)
        assert outcome.to_state is Lifecycle.CANDIDATE
        assert "raised" in outcome.reason

    def test_lowers_maturity_when_active(self) -> None:
        contract = parse_contract(make_contract_dict(maturity="EXPLORATORY"))
        outcome = reload_transition(Lifecycle.CANDIDATE, contract, COMPATIBLE)
        assert outcome.to_state is Lifecycle.EXPLORATORY
        assert "lowered" not in outcome.reason  # only used for the non-activatable-target branch's own text

    def test_unchanged_maturity_when_active(self) -> None:
        contract = parse_contract(make_contract_dict(maturity="EXPLORATORY"))
        outcome = reload_transition(Lifecycle.EXPLORATORY, contract, COMPATIBLE)
        assert outcome.to_state is Lifecycle.EXPLORATORY
        assert "unchanged" in outcome.reason

    def test_active_becomes_retired_on_reload(self) -> None:
        contract = parse_contract(make_contract_dict(maturity="RETIRED"))
        outcome = reload_transition(Lifecycle.EXPLORATORY, contract, COMPATIBLE)
        assert outcome.to_state is Lifecycle.RETIRED
        assert "no longer active" in outcome.reason


class TestDisable:
    def test_disables_from_experimental(self) -> None:
        outcome = disable(Lifecycle.EXPERIMENTAL)
        assert outcome.ok
        assert outcome.to_state is Lifecycle.DISABLED

    def test_disables_from_active_tier(self) -> None:
        outcome = disable(Lifecycle.PROMOTED)
        assert outcome.ok
        assert outcome.to_state is Lifecycle.DISABLED

    def test_rejects_from_invalid(self) -> None:
        outcome = disable(Lifecycle.INVALID)
        assert not outcome.ok

    def test_rejects_from_retired(self) -> None:
        outcome = disable(Lifecycle.RETIRED)
        assert not outcome.ok

    def test_rejects_from_not_implemented(self) -> None:
        outcome = disable(Lifecycle.NOT_IMPLEMENTED)
        assert not outcome.ok


class TestEnable:
    def test_restores_prior_state(self) -> None:
        contract = parse_contract(make_contract_dict())
        outcome = enable(Lifecycle.DISABLED, Lifecycle.EXPLORATORY, contract, COMPATIBLE)
        assert outcome.ok
        assert outcome.to_state is Lifecycle.EXPLORATORY

    def test_no_prior_state_falls_back_to_experimental(self) -> None:
        contract = parse_contract(make_contract_dict())
        outcome = enable(Lifecycle.DISABLED, None, contract, COMPATIBLE)
        assert outcome.to_state is Lifecycle.EXPERIMENTAL

    def test_rejects_from_non_disabled(self) -> None:
        contract = parse_contract(make_contract_dict())
        outcome = enable(Lifecycle.EXPERIMENTAL, None, contract, COMPATIBLE)
        assert not outcome.ok

    def test_rejects_if_no_longer_compatible(self) -> None:
        outcome = enable(Lifecycle.DISABLED, Lifecycle.EXPLORATORY, None, INCOMPATIBLE)
        assert not outcome.ok

    def test_rejects_if_no_longer_valid_contract(self) -> None:
        outcome = enable(Lifecycle.DISABLED, Lifecycle.EXPLORATORY, None, COMPATIBLE)
        assert not outcome.ok


class TestRetire:
    def test_retires_from_active(self) -> None:
        outcome = retire(Lifecycle.PROMOTED)
        assert outcome.ok
        assert outcome.to_state is Lifecycle.RETIRED

    def test_idempotent_on_already_retired(self) -> None:
        outcome = retire(Lifecycle.RETIRED)
        assert outcome.ok
        assert outcome.to_state is Lifecycle.RETIRED
        assert "idempotent" in outcome.reason

    def test_retires_from_not_implemented(self) -> None:
        # T12's transition table says "from: any" -- an operator must be able to permanently
        # withdraw a stub/broken strategy, not leave it stuck in limbo forever.
        outcome = retire(Lifecycle.NOT_IMPLEMENTED)
        assert outcome.ok
        assert outcome.to_state is Lifecycle.RETIRED

    def test_retires_from_invalid(self) -> None:
        outcome = retire(Lifecycle.INVALID)
        assert outcome.ok
        assert outcome.to_state is Lifecycle.RETIRED

    def test_retires_from_disabled(self) -> None:
        outcome = retire(Lifecycle.DISABLED)
        assert outcome.ok
        assert outcome.to_state is Lifecycle.RETIRED


class TestIsHealthIncompatibleBucket:
    def test_returns_incompatible_when_invalid_due_to_compat_failure(self) -> None:
        assert is_health_incompatible_bucket(Lifecycle.INVALID, True, False) is Health.INCOMPATIBLE

    def test_returns_none_when_schema_invalid(self) -> None:
        assert is_health_incompatible_bucket(Lifecycle.INVALID, False, False) is None

    def test_returns_none_when_not_invalid(self) -> None:
        assert is_health_incompatible_bucket(Lifecycle.EXPERIMENTAL, True, True) is None
