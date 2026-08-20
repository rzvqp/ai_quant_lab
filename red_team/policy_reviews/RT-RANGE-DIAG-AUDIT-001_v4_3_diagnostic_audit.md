# RED TEAM — V4.3 DIAGNOSTIC DECISIVE AUDIT
### RT-RANGE-DIAG-AUDIT-001 · Auditor: Red Team · 2026-08-20 · target `VE-RANGE-DIAG-001` (`071fbd7`)

Focused parallel audit of whether the decisive premises VE is using to design V4.4 are factually sound. Not a
re-run of the research program; no V4.4 design; no detector change.

---

## 0 — DISPOSITION

```
V4_3_DIAGNOSTIC_FOUNDATION_CONFIRMED
```

Every decisive premise in `VE-RANGE-DIAG-001` reproduces independently from the frozen, hash-verified MB3
artifacts. The detector re-run matches the frozen predictions **62/62 structures, 0 mismatches**. VE's
diagnostic is not only correct but unusually self-critical — it falsifies its own leading fix, separates a
secondary mechanism it does not yet understand, and discloses an unchecked confound; on audit, all three hold
up and the confound actually **reinforces** VE's conclusion. **No V4.4 design assumption must change.** Design
*requirements* (already stated by VE) are restated in §3.

Provenance verified: `071fbd7` HEAD of discovery-mk-matrix-v1, local=remote ×4, parent `bc6b9dc`; it touches
**only** the report + PROJECT_STATE (no detector/config/scorer change). Detector `bc6b9dc` (`098fa144`,
config_id `24f72a60`), labels `6369f5e0`, predictions `26a7d461` — all re-hashed and matched.

---

## 1 — DECISIVE-CLAIM MATRIX

| # | Claim | VE conclusion | RT independent reproduction | Verdict | Material caveat |
|---|---|---|---|---|---|
| 1 | 39-FP decomposition | 30 directional + 9 over-segmentation | **EXACT**: 39 FP = 30 directional (CHANNEL_UP 14 / CHANNEL_DOWN 8 / TREND_DOWN 4 / TREND_UP 3 / TRANSITION 1) + 9 RANGE-dominant | **SUPPORTED** | FP=39 (scorer `false_positives_macro`) vs my MB3 report's 36; VE traced it — 3 detections each best-matched 2 GT, so unique matched=23, FP=62−23=39. VE is correct; my earlier "36" was the naive 62−26. |
| 2 | 12-FN decomposition | 4 truncation + 5 few-touch + 3 degenerate | **12/12 confirmed all formation/confirmation-timing, ZERO boundary/IoU-quality misses** | **SUPPORTED** | The finer 4/5/3 split is VE's per-bar-chronology categorization; my coarser heuristic gave 4 truncation + 8 (few-touch/degenerate combined) — the decisive property (all timing, 0 boundary) is confirmed; the few-touch-vs-degenerate boundary is a minor categorization choice, immaterial to V4.4. |
| 3 | Directional-discrimination defect | MACRO confirm has **no** directional gate; `normalized_drift`/`s_max` wired only at INTERNAL | **CODE CONFIRMED**: `degeneracy_check` gates only cluster-width `(bu−bl) ≤ 2·w_atr·atr_ref`; `evaluate_candidate` adds only touch-count + duration `d_macro`; `normalized_drift`/`s_max` appears at MACRO **nowhere** — used only at line ~1058 for the INTERNAL `INT_CHANNEL_*` descriptive label | **SUPPORTED** | — |
| 4 | 96/288/480 = latency | MORE_TIME_TO_FIRE, not better recognition | **CONFIRMED**: eligible-after-`d_macro=29` = 67/259/451 (70/90/94%); matched confirm-delay median 29/36/93; the L=480 median (93) exceeds the **entire** L=96 eligible budget (67). | **SUPPORTED** | VE disclosed the GT-length/window-length confound as unchecked; I checked it — corr = **0.40** (real), mean GT-range length 34/38/100 by L. But this **reinforces** MORE_TIME_TO_FIRE (longer windows hold longer ranges needing more confirm time), it does not support BETTER_RECOGNITION. |
| 5 | Naive drift-gate falsification | rejects most directional FP but destroys a similar fraction of TP | **EXACT**: `drift > s_max=1.60` destroys **13/23 TP (57%)** while catching **19/30 directional FP (63%)**; drift distributions overlap (TP median 1.719 vs FP 1.755; 56.5% vs 63.3% over s_max) | **SUPPORTED** | `SINGLE_DRIFT_GATE_FIX_IS_NOT_JUSTIFIED` — confirmed. |
| 6 | MB3-007 | 1 structure, CHANNEL_DOWN, confirm @ `d_macro` clears | **CONFIRMED**: 1 confirmed structure, CEO-dominant CHANNEL_DOWN, confirm bar 31; CEO segments all CHANNEL (no RANGE) — confirmed the instant the duration floor clears, no directional check | **SUPPORTED** | — |
| 7 | MB3-020 | 3 structures, TREND_DOWN cascade | **CONFIRMED**: 3 confirmed structures, all TREND_DOWN-dominant, confirm bars 104/145/261; CEO TREND_DOWN/CHANNEL_UP/TREND_DOWN | **SUPPORTED** | VE's own disclosed nuance holds: one late structure's drift (0.73) sits under s_max despite the CEO's broader TREND label — a genuine local-vs-context ambiguity, not cleanly a detector error. |

