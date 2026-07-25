# DERIVED HYPOTHESIS REGISTER — Flow A

**Purpose.** A pre-registration log for hypotheses that are *not* one of the 40 registered V0 edges but
were *produced by* Flow A's Set-A Discovery (e.g. an edge's own natural control surfaced a stronger,
opposite-signed effect than V0 itself). Per `EDGE_RESEARCH_PROTOCOL.md` §2B and §2C, every such
hypothesis:

- is a **separate hypothesis**, corrected in its **own** multiple-comparison family (never folded into
  the 40-V0 Benjamini-Hochberg family to borrow its threshold);
- must be **frozen in writing here, in full, before Set B is touched** — an un-frozen hypothesis can
  never use Set B (it becomes permanently in-sample);
- carries an explicit **provenance** and **Set-B-eligibility** declaration.

Freezing rule (this file): a hypothesis is *frozen* once its contract below is committed. Its exact
operationalization (event definition, primary test statistic, threshold, control, tie-breaks) is locked
at that commit and may not be adjusted based on any Set B result. This file is append-only.

**This batch frozen:** 2026-07-25. **Freezing commit:** the commit that adds this file (recorded by hash
in the follow-up once known). **Authorizing decision:** CEO directive 2026-07-25 (Task B, three priority
threads; Decisions 1–3).

---

## Set B confirmation family (pre-declared BEFORE any Set B run)

Three hypotheses below are **Set-B-eligible** (E010-D1, E012-D1, E015-V1). They form **one
Benjamini-Hochberg family of 3** for the Set B confirmation:

- **Primary confirmation timeframe = M15** for each (one primary test per hypothesis → family size 3).
- BH at FDR α = 0.05: rank-1 critical `0.05×1/3 = 0.01667`, rank-2 `0.03333`, rank-3 `0.05`.
- H1 is reported as **secondary/supporting** evidence only and is **not** part of the primary family.
- Every Set B result is labelled **REGIME-LIMITED** (§2A) — Set B is a single continuation of the same
  2022-2026 bull regime, not an out-of-regime test.

The fourth hypothesis (E028-INV) is **NOT Set-B-eligible** (RULE 2B-1, burned) and is frozen
in-sample-only, awaiting a genuinely unseen future set.

---

## E010-D1 — Unflipped Order Block Continuation

**Discovery Identity**
1. **Hypothesis ID / name:** E010-D1 — "Unflipped-OB directional continuation."
2. **Provenance:** derived from **E010 (Breaker Block Snatch)** Discovery, Set A — specifically E010's
   *own natural control* (order blocks that are never closed-through). E010's V0 (breaker/flip
   continuation) was NOT supported; the unflipped control instead showed a large directional effect.
   Original-40 registry lineage: **E010**, an enforcement-from-start edge → **Set B INTACT** (RULE 2B-2).
3. **Set-B-eligible:** **YES.**
4. **Frozen:** 2026-07-25. **Freezing commit:** this commit.
5. **Discovery classification:** structural-behavior Discovery, not scalping-validated (§9 blocked).
6. **Status:** Derived Discovery Candidate — not validated alpha, not an execution rule.

**V0 (this hypothesis, frozen verbatim):**
> "An order block that has **not** been closed-through within the test horizon ('unflipped'), once its
> zone is revisited, continues in its **original** polarity direction significantly more often than a
> random-matched-distance zone with no real structure."

