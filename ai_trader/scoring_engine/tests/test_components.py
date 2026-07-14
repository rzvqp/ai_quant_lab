"""Tests for :mod:`ai_trader.scoring_engine.components` — the eight per-signal component functions."""

from __future__ import annotations

from dataclasses import replace as dc_replace
from typing import Any

import pytest

from ai_trader.scoring_engine import components
from ai_trader.scoring_engine.config import ScoringConfig
from ai_trader.scoring_engine.evidence import BoundEvidence
from ai_trader.scoring_engine.tests.fixtures.fake_strategy_manager import make_signal
from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_manager.tests.fixtures.contracts import make_contract_dict
from ai_trader.strategy_manager.types import Lifecycle

CONFIG = ScoringConfig()


def _evidence(
    lifecycle: Lifecycle | None = Lifecycle.CANDIDATE,
    oos_expectancy_r: float | None = None,
    drawdown_r: float | None = None,
    top1_share: float | None = None,
    n: int | None = None,
    **contract_kwargs: Any,
) -> BoundEvidence:
    if lifecycle is None:
        return BoundEvidence(None, None)
    contract = parse_contract(make_contract_dict(**contract_kwargs))
    new_oos = dc_replace(contract.evidence.oos_metrics, expectancy_R=oos_expectancy_r)
    new_hist = dc_replace(
        contract.evidence.historical_metrics, drawdown_R=drawdown_r, top1_share=top1_share, n=n,
    )
    new_evidence = dc_replace(contract.evidence, oos_metrics=new_oos, historical_metrics=new_hist)
    contract = dc_replace(contract, evidence=new_evidence)
    return BoundEvidence(lifecycle=lifecycle, contract=contract)


class TestSignalStrength:
    def test_used_directly(self) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "strength": 0.73, "required_confirmations_met": True,
        })
        assert components.signal_strength(signal) == pytest.approx(0.73)

    def test_clamped_to_unit_range(self) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "strength": 1.0, "required_confirmations_met": True,
        })
        value = components.signal_strength(signal)
        assert 0.0 <= value <= 1.0


class TestHistoricalConfidence:
    def test_missing_evidence_is_zero_with_reason(self) -> None:
        value, reasons = components.historical_confidence(BoundEvidence(None, None))
        assert value == 0.0
        assert reasons[0].code == "EVIDENCE_MISSING"

    def test_zero_prior_lifecycle_is_zero(self) -> None:
        for lc in (Lifecycle.INVALID, Lifecycle.NOT_IMPLEMENTED, Lifecycle.RETIRED, Lifecycle.DISABLED):
            value, reasons = components.historical_confidence(_evidence(lifecycle=lc))
            assert value == 0.0
            assert reasons[0].code == "MATURITY_ZERO_PRIOR"

    def test_promoted_with_positive_oos_and_all_gates_pass_reaches_maturity_prior(self) -> None:
        evidence = _evidence(
            lifecycle=Lifecycle.PROMOTED, oos_expectancy_r=0.5, walk_forward_status="PASS",
            matched_null_status="PASS", global_fdr_status="PASS",
        )
        value, reasons = components.historical_confidence(evidence)
        # maturity_prior(1.0) * oos_factor(1.0) * (0.8+0.3)=1.1 -> capped at maturity_prior(1.0)
        assert value == pytest.approx(1.0)
        assert reasons == ()

    def test_negative_oos_caps_and_reports_reason(self) -> None:
        evidence = _evidence(lifecycle=Lifecycle.CANDIDATE, oos_expectancy_r=-0.2)
        value, reasons = components.historical_confidence(evidence)
        # maturity_prior(0.45) * oos_factor(0.4) * 0.8 = 0.144
        assert value == pytest.approx(0.45 * 0.4 * 0.8)
        assert reasons[0].code == "NEGATIVE_OOS_CAP"

    def test_null_oos_uses_the_neutral_06_factor(self) -> None:
        evidence = _evidence(lifecycle=Lifecycle.CANDIDATE, oos_expectancy_r=None)
        value, _ = components.historical_confidence(evidence)
        assert value == pytest.approx(0.45 * 0.6 * 0.8)

    def test_never_exceeds_its_own_maturity_prior_even_with_full_bonus(self) -> None:
        evidence = _evidence(
            lifecycle=Lifecycle.EXPLORATORY, oos_expectancy_r=10.0, walk_forward_status="PASS",
            matched_null_status="PASS", global_fdr_status="PASS",
        )
        value, _ = components.historical_confidence(evidence)
        assert value <= 0.30 + 1e-9


