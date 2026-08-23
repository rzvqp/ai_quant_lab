"""Fail-closed regression tests for VE-CURRENT-REGIME-TEMPORAL-CAUSALITY-REPAIR-001.

Covers cur_data.causal_bucket_asof (the single canonical timestamp-alignment contract) and
cur_screen.like_at (the concrete lookup this mandate was raised against). Runnable directly
(python test_cur_causal_alignment.py) or under pytest.

Every test proves a NEGATIVE: that no finer-grained decision timestamp can ever be mapped to a
higher-timeframe bucket that has not yet closed as of that timestamp -- not merely that the happy
path returns a plausible-looking answer."""
import os, sys
SP = os.path.dirname(os.path.abspath(__file__))
if SP not in sys.path: sys.path.insert(0, SP)
import numpy as np
import cur_data as CD

H4 = 14400  # seconds
H1 = 3600


# ---- pure arithmetic tests (no data file needed) ----

def test_01_m15_at_h4_bucket_start_uses_prior_bucket():
    # a decision made at the EXACT instant a new H4 bucket opens must not see that bucket's own
    # (not-yet-existent) data -- it must resolve to the bucket that just closed
    starts = np.array([0, 14400, 28800])
    out = CD.causal_bucket_asof(np.array([14400]), starts, "H4")
    assert out[0] == 0, "must resolve to the PRIOR (just-closed) bucket, not the one starting now"


def test_02_m15_inside_h4_bucket_uses_prior_bucket():
    # anywhere strictly inside a forming bucket -- the forming bucket itself must never be reachable
    starts = np.array([0, 14400, 28800])
    for t in (14400 + 1, 14400 + 900, 14400 + 7200, 14400 + 14399):
        out = CD.causal_bucket_asof(np.array([t]), starts, "H4")
        assert out[0] == 0, f"t={t} inside bucket 14400 resolved to {out[0]}, expected prior bucket 0"


def test_03_m15_immediately_before_h4_close_still_uses_prior_bucket():
    # the LAST M15 sub-bar of a forming H4 bucket (one M15 width before its own close) is still
    # inside the forming bucket -- must not see it
    starts = np.array([0, 14400, 28800])
    t = 14400 + (14400 - 900)  # last M15 bar's own open time within the second bucket
    out = CD.causal_bucket_asof(np.array([t]), starts, "H4")
    assert out[0] == 0


def test_04_m15_exactly_at_h4_close_uses_that_bucket_now_closed():
    # the instant a bucket closes (== the next bucket's own start), its OWN data becomes usable
    starts = np.array([0, 14400, 28800])
    out = CD.causal_bucket_asof(np.array([28800]), starts, "H4")
    assert out[0] == 14400, "at t=28800 the [14400,28800) bucket has just closed and must be usable"


def test_05_m15_just_after_h4_close_uses_that_bucket():
    starts = np.array([0, 14400, 28800])
    out = CD.causal_bucket_asof(np.array([28800 + 1]), starts, "H4")
    assert out[0] == 14400


def test_06_no_bucket_has_closed_yet_returns_sentinel():
    # before the first bucket has ever closed, there is nothing causally available -- must fail
    # closed (sentinel -1), never wrap around or return a spurious value
    starts = np.array([0, 14400, 28800])
    out = CD.causal_bucket_asof(np.array([0, 1, 14399]), starts, "H4")
    assert (out == -1).all()


