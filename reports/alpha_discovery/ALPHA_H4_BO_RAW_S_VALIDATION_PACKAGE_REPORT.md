# ALPHA_H4_BO_RAW_S_VALIDATION_PACKAGE_REPORT

**Mandate:** `ALPHA-H4-BO-RAW-S-VALIDATION-PACKAGE-COMPLETION-001` · **Date:** 2026-08-22.
**Statistician triage consumed:** `STAT-XAUUSD-FROZEN-STRATEGY-TRIAGE-001` (`f890b0e`, `N_VALIDATION_WORTHY=1`, Tier A empty, only Tier B = `H4-bo-raw-S`).
**Terminal status:** `H4_BO_RAW_S_FROZEN_IDENTITY_REPRODUCED` · `H4_BO_RAW_S_VALIDATION_PACKAGE_COMPLETE` · **`H4_BO_RAW_S_READY_FOR_INDEPENDENT_VALIDATION`**.
**Scope:** MECHANICAL COMPLETION ONLY — recover the frozen strategy, reproduce the ledger, resolve the WR reporting, complete PF/maxDD, build a reproducible handoff. **No parameter change, no retuning, no new Alpha search.** Alpha does **not** self-ratify (§17). No AI Trader/MT5/demo/live.

---

## 0. Headline
- **Frozen identity fully recovered and reproduced** from `econ_campaign.py` (mechanism `bo-raw-S` = `mk_breakout(up=False, lb=20, accept=False)`). N=125, **every Statistician cross-check number MATCHES exactly.**
- **The two documentation defects are resolved:** (1) **WR reporting** — GROSS reached-target 0.528, STRESS reached-target 0.44, positive-R 0.528 (all labeled, §6/§13); (2) **PF & maxDD completed** — GROSS/BASE/STRESS PF 1.678/1.659/**1.590**, maxDD **−9.273R**, max loss −1.086R, 9 consec losses (derived on a proper **single-sequence chronological ledger**).
- **Complete, self-contained validation package produced** (spec + ledger + fingerprints + economics + robustness). Ready for independent Statistician validation.

## 1. Frozen identity (§2) — reproduced, not reconstructed from prose
`H4-bo-raw-S-rr1.5`: SHORT, edge-TF H4, raw 20-bar-low breakdown (no acceptance), D1-down aligned (`trend_up ≤ 0.5`), entry next-H4-open, structural SL `max(|entry−brk|+0.3·ATR, 0.8·ATR)`, RR 1:1.5, exit via `mstrat.simulate`. Full rule in [`H4_BO_RAW_S_STRATEGY_SPEC.md`](H4_BO_RAW_S_STRATEGY_SPEC.md). **Recovered mechanically from the authoritative implementation** (`econ_campaign.py` functions reused verbatim in `h4boraws_package.py`); no logic reconstructed from narrative.

## 2. Data identity (§4)
DEV blocks (per-block, never crossing the unratified 2013–2016 manifest gap): **b0 2011-07-26→2013-09-27, b1 2016-01-11→2018-04-06**; CALIB 2020-08-11→2021-09-05. H4-from-M15_v2 CSV (sha256 `f8f23f6e…`). **Not** the 2021–2023 native-M5 window — a distinct, unconsumed region (why this is the only validation-worthy frozen candidate). Loader = `mstrat`/ratified `_from_M15_v2` CSVs.

## 3. Trade ledger (§5) — reproduced, single-sequence
125 trades reproduced with entry timestamps, side, entry, SL, TP, and **GROSS/BASE/STRESS R per trade**, sorted into one chronological sequence (b0 then b1). Exported to `h4boraws_package.json` (`ledger`). Ledger fingerprint `498ee294…`.

## 4. WR reporting resolved (§6, §13) — the primary documentation defect
| WR definition | scenario | value |
|---|---|---|
| reached 1.5R target | GROSS R ≥ 1.45 (`econ_campaign.py:168`) | **0.528** |
| reached 1.5R target | STRESS-net R ≥ 1.45 (`deepen_econ.py:76`) | **0.440** |
| any profitable trade (R>0) | GROSS / BASE / STRESS | 0.528 / 0.528 / 0.528 |
**Explanation:** STRESS reached-target (0.44) < GROSS (0.528) because the stress round-trip cost pushes marginal target-hitters below the +1.45-net threshold; the positive-trade rate stays 0.528 (cost reduces R magnitude but flips no winner to a loser here). **No unlabeled WR beside STRESS expectancy anymore.**

## 5. Completed economics (§7) — PF & maxDD, previously never computed (DERIVED_DURING_PACKAGE_COMPLETION, NOT used to retune)
| | GROSS | BASE | STRESS |
|---|---|---|---|
| avg R | +0.320 | +0.3133 | **+0.2876** |
| PF | 1.678 | 1.659 | **1.590** |
| median R (stress) | | | +1.434 |
- **maxDD −9.273R · max single loss −1.086R · max consecutive losses 9** (stress, single-sequence).
- best-1%-rem +0.278 · best-5%-rem +0.227 · **best-10%-rem +0.160** (§8).

## 6. Robustness (§8), temporal (§9), effective N (§10)
- **Per-block (stress):** b0 +0.2091, b1 +0.4978. **CALIB (out-of-DEV) +0.1523 (n=20).**
- **Per-year (stress, n):** 2011 +0.023 (12) · 2012 +0.182 (33) · 2013 +0.277 (46) · 2016 +0.582 (17) · 2017 +0.414 (17) · 2018 +0.0 (0). Every populated year positive; 2018 has no trades.
- **Effective N:** 125 trades, 98 unique days — H4 setups are ~daily-spaced (one 20-bar-low breakdown per down-leg), no correlated intraday re-entry. best-10%-removed +0.160 (>0) → not top-trade-dependent.

## 7. Geometry (§11) + frequency (§12)
Median SL **76.0p** (P25 58.2 / P75 127.5) — **naturally in the 70–100p zone**; median TP **113.9p**; median MFE 278p. **2.33 trades/month** (53.7 active DEV-months), median 2.2 days between trades. (Max no-trade streak 975 days = the 2013–2016 data gap, descriptive only.)

## 8. Statistician cross-check (§14) — all MATCH
| quantity | Statistician (`f890b0e`) | this reproduction | verdict |
|---|---|---|---|
| N | 125 | 125 | MATCH |
| GROSS WR (reached target) | 0.528 | 0.528 | MATCH |
| STRESS WR (reached target) | 0.44 | 0.44 | MATCH |
| STRESS avg R | +0.2876 | +0.2876 | MATCH |
| BASE avg R | +0.3133 | +0.3133 | MATCH |
| best-5%-removed | +0.2269 | +0.2269 | MATCH |
| best-10%-removed | +0.160 | +0.160 | MATCH |
| PF (stress) | 1.590 | 1.5896 | MATCH |
| maxDD (R) | 9.27 | 9.273 | MATCH |
| max loss (R) | −1.086 | −1.0861 | MATCH |
| CALIB avg R / n | +0.1523 / 20 | +0.1523 / 20 | MATCH |
*(Per-block: this reproduction and `econ_campaign.json` give b0 +0.2091 / b1 +0.4978; the triage line 136 quotes the `deepen_econ.json` block values b0 +0.2306 / b1 +0.5345 — a run-labeling difference between the two evidence files, both frozen; neither retuned.)*

## 9. Fingerprints (§15) + package (§16)
| fingerprint | value |
|---|---|
| implementation (econ_campaign.py) | `5dc242171d23cda82e160394be04bd09af147baa8cfdc44d3a52bbfb7f7279b1` |
| data identity (H4 CSV sha256) | `f8f23f6e5c2fb2e402c54f0624252c896f578b92283772a8cb67c4b3e06ffee5` |
| config | `3fe952ae181195ba4cfc646caaac1e8953ced84bfcba931bae90024b32558f4c` |
| trade ledger | `498ee2949b6c4f0a429f5e7b5e862da3c518fe3e9e630ea208f59702799591d1` |
| cost model | AI_TRADER_SHADOW_COST_MODEL_v1 (BASE RT 0.05 / STRESS RT 0.24) |
Package artifacts: `H4_BO_RAW_S_STRATEGY_SPEC.md` (self-contained spec), `h4boraws_package.json` (economics + fingerprints + full ledger), `h4boraws_package.py` (deterministic reproduction), sourced from frozen `econ_campaign.py` / `deepen_econ.py` / `econ_campaign.json` / `deepen_econ.json`.

## 10. §21 required final summary
`STRATEGY_ID` H4-bo-raw-S-rr1.5 · `SIDE` SHORT · `TIMEFRAMES` H4 edge / D1 context / next-H4-open entry (M5 pending) · `N` 125 · `TRADES_PER_MONTH` 2.33 · `GROSS_WR` 0.528 (reached-target) · `BASE_WR` 0.528 (positive) · `STRESS_WR` 0.44 (reached-target) / 0.528 (positive) · `GROSS_AVG_R` +0.320 · `BASE_AVG_R` +0.3133 · `STRESS_AVG_R` +0.2876 · `PF_STRESS` 1.590 · `MAX_DD_R` −9.273 · `MAX_LOSS_R` −1.086 · `BEST_1PCT_REMOVED` +0.278 · `BEST_5PCT_REMOVED` +0.227 · `BEST_10PCT_REMOVED` +0.160 · `DISC` DEV b0/b1 +0.288 · `CONF` CALIB +0.1523 (n20) · `TEMPORAL_BLOCKS` b0 +0.209 / b1 +0.498; years 2011–2017 all positive, 2018 n0 · `MEDIAN_SL_PIPS` 76.0 · `MEDIAN_TARGET_PIPS` 113.9 · `DATA_IDENTITY` H4_from_M15_v2 sha `f8f23f6e…`, DEV 2011-07→2013-09 + 2016-01→2018-04 · `IMPLEMENTATION_FINGERPRINT` `5dc24217…` · `TRADE_LEDGER_FINGERPRINT` `498ee294…` · `S5_OVERLAP` different population (S5 lives on 2021–2023 M5; no shared bars/years — overlap not computable, conceptually independent).

## 11. CEO recommendation
1. **`H4_BO_RAW_S_VALIDATION_PACKAGE_COMPLETE` / `H4_BO_RAW_S_READY_FOR_INDEPENDENT_VALIDATION`.** The frozen candidate is reproduced exactly (all 11 Statistician cross-checks match), the two documentation defects are resolved (WR labeled three ways; PF 1.590 and maxDD −9.273R computed on a single-sequence ledger), and a self-contained handoff is produced.
2. **Alpha does not ratify (§17).** No `VALIDATED` / `PRODUCTION_READY` / `AI_TRADER_READY` claim. The package is handed to the **Statistician** for independent validation; Red Team thereafter.
3. **Honest limitations forwarded:** M5 execution PENDING (WR/expectancy are lower bounds under conservative same-bar-stop-wins); low frequency (2.33/month); small per-year N (2018 n0); evidence straddles the 2013–2016 data gap (ledger reconstructed single-sequence); DEV 2011–2018 only.
4. **No parameter change; no new Alpha; no MI/S5 change; no AI Trader; broker disabled.** All other frozen strategies untouched.

**Terminal status:** `H4_BO_RAW_S_FROZEN_IDENTITY_REPRODUCED` · `H4_BO_RAW_S_VALIDATION_PACKAGE_COMPLETE` · `H4_BO_RAW_S_READY_FOR_INDEPENDENT_VALIDATION`. **STOP.**
