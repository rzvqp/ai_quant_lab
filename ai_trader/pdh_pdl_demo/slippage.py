"""`SlippageObservation`/`SlippageLog` -- persisted, per-fill, REALIZED slippage collection at both the
entry and exit leg of a live trade (CEO mandate, Step 8, 2026-08-13: "Slippage-ul nu se poate masura din
cotatii. Doar din fill-uri... Construieste mecanismul, ca sa fie gata cand apare prima executie.").

Not a new estimate -- a new PERSISTED RECORD of numbers that already exist inline, at the exact two call
sites that already read them (`PdhPdlOrchestrator.submit_candidate`/`_close_pending` and their
`PolicyOrchestrator` twin in `multi_policy_live`, which reuses this module the same way it already reuses
`PendingPdhPdlTrade`/`PdhPdlAuditJournal`): `entry_requested_price`/`entry_realized_price` at order-ack
time, and the close reference/`close_realized_price` at broker-close-detection time. This module adds NO
new MT5 read and NO new inference beyond what `_compute_realized_cost` already did inline in both
orchestrators -- it makes each leg's own already-computed slippage a first-class, queryable, persisted
observation instead of a private input folded into that method's single combined-cost return value.

**Entry leg**: `requested_price = candidate.entry` (the strategy's live decision-time reference quote --
NOT a broker-transmitted price; market orders submit with an unset price field, see `request_builder.py`),
`realized_price = order_result.avg_price` (MT5's own order-acknowledgement response price). Recorded on
EVERY successful entry submission (i.e. whenever a `PendingPdhPdlTrade` is actually created).

**Exit leg, disclosed limitation**: recorded ONLY when `close_reason == "BROKER_SLTP"` -- the ONE case
today where a genuine closing deal exists in MT5's own history to read
(`RealizedFillReader.read_close_price`). `PendingPdhPdlTrade` has no `close_requested_price` field, because
no order either orchestrator's own code submits carries a discrete "close now at X" request -- the SL/TP
bracket executes server-side, mechanically, without a fresh order from this codebase. The closest
defensible reference is which of the strategy's own two known exit levels (`executable_stop_price` /
`target_price`) the realized close price landed nearer to -- the SAME logic `_compute_realized_cost`
already used inline in both orchestrators, reproduced here verbatim, now persisted explicitly instead of
re-derived every audit run.

For `TIME_STOP` (or any other mechanical-close reason CAND-0009's own pluggable check might return): NO
exit observation is recorded. `pdh_pdl_demo/orchestration.py`'s own module docstring claims a mechanical
day-end CLOSE order is submitted, but no code path in this repo actually submits one today (`_close_pending`
only detects and journals a close, never sends an order) -- a pre-existing gap, disclosed here, not fixed
by this mandate. Recording a reference price for a close this codebase does not currently even request
would misrepresent a non-existent fill as a measured one. Fail-closed, not estimated, matching this
project's own "din fill-urile REALIZATE, nu din valori modelate" standard.

**Direction convention**: `signed_slippage = realized_price - requested_price`, unrounded, not `abs()`'d --
so a later consumer can separate adverse vs. favorable execution, not just magnitude.
`_compute_realized_cost`'s own `abs(...)` (needed there because it feeds a single non-negative `cost`
scalar into the audit engine) is reproduced downstream by whoever consumes this log, never decided here.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum

from ai_trader.persistent_state.store import SqliteStateStore

_DEFAULT_LOG_NAME = "pdh_pdl_demo.slippage"


class SlippageLeg(str, Enum):
    """Coded, not free text -- matching this codebase's own established `PdhPdlAuditKind` convention."""

    ENTRY = "entry"
    EXIT = "exit"


@dataclass(frozen=True, slots=True)
class SlippageObservation:
    symbol: str
    magic_number: int
    """Distinguishes which policy this fill belongs to (CAND-0001=the module-level `MAGIC_NUMBER`
    constant, CAND-0007/0009/0019=their own constructor-supplied values) -- one shared log can therefore
    serve every policy sharing a process without a separate log file per policy."""
    client_order_id: str
    leg: SlippageLeg
    as_of: int
    """The decision/detection timestamp (`candidate.as_of` for ENTRY, the closing bar's `ts_close` for
    EXIT) -- this project's own established "decision timestamp, not recording timestamp" convention."""
    direction: int
    requested_price: float
    realized_price: float
    signed_slippage: float
    """`realized_price - requested_price`, never `abs()`'d here -- see module docstring."""
    close_reason: str | None
    """`None` for the ENTRY leg; the close reason string (currently always `"BROKER_SLTP"` -- see module
    docstring) for the EXIT leg."""


def _serialize(observation: SlippageObservation) -> str:
    return json.dumps({
        "symbol": observation.symbol, "magic_number": observation.magic_number,
        "client_order_id": observation.client_order_id, "leg": observation.leg.value,
        "as_of": observation.as_of, "direction": observation.direction,
        "requested_price": observation.requested_price, "realized_price": observation.realized_price,
        "signed_slippage": observation.signed_slippage, "close_reason": observation.close_reason,
    })


def _deserialize(payload: str) -> SlippageObservation:
    data = json.loads(payload)
    return SlippageObservation(
        symbol=data["symbol"], magic_number=data["magic_number"],
        client_order_id=data["client_order_id"], leg=SlippageLeg(data["leg"]), as_of=data["as_of"],
        direction=data["direction"], requested_price=data["requested_price"],
        realized_price=data["realized_price"], signed_slippage=data["signed_slippage"],
        close_reason=data["close_reason"],
    )


class SlippageLog:
    """Append-only, per-fill slippage journal -- same persistence discipline as `SpreadObservationLog`/
    `PdhPdlAuditJournal` (hydrate from the store at construction, `record()` writes through immediately).
    `state_store=None` (the default) keeps this in-memory only, matching every other journal in this
    codebase's own test-friendly no-store mode."""

    def __init__(
        self, state_store: SqliteStateStore | None = None, log_name: str = _DEFAULT_LOG_NAME,
    ) -> None:
        self._state_store = state_store
        self._log_name = log_name
        if state_store is None:
            self._entries: list[SlippageObservation] = []
        else:
            self._entries = [
                _deserialize(payload) for payload in state_store.read_log_entries(log_name)
            ]

    def record(self, observation: SlippageObservation) -> None:
        self._entries.append(observation)
        if self._state_store is not None:
            self._state_store.append_log_entry(self._log_name, _serialize(observation))

    @property
    def entries(self) -> tuple[SlippageObservation, ...]:
        return tuple(self._entries)
