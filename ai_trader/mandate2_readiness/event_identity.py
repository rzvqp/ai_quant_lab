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
    treating it as one would silently accept a corrupted or fabricated timestamp).

    **Tower identity fields (Red Team RT-MANDATE2-0002 remediation, 2026-08-16; extended to N2 by
    RT-TOWER-0008, 2026-08-17)** -- all optional, `None` until a real tower call actually happens
    (Router-ineligible/ATR-insufficient/cost-unavailable outcomes never reach the tower, so they
    correctly carry no tower identity at all, rather than a fabricated placeholder). Every non-`None`
    value here is copied verbatim from the isolated worker's own verified response -- `bridge.py` never
    recomputes or guesses these. `n2_*`/`n3_*`/`n4_*` are deliberately DISTINCT fields, never merged into
    one: N2 answers on H1, N3 on M15, N4 on M5, so their `data_identity`/`node_input_fingerprint` are
    legitimately different values for the same event, while their `event_fingerprint`s are expected to
    AGREE (all describe the same `market_event_id`) -- `bridge.py` treats disagreement as
    `CHAIN_IDENTITY_MISMATCH`, fail-closed. `chain_fingerprint`/`chain_binding_version`/
    `chain_response_contract_version`/`chain_status`/`terminal_reason_code` are the whole-chain identity
    `ve_tower.run_tower_chain` itself returns, shared across N2/N3/N4 for this one call."""

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
    worker_session_id: str | None = None
    worker_identity_fingerprint: str | None = None
    tower_version: str | None = None
    chain_binding_version: str | None = None
    chain_response_contract_version: str | None = None
    chain_fingerprint: str | None = None
    chain_status: str | None = None
    terminal_reason_code: str | None = None
    n2_contract_version: str | None = None
    n2_code_version: str | None = None
    n2_event_fingerprint: str | None = None
    n2_node_input_fingerprint: str | None = None
    n2_data_identity: str | None = None
    n2_output_fingerprint: str | None = None
    n3_contract_version: str | None = None
    n3_code_version: str | None = None
    n3_event_fingerprint: str | None = None
    n3_node_input_fingerprint: str | None = None
    n3_data_identity: str | None = None
    n4_contract_version: str | None = None
    n4_code_version: str | None = None
    n4_event_fingerprint: str | None = None
    n4_node_input_fingerprint: str | None = None
    n4_data_identity: str | None = None

    # -- Request-scoped time fields (RT-TIME-0001 section A, 2026-08-17) -- all optional, `None` until a
    # real tower call actually happens (mirrors the tower identity fields above: a Router-ineligible or
    # ATR-insufficient outcome never reaches the tower, so it correctly carries none of these either).
    # `event_as_of`/`data_cutoff` are what the fetched H1/M15/M5 windows are actually anchored to;
    # `wall_clock_now` is operational-only (never used to select data -- see `wall_clock.py`'s own
    # docstring). `last_closed_h1`/`_m15`/`_m5` are the ts_close of the most recent bar actually fetched
    # for each timeframe (`None` if that window came back empty). `staleness_reason_*` is a bridge-side,
    # informational echo of the SAME staleness math `ve_tower`'s own `DATA_STALE` gate independently
    # performs -- never the authority for the actual decision, only for audit/trace purposes.
    event_as_of: int | None = None
    data_cutoff: int | None = None
    wall_clock_now: int | None = None
    last_closed_h1: int | None = None
    last_closed_m15: int | None = None
    last_closed_m5: int | None = None
    fetch_timestamp: int | None = None
    staleness_reason_h1: str | None = None
    staleness_reason_m15: str | None = None
    staleness_reason_m5: str | None = None

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
