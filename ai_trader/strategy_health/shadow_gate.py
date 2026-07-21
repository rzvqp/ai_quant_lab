"""Strategy Health Integration -- the Eligibility Policy layer (roadmap Flow B step 1/6,
``STRATEGY_HEALTH_INTEGRATION_POLICY_DESIGN.md``, CEO-ACCEPTED WITH CONDITIONS, clarified §§11-15).

A thin, pure wrapper around :func:`ai_trader.strategy_health.evaluator.evaluate_strategy_health` --
adding NO new scoring logic, mirroring :mod:`ai_trader.strategy_health.rolling_gate`'s own established
pattern exactly (same convention this project already used for Phase 6.9's rolling gate). The ONE
difference from ``rolling_gate``: trades are sourced from **Shadow Evidence** (every strategy's own
continuously-running virtual execution, `ai_trader.shadow_evidence.engine.ShadowEvidenceEngine
.trade_legs`) instead of the real competitive ledger -- this is the design's own central fix for why
Phase 6.9's rolling gate produced an absorbing lockout (`PROJECT_STATE_v2.md` §8.21 §3): competitive
trades are scarce and shared-slot-contested, so gating real-trade eligibility BY competitive evidence
made the evidence source and the eligibility gate the same resource. Shadow Evidence is tracked for
every configured strategy unconditionally, regardless of its current eligibility state (never gated by
`ai_trader.simulation.harness.SimulationHarness`'s own ``health_eligible_ids`` -- see that module's own
``__init__`` docstring for the precise mechanism that keeps the two independent), so this module's own
input never runs dry the way Phase 6.9's did.

Frozen modules consumed, never modified: ``evaluator.py``/``types.py``/``metrics.py``/``scoring.py``/
``classifier.py``. This module adds exactly one thing the frozen classifier does not itself have: a
fifth, policy-layer-only state, ``NEW`` (§11 of the design doc), for strategies with too little
Shadow-sourced evidence to trust ANY of the frozen classifier's own four bands yet -- distinguished
here, never inside the frozen classifier itself, and never changing what that classifier computes.
"""

from __future__ import annotations

from collections.abc import Sequence
from enum import Enum

from ai_trader.shadow_evidence.types import ShadowTradeLegRecord
from ai_trader.strategy_health.evaluator import evaluate_strategy_health
from ai_trader.strategy_health.types import ClosedTrade, HealthState, StrategyHealthReport, from_trade_record

#: Reused, not invented -- the same minimum-trade-count floor this project's own `code/alpha_lab.py`
#: (`MINTR=25`) already established and Context Memory's own Checkpoint 13 evidence-sufficiency policy
#: already reused verbatim (`PROJECT_AUDIT.md` cross-reference note, 2026-07-20). A strategy with fewer
#: than this many Shadow-sourced trades in its ENTIRE accumulated ledger (not just the current 12m
#: window -- "has this strategy ever produced enough evidence to trust at all" is a lifetime question,
#: not a rolling-window one) is classified ``NEW`` regardless of what the frozen classifier's own
#: shrinkage-adjusted band happens to say about that thin a sample.
MIN_EVIDENCE_TRADES = 25


class PolicyState(str, Enum):
    """The five-state lifecycle the CEO's own mandatory architecture specifies verbatim (design doc
    §11): ``NEW`` is a policy-layer label only -- it is never emitted by the frozen
    :class:`~ai_trader.strategy_health.types.HealthState` classifier, which has exactly four members.
    Every ``NEW`` strategy would otherwise classify as ``HealthState.WATCHLIST`` (the classifier's own
    safe zero-evidence default); this module additionally requires :data:`MIN_EVIDENCE_TRADES` before
    trusting that -- or any other -- band."""

    NEW = "NEW"
    ACTIVE = "ACTIVE"
    WATCHLIST = "WATCHLIST"
    PROBATION = "PROBATION"
    DISABLED = "DISABLED"


#: The only two states permitted real-competitive-portfolio eligibility (design doc §12, CEO's own
#: mandatory architecture): ACTIVE and WATCHLIST behave identically here -- full eligibility, unchanged
#: from today's system for every non-demoted strategy. PROBATION, DISABLED, and NEW are all
#: Shadow-only.
_REAL_ELIGIBLE_STATES = frozenset({PolicyState.ACTIVE, PolicyState.WATCHLIST})


