"""Phase 6.9A -- Strategy Evidence Flow Audit: the funnel-measurement instrumentation technique
(SCRATCH module, preserved diagnostic artifact, same precedent as phase69_*.py/relevance12m_*.py).

**Zero-file-diff measurement technique**: rather than modifying any frozen pipeline module (Signal
Engine, Scoring Engine, Risk Manager, Execution Simulator), this module monkey-patches the bound
methods of the ALREADY-CONSTRUCTED harness instance's own component objects
(`harness._signal_engine.evaluate`, `harness._scoring_engine.score_batch`,
`harness._risk_manager.evaluate`) AFTER `harness.load()` has built them. Each wrapper calls the
ORIGINAL, unmodified implementation and returns its result UNCHANGED -- it only additionally records
that same result for counting. This changes ZERO lines in any `ai_trader/` source file; the actual
decision logic that runs is the exact same compiled code the production harness always runs.
`phase69a_funnel_run.py::verify_zero_behavior_change()` proves an instrumented run and a plain run
produce a byte-identical trade ledger and FULL simulation report (portfolio summary, performance,
attribution, stats, allocation, risk events -- not just a subset) over the same config -- the
empirical proof this technique changes nothing. It is a manually-invoked script function, not a
pytest-collected regression test; re-run it after any future edit to this module.

The remaining funnel stages (order-level fill/reject/expire/partial, completed trades) need NO
monkey-patch at all: `ExecutionSimulator._orders` (a dict of `WorkingOrder`, each already carrying its
own `strategy_id`) and `PortfolioSimulator.account.trade_ledger` (each `TradeRecord` already carrying
`strategy_id`) are read directly, after the run, with no modification and no private-state mutation --
only reads.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime

SIGNAL_STATE_BUCKETS = (
    "actionable", "wait_confirmation", "need_context", "blocked", "invalid",
    "no_signal_no_setup", "no_signal_setup_present",
)


def _month_key(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=UTC).strftime("%Y-%m")


class FunnelRecorder:
    """Per-strategy, per-month tallies for every funnel stage the CEO's Phase 6.9A directive named.
    A plain, dependency-free counter -- no state feeds back into any decision."""

    def __init__(self) -> None:
        # signal_counts[strategy_id][month][bucket] = count
        self.signal_counts: dict[str, dict[str, dict[str, int]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        # scoring_counts[strategy_id][month]["scored_actionable" | "rejected_by_scoring"] = count
        self.scoring_counts: dict[str, dict[str, dict[str, int]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        # risk_counts[strategy_id][month]["allow" | "deny"] = count; risk_deny_reasons[strategy_id][reason] = count
        self.risk_counts: dict[str, dict[str, dict[str, int]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        self.risk_deny_reasons: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.shared_slot_denials: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    # ------------------------------------------------------------------ Signal Engine tap

    def record_signal_batch(self, as_of: int, signal_batch: object) -> None:
        month = _month_key(as_of)
        for signal in signal_batch.signals:  # type: ignore[attr-defined]
            sid = signal.strategy_id
            state = signal.state.value
            if state in ("BUY", "SELL"):
                bucket = "actionable"
            elif state == "WAIT_CONFIRMATION":
                bucket = "wait_confirmation"
            elif state == "NEED_CONTEXT":
                bucket = "need_context"
            elif state == "BLOCKED":
                bucket = "blocked"
            elif state == "INVALID":
                bucket = "invalid"
            elif state == "NO_SIGNAL":
                why_failed = signal.explanation.why_failed if signal.explanation is not None else ()
                code = why_failed[0].code if why_failed else None
                bucket = "no_signal_setup_present" if code == "NO_SIGNAL_PRESENT" else "no_signal_no_setup"
            else:
                bucket = "no_signal_no_setup"  # LONG_READY/SHORT_READY: not reachable in v1 (pipeline.py's
                # own docstring: "v1 treats every present+confirmed signal as immediately actionable"),
                # kept here only as a fail-safe, never-fabricated default, not a silent crash.
            self.signal_counts[sid][month][bucket] += 1

    # ------------------------------------------------------------------ Scoring Engine tap

    _ALLOWED_RECOMMENDATIONS = frozenset({"STRONG_OPPORTUNITY", "MODERATE_OPPORTUNITY", "WEAK_OPPORTUNITY"})

    def record_score_batch(self, as_of: int, score_batch: object) -> None:
        month = _month_key(as_of)
        for score in score_batch.scores:  # type: ignore[attr-defined]
            sid = score.strategy_id
            if score.recommendation.value in self._ALLOWED_RECOMMENDATIONS:
                self.scoring_counts[sid][month]["scored_actionable"] += 1
            else:
                self.scoring_counts[sid][month]["rejected_by_scoring"] += 1

    # ------------------------------------------------------------------ Risk Manager tap

    def record_decision_batch(self, as_of: int, decision_batch: object) -> None:
        month = _month_key(as_of)
        for decision in decision_batch.decisions:  # type: ignore[attr-defined]
            sid = decision.strategy_id
            if decision.decision.value == "ALLOW":
                self.risk_counts[sid][month]["allow"] += 1
            else:
                self.risk_counts[sid][month]["deny"] += 1
                reasons = decision.denied_reasons or ()
                if reasons:
                    for reason in reasons:
                        self.risk_deny_reasons[sid][reason.code] += 1
                        if reason.code == "LIMIT_MAX_PER_SYMBOL":
                            self.shared_slot_denials[sid][month] += 1
                else:
                    self.risk_deny_reasons[sid]["UNSPECIFIED"] += 1


def instrument(harness: object, recorder: FunnelRecorder) -> None:
    """Monkey-patch the CONSTRUCTED harness instance's own component bound methods to tap their
    return values. Must be called AFTER `harness.load()` (the point `_signal_engine`/
    `_scoring_engine`/`_risk_manager` are actually constructed). Every wrapper delegates to the
    ORIGINAL bound method and returns its result completely unmodified."""
    original_evaluate = harness._signal_engine.evaluate  # type: ignore[attr-defined]

    def wrapped_evaluate(ctx: object, handles: object, trader_state: object = None) -> object:
        batch = original_evaluate(ctx, handles, trader_state)
        recorder.record_signal_batch(batch.as_of, batch)
        return batch

    harness._signal_engine.evaluate = wrapped_evaluate  # type: ignore[attr-defined]

    original_score_batch = harness._scoring_engine.score_batch  # type: ignore[attr-defined]

    def wrapped_score_batch(signals: object) -> object:
        batch = original_score_batch(signals)
        recorder.record_score_batch(batch.as_of, batch)
        return batch

    harness._scoring_engine.score_batch = wrapped_score_batch  # type: ignore[attr-defined]

    original_risk_evaluate = harness._risk_manager.evaluate  # type: ignore[attr-defined]

    def wrapped_risk_evaluate(scores: object, risk_context: object, portfolio_state: object) -> object:
        batch = original_risk_evaluate(scores, risk_context, portfolio_state)
        recorder.record_decision_batch(batch.as_of, batch)
        return batch

    harness._risk_manager.evaluate = wrapped_risk_evaluate  # type: ignore[attr-defined]


def order_level_counts(harness: object) -> dict[str, dict[str, int]]:
    """Read-only, post-run: every order's own terminal `WorkingOrderState`, tagged by its own
    `strategy_id` -- `ExecutionSimulator._orders` already carries both; nothing is mutated, nothing
    added, this only reads a dict that already exists at the end of any run."""
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for order in harness.execution_simulator._orders.values():  # type: ignore[attr-defined]
        sid = order.strategy_id
        state = order.state.value
        counts[sid]["submitted"] += 1
        if state == "FILLED":
            counts[sid]["filled"] += 1
        elif state == "PARTIALLY_FILLED":
            counts[sid]["partially_filled"] += 1
        elif state == "REJECTED":
            counts[sid]["rejected"] += 1
        elif state == "EXPIRED":
            counts[sid]["expired"] += 1
        elif state == "CANCELLED":
            counts[sid]["cancelled"] += 1
    return counts
