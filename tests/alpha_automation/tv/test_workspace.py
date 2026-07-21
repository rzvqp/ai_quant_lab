import json
from conftest import FakeClient

from alpha_automation.tv.workspace import WorkspaceLog


def test_action_sink_appends(tmp_path):
    w = WorkspaceLog(tmp_path / "state")
    sink = w.action_sink()
    sink({"verb": "get_state", "ok": True})
    lines = (tmp_path / "state" / "tv" / "actions.jsonl").read_text().strip().splitlines()
    assert json.loads(lines[0])["verb"] == "get_state"


def test_snapshot_captures_state(tmp_path):
    client = FakeClient({
        "get_state": {"symbol": "OANDA:XAUUSD", "resolution": "60", "chartType": 1,
                      "studies": [{"id": "A1", "name": "SMC"}]},
        "list_drawings": {"shapes": [{"id": "D1", "name": "rectangle"}]},
        "replay_status": {"is_replay_started": True, "current_date": "2024-06-01T00:00:00+00:00"},
    })
    w = WorkspaceLog(tmp_path / "state")
    snap = w.snapshot(client, "INV-000001", {"mode": "replay_pre_cutoff",
                                             "data_regime": "pre_holdout_replay", "note": "x"})
    assert snap["symbol"] == "OANDA:XAUUSD"
    assert snap["studies"][0]["name"] == "SMC"
    assert snap["drawings"][0]["id"] == "D1"
    assert snap["replay"]["is_started"] is True
    # persisted
    lines = (tmp_path / "state" / "tv" / "snapshots.jsonl").read_text().strip().splitlines()
    assert json.loads(lines[0])["task_id"] == "INV-000001"


def test_record_artifact(tmp_path):
    w = WorkspaceLog(tmp_path / "state")
    w.record_artifact("INV-000002", "indicator", "entity_XYZ", {"name": "RSI"})
    rec = json.loads((tmp_path / "state" / "tv" / "artifacts.jsonl").read_text().strip())
    assert rec["kind"] == "indicator" and rec["ref"] == "entity_XYZ"
