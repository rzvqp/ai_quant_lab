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


def test_bounded_run_completes(tmp_path):
    cfg = _config(tmp_path, max_passes=6, seed=123)
    r = Runner(cfg, data_access=FakeDataAccess(), adapter=StubAdapter(123), install_signals=False)
    state = r.start()
    assert state["status"] == "completed"
    assert state["passes_completed"] == 6
    assert state["next_pass"] == 6
    assert r.memory.stats()["investigations"] == 6


def test_no_duplicate_task_ids(tmp_path):
    cfg = _config(tmp_path, max_passes=8)
    r = Runner(cfg, data_access=FakeDataAccess(), adapter=StubAdapter(1), install_signals=False)
    r.start()
    inv = (cfg.memory_dir / "investigations.jsonl").read_text().strip().splitlines()
    tids = [json.loads(l)["task_id"] for l in inv]
    assert len(tids) == len(set(tids)) == 8


def test_run_is_reproducible(tmp_path):
    c1 = _config(tmp_path / "a", max_passes=5, seed=777)
    c2 = _config(tmp_path / "b", max_passes=5, seed=777)
    r1 = Runner(c1, data_access=FakeDataAccess(), adapter=StubAdapter(777), install_signals=False)
    r2 = Runner(c2, data_access=FakeDataAccess(), adapter=StubAdapter(777), install_signals=False)
    r1.start(); r2.start()
    q1 = [json.loads(l)["task"]["question"]
          for l in (c1.memory_dir / "investigations.jsonl").read_text().splitlines()]
    q2 = [json.loads(l)["task"]["question"]
          for l in (c2.memory_dir / "investigations.jsonl").read_text().splitlines()]
    assert q1 == q2


def test_dry_run_needs_no_data_and_never_calls_codex(tmp_path):
    # adapter="codex" but dry_run must use the stub internally and skip data access entirely.
    cfg = _config(tmp_path, max_passes=3, adapter="codex", dry_run=True)
    r = Runner(cfg, data_access=None, install_signals=False)
    state = r.start()
    assert state["status"] == "completed"
    assert r.memory.stats()["investigations"] == 3


def test_graceful_shutdown_stops_and_checkpoints(tmp_path):
    cfg = _config(tmp_path, max_passes=10)
    r = Runner(cfg, data_access=FakeDataAccess(), adapter=StubAdapter(1), install_signals=False)
    orig = r.run_pass

    def wrapped(run_id, pass_no):
        rec = orig(run_id, pass_no)
        if pass_no == 2:
            r._stop = True
        return rec

    r.run_pass = wrapped
    state = r.start()
    assert state["status"] == "stopped"
    assert state["next_pass"] == 3  # completed passes 0,1,2 then stopped before 3
    assert state["passes_completed"] == 3


def test_circuit_breaker_trips_on_repeated_failures(tmp_path):
    cfg = _config(tmp_path, max_passes=20, max_consecutive_failures=3)

    class BoomData(FakeDataAccess):
        def get_window(self, window):
            raise RuntimeError("data source down")

    r = Runner(cfg, data_access=BoomData(), adapter=StubAdapter(1), install_signals=False)
    state = r.start()
    assert state["status"] == "failed"
    assert state["consecutive_failures"] >= 3
    # every attempted pass recorded an ERROR investigation
    assert r.memory.stats()["investigations"] >= 3


def test_run_state_file_is_valid(tmp_path):
    cfg = _config(tmp_path, max_passes=2)
    r = Runner(cfg, data_access=FakeDataAccess(), adapter=StubAdapter(1), install_signals=False)
    state = r.start()
    from alpha_automation import schemas
    path = cfg.runs_dir / state["run_id"] / "run_state.json"
    assert path.exists()
    assert schemas.is_valid(json.loads(path.read_text()), schemas.load_schema("run_state"))
