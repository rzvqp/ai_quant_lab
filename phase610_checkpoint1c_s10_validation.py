"""Phase 6.10 Implementation Checkpoint 1C -- S10 virtual-execution validation against Phase 6.9A.

SCRATCH script, preserved diagnostic artifact (same precedent as phase69_*.py/phase69a_*.py/
phase610_prescope_analysis.py/phase610_checkpoint1b_s10_validation.py). Runs the REAL competitive
harness (all 43 strategies, use_strategy_runtime=True, identical window/config to
phase69a_funnel_run.py) with ai_trader.shadow_evidence's Checkpoint 1C full virtual-execution lifecycle
enabled for S10 only, and:

1. Proves the real, competitive execution is BYTE-IDENTICAL to a plain run with Shadow disabled, over
   the FULL 13-month window (not the smaller pytest fixture window) -- the strongest available
   isolation proof, now covering virtual entry/exit/position-management, not just the read-only tap.
2. Compares S10's own shadow trade ledger (117 legs expected, matching Phase 6.9A's own isolated-run
   count) directly against the already-committed, preserved ``phase69a_isolated_funnel.json`` ground
   truth -- entry/exit price, entry_as_of/exit_as_of, direction, holding_bars, pnl_r (Design §13 test
   3). A per-field, per-trade comparison is reported; any divergence is explained via the already-
   disclosed cooldown-after-loss mid-window-start caveat (Design §7/§13's own "additional test"), never
   silently forced to match.
3. Confirms the position-identity formal invariant (Design §17.1 Q4) and the "SHADOW-" client_order_id
   discriminator (§10 invariant 4) hold over the full run.

No production code is modified by this script. No strategy, Scoring Engine, Risk Manager, or Execution
Engine logic is touched -- it only runs the existing, frozen SimulationHarness with the CEO-approved
shadow_config field set.
"""

from __future__ import annotations

import json
from dataclasses import asdict, replace
from pathlib import Path

from ai_trader.market_scanner.types import SymbolMeta
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.shadow_evidence.config import ShadowConfig
from ai_trader.simulation import performance_analyzer
from ai_trader.simulation.config import DateRange, SimulationContext
from ai_trader.simulation.harness import SimulationHarness
from ai_trader.simulation.types import RunState
from ai_trader.strategy_manager.config import ManagerConfig

REPO_ROOT = Path(__file__).resolve().parent
DATA_DIR = REPO_ROOT / "data" / "market"
SYMBOL_META = {"XAUUSD": SymbolMeta(symbol="XAUUSD", tick_size=0.01, point_value=1.0, price_precision=2)}

# Identical window/config to phase69a_funnel_run.py and the Checkpoint 1B validation, for direct
# comparability -- the SAME window phase69a_isolated_funnel.json's own S10 entry was produced from.
WINDOW_START = 1_729_674_000   # 2024-10-23 09:00:00 UTC
WINDOW_END = 1_761_210_000     # 2025-10-23 09:00:00 UTC
STARTING_BALANCE = 2000.0
RUN_SEED = 1

SHADOW_STRATEGY_ID = "S10"  # the CEO's own chosen first validation target; not hardcoded in production

# Comparable ``TradeRecord`` fields only -- excludes ``client_order_id`` (the isolated run's own id
# scheme differs by construction from the shadow run's "SHADOW-CID-" discriminator, Design §10
# invariant 4) and ``fees``/``gross_pnl`` (identical cost model, redundant with net_pnl for this check).
_COMPARABLE_FIELDS = (
    "symbol", "direction", "entry_price", "exit_price", "entry_as_of", "exit_as_of",
    "qty", "net_pnl", "pnl_r", "holding_bars",
)


def _risk_config() -> RiskConfig:
    cfg = RiskConfig()
    cfg.filters.reference_spread["XAUUSD"] = 0.10
    cfg.filters.liquidity_floor["XAUUSD"] = 1.0
    cfg.sizing = replace(cfg.sizing, risk_per_trade_pct=0.05)
    return cfg


