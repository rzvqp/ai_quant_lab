# RED TEAM — VE HANDOFF VERIFICATION · `ve_brain` @ `bd60c7a`
### RT-HANDOFF-0001 · 17 range conditions · .state lead · BREAKOUT_TRANSITION · simultaneity · router bypass · A5
**Date:** 2026-08-13 · **Auditor:** Red Team · **Target:** the delivered artifact `ve_brain/` @ `bd60c7a` (router multi-axial, 23 VE tests). Per CEO: I attack the **artifact**, not the AI-Trader repo (integration not started). **No engine modified; no repair; no real data.** Verified on imported source @`bd60c7a` + executed fixtures.

# VERDICT — **VE_HANDOFF_FAIL**
**Two hard failures + A5 not imposed + the artifact is pinned to the A2-rejected evaluator.** The router *itself* is genuinely multi-axial and the range block is correctly built **inside the router** — but the router is **bypassable at N6**, so the whole gate (range fail-closed included) does not hold end-to-end; and the `.state` lead is **not closed** — it moved from `market_intelligence` to N1's single `volatility` axis, which still makes COMPRESSION and BREAKOUT_TRANSITION mutually exclusive. PASS is forbidden.

## ENUMERATED DEFECTS (defect · file · line/path · fixture · observed · required · owner)

### 🔴 FAIL-1 — ROUTER_BYPASS (Objective 5, the decisive one)
- **defect:** `decide_n6` never requires an `EligibilityDecision`; it never calls `StrategyRouter`, `applicable_regimes`, or `_declares_range`. The range fail-closed lives **only** in `StrategyRouter.route_one`, so any strategy reaches EV by constructing a `DecisionRequest` directly.
- **file · path:** `ve_brain/n6.py::decide_n6` (whole body); `ve_brain/contracts.py::DecisionRequest` (no eligibility-proof field).
- **fixture (reproducible):** `decide_n6(DecisionRequest(strategy_id="RANGE_STRAT", regime_label="RANGE", validation_status=RATIFIED, all levels available, EV-positive probability_inputs))`.
- **observed:** `decision = TRADE`, `reason = TRADE_VALIDATED_EDGE`. **A range strategy obtains a real-execution TRADE.**
- **required:** N6 must require proof the router passed (an `EligibilityDecision`), and re-assert the range fail-closed → `TRUE_RANGE_NOT_IDENTIFIABLE` / `NO_TRADE`. **Any path calling EV without an EligibilityDecision = ROUTER_BYPASS.**
- **owner:** VE. *(This is the bypassable-guard pattern a third time — after E2E-L2 direct construction and `compare()` un-wired.)*

### 🔴 FAIL-2 — IMPLICIT_PARTITION_BY_EXPANSION_STATE (Objective 2, the .state lead is NOT closed)
- **defect:** `applicable_regimes` consumes a **single `volatility` string**, not the raw `is_compressed`/`is_displacement` flags. COMPRESSION keys on `volatility=="compressed"` and BREAKOUT_TRANSITION on `volatility=="high_directional"` — **mutually-exclusive values of one axis** → they can **never** co-occur, and a bar that is both compressed and displacement loses one axis **before** the router sees it. The partition simply moved from `market_intelligence/expansion.py::_state_for` to N1's volatility axis; it is not eliminated.
- **file · line:** `ve_brain/regime_routing.py:63` (`applicable_regimes(volatility: str, ...)`), `:69` COMPRESSION, `:71` BREAKOUT_TRANSITION.
- **fixture:** `is_compressed=TRUE ∧ is_displacement=TRUE ∧ dir=UP ∧ strength=STRONG`. Exhaustive check: **no** `volatility` value yields `{COMPRESSION, BREAKOUT_TRANSITION}`. If N1 collapses (compressed+displacement) → `high_directional` (the `EXPANDING>COMPRESSED` precedence), **COMPRESSION is erased** and only TREND_UP survives.
- **observed:** COMPRESSION and BREAKOUT_TRANSITION structurally cannot co-exist; the router is blind to simultaneous compression+displacement.
- **required:** the router must consume the **raw** `is_compressed` **and** `is_displacement` (or a volatility **set**), so COMPRESSION survives when displacement co-occurs — exactly what the CEO forbids erasing.
- **owner:** VE (router input contract) + confirm N1's volatility-axis derivation does not collapse the two flags.

### 🟠 FAIL-3 — A5 NOT FULLY IMPOSED (Objective 6)
- **(a) block_end absent.** `decision_fingerprint` has no `block_end`; it delegates to `measurement_run_hash`, and the canonical `run_hash` **omits `block_end`** (my eleventh, still open). Fixture *"same strategy+config, different block_end → different hash"* **fails** at the ve_brain boundary (same `measurement_run_hash` → same fingerprint). `ve_brain/fingerprint.py::decision_fingerprint`. Owner: VE.
- **(b) enforcement not wired.** `require_comparable`/`compare_decisions` exist and raise, but are **never called** inside `decide_n6` or `run_ev` (verified). Opt-in only. CEO: *"NU accepta require_comparable() daca ramane optionala si neapelata intern."* `ve_brain/fingerprint.py` + `n6.py`. Owner: VE.
- **PASSES within A5:** strategy_id **and** strategy_version are in the fingerprint (S1≠S3, v1≠v2 verified); **engine and contract are SEPARATE** identities (`d3_engine`, `d4_measurement_contract`, `d5_ve_brain` — fixes my earlier "conflated in code_version").

