# ALPHA_XAUUSD_H1_H4_SHORT_SPECIALIST_DISCOVERY_REPORT

**Mandate:** `ALPHA-XAUUSD-H1-H4-SHORT-SPECIALIST-DISCOVERY-001` · **Date:** 2026-08-22 · **Stat evidence:** commit `b8d0447`.
**Terminal status:** `XAUUSD_SHORT_ALPHA_DISCOVERY_COMPLETE` · **`NO_ROBUST_SHORT_ALPHA_FOUND`**.
**Firewall (re-verified):** gated M5 loader (file sha `cbb6eebe…`) → causal H1/H4; no `read_csv` on `data/market/`; `N4_M5_TRIGGER_USAGE_COUNT = 0`; `ALPHA_ACCESS_2025_PLUS = 0`. 26 IDs (≤50). DEV-only (CALIB closed). No promotion; broker disabled; existing candidates frozen.

---

## 0. Headline — answers to §27
1. **Genuine robust SHORT specialist? NO** — 0 of 26 mechanisms survive the raw-signal gates (STRESS>0, best-5%-removed>0, top-10%≤60%, incremental over PROJECT TREND_DOWN).
2. **Which TF owns the strongest SHORT edge? Neither** — both fail. **PROJECT TREND_DOWN is itself unprofitable to short: H4 −0.176, H1 +0.016.**
3. **Does bearish displacement contain incremental Alpha? NO** — disp_only H4 −0.056 / H1 −0.104, tail-fragile.
4. **Does bearish follow-through add value after displacement? Relatively yes, absolutely no** — disp_follow beats disp_only (H4 −0.033 vs −0.056; H1 −0.044 vs −0.104), consistent with the bullish effect, but both stay negative/tail-fragile.
5. **Failed bullish continuation tradeable SHORT? NO** — H4 −0.144 / H1 −0.126.
6. **Support/range breakdown tradeable? NO** — breakdown H4 −0.065; positive variants are tail-fragile.
7. **Retest improve/hurt? Neither robustly** — breakdown_retest H1 +0.056 but tail-fragile (top-10% 438%).
8. **M15/M5 entry value? N/A** — no serious candidate to time.
9. **Which beat PROJECT TREND_DOWN? Several beat the deeply-negative H4 baseline on *incremental*, but none clears the absolute/tail gates** — "less bad than shorting pullbacks" ≠ Alpha.
10. **Which target ≥80–300 pips? All** (medTP 110–400p) — geometry is fine, the edge is absent.
11. **Most complementary to S5? None.** 12. **Deserves Statistician review? None.**

## 1. Evidence integrity
Gated M5 via `edge_research._common.load` (loader `flowA_common_v6…`, file sha `cbb6eebe…`), causally aggregated to H4 (2,652 DEV bars) and H1 (10,168 DEV bars). No `read_csv` on `data/market/`; N4 usage 0; 2025+ access 0; CALIB not opened (no survivor to freeze).

## 2. Raw opportunity construction + methodology (§1)
**Raw-signal-first discipline (mandatory after the serialization failures):** each mechanism's complete signal population is built independently of trading; **raw per-signal expectancy (causal, no serialization)** is the primary evidence. SHORT entry next-edge-bar open; **edge-TF structural SL** = max(high[i−4:i]) + 0.15·ATR (H4/H1, not M5); RR H4 1.5 / H1 2.5; walk 48 bars stop-first; cost tick 0.01 / STRESS 0.24. A mechanism is killed at the raw stage (no eventization) if STRESS≤0 **or** incremental-vs-TREND_DOWN≤0 **or** best-5%-removed≤0 **or** top-10%-share>60% — because a raw signal with negative expectancy / median −1.0 has no edge for eventization to recover (contrast the bullish dispaccept, whose raw was +0.262 and broad).

