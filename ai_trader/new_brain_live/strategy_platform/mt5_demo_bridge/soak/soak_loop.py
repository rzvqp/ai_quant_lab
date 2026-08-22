"""Unattended S5 MT5 DEMO operational soak orchestrator (mandate `AI-TRADER-S5-MT5-DEMO-UNATTENDED-
SOAK-001`). Wraps the same incremental, bar-close-driven event model `live_runtime_loop.py` already
established (section 16 explicitly requires reusing it) with: restart reconciliation before ANY new
submission (section 14), continuous position lifecycle tracking (open confirmation + close detection +
exit classification, independent of whether new submissions are currently blocked -- an existing owned
position is always still tracked to its natural SL/TP exit), the safety-stop monitor (section 25 -- once
tripped, NEW submissions stop, but nothing already open is touched), checkpoint/health-snapshot writes,
and the section-23 termination conditions."""

from __future__ import annotations

import dataclasses
import datetime
import time
from pathlib import Path
from typing import Callable

from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.types import MT5DemoConfig
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder
from ai_trader.new_brain_live.dual_clock.upstream_context import build_context
from ai_trader.new_brain_live.strategy_platform import pipeline
from ai_trader.new_brain_live.strategy_platform.catalog import StrategyCatalog
from ai_trader.new_brain_live.strategy_platform.ev_engine import TRADE_DECISION
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge import demo_execution_adapter
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.gateway_ext import MT5BridgeGateway
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.live_runtime_loop import (
    STARTUP_WARMUP_BARS,
    _TIMEFRAME_M15,
    _bar_from_rate,
)
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.mt5_execution_ledger import (
    CLOSED,
    MT5ExecutionLedger,
)
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.reconciliation import (
    any_blocked,
    reconcile_in_doubt_identities,
)
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.risk_sizer import (
    INVALID_SL_DISTANCE,
    LOSS_CALCULATION_FAILED,
)
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.soak import checkpoints, health_state
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.soak.safety_monitor import (
    ACCOUNT_NOT_DEMO,
    BROKER_RECONCILIATION_AMBIGUITY,
    EVIDENCE_IDENTITY_MISMATCH,
    INVALID_SYMBOL_CONTRACT,
    RISK_CALCULATION_INVALID,
    RISK_EXCEEDS_5_PERCENT,
    SL_UNAVAILABLE,
    STRATEGY_IDENTITY_MISMATCH,
    SafetyMonitor,
)
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.soak.trade_lifecycle import (
    detect_closed_positions,
    detect_new_open_positions,
)
from ai_trader.new_brain_live.strategy_platform.real_ev_engine import CostModel, RealEVAuthorityError, RealEVDecisionEngine
from ai_trader.new_brain_live.strategy_platform.risk_execution_adapter import RiskExecutionDeps
from ai_trader.new_brain_live.strategy_platform.router import StrategyRouter
from ai_trader.new_brain_live.strategy_platform.s5_opening_range_breakout import (
    STRATEGY_ID,
    S5OpeningRangeBreakoutLong,
    catalog_entry_for_s5,
)
from ai_trader.new_brain_live.strategy_platform.shadow_ledger import ShadowLedger

SYMBOL = "XAUUSD"
_BAR_SECONDS = 900


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class SoakTerminationConfig:
    max_calendar_days: float = 60.0
    min_genuine_trades: int = 20
    min_trading_days: int = 20


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class SoakReport:
    started_at: float
    ended_at: float
    duration_seconds: float
    termination_reason: str
    final_status: tuple[str, ...]
    closed_trades: int
    submitted_orders: int
    trading_days_observed: int
    exceptions: tuple[str, ...]


def _read_current_equity(gateway: MT5BridgeGateway) -> float | None:
    try:
        info = gateway.account_info()
    except Exception:  # noqa: BLE001
        return None
    if info is None:
        return None
    equity = getattr(info, "equity", None)
    return float(equity) if equity is not None else None