### 🟠 FAIL-4 — pinned to the A2-REJECTED evaluator
- **defect:** `version.py` sets `SOURCE_COMMIT = 3344bff…` and `MEASUREMENT_CONTRACT_VERSION = "canonical-evaluator-v2.7.66"` — the **asymmetric** evaluator the CEO **rejected** in A2. `reason_codes.py` declares `INVALID_EXECUTION = "risc≤0 OR recompensă≤0"` (strict-geometry wording), but the pinned measurement engine is the asymmetric one.
- **file:** `ve_brain/version.py` (`SOURCE_COMMIT`, `MEASUREMENT_CONTRACT_VERSION`).
- **required:** re-pin to the corrected **strict-geometry** evaluator once VE lands it; A2 remains open.
- **owner:** VE.

## WHAT PASSES (verified — so the FAIL is precise, not blanket)
- **Objective 4 — simultaneity: PASS.** `applicable_regimes("compressed","strong","up") = {COMPRESSION, TREND_UP}` — both present, set union, **no if/elif**. The retracted compression-over-trend precedence is gone. Multiple eligible strategies stay **separate** `EligibilityDecision`s (a tuple, one per strategy), not auto-combined. ✅
- **Objective 1 — the 17, at the router: PASS (but voided by FAIL-1).** `SemanticRegime.RANGE` is **never** emitted by `applicable_regimes` (exhaustive over all axis combos = False); no `else: range`, no fallback, "no match" → `UNCERTAIN`; a range-declaring strategy → `TRUE_RANGE_NOT_IDENTIFIABLE` **before** `UNCERTAIN` (condition 17, VE's self-correction, verified). These hold **inside the router** — but FAIL-1 lets N6 be reached without it.
- **Objective 3 — BREAKOUT_TRANSITION: PASS at the router.** `|run|=1` (structure="range") alone or with non-expansion vol → `UNCERTAIN` (not consolidation, not range); only `range + high_directional` → `BREAKOUT_TRANSITION`; warmup/Unavailable structure (None) → `UNCERTAIN`. Used as instability/break evidence, never consolidation. **Explicitly a PER-BAR PROXY** (documented lines 32–34), not a longitudinal 2-state detector — noted, not presented as complete. VE's argument ("warmup ⇒ structure Unavailable ⇒ |run|=1 needs a real break") holds **at the router** (structure=None→UNCERTAIN); the N1 side (warmup truly emits structure=None) is external and must be confirmed against N1.
- **Reason-code coverage:** every `EligibilityDecision` and `DecisionResponse` carries a stable `reason_code` (no free text, no hidden default). **But persistence/queryability (conditions 9/10) is delegated** — ve_brain **returns** codes; it has no store. CONDITIONAL: the data is present on every output; persistence is the consumer's.

## VERDICT — **VE_HANDOFF_FAIL**
PASS required: all 17 pass · `.state` lead closed · no implicit partition · no router bypass · A5 fixed **and imposed** · 12 deliverables present. **Blocked by:** FAIL-1 (router bypass → range strategy TRADEs), FAIL-2 (implicit partition; router uses a single collapsed volatility axis, not raw flags), FAIL-3 (block_end missing + enforcement un-wired), FAIL-4 (pinned to the A2-rejected asymmetric evaluator). The 12 deliverables **appear present** (installable `pyproject.toml`, `SOURCE_COMMIT`, `CONTRACTS.md`, schemas, EV adapter, tests, canonical fixtures, `DEPENDENCIES.md`, `INSTALL.md`, `BROKER_ORDER_SUBMISSION=DISABLED` + validation-status gate, `CHANGELOG.md`) — but presence does not cure the four defects. **Mandate 2 to AI Trader is NOT authorized.**

## HANDOFF → CEO / VE
1. **FAIL-1 (blocking):** make N6 require an `EligibilityDecision` (route proof) and re-assert the range fail-closed at the N6 boundary; forbid any EV call without it.
2. **FAIL-2 (blocking):** route on the raw `is_compressed`/`is_displacement` axes (or a volatility set) so COMPRESSION and BREAKOUT_TRANSITION can co-occur; confirm N1 does not collapse the two flags.
3. **FAIL-3:** add `block_end`/actual cut to the measurement `run_hash` and **wire `require_comparable` into every comparison/aggregation path** (not opt-in).
4. **FAIL-4 / A2:** re-pin to the corrected strict-geometry evaluator once delivered.
5. **Re-submit** for handoff re-verification; until then **VE_HANDOFF_FAIL** stands and Mandate 2 is not authorized. A2 and A5 remain open independently.

Red Team designed no remedy, modified no engine, ran no data on the market, changed nothing outside `red_team/`.
