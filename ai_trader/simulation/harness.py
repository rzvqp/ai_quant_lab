"""The Simulation Harness -- the orchestrator (``SIMULATION_ARCHITECTURE.md`` §3): owns the Replay
Clock, drives the per-bar pipeline, collects outputs. Composes the SIX live pipeline modules (Market
Scanner, Strategy Manager, Signal Engine, Scoring Engine, Risk Manager, Execution Engine) **UNCHANGED**
plus the three simulation-only components (Execution Simulator, Portfolio Simulator, Performance
Analyzer) -- ``SIMULATION_SEQUENCE.md`` §2's exact per-bar loop, one call per line, no logic
duplicated from any composed module.

Additionally composes Learning/Research Feedback (Flow B roadmap step 3/6, real-portfolio side --
``LEARNING_FEEDBACK_ARCHITECTURAL_DECISION_PACKAGE.md``, CEO-authorized): opt-in, off by default
(``learning_feedback_repository_path is None``), and strictly read-only/additive with respect to the six
composed modules above and the three simulation-only components -- it captures Market Intelligence/Edge
Intelligence/Context Memory diagnostics into a separate repository, never feeds back into eligibility,
ranking, scoring, sizing, or execution, and every call site is wrapped in the same failure-isolation
pattern already established for the Shadow Evidence tap (a diagnostic-only capture bug can never fail the
real, competitive run).
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from ai_trader.context_memory.enums import OutcomeKind
from ai_trader.context_memory.repository import ContextMemoryRepository
from ai_trader.execution_engine.config import ExecConfig
from ai_trader.execution_engine.engine import ExecutionEngine
from ai_trader.execution_engine.types import BrokerCapabilities, MarketStatus, OrderState, OrderType, TimeInForce
from ai_trader.learning_feedback.adapters import canonical_cost_model_ref
from ai_trader.learning_feedback.capture import (
    CorrelationMap,
    PendingCapture,
    PendingPosition,
    PositionCorrelationMap,
    capture_decision_observation,
    capture_operational_metadata,
    capture_portfolio_interim,
    capture_portfolio_terminal,
    capture_strategy_interim,
    capture_strategy_terminal,
    promote_opening_fill,
    register_flip_position,
    register_pending_correlation,
    register_shadow_position,
)
from ai_trader.learning_feedback.market_snapshot import build_market_snapshot
from ai_trader.learning_feedback.observation_builder import build_decision_observation
from ai_trader.learning_feedback.position_registry import RealPositionRegistry
from ai_trader.market_scanner.config import ScannerConfig
from ai_trader.market_scanner.scanner import AdapterConfig, MarketScanner
from ai_trader.market_scanner.types import DataQualityLevel, Mode, SymbolMeta
from ai_trader.portfolio_architect.architect import PortfolioArchitect
from ai_trader.portfolio_architect.types import ArchitectDiagnostics, PortfolioArchitectConfig
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.engine import RiskManager
from ai_trader.risk_manager.types import Decision, RiskContext, SymbolRiskSnapshot
from ai_trader.scoring_engine.config import ScoringConfig
from ai_trader.scoring_engine.engine import ScoringEngine
from ai_trader.shadow_evidence.engine import ShadowEvidenceEngine
from ai_trader.shadow_evidence.types import ShadowPositionRecord
from ai_trader.signal_engine.config import EngineConfig as SignalEngineConfig
from ai_trader.signal_engine.engine import SignalEngine
from ai_trader.signal_engine.pipeline import StrategyHandleLike
from ai_trader.signal_engine.types import Direction
from ai_trader.simulation.clock import ReplayClock
from ai_trader.simulation.config import SimulationContext
from ai_trader.simulation.data_source import ReplayDataSource
from ai_trader.simulation.exceptions import DataLoadError
from ai_trader.simulation.execution_simulator import ExecutionSimulator
from ai_trader.simulation.portfolio_simulator import PortfolioSimulator, TradeRecord
from ai_trader.simulation.time_stop import build_time_stop_decision, positions_due_for_time_stop
from ai_trader.simulation.trailing_stop import build_trailing_stop_decision, positions_due_for_trailing_stop
from ai_trader.simulation.types import TERMINAL_RUN_STATES, CloseAtEndPolicy, RunState, SimFillEvent, SimPhase
from ai_trader.strategy_manager.config import ManagerConfig
from ai_trader.strategy_manager.manager import StrategyManager
from ai_trader.strategy_runtime import context_access

logger = logging.getLogger(__name__)


def _build_capabilities(context: SimulationContext, symbol_meta: dict[str, SymbolMeta]) -> BrokerCapabilities:
    tick_size = next(iter(symbol_meta.values())).tick_size if symbol_meta else 0.01
    return BrokerCapabilities(
        supported_order_types=frozenset({
            OrderType.MARKET, OrderType.LIMIT, OrderType.STOP, OrderType.STOP_LIMIT,
            OrderType.BRACKET, OrderType.OCO,
        }),
        supported_time_in_force=frozenset({TimeInForce.IOC, TimeInForce.FOK, TimeInForce.GTC, TimeInForce.DAY}),
        tick_size=tick_size, lot_step=0.01, min_qty=0.01, max_qty=1_000_000.0,
        market_status={s: MarketStatus.OPEN for s in context.symbols},
    )


class SimulationHarness:
    """One run's orchestrator. Not thread-safe/not reusable across runs -- one instance per
    ``SimulationContext`` (``SIMULATION_CONTEXT.md``: a change to any field is a NEW run)."""

    def __init__(
        self, context: SimulationContext, symbol_meta: dict[str, SymbolMeta], data_dir: Path,
        manager_config: ManagerConfig | None = None, use_strategy_runtime: bool = False,
        risk_config: RiskConfig | None = None, enable_time_stops: bool = False,
        enable_trailing_stops: bool = False, strategy_id_filter: frozenset[str] | None = None,
        health_eligible_ids: frozenset[str] | None = None,
        portfolio_architect_config: PortfolioArchitectConfig | None = None,
        learning_feedback_repository_path: Path | None = None,
        learning_feedback_library_path: Path | None = None,
    ) -> None:
        """``manager_config``/``use_strategy_runtime``/``risk_config`` default to Phase 6.7's own
        original, verified-fail-safe behavior (a bare ``ManagerConfig()``/``RiskConfig()`` with no
        auto-admission and no per-symbol filter thresholds, real evaluators never consulted) -- all
        are opt-in, additive Phase 6.8 capabilities. Passing ``use_strategy_runtime=True`` swaps
        ``active_strategies()`` for ``ai_trader.strategy_runtime.registry.build_runtime_handles()``
        when building the handles Signal Engine evaluates; it does not change anything else about how
        the six live pipeline modules are composed. ``risk_config`` should set
        ``filters.reference_spread``/``filters.liquidity_floor`` for every configured symbol --
        Risk Manager's own fail-safe default denies every opportunity for a symbol with no configured
        threshold (``filters.py``: "cannot confirm safe, never assume safe"), so leaving this at the
        bare default with real strategies active means every decision DENYs on FILTER_SPREAD/
        FILTER_LIQUIDITY, not a bug in this module. ``enable_time_stops=True`` additionally enforces
        each active strategy's own ``RuntimeEvaluator.time_stop_bars`` (see
        ``ai_trader.simulation.time_stop``); only meaningful alongside ``use_strategy_runtime=True``
        (default ``False``: Phase 6.7's original behavior, no strategy has ever declared a time-stop
        before Phase 6.8 Wave B, unchanged). ``enable_trailing_stops=True`` additionally enforces
        each active strategy's own ``RuntimeEvaluator.trailing_stop_atr_mult`` (see
        ``ai_trader.simulation.trailing_stop``); only meaningful alongside
        ``use_strategy_runtime=True`` (default ``False``, unchanged). ``strategy_id_filter``
        (default ``None``: no filtering,
        every active strategy participates, unchanged) restricts real evaluation to specific
        strategy ids -- generically useful for isolating one strategy's own behavior from the rest
        of the shared, ever-growing active set (e.g. a per-strategy conformance test), never a
        strategy-specific mechanism in this module's own logic. ``health_eligible_ids`` (default
        ``None``: no filtering, unchanged) is a SEPARATE, additive gate for Strategy Health
        integration (``ai_trader.strategy_health.shadow_gate``) -- deliberately NOT the same knob as
        ``strategy_id_filter``, because that one gates which strategies ``build_runtime_handles()``
        even asks the Signal Engine to evaluate, which would ALSO starve ``shadow_engine`` (Shadow
        Evidence only ever taps the already-computed ``score_batch`` below, never re-scores
        independently) -- reusing it for Health eligibility would silently recreate Phase 6.9's own
        absorbing-lockout failure (the evidence source and the eligibility gate becoming the same
        gated resource). ``health_eligible_ids``, in contrast, filters only the opportunity list
        handed to the Risk Manager, strictly AFTER Signal/Scoring Engine and the Shadow Evidence tap
        have both already run unfiltered -- see the per-bar loop below. Like
        ``strategy_id_filter``, this is a plain mutable attribute a caller may reassign between
        ``step()`` calls to implement a periodic re-evaluation cadence (mirroring the one proven
        precedent for this pattern, ``phase69_rolling_backtest.py``). ``portfolio_architect_config``
        (default ``None``: Portfolio Architect is not invoked at all, stronger than a
        ``PASSTHROUGH``-mode call -- no function call is made when disabled, matching
        ``health_eligible_ids``'s own ``is None`` short-circuit) wires in
        ``ai_trader.portfolio_architect.architect.PortfolioArchitect`` (roadmap Flow B step 2/6, Phase 1:
        PASSTHROUGH scaffold only -- CEO authorization, ``PORTFOLIO_ARCHITECT_DESIGN.md``). Placed in
        the per-bar loop strictly AFTER the ``health_eligible_ids`` filter and strictly BEFORE
        ``risk_manager.evaluate()`` -- the mandatory placement the CEO's own authorization specifies. In
        PASSTHROUGH mode it is a proven no-op: the sequence handed to Risk Manager is byte-identical to
        what it would have received with Portfolio Architect disabled.

        **Shadow Evidence tap reordering, disclosed**: the CEO's own mandatory placement additionally
        requires Portfolio Architect to run "after Shadow Evidence has observed the full score batch"
        (i.e. Shadow's own tap must execute before the ``health_eligible_ids`` filter, before Portfolio
        Architect, and before ``risk_manager.evaluate()``). Prior to this change the Shadow Evidence tap
        ran strictly AFTER ``risk_manager.evaluate()`` (Phase 6.10 Checkpoint 1B's own original
        placement). This change moves the tap call earlier in the per-bar sequence, to immediately after
        ``score_batch``/``risk_context`` are computed. This reordering is provably behavior-preserving:
        ``shadow_engine.observe(as_of, score_batch, risk_context)`` is a pure function of three
        already-fully-materialized, immutable values that nothing between the old and new call sites
        mutates (``score_batch``/``risk_context`` are frozen dataclasses; ``risk_manager.evaluate()``
        returns a new ``RiskDecisionBatch`` without touching its own inputs) -- so WHAT Shadow observes,
        and its own resulting state, is identical regardless of exactly when within the bar the call
        happens. Only the wall-clock/textual call order changes, which no test observes (every existing
        test asserts post-conditions on ``shadow_engine``'s own accumulated state, never the literal
        order of calls within one bar). Proven directly by ``test_shadow_disabled_parity.py``'s own
        28-test suite (including the 43-production-strategy byte-identical run) passing unmodified after
        this reordering, and by a dedicated new regression test in
        ``test_portfolio_architect_passthrough.py``.

        ``learning_feedback_repository_path`` (default ``None``: Learning/Research Feedback is
        completely inert this run, unchanged from every prior phase's own unwired state -- Flow B
        roadmap step 3/6, Architectural Decision Package, CEO-authorized implementation). When set, a
        :class:`~ai_trader.context_memory.repository.ContextMemoryRepository` is opened at this path and
        every REAL-portfolio decision/fill this run produces is captured into it, per the Architectural
        Decision Package's own recommended design: Decision 4 (Option C) builds a real, non-degraded
        Observation from Market Intelligence/Edge Intelligence once per symbol per bar; Decision 1
        (Option D) tracks real position identity via a read-only, bar-level diff of
        ``portfolio_simulator.account.positions`` (never re-deriving its own open/scale/reduce/flip
        bookkeeping); Decision 2 handles a flip as one atomic close-old/open-new event; Decision 3
        produces exactly one terminal ``Outcome`` per position lifecycle plus a separate,
        diagnostic-only ``InterimRealization`` for every partial exit that does not zero the position,
        never both, never neither. **Shadow Evidence (``OutcomeKind.STRATEGY``) is NOT wired by this
        parameter** -- ``ShadowEvidenceEngine.observe()`` returns nothing and exposes no per-strategy
        decision-time state, so this harness has no way to capture a Shadow strategy's own Observation/
        OperationalMetadata at decision time without either modifying ``shadow_evidence/engine.py``
        (crossing its own ownership boundary) or duplicating its internal Risk Manager logic here -- a
        genuine architectural blocker reported to, not silently resolved by, this implementation.
        ``learning_feedback_library_path`` (default ``None``: the real Strategy Library's own default
        path) is passed straight through to Market Intelligence/Edge Intelligence's own contract loading,
        exactly mirroring ``context.strategy_library_path``'s own existing role for the Strategy Manager
        above -- a SEPARATE parameter because Edge Intelligence's own contract loader
        (``ai_trader.edge_intelligence.contracts.load_strategy_contracts``) takes its own path argument,
        independent of ``StrategyManager``'s own library loading. Every Learning Feedback call in this
        module is wrapped in the SAME failure-isolation pattern already established for the Shadow
        Evidence tap above -- a diagnostic-only capture failure can never fail the real, competitive
        run."""
        self.context = context
        self._symbol_meta = symbol_meta
        self._data_dir = data_dir
        self._manager_config = manager_config or ManagerConfig()
        self._use_strategy_runtime = use_strategy_runtime
        self._risk_config = risk_config or RiskConfig()
        self._enable_time_stops = enable_time_stops
        self._enable_trailing_stops = enable_trailing_stops
        self._strategy_id_filter = strategy_id_filter
        self._health_eligible_ids = health_eligible_ids
        self._portfolio_architect_config = portfolio_architect_config
        #: Stateless (no configure() step) -- constructed once regardless of whether it is ever
        #: invoked; cheap, and avoids a per-bar allocation.
        self._portfolio_architect = PortfolioArchitect()
        #: Diagnostics-only, last-bar snapshot -- never read by this class to make any decision (design
        #: doc §5/§10: "diagnostics must not influence the harness"). Exposed purely for test/audit
        #: visibility. ``None`` until Portfolio Architect has been invoked at least once.
        self.last_portfolio_architect_diagnostics: ArchitectDiagnostics | None = None
        self._trailing_entry_atr: dict[str, float] = {}  # keyed by symbol (one position per symbol)
        self.state = RunState.UNINITIALIZED
        self.fail_reason: str | None = None
        self.degraded_reasons: list[str] = []
        self.bars_processed = 0
        self.orders_submitted = 0
        self.fills_total = 0

        self._clock: ReplayClock | None = None
        self._data_source: ReplayDataSource | None = None
        self._scanner: MarketScanner | None = None
        self._strategy_manager: StrategyManager | None = None
        self._signal_engine: SignalEngine | None = None
        self._scoring_engine: ScoringEngine | None = None
        self._risk_manager: RiskManager | None = None
        self._execution_engine: ExecutionEngine | None = None
        self.execution_simulator: ExecutionSimulator | None = None
        self.portfolio_simulator: PortfolioSimulator | None = None
        #: Phase 6.10 Implementation Checkpoint 1B (``PHASE_6_10_SHADOW_EVIDENCE_ARCHITECTURE_DESIGN.
        #: md``): constructed in ``load()`` only when ``context.shadow_config.active_strategy_ids()``
        #: is non-empty. ``None`` (the default) means Shadow Mode is fully inert this run -- unchanged
        #: from Checkpoint 1A's own guarantee.
        self.shadow_engine: ShadowEvidenceEngine | None = None

        #: Learning/Research Feedback (Flow B roadmap step 3/6, Architectural Decision Package) --
        #: real-portfolio side only (see this constructor's own docstring for the Shadow-side gap).
        #: `None` (the default) means Learning Feedback is fully inert this run, unchanged from every
        #: prior phase's own unwired state.
        self._lf_library_path = learning_feedback_library_path
        self._lf_repo: ContextMemoryRepository | None = None
        self._lf_correlation: CorrelationMap | None = None
        self._lf_positions: PositionCorrelationMap | None = None
        self._lf_registry: RealPositionRegistry | None = None
        self._lf_cost_model_ref: str | None = None
        if learning_feedback_repository_path is not None:
            self._lf_repo = ContextMemoryRepository(learning_feedback_repository_path)
            self._lf_correlation = CorrelationMap(context.run_id)
            self._lf_positions = PositionCorrelationMap(context.run_id)
            self._lf_registry = RealPositionRegistry(context.run_id)
            self._lf_cost_model_ref = canonical_cost_model_ref(context.cost_model)

    # ------------------------------------------------------------------ read-only clock introspection

    @property
    def as_of(self) -> int | None:
        return self._clock.as_of if self._clock is not None else None

    @property
    def bar_index(self) -> int:
        return self._clock.bar_index if self._clock is not None else -1

    @property
    def phase(self) -> SimPhase | None:
        return self._clock.phase if self._clock is not None else None

    @property
    def total_ticks(self) -> int:
        return self._clock.total_ticks if self._clock is not None else 0

    def composed_module_versions(self) -> dict[str, str]:
        """The composed pipeline's own version strings, echoed onto every report
        (``SIMULATION_ARCHITECTURE.md`` §10: "a report records the entire pipeline it was produced
        by"). Empty before ``load()`` has composed the modules."""
        versions: dict[str, str] = {}
        if self._scanner is not None:
            versions["market_scanner"] = self._scanner.versions().scanner_version
        if self._strategy_manager is not None:
            versions["strategy_manager"] = self._strategy_manager.versions().manager_version
        if self._signal_engine is not None:
            versions["signal_engine"] = self._signal_engine.versions().signal_engine_version
        if self._scoring_engine is not None:
            versions["scoring_engine"] = self._scoring_engine.versions().scoring_engine_version
        if self._risk_manager is not None:
            versions["risk_manager"] = self._risk_manager.versions().risk_engine_version
        if self._execution_engine is not None:
            versions["execution_engine"] = self._execution_engine.versions().execution_engine_version
        return versions

    # ------------------------------------------------------------------ 1. configure / load

    def configure(self) -> None:
        if set(self._symbol_meta) != set(self.context.symbols):
            self._fail("INVALID_CONTEXT: symbol_meta must cover exactly SimulationContext.symbols")
            return
        self.state = RunState.CONFIGURED

    def load(self) -> None:
        if self.state is not RunState.CONFIGURED:
            self._fail("INVALID_SEQUENCE: load() called before configure()")
            return
        self.state = RunState.LOADING
        try:
            self._data_source = ReplayDataSource(
                self.context.symbols, self.context.timeframes, self.context.base_timeframe, self._data_dir,
            )
            ticks = self._data_source.base_ticks_in_range(
                self.context.date_range.start, self.context.date_range.end, self.context.warmup_bars,
            )
            if not ticks:
                raise DataLoadError("no base-timeframe bars found in the configured date range")
            warmup_ticks = sum(1 for t in ticks if t < self.context.date_range.start)

            self._scanner = MarketScanner(ScannerConfig(base_timeframe=self.context.base_timeframe))
            self._scanner.configure(list(self._symbol_meta.values()), AdapterConfig(mode=Mode.REPLAY, source_id="replay"))

            self._strategy_manager = StrategyManager(self._manager_config)
            self._strategy_manager.configure(self._scanner)
            self._strategy_manager.load_library(as_of=ticks[0], path=self.context.strategy_library_path)

            self._signal_engine = SignalEngine(SignalEngineConfig())
            self._signal_engine.configure()
            self._scoring_engine = ScoringEngine(ScoringConfig())
            self._scoring_engine.configure(manager=self._strategy_manager)
            self._risk_manager = RiskManager(self._risk_config)
            self._execution_engine = ExecutionEngine(ExecConfig())

            caps = _build_capabilities(self.context, self._symbol_meta)
            self.execution_simulator = ExecutionSimulator(self.context, caps)
            self._execution_engine.configure(self.execution_simulator)
            self.portfolio_simulator = PortfolioSimulator(self.context, self._symbol_meta)
            self.execution_simulator.set_free_margin_provider(
                lambda: self.portfolio_simulator.account.equity - self.portfolio_simulator.account.used_margin
                if self.portfolio_simulator is not None else 0.0
            )
            self._risk_manager.configure(portfolio=self.portfolio_simulator.to_portfolio_state(ticks[0]))

            active_shadow_ids = self.context.shadow_config.active_strategy_ids()
            if active_shadow_ids:
                # Checkpoint 1C: the shadow engine now constructs its own fully independent
                # ExecutionEngine/ExecutionSimulator/PortfolioSimulator per strategy (Design §4/§10),
                # so it needs the same context/symbol_meta/capabilities the real stack above was just
                # built from -- shared by reference (all three are read-only/immutable configuration,
                # never mutated after construction, the same sharing precedent §10 invariant 3 already
                # established for RiskConfig).
                self.shadow_engine = ShadowEvidenceEngine(
                    active_shadow_ids, self._risk_config, self.context, self._symbol_meta, caps,
                )

            self._clock = ReplayClock(all_ticks=ticks, warmup_ticks=warmup_ticks)
        except Exception as exc:  # noqa: BLE001 -- configure/load errors fail-fast to FAILED before
            # any bar is processed (SIMULATION_API.md §1/§9), never left half-initialized.
            self._fail(f"LOAD_FAILED: {exc}")
            return
        self.state = RunState.WARMUP

    def _fail(self, reason: str) -> None:
        self.fail_reason = reason
        self.state = RunState.FAILED
        logger.error("SimulationHarness: %s", reason)

    # ------------------------------------------------------------------ 2. running

    def step(self) -> bool:
        """Advance exactly one base bar. Returns ``False`` once the replay is exhausted (the caller
        should then finalize), ``True`` otherwise. A no-op (returns ``False``) if not RUNNING/WARMUP."""
        if self.state not in (RunState.WARMUP, RunState.RUNNING):
            return False
        assert self._clock is not None
        as_of = self._clock.tick()
        if as_of is None:
            self._finalize_at_end()
            self.state = RunState.COMPLETED
            return False
        try:
            self._run_one_bar(as_of)
        except Exception as exc:  # noqa: BLE001 -- a real gap a review caught: RUNNING had no
            # exception safety net at all (unlike configure/load), so ANY unexpected exception from a
            # composed module or this harness's own bar loop would crash the whole process instead of
            # producing a deterministic partial report (SIMULATION_API.md §4.5, SIMULATION_STATE_MACHINE.md
            # §C.4: "no run ends in an undefined state").
            self._fail(f"RUN_FAILED: unexpected exception during bar as_of={as_of}: {exc}")
            return False
        self.bars_processed += 1
        if self.state is RunState.WARMUP and self._clock.phase is SimPhase.RUNNING:
            self.state = RunState.RUNNING
        if self.portfolio_simulator is not None and self.portfolio_simulator.account.liquidation_halted:
            self._fail("LIQUIDATION_HALT: margin_model.halt_on_liquidation triggered")
            return False
        return True

    def run_to_completion(self) -> None:
        while self.step():
            pass

    def stop_now(self) -> None:
        """Stop a run early (``SIMULATION_API.md`` §2: "finalizes the report at the current as_of per
        close_at_end_policy"). The single place ``SimulationAPI.stop()`` calls -- a real gap a review
        caught: the API used to set ``state = STOPPED`` directly, bypassing ``close_at_end_policy``
        entirely (open positions were silently left open, contradicting the documented "close/mark
        open positions per config" end-of-run contract every OTHER completion path already followed)."""
        if self.state not in TERMINAL_RUN_STATES:
            self._finalize_at_end()
            self.state = RunState.STOPPED

    def _finalize_at_end(self) -> None:
        """Apply ``close_at_end_policy`` (``SIMULATION_CONTEXT.md`` §A.6) at end-of-run
        (``SIMULATION_ARCHITECTURE.md`` §8, ``SIMULATION_SEQUENCE.md`` §6, ``SIMULATION_STATE_MACHINE.md``
        transition R6): ``CLOSE_AT_LAST`` synthesizes a reduce-only closing fill for every still-open
        position at the last known bar's close (0 cost -- an accounting mark, not a real market fill);
        ``HOLD_AND_MARK`` leaves positions open (already what happens if this is skipped). A real gap a
        review caught: this was never called anywhere, so a run could complete with open positions
        whose PnL counted in ``equity``/``net_profit`` but was invisible to ``trade_ledger``-derived
        stats (win_rate/profit_factor/attribution) -- an internal inconsistency within the same report.
        """
        if self.portfolio_simulator is None or self._data_source is None:
            return
        if self.context.close_at_end_policy is not CloseAtEndPolicy.CLOSE_AT_LAST:
            if self._lf_positions is not None:
                # HOLD_AND_MARK (Architectural Decision Package Decision 3): every real position still
                # open at run end has its own economic fate genuinely unresolved for this run -- drain
                # the pending correlation state, never fabricate a terminal Outcome for it.
                self._lf_positions.drain_pending()
            if self._lf_correlation is not None:
                # Sprint 2 Blocker 3: bound any decision-time candidate that was registered but never
                # promoted to a position_key (cancelled or expired, never surfaced mid-run) to at most
                # one run's own lifetime -- guarantees pending_count() == 0 at the end of every run.
                self._lf_correlation.drain_pending()
            return
        last_as_of = self.as_of
        if last_as_of is None:
            return
        bars = self._data_source.base_bars_at(last_as_of)
        if self.portfolio_simulator.account.positions:
            fills = []
            for symbol, pos in sorted(self.portfolio_simulator.account.positions.items()):
                bar = bars.get(symbol)
                price = bar.close if bar is not None else pos.avg_entry
                close_direction = Direction.SHORT if pos.direction is Direction.LONG else Direction.LONG
                fills.append(SimFillEvent(
                    client_order_id=f"CLOSE-AT-END-{symbol}", order_request_id=f"CLOSE-AT-END-{symbol}",
                    strategy_id=pos.strategy_id, symbol=symbol, direction=close_direction, intent_close=True,
                    qty=pos.size, price=price, spread_cost=0.0, slippage_cost=0.0, commission=0.0,
                    as_of=last_as_of, reduce_only=True,
                ))
            lf_prev_trade_count = (
                len(self.portfolio_simulator.account.trade_ledger) if self._lf_repo is not None else 0
            )
            fill_tuple = tuple(fills)
            self.portfolio_simulator.apply(fill_tuple, self.bar_index)
            if self._lf_repo is not None:
                self._lf_process_fills_for_bar(last_as_of, fill_tuple, lf_prev_trade_count)

        # Checkpoint 1C: a shadow account can hold an open position at window-end even when the real
        # portfolio does not (or vice versa) -- its own finalization runs independently, per the SAME
        # close_at_end_policy (checked again, internally, by ShadowEvidenceEngine.finalize_at_end).
        if self.shadow_engine is not None:
            lf_prev_leg_count = len(self.shadow_engine.trade_legs) if self._lf_repo is not None else 0
            try:
                self.shadow_engine.finalize_at_end(last_as_of, self.bar_index, bars)
            except Exception as exc:  # noqa: BLE001 -- failure isolation: a shadow finalization bug
                # must never affect the real, already-applied competitive close-at-end result above.
                self.shadow_engine.failures.append((last_as_of, "__engine__", repr(exc)))
                logger.warning("Shadow Evidence: finalize_at_end() raised: %r", exc)
            if self._lf_repo is not None:
                self._lf_process_shadow_trade_legs(lf_prev_leg_count)

        # Sprint 2 Blocker 3: under CLOSE_AT_LAST too, any candidate that was registered but never
        # reached a fill this run (cancelled/expired, never surfaced mid-run) must not persist past the
        # end of the run -- same guarantee as the HOLD_AND_MARK branch above.
        if self._lf_correlation is not None:
            self._lf_correlation.drain_pending()

    # ------------------------------------------------------------------ Learning/Research Feedback
    # (Flow B roadmap step 3/6, real-portfolio side -- Architectural Decision Package, CEO-authorized)

    def _lf_capture_terminal(self, position_key: str, trade: TradeRecord) -> None:
        assert self._lf_repo is not None and self._lf_positions is not None
        entry = self._lf_positions.get(position_key)
        if entry is None:
            return
        capture_portfolio_terminal(
            self._lf_repo, self._lf_positions, self.context.run_id, position_key, trade, entry.decision_as_of,
        )

    def _lf_capture_interim(self, position_key: str, trade: TradeRecord) -> None:
        assert self._lf_repo is not None and self._lf_positions is not None
        entry = self._lf_positions.get(position_key)
        if entry is None:
            return
        capture_portfolio_interim(
            self._lf_repo, self._lf_positions, self.context.run_id, position_key, trade, entry.decision_as_of,
        )

    def _lf_capture_shadow_terminal(
        self, position_key: str, position: ShadowPositionRecord, closing_leg: TradeRecord,
    ) -> None:
        assert self._lf_repo is not None and self._lf_positions is not None
        entry = self._lf_positions.get(position_key)
        if entry is None:
            return
        capture_strategy_terminal(
            self._lf_repo, self._lf_positions, self.context.run_id, position_key, position, closing_leg,
            entry.decision_as_of,
        )

    def _lf_capture_shadow_interim(self, position_key: str, closing_leg: TradeRecord) -> None:
        assert self._lf_repo is not None and self._lf_positions is not None
        entry = self._lf_positions.get(position_key)
        if entry is None:
            return
        capture_strategy_interim(
            self._lf_repo, self._lf_positions, self.context.run_id, position_key, closing_leg,
            entry.decision_as_of,
        )

    def _lf_process_shadow_trade_legs(self, prev_leg_count: int) -> None:
        """Learning/Research Feedback resolution-time capture for Shadow Evidence (Sprint 2 Blocker 1)
        -- called after `shadow_engine.settle_bar()`/`finalize_at_end()` has recorded every new closing/
        partial-exit leg for this bar. Shadow already tracks its own stable `position_id` (Lifecycle
        Specification §3B) -- no registry/diff needed here, unlike the real-portfolio side: this simply
        looks up each new leg's own `ShadowPositionRecord` (by `position_id`) to decide terminal (status
        == 'CLOSED') vs interim. Wrapped in its own try/except, mirroring every other Learning Feedback
        call site in this module."""
        assert self._lf_repo is not None and self._lf_positions is not None and self.shadow_engine is not None
        try:
            new_legs = self.shadow_engine.trade_legs[prev_leg_count:]
            if not new_legs:
                return
            positions_by_id = {p.position_id: p for p in self.shadow_engine.positions}
            for leg_record in new_legs:
                position = positions_by_id.get(leg_record.position_id)
                if position is None:
                    continue  # defensive only -- shadow_evidence guarantees this invariant internally
                if position.status == "CLOSED":
                    self._lf_capture_shadow_terminal(leg_record.position_id, position, leg_record.leg)
                else:
                    self._lf_capture_shadow_interim(leg_record.position_id, leg_record.leg)
        except Exception as exc:  # noqa: BLE001 -- failure isolation, see module docstring.
            logger.warning("Learning Feedback: shadow resolution-time capture raised: %r", exc)

    def _lf_process_fills_for_bar(
        self, as_of: int, fills: tuple[SimFillEvent, ...], prev_trade_count: int,
    ) -> None:
        """Learning/Research Feedback resolution-time capture (Architectural Decision Package Decisions
        1-3) -- called after ``portfolio_simulator.apply(fills, ...)`` has fully processed every fill for
        this bar. Diffs ``portfolio_simulator.account.positions`` against the registry's own
        last-observed state (Decision 1, Option D: bar-granularity, never re-deriving Portfolio
        Simulator's own open/scale/reduce/flip bookkeeping), then attributes every NEW ``TradeRecord``
        produced this bar to the correct ``position_key`` -- exactly one terminal Outcome per closed
        lifecycle, an InterimRealization for every partial that does not zero the position (Decision 3),
        and a flip's own compound close-old/open-new handling (Decision 2). Wrapped in its own try/
        except: a Learning Feedback bug here must never affect the real, already-applied competitive
        result (mirrors the Shadow Evidence tap's own failure-isolation convention throughout this
        module)."""
        assert self._lf_repo is not None and self._lf_correlation is not None
        assert self._lf_positions is not None and self._lf_registry is not None
        assert self.portfolio_simulator is not None
        try:
            diff = self._lf_registry.observe(self.portfolio_simulator.account.positions)

            for birth in diff.births:
                # The opening fill for a newly-born position: exactly one non-reduce-only fill for this
                # symbol this bar, in the overwhelmingly common case (Architectural Decision Package
                # Decision 1's own disclosed bar-granularity limitation covers the rare exception).
                opening_fill = next((f for f in fills if f.symbol == birth.symbol and not f.reduce_only), None)
                if opening_fill is not None:
                    promote_opening_fill(
                        self._lf_correlation, self._lf_positions, self.context.run_id,
                        opening_fill.client_order_id, birth.position_key, OutcomeKind.PORTFOLIO,
                    )

            for old, new in diff.flips:
                register_flip_position(
                    self._lf_positions, self.context.run_id, old.position_key, new.position_key,
                    new.strategy_id,
                )

            death_key_by_symbol = {d.symbol: d.position_key for d in diff.deaths}
            new_trades = self.portfolio_simulator.account.trade_ledger[prev_trade_count:]
            trades_by_symbol: dict[str, list[TradeRecord]] = {}
            for trade in new_trades:
                trades_by_symbol.setdefault(trade.symbol, []).append(trade)

            for symbol, trades in trades_by_symbol.items():
                if symbol in death_key_by_symbol:
                    position_key = death_key_by_symbol[symbol]
                    # Bar-granularity best-effort ordering (Decision 1's own disclosed limitation): the
                    # LAST trade in ledger order for a dying symbol this bar is treated as the one that
                    # zeroed it; any earlier ones this same bar are interim. Exact for the common case
                    # (one closing event per symbol per bar); an accepted approximation otherwise.
                    for interim_trade in trades[:-1]:
                        self._lf_capture_interim(position_key, interim_trade)
                    self._lf_capture_terminal(position_key, trades[-1])
                else:
                    current_key_info = self._lf_registry.current_key(symbol)
                    if current_key_info is None:
                        continue  # a trade for a symbol this registry never saw open -- nothing to attribute
                    for trade in trades:
                        self._lf_capture_interim(current_key_info.position_key, trade)
        except Exception as exc:  # noqa: BLE001 -- failure isolation, see docstring.
            logger.warning("Learning Feedback: resolution-time capture raised for as_of=%s: %r", as_of, exc)

    def _run_one_bar(self, as_of: int) -> None:
        assert self._data_source and self._scanner and self._strategy_manager
        assert self._signal_engine and self._scoring_engine and self._risk_manager
        assert self._execution_engine and self.execution_simulator and self.portfolio_simulator

        self._data_source.feed_up_to(self._scanner, as_of)
        self._scanner.advance_clock(as_of)
        phase_running = self._clock is not None and self._clock.phase is SimPhase.RUNNING
        bars = self._data_source.base_bars_at(as_of)

        if phase_running:
            context_batch = self._scanner.scan(as_of, list(self.context.symbols))
            handles: Sequence[StrategyHandleLike]
            overlay_handles: Sequence[StrategyHandleLike]
            if self._use_strategy_runtime:
                from ai_trader.strategy_runtime.registry import build_runtime_handles
                handles = build_runtime_handles(
                    self._strategy_manager, frozenset(self.context.symbols), only_ids=self._strategy_id_filter,
                )
                # `strategy_id_filter` gates NEW-signal eligibility only (Phase 6.9 CEO directive: a
                # demoted strategy may not open a new position, but an already-open position must keep
                # receiving its own declared time-stop/trailing-stop protection until it closes) -- so
                # overlay eligibility below is derived from the UNFILTERED runtime set, never `handles`.
                # Identical object (no extra computation) whenever no filter is active -- the only case
                # every prior test/Wave D run exercises, so behavior there is byte-for-byte unchanged.
                overlay_handles = handles if self._strategy_id_filter is None else build_runtime_handles(
                    self._strategy_manager, frozenset(self.context.symbols), only_ids=None,
                )
            else:
                handles = self._strategy_manager.active_strategies()
                overlay_handles = handles
            for symbol in sorted(self.context.symbols):
                ctx = context_batch.get(symbol)
                if ctx is None:
                    continue  # NEED_CONTEXT-equivalent: nothing to evaluate this cycle for this symbol
                signal_batch = self._signal_engine.evaluate(ctx, handles, trader_state=None)
                score_batch = self._scoring_engine.score_batch(signal_batch.signals)
                tick_size = self._symbol_meta[symbol].tick_size if symbol in self._symbol_meta else 0.01
                risk_context = _build_risk_context(ctx, as_of, tick_size, self.context.cost_model.spread_ticks)
                portfolio_state = self.portfolio_simulator.to_portfolio_state(as_of)
                # Learning/Research Feedback (Flow B roadmap step 3/6, Architectural Decision Package
                # Decision 4, Option C): build the real, non-degraded Observation for THIS symbol/bar,
                # once, before the Risk Manager decision below -- every ALLOW/DENY this bar attaches to
                # the SAME Observation. `None` (the default, or on any build failure) means no capture
                # happens for this symbol this bar -- never fails the real run (mirrors the Shadow
                # Evidence tap's own failure-isolation convention immediately below).
                lf_observation_id = None
                if self._lf_repo is not None:
                    try:
                        lf_bundle = build_market_snapshot(ctx, self._lf_library_path)
                        lf_observation = build_decision_observation(lf_bundle, self._lf_library_path)
                    except Exception as exc:  # noqa: BLE001 -- failure isolation: a Learning Feedback
                        # snapshot/observation-build bug must never affect competitive execution.
                        logger.warning(
                            "Learning Feedback: market snapshot/observation build raised for symbol=%s: %r",
                            symbol, exc,
                        )
                    else:
                        lf_observation_id = capture_decision_observation(self._lf_repo, lf_observation)
                # Phase 6.10 Implementation Checkpoint 1B, reordered for Portfolio Architect (roadmap
                # Flow B step 2/6, CEO's own mandatory placement -- see __init__'s own docstring): a
                # read-only tap on the already-computed score_batch/risk_context, now placed BEFORE the
                # health_eligible_ids filter, Portfolio Architect, and the real Risk Manager decision
                # below (previously strictly after the decision -- moving it earlier is provably
                # behavior-preserving, see __init__'s own docstring for the full argument).
                # shadow_engine is None unless context.shadow_config.active_strategy_ids() is non-empty
                # (Checkpoint 1A's own disabled-by-default guarantee, unchanged); observe() never
                # reads/writes portfolio_state, decision_batch, or any other real object -- only
                # score_batch/risk_context, both already-produced, immutable values. observe() already
                # isolates a per-strategy failure internally (Design §10.1) -- this outer try/except is
                # defense-in-depth against any exception OUTSIDE that per-strategy boundary (e.g. a bug
                # iterating score_batch.scores itself), so a shadow failure can NEVER fail the real run
                # via step()'s own outer exception handler -- "competitive execution continues" is a
                # hard guarantee, not contingent on shadow_engine's own internal code being bug-free.
                if self.shadow_engine is not None:
                    try:
                        shadow_results = self.shadow_engine.observe(as_of, score_batch, risk_context)
                    except Exception as exc:  # noqa: BLE001 -- failure isolation: shadow must never
                        # affect competitive execution, even via an exception this outer guard didn't
                        # anticipate inside observe() itself.
                        self.shadow_engine.failures.append((as_of, "__engine__", repr(exc)))
                        logger.warning("Shadow Evidence: observe() raised outside its own per-strategy boundary: %r", exc)
                        shadow_results = ()
                    # Learning/Research Feedback Sprint 2, Blocker 1: `observe()`'s own return value
                    # (Learning/Research Feedback Sprint 2 Blocker 1) is processed ONLY here, in the
                    # harness -- shadow_evidence itself never imports/calls learning_feedback. Reuses
                    # the SAME `lf_observation_id` already captured above for this (symbol, as_of) --
                    # Observation is shared per symbol per bar, never per strategy (Architectural
                    # Decision Package Decision 4). `capture_operational_metadata`/`register`/`get` are
                    # all already exception-safe; a defensive symbol match guards against a genuinely
                    # unexpected cross-symbol result (never observed, but never assumed either).
                    if self._lf_repo is not None and lf_observation_id is not None:
                        assert self._lf_positions is not None and self._lf_cost_model_ref is not None
                        for shadow_result in shadow_results:
                            if shadow_result.symbol != symbol:
                                logger.warning(
                                    "Learning Feedback: ShadowObservationResult.symbol=%s does not "
                                    "match the current bar's own symbol=%s -- dropped",
                                    shadow_result.symbol, symbol,
                                )
                                continue
                            capture_operational_metadata(
                                self._lf_repo, shadow_result.decision, None, lf_observation_id,
                            )
                            if shadow_result.position_id is not None:
                                register_shadow_position(self._lf_positions, PendingPosition(
                                    run_id=self.context.run_id, position_key=shadow_result.position_id,
                                    strategy_id=shadow_result.strategy_id, symbol=shadow_result.symbol,
                                    outcome_kind=OutcomeKind.STRATEGY, observation_id=lf_observation_id,
                                    cost_model_ref=self._lf_cost_model_ref, decision_as_of=as_of,
                                ))
                # Strategy Health integration: `health_eligible_ids` filters ONLY the opportunity list
                # handed downstream -- score_batch itself (and the shadow_engine tap above) already saw
                # the full, unfiltered set Signal/Scoring Engine computed for every configured strategy
                # this bar. See __init__'s own docstring for why this must be a separate gate from
                # `strategy_id_filter`.
                risk_opportunities = (
                    score_batch.scores if self._health_eligible_ids is None
                    else tuple(s for s in score_batch.scores if s.strategy_id in self._health_eligible_ids)
                )
                # Portfolio Architect (roadmap Flow B step 2/6, Phase 1: PASSTHROUGH scaffold only) --
                # a new, additive, optional prioritization layer between Strategy Health's own
                # real-eligibility filter and the Risk Manager's own decision. Disabled by default
                # (`self._portfolio_architect_config is None`): no call is made at all, and
                # `architected_opportunities` is then the exact same object as `risk_opportunities`.
                if self._portfolio_architect_config is None:
                    architected_opportunities = risk_opportunities
                else:
                    architect_result = self._portfolio_architect.evaluate(
                        risk_opportunities, portfolio_state, as_of, self._portfolio_architect_config,
                    )
                    architected_opportunities = architect_result.opportunities
                    self.last_portfolio_architect_diagnostics = architect_result.diagnostics
                decision_batch = self._risk_manager.evaluate(architected_opportunities, risk_context, portfolio_state)
                for decision in decision_batch.decisions:
                    if decision.decision is Decision.ALLOW:
                        status = self._execution_engine.execute(decision, portfolio_state)
                        self.orders_submitted += 1
                        if decision.constraints is not None and decision.constraints.stop is not None:
                            self.portfolio_simulator.register_stop_hint(status.client_order_id, decision.constraints.stop)
                        # Learning/Research Feedback: OperationalMetadata + decision-time correlation
                        # registration. Both `capture_operational_metadata`/`register_pending_correlation`
                        # are already internally exception-safe (Phase E's own defense-in-depth
                        # convention) -- never raise, so no extra try/except is needed at this call site.
                        if self._lf_repo is not None and lf_observation_id is not None:
                            assert self._lf_correlation is not None and self._lf_cost_model_ref is not None
                            capture_operational_metadata(self._lf_repo, decision, None, lf_observation_id)
                            # Sprint 2 Blocker 3: a synchronously-rejected/failed order (already known,
                            # for free, right here) will never reach a fill -- never register a
                            # correlation candidate for it at all, rather than registering then relying
                            # on a later cleanup pass to discard it. This is the ONLY terminal-non-fill
                            # disposition observable synchronously; cancellation/expiry are not surfaced
                            # to this call site and are instead bounded by CorrelationMap.drain_pending()
                            # at end-of-run (see _finalize_at_end) -- a deliberately deferred, smaller-
                            # scope correction (Sprint 2 Blocker 3, Option A/C).
                            if status.state not in (OrderState.REJECTED, OrderState.FAILED):
                                # Alias computation mirrors builder.py's own bracket-trigger condition
                                # exactly (Lifecycle Specification I2): each of `-TP`/`-SL` is
                                # independently conditional on `constraints.target`/`constraints.stop`,
                                # never assumed together -- 1, 2, or 3 total aliases, never hardcoded to 3.
                                client_order_ids = [status.client_order_id]
                                if decision.constraints is not None:
                                    if decision.constraints.target is not None:
                                        client_order_ids.append(f"{status.client_order_id}-TP")
                                    if decision.constraints.stop is not None:
                                        client_order_ids.append(f"{status.client_order_id}-SL")
                                register_pending_correlation(self._lf_correlation, PendingCapture(
                                    run_id=self.context.run_id, client_order_ids=tuple(client_order_ids),
                                    strategy_id=decision.strategy_id, symbol=decision.symbol,
                                    decision_id=decision.decision_id, decision_as_of=decision.as_of,
                                    outcome_kind=OutcomeKind.PORTFOLIO, observation_id=lf_observation_id,
                                    cost_model_ref=self._lf_cost_model_ref,
                                ))
                    else:
                        # A real gap a review caught: only liquidation events ever reached
                        # report.risk_events. Every DENY reason, and the batch's own engine_state when
                        # not READY (SUSPENDED/EMERGENCY_STOP), is now recorded too
                        # (PERFORMANCE_ANALYZER.md §6). `strategy_id=decision.strategy_id` (Phase 6.9A,
                        # CEO-approved 2026-07-16): the denial's own already-known originating strategy,
                        # diagnostics only -- does not affect the DENY decision itself.
                        if decision.denied_reasons:
                            for reason in decision.denied_reasons:
                                self.portfolio_simulator.record_risk_event(
                                    f"DENY_{reason.code}", as_of, reason.detail, decision.strategy_id,
                                )
                        else:
                            self.portfolio_simulator.record_risk_event("DENY", as_of, strategy_id=decision.strategy_id)
                        # Learning/Research Feedback: a DENY never reaches execute(), so no
                        # client_order_id/PendingCapture is ever registered for one (structurally
                        # impossible to resolve later, which is correct) -- only OperationalMetadata
                        # records the denial itself.
                        if self._lf_repo is not None and lf_observation_id is not None:
                            capture_operational_metadata(self._lf_repo, decision, None, lf_observation_id)
                if decision_batch.engine_state.value != "READY":
                    # No single strategy caused a batch-level, non-READY engine state -- strategy_id
                    # stays None (the default), unchanged from before this field existed.
                    self.portfolio_simulator.record_risk_event(decision_batch.engine_state.value, as_of)

            if self._enable_time_stops and self._use_strategy_runtime:
                assert self._clock is not None
                time_stop_bars_by_strategy = {
                    h.id: bars_limit for h in overlay_handles
                    if (bars_limit := getattr(h.api, "time_stop_bars", None)) is not None
                }
                if time_stop_bars_by_strategy:
                    due = positions_due_for_time_stop(
                        self.portfolio_simulator.account.positions, self._clock.bar_index,
                        time_stop_bars_by_strategy,
                    )
                    if due:
                        portfolio_state = self.portfolio_simulator.to_portfolio_state(as_of)
                        for position in due:
                            decision = build_time_stop_decision(
                                position, as_of, self._clock.bar_index, self._risk_manager, self._risk_config,
                            )
                            self._execution_engine.execute(decision, portfolio_state)
                            self.orders_submitted += 1
                # Checkpoint 1C: the identical time-stop overlay, applied to each shadow account's OWN
                # positions using the SAME already-computed time_stop_bars_by_strategy dict (Design §4's
                # "Time-stop" row) -- defense-in-depth try/except, mirroring the existing tap call site.
                if self.shadow_engine is not None:
                    try:
                        self.shadow_engine.apply_time_stops(as_of, self._clock.bar_index, time_stop_bars_by_strategy)
                    except Exception as exc:  # noqa: BLE001 -- failure isolation: a shadow overlay bug
                        # must never affect competitive execution.
                        self.shadow_engine.failures.append((as_of, "__engine__", repr(exc)))
                        logger.warning("Shadow Evidence: apply_time_stops() raised: %r", exc)

            if self._enable_trailing_stops and self._use_strategy_runtime:
                atr_mult_by_strategy = {
                    h.id: mult for h in overlay_handles
                    if (mult := getattr(h.api, "trailing_stop_atr_mult", None)) is not None
                }
                positions = self.portfolio_simulator.account.positions
                # Register each newly-opened trailing-enabled position's own entry-bar ATR (the
                # frozen engine's own trailing formula fixes this at signal time, never
                # re-computed bar to bar) -- captured once, the first bar this module observes it.
                for symbol, pos in positions.items():
                    if pos.strategy_id in atr_mult_by_strategy and symbol not in self._trailing_entry_atr:
                        ctx = context_batch.get(symbol)
                        atr = context_access.feature(ctx, "m_atr") if ctx is not None else None
                        if atr is not None and atr > 0:
                            self._trailing_entry_atr[symbol] = atr
                # Drop tracked entries for positions that have since closed.
                for symbol in list(self._trailing_entry_atr):
                    if symbol not in positions:
                        del self._trailing_entry_atr[symbol]

                if atr_mult_by_strategy:
                    due = positions_due_for_trailing_stop(
                        positions, bars, self._trailing_entry_atr, atr_mult_by_strategy,
                    )
                    if due:
                        portfolio_state = self.portfolio_simulator.to_portfolio_state(as_of)
                        for position in due:
                            decision = build_trailing_stop_decision(
                                position, as_of, self._risk_manager, self._risk_config,
                            )
                            self._execution_engine.execute(decision, portfolio_state)
                            self.orders_submitted += 1
                # Checkpoint 1C: the identical trailing-stop overlay, applied to each shadow account's
                # OWN positions, with its OWN per-account entry-ATR tracking (Design §4's "Trailing-
                # stop" row; §10 invariant 3: never reads/writes this harness's own _trailing_entry_atr).
                if self.shadow_engine is not None:
                    try:
                        self.shadow_engine.apply_trailing_stops(as_of, bars, context_batch, atr_mult_by_strategy)
                    except Exception as exc:  # noqa: BLE001 -- failure isolation: a shadow overlay bug
                        # must never affect competitive execution.
                        self.shadow_engine.failures.append((as_of, "__engine__", repr(exc)))
                        logger.warning("Shadow Evidence: apply_trailing_stops() raised: %r", exc)

        fills = self.execution_simulator.advance_bar(as_of, bars)
        assert self._clock is not None
        lf_prev_trade_count = len(self.portfolio_simulator.account.trade_ledger) if self._lf_repo is not None else 0
        self.portfolio_simulator.apply(fills, self._clock.bar_index)
        self.fills_total += len(fills)
        self._execution_engine.reconcile()  # keep EE's own ledger/report in sync (EXECUTION_API.md)
        self.portfolio_simulator.mark_to_market(as_of, bars, phase_running=phase_running)
        if self._lf_repo is not None:
            self._lf_process_fills_for_bar(as_of, fills, lf_prev_trade_count)

        # Checkpoint 1C: the identical fill/mark-to-market sequence, once per shadow account, AFTER the
        # real one above has fully completed (Design §4's "Virtual close" row) -- resolves pending
        # virtual entries and records every closing/partial-exit leg. Runs every bar, unconditionally
        # (not gated on phase_running), exactly mirroring the real sequence's own placement outside the
        # `if phase_running:` block above.
        if self.shadow_engine is not None:
            lf_prev_leg_count = len(self.shadow_engine.trade_legs) if self._lf_repo is not None else 0
            try:
                self.shadow_engine.settle_bar(as_of, self._clock.bar_index, bars, phase_running)
            except Exception as exc:  # noqa: BLE001 -- failure isolation: a shadow settlement bug must
                # never affect competitive execution.
                self.shadow_engine.failures.append((as_of, "__engine__", repr(exc)))
                logger.warning("Shadow Evidence: settle_bar() raised: %r", exc)
            if self._lf_repo is not None:
                self._lf_process_shadow_trade_legs(lf_prev_leg_count)


def _build_risk_context(context: dict[str, Any], as_of: int, tick_size: float, spread_ticks: float) -> RiskContext:
    """Assemble ``RiskContext`` from the already-flowing ``MarketContext`` (``SIMULATION_SEQUENCE.md``
    §2: "RiskContext <- assembled from ctx", never fetched separately).

    IMPLEMENTATION CHOICE, corrected during Phase 6.8's own Checkpoint 1 verification: Phase 6.7's
    original claim that ``atr``/``current_spread``/``liquidity_proxy`` are unavailable in
    ``MarketContext`` was WRONG -- ``ai_trader.market_scanner.features.M15_FEATURE_NAMES`` (confirmed
    by reading the module directly) DOES publish ``m_atr`` and ``atr_ma`` on the M15 timeframe. This
    now threads:
    - ``atr`` <- ``timeframes.M15.features.m_atr`` (the scanner's own ATR).
    - ``atr_rolling_median`` <- ``timeframes.M15.features.atr_ma`` -- a documented approximation
      (mean, not a true rolling median; no rolling-median feature is published) rather than a
      fabricated number.
    - ``current_spread`` <- ``spread_ticks * tick_size`` -- the SAME constant assumed-cost convention
      the Execution Simulator's own cost model already uses (``EXECUTION_SIMULATOR.md`` §4), not a
      real live spread feed (none exists in this repo); reusing the existing assumption rather than
      inventing a second one.
    - ``liquidity_proxy`` <- the current M15 bar's own traded ``volume`` (real OHLCV data, not
      fabricated) as the best available liquidity signal.
    ``current_spread`` here does not include the ± any per-bar variability the Execution Simulator's
    own slippage model may separately apply -- it is a policy-level constant used ONLY for Risk
    Manager's spread-filter gate, never fed back into fill pricing.
    """
    symbol = str(context.get("meta", {}).get("symbol", ""))
    dq_dict = context.get("data_quality")
    level = DataQualityLevel.OK
    if isinstance(dq_dict, dict):
        raw_level = dq_dict.get("level")
        if isinstance(raw_level, str):
            try:
                level = DataQualityLevel(raw_level)
            except ValueError:
                level = DataQualityLevel.OK

    m15 = context.get("timeframes", {}).get("M15", {})
    features = m15.get("features", {}) if isinstance(m15, dict) else {}
    atr = features.get("m_atr") if isinstance(features.get("m_atr"), (int, float)) else None
    atr_rolling_median = features.get("atr_ma") if isinstance(features.get("atr_ma"), (int, float)) else None
    bars = m15.get("bars", []) if isinstance(m15, dict) else []
    last_bar = bars[-1] if bars else None
    liquidity_proxy = last_bar.get("volume") if last_bar is not None else None

    snapshot = SymbolRiskSnapshot(
        atr=float(atr) if atr is not None else None,
        atr_rolling_median=float(atr_rolling_median) if atr_rolling_median is not None else None,
        current_spread=spread_ticks * tick_size,
        liquidity_proxy=float(liquidity_proxy) if isinstance(liquidity_proxy, (int, float)) else None,
        data_quality=level,
    )
    return RiskContext(as_of=as_of, per_symbol={symbol: snapshot}, data_quality=level)
