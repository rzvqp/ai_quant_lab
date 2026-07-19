"""Canonical serialization and deterministic identity generation -- Phase 7 Checkpoint 9.

**Canonical serialization rules (Checkpoint 9 §I)**, all enforced by the single private helper
:func:`_hash_canonical`:

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
    Observation,
    ObservationId,
    Outcome,
    PresentEdgeReference,
    PresentEdgeReferenceId,
    SchemaVersion,
)


def _canonical_schema_version(version: SchemaVersion) -> dict[str, str]:
    return {"namespace": version.namespace, "version": version.version}


def _canonical_float(value: float | None) -> str | None:
    return None if value is None else value.hex()


def _canonical_context_snapshot(snapshot: ContextSnapshot) -> dict[str, Any]:
    return {
        "record_type": "context_memory.context_snapshot",
        "context_memory_schema_version": _canonical_schema_version(CONTEXT_MEMORY_SCHEMA_VERSION),
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
        "context_confidence_score": _canonical_float(snapshot.context_confidence_score),
        "data_quality_state": snapshot.data_quality_state.value,
        "market_intelligence_schema_version": _canonical_schema_version(snapshot.market_intelligence_schema_version),
    }


def _canonical_present_edge_reference(ref: PresentEdgeReference) -> dict[str, Any]:
    return {
        "record_type": "context_memory.present_edge_reference",
        "context_memory_schema_version": _canonical_schema_version(CONTEXT_MEMORY_SCHEMA_VERSION),
        "strategy_id": ref.strategy_id,
        "contract_version": _canonical_schema_version(ref.contract_version),
        "edge_intelligence_schema_version": _canonical_schema_version(ref.edge_intelligence_schema_version),
        "declared_status": ref.declared_status.value,
    }


def _canonical_observation(observation: Observation) -> dict[str, Any]:
    return {
        "record_type": "context_memory.observation",
        "context_memory_schema_version": _canonical_schema_version(CONTEXT_MEMORY_SCHEMA_VERSION),
        "context_snapshot": _canonical_context_snapshot(observation.context_snapshot),
        # already canonically sorted by strategy_id in Observation.__post_init__ -- preserved verbatim,
        # never re-sorted here, so this function stays a pure reflection of already-canonical state.
        "present_edges": [_canonical_present_edge_reference(ref) for ref in observation.present_edges],
        "edge_intelligence_schema_version": _canonical_schema_version(observation.edge_intelligence_schema_version),
        # provenance_note is deliberately excluded -- see Observation's own docstring.
    }


def _canonical_outcome(outcome: Outcome) -> dict[str, Any]:
    return {
        "record_type": "context_memory.outcome",
        "context_memory_schema_version": _canonical_schema_version(CONTEXT_MEMORY_SCHEMA_VERSION),
        "observation_id": outcome.observation_id.value,
        "strategy_id": outcome.strategy_id,
        "horizon": outcome.horizon,
        "horizon_unit": outcome.horizon_unit.value,
        "outcome_definition_version": _canonical_schema_version(outcome.outcome_definition_version),
        "status": outcome.status.value,
        "observation_as_of": outcome.observation_as_of,
        "normalized_result": _canonical_float(outcome.normalized_result),
        "resolution_as_of": outcome.resolution_as_of,
        "cost_model_ref": outcome.cost_model_ref,
        "source_type": outcome.source_type.value,
    }


def _hash_canonical(payload: dict[str, Any]) -> str:
    canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def compute_context_snapshot_id(snapshot: ContextSnapshot) -> ContextSnapshotId:
    return ContextSnapshotId(_hash_canonical(_canonical_context_snapshot(snapshot)))


def compute_present_edge_reference_id(ref: PresentEdgeReference) -> PresentEdgeReferenceId:
    return PresentEdgeReferenceId(_hash_canonical(_canonical_present_edge_reference(ref)))


def compute_observation_id(observation: Observation) -> ObservationId:
    return ObservationId(_hash_canonical(_canonical_observation(observation)))


def compute_edge_evidence_id(outcome: Outcome) -> EdgeEvidenceId:
    return EdgeEvidenceId(_hash_canonical(_canonical_outcome(outcome)))
