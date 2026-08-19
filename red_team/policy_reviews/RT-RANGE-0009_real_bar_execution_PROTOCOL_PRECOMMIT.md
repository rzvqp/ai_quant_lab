# RED TEAM — RANGE V4.3 REAL-BAR EXECUTION · PRE-RUN PROTOCOL (PRE-COMMIT)
### RT-RANGE-0009 · `REAL_BAR_SEALED_CONSTRUCTION_REVALIDATION`
**Date:** 2026-08-19 · **Auditor:** Red Team

**This protocol is committed BEFORE any real bar or the escrow ID→interval mapping is read.** Only meta (escrow tool, published hashes, CEO instructions, canonical corpus filename) has been inspected so far. Reading of the sealed mapping/bars begins only after this commit is pushed and `local = remote` is confirmed.

---

## 1 — Scientific classification (fixed before the run)

```
CORPUS_SEMANTIC_STATUS          = CEO_ASSISTED_CONSTRUCTION_CORPUS
REAL_OHLC_PREVIOUSLY_UNSEEN_BY_VE = TRUE
LABELS_USED_IN_V4_3_DESIGN      = TRUE
INDEPENDENT_SEMANTIC_BLIND      = FALSE
```

Because the 48 windows' labels contributed to the V4.3 contract and parameter choices, the following verdicts are **forbidden** regardless of outcome: `BLIND_PASS`, `SEMANTIC_PASS`, `FINAL_VALIDATION_PASS`, `STRATEGY_CATALOG_READY`, `ALPHA_AUTHORIZED`, `BLIND_PASS_NOT_PERMITTED`. This run can produce only real-bar evidence + a semantic diagnostic.

## 2 — Frozen identity (fixed)

```
prototype_commit = f224e7d
runner_commit    = 82f27c0
contract_version = range-hierarchical-v4.3
config_id        = 24f72a60fcde42746d44f098558a745fac0f20b0141865bdbe0359f9cc3826da
detector file hashes (must match at runtime, inference re-hashes fail-closed):
  range_semantic_v4_3.py = 2aba333c413c484f8ff85c91180e29f852834475d982ab4f4a5c32120ccb238b
  range_engine_v4_3.py   = 84dac346524591fdfe904cd0dde0f1d8888161cdffe62dcd7129cff6eea1c1f2
```
Any mismatch → stop fail-closed.

## 3 — Population (fixed)

```
48 windows · 13,824 bars total · 16×96 + 16×288 + 16×480
corrected lengths: BLIND-046 = 288 · BLIND-047 = 96 · BLIND-048 = 480
level-1: 88 MACRO + 26 LEVEL_ASSIGNMENT_UNRESOLVED = 114
level-2: 12 INTERNAL (separate population)
```
Escrow verification (§4 of the mandate): payload exists; payload SHA-256 = its content-addressed filename; the v3 key opens it and a wrong key / 1-bit change fails the HMAC tag; mapping has exactly 48 IDs, no duplicate ID/bar, no missing window; each window's extracted OHLC SHA-256 = the published hash in `BLIND_LABEL_BATCH_02_HASHES.md`; instrument XAUUSD, timeframe M15, canonical calendar, valid OHLC, total 13,824. If any fails → `RANGE_V4_3_REAL_BAR_EXECUTION_BLOCKED_ESCROW`, no substitution.

## 4 — Metrics (fixed; computed exactly by the audited `82f27c0` scorer)

MACRO and INTERNAL, separately: total labelled, total detected, true positives, false negatives, false positives, recall, precision, IoU {p25, median, p75, max}, boundary error upper/lower (in ATR, where price bands exist), confirm delay. Events: sweeps / breakouts / failed-breakouts / `LIQUIDITY_SWEEP_REVERSAL` / promotions — labelled vs detected, FP/FN, confirm delay. Distributions: per 96/288/480, per block, per window, per depth, all states, all 29 reason codes, full rejection funnel.

## 5 — Matching, denominators, UNRESOLVED, open structures (fixed = the audited scorer's rules)

- Matching rule + tie-breaking = exactly `blind_runner/scoring.py` @ `82f27c0` (deterministic, RT-RANGE-0008 verified). No ad-hoc rule.
- **MACRO recall denominator = 88; INTERNAL recall denominator = 12.** UNRESOLVED (26) reported separately, **never scored**; INTERNAL not re-counted inside the 114.
- **No label may be corrected after seeing predictions; existing ambiguities stay marked, not resolved post-hoc.**
- **Open structures** (confirmed but still open at window end) are included; the scorer measures their span to the observable limit (window `n_bars`), never into the future.

## 6 — Run + freeze discipline (fixed)

- **Two separated stages.** Stage A (inference): frozen detector + runner + real bars only — no labels, no mapping-of-levels, no scorer, no PnL, no broker, no network; run **once** (`RUN_ATTEMPT = 1`) under dynamic audit (files opened, modules imported, child processes, network). Stage B (scoring): created only after predictions are frozen — sealed predictions + manifest + SHA-256 + final labels + level mapping + scorer only; no bars, no detector, no engine, no re-run.
- **One inference execution.** After the first bar is read: no code/config/input/window-order change; no re-run for surprising or weak metrics. A semantic/runner error after data access → `RUN_FAILED_AFTER_DATA_ACCESS`, stop. A pure environment error permits a re-run only if it is proven no bar was read.
- **Freeze before labels.** After inference: write `predictions.json` + `predictions.manifest.json` + `predictions.sha256`; verify the hash independently; mark read-only; keep the prediction payload out of Git (only the hash + sanitized manifest are committed); commit the hash; push; verify `local = remote`; declare `PREDICTIONS_FROZEN_BEFORE_LABEL_ACCESS`. Only then read the labels.

## 7 — Data protection (fixed)

Never publish in Git: real bars, real timestamps, ID→timestamp mapping, the escrow key, predictions that reveal calendar periods, local paths, secrets. Publish only: hashes, a sanitized manifest, aggregate metrics, opaque window IDs, relative indices, reports without sealed data.

## 8 — Stop protocol (fixed)

Fail-closed and stop on: identity mismatch (§2); escrow verification failure (§3 → `BLOCKED_ESCROW`); a semantic/runner error after data access (`RUN_FAILED_AFTER_DATA_ACCESS`); any attempt that would require reading labels before the prediction freeze. Permitted terminal verdicts: `RANGE_V4_3_REAL_BAR_EXECUTION_INTEGRITY_PASS|FAIL`, `RANGE_V4_3_REAL_BAR_METRICS_READY|INVALID`, and the mandatory declaration `INDEPENDENT_SEMANTIC_BLIND = FALSE` / `BLIND_PASS_NOT_PERMITTED`. No post-hoc threshold, no final semantic PASS. Disposition after result: promising-nonempty → `NEW_INDEPENDENT_BLIND_LABEL_BATCH_PREPARATION`; weak → `RANGE_V4_3_DIAGNOSTIC_REVIEW` (then, if evidence warrants, a V4.4 delta). Not authorized regardless: wheel, Strategy Catalog, Alpha, AI Trader, LIVE_SHADOW, broker, trades, 6-hour regression.

```
REAL_BAR_EXECUTION_PROTOCOL_PRECOMMITTED
```
