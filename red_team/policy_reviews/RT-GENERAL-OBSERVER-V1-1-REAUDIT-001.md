# RED TEAM — RE-AUDIT · AI TRADER GENERAL OBSERVER V1.1 (post-remediation `a2637e0`)
### RT-GENERAL-OBSERVER-V1-1-REAUDIT-001 · Auditor: Red Team · 2026-09-06

Re-audit of the three blockers from `RT-GENERAL-OBSERVER-V1-1-FINAL-AUDIT-001` (E113) after VE remediation
`a2637e0`. VE reports 191 passed / 0 failed / 0 skipped. Audited independently — the PASS framing is not
accepted; every fix verified at source and adversarially tested. All three blockers are genuinely closed, no
regression, no new defect. No code modified; nothing fixed; no shadow/broker enabled.

---

## 0 — VERDICT

```
RED_TEAM_REAUDIT_COMPLETE = YES
BEFORE_SNAPSHOT_CAUSALITY = PASS
CATCHUP_CAUSALITY = PASS
RESTART_CAUSALITY = PASS
SWEEP_BREAK_DEDUP = PASS
NEW_INDEPENDENT_MOVE_ALLOWED = PASS
SAME_MOVE_DUPLICATES_SUPPRESSED = PASS
MISSED_MOVE_CLUSTER_IDEMPOTENCY = PASS
CRASH_RESTART_EXACTLY_ONCE = PASS
TEST_SUITE_ADEQUATE = YES
REAL_MT5_SUITE = 191 passed, 0 failed, 0 skipped
S5_UNCHANGED = YES
SEMANTIC_DRIFT_FOUND = NO
FUTURE_LEAK_FOUND = NO
DUPLICATE_EVIDENCE_RISK_FOUND = NO
RED_TEAM_VERDICT = PASS
BLOCKERS = NONE
GENERAL_OBSERVER_V1_1_FINAL = PASS
GENERAL_OBSERVER_READY_FOR_SHADOW_APPRENTICESHIP = YES
LIVE_SHADOW_AUTHORIZED = NO
BROKER_AUTHORIZED = NO
NEXT_AUTHORIZED_ACTION = NONE — CEO REVIEW REQUIRED
```

## 1 — SCOPE

`a2637e0` ("Fix 3 Red Team-confirmed blockers") is HEAD, a direct child of `1e099aa`, changing exactly the
three code files I flagged + their tests + a report: `episode_builder.py` (+19, Blocker 1), `dedup.py` (+40,
Blocker 2), `durable_store.py` (+15, Blocker 3), `tests/test_causal_truncation.py` (NEW +138),
`tests/test_dedup.py` (+80), `tests/test_missed_move_audit.py` (+67), and the fix report. 431 insertions / 16
deletions. Nothing else touched.

## 2 — BLOCKER 1 (BEFORE-SNAPSHOT FUTURE LEAK) — CLOSED

`build_episodes_for_bar` now truncates the higher-timeframe arrays at the top, before any use
(`episode_builder.py`): `h4 = [b for b in h4 if b.ts_close <= bar.ts_close]` (and h1, m5). Verified:
- **Correct bound:** `<= bar.ts_close` is inclusive of bars closing exactly at the trigger (causal —
  complete at the trigger instant) and excludes any bar closing after it. The reassigned locals flow into
  `build_episode_record` (`:234,246`) → `build_snapshot(h4,h1,m15,m5)` (`:138`), so the frozen snapshot now
  contains only ≤-trigger bars.
- **Unbypassable:** `build_snapshot` has exactly one caller (`build_episode_record`), which has exactly one
  non-test caller (`build_episodes_for_bar`), which has exactly one caller (`tick.py:83`). The truncation is
  on the sole path. M15 is deliberately not re-truncated — it is already the caller's causal slice
  `m15[:i+1]` guarded by `detect_displacement`'s fail-fast `assert m15_bars[-1] is bar` (`detectors.py:93`).
- **No behavior change beyond the fix:** the h1 truncation bound equals `compute_eligible_major_levels`'s own
  internal `ts_close <= as_of_ts_close` filter (`as_of = bar.ts_close`), so levels/detection are unchanged;
  only the future bars are removed from the snapshot.
