"""MAGISTRALA MINIMĂ — țesutul conjunctiv care CONECTEAZĂ nivelele ratificate (N1-N4) sub un singur contract,
plus un Policy Matcher și provenance, producând o decizie AUDITABILĂ. REUSE peste REBUILD: primitivele
(`market_state`), contractul `LevelOutput`, identitatea (`opportunity_id`), și nivelele N1-N4 se REFOLOSESC.

CEASUL DECIZIEI = zone_hit (i0), NU hit+W+1 (remediere RT-AUDIT-CHAIN-0002 / E2E-L1). Disciplina CEO, deja definită
în `opportunity_id.py`, e FOLOSITĂ aici, nu reconstruită:
  · `DecisionRecord(decided_at = i0 = zone_hit, inputs_hash peste N1/N2/N3)` — decizia se ia din ce e disponibil LA i0.
  · `EvidenceRecord(attached_at = i0+W+1, descriptor = N4)` — N4 e DOVADĂ atașată POST-decizie.
  · Legate DOAR prin `opportunity_id`; N4 NU poate modifica decizia — prin TIP.
Recunoașterea (Policy Matcher) și decizia citesc EXCLUSIV N1/N2/N3. N4 nu intră niciodată în TRADE/NO_TRADE — altfel
ceasul efectiv ar aluneca la hit+W+1 (ce CEO a interzis, ce Statisticianul a măsurat că elimină 71% din oportunități).

TREI piese (mandatul magistralei):
  1. MarketState canonic — agregă ieșirile RATIFICATE ale turnului sub `LevelOutput`. NU reia
     `MarketIntelligenceSnapshot` (stratul market_intelligence paralel, neratificat) — poartă N1/N2/N3 + N4-ca-dovadă.
  2. Policy Matcher — generalizează REGULA DE RECUNOAȘTERE per politică (MATCH/NO_MATCH/WAITING) peste N1/N2/N3.
     ⚠ Numele din mandat (`pdh_pdl_demo`, `multi_policy_live`) NU EXISTĂ în repo; regulile echivalente sunt
     evaluatoarele de familie PDH/PDL (S1 reversare, S2 fade, S16 breakout). Le generalizez pe ACELEA.
  3. Provenance — cine / ce timeframe / ce timestamp era disponibil / ce detector / ce versiune.

DECIZIA (poarta N6 minimală): DOAR o politică MATCH cu EDGE VALIDAT poate produce TRADE. Biblioteca e EXPLORATORIE
(0 validate statistic; Alpha a măsurat clasa level-fade = fat-tail) ⇒ lanțul spune NO_TRADE. Poarta e un proxy
CONSERVATOR (nu poate produce trade fals) — NU e N6-ul real. Motorul EV complet (bdd15e5, pe alpha-automation-v1) e
obligatoriu ÎNAINTE de ORICE trade (E2E-U1), traversarea cross-branch e RAPORTATĂ, nu forțată aici.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Literal, Sequence, cast

from bias_h1 import BiasState, Direction, compute_bias
from level_output import LevelOutput, Ok, Unavailable
from market_state import atr14
from opportunity_id import DecisionRecord, EvidenceRecord, OpportunityTracker
from regime_classifier import RegimeState, classify_regime
from zone_confirmation import ZoneConfirmationResult, classify_zone_confirmation
from zone_map import Zone, ZoneMap, build_zone_map


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


# ───────────────────────────── slot de oportunitate (decizie la i0 + dovadă la i0+W+1) ─────────────────────────────
@dataclass(frozen=True)
class ConfirmationSlot:
    """O oportunitate identificată: decizia se ia la `decided_at` (zone_hit, din N1/N2/N3); confirmarea N4 e DOVADĂ
    atașată la `evidence_at` (i0+W+1). N4 (`confirmation`) NU intră în decizie — e purtat pentru EvidenceRecord."""
    opportunity_id: str
    decided_at: int                                   # i0 = zone_hit
    evidence_at: int                                  # i0 + W + 1
    confirmation: LevelOutput[ZoneConfirmationResult]  # N4, DOVADĂ post-decizie (NU citit de decide/recognizers)


# ───────────────────────────── MARKETSTATE canonic (piesa 1) ─────────────────────────────
@dataclass(frozen=True)
class MarketState:
    """Starea canonică per-decizie: ieșirile RATIFICATE ale turnului, fiecare sub `LevelOutput`, plus provenance.
    N1/N2/N3 sunt intrările DECIZIEI (la i0); N4 (în `confirmations`) e DOVADĂ post-decizie, izolată prin tip."""
    symbol: str
    as_of: int                                                     # timestamp-ul deciziei (ultima bară M5 închisă)
    regime: LevelOutput[RegimeState]                               # N1 (H4) — intrare de decizie
    bias: LevelOutput[BiasState]                                   # N2 (H1) — intrare de decizie
    zones: LevelOutput[ZoneMap]                                    # N3 (M15) — intrare de decizie
    confirmations: tuple[ConfirmationSlot, ...]                    # N4 (M5) — DOVADĂ, nu intrare de decizie
    provenance: tuple[Provenance, ...]


# ───────────────────────────── POLICY MATCHER (piesa 2) — citește DOAR N1/N2/N3 ─────────────────────────────
class Verdict(Enum):
    """Reia forma SetupResult din strategy_runtime: actionable / no_setup / waiting."""
    MATCH = "match"          # politica își RECUNOAȘTE montajul din N1/N2/N3
    NO_MATCH = "no_match"
    WAITING = "waiting"      # recunoaștere parțială (ex. zonă prezentă dar bias UNKNOWN)


# o regulă de recunoaștere: MarketState → (verdict, motive). CITEȘTE EXCLUSIV N1/N2/N3 (niciodată N4/confirmations).
Recognizer = Callable[[MarketState], "tuple[Verdict, tuple[str, ...]]"]


@dataclass(frozen=True)
class Policy:
    policy_id: str
    recognizer: Recognizer
    has_validated_edge: bool         # False pe toată biblioteca (EXPLORATORIE; 0 validate; level-fade fat-tail)


@dataclass(frozen=True)
class PolicyMatch:
    policy_id: str
    verdict: Verdict
    reasons: tuple[str, ...]
    has_validated_edge: bool
    provenance: Provenance


class PolicyMatcher:
    """Aplică fiecare politică peste N1/N2/N3 din MarketState. Determinist, fără efecte laterale. NU citește N4."""

    def __init__(self, policies: Sequence[Policy]) -> None:
        self._policies = tuple(policies)

    def match(self, state: MarketState) -> tuple[PolicyMatch, ...]:
        out: list[PolicyMatch] = []
        for p in self._policies:
            verdict, reasons = p.recognizer(state)
            prov = Provenance("policy_matcher", "M15", state.as_of, p.policy_id, "policy-matcher-v1")
            out.append(PolicyMatch(p.policy_id, verdict, reasons, p.has_validated_edge, prov))
        return tuple(out)


# ───────────────────────────── DECIZIA (poarta N6 minimală), la zone_hit ─────────────────────────────
class Decision(Enum):
    TRADE = "trade"
    NO_TRADE = "no_trade"


_DECISION_SCHEMA: str = hashlib.sha256(json.dumps({
    "decision_clock": "zone_hit_i0", "inputs": ["N1_regime", "N2_bias", "N3_zones"],
    "n4_role": "evidence_post_decision_not_input", "edge_gate": "validated_edge_only",
    "code_version": "market-bus-v2-zonehit",
}, sort_keys=True).encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class AuditedDecision:
    """Decizia AUDITABILĂ. `decision_records` (la zone_hit, din N1/N2/N3) și `evidence_records` (N4, la i0+W+1) sunt
    SEPARATE, legate doar prin opportunity_id — N4 nu poate schimba decizia. Poartă motivul, politicile, provenance."""
    decision: Decision
    reason: str
    matched_policies: tuple[str, ...]
    decision_records: tuple[DecisionRecord, ...]      # decided_at = zone_hit; inputs_hash DOAR N1/N2/N3
    evidence_records: tuple[EvidenceRecord, ...]      # attached_at = i0+W+1; descriptorul N4
    provenance: tuple[Provenance, ...]


def _inputs_hash_n1n2n3(state: MarketState) -> str:
    """Hash peste N1/N2/N3 AȘA CUM ERAU la i0 — EXCLUDE N4 (dovada). Dacă N4 ar intra aici, ceasul ar aluneca."""
    parts = [
        state.regime.schema_hash if isinstance(state.regime, Ok) else f"U:{state.regime.reason}",
        state.bias.schema_hash if isinstance(state.bias, Ok) else f"U:{state.bias.reason}",
        state.zones.schema_hash if isinstance(state.zones, Ok) else f"U:{state.zones.reason}",
    ]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]


def decide(state: MarketState, matches: Sequence[PolicyMatch]) -> AuditedDecision:
    """Poarta de edge minimală, la zone_hit. Decizia vine din recunoașterea peste N1/N2/N3 (matches) + statusul edge.
    N4 NU e citit aici — e împachetat ca EvidenceRecord, legat prin opportunity_id, post-decizie."""
    prov = state.provenance + tuple(m.provenance for m in matches)
    matched_ids = tuple(m.policy_id for m in matches if m.verdict is Verdict.MATCH)

    outcome_lit: Literal["TRADE", "NO_TRADE"]
    if isinstance(state.regime, Unavailable):                      # cascadă N1: fără regim, fără bază de decizie
        decision, outcome_lit = Decision.NO_TRADE, "NO_TRADE"
        reason = f"regime_unavailable:{state.regime.reason}"
    else:
        tradeable = [m for m in matches if m.verdict is Verdict.MATCH and m.has_validated_edge]
        if tradeable:
            decision, outcome_lit = Decision.TRADE, "TRADE"
            reason = "matched policy with validated edge"
            matched_ids = tuple(m.policy_id for m in tradeable)
        else:
            decision, outcome_lit = Decision.NO_TRADE, "NO_TRADE"
            reason = "no matched policy has validated edge (strategy library EXPLORATORY / level-fade fat-tail)"

    ih = _inputs_hash_n1n2n3(state)                                # DOAR N1/N2/N3 — proba că N4 nu intră
    slots = state.confirmations if state.confirmations else (
        ConfirmationSlot("opp-none", state.as_of, state.as_of, Unavailable("no_zone", state.as_of)),)
    decision_records = tuple(
        DecisionRecord(opportunity_id=s.opportunity_id, decided_at=s.decided_at, outcome=outcome_lit,
                       inputs_hash=ih, schema_hash=_DECISION_SCHEMA) for s in slots)
    evidence_records = tuple(
        EvidenceRecord(opportunity_id=s.opportunity_id, attached_at=s.evidence_at,
                       descriptor=cast("LevelOutput[object]", s.confirmation)) for s in slots)
    return AuditedDecision(decision, reason, matched_ids, decision_records, evidence_records, prov)


# ───────────────────────────── ASAMBLAREA: cablarea turnului în MarketState ─────────────────────────────
def _assert_cut(name: str, t: Sequence[int], as_of: int) -> None:
    """E2E-L2: magistrala NU are încredere în tăietura apelantului — o IMPUNE. Nicio bară din viitor."""
    if len(t) and t[-1] > as_of:
        raise ValueError(f"lookahead: {name} last bar {t[-1]} > decision as_of {as_of}")


def _require_valid(out: LevelOutput[object], who: str, as_of_level: int) -> None:
    """E2E-L2: impune `valid_until >= as_of` pe fiecare nivel Ok (fereastra de validitate nu poate fi în trecut;
    carry-forward dincolo de ea = eroare de contract). NEîncredere, nu presupunere."""
    if isinstance(out, Ok) and out.valid_until < as_of_level:
        raise ValueError(f"{who}: stale level valid_until {out.valid_until} < as_of {as_of_level}")


def build_market_state(
    symbol: str, as_of: int, *,
    h4: tuple[Sequence[float], Sequence[float], Sequence[float], Sequence[float], Sequence[int]],
    h1: tuple[Sequence[float], Sequence[float], Sequence[float], Sequence[float], Sequence[int]],
    m15: tuple[Sequence[float], Sequence[float], Sequence[float], Sequence[float], Sequence[int]],
    m5: tuple[Sequence[float], Sequence[float], Sequence[float], Sequence[float], Sequence[int]],
    top_k_zones: int = 3, w_confirm: int = 3,
) -> MarketState:
    """Rulează N1 (H4) → N2 (H1) → N3 (M15) → N4 (M5) pe barele DEJA tăiate la ≤ as_of pe fiecare timeframe și
    asamblează MarketState. N1/N2/N3 = intrări de decizie (la i0); N4 = dovadă (la i0+W+1). PUR, cauzal.
    E2E-L2: tăietura apelantului e IMPUSĂ (nicio bară > as_of), iar fiecare nivel Ok e verificat `valid_until>=as_of`."""
    _assert_cut("H4", h4[4], as_of); _assert_cut("H1", h1[4], as_of)
    _assert_cut("M15", m15[4], as_of); _assert_cut("M5", m5[4], as_of)
    prov: list[Provenance] = []

    # ── N1: regim pe H4 ──
    o4, hi4, lo4, c4, t4 = h4
    regime = classify_regime(o4, hi4, lo4, c4)
    _require_valid(regime, "N1_regime", len(c4) - 1)
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
    _require_valid(bias, "N2_bias", len(c1) - 1)
    bias_ver = bias.schema_hash if isinstance(bias, Ok) else "unavailable"
    prov.append(Provenance("N2_bias", "H1", (t1[-1] if len(t1) else as_of), "bias_h1.compute_bias", bias_ver))

    # ── N3: harta de zone pe M15 (re-ancorată) ──
    o15, hi15, lo15, c15, t15 = m15
    m15_atr = atr14(list(hi15), list(lo15), list(c15))
    zones = build_zone_map(list(hi15), list(lo15), list(c15), list(o15), list(t15),
                           atr=m15_atr, regime_available=isinstance(regime, Ok), bias_available=isinstance(bias, Ok))
    _require_valid(zones, "N3_zones", len(c15) - 1)
    zones_ver = zones.schema_hash if isinstance(zones, Ok) else "unavailable"
    prov.append(Provenance("N3_zones", "M15", (t15[-1] if len(t15) else as_of), "zone_map.build_zone_map", zones_ver))

    # ── N4: confirmarea pe M5 = DOVADĂ pentru cele mai apropiate K zone; opportunity_id per zonă, decizia la i0 ──
    confirmations: list[ConfirmationSlot] = []
    o5, hi5, lo5, c5, t5 = m5
    if isinstance(zones, Ok) and len(c5) > w_confirm + 2 and len(m15_atr) > 0:
        band_ref = m15_atr[-1]                                     # banda M15 = reper de progres (autocorecția SPEC2)
        tracker = OpportunityTracker(w=w_confirm)
        ref_price = zones.value.reference_price
        atr_prev = band_ref if (band_ref == band_ref and band_ref > 0.0) else 1.0
        i0 = len(c5) - 1                                           # zone_hit (bara M5 curentă) = decided_at
        for z in zones.value.zones[:top_k_zones]:
            opp = tracker.step(i0, close_prev=ref_price, atr_prev=atr_prev, emitted=True)
            opp_id = opp.opportunity_id if opp is not None else f"opp-refresh@{z.zone_id}"
            decided_at = opp.created_at if opp is not None else i0
            evidence_at = opp.evidence_deadline if opp is not None else i0 + w_confirm + 1
            side = 1 if z.price_anchor > ref_price else -1        # zonă deasupra→penetrare sus; sub→jos
            conf = classify_zone_confirmation(
                list(hi5), list(lo5), list(c5), z.price_anchor, side,
                w=w_confirm, atr=[band_ref] * len(c5), search_start=0)
            confirmations.append(ConfirmationSlot(opp_id, decided_at, evidence_at, conf))
        cver = "n/a"
        if confirmations and isinstance(confirmations[0].confirmation, Ok):
            cver = confirmations[0].confirmation.schema_hash
        prov.append(Provenance("N4_confirmation", "M5", (t5[-1] if len(t5) else as_of),
                               "zone_confirmation.classify_zone_confirmation", cver))

    return MarketState(symbol=symbol, as_of=as_of, regime=regime, bias=bias, zones=zones,
                       confirmations=tuple(confirmations), provenance=tuple(prov))


# ───────────────── politici PDH/PDL generalizate — RECUNOSC din N1/N2/N3 (niciodată N4) ─────────────────
def _bias_direction(state: MarketState) -> Direction | None:
    """Direcția din N2, factorul din mulțimea necesară (structure_run_h1). None dacă N2/factorul e indisponibil."""
    if not isinstance(state.bias, Ok):
        return None
    factors = state.bias.value.factors
    if not factors or not isinstance(factors[0], Ok):
        return None
    return factors[0].value.direction


def _nearest_zone(state: MarketState) -> Zone | None:
    """Zona cea mai apropiată din N3 (rangul 1). None dacă N3 e indisponibil sau nu există zone."""
    if not isinstance(state.zones, Ok) or not state.zones.value.zones:
        return None
    return state.zones.value.zones[0]


def policy_pdl_sweep_reversal(state: MarketState) -> tuple[Verdict, tuple[str, ...]]:
    """Generalizează S1 (sweep PDL + reversare): MATCH când zona cea mai apropiată e în DISCOUNT (suport) ȘI biasul
    N2 e LONG. Citește DOAR N3 (atributul zonei) + N2 (direcția) — NU N4."""
    z = _nearest_zone(state); d = _bias_direction(state)
    if z is None:
        return Verdict.NO_MATCH, ("no_zone",)
    if z.attribute == "discount" and d is Direction.LONG:
        return Verdict.MATCH, ("DISCOUNT_ZONE", "BIAS_LONG")
    if z.attribute == "discount" and (d is None or d is Direction.UNKNOWN):
        return Verdict.WAITING, ("DISCOUNT_ZONE", "AWAIT_BIAS")
    return Verdict.NO_MATCH, ("no_discount_long_setup",)


def policy_pdl_failed_break_fade(state: MarketState) -> tuple[Verdict, tuple[str, ...]]:
    """Generalizează S2 (false-break PDL + reclaim/fade): MATCH când zona cea mai apropiată e în DISCOUNT (suport
    rupt fals) ȘI biasul N2 e SHORT (fade-ul ruperii eșuate). Citește DOAR N3 + N2 — NU N4."""
    z = _nearest_zone(state); d = _bias_direction(state)
    if z is None:
        return Verdict.NO_MATCH, ("no_zone",)
    if z.attribute == "discount" and d is Direction.SHORT:
        return Verdict.MATCH, ("PDL_FAILED_BREAK", "FADE_SHORT")
    if z.attribute == "discount" and (d is None or d is Direction.UNKNOWN):
        return Verdict.WAITING, ("PDL_FAILED_BREAK", "AWAIT_BIAS")
    return Verdict.NO_MATCH, ("no_discount_short_fade",)


def policy_pd_close_breakout(state: MarketState) -> tuple[Verdict, tuple[str, ...]]:
    """Generalizează S16 (breakout PD close): MATCH când zona cea mai apropiată e în PREMIUM (rezistență depășită)
    ȘI biasul N2 e LONG. Citește DOAR N3 + N2 — NU N4."""
    z = _nearest_zone(state); d = _bias_direction(state)
    if z is None:
        return Verdict.NO_MATCH, ("no_zone",)
    if z.attribute == "premium" and d is Direction.LONG:
        return Verdict.MATCH, ("PREMIUM_ZONE", "BIAS_LONG")
    return Verdict.NO_MATCH, ("no_premium_long_breakout",)


def default_policies() -> tuple[Policy, ...]:
    """Biblioteca de politici PDH/PDL generalizate (trei, verificat). `has_validated_edge=False` PESTE TOT: biblioteca
    e EXPLORATORIE (0 validate statistic; Alpha a măsurat clasa level-fade = fat-tail). Deci lanțul spune NO_TRADE."""
    return (
        Policy("pdl_sweep_reversal", policy_pdl_sweep_reversal, has_validated_edge=False),
        Policy("pdl_failed_break_fade", policy_pdl_failed_break_fade, has_validated_edge=False),
        Policy("pd_close_breakout", policy_pd_close_breakout, has_validated_edge=False),
    )
