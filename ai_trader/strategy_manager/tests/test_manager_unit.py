"""Unit tests for :class:`ai_trader.strategy_manager.manager.StrategyManager`."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from ai_trader.strategy_manager.config import ManagerConfig
from ai_trader.strategy_manager.exceptions import ManagerNotConfiguredError
from ai_trader.strategy_manager.manager import StrategyManager
from ai_trader.strategy_manager.tests.fixtures.contracts import make_contract_dict
from ai_trader.strategy_manager.tests.fixtures.fake_scanner import FakeScanner
from ai_trader.strategy_manager.types import Health, Lifecycle, NotFound

# Close to make_contract_dict()'s default last_review ("2026-07-01") so tests that don't care about
# staleness don't accidentally trip the STALE health overlay (stale_after_days defaults to 180).
AS_OF = int(datetime(2026, 7, 10, tzinfo=UTC).timestamp())


def _write(tmp_path: Path, folder: str, data: dict) -> None:
    d = tmp_path / folder
    d.mkdir(parents=True, exist_ok=True)
    (d / "strategy.json").write_text(json.dumps(data), encoding="utf-8")


def _manager(tmp_path: Path, scanner: FakeScanner | None = None, **config_kwargs) -> tuple[StrategyManager, FakeScanner]:
    scanner = scanner or FakeScanner()
    mgr = StrategyManager(ManagerConfig(library_path=tmp_path, **config_kwargs))
    mgr.configure(scanner)
    return mgr, scanner


class TestConfigure:
    def test_requires_configure_before_use(self, tmp_path: Path) -> None:
        mgr = StrategyManager(ManagerConfig(library_path=tmp_path))
        with pytest.raises(ManagerNotConfiguredError):
            mgr.load_library(as_of=AS_OF)

    def test_idempotent_reset(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        mgr, scanner = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        assert mgr.statistics().total == 1
        mgr.configure(scanner)  # re-configure -> full reset
        assert mgr.statistics().total == 0

    def test_handshake_failure_degrades_gracefully(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        mgr, scanner = _manager(tmp_path, scanner=FakeScanner(raise_on_handshake=True))
        report = mgr.load_library(as_of=AS_OF)
        assert report.loaded == ("S1",)
        view = mgr.find_strategy("S1")
        assert not isinstance(view, NotFound)
        assert view.health is Health.INCOMPATIBLE  # cannot verify context without a handshake


class TestLoadLibrary:
    def test_loads_valid_strategy(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        mgr, _ = _manager(tmp_path)
        report = mgr.load_library(as_of=AS_OF)
        assert report.loaded == ("S1",)
        assert report.failed == ()
        assert report.duplicates == ()

    def test_empty_library_is_ready_with_empty_active_set(self, tmp_path: Path) -> None:
        mgr, _ = _manager(tmp_path)
        report = mgr.load_library(as_of=AS_OF)
        assert report.loaded == ()
        assert report.notes != ()
        assert mgr.health().overall.value == "OK"
        assert mgr.active_strategies() == []

    def test_invalid_contract_quarantined(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", {"interface_version": "1.0.0"})
        mgr, _ = _manager(tmp_path)
        report = mgr.load_library(as_of=AS_OF)
        assert report.loaded == ()
        assert len(report.failed) == 1
        assert report.failed[0].health is Health.INVALID

    def test_incompatible_contract_quarantined(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1", required_data=[
            {"timeframe": "W1", "fields": ["nonexistent"], "lookback_bars": 5, "htf": None},
        ]))
        mgr, _ = _manager(tmp_path)
        report = mgr.load_library(as_of=AS_OF)
        assert report.loaded == ("S1",)  # schema-valid, so "loaded"
        assert len(report.failed) == 1  # but incompatible -> also in failed
        assert report.failed[0].health is Health.INCOMPATIBLE
        view = mgr.find_strategy("S1")
        assert view.lifecycle is Lifecycle.INVALID

    def test_duplicate_ids(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        _write(tmp_path, "S01_b", make_contract_dict(id="S1"))
        mgr, _ = _manager(tmp_path)
        report = mgr.load_library(as_of=AS_OF)
        assert report.loaded == ("S1",)
        assert len(report.duplicates) == 1

    def test_not_implemented_strategy(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1", status="NOT_IMPLEMENTED"))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        view = mgr.find_strategy("S1")
        assert view.lifecycle is Lifecycle.NOT_IMPLEMENTED

    def test_registers_requirements_with_scanner_even_when_empty(self, tmp_path: Path) -> None:
        mgr, scanner = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        assert len(scanner.registered_requirements) >= 1
        assert scanner.registered_requirements[-1].timeframes == frozenset()

    def test_auto_admit_policy(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1", maturity="EXPLORATORY"))
        mgr, _ = _manager(tmp_path, auto_admit_min_maturity="EXPLORATORY")
        mgr.load_library(as_of=AS_OF)
        view = mgr.find_strategy("S1")
        assert view.active is True
        assert view.lifecycle is Lifecycle.EXPLORATORY

    def test_no_auto_admit_by_default(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        view = mgr.find_strategy("S1")
        assert view.active is False
        assert view.lifecycle is Lifecycle.EXPERIMENTAL


class TestReload:
    def test_unchanged_contract_skipped(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        mgr, scanner = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        n_before = len(scanner.registered_requirements)
        report = mgr.reload(as_of=AS_OF + 1, strategy_id="S1")
        assert "unchanged" in report.notes[0]
        assert len(scanner.registered_requirements) == n_before  # no re-aggregation triggered

    def test_changed_contract_reflected(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1", name="Original"))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        _write(tmp_path, "S01_a", make_contract_dict(id="S1", name="Updated"))
        mgr.reload(as_of=AS_OF + 1, strategy_id="S1")
        view = mgr.find_strategy("S1")
        assert view.name == "Updated"

    def test_reload_raises_maturity_for_active_strategy(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1", maturity="EXPLORATORY"))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        mgr.activate("S1")
        assert mgr.find_strategy("S1").lifecycle is Lifecycle.EXPLORATORY
        _write(tmp_path, "S01_a", make_contract_dict(id="S1", maturity="CANDIDATE"))
        mgr.reload(as_of=AS_OF + 1, strategy_id="S1")
        assert mgr.find_strategy("S1").lifecycle is Lifecycle.CANDIDATE
        assert mgr.find_strategy("S1").active is True

    def test_reload_single_id_never_loaded_before(self, tmp_path: Path) -> None:
        # No prior load_library() call -- _folder_for() falls back to treating the id itself as the
        # folder name (the normal path is always reached via discover(), which this bypasses).
        _write(tmp_path, "S1", make_contract_dict(id="S1"))
        mgr, _ = _manager(tmp_path)
        report = mgr.reload(as_of=AS_OF, strategy_id="S1")
        assert "S1" in report.loaded
        assert mgr.find_strategy("S1").lifecycle is Lifecycle.EXPERIMENTAL

    def test_reload_whole_library(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        _write(tmp_path, "S02_b", make_contract_dict(id="S2"))
        report = mgr.reload(as_of=AS_OF + 1)
        assert "S2" in report.loaded
        assert mgr.statistics().total == 2


class TestValidate:
    def test_validate_single_unknown_id(self, tmp_path: Path) -> None:
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        report = mgr.validate("S999")
        assert report.ok is False
        assert report.reasons == ("unknown id",)

    def test_validate_single_known_id(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        report = mgr.validate("S1")
        assert report.ok is True
        assert report.schema_valid is True

    def test_validate_all(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        _write(tmp_path, "S02_b", make_contract_dict(id="S2"))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        reports = mgr.validate()
        assert isinstance(reports, list)
        assert len(reports) == 2

    def test_validate_never_mutates_lifecycle(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        before = mgr.find_strategy("S1").lifecycle
        mgr.validate("S1")
        assert mgr.find_strategy("S1").lifecycle == before


class TestListStrategies:
    def test_no_filter_returns_all_including_quarantined(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        _write(tmp_path, "S02_b", {"interface_version": "1.0.0"})
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        assert len(mgr.list_strategies()) == 2

    def test_filter_by_lifecycle(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1", status="NOT_IMPLEMENTED"))
        _write(tmp_path, "S02_b", make_contract_dict(id="S2"))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        views = mgr.list_strategies(lifecycle_filter=Lifecycle.NOT_IMPLEMENTED)
        assert [v.id for v in views] == ["S1"]

    def test_filter_by_health(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", {"interface_version": "1.0.0"})
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        assert len(mgr.list_strategies(health_filter=Health.INVALID)) == 1
        assert len(mgr.list_strategies(health_filter=Health.LOADED)) == 0

    def test_filter_by_symbol(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        assert len(mgr.list_strategies(symbol="XAUUSD")) == 1
        assert len(mgr.list_strategies(symbol="EURUSD")) == 0

    def test_filter_by_maturity(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1", maturity="CANDIDATE"))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        from ai_trader.strategy_manager.contract import Maturity
        assert len(mgr.list_strategies(maturity=Maturity.CANDIDATE)) == 1
        assert len(mgr.list_strategies(maturity=Maturity.PROMOTED)) == 0

    def test_unmatched_filter_yields_empty_list_not_error(self, tmp_path: Path) -> None:
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        assert mgr.list_strategies(symbol="NOTHING") == []


class TestFindStrategyAndGetContract:
    def test_find_unknown_returns_not_found(self, tmp_path: Path) -> None:
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        assert isinstance(mgr.find_strategy("S999"), NotFound)

    def test_get_contract_known(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1", name="Alpha"))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        contract = mgr.get_contract("S1")
        assert not isinstance(contract, NotFound)
        assert contract.identity.name == "Alpha"

    def test_get_contract_unknown(self, tmp_path: Path) -> None:
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        assert isinstance(mgr.get_contract("S999"), NotFound)

    def test_get_contract_for_corrupted_entry_is_not_found(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", {"interface_version": "1.0.0"})
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        assert isinstance(mgr.get_contract("S1"), NotFound)


class TestActiveStrategies:
    def test_empty_when_nothing_active(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        assert mgr.active_strategies() == []

    def test_returns_handle_after_activation(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        mgr.activate("S1")
        handles = mgr.active_strategies()
        assert len(handles) == 1
        assert handles[0].id == "S1"


class TestRequiredContext:
    def test_empty_active_set_is_empty_but_valid(self, tmp_path: Path) -> None:
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        agg = mgr.required_context()
        assert agg.timeframes == frozenset()
        assert agg.contributor_ids == ()

    def test_reflects_active_strategy(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        mgr.activate("S1")
        agg = mgr.required_context()
        assert agg.contributor_ids == ("S1",)


class TestLifecycleControl:
    def test_activate_unknown_id(self, tmp_path: Path) -> None:
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        result = mgr.activate("S999")
        assert result.ok is False
        assert result.reason == "unknown id"

    def test_activate_deactivate_roundtrip(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        act = mgr.activate("S1")
        assert act.ok and act.to_state is Lifecycle.EXPLORATORY
        deact = mgr.deactivate("S1")
        assert deact.ok and deact.to_state is Lifecycle.EXPERIMENTAL

    def test_disable_enable_roundtrip(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        mgr.activate("S1")
        dis = mgr.disable("S1", reason="test kill-switch")
        assert dis.ok and dis.to_state is Lifecycle.DISABLED
        assert mgr.find_strategy("S1").health is Health.DISABLED
        en = mgr.enable("S1")
        assert en.ok and en.to_state is Lifecycle.EXPLORATORY  # restored prior state
        assert mgr.find_strategy("S1").health is Health.LOADED

    def test_disable_records_reason(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        mgr.disable("S1", reason="operator kill-switch")
        entry_view = mgr.find_strategy("S1")
        assert entry_view.health is Health.DISABLED

    def test_retire_is_terminal(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        ret = mgr.retire("S1", reason="deprecated by research")
        assert ret.ok and ret.to_state is Lifecycle.RETIRED
        act = mgr.activate("S1")
        assert act.ok is False

    def test_lifecycle_change_triggers_reaggregation(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        mgr, scanner = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        n_before = len(scanner.registered_requirements)
        mgr.activate("S1")
        assert len(scanner.registered_requirements) == n_before + 1
        assert scanner.registered_requirements[-1].timeframes == frozenset({"M15"})


class TestIntrospection:
    def test_statistics(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        mgr.activate("S1")
        stats = mgr.statistics()
        assert stats.total == 1
        assert stats.active_count == 1
        assert stats.by_lifecycle["EXPLORATORY"] == 1

    def test_versions(self, tmp_path: Path) -> None:
        mgr, _ = _manager(tmp_path)
        v = mgr.versions()
        assert v.manager_version == "1.0.0"
        assert v.supported_interface_major == 1

    def test_health_ok_when_all_good(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        assert mgr.health().overall.value == "OK"

    def test_stale_last_review_degrades_health(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1", last_review="2020-01-01"))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)  # AS_OF is 2026-07-10, far past 180 days from 2020-01-01
        assert mgr.find_strategy("S1").health is Health.STALE
        assert mgr.health().overall.value == "DEGRADED"

    def test_snapshot_validates_against_schema(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        _write(tmp_path, "S02_b", {"interface_version": "1.0.0"})
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        mgr.activate("S1")
        errors = mgr.validate_snapshot_against_schema()
        assert errors == [], errors


class TestShutdown:
    def test_deactivates_everything_and_clears_scanner_requirements(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        mgr, scanner = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        mgr.activate("S1")
        assert mgr.active_strategies() != []
        final_health = mgr.shutdown()
        assert mgr.active_strategies() == []
        assert scanner.registered_requirements[-1].timeframes == frozenset()
        assert final_health is not None
