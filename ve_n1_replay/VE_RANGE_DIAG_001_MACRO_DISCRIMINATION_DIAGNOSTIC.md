# VE-RANGE-DIAG-001 — RANGE V4.3 MACRO Discrimination Diagnostic

**DIAGNOSTIC ONLY · ZERO_VALIDATION_WEIGHT · NO_PARAMETER_CHANGES · NO_V4_4_IMPLEMENTATION**
**MB3-025→048 remain SEALED and were not touched in this mandate.**

Investigates the failure Red Team characterized as `MB3_MACRO_GENERALIZATION_NOT_SUPPORTED`
(RT-RANGE-MB3-001, commit `3496b73`/E89): recall generalizes out-of-sample (~0.68–0.70) but precision/F1/IoU
degrade and the detector does not cleanly separate RANGE from CHANNEL/TREND. Every number below was
independently re-derived from the frozen, hash-verified MB3-001→024 predictions and labels — not copied from
the Red Team report — using the ratified (unmodified) scorer plus a diagnostic instrumentation wrapper around
the frozen, unmodified `bc6b9dc` detector. The frozen reference implementation was not modified in any way.

---

## 0 — Sources, verification, provenance note

- `labels_MB3_001_024.json` (sha256 `6369f5e0…4de`) and `mb3_predictions/predictions.json` (sha256
  `26a7d461…33ba`) — both re-hashed here and matched exactly against the values frozen in commits `fddb986`
  (Statistician label freeze) and `a6b0eb0` (Red Team predictions freeze) before any analysis began.
- Re-running the ratified `blind_runner/scoring.py::score()` on this data reproduces **8 of 9** headline
  aggregate figures from the committed Red Team report exactly: GT=38, detected=62, TP=26, FN=12, recall=0.684,
  precision=0.419, IoU (p25/median/p75/max = 0.213/0.352/0.501/0.776), confirm-delay (mean/median =
  127.7/42.5), `by_length`, `by_block`, and promotions=49 — all bit-identical to the committed report.
