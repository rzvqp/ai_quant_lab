"""Functional test of the soak harness itself -- a SHORT run (seconds, not hours) proving the harness
mechanics are correct (distinct MarketStates generated, ledger grows 1:1 with cycles, zero exceptions,
zero order_send, N1 subprocess genuinely exercised) before ever trusting it for the real 6-hour run."""

from __future__ import annotations

from pathlib import Path

from ai_trader.new_brain_live.strategy_platform.soak.harness import run_soak


def test_short_soak_run_completes_cleanly(tmp_path: Path) -> None:
    report = run_soak(duration_seconds=3.0, state_dir=tmp_path, cycle_interval_seconds=0.1)
    assert report.cycles_completed > 0
    assert report.exceptions == ()
    assert report.order_send_calls_total == 0
    assert report.ledger_row_count_matches_cycles is True
    assert report.duplicate_cycles_detected == 0
    assert report.n1_subprocess_calls >= 1
    assert report.n1_subprocess_failures == 0
