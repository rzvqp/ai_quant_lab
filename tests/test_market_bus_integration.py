"""DoD — DEMONSTRAȚIA END-TO-END (cei 13 pași). NU „teste verzi": scopul e ca LANȚUL să producă o DECIZIE
AUDITABILĂ pe date reale, mergând pe calea canonică. NO_TRADE e rezultatul corect (biblioteca e EXPLORATORIE /
level-fade fat-tail) — DoD cere o decizie auditabilă, nu una TRADE.

Traseul: MK real (H4/H1/M15/M5) → aliniere cauzală → N1 regim → N2 direcție → N3 hartă ranked → opportunity_id →
N4 confirmare → MarketState canonic (+provenance) → Policy Matcher → status edge bibliotecă → decizia N6 → audit.

Se sare dacă lipsesc CSV-urile de piață. Fără MT5, fără rețea.
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

from bias_h1 import BiasState  # noqa: E402
from level_output import Ok, Unavailable  # noqa: E402
from market_bus import (  # noqa: E402
    Decision, MarketState, PolicyMatcher, Provenance, Verdict, build_market_state, decide, default_policies,
)
from regime_classifier import RegimeState  # noqa: E402
from zone_map import ZoneMap  # noqa: E402

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
    """Bare ÎNCHISE cu time ≤ as_of (cauzal), cele mai recente `tail`."""
    o, h, l, c, t = bars
    hi = 0
    while hi < len(t) and t[hi] <= as_of:
        hi += 1
    lo = max(0, hi - tail)
    return o[lo:hi], h[lo:hi], l[lo:hi], c[lo:hi], t[lo:hi]


@pytest.mark.skipif(not _HAVE_DATA, reason="CSV-uri de piață absente")
def test_end_to_end_produces_an_auditable_decision() -> None:
    # ── PASUL 1: MK real — cele patru timeframe-uri ratificate ──
    h4_all = _load(_FILES["h4"]); h1_all = _load(_FILES["h1"])
    m15_all = _load(_FILES["m15"]); m5_all = _load(_FILES["m5"])

    # ── PASUL 2: aliniere CAUZALĂ la timestamp-ul deciziei (ultima bară M5 închisă disponibilă) ──
    as_of = m5_all[4][len(m5_all[4]) - 200]          # lăsăm istoric în față și în spate
    h4 = _slice_upto(h4_all, as_of, 200)
    h1 = _slice_upto(h1_all, as_of, 400)
    m15 = _slice_upto(m15_all, as_of, 800)
    m5 = _slice_upto(m5_all, as_of, 3000)
    for tf in (h4, h1, m15, m5):
        assert tf[4][-1] <= as_of                    # nicio bară din viitor (cauzalitate)

    # ── PAȘII 3-8: asamblarea rulează N1→N2→N3→opportunity_id→N4 și construiește MarketState (+provenance) ──
    state = build_market_state("XAUUSD", as_of, h4=h4, h1=h1, m15=m15, m5=m5)

    # PASUL 3 — N1 regim (H4), sub contract
    assert isinstance(state.regime, (Ok, Unavailable))
    if isinstance(state.regime, Ok):
        assert isinstance(state.regime.value, RegimeState)

    # PASUL 4 — N2 direcție (H1), sub contract, cu semantică direcțională
    assert isinstance(state.bias, (Ok, Unavailable))
    if isinstance(state.bias, Ok):
        assert isinstance(state.bias.value, BiasState)

    # PASUL 5 — N3 hartă ranked (M15), re-ancorată
    assert isinstance(state.zones, (Ok, Unavailable))
    if isinstance(state.zones, Ok):
        zm = state.zones.value
        assert isinstance(zm, ZoneMap)
        ranks = [z.relative_rank for z in zm.zones]
        assert ranks == list(range(1, len(zm.zones) + 1))          # ordonare declarată (1..N)

    # PASUL 6 — opportunity_id: cheie surogat (geometrie+ciclu de viață), NU indexul barei
    for opp_id, _conf in state.confirmations:
        assert not opp_id.startswith("zone@")                      # niciodată „zone@bară"

    # PASUL 7 — N4 confirmare (M5, W=3), sub contract (UNDETERMINED = Ok, nu Unavailable)
    for _opp_id, conf in state.confirmations:
        assert isinstance(conf, (Ok, Unavailable))

    # PASUL 8 — MarketState canonic: agregă cele patru nivele RATIFICATE sub LevelOutput
    assert isinstance(state, MarketState) and state.as_of == as_of

    # ── PASUL 9: provenance — cine/timeframe/timestamp-disponibil/detector/versiune, per nivel ──
    who = {p.who for p in state.provenance}
    assert {"N1_regime", "N2_bias", "N3_zones"} <= who             # N4 doar dacă zonele-s Ok
    for p in state.provenance:
        assert isinstance(p, Provenance) and p.who and p.timeframe and p.detector and p.version
        assert p.as_of <= as_of                                   # timestamp DISPONIBIL, nu viitor

    # ── PASUL 10: Policy Matcher — reguli de recunoaștere PDH/PDL generalizate, MATCH/NO_MATCH/WAITING ──
    matcher = PolicyMatcher(default_policies())
    matches = matcher.match(state)
    assert len(matches) == 2
    for m in matches:
        assert m.verdict in set(Verdict) and isinstance(m.provenance, Provenance)

    # ── PASUL 11: biblioteca de strategii — EXPLORATORIE, 0 validate (level-fade fat-tail) ──
    assert all(not m.has_validated_edge for m in matches)

    # ── PASUL 12: decizia N6 (poarta de edge) — NO_TRADE fiindcă niciun MATCH n-are edge validat ──
    rec = decide(state, matches)
    assert rec.decision is Decision.NO_TRADE                        # corect, NU un defect

    # ── PASUL 13: decizia e AUDITABILĂ — motiv + politici + ÎNTREAGA urmă de provenance ──
    assert rec.reason and isinstance(rec.matched_policies, tuple)
    assert len(rec.provenance) >= len(state.provenance)            # include provenance-ul nivelelor + al politicilor
    assert any(p.who == "policy_matcher" for p in rec.provenance)


@pytest.mark.skipif(not _HAVE_DATA, reason="CSV-uri de piață absente")
def test_cascade_n1_unavailable_degrades_to_auditable_no_trade() -> None:
    """Fail-closed auditabil: cu prea puține bare H4, N1 e Unavailable → lanțul spune NO_TRADE cu motiv PROPAGAT,
    nu o presupunere. (Cascada de contract: N2 primește axele indisponibile; decizia citește motivul lui N1.)"""
    m5_all = _load(_FILES["m5"])
    as_of = m5_all[4][len(m5_all[4]) - 200]
    tiny_h4 = _slice_upto(_load(_FILES["h4"]), as_of, 3)           # < 30 bare → N1 Unavailable
    state = build_market_state(
        "XAUUSD", as_of, h4=tiny_h4,
        h1=_slice_upto(_load(_FILES["h1"]), as_of, 400),
        m15=_slice_upto(_load(_FILES["m15"]), as_of, 800),
        m5=_slice_upto(m5_all, as_of, 3000))
    assert isinstance(state.regime, Unavailable)
    rec = decide(state, PolicyMatcher(default_policies()).match(state))
    assert rec.decision is Decision.NO_TRADE
    assert rec.reason.startswith("regime_unavailable:")           # motivul lui N1 e PROPAGAT în decizie


def test_decision_gate_would_trade_only_with_validated_edge() -> None:
    """Poarta de edge, izolată (fără date): un MATCH cu edge VALIDAT ar produce TRADE; unul fără, NO_TRADE.
    Demonstrează că NO_TRADE vine din LIPSA de edge validat, nu dintr-un lanț rupt."""
    from market_bus import Policy, PolicyMatch

    empty = MarketState("X", 0, regime=Ok(value=None, as_of=0, valid_until=1, schema_hash="h"),  # type: ignore[arg-type]
                        bias=Unavailable("na", 0), zones=Unavailable("na", 0), confirmations=(), provenance=())
    prov = Provenance("policy_matcher", "M15", 0, "p", "v")
    no_edge = PolicyMatch("p_exploratory", Verdict.MATCH, ("R",), has_validated_edge=False, provenance=prov)
    with_edge = PolicyMatch("p_validated", Verdict.MATCH, ("R",), has_validated_edge=True, provenance=prov)
    assert decide(empty, [no_edge]).decision is Decision.NO_TRADE
    assert decide(empty, [with_edge]).decision is Decision.TRADE   # doar edge VALIDAT deschide TRADE
    _ = Policy                                                     # simbol reutilizabil (recunoaștere per politică)
