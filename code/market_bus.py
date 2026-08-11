"""MAGISTRALA MINIMĂ — țesutul conjunctiv care CONECTEAZĂ nivelele ratificate (N1-N4) sub un singur contract,
plus un Policy Matcher și provenance, producând o decizie AUDITABILĂ. REUSE peste REBUILD: primitivele
(`market_state`, `institutional_levels`), contractul `LevelOutput`, și nivelele N1/N2/N3/N4 se REFOLOSESC — aici
NU se reconstruiește niciun detector, se cablează cei existenți.

TREI piese (mandatul magistralei):
  1. MarketState canonic — agregă ieșirile RATIFICATE ale turnului sub `LevelOutput`. NU reia
     `MarketIntelligenceSnapshot` (stratul market_intelligence paralel, neratificat: vezi matricea de duplicare) —
     poartă N1 RegimeState, N2 BiasState, N3 ZoneMap, N4 ZoneConfirmationResult, toate sub contract.
  2. Policy Matcher — generalizează REGULA DE RECUNOAȘTERE per politică (MATCH / NO_MATCH / WAITING), reluând forma
     `SetupResult` (actionable/no_setup/waiting) din `ai_trader/strategy_runtime`. ⚠ Numele din mandat
     (`pdh_pdl_demo`, `multi_policy_live`) NU EXISTĂ în repo; regulile echivalente sunt evaluatoarele de familie
     PDH/PDL (S1 sweep+confirmare, S2 reclaim, S16 breakout). Le generalizez pe ACELEA, peste ieșirile turnului.
  3. Provenance — cine / ce timeframe / ce timestamp era disponibil / ce detector / ce versiune. NU exista
     provenance per-decizie (audit găsit: doar Contract.Provenance la nivel de strategie) — se construiește aici.

DECIZIA (poarta N6 minimală): DOAR o politică MATCH cu EDGE VALIDAT poate produce TRADE. Biblioteca de strategii e
EXPLORATORIE (0 validate statistic; Alpha a măsurat clasa level-fade = fat-tail pe toți) ⇒ lanțul spune NO_TRADE.
Aia e CORECT: DoD cere o decizie AUDITABILĂ, nu o decizie TRADE. Motorul EV complet (bdd15e5, pe alpha-automation-v1)
e N6-ul final; aici e poarta de edge minimală, suficientă pentru DoD. Verdictul economic e treaba lui Alpha.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Sequence

from bias_h1 import BiasState, compute_bias
from level_output import LevelOutput, Ok, Unavailable
from market_state import atr14
from opportunity_id import OpportunityTracker
from regime_classifier import RegimeState, classify_regime
from zone_confirmation import ZoneConfirmation, ZoneConfirmationResult, classify_zone_confirmation
from zone_map import ZoneMap, build_zone_map


# ───────────────────────────── PROVENANCE (piesa 3) ─────────────────────────────
@dataclass(frozen=True)
class Provenance:
    """Urma de audit per contribuție: CINE a produs, pe CE timeframe, ce TIMESTAMP era disponibil, ce DETECTOR,
    ce VERSIUNE (schema_hash-ul contractului). Nedeductibilă din git — declarată explicit la producere."""
    who: str                 # componenta (N1_regime / N2_bias / N3_zones / N4_confirmation / policy_matcher)
    timeframe: str           # H4 / H1 / M15 / M5
    as_of: int               # bara ÎNCHISĂ disponibilă la producere (nu bara curentă)
    detector: str            # primitiva/detectorul ratificat
    version: str             # schema_hash sau code_version


# ───────────────────────────── MARKETSTATE canonic (piesa 1) ─────────────────────────────
@dataclass(frozen=True)
class MarketState:
    """Starea canonică per-decizie: ieșirile RATIFICATE ale turnului, fiecare sub `LevelOutput`, plus provenance.
    O stare „fără informație" pe o axă e `Unavailable` (constructorul), niciodată o valoare presupusă."""
    symbol: str
    as_of: int                                                     # timestamp-ul deciziei (ultima bară M5 închisă)
    regime: LevelOutput[RegimeState]                               # N1 (H4)
    bias: LevelOutput[BiasState]                                   # N2 (H1)
    zones: LevelOutput[ZoneMap]                                    # N3 (M15)
    confirmations: tuple[tuple[str, LevelOutput[ZoneConfirmationResult]], ...]   # opportunity_id → N4 (M5)
    provenance: tuple[Provenance, ...]


