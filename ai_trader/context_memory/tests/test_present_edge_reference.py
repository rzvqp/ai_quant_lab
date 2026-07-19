"""Unit tests for :class:`ai_trader.context_memory.contracts.PresentEdgeReference`."""

from __future__ import annotations

import dataclasses

import pytest

from ai_trader.context_memory.contracts import SchemaVersion
from ai_trader.context_memory.enums import ContextEdgeStatus
from ai_trader.context_memory.identities import compute_present_edge_reference_id
from ai_trader.context_memory.tests._fixtures import make_edge_reference
from ai_trader.context_memory.validation import ContextMemoryValidationError


def test_valid_construction() -> None:
    ref = make_edge_reference("S7")
    assert ref.strategy_id == "S7"
    assert ref.declared_status is ContextEdgeStatus.PRESENT


def test_immutable() -> None:
    ref = make_edge_reference("S7")
    with pytest.raises(dataclasses.FrozenInstanceError):
        ref.strategy_id = "S1"  # type: ignore[misc]


def test_rejects_empty_strategy_id() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_edge_reference("")


def test_rejects_wrong_contract_version_type() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_edge_reference("S7", contract_version="1.0.0")  # a raw string, not a SchemaVersion


def test_rejects_wrong_declared_status_type() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_edge_reference("S7", declared_status="PRESENT")  # a raw string


def test_rejects_wrong_edge_intelligence_schema_version_type() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_edge_reference("S7", edge_intelligence_schema_version="ei-v1")  # a raw string


def test_id_is_deterministic() -> None:
    a = make_edge_reference("S7")
    b = make_edge_reference("S7")
    assert compute_present_edge_reference_id(a) == compute_present_edge_reference_id(b)


def test_id_differs_on_strategy_id() -> None:
    a = make_edge_reference("S1")
    b = make_edge_reference("S7")
    assert compute_present_edge_reference_id(a) != compute_present_edge_reference_id(b)


def test_id_differs_on_contract_version() -> None:
    a = make_edge_reference("S1", contract_version=SchemaVersion("strategy_contract", "1.0.0"))
    b = make_edge_reference("S1", contract_version=SchemaVersion("strategy_contract", "2.0.0"))
    assert compute_present_edge_reference_id(a) != compute_present_edge_reference_id(b)


def test_id_fixed_expected_value() -> None:
    ref = make_edge_reference("S7")
    result = compute_present_edge_reference_id(ref)
    assert result.value == "1e7ef8e812151093803ec8f182d3bb4f58a6cf67fc27bd34d785029a2bdf050d"
