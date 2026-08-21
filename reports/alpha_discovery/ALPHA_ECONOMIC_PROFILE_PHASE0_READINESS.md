# ALPHA ECONOMIC-PROFILE PROGRAM — PHASE 0: DATA READINESS + TIMEFRAME ECONOMIC FEASIBILITY

**Directive:** CEO `ALPHA ECONOMIC PROFILE DIRECTIVE` (2026-08-21) — reorient Alpha Discovery to **M15/H1/H4 EDGE → M5 causal trigger → structural SL → 70–80+ project-pip economic target**, searching two profiles (A: 70–80% WR @ 1:1.5–2 RR; B: ~50% WR @ 1:3–4 RR). Pip convention **10 project pips = $1.00**.
**Status:** `ECONOMIC_PROFILE_PHASE0_COMPLETE` · **`M5_EXECUTION_LAYER_BLOCKED_ON_DEV_DATA — CEO DECISION REQUIRED`** + timeframe economic-feasibility findings that stand independently of M5.
**VALIDATION_ACCESS_COUNT = 0. FINAL_HOLDOUT_ACCESS_COUNT = 0.** Manifest-gated DEV only; per-block (no cross-gap); RATIFIED cost BASE 0.05 / STRESS 0.24; broker DISABLED; nothing promoted.

---

## 0. Headline
1. **The economic premise is confirmed:** 70–80+ project-pip opportunities are **abundant** on all three edge timeframes (~50–60% of pro-trend continuation signals reach ≥80 pips MFE within 24h; median favorable excursion 83–91 pips). This is **not** micro-scalping territory — the target size the directive wants is real.
2. **On raw edge/cost economics for the 70–80+ pip regime, the higher timeframes win: H4 > H1 ≫ M15.** The binding constraint is gold's natural ~66–76-pip 24h **adverse** excursion (MAE): a structural SL must be wide enough to survive it, and only H4 (and partially H1) has naturally wide-enough structural stops. M15's tight stops (~23 pips) are shredded by noise → negative expectancy at every target.
3. **HARD BLOCKER:** native M5 XAUUSD data has **ZERO coverage of the DEVELOPMENT discovery blocks** (2011–13, 2016–18). The M5-triggered architecture **cannot be evaluated on the gated discovery population** without a data decision (§1). The only well-covered M5 region is the **SEALED VALIDATION** block — off-limits during discovery.
4. **The M5 layer is well-motivated, not cosmetic:** HTF bars hide the intrabar order of SL-vs-TP touches (large "ambiguous" fraction, §3), which is exactly the path-order an M5 trigger would resolve — a quantified justification for the CEO's architecture.

## 1. M5 execution-layer data readiness — the blocker
`data/market/OANDA_XAUUSD_M5.csv` covers **2021-07-27 → 2026-07-27** only. Against the ratified manifest blocks:
| block | window | M5 bars | usable for discovery? |
|---|---|---|---|
| b0 (DEV) | 2011-07-26 → 2013-09-27 | **0** | ❌ no M5 exists |
| b1 (DEV) | 2016-01-11 → 2018-04-06 | **0** | ❌ no M5 exists |
| calib | 2020-08-11 → 2021-09-05 | 7,787 (only Jul–Sep 2021 sliver) | ⚠️ too small |
| VALIDATION (SEALED) | 2022-12-16 → 2025-10-12 | 199,803 | ❌ VALIDATION_ACCESS=0 |

M5 is **finer** than the M15 base population → it **cannot** be aggregated down from M15 (that would fabricate sub-bar structure). It needs its own gated historical source.
**Decision menu for the CEO:**
- **(A) RECOMMENDED — acquire historical M5 XAUUSD for the DEV blocks** (2011–13, 2016–18) via the Data Acquisition division, under the same manifest gating. Unblocks the full architecture cleanly.
- **(B) PROHIBITED under current governance — re-home discovery to 2022+** where M5 is ample: that region **is** the sealed VALIDATION block; using it as discovery would burn the holdout (`VALIDATION_ACCESS=0`). Not done.
- **(C) INTERIM — proceed with M15/H1/H4 edge research using next-edge-bar-open entry as an M5 proxy**, deferring true M5 refinement until (A) lands. Produces edge candidates and full economic reporting **except** M5 execution quality and intrabar path resolution.

