"""RANGE vNext multi-candidate liveness tests (mandate `VE-RANGE-LIFECYCLE-VNEXT-MULTI-CANDIDATE-
RESEARCH-001` section 18). Construction/regression methodology matches every prior RANGE test file's own
established pattern (direct-construction-plus-real-orchestration-call) -- not organically-grown bars
chosen to coincidentally hit the target state, and not re-derived expectations."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_range_semantic_v4_3 import KW, legs_bars   # noqa: E402

from ve_n1_replay.range_engine_v4_4 import RangeSemanticEngineV44   # noqa: E402
from ve_n1_replay.range_engine_vnext import RangeSemanticEngineVNext, RangeSnapshotErrorVNext   # noqa: E402
from ve_n1_replay.range_semantic_v4_3 import ContractErrorV43, Depth, TOO_SHORT_MACRO   # noqa: E402
from ve_n1_replay.range_semantic_v4_4 import ConfigV44, StructureV44   # noqa: E402
from ve_n1_replay.range_semantic_vnext import (   # noqa: E402
    CANDIDATE_ABANDONED_PRICE_MOVED_ON, CANDIDATE_SUPERSEDED_BY_MERGE, ConfigVNext,
    RANGE_HIERARCHICAL_VNEXT_CONTRACT_VERSION,
    RANGE_HIERARCHICAL_VNEXT_NORMATIVE_CONFIG_ID, REASONS_VNEXT, REGISTRY_CAPACITY_REFUSED,
    RangeSemanticProducerVNext,
)


def cfg44(**kw: Any) -> ConfigV44:
    return ConfigV44(**kw)


def cfgn(**kw: Any) -> ConfigVNext:
    return ConfigVNext(**kw)


def seeded_macro(prod: RangeSemanticProducerVNext, *, structure_id: int, upper: float, lower: float,
                 atr_ref: float = 1.0, start_ts: int = 0, cfg: ConfigVNext | None = None) -> StructureV44:
    """A MACRO candidate with an established boundary, inserted DIRECTLY into the registry -- same
    direct-construction convention every prior RANGE test file already uses for `_active_macro`, now
    targeting a specific registry slot instead of the old singleton field."""
    cfg = cfg or cfgn()
    st = StructureV44(structure_id=structure_id, depth=Depth.MACRO, parent_structure_id=None,
                      start_ts=start_ts, trailing_window=cfg.W)
    st.atr_ref = atr_ref
    st.up.offer(upper, 1e18)
    st.dn.offer(lower, 1e18)
    st.record_touch_v44(start_ts, True)
    st.record_touch_v44(start_ts, False)
    prod._active_macros[structure_id] = st
    return st


# ═══════════════════════════════════ VNEXT-1: multiple simultaneous candidates ═══════════════════════════════════

def test_vnext1_two_spatially_distinct_candidates_coexist() -> None:
    """The central mandate objective, proven directly: two candidates with NON-overlapping zones both
    exist in the registry at once -- neither blocks the other."""
    cfg = cfgn()
    prod = RangeSemanticProducerVNext(cfg)
    seeded_macro(prod, structure_id=1, upper=110.0, lower=100.0, cfg=cfg)
    seeded_macro(prod, structure_id=2, upper=310.0, lower=300.0, cfg=cfg)
    assert len(prod._active_macros) == 2
    assert set(prod._active_macros) == {1, 2}


def test_vnext1b_one_stuck_plus_one_new_valid_candidate() -> None:
    """A candidate that never confirms (fed nothing further) does not prevent a SECOND, spatially distinct
    candidate from forming and confirming via the real, unmodified `_evaluate_macro_formation` gate."""
    cfg = cfgn()
    prod = RangeSemanticProducerVNext(cfg)
    stuck = seeded_macro(prod, structure_id=1, upper=110.0, lower=100.0, start_ts=0, cfg=cfg)
    fresh = seeded_macro(prod, structure_id=2, upper=310.0, lower=300.0, start_ts=0, cfg=cfg)
    # 2nd touch per side, SAME price (median unchanged -- a different price would shift the zone the
    # traversal-count check is measured against, exactly the pitfall found and fixed in the v4.5 mandate)
    fresh.up.offer(310.0, 1e18); fresh.dn.offer(300.0, 1e18)
    # closes must actually swing between the U-zone (>=boundary_upper-width/3=306.67) and L-zone
    # (<=boundary_lower+width/3=303.33) to register traversals -- a tiny wiggle around the center never
    # leaves the neutral M-zone and traversal_count stays 0 (found empirically, not assumed)
    for k in range(1, 40):
        close = 308.0 if k % 2 == 0 else 302.0
        fresh.push_close_v44(k, close)
    events: list[Any] = []
    reason = prod._evaluate_macro_formation(fresh, 39, events)
    assert reason == "OK_RANGE_MACRO"
    assert fresh.reached_confirmed is True
    # the "stuck" candidate is completely unaffected -- still present, still unconfirmed
    assert 1 in prod._active_macros
    assert stuck.reached_confirmed is False


def test_vnext1c_slow_candidate_eventually_confirming_not_blocked_by_a_second() -> None:
    """A SLOW candidate (the one this whole mandate exists to protect) reaches confirmation normally even
    though a second, unrelated candidate is concurrently active in the registry."""
    cfg = cfgn()
    prod = RangeSemanticProducerVNext(cfg)
    slow = seeded_macro(prod, structure_id=1, upper=110.0, lower=100.0, start_ts=0, cfg=cfg)
    slow.up.offer(110.0, 1e18); slow.dn.offer(100.0, 1e18)  # 2nd touch per side, SAME price -- see above
    seeded_macro(prod, structure_id=2, upper=310.0, lower=300.0, start_ts=0, cfg=cfg)
    # closes swing between U-zone (>=106.67) and L-zone (<=103.33) -- see the identical note in vnext1b
    for k in range(1, 40):
        close = 108.0 if k % 2 == 0 else 102.0
        slow.push_close_v44(k, close)
    events: list[Any] = []
    reason = prod._evaluate_macro_formation(slow, 39, events)
    assert reason == "OK_RANGE_MACRO"
    assert slow.reached_confirmed is True
    assert 2 in prod._active_macros  # the second candidate is untouched by the first one's confirmation


# ═══════════════════════════════════ VNEXT-2: candidate overlap / merge / supersession ═══════════════════════════════════

def test_vnext2_overlapping_new_candidate_merges_into_existing() -> None:
    """The central architectural finding this module is built on (see architecture doc section 2): a new
    candidate zone overlapping an ACTIVE macro's own zone (IoU >= IOU_CONTINUE) is detected as MERGE."""
    cfg = cfgn()
    prod = RangeSemanticProducerVNext(cfg)
    seeded_macro(prod, structure_id=1, upper=110.0, lower=100.0, cfg=cfg)
    action, target = prod._episode_identity_for_new_macro_multi((100.5, 109.5), 50)
    assert action == "MERGE"
    assert target == 1


