"""NODUL DE DECIZIE N6 — poarta finală. Consumă rezultatele ACTUALE ale turnului (via `DecisionRequest`), rulează
MOTORUL EV REAL (nu edge=True/False), și emite TRADE / SHADOW_TRADE_CANDIDATE / NO_TRADE cu reason_codes + amprentă.

Reguli (amendamente CEO incluse):
  · schema invalidă / contract incompatibil / date lipsă / probabilități lipsă / strategie neeligibilă ⇒ NO_TRADE
    DETERMINIST, cu reason_code. NU se inventează probabilități, NU se folosesc valori implicite ascunse.
  · A1: SHADOW_ELIGIBLE ajunge la EV → poate produce SHADOW_TRADE_CANDIDATE (fără ordin real); DOAR RATIFIED/PROMOTED
    produc TRADE real. NO_ELIGIBLE_STRATEGY doar dacă nicio strategie nu e eligibilă nici pentru shadow.
  · A5: fiecare răspuns poartă `configuration_fingerprint` peste date‖config‖strategie‖motor‖contract.
"""

from __future__ import annotations

from . import _ev_core
from .contracts import (DecisionRequest, DecisionResponse, OUTPUT_CONTRACT_ID, SchemaValidationError,
                        validate_request)
from .ev_engine import ENGINE_VERSION, run_ev
from .fingerprint import decision_fingerprint
from .reason_codes import ReasonCode
from .strategy_contract import can_execute_real, can_reach_n6

# _ev_core.Reason.value → ReasonCode (mapare stabilă)
_EV_REASON_MAP: dict[str, ReasonCode] = {
    _ev_core.Reason.NO_TRADE_EV_LCB.value: ReasonCode.NEGATIVE_EXPECTED_VALUE,
    _ev_core.Reason.NO_TRADE_FEASIBILITY.value: ReasonCode.NEGATIVE_EXPECTED_VALUE,
    _ev_core.Reason.NO_TRADE_MISSING.value: ReasonCode.MISSING_PROBABILITY_INPUTS,
}


def _fingerprint(req: DecisionRequest) -> str:
    return decision_fingerprint(
        measurement_run_hash=req.configuration_fingerprint, strategy_id=req.strategy_id,
        strategy_version=req.strategy_version, engine_version=ENGINE_VERSION,
        measurement_contract_version=req.measurement_contract_version)


def _response(req: DecisionRequest, decision: str, reason: ReasonCode, fp: str,
              ev: object | None = None) -> DecisionResponse:
    ev_net = getattr(ev, "expected_value_net", None)
    reward = getattr(ev, "expected_reward", None)
    loss = getattr(ev, "expected_loss", None)
    cost = getattr(ev, "estimated_cost", None)
    probs = getattr(ev, "probability_assumptions", {})
    return DecisionResponse(
        contract_id=OUTPUT_CONTRACT_ID, decision=decision, expected_value_net=ev_net, expected_reward=reward,
        expected_loss=loss, estimated_cost=cost, probability_assumptions=dict(probs), strategy_id=req.strategy_id,
        configuration_fingerprint=fp, reason_codes=(reason.value,), engine_version=ENGINE_VERSION)


def decide_n6(req: DecisionRequest) -> DecisionResponse:
    """Poarta N6. Determinist; fără efecte laterale; niciodată un ordin real."""
    fp = _fingerprint(req)

    # 1) schema (eroare EXPLICITĂ, nu default ascuns)
    try:
        validate_request(req)
    except SchemaValidationError:
        return _response(req, "NO_TRADE", ReasonCode.SCHEMA_VALIDATION_FAILED, fp)

    # 2) eligibilitate (A1): dacă strategia nu poate ajunge la N6 nici pentru shadow ⇒ NO_TRADE
    if not can_reach_n6(req.validation_status):
        return _response(req, "NO_TRADE", ReasonCode.NO_ELIGIBLE_STRATEGY, fp)

    # 3) date/nivele necesare din turn — lipsă ⇒ NO_TRADE cu cod specific
    if req.regime_label is None:
        return _response(req, "NO_TRADE", ReasonCode.MISSING_LEVEL_INPUT, fp)
    if not (req.market_map_available and req.levels_available):
        return _response(req, "NO_TRADE", ReasonCode.MISSING_LEVEL_INPUT, fp)
    if not req.confirmation_available:
        return _response(req, "NO_TRADE", ReasonCode.MISSING_CONFIRMATION, fp)

    # 4) probabilități — absente ⇒ NO_TRADE (NU se inventează)
    if req.probability_inputs is None:
        return _response(req, "NO_TRADE", ReasonCode.MISSING_PROBABILITY_INPUTS, fp)

    # 5) MOTORUL EV REAL (nu edge=bool)
    ev = run_ev(req)
    if not ev.enter:
        rc = _EV_REASON_MAP.get(ev.reason, ReasonCode.NEGATIVE_EXPECTED_VALUE)
        return _response(req, "NO_TRADE", rc, fp, ev)

    # 6) EV pozitiv: TRADE real (RATIFIED/PROMOTED) sau SHADOW_TRADE_CANDIDATE (SHADOW_ELIGIBLE)
    if can_execute_real(req.validation_status):
        return _response(req, "TRADE", ReasonCode.TRADE_VALIDATED_EDGE, fp, ev)
    return _response(req, "SHADOW_TRADE_CANDIDATE", ReasonCode.SHADOW_CANDIDATE_EV_POSITIVE, fp, ev)