I did **not** fabricate M5, aggregate M15→M5, or touch VALIDATION. Phase 0 proceeds on option (C)'s in-governance analysis below.

## 2. Timeframe economic-feasibility scan (gated DEV, per-block, ~24h forward horizon)
Canonical robust continuation entry on each edge TF: **20-bar breakout + acceptance, HTF-trend-aligned** (M15/H1 aligned to H4-EMA20>EMA50; H4 aligned to D1), structural SL = broken level ± 0.3·ATR (floored 0.8·ATR), entry next-edge-bar open. MFE/MAE measured over a fixed **24h** forward window (M15 96 bars / H1 24 / H4 6) so target-size is compared apples-to-apples. Cost RATIFIED BASE 0.05 / STRESS 0.24 debited per trade (as a fraction of each trade's SL).

| edge TF | n (L/S) | median SL | MFE pips P25/P50/P75 | %MFE ≥70 / ≥80 / ≥100 | MAE pips P50/P75 |
|---|---|---|---|---|---|
| **M15** | 2291 (1227/1064) | $2.31 (23 pips) | 40 / **83** / 154 | 0.56 / 0.52 / 0.43 | 75 / 143 |
| **H1** | 709 (396/313) | $5.11 (51 pips) | 43 / **91** / 161 | 0.60 / 0.55 / 0.46 | 76 / 145 |
| **H4** | 203 (108/95) | $9.99 (100 pips) | 45 / **83** / 157 | 0.58 / 0.51 / 0.43 | 66 / 140 |

**Read-out:** target-size (MFE) is **timeframe-invariant** (~83–91 pip median) — it's a property of gold's 24h volatility, not the entry TF. What differs is the **structural SL**, which scales with TF ATR: M15 23 pips, H1 51, H4 100.

## 3. Target-anchored profile economics (structural SL + economic TP)
For TP ∈ {70, 80, 100} project pips, RR = TP/SL falls out of the TF. WR shown as a **range** `[pessimistic … optimistic]` because HTF bars hide intrabar SL-vs-TP order (ambiguous = both touched within the window); expectancy is computed **pessimistically** (ambiguous → loss) = a lower bound. STRESS = after 0.24 round-trip.

| edge TF | target | median RR | WR range | **STRESS exp (R)** | best-1%-rem | W/L/ambig/none |
|---|---|---|---|---|---|---|
| M15 | 70p | 1:3.0 | 0.20–0.56 | **−0.344** | −0.335 | 453/966/835/37 |
| M15 | 80p | 1:3.5 | 0.19–0.52 | −0.269 | −0.271 | 436/1056/745/54 |
| M15 | 100p | 1:4.3 | 0.17–0.43 | −0.130 | −0.154 | 389/1211/590/101 |
| H1 | 70p | 1:1.4 | 0.34–0.60 | −0.125 | −0.136 | 242/246/185/36 |
| H1 | 80p | 1:1.6 | 0.31–0.55 | −0.058 | −0.075 | 222/264/167/56 |
| **H1** | **100p** | **1:2.0** | **0.27–0.46** | **+0.061** | +0.031 | 194/300/131/84 |
| H4 | 70p | 1:0.7 | 0.45–0.58 | −0.012 | −0.007 | 92/50/25/36 |
| **H4** | **80p** | **1:0.8** | **0.41–0.51** | **+0.028** | +0.030 | 84/55/20/44 |
| **H4** | **100p** | **1:1.0** | **0.37–0.43** | **+0.098** | +0.096 | 74/62/13/54 |

**The structural mechanism (why H4 wins):** gold's median 24h **MAE ≈ 66–76 pips**. Expectancy is positive only when the structural SL comfortably exceeds this noise floor:
- **M15** SL 23 pips ≪ 75-pip MAE → stopped by noise before the target → **negative at all targets** (STRESS −0.13 to −0.34).
- **H1** SL 51 pips ≈ 76-pip MAE → borderline; turns **positive only at the 100-pip target** (STRESS +0.061, RR 1:2).
- **H4** SL 100 pips > 66-pip MAE → survives noise → **positive at 80 & 100-pip targets** (STRESS +0.028 / **+0.098**, best-1%-rem positive).

## 4. Profile mapping (A vs B) — honest read
Neither a **clean Profile A** (70–80% WR) nor a **clean Profile B** (1:3–4 RR at ~50% WR) is achieved by this *vanilla, no-M5* mechanism — as expected:
- The only STRESS-positive, tail-robust cells are **H4 @ 80–100-pip target** and **H1 @ 100-pip target**, both at **RR ≈ 1:1–1:2 and WR ≈ 37–46%** (pessimistic). That is *between* the two profiles — a modest positive-expectancy zone, not yet either target profile.
- **To reach Profile A** (high WR, small RR) you need a *tighter* SL that is **not** noise-hit — impossible with HTF structural stops (too wide) but plausible with a **well-timed M5 entry** that places a tight stop just beyond an M5 structure. **This is precisely the role of the blocked M5 layer.**
- **To reach Profile B** (1:3–4 RR) you need the target ≫ SL while still being reached often enough — favored by H4's wide-move regime but requiring 300–400-pip targets that fewer signals reach; needs dedicated study.
- **The WR ambiguity (large "ambig" counts) is the intrabar path M5 resolves.** Example: M15 70p has 835 ambiguous of 2291 — the true WR/expectancy hinges on whether SL or TP printed first, which only sub-M15 (M5) bars reveal. This quantifies *why* the CEO's M15/H1/H4-edge → M5-trigger architecture is the right shape.

## 5. What this means for the program (recommendation)
1. **Best edge-source timeframe on current evidence: H4, then H1.** For the 70–80+ pip economic regime, H4 continuation gives the only cleanly STRESS-positive, tail-robust economics (H4 @ 100p: STRESS +0.098, best-1%-rem +0.096); H1 @ 100p is marginally positive; **M15 as a standalone edge source is economically unviable for this target regime** (its tight structural stops are shredded by gold's 24h noise). M15's role, if any, is as a *finer trigger*, not the edge.
2. **Unblock M5 first (option A).** The two target profiles (esp. Profile A) are unreachable without the M5 entry layer, and the WR is only pin-downable with intrabar (M5) path resolution. Recommend tasking Data Acquisition to source manifest-gated historical M5 XAUUSD for the DEV blocks (2011–13, 2016–18).
3. **Interim (option C) next step, if the CEO wants motion before M5 lands:** run the full economic-profile candidate search on **H4 and H1 edges** with next-bar-open entry, reporting every mandated field (SL/TP USD+pips, P25/50/75, %≥70/80/100, MFE/MAE, BASE/STRESS/best-1%-rem, temporal stability, frequency) — flagging M5-execution-quality and exact WR as `PENDING_M5`.
4. **Do not force profiles.** On present evidence the vanilla mechanism sits between A and B; I will not label a candidate Profile A/B until the evidence (with M5 timing) supports it.

## 6. Governance / reproducibility
`VALIDATION_ACCESS=0`, `FINAL_HOLDOUT_ACCESS=0`; VALIDATION M5 (2022+) never read; M15→M5 aggregation refused (would fabricate sub-bar data); per-block gated eval (no 2013→2016 bridging); V4.4 (`23d98c07…`)/Market-Intelligence/N1–N6 untouched; broker DISABLED; nothing promoted. No integrity stop triggered (the M5 gap is reported, not worked around). Artifacts in `reports/alpha_discovery/`: `econ_profile_scan.py`, `econ_profile_scan.json`. Cost model `AI_TRADER_SHADOW_COST_MODEL_v1` (BASE 0.05 / STRESS 0.24). HTF trend from the ratified `_from_M15_v2` sources.

**Terminal status:** `ECONOMIC_PROFILE_PHASE0_COMPLETE` · `M5_EXECUTION_LAYER_BLOCKED_ON_DEV_DATA — CEO_DECISION_REQUIRED` (recommend option A: acquire gated historical M5 for DEV; interim option C available on H4/H1). **STOP.**
