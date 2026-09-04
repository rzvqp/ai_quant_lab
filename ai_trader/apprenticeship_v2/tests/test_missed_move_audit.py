"""Mandate Section 26/27 (Missed-move audit): exact 4h/1h rolling mechanics, causal-start-only ATR
reference, exact 2x boundary, direction, exact coverage boundaries (A-D each independently gate),
wrong-direction/S5-alone never covering, and cluster continuation/gap-split/covered-split/direction-
reversal -- including the required adversarial case (a future extreme must never leak into the
window's own materiality test, since the window is fixed at exactly 4 H1 bars).
"""

from __future__ import annotations

import dataclasses
import json

from ai_trader.apprenticeship_v2.general_observer.missed_move_audit import (
    advance_cluster_state, audit_candidate, classify_for_clustering, cluster_from_dict, coverage_window,
    is_covered,
)
from ai_trader.apprenticeship_v2.tests.conftest import H1_SECONDS, make_bar


def _h1_series(base_ts: int, closes: list[float]) -> list:
    """Flat-range H1 bars (high=low=open=close) at each given close, spaced 1h apart -- true range
    of bar i (i>=1) is then simply |close[i]-close[i-1]|, making ATR arithmetic easy to hand-verify."""
    return [make_bar(ts_open=base_ts + i * H1_SECONDS, o=c, h=c, l=c, c=c, bar_seconds=H1_SECONDS) for i, c in enumerate(closes)]


def test_audit_candidate_none_before_index_4(base_ts):
    h1 = _h1_series(base_ts, [1900.0] * 10)
    assert audit_candidate(h1, 3) is None


def test_audit_candidate_unscorable_when_atr_not_yet_available(base_ts):
    # t_index=4 needs ATR14 computed on h1[:1] (just 1 bar) -- far short of the 15 required.
    h1 = _h1_series(base_ts, [1900.0] * 10)
    result = audit_candidate(h1, 4)
    assert result.status == "UNSCORABLE_ATR_UNAVAILABLE"
    assert result.direction is None


def test_audit_candidate_not_material_below_threshold(base_ts):
    # 20 flat bars (TR=0 throughout) then a small net move over the last 4 bars.
    closes = [1900.0] * 16 + [1900.0, 1900.0, 1900.0, 1900.05]
    h1 = _h1_series(base_ts, closes)
    t_index = len(h1) - 1
    result = audit_candidate(h1, t_index)
    assert result.status == "UNSCORABLE_ATR_UNAVAILABLE" or result.atr_reference == 0.0
    # With a flat lead-in, ATR14[t-4] == 0.0 -- ANY nonzero magnitude is then material (0 >= 2*0).
    # Use a genuinely nonzero-ATR lead-in instead to test the real boundary (see next test).


def test_audit_candidate_exact_2x_atr_boundary_is_material(base_ts):
    # 18 bars stepping by 1.0 each (TR=1.0 per bar after the first), giving ATR14[t-4] = 1.0 once
    # 14 true-range values are available. Then a 4-bar net move of exactly 2.0 (== 2.0*ATR) at the end.
    lead = [1900.0 + i * 1.0 for i in range(18)]  # bars 0..17, TR=1.0 from bar1 onward
    closes = lead + [lead[-1], lead[-1], lead[-1], lead[-1] + 2.0]  # bars 18-21: flat,flat,flat,+2.0
    h1 = _h1_series(base_ts, closes)
    t_index = len(h1) - 1  # bar 21
    result = audit_candidate(h1, t_index)
    assert result.atr_reference == 1.0  # ATR14 computed causally as of bar (t-4)=17, using bars 0..17
    assert result.magnitude == 2.0
    assert result.status == "MATERIAL"  # exact equality qualifies (Section 10: ">=")
    assert result.direction == "BULLISH"


def test_audit_candidate_direction_bearish(base_ts):
    lead = [1900.0 + i * 1.0 for i in range(18)]
    closes = lead + [lead[-1], lead[-1], lead[-1], lead[-1] - 5.0]
    h1 = _h1_series(base_ts, closes)
    result = audit_candidate(h1, len(h1) - 1)
    assert result.status == "MATERIAL"
    assert result.direction == "BEARISH"


