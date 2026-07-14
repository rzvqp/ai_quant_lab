"""Strategy Registry (``STRATEGY_MANAGER_ARCHITECTURE.md`` §2, ``STRATEGY_REGISTRY_SCHEMA.json``) —
the in-memory store of every discovered strategy, including quarantined ones, plus its derived
indices. Indices are always computed fresh from ``entries`` (never separately mutated state), which
is what makes the registry deterministic by construction: "given the same Library + versions, the
registry, indices, and aggregated context are identical every load" (architecture §7 invariant 5).
"""

from __future__ import annotations

from typing import Any

from ai_trader.strategy_manager.types import AggregatedContext, Health, Lifecycle, RegistryEntry


class StrategyRegistry:
    """Owns the canonical list of :class:`~ai_trader.strategy_manager.types.RegistryEntry` objects.

    "Canonical" entries (one per unique ``id``, the first-loaded winner on a duplicate collision)
    are tracked separately from the full ``entries`` list (which includes every duplicate/failed
    entry too, per architecture §4 "both are reported").
    """

    __slots__ = ("_entries", "_by_id")

    def __init__(self) -> None:
        self._entries: list[RegistryEntry] = []
        self._by_id: dict[str, int] = {}

    def clear(self) -> None:
        """Full reset — used by ``load_library()`` (never a silent partial reset, mirrors the
        Market Scanner's ``configure()`` idempotency convention)."""
        self._entries = []
        self._by_id = {}

    def add_discovered(self, entry: RegistryEntry) -> RegistryEntry:
        """Append ``entry`` from a fresh discovery pass (``load_library()``). If its ``id`` collides
        with an already-registered canonical entry, ``entry`` is reclassified ``DUPLICATE``
        (architecture §4: "the later one is rejected as DUPLICATE; the first-loaded wins; both are
        reported") — its ``lifecycle``/``health``/``active`` are overridden and it is appended
        WITHOUT becoming the canonical (``by_id``-indexed) entry for that id. Returns the entry as
        actually stored (which may differ from the input if reclassified).
        """
        if entry.id in self._by_id:
            first = self._entries[self._by_id[entry.id]]
            entry.health = Health.DUPLICATE
            entry.lifecycle = Lifecycle.INVALID
            entry.active = False
            entry.errors = [
                *entry.errors,
                f"duplicate id {entry.id!r}: already loaded from {first.source_path!r}; "
                f"this copy ({entry.source_path!r}) is rejected",
            ]
        else:
            self._by_id[entry.id] = len(self._entries)
        self._entries.append(entry)
        return entry

    def get(self, strategy_id: str) -> RegistryEntry | None:
        """The canonical entry for ``strategy_id``, or ``None`` if unknown."""
        idx = self._by_id.get(strategy_id)
        return self._entries[idx] if idx is not None else None

    def replace_canonical(self, strategy_id: str, new_entry: RegistryEntry) -> None:
        """Overwrite an existing canonical entry in place (``reload()`` of a known id) — never
        creates a duplicate, since ``strategy_id`` is already canonical by definition here."""
        idx = self._by_id[strategy_id]
        self._entries[idx] = new_entry

    def all_entries(self) -> tuple[RegistryEntry, ...]:
        """Every entry, including rejected duplicates and quarantined loads."""
        return tuple(self._entries)

    def canonical_entries(self) -> tuple[RegistryEntry, ...]:
        """One entry per unique id — the winning (first-loaded) copy of each."""
        return tuple(self._entries[i] for i in self._by_id.values())

    def canonical_by_id(self) -> dict[str, RegistryEntry]:
        return {e.id: e for e in self.canonical_entries()}

    def active_entries(self) -> tuple[RegistryEntry, ...]:
        return tuple(e for e in self.canonical_entries() if e.active)

    def build_indices(self) -> dict[str, Any]:
        """Compute the ``indices`` object (``STRATEGY_REGISTRY_SCHEMA.json#/properties/indices``),
        fresh from ``entries`` every call — see module docstring on determinism."""
        by_id: dict[str, int] = dict(self._by_id)
        by_lifecycle: dict[str, list[str]] = {}
        by_health: dict[str, list[str]] = {}
        by_symbol: dict[str, list[str]] = {}
        by_required_field: dict[str, list[str]] = {}
        active: list[str] = []

        for entry in self.canonical_entries():
            by_lifecycle.setdefault(entry.lifecycle.value, []).append(entry.id)
            by_health.setdefault(entry.health.value, []).append(entry.id)
            if entry.active:
                active.append(entry.id)
            if entry.required_context is not None:
                for symbol in sorted(entry.required_context.symbols):
                    by_symbol.setdefault(symbol, []).append(entry.id)
                for fields in entry.required_context.fields_by_timeframe.values():
                    for field_name in sorted(fields):
                        by_required_field.setdefault(field_name, []).append(entry.id)

        return {
            "by_id": by_id,
            "by_lifecycle": by_lifecycle,
            "by_health": by_health,
            "by_symbol": by_symbol,
            "by_required_field": by_required_field,
            "active": sorted(active),
        }

    def snapshot(
        self,
        registry_version: str,
        manager_version: str,
        supported: dict[str, int],
        generated_at: int,
        aggregated_context: AggregatedContext,
        health_summary: dict[str, Any],
    ) -> dict[str, Any]:
        """The full registry object, shaped exactly per ``STRATEGY_REGISTRY_SCHEMA.json`` — used
        for introspection/audit and validated against that schema in the test suite."""
        return {
            "registry_version": registry_version,
            "manager_version": manager_version,
            "supported": supported,
            "generated_at": generated_at,
            "entries": [_entry_to_schema_dict(e) for e in self._entries],
            "indices": self.build_indices(),
            "aggregated_context": _aggregated_context_to_schema_dict(aggregated_context),
            "health_summary": health_summary,
        }


