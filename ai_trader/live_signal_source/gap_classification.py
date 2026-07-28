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

**Reported, never filled**: this module only classifies an already-detected gap -- it never estimates,
interpolates, or invents a value for what happened during it (CEO: "golul se raporteaza, nu se umple").
"""

from __future__ import annotations

from datetime import datetime, timezone

from ai_trader.live_signal_source.types import GapClassification

_SECONDS_PER_DAY = 86_400
_SATURDAY = 5  # datetime.weekday(): Monday=0 .. Sunday=6


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
    if _spans_a_saturday(gap_start, gap_end):
        return GapClassification.WEEKEND
    if _is_maintenance_window(gap_start, gap_end - gap_start):
        return GapClassification.MAINTENANCE
    return GapClassification.UNEXPECTED
