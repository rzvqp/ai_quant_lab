# ALPHA_XAUUSD_H1_RANGE_M5_DISCOVERY_REPORT

**Mandate:** `ALPHA-XAUUSD-H1-RANGE-M5-DISCOVERY-001` · **Date:** 2026-08-21 · **Stat evidence:** commit `b8d0447`.
**Terminal status:** `XAUUSD_H1_RANGE_M5_DISCOVERY_COMPLETE` · **`NO_ROBUST_RANGE_M5_ALPHA_FOUND`**.
**Firewall (re-verified):** gated M5 loader only, no `read_csv` on `data/market/`, `N4_M5_TRIGGER_USAGE_COUNT = 0`, `ALPHA_ACCESS_2025_PLUS = 0`, no shadow_driver. 18 IDs (≤50). No promotion; broker disabled; V4.4 untouched.

---

## 0. Headline
- **No robust RANGE M5 Alpha found.** Across 4 mechanisms × 2 sides × 2 targets (+ M5-confirmation-type variants) with the corrected architecture (H1 owns range/SL/TP; M5 = entry only), **every candidate fails at least one hard gate** — tail-fragility (best-5%-removed negative), CALIBRATION (uniformly negative out-of-DEV), or temporal instability.
- **Range width is NOT the problem** — gold H1 ranges are wide (median **189 pips**; 97% ≥100 pips), amply supporting ≥70–80 pip economics.
- **The boundary-entry intuition is correct in-sample but does not generalize.** Profitability concentrates sharply when entry is within ~10–20% of the boundary (avgR **+0.43…+0.56** vs negative beyond) — the CEO's §6 hypothesis holds on DEV — **but the same subsets fail on CALIBRATION.**
- **M5 entry timing adds ~0 value for range mean-reversion** (fair matched control: Δ avgR ≈ 0), confirming the prior finding that M5 confirmation helps *continuation*, not *reversion*. The earlier apparent M5 "value" was a re-entry artifact, now eliminated.

## 1. RANGE definitions (§1, §10)
Causal H1 range over a 24-H1-bar (1-day) window: `range_high = max(high[i−24:i])`, `range_low = min(low[i−24:i])` (shifted, causal); `width`, `mid`. **In-range** ⇔ |directional efficiency| < 0.35 **and** width ∈ [40, 600] pips **and** ≥2 touches near each boundary (alternation/quality). DEV range bars = **4,352** (43% of DEV H1); CALIB = 1,204. Range-quality features (age, width/ATR, boundary touches) are strategy-local; **RANGE V4.4 not modified.**

## 2–7. Mechanism results (coarse H1 entry, DEV, STRESS) — all FAIL or TAIL_FRAGILE
| mechanism (§) | side | tp | n | WR | avg R | best-5%-rem | verdict |
|---|---|---|---|---|---|---|---|
| boundary rejection (6) | LONG | mid | 115 | 0.47 | −0.017 | −0.19 | FAIL |
| boundary rejection | SHORT | opp | 117 | 0.25 | −0.128 | −0.40 | FAIL |
| **exhaustion** (repeated-test) | SHORT | mid | 99 | **0.44** | **+0.116** | **−0.063** | TAIL_FRAGILE |
| exhaustion | LONG | mid | 101 | 0.47 | +0.063 | −0.18 | TAIL_FRAGILE |
| exhaustion | LONG | opp | 105 | 0.33 | +0.113 | −0.16 | TAIL_FRAGILE |
| failed-breakout (5) | LONG | opp | 126 | 0.25 | +0.157 | −0.26 | TAIL_FRAGILE |
| sweep/reclaim (4) | SHORT | opp | 71 | 0.23 | **+0.523** | −0.22 | TAIL_FRAGILE (pure tail) |
| sweep/reclaim | LONG | mid | 70 | 0.33 | +0.045 | −0.18 | TAIL_FRAGILE |
| range rotation (7) | — | — | — | — | — | — | (covered by reject/opp — boundary→opposite) |
**Every positive-average mechanism is tail-fragile** — removing the best 5% of trades turns it negative. The positive averages are carried by a few ranges that broke into trends (reversion entry catching a large one-way move), **not** a broad mean-reversion edge. `sweep-S-opp` (+0.52) is the extreme case: entirely tail-driven.

