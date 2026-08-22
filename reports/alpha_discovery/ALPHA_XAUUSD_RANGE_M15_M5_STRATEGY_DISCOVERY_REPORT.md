# ALPHA_XAUUSD_RANGE_M15_M5_STRATEGY_DISCOVERY_REPORT

**Mandate:** `ALPHA-XAUUSD-RANGE-M15-M5-STRATEGY-DISCOVERY-001` · **Date:** 2026-08-22.
**Terminal status:** `RANGE_M15_M5_ALPHA_DISCOVERY_COMPLETE` · **`NO_ROBUST_RANGE_M15_M5_ALPHA_FOUND`**.
**Scope:** open RANGE strategy search; M15 structure + M5 entry; price-only XAUUSD; native-M5; DEV-only; no CALIB/2024/2025+/N4/V1; no MI retuning (RANGE v4.4/v4.5 untouched). No AI Trader / execution install. 18 M15 hypotheses tested (≤24), 0 survivors → no Phase B/C. No promotion; broker disabled.

---

## 0. Headline
- **No RANGE mechanism produced a tradeable edge on 2021-2023 gold.** Every family — **fade (mean-reversion), breakout-continuation, compression→expansion, false-breakout→rotation**, both UPPER-SHORT and LOWER-LONG, at multiple targets — is **net-negative after costs**, with **median R ≈ −1.0** (most trades stopped) and **no year-robust positive**.
- **The opportunity is economically trivial:** boundary-attack median favorable excursion is **14–24 project pips** (≥80p only 2–14%), so even before expectancy the natural move is too small relative to the failure rate and cost.
- **Root cause (mechanistic):** the research-local M15 "ranges" of 2021-2023 are shallow consolidations *inside strong trends* (2022 selloff, 2023 rally). **Fades get run over by trend resumption (65–80% structural failure); breakouts whipsaw (58–72% false).** Neither mean-reversion nor breakout has a clean path.
- Per §41, zero survivors is an acceptable outcome — not forced.

## 1. Evidence firewall (§4)
Price-only XAUUSD. Native gated M5 → causal M15 (`m5_data.py`). DEV 2021-07-27→2023-12-29 (M15 ~40,650 bars). No CALIB/2024/2025+/N4/V1/exogenous. No MI retuning.

## 2. Research-local RANGE structure (§7) — `RESEARCH_LOCAL_RANGE_STRUCTURE_v1` (NOT canonical)
Causal, price-only, mechanical, versioned — **explicitly a research-strategy-local structure, not a replacement for RANGE v4.4/v4.5**:
- Trailing window **W = 24 M15 bars** (6h). Boundaries = shifted rolling **max-high / min-low** over [i−W, i−1] (causal Donchian). Mid = (hi+lo)/2.
- Range active iff **|trailing directional efficiency| < 0.35** (balanced auction), **width ∈ [50, 600] project pips**, and close within [lo, hi].
- Episode id = contiguous in-range run.
Result: 33,488 in-range bars, **3,822 episodes**, median width **97p**. (Deliberately broad; the boundary-attack setups are the object of study.) No future bars; no P&L-based tuning.

## 3. M15 setups + event ownership (§11, §30)
First UPPER attack (`high ≥ range_hi`) and first LOWER attack (`low ≤ range_lo`) per episode: **UPPER 864 / LOWER 786** (unique episodes). Breakout setups (was-in-range → M15 close beyond boundary): **UP 916 / DOWN 818**. Compression→expansion: UP 241 / DOWN 192. One row per episode-interaction (no correlated multi-entry inflation).

## 4. Path-first 4-class (§14, §15) + DISC/CONF (§24) — all mechanisms NET-NEGATIVE
Chronological DISC/CONF cut 2023-04-05. Entry next M15 open, M15 structural stop, net STRESS cost (2.4p). avg R / class shares / year:

| mechanism (M15 entry) | N | A clean | C failure | avgR | medR | WR | DISC | CONF | 2021/22/23 |
|---|---|---|---|---|---|---|---|---|---|
| UPPER-FADE-SHORT →mid | 858 | 0.31 | 0.68 | −0.277 | −1.13 | 0.32 | −0.268 | −0.292 | −.32/−.40/−.22 |
| UPPER-FADE-SHORT →oppLo | 858 | 0.16 | 0.80 | −0.300 | −1.16 | 0.20 | −0.299 | −0.302 | −.29/−.25/−.32 |
| LOWER-FADE-LONG →mid | 783 | 0.34 | 0.65 | −0.229 | −1.12 | 0.34 | −0.196 | −0.275 | −.24/−.24/−.23 |
| LOWER-FADE-LONG →oppHi | 783 | 0.17 | 0.79 | −0.234 | −1.14 | 0.21 | −0.297 | −0.149 | −.41/−.29/−.15 |
| UPPER-BREAKOUT-LONG rr2 | 916 | 0.28 | 0.63 | −0.135 | −1.06 | 0.35 | −0.123 | −0.156 | −.11/−.23/−.12 |
| UPPER-BREAKOUT-LONG mm | 916 | 0.26 | 0.66 | −0.099 | −1.08 | 0.32 | −0.111 | −0.080 | +.03/−.25/−.11 |
| LOWER-BREAKOUT-SHORT rr2 | 818 | 0.27 | 0.65 | −0.197 | −1.06 | 0.32 | −0.252 | −0.117 | −.36/−.24/−.11 |
| COMPRESSION-EXP-LONG rr2 | 241 | 0.32 | 0.65 | −0.116 | −1.08 | 0.34 | −0.043 | −0.238 | −.10/−.06/−.14 |
| COMPRESSION-EXP-SHORT rr2 | 192 | 0.29 | 0.69 | −0.217 | −1.07 | 0.30 | −0.171 | −0.309 | −.31/+.00/−.27 |
| FALSE-BREAKUP→SHORT-rotation | 526 | — | — | −0.106 | −1.06 | 0.44 | −0.078 | −0.157 | −.10/−.10/−.11 |
| FALSE-BREAKDOWN→LONG-rotation | 473 | — | — | **−0.021** | −0.83 | 0.48 | −0.009 | −0.041 | −.08/−.06/+.02 |
**Not one family is positive after costs.** The closest to breakeven (false-breakdown→long, −0.021) is still negative on both DISC and CONF and in 2 of 3 years. RR variants (1.5/2/3) all negative (fuller grid in `range_m15m5.py`/`range_m15m5b.py`).