def test_vnext2b_merge_properly_retires_the_superseded_candidate() -> None:
    """The one real behavioral FIX over v4.4's own dead-code MERGE branch (architecture doc section 6):
    the superseded macro is properly terminated (end_ts/end_reason set, appended to history, removed from
    the registry) -- not silently overwritten."""
    cfg = cfgn()
    prod = RangeSemanticProducerVNext(cfg)
    old = seeded_macro(prod, structure_id=7, upper=110.0, lower=100.0, cfg=cfg)
    events: list[Any] = []
    prod._supersede_macro(7, 50, events)
    assert 7 not in prod._active_macros
    assert old.end_ts == 50
    assert old.end_reason == CANDIDATE_SUPERSEDED_BY_MERGE
    assert any(h["structure_id"] == 7 and h["end_reason"] == CANDIDATE_SUPERSEDED_BY_MERGE
              for h in prod.macro_history)
    assert any(e.kind == CANDIDATE_SUPERSEDED_BY_MERGE and e.structure_id == 7 for e in events)


def test_vnext2c_merge_reachable_via_real_offer_swing_everywhere() -> None:
    """Proves MERGE is reachable through the REAL public orchestration path (`_offer_swing_everywhere`),
    not just the isolated `_episode_identity_for_new_macro_multi` helper -- this is EXACTLY what v4.4's own
    module docstring says is structurally impossible there, and is the crux of this whole mandate."""
    cfg = cfgn()
    prod = RangeSemanticProducerVNext(cfg)
    original_id = prod._registry.new_id()  # advance the registry properly, matching real usage (the v4.5
    # mandate's own established precedent) -- otherwise the LATER real new_id() call (for the merging
    # candidate) would also return 1, silently overwriting the same dict key and masking this assertion
    seeded_macro(prod, structure_id=original_id, upper=110.0, lower=100.0, start_ts=0, cfg=cfg)
    events: list[Any] = []
    # a new swing pair whose zone overlaps [100,110] substantially, but whose individual swing prices are
    # each MORE than tol_cluster*atr_ref=1.60 away from the existing cluster's own median (110.0/100.0),
    # so NEITHER is absorbed by step 1 -- forcing the flow through step-2 zone-level MERGE detection.
    # candidate_zone=(98.0,112.0) fully contains (100,110): IoU = 10/14 = 0.714 >= IOU_CONTINUE=0.5.
    prod._offer_swing_everywhere(60, 112.0, True, events)
    prod._offer_swing_everywhere(61, 98.0, False, events)
    assert any(e.kind == "EPISODE_MERGED" for e in events)
    assert any(e.kind == CANDIDATE_SUPERSEDED_BY_MERGE and e.structure_id == original_id for e in events)
    assert original_id not in prod._active_macros
    assert len(prod._active_macros) == 1  # the new, merged-in candidate replaces it
    new_id = next(iter(prod._active_macros))
    assert new_id != original_id
    assert prod._active_macros[new_id].continued_from_id == original_id


def test_vnext2d_non_overlapping_new_candidate_is_replacement_not_merge() -> None:
    cfg = cfgn()
    prod = RangeSemanticProducerVNext(cfg)
    seeded_macro(prod, structure_id=1, upper=110.0, lower=100.0, cfg=cfg)
    action, target = prod._episode_identity_for_new_macro_multi((300.0, 310.0), 50)
    assert action == "REPLACEMENT"
    assert target is None


