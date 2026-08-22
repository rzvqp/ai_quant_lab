# ALPHA_XAUUSD_PROBABILISTIC_BEARISH_STATE_REPORT

**Mandate:** `ALPHA-XAUUSD-PROBABILISTIC-BEARISH-STATE-001` · **Date:** 2026-08-22 · **Stat evidence base:** commit `b8d0447`.
**Terminal status:** `XAUUSD_PROBABILISTIC_BEARISH_STATE_COMPLETE` · **`PROBABILISTIC_BEARISH_SIGNAL_FOUND_EXECUTION_UNSOLVED`** (outcome B; borderline-A — see §DIRECTIONAL GATE).
**Firewall:** 100% XAUUSD price-only (no DXY/yields/macro/news/cross-asset/order-flow); gated M5 → causal M15/H1/H4; no `read_csv`; N4=0; 2025+=0; no V1/holdout/CALIB. **30 core continuous features + 1 justified interaction; 8 model identities (M1–M8) + 4 baselines (≤12/≤30 budgets).** 0 executable candidates frozen. DEV-only. No promotion; broker disabled; the 9 frozen strategies untouched.
**§31 discipline:** this report presents **predictive evidence only.** No feature is claimed to *cause* bearish moves; the failure of price models is **not** evidence that bearish moves are macro-driven. Neither claim is made.

---

## 0. Headline — answers to the §32 questions
1. **Can continuous price state predict bearish probability out-of-sample?** **Only weakly, and only in the extreme tail.** The full model is ~random (CONF AUC 0.505) and uncalibrated; discrimination appears only in the top ~2–5% of predicted states.
2. **Does it outperform discrete price-action sequences?** **Marginally.** It is the first representation to surface a persistent (if thin) out-of-sample *tail* elevation the discrete sequences never produced — but the overall model is no stronger.
3. **Which TF contains the most information?** **H1 > H4.** H4-only AUC 0.460 (below random), H1-only 0.490, H4+H1 0.502. None strong.
4. **Does combining H4+H1 help?** Marginally (0.490 → 0.502); not material.
5. **Does M15 add incremental information?** **No** (+0.003 AUC).
6. **Does rate-of-change matter more than static state?** **No** — ROC-only 0.470, static-only 0.497; both fail, static marginally better.
7. **Are predicted probabilities calibrated?** **No** — Brier 0.184 is *worse* than predicting the base rate (0.178); middle buckets non-monotone. Only the frozen tail thresholds order correctly.
8. **Is there a rare high-confidence bearish state?** **Yes** — top 2–5% predicted states show elevated bearish incidence (q0.90→0.279, q0.95→0.309, q0.98→**0.411** vs 0.231 base), monotone in the DISC-frozen threshold.
9. **Are high-confidence states economically tradeable?** **Not robustly.** The top-2% bucket executes positive and tail-robust (rr2 best-10%-removed +0.165, top-10% share 0.569) but on **n=20 trades, single-year-2023 OOS** → execution unsolved.
10. **Does it work outside 2022?** Cross-year model AUC stays 0.524–0.572 (train2021→test2022 0.572; →2023 0.524–0.529) — weak, no collapse. The executable window is only 2023, so the *strategy* cannot be confirmed outside 2023.
11. **Can it produce ≥80–300p targets?** Yes — top-bucket average bearish excursion ~113–129p; targets available.
12. **Is there an executable SHORT candidate?** **No robust one** — a thin research lead only.

## 1. Evidence integrity
Price-only. Gated M5 → causal M15/H1/H4 (`m5_data.py`). No exogenous inputs; no `read_csv`; N4=0; 2025+=0; CALIB/V1/holdout not opened; DEV-only. Modelling resolution = **H1** (10,001 valid labelled decision bars); H4/M15 state merged causally (last completed bar by `close_time`; alignment assertions pass).

