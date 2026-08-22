# ALPHA_XAUUSD_LONDON_PLH_CAUSAL_FEATURE_MAP_REPORT

**Mandate:** `ALPHA-XAUUSD-LONDON-PLH-CAUSAL-FEATURE-MAP-001` · **Date:** 2026-08-22 · **Parent lineage:** commit `50b099d` (unchanged).
**Terminal verdict:** `PLH_FEATURE_MAP_COMPLETE` · **`PLH_STABLE_FEATURES_FOUND`** — but exactly **one** stable feature (spatial, not anatomy); classifier-readiness is **univariate only** (see §15/rec).
**Scope:** feature-mapping ONLY (no classifier §28, no execution §30, no thresholds §29, no volume §5). Price-only, native-M5, DEV-only; no CALIB/V1/2025+/N4. Univariate characterization of what distinguishes CLEAN (A) from NEW_HIGH_FIRST (B) / CONTINUATION (C). No promotion; broker disabled.

---

## 0. Headline
- **One strong, stable, causal discriminator exists: `plh_minus_asiahigh`** — the signed distance between the Pre-London-High and the Asia High. When PLH sits **far below** Asia High, sweeps reverse cleanly; when PLH is **at/above** Asia High, they continue bullish. Monotone: **P(A) 0.87 → 0.48 → 0.31 → 0.05** across four bins; DISC AUC 0.12 / CONF AUC 0.23; direction consistent 2021/2022/2023; robust to ATR normalization; position-independent by construction.
- **Every sweep-anatomy, velocity, and path feature FAILS** DISC→CONF and/or position control (wick ratio, close location, sweep excursion, approach velocity, time-above-PLH, failed extension, early downside — all sign-flip or collapse to ~0.5 when position-adjusted).
- **Interpretation:** the prior WEAK Pre-London-High edge is *explained* by level geometry — clean reversals are the subset where a **lower** liquidity level (PLH) is swept while a **higher** level (Asia High) remains overhead as context. "What a clean path looks like before the future is known" = **a Pre-London-High well below the Asia High.**

## 1. Parent lineage + exact reproduction (§2, §3)
Recovered mechanically from `frank_london.py` (`50b099d`), **unchanged**: Pre-London window (London-local 07:00–08:00), PLH = max native-M5 high therein, London research window (08:00–10:00), sweep = first M5 `high > PLH`, one sweep/day, 4-class labels (objective = Asia mid). **Reproduced N = 133, unique days = 133.** No parent retuning.

## 2. Timezone/DST + event identity (§7)
DST-aware `tz_convert` (Europe/London, Europe/Berlin — verified year-round Berlin = London+1h, transitions correct). One event row per canonical parent sweep (fields: trading_day, sweep bar index, PLH, sweep_high, session, year, split). No duplicate rows.

## 3. Four-class balance (§6)
A clean 0.368 · B new-high-first 0.278 · C continuation 0.346 · D stalled 0.008. Primary discrimination **A vs B+C** (D dropped, n≈1). Chronological **PLH_FEATURE_DISCOVERY / PLH_FEATURE_CONFIRMATION** split (60/40 by sweep time), frozen before ranking.

## 4. PRIMARY FEATURE MAP — `plh_minus_asiahigh` (§17) — the one stable feature
| PLH − AsiaHigh (pips) | N | **P(A clean)** | P(B) | P(C) |
|---|---|---|---|---|
| < −40 (PLH far below Asia High) | 23 | **0.870** | 0.087 | 0.043 |
| [−40, −20) | 31 | 0.484 | 0.290 | 0.226 |
| [−20, 0) | 39 | 0.308 | 0.410 | 0.282 |
| ≥ 0 (PLH at/above Asia High) | 40 | **0.050** | 0.250 | **0.675** |
Monotone and economically coherent. Class medians: A −32.6p / B −12.2p / C +4.4p. **DISC AUC 0.12, CONF AUC 0.23** (both far from 0.5, same direction). Per-year AUC 0.07 / 0.17 / 0.23 — **direction consistent across all three years** (magnitude softens but never crosses 0.5). ATR-normalized variant equally stable (0.11 / 0.22). **Causal** (two frozen levels known at E0), **position-independent** (fixed-level geometry, not a path variable), full room remaining at E0.

