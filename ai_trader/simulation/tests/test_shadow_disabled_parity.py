"""Shadow Mode isolation proofs -- Phase 6.10 Implementation Checkpoints 1A + 1B + 1C
(``PHASE_6_10_SHADOW_EVIDENCE_ARCHITECTURE_DESIGN.md``). Proves:

- Checkpoint 1A (disabled-by-default): with no ``shadow_strategies`` configured, nothing changes --
  ``harness.shadow_engine`` stays ``None``, exactly one instance each of ``RiskManager``/
  ``ExecutionEngine``/``ExecutionSimulator``/``PortfolioSimulator`` is constructed, and two independent
  runs of the identical (disabled) config are byte-identical.
- Checkpoint 1B (the read-only tap, enabled for one or more strategies): the REAL, competitive
  execution -- the full ``SimulationReportData`` (every field, not a subset -- Phase 6.9A's own
  adversarial-review-caught standard), trade ledger, risk events, and orders -- is BYTE-IDENTICAL
  whether Shadow Mode is enabled or disabled, for any configured strategy set (proving the mechanism is
  generic, not hardcoded to one strategy). Also proves shadow evidence records only ever carry a
  configured strategy's own id, and that a forced shadow-strategy failure degrades only that one
  strategy without affecting competitive execution or crashing the run.
- Checkpoint 1C (the full virtual position lifecycle): the SAME byte-identical competitive-execution
  guarantee still holds once shadow accounts actually open/manage/close virtual positions; the shadow
  ledger itself is non-trivial, deterministic across repeated runs, carries the required "SHADOW-"
  client_order_id discriminator, satisfies the formal position-identity invariant (Design §17.1 Q4)
  exhaustively over a full run, scales correctly across multiple simultaneously-tracked edges, never
  mutates the shared ``RiskConfig`` object, and isolates a forced failure in the NEW settlement path
  exactly as Checkpoint 1B already proved for the read-only tap.
- Checkpoint 3 (the first production strategy set): every one of the SAME guarantees above, now proven
  at the real production scale -- ``all_registered_strategies()``'s own full 43-strategy set, running
  concurrently, over the same 85-day fixture window every other test in this file already uses (a
  deliberately BOUNDED validation scale -- the full 13-month/23,639-bar runtime/memory benchmark Design
  §13 test 8 requires before any wider rollout decision remains separate, not-yet-authorized work; this
  checkpoint proves CORRECTNESS at N=43, not throughput at full historical scale).

Same real-strategy-runtime fixture convention as ``test_risk_event_strategy_attribution.py``
(Phase 6.9A).
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from ai_trader.execution_engine.engine import ExecutionEngine
from ai_trader.market_scanner.types import SymbolMeta
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.engine import RiskManager
from ai_trader.shadow_evidence.config import ShadowConfig, all_registered_strategies
from ai_trader.shadow_evidence.engine import ShadowEvidenceEngine
from ai_trader.simulation import performance_analyzer
from ai_trader.simulation.config import DateRange, SimulationContext
from ai_trader.simulation.execution_simulator import ExecutionSimulator
from ai_trader.simulation.harness import SimulationHarness
from ai_trader.simulation.portfolio_simulator import PortfolioSimulator
from ai_trader.simulation.types import RunState
from ai_trader.strategy_manager.config import ManagerConfig

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data" / "market"
SYMBOL_META = {"XAUUSD": SymbolMeta(symbol="XAUUSD", tick_size=0.01, point_value=1.0, price_precision=2)}


def _risk_config() -> RiskConfig:
    cfg = RiskConfig()
    cfg.filters.reference_spread["XAUUSD"] = 0.10
    cfg.filters.liquidity_floor["XAUUSD"] = 1.0
    return cfg


def _context(run_id: str, shadow_config: ShadowConfig | None = None) -> SimulationContext:
    # Same window/config convention as test_risk_event_strategy_attribution.py (Phase 6.9A).
    return SimulationContext(
        run_id=run_id, date_range=DateRange(1_672_617_600, 1_680_000_000),
        symbols=("XAUUSD",), timeframes=("M15", "H1", "H4", "D1"), starting_balance=2000.0,
        run_seed=1, warmup_bars=200, shadow_config=shadow_config or ShadowConfig(),
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
    return asdict(report)  # type: ignore[call-overload]


def _competitive_fingerprint(harness: SimulationHarness) -> dict[str, object]:
    """Every real, competitive-execution surface the CEO asked to be proven identical: the full
    report, the trade ledger, risk events, and the order book."""
    assert harness.portfolio_simulator is not None
    assert harness.execution_simulator is not None
    return {
        "report": _full_report_dict(harness),
        "trades": [asdict(t) for t in harness.portfolio_simulator.account.trade_ledger],  # type: ignore[call-overload]
        "risk_events": [asdict(e) for e in harness.portfolio_simulator.account.risk_events],  # type: ignore[call-overload]
        "orders": {oid: asdict(o) for oid, o in harness.execution_simulator._orders.items()},  # type: ignore[call-overload]
    }


# ------------------------------------------------------------------------------- Checkpoint 1A: disabled

def test_shadow_config_defaults_to_disabled_and_needs_no_caller_change() -> None:
    context = _context("SHADOW-DEFAULT")
    assert context.shadow_config.enabled is False
    assert context.shadow_config.active_strategy_ids() == frozenset()


def test_disabled_shadow_engine_is_none_and_produces_no_shadow_evidence() -> None:
    harness = _run("SHADOW-NOOP")
    assert harness.shadow_engine is None


def test_disabled_shadow_creates_exactly_one_instance_of_each_core_engine(monkeypatch) -> None:
    counts = {"RiskManager": 0, "ExecutionEngine": 0, "ExecutionSimulator": 0, "PortfolioSimulator": 0}

    def _counted(name: str, original):
        def wrapper(self, *args, **kwargs):
            counts[name] += 1
            return original(self, *args, **kwargs)
        return wrapper

    monkeypatch.setattr(RiskManager, "__init__", _counted("RiskManager", RiskManager.__init__))
    monkeypatch.setattr(ExecutionEngine, "__init__", _counted("ExecutionEngine", ExecutionEngine.__init__))
    monkeypatch.setattr(
        ExecutionSimulator, "__init__", _counted("ExecutionSimulator", ExecutionSimulator.__init__),
    )
    monkeypatch.setattr(
        PortfolioSimulator, "__init__", _counted("PortfolioSimulator", PortfolioSimulator.__init__),
    )

    _run("SHADOW-INSTANCE-COUNT")

    assert counts == {
        "RiskManager": 1, "ExecutionEngine": 1, "ExecutionSimulator": 1, "PortfolioSimulator": 1,
    }


def test_disabled_shadow_run_is_deterministic_across_repeated_runs() -> None:
    fingerprint_a = _competitive_fingerprint(_run("SHADOW-DET-A"))
    fingerprint_b = _competitive_fingerprint(_run("SHADOW-DET-B"))
    assert fingerprint_a == fingerprint_b


# ---------------------------------------------------------------------- Checkpoint 1B: the read-only tap

def test_shadow_enabled_for_one_strategy_produces_byte_identical_competitive_execution() -> None:
    disabled = _competitive_fingerprint(_run("SHADOW-1B-OFF"))
    enabled = _competitive_fingerprint(
        _run("SHADOW-1B-ON-S10", ShadowConfig(enabled=True, shadow_strategies=("S10",))),
    )
    assert disabled == enabled


def test_shadow_enabled_for_multiple_strategies_still_produces_byte_identical_competitive_execution() -> None:
    # Proves the mechanism generalizes -- nothing in the engine is hardcoded to a single strategy id.
    disabled = _competitive_fingerprint(_run("SHADOW-1B-OFF-2"))
    enabled = _competitive_fingerprint(
        _run(
            "SHADOW-1B-ON-MULTI",
            ShadowConfig(enabled=True, shadow_strategies=("S10", "S21", "S39", "S40")),
        ),
    )
    assert disabled == enabled


def test_shadow_engine_only_records_configured_strategies() -> None:
    harness = _run("SHADOW-1B-SCOPE", ShadowConfig(enabled=True, shadow_strategies=("S10",)))
    assert harness.shadow_engine is not None
    for opp in harness.shadow_engine.opportunities:
        assert opp.strategy_id == "S10"
    for rej in harness.shadow_engine.rejections:
        assert rej.strategy_id == "S10"


def test_shadow_engine_disabled_by_master_switch_even_with_strategies_configured() -> None:
    # enabled=False must win over a non-empty shadow_strategies list -- the master switch, not the
    # list emptiness, is authoritative (ShadowConfig.active_strategy_ids()'s own contract).
    context = _context("SHADOW-MASTER-OFF", ShadowConfig(enabled=False, shadow_strategies=("S10",)))
    assert context.shadow_config.active_strategy_ids() == frozenset()
    harness = _run("SHADOW-MASTER-OFF", ShadowConfig(enabled=False, shadow_strategies=("S10",)))
    assert harness.shadow_engine is None


def test_shadow_strategy_failure_is_isolated_and_does_not_affect_competitive_execution(monkeypatch) -> None:
    disabled = _competitive_fingerprint(_run("SHADOW-1B-FAIL-BASELINE"))

    def _always_raise(self, as_of, score, risk_context):
        raise RuntimeError("forced failure for isolation test")

    monkeypatch.setattr(ShadowEvidenceEngine, "_observe_one", _always_raise)
    harness = _run("SHADOW-1B-FAIL", ShadowConfig(enabled=True, shadow_strategies=("S10",)))

    assert harness.state is RunState.COMPLETED, harness.fail_reason
    assert harness.shadow_engine is not None
    assert len(harness.shadow_engine.failures) > 0
    assert all(sid == "S10" for _as_of, sid, _err in harness.shadow_engine.failures)
    assert harness.shadow_engine.opportunities == []
    assert harness.shadow_engine.rejections == []
    assert _competitive_fingerprint(harness) == disabled


def test_shadow_engine_failure_outside_the_per_strategy_boundary_still_does_not_affect_competitive_execution(
    monkeypatch,
) -> None:
    # Found during this checkpoint's own adversarial review: observe()'s per-strategy try/except does
    # not cover a bug OUTSIDE that per-strategy loop. This test forces observe() ITSELF to raise (not
    # _observe_one) to prove the harness.py-level defense-in-depth try/except (added as a direct result
    # of that finding) makes "competitive execution continues" a hard guarantee, not contingent on
    # observe()'s own internal code being bug-free.
    disabled = _competitive_fingerprint(_run("SHADOW-1B-OUTER-FAIL-BASELINE"))

    def _always_raise(self, as_of, score_batch, risk_context):
        raise RuntimeError("forced failure outside the per-strategy boundary")

    monkeypatch.setattr(ShadowEvidenceEngine, "observe", _always_raise)
    harness = _run("SHADOW-1B-OUTER-FAIL", ShadowConfig(enabled=True, shadow_strategies=("S10",)))

    assert harness.state is RunState.COMPLETED, harness.fail_reason
    assert harness.shadow_engine is not None
    assert len(harness.shadow_engine.failures) > 0
    assert all(sid == "__engine__" for _as_of, sid, _err in harness.shadow_engine.failures)
    assert _competitive_fingerprint(harness) == disabled


# ------------------------------------------------------------ Checkpoint 1C: full virtual execution lifecycle

def _shadow_ledger_fingerprint(harness: SimulationHarness) -> dict[str, object]:
    """Every shadow-side artifact, for determinism/content comparisons -- never mixed with
    ``_competitive_fingerprint``'s own real-portfolio surfaces."""
    assert harness.shadow_engine is not None
    engine = harness.shadow_engine
    return {
        "opportunities": [asdict(o) for o in engine.opportunities],  # type: ignore[call-overload]
        "positions": [asdict(p) for p in engine.positions],  # type: ignore[call-overload]
        "trade_legs": [asdict(t) for t in engine.trade_legs],  # type: ignore[call-overload]
        "rejections": [asdict(r) for r in engine.rejections],  # type: ignore[call-overload]
    }


