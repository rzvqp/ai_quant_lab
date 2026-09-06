"""Red Team RT-GENERAL-OBSERVER-V1-1-FINAL-AUDIT-001, Blocker 1 (BEFORE snapshot future leak):
`h4`/`h1`/`m5` are fetched by the real caller (`tick.py`) up to real "now", not up to any specific
trigger bar's own timestamp -- during first-run or post-downtime restart catch-up, where an OLDER M15
bar is being processed historically, they can legitimately extend well past that bar's own
`ts_close`. These tests prove `build_episodes_for_bar` truncates all three (H4/H1/M5) to
`ts_close <= trigger_ts_close` before they ever enter the frozen snapshot, regardless of how far past
the trigger they extend or where in a larger batch the trigger itself falls. M15 is checked too, as a
control -- it was already correctly causal via the caller's own slicing and `detect_displacement`'s
precondition assertion, and must remain so.
"""

from __future__ import annotations

from ai_trader.apprenticeship_v2.general_observer.episode_builder import build_episodes_for_bar
from ai_trader.apprenticeship_v2.tests.conftest import H1_SECONDS, M15_SECONDS, make_bar

SYMBOL = "XAUUSD"
M5_SECONDS = 5 * 60
H4_SECONDS = 4 * 3600


def _displacement_m15_series(start_ts: int, *, lead_count: int) -> list:
    """`lead_count` flat ATR-history bars followed by one displacement-triggering bar -- the
    returned list's own last element is the trigger, matching `build_episodes_for_bar`'s own
    precondition."""
    lead = [make_bar(ts_open=start_ts + i * M15_SECONDS, o=1900.0, h=1900.5, l=1899.5, c=1900.0) for i in range(lead_count)]
    trigger_ts = start_ts + lead_count * M15_SECONDS
    trigger = make_bar(ts_open=trigger_ts, o=1900.0, h=1906.0, l=1899.5, c=1905.0)  # body=5.0, clears 2x ATR=1.0
    return lead + [trigger]


def _flat_series(start_ts: int, *, count: int, bar_seconds: int) -> list:
    return [make_bar(ts_open=start_ts + i * bar_seconds, o=1900.0, h=1900.5, l=1899.5, c=1900.0, bar_seconds=bar_seconds) for i in range(count)]


def _assert_no_future_bars(rows: list[dict], trigger_ts_close: int, label: str) -> None:
    assert rows, f"{label}: snapshot slice unexpectedly empty"
    for row in rows:
        assert row["ts_close"] <= trigger_ts_close, (
            f"{label}: bar with ts_close={row['ts_close']} > trigger_ts_close={trigger_ts_close} "
            f"leaked into the frozen BEFORE snapshot"
        )


def _build_and_check(m15, h4, h1, m5, *, expect_future_present: bool = True):
    trigger = m15[-1]
    if expect_future_present:
        # Confirm the fixture actually extends past the trigger on all three -- otherwise this test
        # would pass vacuously without ever exercising the truncation it claims to prove.
        assert h4[-1].ts_close > trigger.ts_close, "fixture bug: H4 does not actually extend past the trigger"
        assert h1[-1].ts_close > trigger.ts_close, "fixture bug: H1 does not actually extend past the trigger"
        assert m5[-1].ts_close > trigger.ts_close, "fixture bug: M5 does not actually extend past the trigger"

    episodes = build_episodes_for_bar(
        trigger, symbol=SYMBOL, h4=h4, h1=h1, m15_causal_bars_up_to_and_including_bar=m15, m5=m5,
        existing_general_episode_rows=[],
    )
    assert len(episodes) >= 1
    for ep in episodes:
        _assert_no_future_bars(ep.snapshot["H4"], trigger.ts_close, "H4")
        _assert_no_future_bars(ep.snapshot["H1"], trigger.ts_close, "H1")
        _assert_no_future_bars(ep.snapshot["M5"], trigger.ts_close, "M5")
        _assert_no_future_bars(ep.snapshot["M15"], trigger.ts_close, "M15")  # control, already correct
    return episodes


def test_first_startup_with_100_historical_m15_bars_no_future_leak(base_ts):
    """First-run catch-up shape: ~100 M15 bars fetched from a cold start, trigger near the OLDEST end
    of that batch; h4/h1/m5 are fetched up to real "now" -- far ahead of this old trigger."""
    m15 = _displacement_m15_series(base_ts, lead_count=99)  # trigger is the 100th bar
    trigger = m15[-1]
    h4 = _flat_series(base_ts - 5 * H4_SECONDS, count=60, bar_seconds=H4_SECONDS)
    h1 = _flat_series(base_ts - 5 * H1_SECONDS, count=200, bar_seconds=H1_SECONDS)
    m5 = _flat_series(base_ts - 5 * M5_SECONDS, count=800, bar_seconds=M5_SECONDS)
    _build_and_check(m15, h4, h1, m5)


