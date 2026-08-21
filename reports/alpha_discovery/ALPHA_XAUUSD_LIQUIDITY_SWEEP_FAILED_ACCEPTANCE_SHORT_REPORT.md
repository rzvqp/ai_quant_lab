# ALPHA_XAUUSD_LIQUIDITY_SWEEP_FAILED_ACCEPTANCE_SHORT_REPORT

**Mandate:** `ALPHA-XAUUSD-LIQUIDITY-SWEEP-SHORT-001` · **Date:** 2026-08-22 · **Stat evidence:** commit `b8d0447`.
**Terminal status:** `XAUUSD_LIQUIDITY_SWEEP_SHORT_DISCOVERY_COMPLETE` · **`NO_ROBUST_LIQUIDITY_SWEEP_SHORT_ALPHA_FOUND`**.
**Firewall (re-verified):** gated M5 loader (file sha `cbb6eebe…`) → causal H1/H4; no `read_csv` on `data/market/`; `N4=0`; `2025+=0`. 18 IDs (≤40). DEV-only (CALIB closed). No promotion; broker disabled; existing candidates frozen.

---

## 0. Headline — answers to §31
1. **Is liquidity-taking a useful precursor to SHORT Alpha?** — **Diagnostically yes, tradeably no.** Sweeps that precede bearish moves ARE distinguishable (via displacement / structure-break), but no executable short survives realistic cost + structural stops.
2. **Sweep alone useful? NO** (L0 STRESS −0.266; discriminates bearish-vs-bullish by 0pp).
3. **Failure-to-accept add value? NO** — closing back below the swept level discriminates only **+3pp (H4) / −8pp (H1)**; `L1` STRESS −0.253. **The "failed acceptance" in the mandate's primary hypothesis is NOT the operative variable.**
4. **Bearish displacement after sweep add value?** — **the 2nd-strongest discriminator (+17/+27pp), but not tradeable** (`L2` negative across RR).
5. **Follow-through add value? NO** (`L3` H4 −0.259).
6. **Failed reclaim add value? NO** (`S7` −0.21).
7. **Sweep + structure break superior?** — **the strongest discriminator (+19/+25pp) and least-bad trade** (`L4` −0.050) — but still not positive/robust.
8. **Which level matters most? H4 swing high > H1 swing high** — H4 sweeps are rarer but more meaningful (median forward bear excursion 131p vs 64p; 28% vs 7% reach ≥200p).
9. **Identify 100–300p bearish moves? Partially** — 61% of H4 sweeps reach ≥100p bear excursion, but only 44% are net-bearish.
10. **Avoid bullish continuation? This is the core failure** — 56% (H4) / 72% (H1) of sweeps continue bullish; the discriminators lift the bearish rate but the executable stop (above the sweep high) gets hit first.
11. **M15/M5 improve entry? N/A** (no survivor to time).
12. **Genuinely incremental over generic bearish exposure? No robust one** — positive incremental over a *losing* baseline (PROJECT TREND_DOWN H4 −0.176) is not Alpha.
13. **Robust rare-event SHORT specialist? NO.** 14. **Deserves Statistician review? None.**

## 1. Evidence integrity
Gated M5 → causal H1/H4; no `read_csv` on `data/market/`; N4=0; 2025+=0; CALIB not opened.

## 2. Liquidity-level construction (§2) — causal, no hindsight
Levels = **prior confirmed swing highs** via a 5-bar fractal (`h[k] = max(h[k−2 … k+2])`), **confirmed with a 2-bar lag** (usable only at bars ≥ k+2). A **sweep event** = the first bar `i` whose high breaches a prior confirmed swing-high level that had been *unbroken* since it formed (`max(high[k+1:i]) ≤ lvl < high[i]`, `high[i−1] ≤ lvl`). All levels exist before the sweep; no future pivots.

## 3. Raw sweep catalog (§17)
**H4: 250 sweep events; H1: 887.** (H1 sweeps are ~3.5× more frequent but smaller — §24.) Raw opportunity population built before any trade-taking.

## 4. Large-down-move + sweep-outcome diagnostics (§5, §23) — outcome for DIAGNOSIS only
Forward 12-bar excursions from the causal entry (outcome used only to *characterize* sweeps, never as a signal):
| | H4 (n=250) | H1 (n=887) |
|---|---|---|
| bearish-departure (≥100p down & down>up) | **44%** | **28%** |
| bullish-continuation | 56% | 72% |
| median forward bear / bull excursion | 131p / 148p | 64p / 66p |
| % sweeps reaching ≥100 / 150 / 200 / 300p bear | 61 / 44 / 28 / **12** | 31 / 14 / 7 / 2 |
Meaningful bearish moves DO follow many sweeps (H4 targets exist), but the **base rate is bull-favored** (bull excursion ≥ bear on the median).

