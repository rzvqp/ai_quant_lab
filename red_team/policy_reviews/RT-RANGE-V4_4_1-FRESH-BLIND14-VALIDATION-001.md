# RED TEAM — RANGE V4.4.1 FRESH BLIND-14 FINAL VALIDATION
### RT-RANGE-V4_4_1-FRESH-BLIND14-VALIDATION-001 · Auditor: Red Team · 2026-08-21

Final fresh-blind semantic comparison of frozen V4.4 (`3bb61cf`) vs frozen V4.4.1 (`4ed4eb4`, T-STALE, params
29/4/3/12) on the cryptographically-frozen F441 14-window batch. The semantic generalization gate for V4.4.1.
No research/calibration/redesign/threshold-selection/label-review. Detectors, labels, scorer, windows all frozen.

---

## 0 — VERDICTS

```
F441_INFERENCE_INTEGRITY_PASS
F441_SCORING_INTEGRITY_PASS
V4_4_1_FRESH_BLIND14_GENERALIZATION_NOT_SUPPORTED
```

On this fresh 14-window batch V4.4.1's T-STALE mechanism **works as designed** — it recovers genuine RANGE that
V4.4's stale-candidate blocking loses (recall 0.577 → 0.808, +9 TP recovered) — **but it fails both
pre-registered HARD gates**: it doubles total false RANGE (H2: 8 → 16) and adds a directional false positive
(H1: 4 → 5). Under the CEO's prospectively-locked error cost (**false RANGE is more dangerous than missed
RANGE**), a recall/F1 gain can never compensate an H1/H2 failure. It also destroys 3 genuine V4.4 TP via
harmful abandonment. **Frozen V4.4 remains preferable.** Next action requires CEO decision (§14 below).

Not authorized: redesign, recalibration, Strategy Catalog, Alpha, AI Trader, LIVE_SHADOW, broker, orders, live
trading, any promotion.

---

## 1 — INTEGRITY (§2–§13)

| gate | result |
|---|---|
| detector chain: V4.4 `3bb61cf`, V4.4.1 `4ed4eb4`, impl audit `6adef91` (PASS_WITH_NONBLOCKING_NOTES) | verified |
| V4.4.1 config_id recomputed `d7b6c067…` · params 29/4/3/12 · no runtime substitution | PASS |
| F441 chain: protocol `4af8ea9` (pre-committed 03:28) → selection `6a62243` (03:30) → labels `0f6f1a9` (12:07) → freeze `2ad5cab` (12:08); local=remote ×4 | PASS |
| canonical identities: `labels_sha256 4112dbce…`, `session_log 577edf29…`, `selection_manifest c8aa83ba…`, `window_payload f66a8752…` — all reproduced from source | PASS |
| 14 windows · 5×96/5×288/4×480 · block quota B4:5/B1:5/B2:4 (B3 exhausted) · no missing/dup | PASS |
| exclusion accounting: FB14 (E8, 13511 bars) + MB3 (E7, 43337) separate excluded classes → **zero overlap** with FB14/MB3/all prior classes | PASS |
| labels frozen **before** any detector run (`V4_4_EXECUTED=False, V4_4_1_EXECUTED=False, PREDICTIONS_EXIST=False`) | PASS |
| window payload `labels_present=False`, HMAC-valid; **14/14 bars_sha256 reproduced** from canonical M15_v2 delivered df (197094 rows, file `57f4ed95…`) | PASS |
| labels payload `8838b8c5…` HMAC-valid, 1-bit + wrong-key refused; decrypts to `labels_sha256 4112dbce…` | PASS |
| labels: 14/14, **26 MACRO RANGE segments**, **F441-011 = 0 RANGE** (natural negative control), confidence/episode `NOT_SPECIFIED`, `SEMANTIC_AMENDMENT_LOG=EMPTY`, F441-008 note `TRANSCRIPTION_NOTE_NON_SEMANTIC` | PASS |
| Env A isolation: scorer not imported, no label/key access (asserted); input carries no MACRO/RANGE/level fields | PASS |
| predictions frozen (`778778d`) **before** label access; both hashes re-verified fail-closed in Env B; deterministic | PASS |
| Env B isolation: no detector imported; ratified scorer `scoring.py` (byte-identical `664934ab`) used identically for both | PASS |
| FB14 not reused; MB3-001→024 not reused; MB3-025→048 sealed/untouched | PASS |

