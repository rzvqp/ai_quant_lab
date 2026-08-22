"""Core safety-critical proof suite (mandate section 37). Covers: the DEMO-only account hard gate
(accept/reject matrix + account-switch mid-session + missing account info), genuine-signal-only gates
(wrong strategy, wrong/missing evidence, NO_TRADE never submits), dedup/restart, existing-position
reconciliation interacting with fresh submission, and the full canonical pipeline reaching this adapter
with zero fixture shortcuts for the account-type/evidence checks themselves."""

from __future__ import annotations

import dataclasses
from pathlib import Path
from types import SimpleNamespace

from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.types import MT5DemoConfig
from ai_trader.new_brain_live.strategy_platform import pipeline
from ai_trader.new_brain_live.strategy_platform.catalog import StrategyCatalog
from ai_trader.new_brain_live.strategy_platform.ev_engine import NO_TRADE, TRADE_DECISION
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge import demo_execution_adapter
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.preflight import DUPLICATE_IDENTITY
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.tests._fixtures import (
    FakeMT5BridgeGateway,
    make_connected_demo_adapter,
    make_ledger,
    make_no_trade_decision,
    make_s5_hypothesis,
    make_trade_decision,
    real_s5_catalog_entry,
)
from ai_trader.new_brain_live.strategy_platform.real_ev_engine import CostModel, RealEVDecisionEngine
from ai_trader.new_brain_live.strategy_platform.router import StrategyRouter
from ai_trader.new_brain_live.strategy_platform.s5_ev_evidence import S5_REAL_EV_EVIDENCE_V1
from ai_trader.new_brain_live.strategy_platform.s5_opening_range_breakout import (
    ENTRY_WINDOW_FIRST_BIS,
    STRATEGY_ID,
)
from ai_trader.new_brain_live.strategy_platform.tests.test_s5_opening_range_breakout import _fixture, _session_bar

SYMBOL = "XAUUSD"
_CONFIG = MT5DemoConfig(max_order_volume=1.0, expected_server="FusionMarkets-Demo")


def _connect(*, account_trade_mode: int = 0) -> tuple[FakeMT5BridgeGateway, MT5DemoBrokerAdapter]:
    gw = FakeMT5BridgeGateway(account_trade_mode=account_trade_mode)
    adapter = make_connected_demo_adapter(gw, config=_CONFIG)
    return gw, adapter


# ═══ account-type hard gate (sections 3-4, 31-32) ═══

def test_demo_account_accepted(tmp_path: Path) -> None:
    gw, adapter = _connect(account_trade_mode=0)
    ledger, store = make_ledger(tmp_path)
    hyp = make_s5_hypothesis()
    outcome = demo_execution_adapter.execute(
        hypothesis=hyp, decision=make_trade_decision(hyp), adapter=adapter, gateway=gw, config=_CONFIG,
        ledger=ledger, symbol=SYMBOL, expected_strategy_id=STRATEGY_ID,
    )
    assert outcome.submitted is True
    assert len(gw.order_send_calls) == 1
    store.close()


def test_real_account_cannot_connect() -> None:
    gw = FakeMT5BridgeGateway(account_trade_mode=2)  # AccountTradeMode.REAL
    from ai_trader.execution_engine.adapters.exceptions import NonDemoAccountError

    from ai_trader.execution_engine.adapters.connection import BrokerCredentials
    from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter

    adapter = MT5DemoBrokerAdapter(gateway=gw, config=_CONFIG, credentials=BrokerCredentials())
    try:
        adapter.connect()
        raised = False
    except NonDemoAccountError:
        raised = True
    assert raised is True
    assert adapter.is_connected() is False
    assert gw.order_send_calls == []


def test_contest_account_cannot_connect() -> None:
    gw = FakeMT5BridgeGateway(account_trade_mode=1)  # AccountTradeMode.CONTEST
    from ai_trader.execution_engine.adapters.connection import BrokerCredentials
    from ai_trader.execution_engine.adapters.exceptions import NonDemoAccountError
    from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter

    adapter = MT5DemoBrokerAdapter(gateway=gw, config=_CONFIG, credentials=BrokerCredentials())
    try:
        adapter.connect()
        raised = False
    except NonDemoAccountError:
        raised = True
    assert raised is True
    assert gw.order_send_calls == []


