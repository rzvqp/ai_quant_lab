"""Confirms the exact public surface of :mod:`ai_trader.context_memory` -- catches accidental
over-exposure of an internal helper (e.g. a canonicalization function) as much as accidental omission."""

from __future__ import annotations

import ai_trader.context_memory as context_memory

_EXPECTED_PUBLIC_NAMES = {
    "CONTEXT_MEMORY_SCHEMA_VERSION", "EDGE_INTELLIGENCE_SCHEMA_VERSION", "MARKET_INTELLIGENCE_SCHEMA_VERSION",
    "SchemaVersion",
    "ContextSnapshot", "ContextSnapshotId",
    "PresentEdgeReference", "PresentEdgeReferenceId",
    "Observation", "ObservationId",
    "Outcome", "EdgeEvidenceId",
    "ContextTrendDirection", "ContextStructureState", "ContextMomentumState", "ContextVolatilityRegime",
    "ContextLiquidityState", "ContextExpansionState", "ContextAgreementLevel", "ContextDataQualityState",
    "ContextEdgeStatus", "OutcomeStatus", "OutcomeKind", "SourceType", "HorizonUnit",
    "compute_context_snapshot_id", "compute_present_edge_reference_id", "compute_observation_id",
    "compute_edge_evidence_id",
    "ContextMemoryValidationError", "as_of_from_datetime",
    "ContextMemoryRepository", "RepositoryIntegrityReport", "ContextMemoryRepositoryError",
    "RepositoryPathError", "RepositoryWriteError", "RepositoryCorruptionError", "ConflictingDuplicateError",
    "StateFingerprint", "EpisodeId", "Episode",
    "compute_state_fingerprint", "compute_episode_id", "collapse_into_episodes",
    "HistoricalIndex", "IndexStatistics",
    "RETRIEVAL_POLICY_VERSION", "RetrievalQuery", "RetrievalMatch", "RetrievalResult", "RetrievalStatus",
    "retrieve",
    "EVIDENCE_POLICY_VERSION", "EvidencePolicy", "EvidenceStatus", "ContextualEvidenceReport",
    "aggregate_evidence", "aggregate_all_present_edges",
}


def test_public_api_matches_exactly() -> None:
    assert set(context_memory.__all__) == _EXPECTED_PUBLIC_NAMES


def test_every_declared_name_is_actually_importable() -> None:
    for name in context_memory.__all__:
        assert hasattr(context_memory, name), f"{name} is declared in __all__ but not importable"


def test_no_internal_canonicalization_helpers_are_exported() -> None:
    private_names = {n for n in dir(context_memory) if n.startswith("_") and not n.startswith("__")}
    assert private_names.isdisjoint(set(context_memory.__all__))