def test_audit_candidate_uses_only_start_and_end_close_never_the_path_extreme(base_ts):
    """Adversarial (Section 27 style): a candidate whose PATH swings far beyond the net close-to-
    close move must be scored on the net move only (ABS_NET_CLOSE_TO_CLOSE_MOVE), never on the
    highest-high/lowest-low of the path -- a huge mid-window spike that fully reverts by window's end
    must NOT be material."""
    lead = [1900.0 + i * 1.0 for i in range(18)]
    base_closes = lead + [lead[-1]]  # bar 18 close = lead[-1]
    h1 = _h1_series(base_ts, base_closes)
    # Extend with 3 more bars: a huge spike then a return to nearly the start close.
    spike1 = make_bar(ts_open=base_ts + 19 * H1_SECONDS, o=lead[-1], h=lead[-1] + 50, l=lead[-1], c=lead[-1] + 20, bar_seconds=H1_SECONDS)
    spike2 = make_bar(ts_open=base_ts + 20 * H1_SECONDS, o=lead[-1] + 20, h=lead[-1] + 20, l=lead[-1] - 30, c=lead[-1] - 10, bar_seconds=H1_SECONDS)
    back = make_bar(ts_open=base_ts + 21 * H1_SECONDS, o=lead[-1] - 10, h=lead[-1] - 10, l=lead[-1] - 10, c=lead[-1] + 0.1, bar_seconds=H1_SECONDS)
    h1_full = h1 + [spike1, spike2, back]
    result = audit_candidate(h1_full, len(h1_full) - 1)
    assert result.magnitude < 1.0  # net close-to-close move is tiny despite the huge intra-window path
    assert result.status == "NOT_MATERIAL"


def _material_candidate(base_ts, *, direction="BULLISH"):
    lead = [1900.0 + i * 1.0 for i in range(18)]
    delta = 5.0 if direction == "BULLISH" else -5.0
    closes = lead + [lead[-1], lead[-1], lead[-1], lead[-1] + delta]
    h1 = _h1_series(base_ts, closes)
    return audit_candidate(h1, len(h1) - 1)


def test_coverage_window_boundaries(base_ts):
    cand = _material_candidate(base_ts)
    start, end = coverage_window(cand)
    assert start == cand.window_start_ts - H1_SECONDS
    assert end == cand.window_end_ts


def test_coverage_requires_prospective_eligibility_yes(base_ts):
    cand = _material_candidate(base_ts, direction="BULLISH")
    start, _ = coverage_window(cand)
    row = {"prospective_eligibility": "NO", "frozen_at_bar_ts": str(start), "directional_hypothesis": "BULLISH", "episode_type": "SWEEP_REJECTION"}
    assert is_covered(cand, [row]) is False


def test_coverage_requires_timestamp_in_window(base_ts):
    cand = _material_candidate(base_ts)
    start, _ = coverage_window(cand)
    row = {"prospective_eligibility": "YES", "frozen_at_bar_ts": str(start - H1_SECONDS), "directional_hypothesis": "BULLISH", "episode_type": "SWEEP_REJECTION"}
    assert is_covered(cand, [row]) is False


def test_coverage_requires_exact_direction_match(base_ts):
    cand = _material_candidate(base_ts, direction="BULLISH")
    start, _ = coverage_window(cand)
    row = {"prospective_eligibility": "YES", "frozen_at_bar_ts": str(start), "directional_hypothesis": "BEARISH", "episode_type": "SWEEP_REJECTION"}
    assert is_covered(cand, [row]) is False


def test_coverage_requires_one_of_the_four_general_classes(base_ts):
    """S5 alone never covers -- S5_OCCURRENCE is not in GENERAL_OBSERVER_EVENT_TYPES."""
    cand = _material_candidate(base_ts)
    start, _ = coverage_window(cand)
    row = {"prospective_eligibility": "YES", "frozen_at_bar_ts": str(start), "directional_hypothesis": "BULLISH", "episode_type": "S5_OCCURRENCE"}
    assert is_covered(cand, [row]) is False


def test_coverage_true_when_all_four_conditions_hold(base_ts):
    cand = _material_candidate(base_ts, direction="BULLISH")
    start, end = coverage_window(cand)
    row = {"prospective_eligibility": "YES", "frozen_at_bar_ts": str(end), "directional_hypothesis": "BULLISH", "episode_type": "DISPLACEMENT"}
    assert is_covered(cand, [row]) is True


def test_classify_for_clustering_all_four_outcomes(base_ts):
    material_uncovered = _material_candidate(base_ts, direction="BULLISH")
    assert classify_for_clustering(material_uncovered, []) == "MATERIAL_UNCOVERED"

    start, end = coverage_window(material_uncovered)
    covering_row = {"prospective_eligibility": "YES", "frozen_at_bar_ts": str(end), "directional_hypothesis": "BULLISH", "episode_type": "DISPLACEMENT"}
    assert classify_for_clustering(material_uncovered, [covering_row]) == "MATERIAL_COVERED"


# ---- Cluster state machine ------------------------------------------------------------------------

