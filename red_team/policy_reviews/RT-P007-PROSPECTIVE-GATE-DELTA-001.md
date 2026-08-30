# RED TEAM — DELTA REVIEW · DURABLE P007 PROSPECTIVE DETECTION GATE · FINAL GATE BEFORE Q4 RESUME @ BAR 1305
### RT-P007-PROSPECTIVE-GATE-DELTA-001 · Auditor: Red Team · 2026-08-30

Delta review of `8deba48` — the durable prospective PATTERN-007 detection gate, which is the concrete
remediation of Red Team E108's nonblocking finding (the cited `q4_batch_runner.py` preventive fix did not
exist). Read-only audit + independent verification against checkpoint bar 1304. Bar 1305 not accessed /
not materialized; Q4 not continued; no code modified; real durable state not touched.

---

## 0 — VERDICT

The gate correctly and durably forces ATOMIC handling of any prospective P007, reproduces the causal H1
EMA50 and the P007-004 instance exactly, and touches no trade/S5/MGMT/engine behavior. It closes the E108
detection gap.

```
RED_TEAM_P007_GATE_DELTA_REVIEW_COMPLETE = YES
IMPLEMENTATION_COMMIT = 8deba481c17d319c7e960624cc82acf3e5f5fd55
IDENTITY_VERIFIED = YES        SCOPE_CLEAN = YES

CAUSAL_H1_EMA50 = PASS          M15_EMA_USED_FOR_P007 = NO
P007_004_TRIGGER_REPRODUCED = PASS    P007_004_RESOLUTION_REPRODUCED = PASS

P007_ATOMIC_GATE = PASS
HYBRID_BLOCKED_WHILE_P007_OPEN = PASS
RESTART_PRESERVES_P007 = PASS

P007_TRADEABLE_UNCHANGED = YES   S5_UNCHANGED = YES   MGMT004_UNCHANGED = YES

BAR_1305_ACCESSED = NO
TESTS = 94 (77 existing + 17 new: 4 causal_h1 + 8 detector + 5 gate) reproduced + independent RT probe (all pass)

BLOCKING_FINDINGS    = NONE
NONBLOCKING_FINDINGS = 4 (over-inclusive-by-design => HYBRID de-facto disabled + per-crossing resolution
                         needed; stale-ref masking if a crossing is left unresolved; :00-bar EMA convention;
                         gate not yet wired into a resume loop)

SAFE_TO_RESUME_Q4_FROM_BAR_1305 = YES (conditional on wiring the gate into the resume loop + per-crossing
                                       resolution discipline; standing E106 wiring note)
RED_TEAM_VERDICT = PASS_WITH_NONBLOCKING_NOTES
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

## 1 — SCOPE (§1) — clean

`8deba48` ("feat: durable prospective P007 detection gate (Red Team E108 remediation)") is HEAD, a direct
child of the E108 checkpoint `3cb48fe`, adding **exactly the 6 expected files** and nothing else: `causal_h1
.py` (+119), `p007_detector.py` (+128), `p007_gate.py` (+92), and their three test files — **all pure
additions, 788 insertions / 0 deletions**. No existing file modified: `engine.py`, `sealed_reader.py`,
`ema.py`, `persistence.py`, `identity.py`, `errors.py`, `types.py`, the S5/MGMT-004/MT5/risk/execution
code, and every doc/ledger are byte-unchanged. **IDENTITY_VERIFIED = YES · SCOPE_CLEAN = YES.**

## 2 — H1 EMA SEMANTIC (§2) — PASS, all four anchors exact

`p007_detector.py` and `p007_gate.py` compute the reference EMA through the new `causal_h1.CausalH1EmaTracker`
(streaming M15→H1 aggregation, SMA-50 seed, α=2/51, only fully-closed H1 candles) — **not** the M15
`ema.py` helper (no import of it anywhere in the three modules; verified). Feeding the real sealed 1304
fixture through VE's own tracker reproduces every mandated anchor **exactly**:

```
@ bar 378 = 1901.160    @ bar 487 = 1891.748    @ bar 787 = 1918.200    @ bar 878 = 1904.592
```

**CAUSAL_H1_EMA50 = PASS · M15_EMA_USED_FOR_P007 = NO.** (The tracker closes an H1 bucket when the next
hour's first bar arrives — see NONBLOCKING-3 for the one-candle boundary convention this implies at :00
bars, which is immaterial to all four anchors and to P007-004.)

## 3 — P007-004 REGRESSION (§3) — PASS

Running the real `P007Detector` over real bars 1..1304 (data ≤1304 only) reproduces the cataloged instances
exactly: **TRIGGER at bar 787** (close 1916.054 < causal H1 EMA50 1918.200) and **RESOLUTION at bar 878**
(close 1905.436 > 1904.592), with **no spurious resolution inside the 787–877 excursion**. It likewise
reproduces P007-003 (TRIGGER 340, RESOLUTION 487). No retrospective information used — the detector is a
pure forward pass. **P007_004_TRIGGER_REPRODUCED = PASS · P007_004_RESOLUTION_REPRODUCED = PASS.**

## 4 — ATOMIC GATE (§4) — PASS, verified end-to-end on the real engine

`p007_gate.apply_p007_gate()` reuses `engine.py`'s existing `open_event_state_reference` field (the same
field `run_until_gate` already refuses on for Q4-P007-003) — it never modifies `engine.py`; it only WRITES
that one field via `dataclasses.replace` + `DurablePointerStore.save`, exactly the `bind_extended_fixture`
pattern. Independently verified with the real engine and real fixtures (799/800/878 copied to a tmp dir; the
real durable state never touched):

- **Detection → lock:** with durable state at sealed boundary 800 (inside the 787–877 window) and
  `open_event_state_reference = None`, `apply_p007_gate` sets it to `Q4-P007-CANDIDATE:OPEN@bar_787`,
  changing **only** that field (scientific state untouched). **P007_ATOMIC_GATE = PASS.**
- **HYBRID blocked / ATOMIC permitted:** with the lock set, `engine.run_until_gate()` raises
  `HybridModeLockedError`, while `engine.step()` still reveals the next bar. **HYBRID_BLOCKED_WHILE_P007_OPEN
  = PASS.**
- **Restart preserves:** a fresh `DurablePointerStore` over the same file reloads the open reference —
  the P007 survives a runtime restart. **RESTART_PRESERVES_P007 = PASS.**
- **One-directional + idempotent:** the gate never auto-clears (clearing stays the reasoning layer's explicit
  `commit_decision(P007_RESOLUTION)`), is a no-op when already flagged, and — critically — does **not** flag
  at a mechanically-resolved boundary (`compute_p007_candidate_reference(878) is None`, `(800) is
  OPEN@bar_787`), so a resolved P007 does not spuriously re-lock.

## 5 — SCIENTIFIC ISOLATION (§5) — intact

`open_event_state_reference` is read by **only** `engine.run_until_gate` (to refuse HYBRID) — a grep across
the entire tree finds no S5, MGMT-004, trade, risk, or execution code that reads it. The gate therefore
affects **replay mode only** (ATOMIC vs HYBRID), never whether or how a trade is taken. PATTERN-007's
`TRADEABLE=NO / PLAYBOOK_READY=NO` header is unchanged (no ledger/doc modified by `8deba48`), and the S5 and
MGMT-004 code is byte-unchanged. **P007_TRADEABLE_UNCHANGED = YES · S5_UNCHANGED = YES · MGMT004_UNCHANGED =
YES.**

## 6 — TESTS (§6) — 94 reproduced + independent probe

VE's full suite reproduced: **94 passed** (77 existing + 17 new = 4 `test_causal_h1` + 8
`test_p007_detector` + 5 `test_p007_gate`). Independent RT probe (real modules, real fixtures ≤1304, tmp
state) additionally confirmed: all four EMA anchors exact; P007-003/004 trigger+resolution reproduced; the
full gate→engine ATOMIC integration (flag → HYBRID refused → ATOMIC step → restart-preserved → idempotent →
no-flag-when-resolved). All pass. No bar 1305 used.

## 7 — CHECKPOINT FREEZE (§7)

Durable state unchanged: `last_committed_bar = 1304` (ts 1603251900), `next_bar = 1305`,
`open_event_state_reference = null` (consistent — the detector is closed at bar 1304: its last event is a
RESOLUTION at bar 1255, no trigger after, so the resume boundary carries no stale lock), `pending_decision =
null`, POSITION FLAT. No fixture ≥ 1305; the sealed 1304 fixture holds no bar-1305 row. My audit was
read-only (tmp copies only; the real state file is byte-unchanged). **BAR_1305_ACCESSED = NO · Q4_CONTINUED
= NO.**

## 8 — FINDINGS

**BLOCKING: NONE.** The gate is correct, minimal, well-tested, reuses the existing lock mechanism without
touching `engine.py`, reproduces the causal H1 EMA50 and P007-004 exactly, and is scientifically isolated
from trading. It closes the E108 detection gap (the previously-missing, unverifiable preventive fix now
exists, committed and tested — as a more conservative EMA-crossing detector rather than the originally-cited
heavy-volume-gated check).

**NONBLOCKING (4):**
1. **Over-inclusive by design → HYBRID is de-facto disabled during Q4.** The detector flags *every* EMA
   crossing (~30 TRIGGER/RESOLUTION pairs across bars 1–1304), not only the 2 cataloged P007 events — the
   stated "must not silently pass" tradeoff. Consequence: with the gate wired in, a P007 candidate is open a
   large fraction of the time, so `run_until_gate` (HYBRID) is almost always refused and the reasoning layer
   must commit a `P007_RESOLUTION` to clear each flagged crossing. Benign for this apprenticeship (which uses
   ATOMIC exclusively anyway, per E108), but the CEO/integrator should understand HYBRID becomes effectively
   unusable and per-crossing resolution discipline is required.
2. **Stale-ref masking if a crossing is left unresolved.** Because `apply_p007_gate` is a no-op whenever any
   reference is already set, a candidate that the reasoning layer never explicitly resolves leaves a stale
   `open_event_state_reference` that would mask a later crossing's *trigger-bar label* (the lock itself stays
   correctly set, so ATOMIC enforcement is unaffected — only the named trigger bar goes stale; recoverable
   via a fresh `compute_p007_candidate_reference`). Recommend the resume runtime resolve each flagged
   crossing promptly.
3. **:00-bar EMA boundary convention.** `causal_h1.py` closes an H1 bucket on the next hour's first bar, so
   the reference EMA at a :00 (top-of-hour) bar excludes that hour's just-completed predecessor candle —
   differing by one candle from a "close-on-:45" convention, at :00 bars only. All four mandate anchors and
   both cataloged P007 triggers/resolutions are non-:00 bars, so this is immaterial to them; it is an
   internally-consistent, disclosed causal choice, noted only because it could shift a future
   trigger/resolution by up to one bar if a crossing lands exactly on a :00 boundary.
4. **Not yet wired into a resume loop.** As in E106, this commit ships correct, tested *primitives*
   (`apply_p007_gate`, `compute_p007_candidate_reference`) but no orchestrator that calls them; the resume
   runtime must actually invoke `apply_p007_gate` after each `step()`/`bind_extended_fixture()` and pair it
   with the reasoning layer's P007 classification/resolution.

## 9 — CONCLUSION

`8deba48` is a clean, correct, well-isolated remediation of the E108 detection gap. It computes the causal
H1 EMA50 (reproducing all four anchors and both cataloged P007 instances exactly), never uses the M15 EMA
helper, and durably forces ATOMIC handling of any prospective P007 by reusing the engine's existing
`open_event_state_reference` lock — verified end-to-end on the real engine (HYBRID refused, ATOMIC permitted,
restart-preserved). It changes no trade, S5, or MGMT-004 behavior. The remaining work is integration: wiring
`apply_p007_gate` into the resume loop with per-crossing resolution discipline (NONBLOCKING 1–2, 4). With
that wiring and CEO authorization, it is safe to resume Q4 from bar 1305.

```
RED_TEAM_VERDICT                = PASS_WITH_NONBLOCKING_NOTES
SAFE_TO_RESUME_Q4_FROM_BAR_1305 = YES (conditional)
BAR_1305_ACCESSED               = NO
NEXT_AUTHORIZED_ACTION          = NONE — CEO DECISION REQUIRED
```

Bar 1305 not exposed, not materialized; Q4 not continued; no code modified; checkpoint not modified. Control
returned to CEO.

---

*Red Team · durable P007 prospective gate delta · 6 new files, pure additions · causal H1 EMA50 exact at
378/487/787/878 · M15 ema helper not used · P007-004 trigger 787 / resolution 878 reproduced · ATOMIC gate
verified end-to-end (HYBRID refused, restart-preserved) · isolated from trade/S5/MGMT · 94 tests + RT probe
· E108 gap closed · bar 1305 not accessed · LEDGER E109 (prev E108).*
