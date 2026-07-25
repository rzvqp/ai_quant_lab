"""Calendar (F4) — granița zilei = 00:00 UTC; ora zilei pe ore UTC (Calea A).

Nicio conversie locală, niciun DST. `day_index(ts) = ts // 86400` = ziua
calendaristică UTC (epoch 0 = 1970-01-01 00:00 UTC).
"""

from __future__ import annotations

SECONDS_PER_DAY = 86400


def day_index(ts: int) -> int:
    return ts // SECONDS_PER_DAY


def seconds_of_day(ts: int) -> int:
    return ts % SECONDS_PER_DAY


def hms_to_seconds(hms: str) -> int:
    """'13:00:00' -> 46800. '24:00:00' -> 86400 (capăt de zi)."""
    h, m, s = (int(x) for x in hms.split(":"))
    return h * 3600 + m * 60 + s


def session_of(ts: int, boundaries: list[dict]) -> str | None:
    """Eticheta de sesiune pentru un timestamp, după granițele declarate (UTC)."""
    sod = seconds_of_day(ts)
    for b in boundaries:
        start = hms_to_seconds(b["start_utc"])
        end = hms_to_seconds(b["end_utc"])
        if start <= sod < end:
            return b["name"]
    return None
