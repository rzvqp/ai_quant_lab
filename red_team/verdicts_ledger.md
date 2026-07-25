# RED TEAM — VERDICTS LEDGER
### One permanent row per completed review — the public record of what survived and what did not
**Parent:** [CHARTER.md](../CHARTER.md) §6, §13. Append-only. A superseded verdict keeps its row; the new version is added below with a supersede pointer.

| Review id | DC id | Freeze hash (16) | Battery | Verdict | Note | Sealed | Superseded by |
|---|---|---|---|---|---|---|---|
| REVIEW-DC-0001-v1 | DC-0001 | `1f1b3d399f2e9613` | v1.0 | 🟡 NEEDS BETTER EVIDENCE | n=2 visual, no base rate | 2026-07-23 | — |
| REVIEW-DC-0002-v1 | DC-0002 | `9970263b17fdbcb8` | v1.0 | 🟢 CONTINUE INVESTIGATION | pre-registered C4; K05 confound self-named | 2026-07-23 | — |
| REVIEW-DC-0003-v1 | DC-0003 | `e56076c5c4fce6a2` | v1.0 | 🟢 CONTINUE INVESTIGATION | falsifiable re-test of OBS-0017 null | 2026-07-23 | — |
| REVIEW-DC-0004-v1 | DC-0004 | `4560ba15e08226a9` | v1.0 | 🟢 CONTINUE INVESTIGATION | matched-null, sign-stable; Bonferroni/selection flagged; holdout reserved | 2026-07-23 | — |
| REVIEW-DC-0005-v1 | DC-0005 | `7c8750551b31c2e8` | v1.0 | 🟡 NEEDS BETTER EVIDENCE | n=2, folk pattern, no base rate | 2026-07-23 | — |
| REVIEW-DC-0006-v1 | DC-0006 | `ef1e217fd3ff1aeb` | v1.0 | 🟡 NEEDS BETTER EVIDENCE | self-contradicting; scale-confounded | 2026-07-23 | — |
| REVIEW-DC-0007-v1 | DC-0007 | `1823d33ec7394c21` | v1.0 | 🟡 NEEDS BETTER EVIDENCE | n=1 anecdote | 2026-07-23 | — |
| REVIEW-DC-0013-v1 | DC-0013 | `fc8991fbf2f994e7` | v1.0 | 🟢 CONTINUE INVESTIGATION | n=2 (addendum); no-reversal ending recurs | 2026-07-23 | — |
| REVIEW-DC-0014-v1 | DC-0014 | `3cdc39b74e1db801` | v1.0 | 🟡 NEEDS BETTER EVIDENCE | compound shape at n=1 | 2026-07-23 | — |
| REVIEW-DC-0015-v1 | DC-0015 | `f6526ab36f303916` | v1.0 | 🟡 NEEDS BETTER EVIDENCE | distinguishing feature is a sample-extremum | 2026-07-23 | — |
| REVIEW-DC-0016-v1 | DC-0016 | `e1c1c4dce4455e90` | v1.0 | 🟢 CONTINUE INVESTIGATION | n=2 same-hour; ending shape recurs | 2026-07-23 | — |
| REVIEW-DC-0017-v1 | DC-0017 | `dbd07f90a927b2a9` | v1.0 | 🟢 CONTINUE INVESTIGATION | continue as NARROWED — resolution-diversity question, not "hold" (own Addendum B contradicts headline) | 2026-07-23 | — |
| REVIEW-DC-0018-v1 | DC-0018 | `40ce847f27f85220` | v1.0 | 🟡 NEEDS BETTER EVIDENCE | 4-part compound at n=1; sweep-vs-rejection unresolved | 2026-07-23 | — |

| REVIEW-DC-0008-v1 | DC-0008 | `ce52a96e39fcd44d` | v1.0 | 🟢 CONTINUE INVESTIGATION | foundational construction distinction; ~6 instances; news sub-hypothesis self-walked-back | 2026-07-23 | — |
| REVIEW-DC-0009-v1 | DC-0009 | `ac7ffdec7dcd1547` | v1.0 | 🟡 NEEDS BETTER EVIDENCE | rich single-band lifecycle; Addendum D self-contradicts level-as-support | 2026-07-23 | — |
| REVIEW-DC-0010-v1 | DC-0010 | `5855f9606e7070f8` | v1.0 | 🟡 NEEDS BETTER EVIDENCE | hour-specific framing undercut by own addendum + registry counter-instances | 2026-07-23 | — |
| REVIEW-DC-0011-v1 | DC-0011 | `dc0607e02329bfa6` | v1.0 | 🟡 NEEDS BETTER EVIDENCE | outcome recurs 3× but confounded with anomalous-day selection | 2026-07-23 | — |
| REVIEW-DC-0012-v1 | DC-0012 | `4a4791c183230291` | v1.0 | 🟡 NEEDS BETTER EVIDENCE | excellent scannable definition, n=1 (strong 🟡) | 2026-07-23 | — |

**Batch 1 tally (2026-07-23):** 🟢 6 · 🟡 7 · 🔴 0 (DC-0001..0007, 0013..0018).
**Batch 2 tally (2026-07-23):** 🟢 1 · 🟡 4 · 🔴 0 (DC-0008..0012, after handoff reconciliation).
**Portfolio total (18 reviewed):** 🟢 7 · 🟡 11 · 🔴 0. (🟡 is not a rejection.)