- **One provenance discrepancy, resolved and disclosed, not silently absorbed:** the committed report states
  `FP 36`; my reproduction (and independently, this mandate's own CEO-authored brief) states **39**. Traced to
  source: `36 = 62 detected − 26 TP` (a naive detected-minus-matched-count subtraction); `39 = 62 detected −
  23` where 23 is `len(matched_det_spans)` — the count of *distinct* detected structures that were ever the
  best-IoU match for *any* GT segment, exactly what `scoring.score()`'s own `false_positives_macro` field
  computes. The two differ because **3 of the 62 detected structures were each the best match for two separate
  GT segments in the same window** (documented in §6.C below) — a real property of the data, not a scorer
  bug. `39` is the more precise "structures corresponding to nothing in the ground truth" count and is what
  this diagnostic decomposes, matching the mandate's own framing exactly.
- Escrow note: an escrow-shaped directory is present on this machine; per this mandate's explicit §3
  authorization, the frozen CEO labels and frozen predictions for MB3-001→024 **specifically** were read
  (hash-verified against the frozen commits first). `selection_batch_03.json` and the window payload
  necessarily contain all 48 window definitions; only the 24 `MB3-001…024` entries were ever used beyond
  confirming the batch's structure — nothing about MB3-025→048's content, labels, or bars was decrypted,
  read, or used at any point.
- The frozen detector (`bc6b9dc`, `implementation_fingerprint=f1-only-f5-deferred-2026-08-20`) was re-run
  bar-by-bar via its own public `RangeSemanticEngineV43.observe_closed_bar` API, on the real MB3-001→024
  bars, purely to read out internal `Structure` state (`atr_ref`, `normalized_drift`, touch counts) that
  isn't serialized into `predictions.json`. **This re-run was cross-validated against the frozen
  predictions.json and reproduces every one of the 62 confirmed structures' `structure_id`/`confirm_ts`
  exactly, 0 mismatches** — the detector source file was never edited.

---

## A — Executive finding

**V4.3's MACRO confirmation path (`evaluate_candidate`/`degeneracy_check`, `range_semantic_v4_3.py:403–449`)
has no directional-displacement discrimination at all.** It gates on cluster width (`degeneracy_check`),
minimum duration (`bar − start_ts ≥ d_macro=29`), and touch count (`evaluate_candidate_with_n_touch`,
`n_touch=2` per side) — nothing else. As long as price revisits two boundary levels at least twice each,
holding the width above `2·w_atr·ATR`, for 29+ bars, MACRO confirms as a RANGE — **regardless of whether the
price path between those touches was oscillating or net-drifting the whole time.**

The discriminating signal this needs **already exists in the codebase**: `Structure.normalized_drift()` /
`ConfigV43.s_max` (an OLS-slope-based drift measure, O(1)/bar via `_UnboundedSlope`). But per the code's own
comment (`range_semantic_v4_3.py:1041–1051`, dated to an earlier mandate), it was **deliberately connected
only at INTERNAL depth, and there only as a non-blocking descriptive state label** (`INT_CHANNEL_UP`/
`INT_CHANNEL_DOWN`), never as a gate — because the mandate that built it explicitly forbade INTERNAL
classification from closing MACRO. **It was never extended to MACRO at all.** That is the mechanism: not a
bug in existing logic, but a real capability gap — the one variable designed for exactly this discrimination
was scoped out of the level where 30 of the 39 false positives occur.

This explains the majority of false positives directly. It does **not**, on its own, cleanly fix the problem
(§F, §13 falsification below) — the existing signal has real but incomplete separating power, and a second,
distinct mechanism (§B.2) accounts for a smaller cluster of the remaining false positives.

---

## B — FP decomposition: 39/39 accounted

62 confirmed MACRO structures total; 39 never became any GT segment's best-IoU match (`false_positives_macro`
in the ratified scorer). Full per-structure detail (window, length, block, start/confirm/end, end_reason,
promoted-to-TREND flag, CEO dominant class over the structure's span, `normalized_drift` at confirmation,
touch counts, boundary width in ATR units) captured for all 39 — table condensed below by cause; the complete
per-row data is reproducible from the frozen predictions/labels via the method in §0.

### B.1 — Directional false positives: 30/39 (the Q1-relevant population)

Structure's CEO-dominant class (bar-weighted overlap over its span, mirroring the Red Team report's own
classification methodology) is CHANNEL/TREND/TRANSITION, not RANGE:

| CEO dominant class | count |
|---|---|
| CHANNEL_UP | 14 |
| CHANNEL_DOWN | 8 |
| TREND_DOWN | 4 |
| TREND_UP | 3 |
| TRANSITION | 1 |
| **Total** | **30** |

- **32/39** of all FP (including 25 of these 30) were **promoted to TREND** (`IS_TREND_MACRO` fired) — i.e.
  the detector's own downstream promotion logic frequently agrees these are trending, just too late to stop
  the initial MACRO=RANGE confirmation from having already happened and been counted.
- **33/39** eventually resolved via `BREAKOUT_ACCEPTED` (not `ZONES_DEGENERATE`) — consistent with sitting
  inside a longer directional move that resumes after a pause, rather than being a stable range.
- `normalized_drift` at confirmation: **23/39 (59%)** exceed the existing `s_max=1.60` ceiling already used
  (only at INTERNAL) to detect exactly this condition — see §F for why this is suggestive but not sufficient
  evidence for a clean threshold fix.

### B.2 — Over-segmentation on genuine RANGE ground truth: 9/39 (a distinct, secondary phenomenon)

CEO-dominant class **is** RANGE, but the structure still wasn't anyone's best IoU match. Checked directly:
these are **not** simple duplicate/fragmented detections of one range — several windows (MB3-021: 4
RANGE-dominant structures; MB3-024: 5; MB3-015: 3) contain **multiple, temporally sequential, independently-
confirmed range→breakout episodes**, more than the CEO chose to explicitly segment as separate labeled RANGE
spans. This looks like a granularity mismatch between the detector's per-episode output and the CEO's
labeling protocol (which segments coarser, sometimes-merged spans) at least as much as it looks like a
detector defect — it needs its own dedicated look (§G), not folded into the Q1 directional-confusion story.

