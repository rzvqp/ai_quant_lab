"""Mandate Section 26/28/29/30 (AFTER scorecard): per-horizon due/pending gating, restart-safety
(`already_scored`), the BULLISH/BEARISH -> LONG/SHORT direction-vocabulary bridge, and -- patched per
design doc Section 19 (Fifth Addendum) -- the full `classify_expectation_correct` truth table:
Section 19.15's own non-vacuity test vectors, mutual-exclusivity/exhaustiveness proof, universal
NOT_SCORABLE preconditions, and the `STRUCTURAL_FINAL` branch.
"""

from __future__ import annotations

import itertools

import pytest

from ai_trader.apprenticeship_v2 import durable_store
from ai_trader.apprenticeship_v2.general_observer import scorecard
from ai_trader.apprenticeship_v2.general_observer.scorecard import EpisodeContext
from ai_trader.apprenticeship_v2.schemas import ALLOWED_EXPECTATIONS, HorizonMetrics, ScorecardEntry
from ai_trader.apprenticeship_v2.tests.conftest import M15_SECONDS, make_bar


@pytest.fixture(autouse=True)
def _isolated_scorecard_csv(tmp_path, monkeypatch):
    """Redirects `durable_store.SCORECARD_CSV` to a throwaway temp file for every test in this
    module -- these tests must never read or write the real, live production scorecard file."""
    monkeypatch.setattr(durable_store, "SCORECARD_CSV", tmp_path / "AI_TRADER_SCORECARD.csv")


def _episode_row(
    *, episode_id="GO-TEST-1", frozen_at_bar_ts, direction="BULLISH", price=1900.0, prospective_eligibility="YES",
    origin_price=1896.0, move_id="MOVE-1",
):
    import json

    return {
        "episode_id": episode_id, "frozen_at_bar_ts": str(frozen_at_bar_ts),
        "directional_hypothesis": direction, "current_price": str(price),
        "prospective_eligibility": prospective_eligibility, "episode_type": "SWEEP_REJECTION",
        "underlying_move_id": move_id, "reference_levels_json": json.dumps({"swept_level_price": origin_price}),
    }


def _ctx(*, review_horizon="H1", prospective_eligibility="YES", structural_resolution_state=None) -> EpisodeContext:
    return EpisodeContext(
        prospective_eligibility=prospective_eligibility, review_horizon=review_horizon,
        structural_resolution_state=structural_resolution_state,
    )


def _metrics(*, dft, rtm=0.0, mae=0.0, mfe=0.0) -> HorizonMetrics:
    return HorizonMetrics(
        forward_return=0.0, mfe=mfe, mae=mae, max_up_move=0.0, max_down_move=0.0,
        close_location=0.5, directional_follow_through=dft, round_trip_magnitude=rtm,
    )


def test_already_scored_false_when_no_rows_exist():
    assert scorecard.already_scored("GO-X", "H1") is False


def test_already_scored_true_after_append_and_restart_reload():
    entry = ScorecardEntry(
        episode_id="GO-X", review_horizon="H1", original_expectation="FOLLOW_THROUGH_LIKELY",
        original_confidence="HIGH", mechanical_outcome_summary="x", expectation_correct="YES",
        partial_reason=None, scored_at_utc="2026-01-01T00:00:00+00:00",
    )
    durable_store.append_scorecard(entry)
    # Fresh read every call (no in-memory cache anywhere in already_scored) -- simulates a restart.
    assert scorecard.already_scored("GO-X", "H1") is True
    assert scorecard.already_scored("GO-X", "H2") is False  # different horizon, same episode
    assert scorecard.already_scored("GO-Y", "H1") is False  # different episode


def test_due_horizons_empty_when_no_forward_bars_yet(base_ts):
    row = _episode_row(frozen_at_bar_ts=base_ts)
    assert scorecard.due_horizons_for_episode(row, []) == []