def _required_context_to_schema_dict(rc: Any) -> dict[str, Any] | None:
    if rc is None:
        return None
    return {
        "timeframes": sorted(rc.timeframes),
        "fields_by_timeframe": {tf: sorted(fs) for tf, fs in rc.fields_by_timeframe.items()},
        "lookback_by_timeframe": dict(rc.lookback_by_timeframe),
        "symbols": sorted(rc.symbols),
        "optional_fields_by_timeframe": (
            {tf: sorted(fs) for tf, fs in rc.optional_fields_by_timeframe.items()}
            if rc.optional_fields_by_timeframe else None
        ),
    }


def _entry_to_schema_dict(entry: RegistryEntry) -> dict[str, Any]:
    """Project a live :class:`RegistryEntry` onto exactly
    ``STRATEGY_REGISTRY_SCHEMA.json#/$defs/RegistryEntry``'s shape (``additionalProperties: false``
    — extra Python-only bookkeeping fields like ``contract``/``lifecycle_before_disable`` are
    intentionally omitted here)."""
    return {
        "id": entry.id,
        "slug": entry.slug,
        "source_path": entry.source_path,
        "lifecycle": entry.lifecycle.value,
        "health": entry.health.value,
        "loaded": entry.loaded,
        "active": entry.active,
        "contract_ref": {
            "identity_version": entry.contract_ref.identity_version,
            "interface_version": entry.contract_ref.interface_version,
            "content_hash": entry.contract_ref.content_hash,
        },
        "compatibility": {
            "compatible": entry.compatibility.compatible,
            "schema_valid": entry.compatibility.schema_valid,
            "interface_ok": entry.compatibility.interface_ok,
            "runtime_ok": entry.compatibility.runtime_ok,
            "context_ok": entry.compatibility.context_ok,
            "deprecated_fields": entry.compatibility.deprecated_fields or None,
            "reasons": entry.compatibility.reasons or None,
        },
        "required_context": _required_context_to_schema_dict(entry.required_context),
        "last_review": entry.last_review,
        "errors": entry.errors or None,
    }


def _aggregated_context_to_schema_dict(agg: AggregatedContext) -> dict[str, Any]:
    return {
        "timeframes": sorted(agg.timeframes),
        "required_fields_by_timeframe": {
            tf: sorted(fs) for tf, fs in agg.required_fields_by_timeframe.items()
        },
        "optional_fields_by_timeframe": (
            {tf: sorted(fs) for tf, fs in agg.optional_fields_by_timeframe.items()}
            if agg.optional_fields_by_timeframe else None
        ),
        "lookback_by_timeframe": dict(agg.lookback_by_timeframe),
        "symbols": sorted(agg.symbols),
        "warmup_bars": agg.warmup_bars,
        "feature_dictionary_major": agg.feature_dictionary_major,
        "interface_version": agg.interface_version,
        "contributor_ids": list(agg.contributor_ids),
    }