### B.3 — Two windows with zero CEO MACRO RANGE ground truth (mandatory negative controls): 4/39

`MB3-007` (1 FP) and `MB3-020` (3 FP) — full trace in §E; both are already counted within B.1 above (all 4
are directional: 1 CHANNEL_DOWN + 3 TREND_DOWN).

---

## C — FN decomposition: 12/12 accounted

Every missed CEO RANGE segment traced via its window's full per-bar reason-code chronology (not inferred from
aggregate stats). **Zero of the 12 are boundary/IoU-quality failures on an already-confirmed structure** — all
12 are formation/confirmation-timing failures:

| Category | count | mechanism |
|---|---|---|
| `FORMED_NEVER_CONFIRMED_WINDOW_ENDED_BEFORE_CONFIRM` | 4 | a candidate was actively forming toward the GT span when the window's bars ran out — purely mechanical truncation, not a semantic miss |
| `FORMED_NEVER_CONFIRMED` — stuck at `ESTABLISHING_FEW_SWINGS` | 5 | touch-count gate: never accumulated ≥2 confirmed swings on **both** sides within the GT span before the episode ended or the window closed |
| `FORMED_NEVER_CONFIRMED` — killed by `ZONES_DEGENERATE` | 3 | one or more successive candidates over the span had boundary width ≤ `2·w_atr·ATR`, killed before ever reaching the duration/touch gates (MB3-014 shows 3 successive candidates in the same span, each killed this way) |

No case shows a structure that reached `OK_RANGE_MACRO` inside the GT span but scored a miss on boundary/IoU
grounds — recall loss here is entirely about *whether/when* confirmation happens, never about confirmed-but-
inaccurate geometry.

---

## D — Length effect (96 ≪ 288 < 480): quantified, and it is "more time to fire," not "better recognition"

| L | eligible bars after `d_macro=29` warm-up | matched-structure confirm-delay (mean / median) | confirm_ts as fraction of window (mean) |
|---|---|---|---|
| 96 | 67 (69.8% of window) | 34.4 / 29.0 | 0.50 |
| 288 | 259 (89.9% of window) | 89.0 / 36.0 | 0.68 |
| 480 | 451 (94.0% of window) | 121.6 / 77.5 | 0.62 |

The decisive number: **the median confirm-delay for a matched structure in a 480-bar window (77.5 bars)
alone exceeds the *entire* eligible-bar budget of a 96-bar window (67 bars)**, before even accounting for the
`d_macro=29` warm-up both must pay first. A large share of what confirms cleanly at L=480 mechanically could
not have finished confirming inside L=96's total available runway, independent of any pattern-recognition
quality. This is corroborated directly by §C: **all 4 pure-truncation FN happen in the 96/288-bar windows**,
and 3 more L=96 misses are `ESTABLISHING_FEW_SWINGS`-stuck (still gathering touches when time/data ran out).
None of the 15 L=480 windows produced a miss.

**Caveat, stated plainly:** window length and GT segment length are not drawn independently (a longer window
plausibly also tends to contain longer labeled spans), so this is not a fully controlled experiment. But the
duration-budget mechanical argument — d_macro consuming 30% of a 96-bar window's total length vs. 6% of a
480-bar window's, and empirical confirm-delays for genuine matches regularly exceeding what a short window
can even offer — is sufficient on its own to explain the gradient without needing to invoke any actual
improvement in the detector's ability to tell RANGE from CHANNEL/TREND at longer lengths. Verdict: **MORE TIME
TO EVENTUALLY FIRE, not better recognition.**

---

## E — Negative-control traces: MB3-007 and MB3-020

### MB3-007 (96 bars, CEO: CHANNEL_DOWN[0–31] → CHANNEL_UP[32–41] → CHANNEL_DOWN[42–96], no RANGE anywhere)

