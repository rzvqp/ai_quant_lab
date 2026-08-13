# RED TEAM — CEO AMENDMENT · ACKNOWLEDGMENT + IMPACT + CURRENT-ATTACK CHANGES
### RT-AUDIT-MEAS-0006 · A2 (strict geometry) · A5 (T17 five-identity + enforcement) · A4 (two gates) · new VE_HANDOFF task
**Date:** 2026-08-13 · **Auditor:** Red Team · **Trigger:** CEO amendment to the canonical-contract audit. This document confirms receipt, states the impact on prior verdicts, and defines what changes in the current attack. **No engine modified; no repair; no real data.**

## AMENDMENT_RECEIVED ✅
All four parts received and understood:
- **A2 — MEAS-9 asymmetric is REJECTED.** CEO ruling = **strict geometry**: LONG `stop < entry_open < target`, SHORT `target < entry_open < stop`; `risk ≤ 0` **OR** `reward ≤ 0` → **INVALID_EXECUTION**, **including `open` exactly on stop or exactly on target** (strict inequalities). VE corrects; **I attack the CORRECTED version, not `3344bff`.**
- **A5 — T17 not closed by a hash without enforcement.** `run_hash` must jointly identify **five**: data · config · **strategy** · engine · contract-version. Verify all five are covered **and** that the comparator **actually refuses** on **all** paths (not just the main one).
- **A4 — TWO gates, kept distinct:** (i) the **canonical-contract gate** — mine, the whole conformance suite, zero unexplained divergences, final CEO approval; (ii) **AI Trader's 25 end-to-end tests** — Mandate 2. I also attack the **interface** between the two levels (VE's tests ↔ AI Trader's tests).
- **NEW — VE_HANDOFF verification.** I verify VE's Mandate-1 artifact against **12 handoff points** and emit **VE_HANDOFF_PASS | VE_HANDOFF_FAIL**. Only PASS authorizes Mandate 2 to AI Trader. **VE_HANDOFF_PASS is FORBIDDEN until the amendment is fully applied.**

## IMPACT ON PRIOR VERDICTS
- **RT-AUDIT-MEAS-0005 (v2.7.66 @`3344bff`) — the MEAS-9 branch verdict is SUPERSEDED by A2.** I verified `3344bff` faithfully — it implements the **asymmetric** treatment (target-gap `reward ≤ 0` → `gap_through_target`, exit at entry, R = −cost/risk; re-confirmed now: that path returns `ExecutedTrade reason=gap_through_target`). The CEO has now **overruled that design**: under strict geometry the target-gap must also be **INVALID_EXECUTION**. My description of `3344bff` stands; my "MEAS-9 closed, both branches" **assessment no longer applies** to the target branch — it is now the *wrong policy*, pending VE's correction.
- **The S3 saga −0.17 (asymmetric) is PROVISIONAL — NON-COMPARABLE.** Under strict geometry the target-gaps that were booked as small −cost trades become INVALID_EXECUTION and leave the population, so the executable set shrinks again and the number **will move** (a fifth S3 figure is expected). Per the freeze, −0.17 is now explicitly **not** a candidate result.
- **Unchanged and still standing:** MEAS-10 (concentration in the official report) and T12/13 (`half_of` arithmetic = full spread once) are **orthogonal to A2** and remain CLOSED. The limitations I raised — NewType unenforced (no mypy gate), `compare()` un-wired, MEAS-14 (tenth), the eleventh (`run_hash` omits `block_end`) — all **persist** and are reinforced by A5.

