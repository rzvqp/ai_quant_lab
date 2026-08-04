# RED TEAM — CODE ATTACK · Level-1 H4 regime classifier
### RT-CODE-A-0009 · Target: `code/regime_classifier.py` @ `82b1ca3` (discovery-mk-matrix-v1)
**Date:** 2026-08-02 · **Auditor:** Red Team · **Spec:** STAT-LEVEL1-REGIME-H4-SPEC-v1.0 (`7a9013d`, manifest v2.7.49). Level 1, step 3 of 4. **Checklist only: lookahead, leakage, circularity, ambiguity, overfitting, hidden params, reproducibility. No data run · nothing modified · no remedy.** Numeric checks used synthetic OHLC (pure function; engine + `market_state`/`market_structure` deps imported read-only from the branch).

## VERDICT — **PASS_WITH_LIMITATIONS.**
Causal (proven numerically), reproducible, no hidden parameters, no outcome-overfitting, fail-closed correct, W=30 derivation correct, the compression/expansion collapse measured-justified. The limitations are real but none is a correctness failure: a **structural-candidate circularity**, a **"RANGE" misnomer**, soft-assignment that **cannot guard a mis-defined band**, the "undetectable window error" claim being **approximate not exact**, and the CEO "no-regime→no-trade" condition **emitted but not yet wired**.

---

## CHECKLIST

**Lookahead — PASS (proven at source + numerically).** Volatility window is trailing `[i-W+1, i]` inclusive (`_volatility_axis`), `i<W-1` → UNAVAILABLE (warmup). `run` is propagated with `idx<=i` only (`_propagate_run`). `expansion[i]` uses `atr[i-1]`+bar i (causal). **Numeric proof:** classifying bar i on the FULL series `[0,n]` vs the truncated `[0,i+1]` gives **0 run-mismatches and 0 vol-band-mismatches over 78 bars** → the label of bar i is a function of bars ≤ i only. The retrospective bear/bull/correction map (monthly closes over all history) is explicitly **forbidden** in the docstring. ✅

**Leakage — PASS.** All windows trailing; the direction shares use `[i-W+1,i]`; `detect_swings`/`detect_breaks` recomputed on `[0,n)` but the run-propagation filters `idx<=i`, and truncation-stability (above) proves no future bar leaks in. News: `value=FALSE + status=UNAVAILABLE` until a causal calendar is wired; the schedule is causal, the *result* is not used (correctly). Residual: the news *result*'s causality is the caller's responsibility (`news_fn`), unenforced here.

**Reproducibility — PASS.** Deterministic (no RNG); the same bars→same labels; verified stable under truncation, so an incremental caller gets the same key as a batch caller.

**Overfitting — PASS.** Thresholds are **outcome-agnostic partitions** (P10 spec default; P33/P67 tertiles; RUN cuts {2,3}/{≥4}) — data-relative percentiles are *adaptive by design*, not fitted to any performance metric. Occupancy percentages are **reported, not tuned**.

**Hidden parameters — PASS.** Every constant is named with provenance: `W=30` (DERIVAT), `P33/P67`/`RUN_WEAK/STRONG` (ALEGERE, equal-occupancy), `K_SWING=2` (lab default), `N_MIN=30` (fail-closed). No unnamed magic.

**Ambiguity — see L-U1. Circularity — see L-R1.**

## OWN TARGETS (things I transmitted that were corrected)

**W=30 re-derivation — CORRECT; the "undetectable" claim is APPROXIMATE, not exact.**
- **Derivation verified:** W=30 ≈ one week of H4 (empirical 29.84; 5 days × 6 H4-bars). The `460` I transmitted = a **quarter** (460 H4-bars ≈ 77 days ≈ 13 weeks) — a week-on-M15 window transplanted to H4. The re-derivation and the "unit transplant" diagnosis are both right. ✅
- **The claim "the error was undetectable downstream because a percentile gives the same rate at any window" — REFINED.** True under (local) stationarity: a P10 threshold flags ~10% of bars at *any* window (verified: W=30 → **9.8%** occupancy). **But NOT exact under non-stationarity:** a quarter-long window mixes volatility regimes, so the current bar's rank shifts and the occupancy rate moves materially (my synthetic: 9.8% at W=30 vs **2.1%** when the window spans multiple regimes), and **per-bar labels differ ~4%** between nearby windows (96% agreement W=30 vs W=120). **So the error genuinely hid (rate roughly stable for moderate windows) but was not truly invisible** — a quarter-vs-week window relabels individual bars and can shift the rate under regime change. The Statistician's instinct was right; the "same rate at any window" phrasing over-claims. (L-R2.)

**Direction from BOS run-sign — DEFENSIBLE source, but introduces circularity (L-R1).** The spec deriving direction from the sign of the `detect_breaks` run (not EMA/ADX) is internally consistent — it avoids a **third** definition of structure (the reason ADX was rejected), and I followed the spec over my EMA message. **But `detect_breaks` is the SAME primitive that structure-based CANDIDATES consume** (S3 breakout-retest, S11 structure-break-reversal, MK-01 users). A structure candidate filtered by a structure regime **shares its source** → the regime provides **little independent information** for that candidate class (the regime is HIGH-structure exactly when the candidate fires) — a **redundant/near-circular filter**. The volatility and news axes remain independent, so the filter is informative for **non-structural** candidates. Not a hard bug; a disclosed dependency: the level-1 structure axis is **not an independent context** for structure-based level-6 candidates. (L-R1.)

