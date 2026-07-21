import pytest

from alpha_automation.config import Config
from alpha_automation.tv.client import TvClient, TvError
from alpha_automation.tv import capabilities as caps


def _client(responses, actions=None, pine_apply=False):
    cfg = Config(tv_pine_apply=pine_apply)
    run = lambda req: _fake_run(req, responses)
    return TvClient(cfg, action_log=(actions.append if actions is not None else None), run=run)


def _fake_run(req, responses):
    if "batch" in req:
        return {"ok": True, "results": [
            {"ok": True, "verb": it["verb"], "result": responses.get(it["verb"], {})}
            for it in req["batch"]]}
    verb = req["verb"]
    r = responses.get(verb)
    if isinstance(r, dict) and r.get("_fail"):
        return {"ok": False, "verb": verb, "error": r.get("error", "boom"), "code": r.get("code")}
    return {"ok": True, "verb": verb, "result": r if r is not None else {}}


def test_call_returns_result_and_logs():
    actions = []
    c = _client({"get_state": {"symbol": "OANDA:XAUUSD"}}, actions=actions)
    res = c.call("get_state", task_id="INV-000001")
    assert res["symbol"] == "OANDA:XAUUSD"
    assert actions and actions[0]["verb"] == "get_state" and actions[0]["ok"] is True
    assert actions[0]["task_id"] == "INV-000001"


def test_denied_verb_never_executes():
    actions = []
    c = _client({}, actions=actions)
    with pytest.raises(caps.CapabilityDenied):
        c.call("replay_trade", {"action": "buy"})
    assert actions == []  # gate blocks before any execution/log


def test_gated_verb_blocked_without_flag():
    c = _client({}, pine_apply=False)
    with pytest.raises(caps.CapabilityDenied):
        c.call("pine_compile")


def test_batch_authorizes_all_before_running():
    actions = []
    c = _client({"get_state": {}}, actions=actions)
    with pytest.raises(caps.CapabilityDenied):
        c.batch([("get_state", None), ("replay_trade", {"action": "sell"})])
    # No op should have executed/logged because authorization is upfront.
    assert actions == []


def test_call_failure_raises_and_logs():
    actions = []
    c = _client({"get_ohlcv": {"_fail": True, "error": "no data", "code": "DATA"}}, actions=actions)
    with pytest.raises(TvError):
        c.call("get_ohlcv", {"summary": True})
    assert actions[-1]["ok"] is False and actions[-1]["code"] == "DATA"


def test_try_call_returns_none_on_failure():
    c = _client({"get_quote": {"_fail": True}})
    assert c.try_call("get_quote") is None


def test_action_log_marks_mutating():
    actions = []
    c = _client({"add_indicator": {"entity_id": "X1"}}, actions=actions)
    c.call("add_indicator", {"indicator": "Relative Strength Index"})
    assert actions[-1]["mutating"] is True
    assert actions[-1]["capability"] == caps.MUTATE
