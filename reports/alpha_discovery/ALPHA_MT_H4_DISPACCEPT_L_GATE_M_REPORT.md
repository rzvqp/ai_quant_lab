# ALPHA_MT_H4_DISPACCEPT_L_GATE_M_REPORT

**Mandate:** `ALPHA-MT-H4-DISPACCEPT-L-GATE-M-001` (corrective audit) · **Date:** 2026-08-21.
**Gate M question:** *Do displacement + acceptance conditions add predictive Alpha beyond generic H4 LONG trend exposure?*
**VERDICT: `GATE_M_PASS`.** Displacement+acceptance adds **genuine incremental economic value** over the H4 TREND_UP baseline on trajectory-free evidence, is **tail-robust**, is **TRAJECTORY_ROBUST** (the published number is conservative, not a favorable serialization draw), and is **positive even in the adverse 2021 period** where pure trend beta lost. The Alpha comes from the **acceptance/continuation confirmation**, not raw displacement.
**DEV-only. No retuning. No new ID. No V1/protected evidence. No CALIB used for selection.**

---

## 0. Headline (contrast with the efficiency-L audit)
- **Frozen candidate reproduced exactly** (serialized M1 = n 41, WR 0.341, STRESS +0.1972, best-5%-rem +0.1232, best-10%-rem +0.0491) → faithful.
- **Raw per-signal (trajectory-free = SIGNAL value):** M0 all-H4 +0.011 · **M1 dispaccept +0.262** · M2 TREND_UP +0.106. **M1 BEATS M2** (opposite of efficiency-L, where M1 < M2).
- **§5 within-TREND_UP:** dispaccept subset **+0.277** vs all-TREND_UP **+0.106** → **incremental +0.172**, and tail-robust (best-10%-rem +0.162 vs M2's −0.048). Genuine incremental Alpha.
- **Trajectory:** canonical +0.197 sits at the **30.5th percentile** (median random +0.49) → the published figure *understates*; profitability does NOT depend on favorable serialization. `TRAJECTORY_ROBUST`.
- **Temporal:** positive **all three years incl. adverse 2021 (+0.423)** — not bull-segment concentration.
- **Source of the Alpha:** the **acceptance** (continuation confirmation), not raw displacement. Disclosed inefficiency: the frozen d+2 entry timing is *suboptimal* (leaves edge on the table vs d+1) — noted, **not** retuned.

## 1. Frozen identity (unchanged, §1)
`MT-H4-dispaccept-L`: H4 LONG. **Displacement** at bar d: `close[d]−open[d] > 1.0·ATR[d]` (up). **Acceptance** at d+1: `close[d+1] > close[d]`. **Entry** next-open (d+2). **Structural SL** = min(low[i−4:i]) − 0.15·ATR (i = acceptance bar = d+1). **RR 1.5** rr-exit; max hold 48 H4 bars; cost tick 0.01 / STRESS 0.24; mstrat serialization. DEV H4 (aggregated from gated M5). Nothing changed; only the signal condition is ablated for M0/M2 and decomposed for D0/D1/D2.

## 2. Opportunity populations (§3)
| population (H4 DEV, LONG) | raw N |
|---|---|
| M0 (all H4) | 2,601 |
| **M1 (dispaccept, frozen)** | **76** |
| M2 (TREND_UP, ema20>ema50) | 1,467 |
- M1 ∩ M2 = 49 → **64.5% of M1 occurs in TREND_UP** (notably *lower* than efficiency-L's 91.7% — dispaccept also fires at trend *starts* outside strict ema-uptrend). M0∩M1 = 76, M0∩M2 = 1,467. Populations built independently before serialization.

## 3. Trajectory-free signal value (§4) — STRESS
| metric | M0 | **M1 dispaccept** | M2 TREND_UP |
|---|---|---|---|
| N | 2601 | **76** | 1467 |
| WR | 0.333 | 0.368 | 0.372 |
| BASE avg R | +0.039 | **+0.269** | +0.132 |
| STRESS avg R | +0.011 | **+0.262** | +0.106 |
| PF | 1.019 | **1.679** | 1.194 |
| median R | — | +0.327 | — |
| best-1%-removed | −0.004 | **+0.242** | +0.092 |
| best-5%-removed | −0.067 | **+0.208** | +0.033 |
| best-10%-removed | −0.153 | **+0.133** | −0.048 |
| top-1% / 5% / 10% profit share | 1.38 / 6.82 / 13.6 | 0.09 / 0.24 / 0.54 | 0.14 / 0.71 / 1.41 |
**M1 dispaccept dominates BOTH baselines at the raw per-signal level** — 2.5× the TREND_UP expectancy (+0.262 vs +0.106), higher PF, and materially better tails (best-10%-removed +0.133 vs M2's −0.048). The top-share figures show the edge is broad-based (top-1% contributes only 9% of profit), **not** lottery-like.

## 4. Decisive conditional test (§5) — within TREND_UP
| subset | N | avg R | WR | PF | best-10%-rem |
|---|---|---|---|---|---|
| **dispaccept-in-uptrend (M1∩M2)** | 49 | **+0.277** | 0.388 | 1.70 | **+0.162** |
| all TREND_UP (M2) | 1467 | +0.106 | 0.372 | 1.19 | −0.048 |
| TREND_UP NOT dispaccept | 1418 | +0.100 | 0.372 | — | — |
**Incremental avg R of dispaccept within TREND_UP = +0.172** (and PF 1.70 vs 1.19, tails +0.162 vs −0.048). Conditional on the same bullish regime, displacement+acceptance **strongly outperforms** the reference. This is the opposite of efficiency-L (−0.106) → dispaccept **passes** the decisive test.

## 5. Displacement / acceptance attribution (§6)
Parent = 141 displacement events (body > 1.0·ATR up); 75 (53.2%) show acceptance.
| variant | N | avg R (STRESS) | best-10%-rem |
|---|---|---|---|
| D0 TREND_UP reference | 1467 | +0.106 | −0.048 |
| D1 displacement-only (enter d+1) | 141 | +0.125 | −0.028 |
| **D2 displacement + acceptance (enter d+2, frozen)** | 75 | **+0.259** | **+0.128** |
- **Does displacement add value?** *Barely* — D1 (+0.125) is only **+0.020** over D0 (+0.106). Raw displacement alone is close to trend beta.
- **Does acceptance add incremental value after displacement?** *Yes, decisively* — D2 (+0.259) vs D1 (+0.125) = **+0.134**, and it converts a tail-fragile set (D1 best-10%-rem −0.028) into a tail-robust one (+0.128). **The acceptance/continuation-confirmation is the source of the Alpha**, not the displacement.

## 6. Acceptance cost (§7) — a disclosed inefficiency
On the 75 accepted displacements, comparing entry timing (same SL/TP):
| entry | avg R | WR |
|---|---|---|
| **enter d+1 (no wait)** | **+0.478** | 0.493 |
| enter d+2 (accept-wait, frozen) | +0.259 | 0.373 |
**Acceptance-WAIT costs −0.219 avg R** (median entry-price delta +3.68 USD = enters higher/worse for a long; WR drops 0.493→0.373). Also **15 winning displacements were "missed"** because they didn't formally accept. So there are two distinct effects: the acceptance **FILTER** (select continuing displacements) is highly valuable (+0.478 for the accepted set at d+1), but the acceptance **WAIT** (entering a bar later at d+2) gives back roughly half. **The frozen candidate's entry timing is suboptimal** — entering at d+1 would capture more. *This is disclosed, not acted on: no retuning under this mandate.* It does not change the verdict — even with the suboptimal wait, D2 (+0.259) beats the regime baseline (+0.106).

## 7. Serialization audit / trajectory invariance (§8)
| | avg R | n |
|---|---|---|
| canonical (frozen policy) | **+0.1972** | 41 |
| 200 random valid trajectories: mean / median | +0.462 / +0.489 | — |
| p05 / p95 / min / max | −0.876 / +1.488 / −1.014 / +1.491 | — |
| raw per-signal mean (all 76) | +0.262 | — |
| **canonical percentile** | **30.5%** | — |
**The published +0.197 sits BELOW the median trajectory (+0.489) — at the 30.5th percentile.** Unlike efficiency-L (where the canonical was a *favorable* 75.5th-percentile draw inflating a weak signal), here the canonical trajectory is *conservative* and **understates** a genuinely positive signal (raw +0.262; trajectory median +0.489). Profitability does **not** depend on favorable serialization. → `TRAJECTORY_ROBUST`. (Caveat: trajectory variance is wide — p05 −0.88 — a small-sample deployment property, not a signal-validity issue.)

## 8. Temporal attribution (§9) — raw per-signal, STRESS
| year | M0 | **M1 dispaccept** | M2 TREND_UP | efficiency-L (ref) |
|---|---|---|---|---|
| 2021 | −0.085 (n619) | **+0.423** (n15) | −0.021 (n353) | −0.204 |
| 2022 | +0.254 (n444) | +0.017 (n13) | +0.269 (n299) | +0.117 |
| 2023 | −0.020 (n1538) | +0.278 (n48) | +0.101 (n815) | +0.155 |
**Positive in all three years, and strongly positive in the adverse 2021 (+0.423) where every baseline lost** (M0 −0.085, M2 −0.021, efficiency −0.204). Approx. profit share by year: **2021 ~32%, 2022 ~1%, 2023 ~67%** — the adverse year contributes ~a third of the profit, so this is **NOT** bull-segment concentration. This is the strongest single piece of evidence that dispaccept is *not* trend beta.

## 9. Tail audit (§10)
Raw per-signal M1: best-1%-rem +0.242, best-5%-rem +0.208, best-10%-rem +0.133; top-1%/5%/10% profit share 0.09/0.24/0.54. **Broad-based** — survives removing the top 10% strongly and no single trade dominates. (Serialized frozen: best-5%-rem +0.123, best-10%-rem +0.049 — the serialized sample is smaller/thinner but still positive.)

## 10. Effective geometry (§11)
Nominal RR 1.5; median SL **302 pips**, median TP **454 pips**; %TP ≥80 = 1.00, ≥150 = 1.00, ≥200 = 0.99, **≥300 = 0.83**. Genuinely large-move (median $45 target). Geometry is identical to the M0/M2 controls (same structural SL, same RR) — the edge is **not** a hidden geometry difference.

## 11. GATE M VERDICT
```
GATE_M_PASS
```
Displacement+acceptance demonstrates **incremental predictive/economic value beyond H4 TREND_UP beta** on fair, trajectory-free evidence: raw per-signal +0.262 vs +0.106; within-TREND_UP incremental +0.172; tail-robust (best-10%-removed +0.133); positive in the adverse 2021 (+0.423). The edge is `TRAJECTORY_ROBUST` (published figure is conservative) and is driven by the **acceptance/continuation confirmation** (displacement alone barely beats beta). Not a serialization artifact; not bull-segment concentration.

## 12. Honest disclosures / consequences
- **`MT-H4-dispaccept-L` is a genuine incremental-Alpha mechanism** (unlike `MT-H4-efficiency-L`, which failed as trend beta). It may proceed to **Statistician validation preparation**.
- **Disclosed inefficiency (§7):** the frozen entry at d+2 is suboptimal; entering at d+1 captures materially more (+0.478 vs +0.259 on accepted displacements). This is a **future-improvement candidate, NOT a retune** — flagged for a *separate* mandate; the current frozen identity is unchanged.
- **Caveats:** modest sample (raw n=76, serialized n=41, per-year n=13–48); wide trajectory variance (p05 −0.88) — the *expected* value is robustly positive but realized deployment on a small sample is variable. Statistician should weight the small-sample uncertainty.
- **Governance:** V1 not consumed; no protected evidence; no retuning; no new ID; DEV-only; no CALIB used for selection; no Red Team / AI Trader / live.

**Terminal status:** `GATE_M_PASS` · `DISPACCEPT_INCREMENTAL_ALPHA_CONFIRMED` (source = acceptance/continuation confirmation; entry-timing inefficiency disclosed) · `TRAJECTORY_ROBUST`. **STOP.**
