"""Tests for :mod:`ai_trader.strategy_manager.health`."""

from __future__ import annotations

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_manager.health import aggregate_health, refine_health, unsatisfied_dependencies
from ai_trader.strategy_manager.tests.fixtures.contracts import make_contract_dict
from ai_trader.strategy_manager.types import CompatibilityResult, Health, Lifecycle, ManagerOverallHealth, RegistryEntry

AS_OF = 1_800_000_000  # 2027-01-15ish, well after any test's last_review dates


def _entry(
    id_: str, lifecycle: Lifecycle = Lifecycle.EXPERIMENTAL, health: Health = Health.LOADED,
    last_review: str | None = "2027-01-01", dependencies: list[str] | None = None,
    deprecated_fields: list[str] | None = None,
) -> RegistryEntry:
    contract = parse_contract(make_contract_dict(id=id_, dependencies=dependencies, last_review=last_review or "2027-01-01"))
    return RegistryEntry(
        id=id_, slug=f"{id_}_slug", source_path=f"/lib/{id_}/strategy.json", lifecycle=lifecycle, health=health,
        loaded=True, active=lifecycle in {Lifecycle.EXPLORATORY, Lifecycle.CANDIDATE, Lifecycle.VALIDATED, Lifecycle.PROMOTED},
        contract=contract, last_review=last_review,
        compatibility=CompatibilityResult(True, True, True, True, True, deprecated_fields=deprecated_fields or []),
    )


class TestUnsatisfiedDependencies:
    def test_no_dependencies_is_empty(self) -> None:
        entry = _entry("S1")
        assert unsatisfied_dependencies(entry, {"S1": entry}) == []

    def test_missing_id_reported(self) -> None:
        entry = _entry("S1", dependencies=["S99"])
        assert unsatisfied_dependencies(entry, {"S1": entry}) == ["S99"]

    def test_inactive_id_reported(self) -> None:
        dep = _entry("S2", lifecycle=Lifecycle.EXPERIMENTAL)  # not active
        entry = _entry("S1", dependencies=["S2"])
        assert unsatisfied_dependencies(entry, {"S1": entry, "S2": dep}) == ["S2"]

    def test_active_id_satisfies(self) -> None:
        dep = _entry("S2", lifecycle=Lifecycle.EXPLORATORY)  # active
        entry = _entry("S1", dependencies=["S2"])
        assert unsatisfied_dependencies(entry, {"S1": entry, "S2": dep}) == []

    def test_no_contract_is_empty(self) -> None:
        entry = _entry("S1")
        entry.contract = None
        assert unsatisfied_dependencies(entry, {"S1": entry}) == []


class TestRefineHealth:
    def test_disabled_lifecycle_overrides_health(self) -> None:
        entries = [_entry("S1", lifecycle=Lifecycle.DISABLED)]
        refine_health(entries, {"S1": entries[0]}, AS_OF, stale_after_days=180)
        assert entries[0].health is Health.DISABLED

    def test_fresh_entry_stays_loaded(self) -> None:
        entries = [_entry("S1", last_review="2027-01-01")]
        refine_health(entries, {"S1": entries[0]}, as_of=1_800_100_000, stale_after_days=180)
        assert entries[0].health is Health.LOADED

    def test_old_last_review_becomes_stale(self) -> None:
        entries = [_entry("S1", last_review="2020-01-01")]
        refine_health(entries, {"S1": entries[0]}, as_of=AS_OF, stale_after_days=180)
        assert entries[0].health is Health.STALE

    def test_deprecated_fields_take_priority_over_staleness_check_order(self) -> None:
        entries = [_entry("S1", last_review="2020-01-01", deprecated_fields=["execution.target"])]
        refine_health(entries, {"S1": entries[0]}, as_of=AS_OF, stale_after_days=180)
        assert entries[0].health is Health.DEPRECATED  # deprecated is checked before staleness

    def test_missing_dependency(self) -> None:
        entries = [_entry("S1", dependencies=["S99"])]
        refine_health(entries, {"S1": entries[0]}, as_of=AS_OF, stale_after_days=180)
        assert entries[0].health is Health.MISSING_DEPENDENCY

    def test_inactive_dependency_also_counts_as_missing(self) -> None:
        dep = _entry("S2", lifecycle=Lifecycle.EXPERIMENTAL)  # not active
        entries = [_entry("S1", dependencies=["S2"]), dep]
        refine_health(entries, {"S1": entries[0], "S2": dep}, as_of=AS_OF, stale_after_days=180)
        assert entries[0].health is Health.MISSING_DEPENDENCY

    def test_active_dependency_satisfies(self) -> None:
        dep = _entry("S2", lifecycle=Lifecycle.EXPLORATORY)  # active
        entries = [_entry("S1", dependencies=["S2"]), dep]
        refine_health(entries, {"S1": entries[0], "S2": dep}, as_of=1_800_100_000, stale_after_days=180)
        assert entries[0].health is Health.LOADED

    def test_non_loaded_base_health_never_overlaid(self) -> None:
        entries = [_entry("S1", health=Health.INVALID, last_review="2020-01-01")]
        refine_health(entries, {"S1": entries[0]}, as_of=AS_OF, stale_after_days=180)
        assert entries[0].health is Health.INVALID  # never "upgraded" to STALE

    def test_overlay_states_are_recomputed_and_can_recover(self) -> None:
        """MISSING_DEPENDENCY/STALE/DEPRECATED/DISABLED are NOT terminal like CORRUPTED/INVALID/
        INCOMPATIBLE/DUPLICATE -- a second refine_health() call must re-derive them from current
        state, not get stuck on whatever the first call computed."""
        dep = _entry("S2", lifecycle=Lifecycle.EXPERIMENTAL)  # not active yet
        target = _entry("S1", dependencies=["S2"])
        entries = [target, dep]
        by_id = {"S1": target, "S2": dep}

        refine_health(entries, by_id, as_of=1_780_000_000, stale_after_days=180)
        assert target.health is Health.MISSING_DEPENDENCY

        dep.lifecycle = Lifecycle.EXPLORATORY
        dep.active = True  # S2 becomes active between calls
        refine_health(entries, by_id, as_of=1_780_000_000, stale_after_days=180)
        assert target.health is Health.LOADED  # recovered without a fresh contract load

    def test_disabled_recovers_to_loaded_after_lifecycle_restored(self) -> None:
        entries = [_entry("S1", lifecycle=Lifecycle.DISABLED)]
        refine_health(entries, {"S1": entries[0]}, as_of=AS_OF, stale_after_days=180)
        assert entries[0].health is Health.DISABLED

        entries[0].lifecycle = Lifecycle.EXPLORATORY  # simulates enable() restoring the prior tier
        refine_health(entries, {"S1": entries[0]}, as_of=1_800_100_000, stale_after_days=180)
        assert entries[0].health is Health.LOADED


