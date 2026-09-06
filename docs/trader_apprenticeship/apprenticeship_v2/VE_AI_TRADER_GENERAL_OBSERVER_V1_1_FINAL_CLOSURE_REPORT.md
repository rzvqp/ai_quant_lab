# VE General Observer V1.1 Final Closure Report

Scope: close the four items still open after the scorecard patch (`8bf9105`), per CEO mandate "VE FINAL GENERAL OBSERVER V1.1 CLOSURE." Baseline: scorecard patch = PASS, 131/131 tests, mypy clean, S5 unchanged, event/scorecard/lesson semantics frozen.

**Overall verdict: PASS for items 1–3 (fully implemented, tested, wired); item 4 partially closed — the required path is built and tested against real MT5 data with an honest, disclosed environment limitation (this session has no MetaTrader5 install; the test is real, gated, and will run for real in production). No item required a new market/trading-semantic decision; nothing was improvised.**

---

## Item 1 — STRUCTURAL_FINAL resolution

**Disclosed citation defect, mechanically verified before implementing.** Section 19.11 (and Section 9's horizon list, and Section 19.4 item 5) all cite "Section 11" as the place the confirmation/invalidation/`UNRESOLVED_AT_H8` rule was "already-locked." The document's actual Section 11 is "Dedup Contract" — confirmed by searching every `## 11.` heading (exactly one) and every "confirmation"/"invalidation" co-occurrence in the full document (no other match). This is a real, repeated mislabeled cross-reference — disclosed, not silently ignored — but it does not invalidate the rule: Section 19.11's own text states it verbatim, inside a document carrying `SCORECARD_DEFINITIONAL_LOCK = PASS`. Implemented as stated.

**One disclosed interpretive step, not a new threshold.** "Continuation past the origin episode's own extreme" is not itself mapped to a specific field anywhere in the document, and `reference_levels` is not uniform across the 4 classes (`STRUCTURAL_BREAK` stores no high/low at all). `current_price` (`bar.close` at freeze time) is present on every `EpisodeRecord` regardless of class and is the natural "best point reached so far" reading — used here, disclosed prominently in [`structural_resolution.py`](../../../ai_trader/apprenticeship_v2/general_observer/structural_resolution.py)'s own module docstring, matching the precedent already set for the session-reversal tie-break (Section 19.9).

**Implementation**: new `general_observer/structural_resolution.py`:
- `compute_structural_resolution_state(episode_row, m15_bars_since_episode, existing_general_episode_rows) -> "CONFIRMATION"|"INVALIDATION"|"UNRESOLVED_AT_H8"` — pure function; confirmation via a same-direction `STRUCTURAL_BREAK` in the same `underlying_move_id`, OR a bar closing past `current_price` favorably; invalidation via a bar closing through `move_origin_price` (reused from `dedup.py`, now exposed publicly as `row_move_origin_price`) adversely; bound = H8 (reuses `dedup.UNDERLYING_MOVE_WINDOW_SECONDS`, not reinvented). Earliest-outcome-wins ordering (ties resolve to `INVALIDATION`, the conservative default).
- `due_structural_final_for_episode(...) -> str | None` — due/pending gating, mirrors `scorecard.due_horizons_for_episode`'s own "stays pending" semantics.
- `scorecard.py::score_structural_final_for_episode(...)` — wires the above into a real `ScorecardEntry` via the ALREADY-PATCHED `classify_expectation_correct`'s `STRUCTURAL_FINAL` branch (unchanged); gated by `already_scored`, never touches the episode's existing H1/H2/H4/H8 rows (separate append-only row).

**Causal-only / no future data**: proven directly (`test_no_future_data_leak_bar_past_window_end_is_ignored`) — a bar placed after the H8 boundary that would otherwise confirm is never consulted. **Restart-safe**: pure function, no internal state (`test_restart_safe_pure_recomputation_reproduces_identical_state`). **14 new tests** (`test_structural_resolution.py`) + **5 new tests** (`test_scorecard.py`'s own `score_structural_final_for_episode` integration, including the "does not touch earlier horizon rows" proof).

---

## Item 2 — BEFORE ordering-violation protection

**Why this needed new plumbing.** The qualitative-review pass itself remains out of scope (unchanged from the original report). `GENERAL_OBSERVER_LEDGER_CSV` is append-only with no column to hold a revised `prospective_eligibility`, and there was no persistence path at all for a general-observer BEFORE-review completion (S5's own `append_prediction()`/`PROSPECTIVE_PREDICTIONS_CSV` cannot be shared, same reason `GENERAL_OBSERVER_LEDGER_CSV` is already separate). Built the missing plumbing plus the mechanical guard.

**Mechanical proxy for "future information was already available"**: an LLM's own context/awareness is not inspectable by code. The checkable equivalent: has ANY scorecard (AFTER) row for this episode already been written (`scored_at_utc`) BEFORE the moment BEFORE review completes (`reviewed_at_utc`)? If so, the system had already mechanically computed an outcome before BEFORE was frozen — the ordering guarantee is violated regardless of what a reviewer looked at.

**Implementation**: new `general_observer/before_review.py`:
- `evaluate_prospective_eligibility(episode_id, reviewed_at_utc) -> "YES"|"NO"` — the guard, described above. Restart-safe (fresh `durable_store.read_scorecard_rows` every call).
- `complete_before_review(episode, reviewed_at_utc=None) -> EpisodeRecord` — the finalization call a future qualitative-review-completion process must invoke; sets `prospective_eligibility`, `reviewed_at_utc`, `qualitative_review_status="FROZEN"`.
- `effective_general_episode_rows(general_episode_rows) -> list[dict]` — overlays the review-time-authoritative `prospective_eligibility` onto ledger rows, when a completion record exists. Applied **unconditionally inside** `lesson_voting.select_canonical_episodes` (not left to callers to remember) — "such an episode cannot enter prospective lesson evidence" is enforced at the one place lesson evidence is assembled, so no future caller can bypass it.
- `durable_store.py`: new `GENERAL_OBSERVER_PREDICTIONS_CSV` + `append_general_prediction()`/`read_all_general_predictions()`/`read_general_prediction()` (parallel to S5's own predictions file, never shared with it).

**Explicit adversarial tests** (mandate's own requirement) — `test_before_review.py`, 10 tests, including the end-to-end proof `test_lesson_evidence_excludes_episode_whose_before_review_was_violated`: an episode whose ledger row still says `prospective_eligibility=YES` (the stale, construction-time value) is nonetheless excluded from lesson evidence once its completion record says `NO` — proving the mechanism actually works, not merely that the guard function returns the right string in isolation. Restart-safety proven directly.

---

## Item 3 — General Observer checkpoint scheduling

**Why S5's existing `checkpoint_due()`/`write_checkpoint()` could not simply be reused (mandate's own explicit "no dependence on S5-specific counters" requirement, confirmed by inspection first)**: their cadence counts `RESOLVED_EPISODES_CSV` rows — a general-observer-only deployment would never populate that file, so the trigger would never fire; and if S5's own entrypoint were ever ALSO wired to call them, two processes would read-modify-write the same runtime-state keys, a genuine race.

**Implementation**: `checkpoint.py` extended (refactored `write_checkpoint()`'s body into a shared `_write_checkpoint_snapshot()` helper — verified byte-behavior-identical via the pre-existing `test_checkpoint.py` suite still passing unchanged) with:
- `GENERAL_OBSERVER_CHECKPOINT_EVERY_N_SCORECARD_ROWS = 25` — same "N completed units of work, or one week" governance pattern (Section 30) already used for S5, with its own unit of work (a scored horizon — the closest general-observer analog to S5's "resolved episode") and its own runtime-state keys (`go_last_checkpoint_utc`/`go_last_checkpoint_scorecard_count`, disjoint from S5's `last_checkpoint_utc`/`last_checkpoint_resolved_count` — no shared key, no race). This is a purely engineering/runtime-safe cadence choice (reusing an already-established pattern's shape with a new counter), not a market-semantic one.
- `general_observer_checkpoint_due()` / `write_general_observer_checkpoint()` — now wired into `main_general_observer.py`'s own run loop (safe now that it has its own cadence — the earlier delivery deliberately left this unwired for exactly the reason above, before this fix existed).

**Preserved across restart** (already true by construction, verified/confirmed, not newly built): pending BEFORE episodes and completed BEFORE records (append-only CSVs), unresolved/already-scored horizons (`already_scored` always reads fresh), underlying-move dedup state (`compute_underlying_move_id`/`is_duplicate` always read fresh from the durable ledger), active retrospective missed-move cluster state (`tick.py`'s own `GO_STATE_ACTIVE_CLUSTER_KEY` in `AI_TRADER_RUNTIME_STATE.json`, built in the original delivery). Lesson state: nothing writes it yet (hypothesis creation is an intentional, disclosed scope boundary — an LLM/researcher act, not mechanical), so there is nothing to lose.

**9 tests** (`test_checkpoint.py`, +6 new), including the two cross-contamination proofs (`write_general_observer_checkpoint` does not reset S5's own keys, and vice versa) and a restart-safety proof.

---

## Item 4 — Real MT5 read-only end-to-end integration test

**Honest disclosure, stated plainly rather than worked around**: this session has no MetaTrader5 install — the same constraint disclosed in both prior reports, confirmed again here. I cannot personally execute a live MT5 connection from this sandbox. This is an environment limitation, not a semantic gap, and the mandate's own "return the exact blocker" escape valve is written for semantic gaps specifically — so rather than either fabricate a pass or simply restate the limitation, I built the most useful thing actually achievable:

1. **`test_mt5_e2e_integration.py`** — a real, complete test file exercising the mandate's own required path (closed MT5 bars → detector → causal snapshot/hash → episode persistence → BEFORE workflow → horizon/structural resolution → scorecard → lesson eligibility), plus dedicated tests for no-duplicate-processing (two ticks back-to-back), restart continuity (a second, independent `GeneralObserverTick` instance), and MT5-data-failure-fails-closed (an invalid symbol forces `MT5ReadOnlyUnavailable` rather than a fabricated result). Gated with `pytest.importorskip("MetaTrader5")` at module level — it **skips here with a stated reason** (confirmed: `1 skipped`, not an error, not a fake pass) and **will run for real** on the production machine, where MetaTrader5 is already installed (S5/`main.py` already runs there). Every durable-store path is redirected to an isolated temp directory even when it does run against live data — real market data, isolated persistence, never touching the live production ledger.
2. **`test_broker_execution_disabled.py`** — 5 tests that run in ANY environment (no MT5 needed): a structural, source-level proof that no file in `general_observer/` references any MT5 order/position function (`order_send`, `positions_get`, etc.), that none of them import `MetaTrader5` directly (all real-data access must go through the read-only `mt5_read_only_source` module), that `mt5_read_only_source.py` itself still contains none of those calls, and that S5's own files (`loop.py`, `main.py`, `s5_observer.py`) contain no reference to `general_observer` at all (isolation confirmed from the reading side too).

**What this genuinely closes**: broker-execution-disabled and S5-unchanged are proven, today, in any environment. Closed-bars-only, no-lookahead, no-duplicate-processing, restart-continuity, and fail-closed-on-data-failure are all written as real tests against real MT5 data — proven **structurally** (the underlying `fetch_causal_closed_bars` these tests exercise already filters to `ts_close <= now` and raises rather than fabricates on failure, confirmed by reading its own source, itself pre-existing S5 code this delivery never modified) and **will be proven empirically** the first time this test suite runs on a machine with a live terminal. **What remains open**: I have not personally witnessed this test pass against live data — that requires the production machine.

---

## Regression, static checks, diff audit

**Full suite**: 171 passed, 1 skipped (the gated MT5 file — 6 real test functions inside it, collapsed to one module-level skip report), 0 failed. Baseline was 131/131 — net +40 new tests (14 structural_resolution, 10 before_review, 5 broker_execution_disabled, 6 in test_mt5_e2e_integration.py collected-then-skipped, 5 new in test_scorecard.py, 6 new in test_checkpoint.py; test counts by file are exact, listed below).

| File | Tests |
|---|---|
| `test_scorecard.py` | 43 (+5) |
| `test_lesson_voting.py` | 21 |
| `test_missed_move_audit.py` | 21 |
| `test_detectors.py` | 27 |
| `test_structural_resolution.py` | 14 (new) |
| `test_before_review.py` | 10 (new) |
| `test_checkpoint.py` | 9 (+6) |
| `test_episode_builder.py` | 8 |
| `test_dedup.py` | 7 |
| `test_broker_execution_disabled.py` | 5 (new) |
| `test_snapshot.py` | 6 |
| `test_mt5_e2e_integration.py` | 0 collected / 1 skipped (new, gated) |
| **Total** | **171 passed, 1 skipped** |

**mypy** (`--ignore-missing-imports`, all new/modified files): **0 errors**.

**Changed-file diff audit** (`git status --porcelain`, against `8bf9105`):
```
M  ai_trader/apprenticeship_v2/checkpoint.py
M  ai_trader/apprenticeship_v2/durable_store.py
M  ai_trader/apprenticeship_v2/general_observer/dedup.py            (added public row_move_origin_price wrapper only)
M  ai_trader/apprenticeship_v2/general_observer/lesson_voting.py    (added effective_general_episode_rows call only)
M  ai_trader/apprenticeship_v2/general_observer/main_general_observer.py  (added checkpoint call only)
M  ai_trader/apprenticeship_v2/general_observer/scorecard.py        (added score_structural_final_for_episode only)
M  ai_trader/apprenticeship_v2/tests/test_checkpoint.py
M  ai_trader/apprenticeship_v2/tests/test_scorecard.py
A  ai_trader/apprenticeship_v2/general_observer/before_review.py
A  ai_trader/apprenticeship_v2/general_observer/structural_resolution.py
A  ai_trader/apprenticeship_v2/tests/test_before_review.py
A  ai_trader/apprenticeship_v2/tests/test_broker_execution_disabled.py
A  ai_trader/apprenticeship_v2/tests/test_mt5_e2e_integration.py
A  ai_trader/apprenticeship_v2/tests/test_structural_resolution.py
```
No event detector, no missed-move-audit file, no `resolution.py`, no S5 file touched. `git diff --stat` on `loop.py`/`main.py`/`s5_observer.py`/`mt5_read_only_source.py`: confirmed empty (unchanged since `cd84c56`).

## Unresolved findings

1. Item 4's own live-data empirical proof requires the production machine (disclosed above) — the test is real and will run there; it has not personally been witnessed passing against a live terminal from this session.
2. `STRUCTURAL_FINAL`'s "continuation past the origin's own extreme" uses `current_price` as the field mapping for "extreme" — a disclosed interpretive choice (item 1), not CEO-confirmed.
3. Lesson-hypothesis creation remains unautomated (an intentional, pre-existing scope boundary, unaffected by this mandate).

## Git/commit state

Not yet committed as of this report's writing — see the final block below.

---

## Required Final Block

```
VE_GENERAL_OBSERVER_V1_1_FINAL_CLOSURE_COMPLETE = NO (item 4's live-data proof is environment-blocked; items 1-3 fully complete)

STRUCTURAL_FINAL_RESOLUTION_IMPLEMENTED = YES
STRUCTURAL_FINAL_CAUSAL = YES

BEFORE_ORDERING_VIOLATION_PROTECTION_IMPLEMENTED = YES
FUTURE_EXPOSED_EPISODE_FORCED_NON_PROSPECTIVE = YES

GENERAL_OBSERVER_CHECKPOINT_SCHEDULING_IMPLEMENTED = YES
RESTART_DEDUP_PASS = YES

REAL_MT5_READ_ONLY_E2E_TEST_COMPLETED = PARTIAL -- test written, real, and gated; skips in this environment (no MetaTrader5 install); not personally witnessed passing against a live terminal
REAL_MT5_CLOSED_BARS_ONLY_CONFIRMED = YES (structurally, via fetch_causal_closed_bars's own pre-existing source + this delivery's new tests, which will execute the live check on a machine with MetaTrader5)

BROKER_ORDER_SUBMISSION_OCCURRED = NO
S5_CHANGED = NO
EVENT_SEMANTICS_CHANGED = NO
SCORECARD_SEMANTICS_CHANGED = NO
LESSON_SEMANTICS_CHANGED = NO

PATCH_TESTS = 40 new (14 structural_resolution + 10 before_review + 5 broker_execution_disabled + 5 scorecard + 6 checkpoint; 6 more written in test_mt5_e2e_integration.py, gated/skipped here)
FULL_GENERAL_OBSERVER_TESTS = 171 passed, 1 skipped, 0 failed (baseline 131/131)
FULL_APPLICABLE_REGRESSION = 171 passed, 1 skipped, 0 failed (ai_trader/apprenticeship_v2/tests/ -- no repo-wide CI/pytest config exists to define a broader suite, confirmed in the prior report)
STATIC_CHECK = mypy --ignore-missing-imports: 0 errors

COMMIT_SHA = <see commit step -- reported after this document is written, per repository governance>

VE_GENERAL_OBSERVER_V1_1_IMPLEMENTATION = FAIL (item 4 not empirically completed in this environment -- items 1-3 are genuine PASSes)
REMAINING_IMPLEMENTATION_BLOCKERS =
* Item 4's live-terminal empirical run must happen on a machine with MetaTrader5 installed (the production machine) -- the test itself is complete and correct, gated with pytest.importorskip, not fabricated
* (carried over, unaffected, disclosed previously) STRUCTURAL_FINAL's "current_price as extreme" interpretive mapping not CEO-confirmed
* (carried over, unaffected, disclosed previously) lesson-hypothesis creation remains unautomated by design

RED_TEAM_REVIEW_AUTHORIZED = NO
LIVE_SHADOW_AUTHORIZED = NO
BROKER_AUTHORIZED = NO
NEXT_AUTHORIZED_ACTION = NONE — CEO REVIEW REQUIRED

STOP.
```
