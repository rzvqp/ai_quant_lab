"""Tests for :mod:`ai_trader.risk_manager.pipeline` -- the fixed per-opportunity evaluation order."""

from __future__ import annotations

from dataclasses import replace

from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.pipeline import evaluate_opportunity
from ai_trader.risk_manager.tests.fixtures.fake_opportunity import (
    make_below_floor_opportunity,
    make_opportunity,
    make_portfolio,
    make_risk_context,
)
from ai_trader.risk_manager.types import ClosedPosition, EngineState, OpenPosition
from ai_trader.signal_engine.types import Direction

CONFIG = RiskConfig()
CONTEXT = make_risk_context()


def _configured() -> RiskConfig:
    config = RiskConfig()
    config.filters.reference_spread["XAUUSD"] = 0.1
    config.filters.liquidity_floor["XAUUSD"] = 100.0
    return config


class TestGlobalStateGate:
    def test_suspended_denies_immediately(self) -> None:
        opp = make_opportunity()
        outcome = evaluate_opportunity(
            opp, CONTEXT, make_portfolio(), _configured(), EngineState.SUSPENDED, "LOSS_DAILY",
        )
        assert outcome.allowed is False
        assert outcome.denied_reasons[0].code == "LOSS_DAILY"
        assert outcome.applied_rules == (outcome.applied_rules[0],)  # only the global-state rule ran

    def test_emergency_stop_denies_immediately(self) -> None:
        opp = make_opportunity()
        outcome = evaluate_opportunity(
            opp, CONTEXT, make_portfolio(), _configured(), EngineState.EMERGENCY_STOP, "KILL_SWITCH",
        )
        assert outcome.allowed is False
        assert outcome.denied_reasons[0].code == "KILL_SWITCH"

    def test_ready_proceeds_past_global_gate(self) -> None:
        opp = make_opportunity()
        outcome = evaluate_opportunity(
            opp, CONTEXT, make_portfolio(), _configured(), EngineState.READY, "READY",
        )
        assert len(outcome.applied_rules) > 1


class TestOpportunitySanity:
    def test_non_actionable_state_denies_not_actionable(self) -> None:
        from ai_trader.risk_manager.tests.fixtures.fake_opportunity import make_signal
        from ai_trader.scoring_engine.config import ScoringConfig
        from ai_trader.scoring_engine.engine import ScoringEngine

        signal = make_signal(detect_response={"setup_forming": False})
        sc = ScoringEngine(ScoringConfig())
        sc.configure(manager=None)
        opp = sc.score_signal(signal)
        outcome = evaluate_opportunity(opp, CONTEXT, make_portfolio(), _configured(), EngineState.READY, "READY")
        assert outcome.allowed is False
        assert outcome.denied_reasons[0].code == "NOT_ACTIONABLE"

    def test_wrong_side_stop_denies_invalid_input(self) -> None:
        opp = make_opportunity(direction="LONG", entry=100.0, stop=101.0)  # stop above entry for LONG
        outcome = evaluate_opportunity(opp, CONTEXT, make_portfolio(), _configured(), EngineState.READY, "READY")
        assert outcome.allowed is False
        assert outcome.denied_reasons[0].code == "INVALID_INPUT"

    def test_valid_long_stop_below_entry_passes_sanity(self) -> None:
        opp = make_opportunity(direction="LONG", entry=100.0, stop=99.0, strength=0.95)
        outcome = evaluate_opportunity(opp, CONTEXT, make_portfolio(), _configured(), EngineState.READY, "READY")
        rule_names = [r.rule for r in outcome.applied_rules]
        assert "OPPORTUNITY_SANITY_TRADE_CONTEXT" in rule_names

    def test_valid_short_stop_above_entry_passes_sanity(self) -> None:
        opp = make_opportunity(direction="SHORT", entry=100.0, stop=101.0, target=98.0, strength=0.95)
        outcome = evaluate_opportunity(opp, CONTEXT, make_portfolio(), _configured(), EngineState.READY, "READY")
        rule_names = [r.rule for r in outcome.applied_rules]
        assert "OPPORTUNITY_SANITY_TRADE_CONTEXT" in rule_names


class TestRecommendationFloor:
    def test_low_score_denies_below_floor_or_score_too_low(self) -> None:
        opp = make_below_floor_opportunity()
        outcome = evaluate_opportunity(opp, CONTEXT, make_portfolio(), _configured(), EngineState.READY, "READY")
        assert outcome.allowed is False
        assert outcome.denied_reasons[0].code in ("BELOW_FLOOR", "SCORE_TOO_LOW")

    def test_strong_score_passes_floor(self) -> None:
        opp = make_opportunity(strength=0.95)
        outcome = evaluate_opportunity(opp, CONTEXT, make_portfolio(), _configured(), EngineState.READY, "READY")
        rule_names = [r.rule for r in outcome.applied_rules]
        assert "RECOMMENDATION_FLOOR" in rule_names

    def test_score_too_low_is_reachable_independently_of_below_floor(self) -> None:
        """A recommendation that DOES pass the floor but a total_score that still fails MIN_SCORE --
        exercises SCORE_TOO_LOW distinctly from BELOW_FLOOR (the two gates are independent checks)."""
        from dataclasses import replace

        from ai_trader.scoring_engine.types import Recommendation

        opp = replace(make_opportunity(strength=0.95), total_score=10, recommendation=Recommendation.WEAK_OPPORTUNITY)
        outcome = evaluate_opportunity(opp, CONTEXT, make_portfolio(), _configured(), EngineState.READY, "READY")
        assert outcome.allowed is False
        assert outcome.denied_reasons[0].code == "SCORE_TOO_LOW"
        floor_result = next(r for r in outcome.applied_rules if r.rule == "RECOMMENDATION_FLOOR")
        assert floor_result.passed is True


