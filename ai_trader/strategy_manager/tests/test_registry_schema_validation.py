"""Tests for :mod:`ai_trader.strategy_manager.registry_schema_validation`."""

from __future__ import annotations

from ai_trader.strategy_manager.registry_schema_validation import validate_registry_snapshot


def _minimal_valid_snapshot() -> dict:
    return {
        "registry_version": "1.0.0",
        "manager_version": "1.0.0",
        "supported": {"interface_major": 1, "runtime_api_major": 1, "feature_dictionary_major": 1},
        "generated_at": 1700000000,
        "entries": [],
        "indices": {
            "by_id": {}, "by_lifecycle": {}, "by_health": {}, "by_symbol": {}, "by_required_field": {}, "active": [],
        },
        "aggregated_context": {
            "timeframes": [], "required_fields_by_timeframe": {}, "lookback_by_timeframe": {},
            "symbols": [], "feature_dictionary_major": 1, "interface_version": "1.0.0", "contributor_ids": [],
        },
        "health_summary": {"overall": "OK", "total": 0, "active_count": 0, "counts": {}},
    }


class TestValidateRegistrySnapshot:
    def test_minimal_valid_snapshot_passes(self) -> None:
        assert validate_registry_snapshot(_minimal_valid_snapshot()) == []

    def test_missing_required_key_fails(self) -> None:
        data = _minimal_valid_snapshot()
        del data["entries"]
        assert validate_registry_snapshot(data) != []

    def test_wrong_registry_version_const_fails(self) -> None:
        data = _minimal_valid_snapshot()
        data["registry_version"] = "2.0.0"
        assert validate_registry_snapshot(data) != []

    def test_bad_entry_id_pattern_fails(self) -> None:
        data = _minimal_valid_snapshot()
        data["entries"].append({
            "id": "not-valid", "slug": "x", "source_path": "x", "lifecycle": "INVALID", "health": "INVALID",
            "loaded": False, "contract_ref": {"identity_version": None, "interface_version": None, "content_hash": None},
            "compatibility": {"compatible": False, "schema_valid": False, "interface_ok": False, "runtime_ok": False, "context_ok": False},
        })
        assert validate_registry_snapshot(data) != []
