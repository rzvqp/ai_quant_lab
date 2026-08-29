# CAUSAL_REPLAY_ACCELERATOR_V1 — HANDOFF

**Status at handoff**: implemented, tested (34/34), benchmarked, documented, git-checked-in.
**NOT connected to the live Q4 apprenticeship.** `LAST_CONSUMED_BAR = 378`, `NEXT_UNSEEN_BAR = 379`
— unchanged by this mandate. Resuming Q4 (under this accelerator or unchanged Option A) requires a
**separate, explicit CEO instruction** — this document does not itself authorize it.

## 1. What exists now

Four new MCP tools, registered in `tradingview-mcp`'s server (available the next time that server
process starts or reloads its tool set):

- `causal_step_snapshot` — Layer A, one bar per call, bundles step+OHLCV+Pine-table read.
- `causal_run_until_gate` — Layer B, up to 8 bars per call, stops early on a mechanically-detected
  event (see the implementation doc §5 for exactly which event types this does and does not cover
  — **read that section before relying on Layer B for anything but stretches already expected to
  be routine**).
- `causal_commit_decision` — required after every bar revealed by either of the above, even routine
  ones (`decision_type: "ROUTINE_NO_EVENT"`).
- `causal_replay_status` — read-only, returns the accelerator's own handshake state.

## 2. Exactly how to resume from bar 378 without accidental advancement

**Do not call `causal_step_snapshot` or `causal_run_until_gate` with no `expected_pointer_before`
as the first action of a resumed session**, even though the tool schema permits omitting it (that
omission exists for a genuine first-ever call with no prior state, not for resuming a known
position). The correct resume sequence:

1. Call `causal_replay_status` (or the existing `replay_status`, unchanged) to read the live
   `current_date`. **Confirm it equals `378`'s own timestamp before doing anything else.** If it
   does not, STOP and report the discrepancy — do not proceed on an assumption.
2. Call `causal_step_snapshot({ expected_pointer_before: <378's timestamp> })`. This is the call
   that reveals bar 379 for the first time. The tool cross-checks your supplied
   `expected_pointer_before` against the live pointer in the same read used for stepping — if
   anything about the session's state has drifted from what you believe (a crash, a concurrent
   caller, a stale belief), this call fails closed with `POINTER_MISMATCH` **before** taking any
   action, rather than silently stepping from the wrong place.
3. Reason about bar 379 exactly as you would have under the unchanged workflow.
4. Call `causal_commit_decision({ bar_id: <379's timestamp>, decision_type: ..., decision_record: ... })`
   — required before bar 380 can be revealed, regardless of whether 379 turned out to be routine.
5. For the next bar, supply `expected_pointer_before: <379's timestamp>` (the value you just
   committed) — and so on. This is what makes a future crash mid-sequence recoverable: your own
   durable log (the same M15/pattern/thesis ledgers already in use) is the source of truth for what
   you last committed, and every subsequent call verifies it against the live pointer before acting.

**If you ever restart this reasoning session and are not certain what the last committed bar was**,
re-derive it from the persisted logs (`AI_TRADER_Q4_M15_LOG.md` and siblings) exactly as
`Q4_GOVERNANCE_SCOPE_BREACH_001.md` already did for bars 288-378, then use step 1 above to verify it
against the live pointer before calling `causal_step_snapshot` again. Never guess.

## 3. Q4-P007-003 (open at handoff, mandate-relevant)

At bar 378, `Q4-P007-003` (38 consecutive bars below EMA50, the longest sub-EMA excursion in the
whole Q1-Q4 record) is **OPEN/UNRESOLVED**, explicitly deferred pending bar 379+ evidence. This
accelerator's `P007_RESOLUTION` commit type exists precisely to freeze whichever bar eventually
resolves it (`SUPPORT`/`COUNTEREXAMPLE`/`AMBIGUOUS`) — resolve it prospectively, on the bar where
resolution actually becomes visible, never retroactively by looking ahead once resumed.

## 4. When to prefer Layer A vs Layer B

**Default to Layer A** (`causal_step_snapshot`) for any stretch where you have any reason to expect
a thesis trigger, structural level interaction, regime-adjacent price action, or anything in the 12
NOT_MECHANICALLY_GATED categories (implementation doc §5) might occur. **Layer B is appropriate
only for stretches you already expect to be quiet** (e.g. historically thin overnight sessions),
where its 8-bar heartbeat ceiling is an acceptable worst case, not a hoped-for one. This is not a
hard rule the tool itself enforces — it is a judgment call the reasoning layer makes per stretch,
exactly as the compact-vs-full logging decision already is.

## 5. Rollback

Both new source files (`src/core/causal_replay.js`, `src/tools/causal_replay.js`) are purely
additive — `replay_step`/`data_get_ohlcv`/`data_get_pine_tables` and every other existing tool are
byte-unchanged in behavior (the only modification to a pre-existing file is the `_deps` injection
seam added to `getOhlcv`/`getPineTables`, itself behavior-preserving and covered by the unaffected
95/95 regression). To roll back entirely: stop calling the four new tools and resume with the
unchanged `replay_step`/`data_get_ohlcv`/`data_get_pine_tables` sequence — no state migration is
needed either way, since there is no persisted state (§1 of the implementation doc) beyond the live
TradingView pointer itself, which neither this accelerator nor a rollback touches directly.

## 6. Recommended before live use

Per `CAUSAL_REPLAY_ACCELERATOR_V1_DESIGN.md`'s own §7 (`RED_TEAM_REVIEW_REQUIRED = YES`) and this
mandate's own final-report field: an independent adversarial review of this implementation — not
just this mandate's own self-authored test suite — is recommended before connecting it to the live
Q4 apprenticeship, consistent with this lab's standing practice for measurement-integrity-adjacent
code.

## 7. Explicit non-actions (mirroring the design doc's own §8 discipline)

This handoff does not resume Q4. `NEXT_UNSEEN_BAR = 379` remains unconsumed. No live tool was
called. Connecting this accelerator to the live apprenticeship — under Layer A, Layer B, or a mix —
requires a separate, explicit CEO instruction.
