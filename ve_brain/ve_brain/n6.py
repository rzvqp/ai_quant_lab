"""NODUL DE DECIZIE N6 — poarta finală. REVALIDEAZĂ contra REGISTRULUI CANONIC (VE_HANDOFF_CONDITIONAL).

Defectul închis (a 4-a instanță a tiparului): EligibilityDecision + StrategyCandidate pot fi construite MANUAL cu
ID-uri POTRIVITE, is_eligible=TRUE, reason_codes=ROUTER_ELIGIBLE. Un bool `requires_true_range` ar fi la rândul lui
falsificabil. Remediul: proprietatea strategiei se rezolvă din `StrategyRegistry` controlat de artefactul VE; N6
citește `requires_true_range` DIN REGISTRU și aplică blocajul de range INDEPENDENT de reason_codes/is_eligible/EV.
Câmpurile copiate în candidat/eligibilitate sunt pentru AUDIT, NU autoritative.

ORDINEA: StrategyRegistry (definiție canonică) → N1 → Router → EligibilityDecision → StrategyCandidate → EV → N6
REVALIDEAZĂ contra registrului → Risk Manager. N6 NU tratează `eligibility.reason_codes` ca sursă de adevăr pentru
dependența de range.
"""

from __future__ import annotations

from . import _ev_core
from .contracts import (DecisionRequest, DecisionResponse, OUTPUT_CONTRACT_ID, SchemaValidationError,
                        validate_request)
from .ev_engine import ENGINE_VERSION, run_ev
from .fingerprint import data_identity, decision_fingerprint
from .reason_codes import ReasonCode
from .regime_routing import (EligibilityDecision, StrategyRegistry, requires_true_range,
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


# ── REGISTRUL CANONIC e INTERN artefactului VE — NU un parametru al consumatorului. Auto-atac (a 4-a instanță a
# tiparului + addendum CEO): dacă N6 ar primi `registry` ca parametru, consumatorul ar injecta UN REGISTRU FALS
# (range înregistrat ca trend ⇒ requires_true_range=False ⇒ TRADE). Închis: `decide_n6` NU ia registrul; îl citește
# din singleton-ul intern, populat DOAR prin API-ul controlat `register_canonical_strategy`. Suprafața PUBLICĂ nu
# poate injecta un registru fals. (Monkeypatch-ul globalelor private e în afara contractului — orice bibliotecă e
# monkeypatch-abilă; consumatorul s-ar sabota singur, nu ocolește API-ul.) ──
_CANONICAL_REGISTRY: StrategyRegistry = StrategyRegistry()
_REGISTRY_AVAILABLE: bool = True


def register_canonical_strategy(contract: object) -> None:
    """UNICA cale de populare a registrului canonic (controlată de VE). Imuabilă per (id, version)."""
    from .regime_routing import StrategyContract as _SC
    assert isinstance(contract, _SC)
    _CANONICAL_REGISTRY.register(contract)


def reset_canonical_registry() -> None:
    """Doar pentru teste/reîncărcare controlată."""
    global _CANONICAL_REGISTRY, _REGISTRY_AVAILABLE
    _CANONICAL_REGISTRY = StrategyRegistry()
    _REGISTRY_AVAILABLE = True


def set_registry_available(flag: bool) -> None:
    """Injectare de fault (registry indisponibil) — fail-closed."""
    global _REGISTRY_AVAILABLE
    _REGISTRY_AVAILABLE = flag


def decide_n6(candidate: DecisionRequest, eligibility: EligibilityDecision | None) -> DecisionResponse:
    """Poarta N6. Registrul canonic e INTERN (nu parametru). `eligibility` = OBLIGATORIE (de la Router). Determinist."""
    fp = _fingerprint(candidate)

    # 0) contractul N1 — consumatorul care nu înțelege axele brute eșuează EXPLICIT
    if candidate.n1_contract_version != N1_CONTRACT_VERSION:
        return _response(candidate, "NO_TRADE", ReasonCode.INCOMPATIBLE_N1_CONTRACT, fp)

    # 1) schema
    try:
        validate_request(candidate)
    except SchemaValidationError:
        return _response(candidate, "NO_TRADE", ReasonCode.SCHEMA_VALIDATION_FAILED, fp)

    # 2) REGISTRUL CANONIC INTERN — fail-closed dacă e indisponibil
    if not _REGISTRY_AVAILABLE:
        return _response(candidate, "NO_TRADE", ReasonCode.STRATEGY_REGISTRY_UNAVAILABLE, fp)
    # 3) rezolvă strategia (id, version); absentă ⇒ UNKNOWN_STRATEGY
    canon = _CANONICAL_REGISTRY.resolve(candidate.strategy_id, candidate.strategy_version)
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