def test_unknown_trade_mode_value_cannot_connect() -> None:
    gw = FakeMT5BridgeGateway(account_trade_mode=99)  # not any defined AccountTradeMode value
    from ai_trader.execution_engine.adapters.connection import BrokerCredentials
    from ai_trader.execution_engine.adapters.exceptions import NonDemoAccountError
    from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter

    adapter = MT5DemoBrokerAdapter(gateway=gw, config=_CONFIG, credentials=BrokerCredentials())
    try:
        adapter.connect()
        raised = False
    except NonDemoAccountError:
        raised = True
    assert raised is True


def test_missing_account_info_cannot_connect() -> None:
    gw = FakeMT5BridgeGateway()
    gw.account_info_result = None
    from ai_trader.execution_engine.adapters.connection import BrokerCredentials
    from ai_trader.execution_engine.adapters.exceptions import AccountValidationError
    from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter

    adapter = MT5DemoBrokerAdapter(gateway=gw, config=_CONFIG, credentials=BrokerCredentials())
    try:
        adapter.connect()
        raised = False
    except AccountValidationError:
        raised = True
    assert raised is True


def test_account_switch_demo_to_real_mid_session_blocks_next_submission(tmp_path: Path) -> None:
    """Section 32 -- no cached DEMO authorization may survive an account switch: connect while DEMO,
    then the underlying account flips to REAL (simulating MT5 reconnecting to a different account),
    and the VERY NEXT submission attempt must be blocked -- re-verified fresh, not from a cached flag."""
    gw, adapter = _connect(account_trade_mode=0)
    gw.account_info_result = SimpleNamespace(trade_mode=2, trade_allowed=True, server="FusionMarkets-Demo", equity=10_000.0)  # now REAL

    ledger, store = make_ledger(tmp_path)
    hyp = make_s5_hypothesis()
    outcome = demo_execution_adapter.execute(
        hypothesis=hyp, decision=make_trade_decision(hyp), adapter=adapter, gateway=gw, config=_CONFIG,
        ledger=ledger, symbol=SYMBOL, expected_strategy_id=STRATEGY_ID,
    )
    assert outcome.submitted is False
    assert gw.order_send_calls == []
    store.close()


def test_real_account_cannot_reach_order_send_even_with_every_other_input_valid(tmp_path: Path) -> None:
    """Section 4's own explicit required proof: strategy=S5, EV=TRADE_DECISION, Risk-equivalent inputs
    all valid -- the ONLY thing wrong is the account is REAL, not DEMO. Defense in depth: this must be
    refused BEFORE `adapter.connect()` even succeeds (this adapter never reaches a connected state for a
    REAL account, so `execute()` -- which requires an already-connected adapter -- structurally cannot
    even be attempted the normal way; this test proves the connect-time refusal directly, the layer that
    makes every later layer moot for a REAL account)."""
    gw = FakeMT5BridgeGateway(account_trade_mode=2)
    from ai_trader.execution_engine.adapters.connection import BrokerCredentials
    from ai_trader.execution_engine.adapters.exceptions import NonDemoAccountError
    from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter

    adapter = MT5DemoBrokerAdapter(gateway=gw, config=_CONFIG, credentials=BrokerCredentials())
    raised = False
    try:
        adapter.connect()
    except NonDemoAccountError:
        raised = True
    assert raised is True
    assert adapter.is_connected() is False
    assert gw.order_check_calls == []
    assert gw.order_send_calls == []


# ═══ genuine-signal-only gates (sections 2, 28, 33, 34) ═══

def test_wrong_strategy_rejected(tmp_path: Path) -> None:
    gw, adapter = _connect()
    ledger, store = make_ledger(tmp_path)
    hyp = make_s5_hypothesis()
    outcome = demo_execution_adapter.execute(
        hypothesis=hyp, decision=make_trade_decision(hyp), adapter=adapter, gateway=gw, config=_CONFIG,
        ledger=ledger, symbol=SYMBOL, expected_strategy_id="some_other_strategy_id",
    )
    assert outcome.submitted is False
    assert outcome.reason == demo_execution_adapter.WRONG_STRATEGY
    assert gw.order_send_calls == []
    store.close()


def test_wrong_evidence_fingerprint_rejected(tmp_path: Path) -> None:
    gw, adapter = _connect()
    ledger, store = make_ledger(tmp_path)
    hyp = make_s5_hypothesis()
    dec = dataclasses.replace(make_trade_decision(hyp), evidence_fingerprint="not-the-real-evidence-fingerprint")
    outcome = demo_execution_adapter.execute(
        hypothesis=hyp, decision=dec, adapter=adapter, gateway=gw, config=_CONFIG, ledger=ledger,
        symbol=SYMBOL, expected_strategy_id=STRATEGY_ID,
    )
    assert outcome.submitted is False
    assert outcome.reason == demo_execution_adapter.EVIDENCE_MISMATCH
    assert gw.order_send_calls == []
    store.close()


