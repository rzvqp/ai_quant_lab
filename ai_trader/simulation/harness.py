"""The Simulation Harness -- the orchestrator (``SIMULATION_ARCHITECTURE.md`` §3): owns the Replay
Clock, drives the per-bar pipeline, collects outputs. Composes the SIX live pipeline modules (Market
Scanner, Strategy Manager, Signal Engine, Scoring Engine, Risk Manager, Execution Engine) **UNCHANGED**
plus the three simulation-only components (Execution Simulator, Portfolio Simulator, Performance
Analyzer) -- ``SIMULATION_SEQUENCE.md`` §2's exact per-bar loop, one call per line, no logic
duplicated from any composed module.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from ai_trader.execution_engine.config import ExecConfig
from ai_trader.execution_engine.engine import ExecutionEngine
from ai_trader.execution_engine.types import BrokerCapabilities, MarketStatus, OrderType, TimeInForce
from ai_trader.market_scanner.config import ScannerConfig
from ai_trader.market_scanner.scanner import AdapterConfig, MarketScanner
from ai_trader.market_scanner.types import DataQualityLevel, Mode, SymbolMeta
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.engine import RiskManager
from ai_trader.risk_manager.types import Decision, RiskContext, SymbolRiskSnapshot
from ai_trader.scoring_engine.config import ScoringConfig
from ai_trader.scoring_engine.engine import ScoringEngine
from ai_trader.signal_engine.config import EngineConfig as SignalEngineConfig
from ai_trader.signal_engine.engine import SignalEngine
from ai_trader.signal_engine.pipeline import StrategyHandleLike
from ai_trader.signal_engine.types import Direction
from ai_trader.simulation.clock import ReplayClock
from ai_trader.simulation.config import SimulationContext
from ai_trader.simulation.data_source import ReplayDataSource
from ai_trader.simulation.exceptions import DataLoadError
from ai_trader.simulation.execution_simulator import ExecutionSimulator
from ai_trader.simulation.portfolio_simulator import PortfolioSimulator
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
        strategy-specific mechanism in this module's own logic."""
        self.context = context
        self._symbol_meta = symbol_meta
        self._data_dir = data_dir
        self._manager_config = manager_config or ManagerConfig()
        self._use_strategy_runtime = use_strategy_runtime
        self._risk_config = risk_config or RiskConfig()
        self._enable_time_stops = enable_time_stops
        self._enable_trailing_stops = enable_trailing_stops
        self._strategy_id_filter = strategy_id_filter
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
            return
        last_as_of = self.as_of
        if last_as_of is None or not self.portfolio_simulator.account.positions:
            return
        bars = self._data_source.base_bars_at(last_as_of)
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
        self.portfolio_simulator.apply(tuple(fills), self.bar_index)

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
                decision_batch = self._risk_manager.evaluate(score_batch.scores, risk_context, portfolio_state)
                for decision in decision_batch.decisions:
                    if decision.decision is Decision.ALLOW:
                        status = self._execution_engine.execute(decision, portfolio_state)
                        self.orders_submitted += 1
                        if decision.constraints is not None and decision.constraints.stop is not None:
                            self.portfolio_simulator.register_stop_hint(status.client_order_id, decision.constraints.stop)
                    else:
                        # A real gap a review caught: only liquidation events ever reached
                        # report.risk_events. Every DENY reason, and the batch's own engine_state when
                        # not READY (SUSPENDED/EMERGENCY_STOP), is now recorded too
                        # (PERFORMANCE_ANALYZER.md §6).
                        if decision.denied_reasons:
                            for reason in decision.denied_reasons:
                                self.portfolio_simulator.record_risk_event(f"DENY_{reason.code}", as_of, reason.detail)
                        else:
                            self.portfolio_simulator.record_risk_event("DENY", as_of)
                if decision_batch.engine_state.value != "READY":
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

        fills = self.execution_simulator.advance_bar(as_of, bars)
        assert self._clock is not None
        self.portfolio_simulator.apply(fills, self._clock.bar_index)
        self.fills_total += len(fills)
        self._execution_engine.reconcile()  # keep EE's own ledger/report in sync (EXECUTION_API.md)
        self.portfolio_simulator.mark_to_market(as_of, bars, phase_running=phase_running)


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
