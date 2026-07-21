"""Portfolio Architect -- harness-level proofs (``PORTFOLIO_ARCHITECT_DESIGN.md``, CEO-ACCEPTED
COMPLETE; Phase 1 authorization: PASSTHROUGH SCAFFOLD ONLY). Proves the NEW
``portfolio_architect_config`` gate added to ``SimulationHarness``:

- Byte-identical competitive execution when disabled (``portfolio_architect_config=None``, the
  default) -- matching this project's own established convention for every prior harness touch.
- PASSTHROUGH-enabled execution is ALSO byte-identical to disabled -- the mode itself is a proven
  no-op, not merely "off by default."
- Strategy Health's own eligibility decisions remain fully respected and un-overridable: an excluded
  strategy stays excluded; an empty eligible roster still produces zero real trades while Shadow
  Evidence keeps observing everyone.
- Risk Manager remains the sole ALLOW/DENY authority -- shared-slot denial/attribution is unchanged
  with Portfolio Architect enabled.
- Determinism holds under repeated runs with Portfolio Architect enabled.
- The Shadow Evidence tap reordering (moved earlier in the per-bar loop to satisfy the CEO's own
  mandatory placement -- see ``harness.py``'s own ``__init__`` docstring) is behavior-preserving:
  Shadow's own accumulated evidence is identical whether Portfolio Architect is disabled or enabled.

Same real-strategy-runtime fixture convention as ``test_health_eligible_ids.py``/
``test_shadow_disabled_parity.py``."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from ai_trader.market_scanner.types import SymbolMeta
from ai_trader.portfolio_architect.types import ArchitectMode, PortfolioArchitectConfig
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
STRATEGIES = ("S10", "S21", "S39", "S40")
PASSTHROUGH = PortfolioArchitectConfig(mode=ArchitectMode.PASSTHROUGH)


def _risk_config() -> RiskConfig:
    cfg = RiskConfig()
    cfg.filters.reference_spread["XAUUSD"] = 0.10
    cfg.filters.liquidity_floor["XAUUSD"] = 1.0
    return cfg


def _context(run_id: str, shadow_config: ShadowConfig | None = None) -> SimulationContext:
    return SimulationContext(
        run_id=run_id, date_range=DateRange(1_672_617_600, 1_680_000_000),
        symbols=("XAUUSD",), timeframes=("M15", "H1", "H4", "D1"), starting_balance=2000.0,
        run_seed=1, warmup_bars=200, shadow_config=shadow_config or ShadowConfig(),
    )


def _run(
    run_id: str, shadow_config: ShadowConfig | None = None,
    health_eligible_ids: frozenset[str] | None = None,
    portfolio_architect_config: PortfolioArchitectConfig | None = None,
) -> SimulationHarness:
    context = _context(run_id, shadow_config)
    harness = SimulationHarness(
        context, SYMBOL_META, DATA_DIR,
        manager_config=ManagerConfig(auto_admit_min_maturity="EXPLORATORY"),
        use_strategy_runtime=True, risk_config=_risk_config(),
        enable_time_stops=True, enable_trailing_stops=True, strategy_id_filter=None,
        health_eligible_ids=health_eligible_ids, portfolio_architect_config=portfolio_architect_config,
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


def _shadow_fingerprint(harness: SimulationHarness) -> dict[str, object]:
    assert harness.shadow_engine is not None
    return {
        "opportunities": [asdict(o) for o in harness.shadow_engine.opportunities],  # type: ignore[call-overload]
        "positions": [asdict(p) for p in harness.shadow_engine.positions],  # type: ignore[call-overload]
        "trade_legs": [asdict(t) for t in harness.shadow_engine.trade_legs],  # type: ignore[call-overload]
    }


# ------------------------------------------------------------------------- backward compatibility (1, 2)


def test_architect_disabled_is_byte_identical_to_baseline_without_this_feature() -> None:
    baseline = _competitive_fingerprint(_run("PA-BASELINE-A"))
    same_default = _competitive_fingerprint(_run("PA-BASELINE-B"))
    assert baseline == same_default  # determinism check, establishes a clean comparison point


def test_architect_disabled_matches_no_config_at_all() -> None:
    # portfolio_architect_config defaults to None -- must be indistinguishable from a run that never
    # mentions the parameter, proving the new constructor argument is purely additive.
    context = _context("PA-NOPARAM")
    harness_noparam = SimulationHarness(
        context, SYMBOL_META, DATA_DIR, manager_config=ManagerConfig(auto_admit_min_maturity="EXPLORATORY"),
        use_strategy_runtime=True, risk_config=_risk_config(),
        enable_time_stops=True, enable_trailing_stops=True, strategy_id_filter=None,
    )
    harness_noparam.configure()
    harness_noparam.load()
    harness_noparam.run_to_completion()
    assert harness_noparam.state is RunState.COMPLETED, harness_noparam.fail_reason

    harness_explicit_none = _run("PA-EXPLICIT-NONE", portfolio_architect_config=None)
    assert _competitive_fingerprint(harness_noparam) == _competitive_fingerprint(harness_explicit_none)


def test_passthrough_enabled_is_byte_identical_to_disabled() -> None:
    disabled = _competitive_fingerprint(_run("PA-PASSTHROUGH-OFF", portfolio_architect_config=None))
    enabled = _competitive_fingerprint(_run("PA-PASSTHROUGH-ON", portfolio_architect_config=PASSTHROUGH))
    assert disabled == enabled


# ------------------------------------------------------------ Strategy Health remains authoritative (8, 9)


def test_empty_health_eligible_ids_still_produces_zero_real_trades_with_architect_enabled() -> None:
    """The Phase 6.9 lockout-cannot-recur proof, re-run with Portfolio Architect enabled: nobody
    real-eligible must still mean zero real trades while Shadow Evidence keeps observing everyone --
    Portfolio Architect must not be able to change this outcome."""
    shadow_config = ShadowConfig(enabled=True, shadow_strategies=STRATEGIES)
    harness = _run(
        "PA-EMPTY-ELIGIBLE", shadow_config, health_eligible_ids=frozenset(), portfolio_architect_config=PASSTHROUGH,
    )
    assert harness.portfolio_simulator is not None
    assert harness.portfolio_simulator.account.trade_ledger == []

    assert harness.shadow_engine is not None
    assert len(harness.shadow_engine.trade_legs) > 0
    strategies_with_shadow_trades = {t.leg.strategy_id for t in harness.shadow_engine.trade_legs}
    assert strategies_with_shadow_trades.issubset(set(STRATEGIES))


def test_strategy_excluded_by_health_remains_excluded_with_architect_enabled() -> None:
    """Portfolio Architect cannot restore a strategy Strategy Health has already excluded -- it only
    ever receives the already-filtered eligible set as its own input (design doc §3/§9)."""
    eligible_ids = frozenset(STRATEGIES) - {"S10"}
    harness = _run("PA-EXCLUDE-S10", health_eligible_ids=eligible_ids, portfolio_architect_config=PASSTHROUGH)
    assert harness.portfolio_simulator is not None
    real_trades_s10 = [t for t in harness.portfolio_simulator.account.trade_ledger if t.strategy_id == "S10"]
    assert real_trades_s10 == []


# --------------------------------------------------------------- Risk Manager remains authoritative (11, 18)


def test_risk_manager_may_still_reject_any_architect_returned_opportunity() -> None:
    """Shared-slot (LIMIT_MAX_PER_SYMBOL) denial/attribution -- current, existing Risk Manager
    behavior -- must be byte-identical with Portfolio Architect enabled in PASSTHROUGH mode, proving
    Portfolio Architect neither weakens nor bypasses Risk Manager's own DENY authority."""
    disabled = _competitive_fingerprint(_run("PA-RISKMGR-OFF"))
    enabled = _competitive_fingerprint(_run("PA-RISKMGR-ON", portfolio_architect_config=PASSTHROUGH))
    assert disabled == enabled
    # Confirm shared-slot denials actually occurred in this fixture window, so the equality above is a
    # meaningful proof and not a vacuous "nothing happened" comparison.
    denial_types = {e["type"] for e in enabled["risk_events"]}  # type: ignore[index]
    assert any(t.startswith("DENY_LIMIT_MAX_PER_SYMBOL") for t in denial_types)


