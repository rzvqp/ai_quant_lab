# RED TEAM — MB3-001→024 FROZEN BLIND EXECUTION & SCORING
### RT-RANGE-MB3-001 · Auditor: Red Team · 2026-08-20

---

## 0 — VERDICTS

```
MB3_FREEZE_INTEGRITY_PASS
MB3_EXECUTION_INTEGRITY_PASS
MB3_MACRO_GENERALIZATION_NOT_SUPPORTED   (recall ~stable; precision/F1/IoU degraded + poor range/channel/trend discrimination)
MB3_INTERNAL_F4 = NOT_TESTABLE_ON_MB3    (no INTERNAL ground truth in the MB3 labels)
EPISTEMIC CLASS = CEO_ASSISTED_BLIND_EVALUATION   (NOT INDEPENDENT_SEMANTIC_BLIND_PASS)
INDEPENDENT_SEMANTIC_BLIND = FALSE · VALIDATION_WEIGHT applies to out-of-sample evidence only
NO promotion: Wheel / Strategy Catalog / Alpha / AI Trader / LIVE_SHADOW / broker = NOT AUTHORIZED
MB3-025→048 = PRESERVED SEALED (not decrypted for labels, not scored, detector not run on them)
```

The frozen batch executed cleanly on the ratified F1-only detector; freeze and blind-chain integrity hold.
The MACRO **recall generalizes approximately** to this unseen CEO-assisted batch, but **precision, F1 and IoU
degrade** and a classification analysis shows the detector **does not cleanly separate RANGE from
CHANNEL/TREND** — so a generalization *claim* is not affirmatively supported. This is out-of-sample evidence,
not an independent semantic pass.

---

## 1 — PRE-RUN INTEGRITY MATRIX (§2) — all PASS

| check | result |
|---|---|
| Statistician freeze report + commit `fddb986` | PASS (HEAD of statistician-foundation) |
| local = remote (4 mirrors) | PASS |
| `labels_sha256` = `6369f5e0…94de` (plaintext labels file) | PASS (hash-only, semantics not read pre-freeze) |
| labels payload `ac962530` content-addressed + HMAC valid + decrypts to `6369f5e0` + 1-bit refused | PASS |
| window payload `b9d0fd72` content-addressed + HMAC valid + 1-bit refused + wrong-key refused | PASS |
| selection `dd1c8f5f` · manifest `1098abd0` · seed `01b77747` binding | PASS (present in window payload) |
| exactly 24 windows MB3-001→024; 8/8/8 length; 6/6/6/6 block | PASS |
| **24/24 `bars_sha256` reproduced from the canonical corpus** (render window, RT-0011 recipe) | PASS |
| full bar coverage, zero gaps, zero inter-window overlaps | PASS |
| MB3-009 amendment append-only (25 rows / 24 windows, original preserved) | PASS |
| MB3-007 & MB3-020 CEO-declared MACRO absence (no RANGE segment) | PASS |
| no detector output before label freeze (`detector_state_at_freeze` all false; Statistician did not run) | PASS |

→ **`MB3_FREEZE_INTEGRITY_PASS`.**

## 2 — DETECTOR / CONFIG / RUNNER IDENTITY (§3)

```
detector range_semantic_v4_3.py sha256 = 098fa144…  (ratified F1-only build bc6b9dc, RT-RANGE-0013 PASS)
config_id      = 24f72a60fcde42746d44f098558a745fac0f20b0141865bdbe0359f9cc3826da   (unchanged)
contract       = range-hierarchical-v4.3                                            (unchanged)
implementation_fingerprint = f1-only-f5-deferred-2026-08-20
```
No modification to detector / semantics / thresholds / ATR / config / reason codes / state machine / snapshot
schema / scorer. No calibration, no parameter search, no V4.4.

## 3 — EXECUTION INTEGRITY (§4-6) — PASS

- **Env A (inference)**: label/fixture/scorer files removed from the tree; dynamic audit — inference read **no**
  label/scorer file, no subprocess, no socket. Input built from corpus + window-payload canonical indices
  only (no MACRO/level/CHANNEL/TREND/timestamp fields — verified). Detector run **once** (`RUN_ATTEMPT=1`) on
  exactly MB3-001→024 (6912 bars).
- **F1 / OHLC (§4)**: the ratified F1 validator **tolerated 10 sub-tick bars** (close marginally outside
  `[low,high]` within `epsilon = min_tick/2 = 0.005`), emitting `INPUT_OHLC_SUBTICK_TOLERATED` on a separate
  channel. **No OHLC modified, no gate widened, no detector change** — the already-ratified path, so **not
  `MB3_EXECUTION_BLOCKED_F1`**.