def test_due_horizons_only_includes_horizons_with_enough_bars(base_ts):
    row = _episode_row(frozen_at_bar_ts=base_ts)
    # Exactly 4 forward M15 bars available -- H1 (4 bars) is due; H2/H4/H8 (8/16/32) are not.
    forward = [make_bar(ts_open=base_ts + i * M15_SECONDS, o=1900, h=1901, l=1899, c=1900.5) for i in range(1, 5)]
    due = scorecard.due_horizons_for_episode(row, forward)
    assert [name for name, _ in due] == ["H1"]


def test_due_horizons_multiple_at_once_once_enough_bars_exist(base_ts):
    row = _episode_row(frozen_at_bar_ts=base_ts)
    forward = [make_bar(ts_open=base_ts + i * M15_SECONDS, o=1900, h=1901, l=1899, c=1900.5) for i in range(1, 9)]
    due = scorecard.due_horizons_for_episode(row, forward)
    assert [name for name, _ in due] == ["H1", "H2"]


def test_due_horizons_excludes_already_scored(base_ts):
    row = _episode_row(episode_id="GO-Z", frozen_at_bar_ts=base_ts)
    entry = ScorecardEntry(
        episode_id="GO-Z", review_horizon="H1", original_expectation="UNCLEAR",
        original_confidence="LOW", mechanical_outcome_summary="x", expectation_correct="NOT_SCORABLE",
        partial_reason=None, scored_at_utc="2026-01-01T00:00:00+00:00",
    )
    durable_store.append_scorecard(entry)
    forward = [make_bar(ts_open=base_ts + i * M15_SECONDS, o=1900, h=1901, l=1899, c=1900.5) for i in range(1, 5)]
    assert scorecard.due_horizons_for_episode(row, forward) == []  # H1 already scored -- not due again


def test_direction_vocabulary_bridge_produces_real_directional_follow_through(base_ts):
    """BULLISH must translate to LONG so resolution.compute_horizon_metrics's own
    directional_follow_through comes back a real bool, not the direction-unknown None fallback."""
    row = _episode_row(frozen_at_bar_ts=base_ts, direction="BULLISH", price=1900.0)
    forward = [make_bar(ts_open=base_ts + i * M15_SECONDS, o=1900, h=1905, l=1899, c=1904) for i in range(1, 5)]
    due = scorecard.due_horizons_for_episode(row, forward)
    assert len(due) == 1
    _, metrics = due[0]
    assert metrics.directional_follow_through is True  # price rallied -- BULLISH follow-through


def test_direction_vocabulary_bridge_handles_bearish(base_ts):
    row = _episode_row(frozen_at_bar_ts=base_ts, direction="BEARISH", price=1900.0)
    forward = [make_bar(ts_open=base_ts + i * M15_SECONDS, o=1900, h=1901, l=1895, c=1896) for i in range(1, 5)]
    due = scorecard.due_horizons_for_episode(row, forward)
    _, metrics = due[0]
    assert metrics.directional_follow_through is True  # price fell -- BEARISH follow-through


def test_score_due_horizons_now_produces_a_real_verdict_not_a_raise(base_ts):
    """Patched per Section 19 -- the classifier no longer raises; a due horizon now gets a real
    mechanical verdict."""
    row = _episode_row(frozen_at_bar_ts=base_ts)
    prediction = {"ai_trader_expectation": "FOLLOW_THROUGH_LIKELY", "confidence": "HIGH"}
    forward = [make_bar(ts_open=base_ts + i * M15_SECONDS, o=1900, h=1905, l=1899, c=1904) for i in range(1, 5)]
    entries = scorecard.score_due_horizons_for_episode(row, prediction, forward)
    assert len(entries) == 1
    assert entries[0].expectation_correct in ("YES", "NO", "PARTIAL", "NOT_SCORABLE")
    assert entries[0].expectation_correct == "YES"  # rallied, no giveback -- clear follow-through


