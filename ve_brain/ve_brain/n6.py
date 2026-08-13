"""NODUL DE DECIZIE N6 — poarta finală. REVALIDEAZĂ contra CATALOGULUI CANONIC INTERN SIGILAT.

Defectul închis (tiparul, a 4-a→6-a instanță): (4) EligibilityDecision + candidat construite manual cu ID-uri
potrivite; (5) registrul pasat ca parametru injectabil; (6) registrul definit de consumator (register public + gol +
primul câștigă) ⇒ range_fade înregistrat ca trend ⇒ requires_true_range=False ⇒ TRADE. Un bool ar fi falsificabil,
un registru parametrizat ar fi injectabil, un registru populabil de consumator ar fi otrăvibil. Remediul final:
catalogul canonic e ÎNCORPORAT în artefact (literali, fără sursă externă), SIGILAT la import, VERSIONAT + cu amprentă
de integritate. N6 rezolvă proprietatea de aici, citește `requires_true_range` DIN CATALOG și aplică blocajul de range
INDEPENDENT de reason_codes/is_eligible/EV; REFUZĂ un catalog nesigilat sau cu versiune/amprentă nepotrivită. Câmpurile
copiate în candidat/eligibilitate sunt pentru AUDIT, NU autoritative.

ORDINEA: catalog SIGILAT (definiție canonică) → N1 → Router → EligibilityDecision → candidat → EV → N6 REVALIDEAZĂ
contra catalogului → Risk Manager. Consumatorul poate CERE încărcarea unei strategii aprobate; nu poate defini
conținutul ei.
"""

from __future__ import annotations

from . import _ev_core
from .contracts import (DecisionRequest, DecisionResponse, OUTPUT_CONTRACT_ID, SchemaValidationError,
                        validate_request)
from .ev_engine import ENGINE_VERSION, run_ev
from .fingerprint import data_identity, decision_fingerprint
from .reason_codes import ReasonCode
from ._canonical_catalog import CANONICAL_CATALOG_HASH, CANONICAL_CATALOG_VERSION, build_sealed_catalog
from .regime_routing import (EligibilityDecision, SealedRegistry, requires_true_range,
                            strategy_policy_fingerprint)
from .strategy_contract import can_execute_real, can_reach_n6
from .version import N1_CONTRACT_VERSION, ROUTER_VERSION

_EV_REASON_MAP: dict[str, ReasonCode] = {
    _ev_core.Reason.NO_TRADE_EV_LCB.value: ReasonCode.NEGATIVE_EXPECTED_VALUE,
    _ev_core.Reason.NO_TRADE_FEASIBILITY.value: ReasonCode.NEGATIVE_EXPECTED_VALUE,
    _ev_core.Reason.NO_TRADE_MISSING.value: ReasonCode.MISSING_PROBABILITY_INPUTS,
}


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


def _eligibility_matches(candidate: DecisionRequest, elig: EligibilityDecision) -> bool:
    return (elig.strategy_id == candidate.strategy_id and elig.strategy_version == candidate.strategy_version
            and elig.market_event_id == candidate.market_event_id
            and elig.regime_fingerprint == candidate.regime_fingerprint
            and elig.router_version == ROUTER_VERSION and elig.eligible is True)


# ── CATALOGUL CANONIC e INTERN, ÎNCORPORAT și SIGILAT — NU un parametru, NU populabil de consumator. Auto-atac (a
# 6-a suprafață, verdict Red Team): dacă proprietatea se citește din registru dar CONȚINUTUL registrului e definit de
# consumator (register public + registru gol + primul care înregistrează câștigă), atunci consumatorul înregistrează
# range_fade ca TREND ⇒ requires_true_range=False, candidatul oglindește politica otrăvită ⇒ niciun mismatch ⇒ TRADE.
# Închis: catalogul e ÎNCORPORAT (literali Python, fără sursă externă), construit și SIGILAT la import; N6 REFUZĂ un
# registru nesigilat sau cu versiune/amprentă nepotrivită cu cea APROBATĂ. API-ul de definire arbitrară nu mai există
# pe suprafața de producție — hook-urile de test sunt izolate în `ve_brain.testing`, blocate până la un unlock explicit.
# (Monkeypatch-ul globalelor private rămâne în afara contractului — orice bibliotecă e monkeypatch-abilă.) ──
_SEALED_CATALOG: SealedRegistry = build_sealed_catalog()
_APPROVED_CATALOG_VERSION: str = CANONICAL_CATALOG_VERSION
_APPROVED_CATALOG_HASH: str = CANONICAL_CATALOG_HASH


