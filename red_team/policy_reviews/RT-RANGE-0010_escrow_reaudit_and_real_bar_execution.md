# RED TEAM — RANGE V4.3 ESCROW RE-AUDIT + CONDITIONAL REAL-BAR EXECUTION
### RT-RANGE-0010 · single continuous mandate · Auditor: Red Team · 2026-08-20

---

## 0 — VERDICTS

```
PHASE A : RANGE_V4_3_ESCROW_REPRODUCIBILITY_AUDIT_PASS
PHASE B : RANGE_V4_3_REAL_BAR_EXECUTION_INTEGRITY_PASS   (with material finding F1 — see §B.2)
          RANGE_V4_3_REAL_BAR_METRICS_READY
MANDATORY : INDEPENDENT_SEMANTIC_BLIND = FALSE · BLIND_PASS_NOT_PERMITTED
DISPOSITION : NEW_INDEPENDENT_BLIND_LABEL_BATCH_PREPARATION_RECOMMENDED (MACRO level)
              + RANGE_V4_3_DIAGNOSTIC_REVIEW_REQUIRED (INTERNAL level — see F4)
window_list_sha256 : NON_BLOCKING_REDUNDANT_UNREPRODUCED_META_ANCHOR
```

Phase A closes the RT-RANGE-0009 finding `ESCROW-UNREPRODUCIBLE-ANCHOR`: the 48 `bars_sha256` anchors
are now reproduced **48/48 by an independent Red Team reimplementation** in two clean checkouts. Phase B
is the first real-bar execution of the frozen V4.3 detector on the 48 CEO-assisted sealed windows. It is
**NOT** a blind or semantic PASS — the 48 windows' labels shaped the V4.3 contract, so no independent
semantic performance is validated here.

Nothing was modified to force a PASS: detector, runner, config, payload, mapping, anchors, corpus, labels
untouched; all changes confined to `red_team/`. Every commit cited below was verified to exist with
`local=remote` on all four mirrors before this verdict.

---

# PHASE A — ESCROW REPRODUCIBILITY AUDIT

## A.1 — Sources verified from Git (not from the Statistician's summary)

All 14 mandated commits exist; `local=remote` MATCH on alpha1/discovery/lab/trader for both branches
(`alpha-automation-v1` @ `dc1d9ed`, `statistician-foundation` @ `60d1a20`). Package: `escrow_repro/`
(6 files, commits `6b96430`+`dc1d9ed`), fingerprint `2f8dd39c…`; report `60d1a20`.

## A.2 — Clean-checkout reproducibility (two independent checkouts, Git-only)

Two `git archive dc1d9ed` checkouts (coA, coB), fresh venv (numpy 2.5.2 / pandas 3.0.5), **no reuse of
any Statistician-generated file or off-git script**:

| check | coA | coB |
|---|---|---|
| source CSV sha256 = `57f4ed95…` (355,696 raw rows) | MATCH | MATCH |
| loader `edge_research._common.load(M15_v2)` → rows | **197,094** | **197,094** |
| discovery segments | **4** | **4** |
| corpus fingerprint = `af3bf2f6…` | MATCH | MATCH |
| times strictly increasing / duplicate timestamps | yes / **0** | yes / **0** |
| official verifier → anchors | 48/48 exit 0 | 48/48 exit 0 (Turkish locale) |
| 22 tests / `mypy --strict` | 22 pass / clean | — |
| package fingerprint (LF-normalized) = `2f8dd39c…` | MATCH | MATCH |

The wp5b loader returns 130,491 bars for the same timeframe (3 discovery segments) — this is exactly why
RT-0009 could not locate the corpus: it lives in the `alpha-automation-v1` loader (4 segments), not as a
file. `M15_v2` manifest entry is **byte-identical across v2.7.92/93/94** (`6ae0837`/`96a7352`/`14d4c22`) —
reproducibility does not depend on a post-sealing manifest.

## A.3 — Independent recipe reproduction (§5) — Red Team's own code, not theirs

