"""Incremental live loop proof (mandate sections 35-36) -- no real MT5 terminal, deterministic fake
clock/sleep, synthetic M15 rate dicts (support `rate["time"]` exactly like a real MT5 structured-array
row)."""

from __future__ import annotations

from pathlib import Path

from ai_trader.mt5_demo_execution.types import MT5DemoConfig
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.live_runtime_loop import (
    STARTUP_WARMUP_BARS,
    run_live_loop,
)
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.tests._fixtures import (
    FakeMT5BridgeGateway,
    make_connected_demo_adapter,
    make_ledger,
)
from ai_trader.new_brain_live.strategy_platform.real_ev_engine import CostModel
from ai_trader.new_brain_live.strategy_platform.shadow_ledger import ShadowLedger
from ai_trader.new_brain_live.strategy_platform.tests._fixtures import make_risk_execution_deps
from ai_trader.new_brain_live.strategy_platform.risk_execution_adapter import RiskExecutionDeps
from ai_trader.persistent_state.store import SqliteStateStore

SYMBOL = "XAUUSD"
_BAR_SECONDS = 900
_COST = CostModel(cost_model_id="AI_TRADER_SHADOW_COST_MODEL_v1", full_spread_price=0.0, entry_slippage_price=0.12, exit_slippage_price=0.12)


def _rate(ts: int, price: float) -> dict[str, float]:
    return {"time": ts, "open": price, "high": price + 0.3, "low": price - 0.3, "close": price, "tick_volume": 100.0}


def _flat_rates(*, count: int, end_ts: int, base_price: float = 2000.0) -> list[dict[str, float]]:
    return [_rate(end_ts - (count - i) * _BAR_SECONDS, base_price) for i in range(count)]


def test_warmup_fetch_is_bounded_not_full_history(tmp_path: Path) -> None:
    gw = FakeMT5BridgeGateway()
    now = 10_000_000
    gw._rates = _flat_rates(count=25, end_ts=now - 2 * _BAR_SECONDS)
    adapter = make_connected_demo_adapter(gw, config=MT5DemoConfig(max_order_volume=1.0))
    exec_ledger, exec_store = make_ledger(tmp_path, "exec.db")
    shadow_store = SqliteStateStore(tmp_path / "shadow.db")

    run_live_loop(
        adapter=adapter, gateway=gw, config=MT5DemoConfig(max_order_volume=1.0), execution_ledger=exec_ledger,
        shadow_ledger=ShadowLedger(shadow_store), risk_execution_deps=RiskExecutionDeps(**make_risk_execution_deps()),  # type: ignore[arg-type]
        cost_model=_COST, symbol=SYMBOL, poll_interval_seconds=0.0, max_duration_seconds=0.0,
        sleep=lambda s: None, now_fn=lambda: float(now),
    )
    assert len(gw.copy_rates_from_calls) == 1  # exactly one warmup fetch, loop body never entered (duration=0)
    _, _, _, count = gw.copy_rates_from_calls[0]
    assert count == STARTUP_WARMUP_BARS  # bounded, never "all history"
    exec_store.close()
    shadow_store.close()


def test_reconciliation_blocked_prevents_any_warmup_or_processing(tmp_path: Path) -> None:
    from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.mt5_execution_ledger import (
        PENDING_SUBMISSION,
        MT5ExecutionLedgerRecord,
    )

    gw = FakeMT5BridgeGateway()
    gw._positions = (
        __import__("types").SimpleNamespace(symbol=SYMBOL, volume=1.0, price_open=2000.0, time=0, ticket=1),
        __import__("types").SimpleNamespace(symbol=SYMBOL, volume=1.0, price_open=2000.5, time=0, ticket=2),
    )
    adapter = make_connected_demo_adapter(gw, config=MT5DemoConfig(max_order_volume=1.0))
    exec_ledger, exec_store = make_ledger(tmp_path, "exec.db")
    exec_ledger.record(MT5ExecutionLedgerRecord(
        client_order_id="cid-x", decision_id="dec-x", state=PENDING_SUBMISSION, as_of=0,
        strategy_id="s5_c_2d587447_opening_range_breakout_long", strategy_version="rep_7472f3d412f2",
        symbol=SYMBOL, side="LONG", requested_entry=2000.0, actual_quote_bid=None, actual_quote_ask=None,
        sl=1990.0, tp=2030.0, requested_volume=1.0, modeled_risk_money=1.0, modeled_risk_fraction=0.0001,
        account_trade_mode="AccountTradeMode.DEMO", evidence_fingerprint="fp", order_request_id="req-x",
    ))
    shadow_store = SqliteStateStore(tmp_path / "shadow.db")

    report = run_live_loop(
        adapter=adapter, gateway=gw, config=MT5DemoConfig(max_order_volume=1.0), execution_ledger=exec_ledger,
        shadow_ledger=ShadowLedger(shadow_store), risk_execution_deps=RiskExecutionDeps(**make_risk_execution_deps()),  # type: ignore[arg-type]
        cost_model=_COST, symbol=SYMBOL, poll_interval_seconds=0.0, max_duration_seconds=100.0,
        sleep=lambda s: None, now_fn=lambda: 10_000_000.0,
    )
    assert report.reconciliation_blocked is True
    assert report.cycles_processed == 0
    assert gw.copy_rates_from_calls == []  # never even attempted a warmup fetch while blocked
    exec_store.close()
    shadow_store.close()


def test_same_closed_bar_never_processed_twice_across_poll_iterations(tmp_path: Path) -> None:
    gw = FakeMT5BridgeGateway()
    now = 10_000_000
    gw._rates = _flat_rates(count=25, end_ts=now - 2 * _BAR_SECONDS)
    adapter = make_connected_demo_adapter(gw, config=MT5DemoConfig(max_order_volume=1.0))
    exec_ledger, exec_store = make_ledger(tmp_path, "exec.db")
    shadow_store = SqliteStateStore(tmp_path / "shadow.db")

    # fake clock: a small, finite tick sequence so the `while` loop runs a bounded number of times without
    # ever depending on real wall-clock speed.
    ticks = iter([float(now), float(now) + 1, float(now) + 2, float(now) + 3, float(now) + 100])  # last tick exceeds max_duration, ending the loop

    def now_fn() -> float:
        return next(ticks, float(now) + 999)

    report = run_live_loop(
        adapter=adapter, gateway=gw, config=MT5DemoConfig(max_order_volume=1.0), execution_ledger=exec_ledger,
        shadow_ledger=ShadowLedger(shadow_store), risk_execution_deps=RiskExecutionDeps(**make_risk_execution_deps()),  # type: ignore[arg-type]
        cost_model=_COST, symbol=SYMBOL, poll_interval_seconds=0.0, max_duration_seconds=50.0,
        sleep=lambda s: None, now_fn=now_fn,
    )
    # the fake gateway returns the IDENTICAL static rate set on every poll -- no genuinely new bar ever
    # appears after warmup, so cycles_processed must stay at 0 across every subsequent poll iteration
    # (never re-processing the same already-seen bars).
    assert report.cycles_processed == 0
    assert report.exceptions == ()
    assert len(gw.copy_rates_from_calls) >= 2  # warmup + at least one poll iteration actually happened
    exec_store.close()
    shadow_store.close()
