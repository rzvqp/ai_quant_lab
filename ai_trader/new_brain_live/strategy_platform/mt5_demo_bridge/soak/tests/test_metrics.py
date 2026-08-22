from __future__ import annotations

import dataclasses
from pathlib import Path

from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.mt5_execution_ledger import (
    CLOSED,
    PENDING_SUBMISSION,
    MT5ExecutionLedger,
    MT5ExecutionLedgerRecord,
)
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.soak.metrics import compute_metrics
from ai_trader.persistent_state.store import SqliteStateStore

SYMBOL = "XAUUSD"


def _base_row(cid: str, *, as_of: int = 0) -> MT5ExecutionLedgerRecord:
    return MT5ExecutionLedgerRecord(
        client_order_id=cid, decision_id=f"{cid}-dec", state=PENDING_SUBMISSION, as_of=as_of,
        strategy_id="s5", strategy_version="v1", symbol=SYMBOL, side="LONG", requested_entry=2000.0,
        actual_quote_bid=2000.0, actual_quote_ask=2000.1, sl=1990.0, tp=2030.0, requested_volume=1.0,
        modeled_risk_money=100.0, modeled_risk_fraction=0.01, account_trade_mode="DEMO",
        evidence_fingerprint="fp", order_request_id=f"{cid}-req",
    )


def _closed(cid: str, *, net_pl: float, r_result: float, as_of: int = 1000) -> MT5ExecutionLedgerRecord:
    return dataclasses.replace(_base_row(cid, as_of=as_of), state=CLOSED, net_pl_money=net_pl, gross_pl_money=net_pl, r_result=r_result, exit_reason="TARGET" if net_pl > 0 else "STOP")


def _ledger(tmp_path: Path, rows: list[MT5ExecutionLedgerRecord]) -> MT5ExecutionLedger:
    store = SqliteStateStore(tmp_path / "m.db")
    ledger = MT5ExecutionLedger(store)
    for r in rows:
        ledger.record(r)
    return ledger


def test_no_closed_trades_returns_empty_metrics(tmp_path: Path) -> None:
    ledger = _ledger(tmp_path, [])
    m = compute_metrics(ledger=ledger, starting_equity=10_000.0)
    assert m.trades == 0
    assert m.win_rate is None
    assert m.avg_r is None
    assert m.max_drawdown == 0.0


def test_win_loss_counts_and_win_rate(tmp_path: Path) -> None:
    rows = [_closed("a", net_pl=200.0, r_result=2.0), _closed("b", net_pl=-100.0, r_result=-1.0), _closed("c", net_pl=150.0, r_result=1.5)]
    ledger = _ledger(tmp_path, rows)
    m = compute_metrics(ledger=ledger, starting_equity=10_000.0)
    assert m.trades == 3
    assert m.wins == 2
    assert m.losses == 1
    assert abs(m.win_rate - (2 / 3)) < 1e-9  # type: ignore[operator]


def test_avg_r_and_profit_factor(tmp_path: Path) -> None:
    rows = [_closed("a", net_pl=200.0, r_result=2.0), _closed("b", net_pl=-100.0, r_result=-1.0)]
    ledger = _ledger(tmp_path, rows)
    m = compute_metrics(ledger=ledger, starting_equity=10_000.0)
    assert abs(m.avg_r - 0.5) < 1e-9  # type: ignore[operator]  # (2 + -1) / 2
    assert abs(m.profit_factor - 2.0) < 1e-9  # type: ignore[operator]  # win_r=2 / loss_r=1


def test_drawdown_tracked_from_equity_curve(tmp_path: Path) -> None:
    rows = [_closed("a", net_pl=500.0, r_result=5.0, as_of=100), _closed("b", net_pl=-300.0, r_result=-3.0, as_of=200), _closed("c", net_pl=100.0, r_result=1.0, as_of=300)]
    ledger = _ledger(tmp_path, rows)
    m = compute_metrics(ledger=ledger, starting_equity=10_000.0)
    # equity curve: 10000 -> 10500 (peak) -> 10200 (dd=300) -> 10300
    assert abs(m.max_drawdown - 300.0) < 1e-9
    assert abs(m.peak_equity - 10_500.0) < 1e-9  # type: ignore[operator]


def test_consecutive_streaks(tmp_path: Path) -> None:
    rows = [
        _closed("a", net_pl=10.0, r_result=1.0, as_of=1), _closed("b", net_pl=10.0, r_result=1.0, as_of=2),
        _closed("c", net_pl=-10.0, r_result=-1.0, as_of=3), _closed("d", net_pl=-10.0, r_result=-1.0, as_of=4),
        _closed("e", net_pl=-10.0, r_result=-1.0, as_of=5), _closed("f", net_pl=10.0, r_result=1.0, as_of=6),
    ]
    ledger = _ledger(tmp_path, rows)
    m = compute_metrics(ledger=ledger, starting_equity=10_000.0)
    assert m.max_consecutive_wins == 2
    assert m.max_consecutive_losses == 3
    assert m.consecutive_wins == 1  # the LAST trade was a win, streak of 1 at the end
    assert m.consecutive_losses == 0


def test_exit_reason_counts(tmp_path: Path) -> None:
    rows = [_closed("a", net_pl=200.0, r_result=2.0), _closed("b", net_pl=-100.0, r_result=-1.0)]
    ledger = _ledger(tmp_path, rows)
    m = compute_metrics(ledger=ledger, starting_equity=10_000.0)
    assert m.exit_reason_counts == {"TARGET": 1, "STOP": 1}


def test_only_closed_rows_count_pending_ignored(tmp_path: Path) -> None:
    ledger = _ledger(tmp_path, [_base_row("a"), _closed("b", net_pl=50.0, r_result=0.5)])
    m = compute_metrics(ledger=ledger, starting_equity=10_000.0)
    assert m.trades == 1
