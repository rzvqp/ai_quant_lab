"""Shadow Evidence engine -- Checkpoint 1B's read-only pipeline tap (risk-eligibility only) plus
Checkpoint 1C's full virtual position lifecycle (``PHASE_6_10_SHADOW_EVIDENCE_ARCHITECTURE_DESIGN.md``
§4/§5/§6/§7/§9/§10/§10.1). For every strategy named in ``ShadowConfig.shadow_strategies``, observes the
ALREADY-COMPUTED ``OpportunityScore`` batch the real competitive pipeline produces each bar (tapped,
never re-invoked -- Signal Engine and Scoring Engine are called EXACTLY ONCE per bar by
:class:`~ai_trader.simulation.harness.SimulationHarness`, unchanged) and runs a DEDICATED, per-strategy
:class:`~ai_trader.risk_manager.engine.RiskManager` against that strategy's OWN shadow
:class:`~ai_trader.simulation.portfolio_simulator.PortfolioSimulator` projection. On ALLOW, the
opportunity is submitted through that strategy's OWN dedicated, fully independent
:class:`~ai_trader.execution_engine.engine.ExecutionEngine`/
:class:`~ai_trader.simulation.execution_simulator.ExecutionSimulator`/
:class:`~ai_trader.simulation.portfolio_simulator.PortfolioSimulator` -- fresh instances per strategy,
never shared with the real competitive path or with any other shadow strategy (Design §17.1, findings
H1/H2/H3: ``RiskManager``/``ExecutionEngine`` both carry per-instance state that must never leak).

Never touches: the real ``RiskManager``/``PortfolioState``, the real ``ExecutionEngine``/
``ExecutionSimulator``/``PortfolioSimulator``, or any ``RuntimeEvaluator``/strategy-handle object
directly -- only the immutable ``OpportunityScore`` output the real pipeline already produced, plus
(for the time-stop/trailing-stop overlays) the already-computed, generic ``time_stop_bars``/
``trailing_stop_atr_mult`` lookup dictionaries the harness builds once per bar from the SAME
``overlay_handles`` it already uses for the real portfolio's own overlays (Design §4's "Time-stop"/
"Trailing-stop" rows).

Generic over the configured strategy set from day one: nothing in this module names a specific
strategy id anywhere. ``shadow_strategies=("S10",)`` and
``shadow_strategies=("S10", "S21", "S39", "S40")`` are handled by the exact same code, unchanged.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import dataclass, field

from ai_trader.execution_engine.config import ExecConfig
from ai_trader.execution_engine.engine import ExecutionEngine
from ai_trader.execution_engine.types import BrokerCapabilities, OrderState
from ai_trader.market_scanner.types import SymbolMeta
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.engine import RiskManager
from ai_trader.risk_manager.types import Decision, RiskContext
from ai_trader.scoring_engine.types import OpportunityScore, Recommendation, ScoreBatch
from ai_trader.shadow_evidence import aggregation
from ai_trader.shadow_evidence.types import (
    ShadowObservationResult,
    ShadowOpportunityRecord,
    ShadowPositionRecord,
    ShadowRejectionRecord,
    ShadowStrategySummary,
    ShadowTradeLegRecord,
)
from ai_trader.signal_engine.types import Direction, SignalState
from ai_trader.simulation.config import SimulationContext
from ai_trader.simulation.execution_simulator import ExecutionSimulator
from ai_trader.simulation.portfolio_simulator import PortfolioSimulator, TradeRecord
from ai_trader.simulation.time_stop import build_time_stop_decision, positions_due_for_time_stop
from ai_trader.simulation.trailing_stop import build_trailing_stop_decision, positions_due_for_trailing_stop
from ai_trader.simulation.types import Bar, CloseAtEndPolicy, SimFillEvent
from ai_trader.strategy_runtime import context_access
from ai_trader.strategy_runtime.context_access import MarketContext

logger = logging.getLogger(__name__)

#: Design §10 invariant 4 / §17.1 finding H3's required defense-in-depth: every shadow-generated
#: client_order_id/order_request_id carries an explicit discriminator prefix that can never collide
#: with the real harness's own ``ExecutionEngine(ExecConfig())`` default ("CID"/"REQ") -- even a wiring
#: bug could never silently merge a real and a shadow order under one id. Pure configuration, not a
#: new code path: the SAME frozen ``ExecutionEngine``/builder logic reused unmodified.
_SHADOW_EXEC_CONFIG = ExecConfig(client_order_id_prefix="SHADOW-CID", order_request_id_prefix="SHADOW-REQ")

#: Terminal order states that mean "resolved, and no quantity of this order was ever filled" -- the
#: honest counterpart to a fill actually materializing (query_status is part of the same public
#: BrokerAdapter contract every other caller already uses, not new logic).
_TERMINAL_NO_FILL_STATES = frozenset({OrderState.CANCELLED, OrderState.REJECTED, OrderState.EXPIRED})


def _exit_reason_for(client_order_id: str) -> str:
    """Determine the mechanism that closed a shadow leg DIRECTLY from the client_order_id marker this
    engine itself constructed (never inferred from ambiguous production data, unlike the pre-scope
    diagnostic's own necessary post-hoc heuristic, Design §9): OCO bracket children are suffixed
    ``-TP``/``-SL`` by ``ExecutionSimulator._activate_bracket_children`` (unmodified); time-stop/
    trailing-stop decisions carry a ``TIMESTOP-``/``TRAILSTOP-`` marker from
    ``ai_trader.simulation.time_stop``/``trailing_stop`` (unmodified); this engine's own end-of-window
    forced close carries a ``CLOSE-AT-END-`` marker (mirroring
    ``SimulationHarness._finalize_at_end``'s own real-portfolio convention). No strategy id or symbol
    in this project ever contains any of these markers, so each check is unambiguous by construction."""
    if client_order_id.endswith("-TP"):
        return "TAKE_PROFIT"
    if client_order_id.endswith("-SL"):
        return "STOP_LOSS"
    if "TIMESTOP-" in client_order_id:
        return "TIME_STOP"
    if "TRAILSTOP-" in client_order_id:
        return "TRAILING_STOP"
    if "CLOSE-AT-END-" in client_order_id:
        return "FORCED_CLOSE_AT_WINDOW_END"
    return "UNKNOWN"  # pragma: no cover -- defensive only; every shadow-closing mechanism this engine
    # constructs tags its own client_order_id with one of the markers above, so this is unreachable.


@dataclass(frozen=True, slots=True)
class _PendingEntry:
    """One virtual entry order submitted this bar (or an earlier bar), awaiting fill resolution.
    ``ShadowPositionRecord.entry_price`` cannot be known before a real fill exists -- exactly mirroring
    how ``PortfolioSimulator`` itself never creates a ``Position`` until ``_apply_one`` sees an actual
    fill (``portfolio_simulator.py`` line ~174) -- so the corresponding ``ShadowOpportunityRecord`` is
    held here, unpublished, until ``ShadowEvidenceEngine._settle_one`` resolves it one way or the
    other (filled -> a position; terminal-without-fill -> ``resulting_position_id=None``)."""

    opportunity_id: str
    position_id: str
    client_order_id: str
    symbol: str
    as_of: int
    direction: Direction
    signal_state: SignalState
    score_recommendation: Recommendation


@dataclass(slots=True)
class _ShadowAccount:
    """One strategy's fully independent shadow execution stack -- fresh, dedicated instances of every
    frozen production component this design reuses unmodified (Design §2.B/§4/§10). Never shared with
    the real competitive path or with any other shadow strategy."""

    risk_manager: RiskManager
    execution_engine: ExecutionEngine
    execution_simulator: ExecutionSimulator
    portfolio_simulator: PortfolioSimulator
    pending_entries: dict[str, _PendingEntry] = field(default_factory=dict)  # keyed by symbol
    open_position_id: dict[str, str] = field(default_factory=dict)  # keyed by symbol
    trailing_entry_atr: dict[str, float] = field(default_factory=dict)  # keyed by symbol


class ShadowEvidenceEngine:
    """One instance per simulation run, constructed only when
    :meth:`~ai_trader.shadow_evidence.config.ShadowConfig.active_strategy_ids` is non-empty. Holds one
    dedicated, fully independent shadow execution stack per configured strategy -- never shared with
    the real competitive path, never shared across shadow strategies (Design §17.1, findings H1/H3:
    ``RiskManager``/``ExecutionEngine`` both carry per-instance state that must never leak between
    strategies or into the real competitive instances)."""

    def __init__(
        self,
        shadow_strategy_ids: frozenset[str],
        risk_config: RiskConfig,
        context: SimulationContext,
        symbol_meta: dict[str, SymbolMeta],
        capabilities: BrokerCapabilities,
    ) -> None:
        self._shadow_strategy_ids = shadow_strategy_ids
        self._risk_config = risk_config
        self._context = context
        self._symbol_meta = symbol_meta
        self._capabilities = capabilities
        self._accounts: dict[str, _ShadowAccount] = {}
        self._degraded_strategy_ids: set[str] = set()
        self._positions: dict[str, ShadowPositionRecord] = {}
        self.opportunities: list[ShadowOpportunityRecord] = []
        self.rejections: list[ShadowRejectionRecord] = []
        self.trade_legs: list[ShadowTradeLegRecord] = []
        self.failures: list[tuple[int, str, str]] = []  # (as_of, strategy_id, repr(exception))

    @property
    def positions(self) -> tuple[ShadowPositionRecord, ...]:
        """Every shadow position ever opened (OPEN or CLOSED), in first-opened order -- the current,
        possibly-updated record for each ``position_id`` (Design §17.1 Q4's own formal invariant:
        aggregation fields are derived from legs, never the reverse)."""
        return tuple(self._positions.values())

    # ------------------------------------------------------------------ per-strategy lifecycle introspection (Checkpoint 2)

    @property
    def configured_strategy_ids(self) -> frozenset[str]:
        """Every strategy_id this engine was configured to shadow-track, regardless of whether it has
        produced any evidence yet or has since degraded -- the same set passed to ``__init__``."""
        return self._shadow_strategy_ids

    @property
    def degraded_strategy_ids(self) -> frozenset[str]:
        """Every strategy_id that has been degraded by a failure (Design §10.1) -- permanently, for
        the remainder of this run. A read-only snapshot; never mutated by the caller."""
        return frozenset(self._degraded_strategy_ids)

    @property
    def active_strategy_ids(self) -> frozenset[str]:
        """Configured strategies that have NOT degraded -- the set still eligible to accumulate
        evidence on a future bar. Purely a set difference, no new state."""
        return self._shadow_strategy_ids - self._degraded_strategy_ids

    def summaries(self, window: str, as_of: int) -> dict[str, ShadowStrategySummary]:
        """Every currently-tracked strategy's own aggregated shadow statistics for one rolling window
        ending at ``as_of`` (Checkpoint 2's own "generic aggregation layer" requirement) -- a thin,
        read-only pass-through to :mod:`ai_trader.shadow_evidence.aggregation`'s own pure functions;
        this method holds no computation of its own and never affects any decision this engine makes,
        during this call or any future bar. Safe to call at any point during or after a run."""
        return aggregation.all_summaries(window, as_of, self.opportunities, self.rejections, self.trade_legs)

    # ------------------------------------------------------------------ lazy per-strategy construction

    def _account_for(self, strategy_id: str, as_of: int) -> _ShadowAccount:
        account = self._accounts.get(strategy_id)
        if account is None:
            portfolio_simulator = PortfolioSimulator(self._context, self._symbol_meta)
            execution_simulator = ExecutionSimulator(self._context, self._capabilities)
            execution_simulator.set_free_margin_provider(
                lambda: portfolio_simulator.account.equity - portfolio_simulator.account.used_margin
            )
            execution_engine = ExecutionEngine(_SHADOW_EXEC_CONFIG)
            execution_engine.configure(execution_simulator)
            risk_manager = RiskManager(self._risk_config)
            risk_manager.configure(portfolio=portfolio_simulator.to_portfolio_state(as_of))
            account = _ShadowAccount(
                risk_manager=risk_manager, execution_engine=execution_engine,
                execution_simulator=execution_simulator, portfolio_simulator=portfolio_simulator,
            )
            self._accounts[strategy_id] = account
        return account

    # ------------------------------------------------------------------ per-bar, per-symbol tap (risk + virtual entry)

    def observe(
        self, as_of: int, score_batch: ScoreBatch, risk_context: RiskContext,
    ) -> tuple[ShadowObservationResult, ...]:
        """Called once per bar, per symbol, from ``SimulationHarness._run_one_bar`` -- strictly AFTER
        the real Risk Manager has already evaluated the real, shared ``score_batch`` (Design §10,
        invariant 1: the real decision is never read, touched, or influenced by this call). Never
        raises: a failure evaluating one shadow strategy this bar degrades that ONE strategy only
        (Design §10.1) and is recorded in ``self.failures`` -- every other shadow strategy, and the
        real competitive path, are entirely unaffected.

        **Sprint 2, Blocker 1** (``LEARNING_FEEDBACK_NEXT_SPRINT_DESIGN.md``, Option A, CEO-ratified):
        returns one :class:`~ai_trader.shadow_evidence.types.ShadowObservationResult` per genuine Risk
        Manager decision made this call (both ALLOW and DENY) -- purely additive to this method's own
        prior behavior (every existing side effect on ``self.opportunities``/``self.rejections``/
        ``self._accounts``/pending-entry bookkeeping is byte-for-byte unchanged). This package still
        imports nothing from ``ai_trader.learning_feedback`` -- the caller alone decides what, if
        anything, to do with the returned tuple."""
        results: list[ShadowObservationResult] = []
        for score in score_batch.scores:
            strategy_id = score.strategy_id
            if strategy_id not in self._shadow_strategy_ids or strategy_id in self._degraded_strategy_ids:
                continue
            try:
                result = self._observe_one(as_of, score, risk_context)
                if result is not None:
                    results.append(result)
            except Exception as exc:  # noqa: BLE001 -- failure isolation (Design §10.1): a shadow
                # strategy's own failure must never propagate into or alter competitive execution.
                self._degrade(strategy_id, as_of, exc)
        return tuple(results)

    def _observe_one(
        self, as_of: int, score: OpportunityScore, risk_context: RiskContext,
    ) -> ShadowObservationResult | None:
        strategy_id = score.strategy_id
        account = self._account_for(strategy_id, as_of)
        # Design §17.1 finding H1 correction: the shadow risk evaluation now reflects THIS strategy's
        # own, real, evolving shadow portfolio (not an always-empty one) -- once a shadow position is
        # open, LIMIT_MAX_PER_SYMBOL correctly denies a same-strategy same-symbol re-entry, exactly
        # mirroring the isolated-slot precedent (Design §8).
        portfolio_state = account.portfolio_simulator.to_portfolio_state(as_of)
        decision_batch = account.risk_manager.evaluate([score], risk_context, portfolio_state)
        assert len(decision_batch.decisions) == 1, "one shadow opportunity in, exactly one decision out"
        decision = decision_batch.decisions[0]

        shadow_decision = "ALLOW" if decision.decision is Decision.ALLOW else "DENY"
        denied_reason = decision.denied_reasons[0].code if decision.denied_reasons else None
        opportunity_id = f"{strategy_id}:{score.symbol}:{as_of}"

        if shadow_decision == "DENY":
            self.opportunities.append(ShadowOpportunityRecord(
                opportunity_id=opportunity_id, strategy_id=strategy_id, symbol=score.symbol, as_of=as_of,
                direction=score.direction, signal_state=score.state,
                score_recommendation=score.recommendation, shadow_risk_decision="DENY",
                shadow_denied_reason=denied_reason, resulting_position_id=None,
            ))
            self.rejections.append(ShadowRejectionRecord(
                rejection_id=f"{opportunity_id}:REJ", strategy_id=strategy_id, symbol=score.symbol,
                as_of=as_of, direction=score.direction, denied_reason_code=denied_reason or "UNSPECIFIED",
                denied_detail=decision.denied_reasons[0].detail if decision.denied_reasons else None,
            ))
            return ShadowObservationResult(
                strategy_id=strategy_id, symbol=score.symbol, decision=decision, position_id=None,
            )

        if score.symbol in account.pending_entries:
            # Genuine bug found at Checkpoint 3's own 43-strategy validation scale (not visible at
            # N<=4): a strategy's own entry decision can be a LIMIT-priced BRACKET order (whenever its
            # signal carries an explicit `entry` price -- `execution_engine/builder.py`'s own
            # OrderTypeMappingPolicy), which can stay WORKING for many bars before it fills or expires.
            # `LIMIT_MAX_PER_SYMBOL` only sees OPEN positions (`portfolio_state.open_positions`), never
            # pending orders -- so a SECOND ALLOW for the same symbol can legitimately be produced by
            # the SAME dedicated RiskManager while the first entry is still unresolved. The real
            # competitive/production `PortfolioSimulator` handles this fine on its own (a same-
            # direction second fill simply scale-in's into the SAME `Position` via weighted averaging,
            # `portfolio_simulator.py`'s own frozen `_apply_one`) -- but THIS engine's own
            # `position_id`-per-virtual-entry bookkeeping (Design §5) assumes exactly one in-flight
            # entry per symbol at a time, and would corrupt (`account.pending_entries[symbol]`
            # silently overwritten, orphaning the first order's own eventual fill) if a second entry
            # order were submitted here. Never submitted: an honest, shadow-internal denial, not a
            # genuine RiskManager decision -- the underlying RiskManager DID say ALLOW, disclosed via
            # `shadow_denied_reason` rather than silently dropped.
            self.opportunities.append(ShadowOpportunityRecord(
                opportunity_id=opportunity_id, strategy_id=strategy_id, symbol=score.symbol, as_of=as_of,
                direction=score.direction, signal_state=score.state,
                score_recommendation=score.recommendation, shadow_risk_decision="DENY",
                shadow_denied_reason="SHADOW_ENTRY_ALREADY_PENDING", resulting_position_id=None,
            ))
            self.rejections.append(ShadowRejectionRecord(
                rejection_id=f"{opportunity_id}:REJ", strategy_id=strategy_id, symbol=score.symbol,
                as_of=as_of, direction=score.direction,
                denied_reason_code="SHADOW_ENTRY_ALREADY_PENDING",
                denied_detail=f"a prior entry for {score.symbol} is still pending resolution",
            ))
            # Sprint 2 Blocker 1: no ShadowObservationResult here -- this is a shadow-internal
            # bookkeeping veto, not a genuine Risk Manager decision boundary (the underlying decision
            # DID say ALLOW; see ShadowObservationResult's own docstring). Already fully recorded above
            # via ShadowOpportunityRecord/ShadowRejectionRecord; deliberately out of scope for Learning
            # Feedback capture.
            return None

        # ALLOW: submit the virtual entry through THIS strategy's own dedicated, fully separate
        # ExecutionEngine (Design §4/§10 invariant 4) -- never the real one, never another strategy's.
        # The ShadowOpportunityRecord/ShadowPositionRecord for this entry are DEFERRED to
        # ``_settle_one`` once the fill (or its absence) is confirmed on a later bar -- entry_price
        # (ShadowPositionRecord's own required field) cannot be known before a real fill exists.
        status = account.execution_engine.execute(decision, portfolio_state)
        if decision.constraints is not None:
            account.portfolio_simulator.register_stop_hint(status.client_order_id, decision.constraints.stop)
        # Design §5's own recommended deterministic scheme, including run_id -- reproducible across
        # identical replays of the SAME run_id/config (the determinism law, SimulationContext's own
        # docstring), never a random UUID.
        position_id = f"{self._context.run_id}:{strategy_id}:{score.symbol}:{as_of}:{decision.decision_id}"
        account.pending_entries[score.symbol] = _PendingEntry(
            opportunity_id=opportunity_id, position_id=position_id, client_order_id=status.client_order_id,
            symbol=score.symbol, as_of=as_of, direction=score.direction, signal_state=score.state,
            score_recommendation=score.recommendation,
        )
        return ShadowObservationResult(
            strategy_id=strategy_id, symbol=score.symbol, decision=decision, position_id=position_id,
        )

    # ------------------------------------------------------------------ per-bar overlays (time-stop / trailing-stop)

    def apply_time_stops(self, as_of: int, bar_index: int, time_stop_bars_by_strategy: Mapping[str, int]) -> None:
        """Applies each shadow-tracked strategy's OWN declared time-stop horizon to ITS OWN shadow
        positions -- the identical, unmodified mechanism (``ai_trader.simulation.time_stop``) the real
        competitive portfolio already uses, called once per shadow instance instead of once for the
        real portfolio (Design §4's "Time-stop" row). ``time_stop_bars_by_strategy`` is the SAME
        dictionary the harness already computes once per bar from ``overlay_handles`` for the real
        portfolio's own overlay -- reused, not recomputed."""
        for strategy_id in list(self._accounts):
            if strategy_id in self._degraded_strategy_ids:
                continue
            limit = time_stop_bars_by_strategy.get(strategy_id)
            if limit is None:
                continue
            try:
                self._apply_time_stop_one(strategy_id, as_of, bar_index, limit)
            except Exception as exc:  # noqa: BLE001 -- failure isolation (Design §10.1).
                self._degrade(strategy_id, as_of, exc)

    def _apply_time_stop_one(self, strategy_id: str, as_of: int, bar_index: int, limit: int) -> None:
        account = self._accounts[strategy_id]
        due = positions_due_for_time_stop(
            account.portfolio_simulator.account.positions, bar_index, {strategy_id: limit},
        )
        if not due:
            return
        portfolio_state = account.portfolio_simulator.to_portfolio_state(as_of)
        for position in due:
            decision = build_time_stop_decision(position, as_of, bar_index, account.risk_manager, self._risk_config)
            account.execution_engine.execute(decision, portfolio_state)

    def apply_trailing_stops(
        self, as_of: int, bars: dict[str, Bar], context_batch: Mapping[str, MarketContext],
        atr_mult_by_strategy: Mapping[str, float],
    ) -> None:
        """Applies each shadow-tracked strategy's OWN declared trailing-stop distance to ITS OWN shadow
        positions -- identical mechanism to the real portfolio's own overlay (Design §4's "Trailing-
        stop" row), including the same entry-bar-ATR-capture convention, tracked PER SHADOW ACCOUNT
        (Design §10, invariant 3's own "must not read/write the real harness's own state" requirement).
        ``atr_mult_by_strategy``/``context_batch`` are the SAME values the harness already computes/
        holds once per bar for the real portfolio's own overlay -- reused, not recomputed."""
        for strategy_id in list(self._accounts):
            if strategy_id in self._degraded_strategy_ids:
                continue
            atr_mult = atr_mult_by_strategy.get(strategy_id)
            if atr_mult is None:
                continue
            try:
                self._apply_trailing_stop_one(strategy_id, as_of, bars, context_batch, atr_mult)
            except Exception as exc:  # noqa: BLE001 -- failure isolation (Design §10.1).
                self._degrade(strategy_id, as_of, exc)

    def _apply_trailing_stop_one(
        self, strategy_id: str, as_of: int, bars: dict[str, Bar], context_batch: Mapping[str, MarketContext],
        atr_mult: float,
    ) -> None:
        account = self._accounts[strategy_id]
        positions = account.portfolio_simulator.account.positions
        for symbol, pos in positions.items():
            if symbol not in account.trailing_entry_atr:
                ctx = context_batch.get(symbol)
                atr = context_access.feature(ctx, "m_atr") if ctx is not None else None
                if atr is not None and atr > 0:
                    account.trailing_entry_atr[symbol] = atr
        due = positions_due_for_trailing_stop(positions, bars, account.trailing_entry_atr, {strategy_id: atr_mult})
        if not due:
            return
        portfolio_state = account.portfolio_simulator.to_portfolio_state(as_of)
        for position in due:
            decision = build_trailing_stop_decision(position, as_of, account.risk_manager, self._risk_config)
            account.execution_engine.execute(decision, portfolio_state)

    # ------------------------------------------------------------------ per-bar settlement (fills, positions, legs)

    def settle_bar(self, as_of: int, bar_index: int, bars: dict[str, Bar], phase_running: bool) -> None:
        """Called once per bar, AFTER the real ``execution_simulator.advance_bar``/
        ``portfolio_simulator.apply``/``mark_to_market`` sequence (Design §4's "Virtual close" row) --
        runs the identical sequence for every constructed shadow account, resolves any pending virtual
        entries, and records every closing/partial-exit leg. Never raises: a failure settling one
        shadow strategy this bar degrades that ONE strategy only (Design §10.1)."""
        for strategy_id in list(self._accounts):
            if strategy_id in self._degraded_strategy_ids:
                continue
            try:
                self._settle_one(strategy_id, as_of, bar_index, bars, phase_running)
            except Exception as exc:  # noqa: BLE001 -- failure isolation (Design §10.1).
                self._degrade(strategy_id, as_of, exc)

    def _settle_one(
        self, strategy_id: str, as_of: int, bar_index: int, bars: dict[str, Bar], phase_running: bool,
    ) -> None:
        account = self._accounts[strategy_id]
        prior_symbols_open = set(account.portfolio_simulator.account.positions)
        prior_ledger_len = len(account.portfolio_simulator.account.trade_ledger)

        fills = account.execution_simulator.advance_bar(as_of, bars)
        account.portfolio_simulator.apply(fills, bar_index)
        account.execution_engine.reconcile()
        account.portfolio_simulator.mark_to_market(as_of, bars, phase_running=phase_running)

        self._resolve_pending_entries(strategy_id, account, prior_symbols_open)
        self._record_new_trade_legs(strategy_id, account, prior_ledger_len)

        for symbol in list(account.trailing_entry_atr):
            if symbol not in account.portfolio_simulator.account.positions:
                del account.trailing_entry_atr[symbol]

    def _resolve_pending_entries(self, strategy_id: str, account: _ShadowAccount, prior_symbols_open: set[str]) -> None:
        now_open = set(account.portfolio_simulator.account.positions)
        newly_opened = now_open - prior_symbols_open
        for symbol in list(account.pending_entries):
            pending = account.pending_entries[symbol]
            if symbol in newly_opened:
                pos = account.portfolio_simulator.account.positions[symbol]
                self.opportunities.append(ShadowOpportunityRecord(
                    opportunity_id=pending.opportunity_id, strategy_id=strategy_id, symbol=symbol,
                    as_of=pending.as_of, direction=pending.direction, signal_state=pending.signal_state,
                    score_recommendation=pending.score_recommendation, shadow_risk_decision="ALLOW",
                    shadow_denied_reason=None, resulting_position_id=pending.position_id,
                ))
                self._positions[pending.position_id] = ShadowPositionRecord(
                    position_id=pending.position_id, strategy_id=strategy_id, symbol=symbol,
                    direction=pos.direction, entry_as_of=pos.opened_as_of, entry_price=pos.avg_entry,
                    entry_opportunity_id=pending.opportunity_id, status="OPEN", full_exit_as_of=None,
                    n_legs=0, aggregate_net_pnl=None, aggregate_holding_bars_full=None,
                )
                account.open_position_id[symbol] = pending.position_id
                del account.pending_entries[symbol]
                continue
            status = account.execution_simulator.query_status(pending.client_order_id)
            if status is not None and status.state in _TERMINAL_NO_FILL_STATES and status.filled_qty <= 0.0:
                # The virtual entry never filled (e.g. a genuine INSUFFICIENT_MARGIN/QTY_OUT_OF_BOUNDS
                # rejection) -- an honest ALLOW-with-no-resulting-position, never fabricated.
                self.opportunities.append(ShadowOpportunityRecord(
                    opportunity_id=pending.opportunity_id, strategy_id=strategy_id, symbol=symbol,
                    as_of=pending.as_of, direction=pending.direction, signal_state=pending.signal_state,
                    score_recommendation=pending.score_recommendation, shadow_risk_decision="ALLOW",
                    shadow_denied_reason=None, resulting_position_id=None,
                ))
                del account.pending_entries[symbol]
            # else: genuinely still pending (no data this cycle / still working) -- resolved on a later bar.

    def _record_new_trade_legs(self, strategy_id: str, account: _ShadowAccount, prior_ledger_len: int) -> None:
        new_trades: list[TradeRecord] = account.portfolio_simulator.account.trade_ledger[prior_ledger_len:]
        for trade in new_trades:
            position_id = account.open_position_id.get(trade.symbol)
            if position_id is None:  # pragma: no cover -- defensive only; a closing fill implies a
                # position this engine itself opened and is tracking, which cannot happen otherwise by
                # construction. Fail loud via the per-strategy failure boundary rather than silently
                # fabricating a position_id, should this invariant ever somehow be violated.
                raise RuntimeError(
                    f"Shadow Evidence: closing TradeRecord for {strategy_id}/{trade.symbol} with no "
                    f"tracked open position_id (client_order_id={trade.client_order_id!r})"
                )
            exit_reason = _exit_reason_for(trade.client_order_id)
            self.trade_legs.append(ShadowTradeLegRecord(leg=trade, position_id=position_id, exit_reason=exit_reason))
            prior = self._positions[position_id]
            still_open = trade.symbol in account.portfolio_simulator.account.positions
            self._positions[position_id] = ShadowPositionRecord(
                position_id=position_id, strategy_id=prior.strategy_id, symbol=prior.symbol,
                direction=prior.direction, entry_as_of=prior.entry_as_of, entry_price=prior.entry_price,
                entry_opportunity_id=prior.entry_opportunity_id,
                status="OPEN" if still_open else "CLOSED",
                full_exit_as_of=None if still_open else trade.exit_as_of,
                n_legs=prior.n_legs + 1,
                aggregate_net_pnl=(prior.aggregate_net_pnl or 0.0) + trade.net_pnl,
                aggregate_holding_bars_full=None if still_open else trade.holding_bars,
            )
            if not still_open:
                del account.open_position_id[trade.symbol]

    # ------------------------------------------------------------------ end of run

    def finalize_at_end(self, as_of: int, bar_index: int, bars: dict[str, Bar]) -> None:
        """Mirrors ``SimulationHarness._finalize_at_end`` for every shadow account, per the SAME
        ``context.close_at_end_policy`` the real portfolio already follows -- a still-open shadow
        position at the end of the window is closed with a synthetic, 0-cost accounting mark, never
        silently left open and invisible to the shadow trade ledger. Also flushes any shadow entry
        still genuinely pending at the very last bar as an honest, unresolved ALLOW (no position ever
        materialized in the configured window)."""
        if self._context.close_at_end_policy is not CloseAtEndPolicy.CLOSE_AT_LAST:
            return
        for strategy_id in list(self._accounts):
            if strategy_id in self._degraded_strategy_ids:
                continue
            try:
                self._finalize_one(strategy_id, as_of, bar_index, bars)
            except Exception as exc:  # noqa: BLE001 -- failure isolation (Design §10.1).
                self._degrade(strategy_id, as_of, exc)

    def _finalize_one(self, strategy_id: str, as_of: int, bar_index: int, bars: dict[str, Bar]) -> None:
        account = self._accounts[strategy_id]
        if account.portfolio_simulator.account.positions:
            fills = []
            for symbol, pos in sorted(account.portfolio_simulator.account.positions.items()):
                bar = bars.get(symbol)
                price = bar.close if bar is not None else pos.avg_entry
                close_direction = Direction.SHORT if pos.direction is Direction.LONG else Direction.LONG
                fills.append(SimFillEvent(
                    client_order_id=f"SHADOW-CLOSE-AT-END-{strategy_id}-{symbol}",
                    order_request_id=f"SHADOW-CLOSE-AT-END-{strategy_id}-{symbol}",
                    strategy_id=strategy_id, symbol=symbol, direction=close_direction, intent_close=True,
                    qty=pos.size, price=price, spread_cost=0.0, slippage_cost=0.0, commission=0.0,
                    as_of=as_of, reduce_only=True,
                ))
            prior_ledger_len = len(account.portfolio_simulator.account.trade_ledger)
            account.portfolio_simulator.apply(tuple(fills), bar_index)
            self._record_new_trade_legs(strategy_id, account, prior_ledger_len)

        # Any entry still genuinely pending at the very last bar never got the chance to resolve on a
        # later settle_bar() call -- flush it now as an honest, unresolved ALLOW.
        for symbol in list(account.pending_entries):
            pending = account.pending_entries.pop(symbol)
            self.opportunities.append(ShadowOpportunityRecord(
                opportunity_id=pending.opportunity_id, strategy_id=strategy_id, symbol=symbol,
                as_of=pending.as_of, direction=pending.direction, signal_state=pending.signal_state,
                score_recommendation=pending.score_recommendation, shadow_risk_decision="ALLOW",
                shadow_denied_reason=None, resulting_position_id=None,
            ))

    # ------------------------------------------------------------------ internals

    def _degrade(self, strategy_id: str, as_of: int, exc: Exception) -> None:
        self._degraded_strategy_ids.add(strategy_id)
        self.failures.append((as_of, strategy_id, repr(exc)))
        logger.warning("Shadow Evidence: strategy %s degraded after error: %r", strategy_id, exc)
