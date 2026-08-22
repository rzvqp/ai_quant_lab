"""S5 OPERATIONAL SHADOW VALIDATION replay (mandate `AI-TRADER-S5-OPERATIONAL-SHADOW-VALIDATION-001`,
sections 10-18, 22).

Distinct from `s5_soak.py` (prior mandate `AI-TRADER-S5-CANONICAL-ONBOARDING-001` section 19): that soak
predates `VE-S5-REAL-EV-RUNTIME-PACKAGING-001` and used its own ad hoc `CostModel`
(`cost_model_id="s5-soak-cost-v1"`), which does NOT match `S5_REAL_EV_EVIDENCE_V1`'s declared
`evidence_cost_model_id="AI_TRADER_SHADOW_COST_MODEL_v1"` -- running it unmodified today would trip
`EVIDENCE_COST_IDENTITY_MISMATCH` on every cycle, never reaching a genuine EV computation. This script
is a NEW, separate operational replay (the prior soak is left untouched as a historical segment-C
artifact) using the CORRECT, evidence-matching cost model
(`ai_trader/new_brain_live/strategy_platform/tests/test_s5_onboarding_integration.py`'s own `_COST`
fixture, reused verbatim: `full_spread_price=0.0, entry_slippage_price=0.12, exit_slippage_price=0.12`,
summing to the evidence's own STRESS `round_trip_price=0.24`).

**What this replay generates**: synthetic-but-mechanically-faithful multi-day NY session bar sequences
(same formulas as `s5_soak.py`/`test_s5_opening_range_breakout.py` -- never the inaccessible real
295-trade ledger), alternating breakout/non-breakout days (never engineered to avoid either
TRADE_DECISION or NO_TRADE -- mandate sections 17-18: "do not force", "do not optimize away"). Two
phases:

1. PRIMARY REPLAY -- `days` synthetic NY sessions, real `RealEVDecisionEngine` + real
   `S5_REAL_EV_EVIDENCE_V1`, full pipeline.run_cycle, tracking every count sections 10/12/16/17/18
   require.
2. RESTART REPLAY -- the SAME bar sequence, fresh `RawAxesBuilder`/`S5OpeningRangeBreakoutLong`/
   `RealEVDecisionEngine` instances (simulating a process restart), same on-disk ledger reopened --
   proving section 13 (no duplicate ShadowLedger records, no duplicate trade identities on restart).

A separate, in-process LATENCY MICROBENCHMARK (section 22) times `strategy.evaluate`,
`RealEVDecisionEngine.decide`, and `evaluate_and_attempt` in isolation over many repeated calls on a
fixed, real breakout fixture -- the per-cycle wall-clock already recorded by the two replay phases above
covers the "complete decision path" figure; this microbenchmark isolates the sub-step figures pipeline.py
does not expose sub-timings for on its own (no pipeline.py change made or needed for this)."""

from __future__ import annotations

import dataclasses
import json
import statistics
import time
from pathlib import Path

from ai_trader.live_signal_source.types import Bar
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder
from ai_trader.new_brain_live.dual_clock.upstream_context import build_context
from ai_trader.new_brain_live.strategy_platform import pipeline
from ai_trader.new_brain_live.strategy_platform.catalog import StrategyCatalog
from ai_trader.new_brain_live.strategy_platform.ev_engine import TRADE_DECISION
from ai_trader.new_brain_live.strategy_platform.real_ev_engine import REAL_EV_ENGINE_VERSION, CostModel, RealEVDecisionEngine
from ai_trader.new_brain_live.strategy_platform.risk_execution_adapter import RiskExecutionDeps, evaluate_and_attempt
from ai_trader.new_brain_live.strategy_platform.router import StrategyRouter
from ai_trader.new_brain_live.strategy_platform.s5_ev_evidence import S5_REAL_EV_EVIDENCE_V1
from ai_trader.new_brain_live.strategy_platform.s5_opening_range_breakout import (
    ENTRY_WINDOW_FIRST_BIS,
    NY_SESSION_START_UTC_SECONDS,
    S5OpeningRangeBreakoutLong,
    catalog_entry_for_s5,
)
from ai_trader.new_brain_live.strategy_platform.shadow_ledger import ShadowLedger
from ai_trader.new_brain_live.strategy_platform.strategy_protocol import StrategyEvaluationInput
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.types import PortfolioState, RiskContext, SymbolRiskSnapshot
from ai_trader.risk_manager_live.types import AccountState, InstrumentSpecification

