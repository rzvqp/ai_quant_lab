# ALPHA_HISTORICAL_REREVIEW_WAVE2_REPORT + DEVELOPMENT POPULATION INTEGRITY RECOVERY

**Mandate:** `ALPHA-HISTORICAL-REREVIEW-WAVE2-001` · **Date:** 2026-08-21 · **Status:** `ALPHA_HISTORICAL_REREVIEW_WAVE2_COMPLETE` · `DEVELOPMENT_POPULATION_INTEGRITY_RECONCILED` · `READY_FOR_CEO_ALPHA_PORTFOLIO_DECISION`.
**VALIDATION_ACCESS_COUNT = 0. FINAL_HOLDOUT_ACCESS_COUNT = 0.** Manifest-gated evidence only; exact frozen specs; no retuning.

## 0. Integrity finding — OWNED and reconciled
VE (`VE-ALPHA-HISTORICAL-HTF-CONTEXT-MIGRATION-001`, commit `ed57853`) correctly identified that my **Historical Re-Review Wave 1 (`0a73877`) and S5+Candidate-001 Deep Research (`661bb8f`) used a non-manifest-gated 160,888-bar DEVELOPMENT population** — mechanically confirmed: both scripts call `mstrat.load()` and slice `dt<2018-05` with **no discovery-block filtering**, silently including **~54,118 bars (~34%) from the unratified 2013-09-27 → 2016-01-11 gap**. This is material, not bookkeeping. All affected results are re-evaluated below on the correct population. (The Stage-1 campaign `475d6b0` used the properly-gated `edge_research._common.load()` → clean.)