- **Freeze before labels (§5)**: `predictions.json` sha256 `26a7d461…` frozen read-only in Red Team escrow,
  hash + sanitized manifest committed + pushed (4 mirrors MATCH) **before any label access** →
  `MB3_PREDICTIONS_FROZEN_BEFORE_LABEL_ACCESS`. Blind chain intact (labels never accessible to Env A).
- **Env B (scoring)**: scorer + labels only, **no detector/inference importable** (verified). Recomputed
  `labels_sha256` = `6369f5e0` ✓ and `predictions_sha256` = `26a7d461` ✓ before scoring. Ratified scorer run
  unmodified.

→ **`MB3_EXECUTION_INTEGRITY_PASS`.**

## 4 — SCORING RESULTS (§7)

MACRO ground truth = the CEO **RANGE-class** segments (batch `RANGE_MACRO_BLIND`; 38 RANGE segments across 22
windows; MB3-007/020 have none). Ratified scorer, unchanged.

### A. MACRO
```
GT 38 · detected 62 · TP 26 · FP 36 · FN 12
recall 0.684 · precision 0.419 · F1 0.520
IoU  p25 0.213 · median 0.352 · p75 0.501 · max 0.776
confirm-delay mean 127.7 / median 42.5 bars
```
Detection existence is reported separately from boundary quality: recall (existence) 0.684 vs IoU-median
(boundary) 0.352 — the detector finds most ranges but fits their boundaries loosely.

### B. By window length
```
 96 bars : 5/11 matched (recall 0.45)
288 bars : 6/12 matched (recall 0.50)
480 bars : 15/15 matched (recall 1.00)
```
Strong length dependence — long windows detected essentially perfectly, short windows poorly.

### C. By block
```
B1 7/10 · B2 5/10 · B3 7/7 · B4 7/11
```
B2 weakest (two full-miss windows MB3-004, MB3-005). Small denominators — reported, not hidden.

### D. Classification confusion (RANGE ↔ CHANNEL ↔ TREND) — the material finding
Structure-level (each confirmed MACRO structure → CEO dominant class over its span), 62 structures:
```
detector RANGE (not promoted)  = 13 → CEO RANGE 7 · CEO CHANNEL 4 · CEO TREND 2
detector TREND (promoted)      = 49 → CEO CHANNEL 25 · CEO RANGE 16 · CEO TREND 6 · CEO TRANSITION 2
```
Per-bar, the detector sits in a range-state on **~87–90%** of CEO CHANNEL bars and **~79–81%** of CEO TREND
bars — i.e. **it barely discriminates RANGE from CHANNEL/TREND**. It also **over-promotes to TREND** (49/62),
firing trend on 25 CEO-CHANNEL and 16 CEO-RANGE spans. On the two CEO-MACRO-absent windows (007/020) it
produced **4 confirmed MACRO structures — all false positives.** This is the dominant limitation and is robust
to the GT-mapping choice.

### E. Events — DIAGNOSTIC ONLY
No ratified MB3 event-matching rule exists, so events are **not scored** and **no credit** is awarded (per §7E).
Side-by-side counts only: CEO {BREAKOUT_DOWN 16, BREAKOUT_UP 12, SWEEP_DOWN 7, SWEEP_UP 6, FAILED_BREAKOUT_UP 3,
AMBIGUOUS 14, NONE 24}; detector MACRO {BREAKOUT_ACCEPTED 50, SWEEP_CONFIRMED 33, LIQUIDITY_SWEEP_REVERSAL 5}.
The detector has no directional (UP/DOWN) or FAILED_BREAKOUT event vocabulary matching the CEO taxonomy.

### F. INTERNAL / F4
The MB3 labels are **single-level (MACRO/RANGE only) — zero INTERNAL ground truth**. The detector emitted 9
confirmed INTERNAL structures, but with **no INTERNAL GT the F4 collapse question is NOT TESTABLE on MB3**;
neither `MB3_INTERNAL_F4_PERSISTS` nor `_IMPROVED` can be asserted. INTERNAL is kept fully separate from MACRO.

## 5 — COMPARISON WITH RT-RANGE-0010 (§8)

| metric | RT-0010 | MB3 | direction |
|---|---|---|---|
| MACRO recall | 0.705 | **0.684** | **≈ stable** (−0.021) |
| MACRO precision | 0.534 | **0.419** | **materially degraded** (−0.115) |
| MACRO F1 | 0.608 | **0.520** | degraded (−0.088) |
| IoU median | 0.439 | **0.352** | degraded (−0.087) |
| INTERNAL | 1/12 | not testable | — |

