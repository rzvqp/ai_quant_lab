"""Unit tests for :mod:`ai_trader.risk_manager.engine` -- ``RiskManager`` against controllable fake
opportunities/portfolio/context. Real-upstream integration lives in ``test_engine_integration.py``.
"""

from __future__ import annotations

import pytest

from ai_trader.risk_manager.config import PortfolioLimits, RiskConfig
from ai_trader.risk_manager.engine import RiskManager
from ai_trader.risk_manager.exceptions import EngineNotConfiguredError
from ai_trader.risk_manager.tests.fixtures.fake_opportunity import (
    make_below_floor_opportunity,
    make_opportunity,
    make_portfolio,
    make_risk_context,
)
from ai_trader.risk_manager.types import (
    ClosedPosition,
    Decision,
    EngineLifecycleState,
    EngineOverallHealth,
    EngineState,
    NotFound,
)


def _configured_manager() -> RiskManager:
    rm = RiskManager(RiskConfig())
    portfolio = make_portfolio()
    rm.configure(portfolio=portfolio)
    rm._config.filters.reference_spread["XAUUSD"] = 0.1
    rm._config.filters.liquidity_floor["XAUUSD"] = 100.0
    return rm


class TestConfigurationGate:
    def test_evaluate_before_configure_raises(self) -> None:
        rm = RiskManager()
        with pytest.raises(EngineNotConfiguredError):
            rm.evaluate([make_opportunity()], make_risk_context(), make_portfolio())

    def test_allow_trade_before_configure_raises(self) -> None:
        rm = RiskManager()
        with pytest.raises(EngineNotConfiguredError):
            rm.allow_trade(make_opportunity(), make_risk_context(), make_portfolio())

    def test_shutdown_before_configure_raises(self) -> None:
        rm = RiskManager()
        with pytest.raises(EngineNotConfiguredError):
            rm.shutdown()

    def test_health_before_configure_is_failed(self) -> None:
        rm = RiskManager()
        assert rm.health().overall is EngineOverallHealth.FAILED
        assert rm.health().state is EngineLifecycleState.IDLE


class TestConfigureLifecycle:
    def test_no_portfolio_starts_degraded(self) -> None:
        rm = RiskManager()
        rm.configure(portfolio=None)
        assert rm.health().overall is EngineOverallHealth.DEGRADED

    def test_clean_portfolio_starts_ready(self) -> None:
        rm = RiskManager()
        rm.configure(portfolio=make_portfolio())
        assert rm.health().state is EngineLifecycleState.READY
        assert rm.health().overall is EngineOverallHealth.OK

    def test_already_breached_portfolio_starts_suspended(self) -> None:
        rm = RiskManager()
        breached = make_portfolio(realized_pnl_pct_daily=-0.05)
        rm.configure(portfolio=breached)
        assert rm.health().state is EngineLifecycleState.SUSPENDED

    def test_configure_is_idempotent_and_resets_statistics(self) -> None:
        rm = _configured_manager()
        rm.allow_trade(make_opportunity(strength=0.95), make_risk_context(), rm._last_portfolio)
        rm.configure(portfolio=make_portfolio())
        assert rm.statistics().decisions_total == 0


