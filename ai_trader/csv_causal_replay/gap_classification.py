"""`classify_gap` -- logic reproduced verbatim from `ai_trader.live_signal_source.gap_classification`
(same CEO-specified MAINTENANCE formula: `mins<=75 and t0.hour in (20,21)`; same empirically-measured
72h WEEKEND/EXTENDED_PAUSE threshold, "five real weekends measured, every one exactly 49.25h") --
copied rather than imported solely to avoid this package's import graph pulling in that module's
sibling `ai_trader.live_signal_source.__init__` chain (execution_engine/MT5/schema_validation --
see `types.py`'s own docstring for the confirmed import trace). Not a reinterpretation: this is the
same two checks, in the same order, on the same two quantities.
"""

from __future__ import annotations

from datetime import datetime, timezone

from ai_trader.csv_causal_replay.types import GapClassification

_SECONDS_PER_DAY = 86_400
_SATURDAY = 5  # datetime.weekday(): Monday=0 .. Sunday=6

MAX_REAL_WEEKEND_SECONDS = 72 * 3600


def _spans_a_saturday(gap_start: int, gap_end: int) -> bool:
    day = gap_start - (gap_start % _SECONDS_PER_DAY)
    while day < gap_end:
        if datetime.fromtimestamp(day, tz=timezone.utc).weekday() == _SATURDAY:
            return True
        day += _SECONDS_PER_DAY
    return False


def _is_maintenance_window(gap_start: int, duration_seconds: int) -> bool:
    minutes = duration_seconds / 60.0
    start_hour = datetime.fromtimestamp(gap_start, tz=timezone.utc).hour
    return minutes <= 75 and start_hour in (20, 21)


def classify_gap(gap_start: int, gap_end: int) -> GapClassification:
    duration_seconds = gap_end - gap_start
    if _spans_a_saturday(gap_start, gap_end):
        if duration_seconds > MAX_REAL_WEEKEND_SECONDS:
            return GapClassification.EXTENDED_PAUSE
        return GapClassification.WEEKEND
    if _is_maintenance_window(gap_start, duration_seconds):
        return GapClassification.MAINTENANCE
    return GapClassification.UNEXPECTED
