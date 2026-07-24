"""Types owned by Context Engine (Phase 6). Reuses `market_intelligence.types.MarketIntelligenceSnapshot`,
`edge_intelligence.types.EdgeIntelligenceSnapshot`, `market_scanner.types.DataQualityLevel`, and
`context_memory.contracts.SchemaVersion` (+ its existing `MARKET_INTELLIGENCE_SCHEMA_VERSION`/
`EDGE_INTELLIGENCE_SCHEMA_VERSION` instances) unmodified -- only the genuinely missing wrapper pieces
(provenance, calculation trace, the versioned envelope) live here."""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_trader.context_memory.contracts import SchemaVersion
from ai_trader.edge_intelligence.types import EdgeIntelligenceSnapshot
from ai_trader.market_intelligence.types import MarketIntelligenceSnapshot
from ai_trader.market_scanner.types import DataQualityLevel

#: This package's own record-shape version -- bumped by hand whenever a future change alters
#: `MarketContextSnapshot`'s own field set (same convention as `context_memory`'s own schema version).
CONTEXT_ENGINE_SCHEMA_VERSION = SchemaVersion(namespace="context_engine", version="v1")


@dataclass(frozen=True, slots=True)
class CalculationTraceStep:
    """Same shape as the identical type already established in `risk_manager_live`/
    `portfolio_manager_live` -- redeclared here (not imported) to keep this package free of any
    dependency on those downstream trading-domain packages (`CONTEXT_ENGINE_PHASE6_DESIGN.md` §4)."""

    stage: str
    passed: bool
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class Provenance:
    """`source_schema_versions` carries REAL, already-existing `SchemaVersion` instances (official
    existing contracts, reused verbatim) for every upstream source this snapshot drew from.
    `data_source_lineage_id` is an explicitly DISABLED placeholder: no authorized data-source
    identity/lineage-tracking contract exists anywhere upstream today -- deliberately left `None`,
    never fabricated (CEO: "disable, don't invent")."""

    source_schema_versions: dict[str, SchemaVersion]
    data_source_lineage_id: None = None


@dataclass(frozen=True, slots=True)
class MarketContextSnapshot:
    """The Context Engine's own public output. Never carries a "final" confidence score -- only
    `market_intelligence`'s own disclosed `ContextConfidence`, embedded unmodified inside
    `market_intelligence` below, exactly as `market_intelligence.engine.build_market_intelligence`
    itself produced it."""

    symbol: str
    as_of: int
    version: SchemaVersion
    market_intelligence: MarketIntelligenceSnapshot | None
    edge_intelligence: EdgeIntelligenceSnapshot | None
    data_quality: DataQualityLevel
    is_stale: bool
    provenance: Provenance
    calculation_trace: tuple[CalculationTraceStep, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("MarketContextSnapshot.symbol must be non-empty")
        if not self.calculation_trace:
            raise ValueError("MarketContextSnapshot.calculation_trace must be non-empty -- every build attempt is traced")
