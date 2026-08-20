# RED TEAM — RANGE V4.4 FRESH BLIND-14 VALIDATION
### RT-RANGE-V4_4-FRESH-BLIND14-VALIDATION-001 · Auditor: Red Team · 2026-08-21

First semantic fresh-blind comparative validation of frozen V4.4 (`3bb61cf`) vs frozen V4.3 (`bc6b9dc`) on the
14-window FB14 batch. No research/calibration/redesign/threshold-selection. Detectors, labels, scorer all frozen.

---

## 0 — VERDICTS

```
FB14_INFERENCE_INTEGRITY_PASS
FB14_SCORING_INTEGRITY_PASS
V4_4_FRESH_BLIND14_GENERALIZATION_NOT_SUPPORTED
```

On this fresh 14-window batch V4.4 **achieves its design target** — it reduces directional false positives and
improves precision/F1/IoU — **but the pre-registered generalization gates are not all met**: it loses genuine
RANGE true positives and degrades recall (**H2 and H3 FAIL**). The pre-registered rule requires *all* primary
gates to pass; two fail, so generalization is **not supported**. This is not an integrity failure and not the
disclosed gentle-channel limitation — it is a **new false-reject mechanism**: V4.4's traversal gate rejects
genuine CEO ranges that oscillate without fully traversing the band. Next research action requires CEO
authorization (§34).

Not authorized by anything here: Strategy Catalog, Alpha, AI Trader, LIVE_SHADOW, broker, live trading.

---

## 1 — INTEGRITY (§3/§4/§11/§14/§31)

| gate | result |
|---|---|
| impl chain (`bc6b9dc`/`3bb61cf`/`845a03c`) + FB14 chain (`e8ce481`→`7a2c93d`→`20bf599`→`c6d9e02`→`a520039`) | verified, local=remote ×4 |
| 14 windows, length 5×96/5×288/4×480, block B1:5/B2:4/B4:5 (B3 exhausted) | PASS |
| protocol amendment `7a2c93d` (17:53:04) **before** selection `20bf599` (17:55:32); methodological round-robin fill (MB3 precedent), capacity-driven not result-driven | **PRESELECTION_METHOD_AMENDMENT_VALID** |
| B3 exhaustion documented (0 eligible at all lengths; consumed by batches 01/02/MB3) | PASS |
| labels frozen **before** any detector run (`V4_3_EXECUTED=False, V4_4_EXECUTED=False, PREDICTIONS_EXIST=False`) | PASS |
| window payload `4e6e9fcf` HMAC-valid, 1-bit + wrong-key refused; **14/14 bars_sha256 reproduced from the canonical corpus** | PASS |
| labels payload `2ea635aa` HMAC-valid, decrypts to `labels_sha256 d284fd39`, 1-bit refused | PASS |
| labels: 14/14, **24 MACRO RANGE segments**, **FB14-014 = 0 RANGE** (negative control), confidence/state `NOT_SPECIFIED`, amendment-log EMPTY | PASS |
| Env A isolation: no label/scorer/key present; input has no MACRO/RANGE/CHANNEL/level fields | PASS |
| prediction freeze **before** label access; both hashes re-verified in Env B; deterministic | PASS |
| Env B isolation: no detector/inference importable; ratified scorer unchanged; both scored identically | PASS |
| F1: 2 sub-tick bars tolerated via the ratified engine path, OHLC unmodified, no clip/repair | PASS |
| MB3-001→024 not used to select/modify FB14; MB3-025→048 sealed/untouched | PASS |

Provable chronology: windows frozen (`20bf599`) → labels frozen (`c6d9e02`/`a520039`) → Env A (no labels) →
V4.3 run → V4.4 run → both predictions frozen (`26abd13`) → only then labels opened by Env B. Detector
identities: V4.3 `range_semantic_v4_3 098fa144` / config_id `24f72a60`; V4.4 `range_semantic_v4_4 833aedfd` /
config_id `23d98c07` / contract `range-hierarchical-v4.4`. Both `INFERENCE`+`SCORING` **INTEGRITY_PASS**.

## 2 — PRIMARY SCORING TABLE (MACRO GT = 24 CEO RANGE segments; ratified scorer, IoU>0 match)

| Metric | V4.3 | V4.4 | Delta | Gate |
|---|---:|---:|---:|---|
| matched RANGE TP | 15 | 12 | **−3** | H2 |
| detected (confirmed MACRO) | 34 | 22 | −12 | — |
| total FP | 19 | 10 | **−9** | H4 |
| directional FP | 13 | 7 | **−6** | H1 |
| FN | 9 | 12 | +3 | — |
| recall | 0.625 | 0.500 | **−0.125** | H3 |
| precision | 0.441 | 0.545 | **+0.104** | H5 |
| F1 | 0.517 | 0.522 | +0.004 | H5 |
| median IoU | 0.609 | 0.651 | +0.042 | — |

## 3 — H1–H5 GATE MATRIX (pre-registered, `e8ce481` §12; "SUPPORTED requires passing the primary gates exactly")

| H | criterion | result | verdict |
|---|---|---|---|
| **H1** directional FP reduction | V4.4 dir-FP `<` V4.3 | 7 < 13 | **PASS** |
| **H2** TP preservation | V4.4 RANGE TP `≥` V4.3 | 12 ≥ 15 false | **FAIL** |
| **H3** recall non-degradation | V4.4 recall `≥` V4.3 | 0.500 ≥ 0.625 false | **FAIL** |
| **H4** total-FP non-degradation | V4.4 FP `≤` V4.3 | 10 ≤ 19 | **PASS** |
| **H5** quality | precision≥ ∧ F1≥ ∧ ≥1 strict | 0.545≥0.441 ∧ 0.522≥0.517 ∧ strict | **PASS** |

