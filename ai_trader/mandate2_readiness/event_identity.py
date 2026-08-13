"""`EventIdentity`/`NodeTrace` -- CEO Mandate 2 amendment, 2026-08-14, section 4: the minimum per-cycle
and per-node identity fields the future N1-N6/EV pipeline must carry, so "a single trace_id reconstructs
the whole chain: feed -> N1 -> Router -> EV -> N6 -> Risk Manager -> shadow order -> broker blocked."

Prepared as a typed, validated, tested shape now -- so Mandate 2's own wiring has an exact contract to
populate once the artifact exists, not something invented under integration pressure. Nothing in this
file reads or writes N1-N6's own internal state; `NodeTrace.output` is deliberately an opaque, already
-serialized string -- this division records the boundary, never interprets what's inside it (the
standing "never modify N1-N6 internally" instruction, extended here to "never even type its internals")."""

from __future__ import annotations

from dataclasses import dataclass

_EVENT_IDENTITY_REQUIRED_FIELDS = (
    "trace_id", "market_event_id", "symbol", "timeframe", "bar_id", "brain_version", "catalog_hash",
    "configuration_fingerprint",
)


@dataclass(frozen=True, slots=True, kw_only=True)
class EventIdentity:
    """One per decision cycle. Every string field required non-empty; `received_timestamp` can never
    precede `market_timestamp` (receiving a bar before the market produced it is not a valid state, and
    treating it as one would silently accept a corrupted or fabricated timestamp)."""

    trace_id: str
    market_event_id: str
    symbol: str
    timeframe: str
    bar_id: str
    market_timestamp: int
    received_timestamp: int
    brain_version: str
    catalog_hash: str
    configuration_fingerprint: str

    def __post_init__(self) -> None:
        for name in _EVENT_IDENTITY_REQUIRED_FIELDS:
            if not getattr(self, name):
                raise ValueError(f"EventIdentity.{name} must be non-empty")
        if self.received_timestamp < self.market_timestamp:
            raise ValueError(
                f"EventIdentity: received_timestamp ({self.received_timestamp}) cannot precede "
                f"market_timestamp ({self.market_timestamp})"
            )


@dataclass(frozen=True, slots=True, kw_only=True)
class NodeTrace:
    """One per node a cycle passes through (N1, Router, EV, N6, Risk Manager, Execution Adapter, broker
    gate -- CEO's own explicit list). `output` is opaque and pre-serialized -- see module docstring for
    why this division never types or interprets what a node actually produced internally."""

    trace_id: str
    node_name: str
    input_fingerprint: str
    output: str
    reason_codes: tuple[str, ...]
    latency_seconds: float
    component_version: str

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("NodeTrace.trace_id must be non-empty")
        if not self.node_name:
            raise ValueError("NodeTrace.node_name must be non-empty")
        if not self.component_version:
            raise ValueError("NodeTrace.component_version must be non-empty")
        if self.latency_seconds < 0:
            raise ValueError(f"NodeTrace.latency_seconds cannot be negative, got {self.latency_seconds!r}")


REQUIRED_NODE_NAMES = (
    "N1", "Router", "EV", "N6", "RiskManager", "ExecutionAdapter", "BrokerGate",
)
"""The CEO's own explicit chain (section 4): "feed -> N1 -> Router -> EV -> N6 -> Risk Manager -> ordin
shadow -> broker blocked". A complete trace for one `trace_id` needs a `NodeTrace` for each of these --
this tuple exists so a future completeness check can assert exactly that, by name, rather than by an
implicit count."""
