# ALPHA ECONOMIC-PROFILE PROGRAM — INTERIM H4/H1 EDGE CAMPAIGN (option C)

**Directive:** CEO `ALPHA ECONOMIC PROFILE DIRECTIVE` (2026-08-21) + decision **"A + C in parallel"**.
**This report = option C** (interim H4/H1 edge search with next-bar-open entry as an M5 proxy). Option A (M5 acquisition) requested separately in [M5_DEV_DATA_ACQUISITION_REQUEST.md](M5_DEV_DATA_ACQUISITION_REQUEST.md).
**Status:** `ECONOMIC_PROFILE_INTERIM_H4H1_COMPLETE` — **ONE robust interim candidate** (`H4-bo-raw-S`), **no clean Profile-A/B fit under conservative no-M5 execution** (M5 layer required for the WR targets), timeframe ranking **H4 > H1 ≫ M15** confirmed by a second method.
**VALIDATION_ACCESS = 0. FINAL_HOLDOUT_ACCESS = 0.** Gated DEV, per-block; RATIFIED cost; broker DISABLED; nothing promoted.

---

## 0. Headline
1. **One robust interim candidate: `H4-bo-raw-S` (H4 20-bar-low breakdown, D1-downtrend-aligned, structural stop, short).** At RR 1:1.5 it is the **most robust candidate in the entire program** — it is the *first* to pass **best-10%-removed positive (+0.16)** (broad-based, not tail-driven), with **both DEV blocks strongly positive** (b0 +0.209 / **b1 +0.498**), **out-of-DEV CALIBRATION positive** (+0.152), execution-robust, no year concentration. STRESS +0.288, median realized R **+1.434**.
2. **Neither Profile A nor Profile B is cleanly reached** by the vanilla mechanism under **conservative (stop-wins-ties) no-M5 execution**: best win rate anywhere ≈ 53%. Profile A (70–80% WR) is unreachable without the M5 entry layer; the robust edges sit at RR 1:1.5–1:4 with WR 23–53%. **This is the quantified case for M5 (option A).**
3. **Timeframe ranking (2nd method, RR-target realizations): H4 > H1 ≫ M15.** H4-short-breakout is the robust source; H1 corroborates (`H1-hllh-S`) but **fails out-of-DEV CALIBRATION**; M15 is uniformly weak/negative — M15 is a *trigger*, not an edge source.
4. **Economic-target regime satisfied:** the flagship's intended target is ≥70 pips for **87%** of setups (≥80 pips for 81%); median TP 113 pips, median MFE 278 pips. **Not micro-scalping.**

## 1. Method
Edge TFs **M15 / H1 / H4**, gated DEV (b0 2011–13 + b1 2016–18), per-block (no cross-gap). Continuation families (pullback, breakout ±acceptance, displacement+accept, compression, momentum, path-efficiency, HL/LH structure), both directions, HTF-trend-aligned (M15/H1→H4 EMA20>EMA50; H4→D1). **Entry = next-edge-bar open** (M5 proxy → M5 execution quality flagged `PENDING_M5`). **Structural SL** = broken level ± 0.3·ATR (floored 0.8·ATR). **Exit = RR target k ∈ {1.5, 2 (Profile-A lens), 3, 4 (Profile-B lens)}** via `mstrat.simulate` — which resolves intrabar SL-vs-TP **conservatively (stop wins ties)**, so all WR/expectancy figures are a **LOWER bound** a true M5 layer would improve. Cost RATIFIED BASE 0.05 / STRESS 0.24. 184 realized strategies; full records in `econ_campaign.json`.

