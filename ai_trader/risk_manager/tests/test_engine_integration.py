"""Integration tests against the REAL Scoring Engine, and through it the REAL Signal Engine +
Strategy Manager -- mirroring the precedent set by every prior module's own
``test_engine_integration.py``: proves the Risk Manager's fail-safe design holds end-to-end against
the ACTUAL production dependency chain, not just controllable fakes.
"""

from __future__ import annotations

from datetime import UTC, datetime

from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.engine import RiskManager
from ai_trader.risk_manager.tests.fixtures.fake_opportunity import make_portfolio, make_risk_context
from ai_trader.risk_manager.types import Decision
from ai_trader.scoring_engine.config import ScoringConfig
from ai_trader.scoring_engine.engine import ScoringEngine
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


class TestFullChainNeverCrashes:
    """The real StrategyRuntimeHandle raises StrategyApiNotImplementedError for every method except
    required_context() -- so every real strategy's signal is Signal-Engine-classified INVALID, which
    the Scoring Engine turns into SKIP/INVALID, which the Risk Manager must turn into a classified
    DENY(NOT_ACTIONABLE) -- never a crash, anywhere in the four-module chain."""

    def test_real_strategy_end_to_end_is_denied_not_a_crash(self) -> None:
        signal_engine = SignalEngine()
        signal_engine.configure()
        handle = _real_handle("S1")
        signal = signal_engine.evaluate_strategy(make_context(symbol="XAUUSD"), handle, trader_state=None)

        scoring_engine = ScoringEngine(ScoringConfig())
        scoring_engine.configure(manager=None)
        score = scoring_engine.score_signal(signal)

        risk_manager = RiskManager(RiskConfig())
        portfolio = make_portfolio(as_of=score.as_of)
        risk_manager.configure(portfolio=portfolio)
        decision = risk_manager.allow_trade(score, make_risk_context(as_of=score.as_of), portfolio)

        assert decision.decision is Decision.DENY
        assert decision.denied_reasons[0].code == "NOT_ACTIONABLE"

    def test_full_chain_batch_never_raises(self) -> None:
        signal_engine = SignalEngine()
        signal_engine.configure()
        scoring_engine = ScoringEngine(ScoringConfig())
        scoring_engine.configure(manager=None)

        scores = []
        for sid in ("S1", "S2", "S3"):
            signal = signal_engine.evaluate_strategy(
                make_context(symbol="XAUUSD"), _real_handle(sid), trader_state=None,
            )
            scores.append(scoring_engine.score_signal(signal))

        risk_manager = RiskManager(RiskConfig())
        portfolio = make_portfolio(as_of=scores[0].as_of)
        risk_manager.configure(portfolio=portfolio)
        batch = risk_manager.evaluate(scores, make_risk_context(as_of=scores[0].as_of), portfolio)

        assert len(batch.decisions) == 3
        assert all(d.decision is Decision.DENY for d in batch.decisions)


class TestRealStrategyManagerLibrary:
    """Wires the real (v0-seed, all-quarantined) Strategy Library through the whole chain."""

    def test_library_directory_exists(self) -> None:
        assert DEFAULT_LIBRARY_PATH.is_dir()

    def test_managers_currently_empty_active_set_produces_an_empty_risk_batch(self) -> None:
        mgr = StrategyManager(ManagerConfig())
        mgr.configure(FakeScanner())
        mgr.load_library(as_of=AS_OF)
        assert mgr.active_strategies() == []  # documents the known v0-seed gap

        signal_engine = SignalEngine()
        signal_engine.configure()
        signal_batch = signal_engine.evaluate(make_context(symbol="XAUUSD"), mgr.active_strategies(), trader_state=None)
        assert signal_batch.signals == ()

        scoring_engine = ScoringEngine(ScoringConfig())
        scoring_engine.configure(manager=mgr)
        score_batch = scoring_engine.score_batch(list(signal_batch.signals))
        assert score_batch.scores == ()

        risk_manager = RiskManager(RiskConfig())
        portfolio = make_portfolio()
        risk_manager.configure(portfolio=portfolio)
        risk_batch = risk_manager.evaluate(list(score_batch.scores), make_risk_context(), portfolio)
        assert risk_batch.decisions == ()
        assert risk_manager.health().overall.value == "OK"
