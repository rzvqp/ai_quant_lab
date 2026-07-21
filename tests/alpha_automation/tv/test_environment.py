from conftest import FakeClient

from alpha_automation.config import Config
from alpha_automation.adapters.base import AlphaAdapter
from alpha_automation.tv.workspace import WorkspaceLog
from alpha_automation.tv.environment import ResearchEnvironment

WINDOW = {"timeframe": "H1", "start": "2024-05-01T00:00:00+00:00", "end": "2024-07-01T00:00:00+00:00"}
TASK = {"window_hint": {"timeframe": "H1"}, "edge_ref": "E010", "question": "does X happen?"}
PERSP = {"perspective_id": "P0000", "lens": "structure", "framing": "neutral_observation"}

READS = {
    "get_state": {"symbol": "OANDA:XAUUSD", "studies": []},
    "get_ohlcv": {"bar_count": 100},
    "get_study_values": {"study_count": 0, "studies": []},
    "get_pine_lines": {}, "get_pine_labels": {"study_count": 1, "studies": []},
    "get_pine_tables": {}, "get_pine_boxes": {}, "get_quote": {"last": 2360},
    "list_drawings": {"shapes": []},
    "capture_screenshot": {"file_path": "/tmp/s.png"},
}

_GATE_OK = {"novel": False, "evidence_supported": True, "reproducible_or_concrete": True,
            "descriptive_not_causal": True, "not_noise": True, "not_strategy_or_profit_claim": True}


def _resp(finding, requests=None):
    r = {"finding_type": finding, "summary": "s", "observation": "o", "confidence": "Low",
         "gate": dict(_GATE_OK)}
    if requests is not None:
        r["observation_requests"] = requests
    return r


class ScriptedAdapter(AlphaAdapter):
    name = "scripted"

    def __init__(self, responses):
        self.responses = list(responses)
        self.contexts = []

    def _invoke(self, context):
        self.contexts.append(context)
        r = dict(self.responses[min(len(self.contexts) - 1, len(self.responses) - 1)])
        r["task_id"] = context.task_id
        return r


def _env(cfg, client):
    return ResearchEnvironment(cfg, client, WorkspaceLog(cfg.state_dir))


def test_followup_loop_executes_allowed_and_denies_prohibited(tmp_path):
    cfg = Config(research_mode="live_observation", tv_replay_samples=0,
                 state_dir=str(tmp_path / "state"), max_followup_rounds=2)
    client = FakeClient(READS)
    adapter = ScriptedAdapter([
        _resp("TENTATIVE", requests=[
            {"verb": "get_pine_labels", "params": {"study_filter": "SMC"}, "why": "inspect labels"},
            {"verb": "replay_trade", "params": {"action": "buy"}, "why": "PROHIBITED"},
        ]),
        _resp("NEGATIVE", requests=[]),
    ])
    response, prov = _env(cfg, client).investigate(
        task=TASK, window=WINDOW, task_id="INV-000001", adapter=adapter,
        mission="M", perspective=PERSP, prior_questions=[])

    assert response["finding_type"] == "NEGATIVE"       # final response, after follow-up
    assert prov["data_source"] == "live_tv"
    assert prov["followup_rounds"] == 1
    # allowed follow-up executed; prohibited one refused (never reached the client as a trade)
    assert client.calls.count(("get_pine_labels", {"study_filter": "SMC"})) == 1
    assert ("replay_trade", {"action": "buy"}) not in client.calls
    # second Alpha call saw the augmented dossier
    assert "followups" in adapter.contexts[1].data_summary


def test_followup_rounds_are_bounded(tmp_path):
    cfg = Config(research_mode="live_observation", tv_replay_samples=0,
                 state_dir=str(tmp_path / "state"), max_followup_rounds=1)
    client = FakeClient(READS)
    # Adapter ALWAYS asks for more -> loop must still stop at max_followup_rounds.
    always = _resp("TENTATIVE", requests=[{"verb": "get_quote", "why": "again"}])
    adapter = ScriptedAdapter([always, always, always, always])
    response, prov = _env(cfg, client).investigate(
        task=TASK, window=WINDOW, task_id="INV-000002", adapter=adapter,
        mission="M", perspective=PERSP, prior_questions=[])
    assert prov["followup_rounds"] == 1                  # bounded
    # initial invoke + 1 follow-up round == 2 adapter invocations
    assert len(adapter.contexts) == 2


def test_available_actions_offered_to_alpha(tmp_path):
    cfg = Config(research_mode="live_observation", tv_replay_samples=0,
                 state_dir=str(tmp_path / "state"))
    client = FakeClient(READS)
    adapter = ScriptedAdapter([_resp("NEGATIVE", requests=[])])
    _env(cfg, client).investigate(
        task=TASK, window=WINDOW, task_id="INV-000003", adapter=adapter,
        mission="M", perspective=PERSP, prior_questions=[])
    actions = adapter.contexts[0].available_actions
    assert "get_pine_labels" in actions and "add_indicator" in actions
    assert "replay_trade" not in actions and "pine_compile" not in actions  # gated/denied excluded
