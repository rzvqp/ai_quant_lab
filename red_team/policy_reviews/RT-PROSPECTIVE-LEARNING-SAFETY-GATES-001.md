# RED TEAM — PROSPECTIVE-LEARNING SAFETY RE-AUDIT · General Observer activation-T0 + H1-BEFORE-deadline gates
### RT-PROSPECTIVE-LEARNING-SAFETY-GATES-001 · Auditor: Red Team · 2026-09-06

Narrow adversarial re-audit of VE `c86143a` — two prospective-eligibility gates (activation-T0 cutoff, H1
BEFORE deadline) added to `before_review.effective_general_episode_rows`, plus a protocol-cadence doc. VE
baseline `211 passed / 0 / 0`, `REAL_MT5_E2E = 6`. Audited independently; verified at source. Both gates are
correct, downgrade-only, restart-safe, and consume the authoritative activation record; no regression; the
tests are properly isolated from production state. No code modified.

---

## 0 — VERDICT

```
RED_TEAM_PROSPECTIVE_SAFETY_REAUDIT_COMPLETE = YES
ACTIVATION_T0_GATE = PASS
PRE_T0_EXCLUSION = PASS
T0_BOUNDARY_EXCLUSION = PASS
RESTART_T0_ENFORCEMENT = PASS
H1_BEFORE_DEADLINE_GATE = PASS
LATE_BEFORE_EXCLUSION = PASS
RESTART_DEADLINE_ENFORCEMENT = PASS
TEST_ISOLATION = PASS
SEMANTIC_DRIFT_FOUND = NO
S5_UNCHANGED = YES
RED_TEAM_VERDICT = PASS
BLOCKERS = NONE
GROUP_3_PROSPECTIVE_LEARNING_SAFE = YES
LIVE_TRADING_AUTHORIZED = NO
BROKER_AUTHORIZED = NO
NEXT_AUTHORIZED_ACTION = NONE — CEO REVIEW REQUIRED
```

## 1 — SCOPE

`c86143a` ("Add prospective-learning safety gates: activation T0 cutoff + H1 BEFORE deadline") is HEAD, a
direct child of the E114-passed `a2637e0`. The **only code file changed is `before_review.py`** (+116);
everything else is tests (`test_prospective_learning_safety_gates.py` NEW +276, `test_before_review.py` +8,
`test_mt5_e2e_integration.py` +6) and docs (the shadow-apprenticeship protocol V1 + patch report). The
protocol-cadence correction (mandate item 3) is a documentation artifact only — no `checkpoint.py`/runtime
code change.

## 2 — GATE 1: ACTIVATION-T0 CUTOFF — PASS

`load_activation_cutoff_ts` reads T0 from the **authoritative** activation record
(`ACTIVATION_RECORD_JSON = LIVE_STATE_DIR/…SHADOW_APPRENTICESHIP_ACTIVATION.json`,
`data["GENUINELY_PROSPECTIVE_CUTOFF"]["M15_EPISODE_CUTOFF_EXCLUSIVE"]`) — verified against the real on-disk
record, whose schema matches exactly (T0 = 1788717834 = 2026-09-06 18:03 UTC, the activation time). No
hardcoded/duplicated timestamp; returns `None` (gate no-op) only when the record does not exist yet.
`evaluate_activation_cutoff_eligibility` returns `"NO"` iff `frozen_at_bar_ts <= T0`:
- **PRE_T0_EXCLUSION = PASS:** `frozen < T0 → NO`.
- **T0_BOUNDARY_EXCLUSION = PASS:** `frozen == T0 → NO` (uses `<=`; only strictly-after-T0 counts).
- After T0 → `YES` (eligible, subject to Gate 2).

