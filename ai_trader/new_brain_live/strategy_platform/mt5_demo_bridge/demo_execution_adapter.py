"""S5 MT5 DEMO execution orchestrator (mandate sections 1, 6-17, 21-30, 33-34).

Consumes the ALREADY-COMPUTED, UNCHANGED `pipeline.run_cycle` result -- this module never re-implements
EV or Risk. `execute()` is only ever meant to be called once the existing, unmodified pipeline's own
verdict already shows a genuine S5 `TRADE_DECISION` that reached the (still-disabled) shadow broker gate
-- i.e. the existing Risk Engine (`risk_manager_live.evaluate_trade_proposal`) already approved it
(mandate section 34's own "strategy signal alone is insufficient", satisfied by construction: this
module is simply never reached otherwise, by whoever wires the live loop -- see `live_runtime_loop.py`).

This module's own job is everything AFTER that unchanged verdict: evidence-integrity re-check (section
33), deterministic identity + dedup (sections 12, 21), 5%-equity contract-aware sizing (sections 6-11),
full preflight (section 17), and -- only if every one of those independently passes -- the real MT5 DEMO
`order_send`, via the pre-existing, unmodified `MT5DemoBrokerAdapter` (defense in depth: that adapter
independently re-verifies DEMO status itself immediately before submitting, on top of every check this
module and the connection layer already performed -- section 4)."""

from __future__ import annotations

import dataclasses
import time

from ai_trader.execution_engine.types import (
    BracketLegs,
    OrderConstraints,
    OrderIntent,
    OrderRefs,
    OrderRequest,
    OrderSide,
    OrderType,
    TimeInForce,
)
from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.types import MT5DemoConfig
from ai_trader.new_brain_live.strategy_platform.ev_engine import TRADE_DECISION, EVDecision
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge import preflight as preflight_mod
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.gateway_ext import MT5BridgeGateway
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.mt5_execution_ledger import (
    PENDING_SUBMISSION,
    SUBMITTED_ACK,
    SUBMITTED_REJECTED,
    MT5ExecutionLedger,
    MT5ExecutionLedgerRecord,
)
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.order_identity import (
    client_order_id_for,
    decision_id_for,
)
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.risk_sizer import compute_risk_sized_volume
from ai_trader.new_brain_live.strategy_platform.s5_ev_evidence import S5_REAL_EV_EVIDENCE_V1
from ai_trader.new_brain_live.strategy_platform.trade_hypothesis import TradeHypothesis
from ai_trader.signal_engine.types import Direction

ORDER_SCHEMA_VERSION = "1.0.0"
EXECUTION_ENGINE_VERSION = "s5-mt5-demo-bridge-v1"

EVIDENCE_MISMATCH = "S5_MT5_EVIDENCE_MISMATCH"
NOT_TRADE_DECISION = "S5_MT5_NOT_TRADE_DECISION"
WRONG_STRATEGY = "S5_MT5_WRONG_STRATEGY"
EQUITY_UNAVAILABLE = "S5_MT5_EQUITY_UNAVAILABLE"
SYMBOL_CAPABILITIES_UNAVAILABLE = "S5_MT5_SYMBOL_CAPABILITIES_UNAVAILABLE"


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class DemoExecutionOutcome:
    submitted: bool
    client_order_id: str
    reason: str | None = None
    volume: float | None = None
    broker_order_ticket: int | None = None
    preflight: preflight_mod.PreflightResult | None = None


def _canonical_target_price(hypothesis: TradeHypothesis) -> float | None:
    """Reads the canonical RR target straight off the hypothesis the strategy itself produced -- NEVER
    recomputed, moved, or replaced with a fixed distance (mandate section 7). `None` for a non-"rr:"
    exit_specification (e.g. "time:40"/"none") -- an MT5 bracket simply omits `take_profit` then, exactly
    `real_ev_engine._parse_exit_specification`'s own precedent for a target-less request."""
    spec = hypothesis.exit_specification
    if not spec.startswith("rr:"):
        return None
    try:
        rr = float(spec[3:])
    except ValueError:
        return None
    risk = abs(hypothesis.intended_entry - hypothesis.invalidation)
    if hypothesis.direction is Direction.LONG:
        return hypothesis.intended_entry + rr * risk
    return hypothesis.intended_entry - rr * risk


def _read_current_equity(gateway: MT5BridgeGateway) -> float | None:
    try:
        info = gateway.account_info()
    except Exception:  # noqa: BLE001 -- any gateway failure fails closed, never a stale/estimated equity
        return None
    if info is None:
        return None
    equity = getattr(info, "equity", None)
    return float(equity) if equity is not None else None


