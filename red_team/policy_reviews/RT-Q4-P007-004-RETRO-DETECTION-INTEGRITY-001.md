# RED TEAM — Q4 P007-004 RETROSPECTIVE-DETECTION INTEGRITY AUDIT
### RT-Q4-P007-004-RETRO-DETECTION-INTEGRITY-001 · Auditor: Red Team · 2026-08-30

Audit of whether AI Trader's *retrospective* identification of Q4-P007-004 (a ~91-bar below-H1-EMA
excursion, bars 787–878, detected only after the fact) compromises the scientific validity of bars
787–884, or is a non-blocking process-detection gap. Read-only forensics + independent causal-H1-EMA50
reconstruction against checkpoint `3cb48fe` (bar 1304). Bar 1305 not accessed; Q4 not continued; no
historical decision modified; P007 not retuned.

---

## 0 — VERDICT

The missed prospective detection changed no decision and lost no reconstructable evidence. It is a
**process-detection gap**, not a scientific-integrity blocker.

```
P007_004_INTEGRITY_AUDIT_COMPLETE = YES

P007_ATOMIC_CONTRACT_VIOLATED = NO
REASONING_EVIDENCE_LOST       = NO

TRADE_DECISIONS_CHANGED  = NO   S5_DECISIONS_CHANGED = NO   NO_TRADE_DECISIONS_CHANGED = NO
MGMT004_DECISIONS_CHANGED = NO  TRADE_2_VALIDITY_CHANGED = NO   P007_CLASSIFICATION_CHANGED = NO

P007_004_SCIENTIFICALLY_VALID     = YES
BARS_787_884_SCIENTIFICALLY_VALID = YES
BAR_1305_ACCESSED                 = NO

ERROR CLASSIFICATION = PROCESS_DETECTION_GAP_NONBLOCKING  (append-only disclosure prescribed; already present)
BLOCKING_FINDINGS    = NONE
NONBLOCKING_FINDINGS = 3 (detection gap itself; unverifiable batch-runner fix; missing structural-level field)

SAFE_TO_CONTINUE_FROM_BAR_1305 = YES (subject to the standing E106 wiring note + CEO authorization)
RED_TEAM_VERDICT               = PASS_WITH_NONBLOCKING_NOTES
NEXT_AUTHORIZED_ACTION         = NONE — CEO DECISION REQUIRED
```

## 1 — EXACT P007-004 TIMELINE (§1) — independently reconstructed, every claim exact

Reconstructed the causal H1 EMA50 from the sealed 1304 fixture only (M15→H1 aggregation, SMA-50 seed,
α=2/51, only fully-closed H1 candles, gap-aware bar-index→timestamp mapping). **Dual calibration holds
exactly:** H1 EMA50 @ bar 378 = **1901.160** (the E107 checkpoint) and @ bar 487 = **1891.748** (the log's
own P007-003 resolution value). So the method is validated across the full range before trusting its
P007-004 outputs.

```
P007_004_PROSPECTIVE_ELIGIBILITY_BAR = 787  (2020-10-13 12:29:59 UTC; close 1916.054 first closes BELOW
                                             causal H1 EMA50 1918.200 — bars 782–786 were all ABOVE at
                                             1919–1921 — with immediate heavy REAL-volume follow-through:
                                             bar 788 vol 2718, 789 vol 2747, 791 vol 4134, the P007-eligible
                                             "severe/heavy break" component)
P007_004_OPEN_INTERVAL   = bars 787–877  (91 consecutive M15 bars, ALL strictly below the causal H1 EMA50 —
                                          verified bar-by-bar; deepest low 1882.434 @ bar 834; heaviest
                                          volume 4134 @ bar 791 — both exact matches to the ledger)
P007_004_RESOLUTION_BAR  = 878  (close 1905.436 > causal H1 EMA50 1904.592 — first close back above; exact)
P007_004_FINAL_CLASSIFICATION = SUPPORT / RECLAIM  (reclaimed and held above the H1 EMA50 through bars
                                          879–885; no new Q4 low set — 1882.434 is well above the all-time
                                          Q4 low 1872.898 @ bar 375; not a COUNTEREXAMPLE)
```