**Confound disclosed:** RT-0010's MACRO GT was the LEVEL_MAPPING MACRO segments (88), which may include
channel-like ranges; MB3's MACRO GT is the stricter CEO **RANGE-class** set (38, channels/trends excluded).
So the **recall** comparison (does the detector find labeled ranges) is the cleaner cross-batch signal, while
**precision/IoU** are partly confounded by the different GT definitions. Per §8, a single stable metric
(recall) does not establish generalization — and precision/F1/IoU degrade while the classification analysis
shows weak discrimination. Therefore generalization is **not affirmatively supported** (not the same as
refuted): recall holds out-of-sample; range-vs-channel-vs-trend discrimination does not.

## 6 — PER-WINDOW ERROR TABLE (opaque IDs + relative counts only)

```
window    L  blk GT TP FP FN        window    L  blk GT TP FP FN
MB3-001  96  B1  1  1  1  0         MB3-013  96  B1  2  1  0  1
MB3-002 288  B1  2  1  2  1         MB3-014 288  B1  1  0  2  1
MB3-003 480  B1  2  2  1  0         MB3-015 480  B1  2  2  5  0
MB3-004  96  B2  2  0  0  2 (miss)  MB3-016  96  B2  1  1  1  0
MB3-005 288  B2  3  0  0  3 (miss)  MB3-017 288  B2  1  1  0  0
MB3-006 480  B2  2  2  2  0         MB3-018 480  B2  1  1  2  0
MB3-007  96  B3  0  0  1  0 (absent→FP)  MB3-019  96 B3 1 1 0 0
MB3-008 288  B3  2  2  0  0         MB3-020 288  B3  0  0  3  0 (absent→3 FP)
MB3-009 480  B3  3  3  0  0         MB3-021 480  B3  1  1  2  0
MB3-010  96  B4  3  1  0  2         MB3-022  96  B4  1  0  0  1 (miss)
MB3-011 288  B4  1  0  2  1         MB3-023 288  B4  2  2  1  0
MB3-012 480  B4  2  2  2  0         MB3-024 480  B4  2  2  1  0
TOTAL: GT 38 · TP 26 · FN 12 · detected 62
```

## 7 — CONSOLIDATED FINDINGS / FP-FN ANALYSIS

- **FN (12):** concentrated in short/mid windows and B2 — MB3-004 (2), MB3-005 (3), MB3-010 (2), plus single
  misses; two windows (004, 005) produced **no** confirmed MACRO structure at all.
- **FP:** driven by (a) **over-promotion to TREND** on CEO CHANNEL/RANGE spans and (b) **4 structures on the
  two CEO-MACRO-absent windows** (007, 020). The detector rarely abstains — it forms a macro structure almost
  everywhere.
- **Recall generalizes; discrimination does not.** The clean cross-batch signal (recall ≈ 0.68–0.70) holds,
  but the detector's inability to separate RANGE from CHANNEL/TREND is a consistent, material limitation.
- **INTERNAL/F4 untestable** on MB3 (no INTERNAL GT).

## 8 — EPISTEMIC STATUS (§9) & PROHIBITIONS (§12-13)

`CEO_ASSISTED_BLIND_EVALUATION` — real out-of-sample bars unseen by the detector, but the ground truth is
CEO-assisted, so this is **not** `INDEPENDENT_SEMANTIC_BLIND_PASS`. No adaptive intervention was performed:
the first frozen prediction set is the scored set; no rerun, no threshold/label/scorer change, no window
exclusion, no metric cherry-picking. No promotion authorized (Wheel/Strategy Catalog/Alpha/AI Trader/
LIVE_SHADOW/broker) — any next step requires a separate CEO decision. **MB3-025→048 preserved sealed**: not
decrypted for labels (the labels file marks them `NOT_PART_OF_THIS_BATCH`), not scored, detector not run on
them, not used for tuning.

## 9 — RECOMMENDED NEXT ACTION

Report to CEO: MACRO **range detection recall generalizes (~0.68) out-of-sample, but precision/boundary
quality degrade and the detector does not discriminate RANGE from CHANNEL/TREND** (over-promotion + FPs on
MACRO-absent windows). Before any promotion, this discrimination weakness should be characterized (research,
not inside this mandate). A cleaner independent (non-CEO-assisted) semantic gate and a ratified event-matching
+ INTERNAL protocol would be needed to move beyond `CEO_ASSISTED_BLIND_EVALUATION`. Remaining blocker for a
generalization claim: **weak range/channel/trend discrimination**, not detection existence.

---

*Red Team · detector/config/scorer/labels/escrow/windows unmodified · changes only in `red_team/` · MB3-025→048 sealed · LEDGER E89 (prev E88).*