## WHAT CHANGES IN THE CURRENT ATTACK
1. **Target: the CORRECTED evaluator, not `3344bff`.** I hold until VE lands strict geometry, then re-run the (extended) suite with a Test-18 rewritten to the **symmetric-INVALID** expectation: both `risk ≤ 0` and `reward ≤ 0`, **and the two boundary cases** (`open == stop`, `open == target`) → INVALID_EXECUTION, counted and reported, never a trade. My earlier `test_18_gap_open.py` (18B asserted INVALID for the stop-gap; 18A expected exit-at-entry) is **revised**: 18A now also expects INVALID_EXECUTION.
2. **A5 deepened — verified NOW on `3344bff` (structural, likely to persist):** of the five required identities, `run_hash` covers **3.5**:
   - data — RunContext (symbol/timeframe/split/manifest/n_blocks/holdout) — **PARTIAL** (`block_end` still omitted, my eleventh).
   - config — scenarios/K_*/tick — **YES**.
   - **strategy — MISSING.** Verified: `S1` and `S3` on identical data+config produce the **same** `run_hash` (`efabefe3856205b1`), so `compare()` would **not** refuse an S1-vs-S3 comparison. **This alone keeps T17 open** — the id cannot separate strategies.
   - engine — `code_version` — **YES** (conflated with contract).
   - contract-version — `code_version = canonical-evaluator-v2.7.66` — **YES** (conflated with engine; should be a distinct field).
   - **Enforcement:** `compare()`/`require_comparable()` still **not invoked on any internal path** (RT-AUDIT-MEAS-0005 finding d) → opt-in, bypassable. Existence ≠ closure, exactly as the CEO states.
3. **A4 kept distinct.** My suite is the **contract** gate only. I will build the **interface attack** (VE tests ↔ AI Trader 25 e2e): schema-match on the seam, no double-counting/gaps between the two test bodies, and that a NO_TRADE from the contract layer is what AI Trader's e2e actually asserts.
4. **VE_HANDOFF is BLOCKED (cannot be PASS today).** The amendment is not yet applied (A2 uncorrected; A5 strategy-id + enforcement open), so **VE_HANDOFF_FAIL** is the only permissible current state. The 12-point checklist is armed (below).

## THE 12 HANDOFF POINTS — checklist (to be evaluated against VE's delivered artifact)
1. versioned installable artifact · 2. exact source commit · 3. public-contracts document · 4. schema of every input/output · 5. old-EV→current-contract adapter · 6. unit + contract tests · 7. canonical fixtures with known results · 8. dependency list · 9. install/upgrade/rollback procedure · 10. proof EV no longer uses the old levels · 11. deterministic NO_TRADE without a validated strategy · 12. changelog + compatibility.
**Gate rule:** VE_HANDOFF_PASS requires **all 12** + the amendment fully applied (strict geometry live; `run_hash` covering all five identities incl. strategy; `require_comparable` enforced on all paths). Until then → **VE_HANDOFF_FAIL**.

## STANDING FREEZE
Holds and widens: no leaderboard, no elimination, **no S3 number** (incl. −0.17) is definitive; all asymmetric-variant results are PROVISIONAL/NON-COMPARABLE until strict geometry lands and the full suite passes with matching, strategy-inclusive provenance. Contract ratification still requires my whole suite, zero unexplained divergences, and final CEO approval — separate from AI Trader's Mandate-2 gate.

## HANDOFF → CEO / Statistician / VE
1. **VE (A2):** implement strict geometry (risk≤0 OR reward≤0 → INVALID_EXECUTION, boundaries inclusive); the target branch must stop being an `ExecutedTrade`.
2. **VE (A5):** add **strategy identity** to `run_hash` (and `block_end`/actual cut), split engine vs contract-version, and **invoke `require_comparable()` on every aggregation/leaderboard path**.
3. **VE (Mandate 1):** deliver the 12 handoff artifacts; I verify and emit PASS/FAIL.
4. **Red Team next:** re-attack the corrected evaluator with the revised Test-18 + full suite; build the VE↔AI-Trader interface attack; run the 12-point handoff verification. No PASS of anything until the amendment is fully applied.

Red Team designed no remedy, modified no engine, ran no data on the market, changed nothing outside `red_team/`.
