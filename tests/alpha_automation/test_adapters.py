import pytest

from alpha_automation.adapters import StubAdapter
from alpha_automation.adapters.base import AlphaContext, AlphaAdapterError, extract_json
from alpha_automation.adapters.codex_exec import CodexAdapter
from alpha_automation.config import Config
from alpha_automation import boundaries, schemas


def _ctx(task_id="INV-000001"):
    return AlphaContext(
        task_id=task_id,
        mission="MISSION",
        perspective={"lens": "time", "framing": "neutral_observation"},
        task={"question": "does X happen?"},
        window={"timeframe": "H1"},
        data_summary={"n_bars": 100},
        prior_questions=[],
    )


def test_stub_outcomes_are_deterministic():
    assert StubAdapter.planned_outcome("INV-000001") == StubAdapter.planned_outcome("INV-000001")


def test_stub_returns_valid_boundary_clean_response():
    ad = StubAdapter(0)
    schema = schemas.load_schema("alpha_response")
    for i in range(1, 60):
        tid = f"INV-{i:06d}"
        obj = ad.investigate(_ctx(tid))
        assert schemas.is_valid(obj, schema)
        assert obj["task_id"] == tid
        assert boundaries.scan_response(obj) == []
        assert obj["finding_type"] == StubAdapter.planned_outcome(tid)


def test_stub_produces_each_outcome_type():
    seen = {StubAdapter.planned_outcome(f"INV-{i:06d}") for i in range(1, 200)}
    assert seen == {"NEGATIVE", "TENTATIVE", "CANDIDATE_PROPOSED"}


def test_investigate_rejects_task_id_mismatch():
    class WrongId(StubAdapter):
        def _invoke(self, context):
            r = super()._invoke(context)
            r["task_id"] = "INV-999999"
            return r
    with pytest.raises(AlphaAdapterError):
        WrongId(0).investigate(_ctx("INV-000001"))


def test_extract_json_from_prose():
    txt = 'here is the result:\n{"task_id": "INV-000001", "x": 1}\nthanks'
    assert extract_json(txt)["task_id"] == "INV-000001"


def test_codex_build_prompt_contains_contract():
    cfg = Config(adapter="codex")
    ad = CodexAdapter(cfg, run=lambda prompt, model, timeout: "{}")
    prompt = ad.build_prompt(_ctx("INV-000042"))
    assert "INV-000042" in prompt
    assert "JSON" in prompt
    assert "does X happen?" in prompt


def test_codex_investigate_with_fake_run():
    cfg = Config(adapter="codex")
    valid = {
        "task_id": "INV-000001", "finding_type": "NEGATIVE",
        "summary": "nothing", "observation": "clean null", "confidence": "Low",
        "gate": {"novel": False, "evidence_supported": True, "reproducible_or_concrete": True,
                 "descriptive_not_causal": True, "not_noise": True, "not_strategy_or_profit_claim": True},
    }
    import json
    ad = CodexAdapter(cfg, run=lambda prompt, model, timeout: "prefix " + json.dumps(valid))
    obj = ad.investigate(_ctx("INV-000001"))
    assert obj["finding_type"] == "NEGATIVE"


def test_codex_retries_then_succeeds():
    cfg = Config(adapter="codex", adapter_max_retries=1)
    import json
    valid = {
        "task_id": "INV-000001", "finding_type": "NEGATIVE",
        "summary": "nothing", "observation": "clean null", "confidence": "Low",
        "gate": {"novel": False, "evidence_supported": True, "reproducible_or_concrete": True,
                 "descriptive_not_causal": True, "not_noise": True, "not_strategy_or_profit_claim": True},
    }
    calls = {"n": 0}

    def flaky(prompt, model, timeout):
        calls["n"] += 1
        return "not json" if calls["n"] == 1 else json.dumps(valid)

    ad = CodexAdapter(cfg, run=flaky)
    obj = ad.investigate(_ctx("INV-000001"))
    assert obj["finding_type"] == "NEGATIVE"
    assert calls["n"] == 2
