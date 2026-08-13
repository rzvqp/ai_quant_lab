"""Types owned by `pdh_pdl_demo` -- CAND-0001 PDH-PDL v2.0 DEMO wiring. Position-tracking state between
entry and close, and the append-only audit envelope (same generic envelope + JSON-serialized detail
convention `structural_observer.types.StructuralObservation` already established)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol


@dataclass(frozen=True, slots=True)
class LiveTick:
    """A single, freshly-read bid/ask quote -- never cached, never reused across calls (matching this
    codebase's own established `mt5_account_bridge`/`mt5_pnl_source` "no caching" convention)."""

    bid: float
    ask: float
    as_of: int

    def __post_init__(self) -> None:
        if self.ask < self.bid:
            raise ValueError(f"LiveTick: ask must be >= bid, got bid={self.bid!r} ask={self.ask!r}")


class LiveTickReader(Protocol):
    """The injected dependency the recognition rule uses to read effective_spread LIVE, right before
    order submission (CEO: "singura parte care trebuie live") -- structurally typed, matching this
    codebase's own established convention for injected real/fake implementations."""

    def read(self, symbol: str) -> LiveTick | None: ...


class PdhPdlAuditKind(str, Enum):
    """Coded, not free text (CEO instruction, Mandate 4: "ca si cod, nu text liber")."""

    NO_TRADE = "no_trade"
    ENTRY_SUBMITTED = "entry_submitted"
    ENTRY_REJECTED = "entry_rejected"
    POSITION_CLOSED = "position_closed"
    AUDIT_RESULT = "audit_result"
    LEGACY_SHADOW_TELEMETRY = "legacy_shadow_telemetry"
    """Mandate 2, section 4 (CEO, 2026-08-14): recorded instead of ever calling
    `send_after_dry_run_gate` when `DecisionAuthority.NEW_BRAIN` is active -- this orchestrator still
    recognizes and reports (telemetry), but no longer produces the authoritative decision, calls Risk
    Manager, calls the Execution Adapter, or reaches the broker."""


@dataclass(frozen=True, slots=True)
class PdhPdlAuditEntry:
    symbol: str
    as_of: int
    kind: PdhPdlAuditKind
    detail: dict[str, object]


@dataclass(frozen=True, slots=True)
class PendingPdhPdlTrade:
    """Everything known about ONE PDH-PDL entry between order submission and the position's actual
    close -- carried forward bar-to-bar by the day-end closer / close-detection logic. Immutable;
    `dataclasses.replace` on state transitions, matching this codebase's own established convention
    for evolving records."""

    symbol: str
    direction: int  # +1 long (PDL), -1 short (PDH), matching DemoSignal's own convention
    touch_idx: int
    entry_idx: int
    """`touch_idx + 1` -- the bar index whose OPEN the engine will treat as `entry` once available."""
    strategy_stop_price: float
    target_price: float
    atr_at_touch: float
    day_end_idx: int | None
    """The LAST bar index of the entry day, per the SAME day_index boundary the touch bar belongs to.
    `None` until a NEW day_index is observed (Section 4 of the CEO's own confirmed design: the engine
    must never run on a truncated day) -- updated bar-by-bar to "the latest bar index still carrying
    `day_boundary_label`", then frozen the instant a different label appears."""
    day_boundary_label: int
    """The `day_index` value (an opaque UTC-epoch label, see `day_index.py`) of the entry day --
    used to detect when a NEW day has started (i.e. `day_end_idx` has become knowable/reachable)."""

    effective_spread: float
    """Read from the live bid/ask tick IMMEDIATELY before order submission (CEO: "singura parte care
    trebuie live" -- the S2 floor, never a fill-derived or modeled value)."""
    executable_stop_price: float
    """The S2-floored stop actually sent to the broker as the order's `sl`."""

    client_order_id: str
    broker_order_id: str | None
    entry_as_of: int
    entry_requested_price: float
    entry_realized_price: float | None
    """`None` until the broker ack reports a fill price (`MT5OrderSendResult.price`)."""

    closed: bool = False
    close_realized_price: float | None = None
    close_reason: str | None = None
    """One of `pdh_pdl_demo_engine.ExitReason`'s own values -- set only once the position is
    confirmed closed (broker-side SL/TP execution, detected via `query_open_orders`, or the mechanical
    day-end closer)."""
