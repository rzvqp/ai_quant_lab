"""Tests for :mod:`ai_trader.risk_manager.assembler`."""

from __future__ import annotations

from ai_trader.risk_manager import assembler
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.pipeline import PipelineOutcome
from ai_trader.risk_manager.tests.fixtures.fake_opportunity import make_opportunity, make_portfolio
from ai_trader.risk_manager.types import AppliedRule, Constraints, DeniedReason, Decision, EngineState, Sizing, SizingMethod
from ai_trader.signal_engine.types import Direction

CONFIG = RiskConfig()


class TestAssembleDecisionDeny:
    def test_deny_carries_reasons_and_no_sizing(self) -> None:
        opp = make_opportunity()
        outcome = PipelineOutcome(
            allowed=False, applied_rules=(AppliedRule(rule="X", passed=False),),
            denied_reasons=(DeniedReason(code="BELOW_FLOOR"),),
        )
        decision = assembler.assemble_decision(opp, outcome, EngineState.READY, CONFIG)
        assert decision.decision is Decision.DENY
        assert decision.sizing is None
        assert decision.constraints is None
        assert decision.direction is Direction.NONE
        assert decision.denied_reasons == outcome.denied_reasons

    def test_deny_engine_state_reflects_passed_in_state(self) -> None:
        opp = make_opportunity()
        outcome = PipelineOutcome(allowed=False, denied_reasons=(DeniedReason(code="SUSPENDED"),))
        decision = assembler.assemble_decision(opp, outcome, EngineState.SUSPENDED, CONFIG)
        assert decision.engine_state is EngineState.SUSPENDED

    def test_deny_populates_account_equity_when_portfolio_given(self) -> None:
        opp = make_opportunity()
        portfolio = make_portfolio(equity=12345.0)
        outcome = PipelineOutcome(allowed=False, denied_reasons=(DeniedReason(code="X"),))
        decision = assembler.assemble_decision(opp, outcome, EngineState.READY, CONFIG, portfolio_after=portfolio)
        assert decision.refs.account_equity == 12345.0


class TestAssembleDecisionAllow:
    def test_allow_carries_sizing_and_constraints(self) -> None:
        opp = make_opportunity()
        sizing = Sizing(method=SizingMethod.FIXED_FRACTIONAL, risk_per_trade_pct=0.005, risk_R=1.0, size_units=10.0, min_size=1.0, max_size=100.0)
        constraints = Constraints(entry=100.0, stop=99.0)
        outcome = PipelineOutcome(allowed=True, sizing=sizing, constraints=constraints)
        decision = assembler.assemble_decision(opp, outcome, EngineState.READY, CONFIG, portfolio_after=make_portfolio())
        assert decision.decision is Decision.ALLOW
        assert decision.sizing is sizing
        assert decision.constraints is constraints
        assert decision.direction == opp.direction

    def test_allow_engine_state_is_always_ready(self) -> None:
        opp = make_opportunity()
        sizing = Sizing(method=SizingMethod.FIXED_FRACTIONAL, risk_per_trade_pct=0.005, risk_R=1.0, size_units=10.0, min_size=1.0, max_size=100.0)
        outcome = PipelineOutcome(allowed=True, sizing=sizing, constraints=Constraints())
        decision = assembler.assemble_decision(opp, outcome, EngineState.READY, CONFIG, portfolio_after=make_portfolio())
        assert decision.engine_state is EngineState.READY

    def test_allow_portfolio_impact_reflects_running_view(self) -> None:
        opp = make_opportunity()
        sizing = Sizing(method=SizingMethod.FIXED_FRACTIONAL, risk_per_trade_pct=0.005, risk_R=1.0, size_units=10.0, min_size=1.0, max_size=100.0)
        outcome = PipelineOutcome(allowed=True, sizing=sizing, constraints=Constraints())
        portfolio = make_portfolio()
        decision = assembler.assemble_decision(opp, outcome, EngineState.READY, CONFIG, portfolio_after=portfolio)
        assert decision.portfolio_impact is not None
        assert decision.portfolio_impact.open_positions_after == len(portfolio.open_positions)


class TestAssembleInvalidDecision:
    def test_non_opportunity_object_uses_placeholders(self) -> None:
        decision = assembler.assemble_invalid_decision(object(), CONFIG)
        assert decision.strategy_id == "S0"
        assert decision.decision is Decision.DENY
        assert decision.denied_reasons[0].code == "INTERNAL_VALIDATION_FAILED"

    def test_real_opportunity_carries_its_own_identity(self) -> None:
        opp = make_opportunity(strategy_id="S7")
        decision = assembler.assemble_invalid_decision(opp, CONFIG, reason_code="SCHEMA_MISMATCH")
        assert decision.strategy_id == "S7"
        assert decision.denied_reasons[0].code == "SCHEMA_MISMATCH"
