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

#: ALL 43 runtime-eligible strategies, migrated across Checkpoints 2-9 (Wave B COMPLETE):
#: Checkpoint 2 (above) + B4/B6 (S13, S44) + B3 (S26, S27, S28) + B5 (S45, S50) + B7
#: (S3, S4, S5, S10, S23, S46, S48) + B8 (S7, S9, S14, S15, S38, S39, S43) + B9 (S8, S41, S42,
#: S51) + B10 (S20, S25, S40, LAST). S4/S10/S15/S23/S38/S48 use the generic trailing-stop
#: mechanism (``ai_trader.simulation.trailing_stop``); S4/S23/S25/S43/S48 use the generic
#: historical-features window (``context_access.flag_n_ago``/``feature_n_ago``). This is every
#: strategy the frozen Research Lab marks IMPLEMENTED and runtime-eligible -- none remain.
CURRENT_MIGRATED_IDS = CHECKPOINT_2_IDS | frozenset({
    "S13", "S44",  # B4 + B6
    "S26", "S27", "S28",  # B3
    "S45", "S50",  # B5
    "S3", "S4", "S5", "S10", "S23", "S46", "S48",  # B7
    "S7", "S9", "S14", "S15", "S38", "S39", "S43",  # B8
    "S8", "S41", "S42", "S51",  # B9
    "S20", "S25", "S40",  # B10 (LAST)
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


def test_checkpoint_2_ids_remain_a_subset_of_active() -> None:
    """CHECKPOINT_2_IDS's own 15 strategies stay active as later batches are added on top --
    a regression here would mean a later batch broke an earlier one, not just "more strategies
    exist now"."""
    mgr = make_manager()
    handles = registry.build_runtime_handles(mgr, frozenset({"XAUUSD"}))
    ids = {h.id for h in handles}
    assert CHECKPOINT_2_IDS <= ids


def test_build_runtime_handles_shows_exactly_the_current_migrated_count() -> None:
    """StrategyManager.load_library() + build_runtime_handles() against the REAL library must show
    exactly the strategies migrated so far across every checkpoint -- a direct extension of the
    registry's own "expected loaded/active count per batch" testing discipline, updated as each
    new batch lands (documented, not a regression)."""
    mgr = make_manager()
    handles = registry.build_runtime_handles(mgr, frozenset({"XAUUSD"}))
    ids = {h.id for h in handles}
    assert ids == CURRENT_MIGRATED_IDS


def test_time_stop_bars_set_only_for_the_time_exit_strategies() -> None:
    """Only strategies whose own executable_default selects exit=time declare a time-stop; every
    other migrated strategy must NEVER have one -- opting in is per-strategy, never a forced
    default (ai_trader.simulation.time_stop's own generic contract)."""
    mgr = make_manager()
    handles = {h.id: h for h in registry.build_runtime_handles(mgr, frozenset({"XAUUSD"}))}
    time_exit_ids = {"S13", "S14", "S16", "S17", "S18", "S19", "S24", "S25", "S28", "S45"}
    for strategy_id in CURRENT_MIGRATED_IDS:
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
