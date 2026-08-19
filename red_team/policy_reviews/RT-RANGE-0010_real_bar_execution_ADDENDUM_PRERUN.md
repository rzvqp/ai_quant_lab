# RED TEAM — RANGE V4.3 REAL-BAR EXECUTION · PRE-RUN ADDENDUM (Phase B)
### RT-RANGE-0010 · addendum to protocol `38daf9b`

**Committed BEFORE the first real bar is processed and BEFORE the scorer accesses any label.**
Phase A (`RANGE_V4_3_ESCROW_REPRODUCIBILITY_AUDIT`) has **PASSED** (48/48 anchors reproduced by an
independent Red Team reimplementation in two clean checkouts). This addendum freezes the Phase-B
execution plan. Nothing here changes the frozen detector, runner, config, labels, mapping, or anchors.

---

## 1 — Frozen identities (immutable for this run)

```
detector prototype commit   = f224e7d
  range_semantic_v4_3.py     sha256 = 2aba333c413c484f8ff85c91180e29f852834475d982ab4f4a5c32120ccb238b
  range_engine_v4_3.py       sha256 = 84dac346524591fdfe904cd0dde0f1d8888161cdffe62dcd7129cff6eea1c1f2
runner commit               = 82f27c0   (blind_runner: inference.py / scoring.py / schemas.py)
contract_version            = range-hierarchical-v4.3
config_id                   = 24f72a60fcde42746d44f098558a745fac0f20b0141865bdbe0359f9cc3826da
escrow reproducibility pkg  = alpha-automation-v1 @ dc1d9ed (6b96430 + dc1d9ed)
package_fingerprint         = 2f8dd39c567bd0e888d88505b9bd28664d3ca37ac37a1dca30ec8271037162e2
statistician report         = 60d1a20
```

## 2 — Frozen data identities (verified in Phase A)

```
source corpus CSV sha256    = 57f4ed9544993c8fbba28d9c1e3319f2e0665ef5db211fb09d9f4622222ccd37  (355,696 raw rows)
canonical corpus rows       = 197,094   (4 discovery segments; loader edge_research._common.load M15_v2)
canonical corpus fingerprint= af3bf2f6ffc35ba4c4f4c6da9963c06ff5c99c4952b5ab62d42218cc7b254cf3
escrow payload sha256       = b7e103a3d9b86f7257debd0bc1d32da2d76f4031545ecd54e5487daf7ee3f1cb  (20,906 B)
mapping plaintext sha256    = 5d986818ca867270d2bda5566f1bfdc2ac0cd3dd9654b1af6f15bbbc7c679f11
minimal run-mapping sha256  = 83f678d400d885e4385f005889cbc4808a1fbb2287c303d166b509281064fa36  (id + canonical idx + L only)
windows                     = 48 · 13,824 bars · 16×96 + 16×288 + 16×480 · corrected 046=288/047=96/048=480
```

The 48 `bars_sha256` anchors were reproduced 48/48 by Red Team's own recipe over the render window
`[render_start, render_end)`; the detector is fed the **canonical L window**
`[canonical_index_start, canonical_index_end)` — a verified subset of that render block.

## 3 — Inference input (Env A — NO labels)

- For each window `BLIND-xxx`: `L` real bars = `corpus[canonical_index_start : canonical_index_end)`
  (`high/low/open/close` float64 from the canonical corpus). `window_id=BLIND-xxx`, `symbol=XAUUSD`,
  `timeframe=M15`, `bar_interval_seconds=900`.
- `ts_close = i*900`, `ts_open = ts_close-900` for bar `i∈[0,L)` — **exactly the construction
  convention** (`run_construction` used `ts_close=idx*900`). Justified statically: the detector's
  structure spans are relative bar indices and `atr14` is count-based (14-bar), so absolute `ts`
  does not affect structural output; this convention isolates real-vs-synthetic to OHLC only.
- Input is built from the corpus + the escrow mapping's canonical indices ONLY. **No label, no
  LEVEL_MAPPING, no scorer, no PnL, no network.** `input.json` stays off-git (it carries real bars).

## 4 — Single execution + freeze (§14/§15)

- `RUN_ATTEMPT = 1`. Smoke test first on the synthetic dev fixture only (no real bars). After the
  first real bar is processed: no code/config/input/order change; no re-run for weak/surprising
  metrics. A semantic/runner error after data access → `RUN_FAILED_AFTER_DATA_ACCESS`, stop. A pure
  environment error permits a re-run only if provably no real bar was processed.
- Immediately after inference: `predictions.json` + `predictions.manifest.json` + `predictions.sha256`
  (inference writes these; predictions marked read-only). Red Team independently re-hashes, copies to
  its escrow, commits **only the hash + sanitized manifest** (never the predictions payload, which
  encodes per-bar structure), pushes 4 mirrors, verifies `local=remote`, declares
  `PREDICTIONS_FROZEN_BEFORE_LABEL_ACCESS`. Only then are labels read.

## 5 — Exact commands

```
# Env A (inference; off-git dirs; no labels present in the env):
python ve_n1_replay/blind_runner/inference.py --input <off-git>/input.json --output-dir <off-git>/preds

# Env B (scoring; created only after freeze; no detector/engine importable):
python ve_n1_replay/blind_runner/scoring.py --predictions-dir <off-git>/preds \
       --labels <off-git>/labels.json --out <off-git>/metrics.json
```

Env A dir: `C:/rt10_work/envA` · Env B dir: `C:/rt10_work/envB` — physically separate; inference is
label-blind (AST-verified `test_anti_leakage_ast.py`), scoring cannot import the detector.

## 6 — Metrics + denominators (frozen; the audited `82f27c0` scorer computes them)

```
MACRO recall denominator    = 88
INTERNAL recall denominator = 12
UNRESOLVED                  = 26  (reported separately, NEVER in a recall denominator)
```
Labels for scoring come from `construction_reproduction/parse_windows.parse_level_mapping`
(LEVEL_MAPPING.md + PART1-4 fixtures) — the same GT the synthetic reference used, in canonical
`0..L` coordinates. MACRO/INTERNAL: TP/FP/FN, recall, precision, F1, IoU {p25,median,p75,max},
confirm delay, per-length 96/288/480, per-block, per-window; events (sweeps/breakouts/
liquidity-sweep-reversals/promotions); full rejection funnel; all reason codes.

## 7 — Scientific classification (mandatory, fixed regardless of outcome)

```
CORPUS_SEMANTIC_STATUS            = CEO_ASSISTED_CONSTRUCTION_CORPUS
REAL_OHLC_PREVIOUSLY_UNSEEN_BY_VE = TRUE
LABELS_USED_IN_V4_3_DESIGN        = TRUE
INDEPENDENT_SEMANTIC_BLIND        = FALSE
BLIND_PASS_NOT_PERMITTED
```
Forbidden verdicts regardless of result: `BLIND_PASS`, `SEMANTIC_PASS`, `FINAL_VALIDATION_PASS`,
`STRATEGY_CATALOG_READY`, `ALPHA_AUTHORIZED`. This run measures execution integrity + real-bar
behaviour + real-vs-synthetic delta only — never independent semantic performance.

## 8 — Data protection

Never published: real bars, real timestamps, ID→timestamp mapping, escrow key, predictions payload,
local paths. Published only: hashes, sanitized manifest, aggregate metrics, opaque window IDs,
relative in-window indices.

```
RT-RANGE-0010 · REAL_BAR_EXECUTION_ADDENDUM_PRECOMMITTED · PHASE_A=PASS
```
