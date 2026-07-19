"""Unit tests for :mod:`ai_trader.decision_intelligence.engine` -- the public
``make_decision()``/``recommended_or_no_trade()`` entry points. Uses a synthetic Strategy Library
(``tmp_path``) containing only REAL, currently-registered strategy ids (S1, S7, S12), matching the same
pattern ``ai_trader/edge_intelligence/tests/test_engine.py`` established. Real-data integration coverage
against the actual Strategy Library lives in
``ai_trader/decision_intelligence/tests/test_integration.py``.
"""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.decision_intelligence.engine import NO_TRADE, make_decision, recommended_or_no_trade
from ai_trader.decision_intelligence.types import DecisionOutcome, ResearchStats
from ai_trader.market_intelligence.tests._fixtures import make_bar, make_context
from ai_trader.strategy_manager.tests.fixtures.contracts import make_contract_dict

_M15_BARS = [make_bar(1_700_000_000, 2000, 2001, 1999, 2000.5)]

_STRONG_UP_CONTEXT = make_context(
    m15_bars=_M15_BARS,
    m15_features={
        "m_trend_up": True, "h1_trend_up": True, "h4_trend_up": True, "d1_trend_up": True,
        "m_atr": 1.0, "atr_ma": 1.0,
    },
)


def _write_strategy(tmp_path: Path, folder: str, data: dict) -> None:
    strategy_dir = tmp_path / folder
    strategy_dir.mkdir()
    (strategy_dir / "strategy.json").write_text(json.dumps(data), encoding="utf-8")


def _library(tmp_path: Path) -> Path:
    # S1: PRESENT (BOTH, all sessions), high-maturity/high-confidence -> ACCEPT, top-ranked.
    s1 = make_contract_dict(id="S1", maturity="PROMOTED")
    s1["execution"]["long_short"] = "BOTH"
    s1["execution"]["sessions"] = "All sessions"
    s1["evidence"]["confidence"]["level"] = "HIGH"
    _write_strategy(tmp_path, "S1_test", s1)

    # S12: PRESENT (BOTH, all sessions), lower maturity/confidence -> ACCEPT, ranked below S1.
    s12 = make_contract_dict(id="S12", maturity="VALIDATED")
    s12["execution"]["long_short"] = "BOTH"
    s12["execution"]["sessions"] = "All sessions"
    s12["evidence"]["confidence"]["level"] = "MEDIUM"
    _write_strategy(tmp_path, "S12_test", s12)

    # S7: SHORT while the shared context trends UP -> directional CONTRADICTS -> ABSENT, never a candidate.
    s7 = make_contract_dict(id="S7")
    s7["execution"]["long_short"] = "SHORT"
    s7["execution"]["sessions"] = "All sessions"
    _write_strategy(tmp_path, "S7_test", s7)
    return tmp_path


def test_recommends_the_top_ranked_present_and_accepted_candidate(tmp_path: Path) -> None:
    report = make_decision(_STRONG_UP_CONTEXT, library_path=_library(tmp_path))
    assert {c.strategy_id for c in report.candidates} == {"S1", "S12"}  # S7 is ABSENT, never a candidate
    assert all(c.outcome is DecisionOutcome.ACCEPT for c in report.candidates)
    assert report.recommended_strategy_id == "S1"
    assert recommended_or_no_trade(report) == "S1"
    assert len(report.comparison_notes) == 1
    assert "S1 outranks S12" in report.comparison_notes[0]


def test_no_trade_when_every_present_candidate_is_rejected(tmp_path: Path) -> None:
    library_path = tmp_path
    s1 = make_contract_dict(id="S1", maturity="RETIRED")
    s1["execution"]["long_short"] = "BOTH"
    s1["execution"]["sessions"] = "All sessions"
    _write_strategy(library_path, "S1_test", s1)

    report = make_decision(_STRONG_UP_CONTEXT, library_path=library_path)
    assert len(report.candidates) == 1
    assert report.candidates[0].outcome is DecisionOutcome.REJECT
    assert report.recommended_strategy_id is None
    assert recommended_or_no_trade(report) == NO_TRADE
    assert report.comparison_notes == ()


def test_no_trade_when_zero_edges_are_present(tmp_path: Path) -> None:
    # Every strategy declares SHORT while the shared context trends UP -> every one is ABSENT.
    s1 = make_contract_dict(id="S1")
    s1["execution"]["long_short"] = "SHORT"
    s1["execution"]["sessions"] = "All sessions"
    _write_strategy(tmp_path, "S1_test", s1)

    report = make_decision(_STRONG_UP_CONTEXT, library_path=tmp_path)
    assert report.candidates == ()
    assert report.recommended_strategy_id is None
    assert recommended_or_no_trade(report) == NO_TRADE


def test_research_stats_are_used_when_supplied(tmp_path: Path) -> None:
    library_path = _library(tmp_path)
    research_stats = {
        "S1": ResearchStats(n_trades=10, win_rate=0.3, expectancy_r=-0.2, sharpe_ratio=-0.5),
        "S12": ResearchStats(n_trades=10, win_rate=0.6, expectancy_r=0.3, sharpe_ratio=1.2),
    }
    report = make_decision(_STRONG_UP_CONTEXT, research_stats=research_stats, library_path=library_path)
    ids_by_outcome = {c.strategy_id: c.outcome for c in report.candidates}
    assert ids_by_outcome["S1"] is DecisionOutcome.REJECT  # negative expectancy_r
    assert ids_by_outcome["S12"] is DecisionOutcome.ACCEPT
    assert report.recommended_strategy_id == "S12"


def test_is_deterministic(tmp_path: Path) -> None:
    library_path = _library(tmp_path)
    first = make_decision(_STRONG_UP_CONTEXT, library_path=library_path)
    second = make_decision(_STRONG_UP_CONTEXT, library_path=library_path)
    assert first == second
