"""Phase 6.9A -- Strategy Evidence Flow Audit: conversion rates + suppression classification.
SCRATCH script, preserved diagnostic artifact.

Suppression categories (thresholds fixed here, before inspecting the final classification table, per
the CEO's own "do not tune after seeing results" discipline applied throughout this project):

A. GENUINE_LOW_MARKET_FREQUENCY -- raw setup detections themselves are rare (<12 over the whole
   12-month window, i.e. averaging under 1/month) -- the pattern barely occurs, competitive or not.
B. SHARED_SLOT_SUPPRESSION -- isolated-slot trades exceed competitive trades by at least 5 AND at
   least 50% relative -- slot contention measurably costs this strategy real trades.
C. SCORING_SUPPRESSION -- actionable signals that Scoring Engine still downgraded below the allowed
   recommendation floor (STRONG/MODERATE/WEAK_OPPORTUNITY) are >= 20% of this strategy's own
   actionable-signal count.
D. RISK_SUPPRESSION -- Risk Manager DENY reasons OTHER than the mechanical NOT_ACTIONABLE/BELOW_FLOOR
   echoes and OTHER than LIMIT_MAX_PER_SYMBOL (i.e. genuine filter/cooldown/sizing/other-limit denials)
   are >= 20% of this strategy's own scored-actionable count.
E. EXECUTION_SUPPRESSION -- rejected + expired orders are >= 20% of this strategy's own submitted
   orders.
F. INSUFFICIENT_DATA -- NEED_CONTEXT outcomes are >= 50% of all this strategy's own per-bar outcomes.
G. MIXED_CAUSES -- more than one of B-F applies meaningfully, per the above thresholds.

A strategy is NEVER classified from completed-trade count alone -- every rule above reads from the
funnel (setup/signal/scoring/risk/execution counts), never from `n_trades` directly.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

MECHANICAL_ECHO_REASONS = {"NOT_ACTIONABLE", "BELOW_FLOOR"}
SHARED_SLOT_REASON = "LIMIT_MAX_PER_SYMBOL"


def _sum_months(months: dict[str, dict[str, int]], key: str) -> int:
    return sum(bucket.get(key, 0) for bucket in months.values())


def analyze_strategy(sid: str, competitive: dict, isolated: dict) -> dict:
    signal_months = competitive["signal_counts"].get(sid, {})
    scoring_months = competitive["scoring_counts"].get(sid, {})
    risk_months = competitive["risk_counts"].get(sid, {})
    deny_reasons = competitive["risk_deny_reasons"].get(sid, {})
    shared_slot_by_month = competitive["shared_slot_denials_by_month"].get(sid, {})
    order_counts = competitive["order_counts"].get(sid, {})

    actionable = _sum_months(signal_months, "actionable")
    wait_confirmation = _sum_months(signal_months, "wait_confirmation")
    need_context = _sum_months(signal_months, "need_context")
    blocked = _sum_months(signal_months, "blocked")
    invalid = _sum_months(signal_months, "invalid")
    no_signal_no_setup = _sum_months(signal_months, "no_signal_no_setup")
    no_signal_setup_present = _sum_months(signal_months, "no_signal_setup_present")
    no_signal_total = no_signal_no_setup + no_signal_setup_present
    total_bars_evaluated = actionable + wait_confirmation + need_context + blocked + invalid + no_signal_total
    raw_setups = actionable + wait_confirmation + no_signal_setup_present

    scored_actionable = _sum_months(scoring_months, "scored_actionable")
    rejected_by_scoring = _sum_months(scoring_months, "rejected_by_scoring")
    genuine_scoring_suppression = max(0, actionable - scored_actionable)

    allow_count = _sum_months(risk_months, "allow")
    deny_count = _sum_months(risk_months, "deny")
    shared_slot_denials = sum(shared_slot_by_month.values())
    mechanical_echo_denials = sum(deny_reasons.get(r, 0) for r in MECHANICAL_ECHO_REASONS)
    genuine_risk_denials = sum(
        c for r, c in deny_reasons.items() if r not in MECHANICAL_ECHO_REASONS and r != SHARED_SLOT_REASON
    )

    submitted = order_counts.get("submitted", 0)
    filled = order_counts.get("filled", 0)
    partially_filled = order_counts.get("partially_filled", 0)
    rejected = order_counts.get("rejected", 0)
    expired = order_counts.get("expired", 0)
    cancelled = order_counts.get("cancelled", 0)

    n_trades_competitive = isolated["_competitive_trades"][sid]
    n_trades_isolated = isolated["strategies"].get(sid, {}).get("n_trades", 0)

    months_with_zero_setups = sum(
        1 for m, bucket in signal_months.items()
        if (bucket.get("actionable", 0) + bucket.get("wait_confirmation", 0) + bucket.get("no_signal_setup_present", 0)) == 0
    )
    # `months_with_setups_but_zero_trades` is computed by the caller (main()), which has the trade
    # ledger's own month-of-exit membership available; not duplicated here.

    # ---- suppression classification (funnel-based, never from n_trades alone)
    # Ratios computed for the classification (fixed thresholds, decided before inspecting the final
    # table -- see module docstring); kept alongside the raw counts so a reader can independently
    # re-derive every classification instead of trusting the label alone.
    slot_gap = max(0, n_trades_isolated - n_trades_competitive)
    slot_ratio = (slot_gap / n_trades_isolated) if n_trades_isolated > 0 else 0.0
    scoring_ratio = (genuine_scoring_suppression / actionable) if actionable > 0 else 0.0
    risk_ratio = (genuine_risk_denials / scored_actionable) if scored_actionable > 0 else 0.0
    execution_ratio = ((rejected + expired) / submitted) if submitted > 0 else 0.0
    context_ratio = (need_context / total_bars_evaluated) if total_bars_evaluated > 0 else 0.0

    causes = []
    if raw_setups < 12:
        causes.append("A")
    if slot_gap >= 5 and slot_ratio >= 0.30:
        causes.append("B")
    if scoring_ratio >= 0.20:
        causes.append("C")
    if risk_ratio >= 0.20:
        causes.append("D")
    if execution_ratio >= 0.20:
        causes.append("E")
    if context_ratio >= 0.50:
        causes.append("F")

    if len(causes) > 1:
        principal = "G"
        secondary = ",".join(causes)
    elif len(causes) == 1:
        principal = causes[0]
        secondary = None
    else:
        # No single cause crosses its own threshold -- per the CEO's own 7-category scheme this is
        # still "mixed/diffuse" (G), never an 8th invented bucket: report whichever partial,
        # sub-threshold contributors are largest, so the diffuseness itself is inspectable, not hidden.
        principal = "G"
        partials = sorted(
            [("B", slot_ratio), ("C", scoring_ratio), ("D", risk_ratio), ("E", execution_ratio), ("F", context_ratio)],
            key=lambda kv: -kv[1],
        )
        secondary = "sub-threshold: " + ", ".join(f"{k}={v:.0%}" for k, v in partials if v > 0) or "no measurable suppression at any stage"

    # confidence in diagnosis: high if funnel has enough volume to distinguish causes cleanly,
    # low if total_bars_evaluated / raw_setups / scored_actionable are themselves too small to trust
    # the ratios above (a ratio computed from n=1-2 is not a reliable diagnosis).
    if raw_setups >= 20 and (scored_actionable >= 10 or actionable == 0):
        confidence = "HIGH"
    elif raw_setups >= 5:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    return {
        "strategy_id": sid,
        "total_bars_evaluated": total_bars_evaluated,
        "raw_setups": raw_setups,
        "actionable_signals": actionable,
        "no_signal_outcomes": no_signal_total,
        "no_signal_no_setup": no_signal_no_setup,
        "no_signal_setup_present": no_signal_setup_present,
        "wait_confirmation_outcomes": wait_confirmation,
        "need_context_outcomes": need_context,
        "blocked_outcomes": blocked,
        "invalid_outcomes": invalid,
        "scored_actionable": scored_actionable,
        "rejected_by_scoring_total": rejected_by_scoring,
        "genuine_scoring_suppression": genuine_scoring_suppression,
        "risk_allow": allow_count,
        "risk_deny": deny_count,
        "shared_slot_denials": shared_slot_denials,
        "mechanical_echo_denials": mechanical_echo_denials,
        "genuine_risk_denials": genuine_risk_denials,
        "deny_reason_breakdown": deny_reasons,
        "orders_submitted": submitted,
        "orders_filled": filled,
        "orders_partially_filled": partially_filled,
        "orders_rejected": rejected,
        "orders_expired": expired,
        "orders_cancelled": cancelled,
        "n_trades_competitive": n_trades_competitive,
        "n_trades_isolated": n_trades_isolated,
        "missed_opportunities_due_to_slot_contention": slot_gap,
        "shared_slot_suppression_ratio": slot_ratio if n_trades_isolated > 0 else None,
        "scoring_suppression_ratio": scoring_ratio,
        "risk_suppression_ratio": risk_ratio,
        "execution_suppression_ratio": execution_ratio,
        "context_suppression_ratio": context_ratio,
        "months_with_zero_setups": months_with_zero_setups,
        "n_months_in_window": len(signal_months) if signal_months else 13,
        "principal_cause": principal,
        "secondary_causes": secondary,
        "confidence_in_diagnosis": confidence,
    }


def _trade_months(trades: list[dict]) -> dict[str, set]:
    from datetime import UTC, datetime
    by_strategy: dict[str, set] = defaultdict(set)
    for t in trades:
        month = datetime.fromtimestamp(t["exit_as_of"], tz=UTC).strftime("%Y-%m")
        by_strategy[t["strategy_id"]].add(month)
    return by_strategy


def main() -> None:
    competitive = json.loads((REPO_ROOT / "phase69a_competitive_funnel.json").read_text(encoding="utf-8"))
    isolated_raw = json.loads((REPO_ROOT / "phase69a_isolated_funnel.json").read_text(encoding="utf-8"))
    all_ids = competitive["all_strategy_ids"]

    competitive_trade_counts: dict[str, int] = defaultdict(int)
    for t in competitive["trades"]:
        competitive_trade_counts[t["strategy_id"]] += 1
    isolated_wrapped = {"strategies": isolated_raw, "_competitive_trades": competitive_trade_counts}

    trade_months_by_strategy = _trade_months(competitive["trades"])

    rows = []
    for sid in all_ids:
        row = analyze_strategy(sid, competitive, isolated_wrapped)
        setup_months = set()
        for m, bucket in competitive["signal_counts"].get(sid, {}).items():
            if bucket.get("actionable", 0) + bucket.get("wait_confirmation", 0) + bucket.get("no_signal_setup_present", 0) > 0:
                setup_months.add(m)
        trade_months = trade_months_by_strategy.get(sid, set())
        row["months_with_setups_but_zero_trades"] = len(setup_months - trade_months)
        rows.append(row)

    rows.sort(key=lambda r: -r["raw_setups"])

    cause_counts: dict[str, int] = defaultdict(int)
    for r in rows:
        cause_counts[r["principal_cause"]] += 1

    out = {"n_strategies": len(rows), "principal_cause_counts": dict(cause_counts), "strategies": rows}
    (REPO_ROOT / "phase69a_analysis.json").write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")

    print(json.dumps({"principal_cause_counts": dict(cause_counts)}, indent=2))
    for r in rows:
        print(f"{r['strategy_id']:5s} setups={r['raw_setups']:4d} actionable={r['actionable_signals']:4d} "
              f"comp_trades={r['n_trades_competitive']:3d} iso_trades={r['n_trades_isolated']:3d} "
              f"principal={r['principal_cause']:25s} secondary={r['secondary_causes']} conf={r['confidence_in_diagnosis']}")
    print("Wrote phase69a_analysis.json")


if __name__ == "__main__":
    main()
