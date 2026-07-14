"""Unit tests for ai_trader.market_scanner.schema_validation."""

from ai_trader.market_scanner.schema_validation import schema_dict, validate_context

_MINIMAL_VALID_CONTEXT = {
    "meta": {
        "context_schema_version": "1.0.0",
        "feature_dictionary_version": "1.0.0",
        "interface_version": "1.0.0",
        "scanner_version": "1.0.0",
        "symbol": "XAUUSD",
        "base_timeframe": "M15",
        "as_of": 900,
        "generated_at": 900,
        "mode": "REPLAY",
        "source": "test",
    },
    "clock": {
        "as_of": 900, "base_bar_index": 1,
        "is_new_session": True, "is_new_day": True, "is_new_week": True, "is_month_boundary": True,
    },
    "symbol_meta": {
        "symbol": "XAUUSD", "tick_size": 0.1, "point_value": 1.0,
        "price_precision": 2, "session_anchor": "NY_17:00",
    },
    "session": {
        "name": "asia", "block_id": 0, "bar_in_session": 0, "session_open_ts": 0,
        "opening_range": {"high": None, "low": None, "formed": False},
    },
    "calendar": {
        "date": "1970-01-01", "dow": 3, "dom": 1,
        "is_holiday": False, "is_weekend_gap": False, "dst_offset_seconds": 0,
    },
    "timeframes": {
        "M15": {"timeframe": "M15", "bars": [], "features": {}},
    },
    "data_quality": {"overall": "INSUFFICIENT", "by_timeframe": {}},
    "sufficiency": {"overall": "INSUFFICIENT"},
}


def test_schema_loads_and_is_a_valid_draft202012_schema() -> None:
    schema = schema_dict()
    assert schema["title"] == "MarketContext v1"
    assert "$defs" in schema


def test_minimal_valid_context_passes() -> None:
    errors = validate_context(_MINIMAL_VALID_CONTEXT)
    assert errors == []


def test_missing_required_top_level_key_fails() -> None:
    bad = {k: v for k, v in _MINIMAL_VALID_CONTEXT.items() if k != "clock"}
    errors = validate_context(bad)
    assert errors
    assert any("clock" in e for e in errors)


def test_wrong_enum_value_fails() -> None:
    import copy

    bad = copy.deepcopy(_MINIMAL_VALID_CONTEXT)
    bad["meta"]["mode"] = "NOT_A_MODE"
    errors = validate_context(bad)
    assert errors


def test_additional_properties_rejected() -> None:
    import copy

    bad = copy.deepcopy(_MINIMAL_VALID_CONTEXT)
    bad["unexpected_field"] = 1
    errors = validate_context(bad)
    assert errors


def test_negative_staleness_rejected() -> None:
    import copy

    bad = copy.deepcopy(_MINIMAL_VALID_CONTEXT)
    bad["data_quality"]["by_timeframe"]["M15"] = {
        "last_bar_complete": True, "warmup_satisfied": True,
        "staleness_ms": -1, "gaps": [],
    }
    errors = validate_context(bad)
    assert errors
