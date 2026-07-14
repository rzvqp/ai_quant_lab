"""Tests for :mod:`ai_trader.strategy_manager.schema_validation`."""

from __future__ import annotations

from ai_trader.strategy_manager.schema_validation import schema_dict, validate_contract
from ai_trader.strategy_manager.tests.fixtures.contracts import make_contract_dict


class TestValidateContract:
    def test_valid_contract_passes(self) -> None:
        assert validate_contract(make_contract_dict()) == []

    def test_missing_required_top_level_key_fails(self) -> None:
        data = make_contract_dict()
        del data["evidence"]
        errors = validate_contract(data)
        assert errors != []

    def test_wrong_interface_version_const_fails(self) -> None:
        data = make_contract_dict(interface_version="2.0.0")
        assert validate_contract(data) != []

    def test_bad_id_pattern_fails(self) -> None:
        data = make_contract_dict(id="not-a-valid-id")
        data["identity"]["id"] = "not-a-valid-id"
        assert validate_contract(data) != []

    def test_additional_property_rejected(self) -> None:
        data = make_contract_dict()
        data["unexpected_extra_field"] = "nope"
        assert validate_contract(data) != []

    def test_real_v0_seed_contract_fails(self) -> None:
        """Documents the known gap: real Strategy Library files are v0 seed shape and do NOT
        validate against strategy_contract.v1.schema.json (STRATEGY_INTERFACE_v1.md §7)."""
        v0_seed_shape = {"id": "S1", "name": "x", "status": "IMPLEMENTED"}
        assert validate_contract(v0_seed_shape) != []


class TestSchemaDict:
    def test_loads_and_caches(self) -> None:
        schema = schema_dict()
        assert schema["title"] == "Strategy Execution Contract v1"
        assert schema_dict() is schema  # lru_cache: same object every call
