"""Current XAUUSD 12-Month Relevance Audit -- portfolios B/C/D (SCRATCH, preserved artifact).
Identical config to portfolio A (`relevance12m_run.py`), differing ONLY in `strategy_id_filter`:
  B = CURRENTLY_STRONG only
  C = CURRENTLY_STRONG + CURRENTLY_USABLE
  D = all strategies except CURRENTLY_WEAK (i.e. STRONG + USABLE + INSUFFICIENT_EVIDENCE)
"""

from __future__ import annotations

import json
from pathlib import Path

from relevance12m_run import _performance_dict, _trade_to_dict, run_variant

REPO_ROOT = Path(__file__).resolve().parent


def main() -> None:
    per_strategy = json.loads((REPO_ROOT / "relevance12m_perstrategy.json").read_text(encoding="utf-8"))
    rows = per_strategy["strategies"]

    strong = frozenset(r["strategy_id"] for r in rows if r["classification"] == "CURRENTLY_STRONG")
    usable = frozenset(r["strategy_id"] for r in rows if r["classification"] == "CURRENTLY_USABLE")
    weak = frozenset(r["strategy_id"] for r in rows if r["classification"] == "CURRENTLY_WEAK")
    insufficient = frozenset(r["strategy_id"] for r in rows if r["classification"] == "INSUFFICIENT_EVIDENCE")
    all_ids = frozenset(r["strategy_id"] for r in rows)

    variant_b_ids = strong
    variant_c_ids = strong | usable
    variant_d_ids = all_ids - weak

    print(f"STRONG ({len(strong)}): {sorted(strong)}")
    print(f"USABLE ({len(usable)}): {sorted(usable)}")
    print(f"WEAK ({len(weak)}): {sorted(weak)}")
    print(f"INSUFFICIENT_EVIDENCE ({len(insufficient)}): {sorted(insufficient)}")
    print(f"B (STRONG only) = {len(variant_b_ids)} strategies")
    print(f"C (STRONG+USABLE) = {len(variant_c_ids)} strategies")
    print(f"D (all except WEAK) = {len(variant_d_ids)} strategies: {sorted(variant_d_ids)}")

    results = {}
    for label, ids in (("B_strong_only", variant_b_ids), ("C_strong_plus_usable", variant_c_ids), ("D_all_except_weak", variant_d_ids)):
        print(f"=== Running variant {label} ({len(ids)} strategies) ===", flush=True)
        harness = run_variant(f"RELEVANCE12M-{label.upper()}", strategy_id_filter=ids)
        assert harness.portfolio_simulator is not None
        perf = _performance_dict(harness)
        trades = [_trade_to_dict(t) for t in harness.portfolio_simulator.account.trade_ledger]
        print(json.dumps(perf["performance"], indent=2), flush=True)
        results[label] = {"strategy_ids": sorted(ids), "performance": perf, "trades": trades}

    out_path = REPO_ROOT / "relevance12m_portfolioBCD.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
