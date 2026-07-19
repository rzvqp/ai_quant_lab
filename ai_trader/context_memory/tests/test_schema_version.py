"""Unit tests for :class:`ai_trader.context_memory.contracts.SchemaVersion`."""

from __future__ import annotations

import pytest

from ai_trader.context_memory.contracts import SchemaVersion
from ai_trader.context_memory.validation import ContextMemoryValidationError


def test_valid_construction() -> None:
    v = SchemaVersion(namespace="market_intelligence", version="mi-v1")
    assert v.namespace == "market_intelligence"
    assert v.version == "mi-v1"


def test_equality() -> None:
    a = SchemaVersion(namespace="x", version="1")
    b = SchemaVersion(namespace="x", version="1")
    c = SchemaVersion(namespace="x", version="2")
    assert a == b
    assert a != c


def test_immutable() -> None:
    v = SchemaVersion(namespace="x", version="1")
    with pytest.raises(Exception):
        v.version = "2"  # type: ignore[misc]


def test_rejects_empty_namespace() -> None:
    with pytest.raises(ContextMemoryValidationError):
        SchemaVersion(namespace="", version="1")


def test_rejects_whitespace_only_namespace() -> None:
    with pytest.raises(ContextMemoryValidationError):
        SchemaVersion(namespace="   ", version="1")


def test_rejects_empty_version() -> None:
    with pytest.raises(ContextMemoryValidationError):
        SchemaVersion(namespace="x", version="")


def test_rejects_non_string_fields() -> None:
    with pytest.raises(ContextMemoryValidationError):
        SchemaVersion(namespace=123, version="1")  # type: ignore[arg-type]


def test_stable_across_repeated_construction() -> None:
    # A proxy for "stable across process restarts" -- pure string data, no runtime-dependent state.
    a = SchemaVersion(namespace="x", version="1.0.0")
    b = SchemaVersion(namespace="x", version="1.0.0")
    assert a == b
    assert (a.namespace, a.version) == (b.namespace, b.version)
