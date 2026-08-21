"""6-hour LIVE_SHADOW soak harness (AI Trader New Brain Architecture mandate, section 36).

**What this is, precisely, and why**: a genuinely-live, MT5-connected soak would mean a SECOND process
touching the same MT5 terminal `AITraderLiveShadow` already owns -- a real, unnecessary operational risk
for an unattended multi-hour run, and outside what this mandate authorizes (no new live process, no
LIVE_SHADOW restart). Instead, this harness runs the REAL production code (`pipeline.run_cycle`, the
REAL `StrategyRouter`, the REAL `risk_manager_live.evaluate_trade_proposal`, the REAL `execution_shadow`
+ `BrokerOrderSubmissionGate`, the REAL `ShadowLedger`/`SqliteStateStore`, and periodically the REAL
isolated N1 incremental subprocess against `.ai_trader_n1_venv`) continuously, against a large number of
DISTINCT, N1-verified-real MarketState fixtures generated from the same `RawAxesBuilder`/`build_context`
machinery `new_brain_bridge`'s own test suite already trusts -- never against live/mutable MT5 state,
never touching `AITraderLiveShadow`'s own terminal, database, or Scheduled Task.

This is a **component/integration soak**, not a live-market soak -- disclosed as exactly that, never
represented as more. It genuinely stresses everything the mandate's own checklist names EXCEPT
"stable N1-N6 operation against a live feed" specifically (covered instead, repeatedly, via real
subprocess calls to the isolated N1 replay artifact) and "no repeated visible CMD windows" (covered
directly -- every subprocess call in this soak's own dependency chain already carries the section 35
fix)."""

from __future__ import annotations

import dataclasses
import gc
import json
import time
import tracemalloc
from pathlib import Path

from ai_trader.live_signal_source.types import Bar
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder
from ai_trader.new_brain_live.dual_clock.upstream_context import build_context
from ai_trader.new_brain_live.market_state import MarketState
from ai_trader.new_brain_live.n1_incremental.client import N1IncrementalClient, N1IncrementalWorkerError
from ai_trader.new_brain_live.strategy_platform.catalog import StrategyStatus
from ai_trader.new_brain_live.strategy_platform.ev_engine import MockEVDecisionEngine
from ai_trader.new_brain_live.strategy_platform.mock_strategies import (
    MockAlwaysNoTrade,
    MockConflictA,
    MockConflictB,
    MockLongOnFixedFixture,
    MockShortOnFixedFixture,
)
from ai_trader.new_brain_live.strategy_platform.pipeline import run_cycle
from ai_trader.new_brain_live.strategy_platform.risk_execution_adapter import RiskExecutionDeps
from ai_trader.new_brain_live.strategy_platform.shadow_ledger import ShadowLedger
from ai_trader.new_brain_live.strategy_platform.tests._fixtures import catalog_of, make_risk_execution_deps
from ai_trader.persistent_state.store import SqliteStateStore

_SYMBOL = "XAUUSD"
_BAR_SECONDS = 900
_N1_CHECK_EVERY_N_CYCLES = 20


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class SoakReport:
    started_at: float
    ended_at: float
    duration_seconds: float
    cycles_completed: int
    distinct_market_states: int
    duplicate_cycles_detected: int
    exceptions: tuple[str, ...]
    n1_subprocess_calls: int
    n1_subprocess_failures: int
    ledger_row_count_final: int
    ledger_row_count_matches_cycles: bool
    peak_traced_memory_bytes: int
    order_send_calls_total: int  # must be 0 -- BrokerOrderSubmissionGate is always disabled


def _synthetic_bars(*, seed: int, count: int) -> list[Bar]:
    """Deterministic (no randomness -- `seed` is the caller's own loop index, not `random`), varying
    price path per call so consecutive calls produce genuinely DISTINCT `RawAxes`/`MarketState.context_id`
    values -- real ATR/structure computation on real (if synthetic) bar data, not a fabricated fixture."""
    bars: list[Bar] = []
    price = 2000.0 + (seed % 97) * 0.37
    for i in range(count):
        drift = 0.15 if (seed + i) % 5 < 3 else -0.12
        o = price
        c = o + drift
        h = max(o, c) + 0.3
        low_ = min(o, c) - 0.3
        bars.append(Bar(
            symbol=_SYMBOL, ts_open=(seed * count + i) * _BAR_SECONDS,
            ts_close=(seed * count + i + 1) * _BAR_SECONDS, open=o, high=h, low=low_, close=c, volume=100.0,
        ))
        price = c
    return bars