**Compression/expansion collapse into the volatility axis — MEASURED-justified, near-lossless (PASS).** Expansion is 99.5% within HIGH, so it is surfaced as `HIGH_DIRECTIONAL`; compression = the bottom decile (`≤P10`). The nine CEO states are **recoverable** as axis combinations (vol × structure × direction × news), not discarded. **Loss:** the `is_expansion` flag only subdivides the HIGH band (`_lbl` idx==3), so the **0.5% of expansion bars that fall outside HIGH** get their plain vol-band label and drop the expansion tag (L-U3). Small, measured, disclosed — nothing material lost.

**"No regime → no trade" as a limiting case — the SIGNAL is emitted; the OUTCOME is not yet wired (L-U2).** The classifier correctly has **no gate** and emits the no-regime signals — verified: n<W → `UNAVAILABLE`; `n<n_min`/`|run|==1` → direction `NEUTRAL`, confidence→0; boundary bars → low confidence + soft weight to the neighbor. **But the level-6 decision engine (RT-CODE-A-0008) consumes hard OutcomeCell COUNTS, not this soft RegimeState/confidence.** The promised propagation — low confidence → wider posterior → `EV_LCB` falls → no-trade — requires a **level-1→level-6 mapping that is not in either module.** So the CEO condition is **preserved at the classifier** (it emits the right signals) but its **realization is deferred to unbuilt wiring** (step 4). **Direct answer: the signal comes out; the "no trade" result is not yet demonstrable — verify it at integration.**

## STATISTICIAN'S EXPLICIT TARGETS

**Equal-occupancy anchor — a LEGITIMATE convenience, not a market boundary.** Because runs are **geometric / memoryless** (spec-acknowledged), there is **no natural strong/weak threshold** — so *any* cut is arbitrary, and equal-occupancy (balanced cells, maximizes the minimum cell → best per-cell power, no tiny cells) is a sound **default choice**. It is correctly **declared a choice**, not a discovered boundary. Legitimate **as a partition convenience**; it must **not** be read as a market-meaningful regime edge. PASS-with-disclosure.

**|run|==1 = "range" or "post-flip"? — POST-FLIP; "RANGE" is a MISNOMER (L-U1).** `|run|==1` means exactly one break of the current sign since the last opposite CHoCH — i.e. the structure **just reversed** (verified: idx 65, run=−1 → labeled `RANGE`). The code's own comment calls it "direcție proaspăt răsturnată" (freshly-reversed direction). **That is post-flip, not ranging.** Mapping it to direction `NEUTRAL` (unstable, don't commit) is defensible, but the **band name "RANGE" mislabels a fresh-reversal as a consolidation** — two different market conditions. Downstream logic keyed on "RANGE = ranging market" would systematically misread post-flip bars. Naming/semantic finding.

**Can soft assignment hide a systematically wrong label? — YES, at the band level (L-R2).** Soft assignment is **boundary-local**: it splits weight to a neighbor only near a threshold. It gives **no protection against a globally mis-defined band** (wrong window, wrong percentile) — a bar **deep** in a systematically-wrong band gets **confidence = 1.0 on the wrong label**. So a mis-specification like the W=30-vs-460 error would **not** be revealed by the soft-assignment machinery (which is exactly why the occupancy-rate stability let it hide). Soft assignment propagates *sampling* ambiguity, not *specification* error — and can present a systematic error as high-confidence.

## SEVERITY
- 🟠 **L-R1 · Structural circularity/redundancy** — direction/structure from `detect_breaks`, shared with structure-based candidates → the level-1 structure axis is not an independent context for that candidate class. Defensible design (one structure definition) with a disclosed cost.
- 🟠 **L-R2 · Soft assignment cannot guard a mis-defined band + the "undetectable window error" is approximate** — deep-band bars are confident on a possibly-wrong label; percentile occupancy is window-invariant only under stationarity, and per-bar labels differ (~4%) between windows.
- 🟡 **L-U1 · `|run|==1` labeled "RANGE" is a misnomer** (post-flip ≠ ranging); direction NEUTRAL is fine, the band name misleads.
- 🟡 **L-U2 · "No regime → no trade" is emitted but not yet wired** — level 6 consumes hard counts, not the soft RegimeState; the CEO limiting-case realization is deferred to step-4 integration.
- 🟡 **L-U3 · 0.5% of expansion bars outside HIGH lose their expansion tag** (measured, minor).

## WHAT SURVIVES (verified)
Lookahead-free (0 mismatches under truncation); reproducible/deterministic; no hidden parameters (all named + provenance); no outcome-overfitting (adaptive percentile partitions, reported-not-tuned); fail-closed (UNAVAILABLE warmup, NEUTRAL under n_min / RANGE, news value=FALSE+UNAVAILABLE ≠ clean); W=30 derivation correct; compression/expansion collapse measured-justified and near-lossless; equal-occupancy a declared, legitimate convenience.

## HANDOFF → CEO (step 4 of 4), then Statistician
1. **L-U2 (highest for wiring):** build and verify the level-1→level-6 propagation so low confidence / NEUTRAL / UNAVAILABLE actually widens `EV_LCB` and yields no-trade — the CEO condition is only a promise until then.
2. **L-R1:** disclose that the structure axis is redundant for structure-based candidates; the independent filtering power is in the volatility/news axes.
3. **L-U1:** consider that "RANGE" names a post-flip state; ensure no downstream reads it as consolidation.
4. **L-R2:** the percentile-occupancy invariance holds only under local stationarity; the window choice DOES change per-bar labels — treat W=30 as a real modeling decision, not a cosmetic one.

Red Team designed no remedy, ran no data on the market, modified nothing outside `red_team/`.