# ───────────────────────────── POLICY MATCHER (piesa 2) ─────────────────────────────
class Verdict(Enum):
    """Reia forma SetupResult din strategy_runtime: actionable / no_setup / waiting."""
    MATCH = "match"          # politica își RECUNOAȘTE montajul complet
    NO_MATCH = "no_match"    # nu e montajul ei
    WAITING = "waiting"      # recunoaștere parțială (ex. sweep fără confirmare)


# o regulă de recunoaștere: MarketState → (verdict, motive declanșate)
Recognizer = Callable[[MarketState], "tuple[Verdict, tuple[str, ...]]"]


@dataclass(frozen=True)
class Policy:
    """O politică = un id + o REGULĂ DE RECUNOAȘTERE peste starea turnului + statusul EDGE-ului. `has_validated_edge`
    e False pe toată biblioteca curentă (EXPLORATORIE; 0 validate statistic; global_fdr NERULAT; holdout SIGILAT)."""
    policy_id: str
    recognizer: Recognizer
    has_validated_edge: bool


@dataclass(frozen=True)
class PolicyMatch:
    policy_id: str
    verdict: Verdict
    reasons: tuple[str, ...]              # condiții declanșate (stil triggered_conditions)
    has_validated_edge: bool
    provenance: Provenance


class PolicyMatcher:
    """Aplică fiecare politică peste MarketState. Determinist, fără efecte laterale. NU decide — doar recunoaște."""

    def __init__(self, policies: Sequence[Policy]) -> None:
        self._policies = tuple(policies)

    def match(self, state: MarketState) -> tuple[PolicyMatch, ...]:
        out: list[PolicyMatch] = []
        for p in self._policies:
            verdict, reasons = p.recognizer(state)
            prov = Provenance(who="policy_matcher", timeframe="M15", as_of=state.as_of,
                              detector=p.policy_id, version="policy-matcher-v1")
            out.append(PolicyMatch(p.policy_id, verdict, reasons, p.has_validated_edge, prov))
        return tuple(out)


# ───────────────────────────── DECIZIA (poarta N6 minimală) ─────────────────────────────
class Decision(Enum):
    TRADE = "trade"
    NO_TRADE = "no_trade"


@dataclass(frozen=True)
class DecisionRecord:
    """Decizia AUDITABILĂ. Poartă motivul, politicile care au contat și ÎNTREAGA urmă de provenance."""
    decision: Decision
    reason: str
    matched_policies: tuple[str, ...]
    provenance: tuple[Provenance, ...]


def decide(state: MarketState, matches: Sequence[PolicyMatch]) -> DecisionRecord:
    """Poarta de edge minimală: DOAR o politică MATCH cu edge VALIDAT poate produce TRADE. Altfel NO_TRADE auditabil.
    Cascadă de contract: dacă regimul (N1) e Unavailable, nu există bază pentru decizie → NO_TRADE cu motiv propagat."""
    matched = tuple(m.policy_id for m in matches if m.verdict is Verdict.MATCH)
    prov = state.provenance + tuple(m.provenance for m in matches)

    if isinstance(state.regime, Unavailable):
        return DecisionRecord(Decision.NO_TRADE, f"regime_unavailable:{state.regime.reason}", matched, prov)

    tradeable = [m for m in matches if m.verdict is Verdict.MATCH and m.has_validated_edge]
    if not tradeable:
        return DecisionRecord(
            Decision.NO_TRADE,
            "no matched policy has validated edge (strategy library EXPLORATORY / level-fade fat-tail)",
            matched, prov)
    return DecisionRecord(Decision.TRADE, "matched policy with validated edge",
                          tuple(m.policy_id for m in tradeable), prov)


