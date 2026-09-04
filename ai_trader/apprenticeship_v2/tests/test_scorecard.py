"""Mandate Section 26 (AFTER scorecard): per-horizon due/pending gating, restart-safety
(`already_scored`), the BULLISH/BEARISH -> LONG/SHORT direction-vocabulary bridge, and the disclosed
`classify_expectation_correct` gap (deliberately raises rather than guessing a threshold -- see
`scorecard.py`'s own module docstring).
"""

from __future__ import annotations

import pytest

from ai_trader.apprenticeship_v2 import durable_store
from ai_trader.apprenticeship_v2.general_observer import scorecard
from ai_trader.apprenticeship_v2.schemas import HorizonMetrics, ScorecardEntry
from ai_trader.apprenticeship_v2.tests.conftest import M15_SECONDS, make_bar


@pytest.fixture(autouse=True)
def _isolated_scorecard_csv(tmp_path, monkeypatch):
    """Redirects `durable_store.SCORECARD_CSV` to a throwaway temp file for every test in this
    module -- these tests must never read or write the real, live production scorecard file."""
    monkeypatch.setattr(durable_store, "SCORECARD_CSV", tmp_path / "AI_TRADER_SCORECARD.csv")


def _episode_row(*, episode_id="GO-TEST-1", frozen_at_bar_ts, direction="BULLISH", price=1900.0):
    return {
        "episode_id": episode_id, "frozen_at_bar_ts": str(frozen_at_bar_ts),
        "directional_hypothesis": direction, "current_price": str(price),
    }


def _stub_metrics() -> HorizonMetrics:
    return HorizonMetrics(
        forward_return=1.0, mfe=1.5, mae=0.2, max_up_move=1.5, max_down_move=0.2,
        close_location=0.8, directional_follow_through=True, round_trip_magnitude=0.1,
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


def test_classify_expectation_correct_deliberately_raises_not_implemented():
    """The disclosed VE_SEMANTIC_GAP_FOUND -- proves the gap surfaces loudly rather than being
    silently papered over with a guessed threshold."""
    with pytest.raises(NotImplementedError):
        scorecard.classify_expectation_correct("FOLLOW_THROUGH_LIKELY", _stub_metrics())


def test_score_due_horizons_raises_rather_than_fabricating_a_verdict(base_ts):
    row = _episode_row(frozen_at_bar_ts=base_ts)
    prediction = {"ai_trader_expectation": "FOLLOW_THROUGH_LIKELY", "confidence": "HIGH"}
    forward = [make_bar(ts_open=base_ts + i * M15_SECONDS, o=1900, h=1905, l=1899, c=1904) for i in range(1, 5)]
    with pytest.raises(NotImplementedError):
        scorecard.score_due_horizons_for_episode(row, prediction, forward)
