import json
from conftest import FakeClient, FakeDataAccess

from alpha_automation.config import Config
from alpha_automation.runner import Runner
from alpha_automation.adapters import StubAdapter

_GATE_OK = {"novel": False, "evidence_supported": True, "reproducible_or_concrete": True,
            "descriptive_not_causal": True, "not_noise": True, "not_strategy_or_profit_claim": True}


class FakeEnv:
    """Stand-in ResearchEnvironment: returns a valid response + live_tv provenance."""

    def __init__(self):
        self.calls = 0

    def investigate(self, *, task, window, task_id, adapter, mission, perspective, prior_questions):
        self.calls += 1
        response = {
            "task_id": task_id, "finding_type": "NEGATIVE", "summary": "no effect",
            "observation": "clean null under replay observation", "confidence": "Medium",
            "gate": dict(_GATE_OK),
        }
        provenance = {"data_source": "live_tv", "data_regime": "pre_holdout_replay",
                      "timeframe": window["timeframe"], "followup_rounds": 0}
        return response, provenance


def test_runner_uses_tvre_when_enabled(tmp_path):
    cfg = Config(use_tv_research=True, research_mode="replay_pre_cutoff", adapter="stub",
                 max_passes=3, delay_s=0.0, state_dir=str(tmp_path / "state"))
    env = FakeEnv()
    r = Runner(cfg, data_access=FakeDataAccess(), adapter=StubAdapter(1),
               tv_env=env, install_signals=False)
    state = r.start()

    assert state["status"] == "completed"
    assert env.calls == 3
    inv = (cfg.memory_dir / "investigations.jsonl").read_text().strip().splitlines()
    recs = [json.loads(l) for l in inv]
    assert len(recs) == 3
    assert all(rec["data_provenance"]["data_source"] == "live_tv" for rec in recs)
    # windows were selected and logged as reviewed
    assert r.memory.stats()["windows_reviewed"] == 3