def test_shadow_enabled_with_full_execution_still_produces_byte_identical_competitive_execution_one_strategy() -> None:
    disabled = _competitive_fingerprint(_run("SHADOW-1C-OFF"))
    enabled = _competitive_fingerprint(
        _run("SHADOW-1C-ON-S10", ShadowConfig(enabled=True, shadow_strategies=("S10",))),
    )
    assert disabled == enabled


def test_shadow_enabled_with_full_execution_still_produces_byte_identical_competitive_execution_multi_strategy() -> None:
    disabled = _competitive_fingerprint(_run("SHADOW-1C-OFF-2"))
    enabled = _competitive_fingerprint(
        _run(
            "SHADOW-1C-ON-MULTI",
            ShadowConfig(enabled=True, shadow_strategies=("S10", "S21", "S39", "S40")),
        ),
    )
    assert disabled == enabled


def test_shadow_engine_produces_a_non_trivial_virtual_ledger_for_s10() -> None:
    # Checkpoint 1C's own central claim: bypassing the shared slot lets a slot-starved strategy
    # actually accumulate virtual positions/trades, not just risk-eligibility opportunities (1B).
    harness = _run("SHADOW-1C-NONTRIVIAL", ShadowConfig(enabled=True, shadow_strategies=("S10",)))
    assert harness.shadow_engine is not None
    assert len(harness.shadow_engine.opportunities) > 0
    assert len(harness.shadow_engine.positions) > 0
    assert len(harness.shadow_engine.trade_legs) > 0
    assert all(p.strategy_id == "S10" for p in harness.shadow_engine.positions)
    assert all(t.leg.strategy_id == "S10" for t in harness.shadow_engine.trade_legs)


