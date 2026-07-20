"""Unit tests for :mod:`ai_trader.decision_comparison.falsification`."""

from __future__ import annotations

from ai_trader.decision_comparison.falsification import run_falsification_study
from ai_trader.decision_comparison.types import FalsificationVerdict
from ai_trader.decision_intelligence.types import DecisionReport
from ai_trader.decision_intelligence_v2.types import DecisionReportV2


def _v1(as_of: int, recommended: str | None) -> DecisionReport:
    return DecisionReport(symbol="XAUUSD", as_of=as_of, candidates=(), recommended_strategy_id=recommended, comparison_notes=())


def _v2(v1: DecisionReport) -> DecisionReportV2:
    return DecisionReportV2(v1_report=v1, candidates=(), recommended_strategy_id=v1.recommended_strategy_id)


def test_falsification_study_with_no_divergence_yields_v1_remains_active() -> None:
    pairs = [(_v1(1, "S1"), _v2(_v1(1, "S1"))), (_v1(2, None), _v2(_v1(2, None)))]
    report = run_falsification_study(pairs)
    assert report.verdict is FalsificationVerdict.V1_REMAINS_ACTIVE
    assert report.trade_outcome_equivalence.equivalence_holds is True
    assert "v1 remains" in report.rationale.lower()


def test_falsification_study_with_divergence_still_yields_v1_remains_active() -> None:
    v1 = _v1(1, "S1")
    v2 = DecisionReportV2(v1_report=v1, candidates=(), recommended_strategy_id="S1")
    object.__setattr__(v2, "recommended_strategy_id", "S2")
    report = run_falsification_study([(v1, v2)])
    assert report.verdict is FalsificationVerdict.V1_REMAINS_ACTIVE
    assert report.trade_outcome_equivalence.equivalence_holds is False
    assert "diverged" in report.rationale.lower()


def test_falsification_study_empty_input() -> None:
    report = run_falsification_study([])
    assert report.recommendation_comparison.n_compared == 0
    assert report.verdict is FalsificationVerdict.V1_REMAINS_ACTIVE
    assert report.calibration.n_samples == 0
