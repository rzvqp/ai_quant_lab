"""Tests for the runtime-evaluator registry: only strategies BOTH loaded/active by Strategy Manager
AND registered here get a real runtime handle."""

from __future__ import annotations

from ai_trader.market_scanner.config import ScannerConfig
from ai_trader.market_scanner.scanner import AdapterConfig, MarketScanner
from ai_trader.market_scanner.types import Mode, SymbolMeta
from ai_trader.strategy_manager.config import ManagerConfig
from ai_trader.strategy_manager.manager import StrategyManager
from ai_trader.strategy_runtime import registry


def make_manager(auto_admit: str | None = "EXPLORATORY") -> StrategyManager:
    scanner = MarketScanner(ScannerConfig())
    scanner.configure(
        [SymbolMeta(symbol="XAUUSD", tick_size=0.01, point_value=1.0, price_precision=2)],
        AdapterConfig(mode=Mode.REPLAY, source_id="replay"),
    )
    mgr = StrategyManager(ManagerConfig(auto_admit_min_maturity=auto_admit))
    mgr.configure(scanner)
    mgr.load_library(as_of=1_700_000_000)
    return mgr


#: Phase 6.8 Checkpoint 2 -- Wave B batches B1 (session/calendar, 9) + B2 (liquidity/sweep, 5),
#: migrated and implemented alongside S1's own Checkpoint 1 reference slice.
CHECKPOINT_2_IDS = frozenset({
    "S1", "S6", "S16", "S17", "S18", "S19", "S24", "S29", "S30", "S31",  # B1 + S1
    "S2", "S11", "S12", "S21", "S22",  # B2
})


def test_s1_is_registered() -> None:
    registry._ensure_families_imported()
    assert "S1" in registry.registered_strategy_ids()


def test_checkpoint_2_strategies_are_all_registered() -> None:
    registry._ensure_families_imported()
    assert CHECKPOINT_2_IDS <= registry.registered_strategy_ids()


def test_build_runtime_handles_returns_only_registered_and_active() -> None:
    mgr = make_manager()
    handles = registry.build_runtime_handles(mgr, frozenset({"XAUUSD"}))
    ids = {h.id for h in handles}
    assert "S1" in ids
    # every real S2..S51 is either still v0 (INVALID) or lacks a registered evaluator -- neither
    # should ever leak into the runtime handle list.
    assert ids <= registry.registered_strategy_ids()


def test_build_runtime_handles_shows_exactly_the_checkpoint_2_count() -> None:
    """After B1+B2's own migration, StrategyManager.load_library() + build_runtime_handles() against
    the REAL library must show exactly the 15 strategies (S1 + 14) migrated so far -- a direct
    extension of the registry's own "expected loaded/active count per batch" testing discipline."""
    mgr = make_manager()
    handles = registry.build_runtime_handles(mgr, frozenset({"XAUUSD"}))
    ids = {h.id for h in handles}
    assert ids == CHECKPOINT_2_IDS


def test_time_stop_bars_set_only_for_the_time_exit_strategies() -> None:
    """Only S16/S17/S18/S19/S24 (whose own executable_default selects exit=time) declare a
    time-stop; every other Checkpoint 2 strategy must NEVER have one -- opting in is per-strategy,
    never a forced default (ai_trader.simulation.time_stop's own generic contract)."""
    mgr = make_manager()
    handles = {h.id: h for h in registry.build_runtime_handles(mgr, frozenset({"XAUUSD"}))}
    time_exit_ids = {"S16", "S17", "S18", "S19", "S24"}
    for strategy_id in CHECKPOINT_2_IDS:
        expected = 24 if strategy_id in time_exit_ids else None
        assert handles[strategy_id].api.time_stop_bars == expected, strategy_id


def test_no_auto_admit_means_no_runtime_handles() -> None:
    mgr = make_manager(auto_admit=None)
    handles = registry.build_runtime_handles(mgr, frozenset({"XAUUSD"}))
    assert handles == ()


def test_duplicate_registration_raises() -> None:
    import pytest
    from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator

    class _Dummy(RuntimeEvaluator):
        def evaluate(self, context):  # type: ignore[no-untyped-def]
            raise NotImplementedError

    registry.register("S999-TEST-ONLY")(_Dummy)  # first registration succeeds
    with pytest.raises(ValueError):
        registry.register("S999-TEST-ONLY")(_Dummy)  # second registration for the SAME id raises
