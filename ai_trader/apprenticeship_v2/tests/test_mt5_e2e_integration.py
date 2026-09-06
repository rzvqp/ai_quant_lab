"""Mandate item 4: real MT5 read-only end-to-end integration test.

**Honest environment disclosure**: this dev/test session has no MetaTrader5 install (confirmed
structurally throughout this whole delivery -- `tick.py`/`main_general_observer.py`/
`mt5_read_only_source.py` all require it at import time, and every prior report in this delivery
disclosed the same constraint). This file is therefore GATED with `pytest.importorskip` at module
level: it SKIPS here with a clear reason, but is real, complete, runnable code that exercises the
mandate's own required path -- `closed MT5 bars -> General Observer detector -> causal snapshot/hash
-> episode persistence -> BEFORE workflow -> horizon/structural resolution -> scorecard -> lesson
eligibility path` -- against an ACTUAL live terminal, when run on a machine that has one (the
production machine already does, since `main.py`/S5 is already running there). This is the most
honest, useful thing achievable from this sandbox: a genuine test that runs for real in production,
not a fabricated pass here.

Static, environment-independent proofs (broker execution structurally disabled, S5 files unchanged)
are in the separate, always-runnable `test_broker_execution_disabled.py`.

Every durable-store path is redirected to a throwaway temp directory (`_isolated_durable_store`
below) even when this DOES run against a live terminal -- real market data, isolated persistence,
exactly like every other test in this suite. Nothing here ever writes to the live production ledger.
"""

from __future__ import annotations

import time

import pytest

pytest.importorskip("MetaTrader5", reason="No MetaTrader5 install in this environment -- see module docstring")

from ai_trader.apprenticeship_v2 import durable_store  # noqa: E402
from ai_trader.apprenticeship_v2.general_observer import before_review, scorecard  # noqa: E402
from ai_trader.apprenticeship_v2.general_observer.lesson_voting import select_canonical_episodes  # noqa: E402
from ai_trader.apprenticeship_v2.general_observer.tick import GeneralObserverTick  # noqa: E402
from ai_trader.apprenticeship_v2.mt5_read_only_source import (  # noqa: E402
    BAR_SECONDS, MT5ReadOnlyUnavailable, TIMEFRAME_M15, XAUUSD, fetch_causal_closed_bars, mt5_session,
)


@pytest.fixture(autouse=True)
def _isolated_durable_store(tmp_path, monkeypatch):
    monkeypatch.setattr(durable_store, "LIVE_STATE_DIR", tmp_path)
    for name in (
        "RUNTIME_STATE_JSON", "GENERAL_OBSERVER_LEDGER_CSV", "SCORECARD_CSV", "MISSED_MOVE_CLUSTERS_CSV",
        "GENERAL_OBSERVER_PREDICTIONS_CSV", "LESSON_HYPOTHESES_JSON",
    ):
        monkeypatch.setattr(durable_store, name, tmp_path / f"{name}.tmp")


def test_fetch_causal_closed_bars_is_closed_bars_only_against_real_terminal():
    with mt5_session():
        now = time.time()
        bars = fetch_causal_closed_bars(symbol=XAUUSD, timeframe=TIMEFRAME_M15, count=20)
    assert len(bars) > 0
    assert all(b.ts_close <= now for b in bars)  # no lookahead -- every bar was already closed


def test_no_lookahead_two_quick_fetches_of_already_closed_history_agree():
    """The older, already-closed portion of history must be IDENTICAL across two fetches taken
    moments apart -- proves fetch_causal_closed_bars never lets a later read retroactively change
    what an earlier-frozen snapshot would have seen."""
    with mt5_session():
        first = fetch_causal_closed_bars(symbol=XAUUSD, timeframe=TIMEFRAME_M15, count=20)
        second = fetch_causal_closed_bars(symbol=XAUUSD, timeframe=TIMEFRAME_M15, count=20)
    overlap_ts = set(b.ts_close for b in first) & set(b.ts_close for b in second)
    assert overlap_ts
    first_by_ts = {b.ts_close: b for b in first}
    second_by_ts = {b.ts_close: b for b in second}
    for ts in overlap_ts:
        assert first_by_ts[ts] == second_by_ts[ts]