def test_score_due_horizons_not_scorable_when_episode_not_prospectively_eligible(base_ts):
    row = _episode_row(frozen_at_bar_ts=base_ts, prospective_eligibility="NO")
    prediction = {"ai_trader_expectation": "FOLLOW_THROUGH_LIKELY", "confidence": "HIGH"}
    forward = [make_bar(ts_open=base_ts + i * M15_SECONDS, o=1900, h=1905, l=1899, c=1904) for i in range(1, 5)]
    entries = scorecard.score_due_horizons_for_episode(row, prediction, forward)
    assert entries[0].expectation_correct == "NOT_SCORABLE"


# ---- Section 19.15 non-vacuity test vectors (verbatim) --------------------------------------------

@pytest.mark.parametrize("expectation,dft,rtm,mae,mfe,expected", [
    ("FOLLOW_THROUGH_LIKELY", True, 0.20, 0.0, 0.0, "YES"),
    ("FOLLOW_THROUGH_LIKELY", False, 0.0, 0.0, 0.0, "NO"),
    ("FOLLOW_THROUGH_LIKELY", True, 1.0, 0.0, 0.0, "NO"),  # exact boundary
    ("FAILURE_LIKELY", False, 0.0, 0.0, 0.0, "YES"),
    ("FAILURE_LIKELY", True, 0.20, 0.0, 0.0, "NO"),
    ("REVERSAL_LIKELY", False, 0.0, 8.0, 3.0, "YES"),
    ("REVERSAL_LIKELY", False, 0.0, 3.0, 8.0, "NO"),
    ("REVERSAL_LIKELY", False, 0.0, 5.0, 5.0, "NO"),  # exact tie boundary
    ("ROUND_TRIP_LIKELY", False, 1.0, 0.0, 0.0, "YES"),  # exact boundary
    ("ROUND_TRIP_LIKELY", False, 0.45, 0.0, 0.0, "PARTIAL"),
    ("ROUND_TRIP_LIKELY", False, 0.0, 0.0, 0.0, "NO"),
    ("RANGE_LIKELY", False, 0.0, 3.0, 8.0, "YES"),
    ("RANGE_LIKELY", True, 0.0, 1.0, 9.0, "NO"),
    ("UNCLEAR", True, 0.0, 0.0, 0.0, "NOT_SCORABLE"),
])
def test_section_19_15_vectors(expectation, dft, rtm, mae, mfe, expected):
    metrics = _metrics(dft=dft, rtm=rtm, mae=mae, mfe=mfe)
    assert scorecard.classify_expectation_correct(expectation, metrics, _ctx()) == expected


def test_section_19_15_vector_not_eligible():
    metrics = _metrics(dft=True, rtm=0.0)
    ctx = _ctx(prospective_eligibility="NO")
    assert scorecard.classify_expectation_correct("FOLLOW_THROUGH_LIKELY", metrics, ctx) == "NOT_SCORABLE"


def test_section_19_15_vector_structural_final_unresolved():
    metrics = _metrics(dft=True, rtm=0.0)
    ctx = _ctx(review_horizon="STRUCTURAL_FINAL", structural_resolution_state=None)
    assert scorecard.classify_expectation_correct("FOLLOW_THROUGH_LIKELY", metrics, ctx) == "NOT_SCORABLE"


# ---- Universal preconditions, individually (Section 19.4) -----------------------------------------

def test_invalid_expectation_value_is_not_scorable():
    metrics = _metrics(dft=True, rtm=0.0)
    assert scorecard.classify_expectation_correct("SOMETHING_MADE_UP", metrics, _ctx()) == "NOT_SCORABLE"


def test_direction_unresolved_is_not_scorable():
    metrics = _metrics(dft=None, rtm=0.0)
    assert scorecard.classify_expectation_correct("FOLLOW_THROUGH_LIKELY", metrics, _ctx()) == "NOT_SCORABLE"