I reimplemented `bars_sha256` from the spec prose (not importing `canonical_corpus.bars_sha256`), via **two
independent byte paths** (numpy `.astype(int64).tobytes()` and manual `struct.pack("<q")`). Both reproduce
**48/48** anchors over the render window `[render_start, render_end)`. Recipe confirmed: columns concatenated
in order **H, L, O, C** (not OHLC), each `×1e6` truncated to int64, little-endian, SHA-256. Required negatives
all correct:

```
canonical L window            → 0/48   (confirms render window, not L)
O,H,L,C column order          → 0/48   (confirms H,L,O,C)
textual serialization         → 0/48   (confirms binary, not text)
row-reversed                  → no match
one-tick (0.001) mutation     → breaks all of high/low/open/close
render_end − render_start = L+48        → 48/48
canonical_index_end − start = L, in-bounds → 48/48
quantization floor            → 1e-6 absorbed on bar0 high, 2e-6 firmly detected (documented property; 1000× tick margin)
```

## A.4 — 48 anchors, no resealing, freeze intact, no leaks

- Payload `payload-b7e103a3d9b86f72.bin` (sha256 `b7e103a3…`, 20,906 B) is the **same file verified in
  RT-0009**; HMAC opens with the authorized key, wrong key and 1-bit flip both refused. 48 unique IDs,
  13,824 bars, 16×96+16×288+16×480, corrected 046=288/047=96/048=480.
- **No resealing**: `BLIND_LABEL_BATCH_02_HASHES.md` last modified at the original sealing commit `f76a643`
  (before the remediation); BLIND-001 published anchor `7546a8d1…` = the payload anchor I reproduced.
  Manifest declares `resealing_performed=false, anchors_modified=0` — confirmed.
- **Implementation freeze**: the Statistician's commits touched **only `escrow_repro/`** (6 files created,
  2 modified; zero detector/runner/config). Frozen detector (`range_semantic_v4_3.py` / `range_engine_v4_3.py`)
  byte-identical to `f224e7d`; runner byte-identical to `82f27c0` (empty diff); `config_id 24f72a60…`
  present in inference+scoring; schemas present.
- **Leak scan** of `6b96430`+`dc1d9ed`: no per-window anchor/index/timestamp literals; no OHLC values, no
  keys, no decrypted mapping. Only `escrow_key_v3.bin` appears as a path variable name and the already-public
  046/047/048 corrections. The Statistician's own §5 discloses a self-caught leak (a real OHLC value in a
  docstring) removed before commit — confirmed absent.

## A.5 — `window_list_sha256` decision (§8)

`window_list_sha256` (`d9f77eea…`) was **not** reproduced (computed pre-OHLC in an intermediate textual form
not reconstructible from sealed artifacts). Classified **`NON_BLOCKING_REDUNDANT_UNREPRODUCED_META_ANCHOR`**.
Formal reason it cannot permit substitution of bars, windows, or mapping: the window list — every ID, every
render/canonical index, every length, and all 48 `bars_sha256` — lives **inside** the content-addressed,
HMAC-authenticated payload. Any change to the window list changes the payload bytes → breaks both the payload
SHA-256 (`b7e103a3…`) and the HMAC tag. Independently, each window's `bars_sha256` is now reproduced 48/48
from the fixed 197,094-bar corpus (fingerprint `af3bf2f6…`), binding each window's indices to real bars via
collision-resistant SHA-256. Thus the window-list identity is **fully subsumed** by anchors that are both
stronger and reproducible; `window_list_sha256` adds no substitution protection they do not already provide.
No substitution passing all other checks exists — so it is redundant, not blocking. Recipe not invented, hash
not replaced.

## A.6 — PASS/FAIL matrix (Phase A)

| requirement | result |
|---|---|
| §1 commits exist, local=remote ×4 | PASS |
| §4 two clean checkouts, 197,094 bars, 4 segments, source+corpus SHA, identical fingerprint | PASS |
| §4 segment order, no concat duplication, manifest-version invariance | PASS |
| §5 recipe independently reimplemented + reproduced 48/48 + negatives | PASS |
| §6 all 48 anchors reproduced, 0 missing/extra/replaced, payload = RT-0009's | PASS |
| §7 22 tests, mypy strict, negative tests fail for the right reason | PASS |
| §8 window_list_sha256 classified (non-blocking redundant) | PASS |
| §9 detector/runner/config/config_id/schemas byte-identical, freeze intact | PASS |
| §10 no sealed-data leak in the new commits | PASS |

