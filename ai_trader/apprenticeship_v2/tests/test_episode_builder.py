"""Mandate Section 26 (BEFORE pipeline / dedup / underlying-move-id / Section 4D composition):
end-to-end `build_episodes_for_bar` tests covering single-event shells, same-bar multi-class sharing,
duplicate suppression, session-transition-reversal child/attachment semantics, and the "no episode"
null case.
"""

from __future__ import annotations

from ai_trader.apprenticeship_v2.general_observer.episode_builder import build_episodes_for_bar
from ai_trader.apprenticeship_v2.general_observer.snapshot import verify_snapshot_hash
from ai_trader.apprenticeship_v2.tests.conftest import H1_SECONDS, M15_SECONDS, make_bar, make_flat_series

SYMBOL = "XAUUSD"


def _prev_day_h1_bars(day0_ts: int, *, low: float = 1899.0, high: float = 1901.0) -> list:
    return [
        make_bar(ts_open=day0_ts + i * H1_SECONDS, o=1900.0, h=high, l=low, c=1900.0, bar_seconds=H1_SECONDS)
        for i in range(24)
    ]


def test_single_sweep_produces_one_pending_episode_with_correct_fields(base_ts):
    day0 = base_ts  # 2020-10-01 (ASIA hour 0)
    day1 = base_ts + 86400
    h1 = _prev_day_h1_bars(day0, low=1899.0, high=1901.0)
    m15_lead = make_flat_series(start_ts=day1, count=20, price=1900.0)
    trigger = make_bar(ts_open=day1 + 20 * M15_SECONDS, o=1900.0, h=1900.5, l=1898.0, c=1900.2)
    m15 = m15_lead + [trigger]

    episodes = build_episodes_for_bar(
        trigger, symbol=SYMBOL, h4=[], h1=h1, m15_causal_bars_up_to_and_including_bar=m15, m5=[],
        existing_general_episode_rows=[],
    )

    assert len(episodes) == 1
    ep = episodes[0]
    assert ep.episode_type == "SWEEP_REJECTION"
    assert ep.directional_hypothesis == "BULLISH"
    assert ep.setup_direction is None  # S5 isolation
    assert ep.trigger_timeframe == "M15"
    assert ep.qualitative_review_status == "PENDING_LLM_REVIEW"
    assert ep.prospective_eligibility == "YES"
    assert ep.frozen_at_bar_ts == trigger.ts_close
    assert ep.reference_levels["swept_level_type"] == "PREVIOUS_DAY_LOW"
    assert ep.reference_levels["swept_level_price"] == 1899.0
    assert ep.underlying_move_id is not None
    assert verify_snapshot_hash(ep.snapshot, ep.frozen_snapshot_hash) is True


def test_no_episode_when_nothing_fires(base_ts):
    day0 = base_ts
    day1 = base_ts + 86400
    h1 = _prev_day_h1_bars(day0, low=1899.0, high=1901.0)
    m15 = make_flat_series(start_ts=day1, count=21, price=1900.0)  # entirely flat -- nothing crosses/sweeps/displaces
    trigger = m15[-1]

    episodes = build_episodes_for_bar(
        trigger, symbol=SYMBOL, h4=[], h1=h1, m15_causal_bars_up_to_and_including_bar=m15, m5=[],
        existing_general_episode_rows=[],
    )
    assert episodes == []


def test_sweep_and_displacement_same_bar_share_one_underlying_move_id(base_ts):
    """A single bar that is BOTH a sweep (low breach + reclaim) AND a qualifying 2x-ATR displacement
    (huge body -- which, in this fixture, also crosses the previous-day-high closing level, so a
    STRUCTURAL_BREAK correctly co-fires too) produces one episode PER co-firing class (Section 8's
    family model represents several observations of one move, never collapses them into one row),
    all three sharing ONE underlying_move_id."""
    day0 = base_ts
    day1 = base_ts + 86400
    h1 = _prev_day_h1_bars(day0, low=1899.0, high=1901.0)
    # 20 lead bars with TR=1.0 each (h=1900.5, l=1899.5 around a flat o=c=1900 prevclose chain).
    m15_lead = [
        make_bar(ts_open=day1 + i * M15_SECONDS, o=1900.0, h=1900.5, l=1899.5, c=1900.0) for i in range(20)
    ]
    # Trigger: low breaches 1899 (sweep) AND close far above open (large body -> displacement).
    trigger = make_bar(ts_open=day1 + 20 * M15_SECONDS, o=1900.0, h=1906.0, l=1898.0, c=1905.0)
    m15 = m15_lead + [trigger]

    episodes = build_episodes_for_bar(
        trigger, symbol=SYMBOL, h4=[], h1=h1, m15_causal_bars_up_to_and_including_bar=m15, m5=[],
        existing_general_episode_rows=[],
    )

    types = {ep.episode_type for ep in episodes}
    assert {"SWEEP_REJECTION", "DISPLACEMENT"} <= types
    move_ids = {ep.underlying_move_id for ep in episodes}
    assert len(move_ids) == 1  # one shared family, regardless of how many classes co-fired
    for ep in episodes:
        assert ep.directional_hypothesis == "BULLISH"