def test_unclear_always_not_scorable_regardless_of_metrics():
    for dft in (True, False, None):
        metrics = _metrics(dft=dft, rtm=5.0, mae=99.0, mfe=0.001)
        assert scorecard.classify_expectation_correct("UNCLEAR", metrics, _ctx()) == "NOT_SCORABLE"


# ---- STRUCTURAL_FINAL branch (Section 19.11/19.14) -------------------------------------------------

def test_structural_final_confirmation_behaves_as_the_yes_pole():
    ctx = _ctx(review_horizon="STRUCTURAL_FINAL", structural_resolution_state="CONFIRMATION")
    metrics = _metrics(dft=None, rtm=0.0)  # ignored on this branch -- state drives dft/rtm instead
    assert scorecard.classify_expectation_correct("FOLLOW_THROUGH_LIKELY", metrics, ctx) == "YES"
    assert scorecard.classify_expectation_correct("FAILURE_LIKELY", metrics, ctx) == "NO"
    assert scorecard.classify_expectation_correct("ROUND_TRIP_LIKELY", metrics, ctx) == "NO"


def test_structural_final_invalidation_behaves_as_the_no_pole():
    ctx = _ctx(review_horizon="STRUCTURAL_FINAL", structural_resolution_state="INVALIDATION")
    metrics = _metrics(dft=None, rtm=0.0)
    assert scorecard.classify_expectation_correct("FOLLOW_THROUGH_LIKELY", metrics, ctx) == "NO"
    assert scorecard.classify_expectation_correct("FAILURE_LIKELY", metrics, ctx) == "YES"
    assert scorecard.classify_expectation_correct("REVERSAL_LIKELY", metrics, ctx) == "YES"
    assert scorecard.classify_expectation_correct("ROUND_TRIP_LIKELY", metrics, ctx) == "YES"


def test_structural_final_unresolved_at_h8_is_not_scorable():
    ctx = _ctx(review_horizon="STRUCTURAL_FINAL", structural_resolution_state="UNRESOLVED_AT_H8")
    metrics = _metrics(dft=None, rtm=0.0)
    assert scorecard.classify_expectation_correct("FOLLOW_THROUGH_LIKELY", metrics, ctx) == "NOT_SCORABLE"


# ---- Mutual exclusivity + exhaustiveness (Section 19.16 / mandate Section 29/30) -------------------

_REACHABLE_EXPECTATIONS = [e for e in ALLOWED_EXPECTATIONS if e != "UNCLEAR"]
_VERDICTS = ("YES", "NO", "PARTIAL", "NOT_SCORABLE")


def test_classification_is_exhaustive_and_never_falls_through():
    """No valid input may fall through, return None, or raise -- every combination of the grid this
    contract is built from must return exactly one of the four verdicts."""
    dft_values = (True, False)
    rtm_values = (0.0, 0.3, 0.9999, 1.0, 1.7)
    mae_mfe_pairs = ((3.0, 8.0), (8.0, 3.0), (5.0, 5.0))
    for expectation, dft, rtm, (mae, mfe) in itertools.product(_REACHABLE_EXPECTATIONS, dft_values, rtm_values, mae_mfe_pairs):
        metrics = _metrics(dft=dft, rtm=rtm, mae=mae, mfe=mfe)
        verdict = scorecard.classify_expectation_correct(expectation, metrics, _ctx())
        assert verdict in _VERDICTS, (expectation, dft, rtm, mae, mfe, verdict)


def test_follow_through_and_failure_are_exact_logical_complements():
    dft_values = (True, False)
    rtm_values = (0.0, 0.3, 0.9999, 1.0, 1.7)
    for dft, rtm in itertools.product(dft_values, rtm_values):
        metrics = _metrics(dft=dft, rtm=rtm)
        ft = scorecard.classify_expectation_correct("FOLLOW_THROUGH_LIKELY", metrics, _ctx())
        fail = scorecard.classify_expectation_correct("FAILURE_LIKELY", metrics, _ctx())
        assert {ft, fail} == {"YES", "NO"}
        assert ft != fail


