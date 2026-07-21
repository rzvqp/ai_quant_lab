import pathlib
import sys
from datetime import datetime, timedelta, timezone

import pytest

# Put the worktree root on sys.path so `alpha_automation` and `edge_research` import cleanly,
# matching the lab convention (tests insert the needed source dir on sys.path).
ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class FakeDataAccess:
    """Deterministic, pandas-free data source for runner tests."""

    def __init__(self, n=3000, fail_get_window=False):
        base = datetime(2024, 1, 1, tzinfo=timezone.utc)
        self._ts = [(base + timedelta(hours=i)).isoformat() for i in range(n)]
        self._fail = fail_get_window

    def timestamps(self, tf):
        return self._ts

    def get_window(self, window):
        if self._fail:
            raise RuntimeError("data source down")
        summary = {"timeframe": window["timeframe"], "n_bars": window.get("n_bars_requested", 0),
                   "start": window["start"], "end": window["end"]}
        provenance = {"data_source": "csv_fallback", "n_bars": window.get("n_bars_requested", 0),
                      "timeframe": window["timeframe"]}
        return summary, provenance


@pytest.fixture
def fake_data_cls():
    return FakeDataAccess
