"""Integration tests against the REAL Strategy Manager (:mod:`ai_trader.strategy_manager`) and, via
it, the REAL Signal Engine's ``StrategyRuntimeHandle``.

Mirrors the precedent set by ``ai_trader/signal_engine/tests/test_engine_integration.py`` and
``ai_trader/strategy_manager/tests/test_real_library_integration.py``: proves the Scoring Engine's
fail-safe design holds end-to-end against the ACTUAL production dependency chain, not just
controllable fakes. The real Strategy Library is "v0 seed" shape (documented, pre-existing,
CEO-gated-migration gap) -- every real strategy quarantines to ``Lifecycle.INVALID`` with
``entry.contract=None``. This is a genuinely interesting case for the Evidence Binder: ``find_strategy()``
SUCCEEDS (a ``StrategyView`` with ``lifecycle=INVALID`` is returned) while ``get_contract()`` FAILS
(``NotFound``, since the quarantined entry has no parsed contract) -- ``BoundEvidence.found`` requires
BOTH, so this exercises the "partial lookup mismatch" fail-safe path against real data, not just a
synthetic fixture.
"""

from __future__ import annotations

from datetime import UTC, datetime

from ai_trader.scoring_engine.config import ScoringConfig
from ai_trader.scoring_engine.engine import ScoringEngine
from ai_trader.scoring_engine.types import Recommendation
from ai_trader.signal_engine.engine import SignalEngine
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


class TestRealStrategyManagerEvidenceBinding:
    def test_real_quarantined_strategy_is_evidence_missing_not_a_crash(self) -> None:
        """A strategy known to find_strategy() (lifecycle=INVALID) but not get_contract() (no
        parsed contract) must resolve to EVIDENCE_MISSING, never raise, never fabricate."""
        mgr = StrategyManager(ManagerConfig())
        mgr.configure(FakeScanner())
        mgr.load_library(as_of=AS_OF)

        strategy_ids = [v.id for v in mgr.list_strategies()]
        assert strategy_ids  # the real Library has 51 folders (see Strategy Manager's own tests)
        from ai_trader.strategy_manager.types import NotFound as SMNotFound
        # Pick the first id that is STILL v0-seed (no parsed contract) rather than assuming index 0:
        # S1 is migrated to Strategy Interface v1 as of the Phase 6.8 reference slice
        # (STRATEGY_RUNTIME_INTEGRATION_GAP.md) and DOES have a parsed contract now, so a hardcoded
        # "first id" assumption would break here as each further strategy migrates in Wave B too.
        real_id = next(sid for sid in strategy_ids if isinstance(mgr.get_contract(sid), SMNotFound))
        view = mgr.find_strategy(real_id)
        contract = mgr.get_contract(real_id)
        assert not isinstance(view, SMNotFound)  # find_strategy succeeds...
        assert isinstance(contract, SMNotFound)  # ...but get_contract does not (documented v0-seed gap)

        engine = ScoringEngine(ScoringConfig())
        engine.configure(manager=mgr)
        # Build a genuine, schema-valid StrategySignal for this exact real strategy id via the real
        # Signal Engine, so the whole chain (real Strategy Manager evidence + real signal shape) is
        # exercised, not a synthetic approximation of one.
        signal_engine = SignalEngine()
        signal_engine.configure()
        handle = _real_handle(real_id)
        signal = signal_engine.evaluate_strategy(make_context(symbol="XAUUSD"), handle, trader_state=None)

        score = engine.score_signal(signal)
        assert score.strategy_id == real_id
        # the real StrategyRuntimeHandle raises StrategyApiNotImplementedError for every method the
        # Signal Engine's pipeline calls except required_context() -- so this signal is itself
        # already classified INVALID/CORRUPTED_OUTPUT upstream, which the Scoring Engine treats as a
        # non-actionable state -> SKIP (never a crash, never a fabricated positive score).
        assert score.recommendation in (Recommendation.SKIP, Recommendation.INVALID)

    def test_library_directory_exists(self) -> None:
        assert DEFAULT_LIBRARY_PATH.is_dir()


class TestRealStrategyManagerBatchNeverCrashes:
    def test_batch_of_real_quarantined_strategies_never_raises(self) -> None:
        mgr = StrategyManager(ManagerConfig())
        mgr.configure(FakeScanner())
        mgr.load_library(as_of=AS_OF)
        strategy_ids = [v.id for v in mgr.list_strategies()][:5]

        signal_engine = SignalEngine()
        signal_engine.configure()
        signals = [
            signal_engine.evaluate_strategy(make_context(symbol="XAUUSD"), _real_handle(sid), trader_state=None)
            for sid in strategy_ids
        ]

        engine = ScoringEngine(ScoringConfig())
        engine.configure(manager=mgr)
        batch = engine.score_batch(signals)
        assert len(batch.scores) == len(strategy_ids)
        assert all(s.recommendation in (Recommendation.SKIP, Recommendation.INVALID) for s in batch.scores)

    def test_engine_stays_queryable_throughout(self) -> None:
        mgr = StrategyManager(ManagerConfig())
        mgr.configure(FakeScanner())
        mgr.load_library(as_of=AS_OF)
        engine = ScoringEngine(ScoringConfig())
        engine.configure(manager=mgr)

        signal_engine = SignalEngine()
        signal_engine.configure()
        real_id = [v.id for v in mgr.list_strategies()][0]
        signal = signal_engine.evaluate_strategy(
            make_context(symbol="XAUUSD"), _real_handle(real_id), trader_state=None,
        )
        engine.score_signal(signal)
        assert engine.health().state.value in ("READY", "SCORING", "DEGRADED")
        assert engine.statistics().scores_total == 1
