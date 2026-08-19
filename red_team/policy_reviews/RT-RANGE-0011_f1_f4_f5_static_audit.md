# RED TEAM — RANGE V4 · F1 + F4 + F5 STATIC AUDIT + VE DELTA AUTHORIZATION
### RT-RANGE-0011 · Auditor: Red Team · 2026-08-20

---

## 0 — VERDICTS

```
RANGE_V4_F1_F4_F5_STATIC_AUDIT_PASS
RANGE_V4_F1_INPUT_CONTRACT_APPROVED_FOR_VE
INTERNAL_SEMANTIC_CHANGE_NOT_JUSTIFIED_CONFIRMED
F5_EXISTING_CONTRACT_CONFORMANCE_FIX_APPROVED_FOR_VE
MACRO_V4_3_REMAINS_FROZEN
INTERNAL_CAPABILITY_STATUS_RESEARCH_ONLY_NOT_VALIDATED
MACRO_INDEPENDENT_BLIND_PATH_AUTHORIZED_AFTER_VE_PATCH_AUDIT
VE_IMPLEMENTATION_ACCEPTANCE_GATE_REQUIRED (CLI-after-patch must equal predictions 46a9576)
INTERNAL_MUST_NOT_BLOCK_MACRO_INDEPENDENT_BLIND_PATH = TRUE
MANDATORY: INDEPENDENT_SEMANTIC_BLIND=FALSE · BLIND_PASS_NOT_PERMITTED · VALIDATION_WEIGHT=ZERO
```

No material defect of the Statistician's package was found. F1, F4, and F5 were each reproduced
independently and confirmed. No BLIND PASS; no wheel / Alpha authorization. All changes confined to
`red_team/`; nothing in the Statistician's package or VE code was modified.

**Sources verified from Git:** all mandated commits exist; `local=remote` on all four mirrors — package
`f1_input_contract/` at `alpha-automation-v1@870d3f8` (fp `662b3bca…`), report `statistician-foundation@ceb6b66`.
Frozen predictions independently re-hashed `1754c86d…` (= `46a9576`). Detector `f224e7d` / runner `82f27c0`
byte-identical (empty diff); the F1 package is a **new, separate input contract**, not a runner patch.

---

## F1 — INPUT VALIDATOR TOLERANCE · **PASS**

Reproduced independently from the canonical corpus (aggregates + relative indices only):

