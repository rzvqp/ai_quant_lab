"""Incremental, bar-close-driven S5 MT5 DEMO live runtime loop (mandate sections 35-36, 42).

**Section 35's own explicit constraint**: the operational shadow validation (`334a57f`) found
`RawAxesBuilder`'s own incremental axis computation grows markedly superlinear with total accumulated bar
history within one process (a 40-day/1273-cycle replay took ~5 minutes; 250 days was killed after minutes
of pure CPU growth). This loop does **not** replay the full historical dataset on every new tick/bar --
it performs exactly ONE bounded startup warmup (`STARTUP_WARMUP_BARS` recent M15 bars, fetched once via
`copy_rates_from`) to give `RawAxesBuilder` enough history for a real ATR-14, then processes each
GENUINELY NEW closed bar exactly once as it arrives (`RawAxesBuilder.observe`/`S5OpeningRangeBreakoutLong.
observe_bar` are both already incremental, O(1)-ish per call by their own design -- this loop's own
responsibility is simply to never call them twice for the same bar, and never re-seed from scratch after
startup). Steady-state per-cycle latency is measured and reported (section 42) precisely so a future
long-running deployment can verify this incremental property holds well past the bounded window this
mandate itself runs.

**Section 36 (event cadence)**: polls for a newly CLOSED M15 bar at `poll_interval_seconds` -- never
evaluates the broker decision on every tick, and never re-evaluates the SAME closed bar twice (tracked by
its own `ts_close`, monotonically increasing)."""

from __future__ import annotations

import dataclasses
import time
from typing import Any, Callable

from ai_trader.live_signal_source.types import Bar
from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.types import MT5DemoConfig
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder
from ai_trader.new_brain_live.dual_clock.upstream_context import build_context
from ai_trader.new_brain_live.strategy_platform import pipeline
from ai_trader.new_brain_live.strategy_platform.catalog import StrategyCatalog
from ai_trader.new_brain_live.strategy_platform.ev_engine import TRADE_DECISION
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge import demo_execution_adapter
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.gateway_ext import MT5BridgeGateway
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.mt5_execution_ledger import MT5ExecutionLedger
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.reconciliation import (
    any_blocked,
    reconcile_in_doubt_identities,
)
from ai_trader.new_brain_live.strategy_platform.real_ev_engine import CostModel, RealEVDecisionEngine
from ai_trader.new_brain_live.strategy_platform.risk_execution_adapter import RiskExecutionDeps
from ai_trader.new_brain_live.strategy_platform.router import StrategyRouter
from ai_trader.new_brain_live.strategy_platform.s5_opening_range_breakout import (
    STRATEGY_ID,
    S5OpeningRangeBreakoutLong,
    catalog_entry_for_s5,
)
from ai_trader.new_brain_live.strategy_platform.shadow_ledger import ShadowLedger
from ai_trader.persistent_state.store import SqliteStateStore

SYMBOL = "XAUUSD"
_BAR_SECONDS = 900
_TIMEFRAME_M15 = 15  # mt5.TIMEFRAME_M15
STARTUP_WARMUP_BARS = 60


def _bar_from_rate(rate: Any, symbol: str) -> Bar:
    ts_open = int(rate["time"])
    return Bar(
        symbol=symbol, ts_open=ts_open, ts_close=ts_open + _BAR_SECONDS,
        open=float(rate["open"]), high=float(rate["high"]), low=float(rate["low"]),
        close=float(rate["close"]), volume=float(rate["tick_volume"]),
    )


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class LiveLoopReport:
    started_at: float
    ended_at: float
    duration_seconds: float
    startup_warmup_bars: int
    cycles_processed: int
    trade_decisions: int
    demo_orders_submitted: int
    reconciliation_blocked: bool
    exceptions: tuple[str, ...]
    cycle_latency_samples_ms: tuple[float, ...]


