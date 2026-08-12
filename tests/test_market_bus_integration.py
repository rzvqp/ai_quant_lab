"""DoD — DEMONSTRAȚIA END-TO-END (cei 13 pași) + remedierile RT-AUDIT-CHAIN-0002 (E2E-L1/L2/U1).

Scopul e ca LANȚUL să producă o DECIZIE AUDITABILĂ pe date reale, LA ZONE_HIT (nu la hit+W+1): recunoașterea și
decizia citesc N1/N2/N3; N4 e DOVADĂ post-decizie (EvidenceRecord), izolată prin tip. NO_TRADE e corect (biblioteca
EXPLORATORIE / level-fade fat-tail). Se sare dacă lipsesc CSV-urile. Fără MT5, fără rețea.
"""

from __future__ import annotations

import csv
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CODE = os.path.join(_ROOT, "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from bias_h1 import BiasState, Direction, FactorDirection  # noqa: E402
from level_output import Ok, Unavailable  # noqa: E402
from market_bus import (  # noqa: E402
    ConfirmationSlot, Decision, MarketState, Policy, PolicyMatch, PolicyMatcher, Provenance, Verdict,
    build_market_state, decide, default_policies,
)
from regime_classifier import RegimeState  # noqa: E402
from zone_confirmation import ZoneConfirmation, ZoneConfirmationResult  # noqa: E402
from zone_map import Zone, ZoneMap  # noqa: E402

_MKT = os.path.join(_ROOT, "data", "market")
_FILES = {
    "h4": os.path.join(_MKT, "OANDA_XAUUSD_H4_from_M15_v2.csv"),
    "h1": os.path.join(_MKT, "OANDA_XAUUSD_H1_from_M15_v2.csv"),
    "m15": os.path.join(_MKT, "OANDA_XAUUSD_M15.csv"),
    "m5": os.path.join(_MKT, "OANDA_XAUUSD_M5.csv"),
}
_HAVE_DATA = all(os.path.exists(p) for p in _FILES.values())
Bars = tuple[list[float], list[float], list[float], list[float], list[int]]


def _load(path: str) -> Bars:
    o: list[float] = []; h: list[float] = []; l: list[float] = []; c: list[float] = []; t: list[int] = []
    with open(path, "r", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            o.append(float(row["open"])); h.append(float(row["high"])); l.append(float(row["low"]))
            c.append(float(row["close"])); t.append(int(float(row["time"])))
    return o, h, l, c, t


def _slice_upto(bars: Bars, as_of: int, tail: int) -> Bars:
    o, h, l, c, t = bars
    hi = 0
    while hi < len(t) and t[hi] <= as_of:
        hi += 1
    lo = max(0, hi - tail)
    return o[lo:hi], h[lo:hi], l[lo:hi], c[lo:hi], t[lo:hi]


# ───────────────────────────── DoD: 13 pași pe date reale ─────────────────────────────
@pytest.mark.skipif(not _HAVE_DATA, reason="CSV-uri de piață absente")
def test_end_to_end_produces_an_auditable_decision() -> None:
    h4_all = _load(_FILES["h4"]); h1_all = _load(_FILES["h1"])
    m15_all = _load(_FILES["m15"]); m5_all = _load(_FILES["m5"])                # PASUL 1: MK real
    as_of = m5_all[4][len(m5_all[4]) - 200]                                     # PASUL 2: aliniere cauzală
    h4 = _slice_upto(h4_all, as_of, 200); h1 = _slice_upto(h1_all, as_of, 400)
    m15 = _slice_upto(m15_all, as_of, 800); m5 = _slice_upto(m5_all, as_of, 3000)
    for tf in (h4, h1, m15, m5):
        assert tf[4][-1] <= as_of

    state = build_market_state("XAUUSD", as_of, h4=h4, h1=h1, m15=m15, m5=m5)   # PAȘII 3-8

    assert isinstance(state.regime, (Ok, Unavailable))                          # PASUL 3 — N1
    if isinstance(state.regime, Ok):
        assert isinstance(state.regime.value, RegimeState)
    assert isinstance(state.bias, (Ok, Unavailable))                            # PASUL 4 — N2
    if isinstance(state.bias, Ok):
        assert isinstance(state.bias.value, BiasState)
    assert isinstance(state.zones, (Ok, Unavailable))                           # PASUL 5 — N3
    if isinstance(state.zones, Ok):
        ranks = [z.relative_rank for z in state.zones.value.zones]
        assert ranks == list(range(1, len(state.zones.value.zones) + 1))
    for slot in state.confirmations:                                            # PASUL 6 — opportunity_id
        assert not slot.opportunity_id.startswith("zone@")
        assert slot.evidence_at > slot.decided_at                               # N4 (dovadă) DUPĂ zone_hit
        assert isinstance(slot.confirmation, (Ok, Unavailable))                 # PASUL 7 — N4 sub contract
    assert isinstance(state, MarketState) and state.as_of == as_of              # PASUL 8 — MarketState canonic

    who = {p.who for p in state.provenance}                                     # PASUL 9 — provenance
    assert {"N1_regime", "N2_bias", "N3_zones"} <= who
    for p in state.provenance:
        assert isinstance(p, Provenance) and p.who and p.timeframe and p.detector and p.version
        assert p.as_of <= as_of

    matcher = PolicyMatcher(default_policies())                                 # PASUL 10 — Policy Matcher
    matches = matcher.match(state)
    assert len(matches) == 3
    for m in matches:
        assert m.verdict in set(Verdict) and isinstance(m.provenance, Provenance)
    assert all(not m.has_validated_edge for m in matches)                       # PASUL 11 — bibliotecă EXPLORATORIE

    rec = decide(state, matches)                                                # PASUL 12 — decizia N6
    assert rec.decision is Decision.NO_TRADE

    assert rec.reason and isinstance(rec.matched_policies, tuple)               # PASUL 13 — AUDITABILĂ
    assert rec.decision_records and rec.evidence_records
    for dr in rec.decision_records:
        assert dr.outcome == "NO_TRADE" and dr.inputs_hash and dr.schema_hash   # decizia la zone_hit
    assert any(p.who == "policy_matcher" for p in rec.provenance)


# ───────────────────────────── E2E-L1: decizia IGNORĂ N4 (ceasul rămâne zone_hit) ─────────────────────────────
def _ok_regime(as_of: int) -> Ok[RegimeState]:
    rv = RegimeState(volatility=Unavailable("na", as_of), structure=Unavailable("na", as_of),
                     direction=Unavailable("na", as_of), news=Unavailable("na", as_of),
                     trend_long_share=None, trend_short_share=None, run=None, as_of_index=as_of, n_bars=200)
    return Ok(value=rv, as_of=as_of, valid_until=as_of + 1, schema_hash="REG")


def _ok_bias(as_of: int, d: Direction) -> Ok[BiasState]:
    fd = FactorDirection("structure_run_h1", d, Ok(1.0, as_of, as_of + 1, "r"),
                         "market_structure.detect_breaks", assumption=False)
    bv = BiasState(factors=(Ok(fd, as_of, as_of + 1, "f"),), direction_share_long=None,
                   direction_share_short=None, as_of_index=as_of, n_closed_bars=200, zero_eligible_fraction=None)
    return Ok(value=bv, as_of=as_of, valid_until=as_of + 1, schema_hash="BIAS")


def _ok_zones(as_of: int, attribute: str) -> Ok[ZoneMap]:
    z = Zone(zone_id="grp0@anchor1", price_anchor=100.0, band=0.25, composition=(("level", 1),), k=1,
             distance_atr=0.1, age_bars=3, attribute=attribute, relative_rank=1, evidence_available=False)
    zm = ZoneMap(zones=(z,), band_atr=0.25, reference_price=99.0, as_of_index=as_of,
                 k_label="x", sort_key="y")
    return Ok(value=zm, as_of=as_of, valid_until=as_of + 1, schema_hash="ZONES")


def _n4(conf: ZoneConfirmation) -> Ok[ZoneConfirmationResult]:
    r = ZoneConfirmationResult(confirmation=conf, persistence=0.0, progress_atr=0.0, encounters=0,
                               hit_idx=5, window_end_idx=8, descriptor_available_idx=9)
    return Ok(value=r, as_of=9, valid_until=10, schema_hash="N4")


def _state_with_n4(conf_slot: ConfirmationSlot) -> MarketState:
    return MarketState("X", 5, regime=_ok_regime(5), bias=_ok_bias(5, Direction.LONG),
                       zones=_ok_zones(5, "discount"), confirmations=(conf_slot,), provenance=())


def test_e2e_l1_decision_and_inputs_hash_exclude_n4() -> None:
    """RT E2E-L1: decizia se ia la zone_hit din N1/N2/N3. Aceleași N1/N2/N3 + N4 DIFERIT ⇒ aceeași decizie ȘI
    același inputs_hash. Dacă N4 ar intra, ceasul ar aluneca la hit+W+1 (−71% oportunități)."""
    prov = Provenance("policy_matcher", "M15", 5, "p", "v")
    match = PolicyMatch("p", Verdict.MATCH, ("R",), has_validated_edge=False, provenance=prov)
    st_accept = _state_with_n4(ConfirmationSlot("opp-1", 5, 9, _n4(ZoneConfirmation.ACCEPTANCE_BULLISH)))
    st_undet = _state_with_n4(ConfirmationSlot("opp-1", 5, 9, _n4(ZoneConfirmation.UNDETERMINED)))
    st_unavail = _state_with_n4(ConfirmationSlot("opp-1", 5, 9, Unavailable("x", 9)))

    recs = [decide(s, (match,)) for s in (st_accept, st_undet, st_unavail)]
    assert len({r.decision for r in recs}) == 1                    # N4 NU schimbă decizia
    assert len({r.decision_records[0].inputs_hash for r in recs}) == 1   # inputs_hash EXCLUDE N4
    r0 = recs[0]
    assert r0.decision_records[0].decided_at == 5                  # decizia la zone_hit (i0)
    assert r0.evidence_records[0].attached_at == 9                 # dovada la i0+W+1 (post-decizie)
    assert r0.decision_records[0].opportunity_id == r0.evidence_records[0].opportunity_id   # legate DOAR prin id


def test_e2e_l1_validated_edge_trade_is_also_independent_of_n4() -> None:
    """Chiar și un MATCH cu edge VALIDAT produce TRADE INDEPENDENT de N4 — poarta e pe edge+N1/N2/N3, nu pe N4."""
    prov = Provenance("policy_matcher", "M15", 5, "p", "v")
    match_edge = PolicyMatch("p", Verdict.MATCH, ("R",), has_validated_edge=True, provenance=prov)
    a = decide(_state_with_n4(ConfirmationSlot("o", 5, 9, _n4(ZoneConfirmation.ACCEPTANCE_BULLISH))), (match_edge,))
    b = decide(_state_with_n4(ConfirmationSlot("o", 5, 9, Unavailable("x", 9))), (match_edge,))
    assert a.decision is Decision.TRADE and b.decision is Decision.TRADE
    assert a.decision_records[0].inputs_hash == b.decision_records[0].inputs_hash


def test_recognizers_read_only_n1n2n3_not_confirmations() -> None:
    """Structural: schimbând DOAR confirmations (N4), verdictele Policy Matcher rămân identice."""
    matcher = PolicyMatcher(default_policies())
    a = matcher.match(_state_with_n4(ConfirmationSlot("o", 5, 9, _n4(ZoneConfirmation.ACCEPTANCE_BULLISH))))
    b = matcher.match(_state_with_n4(ConfirmationSlot("o", 5, 9, Unavailable("x", 9))))
    assert [(m.policy_id, m.verdict) for m in a] == [(m.policy_id, m.verdict) for m in b]


# ───────────────────────────── E2E-L2: magistrala IMPUNE tăietura ─────────────────────────────
def test_e2e_l2_bus_enforces_the_cut_rejects_lookahead() -> None:
    """Magistrala nu are încredere în tăietura apelantului — o impune. O bară M5 > as_of ⇒ ValueError."""
    n = 200
    o = [100.0] * n; h = [101.0] * n; lo = [99.0] * n; c = [100.0] * n
    good_t = list(range(1000, 1000 + n))
    as_of = good_t[-1] - 1                                          # ultima bară (1000+n-1) > as_of ⇒ lookahead
    tf = (o, h, lo, c, good_t)
    with pytest.raises(ValueError, match="lookahead"):
        build_market_state("X", as_of, h4=tf, h1=tf, m15=tf, m5=tf)


# ───────────────────────────── E2E-U1: S2 cablat (3/3) ─────────────────────────────
def test_e2e_u1_s2_policy_is_wired() -> None:
    ids = {p.policy_id for p in default_policies()}
    assert ids == {"pdl_sweep_reversal", "pdl_failed_break_fade", "pd_close_breakout"}
    assert len(default_policies()) == 3                            # trei, verificat (nu două)


def test_cascade_n1_unavailable_degrades_to_auditable_no_trade() -> None:
    """Fail-closed auditabil, fără date: N1 Unavailable → NO_TRADE cu motiv PROPAGAT (nu o presupunere)."""
    st = MarketState("X", 5, regime=Unavailable("vol_window_incomplete_warmup", 5),
                     bias=Unavailable("na", 5), zones=Unavailable("na", 5), confirmations=(), provenance=())
    rec = decide(st, PolicyMatcher(default_policies()).match(st))
    assert rec.decision is Decision.NO_TRADE
    assert rec.reason.startswith("regime_unavailable:")


def test_decision_gate_trades_only_with_validated_edge() -> None:
    """Poarta de edge: MATCH cu edge validat → TRADE; fără → NO_TRADE. NO_TRADE vine din lipsa de edge, nu din N4."""
    st = _state_with_n4(ConfirmationSlot("o", 5, 9, Unavailable("x", 9)))
    prov = Provenance("policy_matcher", "M15", 5, "p", "v")
    no_edge = PolicyMatch("p_expl", Verdict.MATCH, ("R",), has_validated_edge=False, provenance=prov)
    with_edge = PolicyMatch("p_val", Verdict.MATCH, ("R",), has_validated_edge=True, provenance=prov)
    assert decide(st, [no_edge]).decision is Decision.NO_TRADE
    assert decide(st, [with_edge]).decision is Decision.TRADE
    _ = Policy
