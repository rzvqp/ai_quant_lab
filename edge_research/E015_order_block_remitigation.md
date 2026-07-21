# E015 — Order Block Re-Mitigation

**Program**: 40-Edge Alpha Discovery Program (Flow A). **Protocol**: `EDGE_RESEARCH_PROTOCOL.md`.
**Category**: Price Action / Structure. **Permanent, append-only research log.**

**Third edge run under the CEO's "full edge profile" directive (2026-07-22)**, reusing
`edge_research/_profile.py`. Data loaded exclusively via `_common.load()`; no direct CSV read anywhere
in `e015_order_block_remitigation.py`.

## V0 (frozen, registered 2026-07-20, verbatim)

> An order block that has already been mitigated once can be revisited a second time and still produce
> a reaction.

Measured outcome (as registered): reaction rate/magnitude on the second (and later) mitigation vs. the
first.

## Method (full disclosure in `e015_order_block_remitigation.py`)

- **Order block (OB)**: identical, disclosed construction to E010 (displacement bar >1.5×ATR(prior),
  directional body ≥50%, originating opposite-colored bar within 10 prior bars) — reused unchanged for
  cross-edge consistency, not re-tuned.
- **Mitigation (visit)**: a contiguous span of bars overlapping the OB zone; consecutive touches within
  a 4-bar gap merge into one visit. Visits are numbered sequentially (1st, 2nd, 3rd+) in time order.