## 2. FLAGSHIP CANDIDATE — full mandated report: `H4-bo-raw-S` (RR 1:1.5, ROBUST)
| field | value |
|---|---|
| **signal timeframe** | **H4** |
| entry timeframe | **M5** (interim: next-H4-bar open proxy — `PENDING_M5`) |
| direction | **SHORT** (D1-downtrend-aligned) |
| mechanism | close below prior 20-H4-bar low (raw breakdown), structural stop at broken low +0.3·ATR |
| win rate | **0.528** (target-hit, conservative) |
| avg realized R | **+0.288** (STRESS) |
| intended Risk:Reward | **1:1.5** |
| median realized R | **+1.434** (median trade is a winner) |
| median SL | **$7.54 = 75.4 project pips** |
| median TP | **$11.32 = 113.2 project pips** |
| target distance P25/P50/P75 | **86 / 113 / 178 pips** |
| % target ≥70 / ≥80 / ≥100 pips | **0.874 / 0.813 / 0.604** |
| MFE distribution P50/P75 | 278 / 650 pips |
| MAE distribution P50/P75 | 220 / 485 pips (raw 48-bar window diagnostic) |
| BASE expectancy | **+0.313** |
| STRESS expectancy | **+0.288** |
| best-1%-removed expectancy | **+0.278** |
| **best-5% / best-10%-removed** | **+0.227 / +0.160** (both positive — broad-based) |
| temporal stability (b0 / b1) | **+0.209 / +0.498** (both DEV blocks positive) |
| out-of-DEV CALIBRATION (block2) | **+0.152** (n=20) |
| execution degradation (+1-bar / 1.5×floor) | **+0.204 / +0.151** |
| year-concentration (max single-year share) | 0.354 (no dominance) |
| trade frequency | 18.3 per 1,000 H4 bars |
| **deep-robustness verdict** | **ROBUST** (passes tail + concentration + both-blocks + execution + out-of-DEV) |

## 3. Same mechanism, higher-RR variants (Profile-B lens) — STRONG_PARTIAL
| id | RR | n | WR | STRESS exp | best-1%-rem | best-10%-rem | b0 / b1 | CALIB | med TP pips | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| H4-bo-raw-S | 1:2 | 107 | 0.34 | +0.175 | +0.158 | −0.012 | +0.106 / +0.491 | +0.096 | 151 | STRONG_PARTIAL |
| H4-bo-raw-S | 1:3 | 91 | 0.30 | +0.235 | +0.204 | −0.067 | +0.160 / +0.469 | +0.291 | 226 | STRONG_PARTIAL |
| H4-bo-raw-S | 1:4 | 77 | 0.23 | +0.312 | +0.263 | −0.055 | +0.277 / +0.418 | +0.121 | 302 | STRONG_PARTIAL |
The higher-RR variants are strongly profitable (STRESS +0.18…+0.31), both-blocks-positive, and CALIB-positive, but **thin at best-10%-removed** (slightly negative) — so only the RR 1:1.5 variant is fully ROBUST. Median TP 151–302 pips (all ≥70; %≥100 = 97–100%). These express the *same* edge at larger targets.

## 4. H1 corroboration + M15 rejection
- **`H1-hllh-S` (RR 1:3):** STRESS +0.187, best-1%-rem +0.165, both blocks positive (b0 +0.232 / b1 +0.128), median TP 148 pips, %≥70 = 0.93 — **but CALIBRATION NEGATIVE (−0.139)** → fails out-of-DEV → STRONG_PARTIAL, not ROBUST. H1 short-structure continuation is real in DEV but does not generalize to block2.
- **M15:** across all families/targets, uniformly weak or negative (best cells barely positive, none robust) — consistent with Phase 0. **M15 is a trigger layer, not an edge source, for the 70–80+ pip regime.**

## 5. Profile mapping — honest read
| profile | target | achieved under no-M5 conservative execution? |
|---|---|---|
| **A** (70–80% WR, RR 1:1.5–2) | high WR | **NO** — max WR ≈ 0.53 (flagship). The flagship's *median trade wins* (median R +1.434) and sits just below Profile A, but the 70–80% WR band is **unreachable without M5-timed tight entries.** `PENDING_M5`. |
| **B** (≈50% WR, RR 1:3–4) | high RR | **PARTIAL** — the RR 1:3–4 is achieved and strongly profitable (STRESS +0.23…+0.31), but WR (0.23–0.30) is **below** Profile B's 45–55% band. Again M5 timing would lift WR. |
Per the directive ("do not force a strategy into a profile if the evidence does not support it"), the flagship is reported as a **robust positive-expectancy H4 short-continuation edge, RR-flexible (1:1.5 ROBUST → 1:4 profitable)**, **PROFILE-UNRESOLVED pending M5** — it is closest to Profile A at RR 1:1.5.

