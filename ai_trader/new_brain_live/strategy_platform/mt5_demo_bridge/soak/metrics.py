"""Cumulative DEMO operational metrics (mandate section 21) -- observation only, never fed back into S5/
EV/risk logic anywhere in this codebase (section 26: no strategy optimization during soak)."""

from __future__ import annotations

import dataclasses

from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.mt5_execution_ledger import CLOSED, MT5ExecutionLedger


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class SoakMetrics:
    trades: int
    wins: int
    losses: int
    win_rate: float | None
    gross_r_sum: float
    net_r_sum: float
    avg_r: float | None
    profit_factor: float | None
    equity_curve: tuple[float, ...]
    peak_equity: float | None
    current_drawdown: float
    max_drawdown: float
    consecutive_wins: int
    consecutive_losses: int
    max_consecutive_wins: int
    max_consecutive_losses: int
    exit_reason_counts: dict[str, int]


def compute_metrics(*, ledger: MT5ExecutionLedger, starting_equity: float) -> SoakMetrics:
    closed = [e for e in ledger.entries if e.state == CLOSED]
    trades = len(closed)
    wins = sum(1 for e in closed if (e.net_pl_money or 0.0) > 0.0)
    losses = sum(1 for e in closed if (e.net_pl_money or 0.0) <= 0.0)

    r_values = [e.r_result for e in closed if e.r_result is not None]
    gross_r_sum = sum(r_values)
    net_r_sum = gross_r_sum  # r_result is already computed from NET P/L -- gross vs net R here refers to
    # the SAME series (no separate "gross R" concept exists for a live DEMO trade beyond commission/swap,
    # which are already folded into net_pl_money) -- both fields kept for schema symmetry with the report.

    win_r = sum(r for r in r_values if r > 0.0)
    loss_r = abs(sum(r for r in r_values if r <= 0.0))
    profit_factor = (win_r / loss_r) if loss_r > 0.0 else (None if win_r == 0.0 else float("inf"))

    equity = starting_equity
    equity_curve = [equity]
    peak = equity
    max_dd = 0.0
    for e in closed:
        equity += e.net_pl_money or 0.0
        equity_curve.append(equity)
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
    current_dd = max(0.0, peak - equity) if equity_curve else 0.0

    consecutive_wins = consecutive_losses = 0
    max_consecutive_wins = max_consecutive_losses = 0
    for e in closed:
        if (e.net_pl_money or 0.0) > 0.0:
            consecutive_wins += 1
            consecutive_losses = 0
        else:
            consecutive_losses += 1
            consecutive_wins = 0
        max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
        max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)

    exit_reason_counts: dict[str, int] = {}
    for e in closed:
        reason = e.exit_reason or "UNKNOWN"
        exit_reason_counts[reason] = exit_reason_counts.get(reason, 0) + 1

    return SoakMetrics(
        trades=trades, wins=wins, losses=losses, win_rate=(wins / trades) if trades else None,
        gross_r_sum=gross_r_sum, net_r_sum=net_r_sum, avg_r=(net_r_sum / trades) if trades else None,
        profit_factor=profit_factor, equity_curve=tuple(equity_curve), peak_equity=peak if closed else None,
        current_drawdown=current_dd, max_drawdown=max_dd, consecutive_wins=consecutive_wins,
        consecutive_losses=consecutive_losses, max_consecutive_wins=max_consecutive_wins,
        max_consecutive_losses=max_consecutive_losses, exit_reason_counts=exit_reason_counts,
    )
