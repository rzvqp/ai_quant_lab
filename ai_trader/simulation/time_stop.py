"""Generic, deterministic time-based position exit ("time-stop") overlay for the Simulation
Framework (Phase 6.8 Wave B).

**Why this exists**: several Strategy Library families' own evidence-backed ``executable_default``
select the frozen research engine's ``exit=time`` grammar option (``code/mstrat.py``'s own
``_exitmap``: ``exit_kind=='time' -> 24`` bars, read only, never imported) -- a fixed-bar-count
forced exit, independent of price. No such mechanism existed anywhere in the AI Trader runtime
before this module (confirmed by reading ``STRATEGY_API_v1.md``'s ``Signal`` schema and
``execution_simulator.py``'s order-conflict resolution: only STOP/LIMIT(target) orders existed).

**Design (CEO-approved, 2026-07-15)**: NO new execution path, NO frozen-module edit. A time-stop is
expressed as an ordinary, synthetic, reduce-only ``RiskDecision`` -- the exact same shape every real
opportunity produces -- submitted through :meth:`ai_trader.execution_engine.engine.ExecutionEngine.
execute`, the SAME single gateway every other order in the system already uses. The frozen Order
Builder (``execution_engine/builder.py::build_order``) already fully supports
``constraints.reduce_only=True`` (``_side_for``/``_intent_for`` already flip side and resolve
``OrderIntent.CLOSE`` against the matching open position) -- no new order-construction logic, no
``emergency_flatten`` reuse (which would permanently latch the engine's lifecycle state and block
every other strategy's future entries -- a real regression this module deliberately avoids).

**Generic & reusable**: this module has NO strategy-specific code. A strategy opts in purely by
setting ``RuntimeEvaluator.time_stop_bars`` (see ``strategy_runtime/evaluator.py``); any current or
future strategy that sets it is honored identically. Strategies that never set it (the default,
``None``) are completely unaffected -- their positions are only ever closed by their own stop/target,
exactly as before this module existed.
"""

from __future__ import annotations

from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.types import (
    AppliedRule,
    Constraints,
    Decision,
    EngineState,
    RiskDecision,
    RiskRefs,
    Sizing,
    SizingMethod,
)
from ai_trader.risk_manager.engine import RiskManager
from ai_trader.scoring_engine.config import SCORING_SCHEMA_VERSION
from ai_trader.simulation.portfolio_simulator import Position
from ai_trader.strategy_runtime.migration import INTERFACE_VERSION


def positions_due_for_time_stop(
    positions: dict[str, Position], bar_index: int, time_stop_bars_by_strategy: dict[str, int],
) -> tuple[Position, ...]:
    """Pure function: which open positions have reached their OWN strategy's declared time-stop
    horizon at ``bar_index``. A strategy absent from ``time_stop_bars_by_strategy`` (or explicitly
    mapped to ``None`` by a caller) never matches -- opting into a time-stop is per-strategy and
    additive, never a forced default for strategies that never declared one."""
    due = []
    for pos in positions.values():
        limit = time_stop_bars_by_strategy.get(pos.strategy_id)
        if limit is not None and (bar_index - pos.opened_bar_index) >= limit:
            due.append(pos)
    return tuple(due)


def build_time_stop_decision(
    position: Position, as_of: int, bar_index: int, risk_manager: RiskManager, risk_config: RiskConfig,
) -> RiskDecision:
    """A synthetic, reduce-only ``ALLOW`` decision closing ``position`` in full -- built from the
    exact same :class:`RiskDecision` shape every real opportunity produces, so the frozen,
    unmodified Order Builder requires no new branch to handle it. ``max_slippage`` mirrors
    ``risk_manager.constraints.build_constraints``'s own formula (``entry * max_slippage_pct``) using
    the position's own average entry price as the reference -- the same convention, not a new one."""
    versions = risk_manager.versions()
    max_slippage = position.avg_entry * risk_config.constraints.max_slippage_pct
    decision_id = f"TIMESTOP-{position.strategy_id}-{position.symbol}-{as_of}"
    age_bars = bar_index - position.opened_bar_index
    return RiskDecision(
        risk_schema_version=versions.risk_schema_version,
        risk_engine_version=versions.risk_engine_version,
        risk_policy_version=versions.risk_policy_version,
        decision_id=decision_id,
        score_id="", signal_id="",
        strategy_id=position.strategy_id, symbol=position.symbol,
        timestamp=as_of, as_of=as_of,
        engine_state=EngineState.READY, decision=Decision.ALLOW, direction=position.direction,
        applied_rules=(
            AppliedRule(rule="TIME_STOP", passed=True, detail=f"age_bars={age_bars} >= time_stop_bars"),
        ),
        refs=RiskRefs(
            scoring_schema_version=SCORING_SCHEMA_VERSION, interface_version=INTERFACE_VERSION,
        ),
        sizing=Sizing(
            method=SizingMethod.FIXED_FRACTIONAL, risk_per_trade_pct=0.0, risk_R=0.0,
            size_units=position.size, min_size=position.size, max_size=position.size,
        ),
        constraints=Constraints(reduce_only=True, max_slippage=max_slippage),
    )
