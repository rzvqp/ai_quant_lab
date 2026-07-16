"""Phase 6.9 §8.3.3 -- the single most important correctness property of the Rolling Health-Gated
Backtest: a checkpoint ``T``'s own computed Health Score must be IDENTICAL whether
``evaluate_strategy_health`` is given (a) the trade ledger truncated to ``exit_as_of <= T``, or (b)
the FULL final trade ledger (including trades far in the future of ``T``). Adding future trades to
the input must never change a past checkpoint's own already-computed score.

``metrics.trades_in_window`` already filters every window by ``start <= exit_as_of <= as_of``
(``ai_trader/strategy_health/metrics.py``), so this property holds by construction -- but per the CEO's
own directive this must be PROVEN programmatically against a realistic, multi-strategy, multi-year
trade sequence (mirroring this backtest's own shape), not merely assumed from unit tests that use tiny
synthetic fixtures."""

from __future__ import annotations

import random
from dataclasses import asdict

from ai_trader.strategy_health.evaluator import evaluate_strategy_health
from ai_trader.strategy_health.types import ClosedTrade

_DAY = 86400
RUN_START = 1_671_187_500   # Wave D's own start (2022-12-16)
RUN_END = 1_783_922_400     # Wave D's own end (2026-07-13)
STRATEGY_IDS = tuple(f"S{i}" for i in range(1, 44))  # all 43 runtime-eligible ids


def _synthetic_ledger(seed: int = 1) -> dict[str, list[ClosedTrade]]:
    """A deterministic, realistic-shaped trade ledger: every strategy gets a handful to a few dozen
    trades scattered non-uniformly across the FULL Wave D date range (mirroring real sparse-strategy
    behavior -- some strategies barely trade, some trade often), with net_pnl/pnl_r/holding_bars drawn
    from a fixed-seed RNG so the test itself is reproducible."""
    rng = random.Random(seed)
    ledger: dict[str, list[ClosedTrade]] = {sid: [] for sid in STRATEGY_IDS}
    for sid in STRATEGY_IDS:
        n_trades = rng.randint(0, 60)
        for _ in range(n_trades):
            exit_as_of = rng.randint(RUN_START, RUN_END)
            net_pnl = rng.uniform(-50.0, 80.0)
            pnl_r = rng.uniform(-1.5, 3.0) if rng.random() > 0.1 else None
            holding_bars = rng.randint(1, 400)
            ledger[sid].append(ClosedTrade(
                strategy_id=sid, exit_as_of=exit_as_of, net_pnl=net_pnl, pnl_r=pnl_r,
                holding_bars=holding_bars,
            ))
    return ledger


def _truncate(ledger: dict[str, list[ClosedTrade]], as_of: int) -> dict[str, list[ClosedTrade]]:
    """Every strategy id is KEPT (even if it ends up with an empty list) -- truncating must never
    change WHICH strategies are being evaluated, only which of their trades are visible."""
    return {sid: [t for t in trades if t.exit_as_of <= as_of] for sid, trades in ledger.items()}


# Multiple checkpoints spanning the bootstrap boundary, mid-run, and near the very end -- the
# property must hold everywhere, not just at one convenient point.
CHECKPOINTS = (
    RUN_START + 200 * _DAY,    # inside the 12-month bootstrap window
    RUN_START + 400 * _DAY,    # just past month 13 (first possible real gating checkpoint)
    RUN_START + 900 * _DAY,    # mid-run
    RUN_END - 30 * _DAY,       # near the very end
)


class TestAntiLookahead:
    def test_truncated_and_full_ledger_produce_identical_reports_at_every_checkpoint(self) -> None:
        full_ledger = _synthetic_ledger(seed=1)
        for as_of in CHECKPOINTS:
            truncated_ledger = _truncate(full_ledger, as_of)
            report_from_truncated = evaluate_strategy_health(truncated_ledger, as_of=as_of)
            report_from_full = evaluate_strategy_health(full_ledger, as_of=as_of)
            assert set(report_from_truncated) == set(report_from_full) == set(STRATEGY_IDS)
            for sid in STRATEGY_IDS:
                assert asdict(report_from_truncated[sid]) == asdict(report_from_full[sid]), (
                    f"future trades leaked into checkpoint as_of={as_of} for {sid}"
                )

    def test_adding_a_single_future_trade_never_changes_a_past_checkpoints_score(self) -> None:
        """A narrower, more surgical variant: start from a ledger already truncated at ``as_of``, then
        append ONE additional trade strictly in the future for every strategy, and re-evaluate at the
        SAME ``as_of``. Every report must be byte-identical to the pre-addition baseline."""
        as_of = RUN_START + 500 * _DAY
        baseline_ledger = _truncate(_synthetic_ledger(seed=2), as_of)
        baseline_reports = evaluate_strategy_health(baseline_ledger, as_of=as_of)

        augmented_ledger = {sid: list(trades) for sid, trades in baseline_ledger.items()}
        for sid in STRATEGY_IDS:
            augmented_ledger[sid].append(ClosedTrade(
                strategy_id=sid, exit_as_of=as_of + 30 * _DAY, net_pnl=999.0, pnl_r=5.0,
                holding_bars=1,
            ))
        augmented_reports = evaluate_strategy_health(augmented_ledger, as_of=as_of)

        for sid in STRATEGY_IDS:
            assert asdict(baseline_reports[sid]) == asdict(augmented_reports[sid]), (
                f"a future trade changed checkpoint as_of={as_of}'s own score for {sid}"
            )

    def test_a_strategy_present_only_via_future_trades_is_still_zero_evidence_at_as_of(self) -> None:
        """A strategy whose ONLY trades close after ``as_of`` must be scored identically to a strategy
        with a genuinely empty ledger -- its future trades must contribute nothing at the earlier
        checkpoint."""
        as_of = RUN_START + 300 * _DAY
        future_only = {
            "SFUTURE": [ClosedTrade(
                strategy_id="SFUTURE", exit_as_of=as_of + 10 * _DAY, net_pnl=123.0, pnl_r=2.0,
                holding_bars=5,
            )],
        }
        empty = {"SFUTURE": []}
        assert asdict(evaluate_strategy_health(future_only, as_of=as_of)["SFUTURE"]) == asdict(
            evaluate_strategy_health(empty, as_of=as_of)["SFUTURE"]
        )