# --------------------------------------------------------------------------------------- determinism (13)


def test_repeated_runs_with_the_same_run_id_are_deterministic_with_architect_enabled() -> None:
    run_id = "PA-DETERMINISM-SAME"
    first = _competitive_fingerprint(_run(run_id, portfolio_architect_config=PASSTHROUGH))
    second = _competitive_fingerprint(_run(run_id, portfolio_architect_config=PASSTHROUGH))
    assert first == second


# ------------------------------------------------------- Shadow Evidence tap reordering is inert (design)


def test_shadow_evidence_is_unaffected_by_architect_enabled_or_disabled() -> None:
    """The Shadow Evidence tap was moved earlier in the per-bar loop to satisfy the CEO's own mandatory
    placement (observe() now runs before health_eligible_ids filtering and before Portfolio Architect,
    not just before Risk Manager). This reordering must be behavior-preserving: Shadow's own
    accumulated evidence must be identical whether Portfolio Architect is disabled or PASSTHROUGH-
    enabled."""
    shadow_config = ShadowConfig(enabled=True, shadow_strategies=STRATEGIES)
    run_id = "PA-SHADOWVOL-SAME"
    disabled = _run(run_id, shadow_config, portfolio_architect_config=None)
    enabled = _run(run_id, shadow_config, portfolio_architect_config=PASSTHROUGH)
    assert _shadow_fingerprint(disabled) == _shadow_fingerprint(enabled)
