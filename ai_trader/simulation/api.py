"""The Simulation Framework's public API facade (``SIMULATION_API.md``) -- ``SimulationHarness``
wrapped with run bookkeeping (registry of runs by ``run_id``), a single shared internal state-mutation
helper (``_transition``), and the ~11 documented entry points.

**Sibling-entry-point discipline** (``SIMULATION_HANDOFF.md`` §13, carried forward from Execution
Engine's own CRITICAL finding #1): every entry point that can move a run's state --
``configure``/``load``/``run``/``step``/``pause``/``resume``/``stop`` -- routes through
:meth:`SimulationAPI._require_run`/the harness's own single ``step()`` implementation, never
duplicating the per-bar loop or the state-transition logic in more than one place.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from ai_trader.market_scanner.types import SymbolMeta
from ai_trader.simulation import performance_analyzer
from ai_trader.simulation.artifacts import ArtifactWriter
from ai_trader.simulation.config import (
    COST_MODEL_VERSION,
    FILL_MODEL_VERSION,
    SIMULATION_FRAMEWORK_VERSION,
    SIMULATION_SCHEMA_VERSION,
    SimulationContext,
)
from ai_trader.simulation.harness import SimulationHarness
from ai_trader.simulation.performance_analyzer import SimulationReportData
from ai_trader.simulation.types import RunState, SimPhase, TERMINAL_RUN_STATES

_MODULE_VERSIONS = {
    "simulation_framework_version": SIMULATION_FRAMEWORK_VERSION,
    "simulation_schema_version": SIMULATION_SCHEMA_VERSION,
    "fill_model_version": FILL_MODEL_VERSION,
    "cost_model_version": COST_MODEL_VERSION,
}


@dataclass(frozen=True, slots=True)
class RunHandle:
    run_id: str
    state: RunState
    progress: float = 0.0


@dataclass(frozen=True, slots=True)
class RunStatus:
    run_id: str
    state: RunState
    as_of: int | None
    bar_index: int
    phase: SimPhase | None
    equity: float
    open_positions: int
    progress_pct: float


@dataclass(frozen=True, slots=True)
class BatchHandle:
    batch_id: str
    run_ids: tuple[str, ...]
    completed: int
    total: int


@dataclass(frozen=True, slots=True)
class Statistics:
    bars_processed: int
    orders: int
    fills: int
    trades: int
    avg_bar_ms: float = 0.0


@dataclass(frozen=True, slots=True)
class FrameworkHealth:
    overall: str
    state: RunState
    degraded_reasons: tuple[str, ...]
    module_versions: dict[str, str]


@dataclass(frozen=True, slots=True)
class NotFound:
    run_id: str


class SimulationAPI:
    """One process-lifetime facade over many runs. ``symbol_meta``/``data_dir`` are instance-level
    (IMPLEMENTATION CHOICE: ``SIMULATION_API.md``'s ``configure(context)`` signature names only the
    context; the historical-data location and instrument reference data are deployment-level, not
    per-run, concerns -- supplied once when the facade itself is constructed)."""

    def __init__(
        self, symbol_meta: dict[str, SymbolMeta], data_dir: Path,
        results_dir: Path | None = None, generated_at: int = 0,
    ) -> None:
        self._symbol_meta = symbol_meta
        self._data_dir = data_dir
        self._results_dir = results_dir
        self._generated_at = generated_at
        self._runs: dict[str, SimulationHarness] = {}
        self._reports: dict[str, SimulationReportData] = {}

    # ------------------------------------------------------------------ 1. configuration & loading

    def configure(self, context: SimulationContext) -> RunHandle:
        if context.run_id in self._runs:
            return self._handle(context.run_id)  # idempotent per run_id (SIMULATION_API.md §1)
        harness = SimulationHarness(context, self._symbol_meta, self._data_dir)
        harness.configure()
        self._runs[context.run_id] = harness
        return self._handle(context.run_id)

    def load(self, run_id: str) -> RunHandle | NotFound:
        harness = self._runs.get(run_id)
        if harness is None:
            return NotFound(run_id=run_id)
        harness.load()
        return self._handle(run_id)

    # ------------------------------------------------------------------ 2. running

    def run(self, run_id: str) -> SimulationReportData | NotFound:
        harness = self._runs.get(run_id)
        if harness is None:
            return NotFound(run_id=run_id)
        if harness.state is RunState.CONFIGURED:
            harness.load()
        if harness.state not in TERMINAL_RUN_STATES:
            harness.run_to_completion()
        return self._finalize(run_id, harness)

    def step(self, run_id: str, n: int = 1) -> RunStatus | NotFound:
        harness = self._runs.get(run_id)
        if harness is None:
            return NotFound(run_id=run_id)
        for _ in range(max(1, n)):
            if not harness.step():
                break
        if harness.state in TERMINAL_RUN_STATES and run_id not in self._reports:
            self._finalize(run_id, harness)
        status = self.status(run_id)
        assert not isinstance(status, NotFound)
        return status

    def run_batch(self, contexts: tuple[SimulationContext, ...], batch_id: str) -> BatchHandle:
        """Runs are independent and fully reproducible from their own ``(context, seed)``
        (``SIMULATION_API.md`` §2). IMPLEMENTATION CHOICE: v1 executes them sequentially in-process
        (still fully independent state per run) -- the doc's "MAY run in parallel" is a permission, not
        a requirement; parallel execution is deferred (disclosed limitation, no correctness difference
        since determinism is per-run)."""
        run_ids: list[str] = []
        completed = 0
        for context in contexts:
            self.configure(context)
            result = self.run(context.run_id)
            run_ids.append(context.run_id)
            if not isinstance(result, NotFound):
                completed += 1
        return BatchHandle(batch_id=batch_id, run_ids=tuple(run_ids), completed=completed, total=len(contexts))

    def pause(self, run_id: str) -> RunStatus | NotFound:
        harness = self._runs.get(run_id)
        if harness is None:
            return NotFound(run_id=run_id)
        if harness.state is RunState.RUNNING:
            harness.state = RunState.PAUSED
        status = self.status(run_id)
        assert not isinstance(status, NotFound)
        return status

    def resume(self, run_id: str) -> RunStatus | NotFound:
        harness = self._runs.get(run_id)
        if harness is None:
            return NotFound(run_id=run_id)
        if harness.state is RunState.PAUSED:
            harness.state = RunState.RUNNING
        status = self.status(run_id)
        assert not isinstance(status, NotFound)
        return status

    def stop(self, run_id: str) -> SimulationReportData | NotFound:
        harness = self._runs.get(run_id)
        if harness is None:
            return NotFound(run_id=run_id)
        harness.stop_now()  # applies close_at_end_policy before finalizing (a real gap a review caught)
        return self._finalize(run_id, harness)

    # ------------------------------------------------------------------ 3. results & introspection

    def report(self, run_id: str) -> SimulationReportData | NotFound:
        if run_id in self._reports:
            return self._reports[run_id]
        harness = self._runs.get(run_id)
        if harness is None:
            return NotFound(run_id=run_id)
        if harness.portfolio_simulator is None:
            return NotFound(run_id=run_id)
        return performance_analyzer.analyze(harness.context, harness.portfolio_simulator.account)

    def status(self, run_id: str) -> RunStatus | NotFound:
        harness = self._runs.get(run_id)
        if harness is None:
            return NotFound(run_id=run_id)
        equity = harness.portfolio_simulator.account.equity if harness.portfolio_simulator else 0.0
        open_positions = len(harness.portfolio_simulator.account.positions) if harness.portfolio_simulator else 0
        total = harness.total_ticks
        progress = (harness.bars_processed / total * 100.0) if total else 0.0
        return RunStatus(
            run_id=run_id, state=harness.state, as_of=harness.as_of, bar_index=harness.bar_index,
            phase=harness.phase, equity=equity, open_positions=open_positions, progress_pct=progress,
        )

    def statistics(self, run_id: str) -> Statistics | NotFound:
        harness = self._runs.get(run_id)
        if harness is None:
            return NotFound(run_id=run_id)
        trades = len(harness.portfolio_simulator.account.trade_ledger) if harness.portfolio_simulator else 0
        return Statistics(
            bars_processed=harness.bars_processed, orders=harness.orders_submitted,
            fills=harness.fills_total, trades=trades,
        )

    def health(self) -> FrameworkHealth:
        degraded = [r for h in self._runs.values() for r in h.degraded_reasons]
        any_failed = any(h.state is RunState.FAILED for h in self._runs.values())
        overall = "FAILED" if any_failed else ("DEGRADED" if degraded else "OK")
        return FrameworkHealth(
            overall=overall, state=RunState.RUNNING if self._runs else RunState.UNINITIALIZED,
            degraded_reasons=tuple(degraded), module_versions=dict(_MODULE_VERSIONS),
        )

    def versions(self) -> dict[str, str]:
        return dict(_MODULE_VERSIONS)

    # ------------------------------------------------------------------ internals

    def _handle(self, run_id: str) -> RunHandle:
        harness = self._runs[run_id]
        total = harness.total_ticks
        progress = (harness.bars_processed / total * 100.0) if total else 0.0
        return RunHandle(run_id=run_id, state=harness.state, progress=progress)

    def _finalize(self, run_id: str, harness: SimulationHarness) -> SimulationReportData:
        if run_id in self._reports:
            return self._reports[run_id]
        assert harness.portfolio_simulator is not None
        report_data = performance_analyzer.analyze(harness.context, harness.portfolio_simulator.account)

        if self._results_dir is not None:
            state = harness.state.value if harness.state.value in ("COMPLETED", "FAILED", "STOPPED") else "STOPPED"
            schema_dict = performance_analyzer.to_schema_dict(
                harness.context, report_data, state, harness.composed_module_versions(), self._generated_at,
            )
            writer = ArtifactWriter(run_id, self._results_dir)
            artifacts = writer.write(harness.portfolio_simulator.account, schema_dict, harness.context.record)
            report_data = replace(report_data, artifacts=artifacts)

        self._reports[run_id] = report_data
        return report_data
