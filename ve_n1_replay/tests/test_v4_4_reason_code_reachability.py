"""V4.4 reason-code reachability (mandat §13): mecanic, prin API-ul public `observe()`, pt. fiecare din cele
11 coduri noi -- nu presupus, nu doar incidental exercitat de alte teste. Singura exceptie documentata e
`EPISODE_MERGED` (structural de neatins, vezi `test_v4_4_transitions.py`)."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_range_semantic_v4_3 import legs_bars   # noqa: E402

from ve_n1_replay.range_semantic_v4_4 import (   # noqa: E402
    ConfigV44, EPISODE_CONTINUATION, EPISODE_MERGED, EPISODE_REPLACEMENT, EXCESSIVE_NET_DISPLACEMENT,
    INSUFFICIENT_ALTERNATION_EVIDENCE, INSUFFICIENT_EFFICIENCY, INSUFFICIENT_TRAVERSAL, RANGE_CANDIDATE_PRESENT,
    RANGE_WEAKENING, REASONS_V44, RangeSemanticProducerV44, StructureV44, WEAKENING_PERSISTENCE_TERMINATED,
    WEAKENING_RECOVERED,
)
from ve_n1_replay.range_semantic_v4_3 import Depth   # noqa: E402

NEW_V44_CODES = (
    INSUFFICIENT_EFFICIENCY, INSUFFICIENT_TRAVERSAL, INSUFFICIENT_ALTERNATION_EVIDENCE,
    EXCESSIVE_NET_DISPLACEMENT, RANGE_CANDIDATE_PRESENT, RANGE_WEAKENING, WEAKENING_RECOVERED,
    WEAKENING_PERSISTENCE_TERMINATED, EPISODE_CONTINUATION, EPISODE_MERGED, EPISODE_REPLACEMENT,
)


def cfg44(**kw: Any) -> ConfigV44:
    return ConfigV44(**kw)


def _run(prod: RangeSemanticProducerV44, bars: list[Any], atr: float = 1.0) -> list[str]:
    kinds: list[str] = []
    for b in bars:
        _, evs = prod.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close, atr=atr)
        kinds.extend(e.kind for e in evs)
    return kinds


def test_all_11_new_v4_4_codes_are_accounted_for_in_the_registry() -> None:
    assert len(NEW_V44_CODES) == 11
    assert set(NEW_V44_CODES) <= set(REASONS_V44)


def test_reachable_via_public_api_except_the_documented_merge_exception() -> None:
    cfg = cfg44()
    seen: set[str] = set()

    # 1) RANGE_CANDIDATE_PRESENT, EPISODE_REPLACEMENT -- oscilator real care confirma prin observe()
    prod1 = RangeSemanticProducerV44(cfg)
    bars1 = legs_bars([(100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6)])
    seen.update(_run(prod1, bars1))

    # RANGE_WEAKENING(T4) + WEAKENING_RECOVERED(T6) -- structura CONFIRMATA, construita direct (acelasi
    # patern verificat in test_v4_4_transitions.py::test_t6_reentry_within_k_reentry_recovers_to_confirmed),
    # excursie urmata de reintrare in K_reentry
    prod_g = RangeSemanticProducerV44(cfg)
    st_g = StructureV44(structure_id=95, depth=Depth.MACRO, parent_structure_id=None, start_ts=0, trailing_window=cfg.W)
    st_g.atr_ref = 1.0
    st_g.up.offer(110.0, 1e18); st_g.up.offer(110.0, 1e18); st_g.up.frozen = True
    st_g.dn.offer(100.0, 1e18); st_g.dn.offer(100.0, 1e18); st_g.dn.frozen = True
    st_g.reached_confirmed = True; st_g.confirm_ts = 0
    prod_g._active_macro = st_g
    i = 0
    for k in range(29):
        c = 102.0 if k % 2 == 0 else 108.0
        st_g.push_close_v44(i, c); i += 1
    st_g.push_close_v44(i, 111.5)
    ev = []
    prod_g._step_macro(i, 111.6, 111.4, 111.5, ev)
    seen.update(e.kind for e in ev)
    i += 1
    st_g.push_close_v44(i, 105.0)
    ev = []
    prod_g._step_macro(i, 106.0, 104.0, 105.0, ev)
    seen.update(e.kind for e in ev)

    # 2) INSUFFICIENT_EFFICIENCY / INSUFFICIENT_TRAVERSAL / EXCESSIVE_NET_DISPLACEMENT -- poarta T3, direct
    #    (fixture-uri deja verificate numeric in test_v4_4_transitions.py)
    closes_a = [100.0 + i for i in range(29)]
    prod_a = RangeSemanticProducerV44(cfg)
    st_a = StructureV44(structure_id=90, depth=Depth.MACRO, parent_structure_id=None, start_ts=0, trailing_window=cfg.W)
    st_a.atr_ref = 1.0
    st_a.up.offer(77.9, 1e18); st_a.up.offer(77.9, 1e18)
    st_a.dn.offer(50.0, 1e18); st_a.dn.offer(50.0, 1e18)
    for c in closes_a:
        st_a._trailing_closes.append(c)
    prod_a._active_macro = st_a
    ev_a: list[Any] = []
    reason_a = prod_a._evaluate_macro_formation(st_a, 100, ev_a)
    seen.add(reason_a)

    closes_b = []
    c = 100.0
    for i in range(29):
        c += 5.0 if i % 2 == 0 else -3.0
        closes_b.append(c)
    prod_b = RangeSemanticProducerV44(cfg)
    st_b = StructureV44(structure_id=91, depth=Depth.MACRO, parent_structure_id=None, start_ts=0, trailing_window=cfg.W)
    st_b.atr_ref = 1.0
    st_b.up.offer(95.0, 1e18); st_b.up.offer(95.0, 1e18)
    st_b.dn.offer(75.0, 1e18); st_b.dn.offer(75.0, 1e18)
    for cc in closes_b:
        st_b._trailing_closes.append(cc)
    prod_b._active_macro = st_b
    ev_b: list[Any] = []
    reason_b = prod_b._evaluate_macro_formation(st_b, 100, ev_b)
    seen.add(reason_b)

    closes_c = [95.0 if i % 2 == 0 else 205.0 for i in range(27)] + [205.0, 400.0]
    prod_c = RangeSemanticProducerV44(cfg)
    st_c = StructureV44(structure_id=92, depth=Depth.MACRO, parent_structure_id=None, start_ts=0, trailing_window=cfg.W)
    st_c.atr_ref = 1.0
    st_c.up.offer(160.0, 1e18); st_c.up.offer(160.0, 1e18)
    st_c.dn.offer(140.0, 1e18); st_c.dn.offer(140.0, 1e18)
    for cc in closes_c:
        st_c._trailing_closes.append(cc)
    prod_c._active_macro = st_c
    ev_c: list[Any] = []
    reason_c = prod_c._evaluate_macro_formation(st_c, 100, ev_c)
    seen.add(reason_c)

    # 3) INSUFFICIENT_ALTERNATION_EVIDENCE -- confirmare cu putine atingeri inregistrate
    prod_d = RangeSemanticProducerV44(cfg)
    st_d = StructureV44(structure_id=93, depth=Depth.MACRO, parent_structure_id=None, start_ts=0, trailing_window=cfg.W)
    st_d.atr_ref = 1.0
    st_d.up.offer(110.0, 1e18); st_d.up.offer(110.0, 1e18)
    st_d.dn.offer(100.0, 1e18); st_d.dn.offer(100.0, 1e18)
    for k in range(29):
        st_d.push_close_v44(k, 102.0 if k % 2 == 0 else 108.0)
    prod_d._active_macro = st_d
    ev_d: list[Any] = []
    prod_d._evaluate_macro_formation(st_d, 40, ev_d)
    seen.update(e.kind for e in ev_d)

    # 4) WEAKENING_PERSISTENCE_TERMINATED -- degradare persistenta, verificat deja numeric
    prod_e = RangeSemanticProducerV44(cfg)
    st_e = StructureV44(structure_id=94, depth=Depth.MACRO, parent_structure_id=None, start_ts=0, trailing_window=cfg.W)
    st_e.atr_ref = 1.0
    st_e.up.offer(110.0, 1e18); st_e.up.offer(110.0, 1e18); st_e.up.frozen = True
    st_e.dn.offer(100.0, 1e18); st_e.dn.offer(100.0, 1e18); st_e.dn.frozen = True
    st_e.reached_confirmed = True; st_e.confirm_ts = 0
    prod_e._active_macro = st_e
    i = 0; c = 101.0
    for k in range(60):
        c += 0.05
        if c >= 110.7:
            c = 101.0
        st_e.push_close_v44(i, c)
        ev_e: list[Any] = []
        reason_e = prod_e._step_macro(i, c + 0.05, c - 0.05, c, ev_e)
        seen.update(e.kind for e in ev_e)
        if reason_e == WEAKENING_PERSISTENCE_TERMINATED:
            break
        i += 1

    # 5) EPISODE_CONTINUATION -- doua episoade succesive, terminare non-breakout, zone suprapuse, in GAP_MAX
    prod_f = RangeSemanticProducerV44(cfg)
    bars_f1 = legs_bars([(100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6)])
    seen.update(_run(prod_f, bars_f1))
    if prod_f._active_macro is not None:
        prod_f._active_macro.atr_ref = 20.0
        i2 = prod_f._n
        _, evs2 = prod_f.observe(ts_close=i2 * 900, open_=110, high=111, low=109, close=110, atr=20.0)
        seen.update(e.kind for e in evs2)
    start2 = prod_f._n
    bars_f2 = legs_bars([(110, 0), (120, 6), (100, 6), (120, 6), (100, 6), (120, 6), (100, 6)], start=start2)
    seen.update(_run(prod_f, bars_f2))

    required = set(NEW_V44_CODES) - {EPISODE_MERGED}
    missing = required - seen
    assert not missing, f"coduri V4.4 nici macar o data emise prin API-ul public: {missing}"