Detector identities: V4.4 config_id `23d98c07` / contract range-hierarchical-v4.4; V4.4.1 config_id `d7b6c067…`
/ contract range-hierarchical-v4.4.1. Prediction hashes: `V44 2830a712…`, `V441 f96054f1…`. Both
`INFERENCE`+`SCORING` **INTEGRITY_PASS**.

## 2 — PRIMARY COMPARISON (§24) — MACRO GT = 26 CEO RANGE; ratified scorer, IoU>0 match

| Metric | V4.4 | V4.4.1 | Delta | Gate |
|---|---:|---:|---:|---|
| matched RANGE TP | 15 | 21 | **+6** | H3 |
| detected (confirmed MACRO) | 22 | 37 | +15 | — |
| **total FP** | **8** | **16** | **+8** | **H2 (HARD)** |
| **directional FP** | **4** | **5** | **+1** | **H1 (HARD)** |
| FN | 11 | 5 | −6 | — |
| recall | 0.577 | 0.808 | +0.231 | H4 |
| precision | 0.682 | 0.568 | −0.114 | — |
| F1 | 0.625 | 0.667 | +0.042 | — |
| median IoU | 0.590 | 0.529 | −0.061 | — |

## 3 — H1–H5 GATE MATRIX (pre-registered `4af8ea9`; H1/H2 HARD; false-RANGE-averse; H1–H5 LOCKED)

| H | criterion | result | verdict |
|---|---|---|---|
| **H1** directional FP ≤ | V4.4.1 5 ≤ V4.4 4 | 5 > 4 | **FAIL (HARD)** |
| **H2** total FP ≤ | V4.4.1 16 ≤ V4.4 8 | 16 > 8 | **FAIL (HARD)** |
| H3 TP ≥ | V4.4.1 21 ≥ V4.4 15 | true | PASS |
| H4 recall ≥ | V4.4.1 0.808 ≥ V4.4 0.577 | true | PASS |
| H5 T-STALE benefit | EVALUABLE (natural stale events in 6/6 recovered windows); recovery condition MET (+9 TP) **but violates the "without increasing H1/H2" clause** | — | **FAIL-on-clause / moot** |

**H1 and H2 both FAIL → `GENERALIZATION_NOT_SUPPORTED`** (§35). No gate weakened, no metric substituted, no
window excluded, no post-result adaptation (§32 honored: only frozen alternation=3 and window=29 used; 2/4 and
28/30 never tested on this blind).

## 4 — DIRECTIONAL FP DECOMPOSITION (§25) — false RANGE is the higher-cost error

```
V4.4   FP by CEO class : RANGE 4 (over-seg) · TREND_DOWN 3 · TREND_UP 1                      = 8   (directional 4)
V4.4.1 FP by CEO class : RANGE 11 (over-seg) · TREND_DOWN 4 · TRANSITION 1                   = 16  (directional 5)
```
The H2 failure is dominated by **RANGE-context over-segmentation** (4 → 11): T-STALE frees the single slot
inside a genuine RANGE, letting multiple structures confirm there — one matches the GT (TP), the surplus become
false RANGE. Directional FP also rose (4 → 5), failing H1 outright.

## 5 — TP RECOVERY / LOSS (§26/§18)

- **Recovered by V4.4.1 (V4.4 missed): 9** — F441-004 (×2), 005, 007, 008, 010 (×2), 012. These are the genuine
  stale-blocked ranges the diagnostic predicted; T-STALE's core hypothesis is **empirically real**.
- **Lost by V4.4.1 (V4.4 had): 3** — F441-009, F441-014 (×2). Harmful abandonment: T-STALE killed candidates
  that would have matched. F441-014 (L=96) lost **both** its TP (2 → 0).
- Net TP +6, but bought with +8 FP and −3 genuine matches — a strictly false-RANGE-adverse trade.

## 6 — T-STALE FIRING AUDIT (§21) — 32 fires

| classification (window-level) | count |
|---|---|
| BENEFICIAL (recovers TP, no new FP) | 9 |
| HARMFUL (new FP or lost TP) | **17** |
| NEUTRAL | 6 |

Harmful firings outnumber beneficial nearly 2:1. The over-firing (32 fires across 12 windows) is the mechanism
behind both the recall gain and the FP doubling — the same aggressive slot-freeing that recovers a stuck range
also fragments already-healthy ranges.