class TestEvaluateBatch:
    def test_empty_batch_is_valid(self) -> None:
        rm = _configured_manager()
        batch = rm.evaluate([], make_risk_context(), make_portfolio())
        assert batch.decisions == ()

    def test_portfolio_none_denies_all_with_portfolio_unavailable(self) -> None:
        rm = _configured_manager()
        opp = make_opportunity(strength=0.95)
        batch = rm.evaluate([opp], make_risk_context(), None)
        assert batch.decisions[0].decision is Decision.DENY
        assert batch.decisions[0].denied_reasons[0].code == "PORTFOLIO_UNAVAILABLE"
        assert rm.health().overall is EngineOverallHealth.DEGRADED

    def test_stale_portfolio_denies_all(self) -> None:
        rm = _configured_manager()
        stale = make_portfolio(is_stale=True)
        opp = make_opportunity(strength=0.95)
        batch = rm.evaluate([opp], make_risk_context(), stale)
        assert batch.decisions[0].decision is Decision.DENY
        assert batch.decisions[0].denied_reasons[0].code == "PORTFOLIO_UNAVAILABLE"

    def test_clean_opportunity_is_allowed(self) -> None:
        rm = _configured_manager()
        portfolio = make_portfolio()
        opp = make_opportunity(strength=0.95)
        batch = rm.evaluate([opp], make_risk_context(), portfolio)
        assert batch.decisions[0].decision is Decision.ALLOW

    def test_processed_in_rank_order_regardless_of_input_order(self) -> None:
        rm = _configured_manager()
        portfolio = make_portfolio()
        opp1 = make_opportunity(strategy_id="S1", strength=0.95, rank=2)
        opp2 = make_opportunity(strategy_id="S2", strength=0.9, rank=1)
        batch = rm.evaluate([opp1, opp2], make_risk_context(), portfolio)
        assert [d.strategy_id for d in batch.decisions] == ["S2", "S1"]

    def test_running_portfolio_view_denies_later_opportunity_at_max_positions(self) -> None:
        config = RiskConfig(portfolio_limits=PortfolioLimits(max_positions=1))
        config.filters.reference_spread["XAUUSD"] = 0.1
        config.filters.liquidity_floor["XAUUSD"] = 100.0
        config.filters.reference_spread["EURUSD"] = 0.1
        config.filters.liquidity_floor["EURUSD"] = 100.0
        rm = RiskManager(config)
        portfolio = make_portfolio()
        rm.configure(portfolio=portfolio)
        opp1 = make_opportunity(strategy_id="S1", symbol="XAUUSD", strength=0.95, rank=1)
        opp2 = make_opportunity(strategy_id="S2", symbol="EURUSD", strength=0.9, rank=2)
        ctx = make_risk_context(symbol="XAUUSD")
        from dataclasses import replace
        ctx = replace(ctx, per_symbol={**ctx.per_symbol, **make_risk_context(symbol="EURUSD").per_symbol})
        batch = rm.evaluate([opp1, opp2], ctx, portfolio)
        assert batch.decisions[0].decision is Decision.ALLOW
        assert batch.decisions[1].decision is Decision.DENY
        assert batch.decisions[1].denied_reasons[0].code == "LIMIT_MAX_POSITIONS"

    def test_counts_by_decision(self) -> None:
        rm = _configured_manager()
        portfolio = make_portfolio()
        allowed = make_opportunity(strategy_id="S1", strength=0.95)
        denied = make_opportunity(strategy_id="S2", strength=0.02)
        batch = rm.evaluate([allowed, denied], make_risk_context(), portfolio)
        assert batch.counts_by_decision.get("ALLOW", 0) + batch.counts_by_decision.get("DENY", 0) == 2

    def test_a_signal_whose_own_bad_field_causes_schema_failure_is_reassembled_within_a_batch(self) -> None:
        """Regression guard mirroring the same class of fix made in Scoring Engine: a decision that
        fails RISK_SCHEMA.json validation (e.g. a strategy_id violating ^S\\d+$) must never be emitted
        as-is inside evaluate()'s own batch loop -- it is reassembled as a classified INVALID decision."""
        from dataclasses import replace

        rm = _configured_manager()
        portfolio = make_portfolio()
        broken = replace(make_opportunity(strength=0.95), strategy_id="NOT_VALID")
        batch = rm.evaluate([broken], make_risk_context(), portfolio)
        assert rm.validate(batch.decisions[0]).valid is True
        assert batch.decisions[0].denied_reasons[0].code == "INTERNAL_VALIDATION_FAILED"

    def test_loss_guard_escalation_denies_subsequent_opportunities_in_same_batch(self) -> None:
        rm = _configured_manager()
        portfolio = make_portfolio(realized_pnl_pct_daily=-0.05)  # already breached
        opp1 = make_opportunity(strategy_id="S1", strength=0.95, rank=1)
        opp2 = make_opportunity(strategy_id="S2", strength=0.9, rank=2)
        batch = rm.evaluate([opp1, opp2], make_risk_context(), portfolio)
        assert all(d.decision is Decision.DENY for d in batch.decisions)
        assert rm.health().state is EngineLifecycleState.SUSPENDED


class TestAllowTradeSingle:
    def test_returns_one_decision(self) -> None:
        rm = _configured_manager()
        decision = rm.allow_trade(make_opportunity(strength=0.95), make_risk_context(), make_portfolio())
        assert decision.decision in (Decision.ALLOW, Decision.DENY)

    def test_does_not_persist_running_view(self) -> None:
        rm = _configured_manager()
        portfolio = make_portfolio()
        rm.allow_trade(make_opportunity(strategy_id="S1", strength=0.95), make_risk_context(), portfolio)
        # a second identical single call against the SAME unmodified portfolio should behave identically
        decision2 = rm.allow_trade(make_opportunity(strategy_id="S1", strength=0.95), make_risk_context(), portfolio)
        assert decision2.decision is Decision.ALLOW

    def test_portfolio_none_denies_portfolio_unavailable(self) -> None:
        rm = _configured_manager()
        decision = rm.allow_trade(make_opportunity(), make_risk_context(), None)
        assert decision.decision is Decision.DENY
        assert decision.denied_reasons[0].code == "PORTFOLIO_UNAVAILABLE"