def test_shadow_client_order_ids_all_carry_the_shadow_discriminator_prefix() -> None:
    # Design §10 invariant 4 / §17.1 finding H3's required defense-in-depth -- verified end to end
    # through a full harness run, not just the unit-level construction check.
    harness = _run("SHADOW-1C-PREFIX", ShadowConfig(enabled=True, shadow_strategies=("S10",)))
    assert harness.shadow_engine is not None
    assert len(harness.shadow_engine.trade_legs) > 0
    for trade in harness.shadow_engine.trade_legs:
        assert trade.leg.client_order_id.startswith("SHADOW-CID-")
    # ...and never collides with any real, competitive client_order_id.
    real_ids = {t.client_order_id for t in harness.portfolio_simulator.account.trade_ledger}
    shadow_ids = {t.leg.client_order_id for t in harness.shadow_engine.trade_legs}
    assert real_ids.isdisjoint(shadow_ids)


def test_shadow_position_identity_invariant_holds_across_a_full_run() -> None:
    # Design §17.1 Q4's own formal invariant, checked exhaustively over every position a full run
    # produces: one ShadowOpportunityRecord maps to zero-or-one ShadowPositionRecord; n_legs/
    # aggregate_net_pnl/full_exit_as_of are always derived from the position's own legs.
    harness = _run("SHADOW-1C-IDENTITY", ShadowConfig(enabled=True, shadow_strategies=("S10",)))
    assert harness.shadow_engine is not None
    engine = harness.shadow_engine
    resulting_ids = [o.resulting_position_id for o in engine.opportunities if o.shadow_risk_decision == "ALLOW"]
    assert len(resulting_ids) == len({rid for rid in resulting_ids if rid is not None}) + resulting_ids.count(None)
    position_ids = {p.position_id for p in engine.positions}
    assert len(position_ids) == len(engine.positions)  # no position_id ever duplicated across records
    for position in engine.positions:
        legs = [t for t in engine.trade_legs if t.position_id == position.position_id]
        assert len(legs) == position.n_legs
        if position.status == "CLOSED":
            assert position.aggregate_net_pnl == sum(leg.leg.net_pnl for leg in legs)
            assert position.full_exit_as_of == legs[-1].leg.exit_as_of


