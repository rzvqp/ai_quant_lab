"""SHADOW — colectare PROSPECTIVĂ peste lanțul ÎNGHEȚAT (N1→N2→N3→opportunity_id→N4→PolicyMatcher→N6, commit
ad8b586). NU validare statistică. NU promovează nimic. NU trimite ordine. La fiecare bară: lanțul rulează, produce
TRADE / NO_TRADE, și se jurnalizează INTEGRAL — cu provenance urmăribil până la detector.

Acest modul e DOAR stratul de jurnalizare: importă și rulează lanțul, NU-l modifică (orice modificare a lanțului
RESETEAZĂ complet evidența Shadow). Jurnalul e APPEND-ONLY și imuabil: fiecare intrare e un instantaneu complet;
nicio intrare anterioară nu se rescrie.

DE CE: CAND-0037 are avg_R 0,062 < pragul de detecție 0,0839 chiar la varianța minimă; detectabilitatea cere
n∈[450,990]. Descoperirea e epuizată, holdout-ul sigilat. Shadow e SINGURA cale spre acel n — instrumentul, nu o
formalitate. Va produce aproape numai NO_TRADE (toate politicile edge=False, poartă conservatoare) — CORECT: Shadow
verifică LANȚUL, nu produce profit.
"""

from __future__ import annotations

import json
from typing import Sequence

from level_output import LevelOutput, Ok, Unavailable
from market_bus import (
    AuditedDecision, MarketState, PolicyMatch, PolicyMatcher, build_market_state, decide, default_policies,
)

Bars = tuple[Sequence[float], Sequence[float], Sequence[float], Sequence[float], Sequence[int]]

# versiunea lanțului înghețat pentru Shadow — orice schimbare aici marchează un RESET de evidență
CHAIN_COMMIT = "ad8b586"
SHADOW_SCHEMA = "shadow-journal-v1"


def _level_state(o: LevelOutput[object]) -> dict[str, object]:
    """Serializează starea unui nivel sub contract: Ok (cu schema/cadență) sau Unavailable (cu motiv)."""
    if isinstance(o, Ok):
        return {"state": "Ok", "as_of": o.as_of, "valid_until": o.valid_until, "schema_hash": o.schema_hash}
    return {"state": "Unavailable", "reason": o.reason, "as_of": o.as_of}


def _provenance(state: MarketState) -> list[dict[str, object]]:
    return [{"who": p.who, "timeframe": p.timeframe, "as_of": p.as_of, "detector": p.detector, "version": p.version}
            for p in state.provenance]


def _matches(matches: Sequence[PolicyMatch]) -> list[dict[str, object]]:
    return [{"policy_id": m.policy_id, "verdict": m.verdict.value, "reasons": list(m.reasons),
             "has_validated_edge": m.has_validated_edge} for m in matches]


def serialize_cycle(state: MarketState, matches: Sequence[PolicyMatch], dec: AuditedDecision) -> dict[str, object]:
    """Un instantaneu COMPLET al unui ciclu Shadow — auditat până la detector. Fără efecte laterale."""
    return {
        "shadow_schema": SHADOW_SCHEMA, "chain_commit": CHAIN_COMMIT,
        "symbol": state.symbol, "as_of": state.as_of,
        # decizia și motivul
        "decision": dec.decision.value, "reason": dec.reason, "matched_policies": list(dec.matched_policies),
        # starea fiecărui nivel (intrări de decizie N1/N2/N3 + dovada N4)
        "levels": {
            "N1_regime": _level_state(state.regime),
            "N2_bias": _level_state(state.bias),
            "N3_zones": _level_state(state.zones),
            "N4_confirmations": [
                {"opportunity_id": s.opportunity_id, "decided_at": s.decided_at, "evidence_at": s.evidence_at,
                 "confirmation": _level_state(s.confirmation)} for s in state.confirmations],
        },
        # DecisionRecord (decided_at = zone_hit; inputs_hash DOAR N1/N2/N3) — imuabil
        "decision_records": [
            {"opportunity_id": d.opportunity_id, "decided_at": d.decided_at, "outcome": d.outcome,
             "inputs_hash": d.inputs_hash, "schema_hash": d.schema_hash} for d in dec.decision_records],
        # EvidenceRecord (attached_at = i0+W+1; descriptorul N4) — separat prin tip, legat doar prin id
        "evidence_records": [
            {"opportunity_id": e.opportunity_id, "attached_at": e.attached_at,
             "descriptor": _level_state(e.descriptor)} for e in dec.evidence_records],
        # provenance: cine / timeframe / timestamp-disponibil / detector / versiune
        "provenance": _provenance(state) + [
            {"who": m.provenance.who, "timeframe": m.provenance.timeframe, "as_of": m.provenance.as_of,
             "detector": m.provenance.detector, "version": m.provenance.version} for m in matches],
        "policy_matches": _matches(matches),
    }


def run_shadow_cycle(symbol: str, as_of: int, *, h4: Bars, h1: Bars, m15: Bars, m5: Bars,
                     top_k_zones: int = 3, w_confirm: int = 3) -> dict[str, object]:
    """Un ciclu: rulează lanțul înghețat pe barele tăiate cauzal la ≤ as_of și întoarce instantaneul jurnalizabil."""
    state = build_market_state(symbol, as_of, h4=h4, h1=h1, m15=m15, m5=m5,
                               top_k_zones=top_k_zones, w_confirm=w_confirm)
    matches = PolicyMatcher(default_policies()).match(state)
    dec = decide(state, matches)
    return serialize_cycle(state, matches, dec)


class ShadowJournal:
    """Jurnal APPEND-ONLY. Nu rescrie niciodată o intrare — imuabilitate prin construcție (mod 'a')."""

    def __init__(self, path: str) -> None:
        self.path = path
        self.count = 0

    def append(self, entry: dict[str, object]) -> None:
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
        self.count += 1