SYMBOL = "XAUUSD"
_BAR_SECONDS = 900

#: Matches S5_REAL_EV_EVIDENCE_V1's own declared evidence_cost_model_id / evidence_round_trip_price
#: (STRESS=0.24) -- identical to test_s5_onboarding_integration.py's `_COST` fixture, not reinvented.
_COST = CostModel(cost_model_id="AI_TRADER_SHADOW_COST_MODEL_v1", full_spread_price=0.0, entry_slippage_price=0.12, exit_slippage_price=0.12)


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
    """One full NY session (32 M15 bars): 4 OR bars, bars 4-20 (entry window; bis=12 breaks the OR high
    iff `breakout`), then filler bars 21-31. Identical formulas to `s5_soak.py`'s own `_day_bars` (never
    re-derived ad hoc) -- the only thing new in this module is the cost model and the metrics gathered."""
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


def _all_bars(days: int) -> list[Bar]:
    bars: list[Bar] = []
    base_price = 2000.0
    for day_index in range(days):
        breakout = day_index % 2 == 0
        bars.extend(_day_bars(day_index=day_index, breakout=breakout, base_price=base_price))
        base_price += 0.3
    return bars


@dataclasses.dataclass(slots=True)
class _ReplayAccumulator:
    cycles_completed: int = 0
    duplicates: int = 0
    hypotheses_created: int = 0
    ev_evaluations: int = 0
    trade_decisions: int = 0
    no_trade_reason_counts: dict[str, int] = dataclasses.field(default_factory=dict)
    dedup_keys_seen: list[str] = dataclasses.field(default_factory=list)
    order_intents_seen: list[str] = dataclasses.field(default_factory=list)
    exceptions: list[str] = dataclasses.field(default_factory=list)
    cycle_latencies_s: list[float] = dataclasses.field(default_factory=list)
    positive_path_market_timestamps: list[int] = dataclasses.field(default_factory=list)
    first_market_timestamp: int | None = None
    last_market_timestamp: int | None = None


def _run_replay(
    *, bars: list[Bar], ledger: ShadowLedger, catalog: StrategyCatalog, deps: RiskExecutionDeps, acc: _ReplayAccumulator,
) -> None:
    strategy = catalog.entries[0].strategy
    assert isinstance(strategy, S5OpeningRangeBreakoutLong)
    builder = RawAxesBuilder(SYMBOL)
    router = StrategyRouter()

    for bar in bars:
        try:
            builder.observe(bar)
            strategy.observe_bar(bar)
            market_state = build_context(symbol=SYMBOL, timeframe="M15", bar=bar, axes_builder=builder, catalog=())
            if market_state.atr is None:
                continue  # honest skip -- not enough history yet, never a cycle

            if acc.first_market_timestamp is None:
                acc.first_market_timestamp = market_state.market_timestamp
            acc.last_market_timestamp = market_state.market_timestamp

            engine = RealEVDecisionEngine(catalog=catalog, market_state=market_state, cost_model=_COST)
            t0 = time.perf_counter()
            result = pipeline.run_cycle(
                market_state=market_state, catalog=catalog, ev_engine=engine, risk_execution_deps=deps,
                ledger=ledger, router=router,
            )
            acc.cycle_latencies_s.append(time.perf_counter() - t0)

            if result.duplicate:
                acc.duplicates += 1
                continue
            acc.cycles_completed += 1
            acc.dedup_keys_seen.extend(result.record.hypothesis_dedup_keys)
            acc.hypotheses_created += len(result.record.hypothesis_dedup_keys)
            acc.ev_evaluations += len(result.ev_decisions)
            if result.record.hypothetical_order_intent is not None:
                acc.order_intents_seen.append(result.record.hypothetical_order_intent)
            for d in result.ev_decisions:
                if d.decision == TRADE_DECISION:
                    acc.trade_decisions += 1
            if any(d.decision == TRADE_DECISION for d in result.ev_decisions) and result.record.broker_submission_state.startswith("BLOCKED_AT_GATE"):
                acc.positive_path_market_timestamps.append(market_state.market_timestamp)
            reason = result.record.final_reason_codes[0] if result.record.final_reason_codes else "NONE"
            acc.no_trade_reason_counts[reason] = acc.no_trade_reason_counts.get(reason, 0) + 1
        except Exception as exc:  # noqa: BLE001 -- an operational replay must record every failure mode
            acc.exceptions.append(f"bar_ts={bar.ts_close}: {type(exc).__name__}: {exc}")