## 3. PROJECT TREND_DOWN baseline (§2)
`PROJECT TREND_DOWN = ema20 < ema50 AND effic < −0.30` (mirror of the Statistician-confirmed PROJECT TREND_UP; same short geometry). Raw per-signal STRESS: **H4 −0.176 (n=363), H1 +0.016 (n=1345).** **Shorting the bearish regime on H4 loses money** — the "downtrends" in gold 2021–2023 were pullbacks within an uptrend that reverted. This baseline is itself the first evidence that a robust short is unlikely on this population.

## 4–5. H4 + H1 SHORT results (full raw table, STRESS)
| mechanism | TF | n | STRESS | median R | best-5%-rem | top-10% share | incr vs TD | medTP | verdict |
|---|---|---|---|---|---|---|---|---|---|
| disp_follow | H4 | 75 | −0.033 | −0.824 | −0.096 | ∞* | +0.143 | 400p | RAW_FAIL |
| disp_only | H4 | 144 | −0.056 | −1.008 | −0.136 | ∞ | +0.120 | 316p | RAW_FAIL |
| breakdown | H4 | 73 | −0.065 | −1.006 | −0.132 | ∞ | +0.111 | 341p | RAW_FAIL |
| **breakdown_disp** | H4 | 47 | **+0.055** | −0.108 | −0.009 | 231.7% | +0.231 | 388p | RAW_FAIL (tail/conc) |
| breakdown_retest | H4 | 102 | −0.072 | −1.006 | −0.153 | ∞ | +0.104 | 358p | RAW_FAIL |
| lowerhigh_break | H4 | 183 | −0.121 | −1.008 | −0.204 | ∞ | +0.055 | 259p | RAW_FAIL |
| failed_rally | H4 | 84 | −0.172 | −1.019 | −0.255 | ∞ | +0.004 | 125p | RAW_FAIL |
| failed_bull_cont | H4 | 171 | −0.144 | −1.008 | −0.224 | ∞ | +0.032 | 262p | RAW_FAIL |
| comp_exp_down | H4 | 15 | — | — | — | — | — | — | SPARSE |
| trend_exhaust_down | H4 | 148 | −0.144 | −1.008 | −0.225 | ∞ | +0.032 | 273p | RAW_FAIL |
| momentum_down | H4 | 304 | −0.122 | −1.010 | −0.206 | ∞ | +0.054 | 220p | RAW_FAIL |
| efficiency_down | H4 | 227 | −0.314 | −1.013 | −0.406 | ∞ | −0.138 | 206p | RAW_FAIL |
| range_low_break | H4 | 48 | −0.115 | −1.007 | −0.185 | ∞ | +0.061 | 325p | RAW_FAIL |
| disp_follow | H1 | 311 | −0.044 | −1.008 | −0.172 | ∞ | −0.060 | 322p | RAW_FAIL |
| disp_only | H1 | 638 | −0.104 | −1.017 | −0.236 | ∞ | −0.120 | 242p | RAW_FAIL |
| breakdown | H1 | 311 | +0.035 | −0.903 | −0.089 | 708.7% | +0.019 | 289p | RAW_FAIL (tail/conc) |
| breakdown_disp | H1 | 241 | −0.015 | −0.523 | −0.146 | ∞ | −0.031 | 329p | RAW_FAIL |
| breakdown_retest | H1 | 452 | +0.056 | −0.530 | −0.068 | 437.8% | +0.040 | 307p | RAW_FAIL (tail/conc) |
| lowerhigh_break | H1 | 739 | −0.077 | −1.017 | −0.208 | ∞ | −0.093 | 218p | RAW_FAIL |
| failed_rally | H1 | 276 | −0.260 | −1.042 | −0.395 | ∞ | −0.276 | 109p | RAW_FAIL |
| failed_bull_cont | H1 | 713 | −0.126 | −1.022 | −0.260 | ∞ | −0.142 | 196p | RAW_FAIL |
| comp_exp_down | H1 | 244 | −0.188 | −1.025 | −0.326 | ∞ | −0.204 | 183p | RAW_FAIL |
| trend_exhaust_down | H1 | 622 | −0.103 | −1.022 | −0.238 | ∞ | −0.119 | 199p | RAW_FAIL |
| momentum_down | H1 | 1142 | −0.067 | −1.019 | −0.200 | ∞ | −0.083 | 200p | RAW_FAIL |
| efficiency_down | H1 | 914 | +0.055 | −1.014 | −0.071 | 447.3% | +0.039 | 180p | RAW_FAIL (tail/conc) |
| range_low_break | H1 | 175 | +0.052 | −0.506 | −0.065 | 465.9% | +0.036 | 301p | RAW_FAIL (tail/conc) |
*∞ = top-10% share undefined/huge (net profit ≤0). **Every mechanism fails.** The five with a positive mean (breakdown_disp-H4 +0.055, breakdown-H1 +0.035, breakdown_retest-H1 +0.056, efficiency_down-H1 +0.055, range_low_break-H1 +0.052) are all **tail-fragile (best-5%-removed negative) and catastrophically concentrated (top-10% share 231–709%)** — the tiny net is 1–2 outlier trades.