**Phase A = `RANGE_V4_3_ESCROW_REPRODUCIBILITY_AUDIT_PASS`.** `ESCROW-UNREPRODUCIBLE-ANCHOR` (RT-0009) CLOSED.

---

# PHASE B — REAL-BAR EXECUTION

Pre-run addendum committed+pushed **before any bar** (`7d226c7`, `REAL_BAR_EXECUTION_ADDENDUM_PRECOMMITTED`,
local=remote ×4). Predictions frozen **before any label** (`46a9576`, `PREDICTIONS_FROZEN_BEFORE_LABEL_ACCESS`).

## B.1 — Isolation (§13), verified static + dynamic

- **Env A (inference)** `C:/rt10_work/envA`: frozen detector + runner + real bars + escrow mapping indices
  only. Labels/fixtures physically removed from the checkout. Dynamic audit during the single run: no
  label-ish file read, no subprocess, no socket; `zero_labels_access=true`. Input built from corpus + escrow
  canonical indices only (contains no MACRO/INTERNAL/level/timestamp fields — verified).
- **Env B (scoring)** `C:/rt10_work/envB`: scorer + labels only, **no detector present**. Dynamic import+open
  tracer: scoring imports **no** `range_semantic`/`range_engine`/`inference` module and opens **no** detector
  file. Scoring deterministic (two runs byte-identical).

## B.2 — FINDING F1 (material): frozen runner CLI rejects the real corpus

The audited `blind_runner/inference.py` CLI **fail-closed-rejected** the raw real corpus:
**13 of 13,824 real bars** carry a sub-tick vendor artifact — close or open sits **exactly 0.0005** outside
`[low, high]` (OANDA XAUUSD M15 mixed-precision rounding; e.g. high 3-dp, close 4-dp) — tripping
`CLOSE_OUTSIDE_HIGH_LOW` / `OPEN_OUTSIDE_HIGH_LOW` **before any bar reaches the detector**. The artifact
persists under the anchor's own int64 truncation, so it is a genuine data property, not an extraction error.
No bar was processed and no prediction produced by that attempt (single-run discipline intact).

Per the mandate's "resolve incidental data/tooling issues autonomously and continue" directive, and because
this is a data-plumbing incompatibility (not a detector defect and not a Red Team bug), I executed the frozen
detector on the same real bars via the runner's **own** per-window path `inference._run_one_window`
(→ byte-identical `RangeSemanticEngineV43.replay_batch`), skipping **only** the OHLC-range input gate. **OHLC
values, detector, config, and runner code are all unmodified and byte-identical to `f224e7d`/`82f27c0`.** This
deviation is disclosed, not concealed. **Implication (stated, not fixed by Red Team):** the audited end-to-end
CLI is not real-data-ready; it needs a documented sub-tick tolerance or an explicit normalization step before
a clean end-to-end real-bar run through the CLI is possible.

## B.3 — Single execution + freeze

Smoke test on the synthetic dev fixture first (no real bars). Then `RUN_ATTEMPT=1`: 48 windows / 13,824 real
canonical bars (`ts_close=i*900`, mirroring the construction convention; detector spans are relative bar
indices and `atr14` is count-based, so absolute ts is immaterial). `predictions.json` sha256
`1754c86d…` (independently re-hashed), written read-only, copied to the Red Team escrow; only the hash +
sanitized manifest committed. No re-run after data access.

## B.4 — Metrics (§16) — real bars, audited `82f27c0` scorer, denominators 88 / 12 / 26-separate