## 8. M5 entry families + 9. coarse vs M5 (mandatory control §5)
Fair matched control (M5 arm B vs coarse arm restricted to the **same** signals A|B), so only entry timing differs — after eliminating the re-entry confound (the earlier "reclaim/re-poke" confirmation entered only after the coarse trade had already stopped, producing a spurious +1.3R "timing value").
| mechanism | M5 confirmation | **pure timing Δ avgR (matched)** | Δ WR |
|---|---|---|---|
| rejection | momentum-into-range | +0.00 … +0.06 | ≈0 |
| rejection | micro-BOS | +0.09 (LONG) / neg (SHORT) | ≈0 |
| exhaustion | momentum-into-range | −0.05 … +0.03 | ≈0 |
| failed-breakout | momentum-into-range | −0.02 … −0.06 | ≈0 |
| sweep | reclaim (setup-intrinsic) | +0.20…+0.42* | — |
*The large sweep "timing" value is the **re-breach confound** (reclaim requires price to re-cross the boundary), **not** genuine timing — discounted. **Conclusion: M5 entry timing does not add robust value to range mean-reversion.** Neither the coarse nor the M5 arm survives.

## 10. Range-width economics (§9) — width is NOT the constraint
| metric | value |
|---|---|
| median range width | **189 pips** ($18.9) |
| P25 / P75 | 146 / 247 pips |
| % ≥80 / ≥100 / ≥150 / ≥200 pips | **0.99 / 0.97 / 0.72 / 0.44** |
Gold H1 ranges are wide enough to support the requested ≥70–80 pip (and 100+ pip) economics for the overwhelming majority of setups. The failure is **not** a width/geometry problem — it is a **lack of edge**.

## 11. Entry-distance-from-boundary analysis (§6, §17) — real in-sample, fails out-of-sample
Profitability concentrates sharply at the boundary (diagnostic, not optimized):
| candidate | entry ≤10% of boundary | beyond 10% | ≤20% | beyond 20% |
|---|---|---|---|---|
| exhaust-S-mid | **+0.429** (n=29) | −0.014 (n=70) | +0.302 | −0.211 |
| exhaust-L-mid | **+0.555** (n=22) | −0.074 (n=79) | +0.023 | +0.129 |
**The CEO's structural hypothesis is confirmed on DEV** — entering within ~10–20% of the H1 range boundary is where the (in-sample) edge lives. **But it does not survive CALIBRATION** (see §17), so it is not tradeable. Boundary metrics (representative): entry-to-boundary median ~1–2% of width (right at the boundary); stop 0.25·ATR outside; target = mid (RR ~1.4–1.6) or opposite boundary (RR ~3.1–3.3); ≥3 boundary tests for the exhaustion family.

## 12. WR / RR profiles + 13. SL/TP distributions
Representative (coarse, exhaustion): median SL ~35–55 pips, median TP 52–120 pips, %TP≥70 ≈ 0.55–0.95 (mid/opp), WR 0.33–0.47. **No candidate lands in Profile A (70–80% WR) or Profile B (45–55% @ 1:3–4) robustly** — the WRs (33–47%) are unremarkable and the expectancy is tail-fragile. Neither profile achieved.

## 14–16. BASE/STRESS + tail + temporal robustness
- **Tail (§15):** best-5%-removed is **negative for every candidate** — decisive tail-fragility.
- **Temporal (§16):** no mechanism is positive across all three DEV years. exhaust-S-mid: 2021 +0.22 / **2022 −0.45** / 2023 +0.25. exhaust-L-opp: positive only 2022 (+0.74). failbreak-L-opp: **2021 −0.76**. Instability is structural.