**Consumed by the effective eligibility path (not documentary):** `effective_general_episode_rows` calls
`load_activation_cutoff_ts()` and applies the gate **even when no prediction/completion record exists**,
against the row's own raw `frozen_at_bar_ts` — so a backfilled pre-T0 episode a reviewer mistakenly completes
BEFORE review for, with no scorecard row yet, is still forced `NO` (the exact gap the ordering guard alone
cannot see; proven by `test_backfilled_episode_forced_no_even_if_mistakenly_reviewed_before_any_scoring`: the
ordering guard returns `YES`, the activation gate returns `NO`). And `lesson_voting.select_canonical_episodes`
calls `effective_general_episode_rows` unconditionally then filters to `prospective_eligibility=="YES"`, so a
gated-`NO` row is excluded from canonical selection and voting — end-to-end tests confirm the pre-T0 and
exactly-at-T0 episodes yield `canonical == {}` and `(n_voting, support, counter) == (0,0,0)`.
**ACTIVATION_T0_GATE = PASS.**

**RESTART_T0_ENFORCEMENT = PASS:** the gate is a pure function of persisted, restart-stable facts (the row's
`frozen_at_bar_ts` + the static activation JSON), read fresh every call — no in-memory state. Two independent
evaluations reproduce the identical `NO` (`test_activation_cutoff_restart_preserves_exclusion`).

## 3 — GATE 2: H1 BEFORE DEADLINE — PASS