| claim | Red Team result |
|---|---|
| bars rejected | **13 / 13,824** |
| field | **`close` 13 · `open` 0** (refines RT-0010's "close or open") |
| direction | **above high 9 · below low 4** |
| magnitude | single nominal **0.0005** (float64: 7× `0.0004999999998744897`, 6× `0.0005000000001018634`) |
| per length | 96:1 · 288:6 · 480:6 · distinct windows 6 |
| rule A `min_tick/2 = 0.005` | **tolerates 13/13** |
| rule B `0.0005` | tolerates **7/13** (the 6 float64-over-nominal fail) → correctly REJECTED as a rule that rejects its own data |

**Formula `ohlc_validation_epsilon = min_tick/2`** is **derived, not a hidden literal**: `MIN_TICK=0.01` is
already normative — declared in `SymbolMeta` (`tick_size=0.01`) across four AI-Trader subsystems and ratified
in `RT-AUDIT-MEAS-0001` (which corrected a wrong 0.1 there). `0.005 < 0.01` (one tick), so a whole-tick data
error can never be masked. The Statistician's own published figure (`BARS_SHA256_SPEC` said "tick 0.001")
was self-corrected to 0.01 (their 14th self-caught figure error) — good faith; conclusion only strengthens.

**Comparison form verified:** the contract compares **value vs shifted boundary** (`v > hi+eps` / `v < lo-eps`,
strict-reject), NOT difference-vs-epsilon. I confirmed the float64 edge exactly: `close = high+eps`
constructed exactly → **tolerated** (emits event, no raise); `high+eps + 1 ULP` → **rejected**
(`CLOSE_OUTSIDE_HIGH_LOW`). The difference form would wrongly reject the equality the contract admits.

**Quality event `INPUT_OHLC_SUBTICK_TOLERATED`:** independently verified **outside** the 29 semantic reason
codes (count 0 in the frozen detector). Contract is **stateless** → determinism, chunk-invariance, and
restart/snapshot survival are structural, not accidental. It **does not modify OHLC** — the decisive test
`test_21` (13 real bars tolerated, `seen==13824`, values byte-unchanged) **passes**; the detector receives
identical bytes.

**Tests:** **28 collected — 27 pass, 1 skip**, `mypy --strict` clean. The single skip is `test_20`
(quality-event-not-a-reason-code) which env-skips when the detector isn't in the F1 checkout; I verified that
exact property independently, so nothing is lost.

**VE acceptance gate.** The condition "CLI predictions after the patch = frozen `46a9576`" is **not
demonstrable here** — the Statistician mandate forbade modifying the runner, so the patched CLI does not exist.
This is `VE_IMPLEMENTATION_ACCEPTANCE_GATE_REQUIRED`, a gate on VE's implementation, **not** a defect of the
Statistician's package. The necessary condition (zero OHLC modification → identical detector input) is proven.

---

## F4 — INTERNAL DIAGNOSTIC · **INTERNAL_SEMANTIC_CHANGE_NOT_JUSTIFIED — CONFIRMED**

Reproduced independently from the frozen predictions **without importing the scorer**. The 12-case table
matches **exactly** (per-bar records used to distinguish generated-but-killed from never-generated):

```
cause                                   Red Team   Statistician
PARENT_UNAVAILABLE (no confirmed MACRO)    6/12        6/12   ← dominant (50%)
CANDIDATE_NOT_GENERATED (parent OK)        4/12        4/12
CANDIDATE killed at touch (BLIND-009)      1/12        1/12
TRUE POSITIVE (BLIND-022, IoU 0.415)       1/12        1/12
```

- **1/12** reproduced exactly; **11/12 have IoU exactly 0**. Thresholds **0.5→0, 0.3→1, 0.2→1, 0.1→1** — not
  a boundary/threshold artifact. **Detector-side, not scorer** (reproduced without the scorer).
- **`d_internal=12` is not the cause:** `TOO_SHORT_INTERNAL` = 31 bars of 13,824; ≤1 of the 12 GT spans touch
  it, and that one's dominant reason is `ESTABLISHING_FEW_SWINGS`, not duration.
- **Not structural degeneracy:** INTERNAL GT span width / ATR14 median ≈ 4.85; **0/12 below** the 1.60
  degenerate threshold — INTERNAL segments are as wide as MACRO. (The Statistician's own competing hypothesis,
  disclosed and rejected before publication — good faith.)
- **Decision sound:** 6/12 depend on a **missing confirmed MACRO parent** — a propagated MACRO miss (MACRO
  recall 0.705 → 26/88 missed, inherited downward). These are **not repairable at the INTERNAL level without
  touching frozen MACRO** (§3 forbids). Only **4/12** are localized to internal candidate generation — `n=4`
  is too small for a leave-one-out/robust rule; any rule derived from four cases would be **memorization**.
  Therefore no single dominant *localized* cause exists → `INTERNAL_SEMANTIC_CHANGE_NOT_JUSTIFIED` confirmed.
  `INTERNAL_CAPABILITY_STATUS = RESEARCH_ONLY_NOT_VALIDATED`; `INTERNAL_MUST_NOT_BLOCK_MACRO_INDEPENDENT_BLIND_PATH = TRUE`.

---

## F5 — `tol_cluster` UNITS NONCONFORMITY · **F5_EXISTING_CONTRACT_CONFORMANCE_FIX_REQUIRED**

Confirmed at the source (`range_semantic_v4_3.py` @ `f224e7d`):

```
def tol_cluster -> 2.0 * w_atr = 1.60      # a DIMENSIONLESS ATR-MULTIPLE (whole cluster-membership band)
line 442  cl.offer(price, cfg.tol_cluster * st.atr_ref)      # SCALED → absolute USD  (NORMATIVE)
line 745  abs(price - boundary) <= self._cfg.tol_cluster     # UNSCALED → treats 1.60 as 1.60 USD  (BUG)
          # comment claims "SAME normative tolerance used by Cluster.offer, no invented value" — the code does NOT implement that identity
```

Independently measured on the real bars: median ATR14 ≈ **1.873 USD** → normative band
`tol_cluster×atr_ref` median **2.997 USD** vs implemented **1.600 USD**; the contractual band is **wider on
87.5%** of bars (claim 87.2%).

1. **Normative formula = `tol_cluster × atr_ref`** (line 442 usage + `tol_cluster` defined as an ATR-multiple
   + the comment's own asserted identity). Line 745 uses the dimensionless multiple as an absolute USD
   distance — a genuine **units nonconformity**.
2. **It violates the existing contract** → this is an **implementation conformance fix, not a semantic change**
   (no new constant, no new formula; the normative unit convention already exists at line 442).
3. **File / fix:** `range_semantic_v4_3.py` line 745 → `... <= self._cfg.tol_cluster * self._active_macro.atr_ref`
   (mirroring line 442's `st.atr_ref`; `_active_macro` is a `Structure` carrying `atr_ref`).
4. **Direction — decide on conformance, NOT recall:** the correct (wider) band makes the boundary-retest filter
   fire **more** often → **fewer** INTERNAL candidates → **lower** recall. So F5 is **not** the artificial fix
   for F4's recall; it must be justified purely as conformance, exactly as the Statistician states.
5. **MACRO isolation:** line 745 is guarded by `if forming_internal and self._active_macro is not None` — it is
   strictly on the `forming_internal` path. **MACRO formulas, boundaries, config, and output are unaffected.**
6. **Identity / snapshot gating:** the fix changes detector *behaviour* on the forming-internal path, so the
   **code fingerprint** of `range_semantic_v4_3.py` changes and a **new prototype identity** is required.
   `config_id` (`24f72a60…`) does **not** change (config values are unchanged; only their usage), so the
   snapshot/version gate — which keys on `config_id`/`contract_version` — would NOT refuse pre-fix snapshots by
   default. **VE must ensure the new code fingerprint participates in snapshot/version gating so pre-fix
   snapshots are refused** (a real cross-version-restore hazard, flagged for VE).
7. **Mandatory tests (VE):** units test (745 scaled by `atr_ref`); forming-internal filter regression;
   MACRO-output-unchanged regression; pre-fix-snapshot-refused test.

---

## PASS/FAIL MATRIX

| § | requirement | result |
|---|---|---|
| 4 | F1 reproduced (13, all close, sub-tick, tick normative) | PASS |
| 5 | F1 formula `min_tick/2`, value-vs-boundary, equality behaviour | PASS |
| 6 | F1 quality event outside 29 codes, deterministic, stateless, no OHLC change | PASS |
| 7 | F1 28 tests + mypy strict | PASS (27 pass / 1 benign env-skip / mypy clean) |
| 8 | F4 12-case table reproduced (no scorer) | PASS — exact 6/4/1/1 |
| 8 | 1/12, 11 zeros, thresholds invariant, d_internal & degeneracy not cause | PASS |
| 9 | F4 decision `INTERNAL_SEMANTIC_CHANGE_NOT_JUSTIFIED` | CONFIRMED |
| 10 | F5 normative formula, conformance-vs-semantic, MACRO isolation, direction | PASS — conformance fix, MACRO isolated, not a recall fix |
| 11 | scope decision (VE authorized set) | delivered below |

## AUTHORIZATION MATRIX (§12)

| Component | Status | VE may implement |
|---|---|---|
| F1 validator | **PASS** | **YES** |
| F1 quality event | **PASS** | **YES** |
| F4 semantic change | **NOT JUSTIFIED** | **NO** |
| F5 conformance fix | **REQUIRED** | **YES** |
| MACRO | **FROZEN** | **NO** |
| INTERNAL | **RESEARCH_ONLY_NOT_VALIDATED** | **NO (for integration)** |
| MACRO blind path | **OPEN** (after VE-patch audit) | — |

**VE is authorized to implement ONLY:** (1) the F1 validator patch, (2) the F1 quality event, (3) the F5
conformance fix, (4) the versioning / code-fingerprint / snapshot gating those require, (5) the associated
tests. **Forbidden for VE:** any MACRO change, `d_internal` change, touch relaxation, a third level,
per-window rules, recalibration on the 48 cases, scorer modification, new blind-batch access.

## CONSOLIDATED FINDINGS (single list)

1. **F1 — PASS.** Validator + quality event correct, derived, exact at equality, fail-closed above tolerance,
   stateless, OHLC untouched. Approved for VE. Acceptance gate: patched-CLI predictions must equal `46a9576`.
2. **F4 — decision confirmed.** `INTERNAL_SEMANTIC_CHANGE_NOT_JUSTIFIED`; INTERNAL is `RESEARCH_ONLY_NOT_VALIDATED`
   and must not block the MACRO independent-blind path.
3. **F5 — conformance fix required and approved for VE.** Real units bug at line 745; normative formula is
   `tol_cluster × atr_ref`; MACRO isolated; fixing it lowers INTERNAL recall (conformance grounds only).
   VE must gate pre-fix snapshots on the new code fingerprint (config_id unchanged is a restore hazard).
4. **Non-blocking observation (out of RANGE scope, flagged, not resolved):** `SymbolMeta` declares
   `price_precision=2`, but the real M15 corpus carries up to 4 decimals (confirmed) — an instrument-spec vs
   feed-precision mismatch the Statistician raised. Worth a separate data-governance note; does not affect this
   audit.
5. **Good-faith self-corrections by the Statistician** (published tick figure 0.001→0.01; a pre-published
   INTERNAL-width hypothesis rejected on measurement) are recorded as strengthening, not weakening, the package.

No material defect (implementable ambiguity, missing formula, semantic contradiction, contamination,
compromised integrity, missing normative artifact) was found → **`RANGE_V4_F1_F4_F5_STATIC_AUDIT_PASS`**.

## SCIENTIFIC CLASSIFICATION

```
INDEPENDENT_SEMANTIC_BLIND = FALSE · BLIND_PASS_NOT_PERMITTED · VALIDATION_WEIGHT = ZERO
MACRO baseline (frozen, unchanged): 62/88 · recall 0.705 · precision 0.534 · F1 0.608 · IoU-median 0.439 · INTERNAL 1/12
```

Not authorized regardless: BLIND PASS, wheel, Strategy Catalog, Alpha, AI Trader, LIVE_SHADOW, broker, trades.
The MACRO independent-blind path is authorized **only after** Red Team audits VE's F1+F5 patch.

---

*Red Team · detector/runner/scorer/labels/escrow unmodified · changes only in `red_team/` · LEDGER E86 (prev E85).*