def run_live_loop(
    *, adapter: MT5DemoBrokerAdapter, gateway: MT5BridgeGateway, config: MT5DemoConfig,
    execution_ledger: MT5ExecutionLedger, shadow_ledger: ShadowLedger, risk_execution_deps: RiskExecutionDeps,
    cost_model: CostModel, symbol: str = SYMBOL, poll_interval_seconds: float = 5.0,
    max_duration_seconds: float = 300.0, sleep: Callable[[float], None] = time.sleep,
    now_fn: Callable[[], float] = time.time,
) -> LiveLoopReport:
    started_at = now_fn()
    exceptions: list[str] = []
    latencies: list[float] = []
    cycles_processed = 0
    trade_decisions = 0
    demo_orders_submitted = 0

    # section 25 -- restart reconciliation BEFORE any new submission (or even a warmup fetch) is permitted.
    reconciliation_outcomes = reconcile_in_doubt_identities(ledger=execution_ledger, gateway=gateway, symbol=symbol)
    if any_blocked(reconciliation_outcomes):
        return LiveLoopReport(
            started_at=started_at, ended_at=now_fn(), duration_seconds=now_fn() - started_at,
            startup_warmup_bars=0, cycles_processed=0, trade_decisions=0, demo_orders_submitted=0,
            reconciliation_blocked=True, exceptions=(), cycle_latency_samples_ms=(),
        )

    strategy = S5OpeningRangeBreakoutLong()
    entry = catalog_entry_for_s5(strategy)
    catalog = StrategyCatalog(entries=(entry,))
    builder = RawAxesBuilder(symbol)
    router = StrategyRouter()

    # bounded, ONE-TIME startup warmup -- never repeated, never full-history (section 35).
    now = int(now_fn())
    rates = gateway.copy_rates_from(symbol, _TIMEFRAME_M15, now, STARTUP_WARMUP_BARS)
    warmup_bars = [_bar_from_rate(r, symbol) for r in rates] if rates is not None else []
    warmup_bars = [b for b in warmup_bars if b.ts_close <= now]  # never a still-forming bar
    warmup_bars.sort(key=lambda b: b.ts_close)
    last_processed_ts_close: int | None = None
    for bar in warmup_bars:
        builder.observe(bar)
        strategy.observe_bar(bar)
        last_processed_ts_close = bar.ts_close

    while now_fn() - started_at < max_duration_seconds:
        loop_now = int(now_fn())
        rates = gateway.copy_rates_from(symbol, _TIMEFRAME_M15, loop_now - 3 * _BAR_SECONDS, 4)
        candidates = [_bar_from_rate(r, symbol) for r in rates] if rates is not None else []
        candidates = [b for b in candidates if b.ts_close <= loop_now]
        candidates.sort(key=lambda b: b.ts_close)
        new_bars = [b for b in candidates if last_processed_ts_close is None or b.ts_close > last_processed_ts_close]

        for bar in new_bars:
            t0 = time.perf_counter()
            try:
                builder.observe(bar)
                strategy.observe_bar(bar)
                market_state = build_context(symbol=symbol, timeframe="M15", bar=bar, axes_builder=builder, catalog=())
                last_processed_ts_close = bar.ts_close
                if market_state.atr is None:
                    continue

                ev_engine = RealEVDecisionEngine(catalog=catalog, market_state=market_state, cost_model=cost_model)
                result = pipeline.run_cycle(
                    market_state=market_state, catalog=catalog, ev_engine=ev_engine,
                    risk_execution_deps=risk_execution_deps, ledger=shadow_ledger, router=router,
                )
                if result.duplicate:
                    continue
                cycles_processed += 1
                if any(d.decision == TRADE_DECISION for d in result.ev_decisions):
                    trade_decisions += 1
                    if result.record.broker_submission_state.startswith("BLOCKED_AT_GATE"):
                        winning = next(d for d in result.ev_decisions if d.decision == TRADE_DECISION)
                        outcome = demo_execution_adapter.execute(
                            hypothesis=winning.hypothesis, decision=winning, adapter=adapter, gateway=gateway,
                            config=config, ledger=execution_ledger, symbol=symbol, expected_strategy_id=STRATEGY_ID,
                        )
                        if outcome.submitted:
                            demo_orders_submitted += 1
            except Exception as exc:  # noqa: BLE001 -- a live loop must record every failure mode, never crash silently
                exceptions.append(f"bar_ts={bar.ts_close}: {type(exc).__name__}: {exc}")
            finally:
                latencies.append((time.perf_counter() - t0) * 1000.0)

        sleep(poll_interval_seconds)

    ended_at = now_fn()
    return LiveLoopReport(
        started_at=started_at, ended_at=ended_at, duration_seconds=ended_at - started_at,
        startup_warmup_bars=len(warmup_bars), cycles_processed=cycles_processed, trade_decisions=trade_decisions,
        demo_orders_submitted=demo_orders_submitted, reconciliation_blocked=False, exceptions=tuple(exceptions),
        cycle_latency_samples_ms=tuple(latencies),
    )


def report_to_json(report: LiveLoopReport) -> str:
    import json

    return json.dumps(dataclasses.asdict(report), indent=2)