**Exact operationalization (locked; identical to `e010_breaker_block_snatch.py`):** OB detection with
`PRIMARY_DISP = 1.5×ATR14[prior]`, `BODY_FRAC = 0.5`, revisit within `REVISIT_HORIZON = 480` M15 bars
(5 trading days). "Unflipped" = OB never closed-through within the horizon. "Continuation" = movement in
the OB's original polarity per `_profile.py::movement_profile()`, primary readout at the **1-bar
horizon** (E010's headline readout).

**Pre-registered primary test (M15, Set B):** continuation rate of unflipped-OB revisits vs the
**random-matched-distance control** (same distance profile, no real structure) — two-proportion test.
**Direction pre-committed:** unflipped-OB continuation **> control**. Discovery (Set A) reference to beat:
unflipped-OB ≈ 88.0% (M15) vs control ≈ 50%.
**Pass criterion:** p < BH-adjusted threshold for its rank in the family of 3 **AND** effect in the
pre-committed direction.

**Look-ahead caveat inherited (CEC-001):** "unflipped within horizon" is defined using the same forward
window the outcome is measured over. This confound is **not** resolved by Set B confirmation; a positive
Set B result confirms replicability of the *pattern as defined*, not that the look-ahead risk is absent.
Recorded so it can never be quietly dropped.

---

## E012-D1 — Un-inverted Fair Value Gap Continuation

**Discovery Identity**
1. **Hypothesis ID / name:** E012-D1 — "Un-inverted-FVG directional continuation."
2. **Provenance:** derived from **E012 (Inverted Fair Value Gap)** Discovery, Set A — E012's own natural
   control (FVGs never violated/inverted). E012's V0 (post-inversion continuation) was NOT supported;
   the un-inverted control showed a large directional effect (independently mirroring E010-D1).
   Original-40 lineage: **E012**, enforcement-from-start → **Set B INTACT** (RULE 2B-2).
3. **Set-B-eligible:** **YES.**
4. **Frozen:** 2026-07-25. **Freezing commit:** this commit.
5. **Discovery classification:** structural-behavior Discovery, not scalping-validated.
6. **Status:** Derived Discovery Candidate.

**V0 (frozen verbatim):**
> "A fair-value gap that has **not** been violated/inverted within the test horizon, once revisited,
> reacts in its **original** (gap-fill) role significantly more often than a random-matched-distance
> control."

**Exact operationalization (locked; identical to `e012_inverted_fvg.py`):** FVG detection with
`PRIMARY_MIN_GAP = 0.0×ATR14` (no size filter), revisit within `REVISIT_HORIZON = 480` M15 bars.
"Un-inverted" = FVG never violated within the horizon. "Reaction" per `movement_profile()`, primary
readout at the **1-bar horizon**.

**Pre-registered primary test (M15, Set B):** continuation/reaction rate of un-inverted-FVG revisits vs
**random-matched-distance control**, two-proportion test. **Direction pre-committed:** un-inverted >
control. Set A reference: ≈ 86.8% (M15) vs ≈ 50%.
**Pass criterion:** p < BH-adjusted threshold for its rank **AND** pre-committed direction.

**Look-ahead caveat inherited (CEC-001):** same as E010-D1 — "un-inverted within horizon" uses the
outcome window. Not resolved by Set B.

---

## E015-V1 — First-Mitigation-Concentrated Order-Block Reaction

**Discovery Identity**
1. **Hypothesis ID / name:** E015-V1 — "OB reaction is concentrated in the FIRST mitigation."
2. **Provenance:** derived from **E015 (Order Block Re-Mitigation)** Discovery, Set A. E015's V0
   (2nd+ mitigation still reacts) was NOT supported; Discovery instead found a sharp decay after the
   first mitigation. This is E015's own existing unfrozen V1 candidate, now **frozen**.
   Original-40 lineage: **E015**, enforcement-from-start → **Set B INTACT** (RULE 2B-2).
3. **Set-B-eligible:** **YES.**
4. **Frozen:** 2026-07-25. **Freezing commit:** this commit.
5. **Discovery classification:** structural-behavior Discovery, not scalping-validated.
6. **Status:** Derived Discovery Candidate. **Designed to avoid CEC-001 look-ahead:** visit numbering is
   purely sequential / forward-only, not dependent on the OB's more-distant future.

**V0 (frozen verbatim):**
> "An order block's directional reaction is concentrated in its **first** mitigation (a large reaction in
> the OB's original polarity); the **second and later** mitigations show no directional edge over a
> random-matched-distance control."

**Exact operationalization (locked; identical to `e015_order_block_remitigation.py`):** OB detection
`PRIMARY_DISP = 1.5×ATR14[prior]`, `BODY_FRAC = 0.5`; mitigation = contiguous span overlapping the OB
zone, with the session's disclosed cooldown; visit tracking STOPS at the first later breaker-close
(forward-only classification). Track within `TRACK_HORIZON = 960` M15 bars (10 trading days). Reaction
per `movement_profile()`.

**Pre-registered primary test (M15, Set B):** visit-1 reaction rate vs visit-2+ reaction rate
(two-proportion / χ² on visit-1 vs visit-2), **and** visit-2+ vs random-matched control (seed=42) not
distinguishable. **Direction pre-committed:** visit-1 ≫ visit-2+, and visit-2+ ≈ control.
Set A reference: visit-1 ≈ 76% vs visit-2+ ≈ 50-54% (χ² p=3.1e-123 M15).
**Pass criterion:** visit-1 vs visit-2 p < BH-adjusted threshold for its rank **AND** pre-committed
direction (visit-1 higher), **AND** visit-2+ not significantly above control.

---

## E028-INV — Inverted Fibonacci OTE (Shallow-Retracement Continuation)  — NOT Set-B-eligible

**Discovery Identity**
1. **Hypothesis ID / name:** E028-INV — "Shallow retracements continue better than the OTE zone"
   (inverted relative to textbook ICT, which favors the 0.618-0.79 OTE zone).
2. **Provenance:** derived from **E028 (Fibonacci OTE)** Discovery. E028's V0 (OTE is the favorable
   continuation zone) was NOT supported; the clean run found shallow retracements continue *more* often
   than the OTE zone. Original-40 lineage: **E028** — one of the five **TERMINAL-HOLDOUT-BREACHED**
   edges (its 2026-07-20 run analyzed Set B, verified via `e028_fibonacci_ote_results.json`).
