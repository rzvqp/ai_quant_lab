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