class TestMarketAlignment:
    def test_none_regime_is_neutral(self) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "required_confirmations_met": True, "regime": None,
        })
        assert components.market_alignment(signal) == 0.5

    def test_long_with_trend_up_is_aligned(self) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "required_confirmations_met": True, "regime": "TREND_UP",
        })
        assert components.market_alignment(signal) == 1.0

    def test_long_with_trend_down_is_against(self) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "required_confirmations_met": True, "regime": "TREND_DOWN",
        })
        assert components.market_alignment(signal) == 0.0

    def test_short_with_trend_down_is_aligned(self) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "SHORT", "required_confirmations_met": True, "regime": "TREND_DOWN",
        })
        assert components.market_alignment(signal) == 1.0

    def test_range_regime_is_neutral(self) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "required_confirmations_met": True, "regime": "RANGE",
        })
        assert components.market_alignment(signal) == 0.5


class TestRegimeAlignment:
    def test_none_regime_is_neutral(self) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "required_confirmations_met": True, "regime": None,
        })
        value, reasons = components.regime_alignment(signal, _evidence())
        assert value == 0.5 and reasons == ()

    def test_missing_evidence_is_neutral(self) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "required_confirmations_met": True, "regime": "TREND_UP",
        })
        value, reasons = components.regime_alignment(signal, BoundEvidence(None, None))
        assert value == 0.5 and reasons == ()

    def test_regime_in_applicable_matches(self) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "required_confirmations_met": True, "regime": "TREND_UP",
        })
        evidence = _evidence(market_regime_applicable=["TREND_UP"], market_regime_avoid=[])
        value, reasons = components.regime_alignment(signal, evidence)
        assert value == 1.0
        assert reasons[0].code == "REGIME_MATCH"

    def test_regime_in_avoid_scores_zero_even_if_any_is_applicable(self) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "required_confirmations_met": True, "regime": "TREND_UP",
        })
        evidence = _evidence(market_regime_applicable=["ANY"], market_regime_avoid=["TREND_UP"])
        value, reasons = components.regime_alignment(signal, evidence)
        assert value == 0.0
        assert reasons[0].code == "REGIME_AVOID"

    def test_any_applicable_is_neutral_not_a_match(self) -> None:
        """Regression guard: SCORING_MODEL.md §2 row 4 says "0.5 if ANY/unknown" -- a contract
        declaring applicable=(ANY,) is the model's own "ANY" case, not a specific regime match, so it
        must score neutral (0.5), never the full 1.0 match value."""
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "required_confirmations_met": True, "regime": "HIGH_VOL",
        })
        evidence = _evidence(market_regime_applicable=["ANY"], market_regime_avoid=[])
        value, reasons = components.regime_alignment(signal, evidence)
        assert value == 0.5
        assert reasons == ()

    def test_regime_neither_applicable_nor_avoid_is_neutral(self) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "required_confirmations_met": True, "regime": "HIGH_VOL",
        })
        evidence = _evidence(market_regime_applicable=["TREND_UP"], market_regime_avoid=["TREND_DOWN"])
        value, reasons = components.regime_alignment(signal, evidence)
        assert value == 0.5 and reasons == ()


class TestConfirmationQuality:
    def test_no_confirmations_required_is_full(self) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "required_confirmations_met": True,
        })
        value, _ = components.confirmation_quality(signal)
        assert value == 1.0

    def test_wait_confirmation_scales_by_ratio(self) -> None:
        signal = make_signal(
            required_data=[{"timeframe": "M15", "fields": ["m_atr"], "lookback_bars": 5, "htf": None}],
            generate_signal_response={
                "present": True, "direction": "LONG", "required_confirmations_met": False, "strength": 0.5,
            },
        )
        assert signal.state.value == "WAIT_CONFIRMATION"
        value, _ = components.confirmation_quality(signal)
        assert 0.0 <= value <= 1.0

    def test_fully_confirmed_buy_reports_reason(self) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "required_confirmations_met": True,
        })
        value, reasons = components.confirmation_quality(signal)
        assert value == 1.0
        assert any(r.code == "FULLY_CONFIRMED" for r in reasons)