One confirmed structure (`sid=1`, start=2, confirm=**31**, end=84 via `BREAKOUT_ACCEPTED`, promoted to TREND).
Bar-by-bar: `BETWEEN_EPISODES`(0–8) → `ESTABLISHING_FEW_SWINGS`(9–25, boundary clusters populate: `bu` gets
its first member at bar 17, `bl` at bar 18) → `TOO_SHORT_MACRO`(26–30, touches now sufficient but
`bar−start_ts<29`) → **`OK_RANGE_MACRO`** at bar 31, the instant the duration gate clears. The structure's
CEO-dominant class over its life is CHANNEL_DOWN (71 of 82 overlap bars). `slope_at_confirm = −0.219`
(consistently negative — the price genuinely trended down through the whole formation), `normalized_drift =
2.14` (above `s_max=1.60`). **Confirmation fires the exact bar the duration floor is satisfied, with no check
of the clearly one-directional path that got it there.**

### MB3-020 (288 bars, CEO: TREND_DOWN[0–160] → CHANNEL_UP[161–216, "countertrend inside the dominant bearish
structure"] → TREND_DOWN[217–288])

Three confirmed structures, all over TREND_DOWN spans, in a visible **cascade**: candidates 1→2→3 (bars
9–75) are each killed by `ZONES_DEGENERATE` in succession as price keeps marching down without truly
consolidating — then candidate **4** (start=75, confirm=**104**) finally clears the width/duration/touch
gates and confirms, immediately followed by candidate **6** (confirm=145) and **7** (confirm=261), each
`BREAKOUT_ACCEPTED` in turn. Candidates 4 and 6 are explicitly assigned `role="TREND_CONTINUATION_CONFIRMED"`
by the detector's own post-hoc role-classification machinery (`ROLES_V43`) — **the system already has, and
uses, the concept "this was actually trend continuation," it just applies that label only after the
structure has already been confirmed and counted as a RANGE.** Candidate 7's drift (0.73) sits well under
`s_max` despite its CEO-TREND_DOWN label — a case where the CEO's broader multi-region judgment differs from
what's locally visible to a structure with no context beyond its own boundaries; a genuine ambiguity, not
cleanly a detector error.

---

## F — Discrimination analysis: does an existing variable actually separate the populations?

