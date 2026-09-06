# Prospective-Learning Safety Patch Report

Closes the two narrow gates the CEO mandate authorized after shadow-apprenticeship activation: the
activation record was documentary only and never consulted by the learning path, and no mechanical
BEFORE-review deadline existed. Both gates live in
`ai_trader/apprenticeship_v2/general_observer/before_review.py`, the module that already owned the
ordering-violation guard from the final closure mandate — no new module, no redesign.

## Gate 1 — activation-cutoff

**Verified before writing any code**: `GENERAL_OBSERVER_LEDGER_CSV`/`GENERAL_OBSERVER_PREDICTIONS_CSV`
rows had no code path anywhere consulting
`new_brain_live_state/apprenticeship_v2/AI_TRADER_GENERAL_OBSERVER_SHADOW_APPRENTICESHIP_ACTIVATION.json`
— confirmed by grepping the whole package for "activation" before starting. The ordering-violation
guard alone does **not** cover this: it only fires once a scorecard row exists, so a backfilled
episode reviewed before it is ever scored would sail through as `YES`. Proven directly by
`test_backfilled_episode_forced_no_even_if_mistakenly_reviewed_before_any_scoring`, which first shows
`evaluate_prospective_eligibility` alone says `YES` for exactly this case, then shows the new gate
independently forces `NO`.

**Fix**: `load_activation_cutoff_ts()` reads `GENUINELY_PROSPECTIVE_CUTOFF.M15_EPISODE_CUTOFF_EXCLUSIVE`
from the authoritative activation JSON (the same field the activation record itself already defines —
no duplicated/hardcoded timestamp anywhere). `evaluate_activation_cutoff_eligibility(frozen_at_bar_ts,
cutoff)` returns `"NO"` when `frozen_at_bar_ts <= cutoff` (backfilled, or exactly at T0 — only
strictly-after counts), `"YES"` otherwise. Wired into `effective_general_episode_rows` unconditionally,
applied even to a raw ledger row with no prediction record at all (a backfilled episode that is never
reviewed must still never show `YES`, not merely happen to never vote for the unrelated reason that it
lacks a scorecard row). Returns a no-op (`None` cutoff) only when the activation record does not exist
yet — the chicken-and-egg case where no general-observer episode exists yet either.

## Gate 2 — BEFORE-deadline (H1)

