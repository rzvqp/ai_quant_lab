"""Shadow Evidence read-only pipeline tap -- Phase 6.10 Implementation Checkpoint 1B
(``PHASE_6_10_SHADOW_EVIDENCE_ARCHITECTURE_DESIGN.md`` §4). For every strategy named in
``ShadowConfig.shadow_strategies``, observes the ALREADY-COMPUTED ``OpportunityScore`` batch the real
competitive pipeline produces each bar (tapped, never re-invoked -- Signal Engine and Scoring Engine
are called EXACTLY ONCE per bar by :class:`~ai_trader.simulation.harness.SimulationHarness`, unchanged)
and runs a DEDICATED, per-strategy :class:`~ai_trader.risk_manager.engine.RiskManager` instance against
a structurally empty per-strategy :class:`~ai_trader.risk_manager.types.PortfolioState` -- no virtual
position ever exists in this checkpoint (Checkpoint 1B is read-only evidence collection only, per the
CEO's own explicit scope: no virtual execution/positions/exits).

Never touches: the real ``RiskManager``/``PortfolioState``, the real ``ExecutionEngine``/
``ExecutionSimulator``, or any ``RuntimeEvaluator``/strategy-handle object directly -- only the
immutable ``OpportunityScore`` output the real pipeline already produced.

Generic over the configured strategy set from day one: nothing in this module names a specific
strategy id anywhere. ``shadow_strategies=("S10",)`` and
``shadow_strategies=("S10", "S21", "S39", "S40")`` are handled by the exact same code, unchanged.
"""

from __future__ import annotations

import logging

from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.engine import RiskManager
from ai_trader.risk_manager.types import Decision, PortfolioState, RiskContext
from ai_trader.scoring_engine.types import OpportunityScore, ScoreBatch
from ai_trader.shadow_evidence.types import ShadowOpportunityRecord, ShadowRejectionRecord

logger = logging.getLogger(__name__)


def _empty_portfolio_state(as_of: int, starting_balance: float) -> PortfolioState:
    """A structurally empty per-strategy shadow portfolio. Checkpoint 1B never opens a virtual
    position (out of scope by explicit CEO instruction), so this is the honest, correct account state
    for "a strategy that has never traded" at any bar -- not an approximation. Every ``PortfolioState``
    field beyond ``as_of``/``equity``/``equity_high_water_mark`` already defaults to this same empty
    state (``risk_manager/types.py``: zero open positions, zero recent closed positions, zero realized/
    unrealized PnL, zero consecutive losses, not stale)."""
    return PortfolioState(as_of=as_of, equity=starting_balance, equity_high_water_mark=starting_balance)


class ShadowEvidenceEngine:
    """One instance per simulation run, constructed only when
    :meth:`~ai_trader.shadow_evidence.config.ShadowConfig.active_strategy_ids` is non-empty. Holds one
    dedicated ``RiskManager`` per configured shadow strategy -- never shared with the real, competitive
    ``RiskManager``, never shared across shadow strategies (Design §17.1, finding H1: ``RiskManager``
    carries per-instance lifecycle state, e.g. a SUSPENDED/EMERGENCY_STOP latch, that must never leak
    between strategies or into the real competitive instance)."""

    def __init__(
        self, shadow_strategy_ids: frozenset[str], risk_config: RiskConfig, starting_balance: float,
    ) -> None:
        self._shadow_strategy_ids = shadow_strategy_ids
        self._risk_config = risk_config
        self._starting_balance = starting_balance
        self._risk_managers: dict[str, RiskManager] = {}
        self._degraded_strategy_ids: set[str] = set()
        self.opportunities: list[ShadowOpportunityRecord] = []
        self.rejections: list[ShadowRejectionRecord] = []
        self.failures: list[tuple[int, str, str]] = []  # (as_of, strategy_id, repr(exception))

    def _risk_manager_for(self, strategy_id: str, as_of: int) -> RiskManager:
        risk_manager = self._risk_managers.get(strategy_id)
        if risk_manager is None:
            risk_manager = RiskManager(self._risk_config)
            risk_manager.configure(portfolio=_empty_portfolio_state(as_of, self._starting_balance))
            self._risk_managers[strategy_id] = risk_manager
        return risk_manager

    def observe(self, as_of: int, score_batch: ScoreBatch, risk_context: RiskContext) -> None:
        """Called once per bar, per symbol, from ``SimulationHarness._run_one_bar`` -- strictly AFTER
        the real Risk Manager has already evaluated the real, shared ``score_batch`` (Design §10,
        invariant 1: the real decision is never read, touched, or influenced by this call). Never
        raises: a failure evaluating one shadow strategy this bar degrades that ONE strategy only
        (Design §10.1) and is recorded in ``self.failures`` -- every other shadow strategy, and the
        real competitive path, are entirely unaffected."""
        for score in score_batch.scores:
            strategy_id = score.strategy_id
            if strategy_id not in self._shadow_strategy_ids or strategy_id in self._degraded_strategy_ids:
                continue
            try:
                self._observe_one(as_of, score, risk_context)
            except Exception as exc:  # noqa: BLE001 -- failure isolation (Design §10.1): a shadow
                # strategy's own failure must never propagate into or alter competitive execution.
                self._degraded_strategy_ids.add(strategy_id)
                self.failures.append((as_of, strategy_id, repr(exc)))
                logger.warning("Shadow Evidence: strategy %s degraded after error: %r", strategy_id, exc)

    def _observe_one(self, as_of: int, score: OpportunityScore, risk_context: RiskContext) -> None:
        strategy_id = score.strategy_id
        risk_manager = self._risk_manager_for(strategy_id, as_of)
        empty_portfolio = _empty_portfolio_state(as_of, self._starting_balance)
        decision_batch = risk_manager.evaluate([score], risk_context, empty_portfolio)
        assert len(decision_batch.decisions) == 1, "one shadow opportunity in, exactly one decision out"
        decision = decision_batch.decisions[0]

        shadow_decision = "ALLOW" if decision.decision is Decision.ALLOW else "DENY"
        denied_reason = decision.denied_reasons[0].code if decision.denied_reasons else None
        opportunity_id = f"{strategy_id}:{score.symbol}:{as_of}"

        self.opportunities.append(ShadowOpportunityRecord(
            opportunity_id=opportunity_id, strategy_id=strategy_id, symbol=score.symbol, as_of=as_of,
            direction=score.direction, signal_state=score.state,
            score_recommendation=score.recommendation, shadow_risk_decision=shadow_decision,
            shadow_denied_reason=denied_reason,
            resulting_position_id=None,  # Checkpoint 1B never opens a virtual position (out of scope)
        ))
        if shadow_decision == "DENY":
            self.rejections.append(ShadowRejectionRecord(
                rejection_id=f"{opportunity_id}:REJ", strategy_id=strategy_id, symbol=score.symbol,
                as_of=as_of, direction=score.direction, denied_reason_code=denied_reason or "UNSPECIFIED",
                denied_detail=decision.denied_reasons[0].detail if decision.denied_reasons else None,
            ))