---

## 2 — MISSING-CAUSE SEARCH (§7) — none found

I actively searched for a material alternative VE missed:
- **State/snapshot/replay artifact:** ruled out — the independent engine re-run reproduces all **62/62**
  confirmed structures' `structure_id` + `confirm_ts` exactly.
- **Scorer / FP-count artifact:** the 39-vs-36 gap is fully explained (scorer's `false_positives_macro`
  counts distinct detections matching *nothing*; 3 detections each best-matched two GT segments). Not a bug;
  VE's 39 is the correct count and matches the mandate's own framing.
- **Label-adapter / over-segmentation artifact:** examined the 9 RANGE-dominant FP directly — **all 9 overlap
  a real CEO RANGE segment** (IoU 0.11–0.41) but lost the best-IoU tie in windows with many more detector
  range episodes than CEO RANGE labels (MB3-015 8-vs-2, MB3-021 7-vs-1, MB3-024 6-vs-2). This **confirms VE's
  B.2**: a granularity mismatch between the detector's per-episode output and the CEO's coarser labeling —
  **not** a directional defect and **not** a pure scorer bug. VE correctly kept it out of the directional-fix
  story; a directional gate would not fix these and could over-suppress genuine ranges.
- **ATR / F1 artifact:** the F1 validator tolerated the sub-tick bars without modifying OHLC (MB3 execution
  audit); the engine's causal `atr14` reproduces the frozen structures exactly — no ATR artifact.
- **Boundary / episode-matching / implementation-vs-semantic:** the code path itself (no directional gate at
  MACRO) *is* the semantic gap — not an implementation defect masquerading as one.

No material alternative explanation surfaced. The diagnostic is sound.

## 3 — V4.4 DESIGN REQUIREMENTS (Red Team states; VE owns the design — §8)

None of VE's design assumptions must change. The following requirements (all already recognized by VE) are
confirmed as binding:
- **V4.4 must address** the MACRO directional-displacement gap (30/39 FP), **but not** by wiring the existing
  `normalized_drift > s_max` pair unchanged — that naive gate is falsified (destroys 57% of TP).
- **V4.4 must preserve** the 23 genuine TP: any directional feature must catch directional FP without the
  ~1:1 collateral TP loss the naive gate shows.
- **V4.4 must treat the 9-structure over-segmentation class separately** — it is a labeling-granularity
  mismatch (genuine ranges), not a directional error; a directional gate neither explains nor fixes it.
- **Any candidate feature/threshold must be pre-registered and evaluated on untouched evidence**
  (MB3-025→048 or a fresh batch under Red Team control), never fit against these same 39/23 structures.
- **The length effect is a confirmation-latency/observation-budget constraint, not a recognition deficit** —
  V4.4 should not assume longer context yields better pattern recognition; short-window recall loss is
  mechanical (duration budget), reinforced by the disclosed GT-length/window-length confound.

## 4 — SCOPE / PROHIBITIONS

Focused audit only. No V4.4 design, no thresholds proposed, no detector/config/scorer/label/escrow change, no
implementation, no parameter optimization, no INTERNAL/F4 research, no Alpha/Strategy Catalog/Wheel/LIVE_SHADOW/
broker. **MB3-025→048 remain SEALED** — not decrypted for labels, not scored, detector not run on them, not used
adaptively (the window payload's presence of all 48 definitions was used only to confirm batch structure).
`MACRO_INDEPENDENT_BLIND_PREPARATION_AUTHORIZED` is unaffected by this audit. This audit consumes no evidence
that changes any prior verdict.

---

*Red Team · detector/config/scorer/labels/escrow unmodified · changes only in `red_team/` · MB3-025→048 sealed · LEDGER E90 (prev E89).*