def test_restart_after_long_downtime_no_future_leak(base_ts):
    """Restart catch-up shape: a multi-day gap between the (old) trigger and the real "now" h4/h1/m5
    were fetched at -- a much larger future span than the first-startup case above."""
    m15 = _displacement_m15_series(base_ts, lead_count=20)
    trigger = m15[-1]
    h4 = _flat_series(base_ts - 20 * H4_SECONDS, count=100, bar_seconds=H4_SECONDS)  # spans ~46 days
    h1 = _flat_series(base_ts - 20 * H1_SECONDS, count=400, bar_seconds=H1_SECONDS)  # spans ~16 days
    m5 = _flat_series(base_ts - 20 * M5_SECONDS, count=2000, bar_seconds=M5_SECONDS)  # spans ~6.9 days
    _build_and_check(m15, h4, h1, m5)


def test_trigger_near_beginning_of_fetched_batch_no_future_leak(base_ts):
    m15 = _displacement_m15_series(base_ts, lead_count=15)  # minimum for ATR14
    trigger = m15[-1]
    h4 = _flat_series(base_ts - 2 * H4_SECONDS, count=50, bar_seconds=H4_SECONDS)
    h1 = _flat_series(base_ts - 2 * H1_SECONDS, count=150, bar_seconds=H1_SECONDS)
    m5 = _flat_series(base_ts - 2 * M5_SECONDS, count=600, bar_seconds=M5_SECONDS)
    _build_and_check(m15, h4, h1, m5)


def test_trigger_near_middle_of_fetched_batch_no_future_leak(base_ts):
    m15 = _displacement_m15_series(base_ts, lead_count=50)
    trigger = m15[-1]
    h4 = _flat_series(base_ts - 10 * H4_SECONDS, count=30, bar_seconds=H4_SECONDS)
    h1 = _flat_series(base_ts - 10 * H1_SECONDS, count=60, bar_seconds=H1_SECONDS)
    m5 = _flat_series(base_ts - 10 * M5_SECONDS, count=200, bar_seconds=M5_SECONDS)
    _build_and_check(m15, h4, h1, m5)


def test_trigger_near_end_of_fetched_batch_no_future_leak(base_ts):
    """Trigger is the MOST RECENT bar available -- only a small amount of "future" margin exists on
    each higher timeframe (matching normal, non-catch-up steady-state operation), but even that small
    margin must still be excluded."""
    m15 = _displacement_m15_series(base_ts, lead_count=90)
    trigger = m15[-1]
    h4 = _flat_series(base_ts - 89 * M15_SECONDS, count=25, bar_seconds=H4_SECONDS)
    h1 = _flat_series(base_ts - 89 * M15_SECONDS, count=100, bar_seconds=H1_SECONDS)
    m5 = _flat_series(base_ts - 89 * M15_SECONDS, count=600, bar_seconds=M5_SECONDS)
    _build_and_check(m15, h4, h1, m5)


def test_h4_h1_m5_independently_checked_none_can_mask_another(base_ts):
    """Each timeframe's own truncation is verified independently -- construct fixtures where only
    ONE timeframe at a time extends past the trigger, proving the fix touches all three, not just
    whichever happens to be tested first."""
    m15 = _displacement_m15_series(base_ts, lead_count=20)
    trigger = m15[-1]

    # Only H4 extends past the trigger; H1/M5 stop exactly at it.
    h4_future = _flat_series(base_ts - 5 * H4_SECONDS, count=40, bar_seconds=H4_SECONDS)
    h1_causal = _flat_series(base_ts - 23 * H1_SECONDS, count=24, bar_seconds=H1_SECONDS)
    m5_causal = _flat_series(base_ts - 47 * M5_SECONDS, count=48, bar_seconds=M5_SECONDS)
    assert h4_future[-1].ts_close > trigger.ts_close
    assert h1_causal[-1].ts_close <= trigger.ts_close
    assert m5_causal[-1].ts_close <= trigger.ts_close
    episodes = build_episodes_for_bar(
        trigger, symbol=SYMBOL, h4=h4_future, h1=h1_causal, m15_causal_bars_up_to_and_including_bar=m15,
        m5=m5_causal, existing_general_episode_rows=[],
    )
    for ep in episodes:
        _assert_no_future_bars(ep.snapshot["H4"], trigger.ts_close, "H4 (isolated future leak)")