## 2. Feature construction (§5, §20) — 30 core + 1 interaction
Compact causal continuous library: **H1 (18)** r5, r20, accel, persist, updown_asym, rv, vol_exp, disp, effic, dist_hh20, rangepos50, dist_ema20, ema_gap, slope20, curv20, exc_asym, failed_up, close_loc; **H4 (8)** r5, effic, vol_exp, dist_hh20, dist_ema20, slope20, ema_gap, close_loc; **M15 (4)** r5, accel, vol_exp, disp; **+1 justified interaction** mtf_div (H1−H4 momentum divergence). All past-only (EWM/rolling/shifted); no future-defined pivots.

## 3. Causal normalization (§11) — verified
Every scaler (mean/std) is **frozen on the DISCOVERY population** and applied unchanged to CONFIRMATION. Explicit check: DISC-vs-full-sample standardized mean drift median 0.027 (max 0.070) confirms real regime drift exists, so full-sample normalization *would* leak; we report the frozen-DISC scaler (CONF AUC 0.502 either way here — small, but the principle is enforced, not assumed).

## 4. Label definitions (§8) + path-aware labels (§9) — outcome-only
Primary label = ≥150p net-bearish over forward 24 H1 bars (`bear>bull`); also computed ≥80/100/200/300p. **Path-aware TRADEABLE_BEAR** = bearish label AND pre-declared adverse excursion (MAE before the low) ≤60p: DISC 0.193 / CONF 0.171. Base rate (≥150p): DISC 0.254 / CONF 0.231. Future returns never enter features.

## 5. Discovery / confirmation split (§10)
Chronological, fixed before fitting: DISCOVERY first 60% (n=6,000, base 0.254, 2021-07→2023-04), CONFIRMATION last 40% (n=4,001, base 0.231, 2023-04→2023-12). Feature set, normalization, model class, hyperparameters, thresholds all frozen on DISCOVERY; CONFIRMATION evaluated once.

## 6. Baselines + models — CONFIRMATION metrics (frozen, evaluated once)
Models: ridge logistic via IRLS (pure-numpy, interpretable). Metrics on CONFIRMATION (base rate 0.231):

| identity | AUC | PR-AUC | Brier | logL |
|---|---|---|---|---|
| B1 PROJECT TREND_DOWN | 0.485 | 0.279 | 0.287 | — |
| B2 recent-return (−r20) | **0.563** | 0.287 | (unscaled) | — |
| B3 volatility (vol_exp) | 0.506 | 0.254 | — | — |
| B4 discrete-bear | 0.459 | 0.212 | 0.256 | — |
| M1 H4-only | 0.460 | 0.226 | 0.186 | 0.564 |
| M2 H1-only | 0.490 | 0.223 | 0.185 | 0.560 |
| M3 H4+H1 | 0.502 | 0.252 | 0.184 | 0.558 |
| M4 H4+H1 ridge(L2=20) | 0.494 | 0.247 | 0.184 | 0.558 |
| M5 H4+H1+M15 | 0.505 | 0.254 | 0.184 | 0.557 |
| M6 ROC-only | 0.470 | 0.210 | 0.184 | 0.555 |
| M7 static-only | 0.497 | 0.228 | 0.184 | 0.557 |
| M8 Markov-state (effic×slope terciles) | 0.525 | — | — | — |

**Every continuous model is ~random (AUC 0.46–0.525), none beats the trivial momentum baseline (0.563) on AUC, and all have Brier ≈ base-rate Brier (0.178) — no calibrated information.** PROJECT TREND_DOWN (0.485) is *below* random: already-declining states are *less* likely to add a new 150p bearish leg (mean reversion) — reconfirming that forcing TREND_DOWN is wrong.

## 7. Probability calibration + buckets (§13, §14) — CONFIRMATION, primary M5
Predicted-probability buckets vs actual bearish rate are **non-monotone through the middle** (actual 0.25/0.20/0.23/0.23/0.26/0.19/0.22/0.27/0.20/0.24/0.24) — the model does **not** order opportunity quality across the bulk. **The single exception is the extreme top bucket:** predicted 0.454–0.642 (n=81) → actual **0.395** (base 0.231, +0.164), avg bearish excursion 128.6p. Calibration is poor overall (top bucket over-predicts, 0.50 vs 0.395), but the *tail ranks*.