def test_multi_edge_shadow_evidence_scales_with_more_configured_strategies() -> None:
    # Not a claim about correlation/independence (Design §12) -- only that adding more shadow-tracked
    # edges yields strictly more (never less, never merged/contaminated) accumulated evidence, and that
    # every additional strategy's own positions stay correctly attributed to itself alone.
    solo = _run("SHADOW-1C-SCALE-SOLO", ShadowConfig(enabled=True, shadow_strategies=("S10",)))
    multi = _run(
        "SHADOW-1C-SCALE-MULTI", ShadowConfig(enabled=True, shadow_strategies=("S10", "S21", "S39", "S40")),
    )
    assert solo.shadow_engine is not None and multi.shadow_engine is not None
    assert len(multi.shadow_engine.positions) >= len(solo.shadow_engine.positions)
    by_strategy: dict[str, int] = {}
    for position in multi.shadow_engine.positions:
        by_strategy[position.strategy_id] = by_strategy.get(position.strategy_id, 0) + 1
    assert set(by_strategy).issubset({"S10", "S21", "S39", "S40"})
    for trade in multi.shadow_engine.trade_legs:
        assert trade.leg.strategy_id in {"S10", "S21", "S39", "S40"}


def test_shadow_enabled_run_with_full_execution_is_deterministic_across_repeated_runs() -> None:
    # The SAME run_id both times: position_id is deterministically derived FROM run_id (Design §5), so
    # two runs of the identical (run_id, config) pair -- not merely the same config under different
    # run_ids -- is the actual determinism claim being tested here.
    config = ShadowConfig(enabled=True, shadow_strategies=("S10", "S21"))
    ledger_a = _shadow_ledger_fingerprint(_run("SHADOW-1C-DET", config))
    ledger_b = _shadow_ledger_fingerprint(_run("SHADOW-1C-DET", config))
    assert ledger_a == ledger_b