**Fix**: `H1_WINDOW_SECONDS = schemas.RESOLUTION_HORIZONS_M15[0] * 900 = 3600` — reuses the already-frozen
"H1 = 4 M15 bars" mapping `scorecard.py` itself scores against; no new timing constant introduced, per
the mandate's own instruction. `evaluate_before_deadline_eligibility(frozen_at_bar_ts, reviewed_at_utc)`
returns `"NO"` when `reviewed_at_utc` is strictly after `frozen_at_bar_ts + H1_WINDOW_SECONDS`, `"YES"`
otherwise (exactly-at-the-boundary is eligible — matches this package's existing inclusive-horizon
convention, e.g. `due_horizons_for_episode`'s own `len(forward) < horizon_bars`). Applied only once a
prediction record exists and carries a `reviewed_at_utc` — meaningless before a BEFORE review has
happened, and an unreviewed episode already cannot vote (no prediction/scorecard row can exist for it).
A late BEFORE is never rewritten or deleted (`durable_store.append_general_prediction` is untouched,
append-only as before) — `test_before_after_h1_forced_non_prospective_end_to_end` proves the record
stays readable for qualitative/debugging use while `effective_general_episode_rows` still forces `NO`.

Neither gate ever reads `scored_at_utc` — structurally impossible for scorecard timing to influence
either one, proven directly by `test_no_scorecard_timing_manipulation_can_restore_eligibility` (a
deceptively early scored_at_utc, a genuinely late one, and no scorecard row at all, all leave the
verdict `NO` unchanged).

## Composition with the existing ordering guard

Both new gates are applied in `effective_general_episode_rows`, after the ordering-guard overlay, and
can only ever downgrade `YES` to `NO` — never upgrade a `NO` back to `YES`. All three gates are pure
functions of already-persisted, restart-stable facts (an episode's own `frozen_at_bar_ts`, its
prediction row's `reviewed_at_utc`, the static activation JSON, the scorecard ledger) — no in-memory
state anywhere, so a restart reproduces identical verdicts for all three (proven separately for gates 1
and 2: `test_activation_cutoff_restart_preserves_exclusion`,
`test_before_deadline_restart_cannot_bypass_the_gate`).

## Scope discipline

Not touched: any of the 4 event detectors, `scorecard.py`'s classifier or lesson thresholds,
`lesson_voting.py`, `structural_resolution.py`, `dedup.py`, `episode_builder.py`, `resolution.py`, or
any S5 file (`loop.py`, `main.py`, `s5_observer.py`, `mt5_read_only_source.py`) — confirmed via
`git diff --stat` against all of these by name: zero diff. `scorecard.py::EpisodeContext.
prospective_eligibility` still reads the raw (non-overlaid) `episode_row` at its two call sites in
`scorecard.py`, unchanged — a deliberate scope decision, disclosed here: sufficient for the mandate's
own requirement ("never votes") because `lesson_voting.select_canonical_episodes` already applies
`effective_general_episode_rows` unconditionally before any row can become canonical, so a pre-T0 or
late-BEFORE episode is excluded from voting regardless of what verdict `classify_expectation_correct`
would compute for it in isolation. Touching those two call sites was avoidable and the mandate
explicitly said not to change scorecard semantics, so it was left alone.

Missed-move clusters (`RetrospectiveMissedMoveCluster`) already never enter lesson evidence by
construction (`schemas.py`'s own explicit lock) — no separate cluster-eligibility gate was needed or
added; the activation record's own `H1_CLUSTER_CUTOFF_EXCLUSIVE` field is therefore not consulted by
this patch, since there is no code path for it to protect.

**Disclosed operational fact, not a code gap**: the currently-running `main_general_observer.py`
background process (started before this patch, PID confirmed alive via `Get-CimInstance Win32_Process`
earlier this session) has this module already imported in memory and will not pick up this fix until it
is restarted. The fix and its tests are real and correct against the source on disk; whether the live
process is restarted is an operational decision outside this mandate's scope, not attempted here.

## Test results

New: 20 tests, `test_prospective_learning_safety_gates.py` (both gates, unit + end-to-end, all 9
mandate-required scenarios named explicitly: pre-T0/exactly-at-T0/post-T0/restart for gate 1;
within-H1/exactly-at-boundary/after-H1/restart/no-scorecard-timing-manipulation for gate 2), plus the
adversarial ordering-guard-gap case above.

Full suite (`ai_trader/apprenticeship_v2/tests/`, repo's own `venv`, real MT5 terminal, live demo
account): **211 passed, 0 failed, 0 skipped** (up from 191 baseline). Real MT5 E2E
(`test_mt5_e2e_integration.py`, 6 tests, ran for real — not skipped): all 6 passed, including the full
pipeline path. `mypy --ignore-missing-imports` across the whole package: **0 errors, 39 source files**.

Two pre-existing test files needed a matching isolation fix, disclosed as part of this patch (not new
production-code behavior, but necessary so tests stay hermetic against the real activation record that
now genuinely exists on this machine): `test_before_review.py` and `test_mt5_e2e_integration.py` each
now also monkeypatch `before_review.ACTIVATION_RECORD_JSON` to a throwaway path, alongside their
existing `durable_store` isolation. Without this, both files would have silently read the real
production activation cutoff (`1788717834`) during test runs.

## Files changed

```
M  ai_trader/apprenticeship_v2/general_observer/before_review.py       (both gates + overlay composition)
M  ai_trader/apprenticeship_v2/tests/test_before_review.py             (isolation fixture only)
M  ai_trader/apprenticeship_v2/tests/test_mt5_e2e_integration.py       (isolation fixture only)
A  ai_trader/apprenticeship_v2/tests/test_prospective_learning_safety_gates.py  (20 new tests)
M  docs/trader_apprenticeship/apprenticeship_v2/AI_TRADER_GENERAL_OBSERVER_SHADOW_APPRENTICESHIP_PROTOCOL_V1.md  (cadence correction)
A  docs/trader_apprenticeship/apprenticeship_v2/VE_AI_TRADER_GENERAL_OBSERVER_PROSPECTIVE_LEARNING_SAFETY_PATCH_REPORT.md  (this file)
```

---

## Required Final Block

```
PROSPECTIVE_LEARNING_SAFETY_PATCH_COMPLETE = YES
ACTIVATION_T0_MECHANICALLY_ENFORCED = YES
PRE_T0_EPISODES_FORCED_NON_PROSPECTIVE = YES
T0_BOUNDARY_EPISODE_FORCED_NON_PROSPECTIVE = YES
H1_BEFORE_DEADLINE_MECHANICALLY_ENFORCED = YES
LATE_BEFORE_FORCED_NON_PROSPECTIVE = YES
RESTART_CANNOT_BYPASS = YES
PROTOCOL_CADENCE_CORRECTED = YES
S5_CHANGED = NO
OBSERVER_EVENT_SEMANTICS_CHANGED = NO
SCORECARD_SEMANTICS_CHANGED = NO
LESSON_THRESHOLDS_CHANGED = NO
BROKER_ORDER_SUBMISSION_OCCURRED = NO

NEW_TESTS = 20 (test_prospective_learning_safety_gates.py)
FULL_GENERAL_OBSERVER_SUITE = 211 passed, 0 failed, 0 skipped (baseline was 191)
REAL_MT5_E2E = 6 passed, 0 failed, 0 skipped (ran for real, not skipped)
STATIC_CHECK = mypy --ignore-missing-imports: 0 errors, 39 source files

REMAINING_PROSPECTIVE_LEARNING_BLOCKERS =
* NONE in source code / tests.
* OPERATIONAL (not a code blocker): the currently-running main_general_observer.py background
  process has this fix in memory only after restart -- disclosed above, restart not attempted,
  outside this mandate's scope.

RED_TEAM_REAUDIT_AUTHORIZED = NO
LIVE_TRADING_AUTHORIZED = NO
NEXT_AUTHORIZED_ACTION = NONE -- CEO REVIEW REQUIRED

STOP.
```
