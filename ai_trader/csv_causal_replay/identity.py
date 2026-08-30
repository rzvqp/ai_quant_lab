"""Source/adapter identity and fingerprinting (CSV_CAUSAL_REPLAY_ADAPTER_V1, mandate sections 3, 7,
17). Mirrors `ai_trader.n1_replay.identity`'s own shape (a frozen, hashable identity dataclass with
a `.fingerprint()`/`.matches()` pair used to fail closed on drift) applied to a flat file source
instead of a wrapped runtime.
"""

from __future__ import annotations

import dataclasses
import hashlib
from pathlib import Path

ADAPTER_VERSION = "1.0.0"
"""Bump whenever this package's causal semantics change (bar revelation, commit handshake, gate
evaluation, or durable-state schema). Does NOT change merely because the underlying CSV file grows
with new trailing bars -- see `SourceIdentity.content_hash`, which is scoped to a fixed, named
extract, not "whatever the live file currently contains"."""

DURABLE_STATE_SCHEMA_VERSION = "csv-causal-replay-state-v1"

XAUUSD_M15_SYMBOL = "OANDA:XAUUSD"
"""The exact TradingView ticker `REPLAY_DATA_GAP_LEDGER.md` cites as the Q4 apprenticeship's own
replay source (e.g. GAP-001's `SOURCE: OANDA:XAUUSD, TradingView Bar Replay`) -- reused verbatim as
this adapter's own symbol identity, not re-derived or approximated, so a durable-state record and
the ledger both name the same instrument unambiguously."""

M15_BAR_INTERVAL_SECONDS = 900

Q4_START_TS = 1_601_510_400
"""2020-10-01T00:00:00 UTC -- the first Q4 bar's `ts_open`. Independently confirmed against
`AI_TRADER_Q3_Q4_OPERATING_STANDARD_V1.md` section 20 ("first Q4 bar (2020-10-01 00:00:00 UTC)"),
not merely assumed from the source file. Shared by both `fixtures.materialize_sealed_fixture` (which
writes the fixture using this boundary) and `engine.CSVCausalReplayEngine` (which must classify
warm-up-vs-Q4 rows identically when reading that same fixture back) -- defined once here so the two
can never silently drift apart."""

MAX_Q4_BAR_INDEX = 378
"""`AUTHORITATIVE_NEXT_UNSEEN_Q4_BAR` (379) minus one -- the sealed boundary this whole mandate
exists to enforce."""


def hash_file(path: Path) -> str:
    """SHA-256 of a file's actual on-disk bytes, streamed (never loads the whole file into memory at
    once) -- used both by `fixtures.materialize_sealed_fixture` (to record what it wrote) and by
    `SealedReader`/`engine` (to verify what they are about to open still matches what durable state
    or a manifest already recorded, before trusting it)."""
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class SourceIdentity:
    """The full provenance of one sealed bar source. Two `SourceIdentity` values are equal iff every
    field that could change WHICH BARS are being read is identical -- `fingerprint()` rolls all of
    them into one comparable string, and durable-state restore refuses (`SourceIdentityMismatchError`)
    whenever a freshly-opened file's identity does not match what was last committed against."""

    source_file_name: str
    """Basename only (e.g. `Q4_SEALED_1_378.csv`), never an absolute path -- an absolute path is
    machine-specific and would make durable state falsely "mismatch" merely from being restored on a
    different checkout of this repo."""

    content_hash: str
    """SHA-256 of the exact bytes of `source_file_name` at materialization time (`hash_file`)."""

    symbol: str
    timeframe: str
    bar_interval_seconds: int
    first_bar_ts_open: int
    """The sealed file's own first row -- pinned explicitly (not merely implied by row count) so a
    fixture that was accidentally rebuilt starting from the wrong warm-up point is caught by
    `fingerprint()` changing, not silently accepted."""
    sealed_through_bar_index: int
    """The last Q4 bar index (1-based, matching `AI_TRADER_Q4_M15_LOG.md`'s own `BAR N` numbering)
    physically present in this file. `378` for the fixture this mandate materializes. This field
    existing at all is what makes `SealedBoundaryError` a static, file-content fact rather than a
    runtime-only check -- see `sealed_reader.SealedReader`."""
    adapter_version: str = ADAPTER_VERSION
    durable_state_schema_version: str = DURABLE_STATE_SCHEMA_VERSION

    def fingerprint(self) -> str:
        parts = (
            self.source_file_name, self.content_hash, self.symbol, self.timeframe,
            str(self.bar_interval_seconds), str(self.first_bar_ts_open),
            str(self.sealed_through_bar_index), self.adapter_version, self.durable_state_schema_version,
        )
        return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]

    def matches(self, other: "SourceIdentity") -> bool:
        return self.fingerprint() == other.fingerprint()