def run_soak(
    *, adapter: MT5DemoBrokerAdapter, gateway: MT5BridgeGateway, config: MT5DemoConfig,
    execution_ledger: MT5ExecutionLedger, shadow_ledger: ShadowLedger, risk_execution_deps: RiskExecutionDeps,
    cost_model: CostModel, safety_monitor: SafetyMonitor, symbol: str = SYMBOL, state_dir: Path,
    poll_interval_seconds: float = 5.0, termination: SoakTerminationConfig = SoakTerminationConfig(),
    should_stop: Callable[[], bool] = lambda: False, now_fn: Callable[[], float] = time.time,
    sleep: Callable[[float], None] = time.sleep,
) -> SoakReport:
    started_at = now_fn()
    exceptions: list[str] = []
    trading_days: set[str] = set()
    consecutive_gateway_exceptions = 0
    first_trade_checkpoint_written = (state_dir / "first_trade_checkpoint.json").exists()

    starting_equity = _read_current_equity(gateway) or 0.0

    # section 14 -- restart reconciliation BEFORE any new submission, every process start.
    reconciliation_outcomes = reconcile_in_doubt_identities(ledger=execution_ledger, gateway=gateway, symbol=symbol)
    if any_blocked(reconciliation_outcomes):
        safety_monitor.trip(BROKER_RECONCILIATION_AMBIGUITY, f"{len(reconciliation_outcomes)} in-doubt identities, ambiguous match", at=int(started_at))

    strategy = S5OpeningRangeBreakoutLong()
    entry = catalog_entry_for_s5(strategy)
    catalog = StrategyCatalog(entries=(entry,))
    builder = RawAxesBuilder(symbol)
    router = StrategyRouter()

    now = int(now_fn())
    rates = gateway.copy_rates_from(symbol, _TIMEFRAME_M15, now, STARTUP_WARMUP_BARS)
    warmup_bars = sorted(
        (b for b in ([_bar_from_rate(r, symbol) for r in rates] if rates is not None else []) if b.ts_close <= now),
        key=lambda b: b.ts_close,
    )
    last_processed_ts_close: int | None = None
    for bar in warmup_bars:
        builder.observe(bar)
        strategy.observe_bar(bar)
        last_processed_ts_close = bar.ts_close

    termination_reason = ""
    while True:
        loop_now = now_fn()
        elapsed_days = (loop_now - started_at) / 86400.0
        closed_trades = sum(1 for e in execution_ledger.entries if e.state == CLOSED)

        if closed_trades >= termination.min_genuine_trades and len(trading_days) >= termination.min_trading_days:
            termination_reason = "A_TRADES_AND_DAYS_MET"
            break
        if elapsed_days >= termination.max_calendar_days:
            termination_reason = "B_CALENDAR_DAYS_ELAPSED"
            break
        if safety_monitor.is_blocked():
            termination_reason = "C_SAFETY_BLOCKER"
            break
        if should_stop():
            termination_reason = "D_EXPLICIT_STOP"
            break

        # position lifecycle -- always runs, even while new submissions might be blocked (an already-open
        # position must still be tracked to its own SL/TP exit, section 25's own "manage only via
        # canonical protective orders" -- tracking is not management, it is observation).
        try:
            detect_new_open_positions(ledger=execution_ledger, gateway=gateway, symbol=symbol)
            detect_closed_positions(ledger=execution_ledger, gateway=gateway, symbol=symbol, now=int(loop_now))
            consecutive_gateway_exceptions = 0
        except Exception as exc:  # noqa: BLE001
            exceptions.append(f"lifecycle@{int(loop_now)}: {type(exc).__name__}: {exc}")
            consecutive_gateway_exceptions += 1
            if consecutive_gateway_exceptions >= 5:
                from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.soak.safety_monitor import PERSISTENT_BROKER_API_CORRUPTION
                safety_monitor.trip(PERSISTENT_BROKER_API_CORRUPTION, f"{consecutive_gateway_exceptions} consecutive gateway exceptions", at=int(loop_now))

        checkpoints.maybe_write_checkpoint(
            ledger=execution_ledger, starting_equity=starting_equity, state_dir=state_dir,
            first_trade_written=first_trade_checkpoint_written,
        )
        first_trade_checkpoint_written = first_trade_checkpoint_written or (state_dir / "first_trade_checkpoint.json").exists()

        status = adapter.status()
        equity_now = _read_current_equity(gateway)
        latest_states = [execution_ledger.latest_state_for(cid) for cid in execution_ledger.all_client_order_ids()]
        open_owned_positions = sum(1 for r in latest_states if r is not None and r.state == "OPEN_CONFIRMED")
        pending_owned_orders = sum(1 for r in latest_states if r is not None and r.state == "SUBMITTED_ACK")
        current_block = safety_monitor.current_block()
        health_state.write_health_snapshot(state_dir / "health.json", health_state.HealthSnapshot(
            loop_alive_as_of=int(loop_now), mt5_connected=adapter.is_connected(),
            account_trade_mode=str(status.account_trade_mode), server=status.server, equity=equity_now,
            last_valid_market_event_ts=last_processed_ts_close, last_processed_bar_ts=last_processed_ts_close,
            open_owned_positions=open_owned_positions, pending_owned_orders=pending_owned_orders,
            last_reconciliation_as_of=int(started_at), last_error=exceptions[-1] if exceptions else None,
            safety_blocked=safety_monitor.is_blocked(), safety_block_condition=(current_block.condition if current_block else None),
            trades_closed_so_far=closed_trades, soak_started_at=started_at,
        ))

        if status.account_is_demo is not True:
            safety_monitor.trip(ACCOUNT_NOT_DEMO, f"account_trade_mode={status.account_trade_mode!r}", at=int(loop_now))

        if not safety_monitor.is_blocked():
            try:
                # NEVER `rates or []` here -- the real MT5 copy_rates_from returns a numpy structured
                # array (unlike positions_get/orders_get/history_deals_get, which return plain tuples),
                # and `bool(array)` raises ValueError for any array with more than one element. Live-
                # discovered this exact defect during this mandate's own smoke test against the real
                # terminal -- an `is not None` check is required, matching live_runtime_loop.py's own
                # (already-correct) precedent.
                poll_rates = gateway.copy_rates_from(symbol, _TIMEFRAME_M15, int(loop_now) - 3 * _BAR_SECONDS, 4)
                poll_bars = [_bar_from_rate(r, symbol) for r in poll_rates] if poll_rates is not None else []
                candidates = sorted((b for b in poll_bars if b.ts_close <= int(loop_now)), key=lambda b: b.ts_close)
                new_bars = [b for b in candidates if last_processed_ts_close is None or b.ts_close > last_processed_ts_close]

                for bar in new_bars:
                    builder.observe(bar)
                    strategy.observe_bar(bar)
                    market_state = build_context(symbol=symbol, timeframe="M15", bar=bar, axes_builder=builder, catalog=())
                    last_processed_ts_close = bar.ts_close
                    trading_days.add(datetime.datetime.fromtimestamp(bar.ts_close, tz=datetime.timezone.utc).date().isoformat())
                    if market_state.atr is None:
                        continue

                    try:
                        ev_engine = RealEVDecisionEngine(catalog=catalog, market_state=market_state, cost_model=cost_model)
                    except RealEVAuthorityError as exc:
                        from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.soak.safety_monitor import REAL_EV_FAILURE
                        safety_monitor.trip(REAL_EV_FAILURE, str(exc), at=int(loop_now))
                        break

                    result = pipeline.run_cycle(
                        market_state=market_state, catalog=catalog, ev_engine=ev_engine,
                        risk_execution_deps=risk_execution_deps, ledger=shadow_ledger, router=router,
                    )
                    if result.duplicate:
                        continue
                    if any(d.decision == TRADE_DECISION for d in result.ev_decisions) and result.record.broker_submission_state.startswith("BLOCKED_AT_GATE"):
                        winning = next(d for d in result.ev_decisions if d.decision == TRADE_DECISION)
                        outcome = demo_execution_adapter.execute(
                            hypothesis=winning.hypothesis, decision=winning, adapter=adapter, gateway=gateway,
                            config=config, ledger=execution_ledger, symbol=symbol, expected_strategy_id=STRATEGY_ID,
                        )
                        if not outcome.submitted and outcome.reason is not None:
                            _maybe_trip_from_reason(safety_monitor, outcome.reason, at=int(loop_now))
            except Exception as exc:  # noqa: BLE001
                exceptions.append(f"cycle@{int(loop_now)}: {type(exc).__name__}: {exc}")

        sleep(poll_interval_seconds)

    ended_at = now_fn()
    final_status = _final_status(termination_reason=termination_reason, safety_monitor=safety_monitor, execution_ledger=execution_ledger)
    checkpoints.write_final_report(
        ledger=execution_ledger, starting_equity=starting_equity, state_dir=state_dir,
        termination_reason=termination_reason, wall_clock_seconds=ended_at - started_at,
    )
    return SoakReport(
        started_at=started_at, ended_at=ended_at, duration_seconds=ended_at - started_at,
        termination_reason=termination_reason, final_status=final_status,
        closed_trades=sum(1 for e in execution_ledger.entries if e.state == CLOSED),
        submitted_orders=len(execution_ledger.all_client_order_ids()), trading_days_observed=len(trading_days),
        exceptions=tuple(exceptions),
    )


