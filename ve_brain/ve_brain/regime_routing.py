"""REGIME-CONDITIONAL STRATEGY ROUTING (amendament CEO). N1 Regime → Router → NUMAI strategiile compatibile.
INTERZIS: toate strategiile evaluate permanent, apoi alegem retrospectiv ce a mers.

═══ REZOLVAREA CONFLICTULUI DE TAXONOMIE (NU ocolire) ═══
CEO cere 6 stări semantice; N1 ratificat are PATRU AXE, nu o etichetă unică. NU redefinesc N1 (aprobat, conform
rolului). Construiesc MAPAREA, păstrând distincțiile semantice.

  axe N1 (valorile ratificate):
    DIRECTION   down | weak_down | neutral | weak_up | up
    VOLATILITY  compressed | low | normal | high_choppy | high_directional
    STRUCTURE   none | range(|run|=1, POST-FLIP) | weak(2-3) | strong(>=4)
    NEWS        permanent UNAVAILABLE

  MAPARE → cele 6 stări semantice:
    COMPRESSION         VOLATILITY == compressed                         (banda decilă-joasă = piața „strânsă")
    BREAKOUT_TRANSITION STRUCTURE == range (|run|=1, FLIP proaspăt) ȘI VOLATILITY == high_directional (expansiune)
    TREND_UP            STRUCTURE in {weak,strong} ȘI DIRECTION in {up,weak_up}
    TREND_DOWN          STRUCTURE in {weak,strong} ȘI DIRECTION in {down,weak_down}
    RANGE               DIRECTION == neutral ȘI VOLATILITY in {low,normal}  (ne-trend, ne-comprimat, ne-breakout)
    UNCERTAIN           orice axă necesară Unavailable, sau nicio potrivire curată

⚠ RĂSPUNS EXPLICIT LA CEO despre BREAKOUT_TRANSITION (nu-l inventez):
  · STRUCTURE.range = POST-FLIP (Red Team + Statistician: axa de structură NU are stare de „piață laterală"; acel
    concept e servit de COMPRESSION). „Post-flip" înseamnă că un run NOU tocmai a început la bara curentă.
  · Un flip PROASPĂT (|run|=1) ÎMPREUNĂ CU expansiune (high_directional) ESTE, prin construcție, semnătura pe O
    BARĂ a unei rupturi direcționale — deci BREAKOUT_TRANSITION E DERIVABIL ca proxy per-bară din axele existente.
  · LIMITARE onestă: aceasta e o detecție PER-BARĂ, nu o TRANZIȚIE verificată dintr-o COMPRESSION/RANGE anterioară.
    Versiunea STRICTĂ (regimul barei i-1 ∈ {COMPRESSION, RANGE} → regimul barei i = ruptură) ar cere starea
    regimului ANTERIOR, pe care N1 per-bară NU o poartă. PROPUNEREA: un detector de tranziție cu 2 stări
    (regime[i-1], regime[i]) construit PESTE N1, fără a-l modifica — o singură comparație, cauzală. Nu-l construiesc
    aici fără mandat; îl semnalez ca item necesar pentru versiunea strictă a BREAKOUT_TRANSITION.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .reason_codes import ReasonCode
from .strategy_contract import ValidationStatus, can_reach_n6, can_execute_real


class SemanticRegime(Enum):
    TREND_UP = "TREND_UP"
    TREND_DOWN = "TREND_DOWN"
    RANGE = "RANGE"
    COMPRESSION = "COMPRESSION"
    BREAKOUT_TRANSITION = "BREAKOUT_TRANSITION"
    UNCERTAIN = "UNCERTAIN"


# valorile axelor N1 (ratificate) — importate ca STRINGURI ca să nu cuplăm pachetul de tipurile din turn
_VOL_COMPRESSED = "compressed"
_VOL_HIGH_DIRECTIONAL = "high_directional"
_STRUCT_RANGE = "range"
_STRUCT_TREND = frozenset({"weak", "strong"})
_DIR_UP = frozenset({"up", "weak_up"})
_DIR_DOWN = frozenset({"down", "weak_down"})
_DIR_NEUTRAL = "neutral"
_VOL_RANGE_OK = frozenset({"low", "normal"})


def semantic_regime(volatility: str | None, structure: str | None, direction: str | None) -> SemanticRegime:
    """Mapare PURĂ, per-bară, de la cele patru axe N1 la cele șase stări semantice. Orice axă necesară absentă
    (None = Unavailable) ⇒ UNCERTAIN. Nu redefinește N1; doar traduce."""
    if volatility is None or structure is None or direction is None:
        return SemanticRegime.UNCERTAIN
    # BREAKOUT_TRANSITION înainte de COMPRESSION/TREND: flip proaspăt + expansiune (proxy per-bară)
    if structure == _STRUCT_RANGE and volatility == _VOL_HIGH_DIRECTIONAL:
        return SemanticRegime.BREAKOUT_TRANSITION
    if volatility == _VOL_COMPRESSED:
        return SemanticRegime.COMPRESSION
    if structure in _STRUCT_TREND:
        if direction in _DIR_UP:
            return SemanticRegime.TREND_UP
        if direction in _DIR_DOWN:
            return SemanticRegime.TREND_DOWN
    if direction == _DIR_NEUTRAL and volatility in _VOL_RANGE_OK:
        return SemanticRegime.RANGE
    return SemanticRegime.UNCERTAIN


# ── CONTRACTUL COMPLET al fiecărei strategii (obligatoriu, amendament routing) ──
@dataclass(frozen=True)
class StrategyContract:
    strategy_id: str
    strategy_family: str
    allowed_regimes: tuple[SemanticRegime, ...]
    allowed_directions: tuple[str, ...]          # 'LONG' | 'SHORT'
    arming_regimes: tuple[SemanticRegime, ...]   # pentru breakout: armare în RANGE/COMPRESSION
    trigger_transition: SemanticRegime | None    # ex. BREAKOUT_TRANSITION (None = fără tranziție)
    minimum_regime_confidence: float
    required_N2_bias: str | None                 # 'LONG' | 'SHORT' | None
    required_N3_map: bool
    required_N4_confirmation: str | None         # ex. 'DISPLACEMENT_AND_ACCEPTANCE' | 'ACCEPTANCE' | None
    entry_rule: str
    invalidation_rule: str
    exit_rule: str
    holding_window: int
    validation_status: ValidationStatus
    strategy_version: str
    measurement_contract_version: str
    exit_on_regime_change: bool = False
    exit_on_transition: SemanticRegime | None = None   # dacă exit_on_regime_change, ce tranziție iese


class StrategyRegistry:
    """Registrul strategiilor livrate de Alpha. Adăugarea NU face executabilă — statutul o face (A1: shadow poate
    ajunge la EV; doar RATIFIED/PROMOTED produc TRADE real)."""

    def __init__(self) -> None:
        self._by_id: dict[str, StrategyContract] = {}

    def register(self, c: StrategyContract) -> None:
        self._by_id[c.strategy_id] = c

    def all(self) -> tuple[StrategyContract, ...]:
        return tuple(self._by_id.values())

    def n6_eligible(self) -> tuple[StrategyContract, ...]:
        """Pot ajunge la N6/EV (RATIFIED/PROMOTED/SHADOW_ELIGIBLE). Gol ⇒ NO_ELIGIBLE_STRATEGY prin construcție."""
        return tuple(c for c in self._by_id.values() if can_reach_n6(c.validation_status))

    def real_execution(self) -> tuple[StrategyContract, ...]:
        return tuple(c for c in self._by_id.values() if can_execute_real(c.validation_status))


class RoutingMode(Enum):
    NORMAL = "NORMAL"                 # eligibilă direct în regimul curent
    BREAKOUT_WATCH = "BREAKOUT_WATCH"  # armată în RANGE/COMPRESSION, așteaptă declanșarea N4
    INELIGIBLE = "INELIGIBLE"


@dataclass(frozen=True)
class EligibilityDecision:
    strategy_id: str
    eligible: bool
    mode: RoutingMode
    semantic_regime: SemanticRegime
    reason_codes: tuple[str, ...]


class StrategyRouter:
    """Stabilește eligibilitatea per regim. O strategie NEELIGIBILĂ nu generează semnal, nu produce candidat, nu
    ajunge la EV/N6, NU e numărată ca tranzacție pierdută și NU e considerată „testată" în afara regimului ei."""

    def __init__(self, contracts: tuple[StrategyContract, ...]) -> None:
        self._contracts = contracts

    def route_one(self, c: StrategyContract, regime: SemanticRegime, direction: str | None,
                  confidence: float) -> EligibilityDecision:
        if regime is SemanticRegime.UNCERTAIN:
            return EligibilityDecision(c.strategy_id, False, RoutingMode.INELIGIBLE, regime,
                                       (ReasonCode.UNCERTAIN_REGIME.value,))
        # BREAKOUT_WATCH: armată dacă regimul curent e în arming_regimes ȘI strategia are trigger_transition
        if c.trigger_transition is not None and regime in c.arming_regimes:
            if confidence < c.minimum_regime_confidence:
                return EligibilityDecision(c.strategy_id, False, RoutingMode.INELIGIBLE, regime,
                                           (ReasonCode.BELOW_MIN_REGIME_CONFIDENCE.value,))
            return EligibilityDecision(c.strategy_id, True, RoutingMode.BREAKOUT_WATCH, regime,
                                       (ReasonCode.ROUTER_BREAKOUT_ARMED.value,))
        # NORMAL: regimul curent trebuie să fie în allowed_regimes
        if regime not in c.allowed_regimes:
            return EligibilityDecision(c.strategy_id, False, RoutingMode.INELIGIBLE, regime,
                                       (ReasonCode.INELIGIBLE_REGIME.value,))
        if direction is not None and c.allowed_directions and direction not in c.allowed_directions:
            return EligibilityDecision(c.strategy_id, False, RoutingMode.INELIGIBLE, regime,
                                       (ReasonCode.INELIGIBLE_DIRECTION.value,))
        if confidence < c.minimum_regime_confidence:
            return EligibilityDecision(c.strategy_id, False, RoutingMode.INELIGIBLE, regime,
                                       (ReasonCode.BELOW_MIN_REGIME_CONFIDENCE.value,))
        return EligibilityDecision(c.strategy_id, True, RoutingMode.NORMAL, regime,
                                   (ReasonCode.ROUTER_ELIGIBLE.value,))

    def eligible(self, regime: SemanticRegime, direction: str | None,
                 confidence: float) -> tuple[EligibilityDecision, ...]:
        """Toate deciziile de eligibilitate (eligibile + inele­gibile, cu motiv). Doar cele `eligible=True` merg mai
        departe către N2/N3/N4 → EV → N6."""
        return tuple(self.route_one(c, regime, direction, confidence) for c in self._contracts)