Every field the ledger recorded (trigger 787 @ EMA 1918.2, resolution 878 @ EMA 1904.592, 91-bar span,
deepest 1882.434@834, heaviest 4134@791) reproduces **exactly** from a pure causal recomputation — the
event is fully deterministically reconstructable.

## 2 — ATOMIC / HYBRID INTEGRITY (§2) — contract not violated

```
BARS_WHERE_P007_SHOULD_HAVE_BEEN_OPEN = 787–877 (resolution commit falls on bar 878, itself ATOMIC)
ACTUAL_ATOMIC_BARS                    = 787–878 (in fact all of 386–1304)
ACTUAL_HYBRID_OR_ROUTINE_BARS         = 0 HYBRID bars; bars 787–877 committed as ROUTINE_NO_EVENT LABEL
                                        but via individual ATOMIC step()+commit_decision()
P007_ATOMIC_CONTRACT_VIOLATED         = NO
```

The contract requires that while a P007 episode is OPEN, replay is ATOMIC (one bar at a time), never
HYBRID (`run_until_gate` bulk reveal). Because P007-004 was never flagged, `open_event_state_reference`
was never set, so the *mechanical lock* never engaged for it. **But HYBRID was never used at all this
session** — the log states it explicitly ("HYBRID mode becomes mechanically eligible … not yet used this
session") and three independent facts corroborate it: (a) the engine's own design (each bar revealed via
`extend_next_bar → bind_extended_fixture → engine.step() → commit_decision()`); (b) **927 fully contiguous
per-bar fixtures `Q4_SEALED_1_378 … _1304` with no gaps** — one materialized per bar, exactly what
one-bar-at-a-time extension produces and what bulk `--max-bar`/HYBRID would not require; (c) the log's
"COMPACT BLOCK" entries are documentation-compaction of individually-committed bars, not bulk reveals ("No
batching of unseen bars into one market-reading decision"). Since the very thing the lock guards against —
a bulk/lookahead reveal during the excursion — **did not occur**, the missing lock had no effect and the
atomic discipline was maintained in substance throughout 787–877. Contract not violated.

## 3 — DECISION IMPACT (§3) — nothing changes

Re-evaluated bars 787–884 under a counterfactual prospectively-OPEN P007-004 (no new bars exposed):

```
TRADE_DECISIONS_CHANGED   = NO     S5_DECISIONS_CHANGED     = NO     NO_TRADE_DECISIONS_CHANGED = NO
MGMT004_DECISIONS_CHANGED = NO     TRADE_2_VALIDITY_CHANGED = NO     P007_CLASSIFICATION_CHANGED = NO
```

- **P007 never gates trading.** PATTERN-007 is `BEHAVIORALLY_REAL=YES / TRADEABLE=NO / PLAYBOOK_READY=NO`
  — it is captured as observational field evidence and never authorizes, blocks, or modifies a trade.
- **S5 is mechanical and P007-blind.** The opening-range-breakout trigger (`close > or_high` in the NY
  entry window) reads neither P007 state nor the EMA; an open P007-004 could neither create nor suppress an
  S5 signal. No S5 trigger fired during 787–877 (all NO_TRADE — the NY sessions in that window formed
  opening ranges but no close broke above OR high), and that is unchanged under P007-open.
- **TRADE #2 (bar 884) is untouched.** Its signal bar is **6 bars after** P007-004's reclaim (878); a
  prospectively-open P007-004 would have been *resolved and its lock cleared at bar 878*, so no lock would
  be active at 884 regardless. Independently, at bar 884 price (1912.356) sits **~7pt ABOVE** the reclaimed
  H1 EMA50 (1905.015) — a mechanical S5 LONG (close 1912.356 > or_high 1909.755, OR formed 880–883). Its
  validity is entirely independent of P007-004's detection.
- **MGMT-004 out of scope in the window.** Position was FLAT throughout 787–877 (TRADE #1 closed bar 656;
  TRADE #2 opens bar 884), so no position-management decision existed to change.
- **Classification is a fact of the frozen data.** SUPPORT/RECLAIM, trigger 787, resolution 878, 91 bars,
  deepest/heaviest fields — all reproduce identically whether detected prospectively or retrospectively;
  the reclaim is mechanically determined, not a judgment that hindsight could flip.

## 4 — INFORMATION-LOSS TEST (§4) — no irreversible loss

```
REASONING_EVIDENCE_LOST = NO
```

The question is not merely whether labels can be reconstructed, but whether processing the bars without the
P007 lock *irreversibly* lost reasoning-dependent evidence ATOMIC processing would have captured. It did
not, for three independent reasons:
1. **No bulk reveal happened.** Because HYBRID was never used (§2), every bar 787–877 *was* individually
   revealed and committed (ATOMIC), so the per-bar causal record physically exists — no intermediate bar
   was skipped/bulk-consumed. The only thing not written in real time is the *P007-OPEN annotation /
   prospective pre-classification*.
2. **That annotation is not decision-bearing.** For a `TRADEABLE=NO` observational pattern, the P007-OPEN
   label drives no trade, S5, MGMT-004, or thesis-based decision (§3). Its absence in real time is a
   documentation label, not lost evidence that any decision depended on.
3. **Contamination-free reconstruction is possible and was performed.** Every P007-004 field is a causal
   function of the frozen bars ≤878; I recomputed the H1 EMA50 and the price/volume series and recovered
   the trigger, the full 91-bar below-EMA interval, the deepest low, the heaviest volume, and the reclaim
   bar exactly — using only data through each respective bar, no future knowledge. Identifying the reclaim
   at 878 uses bars ≤878 only.

So no *material* reasoning evidence was irretrievably lost. (The genuinely unrecoverable item — a
same-instant prospective pre-classification formed before the reclaim was seen — is immaterial for a
non-tradeable pattern and is honestly disclosed as retrospective.)

## 5 — SCIENTIFIC CLASSIFICATION (§5)

All four PROCESS_DETECTION_GAP_NONBLOCKING conditions hold: decisions identical (§3); no trade/MGMT
decision changes (§3); P007 reconstructable deterministically (§1, exact); no material reasoning evidence
irretrievably lost (§4). **Classification: `PROCESS_DETECTION_GAP_NONBLOCKING`.** The prescribed remedy is
append-only disclosure — which is **already present** (the ledger's Q4-P007-004 process-disclosure note and
the M15 log's bar-787-878 entry both disclose the retrospective identification openly). No re-replay, no
prior-decision reversal, no P007 retune.

## 6 — CHECKPOINT INTEGRITY (§6) — verified independently

```
LAST_COMMITTED_BAR = 1304  (durable last_committed_bar = 1603251900 = bar 1304 ts; next_bar = 1305)
NEXT_UNSEEN_BAR    = 1305   POSITION = FLAT (pending_decision = null; open_event_state_reference = null)
TRADES_TOTAL       = 4      (S5 ORB LONG: #1 bar 608 +0.651R; #2 bar 884 −1.000R; #3 bar 982 −0.005R;
                             #4 bar 1256 +0.929R)
CONTROL_NET_R      = +0.651 − 1.000 − 0.005 + 0.929 = +0.575R   ✓
BAR_1305_ACCESSED  = NO     (only the sealed 1304 fixture read; no fixture ≥ 1305 exists; fixture holds no
                             bar-1305 row)
```

Checkpoint not modified; my audit was strictly read-only (the audited `csv_causal_replay/` tree is
unmodified; the only working-tree changes are pre-existing cross-session `mt5_demo_bridge` files outside
scope). HEAD unchanged at `3cb48fe`.

## 7 — FINDINGS

**BLOCKING: NONE.** Bars 787–884 are scientifically valid: the P007-004 event is deterministically
reconstructable and exact, no decision changes under a prospectively-open P007-004, the atomic discipline
was maintained (HYBRID never used), and no material reasoning evidence was irretrievably lost.

**NONBLOCKING (3):**
1. **The process-detection gap itself.** The autonomous batch process was not coded to flag a NEW
   P007-eligible heavy-volume H1-EMA break (a judgment-call pattern), so bars 787–877 were committed as
   `ROUTINE_NO_EVENT` and P007-004 was registered retrospectively — the one and only P007 instance not
   pre-classified before resolution. Disclosed. Non-consequential here (§3–§5). Recommend keeping the
   append-only disclosure prominent.
2. **The cited preventive fix is not verifiable in the repo.** The ledger and log state the batch runner
   "has been extended … see `q4_batch_runner.py`, current version" with an added heavy-volume-EMA-crossing
   check, but **no `q4_batch_runner.py` exists anywhere in the audited repo** (nor any file referencing a
   batch runner beyond the docs). So the "this gap will not recur silently" assurance cannot be
   independently confirmed. Recommend the detection fix actually be committed with a test, otherwise the
   same retrospective-detection gap can recur on the next heavy-volume break.
3. **Missing STRUCTURAL_LEVEL field.** Unlike P007-001/002/003 (each broke a specifically-named prior low),
   P007-004's ledger entry names no pre-registered structural level — a descriptive gap of the
   retrospective identification, disclosed rather than backfilled with an invented level. Taxonomy only.

## 8 — CONCLUSION

AI Trader's retrospective identification of Q4-P007-004 is a genuine, disclosed **process-detection gap**,
not a scientific-integrity failure. The event reconstructs deterministically and exactly from the frozen
data (trigger 787, 91-bar below-H1-EMA excursion 787–877, reclaim 878, SUPPORT/RECLAIM), the atomic
discipline was maintained throughout the window (HYBRID was never used — corroborated by 927 contiguous
per-bar fixtures), and because PATTERN-007 is non-tradeable and never gates S5/MGMT-004, no trade, S5,
NO_TRADE, MGMT-004, thesis, or classification decision changes under a prospectively-open P007-004 — TRADE
#2 at bar 884 (a mechanical S5 breakout six bars after the reclaim, from a position above the EMA) is
entirely unaffected. No material reasoning evidence was irretrievably lost. Bars 787–884 are
scientifically valid, and it is safe to continue from bar 1305 — subject to the standing E106 wiring note
and explicit CEO authorization — provided the disclosed batch-runner detection fix is actually committed
and tested (NONBLOCKING-2).

```
RED_TEAM_VERDICT                  = PASS_WITH_NONBLOCKING_NOTES
P007_004_SCIENTIFICALLY_VALID     = YES
BARS_787_884_SCIENTIFICALLY_VALID = YES
BAR_1305_ACCESSED                 = NO
NEXT_AUTHORIZED_ACTION            = NONE — CEO DECISION REQUIRED
```

Bar 1305 not exposed, not materialized; Q4 not continued; no historical decision modified; P007 not
retuned; checkpoint not modified. Control returned to CEO.

---

*Red Team · P007-004 retrospective-detection integrity · causal H1 EMA50 reconstructed to exact dual
calibration (378=1901.160, 487=1891.748) · trigger 787 / 91-bar excursion / reclaim 878 all exact ·
HYBRID never used (927 contiguous per-bar fixtures) · no decision changed, TRADE #2 independent (post-
reclaim, P007-blind S5) · process-detection gap, not a causal one · cited batch-runner fix not present in
repo · bar 1305 not accessed · LEDGER E108 (prev E107).*
