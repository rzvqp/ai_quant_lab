"""Shared fixture builders for `recognition_engine_live` tests. A local copy of the established
per-package "own local test fixtures" convention (`recognition_engine/tests/_fixtures.py`'s own
docstring: "each package keeps its own local test fixtures... rather than a cross-package test
import")."""

from __future__ import annotations

from pathlib import Path

from ai_trader.context_memory.contracts import (
    ContextSnapshot,
    EdgeEvidenceId,
    Observation,
    ObservationId,
    Outcome,
    PositionOutcome,
    PresentEdgeReference,
    SchemaVersion,
)
from ai_trader.context_memory.enums import (
    ContextAgreementLevel,
    ContextDataQualityState,
    ContextEdgeStatus,
    ContextExpansionState,
    ContextLiquidityState,
    ContextMomentumState,
    ContextStructureState,
    ContextTrendDirection,
    ContextVolatilityRegime,
    HorizonUnit,
    OutcomeKind,
    OutcomeStatus,
    SourceType,
)
from ai_trader.context_memory.repository import ContextMemoryRepository
from ai_trader.market_intelligence.types import (
    AgreementLevel,
    ContextConfidence,
    ExpansionReading,
    ExpansionState,
    LiquidityReading,
    LiquidityState,
    MarketIntelligenceSnapshot,
    MomentumReading,
    MomentumState,
    MultiTimeframeAgreement,
    SessionReading,
    StructureReading,
    StructureState,
    TrendDirection,
    TrendReading,
    VolatilityReading,
    VolatilityRegime,
)
from ai_trader.recognition_engine_live.types import RecognitionCandidate

AS_OF = 1_700_000_000


def make_mi_snapshot(session_name: str = "LONDON", **overrides: object) -> MarketIntelligenceSnapshot:
    trend = {
        tf: TrendReading(timeframe=tf, direction=TrendDirection.UP, strength=0.01)
        for tf in ("M15", "H1", "H4", "D1")
    }
    momentum = {
        tf: MomentumReading(timeframe=tf, rsi=55.0, state=MomentumState.NEUTRAL, rate_of_change=0.001)
        for tf in ("M15", "H1", "H4", "D1")
    }
    kwargs: dict[str, object] = {
        "symbol": "XAUUSD", "as_of": AS_OF, "trend": trend, "momentum": momentum,
        "structure": StructureReading(timeframe="M15", state=StructureState.BULLISH_BOS, last_swing_high=None, last_swing_low=None),
        "volatility": VolatilityReading(atr=5.0, atr_ma=5.0, atr_ratio=1.0, volatility_rank=0.5, regime=VolatilityRegime.NORMAL),
        "liquidity": LiquidityReading(volume=1000.0, avg_volume=1000.0, volume_ratio=1.0, state=LiquidityState.NORMAL),
        "expansion": ExpansionReading(state=ExpansionState.NORMAL, is_compressed=False, is_displacement=False),
        "session": SessionReading(session_name=session_name, bar_in_session=1, inside_opening_range=True, above_session_vwap=True, gap=0.0),
        "multi_timeframe_agreement": MultiTimeframeAgreement(directions_by_timeframe={tf: TrendDirection.UP for tf in ("M15", "H1", "H4", "D1")}, agreement_score=1.0, level=AgreementLevel.STRONG),
        "confidence": ContextConfidence(score=0.9, data_quality_ok=True, agreement_component=1.0, volatility_penalty=0.0),
    }
    kwargs.update(overrides)
    return MarketIntelligenceSnapshot(**kwargs)  # type: ignore[arg-type]


def make_candidate(**overrides: object) -> RecognitionCandidate:
    kwargs: dict[str, object] = {
        "strategy_id": "S1", "pattern_id": "REC-SESSION-STRATEGY", "as_of": AS_OF, "correlation_id": "C1",
    }
    kwargs.update(overrides)
    return RecognitionCandidate(**kwargs)  # type: ignore[arg-type]


