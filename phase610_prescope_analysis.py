"""Phase 6.10 Pre-Scope Diagnostic -- read-only post-hoc analysis of existing Phase 6.9A artifacts.

SCRATCH script, diagnostic only (same precedent as phase69_analysis.py / phase69a_analysis.py). Reads
`phase69a_competitive_funnel.json` and `phase69a_isolated_funnel.json` -- NO ai_trader/ source is
imported or executed, NO simulation is re-run, NO strategy/scoring/risk/execution logic is invoked.
Every number below is derived purely from the two existing JSON artifacts Phase 6.9A already produced
and committed. Writes `phase610_prescope_analysis.json`.

**Logical-position correction (found during this script's own construction, disclosed here rather than
silently fixed)**: `TradeRecord` is "one closed trade (OR PARTIAL EXIT)" per its own docstring
(`portfolio_simulator.py` line 51). Direct inspection found 65 (strategy_id, entry_as_of) pairs in the
isolated dataset (25 in the competitive dataset) where TWO TradeRecord rows share the same entry_as_of
AND entry_price AND direction, differing only in exit_as_of/exit_price/holding_bars -- a single
scaled-exit position recorded as two legs, not two independent opportunities. Counting raw TradeRecord
rows as "opportunities" would double-count these 65/25 positions. Every section below that reasons about
"opportunities" (same-bar competition, persistent blocking, gap decomposition, evidence impact) uses
LOGICAL POSITIONS (legs collapsed by (strategy_id, entry_as_of), full_exit_as_of = max leg exit_as_of).
Holding-period statistics report BOTH the raw leg-level view (823/142, matching Phase 6.9A's own
published headline trade counts verbatim) and the logical-position view (758/117), since leg-level
holding_bars is itself meaningful (e.g. "half the position exited at 269 bars, the rest at 861").
"""

from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


def load() -> tuple[dict, dict]:
    competitive = json.loads((REPO_ROOT / "phase69a_competitive_funnel.json").read_text(encoding="utf-8"))
    isolated = json.loads((REPO_ROOT / "phase69a_isolated_funnel.json").read_text(encoding="utf-8"))
    return competitive, isolated


def exit_reason(t: dict) -> str:
    """Classify a TradeRecord's own exit mechanism from its `client_order_id` string.
    Verified against source: `execution_engine/builder.py` derives `client_order_id = f"{prefix}-
    {decision_id}"`; `time_stop.py`/`trailing_stop.py` build `decision_id` as
    "TIMESTOP-{strategy}-{symbol}-{as_of}" / "TRAILSTOP-{strategy}-{symbol}-{as_of}"; a normal OCO
    bracket exit's fill carries the sibling order's own id, suffixed "-SL" or "-TP"
    (`execution_simulator.py` lines 464/473); a forced end-of-window close uses
    "LIQUIDATION-{symbol}-{as_of}" (`portfolio_simulator.py` line 324)."""
    cid = t["client_order_id"]
    if "TIMESTOP" in cid:
        return "time_stop"
    if "TRAILSTOP" in cid:
        return "trailing_stop"
    if "LIQUIDATION" in cid:
        return "liquidation_forced_close"
    if cid.endswith("-SL"):
        return "stop_loss"
    if cid.endswith("-TP"):
        return "take_profit"
    return "unclassified"