def test_no_trade_decision_never_submits(tmp_path: Path) -> None:
    gw, adapter = _connect()
    ledger, store = make_ledger(tmp_path)
    hyp = make_s5_hypothesis()
    outcome = demo_execution_adapter.execute(
        hypothesis=hyp, decision=make_no_trade_decision(hyp), adapter=adapter, gateway=gw, config=_CONFIG,
        ledger=ledger, symbol=SYMBOL, expected_strategy_id=STRATEGY_ID,
    )
    assert outcome.submitted is False
    assert outcome.reason == demo_execution_adapter.NOT_TRADE_DECISION
    assert gw.order_send_calls == []
    store.close()


# ═══ dedup / restart (sections 12, 21, 25) ═══

def test_duplicate_signal_rejected_same_process(tmp_path: Path) -> None:
    gw, adapter = _connect()
    ledger, store = make_ledger(tmp_path)
    hyp = make_s5_hypothesis()
    dec = make_trade_decision(hyp)
    first = demo_execution_adapter.execute(
        hypothesis=hyp, decision=dec, adapter=adapter, gateway=gw, config=_CONFIG, ledger=ledger,
        symbol=SYMBOL, expected_strategy_id=STRATEGY_ID,
    )
    second = demo_execution_adapter.execute(
        hypothesis=hyp, decision=dec, adapter=adapter, gateway=gw, config=_CONFIG, ledger=ledger,
        symbol=SYMBOL, expected_strategy_id=STRATEGY_ID,
    )
    assert first.submitted is True
    assert second.submitted is False
    assert second.reason is not None and DUPLICATE_IDENTITY in second.reason
    assert len(gw.order_send_calls) == 1  # never a second real send for the same identity
    store.close()


def test_restart_duplicate_rejected_via_persisted_ledger(tmp_path: Path) -> None:
    """Same canonical event, fresh adapter/gateway instances (simulating a process restart), SAME
    on-disk ledger file -- the second run must refuse to resubmit."""
    from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.mt5_execution_ledger import MT5ExecutionLedger
    from ai_trader.persistent_state.store import SqliteStateStore

    db_path = tmp_path / "restart_ledger.db"
    hyp = make_s5_hypothesis()
    dec = make_trade_decision(hyp)

    store1 = SqliteStateStore(db_path)
    ledger1 = MT5ExecutionLedger(store1)
    gw1, adapter1 = _connect()
    first = demo_execution_adapter.execute(
        hypothesis=hyp, decision=dec, adapter=adapter1, gateway=gw1, config=_CONFIG, ledger=ledger1,
        symbol=SYMBOL, expected_strategy_id=STRATEGY_ID,
    )
    assert first.submitted is True
    store1.close()

    store2 = SqliteStateStore(db_path)
    ledger2 = MT5ExecutionLedger(store2)
    assert len(ledger2.entries) == 2  # PENDING_SUBMISSION + SUBMITTED_ACK, persisted
    gw2, adapter2 = _connect()
    second = demo_execution_adapter.execute(
        hypothesis=hyp, decision=dec, adapter=adapter2, gateway=gw2, config=_CONFIG, ledger=ledger2,
        symbol=SYMBOL, expected_strategy_id=STRATEGY_ID,
    )
    assert second.submitted is False
    assert gw2.order_send_calls == []  # the restarted process never re-sends
    store2.close()