3. **Set-B-eligible:** **NO — BURNED (RULE 2B-1).** Set B was already seen for E028; it may never be
   used for this hypothesis, in any form, not even labelled.
4. **Frozen:** 2026-07-25. **Freezing commit:** this commit.
   **Marked: `PRE-REGISTERED, AWAITING UNSEEN DATA`** — pre-committed for a future, genuinely unseen set
   (a real "Set C" accruing as the live feed advances past 2026-07-13).
5. **Discovery classification:** structural-behavior Discovery, not scalping-validated.
6. **Status:** Derived Discovery Candidate — reported **REGIME-LIMITED, IN-SAMPLE ONLY**; no OOS
   confirmation, no p-value presented as OOS evidence.

**V0 (frozen verbatim):**
> "After an impulsive leg, price that retraces **shallowly** (retracement depth < 0.618 of the leg)
> continues in the impulse direction **more** often than price that retraces into the **OTE** zone
> (0.618-0.79) — the reverse of the textbook OTE claim."

**Exact operationalization (locked; identical to `e028_fibonacci_ote_clean.py`):** k=5 fractal
zigzag; retracement-depth bins `[-0.001, 0.382, 0.618, 0.79, 1.0, inf]` →
`lt_382 / 382_618 / OTE_618_79 / 79_100 / gt_100`. **Shallow** = `lt_382 ∪ 382_618` (depth < 0.618).
**OTE** = `OTE_618_79` (0.618 ≤ depth ≤ 0.79). "Continued" = leg continues in impulse direction
(`continued = 1`). **Pre-registered test:** χ² on 2×2 (shallow vs OTE) × (continued vs not).

**In-sample Set A finding (REGIME-LIMITED, NOT confirmation):** shallow 63.0% vs OTE 57.0% continuation,
χ² = 4.89, **p = 0.027**. Under the §2C 40-V0 BH family this **does not pass** (0.027 > 0.00125), and it
is in any case in-sample-only. **No Set B run. No OOS claim.**

---

## Confirmation harness — frozen operationalization (2026-07-25, BEFORE Set B is touched)

Locked here, per CEO STEP-2 conditions, before any Set B access. Applies to the three Set-B-eligible
hypotheses (E010-D1, E012-D1, E015-V1). Implemented in `edge_research/_setb.py::countable_events` and
`edge_research/e_setb_confirm.py`; enforced by tests in `edge_research/test_setb.py`.

**Condition 2 — warmup is DERIVED, not chosen.** The deepest indicator lookback across the three
hypotheses' operationalizations is `vol_regime` (`_common.vol_regime`, trailing `window=200`) computed on
`atr14` (`rolling(14)`): the first index at which a 200-bar window contains no NaN ATR is
`13 + 199 = 212` (0-based) → the **213th bar**. Other lookbacks are smaller (ATR-14 = 14; OB
`LOOKBACK_OB` = 10; FVG 3-bar; `context_features` trend = 20 bars). **`WARMUP_BARS = 250 = 213 + 37`.**
Margin justification (37 M15 bars ≈ 9.25h, ~one London+NY span): guarantees not merely Set B bar 0 but
the first ~37 Set B bars' events anchor on a fully-clean `vol_regime`, and absorbs rolling-window edge
effects. Warmup bars come from Set A (already seen at Discovery), are marked `in_setb=False`, and are
lookback-only — they can never be counted as events.

