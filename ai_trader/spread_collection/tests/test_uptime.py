"""`compute_session_uptime` tests -- ground truth (fake `copy_rates_range`) vs recorded
(`SpreadObservationLog`), independently of each other, per the module's own design: a source that only
reports on its own polls cannot detect its own downtime."""

from __future__ import annotations

from typing import Any

from ai_trader.spread_collection.journal import SpreadObservationLog
from ai_trader.spread_collection.types import SpreadObservation
from ai_trader.spread_collection.uptime import compute_session_uptime

SYMBOL = "XAUUSD"
BAR_SECONDS = 900

# 2026-08-04 06:45:00 UTC (asia, hh=6) -- ts_open; ts_close = 07:00:00 UTC, still asia (hh=7)
ASIA_BAR_OPEN = 1785912300
# 2026-08-04 08:15:00 UTC (london, hh=8) -- ts_close = 08:30:00 UTC
LONDON_BAR_OPEN = 1785917700


class _FakeGateway:
    def __init__(self, rates: list[dict[str, Any]]) -> None:
        self._rates = rates

    def copy_rates_range(self, symbol: str, timeframe: int, date_from: int, date_to: int) -> Any:
        return [r for r in self._rates if date_from <= r["time"] <= date_to]


def _rate(ts_open: int) -> dict[str, Any]:
    return {"time": ts_open}


def _obs(as_of: int, session: str) -> SpreadObservation:
    return SpreadObservation(
        symbol=SYMBOL, as_of=as_of, bid=1.0, ask=1.01, spread=0.01, session=session,
        atr=1.0, day_boundary_label=0, is_level_touch=False, touch_level_kind=None,
    )


def test_bars_passed_counted_from_ground_truth_independent_of_journal() -> None:
    gateway = _FakeGateway([_rate(ASIA_BAR_OPEN), _rate(LONDON_BAR_OPEN)])
    journal = SpreadObservationLog()  # empty -- nothing recorded
    now = LONDON_BAR_OPEN + BAR_SECONDS + 100

    reports = compute_session_uptime(
        gateway, journal, SYMBOL, 15, BAR_SECONDS,  # type: ignore[arg-type]
        window_start=ASIA_BAR_OPEN, window_end=now, now=now,
    )

    by_session = {r.session: r for r in reports}
    assert by_session["asia"].bars_passed == 1
    assert by_session["asia"].bars_recorded == 0
    assert by_session["asia"].ratio == 0.0
    assert by_session["london"].bars_passed == 1


def test_ratio_is_one_when_every_true_bar_was_recorded() -> None:
    gateway = _FakeGateway([_rate(ASIA_BAR_OPEN)])
    journal = SpreadObservationLog()
    journal.record(_obs(as_of=ASIA_BAR_OPEN + BAR_SECONDS, session="asia"))
    now = ASIA_BAR_OPEN + BAR_SECONDS + 100

    reports = compute_session_uptime(
        gateway, journal, SYMBOL, 15, BAR_SECONDS,  # type: ignore[arg-type]
        window_start=ASIA_BAR_OPEN, window_end=now, now=now,
    )

    asia = next(r for r in reports if r.session == "asia")
    assert asia.bars_passed == 1
    assert asia.bars_recorded == 1
    assert asia.ratio == 1.0


def test_ratio_is_none_when_the_window_never_touches_a_session() -> None:
    gateway = _FakeGateway([_rate(ASIA_BAR_OPEN)])
    journal = SpreadObservationLog()
    now = ASIA_BAR_OPEN + BAR_SECONDS + 100

    reports = compute_session_uptime(
        gateway, journal, SYMBOL, 15, BAR_SECONDS,  # type: ignore[arg-type]
        window_start=ASIA_BAR_OPEN, window_end=now, now=now,
    )

    ny = next(r for r in reports if r.session == "ny")
    assert ny.bars_passed == 0
    assert ny.ratio is None


def test_still_forming_bar_is_never_counted_as_passed() -> None:
    """A bar whose close time has not yet passed `now` could not possibly have been observed by the
    collector -- counting it against bars_passed would understate the true ratio."""
    gateway = _FakeGateway([_rate(ASIA_BAR_OPEN)])
    journal = SpreadObservationLog()
    now = ASIA_BAR_OPEN + 100  # bar has not closed yet (close = ASIA_BAR_OPEN + 900)

    reports = compute_session_uptime(
        gateway, journal, SYMBOL, 15, BAR_SECONDS,  # type: ignore[arg-type]
        window_start=ASIA_BAR_OPEN, window_end=now, now=now,
    )

    asia = next(r for r in reports if r.session == "asia")
    assert asia.bars_passed == 0


def test_bar_closing_exactly_at_window_start_boundary_is_included() -> None:
    """A bar whose open is just BEFORE window_start but whose close lands exactly at window_start must
    still be counted -- this is the boundary the ts_close-based window comparison exists to fix."""
    ts_close = ASIA_BAR_OPEN + BAR_SECONDS
    gateway = _FakeGateway([_rate(ASIA_BAR_OPEN)])
    journal = SpreadObservationLog()
    now = ts_close + 100

    reports = compute_session_uptime(
        gateway, journal, SYMBOL, 15, BAR_SECONDS,  # type: ignore[arg-type]
        window_start=ts_close, window_end=now, now=now,  # window starts AT the bar's close
    )

    asia = next(r for r in reports if r.session == "asia")
    assert asia.bars_passed == 1


def test_recorded_count_ignores_observations_outside_the_window() -> None:
    gateway = _FakeGateway([_rate(ASIA_BAR_OPEN)])
    journal = SpreadObservationLog()
    journal.record(_obs(as_of=ASIA_BAR_OPEN - 10_000, session="asia"))  # well before the window
    now = ASIA_BAR_OPEN + BAR_SECONDS + 100

    reports = compute_session_uptime(
        gateway, journal, SYMBOL, 15, BAR_SECONDS,  # type: ignore[arg-type]
        window_start=ASIA_BAR_OPEN, window_end=now, now=now,
    )

    asia = next(r for r in reports if r.session == "asia")
    assert asia.bars_recorded == 0


def test_recorded_count_ignores_a_different_symbol() -> None:
    gateway = _FakeGateway([_rate(ASIA_BAR_OPEN)])
    journal = SpreadObservationLog()
    journal.record(SpreadObservation(
        symbol="EURUSD", as_of=ASIA_BAR_OPEN + BAR_SECONDS, bid=1.0, ask=1.01, spread=0.01,
        session="asia", atr=1.0, day_boundary_label=0, is_level_touch=False, touch_level_kind=None,
    ))
    now = ASIA_BAR_OPEN + BAR_SECONDS + 100

    reports = compute_session_uptime(
        gateway, journal, SYMBOL, 15, BAR_SECONDS,  # type: ignore[arg-type]
        window_start=ASIA_BAR_OPEN, window_end=now, now=now,
    )

    asia = next(r for r in reports if r.session == "asia")
    assert asia.bars_recorded == 0


def test_all_four_sessions_always_present_in_the_output() -> None:
    gateway = _FakeGateway([])
    journal = SpreadObservationLog()
    now = ASIA_BAR_OPEN

    reports = compute_session_uptime(
        gateway, journal, SYMBOL, 15, BAR_SECONDS,  # type: ignore[arg-type]
        window_start=0, window_end=now, now=now,
    )

    assert {r.session for r in reports} == {"asia", "london", "ny", "late"}