All five are testable (V4.3 has 13 directional FP; 24 scorable RANGE) — no `NOT_TESTABLE`. **H2 and H3 fail →
`GENERALIZATION_NOT_SUPPORTED`.** No gate weakened, no metric substituted, no window excluded.

## 4 — DIRECTIONAL FP DECOMPOSITION (§19) — the diagnosed V4.3 defect **did** improve

```
V4.3 FP by CEO class : TREND_UP 4 · CHANNEL_UP 5 · TREND_DOWN 3 · TRANSITION 1 · RANGE 6 (over-seg)  = 19
V4.4 FP by CEO class : TREND_UP 4 · CHANNEL_UP 2 · TREND_DOWN 1 ·               · RANGE 3 (over-seg)  = 10
directional (non-RANGE) FP : 13 → 7   (−6, H1 PASS)   ·   over-segmentation (RANGE) FP : 6 → 3   (−3)
```
V4.4 cut both the directional over-promotion (the primary D1 defect) and the over-segmentation (D6). The
design's central mechanism works directionally.

## 5 — TP-PRESERVATION (§20) — the failure, traced

3 genuine RANGE TP matched by V4.3 are lost by V4.4; **0 gained**. All three fail on the **traversal gate**:
```
FB14-003 [110,216)  V4.4 no confirmed structure — dominant in-span reason INSUFFICIENT_TRAVERSAL (106 bars)
FB14-003 [232,288)  V4.4 no confirmed structure — INSUFFICIENT_TRAVERSAL (56 bars)
FB14-012 [211,480)  V4.4 structures land elsewhere (IoU 0) — INSUFFICIENT_TRAVERSAL (267 bars)
```
These are CEO-labelled RANGES that oscillate within a sub-band without crossing UPPER↔LOWER enough to satisfy
`MIN_TRAVERSALS`. This is a **false-reject of genuine ranges by the traversal requirement** — a *new*
mechanism, **distinct** from the disclosed gentle-channel *false-accept* limitation (§7 below).

## 6 — DIAGNOSTICS (secondary, non-adaptive)

**Per length** (recall): 96 → V4.3 1.00 / V4.4 1.00 (unchanged); 288 → 0.45 / **0.27**; 480 → 0.67 / **0.56**.
Recall loss is concentrated in the longer windows, where the traversal gate over-rejects.

**Episode / over-segmentation (§24):** V4.4 reduces over-detection where V4.3 fragmented — FB14-007 (CEO 2:
V4.3 **8**→V4.4 **4**), FB14-012 (CEO 2: 6→2), FB14-014 (CEO 0: 2→1) — but over-corrects FB14-003 (CEO 2:
3→**0**, both TP lost). Fewer stale/duplicate confirmations; no wrongful merges of distinct CEO ranges observed.

**Confirmation timing (§23):** V4.4 median confirm-delay ≈ **29 at all lengths** (96:29, 288:31.5, 480:29) —
length-independent; consistent with the `MORE_TIME_TO_FIRE` fix holding (the construction proof remains
primary; this is fresh diagnostic corroboration only, on 14 non-matched paths).

**FB14-014 negative control (§26):** V4.3 = 2 false MACRO RANGE, V4.4 = **1** (fewer, still one). Diagnostic
only; no acceptance gate built on this single window.

## 7 — GENTLE-CHANNEL LIMITATION (§25)

V4.4 still confirms on some CEO CHANNEL/TREND spans (7 directional FP), consistent with the disclosed
gentle-channel/zigzag limitation — **counted as FP, not excused** (it is inside the H1/H4 numbers above). No
retuning, no special-case channel detector, no MB3 exception was introduced. The dominant failure here,
however, is the *opposite* (false-reject of genuine ranges, §5), which the traversal gate — not the
gentle-channel limitation — drives.

## 8 — V4.3 vs V4.4 STRUCTURE MAP (§27, summary)

V4.4 vs V4.3: **12** confirmed-MACRO fewer (34→22); FP −9, TP −3. V4.4 suppresses V4.3 directional/over-seg
structures (intended) and additionally suppresses 3 genuine ranges (unintended, traversal-gate). No new V4.4
structure matched a GT range that V4.3 missed. Median IoU of surviving matches improves (0.609→0.651): the
ranges V4.4 *does* keep, it fits slightly better.

## 9 — REMAINING RISKS / STATISTICAL RESTRAINT (§28)

14 windows is a small confirmation batch; no population-wide claim, no p-values (none pre-registered), no
bootstrap, no exploratory search. The statement is limited to: **the pre-registered fresh-blind comparative
gates were not all supported on this 14-window batch** — H1/H4/H5 held (FP-reduction/precision), H2/H3 did not
(TP/recall). The TP-preservation risk that the design and RT-RANGE-V4_4-DESIGN-AUDIT-001 flagged as
*unvalidated and requiring the fresh-blind stage* has now **materialized** and is localized to the traversal
gate.

## 10 — NEXT RECOMMENDED CEO ACTION (§34)

Do not redesign here. Recommend to CEO: a **pre-registered calibration/mechanism review of the traversal gate
only** (`MIN_TRAVERSALS`, its band-third definition, and the trailing window `W`) — the component that
over-rejected 3 genuine ranges — evaluated on evidence never used to derive it (a fresh batch, never MB3 or
FB14), keeping the directional-discrimination improvement (H1/H4/H5) intact. Whether to pursue that, accept a
precision/recall trade, or hold V4.3 is a CEO decision. `MB3-025→048` remain sealed for that future evidence.

---

*Red Team · detectors/labels/scorer/escrow unmodified · changes only in `red_team/` · MB3-025→048 sealed · MB3-001→024 zero-validation-weight · LEDGER E93 (prev E92).*
