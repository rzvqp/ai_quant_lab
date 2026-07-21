from alpha_automation import schemas, boundaries
from alpha_automation.adapters.base import validate_response


def _valid_response(task_id="INV-000001", finding="NEGATIVE"):
    return {
        "task_id": task_id,
        "finding_type": finding,
        "summary": "No distinguishable effect.",
        "observation": "The conditioned subset matched the ambient distribution.",
        "confidence": "Medium",
        "gate": {
            "novel": False, "evidence_supported": True, "reproducible_or_concrete": True,
            "descriptive_not_causal": True, "not_noise": True, "not_strategy_or_profit_claim": True,
        },
    }


def test_valid_response_passes_schema():
    schema = schemas.load_schema("alpha_response")
    assert schemas.is_valid(_valid_response(), schema)


def test_missing_required_field_fails():
    schema = schemas.load_schema("alpha_response")
    bad = _valid_response()
    del bad["gate"]
    assert not schemas.is_valid(bad, schema)


def test_bad_enum_fails():
    schema = schemas.load_schema("alpha_response")
    bad = _valid_response(finding="PROFITABLE")
    assert not schemas.is_valid(bad, schema)


def test_additional_property_rejected():
    schema = schemas.load_schema("alpha_response")
    bad = _valid_response()
    bad["secret_trade"] = "buy"
    assert not schemas.is_valid(bad, schema)


def test_boundary_language_detected():
    assert boundaries.forbidden_language("this is a profitable trading strategy")
    assert boundaries.forbidden_language("the Sharpe ratio was high")
    assert boundaries.forbidden_language("place a stop-loss at the low")
    assert not boundaries.forbidden_language("price stalled near the prior high and reversed")


def test_validate_response_rejects_boundary_breach():
    obj = _valid_response()
    obj["observation"] = "This is a profitable setup: enter long, take-profit at the high."
    problems = validate_response(obj, "INV-000001")
    assert any("boundary" in p for p in problems)


def test_validate_response_rejects_task_id_mismatch():
    problems = validate_response(_valid_response(task_id="INV-000009"), "INV-000001")
    assert any("task_id mismatch" in p for p in problems)


def test_mini_validator_basics():
    schema = {"type": "object", "required": ["a"], "properties": {"a": {"type": "integer", "minimum": 0}}}
    assert schemas.is_valid({"a": 3}, schema)
    assert not schemas.is_valid({"a": -1}, schema)
    assert not schemas.is_valid({}, schema)
    assert not schemas.is_valid({"a": True}, schema)  # bool is not integer