# ── BREAKOUT_WATCH: declanșarea cere N4 (ieșire din limită + displacement + ACCEPTARE) ──
# Verificare a semanticii N4 (răspuns la întrebarea CEO):
#   N4 emite o ordinală cu semn: ACCEPTANCE_BULLISH=+2 = „penetrare în SUS ACCEPTATĂ (rămâne peste rezistență)".
#   ACCEPTANCE se atinge DOAR când persistence>=P67 ȘI progress_atr>=P67. `progress_atr` ESTE displacement-ul
#   (progres/ATR), iar persistence e acceptarea. Deci „displacement PLUS acceptare" e DEJA o CONJUNCȚIE în ±2 —
#   nu cere o compunere nouă. Un sweep/wick fără acceptare dă UNDETERMINED sau ABSORPTION_PROXY, NU ±2 ⇒ NO_BREAKOUT.
_ACCEPTANCE_BULLISH = 2
_ACCEPTANCE_BEARISH = -2


def n4_triggers_breakout(confirmation_ordinal: int | None, direction: str) -> bool:
    """Declanșarea breakout: N4 ACCEPTANCE în direcția ruperii (displacement+acceptare, deja conjuncție în ±2).
    Sweep/wick fără acceptare (UNDETERMINED / ABSORPTION_PROXY) ⇒ False (NO_BREAKOUT)."""
    if confirmation_ordinal is None:
        return False
    if direction == "LONG":
        return confirmation_ordinal == _ACCEPTANCE_BULLISH
    if direction == "SHORT":
        return confirmation_ordinal == _ACCEPTANCE_BEARISH
    return False
