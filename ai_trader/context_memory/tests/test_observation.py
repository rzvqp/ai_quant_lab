"""Unit tests for :class:`ai_trader.context_memory.contracts.Observation`."""

from __future__ import annotations

import dataclasses

import pytest

from ai_trader.context_memory.contracts import SchemaVersion
from ai_trader.context_memory.identities import compute_observation_id
from ai_trader.context_memory.tests._fixtures import make_edge_reference, make_observation, make_snapshot
from ai_trader.context_memory.validation import ContextMemoryValidationError


def test_valid_construction() -> None:
    obs = make_observation()
    assert obs.context_snapshot.instrument == "XAUUSD"
    assert len(obs.present_edges) == 1


def test_immutable() -> None:
    obs = make_observation()
    with pytest.raises(dataclasses.FrozenInstanceError):
        obs.provenance_note = "x"  # type: ignore[misc]


def test_rejects_wrong_context_snapshot_type() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_observation(context_snapshot="not-a-snapshot")


def test_rejects_wrong_present_edges_entry_type() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_observation(present_edges=("not-a-reference",))


def test_rejects_wrong_edge_intelligence_schema_version_type() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_observation(edge_intelligence_schema_version="ei-v1")


def test_zero_present_edges_is_explicitly_allowed() -> None:
    obs = make_observation(present_edges=())
    assert obs.present_edges == ()


def test_duplicate_strategy_id_is_rejected() -> None:
    ref_a = make_edge_reference("S1")
    ref_b = make_edge_reference("S1")  # same strategy_id, potentially different contract_version
    with pytest.raises(ContextMemoryValidationError):
        make_observation(present_edges=(ref_a, ref_b))


def test_present_edges_are_canonically_sorted_by_strategy_id() -> None:
    ref_s7 = make_edge_reference("S7")
    ref_s1 = make_edge_reference("S1")
    obs = make_observation(present_edges=(ref_s7, ref_s1))  # supplied out of order
    assert [ref.strategy_id for ref in obs.present_edges] == ["S1", "S7"]


def test_caller_supplied_order_does_not_change_identity() -> None:
    ref_s7 = make_edge_reference("S7")
    ref_s1 = make_edge_reference("S1")
    snap = make_snapshot()
    obs_a = make_observation(context_snapshot=snap, present_edges=(ref_s1, ref_s7))
    obs_b = make_observation(context_snapshot=snap, present_edges=(ref_s7, ref_s1))
    assert compute_observation_id(obs_a) == compute_observation_id(obs_b)


def test_provenance_note_does_not_change_identity() -> None:
    snap = make_snapshot()
    obs_a = make_observation(context_snapshot=snap, provenance_note="backfilled from run A")
    obs_b = make_observation(context_snapshot=snap, provenance_note="backfilled from run B")
    assert compute_observation_id(obs_a) == compute_observation_id(obs_b)


def test_id_differs_on_different_edge_set() -> None:
    snap = make_snapshot()
    obs_a = make_observation(context_snapshot=snap, present_edges=(make_edge_reference("S1"),))
    obs_b = make_observation(context_snapshot=snap, present_edges=(make_edge_reference("S7"),))
    assert compute_observation_id(obs_a) != compute_observation_id(obs_b)


def test_id_fixed_expected_value() -> None:
    # A hardcoded, independently-computed expected hash (not self-referential) -- exact fixture values
    # computed once for this checkpoint's own report and re-asserted here.
    snap = make_snapshot()
    ref_s7 = make_edge_reference("S7")
    ref_s1_v2 = make_edge_reference("S1", contract_version=SchemaVersion("strategy_contract", "2.0.0"))
    obs = make_observation(context_snapshot=snap, present_edges=(ref_s7, ref_s1_v2))
    result = compute_observation_id(obs)
    assert result.value == "d0e6e3a9ac874f9e5cfc760dcb4fb3e60dfac8f5eb9b5113ebff9f2ca312f370"
