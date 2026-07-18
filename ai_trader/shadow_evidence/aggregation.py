"""Shadow Evidence's generic aggregation layer -- Phase 6.10 Implementation Checkpoint 2. Pure
functions only: given the already-recorded ``ShadowOpportunityRecord``/``ShadowRejectionRecord``/
``ShadowTradeLegRecord`` lists a :class:`~ai_trader.shadow_evidence.engine.ShadowEvidenceEngine`
already exposes, compute one :class:`~ai_trader.shadow_evidence.types.ShadowStrategySummary` per
strategy_id, for any strategy_id observed -- N strategies, zero strategy-specific code anywhere in
this module (verified by the same grep-for-strategy-ids discipline every prior Shadow Evidence
checkpoint has used).

Read-only, by construction: every function here takes immutable/frozen input (the engine's own
public, already-recorded lists) and returns a new value -- nothing in this module ever writes back
to the engine, a shadow account, or any real object. Calling `summaries_for()`/`all_summaries()`
during, after, or never during a run changes nothing about how that run itself executes.

Reuses :mod:`ai_trader.strategy_health.metrics`'s own frozen, unmodified ``compute_window_metrics()``
and :func:`ai_trader.strategy_health.types.from_trade_record` -- no new statistics math. Deliberately
does NOT import :mod:`ai_trader.strategy_health.scoring`/``classifier``/``evaluator`` or reference
``HealthState``/``WindowScore`` anywhere -- statistics (this module) is one lifecycle stage earlier
than health (`PHASE_6_10_EDGE_PORTFOLIO_DIRECTION.md` §5), and only the earlier stage is in scope for
Checkpoint 2 (the CEO's own explicit "no Strategy Health / no Edge Health" instruction).
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence

from ai_trader.shadow_evidence.types import (
    ShadowOpportunityRecord,
    ShadowRejectionRecord,
    ShadowStrategySummary,
    ShadowTradeLegRecord,
)
from ai_trader.strategy_health.metrics import compute_window_metrics
from ai_trader.strategy_health.types import from_trade_record


def strategy_ids_observed(opportunities: Sequence[ShadowOpportunityRecord]) -> frozenset[str]:
    """Every strategy_id that has produced at least one shadow opportunity so far -- derived
    entirely from the data, never from a hardcoded list, so this generalizes to any N."""
    return frozenset(o.strategy_id for o in opportunities)


def summary_for(
    strategy_id: str,
    window: str,
    as_of: int,
    opportunities: Sequence[ShadowOpportunityRecord],
    rejections: Sequence[ShadowRejectionRecord],
    trade_legs: Sequence[ShadowTradeLegRecord],
) -> ShadowStrategySummary:
    """One strategy's ``ShadowStrategySummary`` for one rolling window ending at ``as_of``
    (``window`` is one of ``strategy_health.types.WINDOW_DAYS``'s own keys: ``"3m"``/``"6m"``/
    ``"12m"`` -- the SAME canonical windows Strategy Health already uses, not a new scheme). A
    strategy with zero recorded trades yields a valid, honest summary (``window_metrics.n_trades ==
    0``, every optional metric ``None`` -- `compute_window_metrics`'s own "never fabricated"
    convention, unmodified), never raises."""
    closed_trades = [from_trade_record(leg.leg) for leg in trade_legs if leg.leg.strategy_id == strategy_id]
    window_metrics = compute_window_metrics(closed_trades, window, as_of)
    n_opportunities = sum(1 for o in opportunities if o.strategy_id == strategy_id)
    denied_by_reason = Counter(
        r.denied_reason_code for r in rejections if r.strategy_id == strategy_id
    )
    return ShadowStrategySummary(
        strategy_id=strategy_id, source="shadow", window_metrics=window_metrics,
        n_opportunities=n_opportunities, n_shadow_denied_by_reason=dict(denied_by_reason),
    )


def all_summaries(
    window: str,
    as_of: int,
    opportunities: Sequence[ShadowOpportunityRecord],
    rejections: Sequence[ShadowRejectionRecord],
    trade_legs: Sequence[ShadowTradeLegRecord],
) -> dict[str, ShadowStrategySummary]:
    """Every currently-tracked strategy's own ``ShadowStrategySummary``, keyed by ``strategy_id`` --
    the generic aggregation entry point (Checkpoint 2's own "Generic aggregation layer" requirement).
    The strategy-id set is derived from ``opportunities`` itself (:func:`strategy_ids_observed`), so
    this scales from 1 to N configured strategies with no code change, ever."""
    return {
        strategy_id: summary_for(strategy_id, window, as_of, opportunities, rejections, trade_legs)
        for strategy_id in sorted(strategy_ids_observed(opportunities))
    }