def _maybe_trip_from_reason(safety_monitor: SafetyMonitor, reason: str, *, at: int) -> None:
    """Maps a `demo_execution_adapter.execute()`/`risk_sizer` rejection reason to a section-25 safety
    condition, where the reason is a genuine ANOMALY (not routine, expected refusal traffic like an
    honest NO_TRADE or a benign restart-dedup skip, neither of which ever reaches this function)."""
    mapping = {
        demo_execution_adapter.WRONG_STRATEGY: STRATEGY_IDENTITY_MISMATCH,
        demo_execution_adapter.EVIDENCE_MISMATCH: EVIDENCE_IDENTITY_MISMATCH,
        demo_execution_adapter.SYMBOL_CAPABILITIES_UNAVAILABLE: INVALID_SYMBOL_CONTRACT,
        LOSS_CALCULATION_FAILED: RISK_CALCULATION_INVALID,
        INVALID_SL_DISTANCE: SL_UNAVAILABLE,
    }
    condition = mapping.get(reason)
    if condition is not None:
        safety_monitor.trip(condition, reason, at=at)


def _final_status(*, termination_reason: str, safety_monitor: SafetyMonitor, execution_ledger: MT5ExecutionLedger) -> tuple[str, ...]:
    closed = sum(1 for e in execution_ledger.entries if e.state == CLOSED)
    if termination_reason == "C_SAFETY_BLOCKER":
        block = safety_monitor.current_block()
        return ("S5_MT5_DEMO_UNATTENDED_SOAK_BLOCKED", f"blocker={block.condition if block else 'UNKNOWN'}")
    if closed == 0 and len(execution_ledger.all_client_order_ids()) == 0:
        return ("S5_MT5_DEMO_UNATTENDED_SOAK_COMPLETE", "NO_GENUINE_S5_SIGNAL_OBSERVED")
    return (
        "S5_MT5_DEMO_UNATTENDED_SOAK_COMPLETE", "S5_MT5_DEMO_EXECUTION_OPERATIONAL_PASS",
        "S5_MT5_DEMO_RISK_CONTROL_PASS", "S5_MT5_DEMO_RECONCILIATION_PASS",
    )
