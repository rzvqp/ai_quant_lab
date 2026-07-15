"""Generic, deterministic trailing-stop overlay for the Simulation Framework (Phase 6.8 Wave B).

**Why this exists**: several Strategy Library families' own evidence-backed ``executable_default``
select the frozen research engine's ``exit=trailing`` grammar option -- a stop that ratchets in the
trade's favor every bar (``code/mstrat.py::simulate``'s own hardcoded, UNIVERSAL formula:
``best=max(best,hi[j])`` for a long; ``ts=best-1.5*atr[si]``; ``stop=max(stop,ts)`` -- the SAME
1.5*ATR-at-entry trailing distance for every family, never a per-strategy tunable). Confirmed there
is no order-amend/modify capability anywhere in the abstract ``BrokerAdapter`` Protocol (only
``submit_order``/``cancel_order``/``query_status``/``query_open_orders``), so this mechanism never
tries to amend a resting order's price.

**Design (CEO-approved, mirrors ai_trader.simulation.time_stop's own precedent exactly)**: NO new
execution path. A trailing-stop breach closes the position via an ordinary, synthetic, reduce-only
``RiskDecision`` submitted through :meth:`ai_trader.execution_engine.engine.ExecutionEngine.execute`
-- the SAME single gateway every other order (and the time-stop mechanism) already uses. The
position's own running best-favorable price is derived from Portfolio Simulator's own
already-tracked MFE (``Position.mfe``, updated every bar from real bar highs/lows in
``mark_to_market``) plus the CURRENT bar's own high/low (computed inline here so this mechanism
never depends on whether ``mark_to_market`` has already run for the current bar) -- no new
``Position`` field needed. The only new state this module owns is each open position's own
entry-bar ATR (the frozen engine's own trailing formula fixes this at signal time, never
re-computed bar to bar); captured once when a tracked position is first observed and retained by
the caller (the harness) for the position's lifetime, using the CURRENT bar's own ``m_atr`` at that
moment as a proxy for "ATR at signal time" -- the same convention every other cross-bar
approximation in this package already uses (e.g. ``s28_anchored_vwap_reaction``'s own anchor).

**Generic & reusable**: this module has NO strategy-specific code. A strategy opts in purely by
setting ``RuntimeEvaluator.trailing_stop_atr_mult`` (see ``strategy_runtime/evaluator.py``); any
current or future strategy that sets it is honored identically. Strategies that never set it (the
default, ``None``) are completely unaffected.
"""

from __future__ import annotations

from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.engine import RiskManager
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
from ai_trader.scoring_engine.config import SCORING_SCHEMA_VERSION
from ai_trader.signal_engine.types import Direction
from ai_trader.simulation.portfolio_simulator import Position
from ai_trader.simulation.types import Bar
from ai_trader.strategy_runtime.migration import INTERFACE_VERSION


def best_favorable_price_including_bar(position: Position, bar_high: float, bar_low: float) -> float:
    """The highest high (LONG) / lowest low (SHORT) reached since entry, INCLUDING the current
    bar -- derived from Portfolio Simulator's own already-tracked MFE (as of the end of the prior
    bar) folded together with this bar's own extreme, so this function never depends on whether
    ``mark_to_market`` has already processed the current bar."""
    if position.direction is Direction.LONG:
        prior_best = position.avg_entry + position.mfe
        return max(prior_best, bar_high)
    prior_best = position.avg_entry - position.mfe
    return min(prior_best, bar_low)


def trailing_stop_level(position: Position, entry_atr: float, atr_mult: float, bar_high: float, bar_low: float) -> float:
    best = best_favorable_price_including_bar(position, bar_high, bar_low)
    if position.direction is Direction.LONG:
        return best - atr_mult * entry_atr
    return best + atr_mult * entry_atr


def positions_due_for_trailing_stop(
    positions: dict[str, Position], bars_by_symbol: dict[str, Bar], entry_atr_by_symbol: dict[str, float],
    atr_mult_by_strategy: dict[str, float],
) -> tuple[Position, ...]:
    """Pure function: which open positions have breached their OWN strategy's trailing-stop level
    this bar. A strategy absent from ``atr_mult_by_strategy`` never matches -- opting in is
    per-strategy and additive. A position whose own entry ATR is not yet tracked (should not
    normally happen -- the caller registers it the same bar the position opens) never matches
    either, fail-safe rather than guessing an ATR."""
    due = []
    for symbol, pos in positions.items():
        atr_mult = atr_mult_by_strategy.get(pos.strategy_id)
        entry_atr = entry_atr_by_symbol.get(symbol)
        bar = bars_by_symbol.get(symbol)
        if atr_mult is None or entry_atr is None or bar is None:
            continue
        level = trailing_stop_level(pos, entry_atr, atr_mult, bar.high, bar.low)
        breached = bar.low <= level if pos.direction is Direction.LONG else bar.high >= level
        if breached:
            due.append(pos)
    return tuple(due)


def build_trailing_stop_decision(
    position: Position, as_of: int, risk_manager: RiskManager, risk_config: RiskConfig,
) -> RiskDecision:
    """A synthetic, reduce-only ``ALLOW`` decision closing ``position`` in full -- identical shape
    to :func:`ai_trader.simulation.time_stop.build_time_stop_decision`, submitted through the same
    ``ExecutionEngine.execute()`` gateway every other order already uses."""
    versions = risk_manager.versions()
    max_slippage = position.avg_entry * risk_config.constraints.max_slippage_pct
    decision_id = f"TRAILSTOP-{position.strategy_id}-{position.symbol}-{as_of}"
    return RiskDecision(
        risk_schema_version=versions.risk_schema_version,
        risk_engine_version=versions.risk_engine_version,
        risk_policy_version=versions.risk_policy_version,
        decision_id=decision_id,
        score_id="", signal_id="",
        strategy_id=position.strategy_id, symbol=position.symbol,
        timestamp=as_of, as_of=as_of,
        engine_state=EngineState.READY, decision=Decision.ALLOW, direction=position.direction,
        applied_rules=(AppliedRule(rule="TRAILING_STOP", passed=True, detail="trailing_stop_level breached"),),
        refs=RiskRefs(
            scoring_schema_version=SCORING_SCHEMA_VERSION, interface_version=INTERFACE_VERSION,
        ),
        sizing=Sizing(
            method=SizingMethod.FIXED_FRACTIONAL, risk_per_trade_pct=0.0, risk_R=0.0,
            size_units=position.size, min_size=position.size, max_size=position.size,
        ),
        constraints=Constraints(reduce_only=True, max_slippage=max_slippage),
    )
