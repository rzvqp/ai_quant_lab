"""Teste Shadow: instantaneul jurnalizabil e COMPLET (decizie + DecisionRecord@zone_hit + EvidenceRecord@i0+W+1 +
provenance + starea fiecărui nivel) și jurnalul e APPEND-ONLY imuabil. Fără date reale, fără rețea."""

from __future__ import annotations

import json
import os
import sys

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from level_output import Unavailable  # noqa: E402
from market_bus import ConfirmationSlot, MarketState, PolicyMatcher, decide, default_policies  # noqa: E402
from shadow_run import CHAIN_COMMIT, ShadowJournal, serialize_cycle  # noqa: E402


def _state() -> MarketState:
    # regim Unavailable → cascadă NO_TRADE; un slot cu decizie la zone_hit + dovadă N4 la i0+W+1
    slot = ConfirmationSlot("opp-1", decided_at=100, evidence_at=104, confirmation=Unavailable("no_pen", 104))
    return MarketState("XAUUSD", 500, regime=Unavailable("vol_window_incomplete_warmup", 500),
                       bias=Unavailable("na", 500), zones=Unavailable("na", 500),
                       confirmations=(slot,), provenance=())


def _cycle() -> dict[str, object]:
    st = _state()
    matches = PolicyMatcher(default_policies()).match(st)
    return serialize_cycle(st, matches, decide(st, matches))


def test_snapshot_carries_all_mandatory_fields() -> None:
    e = _cycle()
    assert e["chain_commit"] == CHAIN_COMMIT and e["decision"] == "no_trade" and e["reason"]
    lv = e["levels"]
    assert set(lv) == {"N1_regime", "N2_bias", "N3_zones", "N4_confirmations"}   # starea fiecărui nivel
    assert lv["N1_regime"]["state"] == "Unavailable" and lv["N1_regime"]["reason"]  # Unavailable cu motiv


def test_decision_record_at_zone_hit_evidence_after() -> None:
    e = _cycle()
    dr = e["decision_records"][0]; er = e["evidence_records"][0]
    assert dr["decided_at"] == 100 and dr["outcome"] == "NO_TRADE" and dr["inputs_hash"]   # zone_hit + hash N1/N2/N3
    assert er["attached_at"] == 104 and er["opportunity_id"] == dr["opportunity_id"]        # i0+W+1, legat prin id
    assert er["attached_at"] > dr["decided_at"]                                             # dovada DUPĂ decizie


def test_provenance_traceable_to_detector() -> None:
    e = _cycle()
    prov = e["provenance"]
    assert prov and all({"who", "timeframe", "as_of", "detector", "version"} <= set(p) for p in prov)
    assert any(p["detector"].startswith("pdl_") or p["detector"].startswith("pd_") for p in prov)  # până la politică


def test_journal_is_append_only_immutable(tmp_path: object) -> None:
    p = os.path.join(str(tmp_path), "shadow.jsonl")
    jr = ShadowJournal(p)
    jr.append({"as_of": 1, "decision": "no_trade"})
    first_line = open(p, encoding="utf-8").readline()
    jr.append({"as_of": 2, "decision": "no_trade"})
    lines = open(p, encoding="utf-8").read().splitlines()
    assert len(lines) == 2 and jr.count == 2
    assert lines[0] == first_line.rstrip("\n")                    # prima intrare NU s-a rescris (imuabil)
    assert json.loads(lines[0])["as_of"] == 1 and json.loads(lines[1])["as_of"] == 2