def test_shared_risk_config_is_byte_identical_before_and_after_a_shadow_enabled_run() -> None:
    # Design §10 invariant 3 / §17.1 finding M1's own required test: RiskConfig is shared BY REFERENCE
    # across the real RiskManager and every shadow RiskManager -- confirm no code path anywhere ever
    # mutates it in place, end to end through a full run with real virtual execution.
    risk_config = _risk_config()
    before = asdict(risk_config)  # type: ignore[call-overload]
    context = _context("SHADOW-1C-RISKCONFIG-UNCHANGED", ShadowConfig(enabled=True, shadow_strategies=("S10",)))
    harness = SimulationHarness(
        context, SYMBOL_META, DATA_DIR,
        manager_config=ManagerConfig(auto_admit_min_maturity="EXPLORATORY"),
        use_strategy_runtime=True, risk_config=risk_config,
        enable_time_stops=True, enable_trailing_stops=True, strategy_id_filter=None,
    )
    harness.configure()
    harness.load()
    harness.run_to_completion()
    assert harness.state is RunState.COMPLETED, harness.fail_reason
    after = asdict(risk_config)  # type: ignore[call-overload]
    assert before == after


def test_shadow_settlement_failure_is_isolated_and_does_not_affect_competitive_execution(monkeypatch) -> None:
    # Mirrors test_shadow_strategy_failure_is_isolated_and_does_not_affect_competitive_execution, but
    # forces the NEW Checkpoint 1C settlement path (_settle_one) to fail instead of the Checkpoint 1B
    # risk-tap path (_observe_one) -- proving failure isolation covers the full virtual execution
    # lifecycle, not just the original read-only tap.
    disabled = _competitive_fingerprint(_run("SHADOW-1C-SETTLE-FAIL-BASELINE"))

    def _always_raise(self, strategy_id, as_of, bar_index, bars, phase_running):
        raise RuntimeError("forced settlement failure for isolation test")

    monkeypatch.setattr(ShadowEvidenceEngine, "_settle_one", _always_raise)
    harness = _run("SHADOW-1C-SETTLE-FAIL", ShadowConfig(enabled=True, shadow_strategies=("S10",)))

    assert harness.state is RunState.COMPLETED, harness.fail_reason
    assert harness.shadow_engine is not None
    assert len(harness.shadow_engine.failures) > 0
    assert all(sid == "S10" for _as_of, sid, _err in harness.shadow_engine.failures)
    assert harness.shadow_engine.trade_legs == []
    assert _competitive_fingerprint(harness) == disabled


