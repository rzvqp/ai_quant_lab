# STRATEGY DEVELOPMENT REPORT — workstream B (branch strategy-development, baseline 1bc0ffb)

Read-only over the reproducible baseline. In-sample research-segment metrics only; validation (OOS) shown
separately; holdout SEALED. **No statistical verdicts** — matched-null is still under validation on the other
branch. Classifications here are engineering/robustness triage, NOT significance.

## 0. Market context (decisive caveat)
XAUUSD rallied strongly across the research window (2023→2025, ~1800→4000+). **10 of the 11 shortlisted
candidates are LONG.** Much of their in-sample profit may be **directional drift/beta, not entry-timing
alpha.** Separating the two is exactly what the matched-null (Test B) does — and its drift scenario was the
one that required the ATR-scaled-risk fix. Expect several long-momentum candidates to fail matched-null.
Read every positive number below through this lens.

## 1. Classification of the 17 distinct candidates
- **B — Research candidate (11):** positive, valid execution, ≥2 years, multi-month, not top-1/3 dependent,
  mechanism robust to tuning (≥20% neighbours profitable), stability ≥0.45.
- **A — Profitable but fragile (6):** positive but knife-edge tuning, single-year/regime, or low stability.

### Fragile (A) — with the reason
| candidate | mechanism | n | exp | why fragile |
|---|---|---|---|---|
| C_46f00099 | S1/high/swing | 28 | 0.014 | knife-edge: only **3%** of tuning neighbours profitable; tiny n; no OOS |
| C_ff1d4063 | S1/low/session | 326 | 0.020 | knife-edge (17% neighbours); flagged fragile; stability 0.48 |
| C_a55d34d8 | S17/pw_low/reject | 137 | 0.142 | knife-edge (1 of 6 neighbours); high exp is tuning-specific |
| C_38a4ea2c | S17/pw_high/reject | 187 | 0.057 | knife-edge (1 of 6 neighbours) |
| C_3c96bb23 | S14/down (momentum exhaustion) | 118 | 0.035 | only 1 RW variant; stability 0.44; OOS exp −0.137 |
| C_e6081c5b | S6/ny/breakout/up | 395 | 0.017 | stability 0.44; thin edge; likely drift-beta |

## 2. Per-family prioritization (families WITH Research-Worthy)

**S1 — liquidity-sweep reversal (5 mechanisms).** Distinct by direction × liquidity pool.
- *low/pdh_pdl (long, sweep of prior-day low)* — C_dca5629f, n=399, exp .032, stab .77, yearly −.04/.11/.22 (improving), **OOS −0.06**.
- *low/swing (long, sweep of rolling swing low)* — C_954698b1, n=193, exp .071, but yearly −.73/.12/.08/−.08 (unstable, 2022 & 2025 negative), OOS ≈0.
- *high/pdh_pdl (SHORT, sweep of prior-day high)* — C_9214b37b, n=241, exp .017, yearly −.03/.03/.30, **OOS +0.346** — the only SHORT candidate; a genuine diversifier in a long-dominated set.
- Two more (high/swing, low/session) → fragile (§1). **Keep max 3: the two pdh_pdl variants (long + short) + low/swing.**

**S2 — failed-breakout fade (1).** low/ref=pdh_pdl, C_204a973a, n=268, exp .060, yearly −.05/.17/.47, **OOS +0.256**.
Mean-reversion at prior-day levels; economically distinct from momentum; strongest OOS in the set. **Keep.**

**S5 — opening-range momentum (1).** ny/up, C_2d587447, n=287, exp .166, PF 1.48, **maxDD 7.3R (lowest)**,
**positive every year** .166/.134/.162/.46, OOS +0.179. Cleanest, most consistent candidate. **Keep (top).**

**S6 — session-transition (2).** london/fade/down C_227d3ef2 looks good on paper (exp .025, mfrac .75) but
**its entire edge is 2022 (1.86R); 2023-25 ≈ .01-.03** → effectively dead post-2022. ny/breakout/up →
fragile. **Downgrade london/fade to fragile despite passing the screen** (Claude override — see shortlist).