## 5. Sweep-only control + feature discrimination (§5, §6, §7, §8) — the scientific core
Which pre-entry causal features separate bearish-departure sweeps from bullish-continuation sweeps:
| feature | H4 bearish vs bullish | H1 bearish vs bullish | verdict |
|---|---|---|---|
| **structure break** | 23% vs 4% → **+19pp** | 35% vs 10% → **+25pp** | **strongest discriminator** |
| **bearish displacement** | 27% vs 9% → **+17pp** | 44% vs 16% → **+27pp** | strong discriminator |
| close back below level (failed acceptance) | 50% vs 47% → **+3pp** | 44% vs 53% → **−8pp** | **NOT a discriminator** |
| sweep magnitude (pips above level) | 35 vs 35 → **0** | 15 vs 12 → ~0 | not a discriminator (§8) |
| bars spent above level | 1.0 vs 1.0 → **0** | 1.0 vs 0.0 | not a discriminator (§7) |
**By Bayes, conditioning on structure-break raises P(bearish) from 44% to ~82%** (H4) — genuine predictive information. **But the operative variable is displacement / structure-break, NOT "failure to accept," NOT sweep size, NOT time-above.** This directly refutes the mandate's primary emphasis ("failure to accept above the level") — closing back below the swept level carries almost no information.

## 6. Common-parent L0..L4 decomposition (§4) — raw per-signal, STRESS
Same parent sweeps; each mechanism defines the earliest causal short + stop above the sweep extreme, RR (H4 1.5 / H1 2.5):
| mechanism | H4 avgR | H4 med R | H4 best-5%-rem | H1 avgR | verdict |
|---|---|---|---|---|---|
| L0 sweep-only | −0.266 | −1.035 | −0.355 | −0.196 | RAW_FAIL |
| L1 sweep + failed-acceptance | −0.253 | −1.025 | −0.344 | −0.171 | RAW_FAIL |
| **L2 sweep + displacement** | **−0.066** | −1.010 | −0.144 | −0.121 | RAW_FAIL (least-bad H1... ) |
| L3 sweep + disp + follow-through | −0.259 | −1.008 | −0.332 | +0.024* | RAW_FAIL (tail: top-10% 976%) |
| **L4 sweep + structure break** | **−0.050** | −1.008 | −0.103 | −0.015 | RAW_FAIL (least-bad) |
| S7 sweep + failed reclaim | −0.210 | −1.021 | −0.296 | −0.139 | RAW_FAIL |
**0 of 12 survive.** The decomposition mirrors the diagnostic: structure-break (L4) and displacement (L2) are the least-bad (they add relative value), failed-acceptance (L1) barely improves on sweep-only (L0), follow-through/failed-reclaim do not help. **Median R ≈ −1.0 for every mechanism** — the executable short is stopped out.

## 7. Displacement / follow-through / failed-reclaim / structure-break results (§ per-mechanism)
Covered in §5–§6: **displacement and structure-break are the predictive components; follow-through, failed-reclaim, and failed-acceptance are not.** All are tradeably negative.

## 8. Bounded target/stop rescue (§14, §15) — no geometry fixes it
The two best-discriminating mechanisms (L2, L4 on H4) tested across RR {1.0, 2.0, 3.0} and a structural target (prior swing low), transparently (no best-pick):
| variant | avgR | med R | best-5%-rem | top-10% share | verdict |
|---|---|---|---|---|---|
| L2 RR 1/2/3 | −0.061 / −0.069 / −0.045 | ≈ −1.01 | neg | 999% | FAIL |
| L2 structural target | −0.183 | +0.085 | −0.248 | 999% | FAIL |
| L4 RR 1/2/3 | −0.082 / −0.033 / −0.023 | ≈ −1.0 | neg | 999% | FAIL |
**No RR or target geometry produces a positive, tail-safe, incremental short.** The failure is not stop-tightness (median SL for L2/L4 is 100–190p, wide): the "eventual bearish" moves the diagnostic counts frequently arrive *after* an initial rally that hits the stop, and the 56–72% bullish-continuation sweeps deliver large losses.