def test_shadow_outer_boundary_failure_isolation_covers_every_new_checkpoint_1c_call_site(monkeypatch) -> None:
    # Mirrors test_shadow_engine_failure_outside_the_per_strategy_boundary_still_does_not_affect_
    # competitive_execution (Checkpoint 1B's own precedent for observe()) -- forces EVERY new
    # Checkpoint 1C harness-level call site's own PUBLIC method (not its internal _xxx_one helper) to
    # raise, proving harness.py's own defense-in-depth try/except around each one (found necessary by
    # the SAME reasoning the original adversarial review already established for observe()) is real,
    # not merely assumed symmetric with the tested call site.
    disabled = _competitive_fingerprint(_run("SHADOW-1C-OUTER-FAIL-ALL-BASELINE"))

    def _always_raise(self, *args, **kwargs):
        raise RuntimeError("forced failure outside the per-strategy boundary")

    for method in ("apply_time_stops", "apply_trailing_stops", "settle_bar", "finalize_at_end"):
        monkeypatch.setattr(ShadowEvidenceEngine, method, _always_raise)
    harness = _run("SHADOW-1C-OUTER-FAIL-ALL", ShadowConfig(enabled=True, shadow_strategies=("S10",)))

    assert harness.state is RunState.COMPLETED, harness.fail_reason
    assert harness.shadow_engine is not None
    assert len(harness.shadow_engine.failures) > 0
    assert all(sid == "__engine__" for _as_of, sid, _err in harness.shadow_engine.failures)
    assert harness.shadow_engine.trade_legs == []  # settle_bar() never got to run its real body
    assert _competitive_fingerprint(harness) == disabled


# ------------------------------------------------------------------------------- Checkpoint 2: generic multi-edge aggregation

def test_summaries_aggregate_across_multiple_strategies_over_a_full_run() -> None:
    context = _context("SHADOW-2-SUMMARIES", ShadowConfig(enabled=True, shadow_strategies=("S10", "S21", "S39", "S40")))
    harness = _run("SHADOW-2-SUMMARIES", context.shadow_config)
    assert harness.shadow_engine is not None
    engine = harness.shadow_engine

    summaries = engine.summaries("12m", context.date_range.end)

    # Generic: exactly the configured strategies that actually produced evidence, no others, no
    # hardcoded assumption about which specific ones traded.
    assert set(summaries).issubset({"S10", "S21", "S39", "S40"})
    for strategy_id, summary in summaries.items():
        assert summary.strategy_id == strategy_id
        assert summary.source == "shadow"
        own_legs = [t for t in engine.trade_legs if t.leg.strategy_id == strategy_id]
        assert summary.window_metrics.n_trades == len(own_legs)
        if own_legs:
            assert summary.window_metrics.net_pnl == sum(t.leg.net_pnl for t in own_legs)
        own_opportunities = [o for o in engine.opportunities if o.strategy_id == strategy_id]
        assert summary.n_opportunities == len(own_opportunities)


def test_summaries_are_deterministic_across_repeated_runs() -> None:
    config = ShadowConfig(enabled=True, shadow_strategies=("S10", "S21"))
    context = _context("SHADOW-2-DET", config)
    harness_a = _run("SHADOW-2-DET", config)
    harness_b = _run("SHADOW-2-DET", config)
    assert harness_a.shadow_engine is not None and harness_b.shadow_engine is not None
    summaries_a = harness_a.shadow_engine.summaries("12m", context.date_range.end)
    summaries_b = harness_b.shadow_engine.summaries("12m", context.date_range.end)
    assert summaries_a == summaries_b


def test_configured_degraded_active_strategy_ids_are_consistent_over_a_full_run(monkeypatch) -> None:
    def _always_raise(self, strategy_id, as_of, bar_index, bars, phase_running):
        raise RuntimeError("forced failure for lifecycle-introspection test")

    monkeypatch.setattr(ShadowEvidenceEngine, "_settle_one", _always_raise)
    harness = _run("SHADOW-2-LIFECYCLE", ShadowConfig(enabled=True, shadow_strategies=("S10", "S21")))
    assert harness.shadow_engine is not None
    engine = harness.shadow_engine

    assert engine.configured_strategy_ids == frozenset({"S10", "S21"})
    assert engine.degraded_strategy_ids <= engine.configured_strategy_ids
    assert engine.active_strategy_ids == engine.configured_strategy_ids - engine.degraded_strategy_ids
    assert engine.active_strategy_ids.isdisjoint(engine.degraded_strategy_ids)