## 5. E0 static feature map — everything else fails DISC→CONF
| feature | DISC AUC | CONF AUC | stable | note |
|---|---|---|---|---|
| **plh_minus_asiahigh** | 0.12 | 0.23 | **YES** | the one stable feature |
| plh_minus_asiahigh_atr | 0.11 | 0.22 | YES | same feature, ATR-normalized |
| dist_asia_mid | 0.06 | 0.15 | (position) | trivial proximity-to-target; inversely tied to remaining room — **excluded** |
| sweep_excursion / _atr | 0.47/0.49 | 0.41/0.40 | no | §5 sweep size: no info |
| prelondon_range | 0.50 | 0.41 | no | |
| upper_wick_ratio | 0.51 | 0.59 | no | **§18 wick hypothesis NOT supported** |
| body_ratio / close_loc | 0.52/0.47 | 0.51/0.39 | no | |
| bear_body_E0 / range_expansion | 0.56/0.51 | 0.59/0.57 | no | borderline, DISC≈0.5 |
| disp_5/10/15/30m | 0.44–0.51 | 0.41–0.42 | no | **§12 velocity NOT supported** (2021-only: disp_30m 0.75/0.42/0.40) |
| approach_eff | 0.56 | 0.41 | no | flips |

## 6. Landmark path features E1/E2/E3 (§15, §16, §19) — fail DISC→CONF + position control
Undecided-conditioned; AUC(DISC|CONF) and **position-adjusted** (median AUC within tertiles of distance-below-sweep, §25):
| feature | E1 (n38) | E2 (n31) | E3 (n25) | position-adjusted |
|---|---|---|---|---|
| net_downside | 0.31/0.83 | 0.58/0.65 | 0.42/0.83 | **collapses (0.50–0.52)** |
| max_downside | 0.19/0.80 | 0.33/0.70 | 0.35/0.83 | 0.47–0.58 |
| last_bear | 0.31/0.83 | 0.95/0.50 | 0.40/0.72 | 0.50–0.86 (n17 overfit) |
| closes_above_plh (time-above) | 0.69/0.28 | 0.65/0.55 | 0.70/0.44 | **0.48–0.53 (no info)** |
| extend/failed_ext/dn_up_ratio | sign-flip | sign-flip | sign-flip | ~0.50 |
**All path features sign-flip between DISC and CONF and/or collapse to ~0.5 under position control** — the apparent "early downside predicts clean" is largely a *position artifact* (price already farther down). The position control (§25) did its job: it isolated the one genuine, non-position signal (the static level geometry) and killed the rest.

## 7. Two-dimensional feature map (§20)
`plh_minus_asiahigh × close_loc → P(A)`:
| | close_loc < 0.7 | close_loc ≥ 0.7 |
|---|---|---|
| **PLH ≪ AsiaHigh (< −20)** | 0.652 (n23) | 0.645 (n31) |
| PLH ≥ −20 | 0.282 (n39) | 0.075 (n40) |
Close-location adds **nothing** within the PLH≪AsiaHigh group (0.652 vs 0.645) — the entire discriminative content is the spatial separation. (Other requested maps — velocity×failed-extension, time-above×downside — showed no class separation and are in the graveyard.)

## 8. Year-by-year + timeliness (§23, §26)
Year N / base P(A): 2021 N27 / 0.407 · 2022 N47 / 0.383 · 2023 N59 / 0.339. The feature's direction is stable across all three (§4). **Economic timeliness:** `plh_minus_asiahigh` is knowable at **E0** with 0% path consumed and full room to Asia mid — it does not depend on waiting; the path landmarks (E1–E3) add no generalizing information.

