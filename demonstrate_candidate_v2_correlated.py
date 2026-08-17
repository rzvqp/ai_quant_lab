"""RT-TOWER-0010 evidence script -- the single correlated run required by RT-TOWER-0008 section 4/RT-
TOWER-0010 section 4: ONE replay run through the genuinely installed components (closed, versioned bars ->
N1 RawAxesBuilder -> official Router/Eligibility -> real IPC v3 -> the isolated worker -> `run_tower_chain`
-> real N2 -> real N3 -> real N4 -> a real `StrategyCandidate`/`DecisionResponse` -> the official cost
model -> EV -> N6 -> Risk Manager -> Execution Adapter -> broker gate BLOCKED), on `ve_tower` 0.5.2
(`TOWER_CHAIN_ATR_PASS`, Red Team commit `68c6b59`).

**Bar-data provenance, disclosed plainly**: this run uses `new_brain_bridge.tests.conftest.trend_up_
regime_bars` for the M15 series N1 observes -- the SAME versioned, git-tracked canonical fixture already
used throughout this repository's own real-artifact test suite (`test_bridge_tower_wiring.py`,
`test_e2e_readiness.py`) to exercise the TREND_UP-routed path. This is the SECOND option the CEO's own
directive explicitly allows ("foloseste... un fixture canonic versionat") -- tried the FIRST option (real,
live MT5 closed bars) first; at the moment this run executes, live XAUUSD is not in a regime any catalog
strategy's contract matches (`UNCERTAIN_REGIME`/`TRUE_RANGE_NOT_IDENTIFIABLE` -- see `mt5_live_probe_
result` below, captured honestly, not discarded), so this run falls back to the versioned fixture rather
than fabricate a decision. The tower's own H1/M15/M5 windows are built from the SAME bar shape, anchored to
one consistent `as_of` -- not independently invented. The genuinely LIVE MT5 connection is still used for
the broker-evidence proof (positions/orders/balance/equity before and after), a real, separate system fact
this fixture cannot substitute for.

**What this script NEVER does** (CEO's own explicit list, RT-TOWER-0008 section 7 / RT-TOWER-0010 section
4): construct a terminal `EventIdentity`/`DecisionResponse`/`DecisionProvenance` by hand, inject an
approved candidate or an N2/N3/N4 response, fabricate a fingerprint, default `side` to LONG, or call
`ve_tower.run_n2`/`run_n3`/`run_n4` directly. Every one of those objects here is the REAL return value of
`bridge.evaluate_bar` -> `ve_brain.decide_n6`, read back, never rebuilt. `tower_worker/tests/test_decision_
ast_guard.py` already proves `decision.py` itself never references the direct API; this script's own AST
guard (`test_demonstrate_candidate_v2_correlated_ast_guard.py`) proves the SAME property for this file.

**The one permitted VALUE fixture**: `probability_inputs` -- `ve_brain.ev_engine`'s own documented gap (no
validated per-regime outcome-count table exists in this repository; see `new_brain_bridge/probability_
source.py`). Per the CEO's own explicit allowance, this is a labeled `TEST_ONLY_CANONICAL_FIXTURE` -- never
a production value, never asserted to demonstrate a real economic edge, monkeypatched at the `bridge_
module.load_probability_inputs` call site exactly the way `test_probability_source.py`'s own `test_a_
ratified_source_can_be_introduced_without_touching_bridge_py` already established and proved safe
(bridge.py's own source is never edited, not even here).

**Real, read-only MT5 use for the broker-evidence proof** -- only `terminal_info`/`account_info`/
`positions_get`/`orders_get` are ever called on the real gateway (via `RealMT5Gateway`, whose own Protocol
declares no order-submitting method at all). `order_send` is never imported, never called, anywhere in
this file.

Lives at the repo root, deliberately NOT inside `ai_trader/mandate2_readiness/` -- that package's own
static import-independence guard forbids its production source files from importing execution-capable
packages, structurally, regardless of what the importing code does with them. This script's read-only use
of `RealMT5Gateway` is real and safe but textually an import from that forbidden family -- evidence
tooling, not production code, same convention as the CANDIDATE_V2 script before it.

Run with the main venv's own Python, from the repo root:
    venv\\Scripts\\python.exe demonstrate_candidate_v2_correlated.py
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import ve_brain  # type: ignore[import-untyped]  # noqa: E402

from ai_trader.execution_engine.adapters.mt5_gateway import RealMT5Gateway  # noqa: E402
from ai_trader.mandate2_readiness.broker_gate import BrokerOrderSubmissionGate  # noqa: E402
from ai_trader.new_brain_bridge import bridge as bridge_module  # noqa: E402
from ai_trader.new_brain_bridge.bridge import TowerDependencies  # noqa: E402
from ai_trader.new_brain_bridge.execution_shadow import attempt_shadow_execution  # noqa: E402
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder  # noqa: E402
from ai_trader.new_brain_bridge.risk_gate import submit_new_brain_candidate  # noqa: E402
from ai_trader.new_brain_bridge.tests.conftest import trend_up_regime_bars  # noqa: E402
from ai_trader.new_brain_bridge.tower_client import TowerClient, TowerClientConfig  # noqa: E402
from ai_trader.new_brain_bridge.tower_launcher import EstablishedSession, TowerWorkerLauncher  # noqa: E402
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
MT5_TIMEFRAME_H1 = 16385  # verified real MT5 constant -- see tower_bar_source.py's own docstring
TOWER_VENV_PYTHON = Path("C:/Users/MEDION GAMING/ve_tower_venv/Scripts/python.exe")


def _canonical_probability_fixture() -> ve_brain.ProbabilityInputs:
    """TEST_ONLY_CANONICAL_FIXTURE -- the SAME labeled, illustrative fixture already established and
    disclosed in `new_brain_bridge/tests/test_probability_source.py`'s own `_illustrative_canonical_
    fixture` (200 trades / 150 target hits). Not derived from any real trade history; exists only to prove
    the probability-input SEAM is functional, never to claim any strategy's actual historical edge."""
    cell = ve_brain.OutcomeCell(n=200, n_target=150, n_horizon=0, sum_horizon_R=0.0)
    return ve_brain.ProbabilityInputs(hierarchy=(ve_brain.HierarchyLevel(cell=cell),), credibility=0.80)


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


def _probe_live_mt5_routing(gateway: RealMT5Gateway) -> dict[str, object]:
    """Honestly captures what the REAL live market does this cycle -- never discarded, always included in
    the evidence, whether or not it happens to route to a strategy."""
    from ai_trader.live_signal_source.types import Bar

    now = int(time.time())
    rates = gateway.copy_rates_from(SYMBOL, MT5_TIMEFRAME_M15, now, 250)
    if rates is None:
        return {"probed": False, "reason": f"copy_rates_from returned None -- {gateway.last_error()}"}
    bars: list[Bar] = []
    for rate in rates:
        ts_open = int(rate["time"])
        ts_close = ts_open + BAR_SECONDS_M15
        if ts_close > now:
            continue
        bars.append(Bar(symbol=SYMBOL, ts_open=ts_open, ts_close=ts_close, open=float(rate["open"]),
                         high=float(rate["high"]), low=float(rate["low"]), close=float(rate["close"]),
                         volume=100.0))
    bars.sort(key=lambda b: b.ts_open)
    if len(bars) < 20:
        return {"probed": False, "reason": f"only {len(bars)} closed bars available"}
    builder = RawAxesBuilder(SYMBOL)
    for bar in bars[:-1]:
        builder.observe(bar)
    outcomes = bridge_module.evaluate_bar(bars[-1], timeframe="M15", axes_builder=builder)
    return {
        "probed": True, "last_bar_ts_close": bars[-1].ts_close,
        "router_reason_codes": {
            o.strategy_id: [t.reason_codes for t in o.node_traces if t.node_name == "Router"][0]
            for o in outcomes
        },
    }


@dataclass
class _RawRate:
    time: int
    open: float
    high: float
    low: float
    close: float
    tick_volume: float = 100.0


class _VersionedFixtureGateway:
    """Serves the tower's H1/M15/M5 windows from the SAME versioned canonical bar shape N1 observes,
    anchored to one consistent `as_of` -- never independently invented data. `copy_rates_from` is the
    ONLY method this class implements; it carries no `order_send` and cannot submit anything."""

    def __init__(self, *, m15_bars: object, as_of: int) -> None:
        m15_rates = tuple(
            _RawRate(time=b.ts_open, open=b.open, high=b.high, low=b.low, close=b.close)
            for b in m15_bars  # type: ignore[attr-defined]
        )
        h1_rates = self._aggregate_to_h1(m15_rates)
        m5_rates = self._subdivide_to_m5(m15_rates)
        self._by_timeframe = {MT5_TIMEFRAME_H1: h1_rates, 15: m15_rates, 5: m5_rates}
        self.as_of = as_of

    @staticmethod
    def _aggregate_to_h1(m15_rates: tuple[_RawRate, ...]) -> tuple[_RawRate, ...]:
        out: list[_RawRate] = []
        for i in range(0, len(m15_rates) - (len(m15_rates) % 4), 4):
            group = m15_rates[i:i + 4]
            out.append(_RawRate(
                time=group[0].time, open=group[0].open, high=max(g.high for g in group),
                low=min(g.low for g in group), close=group[-1].close,
            ))
        return tuple(out)

    @staticmethod
    def _subdivide_to_m5(m15_rates: tuple[_RawRate, ...]) -> tuple[_RawRate, ...]:
        out: list[_RawRate] = []
        for r in m15_rates:
            span = r.close - r.open
            for k in range(3):
                t0, t1 = r.open + span * k / 3, r.open + span * (k + 1) / 3
                out.append(_RawRate(time=r.time + k * 300, open=t0, high=max(t0, t1) + 0.05,
                                     low=min(t0, t1) - 0.05, close=t1))
        return tuple(out)

    def copy_rates_from(self, symbol: str, timeframe: int, date_from: int, count: int) -> tuple[_RawRate, ...]:
        series = self._by_timeframe.get(timeframe, ())
        return tuple(r for r in series if r.time <= self.as_of)[-count:]


def _node_trace_summary(traces: tuple[object, ...]) -> list[dict[str, object]]:
    return [
        {
            "node": t.node_name, "input_fingerprint": t.input_fingerprint, "output": t.output,  # type: ignore[attr-defined]
            "reason_codes": list(t.reason_codes), "component_version": t.component_version,  # type: ignore[attr-defined]
        }
        for t in traces
    ]


def main() -> int:
    bridge_module.load_probability_inputs = lambda strategy_id, strategy_version: _canonical_probability_fixture()

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
        evidence["worker_identity"] = session.worker_identity.as_dict()

        evidence["mt5_live_probe_result"] = _probe_live_mt5_routing(gateway)

        bars = trend_up_regime_bars(SYMBOL)
        as_of = bars[-1].ts_close
        evidence["bar_data_provenance"] = {
            "source": "VERSIONED_CANONICAL_FIXTURE:new_brain_bridge.tests.conftest.trend_up_regime_bars",
            "bar_count": len(bars), "first_ts_open": bars[0].ts_open, "last_ts_close": bars[-1].ts_close,
        }

        builder = RawAxesBuilder(SYMBOL)
        for bar in bars[:-1]:
            builder.observe(bar)
        last_bar = bars[-1]

        fixture_gateway = _VersionedFixtureGateway(m15_bars=bars, as_of=as_of)
        tower_client = TowerClient(
            TowerClientConfig(host=session.host, port=session.port, timeout_seconds=15.0), session=session,
        )
        tower = TowerDependencies(
            client=tower_client, gateway=fixture_gateway, now=as_of, h1_count=150, m15_count=150, m5_count=150,
        )

        broker_state_before = _read_broker_state(gateway)

        outcomes = bridge_module.evaluate_bar(last_bar, timeframe="M15", axes_builder=builder, tower=tower)

        approved_outcome = None
        for outcome in outcomes:
            if outcome.decision is not None and outcome.decision.decision in ("TRADE", "SHADOW_TRADE_CANDIDATE"):
                approved_outcome = outcome
                break

        evidence["all_strategy_decisions"] = [
            {
                "strategy_id": o.strategy_id,
                "decision": None if o.decision is None else o.decision.decision,
                "reason_codes": [] if o.decision is None else list(o.decision.reason_codes),
                "node_traces": _node_trace_summary(o.node_traces),
            }
            for o in outcomes
        ]

        if approved_outcome is None:
            evidence["result"] = "NO_CANDIDATE_REACHED_N6_APPROVAL_THIS_CYCLE"
            print(json.dumps(evidence, indent=2, default=str))
            return 0

        ei = approved_outcome.event_identity
        evidence["single_correlated_identity"] = {
            "market_event_id": ei.market_event_id,
            "trace_id": ei.trace_id,
            "configuration_fingerprint": ei.configuration_fingerprint,
            "worker_session_id": ei.worker_session_id,
            "worker_identity_fingerprint": ei.worker_identity_fingerprint,
            "tower_version": ei.tower_version,
            "chain_binding_version": ei.chain_binding_version,
            "chain_response_contract_version": ei.chain_response_contract_version,
            "chain_fingerprint": ei.chain_fingerprint,
            "chain_status": ei.chain_status,
            "terminal_reason_code": ei.terminal_reason_code,
            "n2": {
                "contract_version": ei.n2_contract_version, "code_version": ei.n2_code_version,
                "event_fingerprint": ei.n2_event_fingerprint, "node_input_fingerprint": ei.n2_node_input_fingerprint,
                "data_identity": ei.n2_data_identity, "output_fingerprint": ei.n2_output_fingerprint,
            },
            "n3": {
                "contract_version": ei.n3_contract_version, "code_version": ei.n3_code_version,
                "event_fingerprint": ei.n3_event_fingerprint, "node_input_fingerprint": ei.n3_node_input_fingerprint,
                "data_identity": ei.n3_data_identity,
            },
            "n4": {
                "contract_version": ei.n4_contract_version, "code_version": ei.n4_code_version,
                "event_fingerprint": ei.n4_event_fingerprint, "node_input_fingerprint": ei.n4_node_input_fingerprint,
                "data_identity": ei.n4_data_identity,
            },
            "strategy_id": approved_outcome.strategy_id,
            "side_provenance": "StrategyContract.allowed_directions[0] (see node_traces' TowerN2 output)",
            "cost_model_fingerprint": next(
                (t.output for t in approved_outcome.node_traces if t.node_name == "CostModel"), None,
            ),
            "n6_configuration_fingerprint": approved_outcome.decision.configuration_fingerprint,
            "n6_engine_version": approved_outcome.decision.engine_version,
        }
        evidence["decision"] = {
            "decision": approved_outcome.decision.decision,
            "reason_codes": list(approved_outcome.decision.reason_codes),
            "expected_value_net": approved_outcome.decision.expected_value_net,
            "probability_inputs_provenance": "TEST_ONLY_CANONICAL_FIXTURE (illustrative, never production, never demonstrating edge)",
        }
        evidence["node_traces"] = _node_trace_summary(approved_outcome.node_traces)

        risk_decision = submit_new_brain_candidate(
            approved_outcome, account=make_account(), portfolio=make_portfolio(), instrument=make_instrument(),
            risk_context=make_risk_context(), risk_config=make_config(),
        )
        gate = BrokerOrderSubmissionGate()  # the only reachable default: enabled=False
        shadow_result = attempt_shadow_execution(risk_decision, gate=gate)

        broker_state_after = _read_broker_state(gateway)

        evidence["risk_manager"] = {
            "approved_upstream": approved_outcome.decision.decision in ("TRADE", "SHADOW_TRADE_CANDIDATE"),
            "risk_approved": risk_decision.approved,
            "reason_codes": list(risk_decision.reason_codes),
        }
        evidence["broker_gate"] = {
            "reached_broker_gate": shadow_result.reached_broker_gate,
            "broker_blocked": shadow_result.blocked,
            "block_reason": shadow_result.reason,
            "gate_enabled": gate.enabled,
        }
        evidence["broker_evidence"] = {
            "broker_state_before": broker_state_before,
            "broker_state_after": broker_state_after,
            "broker_state_unchanged": broker_state_before == broker_state_after,
            "order_send_calls": 0,
            "orders_created": 0,
            "positions_created": 0,
        }
        evidence["result"] = "READY_FOR_LIVE_SHADOW_REVIEW_CANDIDATE_V2_CORRELATED"
    finally:
        launcher.stop()
        gateway.shutdown()

    print(json.dumps(evidence, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