# ------------------------------------------------------------------------------- Checkpoint 3: first production strategy set

def test_all_43_production_strategies_execute_concurrently_with_byte_identical_competitive_execution() -> None:
    disabled = _competitive_fingerprint(_run("SHADOW-3-OFF"))
    all_ids = tuple(sorted(all_registered_strategies()))
    assert len(all_ids) == 43  # the real, already-established production set -- nothing hand-picked

    shadow_config = ShadowConfig(enabled=True, shadow_strategies=all_ids)
    context = _context("SHADOW-3-ALL-43", shadow_config)
    harness = _run("SHADOW-3-ALL-43", shadow_config)
    assert harness.shadow_engine is not None
    engine = harness.shadow_engine

    # Criterion 5: competitive execution unchanged, at real production scale.
    assert _competitive_fingerprint(harness) == disabled

    # Criterion 1: multiple existing strategies actually executed concurrently (not just risk-tapped).
    strategy_ids_with_positions = {p.strategy_id for p in engine.positions}
    assert len(strategy_ids_with_positions) > 1
    assert strategy_ids_with_positions.issubset(set(all_ids))

    # Criteria 2/3/4/7: every strategy that traded owns an isolated portfolio/ledger/statistics, with
    # no cross-strategy contamination -- checked exhaustively, not sampled.
    summaries = engine.summaries("12m", context.date_range.end)
    for strategy_id in strategy_ids_with_positions:
        own_legs = [t for t in engine.trade_legs if t.leg.strategy_id == strategy_id]
        other_legs = [t for t in engine.trade_legs if t.leg.strategy_id != strategy_id]
        own_positions = [p for p in engine.positions if p.strategy_id == strategy_id]
        assert all(p.strategy_id == strategy_id for p in own_positions)  # no foreign positions leaked in
        assert not any(t.position_id in {p.position_id for p in own_positions} for t in other_legs)
        summary = summaries[strategy_id]
        assert summary.strategy_id == strategy_id
        assert summary.window_metrics.n_trades == len(own_legs)


def test_all_43_production_strategies_replay_is_deterministic() -> None:
    config = ShadowConfig(enabled=True, shadow_strategies=tuple(sorted(all_registered_strategies())))
    harness_a = _run("SHADOW-3-DET", config)
    harness_b = _run("SHADOW-3-DET", config)
    assert harness_a.shadow_engine is not None and harness_b.shadow_engine is not None
    assert _shadow_ledger_fingerprint(harness_a) == _shadow_ledger_fingerprint(harness_b)


def test_one_strategy_failure_among_all_43_is_isolated(monkeypatch) -> None:
    disabled = _competitive_fingerprint(_run("SHADOW-3-FAIL-BASELINE"))
    all_ids = tuple(sorted(all_registered_strategies()))
    target = "S12"  # an arbitrary, real, already-registered strategy -- not special-cased in production code
    assert target in all_ids

    original = ShadowEvidenceEngine._settle_one

    def _raise_for_target(self, strategy_id, as_of, bar_index, bars, phase_running):
        if strategy_id == target:
            raise RuntimeError("forced failure for single-strategy isolation test")
        return original(self, strategy_id, as_of, bar_index, bars, phase_running)

    monkeypatch.setattr(ShadowEvidenceEngine, "_settle_one", _raise_for_target)
    harness = _run("SHADOW-3-FAIL", ShadowConfig(enabled=True, shadow_strategies=all_ids))

    assert harness.state is RunState.COMPLETED, harness.fail_reason
    assert harness.shadow_engine is not None
    engine = harness.shadow_engine

    assert engine.degraded_strategy_ids == frozenset({target})
    assert all(sid == target for _as_of, sid, _err in engine.failures)
    # Every OTHER configured strategy remains active and free to keep producing evidence.
    assert engine.active_strategy_ids == frozenset(all_ids) - {target}
    other_strategy_positions = {p.strategy_id for p in engine.positions if p.strategy_id != target}
    assert len(other_strategy_positions) > 0  # at least one other strategy kept trading normally
    assert _competitive_fingerprint(harness) == disabled
