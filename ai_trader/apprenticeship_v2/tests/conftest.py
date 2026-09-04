"""Pytest configuration for `ai_trader.apprenticeship_v2` tests: make the repo root importable, and
provide a `FakeBar` factory that is shape-compatible with `mt5_read_only_source.ReadOnlyBar` without
importing that module (which transitively requires the `MetaTrader5` package, not installed in this
test environment -- confirmed by trying the import first; see `general_observer/primitives.py`'s own
docstring for the same finding). `FakeBar` carries the exact same field set
(`symbol, timeframe, ts_open, ts_close, open, high, low, close, volume`) so every general_observer
function (which only ever does attribute access, never `isinstance(bar, ReadOnlyBar)`) works
identically against it.
"""

from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import pytest

M15_SECONDS = 15 * 60
H1_SECONDS = 60 * 60
H4_SECONDS = 4 * 60 * 60


@dataclasses.dataclass(frozen=True, slots=True)
class FakeBar:
    symbol: str
    timeframe: int
    ts_open: int
    ts_close: int
    open: float
    high: float
    low: float
    close: float
    volume: float | None = 100.0


def make_bar(*, ts_open: int, o: float, h: float, l: float, c: float, bar_seconds: int = M15_SECONDS, volume: float = 100.0) -> FakeBar:
    return FakeBar(symbol="XAUUSD", timeframe=0, ts_open=ts_open, ts_close=ts_open + bar_seconds, open=o, high=h, low=l, close=c, volume=volume)


def make_flat_series(*, start_ts: int, count: int, price: float, bar_seconds: int = M15_SECONDS, volume: float = 100.0) -> list[FakeBar]:
    return [
        make_bar(ts_open=start_ts + i * bar_seconds, o=price, h=price, l=price, c=price, bar_seconds=bar_seconds, volume=volume)
        for i in range(count)
    ]


@pytest.fixture
def base_ts() -> int:
    """2020-10-01T00:00:00 UTC -- an arbitrary but fixed, round-hour anchor, matching the convention
    already established in `csv_causal_replay`'s own test suite."""
    return 1_601_510_400