## 9. Why predictive-but-not-tradeable
The liquidity-sweep + displacement/structure-break genuinely *identifies* which sweeps precede bearish moves (P(bearish) → ~82% with structure-break). But on the **gated 2021–2024 (long-biased) population** this does not convert into an executable edge: (a) the bearish moves are **path-noisy** (rally first, then fall — hitting the short's structural stop above the sweep extreme); (b) the majority bullish-continuation sweeps produce **large, dominating losses**; (c) even wide stops / larger targets do not overcome the upward drift. **The bearish sweep events occur mostly in TREND_UP/OTHER regimes** (H4: 31 TREND_UP / 6 TREND_DOWN / 72 OTHER of the bearish sweeps) — confirming §10/§11 that this is a *local* reversal inside a bull market, and such reversals are shallow/quickly-recovered here.

## 10. H1 vs H4 liquidity source (§24)
**H4 is the cleaner source.** H4 sweeps: 44% bearish, median bear 131p, 28% reach ≥200p. H1 sweeps: 28% bearish, median bear 64p, 7% reach ≥200p. An H4-high sweep is rarer and more meaningful — but still not tradeable.

## 11. Entry timing / SL-TP geometry (§12–§15)
No serious candidate survived to warrant M15/M5 timing (§25 N/A). Geometry was adequate throughout (L2/L4 median TP 285–341p, ≥300p targets available) — the failure is edge, not target room or stop location.

## 12. Incremental baselines (§19)
Every mechanism was measured vs **PROJECT TREND_DOWN** (H4 −0.176 / H1 +0.016) and the **sweep-only (L0)** control. Some H4 mechanisms show positive incremental vs the *losing* TREND_DOWN baseline (L2 +0.11, L4 +0.13–0.15) — but all are **absolutely negative and tail-fragile**. Incremental over a losing baseline while still losing is correctly rejected.

## 13. Tail + path robustness (§20, §21)
best-5%-removed is negative for all 18 IDs; top-10% net-profit share is 999% (net ≤0) for all executable mechanisms. **Path robustness not reached** — no raw survivor to serialize (the raw-first discipline correctly stops before any serialization could manufacture a spurious edge).

## 14. Temporal (§22)
Consistent with the generic short scan: the (already-negative) sweep shorts do not work in any single year, including the 2022 selloff (the bearish sweeps that do occur are shallow/recovered). No temporal breadth; no episode of robust bearish sweep profitability.

## 15. Graveyard (§32)
All 18 IDs — L0/L1/L2/L3/L4/S7 on H4 and H1, plus the L2/L4 RR/structural-target rescue variants — **NO_EDGE** (median −1.0, negative/tail-fragile). The equal-high / PDH / range-high / bullish-exhaustion level-source variants (§2 C–L) were not separately enumerated: the diagnostic established that the operative discriminator is **displacement/structure-break, not the level source or sweep magnitude**, so further level-source variants are low-information (§29 early-stop, evidence converged). Recorded in `liq_records.json`. New `SW-`/`SH-` IDs; existing candidates untouched.

## 16. Candidate ranking + CEO recommendation (§30)
1. **No liquidity-sweep SHORT candidate is recommended — `NO_ROBUST_LIQUIDITY_SWEEP_SHORT_ALPHA_FOUND`.**
2. **Genuine scientific findings for the CEO (valuable even in a negative result):**
   - **Liquidity-sweep + displacement/structure-break has real DIAGNOSTIC predictive value** (structure-break → P(bearish) ~82%), and it correctly fires in TREND_UP (the angle the generic scan missed) — but it does **not** convert into a tradeable short on this population.
   - **The mandate's primary variable ("failure to accept above the level") is NOT the operative signal** — closing back below the swept level discriminates by only +3pp. The operative components are **displacement and structure break**.
   - **H4 highs > H1 highs** as a liquidity source. **Sweep magnitude and time-above do not matter.**
3. **Why it fails and what would be needed:** the 2021–2024 population is long-biased; local bearish reversals after sweeps are shallow and quickly recovered, so the executable short (structural stop above the sweep) is stopped by the bull drift. A tradeable liquidity-sweep short would likely require (a) a genuine secular-downtrend population, or (b) a much more selective structure-break filter *combined with* a target/stop regime robust to the initial rally — neither achievable as a robust DEV survivor here without post-hoc fitting (explicitly forbidden).
4. **This is the closest any SHORT angle has come** (displacement/structure-break genuinely discriminate, unlike generic momentum/breakdown), but it still fails the tradeable bar. **No promotion; broker disabled; DEV-only; CALIB not opened.** Existing candidates unaltered; portfolio SHORT exposure remains only the frozen `H4-bo-raw-S` (earlier population).

**Terminal status:** `XAUUSD_LIQUIDITY_SWEEP_SHORT_DISCOVERY_COMPLETE` · `NO_ROBUST_LIQUIDITY_SWEEP_SHORT_ALPHA_FOUND`. **STOP.**