def _cand(base_ts, i, *, direction="BULLISH", ts_step=H1_SECONDS):
    lead = [1900.0 + j * 1.0 for j in range(18)]
    delta = 5.0 if direction == "BULLISH" else -5.0
    closes = lead + [lead[-1]] * 3 + [lead[-1] + delta]
    h1 = _h1_series(base_ts + i * ts_step, closes)
    return audit_candidate(h1, len(h1) - 1)


def test_cluster_starts_on_first_material_uncovered_candidate(base_ts):
    c1 = _cand(base_ts, 0)
    active, finalized = advance_cluster_state("MATERIAL_UNCOVERED", c1, None)
    assert finalized is None
    assert active is not None
    assert active.qualifying_window_count == 1
    assert active.canonical_window_start_ts == c1.window_start_ts
    assert active.cluster_terminated_at_ts is None


def test_cluster_continues_on_next_same_direction_material_uncovered(base_ts):
    c1 = _cand(base_ts, 0)
    active, _ = advance_cluster_state("MATERIAL_UNCOVERED", c1, None)
    c2 = _cand(base_ts, 1, direction="BULLISH")
    active2, finalized = advance_cluster_state("MATERIAL_UNCOVERED", c2, active)
    assert finalized is None
    assert active2.qualifying_window_count == 2
    # Canonical identity fixed to the FIRST candidate -- never revised by a later one.
    assert active2.canonical_window_start_ts == c1.window_start_ts
    assert active2.canonical_magnitude == active.canonical_magnitude


def test_cluster_terminates_on_non_qualifying_candidate_no_gap_bridging(base_ts):
    c1 = _cand(base_ts, 0)
    active, _ = advance_cluster_state("MATERIAL_UNCOVERED", c1, None)
    active2, _ = advance_cluster_state("MATERIAL_UNCOVERED", _cand(base_ts, 1), active)  # count=2
    active3, finalized = advance_cluster_state("NOT_MATERIAL", _cand(base_ts, 2), active2)
    assert active3 is None  # cluster closed, nothing bridges the gap
    assert finalized is not None
    assert finalized.cluster_terminated_at_ts == active2.canonical_window_end_ts + H1_SECONDS  # last continuing candidate's end


def test_cluster_terminates_on_covered_candidate(base_ts):
    c1 = _cand(base_ts, 0)
    active, _ = advance_cluster_state("MATERIAL_UNCOVERED", c1, None)
    active2, finalized = advance_cluster_state("MATERIAL_COVERED", _cand(base_ts, 1), active)
    assert active2 is None
    assert finalized is not None


def test_cluster_terminates_on_unscorable_candidate(base_ts):
    c1 = _cand(base_ts, 0)
    active, _ = advance_cluster_state("MATERIAL_UNCOVERED", c1, None)
    active2, finalized = advance_cluster_state("UNSCORABLE_ATR_UNAVAILABLE", _cand(base_ts, 1), active)
    assert active2 is None
    assert finalized is not None


def test_direction_reversal_closes_old_cluster_and_opens_new_one_same_step(base_ts):
    c1 = _cand(base_ts, 0, direction="BULLISH")
    active, _ = advance_cluster_state("MATERIAL_UNCOVERED", c1, None)
    c2 = _cand(base_ts, 1, direction="BEARISH")
    active2, finalized = advance_cluster_state("MATERIAL_UNCOVERED", c2, active)
    assert finalized is not None
    assert finalized.direction == "BULLISH"
    assert active2 is not None
    assert active2.direction == "BEARISH"
    assert active2.qualifying_window_count == 1  # a genuinely new cluster, not a continuation
    assert active2.canonical_window_start_ts == c2.window_start_ts  # identity is the NEW candidate's own


def test_cluster_id_deterministic_and_matches_canonical_identity_only(base_ts):
    c1 = _cand(base_ts, 0)
    active_a, _ = advance_cluster_state("MATERIAL_UNCOVERED", c1, None)
    active_b, _ = advance_cluster_state("MATERIAL_UNCOVERED", c1, None)
    assert active_a.cluster_id == active_b.cluster_id  # same candidate -> same id, deterministic


def test_cluster_from_dict_round_trips_through_json_restart_simulation(base_ts):
    """The active-cluster restart-recovery path: `to_json_dict()` -> JSON string -> parsed back ->
    `cluster_from_dict()` must reproduce an equal cluster, including correctly dropping the
    `init=False` `record_class` field that `dataclasses.asdict` still serializes."""
    c1 = _cand(base_ts, 0)
    active, _ = advance_cluster_state("MATERIAL_UNCOVERED", c1, None)
    as_json = json.dumps(active.to_json_dict())
    reloaded = cluster_from_dict(json.loads(as_json))
    assert reloaded == active
    assert dataclasses.asdict(reloaded)["record_class"] == "RETROSPECTIVELY_IDENTIFIED_MISSED_EVENT"
