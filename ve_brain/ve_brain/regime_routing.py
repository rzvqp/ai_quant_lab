"""REGIME-CONDITIONAL STRATEGY ROUTING — corectat pentru VE_HANDOFF_FAIL (FAIL-1 + FAIL-2).

FAIL-2: axa de volatilitate ca UN SINGUR STRING făcea COMPRESSION (vol==compressed) și BREAKOUT_TRANSITION
(vol==high_directional) MUTUAL EXCLUSIVE — partiția s-a MUTAT din expansion.py în axa N1, nu a fost eliminată.
CORECȚIA: contractul N1 expune ADITIV axe INDEPENDENTE — `is_compressed` (context acumulat) și `is_displacement`
(eveniment curent), NEmutual-exclusive. `volatility_state` rămâne DOAR pentru compatibilitate/telemetrie; Routerul
NU-l poate folosi ca unică sursă. Nu redefinesc sensurile istorice ale enumurilor.

Router citește axele INDEPENDENTE: is_compressed · is_displacement · direction · structure(strength/readiness).
MULTI-AXIAL: mulțime, nu etichetă unică. RANGE rămâne RETRAS (decizie CEO): NICIODATĂ produs; strategiile care cer
RANGE ⇒ fail-closed TRUE_RANGE_NOT_IDENTIFIABLE. BREAKOUT_TRANSITION cheiat pe `is_displacement` + flip proaspăt
(structure==range) = INSTABILITATE, NU consolidare (utilizare semantic diferită de RANGE-ul interzis).

FAIL-1: `EligibilityDecision` poartă IDENTITATEA completă (strategy_id, strategy_version, market_event_id,
regime_fingerprint, router_version, is_eligible). N6 o cere OBLIGATORIU și o verifică; fără ea = MISSING_OR_INVALID.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum

from .reason_codes import ReasonCode
from .strategy_contract import ValidationStatus, can_reach_n6, can_execute_real
from .version import N1_CONTRACT_VERSION, RAW_AXIS_SCHEMA_VERSION, ROUTER_VERSION


class SemanticRegime(Enum):
    TREND_UP = "TREND_UP"
    TREND_DOWN = "TREND_DOWN"
    RANGE = "RANGE"                  # NEIDENTIFICABIL — valoare de enum pt. declarații, NICIODATĂ produsă
    COMPRESSION = "COMPRESSION"
    BREAKOUT_TRANSITION = "BREAKOUT_TRANSITION"
    UNCERTAIN = "UNCERTAIN"


_STRUCT_RANGE = "range"
_STRUCT_TREND = frozenset({"weak", "strong"})
_DIR_UP = frozenset({"up", "weak_up"})
_DIR_DOWN = frozenset({"down", "weak_down"})


@dataclass(frozen=True)
class RawAxes:
    """Contractul N1 ADITIV, VERSIONAT (FAIL-2). Axe INDEPENDENTE — `is_compressed` și `is_displacement` NU sunt
    mutual exclusive. `volatility_state` = rezumat pt. compat/telemetrie, INTERZIS ca unică sursă de eligibilitate."""
    is_compressed: bool | None
    is_displacement: bool | None
    direction: str | None            # down|weak_down|neutral|weak_up|up
    structure: str | None            # none|range(|run|=1)|weak|strong  (strength/readiness)
    volatility_state: str = "unknown"   # rezumat (compressed|expanding|...) — NU pt. eligibilitate
    n1_contract_version: str = N1_CONTRACT_VERSION
    raw_axis_schema_version: str = RAW_AXIS_SCHEMA_VERSION


def applicable_regimes(axes: RawAxes) -> frozenset[SemanticRegime]:
    """MULTI-AXIAL din axele INDEPENDENTE (nu din stringul de volatilitate). NICIODATĂ RANGE. Pură, per-bară."""
    if axes.is_compressed is None or axes.is_displacement is None or axes.direction is None or axes.structure is None:
        return frozenset({SemanticRegime.UNCERTAIN})
    out: set[SemanticRegime] = set()
    if axes.is_compressed:                                   # COMPRESSION din is_compressed, NU din vol==compressed
        out.add(SemanticRegime.COMPRESSION)
    if axes.is_displacement and axes.structure == _STRUCT_RANGE:   # displacement event + flip proaspăt = ruptură
        out.add(SemanticRegime.BREAKOUT_TRANSITION)
    if axes.structure in _STRUCT_TREND:
        if axes.direction in _DIR_UP:
            out.add(SemanticRegime.TREND_UP)
        if axes.direction in _DIR_DOWN:
            out.add(SemanticRegime.TREND_DOWN)
    return frozenset(out) if out else frozenset({SemanticRegime.UNCERTAIN})


def regime_fingerprint(axes: RawAxes) -> str:
    """Amprenta stării de regim a evenimentului curent (din axele brute + versiunile de contract)."""
    payload = {
        "is_compressed": axes.is_compressed, "is_displacement": axes.is_displacement,
        "direction": axes.direction, "structure": axes.structure,
        "n1_contract_version": axes.n1_contract_version, "raw_axis_schema_version": axes.raw_axis_schema_version,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]


# ── CONTRACTUL COMPLET al fiecărei strategii ──
@dataclass(frozen=True)
class StrategyContract:
    strategy_id: str
    strategy_family: str
    allowed_regimes: tuple[SemanticRegime, ...]
    allowed_directions: tuple[str, ...]
    arming_regimes: tuple[SemanticRegime, ...]
    trigger_transition: SemanticRegime | None
    minimum_regime_confidence: float
    required_N2_bias: str | None
    required_N3_map: bool
    required_N4_confirmation: str | None
    entry_rule: str
    invalidation_rule: str
    exit_rule: str
    holding_window: int
    validation_status: ValidationStatus
    strategy_version: str
    measurement_contract_version: str
    exit_on_regime_change: bool = False
    exit_on_transition: SemanticRegime | None = None


def requires_true_range(c: StrategyContract) -> bool:
    """Proprietate DERIVATĂ din definiția canonică: strategia depinde de RANGE real (neidentificabil)."""
    return SemanticRegime.RANGE in c.allowed_regimes or SemanticRegime.RANGE in c.arming_regimes


def strategy_policy_fingerprint(c: StrategyContract) -> str:
    """Amprenta IMUABILĂ a politicii strategiei (recalculabilă de N6 din registru). O pereche (id, version) NU poate
    avea două politici diferite."""
    payload = {
        "strategy_id": c.strategy_id, "strategy_version": c.strategy_version, "strategy_family": c.strategy_family,
        "requires_true_range": requires_true_range(c),
        "allowed_regimes": sorted(r.value for r in c.allowed_regimes),
        "arming_regimes": sorted(r.value for r in c.arming_regimes),
        "validation_status": c.validation_status.value, "measurement_contract_version": c.measurement_contract_version,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]


class DuplicateStrategyPolicyError(RuntimeError):
    """Aceeași (strategy_id, strategy_version) nu poate avea două politici diferite."""


class StrategyRegistry:
    """SURSA CANONICĂ, controlată de artefactul VE. Definiția strategiei e IMUABILĂ per (strategy_id, version);
    N6 rezolvă proprietatea de aici, NU din obiectele consumatorului. Câmpurile copiate în candidat/eligibilitate
    sunt pentru AUDIT, NU autoritative."""

    def __init__(self) -> None:
        self._by_key: dict[tuple[str, str], StrategyContract] = {}

    def register(self, c: StrategyContract) -> None:
        key = (c.strategy_id, c.strategy_version)
        existing = self._by_key.get(key)
        if existing is not None and strategy_policy_fingerprint(existing) != strategy_policy_fingerprint(c):
            raise DuplicateStrategyPolicyError(
                f"{key} are deja o politică diferită — o pereche (id, version) nu poate avea două politici")
        self._by_key[key] = c

    def resolve(self, strategy_id: str, strategy_version: str) -> StrategyContract | None:
        """Definiția canonică pentru (id, version). None dacă absentă/versiune necunoscută."""
        return self._by_key.get((strategy_id, strategy_version))

    def all(self) -> tuple[StrategyContract, ...]:
        return tuple(self._by_key.values())

    def n6_eligible(self) -> tuple[StrategyContract, ...]:
        return tuple(c for c in self._by_key.values() if can_reach_n6(c.validation_status))

    def real_execution(self) -> tuple[StrategyContract, ...]:
        return tuple(c for c in self._by_key.values() if can_execute_real(c.validation_status))


def catalog_hash(strategies: tuple[StrategyContract, ...]) -> str:
    """Amprentă de INTEGRITATE peste conținutul catalogului (id, version, politică). Independentă de ordine."""
    entries = sorted(
        [c.strategy_id, c.strategy_version, strategy_policy_fingerprint(c)] for c in strategies)
    return hashlib.sha256(json.dumps(entries, sort_keys=True).encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class SealedRegistry:
    """Catalogul CANONIC — SIGILAT la construcție, IMUABIL, VERSIONAT, cu amprentă de integritate. NU are `register`:
    conținutul e fixat de `build()`. N6 refuză un registru nesigilat sau cu versiune/amprentă nepotrivită.
    Consumatorul (AI Trader) NU poate defini conținutul — poate doar CERE încărcarea catalogului aprobat."""

    _by_key: dict[tuple[str, str], StrategyContract]
    catalog_version: str
    content_hash: str
    sealed: bool = True

    @classmethod
    def build(cls, strategies: tuple[StrategyContract, ...], catalog_version: str) -> SealedRegistry:
        by_key: dict[tuple[str, str], StrategyContract] = {}
        for c in strategies:
            key = (c.strategy_id, c.strategy_version)
            existing = by_key.get(key)
            if existing is not None and strategy_policy_fingerprint(existing) != strategy_policy_fingerprint(c):
                raise DuplicateStrategyPolicyError(
                    f"{key} are deja o politică diferită în catalog — o pereche (id, version) e unică")
            by_key[key] = c
        return cls(_by_key=dict(by_key), catalog_version=catalog_version, content_hash=catalog_hash(strategies),
                   sealed=True)

    @classmethod
    def unsealed(cls, strategies: tuple[StrategyContract, ...], catalog_version: str) -> SealedRegistry:
        """DOAR pentru fault-injection în teste: un registru marcat NESIGILAT (N6 îl refuză)."""
        base = cls.build(strategies, catalog_version)
        return cls(_by_key=base._by_key, catalog_version=catalog_version, content_hash=base.content_hash, sealed=False)

    def resolve(self, strategy_id: str, strategy_version: str) -> StrategyContract | None:
        return self._by_key.get((strategy_id, strategy_version))

    def all(self) -> tuple[StrategyContract, ...]:
        return tuple(self._by_key.values())

    def n6_eligible(self) -> tuple[StrategyContract, ...]:
        return tuple(c for c in self._by_key.values() if can_reach_n6(c.validation_status))


class RoutingMode(Enum):
    NORMAL = "NORMAL"
    BREAKOUT_WATCH = "BREAKOUT_WATCH"
    INELIGIBLE = "INELIGIBLE"


@dataclass(frozen=True)
class EligibilityDecision:
    """IDENTITATEA completă (FAIL-1): N6 verifică fiecare câmp contra candidatului + starea curentă."""
    strategy_id: str
    strategy_version: str
    market_event_id: str
    regime_fingerprint: str
    router_version: str
    eligible: bool                   # is_eligible
    mode: RoutingMode
    matched_regimes: tuple[str, ...]
    reason_codes: tuple[str, ...]


def _declares_range(c: StrategyContract) -> bool:
    return SemanticRegime.RANGE in c.allowed_regimes or SemanticRegime.RANGE in c.arming_regimes


class StrategyRouter:
    """Poarta OBLIGATORIE. O strategie NEELIGIBILĂ nu generează semnal, nu produce candidat, nu ajunge la EV/N6,
    NU e numărată ca pierdută, NU e „testată" în afara regimului ei. Emite EligibilityDecision cu identitate completă."""

    def __init__(self, contracts: tuple[StrategyContract, ...]) -> None:
        self._contracts = contracts

    def _decide(self, c: StrategyContract, applicable: frozenset[SemanticRegime], bias_direction: str | None,
                confidence: float) -> tuple[bool, RoutingMode, tuple[str, ...], tuple[str, ...]]:
        normal_match = frozenset(c.allowed_regimes) & applicable
        arming_match = (frozenset(c.arming_regimes) & applicable) if c.trigger_transition is not None else frozenset()
        if not normal_match and not arming_match:
            if _declares_range(c):
                return False, RoutingMode.INELIGIBLE, (), (ReasonCode.TRUE_RANGE_NOT_IDENTIFIABLE.value,)
            if applicable == frozenset({SemanticRegime.UNCERTAIN}):
                return False, RoutingMode.INELIGIBLE, (), (ReasonCode.UNCERTAIN_REGIME.value,)
            return False, RoutingMode.INELIGIBLE, (), (ReasonCode.INELIGIBLE_REGIME.value,)
        if arming_match:
            if confidence < c.minimum_regime_confidence:
                return False, RoutingMode.INELIGIBLE, (), (ReasonCode.BELOW_MIN_REGIME_CONFIDENCE.value,)
            return True, RoutingMode.BREAKOUT_WATCH, tuple(sorted(r.value for r in arming_match)), \
                (ReasonCode.ROUTER_BREAKOUT_ARMED.value,)
        if bias_direction is not None and c.allowed_directions and bias_direction not in c.allowed_directions:
            return False, RoutingMode.INELIGIBLE, (), (ReasonCode.INELIGIBLE_DIRECTION.value,)
        if confidence < c.minimum_regime_confidence:
            return False, RoutingMode.INELIGIBLE, (), (ReasonCode.BELOW_MIN_REGIME_CONFIDENCE.value,)
        return True, RoutingMode.NORMAL, tuple(sorted(r.value for r in normal_match)), (ReasonCode.ROUTER_ELIGIBLE.value,)

    def eligible(self, axes: RawAxes, market_event_id: str, bias_direction: str | None,
                 confidence: float) -> tuple[EligibilityDecision, ...]:
        """Rutare MULTI-AXIALĂ din axele INDEPENDENTE. Fiecare decizie poartă amprenta de regim + identitatea."""
        applicable = applicable_regimes(axes)
        fp = regime_fingerprint(axes)
        out: list[EligibilityDecision] = []
        for c in self._contracts:
            elig, mode, matched, reasons = self._decide(c, applicable, bias_direction, confidence)
            out.append(EligibilityDecision(
                strategy_id=c.strategy_id, strategy_version=c.strategy_version, market_event_id=market_event_id,
                regime_fingerprint=fp, router_version=ROUTER_VERSION, eligible=elig, mode=mode,
                matched_regimes=matched, reason_codes=reasons))
        return tuple(out)


# ── BREAKOUT_WATCH: declanșarea cere N4 (displacement + ACCEPTARE, deja conjuncție în ±2) ──
_ACCEPTANCE_BULLISH = 2
_ACCEPTANCE_BEARISH = -2


def n4_triggers_breakout(confirmation_ordinal: int | None, direction: str) -> bool:
    if confirmation_ordinal is None:
        return False
    if direction == "LONG":
        return confirmation_ordinal == _ACCEPTANCE_BULLISH
    if direction == "SHORT":
        return confirmation_ordinal == _ACCEPTANCE_BEARISH
    return False
