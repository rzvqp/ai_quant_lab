"""Context Memory -- Phase 7 Checkpoints 9-12.

Immutable data contracts, controlled vocabularies, deterministic identity generation (Checkpoint 9), an
append-only persistence layer (Checkpoint 10), deterministic episode collapsing plus a rebuildable
historical index (Checkpoint 11), and a deterministic hierarchical-relaxation retrieval mechanism
(Checkpoint 12) for the Context Memory system approved in
``PHASE_7_CHECKPOINT_8_CONTEXT_MEMORY_DESIGN.md``. No contextual statistics/evidence aggregation or
Decision Intelligence integration exist anywhere in this package yet -- see each checkpoint's own report
for the exact boundary at that point.

Deliberately independent of every execution-adjacent package (Signal Engine, Scoring Engine, Risk
Manager, Portfolio, Shadow Evidence, Execution Engine, MT5, Decision Intelligence) and of
``strategy_manager``/``market_intelligence``/``edge_intelligence`` themselves -- every external
vocabulary this package needs (Market Intelligence's regime enums, Edge Intelligence's edge state,
strategy contract versions) is mirrored as a LOCAL, canonically-serialized controlled vocabulary rather
than imported live, so historical records stay interpretable even if an upstream package's own enum
shape changes later (see ``enums.py`` module docstring for the full reasoning).
"""

from __future__ import annotations

from ai_trader.context_memory.contracts import (
    CONTEXT_MEMORY_SCHEMA_VERSION,
    EDGE_INTELLIGENCE_SCHEMA_VERSION,
    MARKET_INTELLIGENCE_SCHEMA_VERSION,
    ContextSnapshot,
    ContextSnapshotId,
    EdgeEvidenceId,
    Observation,
    ObservationId,
    Outcome,
    PresentEdgeReference,
    PresentEdgeReferenceId,
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
    OutcomeStatus,
    SourceType,
)
from ai_trader.context_memory.episodes import (
    Episode,
    EpisodeId,
    StateFingerprint,
    collapse_into_episodes,
    compute_episode_id,
    compute_state_fingerprint,
)
from ai_trader.context_memory.identities import (
    compute_context_snapshot_id,
    compute_edge_evidence_id,
    compute_observation_id,
    compute_present_edge_reference_id,
)
from ai_trader.context_memory.index import HistoricalIndex, IndexStatistics
from ai_trader.context_memory.repository import (
    ConflictingDuplicateError,
    ContextMemoryRepository,
    ContextMemoryRepositoryError,
    RepositoryCorruptionError,
    RepositoryIntegrityReport,
    RepositoryPathError,
    RepositoryWriteError,
)
from ai_trader.context_memory.retrieval import (
    RETRIEVAL_POLICY_VERSION,
    RetrievalMatch,
    RetrievalQuery,
    RetrievalResult,
    RetrievalStatus,
    retrieve,
)
from ai_trader.context_memory.validation import ContextMemoryValidationError, as_of_from_datetime

__all__ = [
    "CONTEXT_MEMORY_SCHEMA_VERSION",
    "EDGE_INTELLIGENCE_SCHEMA_VERSION",
    "MARKET_INTELLIGENCE_SCHEMA_VERSION",
    "SchemaVersion",
    "ContextSnapshot",
    "ContextSnapshotId",
    "PresentEdgeReference",
    "PresentEdgeReferenceId",
    "Observation",
    "ObservationId",
    "Outcome",
    "EdgeEvidenceId",
    "ContextTrendDirection",
    "ContextStructureState",
    "ContextMomentumState",
    "ContextVolatilityRegime",
    "ContextLiquidityState",
    "ContextExpansionState",
    "ContextAgreementLevel",
    "ContextDataQualityState",
    "ContextEdgeStatus",
    "OutcomeStatus",
    "SourceType",
    "HorizonUnit",
    "compute_context_snapshot_id",
    "compute_present_edge_reference_id",
    "compute_observation_id",
    "compute_edge_evidence_id",
    "ContextMemoryValidationError",
    "as_of_from_datetime",
    "ContextMemoryRepository",
    "RepositoryIntegrityReport",
    "ContextMemoryRepositoryError",
    "RepositoryPathError",
    "RepositoryWriteError",
    "RepositoryCorruptionError",
    "ConflictingDuplicateError",
    "StateFingerprint",
    "EpisodeId",
    "Episode",
    "compute_state_fingerprint",
    "compute_episode_id",
    "collapse_into_episodes",
    "HistoricalIndex",
    "IndexStatistics",
    "RETRIEVAL_POLICY_VERSION",
    "RetrievalQuery",
    "RetrievalMatch",
    "RetrievalResult",
    "RetrievalStatus",
    "retrieve",
]
