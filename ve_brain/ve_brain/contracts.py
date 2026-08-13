"""CONTRACTE VERSIONATE — scheme de input și output pentru nodul de decizie N6, VALIDATE la runtime.
Fiecare cerere/răspuns poartă versiune + configuration_fingerprint + reason_codes. Nepotrivire de schemă ⇒ eroare
EXPLICITĂ (SCHEMA_VALIDATION_FAILED), niciodată un default ascuns.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .reason_codes import ReasonCode
from .strategy_contract import ValidationStatus

INPUT_CONTRACT_ID: str = "ve.decision_request.v1"
OUTPUT_CONTRACT_ID: str = "ve.decision_response.v1"


# ── intrările de probabilitate: tabelul de conteo empiric-Bayes al motorului EV (nu se inventează) ──
@dataclass(frozen=True)
class OutcomeCell:
    """Conteoul unei celule (nod × nivel), din REZULTATE ISTORICE ale strategiei validate. NU se fabrică."""
    n: int
    n_target: int          # ieșiri la ȚINTĂ
    n_horizon: int         # ieșiri pe ORIZONT (time-stop)
    sum_horizon_R: float   # suma cu semn a R pe ieșirile de orizont (E[X|h] = sum / n_horizon)


@dataclass(frozen=True)
class HierarchyLevel:
    cell: OutcomeCell
    siblings: tuple[OutcomeCell, ...] = ()


@dataclass(frozen=True)
class ProbabilityInputs:
    """Ierarhia de conteo (global → celulă) + nivelul de credibilitate. Absentă ⇒ NO_TRADE (nu se inventează)."""
    hierarchy: tuple[HierarchyLevel, ...]
    credibility: float = 0.80


# ── INPUT MINIM (cererea de decizie) ──
@dataclass(frozen=True)
class DecisionRequest:
    """StrategyCandidate — construit DUPĂ Router (N1→Router→EligibilityDecision→StrategyCandidate). Poartă
    market_event_id + regime_fingerprint pe care N6 le verifică contra EligibilityDecision."""
    contract_id: str
    strategy_id: str
    strategy_version: str
    validation_status: ValidationStatus
    market_event_id: str                   # FAIL-1: identitatea evenimentului de piață (bara)
    regime_fingerprint: str                # FAIL-1: amprenta regimului curent (din axele brute)
    # starea pieței + nivelele TURNULUI (rezumate; valorile brute rămân în market_state opac pentru audit)
    market_state_ref: str
    regime_label: str | None
    bias_direction: str | None
    market_map_available: bool
    levels_available: bool
    confirmation_available: bool
    # geometria tranzacției
    entry_price: float
    stop_price: float
    target_kind: str
    target_param: float | None
    holding_window: int
    atr: float
    probability_inputs: ProbabilityInputs | None
    full_spread_price: float
    entry_slippage_price: float
    exit_slippage_price: float
    # identitatea DATELOR (A5) — populația oficială = 4 blocuri
    symbol: str
    timeframe: str
    block_start: int
    block_end: int
    segment_id: str
    manifest_hash: str
    # versiuni de contract/politici (FAIL-2 + fingerprint)
    n1_contract_version: str
    raw_axis_schema_version: str
    router_version: str
    eligibility_policy_version: str
    measurement_contract_version: str
    configuration_fingerprint: str


# ── OUTPUT MINIM (răspunsul de decizie) ──
@dataclass(frozen=True)
class DecisionResponse:
    contract_id: str
    decision: str                          # "TRADE" | "NO_TRADE"
    expected_value_net: float | None       # EV_net (LCB), gata gardat de cost
    expected_reward: float | None          # p_t · RR
    expected_loss: float | None            # p_s · 1 (+ gap dacă e cazul)
    estimated_cost: float | None           # c/R
    probability_assumptions: dict[str, Any]  # p_t, p_h, e_x_h, credibility, k_per_level, table_hash
    strategy_id: str
    configuration_fingerprint: str
    reason_codes: tuple[str, ...]
    engine_version: str


# ── validare la RUNTIME ──
class SchemaValidationError(ValueError):
    """Ridicată când cererea/răspunsul nu respectă schema. Reason: SCHEMA_VALIDATION_FAILED."""


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise SchemaValidationError(msg)


def validate_request(req: DecisionRequest) -> None:
    """Validează schema cererii. Eroare EXPLICITĂ pe nepotrivire — niciun default ascuns."""
    _require(req.contract_id == INPUT_CONTRACT_ID, f"contract_id {req.contract_id!r} != {INPUT_CONTRACT_ID!r}")
    _require(bool(req.strategy_id) and bool(req.strategy_version), "strategy_id/version goale")
    _require(isinstance(req.validation_status, ValidationStatus), "validation_status nu e ValidationStatus")
    _require(req.target_kind in ("rr", "price", "none"), f"target_kind invalid: {req.target_kind!r}")
    for name, v in (("entry_price", req.entry_price), ("stop_price", req.stop_price), ("atr", req.atr),
                    ("full_spread_price", req.full_spread_price), ("entry_slippage_price", req.entry_slippage_price),
                    ("exit_slippage_price", req.exit_slippage_price)):
        _require(isinstance(v, (int, float)) and v == v, f"{name} nefinit/absent")
    _require(req.atr > 0.0, "atr trebuie > 0")
    _require(req.holding_window >= 1, "holding_window >= 1")
    _require(bool(req.measurement_contract_version) and bool(req.configuration_fingerprint),
             "measurement_contract_version / configuration_fingerprint goale")
    _require(bool(req.market_event_id) and bool(req.regime_fingerprint), "market_event_id / regime_fingerprint goale")
    _require(bool(req.symbol) and bool(req.timeframe) and bool(req.segment_id) and bool(req.manifest_hash),
             "identitatea datelor incompletă (symbol/timeframe/segment_id/manifest_hash)")
    _require(req.block_start <= req.block_end, "block_start > block_end")
    _require(all((req.n1_contract_version, req.raw_axis_schema_version, req.router_version,
                  req.eligibility_policy_version)), "versiuni de contract/politici goale")
    if req.probability_inputs is not None:
        pi = req.probability_inputs
        _require(len(pi.hierarchy) >= 1, "ierarhia de probabilitate e goală")
        _require(0.0 < pi.credibility < 1.0, "credibility trebuie în (0,1)")
        _require(pi.hierarchy[0].cell.n >= 0, "n global negativ")


def validate_response(resp: DecisionResponse) -> None:
    _require(resp.contract_id == OUTPUT_CONTRACT_ID, f"contract_id {resp.contract_id!r} != {OUTPUT_CONTRACT_ID!r}")
    _require(resp.decision in ("TRADE", "SHADOW_TRADE_CANDIDATE", "NO_TRADE"),   # A1: shadow candidate distinct de trade real
             f"decision invalid: {resp.decision!r}")
    _require(len(resp.reason_codes) >= 1, "reason_codes gol")
    valid = {rc.value for rc in ReasonCode}
    for rc in resp.reason_codes:
        _require(rc in valid, f"reason_code necunoscut: {rc!r}")
