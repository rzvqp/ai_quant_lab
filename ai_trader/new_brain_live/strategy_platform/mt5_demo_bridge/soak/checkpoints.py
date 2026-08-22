"""Interim/final checkpoint reports (mandate sections 22, 24). Reference-only comparison against the
validated S5 population (never a pass/fail verdict from a tiny live sample -- section 22's own explicit
instruction)."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.mt5_execution_ledger import CLOSED, MT5ExecutionLedger
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.soak.metrics import SoakMetrics, compute_metrics

#: mandate section 22 -- reference values only, from the already-cited validated S5 population
#: (AI_TRADER_S5_ONBOARDING_REPORT.md / S5_REAL_EV_RUNTIME_EVIDENCE_CONTRACT.md). Never used as a
#: pass/fail gate anywhere in this module.
REFERENCE_WIN_RATE = 0.549
REFERENCE_BASE_EXPECTANCY_R = 0.210
REFERENCE_STRESS_EXPECTANCY_R = 0.193
REFERENCE_PROFIT_FACTOR = 1.61
REFERENCE_MAX_HISTORICAL_DD_R = -6.44

#: mandate section 24 -- checkpoints at 5 and 10 CLOSED trades (the first-genuine-ORDER checkpoint is
#: handled separately via `first_trade_checkpoint.json`, triggered on submission, not closure).
CHECKPOINT_TRADE_COUNTS = (5, 10)


def _comparison_block(metrics: SoakMetrics) -> dict[str, object]:
    return {
        "observed": {
            "trades": metrics.trades, "win_rate": metrics.win_rate, "avg_r": metrics.avg_r,
            "profit_factor": metrics.profit_factor, "max_drawdown_money": metrics.max_drawdown,
        },
        "reference_validated_s5": {
            "win_rate": REFERENCE_WIN_RATE, "base_expectancy_r": REFERENCE_BASE_EXPECTANCY_R,
            "stress_expectancy_r": REFERENCE_STRESS_EXPECTANCY_R, "profit_factor": REFERENCE_PROFIT_FACTOR,
            "max_historical_dd_r": REFERENCE_MAX_HISTORICAL_DD_R,
        },
        "note": (
            "Reference values only -- a DEMO sample of this size is never sufficient to declare the "
            "strategy validated/failed; no retuning of S5/EV/risk occurs from this comparison "
            "(mandate section 22/26)."
        ),
    }


def maybe_write_checkpoint(*, ledger: MT5ExecutionLedger, starting_equity: float, state_dir: Path, first_trade_written: bool) -> tuple[bool, bool]:
    """Returns (first_trade_checkpoint_written_this_call, milestone_checkpoint_written_this_call)."""
    closed_count = sum(1 for e in ledger.entries if e.state == CLOSED)
    submitted_count = len(ledger.all_client_order_ids())
    metrics = compute_metrics(ledger=ledger, starting_equity=starting_equity)

    first_written = False
    first_trade_path = state_dir / "first_trade_checkpoint.json"
    if submitted_count >= 1 and not first_trade_written and not first_trade_path.exists():
        first_trade_path.parent.mkdir(parents=True, exist_ok=True)
        first_trade_path.write_text(json.dumps({
            "status": "S5_FIRST_GENUINE_DEMO_TRADE_EXECUTED", "submitted_identities": ledger.all_client_order_ids(),
        }, indent=2), encoding="utf-8")
        first_written = True

    milestone_written = False
    state_dir.mkdir(parents=True, exist_ok=True)
    for n in CHECKPOINT_TRADE_COUNTS:
        path = state_dir / f"checkpoint_{n}_closed_trades.json"
        if closed_count >= n and not path.exists():
            path.write_text(json.dumps({
                "checkpoint": f"{n}_closed_trades", "trades_closed": closed_count, "metrics": _metrics_to_dict(metrics),
                "comparison": _comparison_block(metrics),
            }, indent=2), encoding="utf-8")
            milestone_written = True
    return first_written, milestone_written


def _metrics_to_dict(metrics: SoakMetrics) -> dict[str, object]:
    import dataclasses

    return dataclasses.asdict(metrics)


def write_final_report(*, ledger: MT5ExecutionLedger, starting_equity: float, state_dir: Path, termination_reason: str, wall_clock_seconds: float) -> Path:
    metrics = compute_metrics(ledger=ledger, starting_equity=starting_equity)
    path = state_dir / "final_soak_report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "termination_reason": termination_reason, "wall_clock_seconds": wall_clock_seconds,
        "metrics": _metrics_to_dict(metrics), "comparison": _comparison_block(metrics),
        "total_submitted_identities": len(ledger.all_client_order_ids()),
    }, indent=2), encoding="utf-8")
    return path