def test_vnext2e_swing_absorbed_by_existing_cluster_never_reaches_merge_logic() -> None:
    """Step 1 (per-swing cluster tolerance) is the FIRST line of defense (architecture doc section 4) --
    a swing that lands within an existing candidate's own tolerance just extends it; no MERGE/REPLACEMENT
    decision is ever made for it."""
    cfg = cfgn()
    prod = RangeSemanticProducerVNext(cfg)
    st = seeded_macro(prod, structure_id=1, upper=110.0, lower=100.0, cfg=cfg)
    before = len(st.up.members)
    events: list[Any] = []
    prod._offer_swing_everywhere(10, 110.05, True, events)
    assert len(st.up.members) == before + 1
    assert not any(e.kind in ("EPISODE_MERGED", "EPISODE_REPLACEMENT") for e in events)
    assert len(prod._active_macros) == 1


# ═══════════════════════════════════ VNEXT-2f/2g/2h: price-abandonment supersession (added after the ═══
# exploratory measurement found registry occupancy higher than overlap-merge alone resolves -- see the
# research report; NOT age-based, reuses only the existing tol_cluster*atr_ref acceptance distance ═══════

def test_vnext2f_isolated_candidate_never_abandoned_regardless_of_price() -> None:
    """The core protection this mandate exists for: a SOLE active candidate is never retired by this
    mechanism no matter how far price has moved -- there is nothing structurally "closer" to supersede it,
    so it is left exactly as v4.4 would leave a single active macro -- waiting, not released."""
    cfg = cfgn()
    prod = RangeSemanticProducerVNext(cfg)
    seeded_macro(prod, structure_id=1, upper=110.0, lower=100.0, cfg=cfg)
    events: list[Any] = []
    prod._retire_price_abandoned_candidates(500, 5000.0, events)   # price WAY outside, only 1 candidate
    assert 1 in prod._active_macros
    assert not events


def test_vnext2g_abandoned_candidate_retired_when_a_closer_one_exists() -> None:
    cfg = cfgn()
    prod = RangeSemanticProducerVNext(cfg)
    old = seeded_macro(prod, structure_id=1, upper=110.0, lower=100.0, cfg=cfg)
    seeded_macro(prod, structure_id=2, upper=310.0, lower=300.0, cfg=cfg)
    events: list[Any] = []
    # price now near candidate 2 -- candidate 1's own distance (>> tol_cluster*atr_ref=1.6) is far larger
    prod._retire_price_abandoned_candidates(500, 305.0, events)
    assert 1 not in prod._active_macros
    assert 2 in prod._active_macros   # the CLOSER candidate is never touched
    assert old.end_reason == CANDIDATE_ABANDONED_PRICE_MOVED_ON
    assert any(e.kind == CANDIDATE_ABANDONED_PRICE_MOVED_ON and e.structure_id == 1 for e in events)


def test_vnext2h_neither_retired_when_price_still_within_tolerance_of_both() -> None:
    """Negative control: two candidates close enough together that price sits within
    tol_cluster*atr_ref=1.6 of BOTH -- neither is "abandoned", since neither exceeds its own tolerance
    band. Mirrors the mandate's own repeated lesson (section 6/12): do not release on ambiguous evidence."""
    cfg = cfgn()
    prod = RangeSemanticProducerVNext(cfg)
    seeded_macro(prod, structure_id=1, upper=110.0, lower=100.0, cfg=cfg)
    seeded_macro(prod, structure_id=2, upper=111.0, lower=101.0, cfg=cfg)
    events: list[Any] = []
    prod._retire_price_abandoned_candidates(500, 110.5, events)
    assert {1, 2} <= set(prod._active_macros)
    assert not events


def test_vnext2i_confirmed_candidates_never_retired_by_abandonment() -> None:
    """A CONFIRMED range is never touched by this mechanism, however far price has moved -- confirmation
    freezes the boundary (v4.4's own existing semantics, unchanged); only never-confirmed candidates are
    in scope for structural abandonment."""
    cfg = cfgn()
    prod = RangeSemanticProducerVNext(cfg)
    confirmed = seeded_macro(prod, structure_id=1, upper=110.0, lower=100.0, cfg=cfg)
    confirmed.reached_confirmed = True
    seeded_macro(prod, structure_id=2, upper=310.0, lower=300.0, cfg=cfg)
    events: list[Any] = []
    prod._retire_price_abandoned_candidates(500, 305.0, events)
    assert 1 in prod._active_macros
    assert not any(e.structure_id == 1 for e in events)


def test_vnext2j_reachable_via_real_observe_loop() -> None:
    """Proves the mechanism actually runs inside the real per-bar `observe()` orchestration (not just when
    called in isolation, as every other test in this section does): feeds one real bar near candidate 2
    through the public `observe()` API and confirms candidate 1 is retired as a side effect of that single
    call, with no direct call to `_retire_price_abandoned_candidates` at all."""
    cfg = cfgn()
    prod = RangeSemanticProducerVNext(cfg)
    seeded_macro(prod, structure_id=1, upper=110.0, lower=100.0, start_ts=0, cfg=cfg)
    seeded_macro(prod, structure_id=2, upper=310.0, lower=300.0, start_ts=0, cfg=cfg)
    res, events = prod.observe(ts_close=500 * 900, open_=305.0, high=305.5, low=304.5, close=305.0, atr=1.0)
    assert 1 not in prod._active_macros
    assert 2 in prod._active_macros
    assert any(e.kind == CANDIDATE_ABANDONED_PRICE_MOVED_ON and e.structure_id == 1 for e in events)


# ═══════════════════════════════════ VNEXT-3: confirmation arbitration ═══════════════════════════════════

