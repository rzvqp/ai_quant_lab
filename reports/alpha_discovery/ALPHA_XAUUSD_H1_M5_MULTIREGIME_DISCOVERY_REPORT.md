# ALPHA_XAUUSD_H1_M5_MULTIREGIME_DISCOVERY_REPORT

**Mandate:** `ALPHA-XAUUSD-H1-M5-MULTIREGIME-DISCOVERY-001` · **Date:** 2026-08-21 · **Stat authorization:** commit `b8d0447` (`STAT_XAUUSD_M5_ALPHA_ACCESS_N4_EXCLUDED`).
**Terminal status:** `XAUUSD_H1_M5_MULTIREGIME_DISCOVERY_COMPLETE` · `H1_M5_ALPHA_CANDIDATES_READY_FOR_CEO_REVIEW` — **1 robust candidate, classified `ROBUST_ALPHA_BUT_PROFILE_MISMATCH`**; **NEITHER Profile A nor Profile B is achievable** on this population.
**PROTECTED_M5_ACCESS_COUNT = 0 · N4_M5_TRIGGER_USAGE_COUNT = 0 · ALPHA_ACCESS_2025_PLUS = 0.** Gated loader only; no `read_csv` on `data/market/`; no N4; no shadow_driver.

---

## 0. Headline
- **Integrity gate PASSED** — M5 accessed exclusively through the sanctioned fail-closed loader; DEV/CALIB identities verified (file-SHA + timeline-SHA exact, counts exact, no leak).
- **Neither target profile is achievable.** Across 64 IDs, 8 mechanisms, 5 regimes, both directions, both profile RR bands, **no mechanism reaches Profile A (70–80% WR) or Profile B (45–55% WR).** Target-hit win rate structurally caps ≈17% (rr1.5), because M5-triggered entries with honest tight structural M5 stops are stopped ≈50–65% of the time by noise.
- **One robust, CALIB-confirmed, independent positive-expectancy edge:** **LONG H1 trend-pullback + M5 entry (TREND_UP regime, H1-alone).** But it is a **low-WR / high-payoff / positive-drift** edge → `ROBUST_ALPHA_BUT_PROFILE_MISMATCH` (with the §21 high-RR-lottery caution noted).
- **M5 entry DOES add value** — entry quality + signal filtering (turns a coarse-negative mechanism positive; +0.06…+0.24 R vs coarse) — but its value is **not** in raising win rate.