def _context(run_id: str, shadow_config: ShadowConfig | None = None) -> SimulationContext:
    return SimulationContext(
        run_id=run_id, date_range=DateRange(WINDOW_START, WINDOW_END), symbols=("XAUUSD",),
        timeframes=("M15", "H1", "H4", "D1"), starting_balance=STARTING_BALANCE, run_seed=RUN_SEED,
        warmup_bars=200, shadow_config=shadow_config or ShadowConfig(),
    )


def _run(run_id: str, shadow_config: ShadowConfig | None = None) -> SimulationHarness:
    context = _context(run_id, shadow_config)
    harness = SimulationHarness(
        context, SYMBOL_META, DATA_DIR,
        manager_config=ManagerConfig(auto_admit_min_maturity="EXPLORATORY"),
        use_strategy_runtime=True, risk_config=_risk_config(),
        enable_time_stops=True, enable_trailing_stops=True, strategy_id_filter=None,
    )
    harness.configure()
    harness.load()
    harness.run_to_completion()
    assert harness.state is RunState.COMPLETED, harness.fail_reason
    return harness


def _full_report_dict(harness: SimulationHarness) -> dict[str, object]:
    assert harness.portfolio_simulator is not None
    report = performance_analyzer.analyze(harness.context, harness.portfolio_simulator.account)
    return {
        "portfolio_summary": asdict(report.portfolio_summary), "performance": asdict(report.performance),
        "attribution": [asdict(a) for a in report.attribution], "stats": asdict(report.stats),
        "allocation": asdict(report.allocation) if report.allocation is not None else None,
        "risk_events": [asdict(e) for e in report.risk_events],
    }


def _comparable(trade: dict[str, object]) -> dict[str, object]:
    return {k: trade[k] for k in _COMPARABLE_FIELDS}


