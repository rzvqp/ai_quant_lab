# RED TEAM — RANGE V4.3 F1 + F5 IMPLEMENTATION AUDIT
### RT-RANGE-0012 · Auditor: Red Team · 2026-08-20 · audited build `69af414`

---

## 0 — VERDICT

```
RANGE_V4_F1_F5_IMPLEMENTATION_AUDIT_FAIL
```

**One material defect blocks the freeze: F5 changes MACRO on real bars.** F1 is fully correct and, in
isolation, reproduces the frozen baseline exactly. But the F5 fix — although implemented faithfully to the
RT-RANGE-0011 authorization — is MACRO-isolated only in *code location*, not in *effect*: on real bars (real
ATR ≠ 1.0) it shifts MACRO output and **moves the frozen MACRO baseline from 62/88 (recall 0.705) to 58/88
(recall 0.659)**. VE's MACRO byte-identity test does not catch this because it runs the synthetic
construction windows with `atr=1.0`, where the fix `tol_cluster × atr_ref` = `tol_cluster × 1.0` is an exact
no-op. The patched build therefore **cannot be frozen** for MACRO independent-blind preparation.

```
INDEPENDENT_SEMANTIC_BLIND = FALSE · VALIDATION_WEIGHT = ZERO
MACRO_V4_3_BYTE_IDENTITY_AFTER_F5_CONFIRMED = FALSE
RANGE_V4_3_PATCHED_BUILD_FROZEN = FALSE · MACRO_INDEPENDENT_BLIND_PREPARATION_AUTHORIZED = FALSE
WHEEL_AUTHORIZED = FALSE · ALPHA_AUTHORIZED = FALSE · AI_TRADER_INTEGRATION_AUTHORIZED = FALSE
```

Nothing modified to force any result; changes only in `red_team/`. All commits verified from Git with
`local=remote` on all four mirrors; `69af414` (branch `discovery-mk-matrix-v1`, parent `82f27c0`) audited
directly.

---

## 1 — THE MATERIAL DEFECT (F5-MACRO-LEAK)

**Baseline verified first:** re-running the pre-F5 detector (`82f27c0`, hash `2aba333c`) on the 48 real
canonical windows reproduces the frozen predictions `46a9576` (hash `1754c86d`) **exactly, 48/48**. The
baseline is sound.

**F5 changes MACRO on real bars** (post-F5 detector `70e30b3a` vs pre-F5, same real bars, same config):