```
MACRO      GT 88 · matched 62 · detected 116 · recall 0.705 · precision 0.534 · F1 0.608
           IoU {p25 0.300, median 0.439, p75 0.583, max 0.896} · confirm-delay mean 60.8 / median 29 · missed 26 · FP 64
INTERNAL   GT 12 · matched  1 · detected  25 · recall 0.083 · precision 0.040 · IoU median 0.415
UNRESOLVED 26 (reported separately, never in a recall denominator)
by length (MACRO matched/total)  96: 15/25 (0.60) · 288: 24/33 (0.73) · 480: 23/30 (0.77)
by block  B1 15/24 · B2 16/22 · B3 12/19 · B4 19/23
events    sweep_confirmed 79 · breakout_accepted 107 · liquidity_sweep_reversal 9 · promotions 90
funnel    total 689 · macro_new 116 · internal_new 25 · refused_partial_overlap 538 · refused_depth_limit 0 · refused_unresolved 10
top reason codes  BETWEEN_EPISODES 14476 · ESTABLISHING_FEW_SWINGS 8193 · OK_RANGE_MACRO 2575 · TOO_SHORT_MACRO 1337 ·
                  NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT 334 · OK_RANGE_INTERNAL 262 · ZONES_DEGENERATE 230 · ZONES_INVERTED 24
macro states  RANGE_FORMING 8898 · RANGE_CONFIRMED 2575 · EPISODE_CLOSED 216 · TREND_UP 205 · TREND_DOWN 117 · SWEEP_CONFIRMED 67
```

## B.5 — Real vs synthetic (§17) — no recalibration

| metric | synthetic (circular) | real | delta | responsible gate / reading |
|---|---|---|---|---|
| MACRO matched / 88 | 57 | **62** | +5 | more CEO-labeled MACRO ranges found on real bars |
| MACRO recall | 0.648 | **0.705** | +0.057 | — |
| MACRO precision | 0.445 | **0.534** | +0.089 | fewer spurious confirmed ranges relative to detections |
| MACRO IoU median | 0.770 | **0.439** | **−0.331** | synthetic bars were built *from* the label spans → boundaries aligned; real bars align only moderately |
| INTERNAL matched / 12 | 2 | **1** | −1 | level-2 detection weak on both, worse on real (F4) |
| sweeps | 209 | **79** | −130 | synthetic geometry exaggerated sweeps; real bars far fewer clean sweeps |
| breakouts | 112 | **107** | −5 | stable |
| reversals | 21 | **9** | −12 | fewer confirmed liquidity-sweep reversals on real bars |
| promotions | 94 | **90** | −4 | stable |
| funnel total | 725 | **689** | −36 | fewer total structure attempts |

Reading: on **MACRO** the detector recognizes the CEO-identified ranges on real, previously-unseen OHLC with
recall and precision **higher** than the circular synthetic baseline — a genuinely encouraging first real-bar
signal — but fits their boundaries more loosely (IoU median 0.44 vs 0.77), the honest cost of leaving a corpus
whose bars were synthesized from the labels. On **INTERNAL** the detector is effectively non-functional on real
bars (1/12). Nothing was tuned to close any gap.

## B.6 — Bar-by-bar examples (§18) — abstract IDs + relative in-window indices only

```
MACRO detected correctly   BLIND-048 L480 GT[35,105) det[36,112) IoU 0.896 confirm@65
                           BLIND-043 L96  GT[20,80)  det[16,86)  IoU 0.857 confirm@45
                           BLIND-003 L288 GT[70,98)  det[70,104) IoU 0.824 confirm@99
MACRO missed               BLIND-001 L288 GT[72,120) det None · BLIND-002 L96 GT[56,96) det None · BLIND-006 L96 GT[58,96) det None
MACRO false positive       BLIND-002 L96 det[7,39) confirm@36 (matches no GT; same window also misses its GT range)
INTERNAL correct (only 1)  BLIND-022 L288 GT[155,190) det[173,196) IoU 0.415
INTERNAL missed            BLIND-009, BLIND-012, BLIND-019, BLIND-034, BLIND-037 … (11 of 12)
sweep                      BLIND-001 bar 187 (MACRO)      breakout   BLIND-001 bar 201 (MACRO)
liquidity-sweep reversal   BLIND-001 bar 195 (MACRO)      promotion  BLIND-001 bar 205 (IS_TREND_MACRO)
unresolved                 BLIND-003 bar 13               killed candidate  PARTIAL_OVERLAP_NO_CONTAINMENT (538 total); ZONES_DEGENERATE 230 / ZONES_INVERTED 24
boundary case              BLIND-002 (simultaneous miss + false positive — a range found in the wrong location)
```

