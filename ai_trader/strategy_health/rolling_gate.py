"""Phase 6.9 -- the Rolling Health Gate: a thin, pure wrapper around
:func:`ai_trader.strategy_health.evaluator.evaluate_strategy_health`, adding NO new scoring logic
(CEO directive, ``ROLLING_HEALTH_BACKTEST_HANDOFF.md`` §8.4: "the Strategy Health System's own
scoring methodology is CONSUMED as-is"). Given the trade ledger accumulated up to a checkpoint and
that checkpoint's own ``as_of``, returns which strategy ids are currently ``ACTIVE`` -- the only state
permitted to open a NEW position (``ai_trader.strategy_health.types.HealthState`` docstring).

The caller (the rolling-gate orchestrator) is responsible for only ever passing trades already closed
strictly before the checkpoint being evaluated -- calling this at the checkpoint moment, before any
bar of the new period has been simulated, naturally guarantees that (``evaluate_strategy_health``'s
own window math is inclusive of ``as_of`` itself, per its frozen, unmodified semantics; this module
does not alter that convention)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from ai_trader.strategy_health.evaluator import evaluate_strategy_health
from ai_trader.strategy_health.types import ClosedTrade, HealthState, StrategyHealthReport


def health_reports_at(
    trades_by_strategy: Mapping[str, Sequence[ClosedTrade]], as_of: int,
) -> dict[str, StrategyHealthReport]:
    """Every strategy id's full :class:`StrategyHealthReport` at checkpoint ``as_of`` -- exposed
    alongside :func:`active_strategy_ids_at` so an orchestrator can record promotions/demotions/
    turnover from the SAME evaluation call, never a second, possibly-inconsistent one."""
    return evaluate_strategy_health(trades_by_strategy, as_of)


def active_strategy_ids_at(
    trades_by_strategy: Mapping[str, Sequence[ClosedTrade]], as_of: int,
) -> frozenset[str]:
    """The ``ACTIVE``-classified strategy id subset at checkpoint ``as_of`` -- the roster a
    :class:`~ai_trader.simulation.harness.SimulationHarness` should pass as its ``strategy_id_filter``
    for the period following ``as_of``, up to the next checkpoint."""
    reports = health_reports_at(trades_by_strategy, as_of)
    return frozenset(sid for sid, report in reports.items() if report.state is HealthState.ACTIVE)