Tested `normalized_drift` at confirmation (the drift signal that exists but isn't wired to MACRO) directly,
comparing the 23 unique matched-GT structures against the 30 directional-GT false positives:

| group | n | drift mean | drift median | % over s_max=1.60 | boundary width (×ATR) mean | touches (up/dn) mean | % promoted |
|---|---|---|---|---|---|---|---|
| matched (TP) | 23 | 2.091 | 1.719 | 56.5% | 4.29 | 2.74 / 3.61 | 73.9% |
| FP, directional GT | 30 | 2.278 | 1.755 | 63.3% | 3.53 | 3.07 / 3.03 | 83.3% |

**The distributions substantially overlap — `normalized_drift` alone does not cleanly separate true RANGE
from false RANGE-on-CHANNEL/TREND**, even though its mean/median are directionally higher for the false-
positive group. Checked whether this is a duration artifact (since `normalized_drift = |slope|·n_bars/ATR`
scales with the structure's whole confirmed lifetime, and TP structures show far higher variance in
confirmation delay, §D): **no** — correlation between `normalized_drift` and `n_bars_at_confirm` is
essentially zero (r = −0.024 overall, −0.03 within each group). That specific hypothesis is falsified; the
overlap is real, not a duration confound.

A pure-rate alternative (`|slope|/ATR`, no duration multiplier) separates *slightly* better in direction
(TP mean 0.060 vs FP mean 0.089) but a diagnostic-only sweep across candidate thresholds (not a selection —
no threshold is proposed here, per §10) shows the same shape: every operating point that rejects most
directional FPs also rejects a large fraction of genuine TPs. **No single existing variable, at any single
threshold, cleanly separates the two populations.**

**Other variables checked, not separating well either:** touch counts (both groups average 2.7–3.6 per side,
essentially indistinguishable), boundary width in ATR units (FP mean actually *narrower*, 3.53 vs 4.29 —
opposite of a naive "too wide = fake range" intuition), and promoted-to-TREND rate (elevated in both groups,
73.9% vs 83.3% — directionally useful but a lagging/circular signal, since promotion is itself a downstream
consequence of the same missing discrimination, not an independent early signal).

---

## G — Architecture conclusion

```
MULTIPLE_CORRECTIONS_REQUIRED
```

Not `ARCHITECTURAL_REDESIGN_REQUIRED`: the MACRO/INTERNAL hierarchy, sweep/breakout state machine, and
promotion logic all behave as contracted (independently re-verified here via 0-mismatch replay against the
frozen predictions) — the gaps are localized capability gaps in specific gates, not a broken overall design.

Not `NARROW_CORRECTION_LIKELY`: two distinct, independently-confirmed mechanisms are in play, at different
scopes and different levels of readiness —

1. **Dominant (30/39 FP, well-characterized, root cause code-verified):** MACRO confirmation has zero
   directional-displacement gate. The needed variable exists but isn't wired at this depth. **However**,
   §F's falsification shows the existing signal/threshold is *not* a clean drop-in fix — connecting it as-is
   would trade a meaningful chunk of false positives for a comparably-sized loss of true positives. A real
   fix here needs feature refinement/calibration work, not a one-line gate insertion.
2. **Secondary (9/39 FP, distinct mechanism, under-characterized):** over-segmentation / granularity mismatch
   between multiple genuine range→breakout episodes and coarser CEO labeling. Needs its own investigation
   before any correction is even hypothesized with confidence.

Two independent-enough problems, at two different levels of evidentiary readiness, is exactly
`MULTIPLE_CORRECTIONS_REQUIRED`, not one narrow patch.

---

## H — Candidate V4.4 hypothesis (not implemented, not authorized)

```
Observed defect:
MACRO confirmation (evaluate_candidate/degeneracy_check) has no directional-displacement check; the
existing normalized_drift/s_max signal is computed but connected only at INTERNAL depth, as a
non-blocking descriptive label, never as a MACRO gate.

Mechanism:
A boundary-touching, duration-satisfying, width-satisfying price path confirms as MACRO RANGE
regardless of whether it net-drifted the whole time. 30/39 MB3 false positives sit over CEO
CHANNEL/TREND/TRANSITION ground truth this way; the negative-control windows (MB3-007/020) show the
mechanism directly, bar-by-bar.

Candidate correction direction (NOT a specification):
Extend a directional-displacement check to the MACRO confirmation path -- but NOT by wiring the
existing normalized_drift/s_max pair in unchanged. §F shows that exact signal at that exact threshold
rejects 63.3% of directional FPs while ALSO rejecting 56.5% of genuine matched TPs -- collateral
damage roughly as large as the benefit. Any real correction needs its own feature-engineering and
calibration pass (candidates worth exploring: a bounded-window/local drift rate rather than
whole-episode cumulative drift; combining drift with a second signal since no single tested variable
separates cleanly alone; explicitly modeling the MB3-020/sid=7 case where local geometry looks
range-like despite broader-context CEO TREND labeling).

Expected effect (if successfully calibrated):
Reduce the ~30-structure directional-FP class without materially reducing true RANGE recall -- NOT
demonstrated here, only motivated; §13 falsification shows the naive version of this fix does NOT
achieve that tradeoff as-is.

Known risk:
(1) The existing s_max value/formula is not calibrated for MACRO -- reusing it naively costs real
recall, shown directly. (2) Any new threshold must be pre-registered and evaluated on evidence this
mandate did not touch (MB3-025-048 or a fresh batch), never fit against these same 39/23 structures
(mandate §10). (3) The 9-structure over-segmentation class is untouched by this hypothesis entirely
and needs separate work.

Evidence supporting hypothesis:
§A (code-level mechanism trace), §B.1 (30/39 FP directional), §E (two negative-control bar-by-bar
traces), §F (existing-signal direction is correct, magnitude is not sufficient alone).
```

**§13 mandatory falsification, explicit:** the leading hypothesis ("wire up `normalized_drift > s_max` at
MACRO") does **not** survive contact with its own strongest counter-test — applied to the 23 genuine matched
structures, it destroys 13 of them (56.5%), a false-negative rate on true positives nearly as large as its
true-positive rate on false positives (63.3%). It does *not* explain the 9-structure over-segmentation class
at all (only 4 of those 9 exceed the threshold). It is reported here explicitly as a **candidate direction**,
not a validated correction, precisely because the naive form of it fails its own falsification test.

---

## Close-condition summary (mandate §17)

1. **Principal defect:** MACRO confirmation has no directional-displacement gate; the one existing signal
   built for this (`normalized_drift`/`s_max`) was scoped to INTERNAL-only, descriptive-only, and never
   extended to MACRO.
2. **39/39 FP decomposed:** 30 directional (14 CHANNEL_UP/8 CHANNEL_DOWN/4 TREND_DOWN/3 TREND_UP/1
   TRANSITION) + 9 over-segmentation-on-genuine-RANGE (distinct mechanism).
3. **12/12 FN decomposed:** 4 window-truncation, 5 touch-count-insufficient, 3 zones-degenerate-killed, 0
   boundary/IoU-quality failures.
4. **96≪480 explained quantitatively:** duration-budget mechanics (d_macro consumes 30% vs 6% of window
   length) plus empirical confirm-delays that exceed short windows' total runway — **more time to fire, not
   better recognition**.
5. **MB3-007/020 traced bar-by-bar** — both show clean, single, well-defined mechanism instances (§E).
6. **Discrimination variables:** `normalized_drift`/`s_max` and its rate-only variant show real but
   insufficient separating power; touch count and boundary-width/ATR do not separate meaningfully; promotion
   rate is a lagging/circular signal.
7. **Architecture conclusion:** `MULTIPLE_CORRECTIONS_REQUIRED` (§G).
8. **Candidate V4.4 hypothesis:** narrowly stated in §H, **not implemented**.
9. **Known risks of the hypothesis:** naive-threshold collateral damage on true positives (falsified
   directly, §13); the 9-structure secondary class remains unaddressed; any real threshold work requires a
   fresh pre-registered mandate on untouched evidence (mandate §10).
10. **Recommended next mandate (not started here):** a feature-engineering/calibration mandate scoped
    strictly to the MACRO directional-discrimination gap, explicitly required to (a) pre-register any
    candidate feature/threshold before touching evidence, (b) evaluate on data not used to derive the
    hypothesis (MB3-025→048 or a fresh batch, under Red Team's control as before), and (c) separately
    characterize the 9-structure over-segmentation class before folding it into the same fix. A second,
    smaller mandate to characterize B.2 in isolation may be warranted before that.
11. **Red Team audit points:** independently re-derive the 39/23 split and the FN categorization from the
    same frozen artifacts (§0 gives exact hashes and method); verify the 0-mismatch replay claim in §0 and
    §F's instrumentation independently (re-run `bc6b9dc` bar-by-bar, do not trust this report's captured
    values without a separate reproduction); check whether the over-segmentation class (§B.2) has a cleaner
    explanation than offered here; confirm §D's duration-budget argument does not simply relocate to a
    different confound Red Team can see and VE could not (e.g. GT segment length vs window length
    correlation, explicitly disclosed here as unchecked).

`self_declared_pass=false` — this is a diagnostic report, not a validation artifact.
`MACRO_INDEPENDENT_BLIND_PREPARATION_AUTHORIZED` is unaffected by this mandate (no evidence consumed that
would change it). No wheel, no V4.4 code, no threshold/config/detector/scorer/label change, no Strategy
Catalog/Alpha/AI Trader/LIVE_SHADOW/broker action. Next owner: **CEO** (decision on recommended next
mandate), then **Red Team** (audit points above).
