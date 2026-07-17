"""Unit tests for :class:`~ai_trader.shadow_evidence.engine.ShadowEvidenceEngine` -- Phase 6.10
Implementation Checkpoint 1B. Fast, isolated tests using this project's own established fixture
convention (``scoring_engine.tests.fixtures.fake_strategy_manager.make_signal`` + the real
``score_signal_stage1``/``assembler`` pipeline, same technique ``scoring_engine/tests/test_validator.
py::_score()`` already uses) to build genuine, schema-valid ``OpportunityScore`` objects -- not
hand-rolled approximations. Complements the slower, full-harness integration tests in
``ai_trader/simulation/tests/test_shadow_disabled_parity.py``.
"""

from __future__ import annotations

from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.types import RiskContext
from ai_trader.scoring_engine import assembler
from ai_trader.scoring_engine.conflict import ConflictResult
from ai_trader.scoring_engine.config import ScoringConfig
from ai_trader.scoring_engine.pipeline import score_signal_stage1
from ai_trader.scoring_engine.tests.fixtures.fake_strategy_manager import make_signal
from ai_trader.scoring_engine.types import OpportunityScore, ScoreBatch
from ai_trader.shadow_evidence.engine import ShadowEvidenceEngine

CONFIG = ScoringConfig()
AS_OF = 1_700_000_000


def _score(strategy_id: str = "S10", **generate_kwargs: object) -> OpportunityScore:
    defaults: dict[str, object] = {
        "present": True, "direction": "LONG", "entry": 2000.0, "stop": 1990.0, "target": 2020.0,
        "strength": 0.8, "required_confirmations_met": True,
    }
    defaults.update(generate_kwargs)
    signal = make_signal(strategy_id=strategy_id, generate_signal_response=defaults)
    partial = score_signal_stage1(signal, None, {}, CONFIG)
    return assembler.assemble_score(partial, ConflictResult(0.0, ()), CONFIG)


def _batch(*scores: OpportunityScore) -> ScoreBatch:
    return ScoreBatch(
        as_of=AS_OF, symbol="XAUUSD", scores=tuple(scores),
        counts_by_recommendation={}, generated_at=AS_OF,
    )


def _risk_config() -> RiskConfig:
    cfg = RiskConfig()
    cfg.filters.reference_spread["XAUUSD"] = 0.10
    cfg.filters.liquidity_floor["XAUUSD"] = 1.0
    return cfg


def _risk_context() -> RiskContext:
    return RiskContext(as_of=AS_OF)


def test_engine_ignores_scores_from_non_configured_strategies() -> None:
    engine = ShadowEvidenceEngine(frozenset({"S10"}), _risk_config(), 2000.0)
    engine.observe(AS_OF, _batch(_score(strategy_id="S39")), _risk_context())
    assert engine.opportunities == []
    assert engine.rejections == []


def test_engine_records_an_opportunity_for_a_configured_strategy() -> None:
    engine = ShadowEvidenceEngine(frozenset({"S10"}), _risk_config(), 2000.0)
    engine.observe(AS_OF, _batch(_score(strategy_id="S10")), _risk_context())
    assert len(engine.opportunities) == 1
    opp = engine.opportunities[0]
    assert opp.strategy_id == "S10"
    assert opp.as_of == AS_OF
    assert opp.symbol == "XAUUSD"
    assert opp.shadow_risk_decision in ("ALLOW", "DENY")


def test_engine_is_generic_over_multiple_configured_strategies() -> None:
    # Proves genericity directly: nothing in the engine names S10 specifically.
    engine = ShadowEvidenceEngine(frozenset({"S10", "S21", "S39"}), _risk_config(), 2000.0)
    batch = _batch(_score(strategy_id="S10"), _score(strategy_id="S21"), _score(strategy_id="S40"))
    engine.observe(AS_OF, batch, _risk_context())
    recorded_ids = {opp.strategy_id for opp in engine.opportunities}
    assert recorded_ids == {"S10", "S21"}  # S40 was never configured, correctly excluded


def test_engine_creates_a_rejection_record_only_when_denied() -> None:
    # A bare RiskConfig() (no configured reference_spread/liquidity_floor for XAUUSD) makes Risk
    # Manager's own fail-safe deny every opportunity (FILTER_SPREAD/FILTER_LIQUIDITY) -- documented
    # behavior of RiskManager itself (harness.py's own __init__ docstring), reused here to force a
    # deterministic DENY without needing to hand-craft a specific denial condition.
    engine = ShadowEvidenceEngine(frozenset({"S10"}), RiskConfig(), 2000.0)
    engine.observe(AS_OF, _batch(_score(strategy_id="S10")), _risk_context())
    assert len(engine.opportunities) == 1
    assert engine.opportunities[0].shadow_risk_decision == "DENY"
    assert len(engine.rejections) == 1
    assert engine.rejections[0].strategy_id == "S10"
    assert engine.rejections[0].denied_reason_code is not None


def test_engine_reuses_the_same_risk_manager_instance_for_repeated_calls_same_strategy() -> None:
    engine = ShadowEvidenceEngine(frozenset({"S10"}), _risk_config(), 2000.0)
    rm_first = engine._risk_manager_for("S10", AS_OF)
    rm_second = engine._risk_manager_for("S10", AS_OF + 900)
    assert rm_first is rm_second


def test_engine_uses_distinct_risk_manager_instances_per_strategy() -> None:
    engine = ShadowEvidenceEngine(frozenset({"S10", "S21"}), _risk_config(), 2000.0)
    rm_s10 = engine._risk_manager_for("S10", AS_OF)
    rm_s21 = engine._risk_manager_for("S21", AS_OF)
    assert rm_s10 is not rm_s21


def test_engine_failure_isolation_degrades_only_the_failing_strategy() -> None:
    engine = ShadowEvidenceEngine(frozenset({"S10", "S21"}), _risk_config(), 2000.0)

    def _boom(self, as_of, score, risk_context):
        raise RuntimeError("forced failure")

    original = ShadowEvidenceEngine._observe_one
    ShadowEvidenceEngine._observe_one = _boom  # type: ignore[method-assign]
    try:
        engine.observe(AS_OF, _batch(_score(strategy_id="S10"), _score(strategy_id="S21")), _risk_context())
    finally:
        ShadowEvidenceEngine._observe_one = original  # type: ignore[method-assign]

    assert engine.opportunities == []
    assert len(engine.failures) == 2
    failed_ids = {sid for _as_of, sid, _err in engine.failures}
    assert failed_ids == {"S10", "S21"}

    # A strategy already marked degraded is skipped on a later bar without re-raising or re-recording.
    engine.observe(AS_OF + 900, _batch(_score(strategy_id="S10")), _risk_context())
    assert len(engine.failures) == 2  # unchanged -- S10 was already degraded, silently skipped
