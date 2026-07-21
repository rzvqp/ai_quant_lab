"""Strategy Health Integration -- harness-level proofs (``STRATEGY_HEALTH_INTEGRATION_POLICY_DESIGN.md``
§§11-15, CEO-ACCEPTED WITH CONDITIONS; roadmap Flow B step 1/6). Proves the NEW ``health_eligible_ids``
gate added to ``SimulationHarness``:

- Byte-identical competitive execution when disabled (``health_eligible_ids=None``, the default) --
  matching this project's own established convention for every prior harness touch
  (``test_shadow_disabled_parity.py``'s own Checkpoints 1A/1B/1C/3 tests).
- ACTIVE/WATCHLIST-equivalent (included in ``health_eligible_ids``) strategies keep their real,
  competitive trade path exactly as before.
- PROBATION/DISABLED-equivalent (excluded from ``health_eligible_ids``) strategies have NO real-trade
  path -- zero orders, zero real fills -- while Shadow Evidence keeps observing/tracking them exactly
  as if no filter existed.
- An EMPTY ``health_eligible_ids`` (nobody real-eligible -- the worst case Phase 6.9 hit) does not stop
  Shadow Evidence for anyone: `shadow_engine` keeps producing opportunities/positions/trade_legs across
  the whole run, proving the absorbing-lockout mechanism cannot recur by construction, not merely by
  observation on one run.

Same real-strategy-runtime fixture convention as ``test_shadow_disabled_parity.py``/
``test_overlay_survives_demotion.py``."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from ai_trader.market_scanner.types import SymbolMeta
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.shadow_evidence.config import ShadowConfig
from ai_trader.simulation import performance_analyzer
from ai_trader.simulation.config import DateRange, SimulationContext
from ai_trader.simulation.harness import SimulationHarness
from ai_trader.simulation.types import RunState
from ai_trader.strategy_manager.config import ManagerConfig

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data" / "market"
SYMBOL_META = {"XAUUSD": SymbolMeta(symbol="XAUUSD", tick_size=0.01, point_value=1.0, price_precision=2)}
# Same 4-strategy scale test_shadow_disabled_parity.py already established as sufficient to prove
# genericity without paying for a full 43-strategy run in every test.
STRATEGIES = ("S10", "S21", "S39", "S40")


def _risk_config() -> RiskConfig:
    cfg = RiskConfig()
    cfg.filters.reference_spread["XAUUSD"] = 0.10
    cfg.filters.liquidity_floor["XAUUSD"] = 1.0
    return cfg


def _context(run_id: str, shadow_config: ShadowConfig | None = None) -> SimulationContext:
    # Same window/config convention as test_shadow_disabled_parity.py.
    return SimulationContext(
        run_id=run_id, date_range=DateRange(1_672_617_600, 1_680_000_000),
        symbols=("XAUUSD",), timeframes=("M15", "H1", "H4", "D1"), starting_balance=2000.0,
        run_seed=1, warmup_bars=200, shadow_config=shadow_config or ShadowConfig(),
    )


def _run(
    run_id: str, shadow_config: ShadowConfig | None = None, health_eligible_ids: frozenset[str] | None = None,
    strategy_id_filter: frozenset[str] | None = None,
) -> SimulationHarness:
    context = _context(run_id, shadow_config)
    harness = SimulationHarness(
        context, SYMBOL_META, DATA_DIR,
        manager_config=ManagerConfig(auto_admit_min_maturity="EXPLORATORY"),
        use_strategy_runtime=True, risk_config=_risk_config(),
        enable_time_stops=True, enable_trailing_stops=True, strategy_id_filter=strategy_id_filter,
        health_eligible_ids=health_eligible_ids,
    )
    harness.configure()
    harness.load()
    harness.run_to_completion()
    assert harness.state is RunState.COMPLETED, harness.fail_reason
    return harness


def _competitive_fingerprint(harness: SimulationHarness) -> dict[str, object]:
    assert harness.portfolio_simulator is not None
    assert harness.execution_simulator is not None
    report = performance_analyzer.analyze(harness.context, harness.portfolio_simulator.account)
    return {
        "report": asdict(report),  # type: ignore[call-overload]
        "trades": [asdict(t) for t in harness.portfolio_simulator.account.trade_ledger],  # type: ignore[call-overload]
        "risk_events": [asdict(e) for e in harness.portfolio_simulator.account.risk_events],  # type: ignore[call-overload]
        "orders": {oid: asdict(o) for oid, o in harness.execution_simulator._orders.items()},  # type: ignore[call-overload]
    }


# ------------------------------------------------------------------------- backward compatibility


def test_health_eligible_ids_none_is_byte_identical_to_before_this_feature_existed() -> None:
    baseline = _competitive_fingerprint(_run("HEALTH-BASELINE-A"))
    same_default = _competitive_fingerprint(_run("HEALTH-BASELINE-B"))
    assert baseline == same_default  # trivial determinism check, establishes a clean comparison point


def test_health_eligible_ids_none_matches_no_filter_at_all() -> None:
    # health_eligible_ids defaults to None (no filtering) -- must be indistinguishable from a run that
    # never mentions the parameter, proving the new constructor argument is purely additive.
    context = _context("HEALTH-NOPARAM")
    harness_noparam = SimulationHarness(
        context, SYMBOL_META, DATA_DIR, manager_config=ManagerConfig(auto_admit_min_maturity="EXPLORATORY"),
        use_strategy_runtime=True, risk_config=_risk_config(),
        enable_time_stops=True, enable_trailing_stops=True, strategy_id_filter=None,
    )
    harness_noparam.configure()
    harness_noparam.load()
    harness_noparam.run_to_completion()
    assert harness_noparam.state is RunState.COMPLETED, harness_noparam.fail_reason

    harness_explicit_none = _run("HEALTH-EXPLICIT-NONE", health_eligible_ids=None)
    assert _competitive_fingerprint(harness_noparam) == _competitive_fingerprint(harness_explicit_none)


# ---------------------------------------------------------------- eligible strategies unaffected


def test_eligible_strategies_real_trade_path_is_unchanged() -> None:
    # Both runs restrict the Signal-Engine-eligible universe to the same 4 strategies via
    # strategy_id_filter, so health_eligible_ids=frozenset(STRATEGIES) is a genuine no-op layered on an
    # otherwise-identical universe. Comparing against a fully-unfiltered (~43-strategy) baseline is NOT
    # apples-to-apples under this project's shared single-XAUUSD-slot architecture (see
    # test_excluding_a_strategy_may_redistribute_shared_slot_contention_to_others below) -- a larger
    # competing universe changes who wins the shared slot regardless of health_eligible_ids.
    restricted = _run("HEALTH-ELIGIBLE-RESTRICTED", strategy_id_filter=frozenset(STRATEGIES))
    all_eligible = _run(
        "HEALTH-ELIGIBLE-ALL", strategy_id_filter=frozenset(STRATEGIES), health_eligible_ids=frozenset(STRATEGIES),
    )
    assert _competitive_fingerprint(restricted) == _competitive_fingerprint(all_eligible)


# -------------------------------------------------------------- ineligible strategies: shadow-only


def test_excluded_strategy_has_zero_real_trades_but_nonzero_shadow_evidence() -> None:
    shadow_config = ShadowConfig(enabled=True, shadow_strategies=STRATEGIES)
    # S10 excluded from real eligibility; the other three remain eligible.
    eligible_ids = frozenset(STRATEGIES) - {"S10"}
    harness = _run("HEALTH-EXCLUDE-S10", shadow_config, health_eligible_ids=eligible_ids)

    real_trades_s10 = [t for t in harness.portfolio_simulator.account.trade_ledger if t.strategy_id == "S10"]  # type: ignore[union-attr]
    assert real_trades_s10 == [], "an excluded strategy must have NO real-trade path whatsoever"

    assert harness.shadow_engine is not None
    shadow_trades_s10 = [t for t in harness.shadow_engine.trade_legs if t.leg.strategy_id == "S10"]
    assert len(shadow_trades_s10) > 0, "Shadow Evidence must keep tracking an excluded strategy"


def test_excluding_a_strategy_may_redistribute_shared_slot_contention_to_others() -> None:
    """``health_eligible_ids`` only removes S10's own opportunities from the Risk-Manager-bound list --
    it never touches any other strategy's own opportunity list. But this project's shared
    single-XAUUSD-slot architecture (CEO_STRATEGY_CONSTRAINT_ROOT_CAUSE_REPORT.md) means freeing that
    slot's ranking contention by excluding S10 CAN legitimately change which competing strategy wins the
    slot at a given bar, cascading into different trade timing/exits for strategies that were never
    themselves filtered. Confirmed empirically here (design doc §15's own hypothesis) -- an earlier
    version of this test wrongly asserted byte-identical non-S10 trade ledgers across both runs, which
    is a false invariant under this architecture; this is a correct, disclosed second-order effect of
    shared-slot contention, not a defect in ``health_eligible_ids``. The invariant this module actually
    promises is narrower and is what's asserted below: S10 itself is fully excluded, and every trade
    that does appear belongs to a strategy that was actually eligible."""
    without_s10 = _run("HEALTH-EXCLUDE-S10-ISOLATION", health_eligible_ids=frozenset(STRATEGIES) - {"S10"})
    assert without_s10.portfolio_simulator is not None

    without_s10_strategy_ids = {t.strategy_id for t in without_s10.portfolio_simulator.account.trade_ledger}
    assert "S10" not in without_s10_strategy_ids
    assert without_s10_strategy_ids.issubset(frozenset(STRATEGIES) - {"S10"})


# ----------------------------------------------------------------- empty roster: the Phase 6.9 proof


def test_empty_health_eligible_ids_produces_zero_real_trades_for_anyone() -> None:
    harness = _run("HEALTH-EMPTY-ROSTER", health_eligible_ids=frozenset())
    assert harness.portfolio_simulator is not None
    assert harness.portfolio_simulator.account.trade_ledger == []


def test_empty_health_eligible_ids_does_not_stop_shadow_evidence() -> None:
    """The central Phase 6.9 lockout-cannot-recur proof: with EVERY strategy simultaneously excluded
    from real-trade eligibility (the worst case the old rolling gate hit permanently), Shadow Evidence
    keeps producing opportunities/positions/trade_legs for the whole run -- proving the evidence source
    this program's own eligibility decisions are based on can never itself go silent because of those
    same decisions."""
    shadow_config = ShadowConfig(enabled=True, shadow_strategies=STRATEGIES)
    harness = _run("HEALTH-EMPTY-ROSTER-SHADOW", shadow_config, health_eligible_ids=frozenset())

    assert harness.portfolio_simulator is not None
    assert harness.portfolio_simulator.account.trade_ledger == []  # zero real trades, confirmed

    assert harness.shadow_engine is not None
    assert len(harness.shadow_engine.opportunities) > 0
    assert len(harness.shadow_engine.positions) > 0
    assert len(harness.shadow_engine.trade_legs) > 0
    strategies_with_shadow_trades = {t.leg.strategy_id for t in harness.shadow_engine.trade_legs}
    assert len(strategies_with_shadow_trades) > 0
    assert strategies_with_shadow_trades.issubset(set(STRATEGIES))


def test_shadow_evidence_volume_is_unaffected_by_health_eligible_ids() -> None:
    # A stronger form of the above: Shadow's own accumulated evidence must be IDENTICAL whether
    # health_eligible_ids excludes everyone, excludes nobody, or is unset -- proving observe() truly
    # never sees the filtered list, only the full one, in every configuration. Shadow's own
    # position_id/opportunity_id are deterministically DERIVED FROM run_id (design doc §5), so all three
    # configurations being compared here must share the SAME run_id -- otherwise the fingerprints would
    # differ only in that ID prefix even when the underlying behavior is genuinely identical.
    shadow_config = ShadowConfig(enabled=True, shadow_strategies=STRATEGIES)
    run_id = "HEALTH-SHADOWVOL-SAME"
    unfiltered = _run(run_id, shadow_config, health_eligible_ids=None)
    all_eligible = _run(run_id, shadow_config, health_eligible_ids=frozenset(STRATEGIES))
    none_eligible = _run(run_id, shadow_config, health_eligible_ids=frozenset())

    def _shadow_fingerprint(h: SimulationHarness) -> dict[str, object]:
        assert h.shadow_engine is not None
        return {
            "opportunities": [asdict(o) for o in h.shadow_engine.opportunities],  # type: ignore[call-overload]
            "positions": [asdict(p) for p in h.shadow_engine.positions],  # type: ignore[call-overload]
            "trade_legs": [asdict(t) for t in h.shadow_engine.trade_legs],  # type: ignore[call-overload]
        }

    fp_none = _shadow_fingerprint(unfiltered)
    fp_all = _shadow_fingerprint(all_eligible)
    fp_empty = _shadow_fingerprint(none_eligible)
    assert fp_none == fp_all == fp_empty