def test_duplicate_sweep_on_next_bar_is_suppressed(base_ts):
    day0 = base_ts
    day1 = base_ts + 86400
    h1 = _prev_day_h1_bars(day0, low=1899.0, high=1901.0)
    m15_lead = make_flat_series(start_ts=day1, count=20, price=1900.0)
    trigger1 = make_bar(ts_open=day1 + 20 * M15_SECONDS, o=1900.0, h=1900.5, l=1898.0, c=1900.2)
    m15_a = m15_lead + [trigger1]

    first = build_episodes_for_bar(
        trigger1, symbol=SYMBOL, h4=[], h1=h1, m15_causal_bars_up_to_and_including_bar=m15_a, m5=[],
        existing_general_episode_rows=[],
    )
    assert len(first) == 1
    existing_rows = [
        {
            "episode_type": ep.episode_type, "frozen_at_bar_ts": str(ep.frozen_at_bar_ts),
            "directional_hypothesis": ep.directional_hypothesis,
            "reference_levels_json": __import__("json").dumps(ep.reference_levels),
            "underlying_move_id": ep.underlying_move_id,
        }
        for ep in first
    ]

    # A second bar, same level/price/direction -- structurally the same sweep re-triggering.
    trigger2 = make_bar(ts_open=trigger1.ts_close, o=1900.2, h=1900.6, l=1898.0, c=1900.3)
    m15_b = m15_a + [trigger2]

    second = build_episodes_for_bar(
        trigger2, symbol=SYMBOL, h4=[], h1=h1, m15_causal_bars_up_to_and_including_bar=m15_b, m5=[],
        existing_general_episode_rows=existing_rows,
    )
    assert second == []


def test_session_transition_reversal_attaches_to_a_separately_persisted_child(base_ts):
    """Design doc Section 4D: the reversal is a SEPARATE episode from its child (never a
    replacement), carries `reference_levels['child_episode_id']` pointing at the child's own,
    independently-persisted episode_id, and both share one underlying_move_id 'by construction'."""
    import datetime

    # Preceding session (ASIA, hours 0-7) closes BEARISH: first M15 close 1900, last M15 close 1895.
    asia_start = base_ts  # 2020-10-01T00:00 UTC -- hour 0 -> ASIA
    asia_bars = [
        make_bar(ts_open=asia_start + i * M15_SECONDS, o=1900.0 - i * 0.1, h=1900.5 - i * 0.1, l=1899.5 - i * 0.1, c=1900.0 - i * 0.1)
        for i in range(28)  # 28 * 15min = 7h -- stays within ASIA (hour 0..6)
    ]
    assert datetime.datetime.fromtimestamp(asia_bars[0].ts_open, tz=datetime.timezone.utc).hour == 0
    assert datetime.datetime.fromtimestamp(asia_bars[-1].ts_open, tz=datetime.timezone.utc).hour == 6
    # LONDON begins at hour 8 -- insert one more ASIA bar at hour 7 then transition.
    asia_last = make_bar(ts_open=asia_start + 28 * M15_SECONDS, o=1897.2, h=1897.3, l=1896.8, c=1897.0)
    asia_bars = asia_bars + [asia_last]
    assert datetime.datetime.fromtimestamp(asia_last.ts_open, tz=datetime.timezone.utc).hour == 7

    # First LONDON bar (hour 8): sweeps the prior day's low then reclaims, in the BULLISH direction
    # -- opposite to ASIA's own BEARISH close -- so it should qualify as a reversal.
    london_open_ts = asia_start + 32 * M15_SECONDS
    assert datetime.datetime.fromtimestamp(london_open_ts, tz=datetime.timezone.utc).hour == 8
    trigger = make_bar(ts_open=london_open_ts, o=1897.0, h=1897.5, l=1895.5, c=1897.4)

    h1_prev_day = _prev_day_h1_bars(asia_start - 86400, low=1896.0, high=1902.0)
    m15 = asia_bars + [trigger]

    episodes = build_episodes_for_bar(
        trigger, symbol=SYMBOL, h4=[], h1=h1_prev_day, m15_causal_bars_up_to_and_including_bar=m15, m5=[],
        existing_general_episode_rows=[],
    )

    types = [ep.episode_type for ep in episodes]
    assert "SESSION_TRANSITION_REVERSAL" in types
    assert "SWEEP_REJECTION" in types  # the child, persisted as its own row
    reversal = next(ep for ep in episodes if ep.episode_type == "SESSION_TRANSITION_REVERSAL")
    child = next(ep for ep in episodes if ep.episode_type == "SWEEP_REJECTION")
    assert reversal.reference_levels["child_episode_id"] == child.episode_id
    assert reversal.underlying_move_id == child.underlying_move_id
    assert reversal.reference_levels["prior_session_name"] == "ASIA"
    assert reversal.reference_levels["new_session_name"] == "LONDON"
    assert reversal.reference_levels["prior_session_close_direction"] == "BEARISH"
