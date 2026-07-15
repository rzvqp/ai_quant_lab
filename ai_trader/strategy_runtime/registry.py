"""The runtime-evaluator registry: maps ``strategy_id -> RuntimeEvaluator subclass`` and builds the
real :class:`~ai_trader.strategy_runtime.evaluator.RuntimeStrategyHandle` objects Signal Engine
evaluates, from whatever Strategy Manager's own (authoritative, unmodified) ``active_strategies()``
currently reports as loaded.

**Authority stays with Strategy Manager.** This module never re-implements lifecycle/health/admission
logic -- a strategy only gets a runtime handle if (a) Strategy Manager itself successfully loaded and
activated its (now-migrated) contract, AND (b) a real evaluator has been registered for it here. Any
strategy failing either condition is silently excluded (never a stub, never a crash) -- exactly
`STRATEGY_RUNTIME_INTEGRATION_GAP.md` §5's "quarantine, don't force" precedent, extended one layer.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, RuntimeStrategyHandle

if TYPE_CHECKING:
    from ai_trader.strategy_manager.manager import StrategyManager

_FAMILY_EVALUATORS: dict[str, type[RuntimeEvaluator]] = {}


def register(strategy_id: str) -> Callable[[type[RuntimeEvaluator]], type[RuntimeEvaluator]]:
    def _decorator(cls: type[RuntimeEvaluator]) -> type[RuntimeEvaluator]:
        if strategy_id in _FAMILY_EVALUATORS:
            raise ValueError(f"duplicate runtime evaluator registration for {strategy_id!r}")
        _FAMILY_EVALUATORS[strategy_id] = cls
        return cls
    return _decorator


def registered_strategy_ids() -> frozenset[str]:
    return frozenset(_FAMILY_EVALUATORS)


def _ensure_families_imported() -> None:
    """Import the ``families`` package so every module's ``@register(...)`` decorator has run.
    Idempotent (Python caches imports); called lazily so importing this module alone never has the
    side effect of loading every family."""
    import ai_trader.strategy_runtime.families  # noqa: F401


def build_runtime_handles(
    strategy_manager: "StrategyManager", symbols: frozenset[str], only_ids: frozenset[str] | None = None,
) -> tuple[RuntimeStrategyHandle, ...]:
    """Real handles for every currently-active strategy THAT ALSO has a registered evaluator. Order
    is Strategy Manager's own ``active_strategies()`` order (already deterministic there).
    ``only_ids`` (default ``None``: no filtering, current behavior unchanged) restricts the result to
    those specific strategy ids -- generically useful for isolating one strategy's own behavior
    (e.g. a per-strategy conformance test) from the rest of the shared, ever-growing active set,
    never a strategy-specific carve-out in this module's own logic."""
    _ensure_families_imported()
    handles: list[RuntimeStrategyHandle] = []
    for handle in strategy_manager.active_strategies():
        if only_ids is not None and handle.id not in only_ids:
            continue
        evaluator_cls = _FAMILY_EVALUATORS.get(handle.id)
        if evaluator_cls is None:
            continue
        evaluator = evaluator_cls(handle.id, handle.contract, symbols)
        handles.append(RuntimeStrategyHandle(id=handle.id, contract=handle.contract, api=evaluator))
    return tuple(handles)