def test_07_no_decision_can_ever_reach_a_bucket_that_has_not_closed():
    """The central invariant, checked exhaustively rather than at a few hand-picked points: for every
    M15-resolution timestamp across many H4 buckets, the resolved bucket's own CLOSE time must be
    <= the query timestamp. This is what "no lookahead" means mechanically."""
    starts = np.arange(0, 400 * H4, H4)
    times = np.arange(0, 400 * H4, 900)  # every M15 instant across the whole span
    resolved = CD.causal_bucket_asof(times, starts, "H4")
    ok = resolved != -1
    resolved_close = resolved[ok] + H4
    assert (resolved_close <= times[ok]).all(), "found a decision that can see a not-yet-closed bucket"
    # and the resolved bucket must never be the one containing the query time itself
    containing = (times[ok] // H4) * H4
    assert (resolved[ok] != containing).all(), "a decision resolved to its OWN (still-forming) bucket"


def test_08_day_boundary():
    # a bucket grid that happens to cross UTC midnight -- arithmetic must not special-case this
    day = 86400
    starts = np.array([day - H4, day, day + H4])  # 20:00-00:00, 00:00-04:00, 04:00-08:00
    # a decision at 00:00:01 (just after midnight, inside the [day, day+H4) bucket) must use the
    # bucket that closed exactly at midnight, not the one now forming across the boundary
    out = CD.causal_bucket_asof(np.array([day + 1]), starts, "H4")
    assert out[0] == day - H4


def test_09_week_boundary_gap_carries_forward_last_closed_bucket():
    """The defect this mandate's own investigation found beyond the base fix: a market-closed gap
    (weekend) means the arithmetically-prior bucket slot never traded and is ABSENT from any real
    bucket-starts array. A naive fixed-offset shift would silently return "no data" for roughly one
    bucket-width after every reopen; the canonical contract must instead carry forward the last bucket
    that genuinely closed before the gap -- still zero lookahead, strictly more available information."""
    fri_close = 4 * H4          # last Friday H4 bucket start before the weekend, arbitrary anchor
    sun_reopen = fri_close + 3 * H4 + 5 * 86400  # a multi-day gap -- no buckets exist in between
    starts = np.array([fri_close, sun_reopen])   # note: nothing between them -- genuine gap
    # a decision shortly after Sunday reopen, still inside the reopen bucket (must not see it)
    t = sun_reopen + 900
    out = CD.causal_bucket_asof(np.array([t]), starts, "H4")
    assert out[0] == fri_close, (
        "must carry forward the last bucket that actually closed before the gap, not fail to -1 just "
        "because the arithmetically-adjacent slot never traded"
    )
    # sanity: the naive fixed-offset arithmetic this mandate replaced WOULD have failed this exact case
    naive = (t // H4) * H4 - H4
    assert naive not in starts, "test is only meaningful if the naive prior slot is genuinely absent"


def test_10_h1_timeframe_same_contract():
    # the canonical contract is timeframe-generic -- verify it holds for H1 too, not just H4
    starts = np.array([0, H1, 2 * H1])
    out = CD.causal_bucket_asof(np.array([H1 + 1]), starts, "H1")
    assert out[0] == 0


def test_11_repeated_timestamps_and_unsorted_input_are_handled():
    starts = np.array([28800, 0, 14400])  # deliberately unsorted
    times = np.array([30000, 14400, 30000, 100])
    out = CD.causal_bucket_asof(times, starts, "H4")
    assert out[0] == 14400 and out[2] == 14400  # duplicate query, same answer
    assert out[1] == 0
    assert out[3] == -1


# ---- like_at end-to-end tests (real cache/data) ----

def test_20_like_at_never_looks_up_the_forming_bucket():
    """End-to-end proof against the real production lookup's OWN returned values -- not merely the
    arithmetic helper in isolation, which would pass even if like_at internally used a different
    (buggy) formula. Computes the causally-correct expected boolean independently, per timestamp, and
    asserts like_at's ACTUAL output matches it exactly, so a regression inside like_at itself (not just
    inside causal_bucket_asof) is caught."""
    import cur_screen as CS
    CS._load()
    times = CS._M["time"].to_numpy()[::521]   # broad, deterministic stride sample across full history
    resolved = CD.causal_bucket_asof(times, CS._LK_STARTS, "H4")
    ok = resolved != -1
    assert (resolved[ok] + 14400 <= times[ok]).all()
    expected = np.array([bool(CS._LK.get(int(t), False)) for t in resolved])
    actual = CS.like_at(times)
    assert actual.dtype == bool and actual.shape == times.shape
    assert np.array_equal(actual, expected), "like_at's own output diverged from the independently-computed causal expectation"


def test_21_like_at_matches_the_independent_merge_asof_reference():
    """Cross-validates the production lookup against this codebase's OWN separately-established
    correct convention (merge_asof(direction="backward") on close_time, as already used by
    cur_cr13_trade.py's h4_up_map for the H4-trend gate) -- proves there is now exactly one causal
    semantic in this codebase, not two that quietly disagree."""
    import pandas as pd
    import cur_screen as CS
    CS._load()
    h4 = CD.agg(CS._M, "H4")
    h4map = pd.DataFrame({"close_time": h4["close_time"].to_numpy(),
                          "bucket_start": h4["time"].to_numpy()}).sort_values("close_time")
    sample_times = CS._M["time"].to_numpy()[::2003]
    mm = pd.DataFrame({"time": sample_times}).sort_values("time")
    ref = pd.merge_asof(mm, h4map, left_on="time", right_on="close_time", direction="backward").sort_index()
    ref_bucket_start = ref["bucket_start"].to_numpy()
    mine = CD.causal_bucket_asof(sample_times, CS._LK_STARTS, "H4")
    valid = np.isfinite(ref_bucket_start)
    assert np.array_equal(ref_bucket_start[valid].astype(np.int64), mine[valid])


def test_22_statistician_counterexample_regression():
    """Regression coverage for the exact defect the Statistician's independent review found
    (STAT-CRS1-INDEPENDENT-REVIEW-FDR-001, commit 4163382, statistician-foundation): 100% of the
    12,083 CR-13/CRS-1 candidate entries were, before this repair, gated on an H4 bar that had not
    closed at entry. Calls the ACTUAL production `like_at` (not just the arithmetic helper) on
    synthetic M15 timestamps placed inside a real historical H4 bucket, and proves its returned value
    equals the PRIOR bucket's flag, not the current (still-forming, from that entry's point of view)
    bucket's own flag -- the precise failure mode: an entry inside bucket X seeing bucket X's own label."""
    import cur_screen as CS
    CS._load()
    # find a bucket whose flag differs from its own predecessor's -- otherwise the two hypotheses
    # (causally-correct vs. the original bug) would predict the same answer and the test couldn't
    # discriminate between them
    bucket_start = prior_start = None
    for i in range(1, len(CS._LK_STARTS)):
        cur, prev = int(CS._LK_STARTS[i]), int(CS._LK_STARTS[i - 1])
        if cur - prev == 14400 and bool(CS._LK[cur]) != bool(CS._LK[prev]):
            bucket_start, prior_start = cur, prev
            break
    assert bucket_start is not None, "no adjacent differing-flag bucket pair found in real data -- test cannot discriminate"
    own_flag = bool(CS._LK[bucket_start])
    prior_flag = bool(CS._LK[prior_start])
    # M15 entries inside THIS bucket must return the PRIOR bucket's flag via the real like_at call,
    # never this bucket's own (not-yet-closed, from the entry's point of view) flag
    for offset in (0, 900, 7200, 14400 - 900 - 1):
        t = bucket_start + offset
        out = CS.like_at(np.array([t]))
        assert out[0] == prior_flag, (
            f"entry at offset {offset}s into its own bucket got like_at={out[0]}, expected the PRIOR "
            f"bucket's flag ({prior_flag}) -- got own bucket's not-yet-closed flag ({own_flag}) instead: "
            f"this is exactly the Statistician's counterexample"
        )
    # an M15 entry in the NEXT bucket (this one has now closed) correctly sees THIS bucket's flag
    next_entry = np.array([bucket_start + 14400])
    out_next = CS.like_at(next_entry)
    assert out_next[0] == own_flag


if __name__ == "__main__":
    import inspect
    tests = [f for name, f in list(globals().items()) if name.startswith("test_") and callable(f)]
    passed = failed = 0
    for t in sorted(tests, key=lambda f: f.__name__):
        try:
            t(); passed += 1; print(f"PASS {t.__name__}")
        except Exception as e:
            failed += 1; print(f"FAIL {t.__name__}: {e}")
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
