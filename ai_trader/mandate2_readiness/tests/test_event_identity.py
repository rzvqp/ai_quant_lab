"""`EventIdentity`/`NodeTrace` tests."""

from __future__ import annotations

import dataclasses

import pytest

from ai_trader.mandate2_readiness.event_identity import REQUIRED_NODE_NAMES, EventIdentity, NodeTrace


def _identity(**overrides: object) -> EventIdentity:
    defaults: dict[str, object] = dict(
        trace_id="T1", market_event_id="E1", symbol="XAUUSD", timeframe="M15", bar_id="B1",
        market_timestamp=1_700_000_000, received_timestamp=1_700_000_005, brain_version="0.1.3",
        catalog_hash="deadbeef", configuration_fingerprint="cfg-1",
    )
    defaults.update(overrides)
    return EventIdentity(**defaults)  # type: ignore[arg-type]


def test_a_fully_populated_identity_constructs_cleanly() -> None:
    identity = _identity()
    assert identity.trace_id == "T1"


@pytest.mark.parametrize("field", [
    "trace_id", "market_event_id", "symbol", "timeframe", "bar_id", "brain_version", "catalog_hash",
    "configuration_fingerprint",
])
def test_each_required_string_field_rejects_empty(field: str) -> None:
    with pytest.raises(ValueError, match=field):
        _identity(**{field: ""})


def test_received_timestamp_before_market_timestamp_is_rejected() -> None:
    with pytest.raises(ValueError, match="cannot precede"):
        _identity(market_timestamp=1_700_000_100, received_timestamp=1_700_000_000)


def test_received_timestamp_equal_to_market_timestamp_is_accepted() -> None:
    _identity(market_timestamp=1_700_000_000, received_timestamp=1_700_000_000)  # no exception


def test_identity_is_frozen() -> None:
    identity = _identity()
    with pytest.raises(dataclasses.FrozenInstanceError):
        identity.trace_id = "X"  # type: ignore[misc]


def test_node_trace_requires_non_empty_trace_id_node_name_and_component_version() -> None:
    with pytest.raises(ValueError, match="trace_id"):
        NodeTrace(trace_id="", node_name="N1", input_fingerprint="fp", output="{}", reason_codes=(), latency_seconds=0.0, component_version="v1")
    with pytest.raises(ValueError, match="node_name"):
        NodeTrace(trace_id="T1", node_name="", input_fingerprint="fp", output="{}", reason_codes=(), latency_seconds=0.0, component_version="v1")
    with pytest.raises(ValueError, match="component_version"):
        NodeTrace(trace_id="T1", node_name="N1", input_fingerprint="fp", output="{}", reason_codes=(), latency_seconds=0.0, component_version="")


def test_node_trace_rejects_negative_latency() -> None:
    with pytest.raises(ValueError, match="latency_seconds"):
        NodeTrace(trace_id="T1", node_name="N1", input_fingerprint="fp", output="{}", reason_codes=(), latency_seconds=-0.1, component_version="v1")


def test_node_trace_output_is_a_plain_string_never_interpreted_here() -> None:
    """This module never parses `output` -- confirmed structurally: it's typed `str`, not a union of
    N1-N6-specific result types this division would otherwise need to import."""
    trace = NodeTrace(
        trace_id="T1", node_name="N6", input_fingerprint="fp", output='{"decision": "opaque to us"}',
        reason_codes=("SHADOW_ELIGIBLE",), latency_seconds=0.01, component_version="n6-v1",
    )
    assert isinstance(trace.output, str)


def test_required_node_names_matches_the_ceos_own_explicit_chain() -> None:
    assert REQUIRED_NODE_NAMES == ("N1", "Router", "EV", "N6", "RiskManager", "ExecutionAdapter", "BrokerGate")
