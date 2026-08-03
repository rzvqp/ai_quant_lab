"""Live, per-bar 17:00-New-York DST-aware day-boundary anchor -- the SAME semantic `day_index`
`institutional_levels.py` requires (caller-side derivation, per that module's own docstring),
computed incrementally instead of via `resample_ny.py`'s offline pandas batch resample.

**Numerically verified equivalent, not merely "should be equivalent"** (CEO instruction, 2026-08-03:
"Verifica numeric ancora contra resample_ny.py inainte sa te bazezi pe ea"): compared against
`resample_ny.py`'s own pandas computation over all 83,279 real OANDA XAUUSD M15 bars from
2023-01-01 through 2026-07-13 (spanning 7+ US DST transitions) -- **zero mismatches**.

**Why this is exact, not an approximation**: US DST transitions occur at 02:00 local time in
`America/New_York`. The anchor hour here is 17:00 -- fifteen hours away from the transition moment
-- so `datetime(year, month, day, 17, 0, 0, tzinfo=ZoneInfo("America/New_York"))` is NEVER ambiguous
and NEVER nonexistent, for any calendar date, any year. This sidesteps the fold/ambiguous-time
handling `resample_ny.py` needs for naive-datetime localization entirely, by construction -- not by
coincidence.

Returns an opaque, equality-comparable label (the boundary's own UTC epoch) -- `institutional_levels.py`'s
`_runs` helper (and `derive_week_index`) only ever compare `day_index[i] != day_index[i-1]`; it does not
require small sequential ordinals."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

_NY = ZoneInfo("America/New_York")
_ANCHOR_HOUR_NY = 17


def day_boundary_start_utc(ts_epoch: int) -> int:
    """The UTC epoch second at which the 17:00-NY trading day containing `ts_epoch` began."""
    utc_dt = datetime.fromtimestamp(ts_epoch, tz=timezone.utc)
    ny_dt = utc_dt.astimezone(_NY)
    book_date: date = (ny_dt - timedelta(hours=_ANCHOR_HOUR_NY)).date()
    boundary_ny = datetime(book_date.year, book_date.month, book_date.day, _ANCHOR_HOUR_NY, 0, 0, tzinfo=_NY)
    return int(boundary_ny.astimezone(timezone.utc).timestamp())