## 9. Position controls (§25) — mandatory, applied
`plh_minus_asiahigh` is a static two-level geometry, structurally orthogonal to how far price has travelled — it needs no adjustment and retains its effect. The E1–E3 path features were explicitly stratified by distance-below-sweep and **lost their effect** (median tertile AUC ≈ 0.50), confirming they were position-driven.

## 10. Answers to §31 (compact)
1 **`plh_minus_asiahigh`** differs most (A −33 / B −12 / C +4) · 2 **PLH↔AsiaHigh YES** (the one stable feature) · 3 wick NO · 4 close-loc NO · 5 sweep-excursion NO · 6 velocity NO · 7 deceleration NO · 8 time-above NO · 9 failed-extension NO · 10 early-downside — position artifact (collapses) · 11 survive DISC→CONF: **only plh_minus_asiahigh (+ATR)** · 12 survive all years: **plh_minus_asiahigh** · 13 survive position adjustment: **plh_minus_asiahigh** (static; path features do not) · 14 strongest landmark w/ room: **E0** (static geometry, full room) · **15 enough for a classifier? NO — one stable feature only; a multivariate classifier is not justified.**

## 11. Stable ranking / graveyard / limitations
- **Stable (1):** `plh_minus_asiahigh` (+ ATR variant) — strong, monotone, DISC→CONF + all-years consistent, position-independent, timely (E0).
- **Excluded (position-confounded):** `dist_asia_mid` (proximity-to-target; less room).
- **Graveyard (all failed DISC→CONF / position control):** wick ratio, close location, body ratio, sweep excursion, pre-London range, approach velocity (disp_5–30m, efficiency, acceleration), range expansion, time-above-PLH, failed extension, all E1–E3 downside/extension path features. Recorded in `plh_feature_map.py`.
- **Limitations:** the strongest cell (PLH < −40) is n=23; total parent N=133 (partial-2021 from 2021-07). One stable feature ≠ a rich feature set. Objective is Asia-mid (~22p room), a session-mean-reversion target, not a large clean move.

## 12. CEO recommendation
1. **`PLH_STABLE_FEATURES_FOUND` — but a single, static, spatial feature.** The Pre-London-High clean-reversal edge is **causally explained by level geometry**: `plh_minus_asiahigh` (how far PLH sits below Asia High) is a strong, monotone, DISC→CONF-stable, all-years-consistent, position-independent discriminator (P(A) 0.87 when PLH ≪ Asia High → 0.05 when PLH ≥ Asia High). This is the cleanest single feature the SHORT program has surfaced and it sharpens the prior WEAK finding into a mechanism.
2. **NOT ready for classifier research (§15).** The sweep-anatomy, velocity, and path-response feature families **all failed** DISC→CONF and position control — there is no *second* generalizing variable to combine. A "classifier" here would be a univariate threshold on `plh_minus_asiahigh`, which §29 forbids under a feature-mapping mandate. **I therefore do NOT emit `PLH_FEATURE_SET_READY_FOR_CLASSIFIER_RESEARCH`.**
3. **Recommended next step:** hand the single feature `plh_minus_asiahigh` to the **Statistician for independent audit** (is the PLH≪AsiaHigh → clean effect robust at adequate N, and does its clean-path advantage survive the new-high-first path problem?), rather than authorizing multivariate classifier work. The honest scientific result is a *level-geometry characterization*, not a rich multivariate feature set.
4. **No promotion; no classifier; no execution; broker disabled; DEV-only; no CALIB.** Parent (`50b099d`) and all frozen strategies untouched; portfolio SHORT still only frozen `H4-bo-raw-S`.

**Terminal verdict:** `PLH_FEATURE_MAP_COMPLETE` · `PLH_STABLE_FEATURES_FOUND` (one stable spatial feature; not classifier-ready). **STOP.**
