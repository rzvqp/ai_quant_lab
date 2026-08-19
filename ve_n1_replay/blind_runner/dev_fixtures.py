"""Fixture-uri de DEZVOLTARE pt. testarea instalației inference/scoring -- generate MECANIC, FĂRĂ
nicio referire la etichetele CEO sau la cele 48 de ferestre reale (independent complet de
`construction_reproduction/`, deliberat, ca să nu existe nicio cale de "scurgere" între cele
două componente nici măcar în teste). Nu reprezintă bare reale, nu sunt derivate din nicio
etichetă -- simple zigzag-uri deterministe, suficiente doar pt. a exercita I/O-ul runnerului."""
from __future__ import annotations

from typing import Any


def make_dev_bars(n: int = 60, start_ts: int = 1_700_000_000, interval: int = 900) -> list[dict[str, Any]]:
    bars = []
    level = 100.0
    ts_close = start_ts
    for i in range(n):
        turn = level + (5.0 if (i // 4) % 2 == 0 else -5.0)
        c = level + (turn - level) * ((i % 4) + 1) / 4
        o = c - (turn - level) / 4 * 0.4
        h = max(o, c) + 0.3
        lo = min(o, c) - 0.3
        bars.append({"ts_open": ts_close, "ts_close": ts_close + interval, "open": o, "high": h,
                    "low": lo, "close": c, "volume": 100.0, "is_backfilled": False})
        level = c
        ts_close += interval
    return bars


def make_dev_input(n_windows: int = 2, bars_per_window: int = 60) -> dict[str, Any]:
    return {
        "windows": [
            {
                "window_id": f"DEV-{k:03d}", "symbol": "XAUUSD", "timeframe": "15m",
                "bar_interval_seconds": 900,
                "bars": make_dev_bars(n=bars_per_window, start_ts=1_700_000_000 + k * 10_000_000),
            }
            for k in range(n_windows)
        ]
    }


def make_dev_labels_empty() -> dict[str, Any]:
    """Etichete de dezvoltare minimale -- fara pretentia de a reprezenta un adevar de teren real,
    doar suficiente ca sa exercite scorer-ul pe o populatie mica, controlata."""
    return {"segments": []}