class TestPositionSize:
    def test_valid_opportunity_returns_sizing(self) -> None:
        rm = _configured_manager()
        result = rm.position_size(make_opportunity(strength=0.95), make_portfolio(), make_risk_context())
        assert result.valid is True
        assert result.sizing.size_units > 0

    def test_invalid_stop_returns_zero_sizing(self) -> None:
        rm = _configured_manager()
        from dataclasses import replace
        opp = replace(make_opportunity(), trade_context=None)
        result = rm.position_size(opp, make_portfolio(), make_risk_context())
        assert result.valid is False
        assert result.reason == "INVALID_STOP"


class TestPortfolioLimitsIntrospection:
    def test_reports_limits_and_utilization(self) -> None:
        rm = _configured_manager()
        report = rm.portfolio_limits(make_portfolio())
        assert "max_positions" in report.limits
        assert "open_positions" in report.current_utilization
        assert report.breaches == ()

    def test_reports_breaches(self) -> None:
        rm = _configured_manager()
        breached = make_portfolio(realized_pnl_pct_daily=-0.05)
        report = rm.portfolio_limits(breached)
        assert "LOSS_DAILY" in report.breaches

    def test_reports_every_breach_kind_simultaneously(self) -> None:
        from ai_trader.risk_manager.types import OpenPosition
        from ai_trader.signal_engine.types import Direction

        rm = _configured_manager()
        positions = tuple(
            OpenPosition(
                symbol=f"SYM{i}", strategy_id="S1", direction=Direction.LONG, size_units=1,
                entry_price=1, opened_bars_ago=1, risk_pct=0.06,
            )
            for i in range(5)
        )  # 5 positions (at LIMIT_MAX_POSITIONS) with combined risk 0.30 (at LIMIT_MAX_EXPOSURE)
        breached = make_portfolio(
            equity=100.0, equity_high_water_mark=113.7, gross_notional=300.0,  # leverage 3.0
            open_positions=positions, realized_pnl_pct_weekly=-0.06,
        )
        report = rm.portfolio_limits(breached)
        assert set(report.breaches) == {
            "LIMIT_MAX_POSITIONS", "LIMIT_MAX_EXPOSURE", "LIMIT_MAX_LEVERAGE", "LOSS_WEEKLY", "DRAWDOWN_MAX",
        }


class TestValidatePublicMethod:
    def test_delegates_to_the_validator_module(self) -> None:
        rm = _configured_manager()
        decision = rm.allow_trade(make_opportunity(strength=0.95), make_risk_context(), make_portfolio())
        result = rm.validate(decision)
        assert result.valid is True


class TestStatisticsHealthVersions:
    def test_statistics_track_batches_and_decisions(self) -> None:
        rm = _configured_manager()
        rm.evaluate([make_opportunity(strength=0.95)], make_risk_context(), make_portfolio())
        stats = rm.statistics()
        assert stats.batches == 1
        assert stats.decisions_total == 1

    def test_by_reason_tracks_deny_codes(self) -> None:
        rm = _configured_manager()
        rm.evaluate([make_below_floor_opportunity()], make_risk_context(), make_portfolio())
        stats = rm.statistics()
        assert stats.deny == 1
        assert sum(stats.by_reason.values()) >= 1

    def test_versions_reflect_config(self) -> None:
        rm = RiskManager(RiskConfig(risk_engine_version="9.9.9"))
        rm.configure(portfolio=make_portfolio())
        info = rm.versions()
        assert info.risk_engine_version == "9.9.9"
        assert info.supported_scoring_schema_major == 1


