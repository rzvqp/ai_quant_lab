from __future__ import annotations

import json
from pathlib import Path

from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.mt5_execution_ledger import (
    CLOSED,
    MT5ExecutionLedger,
)
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.soak.checkpoints import (
    maybe_write_checkpoint,
    write_final_report,
)
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.soak.tests.test_metrics import _base_row, _closed
from ai_trader.persistent_state.store import SqliteStateStore

SYMBOL = "XAUUSD"


def _ledger(tmp_path: Path) -> MT5ExecutionLedger:
    store = SqliteStateStore(tmp_path / "cp.db")
    return MT5ExecutionLedger(store)


def test_first_trade_checkpoint_written_once_submitted(tmp_path: Path) -> None:
    ledger = _ledger(tmp_path)
    ledger.record(_base_row("cid-1"))
    state_dir = tmp_path / "state"
    first_written, _ = maybe_write_checkpoint(ledger=ledger, starting_equity=10_000.0, state_dir=state_dir, first_trade_written=False)
    assert first_written is True
    assert (state_dir / "first_trade_checkpoint.json").exists()


def test_first_trade_checkpoint_not_rewritten_twice(tmp_path: Path) -> None:
    ledger = _ledger(tmp_path)
    ledger.record(_base_row("cid-1"))
    state_dir = tmp_path / "state"
    maybe_write_checkpoint(ledger=ledger, starting_equity=10_000.0, state_dir=state_dir, first_trade_written=False)
    second_first, _ = maybe_write_checkpoint(ledger=ledger, starting_equity=10_000.0, state_dir=state_dir, first_trade_written=True)
    assert second_first is False


def test_milestone_checkpoint_written_at_5_closed_trades(tmp_path: Path) -> None:
    ledger = _ledger(tmp_path)
    for i in range(5):
        ledger.record(_closed(f"cid-{i}", net_pl=10.0, r_result=1.0))
    state_dir = tmp_path / "state"
    _, milestone_written = maybe_write_checkpoint(ledger=ledger, starting_equity=10_000.0, state_dir=state_dir, first_trade_written=True)
    assert milestone_written is True
    assert (state_dir / "checkpoint_5_closed_trades.json").exists()
    assert not (state_dir / "checkpoint_10_closed_trades.json").exists()


def test_milestone_checkpoint_content_includes_comparison(tmp_path: Path) -> None:
    ledger = _ledger(tmp_path)
    for i in range(5):
        ledger.record(_closed(f"cid-{i}", net_pl=10.0, r_result=1.0))
    state_dir = tmp_path / "state"
    maybe_write_checkpoint(ledger=ledger, starting_equity=10_000.0, state_dir=state_dir, first_trade_written=True)
    data = json.loads((state_dir / "checkpoint_5_closed_trades.json").read_text(encoding="utf-8"))
    assert data["trades_closed"] == 5
    assert "reference_validated_s5" in data["comparison"]
    assert data["comparison"]["reference_validated_s5"]["win_rate"] == 0.549


def test_final_report_written(tmp_path: Path) -> None:
    ledger = _ledger(tmp_path)
    ledger.record(_closed("cid-1", net_pl=50.0, r_result=0.5))
    state_dir = tmp_path / "state"
    path = write_final_report(ledger=ledger, starting_equity=10_000.0, state_dir=state_dir, termination_reason="D_EXPLICIT_STOP", wall_clock_seconds=123.4)
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["termination_reason"] == "D_EXPLICIT_STOP"
    assert data["metrics"]["trades"] == 1