## 7 — FRAGILE PARAMETER WATCH (§22) — the FRAGILE flag materialized

**Every one of the 32 T-STALE firings occurred at alternation count = exactly 3** — the frozen value, calibrated
`FRAGILE` (`9116c2b` §5.3). The entire observed benefit *and* the entire observed harm ride on the exact
fragile boundary the calibration and both prior RT audits flagged. No alternate value was tested (§32). This is
the disclosed residual risk realized on fresh evidence.

## 8 — WINDOW-29 WATCH (§23)

Rejected-evidence ages contributing to firings span 17–91 bars (median ≈ 39); the 29-bar window bounds which
rejections count. No pathological single-edge concentration observed, but firings routinely draw on evidence
across the full window — consistent with the "not independently discriminated" sensitivity note.

## 9 — F441-011 NATURAL NEGATIVE CONTROL (§27)

CEO GT = 0 MACRO RANGE. **V4.4 = 0 confirmed, V4.4.1 = 0 confirmed.** Neither detector fabricates RANGE on the
natural negative control (V4.4.1 fired T-STALE twice here but confirmed nothing — no false RANGE created). Clean
on this single window; not built into a separate gate.

## 10 — PER-LENGTH (§29)

| L | V4.4 TP/FP recall | V4.4.1 TP/FP recall |
|---|---|---|
| 96 | 5/2 · 0.833 | 4/2 · **0.667** (lost F441-014) |
| 288 | 5/4 · 0.500 | 8/6 · 0.800 |
| 480 | 5/2 · 0.500 | 9/**8** · 0.900 |

The FP explosion concentrates in the long windows (480: FP 2 → 8), where a genuine long RANGE offers the most
room for T-STALE-induced fragmentation. On the short windows V4.4.1 is strictly worse.

## 11 — EPISODE / OVER-SEGMENTATION (§30)

26 CEO RANGE episodes vs 37 V4.4.1 confirmed structures (V4.4: 22). V4.4.1's excess confirmations are the
over-segmentation signature: freeing the slot mid-range spawns replacements that confirm as separate structures.
T-STALE reduced stale blocking (recall up) **by creating exactly the excessive episode churn §30 warned
against**.

## 12 — STATISTICAL RESTRAINT (§33)

N = 14 windows; no population-wide claim, no p-values (none pre-registered), no bootstrap, no exploratory
search. Statement is limited to: **the pre-registered fresh-blind gates were not all met on this batch** — H3/H4
held (TP/recall), H1/H2 (the hard gates) did not. The TP-preservation risk from FB14 is resolved (recall
recovered) but a **new, higher-cost false-RANGE regression** replaced it.

---

## 13 — WHAT THIS MEANS

T-STALE is not broken and its diagnosis was correct: the stale-candidate blocking was a real mechanism, and
abandoning stale candidates genuinely recovers missed RANGE (recall 0.577 → 0.808). But the correction is
**miscalibrated against the CEO's error-cost priority**: at the frozen (fragile) thresholds it fires too often
(32×, 17 harmful), doubling false RANGE and adding a directional FP. Under "false RANGE > missed RANGE" with
H1/H2 as hard gates, **V4.4.1 as frozen is a regression, not a generalization**, and **frozen V4.4 remains the
preferable detector**.

## 14 — NEXT CEO ACTION (§37)

Report only, no redesign here. Options for CEO:
1. **Hold V4.4** as the canonical RANGE detector (recommended under the locked false-RANGE-averse objective — it
   has the lower, safer FP profile).
2. Authorize a **future, separate** re-examination of the T-STALE *trigger stringency* (it fires too easily) —
   the mechanism recovers real TP, so a stricter firing condition might keep the recall gain without the FP
   doubling. That would be a new calibration/design cycle on evidence never used here (never F441, FB14, or MB3),
   explicitly targeting the over-segmentation/harmful-abandonment failure mode — **not** a threshold tweak
   applied to this blind.
3. Abandon T-STALE.

The `min_alternation=3` FRAGILE flag is now a **confirmed** material risk, not a theoretical one. `MB3-025→048`
remain sealed for any future evidence.

---

*Red Team · detectors/labels/scorer/escrow unmodified · changes only in `red_team/` · MB3-025→048 sealed ·
FB14/MB3-001→024 not reused · no post-result adaptation · LEDGER E96 (prev E95).*