def _make_snapshot(**overrides: object) -> ContextSnapshot:
    kwargs: dict[str, object] = {
        "instrument": "XAUUSD", "as_of": AS_OF, "session_state": "LONDON",
        "trend_m15": ContextTrendDirection.UP, "trend_h1": ContextTrendDirection.UP,
        "trend_h4": ContextTrendDirection.UP, "trend_d1": ContextTrendDirection.UP,
        "structure_state": ContextStructureState.BULLISH_BOS,
        "momentum_m15": ContextMomentumState.NEUTRAL, "momentum_h1": ContextMomentumState.NEUTRAL,
        "momentum_h4": ContextMomentumState.NEUTRAL, "momentum_d1": ContextMomentumState.NEUTRAL,
        "volatility_regime": ContextVolatilityRegime.NORMAL, "liquidity_state": ContextLiquidityState.NORMAL,
        "expansion_state": ContextExpansionState.NORMAL,
        "multi_timeframe_agreement": ContextAgreementLevel.STRONG, "context_confidence_score": 0.9,
        "data_quality_state": ContextDataQualityState.OK,
    }
    kwargs.update(overrides)
    return ContextSnapshot(**kwargs)  # type: ignore[arg-type]


def _make_edge_reference(strategy_id: str = "S1") -> PresentEdgeReference:
    return PresentEdgeReference(
        strategy_id=strategy_id, contract_version=SchemaVersion(namespace="strategy_contract", version="1.0.0"),
        edge_intelligence_schema_version=SchemaVersion(namespace="edge_intelligence", version="ei-v1"),
        declared_status=ContextEdgeStatus.PRESENT,
    )


def build_repository(tmp_path: Path, records: list[dict[str, object]]) -> ContextMemoryRepository:
    """One (Observation, Outcome, PositionOutcome) triple per record spec, via the repository's own
    real, unmodified public write API -- mirrors `recognition_engine/tests/_fixtures.py::build_repository`."""
    repo = ContextMemoryRepository(tmp_path / "repo")
    for i, spec in enumerate(records):
        strategy_id = str(spec.get("strategy_id", "S1"))
        outcome_kind_obj = spec.get("outcome_kind", OutcomeKind.STRATEGY)
        assert isinstance(outcome_kind_obj, OutcomeKind)
        result = float(spec.get("result", 1.0))  # type: ignore[arg-type]
        as_of = AS_OF + i * 10_000
        raw_overrides = spec.get("snapshot_overrides", {})
        assert isinstance(raw_overrides, dict)
        snapshot_overrides: dict[str, object] = dict(raw_overrides)
        snapshot_overrides.setdefault("as_of", as_of)

        observation = Observation(
            context_snapshot=_make_snapshot(**snapshot_overrides), present_edges=(_make_edge_reference(strategy_id),),
        )
        observation_id = repo.append_observation(observation)
        outcome = Outcome(
            observation_id=observation_id, strategy_id=strategy_id, horizon=20, horizon_unit=HorizonUnit.BARS,
            outcome_definition_version=SchemaVersion(namespace="outcome_definition", version="od-v1"),
            status=OutcomeStatus.RESOLVED, observation_as_of=as_of, normalized_result=result,
            resolution_as_of=as_of + 900, cost_model_ref="GROSS_NO_COSTS",
            source_type=SourceType.SHADOW_EVIDENCE_ADAPTER, outcome_kind=outcome_kind_obj, unavailable_reason=None,
        )
        repo.append_outcome(outcome)
        position_outcome = PositionOutcome(
            observation_id=observation_id, strategy_id=strategy_id,
            position_key=f"TEST-RUN:XAUUSD:{as_of}:LONG", outcome_kind=outcome_kind_obj,
            source_type=SourceType.SHADOW_EVIDENCE_ADAPTER, opened_as_of=as_of, terminal_as_of=as_of + 900,
            total_qty_closed=1.0, weighted_avg_exit_price=2000.0, total_gross_pnl=result, total_net_pnl=result,
            total_costs=0.0, cost_model_ref="GROSS_NO_COSTS",
            terminal_outcome_id=EdgeEvidenceId("t" * 64), constituent_interim_realization_ids=(),
        )
        repo.append_position_outcome(position_outcome)
    return repo
