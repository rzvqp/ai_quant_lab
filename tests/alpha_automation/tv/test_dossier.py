from conftest import FakeClient

from alpha_automation.config import Config
from alpha_automation.tv.mode import ResearchMode
from alpha_automation.tv.workspace import WorkspaceLog
from alpha_automation.tv.dossier import DossierBuilder

PRE = "2024-06-01T00:00:00+00:00"
WINDOW = {"timeframe": "H1", "start": "2024-05-01T00:00:00+00:00", "end": "2024-07-01T00:00:00+00:00"}
TASK = {"window_hint": {"timeframe": "H1"}, "edge_ref": "E010"}

READS = {
    "get_state": {"symbol": "OANDA:XAUUSD", "resolution": "60", "chartType": 1, "studies": []},
    "get_ohlcv": {"bar_count": 100, "summary": {"high": 2400}},
    "get_study_values": {"study_count": 2, "studies": [{"name": "SMC", "values": {}}]},
    "get_pine_lines": {"study_count": 1, "studies": [{"name": "S/R", "horizontal_levels": [2350]}]},
    "get_pine_labels": {"study_count": 1},
    "get_pine_tables": {"study_count": 0},
    "get_pine_boxes": {"study_count": 1},
    "get_quote": {"last": 2360.5, "open": 2350},
    "list_drawings": {"shapes": []},
    "capture_screenshot": {"file_path": "/tmp/shot.png", "method": "cdp"},
}


def _builder(cfg, responses):
    client = FakeClient(responses)
    mode = ResearchMode(cfg, client)
    ws = WorkspaceLog(cfg.state_dir)
    return DossierBuilder(cfg, client, mode, ws), client


def test_live_dossier_has_all_sections(tmp_path):
    cfg = Config(research_mode="live_observation", state_dir=str(tmp_path / "state"))
    b, client = _builder(cfg, READS)
    d = b.build(TASK, WINDOW, "INV-000001")
    assert d["data_regime"] == "live_post_holdout"
    assert d["chart_state"]["symbol"] == "OANDA:XAUUSD"
    assert d["ohlcv_summary"]["bar_count"] == 100
    assert d["indicators"]["study_count"] == 2
    assert d["pine"]["lines"]["studies"][0]["horizontal_levels"] == [2350]
    assert d["quote"]["last"] == 2360.5
    assert d["screenshots"] == ["/tmp/shot.png"]
    assert d["replay_track"] == []          # no replay in live mode
    assert d["multi_tf_context"] == {}      # no context provider
    # symbol/timeframe were set on the chart
    assert "set_symbol" in client.verbs_called() and "set_timeframe" in client.verbs_called()


def test_replay_dossier_builds_holdout_safe_track(tmp_path):
    responses = dict(READS)
    responses["replay_start"] = {"status": "SUCCESS"}
    responses["replay_status"] = {"is_replay_started": True, "current_date": PRE}
    responses["replay_step"] = {"current_date": PRE}
    cfg = Config(research_mode="replay_pre_cutoff", tv_replay_samples=3,
                 state_dir=str(tmp_path / "state"))
    b, client = _builder(cfg, responses)
    d = b.build(TASK, WINDOW, "INV-000002")
    assert d["data_regime"] == "pre_holdout_replay"
    assert len(d["replay_track"]) == 3
    assert all(step["quote"]["last"] == 2360.5 for step in d["replay_track"])
    assert "replay_start" in client.verbs_called()


def test_multi_tf_context_provider(tmp_path):
    cfg = Config(research_mode="live_observation", tv_multi_tf=["H4", "D1"],
                 state_dir=str(tmp_path / "state"))
    client = FakeClient(READS)
    mode = ResearchMode(cfg, client)
    ws = WorkspaceLog(cfg.state_dir)
    provider = lambda tf: {"tf": tf, "mean_close": 2300}
    b = DossierBuilder(cfg, client, mode, ws, context_provider=provider)
    d = b.build(TASK, WINDOW, "INV-000003")
    assert set(d["multi_tf_context"].keys()) == {"H4", "D1"}
    assert d["multi_tf_context"]["H4"]["mean_close"] == 2300