## 6. Bearish displacement (§3A, §27.3)
disp_only: H4 −0.056 / H1 −0.104. **No incremental Alpha** (marginal beat of the deeply-negative H4 baseline only; absolute negative + tail-fragile). Bearish displacement carries no robust predictive edge on this population.

## 7. Bearish follow-through (§5, §27.4)
disp_follow vs disp_only: **H4 −0.033 vs −0.056 (+0.023); H1 −0.044 vs −0.104 (+0.060).** Follow-through *does* improve on displacement-alone — the *same relative effect* the bullish signal showed — but both remain **negative and tail-fragile**. So the bullish disp+follow-through's incremental information has **no profitable bearish analogue** (confirming §5's no-symmetry caution): the relative ordering is preserved, the absolute edge is not.

## 8–12. Failed-bull-continuation / breakdown / failed-rally / range-breakdown / transition
- **Failed bullish continuation** (§6): H4 −0.144 / H1 −0.126 — FAIL (predicting tops via structure break loses).
- **Breakdown** (§7): breakdown H4 −0.065; +displacement H4 +0.055 (tail-fragile); +retest H1 +0.056 (tail-fragile). **Retest neither robustly helps nor hurts** (§27.7) — it produces a marginally-positive-but-concentrated mean, same class as the others.
- **Failed rally** (§8): the *worst* — H4 −0.172 / H1 −0.260 (shorting into resistance in an uptrend is punished).
- **Range-low breakdown** / **trend-exhaustion-down** / **transition-down** (§8): all FAIL (−0.10 to −0.14) or tail-fragile.

## 13. M15/M5 timing (§10)
**Not applicable** — no serious H1/H4 candidate survived the raw gate to time.

## 14. Incremental attribution (§2)
The only mechanisms with *positive incremental vs PROJECT TREND_DOWN* are on H4 (because the H4 TREND_DOWN baseline is −0.176). But every one of them is either **absolutely negative** or **tail-fragile/concentrated**. **No mechanism is both absolutely positive AND tail-robust AND incremental** — the conjunction the gate requires. "Beating a losing baseline while still losing or lottery-dependent" is correctly rejected.

## 15. Tail robustness (§14)
**best-5%-removed is negative for all 26 mechanisms** (range −0.007 to −0.41). The five positive-mean mechanisms have top-10% net-profit share 231–709% (Gate I ≤60% failed by 4–12×). No short mechanism is broad-based.

## 16. Path / serialization robustness (§15)
**Not reached** — path robustness is only tested for raw survivors; there are none. (The raw-first discipline correctly stops before serialization, avoiding the manufacture of a spurious executable edge from a non-edge — the exact error of the H4-DISP-FOLLOW-L-COOLDOWN6 CALIB failure.)