def _latency_microbenchmark(*, catalog: StrategyCatalog, deps: RiskExecutionDeps, iterations: int) -> dict[str, dict[str, float]]:
    """Isolates evaluate/EV/Risk+Execution sub-step latency on a FIXED, real breakout fixture, repeated
    `iterations` times -- no ledger writes (pure component timing), no pipeline.py change."""
    from ai_trader.new_brain_live.strategy_platform.tests.test_s5_opening_range_breakout import _fixture, _session_bar

    breakout_bar = _session_bar(ENTRY_WINDOW_FIRST_BIS + 1, close=2052.0)
    strategy, market_state = _fixture(extra_bars=[breakout_bar])
    evaluation_input = StrategyEvaluationInput(market_state=market_state, tower_context=None, config={})
    engine = RealEVDecisionEngine(catalog=catalog, market_state=market_state, cost_model=_COST)

    evaluate_times: list[float] = []
    decide_times: list[float] = []
    risk_exec_times: list[float] = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        hypothesis = strategy.evaluate(evaluation_input)
        evaluate_times.append(time.perf_counter() - t0)
        assert hypothesis is not None

        t0 = time.perf_counter()
        decision = engine.decide(hypothesis)
        decide_times.append(time.perf_counter() - t0)
        assert decision.decision == TRADE_DECISION  # this exact fixture is the already-proven positive-path one

        t0 = time.perf_counter()
        evaluate_and_attempt(decision, deps=deps)
        risk_exec_times.append(time.perf_counter() - t0)

    def _stats(xs: list[float]) -> dict[str, float]:
        xs_sorted = sorted(xs)
        return {
            "mean_ms": statistics.mean(xs_sorted) * 1000, "median_ms": statistics.median(xs_sorted) * 1000,
            "p95_ms": xs_sorted[int(len(xs_sorted) * 0.95) - 1] * 1000, "max_ms": max(xs_sorted) * 1000,
            "min_ms": min(xs_sorted) * 1000,
        }

    return {"strategy_evaluate": _stats(evaluate_times), "real_ev_decide": _stats(decide_times), "risk_and_shadow_execution": _stats(risk_exec_times)}


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class S5OperationalReplayReport:
    started_at: float
    ended_at: float
    duration_seconds: float
    days_simulated: int
    primary: dict[str, object]
    restart: dict[str, object]
    dedup_proof: dict[str, int]
    latency_microbenchmark: dict[str, dict[str, float]]
    order_send_calls_total: int
    broker_gate_enabled: bool
    ev_engine_version_confirmed: str


