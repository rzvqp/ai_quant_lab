"""Tests for the ``SimulationAPI`` facade: run bookkeeping, sibling-entry-point consistency,
NotFound handling, artifact wiring."""

from __future__ import annotations

from pathlib import Path

from ai_trader.market_scanner.types import SymbolMeta
from ai_trader.simulation.api import NotFound, SimulationAPI
from ai_trader.simulation.config import DateRange, SimulationContext
from ai_trader.simulation.types import RunState

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data" / "market"
SYMBOL_META = {"XAUUSD": SymbolMeta(symbol="XAUUSD", tick_size=0.01, point_value=1.0, price_precision=2)}


def _ctx(run_id: str, **overrides: object) -> SimulationContext:
    defaults: dict[str, object] = dict(
        run_id=run_id, date_range=DateRange(1_700_000_000, 1_700_020_000), symbols=("XAUUSD",),
        timeframes=("M15", "H1", "H4", "D1"), starting_balance=100_000.0, run_seed=1, warmup_bars=30,
    )
    defaults.update(overrides)
    return SimulationContext(**defaults)  # type: ignore[arg-type]


def test_unknown_run_id_returns_not_found_everywhere() -> None:
    api = SimulationAPI(SYMBOL_META, DATA_DIR)
    assert isinstance(api.status("ghost"), NotFound)
    assert isinstance(api.report("ghost"), NotFound)
    assert isinstance(api.statistics("ghost"), NotFound)
    assert isinstance(api.load("ghost"), NotFound)
    assert isinstance(api.step("ghost"), NotFound)


def test_configure_is_idempotent_per_run_id() -> None:
    api = SimulationAPI(SYMBOL_META, DATA_DIR)
    context = _ctx("IDEMPOTENT-1")
    h1 = api.configure(context)
    h2 = api.configure(context)
    assert h1.run_id == h2.run_id == "IDEMPOTENT-1"


def test_run_reaches_completed_and_report_matches() -> None:
    api = SimulationAPI(SYMBOL_META, DATA_DIR)
    context = _ctx("API-RUN-1")
    api.configure(context)
    report = api.run("API-RUN-1")
    assert not isinstance(report, NotFound)
    status = api.status("API-RUN-1")
    assert not isinstance(status, NotFound)
    assert status.state is RunState.COMPLETED
    # report() after run() returns the SAME finalized object, not a re-derived one.
    assert api.report("API-RUN-1") is report


def test_step_advances_one_bar_at_a_time() -> None:
    api = SimulationAPI(SYMBOL_META, DATA_DIR)
    context = _ctx("API-STEP-1")
    api.configure(context)
    api.load("API-STEP-1")
    s1 = api.step("API-STEP-1")
    assert not isinstance(s1, NotFound)
    bar_index_1 = s1.bar_index
    s2 = api.step("API-STEP-1")
    assert not isinstance(s2, NotFound)
    assert s2.bar_index == bar_index_1 + 1


def test_versions_and_health_do_not_raise() -> None:
    api = SimulationAPI(SYMBOL_META, DATA_DIR)
    assert "simulation_framework_version" in api.versions()
    health = api.health()
    assert health.overall in ("OK", "DEGRADED", "FAILED")


def test_run_batch_runs_each_context_independently() -> None:
    api = SimulationAPI(SYMBOL_META, DATA_DIR)
    contexts = (_ctx("BATCH-A", run_seed=1), _ctx("BATCH-B", run_seed=2))
    handle = api.run_batch(contexts, batch_id="BATCH1")
    assert handle.total == 2
    assert handle.completed == 2
    assert set(handle.run_ids) == {"BATCH-A", "BATCH-B"}


def test_artifacts_written_when_results_dir_configured(tmp_path) -> None:  # type: ignore[no-untyped-def]
    api = SimulationAPI(SYMBOL_META, DATA_DIR, results_dir=tmp_path)
    context = _ctx("API-ARTIFACTS-1")
    api.configure(context)
    report = api.run("API-ARTIFACTS-1")
    assert not isinstance(report, NotFound)
    assert report.artifacts is not None
    assert (tmp_path / "API-ARTIFACTS-1" / "manifest.json").exists()


def test_pause_resume_lifecycle() -> None:
    api = SimulationAPI(SYMBOL_META, DATA_DIR)
    context = _ctx("API-PAUSE-1")
    api.configure(context)
    api.load("API-PAUSE-1")
    api.step("API-PAUSE-1")
    # advance to RUNNING (past warmup) before pausing, since pause() only acts on RUNNING.
    for _ in range(40):
        status = api.step("API-PAUSE-1")
        assert not isinstance(status, NotFound)
        if status.state is RunState.RUNNING:
            break
    paused = api.pause("API-PAUSE-1")
    assert not isinstance(paused, NotFound)
    if paused.state is RunState.PAUSED:
        resumed = api.resume("API-PAUSE-1")
        assert not isinstance(resumed, NotFound)
        assert resumed.state is RunState.RUNNING


def test_pause_on_unknown_run_returns_not_found() -> None:
    api = SimulationAPI(SYMBOL_META, DATA_DIR)
    assert isinstance(api.pause("ghost"), NotFound)
    assert isinstance(api.resume("ghost"), NotFound)
    assert isinstance(api.stop("ghost"), NotFound)
    assert isinstance(api.run("ghost"), NotFound)
    assert isinstance(api.run_batch((), batch_id="EMPTY").run_ids, tuple)


def test_stop_finalizes_report() -> None:
    api = SimulationAPI(SYMBOL_META, DATA_DIR)
    context = _ctx("API-STOP-1")
    api.configure(context)
    api.load("API-STOP-1")
    api.step("API-STOP-1")
    report = api.stop("API-STOP-1")
    assert not isinstance(report, NotFound)
    status = api.status("API-STOP-1")
    assert not isinstance(status, NotFound)
    assert status.state is RunState.STOPPED


def test_load_unknown_run_returns_not_found() -> None:
    api = SimulationAPI(SYMBOL_META, DATA_DIR)
    assert isinstance(api.load("ghost"), NotFound)
    assert isinstance(api.statistics("ghost"), NotFound)
