"""Context Aggregator (``STRATEGY_MANAGER_ARCHITECTURE.md`` §6) — computes
``UNION(required_context())`` over ACTIVE strategies. This IS the Market Scanner specification; the
Manager is its sole producer (architecture §6: "the scanner never inspects strategies directly").
"""

from __future__ import annotations

from collections.abc import Sequence

from ai_trader.strategy_manager.types import AggregatedContext, RegistryEntry


def recompute(
    active_entries: Sequence[RegistryEntry],
    symbols: frozenset[str],
    feature_dictionary_major: int,
    interface_version: str,
) -> tuple[AggregatedContext, tuple[str, ...]]:
    """Union every active, compatible entry's ``required_context()`` into one
    :class:`~ai_trader.strategy_manager.types.AggregatedContext`.

    Reads each entry's already-computed ``entry.required_context`` (set once by the caller —
    ``manager._process_outcome`` — via :func:`~ai_trader.strategy_manager.required_context.
    compute_required_context`) rather than recomputing it here, so the same pure function of a
    contract is never evaluated twice per aggregation cycle.

    Args:
        active_entries: the current live active set (already filtered to
            ``lifecycle in ACTIVATABLE_LIFECYCLES``; this function trusts that filtering).
        symbols: the Manager's configured symbol universe (architecture §"Aggregation rules":
            "union the symbols" — every strategy shares the same Manager-configured universe today,
            see :class:`~ai_trader.strategy_manager.config.ManagerConfig.symbols`), used for the
            output's ``symbols`` field (equal to each entry's own ``required_context.symbols`` by
            construction, since both derive from the same Manager configuration).
        feature_dictionary_major: the single supported MAJOR every active entry was checked against.
        interface_version: the Manager's supported interface version line, recorded on the output.

    Returns:
        ``(AggregatedContext, skipped_ids)``. ``skipped_ids`` is the (normally empty) set of active
        entries excluded from the aggregate because their own ``compatibility.context_ok`` is
        ``False`` or their ``required_context`` was never computed — architecture §6's "hard
        conflict" path. In this build's design this cannot actually be reached in normal operation
        (a strategy only ever reaches the active set after its compatibility check passed against
        the Manager's one, single scanner reference — see the Compatibility Checker), but the
        defensive skip is real, tested code: if the registry ever ends up in an inconsistent state
        (e.g. a future reload path admits without re-checking), the aggregate silently degrades to
        excluding the inconsistent entry rather than emitting a Market Scanner spec containing a
        requirement that was never actually verified compatible.
    """
    timeframes: set[str] = set()
    required_fields: dict[str, set[str]] = {}
    optional_fields: dict[str, set[str]] = {}
    lookback: dict[str, int] = {}
    contributor_ids: list[str] = []
    warmups: list[int] = []
    skipped: list[str] = []

    for entry in active_entries:
        if not entry.compatibility.context_ok or entry.required_context is None:
            skipped.append(entry.id)
            continue
        rc = entry.required_context  # already computed once by the caller (manager._process_outcome)
        timeframes.update(rc.timeframes)
        for tf, fields in rc.fields_by_timeframe.items():
            required_fields.setdefault(tf, set()).update(fields)
            lookback[tf] = max(lookback.get(tf, 0), rc.lookback_by_timeframe.get(tf, 0))
        for tf, fields in rc.optional_fields_by_timeframe.items():
            optional_fields.setdefault(tf, set()).update(fields)
        contributor_ids.append(entry.id)
        warmups.append(rc.warmup_bars)

    aggregated = AggregatedContext(
        timeframes=frozenset(timeframes),
        required_fields_by_timeframe={tf: frozenset(f) for tf, f in required_fields.items()},
        optional_fields_by_timeframe={tf: frozenset(f) for tf, f in optional_fields.items()},
        lookback_by_timeframe=dict(lookback),
        symbols=symbols if contributor_ids else frozenset(),
        warmup_bars=max(warmups) if warmups else None,
        feature_dictionary_major=feature_dictionary_major,
        interface_version=interface_version,
        contributor_ids=tuple(sorted(contributor_ids)),
    )
    return aggregated, tuple(skipped)
