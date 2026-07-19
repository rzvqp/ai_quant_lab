# Phase 7 — Checkpoint 10: Append-Only Context Repository

**Validation label: TARGETED VALIDATION PASSED.** Per this batch's own validation policy, only the
`context_memory` package's own tests, `mypy --strict` scoped to the package, and targeted coverage were
run at this checkpoint's own close — the combined-batch full-suite run happens once, after Checkpoint 13.

## 1. Storage Format

One JSON Lines (`.jsonl`) file per persisted record type, all under one repository root directory:
`context_snapshots.jsonl`, `observations.jsonl`, `outcomes.jsonl`. Each line is one JSON envelope:

```json
{"record_id": "<hex sha256>", "sequence": <int>, "payload": {<the exact canonical dict Checkpoint 9's identities.py/Checkpoint 10's codec.py already produce>}}
```

Standard library only (`json`, `pathlib`, `hashlib` via `identities.py`) — no database, no third-party
dependency, human-inspectable with any text editor.

**Only 3 files, not 4** — `PresentEdgeReference` is deliberately NOT given an independent persisted
stream, resolving the mission statement's own hedge ("PresentEdgeReference where independently
persisted"). Every real `PresentEdgeReference` only has meaning as "which edges were present in THIS
observation" — there is no legitimate standalone use case, unlike `ContextSnapshot`, which CAN
meaningfully exist before/without a matching `Observation` (Market Intelligence could produce one before
Edge Intelligence has run for the same `as_of`). References remain fully reachable via their parent
`Observation.present_edges`.

**A disclosed, deliberate redundancy**: a `ContextSnapshot` embedded inside an `Observation` and that
SAME snapshot ALSO appended standalone have byte-identical canonical payloads and IDs — not a
divergence-risking second source of truth, since both are the same immutable value from two legitimate
entry points; integrity verification would catch any impossible divergence immediately.

## 2. Append Semantics

`append_context_snapshot()`/`append_observation()`/`append_outcome()` each compute the record's own
deterministic ID (Checkpoint 9), append one line, and durably flush (`f.flush()` + `os.fsync()`) before
returning. Batch variants (`append_context_snapshots()` etc.) preserve caller-supplied order exactly
(sequence numbers assigned in that order — no "canonical" reordering exists for independent records) and
are explicitly NOT transactional: a failure partway through a batch leaves prior items already durably
persisted, a disclosed simplicity choice ("do not build a complex distributed concurrency system").

## 3. Duplicate Policy

The one documented policy (Checkpoint 10 §B): appending a record whose ID exactly matches an
already-stored record's ID AND whose canonical payload is byte-identical is **idempotent** — a silent
no-op returning the existing ID, never a second line. Appending a record whose ID matches an existing one
but whose payload differs is impossible for a correctly-functioning system (the ID is a pure SHA-256 hash
of the payload) and is raised as `ConflictingDuplicateError` — detectable corruption or a codec defect,
never resolved either way. Because the public Repository API always computes IDs fresh from the object
being appended, this conflict is structurally unreachable through normal use; it is proven directly
against the internal `_JsonlStream.append()` (which accepts an explicit `record_id_value`), a deliberate
white-box test for defense-in-depth.

## 4. Integrity Mechanism

**Integrity IS identity** — no separate "integrity hash" field exists distinct from each record's own
already-existing deterministic ID. Verifying integrity means decoding the stored payload, recomputing its
ID from the decoded value, and confirming the result equals the claimed `record_id`; any mismatch is
corruption, always detected on read (both at repository construction/rebuild AND via the standalone
`verify_integrity()` method, which never mutates live state), never silently accepted.

## 5. Failure Behavior

| Scenario | Behavior |
|---|---|
| Interrupted/partial write | Minimized via `flush()`+`fsync()` per append (never fully eliminated without a WAL, explicitly out of scope); any resulting torn line is caught as corruption on the next read, never silently repaired |
| Duplicate append | Idempotent (exact) / `ConflictingDuplicateError` (conflicting) — §3 |
| Invalid payload | Rejected before ever being written — the repository only ever receives already-`__post_init__`-validated contract instances |
| Corrupted payload | `RepositoryCorruptionError` on read (bad JSON, malformed envelope, undecodable payload, or ID mismatch) |
| Unsupported schema version | `UnsupportedSchemaVersionError` (a `codec.py` type, itself a `ContextMemoryValidationError`) — deliberately NOT wrapped into `RepositoryCorruptionError`, so a caller can distinguish "this repository is newer/older than the record" from "this record is broken" |
| Repository path missing | Auto-created (`Path.mkdir(parents=True, exist_ok=True)`) |
| Repository path invalid (a file, not a directory) | `RepositoryPathError` at construction |
| Read-only filesystem / write failure | `RepositoryWriteError`, wrapping the underlying `OSError` |

Source evidence is never silently repaired anywhere in this checkpoint.

## 6. Concurrency Policy