---

## C — CONSOLIDATED FINDINGS (single list)

1. **F1 · MATERIAL — audited CLI not real-data-ready.** `blind_runner/inference.py` rejects 13/13,824 real
   bars (sub-tick 0.0005 close/open-vs-high/low vendor artifact) at input validation. Detector executed via
   its own engine path with OHLC unmodified; disclosed. Minimal fix (Red Team does not implement): a documented
   sub-tick tolerance or explicit pre-normalization in the runner, then a clean end-to-end CLI re-run.
2. **F2 · NON-BLOCKING — `window_list_sha256` unreproduced** → `NON_BLOCKING_REDUNDANT_UNREPRODUCED_META_ANCHOR`
   (identity fully subsumed by payload SHA-256 + HMAC + 48 reproduced `bars_sha256`; §A.5).
3. **F3 · NON-BLOCKING — quantization floor 1e-6.** Documented anchor property (2e-6 firmly detected; 1000×
   margin over one XAUUSD tick). Not a defect.
4. **F4 · SEMANTIC DIAGNOSTIC — INTERNAL collapses on real bars** (1/12, recall 0.083; IoU median 0.415 on its
   single match) and MACRO boundary fit drops to IoU median 0.439 vs synthetic 0.770. A behavior finding, not a
   package-integrity defect → `RANGE_V4_3_DIAGNOSTIC_REVIEW_REQUIRED` for level-2.
5. **Minor — `manifest_entry_fingerprint_M15_v2` (`5d1cccab…`) not reproduced by Red Team's serialization**,
   but the load-bearing property (byte-invariance of the `M15_v2` entry across v2.7.92/93/94) was verified by
   direct comparison. Non-load-bearing.

No integrity/contamination/substitution/non-reproducibility defect of the escrow package was found — Phase A
FAIL conditions are not met. F1 is an execution/runner-contract finding surfaced transparently, not a forced PASS.

## D — SCIENTIFIC CLASSIFICATION (mandatory)

```
CORPUS_SEMANTIC_STATUS            = CEO_ASSISTED_CONSTRUCTION_CORPUS
REAL_OHLC_PREVIOUSLY_UNSEEN_BY_VE = TRUE
LABELS_USED_IN_V4_3_DESIGN        = TRUE
INDEPENDENT_SEMANTIC_BLIND        = FALSE
BLIND_PASS_NOT_PERMITTED
```

This run validates: escrow reproducibility, execution integrity, real-bar behaviour, preliminary utility, and
the real-vs-synthetic delta. It does **not** validate independent semantic performance. Forbidden verdicts
(`BLIND_PASS`, `SEMANTIC_PASS`, `FINAL_VALIDATION_PASS`, `STRATEGY_CATALOG_READY`, `ALPHA_AUTHORIZED`) are not
emitted. No wheel / Strategy Catalog / Alpha / AI Trader / LIVE_SHADOW / broker / trade authorized.

## E — DISPOSITION

The MACRO real-bar signal (recall 0.705 / precision 0.534 on previously-unseen real OHLC, above the circular
baseline) is promising enough to justify **`NEW_INDEPENDENT_BLIND_LABEL_BATCH_PREPARATION_RECOMMENDED`** — a
truly independent (non-CEO-assisted) blind batch, on real sealed bars, is the correct next step to convert this
into semantic evidence. In parallel, **`RANGE_V4_3_DIAGNOSTIC_REVIEW_REQUIRED`** for the INTERNAL level (F4) and
the runner input-gate fix (F1). Both are recommendations to the CEO; Red Team authorizes neither the wheel nor
any downstream integration.

---

*Red Team · `SEALED/OOS_ACCESS=0` beyond the mandate's authorized sealed bars · detector/runner/config/labels/
mapping/anchors unmodified · changes only in `red_team/` · LEDGER E85 (prev_hash E84).*