## 5. Opportunity magnitude (§16) — economically trivial
Favorable excursion (MFE):
- **Fade** (toward mid): UPPER median MFE **14p**, ≥30p 0.24, ≥50p 0.09, ≥80p 0.02; LOWER median **16p**, ≥80p 0.03.
- **Breakout** (continuation): UPPER median MFE **24p**, ≥30p 0.43, ≥50p 0.27, ≥80p 0.14, ≥100p 0.10; LOWER median **23p**, ≥80p 0.14.
Median adverse (MAE) 15–28p ≈ favorable — a poor favorable/adverse ratio. **Even the winners are small; §5's "reject economically-trivial edge" applies before expectancy even enters.**

## 6. Upper vs lower asymmetry (§9, §26)
No side is tradeable. Fades: LOWER-LONG slightly less-bad than UPPER-SHORT (−0.229 vs −0.277) but both negative. Breakouts: UPPER-LONG less-bad than LOWER-SHORT (−0.10 vs −0.20). The asymmetry reflects the 2021-2023 net-up drift, not an edge — neither side clears zero.

## 7. Phases B/C (§21) — not reached
**No M15 family survived Phase A**, so per the staged process (§21) no M5 value-add (Phase B) or strategy conversion (Phase C) was performed — there is no positive parent for M5 timing to refine, and M5 entry cannot rescue a structurally-negative expectancy (established program-wide). Robustness/concentration/M5 sections (§27–§30) are therefore N/A.

## 8. Candidate registry / graveyard (§22, §45) — full, no hidden graveyard
18 materially-distinct M15 hypotheses, **all in graveyard:** UPPER/LOWER FADE × {mid, opp} (4); UPPER-BREAKOUT-LONG × {rr1.5, rr2, rr3, mm} (4); LOWER-BREAKOUT-SHORT × {rr1.5, rr2, rr3, mm} (4); COMPRESSION-EXP × {LONG, SHORT} × {rr2, rr3} (4); FALSE-BREAKOUT→ROTATION × {up→short, down→long} (2). Config fingerprint: `RESEARCH_LOCAL_RANGE_STRUCTURE_v1` (W=24, |effic|<0.35, width 50-600p), horizon 48 M15 bars, STRESS 2.4p, entry next-M15-open. Artifacts: `range_m15m5.py`, `range_m15m5b.py`.

## 9. Limitations
- Bounded to `RESEARCH_LOCAL_RANGE_STRUCTURE_v1` on 2021-2023 DEV. A different local range definition could select different episodes — but the *economic finding* (2021-2023 gold consolidations are shallow and trend-embedded; fade run-over + breakout-whipsaw) is regime-driven and unlikely to reverse under a reasonable alternative definition.
- Phase A used M15-open entry (per §21); M5 refinement was correctly deferred and, given zero positive parents, not warranted.
- No exogenous rescue attempted (§38).

## 10. CEO recommendation
1. **`NO_ROBUST_RANGE_M15_M5_ALPHA_FOUND`.** A genuine, broad, mechanism-first search — fade, breakout-continuation, compression→expansion, and false-breakout→rotation, both sides, path-first — finds **no tradeable RANGE edge** on 2021-2023 XAUUSD. Every family is net-negative after costs with median R ≈ −1.0 and no year-robust positive; the natural opportunity (14–24p) is economically trivial.
2. **This is regime-consistent, not a search failure.** 2021-2023 gold is trend-dominated; its local balances are shallow consolidations inside trends, so fading them loses to trend resumption and breaking them out loses to whipsaw — the same wall the entire program has met. **Zero survivors is the honest outcome (§41), not forced.**
3. **The canonical parallel stands:** RANGE v4.4 confirms zero macro ranges on this exact period (mandate `79beabf`) — consistent with the research-local finding that 2021-2023 offers little genuine RANGE structure to trade. A productive RANGE-Alpha search likely needs either a genuinely range-bound population (not 2021-2023) or the CEO/VE's RANGE-detector decision.
4. **No MI retuning; no M5/strategy conversion; no promotion; broker disabled; DEV-only.** RANGE v4.4 (`3bb61cf`) and all 9 frozen strategies untouched; portfolio SHORT still only frozen `H4-bo-raw-S`.

**Terminal status:** `RANGE_M15_M5_ALPHA_DISCOVERY_COMPLETE` · `NO_ROBUST_RANGE_M15_M5_ALPHA_FOUND`. **STOP.**
