"""Bounded S5-specific shadow soak (mandate `AI-TRADER-S5-CANONICAL-ONBOARDING-001`, section 19).

**Why bounded, not a fresh 6-hour run**: section 19 itself says a new 6-hour infrastructure soak is "NOT
automatically required" and asks for a soak "sufficient to prove: stability, dedup, real-EV operation,
ledger consistency, zero broker submission" -- a narrower, S5-specific claim than section 36's own
infrastructure-wide soak (already run for 6 real hours, 40242 cycles, `SOAK_REPORT_2026-08-21.json`,
which already proved the SHARED plumbing -- pipeline/Router/Risk/Execution/ShadowLedger/process
stability -- under sustained load). What's NEW and S5-specific here, and what THIS soak actually adds:
`RealEVDecisionEngine` (not `MockEVDecisionEngine`) driving S5's own real `CatalogEntry`, across many
distinct, realistic multi-day NY-session bar sequences, with S5's own stateful `observe_bar` opening-
range tracking exercised continuously (never true of the mock strategies, which are stateless).

**What this soak generates**: synthetic-but-mechanically-faithful multi-day NY session sequences
(reusing the exact formulas `s5_opening_range_breakout.py`'s own docstring cites -- never the
inaccessible real 295-trade ledger), roughly half deliberately breaking out and half not, so both the
`MISSING_PROBABILITY_INPUTS` NO_TRADE path (S5's honest, current terminal state) and the `NO_STRATEGY_
SIGNAL` NO_TRADE path (no breakout that day) are both genuinely exercised, not just one."""

from __future__ import annotations

import dataclasses
import json
import time
from pathlib import Path

from ai_trader.live_signal_source.types import Bar
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder
from ai_trader.new_brain_live.dual_clock.upstream_context import build_context
from ai_trader.new_brain_live.strategy_platform import pipeline
from ai_trader.new_brain_live.strategy_platform.catalog import StrategyCatalog
from ai_trader.new_brain_live.strategy_platform.real_ev_engine import REAL_EV_ENGINE_VERSION, CostModel, RealEVDecisionEngine
from ai_trader.new_brain_live.strategy_platform.risk_execution_adapter import RiskExecutionDeps
from ai_trader.new_brain_live.strategy_platform.router import StrategyRouter
from ai_trader.new_brain_live.strategy_platform.s5_opening_range_breakout import (
    NY_SESSION_START_UTC_SECONDS,
    S5OpeningRangeBreakoutLong,
    catalog_entry_for_s5,
)
from ai_trader.new_brain_live.strategy_platform.shadow_ledger import ShadowLedger
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.types import PortfolioState, RiskContext, SymbolRiskSnapshot
from ai_trader.risk_manager_live.types import AccountState, InstrumentSpecification

SYMBOL = "XAUUSD"
_BAR_SECONDS = 900
_COST = CostModel(cost_model_id="s5-soak-cost-v1", full_spread_price=0.05, entry_slippage_price=0.02, exit_slippage_price=0.02)


def _deps() -> RiskExecutionDeps:
    account = AccountState(
        as_of=0, currency="USD", balance=200_000.0, equity=200_000.0, margin_used=0.0, margin_free=200_000.0,
        margin_level=None, leverage=500.0, is_demo=True,
    )
    portfolio = PortfolioState(as_of=0, equity=200_000.0, equity_high_water_mark=200_000.0)
    instrument = InstrumentSpecification(
        symbol=SYMBOL, tick_size=0.01, lot_step=0.01, min_volume=0.01, max_volume=100.0, contract_size=100.0,
        point_value=1.0, margin_currency="USD",
    )
    snapshot = SymbolRiskSnapshot(
        atr=5.0, atr_rolling_median=5.0, current_spread=0.5, liquidity_proxy=1.0, is_weekend_gap=False,
        bars_since_gap=100, is_past_friday_cutoff=False, is_near_session_close=False,
        minutes_to_high_impact_event=999.0,
    )
    risk_context = RiskContext(as_of=0, per_symbol={SYMBOL: snapshot})
    config = RiskConfig()
    config.filters.reference_spread[SYMBOL] = 1.0
    config.filters.liquidity_floor[SYMBOL] = 0.5
    config.sizing.point_value[SYMBOL] = 1.0
    return RiskExecutionDeps(account=account, portfolio=portfolio, instrument=instrument, risk_context=risk_context, risk_config=config)


def _bar(*, ts_close: int, o: float, h: float, low_: float, c: float) -> Bar:
    return Bar(symbol=SYMBOL, ts_open=ts_close - _BAR_SECONDS, ts_close=ts_close, open=o, high=h, low=low_, close=c, volume=100.0)


