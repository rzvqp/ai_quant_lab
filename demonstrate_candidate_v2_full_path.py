"""Phase 2 step 6/CANDIDATE_V2 evidence script -- CEO mandate 2026-08-16: demonstrate the COMPLETE real
path (MT5 closed bars -> N1/N2 -> IPC -> isolated tower worker -> real N3/N4 -> Router -> Eligibility ->
EV -> N6 -> Risk Manager -> Execution Adapter -> broker gate BLOCKED) against the genuinely installed
`ve_tower` 0.3.0, on REAL, live-read MT5 data -- and separately prove the CEO's stronger requirement: a
CANDIDATE FULLY APPROVED UPSTREAM still reaches the broker barrier and is refused there, with ZERO
`order_send` calls and broker state (positions/orders) unchanged before vs. after.

**Why two proofs, not one.** The real live path (part 1) demonstrates the WIRING is real end-to-end --
but today's real market data cannot be guaranteed to produce a TRADE/SHADOW_TRADE_CANDIDATE (an honest,
disclosed remaining gap: `probability_inputs` is still always `None` -- see `bridge.py`'s own docstring),
so whatever N6 decides live is reported HONESTLY, never coerced. The CEO's own stronger property --
"a candidate every upstream stage approved STILL never reaches the broker" -- needs a candidate that IS
fully approved, which requires the SAME established pattern this codebase already uses for it (test 8,
test 16, test 17 in `tests/test_e2e_readiness.py`): a real `ve_brain.DecisionResponse`/`DecisionProvenance`
constructed directly in the shape N6 itself produces for a genuine SHADOW_TRADE_CANDIDATE, run through the
REAL, unmodified `submit_new_brain_candidate` -> `risk_manager_live.evaluate_trade_proposal` -> REAL
`attempt_shadow_execution` -> REAL `BrokerOrderSubmissionGate` (default-closed, never constructed
`enabled=True` anywhere in this file). This is not a weaker proof than "wait for a live TRADE" -- it is
the ONLY proof that isolates "does the barrier hold" from "did the market happen to offer an edge today,"
which is what the CEO's own section 3 amendment (2026-08-14) explicitly requires.

**Read-only MT5 use throughout** -- only `terminal_info`/`account_info`/`copy_rates_from`/`positions_get`/
`orders_get` are ever called (via `RealMT5Gateway`, whose own Protocol declares no order-submitting
method at all -- see `execution_engine/adapters/mt5_gateway.py`'s own docstring). `order_send` is never
imported, never called, anywhere in this file.

Lives at the repo root, deliberately NOT inside `ai_trader/mandate2_readiness/` -- that package's own
static import-independence guard (`tests/test_import_independence.py`) forbids ANY of its production
source files from importing execution-capable packages (`execution_engine`, `mt5_demo_execution`, ...),
structurally, regardless of what the importing code actually does with them. This script's read-only use
of `RealMT5Gateway` is real and safe, but it is still, textually, an import from that forbidden family --
so it lives outside the package boundary that guard protects, as evidence/tooling, not production code.

Run with the main venv's own Python, from the repo root:
    venv\\Scripts\\python.exe demonstrate_candidate_v2_full_path.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import ve_brain  # type: ignore[import-untyped]  # noqa: E402

from ai_trader.execution_engine.adapters.mt5_gateway import RealMT5Gateway  # noqa: E402
from ai_trader.live_signal_source.types import Bar  # noqa: E402
from ai_trader.mandate2_readiness.broker_gate import BrokerOrderSubmissionGate  # noqa: E402
from ai_trader.mandate2_readiness.decision_provenance import NEW_BRAIN_SOURCE, DecisionProvenance  # noqa: E402
from ai_trader.mandate2_readiness.event_identity import EventIdentity  # noqa: E402
from ai_trader.new_brain_bridge.bridge import NewBrainOutcome, TowerDependencies, evaluate_bar  # noqa: E402
from ai_trader.new_brain_bridge.execution_shadow import attempt_shadow_execution  # noqa: E402
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder  # noqa: E402
from ai_trader.new_brain_bridge.risk_gate import submit_new_brain_candidate  # noqa: E402
from ai_trader.new_brain_bridge.tower_bar_source import fetch_tower_bar_windows  # noqa: E402
from ai_trader.new_brain_bridge.tower_client import TowerClient, TowerClientConfig, TowerN3N4Result  # noqa: E402
from ai_trader.new_brain_bridge.tower_launcher import EstablishedSession, TowerWorkerLauncher  # noqa: E402
from ai_trader.new_brain_bridge.tower_protocol import PROTOCOL_VERSION, REQUEST_SCHEMA_VERSION, TowerRequest  # noqa: E402
from ai_trader.risk_manager_live.tests._fixtures import (  # noqa: E402
    make_account,
    make_config,
    make_instrument,
    make_portfolio,
    make_risk_context,
)

SYMBOL = "XAUUSD"
MT5_TIMEFRAME_M15 = 15
BAR_SECONDS_M15 = 900
TOWER_VENV_PYTHON = Path("C:/Users/MEDION GAMING/ve_tower_venv/Scripts/python.exe")


def _read_broker_state(gateway: RealMT5Gateway) -> dict[str, object]:
    positions = gateway.positions_get()
    orders = gateway.orders_get()
    account = gateway.account_info()
    return {
        "positions_total": 0 if positions is None else len(positions),
        "orders_total": 0 if orders is None else len(orders),
        "balance": None if account is None else account.balance,
        "equity": None if account is None else account.equity,
    }


def _fetch_m15_history(gateway: RealMT5Gateway, *, count: int, now: int) -> list[Bar]:
    rates = gateway.copy_rates_from(SYMBOL, MT5_TIMEFRAME_M15, now, count)
    if rates is None:
        raise RuntimeError(f"copy_rates_from({SYMBOL!r}) returned None -- {gateway.last_error()}")
    bars: list[Bar] = []
    for rate in rates:
        ts_open = int(rate["time"]) if not hasattr(rate, "time") else int(rate.time)
        open_ = float(rate["open"]) if not hasattr(rate, "open") else float(rate.open)
        high = float(rate["high"]) if not hasattr(rate, "high") else float(rate.high)
        low = float(rate["low"]) if not hasattr(rate, "low") else float(rate.low)
        close = float(rate["close"]) if not hasattr(rate, "close") else float(rate.close)
        ts_close = ts_open + BAR_SECONDS_M15
        if ts_close > now:
            continue  # still forming
        bars.append(Bar(symbol=SYMBOL, ts_open=ts_open, ts_close=ts_close, open=open_, high=high,
                         low=low, close=close, volume=100.0))
    bars.sort(key=lambda b: b.ts_open)
    return bars


def part1_real_live_path(gateway: RealMT5Gateway, session: EstablishedSession) -> dict[str, object]:
    """The real path, real data, honest result -- whatever N6 actually decides is reported, never
    coerced toward TRADE."""
    now = int(time.time())
    bars = _fetch_m15_history(gateway, count=250, now=now)
    if len(bars) < 20:
        raise RuntimeError(f"only {len(bars)} closed M15 bars available -- insufficient for a real demo")

    builder = RawAxesBuilder(SYMBOL)
    for bar in bars[:-1]:
        builder.observe(bar)
    last_bar = bars[-1]

    tower_client = TowerClient(
        TowerClientConfig(host=session.host, port=session.port, timeout_seconds=15.0), session=session,
    )
    tower = TowerDependencies(client=tower_client, gateway=gateway, now=now, m15_count=200, m5_count=300)

    outcomes = evaluate_bar(last_bar, timeframe="M15", axes_builder=builder, bias_direction="LONG", tower=tower)
    trend_pullback = next(o for o in outcomes if o.strategy_id == "trend_pullback")

    node_summary = [
        {"node": t.node_name, "reason_codes": list(t.reason_codes)} for t in trend_pullback.node_traces
    ]
    tower_trace = next((t for t in trend_pullback.node_traces if t.node_name == "Tower"), None)

    return {
        "last_bar_ts_close": last_bar.ts_close,
        "bars_observed": builder.bars_observed,
        "decision": None if trend_pullback.decision is None else trend_pullback.decision.decision,
        "reason_codes": [] if trend_pullback.decision is None else list(trend_pullback.decision.reason_codes),
        "node_trace_sequence": node_summary,
        "tower_reason_codes": [] if tower_trace is None else list(tower_trace.reason_codes),
        "tower_version": None if tower_trace is None else tower_trace.component_version,
    }


def part1b_direct_tower_probe_on_live_data(gateway: RealMT5Gateway, session: EstablishedSession) -> dict[str, object]:
    """A direct N3/N4 call over real IPC against TODAY's real M15/M5 windows -- independent of whatever
    the Router happens to decide this cycle (see `part1_real_live_path`'s own docstring: today's regime
    may be `UNCERTAIN_REGIME`, which stops `trend_pullback` at the Router before the tower is ever
    queried). This isolates "does IPC -> worker izolat -> real N3/N4 genuinely work against live data"
    from "did the market happen to route to a trend strategy today" -- the same separation of concerns
    `part2` applies to the broker barrier."""
    now = int(time.time())
    m15_bars, m5_bars = fetch_tower_bar_windows(gateway, symbol=SYMBOL, now=now, m15_count=200, m5_count=300)

    tower_client = TowerClient(
        TowerClientConfig(host=session.host, port=session.port, timeout_seconds=15.0), session=session,
    )
    request = TowerRequest(
        protocol_version=PROTOCOL_VERSION, schema_version=REQUEST_SCHEMA_VERSION,
        request_id=f"candidate-v2-direct-probe-{now}", market_event_id=f"{SYMBOL}:M15:{now}",
        event_fingerprint="", data_identity="candidate-v2-direct-probe-data-identity",
        node_input_fingerprint="candidate-v2-direct-probe-node-input",
        symbol=SYMBOL, as_of=str(now),
        n1_output={"available": True, "fingerprint": "candidate-v2-direct-probe-n1"},
        n2_output={"available": True, "fingerprint": "candidate-v2-direct-probe-n2", "bias_direction": "LONG"},
        m15_closed_bars=m15_bars, m5_closed_bars=m5_bars,
        strategy_id="candidate-v2-direct-probe", strategy_version="1.0",
    )
    result = tower_client.request_n3_n4(request)

    if isinstance(result, TowerN3N4Result):
        market_map = None if result.n3_output is None else result.n3_output.get("market_map")
        level_count = len(market_map) if isinstance(market_map, (list, tuple)) else None
        return {
            "ok": True, "tower_version": result.tower_version,
            "n3_market_map_available": None if result.n3_output is None else result.n3_output.get("market_map_available"),
            "n3_levels_available": None if result.n3_output is None else result.n3_output.get("levels_available"),
            "n3_level_count": level_count,
            "n4_confirmation_available": None if result.n4_output is None else result.n4_output.get("confirmation_available"),
            "reason_codes": list(result.reason_codes),
        }
    return {"ok": False, "reason": result.reason, "detail": result.detail}


def part2_fully_approved_candidate_blocked_at_broker(gateway: RealMT5Gateway) -> dict[str, object]:
    """The CEO's section-3 property: a candidate that cleared EVERY upstream stage still reaches the
    broker barrier and is refused there, with the real gate (default-closed, never overridden) and real
    broker state read before/after."""
    as_of = int(time.time())
    event_identity = EventIdentity(
        trace_id="candidate-v2-demo-trace", market_event_id="candidate-v2-demo-event", symbol=SYMBOL,
        timeframe="M15", bar_id="candidate-v2-demo-bar", market_timestamp=as_of, received_timestamp=as_of,
        brain_version=ve_brain.VE_BRAIN_VERSION, catalog_hash=ve_brain.CANONICAL_CATALOG_HASH,
        configuration_fingerprint="candidate-v2-demo-cfg",
    )
    decision = ve_brain.DecisionResponse(
        contract_id=ve_brain.OUTPUT_CONTRACT_ID, decision="SHADOW_TRADE_CANDIDATE", expected_value_net=0.5,
        expected_reward=1.0, expected_loss=0.3, estimated_cost=0.02, probability_assumptions={},
        strategy_id="trend_pullback", configuration_fingerprint="candidate-v2-demo-cfg",
        reason_codes=(ve_brain.ReasonCode.TRADE_VALIDATED_EDGE.value,), engine_version=ve_brain.ENGINE_VERSION,
    )
    provenance = DecisionProvenance(
        source=NEW_BRAIN_SOURCE, trace_id="candidate-v2-demo-trace", catalog_hash=ve_brain.CANONICAL_CATALOG_HASH,
        configuration_fingerprint="candidate-v2-demo-cfg",
    )
    outcome = NewBrainOutcome(
        event_identity=event_identity, strategy_id="trend_pullback", strategy_version="v1", node_traces=(),
        decision=decision, provenance=provenance, entry_price=2000.0, stop_price=1990.0, target_price=2020.0,
    )

    before = _read_broker_state(gateway)

    risk_decision = submit_new_brain_candidate(
        outcome, account=make_account(), portfolio=make_portfolio(), instrument=make_instrument(),
        risk_context=make_risk_context(), risk_config=make_config(),
    )
    gate = BrokerOrderSubmissionGate()  # the only reachable default: enabled=False
    shadow_result = attempt_shadow_execution(risk_decision, gate=gate)

    after = _read_broker_state(gateway)

    return {
        "risk_manager_approved": risk_decision.approved,
        "risk_manager_reason_codes": list(risk_decision.reason_codes),
        "reached_broker_gate": shadow_result.reached_broker_gate,
        "blocked": shadow_result.blocked,
        "block_reason": shadow_result.reason,
        "gate_enabled": gate.enabled,
        "broker_state_before": before,
        "broker_state_after": after,
        "broker_state_unchanged": before == after,
    }


def main() -> int:
    gateway = RealMT5Gateway()
    if not gateway.initialize():
        print(f"MT5 initialize() failed: {gateway.last_error()}", file=sys.stderr)
        return 1

    launcher = TowerWorkerLauncher(tower_python=TOWER_VENV_PYTHON)
    evidence: dict[str, object] = {"generated_at_utc": int(time.time())}
    try:
        session = launcher.launch_and_handshake()
        if not isinstance(session, EstablishedSession):
            print(f"tower handshake FAILED: {session!r}", file=sys.stderr)
            return 1
        evidence["tower_identity"] = {
            "ve_tower_package_version": session.worker_identity.ve_tower_package_version,
            "package_build_commit": session.worker_identity.package_build_commit,
            "worker_package_version": session.worker_identity.worker_package_version,
        }

        evidence["part1_real_live_path"] = part1_real_live_path(gateway, session)
        evidence["part1b_direct_tower_probe_on_live_data"] = part1b_direct_tower_probe_on_live_data(gateway, session)
        evidence["part2_fully_approved_candidate_blocked_at_broker"] = (
            part2_fully_approved_candidate_blocked_at_broker(gateway)
        )
    finally:
        launcher.stop()
        gateway.shutdown()

    print(json.dumps(evidence, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
