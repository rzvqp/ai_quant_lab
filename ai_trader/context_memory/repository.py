"""Append-only, immutable persistence for Context Memory source records -- Phase 7 Checkpoint 10.

**Storage model**: one JSON Lines (``.jsonl``) file per PERSISTED record type, all living under one
repository root directory: ``context_snapshots.jsonl``, ``observations.jsonl``, ``outcomes.jsonl``,
``operational_metadata.jsonl`` (the last added for the Learning/Research Feedback Normative Model,
Addendum §A2 -- encoded/decoded locally in this module rather than via ``codec.py``, since it is a
diagnostic-only record with no cross-package decode consumer today). Each line is one JSON object --
``{"record_id": "<hex>", "sequence": <int>, "payload": {<canonical dict, exactly as produced by
identities.py/codec.py>}}`` -- append-only, human-inspectable, standard-library only (``json`` +
``pathlib`` + ``hashlib`` via ``identities``/``codec``, no third-party dependency, no database).

**Why only 3 files, not 4** -- :class:`~ai_trader.context_memory.contracts.PresentEdgeReference` is
deliberately NOT given its own independent persisted stream. Checkpoint 10's own mission statement
already hedged this ("PresentEdgeReference where independently persisted"): every real
:class:`~ai_trader.context_memory.contracts.PresentEdgeReference` only ever has meaning as part of
"which edges were present in THIS observation" -- there is no legitimate use case for a bare reference
existing on its own, unlike a :class:`~ai_trader.context_memory.contracts.ContextSnapshot` (which CAN
meaningfully exist before/without a matching :class:`~ai_trader.context_memory.contracts.Observation`,
since Market Intelligence could produce one before Edge Intelligence has run for the same ``as_of``).
References remain fully reachable via their parent Observation's own ``present_edges`` tuple.

**A disclosed, deliberate redundancy**: a :class:`ContextSnapshot` embedded inside an
:class:`Observation` and that SAME snapshot ALSO appended standalone will have byte-identical canonical
payloads and IDs (both are the same immutable value) -- this is NOT a second, divergence-risking source
of truth; it is the same fact recorded from two legitimate entry points, and integrity verification
(§below) would catch any impossible divergence immediately.

**Integrity IS identity**: this repository adds no separate "integrity hash" field distinct from each
record's own already-existing deterministic ID (Checkpoint 9) -- verifying a record's integrity means
decoding its stored payload, recomputing its ID from the decoded value, and confirming the result equals
the ``record_id`` the line itself claims. Any mismatch is corruption, always detected, never silently
accepted (Checkpoint 10 §C).

**Duplicate policy** (Checkpoint 10 §B, the one documented policy this repository uses): appending a
record whose ID EXACTLY matches an already-stored record's ID AND whose canonical payload is
byte-identical is IDEMPOTENT -- a silent no-op, returning the existing ID, never a second line written.
Appending a record whose ID matches an existing one but whose payload DIFFERS is impossible for a
correctly-functioning system (the ID is a pure hash of the payload -- two different payloads cannot
share an ID without an actual SHA-256 collision) and is treated as :class:`ConflictingDuplicateError` --
detectable corruption or a codec defect, never silently resolved either way.

**Concurrency** (Checkpoint 10 §F): a documented SINGLE-WRITER-PROCESS contract -- this class does not
provide cross-process file locking (explicitly out of scope: "do not build a complex distributed
concurrency system"). Within ONE process, a :class:`threading.Lock` serializes concurrent
``append_*`` calls against the same :class:`ContextMemoryRepository` instance, tested directly. Running
two SEPARATE processes with writers against the same repository path is unsupported and undefined.

**Failure policy** (Checkpoint 10 §E): every append is followed by an explicit ``flush()`` +
``os.fsync()`` before the method returns, minimizing (never fully eliminating without a WAL, which is
explicitly out of scope) the chance an interrupted write leaves a torn line. On READ, ANY line that
fails to parse as JSON, fails record-type/schema-version checks, or fails ID re-verification raises
immediately -- corrupted or truncated source evidence is NEVER silently skipped or repaired. A
repository root that does not yet exist is created (`Path.mkdir(parents=True, exist_ok=True)`) --
a repository path that exists but is not a directory raises :class:`RepositoryPathError` immediately.
"""

