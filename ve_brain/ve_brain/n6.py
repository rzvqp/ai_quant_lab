"""NODUL DE DECIZIE N6 — poarta finală. Consumă un StrategyCandidate + o EligibilityDecision OBLIGATORIE emisă de
Router (FAIL-1). Rulează MOTORUL EV REAL (nu edge=bool). Emite TRADE / SHADOW_TRADE_CANDIDATE / NO_TRADE.

ORDINEA OBLIGATORIE: N1 axe → StrategyRouter → EligibilityDecision → StrategyCandidate → EV Engine → N6 → Risk Manager.
Nicio cale nu poate sări peste Router. N6 NU recalculează local eligibilitatea și NU duplică regulile Routerului.

CONDIȚII CUMULATIVE pentru TRADE: strategie VALIDATĂ (RATIFIED/PROMOTED) AND eligibilă în STAREA CURENTĂ (verificat
contra EligibilityDecision) AND EV acceptabil. RATIFIED NU înlocuiește eligibilitatea de regim.
"""

from __future__ import annotations

from . import _ev_core
from .contracts import (DecisionRequest, DecisionResponse, OUTPUT_CONTRACT_ID, SchemaValidationError,
                        validate_request)
from .ev_engine import ENGINE_VERSION, run_ev
from .fingerprint import data_identity, decision_fingerprint
from .reason_codes import ReasonCode
from .regime_routing import EligibilityDecision
from .strategy_contract import can_execute_real, can_reach_n6, ValidationStatus
from .version import N1_CONTRACT_VERSION, ROUTER_VERSION

_EV_REASON_MAP: dict[str, ReasonCode] = {
    _ev_core.Reason.NO_TRADE_EV_LCB.value: ReasonCode.NEGATIVE_EXPECTED_VALUE,
    _ev_core.Reason.NO_TRADE_FEASIBILITY.value: ReasonCode.NEGATIVE_EXPECTED_VALUE,
    _ev_core.Reason.NO_TRADE_MISSING.value: ReasonCode.MISSING_PROBABILITY_INPUTS,
}
_RANGE_REASON = ReasonCode.TRUE_RANGE_NOT_IDENTIFIABLE.value


def _fingerprint(req: DecisionRequest) -> str:
    did = data_identity(symbol=req.symbol, timeframe=req.timeframe, block_start=req.block_start,
                        block_end=req.block_end, segment_id=req.segment_id, manifest_hash=req.manifest_hash)
    return decision_fingerprint(
        measurement_run_hash=req.configuration_fingerprint, data_id=did, strategy_id=req.strategy_id,
        strategy_version=req.strategy_version, engine_version=ENGINE_VERSION,
        measurement_contract_version=req.measurement_contract_version, n1_contract_version=req.n1_contract_version,
        raw_axis_schema_version=req.raw_axis_schema_version, router_version=req.router_version,
        eligibility_policy_version=req.eligibility_policy_version)


def _response(req: DecisionRequest, decision: str, reason: ReasonCode, fp: str,
              ev: object | None = None) -> DecisionResponse:
    return DecisionResponse(
        contract_id=OUTPUT_CONTRACT_ID, decision=decision,
        expected_value_net=getattr(ev, "expected_value_net", None), expected_reward=getattr(ev, "expected_reward", None),
        expected_loss=getattr(ev, "expected_loss", None), estimated_cost=getattr(ev, "estimated_cost", None),
        probability_assumptions=dict(getattr(ev, "probability_assumptions", {})), strategy_id=req.strategy_id,
        configuration_fingerprint=fp, reason_codes=(reason.value,), engine_version=ENGINE_VERSION)


def _eligibility_valid(candidate: DecisionRequest, elig: EligibilityDecision) -> bool:
    """FAIL-1: identitatea EligibilityDecision trebuie să coincidă cu candidatul + starea curentă."""
    return (elig.strategy_id == candidate.strategy_id
            and elig.strategy_version == candidate.strategy_version
            and elig.market_event_id == candidate.market_event_id
            and elig.regime_fingerprint == candidate.regime_fingerprint
            and elig.router_version == ROUTER_VERSION
            and elig.eligible is True)


def decide_n6(candidate: DecisionRequest, eligibility: EligibilityDecision | None) -> DecisionResponse:
    """Poarta N6. `eligibility` e OBLIGATORIE (emisă de Router). Determinist; niciodată un ordin real."""
    fp = _fingerprint(candidate)

    # 0) contractul N1 — consumatorul care nu înțelege axele brute eșuează EXPLICIT
    if candidate.n1_contract_version != N1_CONTRACT_VERSION:
        return _response(candidate, "NO_TRADE", ReasonCode.INCOMPATIBLE_N1_CONTRACT, fp)

    # 1) schema
    try:
        validate_request(candidate)
    except SchemaValidationError:
        return _response(candidate, "NO_TRADE", ReasonCode.SCHEMA_VALIDATION_FAILED, fp)

    # 2) FAIL-1: EligibilityDecision OBLIGATORIE și potrivită. Lipsă / nepotrivire ⇒ MISSING_OR_INVALID_ELIGIBILITY.
    if eligibility is None:
        return _response(candidate, "NO_TRADE", ReasonCode.MISSING_OR_INVALID_ELIGIBILITY, fp)
    # strategie dependentă de range respinsă de Router ⇒ propagă motivul salient
    if _RANGE_REASON in eligibility.reason_codes:
        return _response(candidate, "NO_TRADE", ReasonCode.TRUE_RANGE_NOT_IDENTIFIABLE, fp)
    if not _eligibility_valid(candidate, eligibility):
        return _response(candidate, "NO_TRADE", ReasonCode.MISSING_OR_INVALID_ELIGIBILITY, fp)

    # 3) statut (A1): poate ajunge la N6/EV?
    if not can_reach_n6(candidate.validation_status):
        return _response(candidate, "NO_TRADE", ReasonCode.NO_ELIGIBLE_STRATEGY, fp)

    # 4) date/nivele necesare
    if candidate.regime_label is None:
        return _response(candidate, "NO_TRADE", ReasonCode.MISSING_LEVEL_INPUT, fp)
    if not (candidate.market_map_available and candidate.levels_available):
        return _response(candidate, "NO_TRADE", ReasonCode.MISSING_LEVEL_INPUT, fp)
    if not candidate.confirmation_available:
        return _response(candidate, "NO_TRADE", ReasonCode.MISSING_CONFIRMATION, fp)

    # 5) probabilități (nu se inventează)
    if candidate.probability_inputs is None:
        return _response(candidate, "NO_TRADE", ReasonCode.MISSING_PROBABILITY_INPUTS, fp)

    # 6) MOTORUL EV REAL
    ev = run_ev(candidate)
    if not ev.enter:
        return _response(candidate, "NO_TRADE", _EV_REASON_MAP.get(ev.reason, ReasonCode.NEGATIVE_EXPECTED_VALUE), fp, ev)

    # 7) EV pozitiv: TRADE real (RATIFIED/PROMOTED) sau SHADOW_TRADE_CANDIDATE (SHADOW_ELIGIBLE) — NU fallback RATIFIED+EV
    if can_execute_real(candidate.validation_status):
        return _response(candidate, "TRADE", ReasonCode.TRADE_VALIDATED_EDGE, fp, ev)
    return _response(candidate, "SHADOW_TRADE_CANDIDATE", ReasonCode.SHADOW_CANDIDATE_EV_POSITIVE, fp, ev)


_ = ValidationStatus  # re-export de compatibilitate
