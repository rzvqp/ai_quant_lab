# CAUSAL_REPLAY_ACCELERATOR_V1 — IMPLEMENTATION

**Mandate**: `VE_CAUSAL_REPLAY_ACCELERATOR_V1` (implementation + adversarial testing). Builds the
architecture `CAUSAL_REPLAY_ACCELERATOR_V1_DESIGN.md` scoped as feasible (Option E foundation —
Option B's atomic tool — plus, per this mandate's own explicit authorization, a conservative
event-gated Layer B the design doc itself did not recommend as primary; see §5 below for the
disclosed trade-off this carries).

**Q4 pointer status: UNCHANGED.** `LAST_CONSUMED_BAR = 378`, `NEXT_UNSEEN_BAR = 379`. No
`replay_step`/`replay_start`/`replay_autoplay`/`replay_trade`/`replay_stop` call — mocked or real —
was made against the live connection anywhere in this implementation's own development or test
process; see §6.

---

## 1. Ownership (mandate §22 — identified before any mutation, not assumed)

```
OWNING_COMPONENT     = tradingview-mcp server, C:\Users\MEDION GAMING\tradingview-mcp (this repo)
BRANCH               = main
LIKELY_FILES_MODULES = src/core/replay.js (read only, unmodified), src/core/data.js
                       (getOhlcv/getPineTables given a _deps injection seam, behavior-preserving),
                       new: src/core/causal_replay.js, src/tools/causal_replay.js
```

Confirmed by direct inspection before writing any code: `replay_step`/`data_get_ohlcv`/
`data_get_pine_tables` are implemented in `src/core/replay.js`/`src/core/data.js` in this exact
repo, registered as MCP tools in `src/tools/replay.js`/`src/tools/data.js` and wired into
`src/server.js`. `replay.js` already used a `_deps.evaluate`/`_deps.getReplayApi` injection seam
(pre-existing, proven by `tests/replay.test.js`) enabling fully-mocked unit testing without any
live CDP connection; `data.js` did not have this seam and needed the same minimal addition (§3).

There is **no server-side persisted replay pointer anywhere in this codebase** — `core/replay.js`
reads the live TradingView Desktop instance's own JS replay API (`currentDate()`, `doStep()`, etc.)
via CDP `evaluate()` calls, every time. This has a direct safety consequence: `replay_start` does
not "seek to an earlier point" in an existing session, it **re-initializes the whole replay
session** — meaning even a "test with an earlier date" call would risk destroying the live Q4
apprenticeship's own current position. This finding governed the entire safety posture of this
implementation (§6).

## 2. Architecture delivered

```
LAYER A: causalStepSnapshot()  — src/core/causal_replay.js, exposed as causal_step_snapshot
LAYER B: causalRunUntilGate()  — src/core/causal_replay.js, exposed as causal_run_until_gate
Decision-commit handshake:       causalCommitDecision(), exposed as causal_commit_decision
Read-only status:                exposed as causal_replay_status
```

### Layer A — atomic causal single-bar snapshot

Composes the EXISTING, unmodified `replayCore.step()` + `replayCore.status()` +
`dataCore.getOhlcv({count:1})` + `dataCore.getPineTables()` into one function call (`_stepAndSnapshot`
internally), returning: bar timestamp, OHLC, the full Pine-table read (where
`AI_TRADER_CONTEXT_V1`'s own H4/H1/session/structural fields already live — passthrough, not
reimplemented, see §4), position, a gap/anomaly classification, and a SHA-256 state fingerprint.
Refuses to run (`DECISION_COMMIT_REQUIRED`) if the previously-revealed bar has not been committed.

### Decision-commit handshake

Every `causalStepSnapshot()`/`causalRunUntilGate()` call sets an in-memory `_pendingCommit` flag
for the bar it just revealed. The next call of either is refused until `causalCommitDecision()`
clears it. **Every bar requires an explicit commit, even routine ones** (`decision_type:
"ROUTINE_NO_EVENT"`, no fields required) — this was a deliberate design choice over a "only commit
special bars" scheme: the server cannot itself judge which bars are decision-bearing (that
requires the reasoning layer's own judgment, which this implementation must not replicate — mandate
§11/§21), so making commit mandatory for every bar is the only way to mechanically guarantee no bar
is silently skipped past without SOME acknowledgment, while still making the five required-event
types (`TRADE_CONTRACT`, `P007_PRECLASSIFICATION`, `P007_RESOLUTION`, `MGMT004_TRIGGER`,
`NO_TRADE_ACTIONABLE`) carry their own mandatory field sets (mandate §7-10) enforced at commit time.

```
READY_TO_REVEAL -> [causalStepSnapshot] -> CURRENT_BAR_REVEALED (_pendingCommit set)
  -> WAITING_FOR_DECISION_COMMIT (any further step call refused)
  -> [causalCommitDecision] -> DECISION_COMMITTED (_pendingCommit cleared)
  -> NEXT_BAR_UNLOCKED
```