def test_reversal_and_range_are_exact_logical_complements():
    mae_mfe_pairs = ((3.0, 8.0), (8.0, 3.0), (5.0, 5.0))
    for mae, mfe in mae_mfe_pairs:
        metrics = _metrics(dft=False, mae=mae, mfe=mfe)
        rev = scorecard.classify_expectation_correct("REVERSAL_LIKELY", metrics, _ctx())
        rng = scorecard.classify_expectation_correct("RANGE_LIKELY", metrics, _ctx())
        assert {rev, rng} == {"YES", "NO"}
        assert rev != rng
    # dft=True: both must be NO (REVERSAL/RANGE both require dft==False).
    metrics = _metrics(dft=True, mae=1.0, mfe=9.0)
    assert scorecard.classify_expectation_correct("REVERSAL_LIKELY", metrics, _ctx()) == "NO"
    assert scorecard.classify_expectation_correct("RANGE_LIKELY", metrics, _ctx()) == "NO"


def test_round_trip_three_intervals_partition_with_no_gap_or_overlap():
    for rtm in (0.0, 0.01, 0.5, 0.999, 1.0, 1.5):
        metrics = _metrics(dft=False, rtm=rtm)
        verdict = scorecard.classify_expectation_correct("ROUND_TRIP_LIKELY", metrics, _ctx())
        if rtm >= 1.0:
            assert verdict == "YES"
        elif rtm > 0.0:
            assert verdict == "PARTIAL"
        else:
            assert verdict == "NO"


def test_partial_unreachable_for_every_expectation_except_round_trip():
    dft_values = (True, False)
    rtm_values = (0.0, 0.3, 1.0, 1.7)
    mae_mfe_pairs = ((3.0, 8.0), (8.0, 3.0))
    for expectation in ("FOLLOW_THROUGH_LIKELY", "FAILURE_LIKELY", "REVERSAL_LIKELY", "RANGE_LIKELY"):
        for dft, rtm, (mae, mfe) in itertools.product(dft_values, rtm_values, mae_mfe_pairs):
            metrics = _metrics(dft=dft, rtm=rtm, mae=mae, mfe=mfe)
            verdict = scorecard.classify_expectation_correct(expectation, metrics, _ctx())
            assert verdict != "PARTIAL", (expectation, dft, rtm, mae, mfe)


def test_confidence_never_affects_expectation_correct():
    """CONFIDENCE_AFFECTS_EXPECTATION_CORRECT = NO (Section 19.12) -- the classifier's own signature
    never takes confidence at all, so this is structurally guaranteed; asserted here directly."""
    import inspect

    params = inspect.signature(scorecard.classify_expectation_correct).parameters
    assert "confidence" not in params


# ---- STRUCTURAL_FINAL scoring integration (mandate item 1) -----------------------------------------

def test_score_structural_final_none_while_pending(base_ts):
    row = _episode_row(frozen_at_bar_ts=base_ts, direction="BULLISH", price=1900.0, origin_price=1896.0)
    prediction = {"ai_trader_expectation": "FOLLOW_THROUGH_LIKELY", "confidence": "HIGH"}
    bars = [make_bar(ts_open=base_ts + i * M15_SECONDS, o=1898, h=1898.5, l=1897.5, c=1898.0) for i in range(1, 5)]
    assert scorecard.score_structural_final_for_episode(row, prediction, bars, []) is None


