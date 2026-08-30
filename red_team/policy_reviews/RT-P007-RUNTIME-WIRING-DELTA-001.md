# RED TEAM — FINAL P007 RUNTIME-WIRING DELTA REVIEW · Q4 RESUME GATE @ BAR 1305
### RT-P007-RUNTIME-WIRING-DELTA-001 · Auditor: Red Team · 2026-08-30

Delta review of `3f567a2`, which wires the accepted P007 prospective gate (`8deba48`) into the real Q4
reveal path — closing Red Team E109's nonblocking note #4 ("not yet wired into a resume loop") and
addressing E109's stale-ref-masking note #2. Read-only audit + independent end-to-end verification on real
bars ≤ 1304. Bar 1305 not accessed / not materialized; Q4 not continued; no code modified; real durable
state not touched.

---

## 0 — VERDICT

The canonical reveal path now composes extend→bind→step→gate as one call, so the gate structurally
evaluates every bar the path reveals before the caller can classify it. Verified end-to-end on real data.

```
RED_TEAM_P007_RUNTIME_WIRING_REVIEW_COMPLETE = YES
IMPLEMENTATION_COMMIT = 3f567a2d5226bb9e1fb7d621450c62118ab1e8a1
IDENTITY_VERIFIED = YES        SCOPE_CLEAN = YES

P007_GATE_IN_REAL_REPLAY_PATH             = PASS
P007_GATE_PRECEDES_ROUTINE_CLASSIFICATION = PASS
P007_004_WIRED_TRIGGER    = PASS          P007_004_WIRED_RESOLUTION = PASS

HYBRID_BLOCKED_WHILE_P007_OPEN = PASS      REJECTED_CANDIDATE_CLEARS = PASS
STALE_LOCK_MASKING_PREVENTED   = PASS

CAUSAL_H1_EMA50 = PASS         M15_EMA_USED_FOR_P007 = NO
S5_UNCHANGED = YES             MGMT004_UNCHANGED = YES

BAR_1305_ACCESSED = NO
TESTS = 97 (94 prior + 3 new test_q4_replay_step) reproduced + independent RT wired probe (all pass)

BLOCKING_FINDINGS    = NONE
NONBLOCKING_FINDINGS = 3 (raw-primitive bypass remains possible => runtime must use the wired path
                         exclusively incl. trade-monitoring reveals; masking-fix is a signal not an
                         auto-resolve; carried over-inclusive detector)

SAFE_TO_RESUME_Q4_FROM_BAR_1305 = YES (conditional: runtime routes ALL forward reveals through the wired
                                       path + per-crossing resolution discipline + CEO auth)
RED_TEAM_VERDICT = PASS_WITH_NONBLOCKING_NOTES
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

## 1 — SCOPE (§1) — clean

`3f567a2` ("feat: wire P007 gate into the real Q4 replay path (E109 loop-wiring note)") is HEAD, a direct
child of the accepted gate `8deba48`, adding **exactly the 2 expected files** — `q4_replay_step.py` (+108)
and `tests/test_q4_replay_step.py` (+210) — **pure additions, 318 insertions / 0 deletions**. No existing
file modified: `engine.py`, `p007_detector.py`, `p007_gate.py`, `causal_h1.py`, the S5/MGMT-004/MT5/risk/
execution code, PATTERN-007's definition, and every doc/ledger are byte-unchanged. `q4_replay_step.py`
imports only the already-accepted `extend_next_bar`/`bind_extended_fixture`/`apply_p007_gate`/
`compute_p007_candidate_reference` and the unmodified `CSVCausalReplayEngine` — no `ema`, S5, or MGMT
import. **IDENTITY_VERIFIED = YES · SCOPE_CLEAN = YES.**

## 2 — DECISIVE WIRING QUESTION (§2) — PASS

`reveal_next_bar_with_p007_gate()` is the canonical single entrypoint composing, in the mandated order:

```
extend_next_bar() → bind_extended_fixture() → engine.step() → apply_p007_gate()
```

and it deliberately does **not** call `commit_decision()` — committing stays the reasoning layer's explicit
act. Verified end-to-end on real data (canonical source `57f4ed95`, real fixtures): one call at the 786→787
boundary revealed bar 787 **and** the gate had already run on return (`open_event_state_reference` set). So
when control returns, a `pending_decision` exists for the revealed bar **and** the gate's verdict for that
bar is already in durable state — the caller cannot classify/commit the bar before the gate has evaluated
it. **P007_GATE_IN_REAL_REPLAY_PATH = PASS · P007_GATE_PRECEDES_ROUTINE_CLASSIFICATION = PASS.** (The gate
precedes classification *within* the canonical path; `engine.py` is unmodified by design, so the raw
primitives remain callable and must not be used to bypass it — NONBLOCKING-1.)

## 3 — KNOWN REGRESSION (§3) — PASS, via the wired path on real data

Driving the actual `reveal_next_bar_with_p007_gate` over real bars (≤ 892, never 1305):

- **Trigger:** at the 786→787 boundary the wired call sets `new_p007_candidate_detected = True` and
  `open_event_state_reference = "Q4-P007-CANDIDATE:OPEN@bar_787"` — the known P007-004 trigger, detected
  prospectively through the wired path. `p007_naturally_reclaimed_but_still_locked = False` (price genuinely
  below the causal H1 EMA50 there). **P007_004_WIRED_TRIGGER = PASS.**
- **Resolution:** with the lock set from bar 787, the wired call at the 877→878 boundary reveals bar 878 and
  surfaces `p007_naturally_reclaimed_but_still_locked = True` — the detector, replayed fresh through 878,
  reports the pattern resolved (price back above the causal H1 EMA50), exactly the known bar-878 resolution,
  while the durable lock correctly remains set until an explicit `P007_RESOLUTION` commit. **P007_004_WIRED_
  RESOLUTION = PASS.**

## 4 — REPLAY-MODE SAFETY (§4) — PASS

Independently verified through the wired path + real engine:
- **HYBRID blocked while open:** with the lock set, `engine.run_until_gate()` raises `HybridModeLockedError`;
  the wired ATOMIC reveal proceeds. **HYBRID_BLOCKED_WHILE_P007_OPEN = PASS.**
- **Resolved/rejected candidate clears:** an explicit `commit_decision(decision_type="P007_RESOLUTION", …)`
  clears `open_event_state_reference` to `None`, after which `run_until_gate` is no longer P007-blocked.
  Clearing is the same explicit mechanism whether the reasoning layer *resolves* a genuine P007 or *rejects*
  a trivial candidate. **REJECTED_CANDIDATE_CLEARS = PASS.**
- **Later crossing not masked:** after resolving the bar-787 lock at 878, continuing to drive the wired path
  forward detects the next independent crossing **freshly at bar 892** (`new_p007_candidate_detected = True`)
  — proving the resolved prior candidate does not mask a subsequent one. The `p007_naturally_reclaimed_but_
  still_locked` signal is what prompts the timely resolution that keeps this clean. **STALE_LOCK_MASKING_
  PREVENTED = PASS.**

## 5 — SCIENTIFIC ISOLATION (§5) — intact

The wired path computes P007 through the causal H1 EMA50 (`CausalH1EmaTracker`, via `apply_p007_gate` →
`compute_p007_candidate_reference` → `P007Detector`) — reproducing the 787 trigger and 878 resolution
exactly — and never imports or uses the M15 `ema.py` helper. `q4_replay_step.py` touches no trade path:
PATTERN-007's `TRADEABLE=NO / PLAYBOOK_READY=NO` header is unchanged, and the S5 and MGMT-004 code is
byte-unchanged (scope clean); `open_event_state_reference` remains read only by `engine.run_until_gate`, so
the gate affects replay mode only, never trade/S5/MGMT eligibility. **CAUSAL_H1_EMA50 = PASS ·
M15_EMA_USED_FOR_P007 = NO · S5_UNCHANGED = YES · MGMT004_UNCHANGED = YES.**

## 6 — TESTS (§6)

VE's full suite reproduced: **97 passed** (94 prior + 3 new `test_q4_replay_step`). Independent RT wired
probe (real canonical source, real fixtures, tmp state) additionally confirmed, on real data: wired trigger
@787, wired resolution surfaced @878, HYBRID blocked while locked, explicit resolution clears, and the next
independent crossing detected fresh @892 — all with no bar beyond 892 materialized. All pass.

## 7 — CHECKPOINT (§7)

Real durable state unchanged: `last_committed_bar = 1304` (ts 1603251900), `next_bar = 1305`,
`open_event_state_reference = null`, `pending_decision = null`, POSITION FLAT. The real fixtures directory
still maxes at bar 1304 (my probe materialized bars 787–892 only into a tmp dir); no fixture ≥ 1305 exists;
the audited `csv_causal_replay/` tree is unmodified. **BAR_1305_ACCESSED = NO · Q4_CONTINUED = NO.**

## 8 — FINDINGS

**BLOCKING: NONE.** The wiring is correct, minimal, well-tested, isolated from trading, and reproduces the
P007-004 trigger/resolution through the actual canonical reveal path. It closes the E109 loop-wiring gap and
directly addresses the E109 stale-ref-masking note (via the explicit `p007_naturally_reclaimed_but_still_
locked` signal).

**NONBLOCKING (3):**
1. **Raw-primitive bypass remains possible (runtime contract).** Because `engine.py` is unmodified (by
   scope), the raw `extend_next_bar`/`bind_extended_fixture`/`engine.step` remain callable and would reveal a
   bar without running the gate. The historical record processed open-trade *monitoring* bars via raw
   `engine.step` (not the wired path). Going forward the resume runtime must route **all** forward reveals —
   including trade-monitoring bars — through `reveal_next_bar_with_p007_gate`, else a P007 crossing during a
   non-wired reveal would skip the gate. Recommend: (a) the runtime use the wired path exclusively, and (b)
   in a future mandate, consider an engine-level guard so a raw `step` cannot advance the pointer without the
   gate having evaluated the bar (out of this mandate's minimal scope).
2. **The masking fix is a signal, not an auto-resolve.** `p007_naturally_reclaimed_but_still_locked` makes
   the "reclaimed-but-still-locked" condition impossible to silently miss, but the lock only clears when the
   reasoning layer acts on it (an explicit `P007_RESOLUTION` commit). This is the correct design (resolution
   stays reasoning-dependent) — verified that once resolved, later crossings are detected — so the residual
   is a reasoning-layer discipline requirement, not a mechanical gap.
3. **Carried over-inclusive detector (E109).** The detector still flags every EMA crossing, so with the
   wired path the reasoning layer must classify+resolve each crossing and HYBRID stays de-facto disabled
   during Q4. Benign — the apprenticeship replays ATOMIC exclusively anyway.

## 9 — CONCLUSION

`3f567a2` cleanly closes the last E109 wiring gap: the P007 gate is now composed into the canonical Q4
reveal path so that every bar the path reveals is gated before the caller can classify it, and it
additionally surfaces the reclaimed-but-still-locked condition that E109 flagged as silently missable.
Verified end-to-end on real data (trigger @787, resolution @878, HYBRID-blocked-while-open, resolution
clears, later crossing @892 not masked), scientifically isolated from trading, 97 tests + independent RT
probe. With the resume runtime routing all forward reveals through the wired path (NONBLOCKING-1) and
committing per-crossing resolutions (NONBLOCKING-2/3), and with CEO authorization, it is safe to resume Q4
from bar 1305.

```
RED_TEAM_VERDICT                = PASS_WITH_NONBLOCKING_NOTES
SAFE_TO_RESUME_Q4_FROM_BAR_1305 = YES (conditional)
BAR_1305_ACCESSED               = NO
NEXT_AUTHORIZED_ACTION          = NONE — CEO DECISION REQUIRED
```

Bar 1305 not exposed, not materialized; Q4 not continued; no code modified; checkpoint not modified. Control
returned to CEO.

---

*Red Team · final P007 runtime-wiring delta · 2 new files, pure additions · canonical reveal composes
extend→bind→step→gate, gate precedes classification · wired trigger @787 / resolution @878 on real data ·
HYBRID blocked, resolution clears, later crossing @892 not masked · causal H1 EMA50, M15 helper unused ·
isolated from S5/MGMT · 97 tests + RT probe · closes E109 wiring + masking notes · bar 1305 not accessed ·
LEDGER E110 (prev E109).*
