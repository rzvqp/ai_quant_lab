"""Integration tests against the REAL Risk Manager, and through it the REAL Scoring Engine + Signal
Engine + Strategy Manager -- mirroring the precedent set by every prior module's own
``test_engine_integration.py``: proves the Execution Engine's fail-safe design holds end-to-end against
the ACTUAL production dependency chain, not just controllable fakes.
"""

from __future__ import annotations

from datetime import UTC, datetime

from ai_trader.execution_engine.config import ExecConfig
from ai_trader.execution_engine.engine import ExecutionEngine
from ai_trader.execution_engine.tests.fixtures.fake_broker import FakeBrokerAdapter, make_capabilities
from ai_trader.execution_engine.types import OrderState
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.engine import RiskManager
from ai_trader.risk_manager.tests.fixtures.fake_opportunity import make_portfolio, make_risk_context
from ai_trader.scoring_engine.config import ScoringConfig
from ai_trader.scoring_engine.engine import ScoringEngine
from ai_trader.signal_engine.engine import SignalEngine
from ai_trader.signal_engine.tests.fixtures.fake_strategy import make_context
from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_manager.handle import StrategyHandle, StrategyRuntimeHandle
from ai_trader.strategy_manager.tests.fixtures.contracts import make_contract_dict

AS_OF = int(datetime(2026, 7, 14, tzinfo=UTC).timestamp())
CAPS = make_capabilities()


def _real_handle(strategy_id: str = "S1", symbols: frozenset[str] = frozenset({"XAUUSD"})) -> StrategyHandle:
    contract = parse_contract(make_contract_dict(id=strategy_id))
    api = StrategyRuntimeHandle(strategy_id, contract, symbols)
    return StrategyHandle(id=strategy_id, contract=contract, api=api)


class TestFullChainNeverCrashes:
    """The real ``StrategyRuntimeHandle`` raises ``StrategyApiNotImplementedError`` for every method
    except ``required_context()`` -- so every real strategy's signal is Signal-Engine-classified
    INVALID, which the Scoring Engine turns into SKIP/INVALID, which the Risk Manager turns into a
    classified DENY, which the Execution Engine must turn into a no-op -- never a crash, anywhere in
    the five-module chain."""

    def test_real_strategy_end_to_end_is_a_no_op_not_a_crash(self) -> None:
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
        assert decision.decision.value == "DENY"

        execution_engine = ExecutionEngine(ExecConfig())
        execution_engine.configure(FakeBrokerAdapter(caps=CAPS))
        status = execution_engine.execute(decision, portfolio)
        assert status.state is OrderState.REJECTED
        assert "NOT_ALLOW" in status.reasons[0]

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

        execution_engine = ExecutionEngine(ExecConfig())
        execution_engine.configure(FakeBrokerAdapter(caps=CAPS))
        statuses = [execution_engine.execute(d, portfolio) for d in batch.decisions]
        assert all(s.state is OrderState.REJECTED for s in statuses)
        assert execution_engine.health().overall.value == "OK"


class TestRealAllowDecisionFillsEndToEnd:
    """Uses Risk Manager's OWN fixture-built ``OpportunityScore`` (a real, schema-valid object built
    through the real Scoring Engine -- not a hand-constructed dict) to force a real ALLOW decision, then
    proves it flows all the way through to a FILLED order against a fake (but Protocol-conformant)
    broker."""

    def test_allow_decision_from_a_real_risk_manager_fills(self) -> None:
        from ai_trader.risk_manager.tests.fixtures.fake_opportunity import make_opportunity

        rm = RiskManager(RiskConfig())
        portfolio = make_portfolio()
        rm.configure(portfolio=portfolio)
        rm._config.filters.reference_spread["XAUUSD"] = 0.1
        rm._config.filters.liquidity_floor["XAUUSD"] = 100.0
        opp = make_opportunity(strength=0.95)
        decision = rm.allow_trade(opp, make_risk_context(), portfolio)
        assert decision.decision.value == "ALLOW"

        execution_engine = ExecutionEngine(ExecConfig())
        execution_engine.configure(FakeBrokerAdapter(caps=CAPS))
        status = execution_engine.execute(decision, portfolio)
        assert status.state is OrderState.FILLED
        assert status.filled_qty > 0

        report = execution_engine.report()
        assert len(report.fills) == 1
        assert report.fills[0].symbol == decision.symbol
