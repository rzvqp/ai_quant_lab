import json

from alpha_automation.config import Config
from alpha_automation.runner import Runner
from alpha_automation.adapters import StubAdapter
from conftest import FakeDataAccess


def _config(tmp_path, **kw):
    kw.setdefault("adapter", "stub")
    kw.setdefault("data_source", "csv")
    kw.setdefault("delay_s", 0.0)
    kw.setdefault("state_dir", str(tmp_path / "state"))
    return Config(**kw)


def test_resume_continues_from_checkpoint(tmp_path):
    cfg = _config(tmp_path, max_passes=5, seed=2024)

    # First runner: interrupt after pass 1 (0-indexed) via a stop hook.
    r1 = Runner(cfg, data_access=FakeDataAccess(), adapter=StubAdapter(2024), install_signals=False)
    orig = r1.run_pass

    def wrapped(run_id, pass_no):
        rec = orig(run_id, pass_no)
        if pass_no == 1:
            r1._stop = True
        return rec

    r1.run_pass = wrapped
    s1 = r1.start()
    assert s1["status"] == "stopped"
    assert s1["next_pass"] == 2
    assert r1.memory.stats()["investigations"] == 2

    # Second runner over the SAME state_dir == process restart. Resume the run.
    r2 = Runner(cfg, data_access=FakeDataAccess(), adapter=StubAdapter(2024), install_signals=False)
    s2 = r2.resume(s1["run_id"])
    assert s2["status"] == "completed"
    assert s2["next_pass"] == 5
    assert s2["passes_completed"] == 5

    # No pass lost or duplicated across the restart.
    inv = (cfg.memory_dir / "investigations.jsonl").read_text().strip().splitlines()
    passes = sorted(json.loads(l)["pass"] for l in inv)
    assert passes == [0, 1, 2, 3, 4]
    tids = [json.loads(l)["task_id"] for l in inv]
    assert len(tids) == len(set(tids))


def test_resume_of_completed_run_is_noop(tmp_path):
    cfg = _config(tmp_path, max_passes=2)
    r1 = Runner(cfg, data_access=FakeDataAccess(), adapter=StubAdapter(1), install_signals=False)
    s1 = r1.start()
    assert s1["status"] == "completed"

    r2 = Runner(cfg, data_access=FakeDataAccess(), adapter=StubAdapter(1), install_signals=False)
    s2 = r2.resume(s1["run_id"])
    assert s2["status"] == "completed"
    assert s2["passes_completed"] == 2  # unchanged
