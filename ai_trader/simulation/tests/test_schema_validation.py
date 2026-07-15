"""Tests for schema loading/compilation error paths (mirrors every prior module's own
``schema_validation.py`` test coverage)."""

from __future__ import annotations

import json

import pytest

from ai_trader.simulation.exceptions import SchemaLoadError
from ai_trader.simulation.schema_validation import _compile_schema, _load_schema


def test_missing_file_raises_schema_load_error(tmp_path) -> None:  # type: ignore[no-untyped-def]
    with pytest.raises(SchemaLoadError):
        _load_schema(tmp_path / "does_not_exist.json")


def test_malformed_json_raises_schema_load_error(tmp_path) -> None:  # type: ignore[no-untyped-def]
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(SchemaLoadError):
        _load_schema(bad)


def test_invalid_schema_shape_raises_on_compile(tmp_path) -> None:  # type: ignore[no-untyped-def]
    bad_schema = tmp_path / "bad_schema.json"
    bad_schema.write_text(json.dumps({"type": "not-a-real-type"}), encoding="utf-8")
    with pytest.raises(Exception):  # Draft202012Validator.check_schema raises jsonschema's own error
        _compile_schema(bad_schema)


def test_valid_dict_passes_validation() -> None:
    from ai_trader.simulation.schema_validation import validate_simulation_run_dict
    minimal = {
        "simulation_schema_version": "1.0.0",
        "meta": {
            "run_id": "R1", "state": "COMPLETED", "simulation_framework_version": "1.0.0",
            "fill_model_version": "1.0.0", "cost_model_version": "1.0.0", "module_versions": {},
            "generated_at": 0,
        },
        "context": {
            "run_id": "R1", "date_range": {"start": 1, "end": 2}, "symbols": ["XAUUSD"],
            "timeframes": ["M15"], "starting_balance": 100.0, "base_currency": "USD",
            "cost_model": {"spread_model": "fixed_ticks", "commission_model": "per_lot"},
            "fill_model": {"entry_timing": "next_open", "intrabar": "stop_before_target"},
            "strategy_set": "all_activatable", "run_seed": 1, "deterministic": True,
        },
        "report": {
            "portfolio_summary": {
                "starting_balance": 100.0, "final_balance": 100.0, "final_equity": 100.0,
                "net_profit": 0.0, "return_pct": 0.0, "max_drawdown_pct": 0.0,
            },
            "performance": {
                "trades": 0, "expectancy_R": None, "profit_factor": None, "win_rate": None,
                "sharpe": None, "max_drawdown_pct": 0.0,
            },
            "attribution": [], "stats": {"session": [], "daily": [], "monthly": []},
        },
    }
    assert validate_simulation_run_dict(minimal) == []


def test_invalid_dict_reports_errors() -> None:
    from ai_trader.simulation.schema_validation import validate_simulation_run_dict
    errors = validate_simulation_run_dict({"simulation_schema_version": "1.0.0"})
    assert errors != []