**Condition 1 — no event may be counted on a warmup bar.** `countable_events` drops any event whose
anchor bar has `in_setb=False`; the dropped count is reported as `excluded_warmup`. This closes the path
by which Set A could silently contaminate the Set B confirmation. Tested (`test_warmup_event_excluded`).

**Condition 3 — right-edge rule (pre-registered NOW).** Set B ends at 2026-07-13T06:00Z; there is no data
after. An event whose **full forward result window** does not fit inside the loaded frame is
**EXCLUDED** from the count, and the excluded number is **reported separately** (`excluded_right_edge`).
It is never counted with a truncated result, never counted with a missing result treated as zero, and
never dropped silently after results are seen. Full-window requirement `anchor_idx + 1 + forward_needed
≤ len(frame)`, with `forward_needed`:
- **E010-D1, E012-D1:** `REVISIT_HORIZON (480) + max(HORIZONS) (50) = 530` bars; anchor = `confirm_idx`.
- **E015-V1:** `TRACK_HORIZON (960) + max(HORIZONS) (50) = 1010` bars; anchor = `ob_idx`.
Tested (`test_right_edge_event_excluded`).

**Condition 4 — journal records warmup.** Every `load_setb` call records `n_warmup` and the warmup
window `[first_epoch, last_epoch]` (or null when `warmup_bars=0`). Tested (`test_journal_records_warmup_window`).

**Per-hypothesis primary test (M15 primary; H1 secondary/supporting only):**
- **E010-D1:** among revisited unflipped OBs, continuation rate vs a **random-matched-distance control**
  measured the SAME way — the control reuses E010's exact `random_matched` construction (seed=42,
  distances resampled from the unflipped group's own revisit distances, zone half-width 0.25×ATR) and,
  for each revisited random zone, classifies its `movement_profile` outcome in the zone's assigned random
  direction → a control continuation rate. Two-proportion χ². **Direction pre-committed: unflipped >
  control.**
- **E012-D1:** identical to E010-D1 but on un-inverted FVGs; control = E012's exact `random_matched`
  (seed=42, zone half-width 0.15×ATR) with the same outcome extension. **Direction: un-inverted > control.**
- **E015-V1:** visit-1 continuation vs visit-2 continuation (two-proportion χ², `p_v1_vs_v2`), **direction
  pre-committed visit-1 > visit-2**, AND visit-2+ continuation not above the random-matched-visit control
  (seed=42, `random_matched_visits`). OB anchored on `ob_idx ∈ Set B`.

**BH family = these 3 M15 primary tests.** rank-1 crit 0.05×1/3 = 0.01667, rank-2 0.03333, rank-3 0.05.
Every result labelled **REGIME-LIMITED**. If none pass, that is the reported result — no subset search,
no alternative threshold, no reformulation.

---

## STEP 3 — INVESTIGATION record (NOT a confirmation). CEO ruling 2026-07-25

The Set B run executed (journal `setb_access_journal.jsonl`, 2026-07-25T19:34Z; harness
`e_setb_confirm.py`, raw output `e_setb_confirm_results.json`). **It is recorded here as INVESTIGATION,
not confirmation. No result is committed as a confirmed edge.** The family-size question turned out to be
irrelevant (all three raw p are tiny); the disqualifier is **definitional circularity**, code-verified
below (per CEO instruction: verified in code, not documentation).

**Raw p-values (M15 primary / H1 secondary), retained as audit only:**

| Hypothesis | M15 p | H1 p | Set A finding replicated on Set B? |
|---|---|---|---|
| E010-D1 | 2.0e-21 | 2.8e-05 | unflipped cont 89.8% vs control 52.6% |
| E012-D1 | 9.6e-12 | 1.2e-03 | un-inverted cont 90.3% vs control 57.5% |
| E015-V1 | 1.3e-36 | 1.7e-08 | visit-1 76.5% vs visit-2 51.8% |

### Code verification — E010-D1 / E012-D1: CIRCULAR → **NOT CONFIRMED**

- **Same horizon.** `e010_breaker_block_snatch.py`: unflipped classification uses
  `end = min(j+1+REVISIT_HORIZON, n)` (l.90) with `REVISIT_HORIZON=480` (l.49); the continuation outcome
  uses `revisit_and_react` `end = min(idx+1+horizon, n)` (l.118), same `horizon=480`, `idx=confirm_idx=j`
  (l.107). The outcome window is nested inside the selection window. `e012_inverted_fvg.py` is identical
  (l.72 / l.95, `REVISIT_HORIZON=480`).