def execute(
    *, hypothesis: TradeHypothesis, decision: EVDecision, adapter: MT5DemoBrokerAdapter,
    gateway: MT5BridgeGateway, config: MT5DemoConfig, ledger: MT5ExecutionLedger, symbol: str,
    expected_strategy_id: str, risk_fraction: float = 0.05,
) -> DemoExecutionOutcome:
    cid = client_order_id_for(hypothesis, decision)

    # section 2/28/33/34 -- genuine-signal-only gates, independently re-checked here (never trust the
    # caller alone, mirrors decide_n6's/RealEVDecisionEngine's own "AUDIT, not authoritative" discipline).
    if hypothesis.strategy_id != expected_strategy_id:
        return DemoExecutionOutcome(submitted=False, client_order_id=cid, reason=WRONG_STRATEGY)
    if decision.decision != TRADE_DECISION:
        return DemoExecutionOutcome(submitted=False, client_order_id=cid, reason=NOT_TRADE_DECISION)
    if decision.evidence_fingerprint != S5_REAL_EV_EVIDENCE_V1.evidence_fingerprint:
        return DemoExecutionOutcome(submitted=False, client_order_id=cid, reason=EVIDENCE_MISMATCH)

    pf = preflight_mod.run_preflight(
        adapter=adapter, config=config, symbol=symbol, ledger=ledger, hypothesis=hypothesis, decision=decision,
    )
    if not pf.passed:
        return DemoExecutionOutcome(submitted=False, client_order_id=cid, reason=",".join(pf.reasons), preflight=pf)

    status = adapter.status()
    equity = _read_current_equity(gateway)
    if equity is None:
        return DemoExecutionOutcome(submitted=False, client_order_id=cid, reason=EQUITY_UNAVAILABLE, preflight=pf)

    symbol_caps = adapter.symbol_capabilities(symbol)
    if symbol_caps is None:
        return DemoExecutionOutcome(submitted=False, client_order_id=cid, reason=SYMBOL_CAPABILITIES_UNAVAILABLE, preflight=pf)

    sizing = compute_risk_sized_volume(
        gateway=gateway, equity=equity, side=hypothesis.direction, symbol=symbol,
        entry_price=hypothesis.intended_entry, sl_price=hypothesis.invalidation,
        volume_min=symbol_caps.min_qty, volume_max=min(symbol_caps.max_qty, config.max_order_volume),
        volume_step=symbol_caps.lot_step, risk_fraction=risk_fraction,
    )
    if not sizing.approved:
        return DemoExecutionOutcome(submitted=False, client_order_id=cid, reason=sizing.reason, preflight=pf)

    decision_id = decision_id_for(hypothesis, decision)
    order_request_id = f"{cid}-req"
    now = int(time.time())
    tp = _canonical_target_price(hypothesis)
    assert sizing.volume is not None  # approved=True guarantees this, __post_init__-enforced

    ledger.record(MT5ExecutionLedgerRecord(
        client_order_id=cid, decision_id=decision_id, state=PENDING_SUBMISSION, as_of=now,
        strategy_id=hypothesis.strategy_id, strategy_version=hypothesis.strategy_version, symbol=symbol,
        side=hypothesis.direction.value, requested_entry=hypothesis.intended_entry,
        actual_quote_bid=pf.tick_bid, actual_quote_ask=pf.tick_ask, sl=hypothesis.invalidation, tp=tp,
        requested_volume=sizing.volume, modeled_risk_money=sizing.modeled_risk_money,
        modeled_risk_fraction=sizing.modeled_risk_fraction, account_trade_mode=str(status.account_trade_mode),
        evidence_fingerprint=decision.evidence_fingerprint, order_request_id=order_request_id,
    ))

    order = OrderRequest(
        order_schema_version=ORDER_SCHEMA_VERSION, execution_engine_version=EXECUTION_ENGINE_VERSION,
        order_request_id=order_request_id, client_order_id=cid, decision_id=decision_id,
        strategy_id=hypothesis.strategy_id, symbol=symbol, timestamp=now, as_of=now,
        side=OrderSide.BUY if hypothesis.direction is Direction.LONG else OrderSide.SELL,
        direction=hypothesis.direction, intent=OrderIntent.OPEN, order_type=OrderType.MARKET,
        time_in_force=TimeInForce.IOC, quantity=sizing.volume,
        constraints=OrderConstraints(max_slippage=None, reduce_only=False, post_only=False),
        refs=OrderRefs(risk_schema_version="1.0.0", risk_policy_version="1.0.0"),
        bracket=BracketLegs(take_profit=tp, stop_loss=hypothesis.invalidation),
    )

    ack = adapter.submit_order(order)
    now2 = int(time.time())
    pending_row = ledger.latest_state_for(cid)
    assert pending_row is not None

    if not ack.accepted:
        ledger.record(dataclasses.replace(pending_row, state=SUBMITTED_REJECTED, as_of=now2, reason=ack.reason))
        return DemoExecutionOutcome(submitted=False, client_order_id=cid, reason=ack.reason, volume=sizing.volume, preflight=pf)

    order_state = adapter.query_status(cid)
    ledger.record(dataclasses.replace(
        pending_row, state=SUBMITTED_ACK, as_of=now2,
        broker_order_ticket=int(ack.broker_order_id) if ack.broker_order_id else None,
        filled_volume=order_state.filled_qty if order_state is not None else None,
        avg_price=order_state.avg_price if order_state is not None else None,
    ))
    return DemoExecutionOutcome(
        submitted=True, client_order_id=cid, volume=sizing.volume,
        broker_order_ticket=int(ack.broker_order_id) if ack.broker_order_id else None, preflight=pf,
    )
