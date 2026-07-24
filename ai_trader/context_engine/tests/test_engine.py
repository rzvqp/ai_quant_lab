from __future__ import annotations

from ai_trader.context_engine.engine import build_context_snapshot
from ai_trader.market_intelligence.tests._fixtures import make_context
from ai_trader.market_scanner.types import DataQualityLevel


def test_well_formed_context_produces_a_snapshot_with_market_intelligence() -> None:
    snapshot = build_context_snapshot(make_context())
    assert snapshot.market_intelligence is not None
    assert snapshot.symbol == "XAUUSD"
    assert snapshot.data_quality is DataQualityLevel.OK
    assert snapshot.is_stale is False


def test_snapshot_carries_as_of_from_the_context_never_wall_clock() -> None:
    snapshot = build_context_snapshot(make_context(as_of=1_234_567))
    assert snapshot.as_of == 1_234_567


def test_stale_data_quality_sets_is_stale_true() -> None:
    snapshot = build_context_snapshot(make_context(data_quality_level="STALE"))
    assert snapshot.data_quality is DataQualityLevel.STALE
    assert snapshot.is_stale is True


def test_unrecognized_data_quality_string_fails_closed_to_insufficient() -> None:
    snapshot = build_context_snapshot(make_context(data_quality_level="NOT_A_REAL_LEVEL"))
    assert snapshot.data_quality is DataQualityLevel.INSUFFICIENT


def test_snapshot_never_carries_a_final_confidence_field() -> None:
    """Only `market_intelligence`'s own disclosed `ContextConfidence` is embedded, unmodified --
    never a NEW top-level confidence field on `MarketContextSnapshot` itself."""
    snapshot = build_context_snapshot(make_context())
    field_names = {f for f in snapshot.__dataclass_fields__}
    assert "confidence" not in field_names
    assert "final_confidence" not in field_names
    assert snapshot.market_intelligence is not None
    assert snapshot.market_intelligence.confidence is not None


def test_provenance_carries_real_upstream_schema_versions() -> None:
    snapshot = build_context_snapshot(make_context())
    assert snapshot.provenance.source_schema_versions["market_intelligence"].namespace == "market_intelligence"
    assert snapshot.provenance.source_schema_versions["edge_intelligence"].namespace == "edge_intelligence"


def test_provenance_data_source_lineage_id_is_disabled_not_fabricated() -> None:
    snapshot = build_context_snapshot(make_context())
    assert snapshot.provenance.data_source_lineage_id is None


def test_calculation_trace_is_never_empty() -> None:
    snapshot = build_context_snapshot(make_context())
    assert len(snapshot.calculation_trace) >= 4


def test_edge_intelligence_present_when_evaluable() -> None:
    snapshot = build_context_snapshot(make_context())
    assert snapshot.edge_intelligence is not None


def test_snapshot_version_is_the_context_engine_namespace() -> None:
    snapshot = build_context_snapshot(make_context())
    assert snapshot.version.namespace == "context_engine"


def test_determinism_same_context_produces_equal_snapshot() -> None:
    context = make_context()
    first = build_context_snapshot(context)
    second = build_context_snapshot(context)
    assert first.market_intelligence == second.market_intelligence
    assert first.data_quality == second.data_quality
    assert first.is_stale == second.is_stale
