import pytest
from conftest import FakeClient

from alpha_automation.config import Config
from alpha_automation.tv.mode import ResearchMode, HoldoutViolation

PRE = "2024-06-01T00:00:00+00:00"    # before cutoff
POST = "2025-11-01T00:00:00+00:00"   # after cutoff 2025-10-23
WINDOW = {"timeframe": "H1", "start": "2024-05-01T00:00:00+00:00", "end": "2024-07-01T00:00:00+00:00"}


def _mode(responses, research_mode="replay_pre_cutoff"):
    cfg = Config(research_mode=research_mode)
    return ResearchMode(cfg, FakeClient(responses)), cfg


def test_verify_passes_pre_cutoff():
    m, _ = _mode({"replay_status": {"is_replay_started": True, "current_date": PRE}})
    m.verify()  # no raise


def test_verify_raises_when_not_started():
    m, _ = _mode({"replay_status": {"is_replay_started": False, "current_date": PRE}})
    with pytest.raises(HoldoutViolation):
        m.verify()


def test_verify_raises_at_or_after_cutoff():
    m, _ = _mode({"replay_status": {"is_replay_started": True, "current_date": POST}})
    with pytest.raises(HoldoutViolation):
        m.verify()


def test_verify_raises_when_date_missing():
    m, _ = _mode({"replay_status": {"is_replay_started": True, "current_date": None}})
    with pytest.raises(HoldoutViolation):
        m.verify()


def test_prepare_replay_enters_and_verifies():
    client = FakeClient({"replay_start": {"status": "SUCCESS"},
                         "replay_status": {"is_replay_started": True, "current_date": PRE}})
    m = ResearchMode(Config(research_mode="replay_pre_cutoff"), client)
    info = m.prepare(WINDOW, task_id="INV-000001")
    assert info["data_regime"] == "pre_holdout_replay"
    assert info["validation_eligible"] is False
    assert "replay_start" in client.verbs_called()


def test_prepare_live_tags_regime_and_skips_replay():
    client = FakeClient({})
    m = ResearchMode(Config(research_mode="live_observation"), client)
    info = m.prepare(WINDOW)
    assert info["data_regime"] == "live_post_holdout"
    assert info["validation_eligible"] is False
    assert client.verbs_called() == []  # no replay in live mode


def test_prepare_rejects_post_cutoff_window():
    m, _ = _mode({"replay_status": {"is_replay_started": True, "current_date": PRE}})
    bad = {"timeframe": "H1", "start": "2025-10-20T00:00:00+00:00", "end": "2025-12-01T00:00:00+00:00"}
    with pytest.raises(HoldoutViolation):
        m.prepare(bad)


def test_step_safely_advances_and_reverifies():
    client = FakeClient({"replay_step": {"current_date": PRE},
                         "replay_status": {"is_replay_started": True, "current_date": PRE}})
    m = ResearchMode(Config(research_mode="replay_pre_cutoff"), client)
    res = m.step_safely()
    assert "replay_step" in client.verbs_called()
    assert "replay_status" in client.verbs_called()


def test_unix_seconds_current_date_supported():
    import datetime as dt
    pre_unix = int(dt.datetime(2024, 6, 1, tzinfo=dt.timezone.utc).timestamp())
    m, _ = _mode({"replay_status": {"is_replay_started": True, "current_date": pre_unix}})
    m.verify()
