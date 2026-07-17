"""Shadow Mode isolation proofs -- Phase 6.10 Implementation Checkpoints 1A + 1B
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
from ai_trader.shadow_evidence.config import ShadowConfig
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