# ───────────────────────────── ASAMBLAREA: cablarea turnului în MarketState ─────────────────────────────
def build_market_state(
    symbol: str, as_of: int, *,
    h4: tuple[Sequence[float], Sequence[float], Sequence[float], Sequence[float], Sequence[int]],
    h1: tuple[Sequence[float], Sequence[float], Sequence[float], Sequence[float], Sequence[int]],
    m15: tuple[Sequence[float], Sequence[float], Sequence[float], Sequence[float], Sequence[int]],
    m5: tuple[Sequence[float], Sequence[float], Sequence[float], Sequence[float], Sequence[int]],
    top_k_zones: int = 3, w_confirm: int = 3,
) -> MarketState:
    """Rulează N1 (H4) → N2 (H1) → N3 (M15) → N4 (M5) pe barele DEJA tăiate la ≤ as_of pe fiecare timeframe și
    asamblează MarketState cu provenance. Fiecare tuplu = (open, high, low, close, time). PUR, cauzal (cascadă
    de contract: dacă N1 e Unavailable, N2 primește asta prin `regime_axes_status`)."""
    prov: list[Provenance] = []

    # ── N1: regim pe H4 ──
    o4, hi4, lo4, c4, t4 = h4
    regime = classify_regime(o4, hi4, lo4, c4)
    reg_ver = regime.schema_hash if isinstance(regime, Ok) else "unavailable"
    prov.append(Provenance("N1_regime", "H4", (t4[-1] if len(t4) else as_of), "regime_classifier.classify_regime", reg_ver))

    # statusurile axelor pentru cascada N2 (mulțimea necesară {vol, structure, direction})
    if isinstance(regime, Ok):
        rs = regime.value
        axes_status = ["available" if isinstance(ax, Ok) else "unavailable"
                       for ax in (rs.volatility, rs.structure, rs.direction)]
    else:
        axes_status = ["unavailable", "unavailable", "unavailable"]

    # ── N2: bias pe H1 ──
    o1, hi1, lo1, c1, t1 = h1
    bias = compute_bias(o1, hi1, lo1, c1, len(c1), regime_axes_status=axes_status)
    bias_ver = bias.schema_hash if isinstance(bias, Ok) else "unavailable"
    prov.append(Provenance("N2_bias", "H1", (t1[-1] if len(t1) else as_of), "bias_h1.compute_bias", bias_ver))

    # ── N3: harta de zone pe M15 (re-ancorată) ──
    o15, hi15, lo15, c15, t15 = m15
    m15_atr = atr14(list(hi15), list(lo15), list(c15))
    regime_ok = isinstance(regime, Ok)
    bias_ok = isinstance(bias, Ok)
    zones = build_zone_map(list(hi15), list(lo15), list(c15), list(o15), list(t15),
                           atr=m15_atr, regime_available=regime_ok, bias_available=bias_ok)
    zones_ver = zones.schema_hash if isinstance(zones, Ok) else "unavailable"
    prov.append(Provenance("N3_zones", "M15", (t15[-1] if len(t15) else as_of), "zone_map.build_zone_map", zones_ver))

    # ── N4: confirmarea pe M5 pentru cele mai apropiate K zone; opportunity_id per zonă ──
    confirmations: list[tuple[str, LevelOutput[ZoneConfirmationResult]]] = []
    o5, hi5, lo5, c5, t5 = m5
    if isinstance(zones, Ok) and len(c5) > w_confirm + 2 and len(m15_atr) > 0:
        band_ref = m15_atr[-1]                                     # banda M15 = reper de progres (autocorecția SPEC2)
        tracker = OpportunityTracker(w=w_confirm)
        ref_price = zones.value.reference_price
        atr_prev = band_ref if (band_ref == band_ref and band_ref > 0.0) else 1.0
        for z in zones.value.zones[:top_k_zones]:
            opp = tracker.step(len(c5) - 1, close_prev=ref_price, atr_prev=atr_prev, emitted=True)
            opp_id = opp.opportunity_id if opp is not None else f"opp-refresh@{z.zone_id}"
            side = 1 if z.price_anchor > ref_price else -1        # zonă deasupra→penetrare sus; sub→jos
            conf = classify_zone_confirmation(
                list(hi5), list(lo5), list(c5), z.price_anchor, side,
                w=w_confirm, atr=[band_ref] * len(c5), search_start=0)
            confirmations.append((opp_id, conf))
        cver = confirmations[0][1].schema_hash if confirmations and isinstance(confirmations[0][1], Ok) else "n/a"
        prov.append(Provenance("N4_confirmation", "M5", (t5[-1] if len(t5) else as_of),
                               "zone_confirmation.classify_zone_confirmation", cver))

    return MarketState(symbol=symbol, as_of=as_of, regime=regime, bias=bias, zones=zones,
                       confirmations=tuple(confirmations), provenance=tuple(prov))