def test_reconciled_existing_identity_blocks_fresh_submission(tmp_path: Path) -> None:
    """After startup reconciliation marks an in-doubt identity RECONCILED_EXISTING (a real broker
    position/order/deal was found matching it), a subsequent attempt for the SAME identity must still be
    refused as a duplicate -- reconciliation and ordinary dedup share the same ledger-presence check."""
    from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.mt5_execution_ledger import PENDING_SUBMISSION, MT5ExecutionLedgerRecord
    from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.order_identity import client_order_id_for
    from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.reconciliation import reconcile_in_doubt_identities

    gw, adapter = _connect()
    ledger, store = make_ledger(tmp_path)
    hyp = make_s5_hypothesis()
    dec = make_trade_decision(hyp)
    cid = client_order_id_for(hyp, dec)
    ledger.record(MT5ExecutionLedgerRecord(
        client_order_id=cid, decision_id=f"{cid}-dec", state=PENDING_SUBMISSION, as_of=0,
        strategy_id=STRATEGY_ID, strategy_version=hyp.strategy_version, symbol=SYMBOL, side="LONG",
        requested_entry=hyp.intended_entry, actual_quote_bid=None, actual_quote_ask=None, sl=hyp.invalidation,
        tp=None, requested_volume=0.01, modeled_risk_money=1.0, modeled_risk_fraction=0.0001,
        account_trade_mode="AccountTradeMode.DEMO", evidence_fingerprint=dec.evidence_fingerprint,
        order_request_id=f"{cid}-req",
    ))
    gw.positions_get = lambda symbol=None: (SimpleNamespace(symbol=SYMBOL, volume=0.01, price_open=hyp.intended_entry, time=0, ticket=42),)  # type: ignore[method-assign]
    reconcile_in_doubt_identities(ledger=ledger, gateway=gw, symbol=SYMBOL)

    outcome = demo_execution_adapter.execute(
        hypothesis=hyp, decision=dec, adapter=adapter, gateway=gw, config=_CONFIG, ledger=ledger,
        symbol=SYMBOL, expected_strategy_id=STRATEGY_ID,
    )
    assert outcome.submitted is False
    assert gw.order_send_calls == []
    store.close()


# ═══ full canonical pipeline integration (section 30) ═══

def test_canonical_s5_trade_decision_from_real_pipeline_reaches_demo_adapter(tmp_path: Path) -> None:
    """No fixture shortcuts on the S5/EV side -- runs the REAL, unmodified S5 strategy through the REAL,
    unmodified `pipeline.run_cycle` with a REAL `RealEVDecisionEngine`, exactly the already-proven
    positive path (`test_s5_hypothesis_reaches_real_ev_authority_with_genuine_evidence`). Only once THAT
    unchanged pipeline genuinely reaches TRADE_DECISION does this test hand the resulting hypothesis/
    decision to the new MT5 bridge -- proving the wiring, not re-deriving EV correctness."""
    breakout_bar = _session_bar(ENTRY_WINDOW_FIRST_BIS + 1, close=2052.0)
    strategy, market_state = _fixture(extra_bars=[breakout_bar])
    _, entry = real_s5_catalog_entry()
    catalog = StrategyCatalog(entries=(dataclasses.replace(entry, strategy=strategy),))
    ev_engine = RealEVDecisionEngine(
        catalog=catalog, market_state=market_state,
        cost_model=CostModel(cost_model_id="AI_TRADER_SHADOW_COST_MODEL_v1", full_spread_price=0.0, entry_slippage_price=0.12, exit_slippage_price=0.12),
    )
    from ai_trader.new_brain_live.strategy_platform.shadow_ledger import ShadowLedger
    from ai_trader.new_brain_live.strategy_platform.tests._fixtures import make_risk_execution_deps
    from ai_trader.new_brain_live.strategy_platform.risk_execution_adapter import RiskExecutionDeps
    from ai_trader.persistent_state.store import SqliteStateStore

    shadow_store = SqliteStateStore(tmp_path / "shadow.db")
    result = pipeline.run_cycle(
        market_state=market_state, catalog=catalog, ev_engine=ev_engine,
        risk_execution_deps=RiskExecutionDeps(**make_risk_execution_deps()),  # type: ignore[arg-type]
        ledger=ShadowLedger(shadow_store), router=StrategyRouter(),
    )
    shadow_store.close()
    assert any(d.decision == TRADE_DECISION for d in result.ev_decisions)
    assert result.record.broker_submission_state.startswith("BLOCKED_AT_GATE")  # the existing Risk gate already approved it

    winning = next(d for d in result.ev_decisions if d.decision == TRADE_DECISION)
    gw, adapter = _connect()
    ledger, store = make_ledger(tmp_path, "mt5_bridge_from_pipeline.db")
    outcome = demo_execution_adapter.execute(
        hypothesis=winning.hypothesis, decision=winning, adapter=adapter, gateway=gw, config=_CONFIG,
        ledger=ledger, symbol=SYMBOL, expected_strategy_id=STRATEGY_ID,
    )
    assert outcome.submitted is True
    assert len(gw.order_send_calls) == 1
    sent = gw.order_send_calls[0]
    assert sent["sl"] == winning.hypothesis.invalidation  # canonical SL preserved exactly
    store.close()
