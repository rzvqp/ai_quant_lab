"""Unit tests for :mod:`ai_trader.context_memory.codec`."""

from __future__ import annotations

import pytest

from ai_trader.context_memory import codec
from ai_trader.context_memory.contracts import CONTEXT_MEMORY_SCHEMA_VERSION
from ai_trader.context_memory.identities import (
    compute_context_snapshot_id,
    compute_edge_evidence_id,
    compute_observation_id,
    compute_present_edge_reference_id,
)
from ai_trader.context_memory.tests._fixtures import (
    AS_OF,
    make_edge_reference,
    make_observation,
    make_pending_outcome,
    make_snapshot,
)
from ai_trader.context_memory.validation import ContextMemoryValidationError


def test_context_snapshot_round_trips() -> None:
    snap = make_snapshot()
    decoded = codec.decode_context_snapshot(codec.encode_context_snapshot(snap))
    assert decoded == snap
    assert compute_context_snapshot_id(decoded) == compute_context_snapshot_id(snap)


def test_present_edge_reference_round_trips() -> None:
    ref = make_edge_reference("S7")
    decoded = codec.decode_present_edge_reference(codec.encode_present_edge_reference(ref))
    assert decoded == ref
    assert compute_present_edge_reference_id(decoded) == compute_present_edge_reference_id(ref)


def test_observation_round_trips() -> None:
    obs = make_observation()
    decoded = codec.decode_observation(codec.encode_observation(obs))
    assert decoded == obs
    assert compute_observation_id(decoded) == compute_observation_id(obs)


def test_outcome_round_trips() -> None:
    from ai_trader.context_memory.contracts import ObservationId

    out = make_pending_outcome(ObservationId("x" * 64))
    decoded = codec.decode_outcome(codec.encode_outcome(out))
    assert decoded == out
    assert compute_edge_evidence_id(decoded) == compute_edge_evidence_id(out)


def test_decode_rejects_wrong_record_type() -> None:
    payload = codec.encode_context_snapshot(make_snapshot())
    payload = dict(payload)
    payload["record_type"] = "context_memory.observation"
    with pytest.raises(ContextMemoryValidationError):
        codec.decode_context_snapshot(payload)


def test_decode_rejects_missing_field() -> None:
    payload = dict(codec.encode_context_snapshot(make_snapshot()))
    del payload["as_of"]
    with pytest.raises(ContextMemoryValidationError, match="malformed context_snapshot payload"):
        codec.decode_context_snapshot(payload)


def test_decode_rejects_invalid_enum_value() -> None:
    payload = dict(codec.encode_context_snapshot(make_snapshot()))
    payload["trend_m15"] = "SIDEWAYS"  # not a real ContextTrendDirection member
    with pytest.raises(ContextMemoryValidationError):
        codec.decode_context_snapshot(payload)


def test_decode_rejects_unsupported_schema_version() -> None:
    payload = dict(codec.encode_context_snapshot(make_snapshot()))
    payload["context_memory_schema_version"] = {"namespace": "context_memory", "version": "v999"}
    with pytest.raises(codec.UnsupportedSchemaVersionError):
        codec.decode_context_snapshot(payload)


def test_decode_rejects_missing_schema_version() -> None:
    payload = dict(codec.encode_context_snapshot(make_snapshot()))
    del payload["context_memory_schema_version"]
    with pytest.raises(codec.UnsupportedSchemaVersionError):
        codec.decode_context_snapshot(payload)


def test_encoded_snapshot_carries_the_current_schema_version() -> None:
    payload = codec.encode_context_snapshot(make_snapshot())
    assert payload["context_memory_schema_version"] == {
        "namespace": CONTEXT_MEMORY_SCHEMA_VERSION.namespace,
        "version": CONTEXT_MEMORY_SCHEMA_VERSION.version,
    }
