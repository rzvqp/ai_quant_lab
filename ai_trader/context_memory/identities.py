"""Canonical serialization and deterministic identity generation -- Phase 7 Checkpoint 9.

**Checkpoint 10 update**: ``canonical_*``/``hash_canonical`` were promoted from Checkpoint 9's own
leading-underscore-private names to plain package-internal names (still NOT exported via
``ai_trader.context_memory.__init__``'s ``__all__`` -- Checkpoint 9 §K's "no internal helper as public
API" still holds) so :mod:`ai_trader.context_memory.codec` can reuse the exact same canonicalization
logic for its own encode path, rather than duplicating it. A pure rename; no behavior changed.

**Canonical serialization rules (Checkpoint 9 §I)**, all enforced by the single package-internal helper
:func:`hash_canonical`:

- Every record is first converted to a plain, JSON-primitive-only ``dict`` (never ``repr()`` -- raw
  ``repr()`` output is explicitly avoided everywhere in this module, since its exact formatting is not a
  contract Python guarantees to hold across versions).
- Enum members serialize to their own ``.value`` string, never the member name.
- ``None`` serializes to JSON ``null``.
- Floats serialize via ``float.hex()`` -- an EXACT, unambiguous, base-16 encoding of the IEEE-754 bit
  pattern that the Python language itself guarantees round-trips exactly via ``float.fromhex()``, never
  the shortest-round-trip DECIMAL text ``repr(float)``/``str(float)`` produce (which, while stable in
  practice since Python 3.1, is not the representation this design chooses to depend on).
- ``dict`` keys are sorted (``json.dumps(..., sort_keys=True)``) at every nesting level, including
  nested ``SchemaVersion`` payloads -- resolves "map key ordering" for every dict this module ever
  builds.
- This package never places a Python ``set``/``frozenset`` in any canonical payload -- the one naturally
  unordered collection in these contracts (``Observation.present_edges``) is canonically sorted into a
  ``tuple`` BEFORE it ever reaches this module (``contracts.py::Observation.__post_init__``), so no
  separate "set/list ordering" rule is needed here: every list already arrives pre-ordered.
- ``json.dumps(..., ensure_ascii=True)`` forces every non-ASCII character to a ``\\uXXXX`` escape,
  removing any platform/locale-dependent Unicode encoding ambiguity from the canonical byte string.
- ``separators=(",", ":")`` removes the whitespace ``json.dumps`` would otherwise insert by default --
  the canonical string must be byte-for-byte identical regardless of ``json``'s own default formatting
  choices, which are not part of its documented stability contract.
- Every payload's own top-level ``"record_type"`` key namespaces the hash by record kind (Checkpoint 9
  §H's "explicit record-type namespace") -- two records of DIFFERENT types can never collide even if
  every other field happened to serialize identically.

**Hashing**: ``hashlib.sha256`` only -- a stable-across-restarts, standard-library, non-salted digest.
Python's own built-in ``hash()`` is NEVER used anywhere in this module (Checkpoint 9 §H's own explicit
prohibition -- ``hash()`` is per-process-salted by default and not a durable identity primitive). No
``uuid.uuid4()`` (random), no ``time``/``datetime.now()`` (clock-dependent), no filesystem read, and no
mutable global state participates in any ID computed here -- every ID is a pure function of its own
record's already-validated, already-immutable field values.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from ai_trader.context_memory.contracts import (
    CONTEXT_MEMORY_SCHEMA_VERSION,
    ContextSnapshot,
    ContextSnapshotId,
    EdgeEvidenceId,
    InterimRealization,
    InterimRealizationId,
    Observation,
    ObservationId,
    OperationalMetadata,
    OperationalMetadataId,
    Outcome,
    PositionOutcome,
    PositionOutcomeId,
    PresentEdgeReference,
    PresentEdgeReferenceId,
    SchemaVersion,
)


def canonical_schema_version(version: SchemaVersion) -> dict[str, str]:
    return {"namespace": version.namespace, "version": version.version}


def canonical_float(value: float | None) -> str | None:
    return None if value is None else value.hex()


def canonical_context_snapshot(snapshot: ContextSnapshot) -> dict[str, Any]:
    return {
        "record_type": "context_memory.context_snapshot",
        "context_memory_schema_version": canonical_schema_version(CONTEXT_MEMORY_SCHEMA_VERSION),
        "instrument": snapshot.instrument,
        "as_of": snapshot.as_of,
        "session_state": snapshot.session_state,
        "trend_m15": snapshot.trend_m15.value,
        "trend_h1": snapshot.trend_h1.value,
        "trend_h4": snapshot.trend_h4.value,
        "trend_d1": snapshot.trend_d1.value,
        "structure_state": snapshot.structure_state.value,
        "momentum_m15": snapshot.momentum_m15.value,
        "momentum_h1": snapshot.momentum_h1.value,
        "momentum_h4": snapshot.momentum_h4.value,
        "momentum_d1": snapshot.momentum_d1.value,
        "volatility_regime": snapshot.volatility_regime.value,
        "liquidity_state": snapshot.liquidity_state.value,
        "expansion_state": snapshot.expansion_state.value,
        "multi_timeframe_agreement": snapshot.multi_timeframe_agreement.value,
        "context_confidence_score": canonical_float(snapshot.context_confidence_score),
        "data_quality_state": snapshot.data_quality_state.value,
        "market_intelligence_schema_version": canonical_schema_version(snapshot.market_intelligence_schema_version),
    }


def canonical_present_edge_reference(ref: PresentEdgeReference) -> dict[str, Any]:
    return {
        "record_type": "context_memory.present_edge_reference",
        "context_memory_schema_version": canonical_schema_version(CONTEXT_MEMORY_SCHEMA_VERSION),
        "strategy_id": ref.strategy_id,
        "contract_version": canonical_schema_version(ref.contract_version),
        "edge_intelligence_schema_version": canonical_schema_version(ref.edge_intelligence_schema_version),
        "declared_status": ref.declared_status.value,
    }


def canonical_observation(observation: Observation) -> dict[str, Any]:
    return {
        "record_type": "context_memory.observation",
        "context_memory_schema_version": canonical_schema_version(CONTEXT_MEMORY_SCHEMA_VERSION),
        "context_snapshot": canonical_context_snapshot(observation.context_snapshot),
        # already canonically sorted by strategy_id in Observation.__post_init__ -- preserved verbatim,
        # never re-sorted here, so this function stays a pure reflection of already-canonical state.
        "present_edges": [canonical_present_edge_reference(ref) for ref in observation.present_edges],
        "edge_intelligence_schema_version": canonical_schema_version(observation.edge_intelligence_schema_version),
        # provenance_note is deliberately excluded -- see Observation's own docstring.
    }


def canonical_outcome(outcome: Outcome) -> dict[str, Any]:
    return {
        "record_type": "context_memory.outcome",
        "context_memory_schema_version": canonical_schema_version(CONTEXT_MEMORY_SCHEMA_VERSION),
        "observation_id": outcome.observation_id.value,
        "strategy_id": outcome.strategy_id,
        "horizon": outcome.horizon,
        "horizon_unit": outcome.horizon_unit.value,
        "outcome_definition_version": canonical_schema_version(outcome.outcome_definition_version),
        "status": outcome.status.value,
        "observation_as_of": outcome.observation_as_of,
        "normalized_result": canonical_float(outcome.normalized_result),
        "resolution_as_of": outcome.resolution_as_of,
        "cost_model_ref": outcome.cost_model_ref,
        "source_type": outcome.source_type.value,
        "outcome_kind": outcome.outcome_kind.value,
        "unavailable_reason": outcome.unavailable_reason.value if outcome.unavailable_reason is not None else None,
    }


def canonical_operational_metadata(metadata: OperationalMetadata) -> dict[str, Any]:
    return {
        "record_type": "context_memory.operational_metadata",
        "context_memory_schema_version": canonical_schema_version(CONTEXT_MEMORY_SCHEMA_VERSION),
        "observation_id": metadata.observation_id.value,
        "strategy_id": metadata.strategy_id,
        "risk_decision": metadata.risk_decision.value,
        "denied_reason_code": metadata.denied_reason_code,
        "rejection_stage": metadata.rejection_stage,
        "strategy_health_policy_state": metadata.strategy_health_policy_state,
    }


def canonical_interim_realization(realization: InterimRealization) -> dict[str, Any]:
    return {
        "record_type": "context_memory.interim_realization",
        "context_memory_schema_version": canonical_schema_version(CONTEXT_MEMORY_SCHEMA_VERSION),
        "observation_id": realization.observation_id.value,
        "strategy_id": realization.strategy_id,
        "position_key": realization.position_key,
        "outcome_kind": realization.outcome_kind.value,
        "source_type": realization.source_type.value,
        "horizon": realization.horizon,
        "horizon_unit": realization.horizon_unit.value,
        "observation_as_of": realization.observation_as_of,
        "realization_as_of": realization.realization_as_of,
        "normalized_result": canonical_float(realization.normalized_result),
        "cost_model_ref": realization.cost_model_ref,
        "unavailable_reason": (
            realization.unavailable_reason.value if realization.unavailable_reason is not None else None
        ),
    }


def canonical_position_outcome(position_outcome: PositionOutcome) -> dict[str, Any]:
    return {
        "record_type": "context_memory.position_outcome",
        "context_memory_schema_version": canonical_schema_version(CONTEXT_MEMORY_SCHEMA_VERSION),
        "observation_id": position_outcome.observation_id.value,
        "strategy_id": position_outcome.strategy_id,
        "position_key": position_outcome.position_key,
        "outcome_kind": position_outcome.outcome_kind.value,
        "source_type": position_outcome.source_type.value,
        "opened_as_of": position_outcome.opened_as_of,
        "terminal_as_of": position_outcome.terminal_as_of,
        "total_qty_closed": canonical_float(position_outcome.total_qty_closed),
        "weighted_avg_exit_price": canonical_float(position_outcome.weighted_avg_exit_price),
        "total_gross_pnl": canonical_float(position_outcome.total_gross_pnl),
        "total_net_pnl": canonical_float(position_outcome.total_net_pnl),
        "total_costs": canonical_float(position_outcome.total_costs),
        "cost_model_ref": position_outcome.cost_model_ref,
        "terminal_outcome_id": position_outcome.terminal_outcome_id.value,
        # already caller-supplied in accumulation order (oldest first) -- not re-sorted here, since
        # accumulation order IS the canonical, meaningful order (chronological), unlike Observation's
        # own present_edges (which has no inherent order and is re-sorted for that reason).
        "constituent_interim_realization_ids": [ref.value for ref in position_outcome.constituent_interim_realization_ids],
    }


def hash_canonical(payload: dict[str, Any]) -> str:
    canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def compute_context_snapshot_id(snapshot: ContextSnapshot) -> ContextSnapshotId:
    return ContextSnapshotId(hash_canonical(canonical_context_snapshot(snapshot)))


def compute_present_edge_reference_id(ref: PresentEdgeReference) -> PresentEdgeReferenceId:
    return PresentEdgeReferenceId(hash_canonical(canonical_present_edge_reference(ref)))


def compute_observation_id(observation: Observation) -> ObservationId:
    return ObservationId(hash_canonical(canonical_observation(observation)))


def compute_edge_evidence_id(outcome: Outcome) -> EdgeEvidenceId:
    return EdgeEvidenceId(hash_canonical(canonical_outcome(outcome)))


def compute_operational_metadata_id(metadata: OperationalMetadata) -> OperationalMetadataId:
    return OperationalMetadataId(hash_canonical(canonical_operational_metadata(metadata)))


def compute_interim_realization_id(realization: InterimRealization) -> InterimRealizationId:
    return InterimRealizationId(hash_canonical(canonical_interim_realization(realization)))


def compute_position_outcome_id(position_outcome: PositionOutcome) -> PositionOutcomeId:
    return PositionOutcomeId(hash_canonical(canonical_position_outcome(position_outcome)))
