"""Shadow Mode disabled-mode parity scaffold -- Phase 6.10 Implementation Checkpoint 1A
(``PHASE_6_10_SHADOW_EVIDENCE_ARCHITECTURE_DESIGN.md``). Proves that adding
``SimulationContext.shadow_config`` (defaulting to disabled) changes NOTHING about the harness's own
real, competitive behavior: the trade ledger, the full ``SimulationReportData`` (every field, not a
subset -- Phase 6.9A's own adversarial-review-caught standard, ``PHASE_6_9A_STRATEGY_EVIDENCE_FLOW_
AUDIT_REPORT.md`` §4.1), risk events, and order sequencing are all unaffected across two independent
runs of the identical config; no shadow evidence record of any kind is created; and exactly one
instance each of ``RiskManager``/``ExecutionEngine``/``ExecutionSimulator``/``PortfolioSimulator`` is
constructed per run -- never an extra, shadow-owned instance, since no tap exists yet in this
checkpoint. Same real-strategy-runtime fixture convention as ``test_risk_event_strategy_attribution.py``
(Phase 6.9A).
"""

from __future__ import annotations

import inspect
from dataclasses import asdict
from pathlib import Path

import ai_trader.simulation.harness as harness_module
from ai_trader.execution_engine.engine import ExecutionEngine
from ai_trader.market_scanner.types import SymbolMeta
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.engine import RiskManager
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


def _context(run_id: str) -> SimulationContext:
    # Same window/config convention as test_risk_event_strategy_attribution.py (Phase 6.9A).
    return SimulationContext(
        run_id=run_id, date_range=DateRange(1_672_617_600, 1_680_000_000),
        symbols=("XAUUSD",), timeframes=("M15", "H1", "H4", "D1"), starting_balance=2000.0,
        run_seed=1, warmup_bars=200,
    )


def _run(run_id: str) -> SimulationHarness:
    context = _context(run_id)
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


def test_shadow_config_defaults_to_disabled_and_needs_no_caller_change() -> None:
    context = _context("SHADOW-DEFAULT")
    assert context.shadow_config.enabled is False


def test_disabled_shadow_produces_no_shadow_evidence_objects() -> None:
    harness = _run("SHADOW-NOOP")
    for attr in ("shadow_ledger", "shadow_positions", "shadow_opportunities", "shadow_engines"):
        assert not hasattr(harness, attr)
    # Strongest available proof harness.py cannot construct any shadow object this checkpoint: it does
    # not even import the package. If a later checkpoint wires the tap in, this test's own failure is
    # the expected, deliberate signal that Checkpoint 1B has begun -- not a regression.
    assert "shadow_evidence" not in inspect.getsource(harness_module)


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
    harness_a = _run("SHADOW-DET-A")
    harness_b = _run("SHADOW-DET-B")

    assert harness_a.portfolio_simulator is not None
    assert harness_b.portfolio_simulator is not None

    # Full SimulationReportData (portfolio_summary, performance, attribution, stats, allocation,
    # risk_events -- every field), not a subset.
    assert _full_report_dict(harness_a) == _full_report_dict(harness_b)

    trades_a = [asdict(t) for t in harness_a.portfolio_simulator.account.trade_ledger]  # type: ignore[call-overload]
    trades_b = [asdict(t) for t in harness_b.portfolio_simulator.account.trade_ledger]  # type: ignore[call-overload]
    assert trades_a == trades_b

    risk_events_a = [asdict(e) for e in harness_a.portfolio_simulator.account.risk_events]  # type: ignore[call-overload]
    risk_events_b = [asdict(e) for e in harness_b.portfolio_simulator.account.risk_events]  # type: ignore[call-overload]
    assert risk_events_a == risk_events_b

    orders_a = {oid: asdict(o) for oid, o in harness_a.execution_simulator._orders.items()}  # type: ignore[call-overload]
    orders_b = {oid: asdict(o) for oid, o in harness_b.execution_simulator._orders.items()}  # type: ignore[call-overload]
    assert orders_a == orders_b
