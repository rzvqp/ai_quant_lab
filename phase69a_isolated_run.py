"""Phase 6.9A -- Strategy Evidence Flow Audit: the isolated-slot counterfactual. Runs EVERY one of the
43 strategies ALONE (`strategy_id_filter=frozenset({that one id})`) over the EXACT SAME window/config
as the competitive run (`phase69a_funnel_run.py`) -- same market data, cost model, risk policy,
scoring logic, execution model, initial capital, seed. A diagnostic counterfactual only: measures how
many trades/signals each strategy would produce with ZERO competition for the shared XAUUSD slot.
Does NOT change, and is never used to change, production (all-43) behavior. SCRATCH script, preserved
diagnostic artifact.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from ai_trader.simulation.types import RunState
from phase69a_funnel_recorder import FunnelRecorder, instrument, order_level_counts
from phase69a_funnel_run import _performance_dict, _trade_to_dict, new_harness

REPO_ROOT = Path(__file__).resolve().parent


def run_isolated(strategy_id: str) -> dict[str, object]:
    harness = new_harness(f"PHASE69A-ISOLATED-{strategy_id}", strategy_id_filter=frozenset({strategy_id}))
    recorder = FunnelRecorder()
    instrument(harness, recorder)
    harness.run_to_completion()
    assert harness.state is RunState.COMPLETED, harness.fail_reason
    assert harness.portfolio_simulator is not None

    trades = [_trade_to_dict(t) for t in harness.portfolio_simulator.account.trade_ledger]
    order_counts = order_level_counts(harness)
    return {
        "strategy_id": strategy_id,
        "performance": _performance_dict(harness),
        "trades": trades,
        "n_trades": len(trades),
        "signal_counts": {m: dict(b) for m, b in recorder.signal_counts.get(strategy_id, {}).items()},
        "scoring_counts": {m: dict(b) for m, b in recorder.scoring_counts.get(strategy_id, {}).items()},
        "risk_counts": {m: dict(b) for m, b in recorder.risk_counts.get(strategy_id, {}).items()},
        "risk_deny_reasons": dict(recorder.risk_deny_reasons.get(strategy_id, {})),
        "order_counts": dict(order_counts.get(strategy_id, {})),
    }


def main() -> None:
    competitive = json.loads((REPO_ROOT / "phase69a_competitive_funnel.json").read_text(encoding="utf-8"))
    all_ids = competitive["all_strategy_ids"]

    results: dict[str, object] = {}
    for i, sid in enumerate(all_ids, start=1):
        print(f"=== [{i}/{len(all_ids)}] isolated run: {sid} ===", flush=True)
        result = run_isolated(sid)
        print(f"  trades={result['n_trades']}", flush=True)
        results[sid] = result

    out_path = REPO_ROOT / "phase69a_isolated_funnel.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}", flush=True)


if __name__ == "__main__":
    main()