- **Tested (`test_causal_truncation.py`, 6 tests, all catch-up shapes):** first-startup (100 historical M15,
  trigger at the oldest), restart-after-long-downtime (multi-day future span), trigger near
  beginning/middle/end of batch, and each timeframe isolated. Every test **asserts the fixture actually
  extends past the trigger** (non-vacuous) and then asserts every snapshot bar's `ts_close <=
  trigger_ts_close`. Reverting the truncation makes these fail. **BEFORE_SNAPSHOT_CAUSALITY / CATCHUP /
  RESTART = PASS; FUTURE_LEAK_FOUND = NO.**

## 3 — BLOCKER 2 (SWEEP/BREAK DEDUP) — CLOSED, spec-faithful

`per_class_dedup_key` and `_row_dedup_key` now include `underlying_move_id` in the SWEEP_REJECTION /
STRUCTURAL_BREAK keys (`dedup.py:126-131,154-170`), exactly as DISPLACEMENT already did. This is the direct,
threshold-free mechanical encoding of Section 4A/4B ("a sweep/break of the same level is a duplicate UNLESS
price has since closed back through … a genuinely new event") — the "closed back through" condition is
precisely what `compute_underlying_move_id` already evaluates (price continuity within the H8 window) to
decide same-vs-new family. No new numeric threshold. Verified:
- **Same move suppressed:** two triggers of the identical level/price/direction within the same still-open
  family get the same `underlying_move_id` → identical key → suppressed. Tested end-to-end
  (`test_dedup.py::test_duplicate_event_inside_same_move_suppressed_end_to_end`,
  `…_repeated_same_level_later_but_same_move_still_suppressed`).
- **New independent move allowed:** after a full round-trip (adverse close breaks continuity),
  `compute_underlying_move_id` mints a NEW id → different key → the re-sweep is **not** suppressed
  (`…_same_level_revisited_after_move_closure_is_a_new_episode` asserts `is_duplicate(...) is False`). This is
  exactly the E113 defect, now fixed.
- **Restart-safe:** the episode ledger persists `underlying_move_id` (`durable_store.py:68,203`), so
  `_row_dedup_key` reads the correct id across ticks/restart; a re-detected event deterministically recomputes
  the same id (`…_restart_preserves_identical_new_independent_move_behavior`, JSON round-trip). No artificial
  multiplication (same-move still collapses) and no permanent suppression (new move passes).
- **Lesson evidence:** two independent moves now carry two distinct ids → two distinct one-per-move votes
  (`…_lesson_evidence_sees_independent_moves_separately`). The tests use `compute_underlying_move_id` +
  `is_duplicate` **together** (the shape that would have caught the original defect; the old test used a
  displacement and never exercised two families). **SWEEP_BREAK_DEDUP / NEW_INDEPENDENT_MOVE_ALLOWED /
  SAME_MOVE_DUPLICATES_SUPPRESSED = PASS; SEMANTIC_DRIFT_FOUND = NO; DUPLICATE_EVIDENCE_RISK = NO.**

## 4 — BLOCKER 3 (MISSED-MOVE CLUSTER IDEMPOTENCY) — CLOSED

`append_missed_move_cluster` now no-ops if the deterministic `cluster_id` already exists — a fresh ledger
read every call: `if any(row.get("cluster_id") == cluster.cluster_id for row in read_missed_move_clusters()):
return` (`durable_store.py`). Verified:
- **Determinism:** `cluster_id` is a hash over the first candidate's fixed `(window_start_ts, window_end_ts,
  direction)`, set once in `_start_cluster` and never revised (`missed_move_audit.py:109-115,118-126`), so a
  restart re-derives the identical id.
- **Exactly once on crash-restart:** appending the same terminated cluster twice yields one row
  (`test_missed_move_audit.py::test_crash_before_watermark_then_restart_emits_cluster_exactly_once`); a
  reconstructed-from-scratch cluster (different process) still yields one
  (`…_idempotent_append_restart_safe_via_fresh_read`, no in-memory flag).
- **Distinct clusters still written:** a genuinely different cluster (different canonical window) persists
  normally (`…_next_genuinely_different_cluster_still_persists_normally`, 2 rows). Reverting the guard makes
  the first test yield 2 rows and fail. **MISSED_MOVE_CLUSTER_IDEMPOTENCY / CRASH_RESTART_EXACTLY_ONCE =
  PASS.**

## 5 — REGRESSION (§4) — none

Confirmed **byte-unchanged** by `a2637e0`: `structural_resolution.py` (STRUCTURAL_FINAL), `scorecard.py`,
`lesson_voting.py`, `mt5_read_only_source.py` (the watermark fix), `s5_observer.py`, `tick.py`, `snapshot.py`,
`loop.py`, `main.py`. Broker safety intact — `test_broker_execution_disabled.py` (unchanged) still passes,
and the two new `general_observer/` code changes (`episode_builder.py`, `dedup.py`) introduce no MT5/order
call (pure logic). The Blocker-2 key change is consumed only by `is_duplicate`; the Blocker-1 truncation is
idempotent with the existing levels filter — neither touches scorecard/lesson/structural semantics.
**S5_UNCHANGED = YES.** (S5 isolation and the watermark-fix causality/S5 findings from E113 stand unchanged.)

## 6 — TEST QUALITY (§5) — adequate

14 new tests (6 causal-truncation + 5 dedup + 3 cluster), all balanced (they assert both the fixed behavior
AND that the guard doesn't over-correct) and non-vacuous (the truncation tests assert the fixture leaks
before checking it doesn't; the dedup tests exercise two genuine families). Each would fail if its
corresponding E113 defect were reintroduced: remove the truncation → snapshot future-bar assertion fails;
drop `underlying_move_id` from the sweep key → the round-trip test's `is_duplicate(...) is False` flips to
True; remove the idempotency guard → the crash test's `len(rows)==1` becomes 2. **TEST_SUITE_ADEQUATE = YES.**

## 7 — REAL MT5 / RESTART (§6)

Reproduced the full suite against the live MT5-connected `venv`: **191 passed, 0 failed, 0 skipped** (2.5s,
including the gated real-terminal E2E tests) — up from 177 by exactly the 14 new tests. **REAL_MT5_SUITE = 191
passed, 0 failed, 0 skipped.**

## 8 — CONCLUSION

All three E113 blockers are genuinely closed at source, with spec-faithful fixes (no new thresholds), no
regression to any other subsystem (S5, STRUCTURAL_FINAL, scorecard, lesson, watermark, broker all
byte-unchanged and still isolated), and adequate adversarial tests that would catch each defect's
reintroduction. The BEFORE snapshot is now causal for every trigger under catch-up and restart; sweep/break
dedup matches Section 4A/4B/11 (same-move suppressed, new independent move allowed, restart-consistent); the
missed-move cluster append is idempotent across crash-restart. `GENERAL_OBSERVER_V1_1_FINAL = PASS`; the
system is ready for shadow apprenticeship, subject to CEO authorization (which this audit does not grant).

```
RED_TEAM_VERDICT = PASS   GENERAL_OBSERVER_V1_1_FINAL = PASS
GENERAL_OBSERVER_READY_FOR_SHADOW_APPRENTICESHIP = YES
LIVE_SHADOW_AUTHORIZED = NO   BROKER_AUTHORIZED = NO
NEXT_AUTHORIZED_ACTION = NONE — CEO REVIEW REQUIRED
```

Read-only re-audit; no code modified, no finding fixed, no shadow or broker execution enabled. Control
returned to CEO.

---

*Red Team · General Observer V1.1 re-audit · a2637e0 closes all 3 E113 blockers · BEFORE snapshot truncated
to trigger ts_close (unbypassable, tested across catch-up/restart shapes) · sweep/break dedup now keyed on
underlying_move_id (same-move suppressed, round-trip new move allowed, restart-safe, Section 4/11-faithful,
no new threshold) · missed-move cluster append idempotent (deterministic cluster_id, exactly-once on crash) ·
S5/STRUCTURAL_FINAL/scorecard/lesson/watermark/broker byte-unchanged · 191/191 real MT5 · 14 new tests catch
reintroduced defects · VERDICT PASS · READY_FOR_SHADOW (CEO auth pending) · LEDGER E114 (prev E113).*