## 17. Temporal robustness (§16) — the decisive structural finding
For the least-bad mechanisms (raw per-signal, STRESS):
| mechanism | 2021 | **2022 (gold selloff)** | 2023 |
|---|---|---|---|
| SH-H4-breakdown_disp | +0.195 | **−0.784** | +0.114 |
| SH-H4-disp_follow | +0.122 | **−0.689** | +0.116 |
| SH-H1-efficiency_down | +0.292 | **−0.256** | +0.052 |
| SH-H1-disp_follow | −0.113 | +0.026 | −0.035 |
**Short mechanisms LOSE in 2022 — the year with gold's largest bearish move** (Mar–Sep 2022 selloff), whipsawed by the sharp Q4-2022 recovery. The marginal positives sit in the bullish/recovery years (2021, 2023) as tail outliers. This is stronger than `TEMPORAL_CONCENTRATION`: there is **no** bearish episode where shorts robustly work — not even the big-selloff year. Median short = full stop everywhere.

## 18. Effective RR + 19. Economic geometry (§13, §25)
Geometry is adequate (SHORT is not failing for lack of target room): median TP 110–400 pips across mechanisms; H4 breakdown-family medTP 340–400p, %TP≥80 = 1.00, ≥300 ≈ 0.5–0.85. Nominal = effective RR (rr-exit). **The failure is edge, not economics.**

## 20. CALIB (§20)
**Not opened.** No candidate passed DEVELOPMENT; per §20 CALIB remains closed. No frozen identity to evaluate.

## 21. Complementarity (§26)
**Not applicable** — no survivor to compare against `S5` / `H4-bo-raw-S`. (The frozen `H4-bo-raw-S` short — from the earlier 2011–2018 population — was untouched and is unaffected; it does not exist on this 2021–2024 population's mechanisms.)

## 22. Graveyard (§28) — all 26, NO_EDGE class
All bearish mechanisms on H4+H1 — displacement, displacement+follow-through, breakdown (±displacement, ±retest), lower-high break, failed rally, failed bullish continuation, compression→expansion-down, trend-exhaustion-down, momentum-down, efficiency-down, range-low breakdown. Failure code **NO_EDGE** (median −1.0, negative/tail-fragile raw expectancy) for all; the five positive-mean ones additionally **TAIL + CONCENTRATION**. Recorded in `short_records.json`. New `SH-` IDs; existing candidates untouched.

## 23–24. Candidate ranking + CEO recommendation
1. **No SHORT candidate is recommended — `NO_ROBUST_SHORT_ALPHA_FOUND`.** Across 26 diverse bearish mechanisms on H4 and H1, none produces a robust, tail-safe, incremental short edge after realistic cost on the gated 2021–2024 population.
2. **Structural conclusion for the CEO:** the persistent "no SHORT specialist" gap is a **property of the data, not the search method.** Gold 2021–2024 was fundamentally long-biased: **even the bearish regime (PROJECT TREND_DOWN) is unprofitable to short (H4 −0.176)**, the median short is a full stop, and — decisively — **short mechanisms lose in 2022, the actual selloff year** (whipsaw). The bullish disp+follow-through signal's incremental information has **no profitable bearish mirror** (§5 confirmed empirically — do not assume symmetry).
3. **What this rules out and what remains:** a robust SHORT specialist does not exist for standard price-structure mechanisms on this population. A genuine bearish edge would likely require either (a) a different population containing a real secular gold downtrend (e.g., 2011–2013, where `H4-bo-raw-S` was found), or (b) a fundamentally different (non-price-structure) signal class — neither in scope here.
4. **No promotion; broker disabled; DEV-only; CALIB not opened.** Existing candidates (`S5`, `H4-bo-raw-S`, `TR-H4-rng2trend_disponly-L`, `IR-DIR-L-mid`, `HR-TU-pb-L`, all frozen references) unaltered. The portfolio's SHORT exposure remains only the frozen `H4-bo-raw-S` (different, earlier population).

**Terminal status:** `XAUUSD_SHORT_ALPHA_DISCOVERY_COMPLETE` · `NO_ROBUST_SHORT_ALPHA_FOUND`. **STOP.**
