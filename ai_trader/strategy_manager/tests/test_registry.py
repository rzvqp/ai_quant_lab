"""Tests for :mod:`ai_trader.strategy_manager.registry`."""

from __future__ import annotations

from ai_trader.strategy_manager.registry import StrategyRegistry
from ai_trader.strategy_manager.registry_schema_validation import validate_registry_snapshot
from ai_trader.strategy_manager.tests.fixtures.contracts import make_contract_dict
from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_manager.required_context import compute_required_context
from ai_trader.strategy_manager.types import AggregatedContext, CompatibilityResult, Health, Lifecycle, RegistryEntry


def _entry(id_: str, health: Health = Health.LOADED, lifecycle: Lifecycle = Lifecycle.EXPERIMENTAL, active: bool = False, with_contract: bool = True) -> RegistryEntry:
    contract = parse_contract(make_contract_dict(id=id_)) if with_contract else None
    rc = compute_required_context(contract, frozenset({"XAUUSD"})) if contract else None
    return RegistryEntry(
        id=id_, slug=f"{id_}_slug", source_path=f"/lib/{id_}/strategy.json", lifecycle=lifecycle, health=health,
        loaded=with_contract, active=active, contract=contract, required_context=rc,
        compatibility=CompatibilityResult(True, True, True, True, True),
    )


def _empty_agg() -> AggregatedContext:
    return AggregatedContext(
        timeframes=frozenset(), required_fields_by_timeframe={}, lookback_by_timeframe={},
        symbols=frozenset(), feature_dictionary_major=1, interface_version="1.0.0", contributor_ids=(),
    )


class TestAddDiscovered:
    def test_first_entry_becomes_canonical(self) -> None:
        reg = StrategyRegistry()
        entry = reg.add_discovered(_entry("S1"))
        assert reg.get("S1") is entry
        assert entry.health is Health.LOADED

    def test_duplicate_id_is_rejected(self) -> None:
        reg = StrategyRegistry()
        first = reg.add_discovered(_entry("S1"))
        second = reg.add_discovered(_entry("S1"))
        assert reg.get("S1") is first
        assert second.health is Health.DUPLICATE
        assert second.lifecycle is Lifecycle.INVALID
        assert second.active is False
        assert any("duplicate id" in e for e in second.errors)
        assert len(reg.all_entries()) == 2
        assert len(reg.canonical_entries()) == 1

    def test_clear_resets_everything(self) -> None:
        reg = StrategyRegistry()
        reg.add_discovered(_entry("S1"))
        reg.clear()
        assert reg.all_entries() == ()
        assert reg.get("S1") is None


class TestReplaceCanonical:
    def test_overwrites_in_place_without_duplicating(self) -> None:
        reg = StrategyRegistry()
        reg.add_discovered(_entry("S1"))
        new_entry = _entry("S1", lifecycle=Lifecycle.EXPLORATORY, active=True)
        reg.replace_canonical("S1", new_entry)
        assert reg.get("S1") is new_entry
        assert len(reg.all_entries()) == 1


class TestQueries:
    def test_active_entries_filters_correctly(self) -> None:
        reg = StrategyRegistry()
        reg.add_discovered(_entry("S1", active=True, lifecycle=Lifecycle.EXPLORATORY))
        reg.add_discovered(_entry("S2", active=False))
        assert [e.id for e in reg.active_entries()] == ["S1"]

    def test_canonical_by_id(self) -> None:
        reg = StrategyRegistry()
        reg.add_discovered(_entry("S1"))
        reg.add_discovered(_entry("S2"))
        by_id = reg.canonical_by_id()
        assert set(by_id) == {"S1", "S2"}


class TestBuildIndices:
    def test_indices_shape(self) -> None:
        reg = StrategyRegistry()
        reg.add_discovered(_entry("S1", active=True, lifecycle=Lifecycle.EXPLORATORY))
        reg.add_discovered(_entry("S2", health=Health.INVALID, lifecycle=Lifecycle.INVALID, with_contract=False))
        indices = reg.build_indices()
        assert indices["by_id"] == {"S1": 0, "S2": 1}
        assert indices["by_lifecycle"]["EXPLORATORY"] == ["S1"]
        assert indices["by_lifecycle"]["INVALID"] == ["S2"]
        assert indices["by_health"]["LOADED"] == ["S1"]
        assert indices["by_health"]["INVALID"] == ["S2"]
        assert indices["active"] == ["S1"]
        assert "XAUUSD" in indices["by_symbol"]
        assert "S1" in indices["by_symbol"]["XAUUSD"]
        assert "m_atr" in indices["by_required_field"]

    def test_deterministic_across_calls(self) -> None:
        reg = StrategyRegistry()
        reg.add_discovered(_entry("S1", active=True, lifecycle=Lifecycle.EXPLORATORY))
        assert reg.build_indices() == reg.build_indices()


class TestSnapshot:
    def test_valid_against_schema_empty_registry(self) -> None:
        reg = StrategyRegistry()
        snap = reg.snapshot(
            "1.0.0", "1.0.0", {"interface_major": 1, "runtime_api_major": 1, "feature_dictionary_major": 1},
            1700000000, _empty_agg(), {"overall": "OK", "total": 0, "active_count": 0, "counts": {}},
        )
        assert validate_registry_snapshot(snap) == []

    def test_valid_against_schema_with_entries(self) -> None:
        reg = StrategyRegistry()
        reg.add_discovered(_entry("S1", active=True, lifecycle=Lifecycle.EXPLORATORY))
        reg.add_discovered(_entry("S1"))  # forces a DUPLICATE entry too
        reg.add_discovered(_entry("S2", health=Health.CORRUPTED, lifecycle=Lifecycle.INVALID, with_contract=False))
        snap = reg.snapshot(
            "1.0.0", "1.0.0", {"interface_major": 1, "runtime_api_major": 1, "feature_dictionary_major": 1},
            1700000000, _empty_agg(), {"overall": "DEGRADED", "total": 2, "active_count": 1, "counts": {"LOADED": 1, "CORRUPTED": 1, "DUPLICATE": 1}},
        )
        errors = validate_registry_snapshot(snap)
        assert errors == [], errors
        assert len(snap["entries"]) == 3

    def test_extra_python_only_fields_not_leaked_into_snapshot(self) -> None:
        reg = StrategyRegistry()
        reg.add_discovered(_entry("S1"))
        snap = reg.snapshot(
            "1.0.0", "1.0.0", {"interface_major": 1, "runtime_api_major": 1, "feature_dictionary_major": 1},
            1700000000, _empty_agg(), {"overall": "OK", "total": 1, "active_count": 0, "counts": {}},
        )
        entry_dict = snap["entries"][0]
        assert "contract" not in entry_dict
        assert "lifecycle_before_disable" not in entry_dict