## 6. Relationship to existing candidates
- **`H4-bo-raw-S` vs the prior `H1-B-bo-acc-SHORT`** (H1 pro-trend mandate): **same economic edge** — short breakout-continuation in gold downtrends, HTF-down-aligned — expressed on adjacent timeframes. **`H4-bo-raw-S` is the strictly more robust expression** (best-10%-rem +0.16 vs −0.028; b1 +0.498 vs +0.008; CALIB +0.152 vs +0.057). Recommend **H4 as the canonical timeframe** for this edge; they are **RELATED, not independent** — do not double-count.
- **vs S5 / S20** (LONG M15 breakout-continuation): **directionally orthogonal** (short vs long) → independent; this SHORT edge **diversifies** the LONG portfolio.

## 7. Answer to the directive's comparison question
**Which timeframe gives the strongest combination of robust expectancy, WR, RR, frequency, target size, cost survival, M5-execution quality?**
- **Robust expectancy / cost survival / temporal stability: H4 wins decisively** (only H4-short-breakout passes the full deep battery incl. best-10%-removed and out-of-DEV CALIB).
- **Target size: all three offer 70–80+ pip opportunities**, but only H4/H1 have structural stops wide enough to survive gold's ~66–76-pip 24h noise (Phase 0).
- **WR: capped at ≈53% for all under conservative no-M5 execution** → the WR dimension (and thus Profile A) is **gated on M5**, which is why option A matters.
- **Frequency: M15 ≫ H1 > H4** (H4 flagship 18/1k bars, low-frequency) — a real trade-off: H4 is the most robust but lowest-frequency.
- **M5-execution quality: unmeasurable until M5 DEV data lands** (`PENDING_M5`).
**Net: H4 is the strongest EDGE source; M5 is the missing piece for the WR/Profile-A dimension and exact intrabar path.**

## 8. Governance / reproducibility
`VALIDATION_ACCESS=0`, `FINAL_HOLDOUT_ACCESS=0`; VALIDATION (2022+) never read; M15→M5 aggregation refused; per-block gated (no 2013→2016 bridge); V4.4 (`23d98c07…`)/Market-Intelligence/N1–N6 untouched; broker DISABLED; nothing promoted; no integrity stop. Conservative stop-wins-ties execution → all figures are lower bounds. Artifacts in `reports/alpha_discovery/`: `econ_campaign.py`, `econ_campaign.json` (184 realizations), `deepen_econ.py`, `deepen_econ.json`. Cost model `AI_TRADER_SHADOW_COST_MODEL_v1` (BASE 0.05 / STRESS 0.24).

## 9. Recommendation / next step
1. **Forward `H4-bo-raw-S` (RR 1:1.5, ROBUST) to the validation queue** as a robust, temporally-stable, out-of-DEV-positive **SHORT** H4-continuation Alpha — the strongest candidate the program has produced — explicitly flagged `PROFILE-UNRESOLVED / PENDING_M5` and `PENDING_INDEPENDENT_VALIDATION`. It supersedes `H1-B-bo-acc-SHORT` (same edge, weaker TF).
2. **Option A (M5 acquisition) is the gating next step for the profiles:** once gated historical M5 for DEV lands, re-run this exact campaign with true M5 triggers to (a) pin the real WR, (b) test whether M5-timed tight entries lift the flagship into Profile A (70–80% WR @ 1:1.5), and (c) resolve intrabar path.
3. **Do not promote** anything to Strategy Catalog / AI Trader / LIVE; discovery-only.

**Terminal status:** `ECONOMIC_PROFILE_INTERIM_H4H1_COMPLETE` · `ROBUST_H4_SHORT_CONTINUATION_CANDIDATE_READY_FOR_CEO_REVIEW` (1 candidate, PROFILE-UNRESOLVED / PENDING_M5) · `M5_ACQUISITION_PENDING (option A)`. **STOP.**