class TestOperationalControls:
    def test_suspend_sets_suspended(self) -> None:
        rm = _configured_manager()
        health = rm.suspend("operator halt")
        assert health.state is EngineLifecycleState.SUSPENDED

    def test_resume_guarded_stays_suspended_if_still_breached(self) -> None:
        rm = RiskManager()
        breached = make_portfolio(realized_pnl_pct_daily=-0.05)
        rm.configure(portfolio=breached)
        assert rm.health().state is EngineLifecycleState.SUSPENDED
        health = rm.resume()
        assert health.state is EngineLifecycleState.SUSPENDED

    def test_resume_succeeds_when_not_breached(self) -> None:
        rm = _configured_manager()
        rm.suspend("manual")
        health = rm.resume()
        assert health.state is EngineLifecycleState.READY

    def test_emergency_stop_sets_emergency(self) -> None:
        rm = _configured_manager()
        health = rm.emergency_stop("critical fault")
        assert health.state is EngineLifecycleState.EMERGENCY_STOP

    def test_kill_switch_denies_with_kill_switch_reason(self) -> None:
        rm = _configured_manager()
        rm.emergency_stop("operator kill switch", is_kill_switch=True)
        decision = rm.allow_trade(make_opportunity(strength=0.95), make_risk_context(), make_portfolio())
        assert decision.decision is Decision.DENY
        assert decision.denied_reasons[0].code == "KILL_SWITCH"

    def test_clear_emergency_guarded_stays_stopped_if_still_breached(self) -> None:
        rm = RiskManager()
        breached = make_portfolio(equity=88.0, equity_high_water_mark=100.0)
        rm.configure(portfolio=breached)
        rm.emergency_stop("kill switch", is_kill_switch=True)
        health = rm.clear_emergency()
        assert health.state is EngineLifecycleState.EMERGENCY_STOP

    def test_clear_emergency_succeeds_when_reconciled(self) -> None:
        rm = _configured_manager()
        rm.emergency_stop("kill switch", is_kill_switch=True)
        health = rm.clear_emergency()
        assert health.state is EngineLifecycleState.READY

    def test_every_evaluate_denies_while_emergency_stop(self) -> None:
        rm = _configured_manager()
        rm.emergency_stop("kill switch", is_kill_switch=True)
        batch = rm.evaluate([make_opportunity(strength=0.95)], make_risk_context(), make_portfolio())
        assert all(d.decision is Decision.DENY for d in batch.decisions)
        assert all(d.denied_reasons[0].code == "KILL_SWITCH" for d in batch.decisions)


class TestShutdown:
    def test_shutdown_reports_true_last_known_health(self) -> None:
        rm = _configured_manager()
        health = rm.shutdown()
        assert health.overall is EngineOverallHealth.OK

    def test_after_shutdown_engine_requires_reconfigure(self) -> None:
        rm = _configured_manager()
        rm.shutdown()
        with pytest.raises(EngineNotConfiguredError):
            rm.evaluate([], make_risk_context(), make_portfolio())

    def test_shutdown_releases_snapshots(self) -> None:
        rm = _configured_manager()
        rm.shutdown()
        rm.configure(portfolio=make_portfolio())
        assert rm._last_portfolio is not None  # freshly configured, not the old shutdown snapshot