class TestAggregateHealth:
    def test_empty_registry_is_ok(self) -> None:
        result = aggregate_health([], active_count=0, aggregated_context_ready=True)
        assert result.overall is ManagerOverallHealth.OK
        assert "no strategies discovered" in result.notes[0]

    def test_all_healthy_is_ok(self) -> None:
        entries = [_entry("S1"), _entry("S2")]
        result = aggregate_health(entries, active_count=0, aggregated_context_ready=True)
        assert result.overall is ManagerOverallHealth.OK

    def test_all_unusable_is_failed(self) -> None:
        entries = [_entry("S1", health=Health.INVALID), _entry("S2", health=Health.CORRUPTED)]
        result = aggregate_health(entries, active_count=0, aggregated_context_ready=True)
        assert result.overall is ManagerOverallHealth.FAILED

    def test_partial_unusable_is_degraded(self) -> None:
        entries = [_entry("S1", health=Health.INVALID), _entry("S2")]
        result = aggregate_health(entries, active_count=0, aggregated_context_ready=True)
        assert result.overall is ManagerOverallHealth.DEGRADED

    def test_missing_dependency_entries_reported_in_notes(self) -> None:
        entries = [_entry("S1", health=Health.MISSING_DEPENDENCY)]
        result = aggregate_health(entries, active_count=0, aggregated_context_ready=True)
        assert result.overall is ManagerOverallHealth.DEGRADED
        assert any("missing/inactive dependency" in n for n in result.notes)

    def test_duplicate_id_collision_is_degraded_not_ok(self) -> None:
        entries = [_entry("S1"), _entry("S1", health=Health.DUPLICATE)]
        result = aggregate_health(entries, active_count=0, aggregated_context_ready=True)
        assert result.overall is ManagerOverallHealth.DEGRADED
        assert any("duplicate id collision" in n for n in result.notes)

    def test_duplicate_never_counts_toward_failed(self) -> None:
        # A duplicate's rejected copy had a valid, loaded contract -- unlike CORRUPTED/INVALID/
        # INCOMPATIBLE, it must never push overall status to FAILED on its own.
        entries = [_entry("S1", health=Health.DUPLICATE)]
        result = aggregate_health(entries, active_count=0, aggregated_context_ready=True)
        assert result.overall is not ManagerOverallHealth.FAILED

    def test_stale_entries_are_degraded_not_failed(self) -> None:
        entries = [_entry("S1", health=Health.STALE)]
        result = aggregate_health(entries, active_count=0, aggregated_context_ready=True)
        assert result.overall is ManagerOverallHealth.DEGRADED

    def test_counts_by_health_complete(self) -> None:
        entries = [_entry("S1"), _entry("S2", health=Health.INVALID)]
        result = aggregate_health(entries, active_count=0, aggregated_context_ready=True)
        assert result.counts_by_health["LOADED"] == 1
        assert result.counts_by_health["INVALID"] == 1
        assert result.counts_by_health["CORRUPTED"] == 0

    def test_active_count_and_context_readiness_passed_through(self) -> None:
        result = aggregate_health([], active_count=3, aggregated_context_ready=False)
        assert result.active_count == 3
        assert result.aggregated_context_ready is False
