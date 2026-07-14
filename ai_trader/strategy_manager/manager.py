"""``StrategyManager`` — the public facade implementing ``STRATEGY_MANAGER_API.md`` exactly.

This is the ONLY class other AI-Trader modules touch. It wires together the Strategy Loader,
Compatibility Checker, Strategy Registry, Lifecycle Controller, Context Aggregator, and Health
Monitor into the documented, versioned, fail-safe Strategy Manager behaviour. It is a pure
management/registry/validation module: no signals, no scoring, no orders, no Research-Lab access
(``STRATEGY_MANAGER_ARCHITECTURE.md`` §1/§7).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Protocol

from ai_trader.market_scanner.types import CompatibilityReport as ScannerCompatibilityReport
from ai_trader.market_scanner.types import ProvidedFeatures, Requirements, ScannerVersions

from ai_trader.strategy_manager import compatibility, health, lifecycle, loader, registry as registry_mod
from ai_trader.strategy_manager.config import ManagerConfig
from ai_trader.strategy_manager.contract import Contract, Maturity, maturity_rank
from ai_trader.strategy_manager.exceptions import ManagerNotConfiguredError
from ai_trader.strategy_manager.handle import StrategyHandle, StrategyRuntimeHandle
from ai_trader.strategy_manager.lifecycle import TransitionOutcome
from ai_trader.strategy_manager.loader import LoadOutcome
from ai_trader.strategy_manager.registry import StrategyRegistry
from ai_trader.strategy_manager.registry_schema_validation import validate_registry_snapshot
from ai_trader.strategy_manager.required_context import compute_required_context
from ai_trader.strategy_manager.types import (
    ACTIVATABLE_LIFECYCLES,
    AggregatedContext,
    CompatibilityResult,
    Health,
    LifecycleResult,
    Lifecycle,
    LoadFailure,
    LoadReport,
    ManagerHealth,
    NotFound,
    RegistryEntry,
    Statistics,
    StrategyView,
    ValidationReport,
    VersionInfo,
)
from ai_trader.strategy_manager import aggregator

logger = logging.getLogger(__name__)


class MarketScannerLike(Protocol):
    """Structural shape of the Market Scanner methods the Manager talks to
    (``STRATEGY_MANAGER_ARCHITECTURE.md`` §10: "the Manager communicates directly ONLY with the
    Market Scanner ... and the Signal Engine"). Any object with these three methods works — in
    production this is a real :class:`ai_trader.market_scanner.scanner.MarketScanner`; tests inject
    a lightweight double instead of standing up a fully configured scanner."""

    def get_provided_features(self) -> ProvidedFeatures: ...
    def versions(self) -> ScannerVersions: ...
    def register_requirements(self, req: Requirements) -> ScannerCompatibilityReport: ...


def _to_scanner_requirements(agg: AggregatedContext) -> Requirements:
    """Convert the Manager's own :class:`AggregatedContext` into the Market Scanner's
    ``Requirements`` shape (a straightforward field-for-field mapping — both already use
    ``frozenset``s; no Market Scanner code is touched, only its published type is constructed)."""
    return Requirements(
        timeframes=agg.timeframes,
        fields_by_timeframe=dict(agg.required_fields_by_timeframe),
        lookback_by_timeframe=dict(agg.lookback_by_timeframe),
        symbols=agg.symbols,
        optional_fields_by_timeframe=dict(agg.optional_fields_by_timeframe),
    )


def _empty_aggregated_context(config: ManagerConfig) -> AggregatedContext:
    return AggregatedContext(
        timeframes=frozenset(),
        required_fields_by_timeframe={},
        lookback_by_timeframe={},
        symbols=frozenset(),
        feature_dictionary_major=config.supported.feature_dictionary_major,
        interface_version=f"{config.supported.interface_major}.0.0",
        contributor_ids=(),
    )


class StrategyManager:
    """The Strategy Manager. See ``STRATEGY_MANAGER_API.md`` for the full contract."""

    def __init__(self, config: ManagerConfig | None = None) -> None:
        self._config = config or ManagerConfig()
        self._registry = StrategyRegistry()
        self._scanner: MarketScannerLike | None = None
        self._provided_features: ProvidedFeatures | None = None
        self._scanner_versions: ScannerVersions | None = None
        self._aggregated_context: AggregatedContext = _empty_aggregated_context(self._config)
        self._configured = False
        self._last_as_of = 0

    # ------------------------------------------------------------------ 0. configuration

    def configure(self, scanner: MarketScannerLike) -> None:
        """Wire the Manager to a Market Scanner and reset all state (architecture §12 steps 1-2:
        handshake). Idempotent: calling again fully resets the registry, matching the Market
        Scanner's own ``configure()`` convention ("never a silent partial reset").

        Fail-safe: if the handshake itself raises (e.g. the scanner is misconfigured), the Manager
        still becomes configured with a ``None`` feature dictionary — every contract's compatibility
        check then honestly reports "no Market Scanner handshake available" (architecture §12: "if
        the Scanner handshake ... partially fails, the Manager starts with only the strategies that
        passed").
        """
        self._scanner = scanner
        self._registry.clear()
        self._aggregated_context = _empty_aggregated_context(self._config)
        self._configured = True
        try:
            self._provided_features = scanner.get_provided_features()
            self._scanner_versions = scanner.versions()
        except Exception as exc:  # noqa: BLE001 -- deliberate: an external dependency's failure
            # must never abort configure(); every subsequent compatibility check degrades honestly.
            logger.warning("Market Scanner handshake failed during configure(): %s", exc)
            self._provided_features = None
            self._scanner_versions = None
        logger.info("StrategyManager configured (scanner handshake %s)", "ok" if self._provided_features else "degraded")

    def _require_configured(self) -> None:
        if not self._configured:
            raise ManagerNotConfiguredError("StrategyManager.configure(...) must be called first")

    # ------------------------------------------------------------------ 1. loading & validation

    def load_library(self, as_of: int, path: str | Path | None = None) -> LoadReport:
        """Discover, parse, schema-validate, and compatibility-check every ``strategy.json`` under
        the Library path; populate the registry, assign initial lifecycles, apply the admission
        policy, and (re)compute the aggregated context (``STRATEGY_MANAGER_API.md`` §1).
        """
        self._require_configured()
        library_path = Path(path) if path is not None else self._config.library_path
        self._registry.clear()
        self._last_as_of = as_of

        outcomes = loader.load_all(library_path)
        for outcome in outcomes:
            self._process_outcome(outcome)

        self._recompute_full(as_of)
        notes: tuple[str, ...] = () if outcomes else (f"no strategy.json files found under {library_path}",)
        return self._build_load_report(notes)

    def reload(self, as_of: int, strategy_id: str | None = None) -> LoadReport:
        """Re-load the whole Library (``strategy_id`` omitted) or a single strategy
        (``STRATEGY_MANAGER_API.md`` §1). Detects contract changes via ``content_hash``; unchanged
        contracts are skipped (no re-validation, no lifecycle churn)."""
        self._require_configured()
        self._last_as_of = as_of
        library_path = self._config.library_path

        if strategy_id is None:
            changed_ids: list[str] = []
            for path in loader.discover(library_path):
                outcome = loader.load_one(path)
                existing = self._registry.get(outcome.id) if outcome.id else None
                if existing is not None and existing.contract_ref.content_hash == outcome.contract_ref.content_hash:
                    continue  # unchanged -> skip (sequence §3)
                self._process_outcome(outcome, is_reload=existing is not None)
                if outcome.id:
                    changed_ids.append(outcome.id)
            self._recompute_full(as_of)
            return self._build_load_report((), only_ids=frozenset(changed_ids) if changed_ids else None)

        existing = self._registry.get(strategy_id)
        candidate_path = library_path / self._folder_for(strategy_id, existing) / "strategy.json"
        outcome = loader.load_one(candidate_path)
        if existing is not None and existing.contract_ref.content_hash == outcome.contract_ref.content_hash:
            return LoadReport((), (), (), self._counts_by_lifecycle(), self._counts_by_health(), self._config.registry_version, (f"{strategy_id}: unchanged, skipped",))
        self._process_outcome(outcome, is_reload=existing is not None)
        self._recompute_full(as_of)
        return self._build_load_report((), only_ids=frozenset({strategy_id}))

    @staticmethod
    def _folder_for(strategy_id: str, existing: RegistryEntry | None) -> str:
        if existing is not None:
            return Path(existing.source_path).parent.name
        return strategy_id  # best-effort fallback if never loaded before; discover() is the normal path

    def _process_outcome(self, outcome: LoadOutcome, is_reload: bool = False) -> None:
        existing = self._registry.get(outcome.id) if (is_reload and outcome.id) else None
        compat = self._check_compatibility(outcome)

        if is_reload and existing is not None:
            transition = lifecycle.reload_transition(existing.lifecycle, outcome.contract, compat)
            new_lifecycle = transition.to_state if transition.to_state is not None else Lifecycle.INVALID
        else:
            new_lifecycle = lifecycle.initial_lifecycle(outcome, compat)

        entry = loader.draft_registry_entry(outcome, compat, new_lifecycle)
        specific_health = lifecycle.is_health_incompatible_bucket(new_lifecycle, outcome.ok, compat.compatible)
        if specific_health is not None:
            entry.health = specific_health
        if new_lifecycle is Lifecycle.DISABLED:
            # reload_transition() preserves DISABLED as an operator overlay across a content reload
            # (T10/T11 are the only documented ways in/out) -- carry the pre-disable tier forward too,
            # so a later enable() still restores to the right place, not just Health.DISABLED itself.
            entry.health = Health.DISABLED
            entry.lifecycle_before_disable = existing.lifecycle_before_disable if existing is not None else None
        if entry.contract is not None:
            entry.required_context = compute_required_context(entry.contract, self._config.symbols)
        entry.active = entry.lifecycle in ACTIVATABLE_LIFECYCLES

        if is_reload and outcome.id:
            self._registry.replace_canonical(outcome.id, entry)
        else:
            self._registry.add_discovered(entry)

        if (
            entry.health is Health.LOADED
            and entry.lifecycle is Lifecycle.EXPERIMENTAL
            and self._config.auto_admit_min_maturity is not None
        ):
            self._maybe_auto_admit(entry)

    def _maybe_auto_admit(self, entry: RegistryEntry) -> None:
        threshold = self._config.auto_admit_min_maturity
        if threshold is None or entry.contract is None:
            return
        if maturity_rank(entry.contract.lifecycle.maturity) >= maturity_rank(Maturity(threshold)):
            outcome = lifecycle.admit(entry.lifecycle, entry.contract)
            self._apply_transition(entry, outcome, "activate")

    def _check_compatibility(self, outcome: LoadOutcome) -> CompatibilityResult:
        if outcome.contract is None:
            return CompatibilityResult(False, schema_valid=False, interface_ok=False, runtime_ok=False, context_ok=False)
        return compatibility.check(
            outcome.contract, self._provided_features, self._config.supported, self._config.deprecated_field_paths,
        )

    def validate(self, strategy_id: str | None = None) -> ValidationReport | list[ValidationReport]:
        """Dry validation, without mutating lifecycle/activation (``STRATEGY_MANAGER_API.md`` §1)."""
        self._require_configured()
        if strategy_id is not None:
            entry = self._registry.get(strategy_id)
            if entry is None:
                return ValidationReport(strategy_id, False, False, False, False, False, reasons=("unknown id",))
            return self._entry_validation_report(entry)
        return [self._entry_validation_report(e) for e in self._registry.canonical_entries()]

    @staticmethod
    def _entry_validation_report(entry: RegistryEntry) -> ValidationReport:
        compat = entry.compatibility
        return ValidationReport(
            id=entry.id, ok=compat.compatible, schema_valid=compat.schema_valid,
            interface_ok=compat.interface_ok, runtime_ok=compat.runtime_ok, context_ok=compat.context_ok,
            deprecated=tuple(compat.deprecated_fields), reasons=tuple(compat.reasons) + tuple(entry.errors),
        )

    # ------------------------------------------------------------------ 2. querying the registry

    def list_strategies(
        self,
        lifecycle_filter: Lifecycle | None = None,
        health_filter: Health | None = None,
        symbol: str | None = None,
        maturity: Maturity | None = None,
    ) -> list[StrategyView]:
        """Read-only views, optionally filtered (``STRATEGY_MANAGER_API.md`` §2). Includes
        quarantined entries. An unmatched filter value yields an empty list, never an error."""
        self._require_configured()
        views: list[StrategyView] = []
        for entry in self._registry.canonical_entries():
            if lifecycle_filter is not None and entry.lifecycle is not lifecycle_filter:
                continue
            if health_filter is not None and entry.health is not health_filter:
                continue
            if symbol is not None and (entry.required_context is None or symbol not in entry.required_context.symbols):
                continue
            contract_maturity = entry.contract.lifecycle.maturity if entry.contract is not None else None
            if maturity is not None and contract_maturity is not maturity:
                continue
            views.append(self._to_view(entry))
        return views

    @staticmethod
    def _to_view(entry: RegistryEntry) -> StrategyView:
        contract = entry.contract
        return StrategyView(
            id=entry.id,
            name=contract.identity.name if contract is not None else None,
            slug=entry.slug,
            lifecycle=entry.lifecycle,
            health=entry.health,
            identity_version=entry.contract_ref.identity_version,
            interface_version=entry.contract_ref.interface_version,
            maturity=contract.lifecycle.maturity if contract is not None else None,
            active=entry.active,
        )

    def active_strategies(self) -> list[StrategyHandle]:
        """Interface handles for the live active set — the ONLY method that yields runtime handles,
        for the Signal Engine (``STRATEGY_MANAGER_API.md`` §2)."""
        self._require_configured()
        handles: list[StrategyHandle] = []
        for entry in self._registry.active_entries():
            if entry.contract is None:
                continue  # cannot happen for an active entry (active implies a loaded contract), defensive
            api = StrategyRuntimeHandle(entry.id, entry.contract, self._config.symbols)
            handles.append(StrategyHandle(id=entry.id, contract=entry.contract, api=api))
        return handles

    def find_strategy(self, strategy_id: str) -> StrategyView | NotFound:
        self._require_configured()
        entry = self._registry.get(strategy_id)
        return NotFound(strategy_id) if entry is None else self._to_view(entry)

    def get_contract(self, strategy_id: str) -> Contract | NotFound:
        self._require_configured()
        entry = self._registry.get(strategy_id)
        if entry is None or entry.contract is None:
            return NotFound(strategy_id)
        return entry.contract

    # ------------------------------------------------------------------ 3. context aggregation

    def required_context(self) -> AggregatedContext:
        """``UNION(required_context())`` over ACTIVE strategies — the Market Scanner specification
        (``STRATEGY_MANAGER_API.md`` §3). Stable given the current active set; empty-but-valid if
        the active set is empty."""
        self._require_configured()
        return self._aggregated_context

    def _recompute_context_only(self) -> None:
        agg, skipped = aggregator.recompute(
            self._registry.active_entries(), self._config.symbols,
            self._config.supported.feature_dictionary_major,
            f"{self._config.supported.interface_major}.0.0",
        )
        if skipped:
            logger.warning("Context Aggregator excluded %d inconsistent active entr(y/ies): %s", len(skipped), skipped)
        self._aggregated_context = agg
        if self._scanner is not None:
            self._scanner.register_requirements(_to_scanner_requirements(agg))

    def _recompute_full(self, as_of: int) -> None:
        health.refine_health(self._registry.all_entries(), self._registry.canonical_by_id(), as_of, self._config.stale_after_days)
        self._recompute_context_only()

    # ------------------------------------------------------------------ 4. lifecycle control

    def _apply_transition(self, entry: RegistryEntry, outcome: TransitionOutcome, trigger: str) -> None:
        if not outcome.ok or outcome.to_state is None:
            return
        if trigger == "disable":
            entry.lifecycle_before_disable = outcome.from_state
        elif trigger == "enable":
            entry.lifecycle_before_disable = None
        entry.lifecycle = outcome.to_state
        entry.active = entry.lifecycle in ACTIVATABLE_LIFECYCLES
        # Health is NOT set here -- _mutate() always runs a full refine_health() afterward, which
        # picks up DISABLED (from entry.lifecycle) and every other overlay uniformly.

    def _mutate(self, strategy_id: str, op: str, transition_fn: object) -> LifecycleResult:
        self._require_configured()
        entry = self._registry.get(strategy_id)
        if entry is None:
            return LifecycleResult(strategy_id, None, None, False, "unknown id")
        outcome = transition_fn(entry)  # type: ignore[operator]
        self._apply_transition(entry, outcome, op)
        if outcome.ok:
            # A full refine, not a single-entry one: this entry's own lifecycle change can flip
            # OTHER entries' MISSING_DEPENDENCY classification too (a dependency just became
            # active/inactive) -- see health.unsatisfied_dependencies().
            health.refine_health(
                self._registry.all_entries(), self._registry.canonical_by_id(),
                self._last_as_of, self._config.stale_after_days,
            )
            self._recompute_context_only()
        return LifecycleResult(strategy_id, outcome.from_state, outcome.to_state, outcome.ok, outcome.reason)

    def activate(self, strategy_id: str) -> LifecycleResult:
        self._require_configured()
        entry = self._registry.get(strategy_id)
        if entry is not None:
            missing = health.unsatisfied_dependencies(entry, self._registry.canonical_by_id())
            if missing:
                return LifecycleResult(
                    strategy_id, entry.lifecycle, entry.lifecycle, False,
                    f"cannot activate: missing/inactive dependencies {missing}",
                )
        return self._mutate(strategy_id, "activate", lambda e: lifecycle.admit(e.lifecycle, e.contract))

    def deactivate(self, strategy_id: str) -> LifecycleResult:
        return self._mutate(strategy_id, "deactivate", lambda e: lifecycle.withdraw_admit(e.lifecycle))

    def disable(self, strategy_id: str, reason: str) -> LifecycleResult:
        result = self._mutate(strategy_id, "disable", lambda e: lifecycle.disable(e.lifecycle))
        if result.ok:
            entry = self._registry.get(strategy_id)
            if entry is not None:
                entry.errors = [*entry.errors, f"disabled: {reason}"]
        return result

    def enable(self, strategy_id: str) -> LifecycleResult:
        self._require_configured()
        entry = self._registry.get(strategy_id)
        if entry is not None and entry.contract is not None:
            # "enable re-validates before restoring" (STRATEGY_MANAGER_API.md §4) -- recompute
            # compatibility fresh here rather than trusting whatever was cached from the last load,
            # so a scanner feature-dictionary change while this strategy sat disabled is honored.
            entry.compatibility = compatibility.check(
                entry.contract, self._provided_features, self._config.supported, self._config.deprecated_field_paths,
            )
        return self._mutate(
            strategy_id, "enable",
            lambda e: lifecycle.enable(e.lifecycle, e.lifecycle_before_disable, e.contract, e.compatibility),
        )

    def retire(self, strategy_id: str, reason: str) -> LifecycleResult:
        result = self._mutate(strategy_id, "retire", lambda e: lifecycle.retire(e.lifecycle))
        if result.ok:
            entry = self._registry.get(strategy_id)
            if entry is not None:
                entry.errors = [*entry.errors, f"retired: {reason}"]
        return result

    # ------------------------------------------------------------------ 5. introspection & health

    def statistics(self) -> Statistics:
        self._require_configured()
        entries = self._registry.canonical_entries()
        agg = self._aggregated_context
        return Statistics(
            total=len(entries),
            by_lifecycle=self._counts_by_lifecycle(),
            by_health=self._counts_by_health(),
            active_count=len(self._registry.active_entries()),
            aggregated_context_summary={
                "timeframes": sorted(agg.timeframes),
                "symbols": sorted(agg.symbols),
                "contributor_count": len(agg.contributor_ids),
                "feature_dictionary_major": agg.feature_dictionary_major,
            },
        )

    def health(self) -> ManagerHealth:
        """Overall Manager health (``STRATEGY_MANAGER_API.md`` §5). Reports only; takes no action."""
        self._require_configured()
        entries = self._registry.canonical_entries()
        return health.aggregate_health(entries, len(self._registry.active_entries()), aggregated_context_ready=True)

    def versions(self) -> VersionInfo:
        return VersionInfo(
            manager_version=self._config.manager_version,
            registry_version=self._config.registry_version,
            supported_interface_major=self._config.supported.interface_major,
            supported_runtime_api_major=self._config.supported.runtime_api_major,
            supported_feature_dictionary_major=self._config.supported.feature_dictionary_major,
        )

    # ------------------------------------------------------------------ 6. shutdown

    def shutdown(self) -> ManagerHealth:
        """Deactivate every strategy, leave the Market Scanner requirements empty
        (architecture §12 "Shutdown"), and return the final health snapshot."""
        self._require_configured()
        for entry in self._registry.canonical_entries():
            if entry.lifecycle in ACTIVATABLE_LIFECYCLES:
                outcome = lifecycle.withdraw_admit(entry.lifecycle)
                self._apply_transition(entry, outcome, "deactivate")
        self._recompute_context_only()
        return self.health()

    # ------------------------------------------------------------------ introspection helpers

    def snapshot(self) -> dict[str, object]:
        """The full registry object, schema-shaped (``STRATEGY_REGISTRY_SCHEMA.json``)."""
        self._require_configured()
        supported = {
            "interface_major": self._config.supported.interface_major,
            "runtime_api_major": self._config.supported.runtime_api_major,
            "feature_dictionary_major": self._config.supported.feature_dictionary_major,
        }
        health_summary = self._health_summary_dict()
        return self._registry.snapshot(
            self._config.registry_version, self._config.manager_version, supported,
            self._last_as_of, self._aggregated_context, health_summary,
        )

    def _health_summary_dict(self) -> dict[str, object]:
        mh = self.health()
        return {
            "overall": mh.overall.value,
            "total": len(self._registry.canonical_entries()),
            "active_count": mh.active_count,
            "counts": mh.counts_by_health,
        }

    def validate_snapshot_against_schema(self) -> list[str]:
        """Convenience for tests/tooling: validate :meth:`snapshot` against
        ``STRATEGY_REGISTRY_SCHEMA.json`` directly."""
        return validate_registry_snapshot(self.snapshot())

    def _counts_by_lifecycle(self) -> dict[str, int]:
        counts: dict[str, int] = {lc.value: 0 for lc in Lifecycle}
        for entry in self._registry.canonical_entries():
            counts[entry.lifecycle.value] += 1
        return counts

    def _counts_by_health(self) -> dict[str, int]:
        counts: dict[str, int] = {h.value: 0 for h in Health}
        for entry in self._registry.canonical_entries():
            counts[entry.health.value] += 1
        return counts

    def _build_load_report(self, notes: tuple[str, ...], only_ids: frozenset[str] | None = None) -> LoadReport:
        loaded: list[str] = []
        failed: list[LoadFailure] = []
        duplicates: list[LoadFailure] = []
        for entry in self._registry.all_entries():
            if only_ids is not None and entry.id not in only_ids:
                continue
            if entry.health is Health.DUPLICATE:
                duplicates.append(LoadFailure(entry.source_path, entry.id, entry.health, tuple(entry.errors)))
                continue
            if entry.loaded:
                loaded.append(entry.id)
                if not entry.compatibility.compatible:
                    failed.append(LoadFailure(entry.source_path, entry.id, entry.health, tuple(entry.errors) or tuple(entry.compatibility.reasons)))
            else:
                failed.append(LoadFailure(entry.source_path, entry.id, entry.health, tuple(entry.errors)))
        return LoadReport(
            loaded=tuple(loaded), failed=tuple(failed), duplicates=tuple(duplicates),
            counts_by_lifecycle=self._counts_by_lifecycle(), counts_by_health=self._counts_by_health(),
            registry_version=self._config.registry_version, notes=notes,
        )
