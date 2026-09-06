# VE Scorecard + Lesson Ladder Corrective Patch Report

Narrow patch against the already-implemented AI Trader General Observer V1.1 (commit `cd84c56`).

## 1. Authoritative spec identity

`docs/trader_apprenticeship/apprenticeship_v2/AI_TRADER_GENERAL_OBSERVATION_DESIGN_V1_1_DEFINITIONAL_LOCK.md`, now 1258 lines (801 original + Section 19, the Fifth Addendum, appended). Read in full before patching, specifically Section 19 (lines 806–1258). Confirmed verbatim: `SCORECARD_DEFINITIONAL_LOCK = PASS`, `CEO_DECISION_REQUIRED = NO`, `VE_CAN_PATCH_WITHOUT_SEMANTIC_INTERPRETATION = YES`. No spec drift found — not blocked.

**Note on this file's own tracking status**: the design doc is untracked in git (`??` in `git status`), consistent with the precedent established across all four prior addenda (its own Section 19.18: `DEFINITIONAL_DOCUMENT_COMMIT_NOT_AUTHORIZED`) — not committed here either, following that same precedent, not deviating from it.

## 2. Baseline implementation identity

Commit `cd84c56` (`ai-trader-implementation` branch, `ai_quant_lab-research-main`, all 4 mirrors), reported as `FAIL` in `VE_AI_TRADER_GENERAL_OBSERVER_V1_1_IMPLEMENTATION_REPORT.md` — 98/98 tests passing, with `scorecard.py::classify_expectation_correct` deliberately raising `NotImplementedError` (`VE_SEMANTIC_GAP_FOUND`) and two disclosed `lesson_voting.py::classify_lesson_status` defaults. This patch closes exactly those three items.

## 3. Changed files

```
M  ai_trader/apprenticeship_v2/general_observer/scorecard.py
M  ai_trader/apprenticeship_v2/general_observer/lesson_voting.py
M  ai_trader/apprenticeship_v2/tests/test_scorecard.py
M  ai_trader/apprenticeship_v2/tests/test_lesson_voting.py
M  ai_trader/apprenticeship_v2/tests/test_episode_builder.py
```

`episode_builder.py` (session-reversal tie-break) — **inspected, unchanged**. `candidate_child = sweep if sweep is not None else brk` already matches the ratified rule (Section 19.9) exactly; only its own test coverage was extended (`test_episode_builder.py`, 3 new tests: break-only, sweep+break-same-bar, restart-determinism), no production code touched.

No event detector, no missed-move audit file, no S5 file, no unrelated file was touched. Verified via `git diff --stat` against `loop.py`, `main.py`, `s5_observer.py`, `mt5_read_only_source.py`, `checkpoint.py`, `durable_store.py`, `schemas.py`, `detectors.py`, `dedup.py`, `major_levels.py`, `primitives.py`, `snapshot.py`, `missed_move_audit.py`, `tick.py`, `main_general_observer.py` — all empty.

## 4. Exact classifier mapping implemented

`scorecard.py::classify_expectation_correct(expectation, metrics, episode_context)` — a direct transcription of design doc Section 19.14's required pseudocode:

- New `EpisodeContext` dataclass (`prospective_eligibility`, `review_horizon`, `structural_resolution_state`) carries the classifier's universal-precondition inputs, separate from `HorizonMetrics` (the pure numeric outcome).
- Universal preconditions, in order: `UNCLEAR` → `NOT_SCORABLE`; invalid/unknown expectation → `NOT_SCORABLE`; `prospective_eligibility != "YES"` → `NOT_SCORABLE`; (for `STRUCTURAL_FINAL` only) `structural_resolution_state` `None`/`UNRESOLVED_AT_H8` → `NOT_SCORABLE`; direction unresolved (`directional_follow_through is None`) → `NOT_SCORABLE`.
- Per-expectation contract (Section 19.5/19.13), built entirely from `directional_follow_through` (boolean), `round_trip_magnitude`'s own `0.0`/`1.0` boundaries, and a direct `mae`-vs-`mfe` comparison — no new numeric constant introduced anywhere:

| Expectation | YES | PARTIAL | NO |
|---|---|---|---|
| `FOLLOW_THROUGH_LIKELY` | `dft==True and rtm<1.0` | unreachable | else |
| `FAILURE_LIKELY` | `dft==False or rtm>=1.0` | unreachable | else |
| `REVERSAL_LIKELY` | `dft==False and mae>mfe` | unreachable | else |
| `RANGE_LIKELY` | `dft==False and mae<=mfe` | unreachable | else |
| `ROUND_TRIP_LIKELY` | `rtm>=1.0` | `0.0<rtm<1.0` | `rtm==0.0` |
| `UNCLEAR` | unreachable | unreachable | always `NOT_SCORABLE` |