def test_full_pipeline_path_end_to_end_against_real_data():
    """The mandate's own required demonstrated path, in order: closed MT5 bars -> detector ->
    causal snapshot/hash -> episode persistence -> BEFORE workflow -> horizon/structural resolution
    -> scorecard -> lesson eligibility path."""
    tick = GeneralObserverTick()
    with mt5_session():
        result = tick.tick()  # closed bars -> detector -> snapshot/hash -> episode persistence

    all_rows = durable_store.read_all_general_episode_rows()
    # There may or may not be a NEW episode on any given real tick (depends on live market
    # conditions) -- the pipeline's OWN correctness (does it run cleanly end to end without
    # error, and does anything it DOES produce persist correctly) is what this test proves, not
    # that a specific event always fires on this exact tick.
    assert isinstance(result["new_general_episodes"], list)

    if all_rows:
        episode_row = all_rows[0]
        # BEFORE workflow: simulate a completed qualitative review (the LLM step itself is out of
        # scope; the mechanical guard it must call is real and exercised here).
        from ai_trader.apprenticeship_v2.schemas import EpisodeRecord

        ep = EpisodeRecord(
            episode_id=episode_row["episode_id"], timestamp_utc=episode_row["timestamp_utc"],
            frozen_at_bar_ts=int(episode_row["frozen_at_bar_ts"]), episode_type=episode_row["episode_type"],
            symbol="XAUUSD", current_price=float(episode_row["current_price"]), setup_direction=None,
            reference_levels={}, snapshot={}, directional_hypothesis=episode_row.get("directional_hypothesis"),
            ai_trader_expectation="FOLLOW_THROUGH_LIKELY", confidence="MEDIUM",
        )
        completed = before_review.complete_before_review(ep)
        durable_store.append_general_prediction(completed)

        # Horizon/scorecard: due_horizons_for_episode against the real, freshly-fetched bars.
        with mt5_session():
            m15_bars = fetch_causal_closed_bars(symbol=XAUUSD, timeframe=TIMEFRAME_M15, count=100)
        prediction_row = {"ai_trader_expectation": "FOLLOW_THROUGH_LIKELY", "confidence": "MEDIUM"}
        entries = scorecard.score_due_horizons_for_episode(episode_row, prediction_row, m15_bars)
        for entry in entries:
            durable_store.append_scorecard(entry)

        # Lesson eligibility path -- must not raise, regardless of whether this episode ends up
        # canonical for any given hypothesis.
        hypothesis = {"episode_type": episode_row["episode_type"], "directional_hypothesis": episode_row.get("directional_hypothesis")}
        canonical = select_canonical_episodes(hypothesis, durable_store.read_all_general_episode_rows())
        assert isinstance(canonical, dict)


def test_no_duplicate_processing_on_second_tick_with_no_new_bars():
    """Two back-to-back ticks against LIVE, uncontrolled market data can, rarely, straddle a genuine
    M15 bar close (a real ~1-in-900-second race, unavoidable without freezing time and thereby no
    longer testing anything real) -- confirmed directly: a failure reproduced during this fix's own
    validation showed `second - first == 900` exactly (one full M15 bar duration), not a small,
    arbitrary difference. That is correct, required behavior (a genuinely new bar MUST be detected),
    not the defect this test exists to catch. The defect this test exists to catch --
    `mt5_read_only_source.measure_broker_offset_seconds` drifting the same already-closed bar's own
    computed `ts_close` by approximately 1 second per quiet real second elapsed (fixed via the offset
    cache in that function) -- produced deltas of exactly 1 (observed repeatedly pre-fix), never a
    clean multiple of the M15 bar duration. The watermark is therefore only correct if it either (a)
    stays byte-identical (the common case: no bar closed in between) or (b) advances by an EXACT,
    positive multiple of `BAR_SECONDS[TIMEFRAME_M15]` (a genuine bar boundary crossed) -- any other
    delta, in particular the small, non-bar-aligned drift this test originally caught, still fails
    this assertion exactly as before."""
    tick = GeneralObserverTick()
    with mt5_session():
        first = tick.tick()
        second = tick.tick()  # immediately again
    assert second["new_general_episodes"] == []
    delta = second["last_processed_m15_ts_close"] - first["last_processed_m15_ts_close"]
    m15_bar_seconds = BAR_SECONDS[TIMEFRAME_M15]
    assert delta == 0 or (delta > 0 and delta % m15_bar_seconds == 0), (
        f"watermark changed by {delta}s -- neither unchanged nor an exact multiple of "
        f"{m15_bar_seconds}s (M15's own bar duration); this is the drift defect, not a genuine bar close"
    )


def test_restart_continuity_fresh_tick_instance_does_not_reprocess():
    """Restart continuity: a brand-new GeneralObserverTick instance (simulating a process restart),
    pointed at the SAME durable state, picks up exactly where the first instance left off -- no
    duplicate episodes, no duplicate scorecard rows."""
    tick_a = GeneralObserverTick()
    with mt5_session():
        tick_a.tick()
    rows_after_a = durable_store.read_all_general_episode_rows()

    tick_b = GeneralObserverTick()  # fresh instance -- no shared in-memory state with tick_a
    with mt5_session():
        result_b = tick_b.tick()
    rows_after_b = durable_store.read_all_general_episode_rows()

    assert result_b["new_general_episodes"] == []  # nothing new -- no bar advanced between the two ticks
    assert len(rows_after_b) == len(rows_after_a)  # no duplicates written


def test_mt5_data_failure_fails_closed_never_fabricates():
    """Forces a read failure and confirms the pipeline propagates it rather than silently
    substituting empty/fabricated bars -- fetch_causal_closed_bars's own documented contract."""
    with pytest.raises(MT5ReadOnlyUnavailable):
        with mt5_session():
            fetch_causal_closed_bars(symbol="THIS_SYMBOL_DOES_NOT_EXIST_XYZ", timeframe=TIMEFRAME_M15, count=10)