## 17. Calibration (§17) — the decisive gate
Frozen DEV mechanism evaluated on CALIB (2024-01→06-20), no retuning:
| candidate | CALIB n | CALIB avg R | CALIB best-5%-rem | verdict |
|---|---|---|---|---|
| exhaust-S-mid | 34 | +0.035 | −0.055 | tail-fragile, marginal |
| exhaust-L-mid | 22 | **−0.376** | −0.502 | FAIL |
| exhaust-L-opp | 22 | **−0.823** | −0.958 | FAIL |
| failbreak-L-opp | 33 | **−0.570** | −0.789 | FAIL |
| exhaust-L-opp (width≥150) | 17 | **−0.734** | −0.905 | FAIL (DEV +0.389 → overfit) |
**CALIBRATION uniformly fails.** The single DEV-robust-looking cell (exhaust-L-opp, width≥150: DEV +0.389, best-5%-removed +0.078) collapses to CALIB −0.734 — a textbook in-sample overfit. No frozen RANGE candidate behaves plausibly out-of-DEV.

## 18. V4.4 incremental value (§11)
**Not applicable / moot.** No ungated RANGE mechanism produced a robust base edge, and a context gate **filters** signals — it cannot **create** Alpha where none exists (as the mandate itself states: "Market Intelligence describes context; it does not automatically create Alpha"). Gating a non-edge with V4.4 RANGE context would only reduce sample. V4.4 was not modified or re-derived; no V4.4 evidence consumed. If a future RANGE base edge emerges, the V4.4-gate comparison should be run then.

## 19. LONG / SHORT asymmetry (§12)
Both sides fail. LONG-at-low (reject/exhaust/failbreak) and SHORT-at-high (reject/exhaust/sweep) are each tail-fragile on DEV and negative on CALIB. There is **no robust directional RANGE edge on either side** in the gated 2021–2024 population — not a LONG-only nor a SHORT-only survivor. (The prior apparent SHORT survivor was the re-entry artifact, now falsified.)

## 20. Independent candidate families
None. Zero robust RANGE candidates to compare against `S5` / `HR-TU-pb-L` / `H4-bo-raw-S` / `S20` (those left unaltered, per §19).

## 21. Graveyard (do not rediscover)
All 18 IDs: boundary-rejection (L/S × mid/opp), sweep/reclaim (L/S × mid/opp), failed-breakout (L/S × mid/opp), exhaustion (L/S × mid/opp), and reject-mbos (L/S). Plus the width≥100/150 and entry-location-filtered niches (DEV-positive, CALIB-negative). Recorded with metrics in `range_records.json`. **Do not resurrect the "SHORT range survivor" — it was a re-poke re-entry confound.**

## 22. Recommendation to CEO
1. **No RANGE M5 candidate is recommended.** On the gated 2021–2024 XAUUSD population, H1 range mean-reversion (LONG at low / SHORT at high), entered coarsely or via M5 confirmation, with H1 structural SL/TP, **does not produce robust positive expectancy after realistic (STRESS 0.24) cost** — every mechanism is tail-fragile and fails CALIBRATION.
2. **Two specific, honest findings for the CEO:**
   - **(a)** The boundary-entry hypothesis is **correct in-sample** — profitability concentrates at entry within ~10–20% of the H1 range boundary (avgR +0.43…+0.56) — but this edge **does not survive out-of-DEV**, so it is a real structural regularity that is nonetheless **not tradeable** as tested.
   - **(b)** **M5 entry timing does not rescue range mean-reversion** (fair matched control ≈ 0); M5's demonstrated value remains specific to **trend-continuation** (`HR-TU-pb-L`). The prior "M5 helps RANGE shorts" reading was a re-entry artifact and is retracted.
3. **Why it likely fails:** gold ranges are wide (median 189 pips) but frequently **resolve into trends**; the boundary "reversion" entry that pays in-sample is really catching occasional large one-way moves (tail), and when the boundary breaks the fixed H1 stop takes a full loss — net tail-fragile, non-generalizing. A robust RANGE edge would need a genuinely predictive *range-continuation-vs-break* discriminator, which this search did not find.
4. **No promotion; broker disabled; highest status = research (negative result).** Existing candidates (`S5`, `HR-TU-pb-L`, `H4-bo-raw-S`, `S20`) unaltered.

**Terminal status:** `XAUUSD_H1_RANGE_M5_DISCOVERY_COMPLETE` · `NO_ROBUST_RANGE_M5_ALPHA_FOUND`. **STOP.**
