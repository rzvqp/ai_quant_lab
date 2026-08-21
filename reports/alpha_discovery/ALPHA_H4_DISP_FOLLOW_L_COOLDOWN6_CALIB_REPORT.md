# ALPHA_H4_DISP_FOLLOW_L_COOLDOWN6_CALIB_REPORT

**Mandate:** `ALPHA-H4-DISP-FOLLOW-L-COOLDOWN6-CALIB-001` · **Date:** 2026-08-21 · **Frozen from commit:** `696e46b`.
**Terminal status:** **`H4_DISP_FOLLOW_L_COOLDOWN6_CALIB_FAIL`.** The frozen executable policy **loses its edge and violates multiple hard robustness gates on CALIBRATION** — Gate I concentration, best-10%-removed, negative median, and (decisively) **negative incremental value vs PROJECT TREND_UP**. No rescue attempted (§5); a repaired version would require a new ID + new mandate.
**One frozen pass only. K=6 only. No retuning. DEV untouched. No V1/protected/2025+/N4/raw-read.**

---

## 0. Headline
- **The disp+follow-through SIGNAL remains DEV-confirmed** (Statistician `c028eb2`; not re-litigated here). **What failed is the executable `COOLDOWN6` policy on CALIB** — the DEV eventization "fix" did not generalize.
- **CALIB reverted to the failure mode §8 warned against:** positive mean (+0.092) but **negative median (−0.508)** driven by a few winners (top-10% share **162.9%**; best-10%-removed **−0.064**).
- **Decisive:** on CALIB the candidate is **negatively incremental vs PROJECT TREND_UP** (+0.092 vs **+0.403** → **−0.311**). Gold trended strongly in H1-2024; plain regime exposure beat the "specific" signal. The DEV incremental edge (+0.249) **reversed sign**.
- **Verdict: `CALIB_FAIL`** (multi-gate). Honest sample caveat: N=10 makes percentages unstable — but the failure is directionally unambiguous (negative median, below-baseline, one-month concentration), not merely underpowered; per §7 I do **not** silently waive the gate.

## 1. Frozen identity + fingerprints (§1)
`H4-DISP-FOLLOW-L-COOLDOWN6`, recovered mechanically from `eventize_dispfollow.py` @ `696e46b`, unchanged: H4 displacement `close[d]−open[d] > 1.0·ATR14[d]`; follow-through `close[d+1] > close[d]`; stop `min(low[d−3…d+1]) − 0.15·ATR[d+1]`; **entry OPEN[d+2]** (causal floor); target `entry + 1.5·risk` (floor `max(5·tick, 0.10·ATR)`); walk d+2…d+49 stop-before-target; **one-position-at-a-time + 6-H4-bar post-exit cooldown**; cost tick 0.01 / STRESS 0.24. **K=6 permanently frozen** — no K3/K9/K12/K18 on CALIB (§2).

## 2. Causal chronology invariant (§3)
d: displacement (closed bar). d+1: follow-through observed only after CLOSE[d+1]. **d+2: earliest legal entry OPEN[d+2].** `OPEN[d+1]` is lookahead, permanently forbidden — not used.

## 3. CALIB population identity (§4)
Gated M5 CALIB **2024-01-01 23:00Z → 2024-06-20 00:40Z**, 33,309 M5 bars, ohlc_sha256 `3c170953…`, timeline_sha256 `24e51ef4…` (Statistician-frozen; verified in the H1→M5 integrity gate). Causally aggregated to **H4: 725 CALIB bars, 2024-01-02 → 2024-06-19**. No 2025+; no V1; no independent-validation population; no N4; no raw `read_csv`.

## 4. CALIB economics (§6) — one frozen pass, STRESS
| metric | value |
|---|---|
| N | **10** |
| win rate | 0.40 |
| BASE expectancy | +0.098 |
| **STRESS expectancy** | **+0.092** |
| PF | 1.182 |
| **median R** | **−0.508** |
| avg winner / avg loser | +1.493 (n=4) / −0.842 (n=6) |
| maxDD / max loss | 2.01R / −1.014R |
| median MAE / MFE | 297p / 368p |
| median hold | 22 H4 bars |
| nominal / effective RR | 1.5 / 1.5 |
Mean is barely positive; **median is −0.508** — 6 of 10 trades lose; the mean rides on 4 winners.

## 5. Tail concentration (§7) — Gate I FAIL
| metric | CALIB |
|---|---|
| top-1% / 5% / **10% profit share** (net-profit denominator) | 162.9 / 162.9 / **162.9%** |
| best-1% / 5% / **10%-removed** | −0.064 / −0.064 / **−0.064** |
With N=10, top-10% = the single best trade, which is **162.9% of net profit** — i.e. removing it turns the policy negative (best-10%-removed −0.064). **Gate I (≤60%) FAILS.** Per §7 the small N makes the exact percentage unstable, reported honestly — but the qualitative failure (edge concentrated in ~1 trade; negative once removed) is unambiguous, not an artifact to waive.

