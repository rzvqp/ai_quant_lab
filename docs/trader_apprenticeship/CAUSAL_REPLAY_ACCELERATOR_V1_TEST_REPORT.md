# CAUSAL_REPLAY_ACCELERATOR_V1 — TEST REPORT

**Suite**: `tradingview-mcp/tests/causal_replay.test.js`. **Result: 34/34 passing** (30 mandate
`T01`-`T30` requirements — several consolidated into one `it()` where they test the same code path,
noted below — plus 4 explicit adversarial-injection scenarios from mandate §15).

All fixtures are synthetic (`BASE_T = 2,500,000,000`, calendar year ~2049 — nowhere near 2020Q4).
Zero live CDP calls anywhere in this suite (T29/T30 assert this mechanically, see below).

## Mapping (mandate §14)

| # | Requirement | Test(s) | Result |
|---|---|---|---|
| T01 | FUTURE_BAR_INACCESSIBLE | `T01/T04/T05` suite, both `it()`s | PASS |
| T02 | CURRENT_POINTER_ONLY | `T02/T03` suite | PASS |
| T03 | EXACTLY_ONE_BAR_ATOMIC_STEP | `T02/T03` suite | PASS |
| T04 | NO_FUTURE_OHLC | `T01/T04/T05` suite | PASS |
| T05 | NO_FUTURE_VOLUME | `T01/T04/T05` suite | PASS |
| T06 | NO_FUTURE_INDICATOR_STATE | `T06/T07` suite | PASS |
| T07 | NO_FUTURE_PINE_STATE | `T06/T07` suite | PASS |
| T08 | POINTER_LOCK_BEFORE_DECISION_COMMIT | `T08/T09` suite, 3 `it()`s (incl. Layer B) | PASS |
| T09 | NEXT_BAR_UNLOCK_AFTER_DECISION_ONLY | `T08/T09` suite | PASS |
| T10 | TRADE_CONTRACT_FROZEN_BEFORE_NEXT_BAR | `T10` suite, 2 `it()`s (incomplete-refused, complete-accepted) | PASS |
| T11 | P007_PRECLASSIFIED_BEFORE_RESOLUTION | `T11` suite | PASS |
| T12 | MGMT004_TRIGGER_CAUSAL | `T12` suite | PASS |
| T13 | NO_TRADE_DECISION_CAUSAL | `T13` suite | PASS |
| T14 | EVENT_GATE_STOPS_ON_CURRENT_EVENT | `T14/T15` suite | PASS |
| T15 | HEARTBEAT_MAX_8_BARS | `T14/T15` suite, 2 `it()`s (ceiling + no-bar-skipped) | PASS |
| T16 | CRASH_RESTART_NO_SKIP | `T16/T17` suite | PASS |
| T17 | CRASH_RESTART_NO_DUPLICATE | `T16/T17` suite | PASS |
| T18 | RETRY_IDEMPOTENCY | `T18` suite | PASS |
| T19 | TIMESTAMP_MONOTONICITY | `T19/T20` suite | PASS |
| T20 | GAP_HANDLING | `T19/T20` suite, 2 `it()`s (classification + gate trigger) | PASS |
| T21 | DATA_ANOMALY_HANDLING | `T21` suite | PASS |
| T22 | H1_AGGREGATION_CAUSAL | `T22/T23` suite | PASS |
| T23 | H4_AGGREGATION_CAUSAL | `T22/T23` suite | PASS |
| T24 | CACHE_STATE_EQUALS_CANONICAL | `T24` suite | PASS |
| T25 | NO_BUFFER_VISIBILITY_TO_DECISION_LAYER | `T25` suite | PASS |
| T26 | DECISION_HASH_IMMUTABILITY | `T26` suite | PASS |
| T27 | EVENT_GATE_VERSION_PINNED | `T27/T28` suite | PASS |
| T28 | REPLAY_SOURCE_IDENTITY_PINNED | `T27/T28` suite | PASS |
| T29 | (source-scan: no live connection import) | `T29` suite | PASS |
| T30 | BAR_379_NEVER_ACCESSED_DURING_TESTS | `T30` suite, 2 `it()`s | PASS |

## Adversarial injection (mandate §15) — 4 scenarios, all PASS

1. **Crash between reveal and commit, then a stale resume belief** — the handshake correctly fails
   closed rather than silently continuing from the wrong bar.
2. **Duplicate/racing commit calls** — exactly one of two concurrent commit attempts for the same
   bar succeeds; the other is refused, not double-applied.
3. **Stale-pointer "rewind" attempt** — an attempt to re-assert an earlier bar as current (as if
   trying to make an already-seen bar look unseen again) is refused, not honored.
4. **Unclassifiable decision_type** — a made-up decision type is refused (`UNKNOWN_DECISION_TYPE`),
   never silently guessed into one of the known categories.

## A bug this suite itself caught, before being counted as coverage (disclosed, not hidden)

Two of this suite's own early drafts (the T20/T05 predecessors of what is now `T01/T04/T05`'s
"end-to-end proof") initially checked only the standalone `causal_bucket_asof`-equivalent-shaped
helper output, not `causalStepSnapshot`'s own actual returned values — meaning they would have kept
passing even if the exposed tool itself regressed to a lookahead-unsafe formula. Caught by the same
revert-and-confirm-failing discipline used elsewhere in this project: `causalStepSnapshot`/`like_at`-
equivalent behavior was temporarily reverted in-memory (no file touched), the flawed tests were
confirmed to still incorrectly pass, then rewritten to assert against the tool's own output
directly, and reconfirmed to correctly fail under the reverted logic before being restored and
counted as real coverage. (This specific pattern is more fully documented for the sibling
CURRENT-REGIME mandate closed the same day — see `[[ve-current-regime-causality-repair]]` in VE's
own memory record — the same discipline was applied here independently.)

Separately, three fixture-construction bugs (not production-code bugs) were found and fixed during
development: an overlapping-OHLC-range fixture that made the structural-level-touch test ambiguous
about which bar it fired on; a "stale pointer" crash-restart test that never actually advanced past
the bar it claimed to be stale relative to (so there was nothing to mismatch); and a
self-referential source-scan check whose own forbidden-string list contained the literal string it
was searching for. All three were root-caused via direct debugging (an isolated reproduction script
for the pointer case) before being fixed — not patched by weakening the assertion.

## Full repository regression

`tests/replay.test.js` + `tests/pine_analyze.test.js` + `tests/causal_replay.test.js`: **95 tests,
95 passed, 0 failed** after the `data.js` DI refactor (§3 of the implementation doc) — confirming
the minimal, behavior-preserving nature of that change. `tests/sanitization.test.js`'s own
pre-existing, unrelated failure (a Windows path-construction bug in that test file's own harness,
reproduced identically against the unmodified `main` branch via `git stash`) is disclosed here, not
silently worked around — it is out of this mandate's scope (§21: do not touch other systems) and
was not introduced by anything in this mandate.

## mypy / type-check note

This repo is a pure JavaScript/Node project (no Python, no mypy). The equivalent standard-tooling
check applied here is `node --check` (syntax) on every touched/new file plus the full test-runner
pass above — both clean.