- **Deliberate methodological safeguard against the CEC-001 risk** (`CROSS_EDGE_RESEARCH_CANDIDATES.md`):
  visit tracking for a given OB stops the first time a later bar's CLOSE decisively violates the zone
  (E010's own "breaker" definition). This uses only information available up to and including that bar
  — no visit's own numbering (1st/2nd/3rd) depends on knowledge of the OB's more-distant future beyond
  "has it broken as of now." This is a materially different, weaker form of conditioning than CEC-001's
  own look-ahead risk (see "Known residual risk" below for the honest caveat that remains).
- **V0 test**: for each visit number, does price react (reverse away from the zone, in the OB's
  ORIGINAL polarity direction)? `_profile.py::movement_profile()`, same 7 horizons/5 ATR thresholds
  used throughout this session. Visit-1 vs. visit-2 vs. visit-3+ compared directly — a within-population,
  repeated-measures design (no external "does an OB work at all" control needed here; that question is
  E010's/CEC-001's own).
- **Control**: random-matched zones (seed=42), same visit/censoring logic, to check whether any
  visit-number pattern is generic rather than OB-specific.
- **Data split**: `data_split_id = pre_holdout_2025-10-23T09-15-00Z_v1`,
  `holdout_cutoff = 2025-10-23T09:15:00+00:00`, `holdout_excluded = true`.

## A. V0 test — headline result: **NOT SUPPORTED — a sharp, clean DECAY, not "still produces a
reaction"**

| Timeframe | Visit | n | Continuation rate | Mean net return @ 1 bar (ATR) |
|---|---|---|---|---|
| M15 | **1st** | 6,918 | **76.2%** | +0.647 |
| M15 | 2nd | 3,981 | 54.3% | +0.017 |
| M15 | 3rd+ | 3,060 | 52.2% | −0.073 |
| H1 | **1st** | 1,873 | **76.3%** | +0.693 |
| H1 | 2nd | 1,074 | 54.0% | −0.046 |
| H1 | 3rd+ | 822 | 51.5% | +0.002 |

The **first** mitigation shows a real, substantial edge (76% continuation, matching the magnitude of
E010's own unflipped-OB finding — unsurprising, since "unbroken OB, first touch" describes much the same
population). **The second mitigation collapses almost exactly to a coin flip** (54.3%/54.0%), and the
**third-plus mitigation stays at or below that** (52.2%/51.5%, with the 20/50-bar horizons actually
turning slightly NEGATIVE on M15 — −0.21/−0.62 ATR — the opposite of "still produces a reaction").
Random-matched control confirms this decay is not a generic multi-visit artifact — it starts at ~50%
already (as expected for pure noise) and stays flat across visit number (49.7%→51.5%→51.3%, M15),
**unlike the real OB group, which starts high and collapses toward that same ~50% floor**.

**Statistical significance**: visit-1 vs. visit-2 continuation-rate difference is overwhelming on both
timeframes (χ² p=3.1×10⁻¹²³, M15; p=1.2×10⁻³⁵, H1); visit-1 vs. visit-3+ similarly (p=8.0×10⁻¹²⁶, M15;
p=2.8×10⁻³⁷, H1). **V0's specific claim — that a second-or-later mitigation "still produces a
reaction" — is not supported; the data instead shows the reaction is concentrated almost entirely in
the first mitigation and decays to noise thereafter.**

## B. Timeframe profile

| Timeframe | Available? | n OBs | Visit-1 rate | Visit-2 rate | Visit-3+ rate |
|---|---|---|---|---|---|
| M1 | **No** — confirmed unavailable, `EDGE_DISCOVERY_ROADMAP.md` §1 | — | — | — | — |
| M5 | **No** — same reason | — | — | — | — |
| **M15** | Yes | 6,929 | 76.2% | 54.3% | 52.2% |
| **H1** | Yes | 1,875 | 76.3% | 54.0% | 51.5% |
| H4 / D1 | Not tested — registry's own listed timeframes for this edge are M5/M15/H1 only |

Both timeframes agree closely on both the magnitude of the visit-1 edge and the sharp visit-2 collapse
— the decay is not an artifact of one timeframe's resolution.

## C. Movement profile (M15, visit-1 vs. visit-2, primary config)

| Horizon (bars) | Visit-1 mean ret (ATR) | Visit-2 mean ret (ATR) | Visit-1 MFE/MAE | Visit-2 MFE/MAE |
|---|---|---|---|---|
| 1 | +0.647 | +0.017 | 1.22 / 0.51 | 0.85 / 0.88 |
| 5 | +1.294 | +0.022 | 2.96 / 1.11 | 1.85 / 1.88 |
| 20 | +1.331 | +0.209 | 4.63 / 2.44 | 3.70 / 3.57 |
| 50 | +1.404 | +0.299 | 7.09 / 4.70 | 5.87 / 5.64 |

Visit-1's MFE/MAE are asymmetric (favorable side clearly larger at every horizon) — a genuine
directional signature. Visit-2's MFE/MAE are close to symmetric at every horizon — the same
non-directional signature found for E010's/E012's own broken/flipped groups.

## D. Context profile (M15, visit-1 vs. visit-2)

| Dimension | Visit-1 range | Visit-2 range | Verdict |
|---|---|---|---|
| Session | 73.7%–78.5% | 49.3%–56.5% | Decay present in every session |
| Volatility regime | 72.0%–78.8% | 52.6%–55.7% | Decay present in every regime |
| Trend context | 74.9%–76.7% | 54.0%–55.0% | Decay present in every context |

The decay is not concentrated in one session, regime, or trend context — it is a pervasive, structural
feature of the second visit, not a niche condition. Day-of-week and finer daily-range-position slices
were not separately run this pass (same disclosed scope choice as E010/E012, given the pattern is
already this uniform across the dimensions tested).

## E. Controls and falsification

- **Random-matched-visit control**: confirms the decay pattern is NOT a generic "any zone's Nth visit
  weakens" artifact — the random group starts at ~50% (visit-1) and stays there (visit-2, visit-3+),
  whereas the real OB group starts at ~76% and decays DOWN to that same ~50% floor. This is a
  meaningfully different, more informative shape than a flat null would be, and rules out "the movement
  profile machinery itself manufactures decay" as an explanation.
- **Explanations tested and not sufficient alone**: displacement-threshold selection (1.2×/1.5×/2.0×
  ATR — decay shape identical at every threshold, section G), session, volatility regime, and trend
  context (section D) — none explains away the decay.

## F. Edge improvement search (V1)

**No V1 candidate is proposed for V0 as registered** (a general "2nd+ mitigation still reacts" claim) —
that claim is not supported. However, unlike E010/E012 (flat nulls), this edge's own evidence points to
a **specific, well-evidenced, narrower refinement worth naming as an unfrozen V1 candidate**: *"An order
block's reaction is concentrated in its FIRST mitigation; by the second mitigation, reaction magnitude
and continuation rate have already collapsed to noise, robust across timeframe, displacement threshold,
session, volatility regime, and trend context."* This candidate:
- has an economic/behavioral logic (a zone's informational content about resting orders/imbalance is
  plausibly consumed by the first real test of it);
- has a large sample (n=6,918/3,981 M15, n=1,873/1,074 H1);
- shows a consistent effect (visit-1 > visit-2 on every slice tested, no exceptions);
- is superior to the natural control (random-matched shows no such decay);
- is reasonably parameter-insensitive (stable across 3 displacement thresholds);
- is stable across session/volatility/trend segments and across years (section G);
- has NOT been tested net of costs (Discovery-stage scope, per protocol §0.2).

Per the CEO's own rule (F.6), this is flagged as a genuinely broad, non-fragile pattern (not confined to
a small segment) — but it is still only a Discovery-stage candidate, not Frozen, and it inverts rather
than extends V0's own wording (V0 claims the 2nd mitigation still works; the evidence says the opposite
— that the 1st mitigation is where the real information is). Per protocol §1, this is recorded as a new,
appended V1 version of the hypothesis, not a retroactive edit of V0.