- **Same-sided thresholds.** "Violated" = a `close` beyond the zone (e010 l.92-101); "reversal" = an
  adverse ≥1×ATR move (`_profile.py::movement_profile` l.36-38, 57-66). A 1-ATR adverse move almost
  always entails a close beyond the zone → a violation → the OB/FVG is removed from the unflipped/
  un-inverted group. The selection therefore **suppresses reversals while retaining continuations** — the
  89.8% / 90.3% is largely the selection condition measuring itself, not an edge.
- This is the exact confound the freeze already flagged (CEC-001 caveat, above) — under-weighted then as
  a "caveat"; it is disqualifying. **E010-D1 and E012-D1 fall definitively.**

### Code verification — E015-V1: NO circularity → **SUSPENDED (open)**

- `visits_for_ob` collects visits only for `i < break_pos` (l.108), but **visit-1 membership does not
  depend on its own forward outcome**: a reversal at visit-1 (even one that produces the break) is
  RETAINED — the break at a later index does not remove the earlier visit-1. `build_visit_rows` applies
  no outcome-dependent filter (l.119-137). Contrast E010, where a break removes the entire OB.
- visit-1 vs visit-2 is measured on the same OB population; the decay cannot be a selection artifact of
  the E010 kind. **p_v1_vs_v2 = 1.3e-36 remains real and unexplained. SUSPENDED — not rejected, not
  confirmed — pending investigation.**

### Recorded separately (CEO)
`control_with_outcome` (the primary comparator for E010-D1/E012-D1) was authored this session, was NOT
part of the original E010/E012 Discovery, and was frozen with knowledge of the Set A numbers — i.e. **the
primary comparator for two of the three hypotheses was not pre-registered.** This does not change the
verdicts (they fall on circularity, not on the control), but it stands on the record.

**Dispositions:** E010-D1 → NOT CONFIRMED. E012-D1 → NOT CONFIRMED. E015-V1 → SUSPENDED.

### E015-V1 dependence-structure MEASUREMENT (CEO task 2026-07-25) — facts only, no interpretation

Reconstructed from the same STEP 3 events (`e015_setb_dependence.py`, `e015_setb_dependence_results.json`;
visit-1/visit-2 row counts match STEP 3 exactly). **STRUCTURE only — no outcome, no p, no threshold.**
Handed to the Statistician to estimate effective sample size. E015-V1 stays SUSPENDED. Chi-square treats
each visit ROW as independent; the counts below quantify how far from independent they are.

**M15 (primary):**
1. **Counts per group.** Distinct OB zones = **1,315**. Total visit rows = **3,219**. visit-1 rows =
   **1,546**, visit-2+ rows = **1,673** (visit-2 bucket 925, visit-3+ bucket 748). Distinct zones per
   bucket: v1 1,315 / v2 759 / v3+ 334.
2. **Visits per zone.** median **2**, max **10**, mean 2.05. Zones with exactly 1 visit = **556**; with
   >1 = **759**. Histogram (visits→#zones): 1→556, 2→425, 3→180, 4→80, 5→40, 6→21, 7→5, 8→5, 9→2, 10→1.
3. **Forward-window overlap.** For each visit, other visits landing in its 50-bar movement window
   `[vidx+1, vidx+50]`: median **10**, mean 10.1, max 30; only **0.59%** of visits have zero overlap.
   Distribution: 0→19, 1→4, 2→47, 3-5→343, 6-10→1,454, >10→1,352.
4. **Duplication & collisions.** OB events with visits **1,546** vs distinct zones **1,315** → **231
   duplicate OB events** (multiple displacement bars mapping to the same zone, each re-emitting the same
   visits). Total rows 3,219 vs distinct (zone, visit-bar) pairs 2,695 → **524 exact-duplicate visit
   rows**. Same bar: **1,446** visits share a bar across 613 bars (263 bars mix different zones, 350 are
   same-zone-only). Same hour: **2,211** visits fall in hours holding >1 visit, across 823 hours.

**H1 (secondary):** distinct zones 245, total rows 698, visit-1 299 / visit-2+ 399; visits/zone median 2
max 8; forward-overlap median 10 mean 10.3 (0.43% zero); 54 duplicate OB events, 144 exact-duplicate
rows; 371 same-bar visits across 156 bars (63 diff-zone), 371 same-hour across 156 hours.

No conclusion drawn here on validity or effective n — that is the Statistician's call.