A documented **single-writer-process** contract — no cross-process file locking is provided (explicitly
out of scope: "do not build a complex distributed concurrency system"). Within one process, a
`threading.Lock` per `_JsonlStream` serializes concurrent `append()` calls against the same repository
instance — tested directly with 4 threads racing to append the same 20 records, confirmed to leave
exactly 20 distinct records (idempotency + the lock together prevent any race-induced duplication or
corrupted count). Two separate PROCESSES writing to the same repository path is unsupported and
undefined — disclosed, not silently assumed safe.

## 7. Files Changed

New: `ai_trader/context_memory/codec.py`, `ai_trader/context_memory/repository.py`,
`ai_trader/context_memory/tests/test_codec.py`, `ai_trader/context_memory/tests/test_repository.py`.
Modified: `ai_trader/context_memory/__init__.py` (new exports for the repository's public surface),
`ai_trader/context_memory/identities.py` (its own private `_canonical_*`/`_hash_canonical` helpers
promoted to package-internal, non-underscore names — `canonical_context_snapshot()` etc. — so `codec.py`
can reuse them for its ENCODE direction rather than duplicating that logic; a pure rename, no behavior
changed, re-verified by re-running every existing Checkpoint 9 test unmodified), and
`ai_trader/context_memory/tests/test_public_api.py` (expanded expected-export set). No file outside
`ai_trader/context_memory/` was touched.

## 8. Tests

150 total tests in the package (92 from Checkpoint 9, unchanged, + 32 new `test_codec.py`/
`test_repository.py` tests + 8 new gap-closing tests added during coverage closure = 132 tests actually
new/modified this checkpoint, 132 total passing in the full package run). Every category from Checkpoint
10 §G covered: first append, repeated exact append (idempotent), conflicting duplicate (white-box),
deterministic batch append (order-preserving), read by ID, read missing ID (returns `None`), deterministic
iteration, record-type isolation (trivially satisfied — each stream is already one type, verified by
type-checking every yielded record), reopen and rebuild (two independent instances against the same
path; explicit `rebuild()` picking up a second writer's changes), integrity verification (healthy +
corrupt), malformed record detection, truncated record detection, unsupported schema detection, invalid
path behavior, source records remain unchanged after append, no future-data field survives the round
trip, concurrent-append serialization, and the codec's own round-trip/malformed/schema-mismatch tests.

## 9. Targeted Coverage

```
coverage report (--source=ai_trader.context_memory, --omit tests/):
    __init__.py         7 stmts   0 miss   100%
    codec.py            62 stmts   0 miss   100%
    contracts.py       145 stmts   0 miss   100%
    enums.py             59 stmts   0 miss   100%
    identities.py        28 stmts   0 miss   100%
    repository.py       185 stmts   0 miss   100%
    validation.py         32 stmts   0 miss   100%
    TOTAL                518 stmts   0 miss   100%
```

Every module in the package (Checkpoint 9's carried-forward modules AND this checkpoint's new ones)
reaches 100% targeted coverage — satisfying §I's requirement across the whole package, not just the new
files. A first coverage run surfaced 14 missed lines in `repository.py` (blank-line-skip branches,
malformed-envelope/undecodable-payload exception branches, the write-failure wrapper, three
never-directly-called read/batch methods, and the `root_path` property) — all closed with 8 additional
targeted tests, including one using `monkeypatch` to simulate an `os.fsync` failure for the
`RepositoryWriteError` path, before reaching the number above.

## 10. mypy Result

```
mypy --strict ai_trader/context_memory/ --exclude 'tests/'
    -> Success: no issues found in 7 source files (up from 5 at Checkpoint 9)
```

## 11. Deferred Functionality (explicit confirmation, Checkpoint 10 §H)

**No episode collapsing, historical similarity, relaxation ladders, contextual statistics, evidence
sufficiency, or Decision Intelligence integration was implemented anywhere in this checkpoint.** This
package can now durably store and retrieve immutable source records and verify their integrity —
nothing more. `repository.py` never imports `market_intelligence`, `edge_intelligence`,
`shadow_evidence`, `decision_intelligence`, or any execution-adjacent package (grep/AST-verified, §12).

## 12. Protected-Path and Import-Independence Verification

`git status --porcelain` before staging showed exactly the files listed in §7 — nothing under `code/`,
`results/`, `knowledge/`, or any other `ai_trader/` package. The existing static AST-based
`test_import_independence.py` (Checkpoint 9) automatically covers `codec.py`/`repository.py` too (it
scans every top-level `.py` file in the package directory, not a fixed file list) — re-run and confirmed
passing, zero forbidden imports, zero `"harness"` string reference anywhere in the package.

## 13. Commit Hash / Branch / Working Tree Status

- Branch: `ai-trader-implementation`
- Parent commit: `30213d0adf5c3fb6f2d860a84c8a81bc4b848cb2` (Checkpoint 9)
- This checkpoint's commit hash: recorded after commit, see final session output.
- Working tree: clean after commit, verified before Checkpoint 11 begins.
