"""Integration tests against the REAL Strategy Manager (:mod:`ai_trader.strategy_manager`).

Mirrors ``ai_trader/strategy_manager/tests/test_real_library_integration.py``'s own precedent:
proves the Signal Engine's fail-safe design holds against the ACTUAL production dependency, not just
controllable fakes. The real :class:`~ai_trader.strategy_manager.handle.StrategyRuntimeHandle` raises
``StrategyApiNotImplementedError`` for every method the pipeline calls except ``required_context()``
(see its own module docstring) -- the Signal Engine must degrade every such strategy to a classified
``INVALID``/``CORRUPTED_OUTPUT`` signal, never crash, and never fabricate a trading decision.
"""

from __future__ import annotations

from datetime import UTC, datetime

from ai_trader.signal_engine.engine import SignalEngine
from ai_trader.signal_engine.types import EngineOverallHealth, QualityFlag, SignalState
from ai_trader.signal_engine.tests.fixtures.fake_strategy import make_context
from ai_trader.strategy_manager.config import DEFAULT_LIBRARY_PATH, ManagerConfig
from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_manager.handle import StrategyHandle, StrategyRuntimeHandle
from ai_trader.strategy_manager.manager import StrategyManager
from ai_trader.strategy_manager.tests.fixtures.contracts import make_contract_dict
from ai_trader.strategy_manager.tests.fixtures.fake_scanner import FakeScanner

AS_OF = int(datetime(2026, 7, 14, tzinfo=UTC).timestamp())


def _real_handle(strategy_id: str = "S1", symbols: frozenset[str] = frozenset({"XAUUSD"})) -> StrategyHandle:
    contract = parse_contract(make_contract_dict(id=strategy_id))
    api = StrategyRuntimeHandle(strategy_id, contract, symbols)
    return StrategyHandle(id=strategy_id, contract=contract, api=api)


class TestRealStrategyRuntimeHandleDegradesGracefully:
    def test_evaluate_strategy_never_raises_for_the_real_handle(self) -> None:
        engine = SignalEngine()
        engine.configure()
        handle = _real_handle()
        signal = engine.evaluate_strategy(make_context(), handle, trader_state=None)
        assert signal.state is SignalState.INVALID
        assert QualityFlag.CORRUPTED_OUTPUT in signal.quality_flags

    def test_evaluate_batch_with_only_real_handles_never_raises(self) -> None:
        engine = SignalEngine()
        engine.configure()
        handles = [_real_handle(f"S{i}") for i in range(1, 4)]
        batch = engine.evaluate(make_context(), handles, trader_state=None)
        assert len(batch.signals) == 3
        assert all(s.state is SignalState.INVALID for s in batch.signals)

    def test_engine_stays_queryable_after_only_corrupted_signals(self) -> None:
        engine = SignalEngine()
        engine.configure()
        handle = _real_handle()
        engine.evaluate(make_context(), [handle], trader_state=None)
        assert engine.health().overall is EngineOverallHealth.OK  # engine itself is healthy; the
        # signal it produced is the one classified INVALID -- these are different questions.
        assert engine.statistics().invalids == 1

    def test_real_handle_required_context_is_still_used_for_scoping(self) -> None:
        """required_context() IS implemented on the real handle -- confirms scoping still works
        correctly even though every other method is unimplemented."""
        engine = SignalEngine()
        engine.configure()
        handle = _real_handle(symbols=frozenset({"EURUSD"}))
        batch = engine.evaluate(make_context(symbol="XAUUSD"), [handle], trader_state=None)
        assert batch.signals == ()  # not scoped to XAUUSD -> skipped entirely, never evaluated


class TestRealLibraryThroughStrategyManager:
    """Wires an actual :class:`StrategyManager` (real, unmigrated Strategy Library) into the Signal
    Engine end-to-end -- the whole point being that ``active_strategies()`` is currently empty
    (v0-seed schema gap, documented in Strategy Manager's own tests), so the Signal Engine must
    handle an empty handle list cleanly rather than assuming at least one strategy exists."""

    def test_signal_engine_handles_the_managers_currently_empty_active_set(self) -> None:
        mgr = StrategyManager(ManagerConfig())
        mgr.configure(FakeScanner())
        mgr.load_library(as_of=AS_OF)
        assert mgr.active_strategies() == []  # documents the known v0-seed gap (see Strategy
        # Manager's own test_real_library_integration.py) -- if this assertion ever fails because a
        # future migration lands, the rest of this test still exercises the real integration path.

        engine = SignalEngine()
        engine.configure()
        batch = engine.evaluate(make_context(), mgr.active_strategies(), trader_state=None)
        assert batch.signals == ()
        assert engine.health().overall is EngineOverallHealth.OK

    def test_library_directory_exists(self) -> None:
        assert DEFAULT_LIBRARY_PATH.is_dir()