`H1_WINDOW_SECONDS = RESOLUTION_HORIZONS_M15[0] * 900 = 3600` — **reuses the already-frozen "H1 = 4 M15 bars"
horizon**; the `_M15_BAR_SECONDS` constant is unit conversion, not a policy threshold, so **no new trading
threshold is introduced** (`test_h1_window_seconds_reuses_the_frozen_horizon_no_new_constant` asserts the
identity). `evaluate_before_deadline_eligibility` returns `"NO"` iff `reviewed_at_utc > frozen_at_bar_ts +
H1_WINDOW_SECONDS`:
- Within H1 → `YES` (**BEFORE completed within the frozen H1 window may remain eligible**).
- Exactly at the boundary → `YES` (inclusive, matching the package's existing horizon convention).
- **LATE_BEFORE_EXCLUSION = PASS:** after H1 → `NO`, mechanically forced non-prospective. The late BEFORE
  record is **kept on the durable ledger** (never rewritten/deleted — `test_before_after_h1_forced_non_
  prospective_end_to_end` confirms `read_general_prediction` still returns it), but it can never vote
  (`select_canonical_episodes → {}`).

**RESTART_DEADLINE_ENFORCEMENT = PASS:** pure function of persisted `frozen_at_bar_ts` + `reviewed_at_utc`,
fresh reads; two evaluations reproduce `NO` (`test_before_deadline_restart_cannot_bypass_the_gate`).
**Scorecard timing cannot restore eligibility:** neither gate reads `scored_at_utc`
(`test_no_scorecard_timing_manipulation_can_restore_eligibility` proves no scorecard, a deceptively-early
scorecard, and a later scorecard all leave the late-BEFORE verdict at `NO`). **H1_BEFORE_DEADLINE_GATE =
PASS.**

## 4 — DOWNGRADE-ONLY (NO ACCIDENTAL PROMOTION) — verified

Both gates in `effective_general_episode_rows` are guarded by `if eligibility == "YES": … eligibility =
"NO"` — they can **only** transition `YES → NO`, never the reverse. The initial `eligibility` is the
prediction's authoritative review-time value (if any) else the row's ledger value, and the ledger's
`prospective_eligibility` is written as `"YES"` at construction (`episode_builder.py:156`) and never mutated
in place (the function returns a copy). So the output is effectively `min(ordering_guard, gate1, gate2)` — an
otherwise-ineligible episode (prediction `NO`, or pre-T0, or late-BEFORE) can never be promoted to `YES`.
Confirmed at source and by the end-to-end tests (only genuinely post-T0, within-H1 episodes retain `YES`).

## 5 — TEST ISOLATION (mandate: no accidental production-state dependence) — PASS

The `autouse` fixture `_isolated_durable_store` monkeypatches `durable_store.SCORECARD_CSV`,
`durable_store.GENERAL_OBSERVER_PREDICTIONS_CSV`, and **`before_review.ACTIVATION_RECORD_JSON`** to `tmp_path`
— its docstring explicitly notes "the real activation record, with this exact cutoff value, genuinely exists
on this machine," and deliberately redirects it. Every test writes its own schema-faithful synthetic
activation record (`{"GENUINELY_PROSPECTIVE_CUTOFF": {"M15_EPISODE_CUTOFF_EXCLUSIVE": …}}`, matching
production and the code's read path). No test reads the real activation JSON, predictions, or scorecard.
Coverage is complete and adversarial (pre/at/post-T0, backfill-before-scoring, restart, within/at/after-H1,
scorecard-manipulation, both no-op cases). Each gate's removal would flip a passing assertion. **TEST_ISOLATION
= PASS.**

## 6 — REGRESSION / ISOLATION (§4) — none

Confirmed **byte-unchanged** by `c86143a`: `detectors.py` (event semantics), `structural_resolution.py`
(STRUCTURAL_FINAL), `scorecard.py` (scorecard semantics), `lesson_voting.py` (lesson thresholds — `N≥10` /
`0.70` / `0.5` intact), `dedup.py`, `episode_builder.py`, `mt5_read_only_source.py` (MT5 watermark logic),
`s5_observer.py`, `tick.py`, `schemas.py`. `before_review.py` adds no MT5/order call (pure logic + a JSON
read); broker safety intact (`test_broker_execution_disabled` unchanged and passing). **S5_UNCHANGED = YES;
SEMANTIC_DRIFT_FOUND = NO** (the gates reuse the frozen H1 horizon, are downgrade-only, and touch no other
subsystem's semantics). Suite reproduced live: **211 passed, 0 failed, 0 skipped**; real-MT5 E2E: **6
passed**.

## 7 — CONCLUSION

`c86143a` closes a real, previously-unenforced gap — the shadow-apprenticeship activation record was
documentary-only and never consulted by the learning path, so the ~27 backfilled first-tick episodes could
have entered canonical lesson evidence if ever reviewed. Both new gates are correct (pre/at-T0 excluded,
post-T0 eligible; late BEFORE forced non-prospective; H1 boundary inclusive), consume the authoritative
activation record, are downgrade-only (no promotion), restart-safe, and immune to scorecard-timing
manipulation; they reuse the frozen H1 horizon with no new threshold; and they leave every other subsystem
(S5, event semantics, STRUCTURAL_FINAL, scorecard, lesson thresholds, MT5 watermark, broker safety)
byte-unchanged. The new tests are properly isolated from production activation state. **GROUP_3 prospective
learning is safe.**

```
RED_TEAM_VERDICT = PASS   GROUP_3_PROSPECTIVE_LEARNING_SAFE = YES
LIVE_TRADING_AUTHORIZED = NO   BROKER_AUTHORIZED = NO
NEXT_AUTHORIZED_ACTION = NONE — CEO REVIEW REQUIRED
```

Read-only re-audit; no code modified, no runtime/broker enabled. Control returned to CEO.

---

*Red Team · prospective-learning safety gates · only before_review.py changed · activation-T0 gate reads the
authoritative JSON (T0=1788717834), <=T0 → NO (pre + exactly-at excluded), consumed by the vote path, catches
backfill-reviewed-before-scoring · H1 BEFORE-deadline gate reuses RESOLUTION_HORIZONS_M15[0] (no new
threshold), late→NO record-kept, boundary inclusive, scorecard-timing-immune · both downgrade-only (no
promotion), restart-safe · tests isolate the real activation record via monkeypatch · S5/structural_final/
scorecard/lesson-thresholds/watermark/broker byte-unchanged · 211/0/0, E2E 6 · VERDICT PASS · LEDGER E115
(prev E114).*