**S8 — extension mean-reversion (1).** vwap/up C_5ae92203, n=302, exp .017, but yearly .35/−.04/.08/−.02 —
**2022-only, negative in 2023 & 2025** (top-year concentration 1.97). Fragile in practice. **Keep only as a
mean-reversion probe, low priority.**

**S9 — MTF-trend momentum (2).** c4h=up/any (n=545) and c4h=up/align (n=512). Both long-trend continuation,
improving yearly, OOS +0.10 / +0.25. **They correlate r=0.70 → redundant; keep ONE (any, larger n).**

**S14 — momentum exhaustion (1).** down, fragile (§1). Only 1 RW; OOS negative. **Registry only.**

**S17 — weekly levels (3).** pw_high/breakout C_11418358 (n=171, exp .287 — highest exp, PF 1.43, yearly
.09/.45/.31 all positive) but **OOS −0.086** (in-sample strong, OOS weak). The two reject variants → knife-edge
fragile. **Keep pw_high/breakout, but flag the OOS red flag.**

**S20 — hybrid sweep+MTF (1).** h4up/breakout C_09d2245b, n=456, exp .075, yearly .09/−.00/.43 (2025-heavy),
OOS +0.087. Long-momentum; correlates with S9/S17 cluster. **Keep as the hybrid representative.**

## 3. Families with profitability but 0 Research-Worthy (exploratory — keep, do not optimize)
| family | econ | profitable variants | best | note |
|---|---|---|---|---|
| S3 | breakout-retest | 2 | exp .063 pf 1.09 n=761 long | thin edge, no variant clears RW screen |
| S13 | imbalance (FVG) fill | 5 | exp .041 pf 1.08 n=1324 long | high-frequency, low per-trade edge |
| S16 | previous-day levels | 1 | exp .032 pf 1.04 n=1146 long | marginal |
| S18 | time-of-day | 5 | exp .177 pf 1.31 n=534 long | interesting exp but no RW clear; calendar effect, drift-suspect |
| S19 | session gap | 4 | exp .915 pf 3.52 **n=16** | high exp but n<25 → statistically empty; not investable |
These remain in the registry as EXPLORATORY. No parameter tuning applied.

## 4. Families completely negative (do NOT rewrite to force profit)
| family | econ | variants | bestExp | why it failed / what a future version would need |
|---|---|---|---|---|
| S4 | vol-regime expansion | 32 | −0.145 | compression→expansion breakout has no directional edge on XAUUSD M15; expansion direction is ~random. A future version needs a directional filter (HTF bias) at the expansion, not raw range-expansion. |
| S7 | trend-pullback | 24 | −0.099 | EMA-pullback continuation; entries chase after the pullback confirms → enters late, adverse fill. Would need earlier limit entry into the pullback zone + trend-strength filter. |
| S10 | displacement continuation | 48 | −0.051 | continuation after displacement + controlled pullback; the pullback trigger front-runs reversals. Needs displacement-quality gating (volume/imbalance) and invalidation. |
| S11 | structure-break reversal | 24 | −0.052 | CHoCH against HTF trend fades a trend that persists (drift). In a bull market, shorting structure breaks loses. Needs regime conditioning. |
| S12 | range rotation | 48 | −0.036 | rotation from range extreme assumes ranging; the market trended → extremes kept extending. Needs a range-regime detector. |
| S15 | trend acceleration | 24 | −0.050 | buys acceleration bars → buys local tops; enters at max short-term extension. Needs a pullback-after-acceleration entry. |
Common theme: the six failures are mostly **continuation/expansion entries that chase moves** or
**counter-trend fades in a trending market**. None is a candidate now; each is a design note for a future
*new* family (not a re-tune of the existing one).

## 5. Answers
- Fragile strategies: the 6 in §1 (+ S6/london/fade and S8/vwap downgraded on yearly evidence).
- Distinct research candidates worth development: **~7–9** (see TOP_STRATEGIES_SHORTLIST).
- Everything positive here is PROVISIONAL and drift-suspect until matched-null + global-FDR run.