class TestDataQualityComponent:
    def test_ok_is_one(self) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "required_confirmations_met": True,
        }, context_overrides={"data_quality": {"overall": "OK", "by_timeframe": {}}})
        value, reasons = components.data_quality_component(signal)
        assert value == 1.0 and reasons == ()

    @pytest.mark.parametrize("dq,expected", [("DEGRADED", 0.6), ("STALE", 0.3), ("INSUFFICIENT", 0.0)])
    def test_degraded_levels(self, dq: str, expected: float) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "required_confirmations_met": True,
        }, context_overrides={"data_quality": {"overall": dq, "by_timeframe": {}}})
        value, reasons = components.data_quality_component(signal)
        assert value == pytest.approx(expected)
        assert reasons[0].code == "DATA_DEGRADED"


class TestExecutionReadiness:
    def test_buy_with_full_trade_params_is_one(self) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "entry": 100.0, "stop": 99.0, "target": 102.0,
            "required_confirmations_met": True,
        })
        value, reasons = components.execution_readiness(signal)
        assert value == 1.0 and reasons == ()

    def test_buy_with_missing_stop_is_partial(self) -> None:
        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "entry": 100.0, "target": 102.0,
            "required_confirmations_met": True,
        })
        value, reasons = components.execution_readiness(signal)
        assert value == 0.6
        assert reasons[0].code == "PARTIAL_TRADE_PARAMS"

    def test_wait_confirmation_is_03(self) -> None:
        signal = make_signal(
            required_data=[{"timeframe": "M15", "fields": ["m_atr"], "lookback_bars": 5, "htf": None}],
            generate_signal_response={
                "present": True, "direction": "LONG", "required_confirmations_met": False, "strength": 0.5,
            },
        )
        value, _ = components.execution_readiness(signal)
        assert value == 0.3

    def test_no_signal_is_zero(self) -> None:
        signal = make_signal(detect_response={"setup_forming": False})
        value, reasons = components.execution_readiness(signal)
        assert value == 0.0 and reasons == ()

    def test_long_ready_is_06(self) -> None:
        """LONG_READY/SHORT_READY are documented, fully-implemented states the Signal Engine v1
        pipeline never actually produces (see its own module docstring) -- exercised here directly
        via a synthetic state override, since this component's own logic must still handle them
        correctly whenever a future Signal Engine MINOR starts emitting them."""
        from dataclasses import replace as dc_replace
        from ai_trader.signal_engine.types import SignalState

        signal = make_signal(generate_signal_response={
            "present": True, "direction": "LONG", "entry": 100.0, "stop": 99.0, "target": 102.0,
            "required_confirmations_met": True,
        })
        ready_signal = dc_replace(signal, state=SignalState.LONG_READY)
        value, reasons = components.execution_readiness(ready_signal)
        assert value == 0.6
        assert reasons == ()


class TestRiskPenalty:
    def test_missing_evidence_is_neutral_not_worst_case(self) -> None:
        """Regression guard: risk_penalty must NOT force 1.0 on a wholly-missing contract -- that
        would make penalty_factor collapse to zero and silently zero every evidence-missing score
        regardless of signal quality, double-punishing the same fact historical_confidence already
        penalizes."""
        value = components.risk_penalty(BoundEvidence(None, None), CONFIG)
        assert value == 0.5

    def test_clean_evidence_has_low_penalty(self) -> None:
        evidence = _evidence(drawdown_r=0.5, top1_share=0.1, n=500)
        value = components.risk_penalty(evidence, CONFIG)
        assert value < 0.2

    def test_large_drawdown_fragile_tiny_sample_is_maximal(self) -> None:
        evidence = _evidence(drawdown_r=50.0, top1_share=0.9, n=0)
        value = components.risk_penalty(evidence, CONFIG)
        assert value == pytest.approx(1.0)

    def test_missing_specific_fields_use_worst_case_per_field(self) -> None:
        evidence = _evidence(drawdown_r=None, top1_share=None, n=None)
        value = components.risk_penalty(evidence, CONFIG)
        assert value == pytest.approx(1.0)


class TestClamp:
    def test_clamps_below_and_above(self) -> None:
        assert components.clamp(-1.0, 0.0, 1.0) == 0.0
        assert components.clamp(2.0, 0.0, 1.0) == 1.0
        assert components.clamp(0.5, 0.0, 1.0) == 0.5
