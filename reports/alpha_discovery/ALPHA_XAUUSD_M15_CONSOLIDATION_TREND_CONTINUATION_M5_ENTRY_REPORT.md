# ALPHA_XAUUSD_M15_CONSOLIDATION_TREND_CONTINUATION_M5_ENTRY_REPORT

**Mandate:** `ALPHA-XAUUSD-M15-CONSOLIDATION-TREND-CONTINUATION-M5-ENTRY-001` · **Date:** 2026-08-22.
**Terminal status:** `M15_TREND_CONTINUATION_ALPHA_DISCOVERY_COMPLETE` · **`M15_TREND_CONTINUATION_SIGNALS_WEAK`** · `FRESH_OR_DIFFERENT_TREND_HYPOTHESES_REQUIRED`.
**Scope:** NEW independent family (H4/H1 trend context → M15 consolidation/pullback → continuation, M5 entry). Price-only XAUUSD; native-M5; DEV-only; no CALIB/2024/2025+/N4/V1; no MI/RANGE/S5 change. Not RANGE research (uses "consolidation/pullback/compression", never "RANGE"). No AI Trader/execution. No promotion; broker disabled.

---

## 0. Headline
- **No robust candidate; one weak lead.** Across 3 mechanisms × LONG/SHORT × RR, the **only** positive, multi-year family is **`TREND-CONT-SHORT-PB-BREAK` (H1-downtrend + M15 shallow-pullback break-down + H1-structural stop, rr2): avgR +0.164, positive all three years (2021 +0.33 / 2022 +0.01 / 2023 +0.15), class-C reversal 0.22, WR 0.49, N=128** — but it **fails robustness** (best-10%-removed −0.022, tail-dependent), is **DISC-weak** (+0.027 vs CONF +0.274), and **M5 timing adds no value.** Not a candidate; a weak lead.
- **The key structural finding:** M15 continuation only works with a **wider H1-structural stop, not a tight M15 stop** — tight M15 pullback-low stops give 49–73% class-C reversal (noise stop-out); H1 stops drop reversal to ~22% (§23 confirmed: the parent structure must own invalidation).
- **M5 confirmation does not prove incremental value (§21) → M5 layer rejected** (it made SHORT DISC negative and 2022 negative; LONG 2021 negative).

## 1. Evidence firewall + timeframe hierarchy (§3, §5)
Price-only. Native gated M5 → causal M15/H1/H4 (`m5_data.py`). DEV 2021-07-27→2023-12-29 (M15 40,649 bars). **H4 = broad context, H1 = active trend context (`regime==TREND_UP/DOWN`, i.e. `ema20 vs ema50 & effic ≷ ±0.30`, aligned to M15 by close_time), M15 = setup, M5 = entry only.** M15 DEV: H1_up 6,767 bars / H1_dn 5,237.

## 2. M15 mechanisms tested (§8) — impulse/consolidation/pullback, causal
Six materially-distinct M15 hypotheses (× LONG/SHORT), all causal (no future pivots):
- **PB_EMA** — pullback below/above ema20 then trend-side reclaim (impulse→pullback→continuation).
- **PB_BREAK** — shallow pullback (<60% of prior impulse) then break of the recent consolidation extreme in trend direction.
- **COMP_EXP** — ATR compression after impulse then trend-direction expansion bar (volatility contraction→expansion).
Event ownership: dedup within 4 bars (one event per cluster, §37).

## 3. Phase A — M15 parent discovery (§19), path-first 4-class
Entry next M15 open, **tight M15 structural stop** (pullback low), net STRESS, 4-class (A clean / B adverse-first-then-continue / C reversal / D stall), DISC/CONF cut 2023-05-16. **Every mechanism/side/RR NET-NEGATIVE** (avgR −0.07 to −0.42), **class-C reversal 49–73%**, median R ≈ −1.0, best-10%-removed negative, no year-robust positive (positive cells single-year: PB_EMA-LONG 2023, PB_BREAK-SHORT 2021). **Tight M15 stops are noise-stopped before continuation.**

## 4. Phase A variant — H1-structural (wider) stop (§23) — the lead emerges
Same setups, **H1-structural stop** (recent H1 swing low/high, median risk ~80p): class-C reversal drops to ~22% for PB_BREAK. Results (net STRESS, M15 entry):
| family (H1 stop) | N | avgR | medR | WR | best-10%-rem | DISC | CONF | 2021/22/23 |
|---|---|---|---|---|---|---|---|---|
| **PB_BREAK-SHORT rr2** | 128 | **+0.164** | −0.039 | 0.49 | **−0.022** | +0.027 | +0.274 | **+0.33 / +0.01 / +0.15** |
| PB_BREAK-SHORT rr3 | 128 | +0.170 | −0.062 | 0.48 | −0.083 | +0.006 | +0.301 | +0.37 / −0.09 / +0.16 |
| PB_BREAK-LONG rr3 | 229 | +0.038 | −0.121 | 0.46 | −0.219 | +0.059 | +0.006 | −0.10 / +0.07 / +0.09 |
| PB_EMA-SHORT rr3 | 277 | +0.018 | −1.041 | 0.34 | −0.296 | −0.096 | +0.153 | +0.16 / −0.01 / −0.02 |
| COMP_EXP (all) | 69–90 | −0.05 to −0.27 | — | — | negative | — | — | negative |
| PB_EMA-LONG (all) | 363 | −0.07 to −0.12 | — | — | negative | — | — | negative |
**Only PB_BREAK-SHORT rr2/rr3 is positive across all/most years with both splits positive** — but best-10%-removed is negative (tail-dependent), and the edge is CONF/2021-concentrated (DISC only +0.027).

