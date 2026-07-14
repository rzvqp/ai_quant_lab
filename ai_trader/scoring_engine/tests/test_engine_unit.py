"""Unit tests for :mod:`ai_trader.scoring_engine.engine` -- ``ScoringEngine`` against controllable
fake strategy signals/manager. Real-Strategy-Manager integration lives in
``test_engine_integration.py``.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from ai_trader.scoring_engine.config import ScoringConfig
from ai_trader.scoring_engine.engine import ScoringEngine
from ai_trader.scoring_engine.evidence import BoundEvidence
from ai_trader.scoring_engine.exceptions import EngineNotConfiguredError
from ai_trader.scoring_engine.tests.fixtures.fake_strategy_manager import FakeStrategyManager, make_signal
from ai_trader.scoring_engine.types import (
    EngineLifecycleState,
    EngineOverallHealth,
    NotFound,
    Quality,
    Recommendation,
)
from ai_trader.signal_engine.types import StrategySignal
from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_manager.tests.fixtures.contracts import make_contract_dict
from ai_trader.strategy_manager.types import Lifecycle


def _buy(strategy_id: str = "S1", strength: float = 0.8) -> StrategySignal:
    return make_signal(strategy_id=strategy_id, generate_signal_response={
        "present": True, "direction": "LONG", "entry": 100.0, "stop": 99.0, "target": 102.0,
        "strength": strength, "required_confirmations_met": True, "regime": "TREND_UP",
    })


class TestConfigurationGate:
    def test_score_signal_before_configure_raises(self) -> None:
        engine = ScoringEngine()
        with pytest.raises(EngineNotConfiguredError):
            engine.score_signal(_buy())

    def test_score_batch_before_configure_raises(self) -> None:
        engine = ScoringEngine()
        with pytest.raises(EngineNotConfiguredError):
            engine.score_batch([_buy()])

    def test_shutdown_before_configure_raises(self) -> None:
        engine = ScoringEngine()
        with pytest.raises(EngineNotConfiguredError):
            engine.shutdown()

    def test_health_before_configure_is_failed(self) -> None:
        engine = ScoringEngine()
        assert engine.health().overall is EngineOverallHealth.FAILED
        assert engine.health().state is EngineLifecycleState.UNINITIALIZED


class TestConfigureLifecycle:
    def test_no_manager_starts_degraded(self) -> None:
        engine = ScoringEngine()
        engine.configure(manager=None)
        assert engine.health().overall is EngineOverallHealth.DEGRADED
        assert engine.health().state is EngineLifecycleState.DEGRADED

    def test_with_manager_starts_ready(self) -> None:
        engine = ScoringEngine()
        engine.configure(manager=FakeStrategyManager())
        assert engine.health().overall is EngineOverallHealth.OK
        assert engine.health().state is EngineLifecycleState.READY

    def test_configure_is_idempotent_and_resets_statistics(self) -> None:
        engine = ScoringEngine()
        engine.configure(manager=FakeStrategyManager())
        engine.score_signal(_buy())
        engine.configure(manager=FakeStrategyManager())
        assert engine.statistics().scores_total == 0


class TestScoreSignal:
    def test_returns_one_score_for_the_input_signal(self) -> None:
        engine = ScoringEngine()
        engine.configure(manager=FakeStrategyManager())
        score = engine.score_signal(_buy("S9"))
        assert score.strategy_id == "S9"
        assert score.rank == 1

    def test_lone_call_gets_zero_conflict_and_no_batch_context_reason(self) -> None:
        engine = ScoringEngine()
        engine.configure(manager=FakeStrategyManager())
        score = engine.score_signal(_buy())
        assert score.component_scores.conflict_penalty == 0.0
        assert any(r.code == "NO_BATCH_CONTEXT" for r in score.reason_codes)

    def test_skipped_signal_has_no_no_batch_context_reason(self) -> None:
        engine = ScoringEngine()
        engine.configure(manager=FakeStrategyManager())
        signal = make_signal(detect_response={"setup_forming": False})
        score = engine.score_signal(signal)
        assert score.recommendation is Recommendation.SKIP
        assert not any(r.code == "NO_BATCH_CONTEXT" for r in score.reason_codes)

    def test_evidence_override_bypasses_the_manager(self) -> None:
        engine = ScoringEngine()
        mgr = FakeStrategyManager()
        engine.configure(manager=mgr)
        contract = parse_contract(make_contract_dict(id="S1"))
        override = BoundEvidence(lifecycle=Lifecycle.PROMOTED, contract=contract)
        score = engine.score_signal(_buy("S1"), evidence=override)
        assert score.confidence is not None
        assert "find_strategy:S1" not in mgr.calls

    def test_malformed_input_never_raises(self) -> None:
        engine = ScoringEngine()
        engine.configure(manager=FakeStrategyManager())
        score = engine.score_signal(object())  # type: ignore[arg-type]
        assert score.recommendation is Recommendation.INVALID

    def test_a_signal_whose_own_bad_field_causes_the_schema_failure_still_emits_a_valid_score(self) -> None:
        """Regression guard: the reassembly fallback used to copy identity fields (strategy_version,
        etc.) straight from the SAME signal that caused the original schema failure -- if that field
        was itself the problem, the "fixed" score could still be schema-invalid and would be emitted
        anyway since nothing re-checked it. A signal with a malformed strategy_version (violating
        SCORING_SCHEMA.json's ^\\d+\\.\\d+\\.\\d+$ pattern) must still produce a genuinely valid,
        schema-conformant emitted score."""
        engine = ScoringEngine()
        engine.configure(manager=FakeStrategyManager())
        broken_signal = replace(_buy("S1"), strategy_version="not-a-version")
        score = engine.score_signal(broken_signal)
        assert engine.validate(score).valid is True
        assert score.recommendation is Recommendation.INVALID


class TestScoreBatch:
    def test_empty_batch_is_valid(self) -> None:
        engine = ScoringEngine()
        engine.configure(manager=FakeStrategyManager())
        batch = engine.score_batch([])
        assert batch.scores == ()
        assert batch.symbol is None

    def test_batch_ranks_scores_by_total_score(self) -> None:
        engine = ScoringEngine()
        engine.configure(manager=FakeStrategyManager())
        strong = _buy("S1", strength=0.95)
        weak = _buy("S2", strength=0.1)
        batch = engine.score_batch([strong, weak])
        assert batch.scores[0].strategy_id == "S1"
        assert batch.scores[0].rank == 1
        assert batch.scores[1].rank == 2

    def test_symbol_and_as_of_reflect_the_common_group(self) -> None:
        engine = ScoringEngine()
        engine.configure(manager=FakeStrategyManager())
        s1, s2 = _buy("S1"), _buy("S2")
        batch = engine.score_batch([s1, s2])
        assert batch.symbol == "XAUUSD"
        assert batch.as_of == s1.as_of

    def test_isolation_one_malformed_does_not_affect_others(self) -> None:
        engine = ScoringEngine()
        engine.configure(manager=FakeStrategyManager())
        batch = engine.score_batch([object(), _buy("S1")])  # type: ignore[list-item]
        by_id = {s.strategy_id: s for s in batch.scores}
        assert by_id["S0"].recommendation is Recommendation.INVALID
        assert by_id["S1"].recommendation in (
            Recommendation.STRONG_OPPORTUNITY, Recommendation.MODERATE_OPPORTUNITY,
            Recommendation.WEAK_OPPORTUNITY, Recommendation.SKIP,
        )

    def test_counts_by_recommendation(self) -> None:
        engine = ScoringEngine()
        engine.configure(manager=FakeStrategyManager())
        skipped = make_signal(strategy_id="S2", detect_response={"setup_forming": False})
        batch = engine.score_batch([_buy("S1"), skipped])
        assert batch.counts_by_recommendation.get("SKIP") == 1


class TestExplainScore:
    def test_finds_a_score_produced_this_cycle(self) -> None:
        engine = ScoringEngine()
        engine.configure(manager=FakeStrategyManager())
        score = engine.score_signal(_buy("S1"))
        explanation = engine.explain_score(score.score_id)
        assert not isinstance(explanation, NotFound)
        assert explanation.score_id == score.score_id
        assert explanation.model_version == score.scoring_model_version

    def test_not_found_for_unknown_score_id(self) -> None:
        engine = ScoringEngine()
        engine.configure(manager=FakeStrategyManager())
        assert isinstance(engine.explain_score("nonexistent"), NotFound)


class TestValidatePublicMethod:
    def test_delegates_to_the_validator_module(self) -> None:
        engine = ScoringEngine()
        engine.configure(manager=FakeStrategyManager())
        score = engine.score_signal(_buy())
        result = engine.validate(score)
        assert result.valid is True

    def test_detects_a_broken_score(self) -> None:
        engine = ScoringEngine()
        engine.configure(manager=FakeStrategyManager())
        score = engine.score_signal(_buy())
        broken = replace(score, total_score=999)
        assert engine.validate(broken).valid is False


class TestStatisticsHealthVersions:
    def test_statistics_track_batches_and_scores(self) -> None:
        engine = ScoringEngine()
        engine.configure(manager=FakeStrategyManager())
        engine.score_batch([_buy("S1"), _buy("S2")])
        stats = engine.statistics()
        assert stats.batches == 1
        assert stats.scores_total == 2

    def test_avg_score_reflects_total_scores(self) -> None:
        engine = ScoringEngine()
        engine.configure(manager=FakeStrategyManager())
        engine.score_signal(_buy())
        assert engine.statistics().avg_score >= 0.0

    def test_by_quality_tracks_bands(self) -> None:
        engine = ScoringEngine()
        engine.configure(manager=FakeStrategyManager())
        score = engine.score_signal(_buy())
        stats = engine.statistics()
        assert stats.by_quality[score.quality.value] >= 1

    def test_versions_reflect_config(self) -> None:
        engine = ScoringEngine(ScoringConfig(scoring_engine_version="9.9.9"))
        engine.configure(manager=FakeStrategyManager())
        info = engine.versions()
        assert info.scoring_engine_version == "9.9.9"
        assert info.supported_signal_schema_major == 1


class TestShutdown:
    def test_shutdown_reports_true_last_known_health(self) -> None:
        engine = ScoringEngine()
        engine.configure(manager=FakeStrategyManager())
        engine.score_signal(_buy())
        health = engine.shutdown()
        assert health.overall is EngineOverallHealth.OK

    def test_after_shutdown_engine_requires_reconfigure(self) -> None:
        engine = ScoringEngine()
        engine.configure(manager=FakeStrategyManager())
        engine.shutdown()
        with pytest.raises(EngineNotConfiguredError):
            engine.score_batch([])

    def test_shutdown_releases_the_score_cache(self) -> None:
        engine = ScoringEngine()
        engine.configure(manager=FakeStrategyManager())
        score = engine.score_signal(_buy("S1"))
        engine.shutdown()
        engine.configure(manager=FakeStrategyManager())
        assert isinstance(engine.explain_score(score.score_id), NotFound)


class TestDeterminism:
    def test_score_signal_is_deterministic_across_calls(self) -> None:
        engine = ScoringEngine()
        engine.configure(manager=FakeStrategyManager())
        signal = _buy("S1")
        first = engine.score_signal(signal)
        second = engine.score_signal(signal)
        assert first == second

    def test_fresh_engine_same_config_reproduces_the_same_score(self) -> None:
        signal = _buy("S1")
        e1 = ScoringEngine()
        e1.configure(manager=FakeStrategyManager())
        s1 = e1.score_signal(signal)
        e2 = ScoringEngine()
        e2.configure(manager=FakeStrategyManager())
        s2 = e2.score_signal(signal)
        assert s1 == s2