## G. Robustness (visit-1 vs. visit-2, M15 unless noted)

- **Displacement-threshold sensitivity**: visit-1/visit-2 continuation 75.3%/53.8% (1.2×ATR, n=11,363
  OBs), 76.2%/54.3% (1.5×ATR, n=6,929), 78.5%/53.9% (2.0×ATR, n=3,163) — the decay shape is stable
  across a >3× range in event count; no threshold was searched for or selected.
- **Yearly stability**: 2022 (n=88/52, thin) 78.4%→48.1%; 2023 (n=2,491/1,395) 76.0%→54.5%; 2024
  (n=2,420/1,393) 75.7%→54.7%; 2025 (n=1,919/1,141) 76.9%→53.8%. H1: 2023 76.8%→54.4%, 2024 78.2%→55.6%,
  2025 73.2%→51.2%. **The decay magnitude (roughly 20-25 percentage points) is essentially constant
  across every full year and both timeframes** — this is one of the most stable patterns found this
  program.
- **Concentration risk**: thousands of events per visit-number bucket in every slice — not produced by
  a handful of extreme observations.
- **Multiple-testing risk**: many slices tested, uncorrected; the decay direction and rough magnitude
  replicate so consistently (every year, every session, every regime, every trend context, every
  displacement threshold) that this is not plausibly a multiple-testing artifact.
- **Cost/slippage impact**: not modeled — Discovery-stage scope only; the visit-1 edge's own
  cost-adjusted tradability is an explicit open question for any future Validation-stage work.