def holding_stats(trades: list[dict], label: str) -> dict:
    hb = sorted(t["holding_bars"] for t in trades)
    n = len(hb)

    def pct(p: float) -> float | None:
        if n == 0:
            return None
        k = (n - 1) * p
        f = int(k)
        c = min(f + 1, n - 1)
        if f == c:
            return hb[f]
        return hb[f] + (hb[c] - hb[f]) * (k - f)

    total_bars = sum(hb)
    top_n = max(1, round(n * 0.10))
    top_share = (sum(hb[-top_n:]) / total_bars) if total_bars else None

    by_reason: dict[str, list[int]] = defaultdict(list)
    for t in trades:
        by_reason[exit_reason(t)].append(t["holding_bars"])

    reason_summary = {
        r: {
            "count": len(v),
            "pct_of_trades": len(v) / n if n else None,
            "median_holding_bars": statistics.median(v) if v else None,
            "mean_holding_bars": round(statistics.mean(v), 1) if v else None,
            "pct_of_total_slot_bar_time": (sum(v) / total_bars) if total_bars else None,
        }
        for r, v in sorted(by_reason.items())
    }

    return {
        "label": label,
        "n_trades": n,
        "median_holding_bars": pct(0.5),
        "mean_holding_bars": round(statistics.mean(hb), 1) if hb else None,
        "p75_holding_bars": pct(0.75),
        "p90_holding_bars": pct(0.9),
        "p95_holding_bars": pct(0.95),
        "max_holding_bars": hb[-1] if hb else None,
        "total_slot_bars_occupied": total_bars,
        "top10pct_trade_count": top_n,
        "top10pct_share_of_total_slot_time": top_share,
        "by_exit_reason": reason_summary,
    }


def collapse_to_positions(trades: list[dict]) -> list[dict]:
    """Collapse partial-exit legs sharing (strategy_id, entry_as_of) into one logical position:
    full_exit_as_of = max leg exit_as_of (the position's own symbol slot isn't free until the LAST leg
    closes); holding_bars_full = bars from entry to that full close; n_legs recorded for transparency."""
    groups: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for t in trades:
        groups[(t["strategy_id"], t["entry_as_of"])].append(t)
    positions = []
    for (sid, entry), legs in groups.items():
        full_exit = max(leg["exit_as_of"] for leg in legs)
        positions.append({
            "strategy_id": sid,
            "direction": legs[0]["direction"],
            "entry_as_of": entry,
            "entry_price": legs[0]["entry_price"],
            "full_exit_as_of": full_exit,
            "holding_bars_full": max(leg["holding_bars"] for leg in legs if leg["exit_as_of"] == full_exit),
            "n_legs": len(legs),
        })
    return positions


