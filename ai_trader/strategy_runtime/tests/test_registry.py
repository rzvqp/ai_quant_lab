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


def test_s1_is_registered() -> None:
    registry._ensure_families_imported()
    assert "S1" in registry.registered_strategy_ids()


def test_build_runtime_handles_returns_only_registered_and_active() -> None:
    mgr = make_manager()
    handles = registry.build_runtime_handles(mgr, frozenset({"XAUUSD"}))
    ids = {h.id for h in handles}
    assert "S1" in ids
    # every real S2..S51 is either still v0 (INVALID) or lacks a registered evaluator -- neither
    # should ever leak into the runtime handle list.
    assert ids <= registry.registered_strategy_ids()


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