from __future__ import annotations

import json
import os
import threading
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Generic, TypeVar

from ai_trader.context_memory import codec
from ai_trader.context_memory.codec import UnsupportedSchemaVersionError
from ai_trader.context_memory.contracts import (
    CONTEXT_MEMORY_SCHEMA_VERSION,
    ContextSnapshot,
    ContextSnapshotId,
    EdgeEvidenceId,
    Observation,
    ObservationId,
    OperationalMetadata,
    OperationalMetadataId,
    Outcome,
)
from ai_trader.context_memory.enums import ContextRiskDecision
from ai_trader.context_memory.identities import (
    canonical_operational_metadata,
    compute_context_snapshot_id,
    compute_edge_evidence_id,
    compute_observation_id,
    compute_operational_metadata_id,
)
from ai_trader.context_memory.validation import ContextMemoryValidationError

_T = TypeVar("_T")
_IdT = TypeVar("_IdT")


class ContextMemoryRepositoryError(Exception):
    """Base class for every repository-layer (storage/IO/integrity) failure -- deliberately separate
    from :class:`~ai_trader.context_memory.validation.ContextMemoryValidationError`, which covers
    in-memory CONTRACT construction failures, a genuinely different failure domain."""


class RepositoryPathError(ContextMemoryRepositoryError):
    """The repository root path exists but is not usable as a repository directory."""


class RepositoryWriteError(ContextMemoryRepositoryError):
    """A durable append failed at the filesystem level (e.g. read-only filesystem)."""


class RepositoryCorruptionError(ContextMemoryRepositoryError):
    """A stored line could not be parsed, or its recomputed ID does not match its claimed ``record_id``."""


class ConflictingDuplicateError(ContextMemoryRepositoryError):
    """A newly-appended record's ID matches an already-stored record's ID, but the payload differs --
    impossible under a correctly functioning SHA-256 identity, so this is always treated as corruption
    or a codec defect, never resolved silently either way (Checkpoint 10 §B)."""


@dataclass(frozen=True)
class RepositoryIntegrityReport:
    """The result of :meth:`ContextMemoryRepository.verify_integrity` -- every record was re-decoded and
    re-hashed; ``corrupt_lines`` is always empty for a healthy repository."""

    context_snapshot_count: int
    observation_count: int
    outcome_count: int
    corrupt_lines: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.corrupt_lines


def _encode_operational_metadata(metadata: OperationalMetadata) -> dict[str, Any]:
    return canonical_operational_metadata(metadata)


def _decode_operational_metadata(payload: dict[str, Any]) -> OperationalMetadata:
    # Kept local to this module rather than added to codec.py: OperationalMetadata (Learning/Research
    # Feedback Normative Model, Addendum §A2) is a diagnostic-only, repository-internal record with no
    # cross-package decode consumer today, unlike ContextSnapshot/Observation/Outcome. The Learning/
    # Research Feedback Implementation Plan's own file list explicitly does not touch codec.py.
    actual = payload.get("record_type")
    if actual != "context_memory.operational_metadata":
        raise ContextMemoryValidationError(
            f"expected record_type='context_memory.operational_metadata', got {actual!r}"
        )
    raw_schema = payload.get("context_memory_schema_version")
    if (
        not isinstance(raw_schema, dict)
        or raw_schema.get("namespace") != CONTEXT_MEMORY_SCHEMA_VERSION.namespace
    ):
        raise UnsupportedSchemaVersionError(f"missing or malformed context_memory_schema_version: {raw_schema!r}")
    if raw_schema.get("version") != CONTEXT_MEMORY_SCHEMA_VERSION.version:
        raise UnsupportedSchemaVersionError(
            f"unsupported context_memory_schema_version {raw_schema!r} -- this build understands "
            f"{CONTEXT_MEMORY_SCHEMA_VERSION.version!r} only"
        )
    try:
        return OperationalMetadata(
            observation_id=ObservationId(payload["observation_id"]),
            strategy_id=payload["strategy_id"],
            risk_decision=ContextRiskDecision(payload["risk_decision"]),
            denied_reason_code=payload["denied_reason_code"],
            rejection_stage=payload["rejection_stage"],
            strategy_health_policy_state=payload["strategy_health_policy_state"],
        )
    except ContextMemoryValidationError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        raise ContextMemoryValidationError(f"malformed operational_metadata payload: {exc}") from exc


