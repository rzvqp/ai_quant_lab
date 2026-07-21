import pytest

from alpha_automation.window_selector import MarketWindowSelector
from alpha_automation import schemas

CUTOFF = "2025-10-23T09:15:00+00:00"


def _ts(n, start_year=2024):
    # ascending hourly ISO timestamps well before the cutoff
    from datetime import datetime, timedelta, timezone
    base = datetime(start_year, 1, 1, tzinfo=timezone.utc)
    return [(base + timedelta(hours=i)).isoformat() for i in range(n)]


def _task(tf="H1", span=100, edge="E010"):
    return {
        "task_id": "INV-000001",
        "edge_ref": edge,
        "window_hint": {"timeframe": tf, "span_bars": span, "prefer_regime": "any"},
    }


def _sel():
    return MarketWindowSelector(7, "XAUUSD", "split_v1", CUTOFF)


def test_window_is_reproducible():
    ts = _ts(1000)
    w1 = _sel().select(_task(), 0, ts, [])
    w2 = _sel().select(_task(), 0, ts, [])
    assert w1 == w2
    assert schemas.is_valid(w1, schemas.load_schema("market_window"))


def test_window_avoids_immediate_duplicate():
    ts = _ts(1000)
    sel = _sel()
    w1 = sel.select(_task(), 0, ts, [])
    reviewed = [{"timeframe": "H1", "start": w1["start"], "end": w1["end"], "edge_ref": "E010"}]
    w2 = sel.select(_task(), 0, ts, reviewed)
    # Must not overlap the reviewed window.
    assert not (w2["start"] <= w1["end"] and w2["end"] >= w1["start"])


def test_window_never_crosses_holdout():
    # timestamps that run right up to (but below) the cutoff; span forces near-cutoff selection
    from datetime import datetime, timedelta, timezone
    cutoff = datetime.fromisoformat(CUTOFF)
    ts = [(cutoff - timedelta(hours=i)).isoformat() for i in range(300)][::-1]  # ascending, all < cutoff
    w = _sel().select(_task(span=50), 0, ts, [])
    assert datetime.fromisoformat(w["end"]) < cutoff


def test_defensive_holdout_rejection():
    # If a timestamp somehow equals/exceeds the cutoff, _build must refuse.
    from datetime import datetime, timedelta, timezone
    cutoff = datetime.fromisoformat(CUTOFF)
    bad = [(cutoff + timedelta(hours=i)).isoformat() for i in range(60)]
    with pytest.raises(ValueError):
        _sel().select(_task(span=10), 0, bad, [])


def test_empty_series_returns_none():
    assert _sel().select(_task(), 0, [], []) is None


def test_span_larger_than_series_uses_full_range():
    ts = _ts(30)
    w = _sel().select(_task(span=100), 0, ts, [])
    assert w["start"] == ts[0] and w["end"] == ts[-1]
