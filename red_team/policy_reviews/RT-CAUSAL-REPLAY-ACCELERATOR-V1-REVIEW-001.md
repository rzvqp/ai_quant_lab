# RED TEAM — CAUSAL REPLAY ACCELERATOR V1 · NO-LOOKAHEAD / PROSPECTIVE-INTEGRITY AUDIT
### RT-CAUSAL-REPLAY-ACCELERATOR-V1-REVIEW-001 · Auditor: Red Team · 2026-08-30

Independent adversarial review of `VE_CAUSAL_REPLAY_ACCELERATOR_V1` (commit `cf6f470`). No trust extended to
VE's PASS. Live Q4 replay NOT resumed; no TradingView replay tool called (the MCP replay tools were disconnected
for this session); **bar 379 not accessed**. Accelerator code not modified.

---

## 0 — REQUIRED FINAL VERDICT

```
RED_TEAM_ACCELERATOR_REVIEW_COMPLETE = YES
ARTIFACT_COMMIT = cf6f470cd311ae1ff9a35ae72fd0c9edaed67ec6
REMOTE_IDENTITY_VERIFIED = YES

ATOMIC_MODE_VERDICT = PASS
HYBRID_MODE_VERDICT = PASS

FUTURE_BAR_INACCESSIBLE = PASS
NO_FUTURE_INDICATOR_LEAK = PASS
POINTER_LOCK = PASS
DECISION_COMMIT_HANDSHAKE = PASS
CRASH_RECOVERY = PASS

TRADE_CONTRACT_PROTECTION = PASS
P007_PROSPECTIVE_PROTECTION = PASS
MGMT004_CAUSALITY = PASS
NO_TRADE_PROSPECTIVE_PROTECTION = PASS
HEARTBEAT_ENFORCEMENT = PASS

APPRENTICESHIP_INFORMATION_LOSS = MODERATE

BLOCKING_FINDINGS = NONE
NONBLOCKING_FINDINGS = 4 (see §15)

RED_TEAM_VERDICT = PASS_WITH_NONBLOCKING_NOTES
SAFE_FOR_AI_TRADER_Q4 = YES (conditional on the HYBRID usage contract in §15 note 1)

AUTHORITATIVE_LAST_CONSUMED_Q4_BAR = 378
AUTHORITATIVE_NEXT_UNSEEN_Q4_BAR = 379
BAR_379_ACCESSED = NO
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

## 1 — ARTIFACT IDENTITY (§2)

| check | result |
|---|---|
| remote `rzvqp/tradingview-mcp-aql`, branch `integration/causal-replay-accelerator-v1` tip | `cf6f470` — **REMOTE_COMMIT_MATCH = YES** (read-only fetch) |
| local `cf6f470` exists, audited the committed tree | YES (worktree `src/core/causal_replay.js` + `tests/causal_replay.test.js` byte-identical to `cf6f470`) |
| files in the commit | `src/core/causal_replay.js` (310), `src/tools/causal_replay.js` (50), `tests/causal_replay.test.js` (518), `causal_replay_benchmark.mjs`, `src/core/data.js` (+`_deps` seam, 10 lines), `src/server.js` (2), `.gitignore` |
| scope | composes the **existing, unmodified** `replay.js step()/status()` + `data.js getOhlcv()/getPineTables()`; computes NO new market intelligence (verified: no indicator/level/trigger logic of its own) |

The `data.js` change is a behavior-preserving `_deps` injection seam (`_eval = _deps?.evaluate || evaluate`), defaulting to the real `evaluate` — a test seam, no production behavior change.

## 2 — FUTURE-ISOLATION BOUNDARY (§5) — no leakage found

`_stepAndSnapshot` does: `status()` (read pointer, verify `expected_pointer_before`) → `step()` (advance ONE bar)
→ `getOhlcv({count:1})` (the just-revealed current bar only) + `getPineTables()` (current Pine state). The
snapshot exposes exactly the current bar's `ohlc`, `pine_state`, `position`, gap status. **No future OHLC / volume
/ indicator / Pine / next-bar field is read or returned** (tests T01/T04/T05/T06/T07; response schema scanned for
`next_bar`/`future`/`lookahead` — absent). The no-lookahead property at the CDP level is **inherited** from the
existing replay/data primitives (unchanged); the accelerator changes only how many round-trips it takes, not
what is returned. Source-scan (T373) confirms **no memoization/cache layer** carrying state across steps.

## 3 — TWO MODES (§4)

| | ATOMIC (`causalStepSnapshot`) | HYBRID (`causalRunUntilGate`) |
|---|---|---|
| FUTURE_INFORMATION_EXPOSURE | **NO** — one bar per call | **NO** at module level — bars revealed sequentially, one `step()` at a time, gate evaluated AFTER each; stops at the first mechanical gate or the 8-bar heartbeat; every bar listed in `bars_processed`, none pre-fetched or skipped (T14/T15) |
| POINTER_ADVANCE_SAFE | **YES** — refuses to step while a commit is pending | **YES** — refuses to start while a commit is pending; `cap = min(max_bars, 8)` |
| DECISION_FREEZE_SAFE | **YES** — every bar gets a pending commit, must be committed before the next | **Partial/conditional** — only the FINAL (gated/heartbeat) bar gets a pending commit; intermediate ROUTINE bars advance without an individual freeze. Reasoning-dependent decision bars are protected only by the mechanical gates + the heartbeat ceiling + correct usage (see §15 note 1) |
| CRASH_RECOVERY_SAFE | **YES** (§4 below) | **YES** (same pointer-mismatch mechanism) |

The two modes do **not** carry identical risk: ATOMIC gives a full per-bar prospective guarantee; HYBRID trades
per-bar freezing for fewer round-trips on routine stretches, with the reasoning-dependent protection delegated.

## 4 — DECISION HANDSHAKE + CRASH (§6) — fail-closed, verified

- `causalStepSnapshot`/`causalRunUntilGate` throw `DECISION_COMMIT_REQUIRED` if a bar is pending (T08).
- `causalCommitDecision` requires a pending bar (`NO_PENDING_COMMIT`), `bar_id` must match the pending
  (`BAR_ID_MISMATCH`), `decision_type` must be known (`UNKNOWN_DECISION_TYPE`), required fields present
  (`INCOMPLETE_DECISION_RECORD`); only then is the pending cleared → next bar unlocked (T09/T18).
- **Crash recovery**: handshake is in-memory only (by design — TradingView's live `currentDate()` is the sole
  durable pointer; there is no server-side pointer file). After a crash the flag is lost, but
  `expected_pointer_before` is checked against the LIVE pointer on the next call: if the caller resumes with its
  last **durably-committed** bar and the live pointer is ahead (a revealed-but-uncommitted bar), it throws
  `POINTER_MISMATCH` and fails closed (**T16**). Clean resume with a correct belief re-emits no bar (**T17**).
  Adversarial cases — duplicate/out-of-order commit, stale-pointer "rewind", ambiguous `decision_type` — are all
  refused, not guessed (mandate §15 injection suite, 4/4).

## 5 — TRADE / P007 / MGMT-004 / NO_TRADE (§7–§10)

- **TRADE_CONTRACT_PROTECTION = PASS**: a `TRADE_CONTRACT` commit mechanically requires `entry, direction,
  initial_stop, structural_target, baseline_management, thesis, invalidation` **before** the pointer can advance;
  an incomplete contract is refused and the pointer stays locked (T10).
- **P007_PROSPECTIVE_PROTECTION = PASS** (ATOMIC): `P007_PRECLASSIFICATION` must be committed on the eligibility
  bar before the next bar; a `P007_RESOLUTION` is stamped with the **resolving** bar, not the trigger — the system
  cannot retrospectively re-label a completed reclaim as prospective (T11). In HYBRID this holds only under §15
  note 1.
- **MGMT004_CAUSALITY = PASS**: an `MGMT004_TRIGGER` is stamped at the bar where +1.0R was **causally observed**,
  not retroactively; it names the triggering trade + R-multiple (T12).
- **NO_TRADE_PROSPECTIVE_PROTECTION = PASS**: a `NO_TRADE_ACTIONABLE` requires `setup_description` + `rationale`,
  recorded at the setup bar itself (T13). In HYBRID a NO_TRADE surface on a routine bar not caught by a mechanical
  gate depends on §15 note 1.

## 6 — HEARTBEAT (§11)

`MAX_HEARTBEAT_BARS = 8`, mechanically enforced: `cap = Math.min(max_bars ?? 8, 8)` — a requested `max_bars=1000`
still processes exactly 8 and returns `PERIODIC_APPRENTICESHIP_HEARTBEAT` (T15). **HEARTBEAT_ENFORCEMENT = PASS.**

**APPRENTICESHIP_INFORMATION_LOSS = MODERATE.** In HYBRID, per-bar reasoning is skipped on routine stretches, so
slow acceptance / gradual momentum / regime transitions / session development that do not trip a mechanical gate
receive no per-bar reasoning pause. Mitigated: every bar's OHLC is still returned in `bars_processed` (nothing
silently dropped), the window is capped at 8 bars, and the mode is explicitly opt-in for routine stretches only.
Not a technical FAIL — but the AI Trader should use HYBRID sparingly to preserve apprenticeship quality.

## 7 — TESTS (§12) — reproduced independently

I re-ran the accelerator suite: **34/34 PASS, 0 fail** (worktree byte-identical to `cf6f470`). The tests are
substantive, not trivial: the fixture `_deps` mock faithfully simulates the CDP `doStep`/`currentDate`/
`bars.lastIndex` surface (one current bar per step — it structurally **cannot** supply a future bar); T14 proves
the runner stops **exactly** at the touching bar (count=3), not later; T16/T17 drive a real reveal→crash→resume
sequence; T29/T30 source-scan the module for a direct `connection.js` import and any hardcoded protected Q4
bar/date/token (concatenation-built to avoid self-reference) and assert the fixture epoch is outside 2020. No
future-data objects present-but-unused; no self-referential trivially-passing assertions found.

**Broader regression**: the full suite's only failure is `tests/sanitization.test.js:298` — a **pre-existing
Windows path-construction bug** (a malformed `C:\C:\…%20…` scandir path), on a file `cf6f470` did **not** touch.
VE-disclosed, not accelerator-caused, out of scope.

## 8 — FAIL-CLOSED (§13)

Verified throw-on: pointer mismatch (`POINTER_MISMATCH`), timestamp disorder (`TIMESTAMP_ORDER_VIOLATION`, on a
non-monotonic delta), missing/duplicate commit (`DECISION_COMMIT_REQUIRED`/`NO_PENDING_COMMIT`), wrong bar
(`BAR_ID_MISMATCH`), incomplete/unknown decision (`INCOMPLETE_DECISION_RECORD`/`UNKNOWN_DECISION_TYPE`), invalid
`max_bars`. Gap forward is flagged (`GAP_FORWARD`) and treated as a gate event (stop+expose), mirroring the
GAP-151..154 discipline. No fail-open path found. Telemetry write is best-effort and never blocks the guarantee.

## 9 — PERFORMANCE HONESTY (§14)

Not audited for profitability. The claims (atomic ≈ 2 calls/bar vs current ≈ 3; hybrid ≈ 0.25 effective on
routine stretches) are represented honestly and are structurally consistent with the code (one composed call
per bar; up to 8 bars per hybrid call → ≥ down to ~1 external round-trip per 8 routine bars). The scientific gate
is causal integrity, which passes; no real speedup was required or claimed as the gate.

## 10 — FINDINGS (§15)

**BLOCKING: NONE.** No future leakage, no unsafe pointer advancement, no unrecoverable crash ambiguity, and no
mechanism by which the module itself performs retrospective event classification.

**NONBLOCKING:**
1. **HYBRID prospective protection for reasoning-dependent events is a USAGE CONTRACT, not a mechanical
   guarantee.** P007/MGMT004/trade-setup/NO_TRADE eligibility are declared `NOT_MECHANICALLY_GATED` and covered
   only by the 8-bar heartbeat + mechanical level/vol/gap gates. If HYBRID is run over a stretch containing such
   an event that does not touch a registered level, the runner advances past it and the reasoning layer could
   classify it after later bars are revealed. **Mitigation (already in place): disclosed verbatim in the module
   docstring AND the `causal_run_until_gate` tool description ("NOT a substitute for causal_step_snapshot on any
   bar you suspect may be decision-bearing … anything but routine stretches"), bounded to 8 bars, and the ATOMIC
   mode is the fully-safe path. REQUIRED of the AI Trader integration: use `causal_step_snapshot` (ATOMIC)
   whenever a trade is open or a pattern watch is active, and register all relevant structural levels.**
2. **Crash-recovery correctness depends on the caller passing `expected_pointer_before` = last DURABLY COMMITTED
   bar** (not last revealed). Under that protocol `POINTER_MISMATCH` fails closed (T16); the tool description
   documents it ("the last bar_id you durably recorded"). The module cannot enforce which value the caller
   supplies — a resume protocol note for the AI Trader.
3. **In-memory-only handshake state** (no disk persistence) — by design; acceptable because the live pointer is
   the ground truth and note 2's pointer check backstops it. Informational-to-nonblocking.
4. **Pre-existing `sanitization.test.js` Windows path bug** — VE-disclosed, unchanged by `cf6f470`, out of scope;
   flagged so it is not mistaken for accelerator breakage.

**INFORMATIONAL:** event-gate coverage is 3 of the mandate's 15 categories (honestly disclosed, the rest via
heartbeat); `startRun` uses `Date.now()/Math.random()` for a cosmetic run-id fingerprint (not on any causal
path).

## 11 — CONCLUSION

`VE_CAUSAL_REPLAY_ACCELERATOR_V1` preserves genuine prospective causality. Both modes reveal only the current
bar, mechanically block the pointer behind an explicit decision commit, fail closed on pointer/timestamp/commit
anomalies, and recover from crashes via a live-pointer cross-check. The one real limitation — HYBRID's
delegated protection for reasoning-dependent events — is disclosed, bounded, and has a fully-safe ATOMIC
fallback. VE's `VE_HANDOFF_PASS` is **independently corroborated**, subject to the §15 note-1 usage contract.

```
RED_TEAM_VERDICT = PASS_WITH_NONBLOCKING_NOTES
SAFE_FOR_AI_TRADER_Q4 = YES (conditional on the HYBRID usage contract)
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

Live TradingView replay NOT restored, Q4 NOT resumed, bar 379 NOT accessed, accelerator code NOT modified.
`LIVE_TRADINGVIEW_REPLAY_STATE` remains NOT-YET-VERIFIED (separate prerequisite, out of scope here). Control
returned to CEO.

---

*Red Team · independent adversarial review · remote identity verified · 34/34 accelerator tests reproduced ·
no accelerator modification · bar 379 not accessed · LEDGER E102 (prev E101).*