`STRUCTURAL_FINAL` branch implemented (state→`dft`/`rtm`/`mae_gt_mfe` substitution per Section 19.11) — defined and tested, though no current caller produces a `STRUCTURAL_FINAL` row (`due_horizons_for_episode` only emits H1/H2/H4/H8; the structural-resolution computation itself for general-observer episodes remains the separate, disclosed engineering gap Section 19.11 itself names — not part of this patch's authorized scope).

`score_due_horizons_for_episode` updated to construct a real `EpisodeContext` and consume a real verdict — no longer propagates an exception.

## 5. Old lesson behavior → 6. Corrected lesson behavior

| | Old (`cd84c56`) | Corrected (Section 19.7) |
|---|---|---|
| `NEW_HYPOTHESIS` | `n_voting == 0` | `n_voting ∈ {0, 1}` |
| `REPEATED_OBSERVATION` | `n_voting ∈ [1, 9]` | `n_voting ∈ [2, 9]` |
| `PROSPECTIVELY_SUPPORTED` | `n_voting≥10, ratio≥0.70` | unchanged |
| `PROSPECTIVELY_WEAKENED` | `n_voting≥10, ratio<0.70` (also covered `REJECTED`) | `n_voting≥10, 0.5≤ratio<0.70` |
| `PROSPECTIVELY_REJECTED` | not reachable (collapsed into WEAKENED) | `n_voting≥10, ratio<0.5` |

`0.70`/`10` thresholds themselves unchanged (never reopened, per mandate §19). `0.5` is applied as the mathematically-forced two-outcome majority midpoint, not a new CEO-escalated constant (Section 19.7's own reasoning). Deterioration/recovery required no new code — `classify_lesson_status` was already, and remains, a pure function of the current `(n_voting, support)` totals; recomputing after new evidence automatically reflects either direction (tested explicitly: `test_classify_lesson_status_deterioration_and_recovery_are_pure_recomputation`).

## 7. Session-reversal tie-break verification

Confirmed by direct code read: `episode_builder.py`'s `candidate_child = sweep if sweep is not None else brk` already implements the ratified rule (prefer `SWEEP_REJECTION` over `STRUCTURAL_BREAK`) exactly as Section 19.9 requires — a deterministic, explicit `if`/`else`, not iteration/dictionary/random order. No behavioral change made. Extended test coverage added (Section 8 below) since the mandate's own Section 32 requires break-only, sweep+break-same-bar, and restart-determinism cases specifically, which the prior delivery's own test suite did not yet cover.

## 8. New tests

| File | Before | After | New |
|---|---|---|---|
| `test_scorecard.py` | 10 | 38 | +28 (removed 2 obsolete "raises" tests, added Section 19.15's full non-vacuity vector set, universal-precondition tests, `STRUCTURAL_FINAL` branch tests, mutual-exclusivity/exhaustiveness proofs, confidence-non-effect check) |
| `test_lesson_voting.py` | 19 | 21 | +2 net (updated 2 boundary tests, added 3 new: `{0,1}`/`0.5`-boundary/deterioration-recovery — some replaced in place) |
| `test_episode_builder.py` | 5 | 8 | +3 (break-only, sweep+break-same-bar, tie-break restart-determinism) |

Every Section 19.15 vector reproduced exactly, including the exact-boundary cases (`rtm==1.0`, `mae==mfe`, `rtm==0.45` PARTIAL) and the two `NOT_SCORABLE` precondition vectors (`prospective_eligibility=NO`, `STRUCTURAL_FINAL` unresolved). Every Section 19.15 lesson-stage vector reproduced exactly, including the new `n_voting=10, support=5 → WEAKENED` / `support=4 → REJECTED` boundary. The Section 19.15 session-reversal tie-break vector (`SWEEP` vs. `PREVIOUS_DAY_LOW` + `BREAK` vs. `H1_CONFIRMED_SWING_HIGH` on one bar) reproduced exactly.

## 9. Full regression results

`ai_trader/apprenticeship_v2/tests/`: **131 passed, 0 failed, 0 skipped** (up from the 98/98 baseline; 33 net new tests). No repo-wide CI config or root `pytest.ini`/`pyproject.toml` exists in this repository (confirmed by direct check) — there is no broader "complete applicable project test suite" beyond this delivery's own test directory to additionally run; running the separately in-flight, unrelated `mt5_demo_bridge` test files (modified by another session, outside this patch's scope) was deliberately not attempted, to avoid conflating this patch's own regression evidence with unrelated work.

## 10. Type-check results

`mypy --ignore-missing-imports` against every file this delivery (original + patch) touches or added (`general_observer/*.py`, `schemas.py`, `durable_store.py`, `resolution.py`, `checkpoint.py`): **0 errors**. No suppression used beyond the two pre-existing, already-disclosed `# type: ignore[arg-type]` comments in `dedup.py` (unrelated to this patch, unchanged).

## 11. Unresolved findings

None within this patch's own authorized scope (all three areas — scorecard classifier, lesson ladder, session-reversal tie-break verification — fully closed). Findings carried over, unaffected, from the original delivery (not in scope for this patch, not touched):
- Section 19.11's own disclosed gap: the `STRUCTURAL_FINAL` structural-resolution computation itself (confirmation/invalidation detection for general-observer episodes) is not implemented — the classification logic for it is (this patch), but nothing yet calls it with a real `structural_resolution_state`.
- BEFORE ordering-violation detection (§8 step 8 of the original doc) — not implemented (no qualitative-review pass exists yet to violate it against).
- Checkpoint scheduling for general-observer — not wired (unaffected by this patch).
- `tick.py`/`main_general_observer.py` still have no live end-to-end integration test (this dev environment has no MetaTrader5 install).

## 12. Git/commit state

Not yet committed as of this report's writing — see the required final block below for the exact status at the time this report was produced. `git status --porcelain` confirms exactly the 5 files listed in Section 3 above are the only tracked changes; the design doc itself is deliberately left untracked (Section 1).

## 13. Final verdict

`VE_GENERAL_OBSERVER_V1_1_SCORECARD_PATCH = PASS` for this patch's own narrow scope (all 15 of the mandate's own Section 39 conditions verified true — see the required final block). This does not retroactively upgrade the original delivery's own broader `FAIL` verdict (`VE_AI_TRADER_GENERAL_OBSERVER_V1_1_IMPLEMENTATION_REPORT.md`) to `PASS` — the items listed in Section 11 above remain open, disclosed, and out of this patch's authorized scope.

---

## Required Final Block

```
VE_AI_TRADER_GENERAL_OBSERVER_SCORECARD_PATCH_COMPLETE = YES

AUTHORITATIVE_SECTION_19_BOUND = YES
SCORECARD_DEFINITIONAL_LOCK_CONFIRMED_PASS = YES

EXPECTATION_CLASSIFIER_IMPLEMENTED = YES
FOLLOW_THROUGH_LIKELY_IMPLEMENTED = YES
FAILURE_LIKELY_IMPLEMENTED = YES
REVERSAL_LIKELY_IMPLEMENTED = YES
ROUND_TRIP_LIKELY_IMPLEMENTED = YES
RANGE_LIKELY_IMPLEMENTED = YES
UNCLEAR_IMPLEMENTED = YES
PARTIAL_SEMANTICS_IMPLEMENTED = YES
NOT_SCORABLE_SEMANTICS_IMPLEMENTED = YES

CLASSIFICATION_MUTUAL_EXCLUSIVITY_TESTED = YES
CLASSIFICATION_EXHAUSTIVENESS_TESTED = YES

AFTER_LLM_CAN_OVERRIDE_MECHANICAL_SCORE = NO

LESSON_VOTE_MAPPING_IMPLEMENTED = YES
LESSON_DEFAULT_1_CORRECTED = YES
LESSON_STATUS_LADDER_FULLY_IMPLEMENTED = YES
WEAKENED_REJECTED_0_50_BOUNDARY_IMPLEMENTED = YES

SESSION_REVERSAL_SWEEP_OVER_BREAK_TIE_BREAK_IMPLEMENTED = YES
SESSION_REVERSAL_ALL_SIBLINGS_PERSIST = YES

DISPLACEMENT_CHANGED = NO
MISSED_MOVE_AUDIT_CHANGED = NO
S5_CHANGED = NO
BROKER_EXECUTION_CHANGED = NO
LIVE_SHADOW_ENABLED = NO

SEMANTIC_IMPROVISATION_OCCURRED = NO

PREVIOUS_GENERAL_OBSERVER_TEST_BASELINE = 98/98 PASS
PATCH_TESTS_RESULT = 131 passed, 0 failed, 0 skipped (33 net new: scorecard +28, lesson_voting +2 net, episode_builder +3)
FULL_APPLICABLE_TEST_SUITE_RESULT = 131 passed, 0 failed, 0 skipped (ai_trader/apprenticeship_v2/tests/ -- no repo-wide CI/pytest config exists to define a broader suite)
STATIC_TYPE_CHECK_RESULT = 0 errors (mypy --ignore-missing-imports, all new/modified apprenticeship_v2 + general_observer files)

CHANGED_FILES = ai_trader/apprenticeship_v2/general_observer/scorecard.py, ai_trader/apprenticeship_v2/general_observer/lesson_voting.py, ai_trader/apprenticeship_v2/tests/test_scorecard.py, ai_trader/apprenticeship_v2/tests/test_lesson_voting.py, ai_trader/apprenticeship_v2/tests/test_episode_builder.py

PATCH_COMMIT_SHA = <see commit step -- reported after this document is written, per repository governance>

VE_GENERAL_OBSERVER_V1_1_SCORECARD_PATCH = PASS

REMAINING_IMPLEMENTATION_BLOCKERS =
* NONE (within this patch's authorized scope)
* Carried over, unaffected, out of scope: STRUCTURAL_FINAL structural-resolution computation itself (Section 19.11); BEFORE ordering-violation detection; checkpoint scheduling; no live MT5 integration test

RED_TEAM_REVIEW_AUTHORIZED = NO
LIVE_SHADOW_AUTHORIZED = NO
BROKER_AUTHORIZED = NO
NEXT_AUTHORIZED_ACTION = NONE — CEO REVIEW REQUIRED

STOP.
```
