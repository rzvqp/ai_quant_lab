# ALPHA_MT_H4_EFFICIENCY_L_GATE_M_REPORT

**Mandate:** `ALPHA-MT-H4-EFFICIENCY-L-GATE-M-001` (corrective audit) · **Date:** 2026-08-21 · **Statistician ref:** `STAT_MT_H4_EFFICIENCY_L_INDEPENDENT_VALIDATION_PROTOCOL.md`, commit `32e69ab`.
**Gate M question:** *Does `effic > 0.4` add Alpha beyond simple H4 LONG trend beta?*
**VERDICT: `GATE_M_FAIL_H4_TREND_BETA`.** The efficiency condition provides **no incremental economic value** over the bullish-regime baseline; conditional on TREND_UP it is **negatively** incremental. The candidate's standalone edge is **serialization/trajectory value, not signal-filter value**.
**DEV-only. No CALIB used for selection. No retuning. No new ID. Candidate geometry unchanged.**

---

## 0. Headline
- **Frozen candidate reproduced exactly** (serialized M1 = n 46, WR 0.435, STRESS +0.3798, best-5%-rem +0.3226, best-10%-rem +0.2668) → audit is faithful.
- **Raw per-signal (trajectory-free, pure SIGNAL FILTER value):** M0 all-H4 +0.011 · **M1 effic +0.080** · **M2 TREND_UP +0.106**. **M1 is WORSE than M2.**
- **§8 decisive diagnostic — within TREND_UP:** effic subset **−0.0001** vs all-TREND_UP **+0.106** → **incremental −0.106.** Efficiency selects *worse* trades once the regime is fixed.
- **The serialized +0.3798 is a trajectory artifact:** 200 alternate valid trajectories of the same M1 signals have median **−0.010** (mean +0.024); the frozen ordering sits at the 75.5th percentile of a ~0-centred, very-wide distribution. Not trajectory-invariant.
- **Interpretation (per §8): the candidate is primarily `H4_LONG_TREND_BETA`.**

## 1. Frozen identity (unchanged, §1)
`MT-H4-efficiency-L`: H4 LONG; signal `effic[i] > 0.4` (net/path over 20 H4 bars); entry next-H4-open; **structural SL** = min(low[i−4:i]) − 0.15·ATR (H4); **RR 1.5** rr-exit; max hold 48 H4 bars; cost tick 0.01 / STRESS RT 0.24; mstrat serialization (non-overlap guard); DEV population (H4 aggregated from gated M5). **Nothing changed** — only the signal condition is ablated for M0/M2.

## 2. M0 / M1 / M2 definitions (§2–§3)
| id | signal condition (all else identical) |
|---|---|
| **M0_ALL_H4_REFERENCE** | every H4 bar LONG (efficiency filter removed entirely) |
| **M1_EFFICIENCY_FILTERED** | `effic > 0.4` — **the frozen candidate** |
| **M2_TREND_UP_REFERENCE** | `ema20 > ema50` (bullish regime, NO efficiency) — diagnostic control, not a promoted strategy |

## 3. Opportunity populations + intersections (§4, §7)
| population (H4 DEV, LONG, i≥51, ATR-valid) | raw N |
|---|---|
| M0 (all H4) | **2,601** |
| M1 (effic>0.4) | **339** |
| M2 (ema20>ema50) | **1,467** |
- **M1 ∩ M2 = 311** → **91.7% of M1 signals occur in TREND_UP** (confirms the ~90% figure).
- **Selectivity:** M1 selects **13.0%** of all H4 opportunities, and **23.1%** of TREND_UP opportunities.
- Populations constructed **independently before execution** (no IR-DIR-L-mid ablation error).