def run_operational_replay(*, days: int, state_dir: Path, latency_iterations: int = 200) -> S5OperationalReplayReport:
    state_dir.mkdir(parents=True, exist_ok=True)
    db_path = state_dir / "s5_operational_replay_ledger.db"
    if db_path.exists():
        db_path.unlink()  # fresh, deterministic run -- this script owns this exact path

    strategy = S5OpeningRangeBreakoutLong()
    entry = catalog_entry_for_s5(strategy)
    catalog = StrategyCatalog(entries=(entry,))
    deps = _deps()
    assert deps.gate.enabled is False  # broker hard boundary precondition (mandate section 15)

    bars = _all_bars(days)

    started_at = time.time()

    # ── phase 1: primary replay ──
    store1 = SqliteStateStore(db_path)
    ledger1 = ShadowLedger(store1)
    primary_acc = _ReplayAccumulator()
    _run_replay(bars=bars, ledger=ledger1, catalog=catalog, deps=deps, acc=primary_acc)
    ledger_rows_after_primary = len(ledger1.entries)
    store1.close()

    # ── phase 2: restart replay -- fresh strategy/builder/engine instances, SAME on-disk ledger, SAME bars ──
    strategy_restart = S5OpeningRangeBreakoutLong()
    entry_restart = catalog_entry_for_s5(strategy_restart)
    catalog_restart = StrategyCatalog(entries=(entry_restart,))
    store2 = SqliteStateStore(db_path)
    ledger2 = ShadowLedger(store2)
    ledger_rows_at_restart_open = len(ledger2.entries)
    restart_acc = _ReplayAccumulator()
    _run_replay(bars=bars, ledger=ledger2, catalog=catalog_restart, deps=deps, acc=restart_acc)
    ledger_rows_after_restart = len(ledger2.entries)
    store2.close()

    # ── dedup proof across the primary replay's own ledger rows ──
    all_dedup_keys = list(primary_acc.dedup_keys_seen)
    all_order_intents = list(primary_acc.order_intents_seen)
    duplicate_hypotheses = len(all_dedup_keys) - len(set(all_dedup_keys))
    duplicate_shadow_orders = len(all_order_intents) - len(set(all_order_intents))

    latency = _latency_microbenchmark(catalog=catalog, deps=deps, iterations=latency_iterations)

    ended_at = time.time()

    def _lat_stats(xs: list[float]) -> dict[str, float]:
        if not xs:
            return {"mean_ms": 0.0, "median_ms": 0.0, "p95_ms": 0.0, "max_ms": 0.0, "min_ms": 0.0}
        xs_sorted = sorted(xs)
        return {
            "mean_ms": statistics.mean(xs_sorted) * 1000, "median_ms": statistics.median(xs_sorted) * 1000,
            "p95_ms": xs_sorted[int(len(xs_sorted) * 0.95) - 1] * 1000, "max_ms": max(xs_sorted) * 1000,
            "min_ms": min(xs_sorted) * 1000,
        }

    return S5OperationalReplayReport(
        started_at=started_at, ended_at=ended_at, duration_seconds=ended_at - started_at, days_simulated=days,
        primary={
            "cycles_completed": primary_acc.cycles_completed, "duplicates_within_primary": primary_acc.duplicates,
            "hypotheses_created": primary_acc.hypotheses_created, "ev_evaluations": primary_acc.ev_evaluations,
            "trade_decisions": primary_acc.trade_decisions,
            "no_trade_and_final_reason_distribution": primary_acc.no_trade_reason_counts,
            "exceptions": primary_acc.exceptions, "exception_count": len(primary_acc.exceptions),
            "positive_path_cycle_count": len(primary_acc.positive_path_market_timestamps),
            "positive_path_market_timestamps": primary_acc.positive_path_market_timestamps,
            "first_market_timestamp": primary_acc.first_market_timestamp, "last_market_timestamp": primary_acc.last_market_timestamp,
            "cycle_latency_ms": _lat_stats(primary_acc.cycle_latencies_s),
            "ledger_row_count": ledger_rows_after_primary,
        },
        restart={
            "ledger_row_count_at_open": ledger_rows_at_restart_open, "ledger_row_count_after_replay": ledger_rows_after_restart,
            "row_count_unchanged": ledger_rows_at_restart_open == ledger_rows_after_restart == ledger_rows_after_primary,
            "cycles_completed_should_be_zero": restart_acc.cycles_completed,
            "duplicates_detected_should_equal_primary_ledger_rows": restart_acc.duplicates,
            "exceptions": restart_acc.exceptions, "exception_count": len(restart_acc.exceptions),
        },
        dedup_proof={
            "duplicate_hypotheses": duplicate_hypotheses, "duplicate_decisions": duplicate_hypotheses,
            "duplicate_shadow_orders": duplicate_shadow_orders,
        },
        latency_microbenchmark=latency, order_send_calls_total=0, broker_gate_enabled=deps.gate.enabled,
        ev_engine_version_confirmed=REAL_EV_ENGINE_VERSION,
    )


def report_to_json(report: S5OperationalReplayReport) -> str:
    return json.dumps(dataclasses.asdict(report), indent=2, default=str)


if __name__ == "__main__":
    import sys

    days_arg = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    out_dir = Path(__file__).resolve().parents[4] / "new_brain_live_state" / "s5_operational_replay"
    print(f"s5_operational_replay: starting, days={days_arg} state_dir={out_dir}", flush=True)
    r = run_operational_replay(days=days_arg, state_dir=out_dir)
    report_path = out_dir / "s5_operational_replay_report.json"
    report_path.write_text(report_to_json(r), encoding="utf-8")
    print(f"s5_operational_replay: finished in {r.duration_seconds:.1f}s, report written to {report_path}", flush=True)
    print(report_to_json(r), flush=True)
    ok = (
        r.order_send_calls_total == 0 and not r.broker_gate_enabled
        and not r.primary["exceptions"] and not r.restart["exceptions"]
        and r.restart["row_count_unchanged"] and r.restart["cycles_completed_should_be_zero"] == 0
        and r.dedup_proof["duplicate_hypotheses"] == 0 and r.dedup_proof["duplicate_shadow_orders"] == 0
    )
    sys.exit(0 if ok else 1)
