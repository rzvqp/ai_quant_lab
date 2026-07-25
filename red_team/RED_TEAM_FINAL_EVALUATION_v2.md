# RED TEAM — FINAL CANDIDATE EVALUATION (REVISED)
### RT-FINAL-0002 · Full reconciliation before Statistician hand-off
**Date:** 2026-07-25 · **Auditor:** Red Team · **Mandate:** CEO — final reconciliation before hand-off
**Supersedes:** RT-FINAL-0001 (2026-07-24, 25 candidates), which is preserved unmodified. Any prior hand-off is **halted**.

> **Governance framing (unchanged from RT-FINAL-0001):** these are Red Team **risk/screening recommendations**, not laboratory decisions. SURVIVED = "no major vulnerability obstructs statistical evaluation" (the permitted READY-FOR-STATISTICAL-VALIDATION sense) → *recommend hand-off*; REJECTED = "recommend elimination, does not survive falsification" — **final elimination authority is the CEO's**; NEEDS MORE EVIDENCE = not falsified, too thin for statistical work. Single-observation rule (E10) respected. Nothing modified in Alpha #1 / Alpha #2 / KB; no statistics run; nothing sent to the Statistician.

---

## 0. ⚠️ INVENTORY DISCREPANCY — READ FIRST

The task specified **27 candidates** (Alpha #1 = 26, Alpha #2 = **1**). Reconstructing **exclusively from the official repositories** as instructed, the true frozen inventory is **28**:

| Source | Count | IDs |
|---|---|---|
| Alpha #1 (`ai_quant_lab-alpha-automation`) | **26** | DC-0001 … DC-0026 (index = folders = handoff FROZEN lines = 26; all FROZEN v1) |
| Alpha #2 (`ai_quant_lab/alpha_instance_2`) | **2** | AP2-DC-0001, **AP2-DC-0002** |
| **TOTAL** | **28** | |

**The delta is `AP2-DC-0002`** — "A Major Scheduled Political Catalyst… Extended High-Volatility Episode", **FROZEN / SUBMITTED 2026-07-25** (in the Alpha #2 index and handoff log, hash `ff55a8ba…`, 1 addendum). The Alpha #2 instance was subsequently **CLOSED by CEO instruction** (final replay position 2024-12-20 ~10:00 UTC; final state "2 candidates frozen"). It was frozen *after* the task's stated inventory was composed, which is why the count reads 27 there.

**Red Team reconciled to the repository, per your instruction not to miss candidates** (the exact failure this task exists to correct). AP2-DC-0002 is analysed below (Phase 0 screening: `RT-DS-0002`). **This 28-vs-27 discrepancy is flagged for CEO ratification** — Red Team does not unilaterally expand a CEO-set scope, but also does not silently drop a real frozen candidate.

---

## 1. WHAT WAS ANALYSED (coverage reconciliation)

| Candidate set | Covered by | Individual review file? |
|---|---|---|
| DC-0001 … DC-0018 | RED_TEAM_PHASE1_REPORT + reviews/ | ✅ yes |
| DC-0019 … DC-0024 | RT-AUDIT-0002 (per-DC) + RT-FINAL-0001 | ✅ **backfilled this pass** (reviews/DC-0019..0024) |
| **DC-0025, DC-0026** | **this pass (new)** | ✅ created |
| AP2-DC-0001 | RT-DS-0001 + RT-AUDIT-0001 | ✅ (screening doc) |
| **AP2-DC-0002** | **this pass (new)** — RT-DS-0002 | ✅ created |

**All 28 are now analysed.** RT-FINAL-0001 covered 25; this revision adds DC-0025, DC-0026 and AP2-DC-0002, and backfills the six missing DC-0019..0024 individual review files per the constitution.

---

## 2. RECONCILED VERDICT TALLY (28)

| Verdict | Count | Candidates |
|---|---|---|
| 🟢 **SURVIVED** → recommend Statistician | **3** | DC-0003, DC-0004 *(integrity-flagged, §5)*, DC-0008 |
| 🟡 **NEEDS MORE EVIDENCE** | **18** | DC-0001, DC-0002, DC-0005, DC-0007, DC-0009, DC-0011, DC-0012, DC-0013, DC-0014, DC-0016, DC-0018, DC-0019, DC-0020, DC-0021, DC-0023, DC-0026, AP2-DC-0001, AP2-DC-0002 |
| 🔴 **REJECTED** (recommend elimination) | **7** | DC-0006, DC-0010, DC-0015, DC-0017, DC-0022, DC-0024, DC-0025 |

3 + 18 + 7 = **28.** ✓

**Changes from RT-FINAL-0001:** +DC-0025 (REJECTED), +DC-0026 (NEEDS MORE EVIDENCE), +AP2-DC-0002 (NEEDS MORE EVIDENCE). All 25 prior verdicts unchanged.

---

## 3. ELIGIBLE FOR STATISTICIAN (SURVIVED — the hand-off package)

| DC | Defined falsifiable test the Statistician can run | Caveats that must travel with it |
|---|---|---|
| **DC-0003** | Re-run OBS-0017's 384 swing-high exceedances **with scale separation**; pass = the pooled null decomposes. Uses existing data. | scale/liquidity entangled (covariate); class boundary (ATR multiple) unspecified; micro n=2. |
| **DC-0004** | Assess **selection-corrected** significance of the NY PDH sweep-reject reversion (matched-null p=0.021, sign-stable, unique among 6 cells). | **HOLDOUT INTEGRITY FLAG — see §5.** Also fails Bonferroni; selection over ~12 cells. Enters as a hypothesis, not a result. |
| **DC-0008** | Compute the M1/M5 concentration-ratio distribution across all large M15 candles; test **bimodality** and **aftermath-by-construction**. **Highest leverage — gates the whole DC-0013 family.** | "different aftermath" half untested; volatility-clustering is an unexcluded general alternative. |

---

## 4. NEEDS MORE EVIDENCE (18) — not falsified, not yet Statistician-ready

DC-0001 *(hash non-reproducible, RT-AUDIT-0002 I1)* · DC-0002 *("compression" undefined → not yet selectable; K05 confound)* · DC-0005 · DC-0007 · DC-0009 *(Addendum D self-contradiction)* · DC-0011 *(anomalous-day confound; title contradicted by Addendum B)* · DC-0012 · DC-0013 *(family container, ~12 instances, still reads "One instance")* · DC-0014 · DC-0016 *(strongest family member, n=2)* · DC-0018 *(replicated by AP2-DC-0001)* · DC-0019 · DC-0020 *(near-duplicate of DC-0018)* · DC-0021 · DC-0023 *(paralleled by AP2-DC-0002)* · **DC-0026** *(distinct thin-liquidity mechanism, M15/M5/M1-verified, n=1 — strongest of the new batch)* · AP2-DC-0001 *(VARIANT OF DC-0018; feed-provenance blocker)* · **AP2-DC-0002** *(VARIANT OF DC-0023; catalyst untestable in-window, n=1)*.

---

## 5. RECOMMENDED FOR ELIMINATION (REJECTED — 7)

| DC | Why it does not survive falsification | Legitimate residue survives at |
|---|---|---|
| **DC-0006** | Contradicted by ≥3 corpus counter-instances (DC-0008/0013/0017 extended on extreme volume) + self-inversion next day + DC-0003 scale confound | DC-0008 ratio test |
| **DC-0010** | Own Addendum A shows the whole session ran hot, not the hour; registry logs the hour ordinary later | Volatility primitive |
| **DC-0015** | "Longest run" = sample extremum → unfalsifiable; already superseded | DC-0013 family duration distribution |
| **DC-0017** | Own Addendum B contradicts the "holds" headline; DC-0008's 12:30 series shows no convergent outcome | DC-0008 12:30 series |
| **DC-0022** | Record claim **factually wrong** vs DC-0013 addenda (180.53pt) + unfalsifiable extremum; mechanism precedented | DC-0013 family + running-max register |
| **DC-0024** | Unfalsifiable magnitude record; record chain omits larger addendum values; duplicates recovery family | recovery family + running-max register |
| **DC-0025** | Volume-record headline **superseded by its own Addenda A/B** (39,353→41,995→42,808) before review; mechanism precedented | velocity dimension → DC-0013 family; record → running-max register |

*In every case the underlying observation is not discarded — only the standalone candidate is not recommended for continuation in its current form. The CEO holds final elimination authority and may still choose revision, Addendum, or archiving.*

---

## 6. DC-0004 — MANDATORY HOLDOUT INTEGRITY WARNING *(CEO-requested, §5)*

> **The reserved out-of-sample holdout named by DC-0004 as its decisive test has been CONSUMED at the laboratory level.**
> DC-0004 (Additional Notes) states its decisive test is *"out-of-sample confirmation on the reserved holdout (post 2025-10-23), which is a CEO-gated resource and has deliberately not been spent."* However, Alpha #1's reopened Discovery window observed **post-cutoff** market data (DC-0019 … DC-0026 all fall after `2025-10-23T09:15Z`; confirmed in DC-0019's Additional Notes and `SESSION_CLOSE_ALPHA_DISCOVERY_WINDOW_2025-10-23.md`).
>
> **Consequence for the Statistician:** any result computed on post-2025-10-23 data **cannot be treated as independent confirmatory validation** of DC-0004. The holdout has been contaminated by discretionary observation; whatever OOS reserve DC-0004 assumed no longer exists in clean form. DC-0004 remains SURVIVED **only** as an in-sample hypothesis with a real, sign-stable, selection-uncorrected signal — its confirmatory test must be re-designed on data provably untouched by the reopened window, or treated as unavailable.

This warning is attached to the hand-off record and to `audit/LEDGER.md`.

---

## 7. INTEGRITY WARNINGS REGISTER (all)

| # | Warning | Affects |
|---|---|---|
| W1 | **Holdout consumed** — post-cutoff observation contaminates DC-0004's decisive test | DC-0004 (§6) |
| W2 | **DC-0001 content hash does not reproduce** (17/18 reproduce; DC-0001 does not) — Alpha OPEN item, administrative | DC-0001 |
| W3 | **Record bookkeeping is internally inconsistent** — DC-0022/DC-0024/DC-0025 record claims contradict DC-0013's own addenda / their own addenda | DC-0022, 0024, 0025 |
| W4 | **DC-0025 / DC-0026 have no `metadata_v1.json`** (structural divergence from DC-0001..0024; hash verified via in-document == handoff) | DC-0025, DC-0026 |
| W5 | **The 42.7% organic-construction threshold rests on one anchor** and is now split to hundredths (42.68 vs 42.70) | all post-DC-0018 volume candidates |
| W6 | **Alpha #2 confidence calibration** rates n=1 events Medium where Alpha #1 rates Low | AP2-DC-0001, AP2-DC-0002 |
| W7 | **AP2-DC-0001 feed provenance** — volume series may span OANDA / FusionMarkets | AP2-DC-0001 |
| W8 | **Inventory discrepancy** — repo holds 28, task stated 27; delta = AP2-DC-0002 (frozen 2026-07-25) | §0 |

---

## 8. WHAT RED TEAM DID NOT DO
No Alpha #1 / Alpha #2 / KB / Statistician artifact modified. No candidate or addendum created. No new observation, no statistics, no strategy, no promotion, no consolidation, no official status change. Nothing sent to the Statistician — the SURVIVED list is a recommendation for CEO routing. RT-FINAL-0001 preserved unmodified; this document supersedes it for inventory completeness.

---

**Revised evaluation ends (28 candidates reconciled). Red Team halts and awaits CEO approval.**