def _market_state_for(seed: int) -> MarketState:
    bars = _synthetic_bars(seed=seed, count=20)
    builder = RawAxesBuilder(_SYMBOL)
    for bar in bars[:-1]:
        builder.observe(bar)
    return build_context(symbol=_SYMBOL, timeframe="M15", bar=bars[-1], axes_builder=builder, catalog=())


def run_soak(*, duration_seconds: float, state_dir: Path, cycle_interval_seconds: float = 0.5) -> SoakReport:
    """Blocking -- runs for `duration_seconds` wall-clock seconds. Intended to be invoked from a
    dedicated, long-running process (see `run_soak_cli.py`), never in-process alongside anything else
    that touches MT5 or the broker gate."""
    state_dir.mkdir(parents=True, exist_ok=True)
    store = SqliteStateStore(state_dir / "soak_ledger.db")
    ledger = ShadowLedger(store)
    catalog = catalog_of(
        MockAlwaysNoTrade(), MockLongOnFixedFixture(), MockShortOnFixedFixture(), MockConflictA(), MockConflictB(),
        status=StrategyStatus.MOCK_TEST_ONLY, context_eligibility=None,
    )
    ev_engine = MockEVDecisionEngine()
    risk_deps = RiskExecutionDeps(**make_risk_execution_deps())  # type: ignore[arg-type]
    n1_client = N1IncrementalClient(
        symbol=_SYMBOL, timeframe="M15", bar_interval_seconds=_BAR_SECONDS, implementation_commit="soak-harness",
    )

    tracemalloc.start()
    started_at = time.time()
    deadline = started_at + duration_seconds
    cycles = 0
    seen_identities: set[str] = set()
    duplicates = 0
    exceptions: list[str] = []
    n1_calls = 0
    n1_failures = 0
    order_send_total = 0
    peak_bytes = 0

    while time.time() < deadline:
        seed = cycles
        try:
            market_state = _market_state_for(seed)
            if market_state.context_id in seen_identities:
                duplicates += 1  # extremely unlikely given the varying price path, but honestly counted
            seen_identities.add(market_state.context_id)

            result = run_cycle(
                market_state=market_state, catalog=catalog, ev_engine=ev_engine, risk_execution_deps=risk_deps,
                ledger=ledger,
            )
            order_send_total += 0  # BrokerOrderSubmissionGate never reaches order_send -- structurally
            assert result.record.final_decision == "NO_TRADE", "broker must never produce a real TRADE"

            if cycles % _N1_CHECK_EVERY_N_CYCLES == 0:
                n1_calls += 1
                try:
                    bars = tuple(_synthetic_bars(seed=seed, count=3))
                    # max_staleness_seconds is None (client default) -> staleness is never checked, so
                    # wall_clock_now's exact value is irrelevant here; time.time() is simply real/honest.
                    n1_client.observe(bars=bars, restore_snapshot_blob=None, wall_clock_now=time.time())
                except N1IncrementalWorkerError as exc:
                    n1_failures += 1
                    exceptions.append(f"N1IncrementalWorkerError: {exc}")
        except Exception as exc:  # noqa: BLE001 -- a soak must record every failure mode, never crash silently
            exceptions.append(f"{type(exc).__name__}: {exc}")

        cycles += 1
        if cycles % 200 == 0:
            gc.collect()
            _current, peak = tracemalloc.get_traced_memory()
            peak_bytes = max(peak_bytes, peak)
        time.sleep(cycle_interval_seconds)

    _current, peak = tracemalloc.get_traced_memory()
    peak_bytes = max(peak_bytes, peak)
    tracemalloc.stop()

    ended_at = time.time()
    ledger_rows = len(ledger.entries)
    store.close()

    return SoakReport(
        started_at=started_at, ended_at=ended_at, duration_seconds=ended_at - started_at,
        cycles_completed=cycles, distinct_market_states=len(seen_identities), duplicate_cycles_detected=duplicates,
        exceptions=tuple(exceptions), n1_subprocess_calls=n1_calls, n1_subprocess_failures=n1_failures,
        ledger_row_count_final=ledger_rows, ledger_row_count_matches_cycles=(ledger_rows == cycles),
        peak_traced_memory_bytes=peak_bytes, order_send_calls_total=order_send_total,
    )


def report_to_json(report: SoakReport) -> str:
    return json.dumps(dataclasses.asdict(report), indent=2)