def main() -> None:
    competitive, isolated = load()
    competitive_trades = competitive["trades"]
    all_isolated_trades: list[dict] = []
    for sid, data in isolated.items():
        for t in data["trades"]:
            all_isolated_trades.append(t)

    assert len(competitive_trades) == 142, f"unexpected competitive trade count {len(competitive_trades)}"
    assert len(all_isolated_trades) == 823, f"unexpected isolated trade count {len(all_isolated_trades)}"

    # =========================================================== Section C: holding-period structure
    # Leg level (matches Phase 6.9A's own published 823/142 headline trade counts verbatim).
    holding_competitive_legs = holding_stats(competitive_trades, "competitive_142_legs")
    holding_isolated_legs = holding_stats(all_isolated_trades, "isolated_823_legs")

    # Logical-position level (partial-exit legs collapsed; see module docstring).
    isolated_positions = collapse_to_positions(all_isolated_trades)
    competitive_positions = collapse_to_positions(competitive_trades)

    def position_holding_stats(positions: list[dict], label: str) -> dict:
        hb = sorted(p["holding_bars_full"] for p in positions)
        n = len(hb)
        total_bars = sum(hb)
        top_n = max(1, round(n * 0.10))
        top_share = (sum(hb[-top_n:]) / total_bars) if total_bars else None

        def pct(p: float) -> float | None:
            if n == 0:
                return None
            k = (n - 1) * p
            f = int(k)
            c = min(f + 1, n - 1)
            return hb[f] if f == c else hb[f] + (hb[c] - hb[f]) * (k - f)

        return {
            "label": label, "n_positions": n,
            "median_holding_bars": pct(0.5), "mean_holding_bars": round(statistics.mean(hb), 1) if hb else None,
            "p90_holding_bars": pct(0.9), "max_holding_bars": hb[-1] if hb else None,
            "total_slot_bars_occupied": total_bars,
            "top10pct_position_count": top_n,
            "top10pct_share_of_total_slot_time": top_share,
        }

    holding_isolated_positions = position_holding_stats(isolated_positions, "isolated_758_positions")
    holding_competitive_positions = position_holding_stats(competitive_positions, "competitive_117_positions")

    # =========================================================== Section A: same-bar competition
    # Opportunity unit = logical position (see module docstring). Proxy definition (disclosed as a
    # limitation): the only bar-stamped, cross-strategy-comparable event available without new
    # instrumentation is an ISOLATED POSITION ENTRY -- each one already survived Signal->Scoring->
    # Risk->Execution in isolation. True same-bar competition among the full 30,239-signal population
    # cannot be measured this way (signal_counts is a monthly aggregate with no bar timestamp/direction
    # retained) -- flagged in the report's Limitations section.
    by_bar: dict[int, list[dict]] = defaultdict(list)
    for p in isolated_positions:
        by_bar[p["entry_as_of"]].append(p)

    # A "conflict" bar requires >=2 DISTINCT STRATEGIES (not just >=2 position rows -- a single
    # strategy cannot compete against itself).
    same_bar_groups = {bar: ps for bar, ps in by_bar.items() if len({p["strategy_id"] for p in ps}) >= 2}
    positions_in_conflict = sum(len(v) for v in same_bar_groups.values())

    agree_groups = 0
    conflict_groups = 0
    price_spreads = []
    strategy_conflict_counts: dict[str, int] = defaultdict(int)
    same_direction_pair_counts: dict[tuple[str, str], int] = defaultdict(int)
    opposite_direction_pair_counts: dict[tuple[str, str], int] = defaultdict(int)

    for bar, ps in same_bar_groups.items():
        dirs = {p["direction"] for p in ps}
        if len(dirs) == 1:
            agree_groups += 1
        else:
            conflict_groups += 1
        prices = [p["entry_price"] for p in ps]
        price_spreads.append(max(prices) - min(prices))
        for p in ps:
            strategy_conflict_counts[p["strategy_id"]] += 1
        for i in range(len(ps)):
            for j in range(i + 1, len(ps)):
                a, b = ps[i], ps[j]
                if a["strategy_id"] == b["strategy_id"]:
                    continue
                pair = tuple(sorted((a["strategy_id"], b["strategy_id"])))
                if a["direction"] == b["direction"]:
                    same_direction_pair_counts[pair] += 1
                else:
                    opposite_direction_pair_counts[pair] += 1

    competitive_entry_bars = {p["entry_as_of"] for p in competitive_positions}
    competitive_bars_that_were_conflicted = competitive_entry_bars & set(same_bar_groups.keys())

    same_bar_analysis = {
        "definition": "an entry_as_of bar shared by >=2 DIFFERENT strategies' isolated-run logical positions",
        "total_isolated_positions": len(isolated_positions),
        "distinct_entry_bars_used_by_isolated_positions": len(by_bar),
        "bars_with_2plus_competing_strategies": len(same_bar_groups),
        "isolated_positions_involved_in_a_same_bar_conflict": positions_in_conflict,
        "pct_isolated_positions_in_same_bar_conflict": positions_in_conflict / len(isolated_positions),
        "conflict_groups_all_same_direction": agree_groups,
        "conflict_groups_mixed_direction": conflict_groups,
        "pct_conflict_groups_mixed_direction": (conflict_groups / len(same_bar_groups)) if same_bar_groups else None,
        "mean_entry_price_spread_within_conflict_group": statistics.mean(price_spreads) if price_spreads else None,
        "max_entry_price_spread_within_conflict_group": max(price_spreads) if price_spreads else None,
        "competitive_position_entry_bars_total": len(competitive_entry_bars),
        "competitive_position_entry_bars_that_were_also_isolated_conflict_bars": len(competitive_bars_that_were_conflicted),
        "top_10_strategies_by_conflict_participation": sorted(strategy_conflict_counts.items(), key=lambda kv: -kv[1])[:10],
        "top_10_same_direction_pairs": sorted(same_direction_pair_counts.items(), key=lambda kv: -kv[1])[:10],
        "top_10_opposite_direction_pairs": sorted(opposite_direction_pair_counts.items(), key=lambda kv: -kv[1])[:10],
    }

    # =========================================================== Section B: persistent blocking
    # Definition: position X's entry_as_of falls STRICTLY inside another (different-strategy) isolated
    # position Y's own open interval [entry_as_of, full_exit_as_of). Counterfactual overlay (assumes all
    # 43 strategies' isolated positions were simultaneously "real", which only one slot could ever
    # actually hold) -- an upper-bound proxy for blocking pressure, not an exact historical
    # reconstruction. Disclosed as a limitation.
    blocked_count = 0
    blocked_by_strategy: dict[str, int] = defaultdict(int)
    blocker_strategy: dict[str, int] = defaultdict(int)
    blocking_pairs: dict[tuple[str, str], int] = defaultdict(int)
    persistent_block_durations: list[int] = []
    blocked_position_keys: set[tuple[str, int]] = set()

    for x in isolated_positions:
        for y in isolated_positions:
            if x["strategy_id"] == y["strategy_id"]:
                continue
            if y["entry_as_of"] < x["entry_as_of"] < y["full_exit_as_of"]:
                blocked_count += 1
                blocked_by_strategy[x["strategy_id"]] += 1
                blocker_strategy[y["strategy_id"]] += 1
                blocking_pairs[(y["strategy_id"], x["strategy_id"])] += 1
                persistent_block_durations.append(y["holding_bars_full"])
                blocked_position_keys.add((x["strategy_id"], x["entry_as_of"]))

    persistent_blocking_analysis = {
        "definition": "position entry falls strictly inside another (different-strategy) isolated position's open interval [entry_as_of, full_exit_as_of)",
        "total_blocking_relationships_measured": blocked_count,
        "distinct_isolated_positions_blocked_at_least_once": len(blocked_position_keys),
        "pct_isolated_positions_blocked_at_least_once": len(blocked_position_keys) / len(isolated_positions),
        "top_10_blocker_strategies": sorted(blocker_strategy.items(), key=lambda kv: -kv[1])[:10],
        "top_10_victim_strategies": sorted(blocked_by_strategy.items(), key=lambda kv: -kv[1])[:10],
        "top_10_blocker_victim_pairs": sorted(blocking_pairs.items(), key=lambda kv: -kv[1])[:10],
        "median_blocking_position_holding_bars": statistics.median(persistent_block_durations) if persistent_block_durations else None,
        "mean_blocking_position_holding_bars": round(statistics.mean(persistent_block_durations), 1) if persistent_block_durations else None,
    }

    # =========================================================== Gap decomposition (same-bar vs persistent vs unexplained)
    # Opportunity unit = logical position. For each isolated position, does a competitive position exist
    # at the same (strategy_id, entry_as_of)? If yes -> "realized". If not, it is part of "the gap".
    #
    # IMPORTANT (found during this script's own consistency re-check, disclosed rather than silently
    # fixed): same-bar conflict and persistent blocking are NOT naturally mutually exclusive sets -- a
    # gap position can simultaneously (a) share its entry bar with another strategy's isolated position
    # AND (b) fall inside a THIRD strategy's longer-held isolated position. An earlier version of this
    # script used a priority rule (classify same-bar first, else persistent, else neither) that silently
    # forced a partition and buried this overlap. This version reports the full, honest 4-way breakdown
    # (same-bar-ONLY / persistent-ONLY / BOTH / neither) with no priority rule -- both the ORIGINAL
    # forced-partition figures (kept for continuity with the already-published report) and the true
    # overlap are written out, so the reader sees the overlap explicitly rather than an artifact of
    # classification order.
    competitive_keys = {(p["strategy_id"], p["entry_as_of"]) for p in competitive_positions}
    isolated_keys = {(p["strategy_id"], p["entry_as_of"]) for p in isolated_positions}

    matched = isolated_keys & competitive_keys
    unmatched = isolated_keys - competitive_keys
    competitive_without_isolated_match = competitive_keys - isolated_keys

    same_bar_conflict_keys = set()
    for bar, ps in same_bar_groups.items():
        for p in ps:
            same_bar_conflict_keys.add((p["strategy_id"], p["entry_as_of"]))

    gap_same_bar_forced = 0   # priority: same-bar checked first (matches the originally published figures)
    gap_persistent_forced = 0
    gap_unexplained = 0
    gap_same_bar_only = 0     # honest 4-way breakdown, no priority rule
    gap_persistent_only = 0
    gap_both = 0
    for key in unmatched:
        in_same_bar = key in same_bar_conflict_keys
        in_blocked = key in blocked_position_keys
        if in_same_bar:
            gap_same_bar_forced += 1
        elif in_blocked:
            gap_persistent_forced += 1
        else:
            gap_unexplained += 1

        if in_same_bar and in_blocked:
            gap_both += 1
        elif in_same_bar:
            gap_same_bar_only += 1
        elif in_blocked:
            gap_persistent_only += 1

    gap_decomposition = {
        "isolated_positions_total": len(isolated_positions),
        "competitive_positions_total": len(competitive_positions),
        "raw_gap_positions": len(isolated_positions) - len(competitive_positions),
        "isolated_positions_matched_to_a_same_strategy_same_bar_competitive_position": len(matched),
        "isolated_positions_unmatched_i_e_the_gap": len(unmatched),
        "competitive_positions_with_no_matching_isolated_entry_cooldown_asymmetry_signal": len(competitive_without_isolated_match),
        # forced-partition view (same-bar given priority) -- matches the originally published headline split
        "forced_partition_gap_same_bar_priority": gap_same_bar_forced,
        "forced_partition_gap_persistent_priority": gap_persistent_forced,
        "forced_partition_gap_unexplained": gap_unexplained,
        "forced_partition_pct_same_bar": gap_same_bar_forced / len(unmatched) if unmatched else None,
        "forced_partition_pct_persistent": gap_persistent_forced / len(unmatched) if unmatched else None,
        "forced_partition_pct_unexplained": gap_unexplained / len(unmatched) if unmatched else None,
        # honest 4-way breakdown -- no priority rule, overlap shown explicitly
        "honest_gap_same_bar_only": gap_same_bar_only,
        "honest_gap_persistent_only": gap_persistent_only,
        "honest_gap_both_mechanisms": gap_both,
        "honest_gap_neither": gap_unexplained,
        "pct_gap_same_bar_only": gap_same_bar_only / len(unmatched) if unmatched else None,
        "pct_gap_persistent_only": gap_persistent_only / len(unmatched) if unmatched else None,
        "pct_gap_both_mechanisms": gap_both / len(unmatched) if unmatched else None,
        "pct_gap_neither": gap_unexplained / len(unmatched) if unmatched else None,
        # "present" totals -- how often each mechanism appears at all, alone or combined
        "pct_gap_with_same_bar_present": (gap_same_bar_only + gap_both) / len(unmatched) if unmatched else None,
        "pct_gap_with_persistent_present": (gap_persistent_only + gap_both) / len(unmatched) if unmatched else None,
    }

    # =========================================================== Section E: independent-evidence estimate
    # Economically-distinct opportunity count, two bounds, both over logical positions:
    #  LOWER bound (strict): dedup only exact-same-bar entries into one event each.
    #  UPPER bound (loose):  connected components of the full temporal-overlap graph (same-bar OR
    #                        persistent-block edges) -- unions everything that ever touches.
    lower_bound_distinct = len(by_bar)

    idx = list(range(len(isolated_positions)))
    parent = list(range(len(isolated_positions)))

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    trades_sorted_idx = sorted(idx, key=lambda i: isolated_positions[i]["entry_as_of"])
    for ii in range(len(trades_sorted_idx)):
        i = trades_sorted_idx[ii]
        ti = isolated_positions[i]
        for jj in range(ii + 1, len(trades_sorted_idx)):
            j = trades_sorted_idx[jj]
            tj = isolated_positions[j]
            if tj["entry_as_of"] > ti["full_exit_as_of"] and tj["entry_as_of"] != ti["entry_as_of"]:
                break  # sorted by entry: once tj starts after ti closes (non-tie), no further j overlaps ti
            if ti["strategy_id"] == tj["strategy_id"]:
                continue
            same_bar = ti["entry_as_of"] == tj["entry_as_of"]
            overlap = (ti["entry_as_of"] <= tj["entry_as_of"] < ti["full_exit_as_of"]
                       or tj["entry_as_of"] <= ti["entry_as_of"] < tj["full_exit_as_of"])
            if same_bar or overlap:
                union(i, j)

    upper_bound_distinct = len({find(i) for i in idx})

    raw_setups_total = 0
    for sid, months in competitive["signal_counts"].items():
        for month, bucket in months.items():
            raw_setups_total += bucket.get("actionable", 0) + bucket.get("wait_confirmation", 0) + bucket.get("no_signal_setup_present", 0)
    risk_allow_total = 0
    risk_deny_total = 0
    for sid, months in competitive["risk_counts"].items():
        for month, bucket in months.items():
            risk_allow_total += bucket.get("allow", 0)
            risk_deny_total += bucket.get("deny", 0)

    evidence_impact = {
        "raw_setup_detections_portfolio_wide": raw_setups_total,
        "risk_manager_allow_total": risk_allow_total,
        "risk_manager_deny_total": risk_deny_total,
        "risk_manager_evaluated_opportunities": risk_allow_total + risk_deny_total,
        "executable_opportunity_count_isolated_no_slot_contention_legs": len(all_isolated_trades),
        "executable_opportunity_count_isolated_no_slot_contention_positions": len(isolated_positions),
        "economically_distinct_opportunity_count_lower_bound_strict_same_bar_dedup": lower_bound_distinct,
        "economically_distinct_opportunity_count_upper_bound_overlap_connected_components": upper_bound_distinct,
        "redundancy_ratio_lower_bound": 1 - (lower_bound_distinct / len(isolated_positions)),
        "redundancy_ratio_upper_bound": 1 - (upper_bound_distinct / len(isolated_positions)),
        "completed_trades_competitive_realized_evidence_legs": len(competitive_trades),
        "completed_trades_competitive_realized_evidence_positions": len(competitive_positions),
    }

    out = {
        "source_artifacts": ["phase69a_competitive_funnel.json", "phase69a_isolated_funnel.json"],
        "logical_position_correction": {
            "isolated_legs": len(all_isolated_trades), "isolated_positions": len(isolated_positions),
            "isolated_multi_leg_positions": len(all_isolated_trades) - len(isolated_positions),
            "competitive_legs": len(competitive_trades), "competitive_positions": len(competitive_positions),
            "competitive_multi_leg_positions": len(competitive_trades) - len(competitive_positions),
        },
        "holding_period": {
            "legs": {"competitive": holding_competitive_legs, "isolated": holding_isolated_legs},
            "positions": {"competitive": holding_competitive_positions, "isolated": holding_isolated_positions},
        },
        "same_bar_competition": same_bar_analysis,
        "persistent_blocking": persistent_blocking_analysis,
        "gap_decomposition": gap_decomposition,
        "evidence_impact": evidence_impact,
    }

    out_path = REPO_ROOT / "phase610_prescope_analysis.json"
    out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(json.dumps(out, indent=2, default=str))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