## 8. Rare high-confidence states (§15) — DISC-frozen thresholds, monotone tail
Thresholds frozen on DISCOVERY percentiles; CONFIRMATION bearish rate rises **monotonically** with the frozen threshold:

| frozen threshold | CONF n (states) | CONF bearish rate | lift vs base |
|---|---|---|---|
| p ≥ DISC-q0.90 (0.368) | 369 | 0.279 | +0.048 |
| p ≥ DISC-q0.95 (0.414) | 194 | 0.309 | +0.078 |
| p ≥ DISC-q0.98 (0.473) | 56 | **0.411** | **+0.180** (≈3.2 SE) |

This monotone tail response to *pre-frozen* thresholds is the genuine (if thin) predictive signal — the top-2% of states carry a real out-of-sample bearish elevation.

## 9. Feature attribution (§18) — predictive only, not causal
Standardized coefficients (primary M5), largest |w|: h1_ema_gap +0.61, h1_updown_asym −0.48, h1_exc_asym +0.36, h4_slope20 −0.30, h1_rangepos50 +0.29, h1_dist_ema20 +0.27, h1_dist_hh20 +0.20, h1_accel −0.18. Direction reads as "elevated bearish odds from an over-extended, high-in-range, momentum-decelerating up-state." **These are predictive associations on DISCOVERY, not mechanisms** — and because the model is ~random OOS, most are unstable; only the tail composite survives.

## 10. State-transition analysis (§6, M8)
The discrete Markov-state model (DISC-frozen terciles of efficiency × trend-slope → P(bear|state)) reaches CONF AUC 0.525 — the best of the actual models, still barely above random. Rate-of-change features (M6, 0.470) do **not** beat static state (M7, 0.497); state *change* carries no more information than state *level* here.

## 11. Directional gate (§22) — PARTIAL PASS (tail only) → outcome B
The §22 minimums are **mixed:** the model does **not** beat the best baseline on AUC and is **not** calibrated (fails two minimums), but it **does** exhibit a non-trivial, DISC-frozen high-probability bucket with monotone OOS elevation and no cross-year AUC collapse (0.52–0.57). Because a genuine tail signal exists but the model-level discrimination is absent, this is **outcome B, not C — and it is borderline-A.** A skeptic's case for A is legitimate (model AUC random; the tail pass rests on n=56 states / 20 executed trades, a single-year-2023 OOS window, and the most extreme of three thresholds). We classify B because the tail elevation is monotone in *pre-frozen* thresholds and ~3.2 SE — more than nothing — but flag it as a **thin research lead, not an edge.**

## 12. Execution conversion (§23, §24, §25, §28, §29) — UNSOLVED
Frozen-threshold states → short next H1 open, H1 structural stop, RR targets, STRESS cost, one-at-a-time, CONFIRMATION (2023) only:

| frozen bucket | rr | n | WR | avgR | medR | best-5%-rem | best-10%-rem | top-10% share |
|---|---|---|---|---|---|---|---|---|
| p≥q0.90 | 2.0 | 85 | 0.365 | −0.086 | −1.03 | −0.188 | −0.300 | — |
| p≥q0.95 | 2.0 | 44 | 0.432 | +0.107 | −1.03 | +0.018 | −0.079 | 1.67 |
| p≥q0.98 | 2.0 | **20** | 0.50 | **+0.345** | −0.043 | **+0.259** | **+0.165** | **0.569** |
| p≥q0.98 | 3.0 | 20 | 0.40 | +0.335 | −1.03 | +0.197 | +0.044 | 0.882 |
| momentum-short (r20≤DISC-q15) | 2.0 | 101 | 0.386 | +0.005 | −1.01 | −0.097 | −0.210 | 38.4 |

