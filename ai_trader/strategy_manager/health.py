"""Health Monitor (``STRATEGY_MANAGER_ARCHITECTURE.md`` §8) — classifies each registry entry and
the aggregate. Reports only; never mutates lifecycle or activation (that is the Lifecycle
Controller's job, "driven by policy/operator" per the architecture).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import UTC, date, datetime

from ai_trader.strategy_manager.types import Health, Lifecycle, ManagerHealth, ManagerOverallHealth, RegistryEntry

#: Classifications that only change via an actual new contract version (a real ``content_hash``
#: change re-processed by the Loader/Compatibility Checker) -- :func:`refine_health` never touches
#: these. Contrast with ``STALE``/``MISSING_DEPENDENCY``/``DEPRECATED``/``DISABLED``, which are
#: overlays computed from CURRENT registry state (the clock, other entries' active status) and so
#: must be re-derived from scratch every call -- they can legitimately reverse (a dependency becomes
#: active, an operator re-enables) without the entry's own contract ever changing.
_TERMINAL_HEALTH: frozenset[Health] = frozenset({
    Health.CORRUPTED, Health.INVALID, Health.INCOMPATIBLE, Health.DUPLICATE,
})


def _last_review_epoch(last_review: str) -> int:
    """Parse a ``YYYY-MM-DD`` date (UTC midnight) into epoch seconds."""
    parsed = date.fromisoformat(last_review)
    return int(datetime(parsed.year, parsed.month, parsed.day, tzinfo=UTC).timestamp())


def _is_stale(last_review: str, as_of: int, stale_after_days: int) -> bool:
    return (as_of - _last_review_epoch(last_review)) >= stale_after_days * 86400


def unsatisfied_dependencies(entry: RegistryEntry, canonical_by_id: Mapping[str, RegistryEntry]) -> list[str]:
    """Declared ``semantics.dependencies`` ids that are absent from the registry or not currently
    active (architecture §9: "missing declared dependency ... strategy not activatable until
    resolved"). Empty if ``entry`` has no contract or no dependencies. Shared by :func:`refine_health`
    (health reporting) and :mod:`ai_trader.strategy_manager.manager` (the ``activate()`` GUARD --
    reporting ``MISSING_DEPENDENCY`` health alone does not stop a strategy from being admitted; this
    function is what both call sites check to actually enforce it).
    """
    if entry.contract is None or not entry.contract.semantics.dependencies:
        return []
    return [
        dep for dep in entry.contract.semantics.dependencies
        if dep not in canonical_by_id or not canonical_by_id[dep].active
    ]


def refine_health(
    entries: Sequence[RegistryEntry],
    canonical_by_id: Mapping[str, RegistryEntry],
    as_of: int,
    stale_after_days: int,
) -> None:
    """Apply the health overlays that depend on the FULL registry picture (architecture §8):
    ``DISABLED`` (lifecycle overlay), ``MISSING_DEPENDENCY`` (cross-entry dependency check),
    ``DEPRECATED`` (already-computed compatibility flag surfaced as health), and ``STALE``
    (``last_review`` age vs. the caller-supplied ``as_of`` — never wall-clock, "Everything
    deterministic"). Recomputed from scratch every call for every non-:data:`_TERMINAL_HEALTH`
    entry (never assumes the previous overlay is still correct — a dependency may have become
    active, an operator may have re-enabled a strategy, more time may have passed). Entries whose
    BASE health is ``CORRUPTED``/``INVALID``/``INCOMPATIBLE``/``DUPLICATE`` are final
    classifications from the Loader/Compatibility Checker and are never touched here. Mutates
    ``entry.health`` in place.
    """
    for entry in entries:
        if entry.health in _TERMINAL_HEALTH:
            continue
        if entry.lifecycle is Lifecycle.DISABLED:
            entry.health = Health.DISABLED
            continue

        if unsatisfied_dependencies(entry, canonical_by_id):
            entry.health = Health.MISSING_DEPENDENCY
            continue

        if entry.compatibility.deprecated_fields:
            entry.health = Health.DEPRECATED
            continue

        if entry.last_review is not None and _is_stale(entry.last_review, as_of, stale_after_days):
            entry.health = Health.STALE
            continue

        entry.health = Health.LOADED


def aggregate_health(
    entries: Sequence[RegistryEntry], active_count: int, aggregated_context_ready: bool,
) -> ManagerHealth:
    """``health()`` (``STRATEGY_MANAGER_API.md`` §5): overall Manager health, per-state counts,
    aggregated-context readiness, and notes.

    Overall status:
    - ``FAILED`` — every entry is unusable (``CORRUPTED``/``INVALID``/``INCOMPATIBLE``), or there
      are entries but none loaded at all.
    - ``DEGRADED`` — at least one entry is unusable, stale, missing a dependency, or a duplicate id
      collision, but not all.
    - ``OK`` — everything else, including the valid, safe "empty library" state (architecture §12:
      "If NOTHING loads, the Manager is READY with an empty ACTIVE set").

    ``DUPLICATE`` counts toward ``DEGRADED`` (a real, worth-surfacing operational problem — an id
    collision) but never toward ``unusable``/``FAILED``: unlike ``CORRUPTED``/``INVALID``/
    ``INCOMPATIBLE``, a duplicate entry's rejected copy still had a valid, loaded contract; it's the
    canonical (first-loaded) entry under the same id that determines whether the strategy itself is
    usable.
    """
    counts: dict[str, int] = {h.value: 0 for h in Health}
    for entry in entries:
        counts[entry.health.value] += 1

    total = len(entries)
    unusable = counts[Health.CORRUPTED.value] + counts[Health.INVALID.value] + counts[Health.INCOMPATIBLE.value]
    degraded_signal = (
        unusable + counts[Health.STALE.value] + counts[Health.MISSING_DEPENDENCY.value]
        + counts[Health.DUPLICATE.value]
    )

    if total > 0 and unusable == total:
        overall = ManagerOverallHealth.FAILED
    elif degraded_signal > 0:
        overall = ManagerOverallHealth.DEGRADED
    else:
        overall = ManagerOverallHealth.OK

    notes: list[str] = []
    if total == 0:
        notes.append("no strategies discovered in the Library -- READY with an empty active set")
    if unusable > 0:
        notes.append(f"{unusable} strategy(ies) are quarantined (CORRUPTED/INVALID/INCOMPATIBLE)")
    if counts[Health.STALE.value] > 0:
        notes.append(f"{counts[Health.STALE.value]} strategy(ies) are STALE (last_review too old)")
    if counts[Health.MISSING_DEPENDENCY.value] > 0:
        notes.append(f"{counts[Health.MISSING_DEPENDENCY.value]} strategy(ies) have a missing/inactive dependency")
    if counts[Health.DUPLICATE.value] > 0:
        notes.append(f"{counts[Health.DUPLICATE.value]} duplicate id collision(s) rejected")

    return ManagerHealth(
        overall=overall,
        counts_by_health=counts,
        active_count=active_count,
        aggregated_context_ready=aggregated_context_ready,
        notes=tuple(notes),
    )