- **Known residual risk (honest, in the spirit of CEC-001's own scrutiny)**: visit-2 and visit-3+
  populations are conditioned on the OB having survived (not yet broken) up to that visit — a much
  milder form of the survivorship concern flagged for CEC-001 (it conditions only on "not yet broken as
  of now," not on "will never break," so it does not share CEC-001's own look-ahead/tautology severity),
  but it is not zero risk and is disclosed rather than ignored.

## H. Practical profile

**What it is**: order blocks are claimed to remain valid reaction zones across repeated tests, not just
their first. **When it appears**: whenever an OB gets touched a second time before breaking — common
(3,981 second-visit events on M15 alone). **Timeframe**: clear and consistent on M15 and H1; M1/M5
unavailable. **Session/regime**: the decay from visit-1 to visit-2 is uniform everywhere tested — no
session or regime preserves the visit-1-level edge into visit-2. **Average movement**: visit-1 produces
a real, asymmetric, favorable-biased move (+0.65 ATR by 1 bar, growing to +1.4 ATR by 50 bars); visit-2
produces essentially none. **Frequency**: common. **Controls**: random-matched shows the decay shape is
OB-specific, not a generic artifact of the movement-profile machinery. **Can it be used alone?** The
*first*-mitigation version might be (matching E010's own unflipped-OB strength) — but that is a
different, already-flagged (CEC-001) observation, not this edge's own V0. **V1 candidate?** Yes — the
"reaction concentrated in the first mitigation only" reformulation (section F), Discovery-stage,
unfrozen. **Confidence level**: high confidence in the DECAY finding specifically (very consistent
across every dimension tested); the CEC-001-adjacent first-visit effect itself carries the same
residual-risk caveats already registered there. **Key limitation**: below the ~5-6yr horizon (clean data
~2.85yr); no formal out-of-time split beyond the yearly breakdown; the OB/mitigation operational
definitions are one disclosed, reasonable choice, not the only possible one.

## Answers to the 9 mandatory Discovery questions

1. **Does the edge exist at all?** Not as V0 states it. A real, strong, well-evidenced effect exists —
   but it is concentrated in the FIRST mitigation and decays sharply by the second, the reverse of V0's
   own claim that a second mitigation "still" works.
2. **Frequency?** ~6,929 OBs on M15 alone over ~2.85 years; 3,981 (57%) get a second visit before
   breaking, 3,060 (44%) get a third-or-later.
3/4. **Days it works/fails?** Not separately sliced by day-of-week this pass (deferred, same reasoning
   as E010/E012).
5. **Sessions?** The visit-1→visit-2 decay occurs in every session; no session preserves visit-1's edge.
6. **Volatility regimes?** Decay occurs in every regime.
7. **Filters that improve it?** None found for "does visit-2 still work" — the decay is remarkably
   uniform. The narrower V1 (section F) is itself the "filter" that survives: restrict to visit-1 only.
8. **Conditions that invalidate it?** V0 as registered is invalidated broadly — the qualifier "2nd and
   later" is precisely the condition under which the effect disappears.
9. **Out-of-sample?** Yearly breakdown (section G) shows the decay pattern replicating in every full
   year on both timeframes — the closest available check in this pass.

## Current status

**Version: V0 → V1 candidate proposed (unfrozen, Discovery-stage only — not a Frozen Candidate).**
**Verdict: NONE ISSUED** — per protocol §2, below the ~5-6yr horizon. Remains in **Stage 2 — Discovery,
full profile complete**.

**V0 NOT SUPPORTED as registered.** **V1 candidate (unfrozen)**: "An order block's reaction is
concentrated in its first mitigation; the second and later mitigations show no directional edge over a
random-matched control, robust across timeframe, displacement threshold, session, volatility regime,
trend context, and year." This does not rescue V0 — it replaces "2nd mitigation still works" with
"2nd mitigation does not," which is why it is recorded as a new, separately-versioned V1, not a
retroactive edit of V0 (protocol §1/§7).

**Next steps if revisited**: (a) Tier-0 history extension; (b) day-of-week slice; (c) formal
out-of-time split; (d) cost-adjusted tradability check of the visit-1-only V1 candidate, if the CEO
authorizes moving toward Frozen Candidate/Validation for it; (e) cross-reference with CEC-001
(`CROSS_EDGE_RESEARCH_CANDIDATES.md`) before any such move, since the visit-1 effect and CEC-001's own
unbroken-zone effect likely describe closely related (possibly the same) underlying phenomenon and
CEC-001's own risk register (look-ahead/tautology/survivorship) should be re-checked against this
edge's own, more sequential/lower-risk construction before treating either as independently confirmed.

**Artifacts**: `e015_order_block_remitigation.py`, `e015_order_block_remitigation_results.json` (full
output, both timeframes, all slices, sensitivity, and yearly stability).