## 1. Evidence identities (verified)
Gated M5 via `edge_research._common.load('M5', data_split_id='pre_holdout_2025-10-23T09-15-00Z_v1', cutoff='2025-10-23T09:15:00+00:00')`. Loader `flowA_common_v6_context_derived_2026-07-27`, manifest **v2.7.94**, M5 file sha256 **`cbb6eebe…`** (verified by the loader's own fail-closed check).
| population | window (UTC) | bars | ohlc_sha256 | timeline_sha256 |
|---|---|---|---|---|
| DEVELOPMENT | 2021-07-27 15:45 → 2023-12-29 21:55 | **121,949** | `b30912e1…488` | `2a389cd7…131` |
| CALIBRATION | 2024-01-01 23:00 → 2024-06-20 00:40 | **33,309** | `3c170953…deb` | `24e51ef4…` |
DEV+CALIB = 155,258; overlap 0; bars ≥2025-01-01 = **0**; bars past cutoff = **0** (all verified).

## 2. Loader / firewall proof
- Loader returned successfully → manifest content_hash ✓, M5 status `VALIDATED` ✓, file SHA-256 `cbb6eebe…` ✓ (fail-closed).
- **DEV `timeline_sha256` reproduced EXACTLY (`2a389cd7…`)** → DEV row set + order bit-identical to the frozen population. Counts/bounds exact; leak checks all 0.
- `ohlc_sha256` recipe not reproduced across 22 standard serializations, BUT timeline-SHA + file-SHA both matching prove the OHLC *values* are bit-identical → hashing-convention gap, **not** an evidence discrepancy (reported honestly, not faked).
- **Static firewall (my scripts):** 0 `read_csv` on `data/market/`; 0 references to `zone_confirmation`/`market_bus`/`shadow_driver`/`classify_zone`/`ConfirmationSlot` (matches were doc-comments only). H1/M15/H4 built by causal aggregation from the gated M5 (12×/3×/48×), since the H1 loader key is SEALED (`AWAITING_REGIME_MAP`).

## 3. N4 exclusion proof
`N4_M5_TRIGGER_USAGE_COUNT = 0`. No import or call of `code/zone_confirmation.py`, `classify_zone_confirmation`, `market_bus`, `ConfirmationSlot`, or the `confirmation` descriptor anywhere in the campaign code. N4 W=3 thresholds/outputs never touched, never re-derived. `scratch_verify/shadow_driver.py` and `measure_n4_w3_tertiles.py` never invoked.

## 4. Hypothesis registry (64 IDs — ceiling 150)
8 mechanisms × 2 directions × 4 RR (1.5, 2.0, 3.0, 4.0 = sanctioned neighborhood, A={1.5,2}, B={3,4}). Entry = **M5 trigger** (breakout / accept / retest) within 3 H1 of the H1 signal; structural M5-swing stop; RR target exit; max hold 24h; cost tick 0.01, STRESS RT 0.24.

## 5. Family / regime coverage
| regime | mechanisms (edge @ H1) | directions |
|---|---|---|
| TREND_UP / TREND_DOWN | trend_pullback, trend_breakout | LONG + SHORT |
| RANGE | range_reject, **range_sweep** (dedicated Profile-A mean-reversion), range_failbreak | LONG + SHORT |
| TRANSITION | transition_breakout | LONG + SHORT |
| REGIME_INDEPENDENT | ri_displacement, ri_momentum | LONG + SHORT |
DEV H1 regime mix: RANGE 4261 / REGIME_INDEP 2246 / TREND_UP 1692 / TREND_DOWN 1309 / TRANSITION 660.

## 6. H1 primary results
Survivors of fast-falsification (BASE>0, STRESS>0, best-5%-removed>0, n≥50) = **9, ALL LONG**, in TREND_UP and RANGE: `TU-pb` (rr1.5/2/3/4), `TB-bo` (rr3), `RG-rej` (rr2/3/4). Every SHORT, TRANSITION, and REGIME_INDEPENDENT ID failed or was tail-fragile.

## 7. H4 incremental-context results (§11)
On the flagship `TU-pb-L` (rr4): **H1-alone +0.457 (n=59) vs H1+H4-TREND_UP-gated +0.350 (n=23).** The H4 gate cuts trades 61% and **lowers** expectancy → **H4 dependency REMOVED** (per §11). The edge is H1-native.

## 8. M15 incremental results (§12)
Not adopted. The M5 trigger already supplies the entry-timing layer; inserting an M15 confirmation between H1 and M5 only reduces sample without an expectancy case on the surviving family. `H1 → M5` preferred over `H1 → M15 → M5` (no incremental value demonstrated).

## 9. M5 trigger families
breakout (M5 breaks the H1 signal extreme), accept (M5 closes through with body confirmation), retest (M5 returns to the level and closes in-direction). The surviving family uses **breakout** (trend_pullback); accept/retest variants underperformed or failed CALIB.

## 10 & 19. H1-COARSE vs M5-TRIGGER (mandatory M5-value delta)
| candidate | M5 avg_R | COARSE avg_R | **Δ avg_R** | M5 n | COARSE n | Δ WR | read |
|---|---|---|---|---|---|---|---|
| TU-pb-L (rr4) | **+0.457** | +0.220 | **+0.237** | 59 | 109 | −0.01 | M5 filters ~46% of signals, big expectancy lift |
| TU-pb-L (rr3) | +0.406 | +0.250 | +0.156 | 59 | 109 | −0.05 | lift + filter |
| **TB-bo-L (rr3)** | +0.159 | **−0.061** | **+0.221** | 81 | 325 | +0.03 | **M5 turns a negative coarse edge positive** |
| RG-rej-L (rr2) | +0.238 | +0.091 | +0.147 | 54 | 170 | +0.01 | lift |
| RG-rej-L (rr3) | +0.142 | +0.155 | −0.012 | 54 | 170 | 0.00 | no M5 value here |
**Finding:** M5 entry adds value on most mechanisms via **entry quality + signal filtering** (Δ avg_R up to +0.24; decisive for TB-bo), **not** via win rate (Δ WR ≈ 0). Complexity earns its place for the trend-continuation family.

## 11–15. Per-regime results
- **11 TREND_UP (LONG):** `trend_pullback` is the one robust, CALIB-confirmed edge. `trend_breakout` survives DEV but FAILS CALIB (§25).
- **12 TREND_DOWN (SHORT):** all FAIL (gold 2021–2024 DEV window is long-biased/ranging; no down-trend edge).
- **13 RANGE:** `range_reject` survives DEV but is CALIB-fragile (n=8, negative tail); **`range_sweep` (the dedicated high-WR mean-reversion) and `range_failbreak` FAIL.** No robust RANGE edge; RANGE mean-reversion did NOT deliver the hoped Profile-A win rate.
- **14 TRANSITION:** event-sparse / fail (few signals, no edge).
- **15 REGIME_INDEPENDENT:** `ri_displacement` and `ri_momentum` FAIL both directions.

## 16–18. Profile A / Profile B / mismatches
- **16 Profile A candidates: NONE.** Max target-hit WR ≈17% (rr1.5) — nowhere near 70–80%. Even the purpose-built sweep-reversal mean-reversion did not raise WR.
- **17 Profile B candidates: NONE clean.** The high-RR survivors have **3–14% WR**, far below Profile B's 45–55% band — and at rr3–4 they approach the "15–25% high-RR lottery" §21 warns against (actually lower).
- **18 Profile mismatch: `TU-pb-L`** — genuine robust positive expectancy but low-WR/high-payoff geometry.

## 19. (see §10 — combined)

## 20–21. RR / WR distributions
`TU-pb-L` across the RR neighborhood (DEV, STRESS): rr1.5 WR 0.169 / avg +0.194 · rr2 WR 0.136 / avg +0.306 · rr3 WR 0.051 / avg +0.406 · rr4 WR 0.034 / avg +0.457. Higher RR → higher avg_R but lower WR (captures more favorable drift on the ~35% non-stopped trades). No RR band yields a profile-compatible win rate.

## 22 & 23. Structural stop + TP/SL pip distributions (flagship `TU-pb-L`)
Structural stop = M5 swing invalidation (recent-6-M5 low − 0.1·ATR), floored to 0.10·ATR_M5 / 5 ticks — **not** shrunk to manufacture RR.
| rr | med SL pips (P25/P75) | med TP pips (P25/P75) | %TP≥70 | ≥80 | ≥100 |
|---|---|---|---|---|---|
| 2.0 | 35.0 (22/50) | 70.0 (45/100) | 0.51 | 0.42 | 0.25 |
| 3.0 | 35.0 (22/50) | 105.1 (67/151) | 0.73 | 0.64 | 0.54 |
| 4.0 | 35.0 (22/50) | 140.1 (89/201) | 0.86 | 0.80 | 0.64 |
Economic-target regime satisfied at rr3–4 (median TP 105–140 pips; ≥70p for 73–86% of trades).

## 24. Mandatory economics (flagship `TU-pb-L`, DEV, STRESS)
| metric | rr3.0 | rr4.0 | rr2.0 |
|---|---|---|---|
| N | 59 | 59 | 59 |
| win rate (target-hit) | 0.051 | 0.034 | 0.136 |
| intended RR | 1:3 | 1:4 | 1:2 |
| avg realized R | +0.406 | +0.457 | +0.306 |
| median realized R | **−1.05** | −1.05 | −1.01 |
| avg winner / avg loser | +2.45 / −1.10 | +3.08 / −1.10 | +1.75 / −1.09 |
| profit factor | 1.640 | 1.661 | 1.552 |
| gross / BASE / STRESS avg | +0.492 / ~+0.44 / +0.406 | +0.544 / ~+0.47 / +0.457 | +0.393 / ~+0.34 / +0.306 |
| max loss | −1.45R | −1.45R | −1.23R |
| max drawdown (Σ R) | 5.75R | 6.06R | 4.51R |
| trade frequency | 5.8 / 1000 H1 bars | 5.8 | 5.8 |
Median trade is a full stop; expectancy comes from winner/loser asymmetry (2.45R vs −1.1R) + favorable time-exits — **a low-WR trend-following distribution, not a profile fit.**

## 25. Calibration results (§28 — frozen mechanism, out-of-DEV, 2024-01→06-20)
| candidate | CALIB n | CALIB avg_R | CALIB best-5%-rem | verdict |
|---|---|---|---|---|
| **TU-pb-L (rr4)** | 20 | **+0.269** | **+0.074** | **HOLDS (positive, tail-positive)** |
| TU-pb-L (rr3) | 20 | +0.124 | −0.026 | holds (positive, thin tail) |
| TU-pb-L (rr2) | 20 | +0.036 | −0.066 | weak-positive |
| TB-bo-L (rr3) | 20 | **−0.064** | −0.224 | **FAILS CALIB** |
| RG-rej-L (rr2/3) | 8 | +0.03 / −0.09 | neg | inconclusive (n too small) / fails |
Only **`TU-pb-L`** confirms out-of-DEV. No retuning on CALIB was performed.

## 26. Tail robustness (flagship `TU-pb-L`)
rr4: best-1%-rem +0.396, best-5%-rem +0.334, best-10%-rem +0.133 (all positive). rr3: +0.362 / +0.316 / +0.170. **Not a few-trade artifact** — survives removing the top 10%. (rr2: +0.277 / +0.247 / +0.152.)

## 27. Temporal robustness (§27)
`TU-pb-L` DEV by year: **2021 −0.10…−0.17 (n≈14), 2022 +0.69…+0.79 (n≈10), 2023 +0.53…+0.61 (n≈35)**, then CALIB **2024 +0.12…+0.27 (n=20)**. Positive in the **three most recent periods**; negative only in the earliest, smallest-sample year (2021). No months deleted. Bulk of the sample (35/59) is in 2023 and positive — the temporal trend is favorable, though 2021 is a genuine caveat.

## 28. (see §25)

## 29. Independent Alpha-source analysis (§33)
`TU-pb-L` = **LONG H1 trend-pullback + M5 breakout entry (TREND_UP)**.
- vs `H4-bo-raw-S` (SHORT H4 breakdown): opposite direction + timeframe → **INDEPENDENT**.
- vs `H1-B-bo-acc-SHORT` (SHORT): opposite direction → **INDEPENDENT**.
- vs `S5` (LONG M15 NY opening-range breakout): shared long bias but different edge TF (H1 vs M15), mechanism (pullback vs opening-range breakout), and trigger (M5 vs none) → **INDEPENDENT_ALPHA_SOURCE** (distinct construction; S5 validation evidence not accessed).

## 30. Graveyard (do not rediscover)
All SHORT (every regime); TREND_DOWN (all); TRANSITION (sparse/fail); REGIME_INDEPENDENT displacement + momentum (fail both dir); RANGE sweep-reversal + failbreak (fail); `TB-bo-L` (DEV-positive, **CALIB-negative**); `RG-rej-L` (DEV-positive, CALIB-fragile, n=8). Recorded in `h1m5_records.json`.

## 31. Checkpoint history
25 IDs → 8 survivors; 50 IDs → 9 survivors; 64 IDs (final) → 9 survivors, all collapsing to 3 LONG families, of which only trend-pullback survives CALIB. **Early-stopped at 64 of 150:** information gain collapsed — the dedicated Profile-A mechanism (sweep-reversal) failed, all survivors are one direction and cluster into one CALIB-robust family; extending with more cosmetic variants would be uninformative.

## 32. Protected evidence access count
`PROTECTED_M5_ACCESS_COUNT = 0`, `ALPHA_ACCESS_2025_PLUS = 0`, `FINAL_HOLDOUT_ACCESS = 0`, `S5_VALIDATION_EVIDENCE_ACCESS = 0`. Only the gated DEV/CALIB M5 populations were read.

## 33. N4 usage count + integrity verdict
`N4_M5_TRIGGER_USAGE_COUNT = 0`. **INTEGRITY VERDICT: CLEAN.** Loader fail-closed passed; identities verified; no `read_csv` on `data/market/`; no N4 / market_bus-confirmations / shadow_driver; no 2025+; no leakage (all HTF derived by causal aggregation from the gated M5). No `H1_M5_ALPHA_DISCOVERY_INTEGRITY_STOP` condition arose.

## Final candidate portfolio + recommendation to CEO
1. **One research candidate: `TU-pb-L` (H1 trend-pullback LONG + M5 breakout entry, TREND_UP, H1-alone, rr3–4).** `ROBUST_ALPHA_BUT_PROFILE_MISMATCH` — positive DEV+CALIB expectancy (STRESS +0.41/+0.46), tail-robust (best-10%-removed positive), M5 adds value, independent of existing references, economic target ≥70–140 pips. **Caveats (report honestly):** low target-hit WR (3–5% at rr3–4) → **does NOT fit Profile A or B**; median trade is a full stop; maxDD ~6R; 2021 negative (small n); N=59 DEV is modest. Forward to Statistician/Red Team for independent validation **as a low-WR/high-payoff trend edge, NOT as a Profile A/B candidate** (heed §21's high-RR caution).
2. **Structural conclusion for the CEO:** on the gated 2021–2024 XAUUSD population, **neither Profile A (70–80% WR) nor Profile B (45–55% WR) is achievable** with H1-edge/M5-trigger and honest structural stops — target-hit WR caps ≈17% because tight M5 stops are noise-stopped ≈50–65% of the time. **M5 entry's real value is entry quality + filtering, not win rate.** Reaching the high-WR Profile A likely requires either a fundamentally different edge class (not trend/range continuation), or accepting that gold's M5 noise floor makes 70–80% WR structurally unavailable at economic (≥70-pip) targets.
3. **No promotion.** `BROKER_ORDER_SUBMISSION = DISABLED`; no AI Trader / Strategy Catalog / LIVE. Highest status reached = research candidate (`H1_M5_DEEP_RESEARCH` level, profile-mismatched).

**Terminal status:** `XAUUSD_H1_M5_MULTIREGIME_DISCOVERY_COMPLETE` · `H1_M5_ALPHA_CANDIDATES_READY_FOR_CEO_REVIEW` (1, `ROBUST_ALPHA_BUT_PROFILE_MISMATCH`) + structural finding **NEITHER_PROFILE_ACHIEVABLE**. **STOP.**