**The top-2% bucket (p≥q0.98) is the first SHORT in this program to show positive, tail-robust out-of-sample execution** (rr2: best-5%- and best-10%-removed both positive, top-10% share <60%). **But execution is NOT solved:** n=20 executed trades, **2023-only**, median R ≈ 0/−1.03 (positive expectancy minority-carried), and it is the strongest of three thresholds (selection risk). The momentum baseline short fails outright (tail lottery). **No candidate is frozen** — the bar for outcome C (robust, multi-year, adequately-powered) is not met.

## 13. SL/TP geometry (§25, §26)
H1 structural invalidation (recent H1 swing high above entry) → median risk ~30–40p; targets ≥150p supported (top-bucket bearish excursion 113–129p). No micro-scalping. Geometry is feasible; **selection power (n, years) is the binding limitation**, not geometry.

## 14. Candidate table (§28) — EMPTY (research lead recorded)
**Zero executable candidates frozen** (outcome B). Recorded lead for independent testing: *"H1+H4 continuous-state ridge-logistic, top-2% DISC-frozen probability (≥0.473), short next H1 open, H1 structural stop, rr2"* — CONF n=20, avgR +0.345, tail-robust, **but single-year-2023 and under-powered.** This is a hypothesis for the Statistician, **not** a candidate.

## 15. Graveyard (§30)
- All continuous logistic models (H4/H1/combined/ridge/ROC/static) — CONF AUC ~random, uncalibrated.
- M15 increment — nil (+0.003). Rate-of-change family — no advantage over static.
- Momentum-short and PROJECT TREND_DOWN — fail execution / below random.
- Middle probability buckets — non-monotone. Recorded in `prob_state.py` / `prob_state2.py`.

## 16. Remaining unexplored price-only classes (§33)
Bounded to compact interpretable models on 2021–2024 with a single 2023 OOS window. Genuinely unexplored: (1) **more OOS years** — the binding limitation here is that the chronological split yields only 2023 out-of-sample; a purpose-built multi-fold temporal CV (still DEV-only) could power the tail test; (2) **richer but still-interpretable models** (monotone GBM with heavy regularization, small causal HMM with >2 states); (3) **conditional tail models** trained only within specific regimes; (4) a **genuinely bearish population** (2011–2013). Each remains price-only.

## 17. CEO recommendation
1. **`PROBABILISTIC_BEARISH_SIGNAL_FOUND_EXECUTION_UNSOLVED` (outcome B).** Continuous/probabilistic state modelling did **not** yield a calibrated, baseline-beating directional model (CONF AUC 0.505, Brier worse than base rate). **But — for the first time in the SHORT program — a rare high-confidence tail (top 2–5% of predicted states) shows a monotone, out-of-sample bearish elevation (0.28→0.31→0.41 vs 0.23 base) under DISC-frozen thresholds, and its top-2% execution is positive and tail-robust.** This is a real, if weak, probabilistic signal in the tail.
2. **It is explicitly NOT an executable edge and NOT a candidate.** The tail pass rests on n=56 states / 20 trades, a single-year-2023 OOS window, and threshold selection — inadequate for promotion or even a frozen candidate. Median R ≈ 0; the positive expectancy is minority-carried. **Execution is unsolved.**
3. **Recommended next step (research, not promotion):** hand the top-2% high-confidence state definition to the **Statistician** for an independently-powered temporal-CV test (multi-fold, DEV-only) to determine whether the tail elevation survives out of a single year. If it does, *then* an execution mandate is warranted.
4. **§31 honored:** no causal narrative. The price models' weakness is **not** claimed as evidence of macro causation; the tail features are **not** claimed to cause declines. Predictive evidence only. **No promotion; broker disabled; DEV-only; no candidate; no CALIB.** The 9 frozen strategies are unaltered; portfolio SHORT remains only frozen `H4-bo-raw-S`.

**Terminal status:** `XAUUSD_PROBABILISTIC_BEARISH_STATE_COMPLETE` · `PROBABILISTIC_BEARISH_SIGNAL_FOUND_EXECUTION_UNSOLVED`. **STOP.**
