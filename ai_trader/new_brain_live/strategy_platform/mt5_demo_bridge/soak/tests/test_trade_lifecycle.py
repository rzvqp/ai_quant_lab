from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.mt5_execution_ledger import (
    CLOSED,
    OPEN_CONFIRMED,
    SUBMITTED_ACK,
    MT5ExecutionLedger,
    MT5ExecutionLedgerRecord,
)
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.soak.trade_lifecycle import (
    OTHER_BROKER_EXCEPTION,
    STOP,
    TARGET,
    detect_closed_positions,
    detect_new_open_positions,
)
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.tests._fixtures import FakeMT5BridgeGateway
from ai_trader.persistent_state.store import SqliteStateStore

SYMBOL = "XAUUSD"


def _ledger(tmp_path: Path, name: str = "lifecycle.db") -> tuple[MT5ExecutionLedger, SqliteStateStore]:
    store = SqliteStateStore(tmp_path / name)
    return MT5ExecutionLedger(store), store


def _ack_row(cid: str, *, as_of: int = 1000, entry: float = 2000.0, volume: float = 1.0, sl: float = 1990.0, tp: float | None = 2030.0) -> MT5ExecutionLedgerRecord:
    return MT5ExecutionLedgerRecord(
        client_order_id=cid, decision_id=f"{cid}-dec", state=SUBMITTED_ACK, as_of=as_of, strategy_id="s5",
        strategy_version="v1", symbol=SYMBOL, side="LONG", requested_entry=entry, actual_quote_bid=entry,
        actual_quote_ask=entry + 0.1, sl=sl, tp=tp, requested_volume=volume, modeled_risk_money=10.0,
        modeled_risk_fraction=0.001, account_trade_mode="DEMO", evidence_fingerprint="fp", order_request_id=f"{cid}-req",
    )


def test_new_open_position_detected_and_recorded(tmp_path: Path) -> None:
    gw = FakeMT5BridgeGateway()
    ledger, store = _ledger(tmp_path)
    ledger.record(_ack_row("cid-1"))
    gw._positions = (SimpleNamespace(symbol=SYMBOL, volume=1.0, price_open=2000.0, time=1000, ticket=555),)

    confirmed = detect_new_open_positions(ledger=ledger, gateway=gw, symbol=SYMBOL)
    assert confirmed == ("cid-1",)
    row = ledger.latest_state_for("cid-1")
    assert row is not None
    assert row.state == OPEN_CONFIRMED
    assert row.broker_position_ticket == 555
    store.close()


def test_no_matching_position_leaves_state_unchanged(tmp_path: Path) -> None:
    gw = FakeMT5BridgeGateway()
    ledger, store = _ledger(tmp_path)
    ledger.record(_ack_row("cid-1"))
    # no positions scripted -- nothing matches yet (order accepted but not yet visible as a position)

    confirmed = detect_new_open_positions(ledger=ledger, gateway=gw, symbol=SYMBOL)
    assert confirmed == ()
    row = ledger.latest_state_for("cid-1")
    assert row is not None
    assert row.state == SUBMITTED_ACK
    store.close()


def _open_confirmed_row(cid: str, ticket: int, **overrides: object) -> MT5ExecutionLedgerRecord:
    import dataclasses

    kwargs: dict[str, object] = {"state": OPEN_CONFIRMED, "broker_position_ticket": ticket}
    kwargs.update(overrides)
    return dataclasses.replace(_ack_row(cid), **kwargs)  # type: ignore[arg-type]


def test_closed_position_detected_and_classified_as_target(tmp_path: Path) -> None:
    gw = FakeMT5BridgeGateway()
    ledger, store = _ledger(tmp_path)
    ledger.record(_open_confirmed_row("cid-1", 555, tp=2030.0, sl=1990.0))
    # position no longer in positions_get (gw._positions defaults to ()) -- closed
    gw._deals = (SimpleNamespace(position_id=555, entry=1, price=2030.0, time=2000, profit=300.0, commission=-1.0, swap=0.0),)

    closed = detect_closed_positions(ledger=ledger, gateway=gw, symbol=SYMBOL, now=3000)
    assert closed == ("cid-1",)
    row = ledger.latest_state_for("cid-1")
    assert row is not None
    assert row.state == CLOSED
    assert row.exit_reason == TARGET
    assert row.exit_price == 2030.0
    assert abs(row.net_pl_money - 299.0) < 1e-9  # type: ignore[operator]  # 300 profit - 1 commission
    assert abs(row.r_result - 29.9) < 1e-9  # type: ignore[operator]  # net_pl / modeled_risk_money(10.0)
    store.close()


def test_closed_position_detected_and_classified_as_stop(tmp_path: Path) -> None:
    gw = FakeMT5BridgeGateway()
    ledger, store = _ledger(tmp_path)
    ledger.record(_open_confirmed_row("cid-1", 555, tp=2030.0, sl=1990.0))
    gw._deals = (SimpleNamespace(position_id=555, entry=1, price=1990.0, time=2000, profit=-100.0, commission=-1.0, swap=0.0),)

    closed = detect_closed_positions(ledger=ledger, gateway=gw, symbol=SYMBOL, now=3000)
    assert closed == ("cid-1",)
    row = ledger.latest_state_for("cid-1")
    assert row is not None
    assert row.exit_reason == STOP
    store.close()


def test_closed_position_far_from_sl_tp_classified_as_other() -> None:
    from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.soak.trade_lifecycle import _classify_exit

    assert _classify_exit(exit_price=2010.0, sl=1990.0, tp=2030.0) == OTHER_BROKER_EXCEPTION


def test_position_still_open_is_not_closed(tmp_path: Path) -> None:
    gw = FakeMT5BridgeGateway()
    ledger, store = _ledger(tmp_path)
    ledger.record(_open_confirmed_row("cid-1", 555))
    gw._positions = (SimpleNamespace(symbol=SYMBOL, volume=1.0, price_open=2000.0, time=1000, ticket=555),)

    closed = detect_closed_positions(ledger=ledger, gateway=gw, symbol=SYMBOL, now=3000)
    assert closed == ()
    row = ledger.latest_state_for("cid-1")
    assert row is not None
    assert row.state == OPEN_CONFIRMED
    store.close()


def test_vanished_position_without_matching_deal_yet_stays_open_never_guessed(tmp_path: Path) -> None:
    gw = FakeMT5BridgeGateway()
    ledger, store = _ledger(tmp_path)
    ledger.record(_open_confirmed_row("cid-1", 555))
    # no positions, no deals scripted -- broker history simply hasn't caught up yet
    closed = detect_closed_positions(ledger=ledger, gateway=gw, symbol=SYMBOL, now=3000)
    assert closed == ()
    row = ledger.latest_state_for("cid-1")
    assert row is not None
    assert row.state == OPEN_CONFIRMED  # never guessed a close without a matching deal
    store.close()
