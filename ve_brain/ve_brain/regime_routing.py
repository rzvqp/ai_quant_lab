"""REGIME-CONDITIONAL STRATEGY ROUTING (amendament CEO + DECIZIA CEO pe defectul de range). N1 Regime → Router →
NUMAI strategiile compatibile. INTERZIS: toate strategiile evaluate permanent, apoi alegem retrospectiv ce a mers.

═══ MAPAREA (după DECIZIA CEO pe range) ═══
NU redefinesc N1 (aprobat). Traduc cele PATRU axe N1 în stări semantice. **MULTI-AXIAL: nicio regulă globală de
precedență** — o bară COMPRESSED ȘI UP ȘI STRONG poate activa SIMULTAN strategii de trend ȘI de compresie. `applicable_
regimes` întoarce o MULȚIME, nu o etichetă unică (o etichetă unică ar fi o partiție implicită = selecție deghizată).

  axe N1: DIRECTION down|weak_down|neutral|weak_up|up · VOLATILITY compressed|low|normal|high_choppy|high_directional
          STRUCTURE none|range(|run|=1 POST-FLIP)|weak(2-3)|strong(>=4) · NEWS permanent UNAVAILABLE

  stări DERIVABILE SIGUR (rămân):
    COMPRESSION          vol == compressed
    TREND_UP             struct in {weak,strong} ȘI dir in {up,weak_up}
    TREND_DOWN           struct in {weak,strong} ȘI dir in {down,weak_down}
    BREAKOUT_TRANSITION  struct == range(|run|=1) ȘI vol == high_directional   (vezi justificarea de mai jos)
    UNCERTAIN            orice axă necesară Unavailable

  ⛔ RETRAS (DECIZIE CEO): RANGE = dir==neutral ȘI vol in {low,normal}. `Direction.NEUTRAL` e INTERZIS ca dovadă de
     consolidare — conflatează PATRU situații (range real, lipsă de structură, WARMUP, fail-closed sub n_min). Maparea
     ar fi rutat barele de WARMUP în range. RANGE devine NEIDENTIFICABIL și e SCOS din mapare. `SemanticRegime.RANGE`
     rămâne ca VALOARE de enum (strategiile îl pot DECLARA), dar NU e produs NICIODATĂ de mapare.
     MECANIC INTERZIS: StructBand.RANGE → strategie de range · Direction.NEUTRAL → range · warmup → range · lipsă → range.
     Strategiile care cer RANGE ⇒ eligibility=FALSE, reason TRUE_RANGE_NOT_IDENTIFIABLE (fail-closed, persistat).

⚠ BREAKOUT_TRANSITION — de ce interdicția RANGE NU se aplică aici (utilizare semantic DIFERITĂ, PĂSTRAT):
  · `StructBand.RANGE` = |run|=1 = un run NOU tocmai a început (FLIP proaspăt). Cere un BREAK REAL — deci NU e artefact
    de WARMUP (la warmup structura e Unavailable → UNCERTAIN, nu range) și NU e artefact de LIPSĂ de date.
  · Folosesc |run|=1 ca dovadă de INSTABILITATE (flip proaspăt), NU ca dovadă de CONSOLIDARE — exact framing-ul CEO
    („range de la STRUCTURE înseamnă POST-FLIP, nu piață laterală"). Combinat cu expansiune (high_directional), e
    semnătura pe-o-bară a unei RUPTURI. Activează o strategie de BREAKOUT, nu una de range.
  · LIMITARE (acceptată de CEO): e detecție PER-BARĂ, nu o tranziție verificată dintr-o COMPRESSION/RANGE anterioară.
    Versiunea STRICTĂ cere un detector de tranziție cu 2 stări (regime[i-1], regime[i]) construit PESTE N1 — SEMNALAT,
    NEINVENTAT (cere mandat).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .reason_codes import ReasonCode
from .strategy_contract import ValidationStatus, can_reach_n6, can_execute_real


class SemanticRegime(Enum):
    TREND_UP = "TREND_UP"
    TREND_DOWN = "TREND_DOWN"
    RANGE = "RANGE"                  # NEIDENTIFICABIL — valoare de enum pt. declarații, NICIODATĂ produsă de mapare
    COMPRESSION = "COMPRESSION"
    BREAKOUT_TRANSITION = "BREAKOUT_TRANSITION"
    UNCERTAIN = "UNCERTAIN"


_VOL_COMPRESSED = "compressed"
_VOL_HIGH_DIRECTIONAL = "high_directional"
_STRUCT_RANGE = "range"
_STRUCT_TREND = frozenset({"weak", "strong"})
_DIR_UP = frozenset({"up", "weak_up"})
_DIR_DOWN = frozenset({"down", "weak_down"})


def applicable_regimes(volatility: str | None, structure: str | None, direction: str | None) -> frozenset[SemanticRegime]:
    """MULTI-AXIAL: MULȚIMEA stărilor semantice pe care le satisface bara curentă (fără precedență, fără partiție).
    Orice axă necesară absentă ⇒ {UNCERTAIN}. NICIODATĂ RANGE (retras). Pură, per-bară, fără lookahead."""
    if volatility is None or structure is None or direction is None:
        return frozenset({SemanticRegime.UNCERTAIN})
    out: set[SemanticRegime] = set()
    if volatility == _VOL_COMPRESSED:
        out.add(SemanticRegime.COMPRESSION)
    if structure == _STRUCT_RANGE and volatility == _VOL_HIGH_DIRECTIONAL:   # flip proaspăt + expansiune = ruptură
        out.add(SemanticRegime.BREAKOUT_TRANSITION)
    if structure in _STRUCT_TREND:
        if direction in _DIR_UP:
            out.add(SemanticRegime.TREND_UP)
        if direction in _DIR_DOWN:
            out.add(SemanticRegime.TREND_DOWN)
    # NU există RANGE și NU există fallback către range: dacă nimic nu se potrivește curat ⇒ UNCERTAIN
    return frozenset(out) if out else frozenset({SemanticRegime.UNCERTAIN})


# ── CONTRACTUL COMPLET al fiecărei strategii (obligatoriu, amendament routing) ──
@dataclass(frozen=True)
class StrategyContract:
    strategy_id: str
    strategy_family: str
    allowed_regimes: tuple[SemanticRegime, ...]
    allowed_directions: tuple[str, ...]          # 'LONG' | 'SHORT'
    arming_regimes: tuple[SemanticRegime, ...]   # pentru breakout (armare); RANGE aici e MORT (neproductibil)
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


class StrategyRegistry:
    """Registrul strategiilor. Adăugarea NU face executabilă — statutul o face (A1: shadow ajunge la EV; doar
    RATIFIED/PROMOTED produc TRADE real)."""

    def __init__(self) -> None:
        self._by_id: dict[str, StrategyContract] = {}

    def register(self, c: StrategyContract) -> None:
        self._by_id[c.strategy_id] = c

    def all(self) -> tuple[StrategyContract, ...]:
        return tuple(self._by_id.values())

    def n6_eligible(self) -> tuple[StrategyContract, ...]:
        return tuple(c for c in self._by_id.values() if can_reach_n6(c.validation_status))

    def real_execution(self) -> tuple[StrategyContract, ...]:
        return tuple(c for c in self._by_id.values() if can_execute_real(c.validation_status))


class RoutingMode(Enum):
    NORMAL = "NORMAL"
    BREAKOUT_WATCH = "BREAKOUT_WATCH"
    INELIGIBLE = "INELIGIBLE"


@dataclass(frozen=True)
class EligibilityDecision:
    strategy_id: str
    eligible: bool
    mode: RoutingMode
    matched_regimes: tuple[str, ...]             # stările din applicable pe care strategia le folosește (multi-axial)
    reason_codes: tuple[str, ...]


def _declares_range(c: StrategyContract) -> bool:
    return SemanticRegime.RANGE in c.allowed_regimes or SemanticRegime.RANGE in c.arming_regimes


class StrategyRouter:
    """Eligibilitate MULTI-AXIALĂ per bară. O strategie NEELIGIBILĂ nu generează semnal, nu produce candidat, nu
    ajunge la EV/N6, NU e numărată ca tranzacție pierdută, NU e „testată" în afara regimului ei."""

    def __init__(self, contracts: tuple[StrategyContract, ...]) -> None:
        self._contracts = contracts

    def route_one(self, c: StrategyContract, applicable: frozenset[SemanticRegime], bias_direction: str | None,
                  confidence: float) -> EligibilityDecision:
        # potriviri PRODUCTIBILE (RANGE nu e NICIODATĂ în `applicable`)
        normal_match = frozenset(c.allowed_regimes) & applicable
        arming_match = (frozenset(c.arming_regimes) & applicable) if c.trigger_transition is not None else frozenset()
        if not normal_match and not arming_match:
            # nicio stare productibilă: dacă strategia DEPINDE de RANGE ⇒ fail-closed EXPLICIT (înaintea UNCERTAIN,
            # ca reason-ul salient să fie range-ul, nu incertitudinea). Fără fallback/rutare implicită către range.
            if _declares_range(c):
                return EligibilityDecision(c.strategy_id, False, RoutingMode.INELIGIBLE, (),
                                           (ReasonCode.TRUE_RANGE_NOT_IDENTIFIABLE.value,))
            if applicable == frozenset({SemanticRegime.UNCERTAIN}):
                return EligibilityDecision(c.strategy_id, False, RoutingMode.INELIGIBLE, (),
                                           (ReasonCode.UNCERTAIN_REGIME.value,))
            return EligibilityDecision(c.strategy_id, False, RoutingMode.INELIGIBLE, (),
                                       (ReasonCode.INELIGIBLE_REGIME.value,))
        if arming_match:  # BREAKOUT_WATCH — armat via o stare productibilă (COMPRESSION; RANGE e mort)
            if confidence < c.minimum_regime_confidence:
                return EligibilityDecision(c.strategy_id, False, RoutingMode.INELIGIBLE, (),
                                           (ReasonCode.BELOW_MIN_REGIME_CONFIDENCE.value,))
            return EligibilityDecision(c.strategy_id, True, RoutingMode.BREAKOUT_WATCH,
                                       tuple(sorted(r.value for r in arming_match)),
                                       (ReasonCode.ROUTER_BREAKOUT_ARMED.value,))
        if bias_direction is not None and c.allowed_directions and bias_direction not in c.allowed_directions:
            return EligibilityDecision(c.strategy_id, False, RoutingMode.INELIGIBLE, (),
                                       (ReasonCode.INELIGIBLE_DIRECTION.value,))
        if confidence < c.minimum_regime_confidence:
            return EligibilityDecision(c.strategy_id, False, RoutingMode.INELIGIBLE, (),
                                       (ReasonCode.BELOW_MIN_REGIME_CONFIDENCE.value,))
        return EligibilityDecision(c.strategy_id, True, RoutingMode.NORMAL,
                                   tuple(sorted(r.value for r in normal_match)), (ReasonCode.ROUTER_ELIGIBLE.value,))

    def eligible(self, volatility: str | None, structure: str | None, direction_axis: str | None,
                 bias_direction: str | None, confidence: float) -> tuple[EligibilityDecision, ...]:
        """Rutare MULTI-AXIALĂ din cele patru axe N1. Doar deciziile `eligible=True` merg mai departe către
        N2/N3/N4 → EV → N6. Range-dependente ⇒ TRUE_RANGE_NOT_IDENTIFIABLE (fail-closed)."""
        applicable = applicable_regimes(volatility, structure, direction_axis)
        return tuple(self.route_one(c, applicable, bias_direction, confidence) for c in self._contracts)


# ── BREAKOUT_WATCH: declanșarea cere N4 (ieșire din limită + displacement + ACCEPTARE) ──
# N4 ACCEPTANCE (±2) se atinge DOAR când persistence>=P67 ȘI progress_atr>=P67. `progress_atr` ESTE displacement-ul;
# persistence e acceptarea. Deci „displacement PLUS acceptare" e DEJA conjuncție în ±2 — fără compunere nouă.
_ACCEPTANCE_BULLISH = 2
_ACCEPTANCE_BEARISH = -2


def n4_triggers_breakout(confirmation_ordinal: int | None, direction: str) -> bool:
    """Declanșarea breakout: N4 ACCEPTANCE în direcția ruperii. Sweep/wick fără acceptare (UNDETERMINED/
    ABSORPTION_PROXY) ⇒ False (NO_BREAKOUT)."""
    if confirmation_ordinal is None:
        return False
    if direction == "LONG":
        return confirmation_ordinal == _ACCEPTANCE_BULLISH
    if direction == "SHORT":
        return confirmation_ordinal == _ACCEPTANCE_BEARISH
    return False