| MACRO comparison (real bars) | result |
|---|---|
| MACRO geometry differs (start/confirm/end/boundaries/reason/**role**, excluding structure_id) | **12 / 48 windows** |
| MACRO-depth events differ (bar, kind, excluding structure_id) | **12 / 48 windows** |
| MACRO-depth SWEEP_CONFIRMED | 67 → **59** |
| MACRO-depth BREAKOUT_ACCEPTED | 96 → **93** |
| MACRO-depth LIQUIDITY_SWEEP_REVERSAL | 7 → **6** |
| MACRO-depth IS_TREND_MACRO (promotions) | 90 → **89** |
| **Frozen MACRO baseline (scored vs labels)** | **62/88 (recall 0.705) → 58/88 (recall 0.659)** |

Concrete example (BLIND-004): a confirmed MACRO structure's role flips `TREND_CONTINUATION_CONFIRMED → None`
and the trailing structure's confirm timing shifts (`start 449 confirm 478 → start 460 confirm None`).

**Mechanism.** The F5 line correctly scales by ATR and is guarded by `forming_internal`, so it only *decides*
whether a new INTERNAL candidate is suppressed. But INTERNAL candidate formation is **not state-isolated from
MACRO**: (a) the structure-id counter is shared MACRO/INTERNAL, so suppressing a candidate renumbers later
MACRO structures; (b) INTERNAL candidates can be **promoted to MACRO** (`IS_TREND_MACRO`), so suppressing them
changes the MACRO population; (c) pending-swing / `_active_internal` state feeds back into MACRO processing.
On real bars the normative band `tol_cluster × atr_ref` (median ≈ 2.997 USD) is much wider than the buggy
`1.60 USD`, so many more candidates are suppressed — and those suppressions propagate into MACRO. F5 is
MACRO-isolated in *where the code sits*, not in *what it changes*.

**Why VE's proof missed it.** VE's `test_macro_byte_identity_projection_hash_48_windows` runs the 48
**synthetic** construction windows through `prod.observe(..., atr=1.0)`. With `atr_ref = 1.0`, the fix
`tol_cluster × atr_ref = tol_cluster × 1.0 = tol_cluster` is byte-identical to the pre-F5 line — F5 is a
complete no-op, INTERNAL included. So the "973 MACRO events, 0 mismatches" anchor is **vacuous**: it proves
identity only in the one regime where the fix does nothing. It never exercises real ATR.

This is not a hidden or bad-faith change — VE implemented exactly the line RT-RANGE-0011 authorized. The fault
is shared: RT-RANGE-0011's "MACRO isolated" finding was verified at the code-guard level, not behaviorally
(a self-correction this division records), and VE's regression test picked the one ATR value that hides the
effect. But for *this* audit the consequence is unambiguous: **the patched build's MACRO ≠ the frozen
baseline → FAIL by §3 and §7.**

---

## 2 — EVERYTHING ELSE (all PASS)

### F1 — validator, byte identity, freeze match (all PASS)
- **Formula:** `epsilon = min_tick/2 = 0.005`, derived from `SYMBOL_MIN_TICK={"XAUUSD":0.01}` (symbol metadata;
  unknown symbol → fail-closed `UNKNOWN_SYMBOL_MIN_TICK`); not a hidden literal.
- **Float64 form:** value-vs-shifted-boundary (`v > hi+eps` / `v < lo-eps` reject). Verified at the edge:
  `close = high+eps` exactly → **tolerated**; `+1 ULP` → **rejected**; `close = low-eps` → tolerated;
  `-1 ULP` → rejected. (Both boundaries.)
- **13 bars:** reproduced independently — 13/13,824, **all on `close`** (0 open), 9 above high / 4 below low,
  per length 96:1/288:6/480:6, 6 windows; eps 0.005 tolerates 13/13, nominal 0.0005 tolerates 7/13.
- **`F1_OHLC_BYTE_IDENTITY = TRUE`:** validated bars are byte-identical to the source (payload hash equal); the
  quality event carries the unmodified `original_value`; no clip/round/normalize/reorder/timestamp change.
- **Quality event `INPUT_OHLC_SUBTICK_TOLERATED`:** a separate `input_quality_events` channel in
  predictions.json (not mixed into semantic records); outside the 29 reason codes (count 0 in detector);
  relative `bar_index`; deterministic; stateless.
- **★ `F1_ONLY_PATCHED_CLI_PREDICTIONS_MATCH_FREEZE = TRUE`** — the decisive §5 gate VE reported as
  NOT_VERIFIABLE_HERE. Running VE's F1 validator + the **pre-F5** detector on the real bars reproduces the
  frozen `46a9576` semantic projection **48/48, hash `62273c1e…` identical**. F1 alone perturbs nothing
  semantic. (The 13 quality events and the byte-identical OHLC were compared as separate channels.)

### F5 — formula and units (PASS as a code change; but see §1 for the effect)
- Line 745 now reads `abs(price - boundary) <= self._cfg.tol_cluster * atr_ref` with
  `atr_ref = self._active_macro.atr_ref` — the dimensionless multiple (1.60) is correctly scaled to an
  absolute USD band, mirroring line 442. No bare `1.60`-USD comparison remains. ATR-causal: `atr_ref` is the
  frozen MACRO's own reference; when unavailable (`None`) the filter is not applied (fail-closed toward "not a
  re-test"). Two ATR values yield two bands; equality and immediately-beyond behave per contract. F5 has a
  **real, non-no-op effect** on INTERNAL (confirmed internal structures 25 → 20). The units conformance itself
  is correct — the problem is that its effect is not confined to INTERNAL (§1).

### Other gates (PASS)
- **Diff scope:** only F1 (`schemas.py`, `inference.py`), F5 + fingerprint + snapshot (`range_semantic_v4_3.py`,
  exactly 5 hunks, +33/−3), an identity-gate update in `scoring.py` (`prototype_commit → f224e7d+F1F5` +
  `implementation_fingerprint` check — **not** a scoring-logic change), tests, and docs. **No** MACRO-formula
  edit, **no** config/CEO-param change, **no** `d_internal`/touch/third-level/per-window/48-tuning, no scorer
  logic, no label/escrow/29-reason-code change, no Wheel/Alpha/AI-Trader/broker code.
- **F4 semantic absence:** confirmed — none of `d_internal`, parent-bypass, touch relaxation, duration cut,
  third level, per-segment rules, 12-case tuning, scorer/IoU-threshold change, or label-use-in-inference is
  present. `INTERNAL_CAPABILITY_STATUS = RESEARCH_ONLY_NOT_VALIDATED` unchanged.
- **Fingerprint / snapshot fail-closed:** `contract_version` = `range-hierarchical-v4.3` and `config_id` =
  `24f72a60…` both unchanged; `implementation_fingerprint = "f1-f5-conformance-2026-08-20"` added to the
  snapshot and enforced in restore *in addition to* config_id/contract_version. Verified: pre-F5 snapshot
  (no fingerprint) refused, wrong fingerprint refused, correct restore OK.
- **construction_reproduction pin:** pinned to `f224e7d`; refuses the post-F5 detector fail-closed with the
  correct byte-identity error — deterministic, not masking a regression (the active suites run separately).
- **Tests / mypy:** VE's active suites pass (94/94 in blind_runner+F5 here; VE reports 464/464 overall),
  `mypy --strict` clean on all four touched production files. **Caveat:** the passing suite includes the
  vacuous MACRO-identity test (§1) — green tests here do not establish MACRO identity on real bars.
- **Determinism / chunk / two-instances:** VE's F5 tests plus my own repeated pre/post runs are deterministic.

---

## 3 — MATRIX

| Section | Verdict |
|---|---|
| Sources & local=remote | PASS |
| Diff scope | PASS |
| F1 formula | PASS |
| Float64 equality/ULP | PASS |
| 13 bars | PASS |
| OHLC byte identity | PASS |
| Quality event separate | PASS |
| F1-only CLI freeze match | PASS |
| F5 formula & units (code) | PASS |
| ATR causal | PASS |
| **INTERNAL-only scope** | **FAIL** |
| **MACRO byte identity** | **FAIL** |
| F4 semantic absence | PASS |
| Fingerprint | PASS |
| Snapshot fail-closed | PASS |
| Construction reproduction pin | PASS |
| Tests (active suites) | PASS (MACRO-identity test vacuous) |
| mypy --strict | PASS |
| Determinism | PASS |
| Chunk invariance | PASS |
| Two instances | PASS |
| Leak scan | PASS |
| Audit limits | PASS |

---

## 4 — CONSOLIDATED FINDINGS

**Material (blocking):**
1. **F5-MACRO-LEAK.** On real bars, the F5 fix changes MACRO output (12/48 windows geometry; MACRO event
   counts shift; baseline 62/88 → 58/88). Violates §3 (MACRO frozen) and §7 (any MACRO difference = FAIL).
   Root: INTERNAL candidate suppression is not state-isolated from MACRO (shared structure-id counter,
   INTERNAL→MACRO promotion, shared pending-swing/active-internal state). VE's MACRO-identity anchor is
   vacuous (synthetic `atr=1.0` makes F5 a no-op).

**Non-blocking observations:**
2. VE's `test_macro_byte_identity_projection_hash_48_windows` should exercise **real (non-unit) ATR**, or be
   labelled as an `atr=1.0` no-op check; as written it cannot detect an F5→MACRO leak.
3. F1 is fully correct and freeze-preserving; nothing in F1 contributed to the failure.

**Remediation options (Red Team states, does not implement):**
- **(a)** Rework F5 so its effect is genuinely MACRO-isolated — e.g. give INTERNAL candidate formation its own
  id space and ensure forming-internal suppression cannot alter MACRO promotion or pending-swing state — then
  re-prove MACRO byte identity **on real ATR**; or
- **(b)** Ship **F1 only** now (proven to reproduce the 62/88 baseline exactly) and defer F5; the MACRO
  independent-blind path can proceed on the F1-only build without disturbing MACRO; or
- **(c)** Accept a new MACRO baseline established on the post-F5 build and re-audit it as a *changed* MACRO
  (this abandons "MACRO frozen at 62/88" and is a separate, larger decision — not authorized here).

Any of these requires a fresh VE delivery and a new Red Team audit before the build can be frozen.

---

## 5 — LIMITS / CLASSIFICATION

`INDEPENDENT_SEMANTIC_BLIND = FALSE`, `VALIDATION_WEIGHT = ZERO`. The 48 windows were used only for
reproduction/regression/identity — no new blind batch, no label use in inference, no recalibration, no
threshold change, no MACRO/INTERNAL/scorer modification. No BLIND PASS. Not authorized: freezing the build,
blind preparation, Wheel, Strategy Catalog, Alpha, AI Trader integration, broker/orders.

---

*Red Team · VE/Statistician/scorer/escrow/labels unmodified · changes only in `red_team/` · LEDGER E87 (prev E86).*
