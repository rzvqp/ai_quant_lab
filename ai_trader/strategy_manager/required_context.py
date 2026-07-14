"""A single strategy's ``required_context()`` — a pure function of its contract.

Shared by :mod:`ai_trader.strategy_manager.aggregator` (which unions this over every ACTIVE
strategy) and :mod:`ai_trader.strategy_manager.handle` (whose runtime handle exposes exactly this
one Strategy API method, ``STRATEGY_API_v1.md`` §1: "Pure function of the contract ... Deterministic,
cheap, cacheable"). Split into its own module so neither of those needs to import the other.
"""

from __future__ import annotations

from ai_trader.strategy_manager.contract import Contract
from ai_trader.strategy_manager.types import RequiredContext


def compute_required_context(contract: Contract, symbols: frozenset[str]) -> RequiredContext:
    """Derive ``contract``'s own data requirement from ``semantics.required_data``.

    ``optional_fields_by_timeframe`` is always empty: the frozen ``strategy_contract.v1.schema.json``
    has no per-field "optional" marker in ``required_data`` today (architecture §6 describes an
    optional/required split as a Context Aggregator concept for a *future* interface capability —
    every field in the current schema is, by construction, required). ``symbols`` comes from the
    Manager's configuration, not the contract (see :class:`~ai_trader.strategy_manager.config.
    ManagerConfig.symbols`'s docstring: the contract schema has no symbol field at all).

    The schema does not require ``required_data`` entries to have distinct ``timeframe`` values, so
    two entries CAN legally share the same timeframe (e.g. one for a base field set, one adding a
    confirmation field). Every entry is merged (fields unioned, lookback max-wins) rather than
    keeping only the last entry for a given timeframe — this mirrors
    :func:`ai_trader.strategy_manager.compatibility.check`, which already validates every entry
    individually without collapsing by timeframe; a strategy that passes compatibility must not then
    have its own runtime handle/aggregation under-report what it actually needs.
    """
    fields_by_timeframe: dict[str, set[str]] = {}
    lookback_by_timeframe: dict[str, int] = {}
    htf: set[str] = set()
    warmup_bars = 0
    for rd in contract.semantics.required_data:
        fields_by_timeframe.setdefault(rd.timeframe, set()).update(rd.fields)
        lookback_by_timeframe[rd.timeframe] = max(lookback_by_timeframe.get(rd.timeframe, 0), rd.lookback_bars)
        if rd.htf:
            htf.update(rd.htf)
        warmup_bars = max(warmup_bars, rd.lookback_bars)
    return RequiredContext(
        timeframes=frozenset(fields_by_timeframe),
        fields_by_timeframe={tf: frozenset(fs) for tf, fs in fields_by_timeframe.items()},
        lookback_by_timeframe=lookback_by_timeframe,
        symbols=symbols,
        optional_fields_by_timeframe={},
        htf=frozenset(htf),
        warmup_bars=warmup_bars,
    )
