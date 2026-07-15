"""Tests for the artifact/report writer: atomic writes, manifest checksums, ref paths."""

from __future__ import annotations

import hashlib
import json

from ai_trader.simulation.artifacts import ArtifactWriter
from ai_trader.simulation.config import RecordConfig
from ai_trader.simulation.portfolio_simulator import EquityPoint, SimAccount, TradeRecord
from ai_trader.signal_engine.types import Direction


def make_account() -> SimAccount:
    account = SimAccount(starting_balance=1000.0, balance=1050.0, equity=1050.0, equity_hwm=1050.0)
    account.trade_ledger = [TradeRecord(
        client_order_id="C", strategy_id="S1", symbol="XAUUSD", direction=Direction.LONG,
        entry_price=100.0, exit_price=150.0, entry_as_of=100, exit_as_of=200, qty=1.0,
        gross_pnl=50.0, fees=0.0, net_pnl=50.0, pnl_r=None, holding_bars=4, mfe=0.0, mae=0.0,
    )]
    account.equity_curve = [EquityPoint(as_of=200, balance=1050.0, equity=1050.0, drawdown_pct=0.0)]
    return account


def test_write_creates_files_and_manifest(tmp_path) -> None:  # type: ignore[no-untyped-def]
    writer = ArtifactWriter("RUN1", tmp_path)
    account = make_account()
    artifacts = writer.write(account, {"meta": {"run_id": "RUN1"}}, RecordConfig())

    run_dir = tmp_path / "RUN1"
    assert (run_dir / "trade_history.jsonl").exists()
    assert (run_dir / "equity_curve.jsonl").exists()
    assert (run_dir / "report.json").exists()
    assert (run_dir / "manifest.json").exists()
    assert artifacts.trade_history_ref == "trade_history.jsonl"
    assert artifacts.equity_curve_ref == "equity_curve.jsonl"

    manifest = json.loads((run_dir / "manifest.json").read_text())
    for name, meta in manifest["files"].items():
        content = (run_dir / name).read_bytes()
        assert hashlib.sha256(content).hexdigest() == meta["sha256"]
        assert meta["bytes"] == len(content)


def test_trade_history_jsonl_is_valid_json_lines(tmp_path) -> None:  # type: ignore[no-untyped-def]
    writer = ArtifactWriter("RUN2", tmp_path)
    writer.write(make_account(), {}, RecordConfig())
    lines = (tmp_path / "RUN2" / "trade_history.jsonl").read_text().strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["symbol"] == "XAUUSD"
    assert record["direction"] == "LONG"


def test_record_config_disables_a_file(tmp_path) -> None:  # type: ignore[no-untyped-def]
    writer = ArtifactWriter("RUN3", tmp_path)
    writer.write(make_account(), {}, RecordConfig(trade_history=False))
    assert not (tmp_path / "RUN3" / "trade_history.jsonl").exists()