## 1. VE migration identity (verified before use)
`ed57853`, `code/htf_context_historical.py`, **25/25 tests PASS** (re-run and confirmed). Causal H1/H4 (EMA20>EMA50 on each HTF's own closes, `mtf._ind` frozen), causal PDH/PDL (last fully-closed D1, `s1.load_s1` frozen), same-discovery-block guard (no cross-gap bridging), hash-verified against `config/split_manifest.json`, deterministic, PDH/PDL 100% exact on overlap. Consumed via `load_mstrat_historical()`; HTF context not recreated independently.

## 2. Authoritative DEVELOPMENT population (bound before scoring)
| field | value |
|---|---|
| loader | `htf_context_historical.load_mstrat_historical()` (VE `ed57853`), manifest `config/split_manifest.json` |
| discovery blocks (DEV) | block0 `2011-07-26 → 2013-09-27` + block1 `2016-01-11 → 2018-04-06` |
| **DEV bars** | **105,255** (block0 52,404 + block1 52,851) — matches VE's ~105,254 |
| OHLC sha256 (first 16) | `47c9b16ba77bcbaf` |
| CALIBRATION (block2) | `2020-08-11 → 2021-09-05`, 25,237 bars (not used for scoring) |
| VALIDATION (block3) / SEALED | never loaded/evaluated |
Evaluation is **per-block** (block0 and block1 run separately, results combined) → the 2013→2016 gap is never bridged.

## 3–6. Integrity audits
- **Wave-1 population discrepancy:** confirmed (§0). Non-gated 160,888 vs gated 105,255.
- **S5 audit → Case B (contaminated).** Previous S5 result froze as `S5_PREVIOUS_RESULT_EVIDENCE_POPULATION_INVALIDATED`; exact frozen spec replayed on gated population (below).
- **S1-swing audit → Case B.** Replayed on gated population (below).
- **Candidate-001 audit → affected (deep re-baseline used 160,888).** Integrity replay of the frozen V1 only (not resurrected/modified).

## 7. Corrected replay results (gated 105,255, BASE/STRESS, per-block)
| Candidate | n | GROSS | BASE | STRESS | best-1%-removed | per-block (b0 / b1) R | Verdict |
|---|---|---|---|---|---|---|---|
| **S5 C_2d587447** | 627 | +0.097 | **+0.089** | **+0.055** | **+0.061** (legit skew) | +33.8 / +21.7 (both +) | **CONFIRMED — PASS REPRODUCED** |
| **S20 C_09d2245b** | 690 | +0.175 | **+0.153** | **+0.069** | **+0.128** (legit skew) | +40.2 / +65.5 (both +) | **CONFIRMED (NEW survivor)** |
| S9 C_0bb5095b (v1) | 978 | +0.045 | +0.035 | −0.003 | +0.017 | −17.5 / +51.7 (unstable) | COST_FRAGILE |
| S9 C_d008e0a4 (v2) | 889 | +0.009 | −0.003 | −0.050 | −0.031 | −35.1 / +32.1 | FAIL |
| S1-PDH C_dca5629f (v1, long) | 847 | +0.193 | **+0.151** | −0.005 | +0.134 | +70.8 / +57.5 (both +) | COST_FRAGILE (razor STRESS) |
| S1-PDH C_9214b37b (v2, short) | 511 | +0.115 | +0.084 | −0.034 | +0.055 | +30.3 / +12.7 (both +) | COST_FRAGILE |
| S1-swing C_954698b1 | 268 | −0.030 | −0.038 | −0.071 | −0.084 | +3.8 / −14.1 | FAIL (reproduced) |
| Candidate-001 V1 (integrity) | 1947 | +0.130 | +0.114 | +0.053 | **−0.014** | +145 / +77 | **FAIL — outlier-dependence reproduces** |

**S5 → `S5_DEEP_RESEARCH_PASS_REPRODUCED`** (in fact stronger on the correct population: B +0.089 vs prior +0.064, best-1%-removed +0.061 vs +0.036). **Candidate-001 V1**: gross/BASE/STRESS are positive on gated DEV blocks, but the **deep tail criterion reproduces** — best-1%-removed **−0.014** = `UNSTABLE_OUTLIER_DEPENDENCE` → its DEEP_RESEARCH_FAIL **stands**.

## 8–10. Wave-2 primary candidates (S9×2, S20, S1-PDH×2) — now economically evaluable
- **S20** (hybrid: H4-up context + 50-bar breakout, ATR stop, RR3): **the standout** — B +0.153, S +0.069, legitimate skew, both blocks strongly positive. **A robust second Alpha.**
- **S1-PDH v1** (PDH/PDL sweep, low, long): very strong gross+BASE (+0.19/+0.15, both blocks +, legit skew) but **razor-negative at STRESS** (−0.005) → COST_FRAGILE, one step from surviving.
- **S1-PDH v2** (short): real gross+BASE edge, STRESS-negative → COST_FRAGILE.
- **S9 v1**: COST_FRAGILE + block-unstable (b0 negative). **S9 v2**: FAIL.
- **S20 component note (item 12):** S20 is the H4-trend-context breakout hybrid; it is the strongest of the MTF family (S9 variants are cost-fragile/fail), i.e. the H4-context conditioning of the breakout is where the incremental value sits. No post-hoc component optimization performed.

## 11–15. Tail / temporal / overlap
- **Tail:** S5 and S20 both show **legitimate positive skew** (best-1%-removed positive); Candidate-001 shows outlier-dependence (negative). S1-PDH v1 also legit-skew but STRESS-fragile.
- **Temporal:** S5 and S20 positive in **both** discovery blocks; S9 variants block-unstable.
- **Overlap (survivors, gated):** **S5 vs S20 Jaccard 0.047 → INDEPENDENT**; S5 vs C-001 0.028; S20 vs C-001 0.017. **S5 and S20 are two mutually-independent Alpha sources** (both LONG breakout-family, decorrelated entries: NY opening-range vs H4-context rolling-breakout).

## 16–18. Survivors / failures / blockers
- **Survivors (CONFIRMED_FOR_DEEPER_RESEARCH):** **S5, S20** — independent.
- **Cost-fragile:** S9 v1, S1-PDH v1 (strong gross+BASE), S1-PDH v2.
- **Fail:** S9 v2, S1-swing, Candidate-001 V1 (outlier-dependent).
- **DC-0003 / DC-0008:** status preserved — `IMPLEMENTATION_MIGRATION_REQUIRED` (class boundary / M1 anatomy unresolved; not approximated). **DC-0004:** `GOVERNANCE_PAUSED_REQUIRES_FRESH_EVIDENCE` (burned evidence, not reused).

## 19. MANDATORY corrected-evidence table
| Candidate | Previous evidence population | Correct population | Previous verdict | Corrected verdict | Changed? |
|---|---|---|---|---|---|
| S5 C_2d587447 | 160,888 (non-gated, incl. gap) | 105,255 (gated) | DEEP_RESEARCH_PASS | CONFIRMED — **PASS reproduced (stronger)** | NO (reproduced) |
| S1-swing C_954698b1 | 160,888 (non-gated) | 105,255 (gated) | FAIL | FAIL | NO (reproduced) |
| Candidate-001 V1 | 160,888 (deep re-baseline) | 105,255 (gated) | DEEP_RESEARCH_FAIL (outlier-dep) | FAIL — outlier-dep reproduces | NO (reproduced) |
| S9 C_0bb5095b (v1) | not evaluable (MIGRATION_REQUIRED) | 105,255 (gated) | — | COST_FRAGILE | **YES (now evaluable)** |
| S9 C_d008e0a4 (v2) | MIGRATION_REQUIRED | 105,255 (gated) | — | FAIL | **YES** |
| S20 C_09d2245b | MIGRATION_REQUIRED | 105,255 (gated) | — | **CONFIRMED (new survivor)** | **YES** |
| S1-PDH C_dca5629f (v1) | MIGRATION_REQUIRED | 105,255 (gated) | — | COST_FRAGILE | **YES** |
| S1-PDH C_9214b37b (v2) | MIGRATION_REQUIRED | 105,255 (gated) | — | COST_FRAGILE | **YES** |
*The DEVELOPMENT-population discrepancy is now permanently visible. Both HISTORICAL and CORRECTED results are preserved (prior reports untouched; §22).*

## 20–22. Governance / preservation
VALIDATION_ACCESS_COUNT = 0; FINAL_HOLDOUT_ACCESS_COUNT = 0; native 2023+ (VALIDATION-overlapping) period never used. Prior reports (`ALPHA_HISTORICAL_REREVIEW_WAVE1_REPORT.md`, `ALPHA_S5_C001_DEEP_RESEARCH_REPORT.md`) are **not erased** — their results stand as HISTORICAL, superseded by the CORRECTED_AUTHORITATIVE results here. No silent rewrite. V4.4 frozen (`23d98c07…`); no MI retune; no new families; broker disabled; no AI Trader.

## 23. Recommended next candidate portfolio + exact CEO next step
1. **Two robust, independent Alpha sources now stand on the correct population: S5 (reproduced) and S20 (new).** Both CONFIRMED, both legitimate-skew, both block-stable, both survive STRESS, mutually independent (Jaccard 0.047).
2. **S5 validation firewall lifted:** S5 reproduced `DEEP_RESEARCH_PASS` on the gated population → **CEO may proceed with fresh independent S5 validation evidence.** Recommend S20 join the same validation-decision queue.
3. **Watchlist (cost-fragile, real gross+BASE edge):** S1-PDH v1 (long, STRESS −0.005 — one step away) and v2 (short) — candidates for an exit/target study (not this mandate).
4. **Closed:** Candidate-001 V1 (outlier-dependent, reproduced), S1-swing (fail, reproduced), S9 v2 (fail).
5. **Exact next step:** send **S5 + S20** to independent Statistician/Red Team validation as two distinct pro-continuation Alpha sources; nothing promoted to Strategy Catalog/AI Trader/LIVE by Alpha Discovery.

**STOP** — `READY_FOR_CEO_ALPHA_PORTFOLIO_DECISION`.