class TestPreTradeFilters:
    def test_stale_data_denies(self) -> None:
        """Data-quality runs LAST among the pre-trade filters (RISK_POLICY.md §5's table order), so
        every symbol-level field must be otherwise clean for DATA_DEGRADED specifically to surface as
        the first failure."""
        from ai_trader.market_scanner.types import DataQualityLevel
        from ai_trader.risk_manager.types import RiskContext, SymbolRiskSnapshot

        opp = make_opportunity(strength=0.95)
        ctx = RiskContext(as_of=1, per_symbol={"XAUUSD": SymbolRiskSnapshot(
            atr=1.0, atr_rolling_median=1.0, current_spread=0.2, liquidity_proxy=1000.0,
            data_quality=DataQualityLevel.STALE,
        )})
        outcome = evaluate_opportunity(opp, ctx, make_portfolio(), _configured(), EngineState.READY, "READY")
        assert outcome.allowed is False
        assert outcome.denied_reasons[0].code == "DATA_DEGRADED"

    def test_clean_context_passes_filters(self) -> None:
        opp = make_opportunity(strength=0.95)
        outcome = evaluate_opportunity(opp, CONTEXT, make_portfolio(), _configured(), EngineState.READY, "READY")
        rule_names = [r.rule for r in outcome.applied_rules]
        assert "FILTER_VOLATILITY" in rule_names


class TestPortfolioLimits:
    def test_full_portfolio_denies_limit_max_positions(self) -> None:
        opp = make_opportunity(strength=0.95, symbol="XAUUSD")
        positions = tuple(
            OpenPosition(symbol=f"SYM{i}", strategy_id="S1", direction=Direction.LONG, size_units=1,
                         entry_price=1, opened_bars_ago=1, risk_pct=0.01)
            for i in range(5)
        )
        portfolio = make_portfolio(open_positions=positions)
        outcome = evaluate_opportunity(opp, CONTEXT, portfolio, _configured(), EngineState.READY, "READY")
        assert outcome.allowed is False
        assert outcome.denied_reasons[0].code == "LIMIT_MAX_POSITIONS"


class TestLossDrawdownGuards:
    def test_daily_loss_denies_and_escalates(self) -> None:
        opp = make_opportunity(strength=0.95)
        portfolio = make_portfolio(realized_pnl_pct_daily=-0.05)
        outcome = evaluate_opportunity(opp, CONTEXT, portfolio, _configured(), EngineState.READY, "READY")
        assert outcome.allowed is False
        assert outcome.denied_reasons[0].code == "LOSS_DAILY"
        assert outcome.escalate_to is EngineState.SUSPENDED


class TestCooldowns:
    def test_recent_loss_on_symbol_denies(self) -> None:
        opp = make_opportunity(strength=0.95, symbol="XAUUSD")
        closed = (ClosedPosition(symbol="XAUUSD", strategy_id="S1", was_loss=True, bars_since_close=1),)
        portfolio = make_portfolio(recent_closed_positions=closed)
        outcome = evaluate_opportunity(opp, CONTEXT, portfolio, _configured(), EngineState.READY, "READY")
        assert outcome.allowed is False
        assert outcome.denied_reasons[0].code == "COOLDOWN_AFTER_LOSS"


class TestFullAllowPath:
    def test_clean_opportunity_is_allowed_with_sizing_and_constraints(self) -> None:
        opp = make_opportunity(strength=0.95)
        outcome = evaluate_opportunity(opp, CONTEXT, make_portfolio(), _configured(), EngineState.READY, "READY")
        assert outcome.allowed is True
        assert outcome.sizing is not None
        assert outcome.constraints is not None
        assert outcome.denied_reasons == ()

    def test_size_below_min_denies_after_all_gates_passed(self) -> None:
        """The exposure budget is nearly exhausted -> the remaining risk budget for this trade is
        below min_allocation_risk_pct -> SIZE_BELOW_MIN at the sizing stage (7), after every policy
        gate (0-6) already passed."""
        opp = make_opportunity(strength=0.95)
        almost_full = OpenPosition(
            symbol="OTHER", strategy_id="S9", direction=Direction.LONG, size_units=1, entry_price=1,
            opened_bars_ago=1, risk_pct=_configured().portfolio_limits.max_exposure_pct - 0.0001,
        )
        portfolio = make_portfolio(open_positions=(almost_full,))
        outcome = evaluate_opportunity(opp, CONTEXT, portfolio, _configured(), EngineState.READY, "READY")
        assert outcome.allowed is False
        assert outcome.denied_reasons[0].code == "SIZE_BELOW_MIN"
        rule_names = [r.rule for r in outcome.applied_rules]
        assert "POSITION_SIZING" in rule_names

    def test_applied_rules_records_every_rule_up_to_and_including_the_failure(self) -> None:
        opp = make_below_floor_opportunity()  # fails at recommendation floor
        outcome = evaluate_opportunity(opp, CONTEXT, make_portfolio(), _configured(), EngineState.READY, "READY")
        rule_names = [r.rule for r in outcome.applied_rules]
        # never reached later stages
        assert "FILTER_VOLATILITY" not in rule_names
        assert "LIMIT_MAX_POSITIONS" not in rule_names


class TestDeterminism:
    def test_identical_inputs_produce_identical_outcome(self) -> None:
        opp = make_opportunity(strength=0.95)
        portfolio = make_portfolio()
        first = evaluate_opportunity(opp, CONTEXT, portfolio, _configured(), EngineState.READY, "READY")
        second = evaluate_opportunity(opp, CONTEXT, portfolio, _configured(), EngineState.READY, "READY")
        assert first == second
