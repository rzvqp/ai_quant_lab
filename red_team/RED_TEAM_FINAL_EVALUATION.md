# RED TEAM — FINAL CANDIDATE EVALUATION (FALSIFICATION PASS)
### All remaining Alpha #1 + Alpha #2 candidates · one verdict each
**ID:** RT-FINAL-0001 · **Date:** 2026-07-24 · **Auditor:** Red Team · **Mandate:** CEO — Final falsification pass

**Scope:** Alpha #1 DC-0001…DC-0024 (24) + Alpha #2 AP2-DC-0001 (1) = **25 candidates.**
**Basis:** the full corpus already read and analysed this session — `RED_TEAM_PHASE1_REPORT.md` (DC-0001..0018), `RT-AUDIT-0002_ALPHA1.md` (all 24 + 30 addenda), `RT-DS-0001` + `RT-AUDIT-0001` (AP2-DC-0001 + 4 addenda). No new observation performed; no Alpha/KB artifact modified; no statistics run; no strategy implemented.

> **Governance reconciliation (read once).** The CEO ratified (2026-07-24) that Red Team issues *risk verdicts only* and retired "REJECT". This task explicitly requests REJECTED / NEEDS MORE EVIDENCE / SURVIVED. They are therefore Red Team **adversarial-screening recommendations**, not laboratory dispositions:
> - **SURVIVED** = withstood the falsification attempt; a defined, falsifiable test remains → *recommend hand-off to the Statistician* (the permitted "READY FOR STATISTICAL VALIDATION" sense: no major vulnerability obstructs statistical evaluation). **Not** accepted, validated or promoted.
> - **NEEDS MORE EVIDENCE** = not falsified, but too thin / confounded / single-instance to justify statistical work yet.
> - **REJECTED** = Red Team recommends elimination — the candidate does not survive falsification (contradicted by corpus evidence, or unfalsifiable as stated, or its distinct claim duplicates another with nothing surviving). **Final elimination authority remains the CEO's** — confirmed by this task routing SURVIVED onward to the Statistician rather than Red Team closing anything.
>
> Per the single-observation rule ([EVIDENCE_RULES](methodology/EVIDENCE_RULES.md) E10), REJECTED is used only where a **sufficient body** of contrary evidence exists (multiple corpus instances, or self-contradiction within the candidate's own package), never on one contrary instance.

---

## 1. RESULT SUMMARY

| Verdict | Count | Candidates |
|---|---|---|
| 🟢 **SURVIVED** → Statistician | **3** | DC-0003, DC-0004, DC-0008 |
| 🟡 **NEEDS MORE EVIDENCE** | **16** | DC-0001, DC-0002, DC-0005, DC-0007, DC-0009, DC-0011, DC-0012, DC-0013, DC-0014, DC-0016, DC-0018, DC-0019, DC-0020, DC-0021, DC-0023, AP2-DC-0001 |
| 🔴 **REJECTED** (recommend elimination) | **6** | DC-0006, DC-0010, DC-0015, DC-0017, DC-0022, DC-0024 |

**The SURVIVED bar is deliberately strict:** a candidate survives only if a *defined, runnable, falsifiable test* remains after the attack — something the Statistician can actually execute. Exactly three meet it.

---

## 2. THE SURVIVED THREE (hand-off package for the Statistician)

### DC-0003 — Scale inversion (boundary inside vs outside prevailing noise)
- **Duplicate check:** subsumes DC-0002 (DC-0003 says so); not itself a duplicate — it is the general statement.
- **Falsification attempt — failed to break it.** It stakes a **specific, falsifiable prediction on existing data**: re-run OBS-0017's 384 swing-high exceedances *with scale separation*; if the pooled null does not decompose, the candidate dies. That is an unusually clean pass/fail the Statistician can run without new observation.
- **Documented problems (for the Statistician, not blockers):** scale/liquidity entangled (both micro cases in thin Asian tape) — a covariate, not a refutation; class-boundary (multiple of ATR) unspecified; micro n=2.
- **Verdict: SURVIVED.** The only candidate whose decisive test uses data already in hand.

### DC-0004 — NY-session prior-day-high sweep-reject → reversion
- **Duplicate check:** subject-related to the level thread (DC-0005/0007/0009) but methodologically distinct; the only candidate with a defined event/population.
- **Falsification attempt — survived, with caveats it discloses itself.** Defined event, session window and horizon; matched-null p=0.021 (K6), sign-stable across both temporal halves, uniquely significant among six cells. Adversarial pressure did not overturn the in-sample signal.
- **Documented problems (must travel with it):** fails Bonferroni (0.021 vs 0.0083); selection over ~12 cells → in-sample p is not selection-corrected; **its named decisive test — the reserved post-2025-10-23 holdout — has been partly CONSUMED by the reopened observation window (RT-AUDIT-0002 F3).** The Statistician must be told the clean OOS reserve no longer exists in the form the candidate assumes.
- **Verdict: SURVIVED.** The portfolio's only quantitatively-supported candidate; enters as a *hypothesis*, not a result.

### DC-0008 — Sustained vs single-minute construction
- **Duplicate check:** the **root** of the DC-0013…0024 family — not a duplicate; the others are its instances.
- **Falsification attempt — survived and gained.** Operationally defined: *(largest M1/M5 volume share) ÷ (M15 total)* + whether volume returns to baseline before close. ~6 instances. Its own addenda already **falsified its NFP sub-hypothesis** (reframed to day-of-week) — self-falsification it survived by narrowing honestly.
- **Falsifiable test the Statistician can run:** compute the concentration-ratio distribution across all large M15 candles. If unimodal/continuous, the two "constructions" are a visual artifact and much of the family collapses; if bimodal, test whether aftermath differs by type. **This single test gates the whole family.**
- **Documented problems:** the "different aftermath" half is untested; volatility-clustering is an unexcluded general alternative.
- **Verdict: SURVIVED.** Highest-leverage hand-off — resolving it clarifies eleven other candidates.

---

## 3. REJECTED — recommend elimination (6)

*Each carries a sufficient body of contrary evidence or is unfalsifiable as stated. The underlying observation is not discarded — in every case its legitimate residue survives elsewhere.*

### DC-0006 — Extreme relative volume fails to extend
- **Falsified by the corpus's own evidence.** Three independent counter-instances already in the lab: DC-0008 (vol 24,005 → extended to new highs), DC-0013 (29,674 → extended four candles), DC-0017 (30,975 → held/drifted up). Plus a self-reported inversion the next replay day. Plus confounded with DC-0003 (3 of ~5 instances are micro coils where failure is *already* predicted by scale).
- **Duplicate:** the volume-failure claim also lives in DC-0018/DC-0020.
- **Verdict: REJECTED.** A sufficient body of contrary instances exists. Residual question (does volume predict continuation) belongs to **DC-0008**'s ratio test.

### DC-0010 — A consistently quiet hour breaks with a sustained expansion
- **Falsified by its own package + the registry.** Its **own Addendum A** shows the *entire* 2025-08-07 session ran 2–3× baseline with a second spike — an all-day phenomenon, not an hour. The Observation Registry then logs the same hour running ordinary on multiple later days, Alpha concluding *"no consistent single characterization of this hour holds."*
- **Verdict: REJECTED** as an hour-specific claim. Residue ("some days run hot") is not a candidate and belongs to the Volatility primitive.

### DC-0015 — Eleven-candle run, longest observed
- **Unfalsifiable as stated.** The distinguishing feature is a **sample extremum** — "longest so far" cannot be false and is superseded automatically (indeed DC-0022 later claimed to supersede it). A maximum is an order statistic, not a hypothesis; there is no observation that could contradict it.
- **Duplicate:** the construction is DC-0008/DC-0013's; only the record differs.
- **Verdict: REJECTED.** Its content (duration distribution) belongs to the family, where it has a denominator.

### DC-0017 — NFP-scale 12:30 impulse holds its gains
- **Contradicted by its own submitted evidence.** Addendum B documents a comparable-magnitude 12:30 print that gave back the *entire* move; Addendum A shows the original drifted higher over ~4h15m rather than "holding." The headline claim is refuted inside its own package (sufficient body: its own addenda + DC-0008's five-instance 12:30 series showing no convergent outcome).
- **Verdict: REJECTED** as the "holds" claim. The resolution-diversity question survives in DC-0008's 12:30 series.

### DC-0022 — NY-afternoon record duration + magnitude
- **Unfalsifiable AND factually wrong.** Distinguishing claim is a magnitude/duration record (sample extremum — no failure state) **and it is incorrect against Alpha #1's own artifacts**: it declares 86.75pt a family record while DC-0013's Addenda D/F/H already recorded 89.4 / 100.97 / **180.53**pt. Its own text concedes the mechanism "has ample precedent."
- **Verdict: REJECTED.** No distinct falsifiable claim survives; the observation should be an addendum to the DC-0013 family.

### DC-0024 — London-morning record decline (125.7pt)
- **Unfalsifiable + duplicate.** Distinguishing feature is again an all-time magnitude record (sample extremum), whose record chain omits the larger DC-0013 addendum values (RT-AUDIT-0002 F2); the "large move then partial recovery" shape duplicates DC-0019/DC-0021 at larger scale; mechanism conceded precedented. *(Credit: it honestly reports a 48.1% breach of its own 42.7% convention — good conduct, but it does not restore a falsifiable distinct claim.)*
- **Note:** rated HIGH (not CRITICAL) on *conduct* in RT-AUDIT-0002; REJECTED here on *falsifiability of its distinct claim* — different axes.
- **Verdict: REJECTED.** Belongs to the record-register / recovery-shape family as evidence, not as a standalone edge.

---

## 4. NEEDS MORE EVIDENCE (16) — not falsified, not yet Statistician-ready

| DC | Duplicate / overlap | Key weakness (falsification attempt did not break it, but…) |
|---|---|---|
| **DC-0001** | isolated (only velocity candidate) | n=2, pace never measured (visual only); **content hash does not reproduce** (admin, RT-AUDIT-0002 I1); alt = regression-to-mean unexcluded. |
| **DC-0002** | ⊂ DC-0003 | K05 long-beta confound self-declared (3/4 up in a bull → "resolves with bias" ≈ "goes up"); **"compression" is undefined**, so the Statistician cannot select events → not yet testable. |
| **DC-0005** | level thread (DC-0007/0009) | n=2, one impure ("died inside the range"); folk knowledge; no base rate of third-tests that did nothing. |
| **DC-0007** | overlaps DC-0011, level thread | n=1; excursion (~2.4pt) sits inside local noise by DC-0003's own criterion. |
| **DC-0009** | level thread | one band; **Addendum D contradicts Addendum C** (level-memory not durable) — but the touch-count question itself is unrefuted, just unsupported at n=1 level. |
| **DC-0011** | overlaps DC-0007 | 3 instances but **all on days pre-flagged anomalously active** (unbroken confound); Addendum B's reclaim was multi-minute, violating the "single-minute" title. |
| **DC-0012** | overlaps DC-0021 | cleanest operational definition in the corpus, but the shape is seen once (n=1). |
| **DC-0013** | **family container** (root DC-0008) | ~12 instances via 11 addenda, but as stated it is **not a single falsifiable claim** — the family exhausts the outcome space. Needs a defined sub-claim before statistical work; still reads "One instance". |
| **DC-0014** | family (root DC-0008) | compound 3-part shape at n=1, at an hour the registry says has no consistent behaviour; decompose before resourcing. |
| **DC-0016** | family (root DC-0008) | **strongest family member** — ending shape (marginal-high→reversal) recurred across 2 same-hour instances, magnitude shown variable; still n=2. |
| **DC-0018** | overlaps DC-0006/DC-0020; **replicated by AP2-DC-0001** | 4-part compound; sweep-vs-rejection ambiguity unresolved by its own text. The independent Alpha #2 replication *strengthens* the core (n=2 across observers) but does not resolve the compound structure. |
| **DC-0019** | overlaps DC-0021 (large move → partial recovery) | n=1, record-framed; triggering condition + session + volume band all new at once. |
| **DC-0020** | strongly overlaps DC-0018 | n=1, record-framed (volume record = sample extremum); 18:00 explicitly disclaimed as a mechanism; the other 18:00 instance was a suspected **data artifact**. |
| **DC-0021** | overlaps DC-0012 (absorption) | own text: "each phase individually replicates an already-documented mechanism"; n=2, same session window, consecutive days. |
| **DC-0023** | composition of DC-0021/DC-0022 | n=1; all elements precedented; the DC-0022→DC-0023 sequencing is n=1, self-labelled observation-only. |
| **AP2-DC-0001** | **VARIANT OF DC-0018** (RT-DS-0001) — independent replication, not a separate line | **feed-provenance blocker**: volume series may span OANDA / FusionMarkets (all claims are volume-ratios); M15-only; 2 of 5 "instances" same session. Its evidence attaches to DC-0018. |

---

## 5. CROSS-CUTTING DUPLICATE MAP (for the CEO)

- **One construction, twelve objects:** DC-0008 (root) → DC-0013, 0014, 0015, 0016, 0017, 0018, 0019, 0020, 0021, 0022, 0023, 0024, and Alpha #2's AP2-DC-0001. Distinguished by post-hoc descriptors (session, duration, magnitude, direction, ending), not by mechanism. **The family as a set cannot be falsified — it now catalogues every possible outcome.**
- **Level-interaction thread:** DC-0005 / DC-0007 / DC-0009 (touch counts 3, 3-then-swept, 7→9).
- **Extreme-volume-failure thread:** DC-0006 / DC-0018 / DC-0020 (+ AP2-DC-0001).
- **Absorption thread:** DC-0012 / DC-0021.
- **Large-move-then-partial-recovery thread:** DC-0019 / DC-0021 / DC-0024.
- **Subset relation:** DC-0002 ⊂ DC-0003.

*Consolidation is a later-stage decision (Statistician + Reasoning Engine), never Red Team — recorded as findings only; no structure changed.*

---

## 6. HAND-OFF TO STATISTICIAN

Red Team recommends the following three be handed to the Statistician for statistical evaluation, each with its defined test and its disclosed caveats:

1. **DC-0003** — run OBS-0017's 384 exceedances with scale separation; pass = the pooled null decomposes.
2. **DC-0004** — assess selection-corrected significance; **flag: the reserved OOS holdout is compromised (post-cutoff observation occurred).**
3. **DC-0008** — compute the M1/M5 concentration-ratio distribution across all large M15 candles; test bimodality and aftermath-by-construction. *(Highest leverage — gates the family.)*

*Red Team does not contact the Statistician (per constitution); this is a recommendation for the CEO to route.*

---

## 7. WHAT RED TEAM DID NOT DO

No Alpha #1, Alpha #2, KB or Statistician artifact modified. No candidate or addendum created. No new observation, no statistics, no strategy, no promotion, no consolidation, no official status change. REJECTED/SURVIVED are Red Team screening recommendations; final disposition is the CEO's and statistical evaluation is the Statistician's.

---

**Evaluation ends. Red Team halts and awaits CEO decision.**