Crash-recovery (mandate §16/§20) does **not** depend on persisting this flag to disk — the one
durable ground truth is TradingView's own live pointer (§1). Every call after a session's first
should supply `expected_pointer_before` (the bar_id the caller last durably recorded); the
implementation cross-checks it against the live pointer in the SAME `status()` read already needed
for stepping (folded together, not a second round-trip) and fails closed (`POINTER_MISMATCH`) on any
disagreement — this is what actually makes crash-restart safe, not the in-memory flag.

### Layer B — conservative causal event-gated runner

Steps up to `MAX_HEARTBEAT_BARS = 8` bars internally in one call, evaluating only MECHANICALLY
computable event gates per bar (§4), stopping at the first firing gate or at the 8-bar ceiling.
Every bar processed — including routine ones the reasoning layer never individually narrates — is
still listed in the response's `bars_processed` array; none are silently dropped from the record.

## 3. `data.js` DI refactor (minimal, behavior-preserving)

`getOhlcv`/`getPineTables` now accept an optional `_deps.evaluate` override, mirroring
`replay.js`'s own established pattern exactly (default to the real import, override only when
supplied). No other behavior changed — verified: `tests/replay.test.js`,
`tests/pine_analyze.test.js`, and `tests/sanitization.test.js` (a pre-existing, unrelated Windows
path-construction bug in that file's own test harness aside — reproduced identically against the
unmodified code via `git stash`, disclosed not fixed, out of this mandate's scope) all still pass.

## 4. Canonical source / Pine parity (mandate §12)

H4/H1 context, structural levels, session metadata, and active-thesis fields are **already
Pine-canonical** — computed by the `AI_TRADER_CONTEXT_V1` indicator and read via the existing,
unmodified `getPineTables()`. This implementation chose **option B (keep the canonical calculation
source)**: Layer A/B bundle the EXISTING Pine-table read unchanged; nothing is reimplemented in
JS. No new indicator, level, or trigger logic was written anywhere in this module.

## 5. Event gate coverage — explicit, disclosed limitation

Mandate §3 lists 15 gate categories. Only 3 are mechanically evaluable from data already exposed by
the existing tools without inventing new market intelligence:

```
MECHANICALLY_GATED (EVENT_GATE_VERSION 1.0.0):
  STRUCTURAL_LEVEL_TOUCH        — close/range within tolerance of a caller-registered price
  MATERIAL_VOLATILITY_TRANSITION — bar range >= a caller-registered ATR-multiple
  GAP_OR_INTEGRITY_ANOMALY      — from the same gap classification Layer A always computes
```

The remaining 12 (active-thesis trigger, structural acceptance/rejection, H1/H4 structural-state
transition, P007/pattern/trade-setup eligibility, NO_TRADE decision surface, open-trade management
event, MGMT-004 eligibility/trigger, stop/target interaction, regime-transition candidate,
periodic heartbeat) are **not** mechanically pre-filtered — Layer B never attempts to classify them
per-bar. They are covered only by the 8-bar heartbeat ceiling (mandate §4's own required fallback),
meaning the reasoning layer sees a full snapshot at least once every 8 bars regardless, but a
routine-classified stretch of up to 7 bars could in principle contain one of these 12 event types
without Layer B stopping early for it.

**This is the same real, disclosed trade-off `CAUSAL_REPLAY_ACCELERATOR_V1_DESIGN.md` already
identified for its own Option D** ("a plausible source of a subtle gate-definition bug that
silently drops a genuine trigger") **and explicitly recommended against making primary for exactly
this reason.** This mandate authorized building Layer B anyway ("if mechanically safe") — it is
built, tested, and available, but this limitation is not silently resolved: recommended usage is
Layer A (`causal_step_snapshot`) as the default for any stretch the reasoning layer has any reason
to think might be decision-bearing, and Layer B (`causal_run_until_gate`) reserved for stretches
already known/expected to be routine (e.g. thin overnight sessions), with its own 8-bar ceiling as
the safety net — never as a blanket replacement for Layer A. See the handoff doc for the concrete
recommendation.

## 6. Zero live-connection interaction during this entire mandate

Every line of implementation, every test, and the benchmark script use exclusively the
`_deps.evaluate`/`_deps.getReplayApi` mock injection seam. No `mcp__tradingview__replay_*` tool
(or any other live TradingView tool) was invoked at any point during this mandate. This was a
deliberate, absolute constraint (not merely "avoid consuming bar 379") — see §1's own finding that
even `replay_start` with an earlier test date would risk destroying the live session's current
position, which ruled out any live-connection testing whatsoever, not just replay_step calls.

## 7. Versioning (mandate §23)

```
CAUSAL_REPLAY_ACCELERATOR_VERSION = 1.0.0
EVENT_GATE_VERSION                = 1.0.0
STATE_SCHEMA_VERSION              = 1.0.0
INTEGRITY_PROTOCOL_VERSION        = 1.0.0
```

Every response from `causal_step_snapshot`/`causal_run_until_gate` carries all four. A future
change to event-gate semantics requires bumping `EVENT_GATE_VERSION` — enforced by convention, not
mechanically (no other version currently gates behavior; this is disclosed, not hidden).
