import pytest

from alpha_automation.data_access import summarize_bars


def test_summarize_bars_is_descriptive_and_boundary_safe():
    bars = [
        {"dt": "2024-01-01T00:00:00+00:00", "o": 2000, "h": 2005, "l": 1998, "c": 2003, "v": 100, "session": "asia"},
        {"dt": "2024-01-01T01:00:00+00:00", "o": 2003, "h": 2010, "l": 2001, "c": 2008, "v": 120, "session": "asia"},
        {"dt": "2024-01-01T02:00:00+00:00", "o": 2008, "h": 2009, "l": 2000, "c": 2002, "v": 90, "session": "london"},
    ]
    s = summarize_bars(bars, "H1")
    assert s["n_bars"] == 3
    assert s["price"]["max_high"] == 2010
    assert s["session_counts"] == {"asia": 2, "london": 1}
    # descriptive only -- no tradability/strategy fields
    assert "signal" not in s and "profit" not in s


def test_summarize_empty():
    assert summarize_bars([], "H1")["n_bars"] == 0


def test_csv_fallback_path_real_data(tmp_path):
    pd = pytest.importorskip("pandas")
    try:
        import edge_research._common  # noqa: F401
    except Exception:
        pytest.skip("edge_research loader not importable in this environment")

    from alpha_automation.config import Config
    from alpha_automation.data_access import DataAccess

    cfg = Config(data_source="csv", state_dir=str(tmp_path / "state"))
    da = DataAccess(cfg)

    ts = da.timestamps("D1")
    assert ts == sorted(ts)                      # ascending
    cutoff = cfg.holdout_cutoff
    from datetime import datetime
    assert datetime.fromisoformat(ts[-1]) < datetime.fromisoformat(cutoff)  # holdout-safe

    window = {"timeframe": "D1", "start": ts[0], "end": ts[50]}
    summary, prov = da.get_window(window)
    assert prov["data_source"] == "csv_fallback"
    assert summary["n_bars"] > 0