def shadow_closed_trades_by_strategy(
    trade_legs: Sequence[ShadowTradeLegRecord], strategy_ids: frozenset[str],
) -> dict[str, list[ClosedTrade]]:
    """Group + adapt Shadow Evidence's own raw trade-leg ledger into the
    ``Mapping[str, Sequence[ClosedTrade]]`` shape :func:`~ai_trader.strategy_health.evaluator.
    evaluate_strategy_health` requires -- the exact one-line adaptation
    :func:`ai_trader.shadow_evidence.aggregation.summary_for` already uses
    (``from_trade_record(leg.leg)``), reused here rather than reinvented. Every id in ``strategy_ids``
    is present in the result, defaulting to an empty list, so every configured strategy gets a report
    even before its first Shadow trade closes (the ``NEW`` case) -- callers should pass the FULL
    configured Shadow roster (e.g. ``harness.context.shadow_config.active_strategy_ids()`` or
    :func:`ai_trader.shadow_evidence.config.all_registered_strategies`), not just the ids that happen
    to already have trades."""
    by_strategy: dict[str, list[ClosedTrade]] = {sid: [] for sid in strategy_ids}
    for record in trade_legs:
        sid = record.leg.strategy_id
        if sid not in by_strategy:
            continue  # a leg for a strategy outside the caller's own declared roster -- ignored, not
            # silently added, so the roster the caller declared is exactly the roster reported on.
        by_strategy[sid].append(from_trade_record(record.leg))
    return by_strategy


def shadow_health_reports_at(
    trade_legs: Sequence[ShadowTradeLegRecord], as_of: int, strategy_ids: frozenset[str],
) -> dict[str, StrategyHealthReport]:
    """Every strategy id's full :class:`~ai_trader.strategy_health.types.StrategyHealthReport` at
    ``as_of``, computed from Shadow Evidence's own trade ledger only -- never the competitive one
    (that remains available, completely unmodified, via
    :func:`ai_trader.strategy_health.rolling_gate.health_reports_at` for anyone who wants the
    competitive-evidence-sourced report for audit/reference; the two are never blended into one number
    by this module or any other)."""
    trades_by_strategy = shadow_closed_trades_by_strategy(trade_legs, strategy_ids)
    return evaluate_strategy_health(trades_by_strategy, as_of)


def classify_policy_state(report: StrategyHealthReport, n_shadow_trades: int) -> PolicyState:
    """Map one strategy's frozen :class:`~ai_trader.strategy_health.types.HealthState` classification
    onto the five-state policy lifecycle: below :data:`MIN_EVIDENCE_TRADES` lifetime Shadow trades,
    always ``NEW`` -- regardless of what band the frozen classifier's own shrinkage happened to land
    on for that thin a sample (a defensive floor, not merely a WATCHLIST-only override: Bühlmann
    shrinkage pulls small-``n`` scores toward 50, which lands in WATCHLIST's own band in the common
    case, but this floor does not depend on that being true in every case). At or above the floor, the
    frozen classification is trusted as-is, one-to-one."""
    if n_shadow_trades < MIN_EVIDENCE_TRADES:
        return PolicyState.NEW
    return PolicyState(report.state.value)


def policy_states_at(
    trade_legs: Sequence[ShadowTradeLegRecord], as_of: int, strategy_ids: frozenset[str],
) -> dict[str, PolicyState]:
    """Every configured strategy's current :class:`PolicyState`, for reporting/testing -- the full
    5-way classification, not just the real-eligible subset (see :func:`real_eligible_strategy_ids_at`
    for that)."""
    trades_by_strategy = shadow_closed_trades_by_strategy(trade_legs, strategy_ids)
    reports = evaluate_strategy_health(trades_by_strategy, as_of)
    return {
        sid: classify_policy_state(report, len(trades_by_strategy.get(sid, ())))
        for sid, report in reports.items()
    }


def real_eligible_strategy_ids_at(
    trade_legs: Sequence[ShadowTradeLegRecord], as_of: int, strategy_ids: frozenset[str],
) -> frozenset[str]:
    """The roster to pass as :class:`~ai_trader.simulation.harness.SimulationHarness`'s own
    ``health_eligible_ids`` for the period following ``as_of`` -- every strategy currently classified
    ``ACTIVE`` or ``WATCHLIST`` (design doc §12: both retain full real-competitive-portfolio
    eligibility, identical to today's unfiltered behavior; ``NEW``/``PROBATION``/``DISABLED`` are all
    Shadow-only). Recomputing this at a later ``as_of`` with a longer ``trade_legs`` history is the
    ENTIRE recovery mechanism (design doc §14) -- there is no separate "recovery" code path, because
    Shadow Evidence keeps accumulating genuinely new trades for every strategy regardless of its
    current membership in this returned set, so a later call over more evidence can only ever reflect
    real, new performance, never a timer or evidence expiring out of a window."""
    states = policy_states_at(trade_legs, as_of, strategy_ids)
    return frozenset(sid for sid, state in states.items() if state in _REAL_ELIGIBLE_STATES)
