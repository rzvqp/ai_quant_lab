import pathlib
import sys
from datetime import datetime, timedelta, timezone

ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class FakeClient:
    """Stub TvClient (no capability gate, no subprocess) for TVRE logic tests."""

    def __init__(self, responses=None):
        self.responses = responses or {}
        self.calls = []

    def _resolve(self, verb, params):
        v = self.responses.get(verb)
        if callable(v):
            return v(params)
        return v if v is not None else {}

    def call(self, verb, params=None, *, task_id=None):
        self.calls.append((verb, params))
        return self._resolve(verb, params)

    def try_call(self, verb, params=None, *, task_id=None):
        try:
            return self.call(verb, params, task_id=task_id)
        except Exception:
            return None

    def batch(self, ops, *, task_id=None, strict=True):
        out = []
        for verb, params in ops:
            self.calls.append((verb, params))
            out.append({"ok": True, "verb": verb, "result": self._resolve(verb, params)})
        return out

    def verbs_called(self):
        return [v for v, _ in self.calls]


class FakeDataAccess:
    def __init__(self, n=3000):
        base = datetime(2024, 1, 1, tzinfo=timezone.utc)
        self._ts = [(base + timedelta(hours=i)).isoformat() for i in range(n)]

    def timestamps(self, tf):
        return self._ts

    def get_window(self, window):
        return ({"n_bars": 0}, {"data_source": "csv_fallback"})