def test_vnext3_simultaneous_confirmation_eligibility_deterministic_arbitration() -> None:
    """Mandate section 7: when multiple candidates are CONFIRMED simultaneously, the canonical selection is
    deterministic and structural (current-price containment, then nearest-boundary, then lowest id) --
    never profitability, never hindsight."""
    cfg = cfgn()
    prod = RangeSemanticProducerVNext(cfg)
    a = seeded_macro(prod, structure_id=1, upper=110.0, lower=100.0, cfg=cfg)
    b = seeded_macro(prod, structure_id=2, upper=310.0, lower=300.0, cfg=cfg)
    a.reached_confirmed = True
    b.reached_confirmed = True
    assert prod._select_canonical_macro(305.0) is b     # price inside B's own zone
    assert prod._select_canonical_macro(105.0) is a     # price inside A's own zone
    assert prod._select_canonical_macro(200.0) is a     # equidistant-ish -- nearer to A (100 vs 105) wins...
    assert prod._select_canonical_macro(1000.0) is b    # far outside both -- nearest boundary (B's 310) wins


def test_vnext3b_canonical_selection_ignores_unconfirmed_candidates() -> None:
    cfg = cfgn()
    prod = RangeSemanticProducerVNext(cfg)
    seeded_macro(prod, structure_id=1, upper=110.0, lower=100.0, cfg=cfg)  # never confirmed
    assert prod._select_canonical_macro(105.0) is None


def test_vnext3c_tie_broken_by_lowest_structure_id_deterministic() -> None:
    cfg = cfgn()
    prod = RangeSemanticProducerVNext(cfg)
    a = seeded_macro(prod, structure_id=5, upper=110.0, lower=100.0, cfg=cfg)
    b = seeded_macro(prod, structure_id=3, upper=110.0, lower=100.0, cfg=cfg)  # identical zone, lower id
    a.reached_confirmed = True
    b.reached_confirmed = True
    assert prod._select_canonical_macro(105.0) is b


# ═══════════════════════════════════ VNEXT-4: registry bound ═══════════════════════════════════

def test_vnext4_registry_capacity_refuses_gracefully_no_exception() -> None:
    cfg = cfgn(max_active_macro_candidates=1)
    prod = RangeSemanticProducerVNext(cfg)
    seeded_macro(prod, structure_id=1, upper=110.0, lower=100.0, start_ts=0, cfg=cfg)
    events: list[Any] = []
    prod._offer_swing_everywhere(60, 300.0, True, events)
    prod._offer_swing_everywhere(61, 290.0, False, events)
    assert len(prod._active_macros) == 1  # the new, non-overlapping candidate was REFUSED, not admitted
    assert any(e.kind == REGISTRY_CAPACITY_REFUSED for e in events)


def test_vnext4b_refused_swings_are_not_lost_a_later_bar_can_still_succeed() -> None:
    """Matches the existing v4.3/v4.4 convention: a refused candidate's swings are not discarded forever --
    freeing the registry lets a subsequent attempt with fresh swings succeed."""
    cfg = cfgn(max_active_macro_candidates=1)
    prod = RangeSemanticProducerVNext(cfg)
    seeded_macro(prod, structure_id=1, upper=110.0, lower=100.0, start_ts=0, cfg=cfg)
    events: list[Any] = []
    prod._offer_swing_everywhere(60, 300.0, True, events)
    prod._offer_swing_everywhere(61, 290.0, False, events)
    assert len(prod._active_macros) == 1
    del prod._active_macros[1]   # slot frees up (simulating a termination elsewhere)
    events2: list[Any] = []
    prod._offer_swing_everywhere(70, 305.0, True, events2)
    prod._offer_swing_everywhere(71, 295.0, False, events2)
    assert any(e.kind == "EPISODE_REPLACEMENT" for e in events2)
    assert len(prod._active_macros) == 1


# ═══════════════════════════════════ VNEXT-5: no future information ═══════════════════════════════════

def test_vnext5_confirmation_gate_reads_only_already_observed_bars() -> None:
    """Mechanical proof (mirrors the v4.5 mandate's own test_live1i precedent): `_evaluate_macro_formation`
    reads only `st`'s own already-accumulated fields and `i` (the current bar index) -- never a future bar,
    never a registry-wide lookahead."""
    import inspect
    src = inspect.getsource(RangeSemanticProducerVNext._evaluate_macro_formation)
    assert "self._active_macros[" not in src  # never peeks at OTHER candidates' state to confirm this one
    for forbidden in ("future", "lookahead", "peek_ahead"):
        assert forbidden not in src.lower()


# ═══════════════════════════════════ VNEXT-6: determinism / restart ═══════════════════════════════════