def main() -> None:
    print("=== Run 1/2: plain (Shadow disabled) ===", flush=True)
    plain = _run("CKPT1C-PLAIN")
    plain_report = _full_report_dict(plain)
    assert plain.portfolio_simulator is not None
    plain_trades = [asdict(t) for t in plain.portfolio_simulator.account.trade_ledger]
    print(f"Plain run: {len(plain_trades)} trades", flush=True)

    print("=== Run 2/2: Shadow enabled for S10 (full virtual execution) ===", flush=True)
    shadow_harness = _run("CKPT1C-SHADOW-S10", ShadowConfig(enabled=True, shadow_strategies=(SHADOW_STRATEGY_ID,)))
    shadow_report = _full_report_dict(shadow_harness)
    assert shadow_harness.portfolio_simulator is not None
    shadow_trades = [asdict(t) for t in shadow_harness.portfolio_simulator.account.trade_ledger]
    print(f"Shadow-enabled run: {len(shadow_trades)} trades", flush=True)

    isolation_proof = {
        "full_report_identical": plain_report == shadow_report,
        "trade_ledger_identical": plain_trades == shadow_trades,
        "plain_trade_count": len(plain_trades),
        "shadow_run_trade_count": len(shadow_trades),
    }
    print(f"Isolation proof: {json.dumps(isolation_proof, indent=2)}", flush=True)
    if not isolation_proof["full_report_identical"] or not isolation_proof["trade_ledger_identical"]:
        print("!!! PARITY FAILURE -- STOPPING, NOT EXPLAINING AWAY !!!", flush=True)
        raise SystemExit(1)

    assert shadow_harness.shadow_engine is not None
    engine = shadow_harness.shadow_engine

    # -------- position-identity invariant (Design §17.1 Q4), checked exhaustively --------
    resulting_ids = [o.resulting_position_id for o in engine.opportunities if o.shadow_risk_decision == "ALLOW"]
    non_none = [rid for rid in resulting_ids if rid is not None]
    identity_ok = len(non_none) == len(set(non_none))
    position_ids = {p.position_id for p in engine.positions}
    positions_unique = len(position_ids) == len(engine.positions)
    legs_by_position: dict[str, list[dict[str, object]]] = {}
    for leg in engine.trade_legs:
        legs_by_position.setdefault(leg.position_id, []).append(asdict(leg.leg))
    aggregation_ok = True
    for position in engine.positions:
        legs = legs_by_position.get(position.position_id, [])
        if len(legs) != position.n_legs:
            aggregation_ok = False
        if position.status == "CLOSED":
            if position.aggregate_net_pnl != sum(l["net_pnl"] for l in legs):
                aggregation_ok = False
            if legs and position.full_exit_as_of != legs[-1]["exit_as_of"]:
                aggregation_ok = False

    # -------- "SHADOW-" discriminator prefix (Design §10 invariant 4) --------
    all_shadow_ids_prefixed = all(
        leg.leg.client_order_id.startswith("SHADOW-CID-") for leg in engine.trade_legs
    )
    real_ids = {t.client_order_id for t in shadow_harness.portfolio_simulator.account.trade_ledger}
    shadow_ids_set = {leg.leg.client_order_id for leg in engine.trade_legs}
    no_id_collision = real_ids.isdisjoint(shadow_ids_set)

    # -------- Design §13 test 3: direct comparison against phase69a_isolated_funnel.json --------
    isolated_path = REPO_ROOT / "phase69a_isolated_funnel.json"
    isolated_data = json.loads(isolated_path.read_text(encoding="utf-8"))
    isolated_s10_trades = [_comparable(t) for t in isolated_data["S10"]["trades"]]
    shadow_s10_trades = [_comparable(asdict(leg.leg)) for leg in engine.trade_legs]

    exact_trade_ledger_match = shadow_s10_trades == isolated_s10_trades
    n_matching_prefix = 0
    for a, b in zip(shadow_s10_trades, isolated_s10_trades):
        if a == b:
            n_matching_prefix += 1
        else:
            break

    comparison = {
        "isolated_n_trades": len(isolated_s10_trades),
        "shadow_n_trades": len(shadow_s10_trades),
        "exact_trade_ledger_match": exact_trade_ledger_match,
        "n_matching_from_start": n_matching_prefix,
        "first_divergence_index": n_matching_prefix if not exact_trade_ledger_match else None,
        "first_divergent_shadow_trade": (
            shadow_s10_trades[n_matching_prefix] if n_matching_prefix < len(shadow_s10_trades) else None
        ),
        "first_divergent_isolated_trade": (
            isolated_s10_trades[n_matching_prefix] if n_matching_prefix < len(isolated_s10_trades) else None
        ),
        "note": (
            "A divergence starting mid-run (not at trade 0) is consistent with the already-disclosed "
            "cooldown-after-loss mid-window-start caveat (Design §7/§13) -- NOT assumed away here, "
            "reported for CEO inspection."
        ),
    }
    print(f"S10 isolated-ledger comparison: {json.dumps(comparison, indent=2, default=str)}", flush=True)

    out = {
        "config": {"window_start": WINDOW_START, "window_end": WINDOW_END, "shadow_strategy": SHADOW_STRATEGY_ID},
        "isolation_proof": isolation_proof,
        "position_identity_invariant": {
            "resulting_position_ids_unique": identity_ok,
            "shadow_position_ids_unique": positions_unique,
            "leg_aggregation_correct": aggregation_ok,
            "n_positions": len(engine.positions),
            "n_trade_legs": len(engine.trade_legs),
            "n_opportunities": len(engine.opportunities),
            "n_failures": len(engine.failures),
        },
        "shadow_id_discriminator": {
            "all_shadow_client_order_ids_prefixed": all_shadow_ids_prefixed,
            "no_collision_with_real_client_order_ids": no_id_collision,
        },
        "comparison_against_phase69a_isolated": comparison,
    }
    out_path = REPO_ROOT / "phase610_checkpoint1c_s10_validation.json"
    out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {out_path}", flush=True)


if __name__ == "__main__":
    main()