## 4. Serialization control — SIGNAL FILTER value vs SERIALIZATION value (§4) — the crux
| population | **RAW per-signal** avg R (trajectory-free) | **SERIALIZED** (frozen policy) avg R | n raw → n serialized |
|---|---|---|---|
| M0 all-H4 | +0.011 | −0.027 | 2601 → 325 |
| **M1 effic** | **+0.080** | **+0.3798** (= frozen candidate) | 339 → 46 |
| M2 TREND_UP | +0.106 | +0.110 | 1467 → 131 |
**The serialized M1 (+0.38) is ~5× its own raw per-signal value (+0.08).** That uplift is **serialization/dedup value**, not signal value: the non-overlap guard, applied to M1's *sparse, clustered* efficiency signals, systematically selects the *first-of-cluster* (early-move) trade and skips the extended ones. At the SIGNAL-FILTER level (raw), **M1 (+0.080) is below M2 (+0.106).** This is precisely the SIGNAL-vs-SERIALIZATION distinction the mandate required, and it inverts the apparent ranking.

## 5. Required comparisons (§5) — raw per-signal, STRESS
| metric | M0 | **M1** | M2 | **M1−M0** | **M1−M2** |
|---|---|---|---|---|---|
| N | 2601 | 339 | 1467 | — | — |
| WR | 0.333 | 0.351 | 0.372 | +0.018 | **−0.021** |
| BASE avg R | +0.039 | +0.098 | +0.132 | +0.059 | **−0.034** |
| STRESS avg R | +0.011 | +0.080 | +0.106 | +0.069 | **−0.026** |
| PF | 1.019 | 1.153 | 1.194 | +0.134 | −0.041 |
| maxDD | 233.9R | 38.3R | 84.8R | — | — |
| best-1%-removed | −0.004 | +0.067 | +0.092 | — | −0.025 |
| best-5%-removed | −0.067 | +0.009 | +0.033 | — | −0.024 |
| best-10%-removed | −0.153 | −0.073 | −0.048 | — | −0.025 |
| top-1% profit share | 1.375 | 0.176 | 0.137 | — | — |
| top-5% share | 6.82 | 0.889 | 0.705 | — | — |
| top-10% share | 13.61 | 1.82 | 1.406 | — | — |
**M1 beats M0** (efficiency avoids non-uptrend bars) **but LOSES to M2 on every economic metric** — expectancy, WR, PF, and all tail metrics. Efficiency is a **noisier, worse proxy for "be in an uptrend."** (M2's larger top-share vs M1 is a scale effect of its larger sample; both are far below M0's pathological concentration.)

## 6. Regime-conditioned incremental value (§8) — THE most important diagnostic
Within TREND_UP only (raw per-signal, STRESS):
| subset | N | avg R | WR | best-10%-rem |
|---|---|---|---|---|
| **effic-in-uptrend (M1∩M2)** | 311 | **−0.0001** | 0.328 | −0.166 |
| all TREND_UP (M2) | 1467 | +0.106 | 0.372 | −0.048 |
| TREND_UP but NOT effic (M2−M1) | 1156 | **+0.134** | 0.384 | — |
**Incremental avg R of `effic>0.4` within TREND_UP = −0.106.** Conditional on the same bullish regime, the efficiency-filtered subset (≈0) **underperforms** both the full TREND_UP reference (+0.106) and the non-efficiency uptrend bars (+0.134). **Efficiency does not separate better future outcomes from ordinary bullish H4 persistence — it selects the *worse* ones** (over-extended/late-in-move bars that stall or mean-revert). → `EFFICIENCY_FILTER_NO_INCREMENTAL_ALPHA`.