def decide_n6(candidate: DecisionRequest, eligibility: EligibilityDecision | None) -> DecisionResponse:
    """Poarta N6. Catalogul canonic e INTERN + SIGILAT (nu parametru, nu populabil). `eligibility` = OBLIGATORIE."""
    fp = _fingerprint(candidate)

    # 0) contractul N1 — consumatorul care nu înțelege axele brute eșuează EXPLICIT
    if candidate.n1_contract_version != N1_CONTRACT_VERSION:
        return _response(candidate, "NO_TRADE", ReasonCode.INCOMPATIBLE_N1_CONTRACT, fp)

    # 1) schema
    try:
        validate_request(candidate)
    except SchemaValidationError:
        return _response(candidate, "NO_TRADE", ReasonCode.SCHEMA_VALIDATION_FAILED, fp)

    # 2) CATALOGUL CANONIC — REFUZĂ un registru nesigilat sau cu versiune/amprentă nepotrivită (fail-closed)
    if not _SEALED_CATALOG.sealed:
        return _response(candidate, "NO_TRADE", ReasonCode.CATALOG_NOT_SEALED, fp)
    if (_SEALED_CATALOG.catalog_version != _APPROVED_CATALOG_VERSION
            or _SEALED_CATALOG.content_hash != _APPROVED_CATALOG_HASH):
        return _response(candidate, "NO_TRADE", ReasonCode.CATALOG_VERSION_MISMATCH, fp)
    # 3) rezolvă strategia (id, version) DIN CATALOGUL SIGILAT; absentă ⇒ UNKNOWN_STRATEGY
    canon = _SEALED_CATALOG.resolve(candidate.strategy_id, candidate.strategy_version)
    if canon is None:
        return _response(candidate, "NO_TRADE", ReasonCode.UNKNOWN_STRATEGY, fp)
    # 4) recalculează + verifică amprenta de politică + metadatele; nepotrivire ⇒ STRATEGY_POLICY_MISMATCH
    canon_fp = strategy_policy_fingerprint(canon)
    if (candidate.strategy_policy_fingerprint != canon_fp
            or candidate.strategy_family != canon.strategy_family
            or candidate.validation_status != canon.validation_status):
        return _response(candidate, "NO_TRADE", ReasonCode.STRATEGY_POLICY_MISMATCH, fp)
    # 5+7) requires_true_range DIN REGISTRU → blocaj INDEPENDENT de reason_codes/is_eligible/EV
    if requires_true_range(canon):
        return _response(candidate, "NO_TRADE", ReasonCode.TRUE_RANGE_NOT_IDENTIFIABLE, fp)

    # 8) abia acum: eligibilitatea (FAIL-1) + statutul CANONIC + intrări + EV
    if eligibility is None or not _eligibility_matches(candidate, eligibility):
        return _response(candidate, "NO_TRADE", ReasonCode.MISSING_OR_INVALID_ELIGIBILITY, fp)
    if not can_reach_n6(canon.validation_status):                 # statut din REGISTRU, nu din candidat
        return _response(candidate, "NO_TRADE", ReasonCode.NO_ELIGIBLE_STRATEGY, fp)
    if candidate.regime_label is None:
        return _response(candidate, "NO_TRADE", ReasonCode.MISSING_LEVEL_INPUT, fp)
    if not (candidate.market_map_available and candidate.levels_available):
        return _response(candidate, "NO_TRADE", ReasonCode.MISSING_LEVEL_INPUT, fp)
    if not candidate.confirmation_available:
        return _response(candidate, "NO_TRADE", ReasonCode.MISSING_CONFIRMATION, fp)
    if candidate.probability_inputs is None:
        return _response(candidate, "NO_TRADE", ReasonCode.MISSING_PROBABILITY_INPUTS, fp)

    ev = run_ev(candidate)
    if not ev.enter:
        return _response(candidate, "NO_TRADE", _EV_REASON_MAP.get(ev.reason, ReasonCode.NEGATIVE_EXPECTED_VALUE), fp, ev)
    if can_execute_real(canon.validation_status):
        return _response(candidate, "TRADE", ReasonCode.TRADE_VALIDATED_EDGE, fp, ev)
    return _response(candidate, "SHADOW_TRADE_CANDIDATE", ReasonCode.SHADOW_CANDIDATE_EV_POSITIVE, fp, ev)