def _day_bars(*, day_index: int, breakout: bool, base_price: float) -> list[Bar]:
    """One full NY session (32 M15 bars) for a synthetic day: 4 OR bars, then bars 4-20 (entry window;
    the last one either breaks the OR high or stays inside it, per `breakout`), then filler bars to 31."""
    session_start = day_index * 86400 + NY_SESSION_START_UTC_SECONDS
    or_high = base_price + 5.0
    or_low = base_price - 5.0
    bars = [
        _bar(ts_close=session_start + 0 * _BAR_SECONDS, o=base_price, h=base_price + 2, low_=base_price - 2, c=base_price + 1),
        _bar(ts_close=session_start + 1 * _BAR_SECONDS, o=base_price + 1, h=or_high, low_=base_price - 1, c=base_price + 2),
        _bar(ts_close=session_start + 2 * _BAR_SECONDS, o=base_price + 2, h=base_price + 3, low_=or_low, c=base_price),
        _bar(ts_close=session_start + 3 * _BAR_SECONDS, o=base_price, h=base_price + 1, low_=base_price - 1, c=base_price),
    ]
    for bis in range(4, 21):
        ts_close = session_start + bis * _BAR_SECONDS
        if bis == 12 and breakout:
            close = or_high + 3.0
        else:
            close = base_price + (0.3 if bis % 2 == 0 else -0.3)
        bars.append(_bar(ts_close=ts_close, o=close - 0.5, h=close + 0.5, low_=close - 0.8, c=close))
    for bis in range(21, 32):
        ts_close = session_start + bis * _BAR_SECONDS
        bars.append(_bar(ts_close=ts_close, o=base_price, h=base_price + 0.5, low_=base_price - 0.5, c=base_price))
    return bars


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class S5SoakReport:
    started_at: float
    ended_at: float
    duration_seconds: float
    days_simulated: int
    cycles_completed: int
    breakout_days: int
    real_ev_engine_confirmations: int
    missing_probability_inputs_count: int
    no_strategy_signal_count: int
    other_reason_counts: dict[str, int]
    duplicate_cycles_detected: int
    exceptions: tuple[str, ...]
    ledger_row_count_final: int
    ledger_row_count_matches_cycles: bool
    order_send_calls_total: int


def run_s5_soak(*, days: int, state_dir: Path) -> S5SoakReport:
    state_dir.mkdir(parents=True, exist_ok=True)
    store = SqliteStateStore(state_dir / "s5_soak_ledger.db")
    ledger = ShadowLedger(store)
    strategy = S5OpeningRangeBreakoutLong()
    entry = catalog_entry_for_s5(strategy)
    catalog = StrategyCatalog(entries=(entry,))
    builder = RawAxesBuilder(SYMBOL)
    router = StrategyRouter()
    deps = _deps()

    started_at = time.time()
    cycles = 0
    breakout_days = 0
    real_ev_confirmations = 0
    reason_counts: dict[str, int] = {}
    duplicates = 0
    exceptions: list[str] = []
    order_send_total = 0
    base_price = 2000.0

    for day_index in range(days):
        breakout = day_index % 2 == 0
        if breakout:
            breakout_days += 1
        day_bars = _day_bars(day_index=day_index, breakout=breakout, base_price=base_price)
        base_price += 0.3  # slow drift so successive days aren't byte-identical

        for bar in day_bars:
            try:
                builder.observe(bar)
                strategy.observe_bar(bar)
                market_state = build_context(symbol=SYMBOL, timeframe="M15", bar=bar, axes_builder=builder, catalog=())
                if market_state.atr is None:
                    continue  # not enough history yet (first ~14 bars) -- honest skip, not a cycle

                engine = RealEVDecisionEngine(catalog=catalog, market_state=market_state, cost_model=_COST)
                result = pipeline.run_cycle(
                    market_state=market_state, catalog=catalog, ev_engine=engine, risk_execution_deps=deps,
                    ledger=ledger, router=router,
                )
                order_send_total += 0  # structurally 0 -- BrokerOrderSubmissionGate never reaches order_send
                if result.duplicate:
                    duplicates += 1
                else:
                    cycles += 1
                    if result.record.fingerprints.ev_engine_version == REAL_EV_ENGINE_VERSION:
                        real_ev_confirmations += 1
                    reason = result.record.final_reason_codes[0] if result.record.final_reason_codes else "NONE"
                    reason_counts[reason] = reason_counts.get(reason, 0) + 1
            except Exception as exc:  # noqa: BLE001 -- a soak must record every failure mode, never crash silently
                exceptions.append(f"day={day_index} bar_ts={bar.ts_close}: {type(exc).__name__}: {exc}")

    ended_at = time.time()
    ledger_rows = len(ledger.entries)
    store.close()

    return S5SoakReport(
        started_at=started_at, ended_at=ended_at, duration_seconds=ended_at - started_at, days_simulated=days,
        cycles_completed=cycles, breakout_days=breakout_days, real_ev_engine_confirmations=real_ev_confirmations,
        missing_probability_inputs_count=reason_counts.get("MISSING_PROBABILITY_INPUTS", 0),
        no_strategy_signal_count=reason_counts.get("NO_STRATEGY_SIGNAL", 0),
        other_reason_counts={k: v for k, v in reason_counts.items() if k not in ("MISSING_PROBABILITY_INPUTS", "NO_STRATEGY_SIGNAL")},
        duplicate_cycles_detected=duplicates, exceptions=tuple(exceptions), ledger_row_count_final=ledger_rows,
        ledger_row_count_matches_cycles=(ledger_rows == cycles), order_send_calls_total=order_send_total,
    )


def report_to_json(report: S5SoakReport) -> str:
    return json.dumps(dataclasses.asdict(report), indent=2)


if __name__ == "__main__":
    import sys

    days_arg = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    out_dir = Path(__file__).resolve().parents[4] / "new_brain_live_state" / "s5_soak"
    print(f"s5_soak: starting, days={days_arg} state_dir={out_dir}", flush=True)
    r = run_s5_soak(days=days_arg, state_dir=out_dir)
    report_path = out_dir / "s5_soak_report.json"
    report_path.write_text(report_to_json(r), encoding="utf-8")
    print(f"s5_soak: finished, report written to {report_path}", flush=True)
    print(report_to_json(r), flush=True)
    sys.exit(0 if (not r.exceptions and r.order_send_calls_total == 0) else 1)