## 7. Temporal comparison (§6) — raw per-signal, STRESS (N / avg R / WR)
| year | M0 | M1 (effic) | M2 (TREND_UP) |
|---|---|---|---|
| 2021 | 619 / −0.085 / 0.288 | 64 / **−0.204** / 0.172 | 353 / **−0.021** / 0.309 |
| 2022 | 444 / +0.254 / 0.432 | 60 / +0.117 / 0.367 | 299 / **+0.269** / 0.448 |
| 2023 | 1538 / −0.020 / 0.322 | 215 / +0.155 / 0.400 | 815 / +0.101 / 0.372 |
**Efficiency does NOT improve the adverse period — it makes it worse:** 2021 M1 −0.204 vs M2 −0.021 (efficiency is 10× more negative in the weak year). In 2022 M2 (+0.269) beats M1 (+0.117). Only in 2023 does M1 (+0.155) edge M2 (+0.101) at the raw level — a single favorable year, not a systematic improvement. The frozen candidate's serialized 2023-concentration (~92% of profit) is amplified by serialization; the raw efficiency signal is not even 2023-concentrated (2022 +0.117 ≈ 2023 +0.155). **Efficiency concentrates/worsens rather than stabilizes.**

## 8. Trajectory invariance (§9 / Gate N)
Serializing the same M1 signal set over 200 alternate valid non-overlapping trajectories:
| | avg R |
|---|---|
| canonical (ei-ascending = frozen policy) | **+0.3798** |
| 200 random valid trajectories: mean / median | +0.024 / **−0.010** |
| p05 / p95 / min / max | −1.01 / +0.74 / −1.05 / +0.98 |
| raw per-signal mean (all 339) | +0.080 |
The frozen +0.38 sits at the **75.5th percentile** of a **~0-centred, extremely wide** trajectory distribution. **The serialized edge is NOT trajectory-invariant** — it is one favorable draw of the non-overlap policy on sparse signals. The Gate M conclusion, however, **is** trajectory-invariant, because it rests on the raw per-signal / §8 comparison (which uses all signals, no serialization).

## 9. Incremental-value conclusion
- `effic > 0.4` **beats M0 (all-H4)** only because it correlates with being in an uptrend (regime selection).
- `effic > 0.4` **loses to M2 (TREND_UP)** on every raw metric, and is **−0.106 incremental within TREND_UP**.
- Efficiency **worsens** the adverse 2021 period and does not systematically beat the regime baseline in any year.
- The standalone serialized +0.38 is **serialization/trajectory value**, high-variance and non-invariant.
→ **`EFFICIENCY_FILTER_NO_INCREMENTAL_ALPHA`.** The candidate `MT-H4-efficiency-L` is properly interpreted as **`H4_LONG_TREND_BETA`** — bullish-regime exposure to gold's 2021–2024 up-move, executed with a favorable serialization draw, not an efficiency edge.

## 10. GATE M VERDICT
```
GATE_M_FAIL_H4_TREND_BETA
```
`effic > 0.4` does **not** demonstrate meaningful incremental economic value over the TREND_UP baseline; conditional on the regime it is negatively incremental (−0.106) and it worsens the weak period. Sample is adequate (M1 raw n=339, M2 n=1467) → not inconclusive. Standards were not lowered because the frozen candidate is profitable — its profitability is trend beta + serialization, not the efficiency filter.

## 11. Consequences / honest disclosures
- **`MT-H4-efficiency-L` should NOT be advanced as an "efficiency edge."** Its edge is H4 long trend beta. If a bullish-regime beta strategy is wanted, the simpler, better-founded reference is **M2 (`ema20>ema50` H4 LONG)** — which dominates M1 at the raw level — but M2 is a **diagnostic control, not a promoted strategy** (§3), and this mandate creates **no new ID**.
- **Flag for the Statistician:** `MT-H4-dispaccept-L` (also H4 LONG, same family) warrants the identical Gate M audit — it may share the same trend-beta-plus-serialization character. Not audited here (out of scope).
- **Governance:** V1 not consumed; protected evidence not accessed; candidate not retuned; no new strategy ID; DEV-only; no CALIB used for selection; no Red Team / AI Trader / live.

**Terminal status:** `GATE_M_FAIL_H4_TREND_BETA` · `EFFICIENCY_FILTER_NO_INCREMENTAL_ALPHA` · `MT-H4-efficiency-L → interpret as H4_LONG_TREND_BETA`. **STOP.**