## 5. Phase B — M5 value-add (§20, §21) — rejected
M5-confirmation entry (first M5 bar continuing the break within 8 bars after the M15 setup) vs the M15-open baseline, PB_BREAK, H1 stop:
| | M15 baseline | M5-confirm |
|---|---|---|
| SHORT rr2: avgR / DISC / 2022 | +0.164 / +0.027 / +0.008 | +0.095 / **−0.170** / **−0.247** (N 128→79) |
| LONG rr3: avgR / 2021 | +0.038 / −0.098 | +0.056 / **−0.274** |
**M5 filtering does not improve — it worsens DISC and single years and cuts N.** Per §21, the M5 layer is **rejected** (no genuine incremental value).

## 6. Opportunity magnitude (§17)
PB_BREAK (the lead) median MFE 30–35p, ≥80p 16–19%, ≥100p 9–13% — modest but the best of the mechanisms (PB_EMA 20–25p, COMP_EXP 20–29p). MAE ≈ MFE (poor ratio with tight stops; the H1 stop is what makes PB_BREAK-SHORT marginally work). Natural opportunity is below the CEO's preferred 70–80p+ for most setups.

## 7. Robustness / concentration / effective N (§34, §35, §36) — why the lead is WEAK not robust
`PB_BREAK-SHORT` (H1 stop, rr2): **best-10%-removed −0.022, best-5%-removed +0.075** → the positive expectancy is carried by the top ~10% of trades (tail-dependent); removing them turns it negative. **DISC +0.027 vs CONF +0.274** → the edge is confirmation/period-concentrated, not discovery-robust. N=128 across ~128 unique H1-downtrend episodes (moderate). **Fails the §42 serious-candidate bar (robustness after top-trade removal; DISC→CONF magnitude consistency).**

## 8. LONG / SHORT asymmetry (§33)
Asymmetric, as expected: the weak-positive is the **SHORT** side (PB_BREAK), not LONG — in the H1-downtrend pockets of 2021–2023, a shallow-pullback break-down continues marginally often enough (with an H1 stop) to be tail-carried positive; the LONG equivalent is flat/tail-negative. Neither side is robust.

## 9. Candidate registry / graveyard (§28, §45) — complete, no hidden
18 core M15 hypotheses (PB_EMA / PB_BREAK / COMP_EXP × LONG/SHORT × {M15-stop, H1-stop}) + 2 M5 variants on the survivor. **Graveyard (all fail):** every PB_EMA, every COMP_EXP, PB_BREAK-LONG (tail-negative), PB_BREAK with tight M15 stop, all M5-confirmation variants. **Weak lead (not promoted):** `TREND-CONT-SHORT-PB-BREAK` (H1 stop, rr2). Config fingerprint: H1 `regime` context, M15 PB_BREAK setup (shallow<60% pullback + consolidation-extreme break), H1-swing stop, rr2, HOR 32 M15, STRESS 2.4p, entry next-M15-open. Artifacts: `trend_cont.py`.

## 10. Limitations
- Bounded to the tested mechanisms/contexts on 2021-2023 DEV. The weak lead is tail-dependent and DISC-weak — likely period-luck as much as edge.
- The winning geometry (H1 stop) partly overlaps the *concept* of the frozen `HR-TU-pb-L` (H1 trend-pullback) — but that is a frozen LONG H1 candidate; this weak lead is a distinct SHORT M15 family and is **not** merged with it (§2).
- No exogenous rescue (§38); no threshold grid-mining (§29) — only the structural stop-ownership variant was tested.

## 11. CEO recommendation
1. **`M15_TREND_CONTINUATION_SIGNALS_WEAK`.** A genuine, broad, path-first search finds **no robust trend-continuation candidate** ready for validation, but **one weak lead**: `TREND-CONT-SHORT-PB-BREAK` (H1-downtrend + M15 shallow-pullback break-down + H1-structural stop, rr2) — positive expectancy (+0.164) across all three years, low reversal rate (0.22) — **held back by tail-dependence (best-10%-removed negative) and a DISC-weak/CONF-strong split.**
2. **Do NOT forward it to validation as-is** — it fails the §42 robustness bar. **`FRESH_OR_DIFFERENT_TREND_HYPOTHESES_REQUIRED`.** The two structural lessons worth carrying forward: (a) M15 continuation needs an **H1-structural stop**, not a tight M15 stop (a tight stop is noise-stopped 49–73%); (b) **M5 entry timing adds no value** to these M15 continuation parents (rejected on evidence, §21).
3. **Honest negatives dominate:** PB_EMA and COMP_EXP fail both sides; PB_BREAK-LONG is tail-negative; M5-confirmation worsens robustness. Zero robust survivors is the accepted outcome (§44), not forced.
4. **No MI/RANGE/S5 change; no M5 promotion; no AI Trader; broker disabled; DEV-only.** All 9 frozen strategies untouched; portfolio SHORT still only frozen `H4-bo-raw-S`.

**Terminal status:** `M15_TREND_CONTINUATION_ALPHA_DISCOVERY_COMPLETE` · `M15_TREND_CONTINUATION_SIGNALS_WEAK` · `FRESH_OR_DIFFERENT_TREND_HYPOTHESES_REQUIRED`. **STOP.**