# ───────────────────────────── politici PDH/PDL generalizate (peste ieșirile turnului) ─────────────────────────────
def _first_confirmation(state: MarketState) -> ZoneConfirmation | None:
    """Confirmarea N4 a celei mai apropiate zone (rangul 1), dacă e disponibilă (Ok). Altfel None."""
    for _opp, conf in state.confirmations:
        if isinstance(conf, Ok):
            return conf.value.confirmation
        return None
    return None


def policy_pdl_sweep_reversal(state: MarketState) -> tuple[Verdict, tuple[str, ...]]:
    """Generalizează S1 (sweep PDL + confirmare): MATCH când zona cea mai apropiată e ABSORBITĂ în jos (bull respins
    proxy → reversare bullish). Reia semantica: sweep absorbit = ABSORPTION_PROXY_BEARISH (+1)."""
    conf = _first_confirmation(state)
    if conf is None:
        return Verdict.NO_MATCH, ("no_zone_confirmation",)
    if conf is ZoneConfirmation.ABSORPTION_PROXY_BEARISH:
        return Verdict.MATCH, ("PDL_SWEEP_ABSORBED", "REVERSAL_CONFIRM")
    if conf is ZoneConfirmation.UNDETERMINED:
        return Verdict.WAITING, ("PDL_SWEEP", "AWAIT_CONFIRM")
    return Verdict.NO_MATCH, ("no_absorbed_sweep",)


def policy_pd_close_breakout(state: MarketState) -> tuple[Verdict, tuple[str, ...]]:
    """Generalizează S16 (breakout PD close): MATCH când zona cea mai apropiată e ACCEPTATĂ în sus (rămâne peste)."""
    conf = _first_confirmation(state)
    if conf is None:
        return Verdict.NO_MATCH, ("no_zone_confirmation",)
    if conf is ZoneConfirmation.ACCEPTANCE_BULLISH:
        return Verdict.MATCH, ("PD_CLOSE_BREAKOUT", "ACCEPTANCE_CONFIRM")
    return Verdict.NO_MATCH, ("no_bullish_acceptance",)


def default_policies() -> tuple[Policy, ...]:
    """Biblioteca de politici PDH/PDL generalizate. `has_validated_edge=False` PESTE TOT: biblioteca e EXPLORATORIE
    (0 validate statistic; Alpha a măsurat clasa level-fade = fat-tail). Deci lanțul va spune NO_TRADE — corect."""
    return (
        Policy("pdl_sweep_reversal", policy_pdl_sweep_reversal, has_validated_edge=False),
        Policy("pd_close_breakout", policy_pd_close_breakout, has_validated_edge=False),
    )