---
**Verdict legend:** 🟢 CONTINUE INVESTIGATION · 🟡 NEEDS BETTER EVIDENCE · 🔴 NOT RECOMMENDED — defined in [methodology/VERDICT_RULES.md](methodology/VERDICT_RULES.md). (UNREVIEWABLE is an intake status, not a verdict.)

---

## CONSOLIDATED REGISTER — final reconciliation (ratified 2026-07-25 by Chief Architect under CEO delegation; LEDGER [13]/E13)

**Ratified inventory: 28 candidates** — Alpha #1 = 26 (DC-0001…DC-0026), Alpha #2 = 2 (AP2-DC-0001, **AP2-DC-0002** formally included). Final verdicts per RT-FINAL-0002. These are Red Team **risk/screening** outcomes; final laboratory disposition is the CEO's / Statistician's.

### 🟢 SURVIVED (3) — recommended for Statistician (routing is the CEO's)
| DC | Note |
|---|---|
| DC-0003 | scale-separated re-run of the OBS-0017 null |
| DC-0004 | ⚠️ **holdout consumed** — post-2025-10-23 results are NOT independent confirmatory validation (RT-FINAL-0002 §6); in-sample hypothesis only |
| DC-0008 | M1/M5 concentration-ratio distribution; gates the family |

### 🔴 REJECTED → **ARCHIVED** (7) — not deleted; IDs permanently reserved, never reused
`DC-0006` · `DC-0010` · `DC-0015` · `DC-0017` · `DC-0022` · `DC-0024` · `DC-0025` — each with its legitimate residue surviving elsewhere (see RT-FINAL-0002 §5). Status: **ARCHIVED (ID reserved)**.

### 🟡 NEEDS MORE EVIDENCE (18)
DC-0001, 0002, 0005, 0007, 0009, 0011, 0012, 0013, 0014, 0016, 0018, 0019, 0020, 0021, 0023, 0026, AP2-DC-0001, AP2-DC-0002.

### Consolidated determinations (recorded here only — NOT written into Alpha's tree)
- **RT-DS-0001:** AP2-DC-0001 = **VARIANT OF DC-0018**; determination = attach as an addendum to DC-0018. Alpha #1 is **CLOSED**, no mandate exists there → the physical attachment will not occur; the determination lives in this register as the record of record.
- **RT-DS-0002:** AP2-DC-0002 = **VARIANT OF DC-0023** (extended multi-hour high-volume episode + political-catalyst condition).
- **Audits accepted:** RT-AUDIT-0001 (Alpha #2), RT-AUDIT-0002 (Alpha #1). Both Alpha divisions CLOSED → recommendations retained for any **future** Alpha instance; no active recipient.

*No candidate producer remains. Red Team is in terminal standby.*

### Integrity register — extension (W1–W8 in RT-FINAL-0002 §7)

**W9 — Same defect, two contradictory states in one repository; divisions worked on the wrong one.** *(Integrity risk, not a statistical verdict. Recorded 2026-07-25; LEDGER [14]/E14.)*
- Defect **D3** (`PROJECT_AUDIT.md`) — *matched-null miscalibrated*, severity **HIGH** — is marked **RESOLVED 2026-07-13 on `flow-c-foundation`** via commits **28c35b6, aa5bee3, 69747fd**. On **`statistician-foundation`** (the official line) D3 is **still OPEN**, because those commits were **never merged**.
- **Red Team verification (branch state only — implementation NOT read):** all three commits exist and are contained in `flow-c-foundation`; **none** is contained in `statistician-foundation`. Confirms "never merged."
- **Consequence (as surfaced by the Chief Architect):** the Validation Engine rebuilt from scratch, in F6, a matched-null calibration that already existed — without the adversarial battery of the 2026-07-13 version. Statistician and Research Lab proceeded assuming the method was unvalidated. ~~The 2026-07-13 battery reported FPR = 0.975 under `drift_long` and 0.925 under `trend_short`~~; F6/F6.1 did not test drift at all.
- **Red Team finding:** *the same defect holds two contradictory states in the same repository, and divisions have worked on the wrong state.* Red Team does **not** evaluate which validation is superior — outside its mandate; it ran neither. **No merge performed; no implementation read.** Resolution is a separate matter (the `flow-c-foundation` divergence, W-note in the branch-architecture record).

> **⚠ CORRECTION (LEDGER [15]/E15, 2026-07-25).** The struck line above was factually wrong. **0.975 / 0.925 / 0.25 are the PRE-FIX state** of the first engine version — a defect the adversarial battery *exposed and then fixed* (bootstrap risk/ATR ratio rescaled to ATR at the null entry). **Post-fix: 0.00 / 0.00 / 0.00** across 12 adversarial scenarios, all FPR(0.05) < 0.075, `ALL_SCENARIOS_CALIBRATED = True` (source: `MATCHED_NULL_VALIDATION.md §2` on flow-c-foundation; independent verification: Research Lab commit `e89ded1` / `TRANSFERABILITY_ADDENDUM_v1.1.md` — both confirmed by Red Team against the source). The error was introduced by the Chief Architect and propagated in good faith; it is corrected append-only, not rewritten. **W9's substance is unchanged and its severity does not decrease** — if anything it is greater: the pre-existing version was *more* complete (it carried the battery + the drift-beta control that F6/F6.1 lack) than the F6 reconstruction.
