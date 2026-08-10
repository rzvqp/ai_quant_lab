"""`classify_gap` -- CEO instruction, 2026-07-27: three categories (MAINTENANCE, WEEKEND, UNEXPECTED),
all recorded, only the last one a problem.

**MAINTENANCE, reused verbatim, not rewritten** (CEO's own explicit instruction, citing the exact prior
discrepancy this avoided): `code/gapfind.py` line 11 reads
``if mins<=75 and t0.hour in (20,21): continue`` -- ``mins`` there is the raw open-to-open difference
between the last good bar and the next one (``d[i]/60`` where ``d = np.diff(m['time'].values)``), and
``t0`` is the LAST GOOD bar's own timestamp, not the gap's nominal start. `_is_maintenance_window` below
reproduces this exact boolean expression on the exact same two quantities (`gap_start` here IS that
`t0`, `duration_seconds` here IS that raw open-to-open difference in seconds) -- not a reinterpretation.

**WEEKEND, checked first**: no CEO-specified formula existed to reuse for this one (unlike MAINTENANCE),
so this is a new, disclosed decision: a gap is WEEKEND if its span contains any UTC calendar day that is
a Saturday. Robust to the exact Friday-close/Sunday-open time varying slightly by broker, and by
construction never confused with MAINTENANCE (a weekend closure is always far longer than the 75-minute
allowance).

**`EXTENDED_PAUSE`, added 2026-08-10** (CEO: "131,5 ore etichetat WEEKEND. Mecanic corect, dar nu
distinge pauza de operator... adauga o clasa: gol care depaseste durata maxima a unui weekend real"):
checked BEFORE the plain `_spans_a_saturday` check, so it is the MORE SPECIFIC classification for a
weekend-shaped gap that is anomalously long, not a fourth independent condition. `MAX_REAL_WEEKEND_SECONDS`
is empirically measured, not guessed: scanned 35 days of real MT5 XAUUSD M15 history (2026-07-06 through
2026-08-10) and found five consecutive real weekend closures, EVERY ONE exactly 49.25h (Friday 23:45 UTC
close to Sunday/Monday 01:00 UTC reopen, zero variance across five weeks) -- the actual 6-day operator
pause this same run measured as 131.5h, 2.67x that. The threshold is set at 72h (a full day of margin
above the observed 49.25h, generous enough to absorb a legitimate long-holiday weekend without ever
being mistaken for one) -- disclosed as a reasoned choice, not a re-derivation of the exact 49.25h figure
itself, since a holiday closure could plausibly run longer than an ordinary weekend and re-measuring
every possible holiday was out of scope.

**Reported, never filled**: this module only classifies an already-detected gap -- it never estimates,
interpolates, or invents a value for what happened during it (CEO: "golul se raporteaza, nu se umple").
"""

from __future__ import annotations

from datetime import datetime, timezone

from ai_trader.live_signal_source.types import GapClassification

_SECONDS_PER_DAY = 86_400
_SATURDAY = 5  # datetime.weekday(): Monday=0 .. Sunday=6

MAX_REAL_WEEKEND_SECONDS = 72 * 3600
"""72h -- see this module's own docstring for the empirical basis (five real weekends measured, every
one exactly 49.25h) and the reasoning for the margin above that figure."""


def _spans_a_saturday(gap_start: int, gap_end: int) -> bool:
    day = gap_start - (gap_start % _SECONDS_PER_DAY)
    while day < gap_end:
        if datetime.fromtimestamp(day, tz=timezone.utc).weekday() == _SATURDAY:
            return True
        day += _SECONDS_PER_DAY
    return False


def _is_maintenance_window(gap_start: int, duration_seconds: int) -> bool:
    """Verbatim reproduction of `code/gapfind.py`'s own ``mins<=75 and t0.hour in (20,21)``."""
    minutes = duration_seconds / 60.0
    start_hour = datetime.fromtimestamp(gap_start, tz=timezone.utc).hour
    return minutes <= 75 and start_hour in (20, 21)


def classify_gap(gap_start: int, gap_end: int) -> GapClassification:
    """`gap_start` is the last known-good bar's own `ts_open`; `gap_end` is the first bar seen after
    the gap. Both UTC epoch seconds."""
    duration_seconds = gap_end - gap_start
    if _spans_a_saturday(gap_start, gap_end):
        if duration_seconds > MAX_REAL_WEEKEND_SECONDS:
            return GapClassification.EXTENDED_PAUSE
        return GapClassification.WEEKEND
    if _is_maintenance_window(gap_start, duration_seconds):
        return GapClassification.MAINTENANCE
    return GapClassification.UNEXPECTED