class TestAdversarialReviewFixes:
    """Regression guards for each finding of the independent adversarial code review."""

    def test_a_malformed_opportunity_field_never_crashes_the_batch(self) -> None:
        """CRITICAL finding #1: a runtime-malformed field (``total_score=None``) used to raise a
        ``TypeError`` out of ``pipeline.evaluate_opportunity``'s ``>=`` comparison, crashing the whole
        ``evaluate()`` call. It must instead degrade to a classified ``DENY(INTERNAL_ERROR)`` for that
        ONE opportunity while every other opportunity in the same batch is still evaluated normally."""
        from dataclasses import replace

        rm = _configured_manager()
        portfolio = make_portfolio()
        broken = replace(make_opportunity(strategy_id="S1", strength=0.95), total_score=None)  # type: ignore[arg-type]
        healthy = make_opportunity(strategy_id="S2", strength=0.95, rank=2)
        batch = rm.evaluate([broken, healthy], make_risk_context(), portfolio)
        broken_decision = next(d for d in batch.decisions if d.strategy_id == "S1")
        healthy_decision = next(d for d in batch.decisions if d.strategy_id == "S2")
        assert broken_decision.decision is Decision.DENY
        assert broken_decision.denied_reasons[0].code == "INTERNAL_ERROR"
        assert rm.validate(broken_decision).valid is True
        assert healthy_decision.decision is Decision.ALLOW

    def test_a_malformed_opportunity_that_also_fails_reassembly_falls_back_to_the_placeholder(self) -> None:
        """CRITICAL finding #1, second-level fallback: if the exception-triggering opportunity's own
        identity fields (here, ``strategy_id``) are ALSO schema-invalid, the first reassembly attempt
        (which still copies those identity fields) is itself invalid -- falls back further to the
        fully placeholder-based decision, mirroring ``_finalize_decision``'s own double-fallback."""
        from dataclasses import replace

        rm = _configured_manager()
        portfolio = make_portfolio()
        broken = replace(
            make_opportunity(strength=0.95), total_score=None, strategy_id="NOT_VALID",  # type: ignore[arg-type]
        )
        batch = rm.evaluate([broken], make_risk_context(), portfolio)
        assert batch.decisions[0].decision is Decision.DENY
        assert batch.decisions[0].denied_reasons[0].code == "INTERNAL_ERROR"
        assert rm.validate(batch.decisions[0]).valid is True

    def test_portfolio_unavailable_decisions_are_schema_valid_even_for_a_malformed_opportunity(self) -> None:
        """CRITICAL finding #2: the PORTFOLIO_UNAVAILABLE branch used to call
        ``assembler.assemble_decision`` directly, bypassing ``_finalize_decision``'s validation/
        reassembly -- a decision built from a schema-invalid opportunity (bad ``strategy_id``) could
        be emitted unvalidated. It must now be routed through the same reassembly path as every other
        decision."""
        from dataclasses import replace

        rm = _configured_manager()
        broken = replace(make_opportunity(strength=0.95), strategy_id="NOT_VALID")
        batch = rm.evaluate([broken], make_risk_context(), None)
        assert rm.validate(batch.decisions[0]).valid is True
        assert batch.decisions[0].denied_reasons[0].code == "INTERNAL_VALIDATION_FAILED"

    def test_allow_trade_portfolio_impact_reflects_its_own_effect(self) -> None:
        """MEDIUM finding #4: ``allow_trade()``'s ``portfolio_impact`` for its own ALLOW previously
        reported the PRE-trade portfolio unchanged, instead of reflecting the position it just
        decided to allow -- inconsistent with what ``evaluate()`` reports for the identical
        opportunity."""
        rm = _configured_manager()
        portfolio = make_portfolio()  # 0 open positions
        decision = rm.allow_trade(make_opportunity(strength=0.95), make_risk_context(), portfolio)
        assert decision.decision is Decision.ALLOW
        assert decision.portfolio_impact is not None
        assert decision.portfolio_impact.open_positions_after == 1

    def test_health_recovers_after_a_fresh_portfolio_arrives(self) -> None:
        """MEDIUM finding #5: ``health()``'s DEGRADED status, once set by a stale/missing-portfolio
        ``evaluate()`` call, previously never cleared even after a later ``evaluate()`` call received
        a fresh, valid portfolio -- contradicting RISK_SEQUENCE.md §8's "recovers to normal ... once
        PortfolioState is fresh again." Only a full ``configure()`` used to reset it."""
        rm = _configured_manager()
        rm.evaluate([make_opportunity(strength=0.95)], make_risk_context(), None)
        assert rm.health().overall is EngineOverallHealth.DEGRADED
        rm.evaluate([make_opportunity(strength=0.95)], make_risk_context(), make_portfolio())
        assert rm.health().overall is EngineOverallHealth.OK

    def test_fallback_decision_engine_state_matches_actual_global_state_when_suspended(self) -> None:
        """LOW finding #7: ``assemble_invalid_decision()`` used to hardcode ``engine_state=READY``
        regardless of the actual global state at fallback time, producing an internally-inconsistent
        decision (individual decision says READY while the batch/engine says SUSPENDED)."""
        from dataclasses import replace

        rm = _configured_manager()
        rm.suspend("operator halt")
        broken = replace(make_opportunity(strength=0.95), strategy_id="NOT_VALID")
        batch = rm.evaluate([broken], make_risk_context(), make_portfolio())
        assert rm.validate(batch.decisions[0]).valid is True
        assert batch.decisions[0].engine_state is EngineState.SUSPENDED


class TestDeterminism:
    def test_evaluate_is_deterministic_across_calls(self) -> None:
        opp = make_opportunity(strength=0.95)
        portfolio = make_portfolio()
        rm1 = _configured_manager()
        rm2 = RiskManager(rm1._config)
        rm2.configure(portfolio=portfolio)
        d1 = rm1.evaluate([opp], make_risk_context(), portfolio)
        d2 = rm2.evaluate([opp], make_risk_context(), portfolio)
        assert d1.decisions == d2.decisions