def test_score_structural_final_confirmation_produces_a_row(base_ts):
    row = _episode_row(frozen_at_bar_ts=base_ts, direction="BULLISH", price=1900.0, origin_price=1896.0)
    prediction = {"ai_trader_expectation": "FOLLOW_THROUGH_LIKELY", "confidence": "HIGH"}
    bars = [make_bar(ts_open=base_ts + M15_SECONDS, o=1901, h=1902, l=1900.5, c=1901.5)]  # continuation past current_price
    entry = scorecard.score_structural_final_for_episode(row, prediction, bars, [])
    assert entry is not None
    assert entry.review_horizon == "STRUCTURAL_FINAL"
    assert entry.expectation_correct == "YES"
    assert "structural_resolution_state=CONFIRMATION" in entry.mechanical_outcome_summary


def test_score_structural_final_invalidation_produces_a_row(base_ts):
    row = _episode_row(frozen_at_bar_ts=base_ts, direction="BULLISH", price=1900.0, origin_price=1896.0)
    prediction = {"ai_trader_expectation": "FOLLOW_THROUGH_LIKELY", "confidence": "HIGH"}
    bars = [make_bar(ts_open=base_ts + M15_SECONDS, o=1897, h=1897.5, l=1895.0, c=1895.5)]  # adverse close through origin
    entry = scorecard.score_structural_final_for_episode(row, prediction, bars, [])
    assert entry is not None
    assert entry.expectation_correct == "NO"
    assert "structural_resolution_state=INVALIDATION" in entry.mechanical_outcome_summary


def test_score_structural_final_does_not_touch_earlier_horizon_rows(base_ts, tmp_path, monkeypatch):
    """STRUCTURAL_FINAL scoring is a completely separate (episode_id, review_horizon) row -- it must
    never overwrite or duplicate an already-written H1 row for the same episode."""
    row = _episode_row(frozen_at_bar_ts=base_ts, direction="BULLISH", price=1900.0, origin_price=1896.0)
    prediction = {"ai_trader_expectation": "FOLLOW_THROUGH_LIKELY", "confidence": "HIGH"}
    h1_bars = [make_bar(ts_open=base_ts + i * M15_SECONDS, o=1900, h=1905, l=1899, c=1904) for i in range(1, 5)]
    h1_entries = scorecard.score_due_horizons_for_episode(row, prediction, h1_bars)
    for entry in h1_entries:
        durable_store.append_scorecard(entry)
    assert scorecard.already_scored(row["episode_id"], "H1") is True

    structural_bars = [make_bar(ts_open=base_ts + M15_SECONDS, o=1901, h=1902, l=1900.5, c=1901.5)]
    structural_entry = scorecard.score_structural_final_for_episode(row, prediction, structural_bars, [])
    durable_store.append_scorecard(structural_entry)

    rows = durable_store.read_scorecard_rows(row["episode_id"])
    horizons_present = sorted(r["review_horizon"] for r in rows)
    assert horizons_present == ["H1", "STRUCTURAL_FINAL"]
    h1_row_after = next(r for r in rows if r["review_horizon"] == "H1")
    assert h1_row_after["expectation_correct"] == h1_entries[0].expectation_correct  # untouched


def test_score_structural_final_already_scored_returns_none(base_ts):
    row = _episode_row(frozen_at_bar_ts=base_ts, direction="BULLISH", price=1900.0, origin_price=1896.0)
    prediction = {"ai_trader_expectation": "FOLLOW_THROUGH_LIKELY", "confidence": "HIGH"}
    entry = ScorecardEntry(
        episode_id=row["episode_id"], review_horizon="STRUCTURAL_FINAL", original_expectation="FOLLOW_THROUGH_LIKELY",
        original_confidence="HIGH", mechanical_outcome_summary="x", expectation_correct="YES",
        partial_reason=None, scored_at_utc="2026-01-01T00:00:00+00:00",
    )
    durable_store.append_scorecard(entry)
    bars = [make_bar(ts_open=base_ts + M15_SECONDS, o=1901, h=1902, l=1900.5, c=1901.5)]
    assert scorecard.score_structural_final_for_episode(row, prediction, bars, []) is None