class _JsonlStream(Generic[_T, _IdT]):
    """One append-only ``.jsonl`` file plus its own in-memory identity -> decoded-record lookup dict,
    rebuilt from disk on every :class:`ContextMemoryRepository` construction (Checkpoint 10 §D's own
    "rebuild in-memory lookup state from persisted source records" -- this dict IS that state, and it is
    never itself the source of truth; deleting it and re-opening the repository reproduces it exactly).
    """

    def __init__(
        self, path: Path,
        encode: Callable[[_T], dict[str, Any]], decode: Callable[[dict[str, Any]], _T],
        compute_id: Callable[[_T], _IdT],
    ) -> None:
        self._path = path
        self._encode = encode
        self._decode = decode
        self._compute_id = compute_id
        self._by_id: dict[str, _T] = {}
        self._order: list[str] = []
        self._next_sequence = 0
        self._lock = threading.Lock()
        self._rebuild()

    def _rebuild(self) -> None:
        self._by_id = {}
        self._order = []
        self._next_sequence = 0
        if not self._path.exists():
            return
        with self._path.open("r", encoding="utf-8") as f:
            for line_number, raw_line in enumerate(f, start=1):
                line = raw_line.strip()
                if not line:
                    continue
                self._ingest_line(line, line_number)

    def _ingest_line(self, line: str, line_number: int) -> None:
        try:
            envelope = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RepositoryCorruptionError(
                f"{self._path.name}:{line_number}: line is not valid JSON: {exc}"
            ) from exc
        try:
            record_id = envelope["record_id"]
            sequence = envelope["sequence"]
            payload = envelope["payload"]
        except (KeyError, TypeError) as exc:
            raise RepositoryCorruptionError(f"{self._path.name}:{line_number}: malformed envelope: {exc}") from exc
        try:
            record = self._decode(payload)
        except UnsupportedSchemaVersionError:
            # A genuinely distinct failure mode from generic corruption (Checkpoint 10 §E lists them
            # separately) -- propagated as-is, never wrapped into RepositoryCorruptionError, so a caller
            # can distinguish "this repository is newer/older than the record" from "this record is
            # broken."
            raise
        except ContextMemoryValidationError as exc:
            raise RepositoryCorruptionError(f"{self._path.name}:{line_number}: undecodable payload: {exc}") from exc
        recomputed = self._compute_id(record)
        if getattr(recomputed, "value", recomputed) != record_id:
            raise RepositoryCorruptionError(
                f"{self._path.name}:{line_number}: stored record_id {record_id!r} does not match "
                f"recomputed id {getattr(recomputed, 'value', recomputed)!r} -- corrupted or tampered record"
            )
        self._by_id[record_id] = record
        self._order.append(record_id)
        self._next_sequence = max(self._next_sequence, sequence + 1)

    def append(self, record: _T, record_id_value: str) -> bool:
        """Returns ``True`` if a new line was written, ``False`` if this was an idempotent no-op
        (an exact duplicate already present)."""
        with self._lock:
            existing = self._by_id.get(record_id_value)
            if existing is not None:
                if existing == record:
                    return False
                raise ConflictingDuplicateError(
                    f"{self._path.name}: record_id {record_id_value!r} already exists with different content"
                )
            payload = self._encode(record)
            envelope = {"record_id": record_id_value, "sequence": self._next_sequence, "payload": payload}
            line = json.dumps(envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
            try:
                self._path.parent.mkdir(parents=True, exist_ok=True)
                with self._path.open("a", encoding="utf-8") as f:
                    f.write(line)
                    f.write("\n")
                    f.flush()
                    os.fsync(f.fileno())
            except OSError as exc:
                raise RepositoryWriteError(f"failed to append to {self._path}: {exc}") from exc
            self._by_id[record_id_value] = record
            self._order.append(record_id_value)
            self._next_sequence += 1
            return True

    def get(self, record_id_value: str) -> _T | None:
        return self._by_id.get(record_id_value)

    def iter_in_order(self) -> Iterator[_T]:
        return iter(self._by_id[rid] for rid in self._order)

    def count(self) -> int:
        return len(self._order)

    def verify(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self._path.exists():
            return ()
        with self._path.open("r", encoding="utf-8") as f:
            for line_number, raw_line in enumerate(f, start=1):
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    self._ingest_line_readonly(line, line_number)
                except (RepositoryCorruptionError, ContextMemoryValidationError) as exc:
                    errors.append(f"{self._path.name}:{line_number}: {exc}")
        return tuple(errors)

    def _ingest_line_readonly(self, line: str, line_number: int) -> None:
        # A read-only variant of _ingest_line used only by verify() -- never mutates self._by_id, so
        # verify() can be called freely without affecting the repository's own live lookup state.
        # Deliberately reports EVERY failure mode verify() cares about (bad JSON, malformed envelope,
        # undecodable/unsupported-version payload, ID mismatch) as one uniform corrupt_lines entry --
        # a diagnostic report, unlike _ingest_line's own typed-exception distinction used at rebuild time.
        try:
            envelope = json.loads(line)
            record_id = envelope["record_id"]
            payload = envelope["payload"]
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            raise RepositoryCorruptionError(f"malformed line: {exc}") from exc
        record = self._decode(payload)
        recomputed = self._compute_id(record)
        if getattr(recomputed, "value", recomputed) != record_id:
            raise RepositoryCorruptionError(
                f"stored record_id {record_id!r} does not match "
                f"recomputed id {getattr(recomputed, 'value', recomputed)!r}"
            )


class ContextMemoryRepository:
    """The append-only Context Memory repository -- three independently-streamed record types
    (:class:`ContextSnapshot`, :class:`Observation`, :class:`Outcome`), each backed by one ``.jsonl``
    file under ``root_path``. See the module docstring for the full storage/duplicate/integrity/
    concurrency/failure policy."""

    def __init__(self, root_path: Path) -> None:
        root_path = Path(root_path)
        if root_path.exists() and not root_path.is_dir():
            raise RepositoryPathError(f"{root_path} exists and is not a directory")
        root_path.mkdir(parents=True, exist_ok=True)
        self._root_path = root_path
        self._snapshots = _JsonlStream(
            root_path / "context_snapshots.jsonl",
            codec.encode_context_snapshot, codec.decode_context_snapshot, compute_context_snapshot_id,
        )
        self._observations = _JsonlStream(
            root_path / "observations.jsonl",
            codec.encode_observation, codec.decode_observation, compute_observation_id,
        )
        self._outcomes = _JsonlStream(
            root_path / "outcomes.jsonl",
            codec.encode_outcome, codec.decode_outcome, compute_edge_evidence_id,
        )
        self._operational_metadata = _JsonlStream(
            root_path / "operational_metadata.jsonl",
            _encode_operational_metadata, _decode_operational_metadata, compute_operational_metadata_id,
        )

    # ------------------------------------------------------------------ append (single)

    def append_context_snapshot(self, snapshot: ContextSnapshot) -> ContextSnapshotId:
        record_id = compute_context_snapshot_id(snapshot)
        self._snapshots.append(snapshot, record_id.value)
        return record_id

    def append_observation(self, observation: Observation) -> ObservationId:
        record_id = compute_observation_id(observation)
        self._observations.append(observation, record_id.value)
        return record_id

    def append_outcome(self, outcome: Outcome) -> EdgeEvidenceId:
        record_id = compute_edge_evidence_id(outcome)
        self._outcomes.append(outcome, record_id.value)
        return record_id

    def append_operational_metadata(self, metadata: OperationalMetadata) -> OperationalMetadataId:
        record_id = compute_operational_metadata_id(metadata)
        self._operational_metadata.append(metadata, record_id.value)
        return record_id

    # ------------------------------------------------------------------ append (batch)
    # IMPLEMENTATION CHOICE (Checkpoint 10 §D): batch append preserves the caller-supplied order exactly
    # (sequence numbers are assigned in that order) -- there is no meaningful "canonical" ordering to
    # normalize independent records to. Batch append is NOT transactional: each item is appended
    # independently and durably; a failure partway through leaves prior items already persisted, a
    # disclosed simplicity choice ("do not build a complex distributed concurrency system").

    def append_context_snapshots(self, snapshots: Sequence[ContextSnapshot]) -> tuple[ContextSnapshotId, ...]:
        return tuple(self.append_context_snapshot(s) for s in snapshots)

    def append_observations(self, observations: Sequence[Observation]) -> tuple[ObservationId, ...]:
        return tuple(self.append_observation(o) for o in observations)

    def append_outcomes(self, outcomes: Sequence[Outcome]) -> tuple[EdgeEvidenceId, ...]:
        return tuple(self.append_outcome(o) for o in outcomes)

    def append_operational_metadatas(
        self, items: Sequence[OperationalMetadata]
    ) -> tuple[OperationalMetadataId, ...]:
        return tuple(self.append_operational_metadata(m) for m in items)

    # ------------------------------------------------------------------ read by identity

    def get_context_snapshot(self, record_id: ContextSnapshotId) -> ContextSnapshot | None:
        return self._snapshots.get(record_id.value)

    def get_observation(self, record_id: ObservationId) -> Observation | None:
        return self._observations.get(record_id.value)

    def get_outcome(self, record_id: EdgeEvidenceId) -> Outcome | None:
        return self._outcomes.get(record_id.value)

    def get_operational_metadata(self, record_id: OperationalMetadataId) -> OperationalMetadata | None:
        return self._operational_metadata.get(record_id.value)

    # ------------------------------------------------------------------ deterministic iteration
    # "filter by record type" (Checkpoint 10 §D) is satisfied structurally: each stream already IS one
    # record type, so iterating a specific stream's own method already is the filter -- no generic
    # "iterate all, filter by type" API is needed since no interleaved, multi-type stream ever exists.

    def iter_context_snapshots(self) -> Iterator[ContextSnapshot]:
        return self._snapshots.iter_in_order()

    def iter_observations(self) -> Iterator[Observation]:
        return self._observations.iter_in_order()

    def iter_outcomes(self) -> Iterator[Outcome]:
        return self._outcomes.iter_in_order()

    def iter_operational_metadata(self) -> Iterator[OperationalMetadata]:
        return self._operational_metadata.iter_in_order()

    # ------------------------------------------------------------------ counts

    def count_context_snapshots(self) -> int:
        return self._snapshots.count()

    def count_observations(self) -> int:
        return self._observations.count()

    def count_outcomes(self) -> int:
        return self._outcomes.count()

    def count_operational_metadata(self) -> int:
        return self._operational_metadata.count()

    # ------------------------------------------------------------------ integrity / rebuild

    def verify_integrity(self) -> RepositoryIntegrityReport:
        errors = (
            *self._snapshots.verify(),
            *self._observations.verify(),
            *self._outcomes.verify(),
        )
        return RepositoryIntegrityReport(
            context_snapshot_count=self.count_context_snapshots(),
            observation_count=self.count_observations(),
            outcome_count=self.count_outcomes(),
            corrupt_lines=errors,
        )

    def rebuild(self) -> None:
        """Re-reads every ``.jsonl`` file from disk into a fresh in-memory lookup state -- for a reader
        that wants to observe records another process/instance appended since this instance was opened.
        Raises :class:`RepositoryCorruptionError` immediately on any corrupt line, exactly like
        construction does."""
        self._snapshots._rebuild()
        self._observations._rebuild()
        self._outcomes._rebuild()
        self._operational_metadata._rebuild()

    @property
    def root_path(self) -> Path:
        return self._root_path