## 6. Median trade (§8) — reverted to the bad profile
CALIB median R **−0.508** vs DEV **+0.413**. This is precisely the reversion §8 flagged: **positive mean + negative median + few large winners.** The DEV policy's broad-based character (median +0.413) did **not** survive out-of-DEV.

## 7. PROJECT TREND_UP comparison (§9) — negative incremental (decisive)
PROJECT TREND_UP = `ema20>ema50 AND effic>0.30`, identical geometry.
| | CALIB avg R | n |
|---|---|---|
| candidate `COOLDOWN6` | **+0.092** | 10 |
| PROJECT TREND_UP baseline | **+0.403** | 138 |
| **incremental** | **−0.311** | — |
On CALIB, gold's strong H1-2024 uptrend made plain regime exposure highly profitable (+0.403), and the displacement+follow-through candidate **underperformed it by −0.311.** The DEV incremental edge (+0.249) **reversed sign**. `INCREMENTAL_ALPHA_OVER_PROJECT_TREND_UP` is **NOT** maintained — the required §9 invariant fails.

## 8. Economic geometry (§12) — geometry holds, edge does not
median SL **325 pips**, median TP **488 pips**; TP P25/P50/P75 = 372 / 488 / 583 pips; %TP ≥80 = 1.00, ≥100 = 1.00, ≥150 = 1.00, ≥200 = 1.00, ≥300 = 0.90, ≥400 = 0.60. Large-move geometry reproduces on CALIB — confirming the *geometry* is stable; the *edge* is what failed.

## 9. Temporal (§11) — one-month concentration
CALIB is a single ~5.5-month segment (2024). Monthly (N per cell too small to over-interpret, reported per §11): **2024-02 (n3, −0.18), 2024-03 (n2, +1.49), 2024-04 (n1, −1.0), 2024-05 (n2, +0.24), 2024-06 (n2, −0.51).** The positive mean is **entirely March 2024** (the 2 large winners). Four of five months are net-negative or flat. No temporal breadth.

## 10. DEV vs CALIB (§13) — labeled separately, DEV recomputed-free
| metric | DEVELOPMENT | CALIBRATION |
|---|---|---|
| N | 34 | 10 |
| STRESS avg R | +0.264 | +0.092 |
| **median R** | **+0.413** | **−0.508** |
| PF | 1.662 | 1.182 |
| best-10%-removed | +0.135 | **−0.064** |
| **top-10% share** | **53.2%** | **162.9%** |
| **incremental vs PROJECT TREND_UP** | **+0.249** | **−0.311** |
Every quality dimension reverses: broad→concentrated, positive-median→negative-median, incremental-positive→incremental-negative. DEV was not recomputed on combined data; CALIB only evaluated.

## 11. CALIB VERDICT (§14)
```
H4_DISP_FOLLOW_L_COOLDOWN6_CALIB_FAIL
```
Per §14, `CALIB_FAIL` is returned because the frozen candidate **violates multiple hard robustness gates** on CALIB: (a) **Gate I** top-10% concentration 162.9% > 60%; (b) **best-10%-removed −0.064 < 0**; (c) **median R negative (−0.508)**, reverting to the concentrated profile; (d) **incremental vs PROJECT TREND_UP negative (−0.311)** — the §9 invariant fails, the candidate loses to plain regime beta. The barely-positive mean (+0.092) is one month (March). This is not `CALIB_WEAK` (which would require staying *above* baseline while underpowered); the candidate is *below* baseline with a negative median — a genuine edge failure, not a small-sample technicality (though N=10 is small and reported as such per §7).

## 12. Consequences (§5, §14, §15) — no rescue
- **This exact candidate (`H4-DISP-FOLLOW-L-COOLDOWN6`) fails.** No threshold/cooldown/SL/TP/hold changes, no filter additions, no regime changes, no rescue (§5). Any repaired variant needs a **new ID + new research mandate + new evidence treatment.**
- **The disp+follow-through SIGNAL is unaffected** — it remains `SIGNAL_ALPHA_CONFIRMED` on DEV (Statistician). What this mandate establishes: **that signal does not (via the COOLDOWN6 event policy) generalize into a CALIB-robust executable edge.** The raw signal is real but small-N, and its executable form did not survive out-of-DEV.
- **No validation claims** (§15): this is not `INDEPENDENT_VALIDATION_PASS` / `VALIDATED_STRATEGY` / `AI_TRADER_READY` / `LIVE_READY`. Nothing promoted; broker disabled; no live.
- **Portfolio impact:** the CALIB-passing candidates from other mandates (`TR-H4-rng2trend_disponly-L`, `IR-DIR-L-mid`, `HR-TU-pb-L`) are unaffected. The dispaccept lineage now stands as: signal confirmed, **no executable policy CALIB-survivor**.

**Terminal status:** `H4_DISP_FOLLOW_L_COOLDOWN6_CALIB_FAIL`. **STOP.**