def test_vnext6_deterministic_replay_same_input_same_output() -> None:
    cfg = cfgn()
    bars = legs_bars([(100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (250, 4), (270, 4), (250, 4)])
    results = []
    for _ in range(3):
        engine = RangeSemanticEngineVNext(range_config=cfg, acknowledge_construction_only=True, **KW)
        run = []
        for bar in bars:
            _, res, ev = engine.observe_closed_bar(bar)
            run.append((res.macro_id, res.macro_state, res.macro_reason, res.active_macro_count,
                       res.active_macro_ids, tuple(e.kind for e in ev)))
        results.append(tuple(run))
    assert results[0] == results[1] == results[2]


def test_vnext6b_snapshot_restart_mid_multi_candidate_identical() -> None:
    cfg = cfgn()
    bars = legs_bars([(100, 0), (120, 6), (100, 6), (120, 6), (100, 6), (250, 4), (270, 4), (250, 4),
                      (270, 4), (250, 4)])

    engine_a = RangeSemanticEngineVNext(range_config=cfg, acknowledge_construction_only=True, **KW)
    continuous = []
    for bar in bars:
        _, res, ev = engine_a.observe_closed_bar(bar)
        continuous.append((res.macro_id, res.macro_state, res.active_macro_count, tuple(e.kind for e in ev)))

    engine_b = RangeSemanticEngineVNext(range_config=cfg, acknowledge_construction_only=True, **KW)
    split = len(bars) // 2
    for bar in bars[:split]:
        engine_b.observe_closed_bar(bar)
    snap = engine_b.snapshot()
    engine_c = RangeSemanticEngineVNext(range_config=cfg, acknowledge_construction_only=True, **KW)
    for bar in bars[:split]:
        engine_c.observe_closed_bar(bar)
    engine_c.restore(snap)
    resumed = []
    for bar in bars[split:]:
        _, res, ev = engine_c.observe_closed_bar(bar)
        resumed.append((res.macro_id, res.macro_state, res.active_macro_count, tuple(e.kind for e in ev)))
    assert continuous[split:] == resumed


def test_vnext6c_restore_refuses_v4_4_snapshot() -> None:
    engine44 = RangeSemanticEngineV44(range_config=cfg44(), acknowledge_construction_only=True, **KW)
    for bar in legs_bars([(105.0, 3), (106.0, 3)]):
        engine44.observe_closed_bar(bar)
    snap44 = engine44.snapshot()
    engine_n = RangeSemanticEngineVNext(range_config=cfgn(), acknowledge_construction_only=True, **KW)
    import pytest
    with pytest.raises(RangeSnapshotErrorVNext):
        engine_n.restore(snap44)


def test_vnext6d_registry_survives_snapshot_restore_exactly() -> None:
    """Targeted check that the FULL multi-candidate registry (not just a singleton) round-trips through
    snapshot/restore -- both active macro ids, their own boundaries and touch counts."""
    cfg = cfgn()
    prod = RangeSemanticProducerVNext(cfg)
    seeded_macro(prod, structure_id=1, upper=110.0, lower=100.0, cfg=cfg)
    seeded_macro(prod, structure_id=2, upper=310.0, lower=300.0, cfg=cfg)
    snap = prod.snapshot_state()
    prod2 = RangeSemanticProducerVNext(cfg)
    prod2.restore_state(snap)
    assert set(prod2._active_macros) == {1, 2}
    assert prod2._active_macros[1].boundary_upper == 110.0
    assert prod2._active_macros[2].boundary_lower == 300.0


# ═══════════════════════════════════ VNEXT-7: v4.4 regression -- byte-untouched ═══════════════════════════════════

def test_vnext7_v4_4_module_byte_untouched() -> None:
    import subprocess
    out = subprocess.run(
        ["git", "diff", "--stat", "HEAD", "--", "range_semantic_v4_4.py", "range_engine_v4_4.py"],
        cwd=str(Path(__file__).resolve().parent.parent / "ve_n1_replay"), capture_output=True, text=True)
    assert out.stdout.strip() == "", f"v4.4 must remain byte-untouched, but git diff shows: {out.stdout}"


def test_vnext7b_v4_4_producer_still_single_slot_unaffected_by_vnext_existing() -> None:
    """vNext's mere existence changes nothing about v4.4's own real, single-slot behavior."""
    from ve_n1_replay.range_semantic_v4_4 import RangeSemanticProducerV44
    prod44 = RangeSemanticProducerV44(cfg44())
    st1 = StructureV44(structure_id=1, depth=Depth.MACRO, parent_structure_id=None, start_ts=0,
                       trailing_window=cfg44().W)
    st1.atr_ref = 1.0
    st1.up.offer(110.0, 1e18); st1.dn.offer(100.0, 1e18)
    st1.record_touch_v44(0, True); st1.record_touch_v44(0, False)
    prod44._active_macro = st1
    action, target = prod44._episode_identity_for_new_macro((100.5, 109.5), 50)
    assert action == "MERGE"  # the geometry itself still resolves to MERGE...
    # ...but v4.4's own public observe() can never reach this call while a macro is active (unchanged,
    # untouched) -- proven already by v4.4's own test_v4_4_transitions.py; not re-proven here


# ═══════════════════════════════════ VNEXT-8: no M5 / M15 authority preserved ═══════════════════════════════════

def test_vnext8_no_m5_timeframe_reference_anywhere_in_vnext() -> None:
    import inspect
    from ve_n1_replay import range_engine_vnext as eng_mod
    from ve_n1_replay import range_semantic_vnext as sem_mod
    for mod in (eng_mod, sem_mod):
        src = inspect.getsource(mod)
        assert '"5m"' not in src and "'5m'" not in src, f"{mod.__name__} must never hardcode an M5 timeframe"
        assert "H1RangeDetector" not in src and "H4RangeDetector" not in src


def test_vnext8b_engine_requires_explicit_timeframe_no_default() -> None:
    import inspect
    sig = inspect.signature(RangeSemanticEngineVNext.__init__)
    assert sig.parameters["timeframe"].default is inspect.Parameter.empty


# ═══════════════════════════════════ VNEXT-9: identity ═══════════════════════════════════

def test_vnext9_identity_distinct_from_all_prior_versions() -> None:
    from ve_n1_replay.range_semantic_v4_4 import RANGE_HIERARCHICAL_V4_4_NORMATIVE_CONFIG_ID
    from ve_n1_replay.range_semantic_v4_4_1 import RANGE_HIERARCHICAL_V4_4_1_NORMATIVE_CONFIG_ID
    from ve_n1_replay.range_semantic_v4_5 import RANGE_HIERARCHICAL_V4_5_NORMATIVE_CONFIG_ID
    assert RANGE_HIERARCHICAL_VNEXT_CONTRACT_VERSION == "range-hierarchical-vnext-multicandidate-v1"
    assert RANGE_HIERARCHICAL_VNEXT_NORMATIVE_CONFIG_ID not in (
        RANGE_HIERARCHICAL_V4_4_NORMATIVE_CONFIG_ID, RANGE_HIERARCHICAL_V4_4_1_NORMATIVE_CONFIG_ID,
        RANGE_HIERARCHICAL_V4_5_NORMATIVE_CONFIG_ID)


def test_vnext9b_all_inherited_thresholds_byte_identical_to_v4_4() -> None:
    c44, cn = cfg44(), cfgn()
    for field in ("d_macro", "d_internal", "n_touch", "K_reentry", "N_accept", "K_struct",
                 "n_external_swings", "atr_window", "w_atr", "ER_max", "RND_max", "ALT_MIN",
                 "MIN_TRAVERSALS", "W", "ER_weakening", "RND_weakening", "WEAKENING_MAX_BARS",
                 "IOU_CONTINUE", "GAP_MAX"):
        assert getattr(c44, field) == getattr(cn, field), f"{field} diverged from the frozen v4.4 value"
    assert len(REASONS_VNEXT) == 43


# ═══════════════════════════════════ VNEXT-10: no strategy/P&L/future-bar contamination ═══════════════════════════════════

def test_vnext10_no_pnl_or_strategy_outcome_field_anywhere() -> None:
    import inspect
    from ve_n1_replay import range_engine_vnext as eng_mod
    from ve_n1_replay import range_semantic_vnext as sem_mod
    for mod in (eng_mod, sem_mod):
        src = inspect.getsource(mod)
        for forbidden in ("pnl", "win_rate", "profit", "expectancy", "trade_outcome"):
            # excludes the module docstring's own disclosure sentence (e.g. "no p&l/wr/rr data is read
            # anywhere here") from the scan -- it explains an absence, it is not a live reference
            body = src.split('"""', 2)[-1] if src.startswith('"""') else src
            assert forbidden not in body.lower(), f"{mod.__name__} must never reference {forbidden!r}"


# ═══════════════════════════════════ VNEXT-11: hard-cap structural invariant (remediation
# VE-RANGE-VNEXT-HARD-CAP-REMEDIATION-001) ═══════════════════════════════════
# Statistician's independent validation (commit `54fa51f`) reproduced cap=3 / active-reached=34 with zero
# REGISTRY_CAPACITY_REFUSED events: the capacity check at the registry insertion point only gated
# `action == "REPLACEMENT"`, leaving CONTINUATION free to add candidates past the configured cap without
# limit. These tests reproduce the exact blocker via the real registry-mutating path
# (`_offer_swing_everywhere`, never the isolated identity function alone), then verify the fix under every
# action type and combination the remediation mandate requires.

def test_vnext11_mandatory_continuation_at_capacity_is_refused_not_admitted() -> None:
    """The Statistician's exact reproduction. cap=3, registry full with 3 spatially distinct candidates, a
    CONTINUATION-eligible swing pair arrives (matches a recently, non-breakout-terminated zone within
    GAP_MAX, per the real `_episode_identity_for_new_macro_multi` precedence). Required result: active
    count stays <=3, REGISTRY_CAPACITY_REFUSED is emitted, no unrelated candidate disappears, and repeating
    the identical attempt changes nothing (deterministic refusal, not a one-shot check)."""
    cfg = cfgn(max_active_macro_candidates=3)
    prod = RangeSemanticProducerVNext(cfg)
    seeded_macro(prod, structure_id=1, upper=110.0, lower=100.0, start_ts=0, cfg=cfg)
    seeded_macro(prod, structure_id=2, upper=310.0, lower=300.0, start_ts=0, cfg=cfg)
    seeded_macro(prod, structure_id=3, upper=510.0, lower=500.0, start_ts=0, cfg=cfg)
    # simulate a 4th macro (id=99), spatially distinct from 1/2/3, that terminated non-breakout 5 bars ago
    # -- well within GAP_MAX=12 -- at zone [700,710] (direct-field setup, the same established convention
    # `seeded_macro` itself already uses for `_active_macros`)
    prod._last_terminated_macro_zone = (700.0, 710.0)
    prod._last_terminated_macro_end_ts = 45
    prod._last_terminated_macro_id = 99
    prod._last_terminated_macro_end_reason = TOO_SHORT_MACRO
    events: list[Any] = []
    # IoU>=0.5 against [700,710] -- the same 0.714 IoU construction proven in test_vnext2c -- and
    # non-overlapping with macros 1/2/3: CONTINUATION, not MERGE or REPLACEMENT
    prod._offer_swing_everywhere(50, 712.0, True, events)
    prod._offer_swing_everywhere(51, 698.0, False, events)
    assert set(prod._active_macros) == {1, 2, 3}, "no unrelated candidate may disappear"
    assert len(prod._active_macros) == 3
    assert any(e.kind == REGISTRY_CAPACITY_REFUSED for e in events)
    assert not any(e.kind == "EPISODE_CONTINUATION" for e in events), "the refused action must not complete"
    # determinism: repeating the identical attempt changes nothing
    events2: list[Any] = []
    prod._offer_swing_everywhere(52, 712.0, True, events2)
    prod._offer_swing_everywhere(53, 698.0, False, events2)
    assert any(e.kind == REGISTRY_CAPACITY_REFUSED for e in events2)
    assert set(prod._active_macros) == {1, 2, 3}
    assert len(prod._active_macros) == 3


def test_vnext11b_replacement_at_capacity_still_refused_regression_guard() -> None:
    """The pre-existing REPLACEMENT-at-capacity behavior (already covered by test_vnext4) must survive the
    remediation unchanged -- an explicit regression guard alongside the new CONTINUATION coverage."""
    cfg = cfgn(max_active_macro_candidates=3)
    prod = RangeSemanticProducerVNext(cfg)
    seeded_macro(prod, structure_id=1, upper=110.0, lower=100.0, start_ts=0, cfg=cfg)
    seeded_macro(prod, structure_id=2, upper=310.0, lower=300.0, start_ts=0, cfg=cfg)
    seeded_macro(prod, structure_id=3, upper=510.0, lower=500.0, start_ts=0, cfg=cfg)
    events: list[Any] = []
    prod._offer_swing_everywhere(50, 912.0, True, events)
    prod._offer_swing_everywhere(51, 898.0, False, events)
    assert any(e.kind == REGISTRY_CAPACITY_REFUSED for e in events)
    assert set(prod._active_macros) == {1, 2, 3}
    assert len(prod._active_macros) == 3


def test_vnext11c_merge_at_capacity_succeeds_net_zero_registry_size_unchanged() -> None:
    """MERGE is the one action that frees a slot in the SAME operation (`_supersede_macro` removes the
    target before the new candidate is inserted) -- it must NOT be refused purely for being at capacity,
    and the registry must land at exactly the same size, never cap+1."""
    cfg = cfgn(max_active_macro_candidates=3)
    prod = RangeSemanticProducerVNext(cfg)
    # advance the registry counter past 1/2/3 first (test_vnext2c's own established fix for this exact
    # pitfall) -- otherwise the merge's own new_id() call below would ALSO return 1, silently overwriting
    # the same dict key rather than proving supersession actually happened
    for _ in range(3):
        prod._registry.new_id()
    seeded_macro(prod, structure_id=1, upper=110.0, lower=100.0, start_ts=0, cfg=cfg)
    seeded_macro(prod, structure_id=2, upper=310.0, lower=300.0, start_ts=0, cfg=cfg)
    seeded_macro(prod, structure_id=3, upper=510.0, lower=500.0, start_ts=0, cfg=cfg)
    events: list[Any] = []
    # IoU>=0.5 against macro 1's own zone [100,110] -- the same 0.714 construction as test_vnext2c
    prod._offer_swing_everywhere(50, 112.0, True, events)
    prod._offer_swing_everywhere(51, 98.0, False, events)
    assert any(e.kind == "EPISODE_MERGED" for e in events)
    assert not any(e.kind == REGISTRY_CAPACITY_REFUSED for e in events)
    assert len(prod._active_macros) == 3
    assert 1 not in prod._active_macros, "the merge target must be superseded, not left dangling"
    assert {2, 3} <= set(prod._active_macros)


def test_vnext11d_repeated_continuation_attempts_all_refused_deterministically() -> None:
    """Multiple separate attempts at the SAME capacity-exceeding CONTINUATION, across several bars, must
    ALL be refused identically -- not admitted on a later attempt due to any accumulated state leak."""
    cfg = cfgn(max_active_macro_candidates=3)
    prod = RangeSemanticProducerVNext(cfg)
    seeded_macro(prod, structure_id=1, upper=110.0, lower=100.0, start_ts=0, cfg=cfg)
    seeded_macro(prod, structure_id=2, upper=310.0, lower=300.0, start_ts=0, cfg=cfg)
    seeded_macro(prod, structure_id=3, upper=510.0, lower=500.0, start_ts=0, cfg=cfg)
    prod._last_terminated_macro_zone = (700.0, 710.0)
    prod._last_terminated_macro_end_ts = 45
    prod._last_terminated_macro_id = 99
    prod._last_terminated_macro_end_reason = TOO_SHORT_MACRO
    for attempt, (bar_hi, bar_lo) in enumerate([(50, 51), (52, 53), (54, 55)]):
        events: list[Any] = []
        prod._offer_swing_everywhere(bar_hi, 712.0, True, events)
        prod._offer_swing_everywhere(bar_lo, 698.0, False, events)
        assert any(e.kind == REGISTRY_CAPACITY_REFUSED for e in events), f"attempt {attempt} was not refused"
        assert set(prod._active_macros) == {1, 2, 3}, f"attempt {attempt} changed the registry"


def test_vnext11e_mixed_sequence_invariant_holds_after_every_single_operation() -> None:
    """A sequence mixing all three action types at/near capacity -- len<=cap must hold after EVERY
    operation, not just at the end, and a genuinely freed slot must correctly re-admit a new candidate
    afterward (capacity refusal is not permanent once room exists)."""
    cfg = cfgn(max_active_macro_candidates=3)
    prod = RangeSemanticProducerVNext(cfg)
    # advance the registry counter past 1/2/3 first (test_vnext2c's own established fix) -- step 3 below
    # merges and would otherwise reuse id 1 for the new structure, masking the supersession assertion
    for _ in range(3):
        prod._registry.new_id()
    seeded_macro(prod, structure_id=1, upper=110.0, lower=100.0, start_ts=0, cfg=cfg)
    seeded_macro(prod, structure_id=2, upper=310.0, lower=300.0, start_ts=0, cfg=cfg)
    seeded_macro(prod, structure_id=3, upper=510.0, lower=500.0, start_ts=0, cfg=cfg)
    assert len(prod._active_macros) <= cfg.max_active_macro_candidates

    # 1) REPLACEMENT attempt at capacity -- refused
    events1: list[Any] = []
    prod._offer_swing_everywhere(50, 912.0, True, events1)
    prod._offer_swing_everywhere(51, 898.0, False, events1)
    assert any(e.kind == REGISTRY_CAPACITY_REFUSED for e in events1)
    assert len(prod._active_macros) <= cfg.max_active_macro_candidates

    # 2) CONTINUATION attempt at capacity -- refused
    prod._last_terminated_macro_zone = (700.0, 710.0)
    prod._last_terminated_macro_end_ts = 45
    prod._last_terminated_macro_id = 99
    prod._last_terminated_macro_end_reason = TOO_SHORT_MACRO
    events2: list[Any] = []
    prod._offer_swing_everywhere(52, 712.0, True, events2)
    prod._offer_swing_everywhere(53, 698.0, False, events2)
    assert any(e.kind == REGISTRY_CAPACITY_REFUSED for e in events2)
    assert len(prod._active_macros) <= cfg.max_active_macro_candidates

    # 3) MERGE attempt at capacity -- succeeds, net-zero
    events3: list[Any] = []
    prod._offer_swing_everywhere(54, 112.0, True, events3)
    prod._offer_swing_everywhere(55, 98.0, False, events3)
    assert any(e.kind == "EPISODE_MERGED" for e in events3)
    assert 1 not in prod._active_macros
    assert len(prod._active_macros) == 3

    # 4) a real termination frees a slot -- a subsequent REPLACEMENT now succeeds
    freed_id = next(iter(set(prod._active_macros) - {2, 3}))   # the id that replaced 1 via merge
    events4: list[Any] = []
    prod._kill_macro(freed_id, 56, TOO_SHORT_MACRO, events4)
    assert len(prod._active_macros) == 2
    events5: list[Any] = []
    prod._offer_swing_everywhere(57, 912.0, True, events5)
    prod._offer_swing_everywhere(58, 898.0, False, events5)
    assert any(e.kind == "EPISODE_REPLACEMENT" for e in events5)
    assert not any(e.kind == REGISTRY_CAPACITY_REFUSED for e in events5)
    assert len(prod._active_macros) == 3


def test_vnext11f_snapshot_restore_at_capacity_preserves_exact_registry() -> None:
    cfg = cfgn(max_active_macro_candidates=3)
    prod = RangeSemanticProducerVNext(cfg)
    seeded_macro(prod, structure_id=1, upper=110.0, lower=100.0, start_ts=0, cfg=cfg)
    seeded_macro(prod, structure_id=2, upper=310.0, lower=300.0, start_ts=0, cfg=cfg)
    seeded_macro(prod, structure_id=3, upper=510.0, lower=500.0, start_ts=0, cfg=cfg)
    snap = prod.snapshot_state()
    restored = RangeSemanticProducerVNext(cfg)
    restored.restore_state(snap)
    assert set(restored._active_macros) == {1, 2, 3}
    assert len(restored._active_macros) == 3
    for mid in (1, 2, 3):
        assert restored._active_macros[mid].boundary_upper == prod._active_macros[mid].boundary_upper
        assert restored._active_macros[mid].boundary_lower == prod._active_macros[mid].boundary_lower


def test_vnext11g_post_restore_capacity_still_enforced() -> None:
    """Capacity refusal must not be a construction-only check -- a producer rebuilt via `restore_state`
    must refuse an over-cap admission exactly like a freshly-constructed one."""
    cfg = cfgn(max_active_macro_candidates=3)
    prod = RangeSemanticProducerVNext(cfg)
    seeded_macro(prod, structure_id=1, upper=110.0, lower=100.0, start_ts=0, cfg=cfg)
    seeded_macro(prod, structure_id=2, upper=310.0, lower=300.0, start_ts=0, cfg=cfg)
    seeded_macro(prod, structure_id=3, upper=510.0, lower=500.0, start_ts=0, cfg=cfg)
    snap = prod.snapshot_state()
    restored = RangeSemanticProducerVNext(cfg)
    restored.restore_state(snap)
    events: list[Any] = []
    restored._offer_swing_everywhere(60, 912.0, True, events)
    restored._offer_swing_everywhere(61, 898.0, False, events)
    assert any(e.kind == REGISTRY_CAPACITY_REFUSED for e in events)
    assert len(restored._active_macros) == 3
    assert set(restored._active_macros) == {1, 2, 3}
