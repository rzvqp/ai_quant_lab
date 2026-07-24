from __future__ import annotations

import pytest

from ai_trader.context_engine.types import CONTEXT_ENGINE_SCHEMA_VERSION, MarketContextSnapshot, Provenance
from ai_trader.market_scanner.types import DataQualityLevel


def test_snapshot_requires_nonempty_symbol() -> None:
    with pytest.raises(ValueError):
        MarketContextSnapshot(
            symbol="", as_of=1, version=CONTEXT_ENGINE_SCHEMA_VERSION, market_intelligence=None,
            edge_intelligence=None, data_quality=DataQualityLevel.OK, is_stale=False,
            provenance=Provenance(source_schema_versions={}), calculation_trace=(),
        )


def test_snapshot_requires_nonempty_calculation_trace() -> None:
    from ai_trader.context_engine.types import CalculationTraceStep

    with pytest.raises(ValueError):
        MarketContextSnapshot(
            symbol="XAUUSD", as_of=1, version=CONTEXT_ENGINE_SCHEMA_VERSION, market_intelligence=None,
            edge_intelligence=None, data_quality=DataQualityLevel.OK, is_stale=False,
            provenance=Provenance(source_schema_versions={}), calculation_trace=(),
        )
    # sanity: a non-empty trace is accepted
    MarketContextSnapshot(
        symbol="XAUUSD", as_of=1, version=CONTEXT_ENGINE_SCHEMA_VERSION, market_intelligence=None,
        edge_intelligence=None, data_quality=DataQualityLevel.OK, is_stale=False,
        provenance=Provenance(source_schema_versions={}), calculation_trace=(CalculationTraceStep("X", True),),
    )


def test_provenance_disabled_field_defaults_to_none() -> None:
    provenance = Provenance(source_schema_versions={})
    assert provenance.data_source_lineage_id is None
