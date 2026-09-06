# Red Team Blocker Fix Report — RT-GENERAL-OBSERVER-V1-1-FINAL-AUDIT-001

Fixes the 3 blockers Red Team confirmed independently (verdict `FAIL`); all 3 verified against the current code before any change, per standing discipline (never trust a cross-session finding without mechanical re-verification).

## Blocker 1 — BEFORE snapshot future leak

**Verified**: `tick.py` fetches `h4`/`h1`/`m5` once per tick, up to real "now" — only `m15` is per-bar-sliced (`m15[:i+1]`). `episode_builder.py::build_episode_record` passed `h4`/`h1`/`m5` straight into `snapshot.build_snapshot`, which just takes each list's own trailing N bars — no truncation to the trigger bar's own `ts_close` anywhere. During first-run or post-downtime catch-up, where an *older* M15 bar is being processed historically, `h4`/`h1`/`m5` legitimately extend past that bar's own close — a real causality violation in the frozen, immutable BEFORE snapshot.

**Fix**: `episode_builder.py::build_episodes_for_bar` now truncates `h4`/`h1`/`m5` to `ts_close <= bar.ts_close` at its own entry point, before any use (snapshot construction and the major-levels computation, which already filtered `h1` internally — now redundant-but-harmless there). `m15_causal_bars_up_to_and_including_bar` was not touched: it was already causally guaranteed by the caller's own slicing and by `detect_displacement`'s existing precondition assertion, which stays a loud, fail-fast check rather than being replaced with a silent truncation.

**New tests** (`test_causal_truncation.py`, 6): first-startup with ~100 historical M15 bars, restart after a multi-day downtime, trigger near the beginning/middle/end of a fetched batch, and an isolated per-timeframe check proving H4 alone (with H1/M5 already causal) still gets caught. Every test constructs fixtures that provably extend past the trigger on the relevant timeframe(s) first (a self-check that already caught one of my own fixture-arithmetic mistakes during development), then asserts zero leaked bars on H4, H1, M5, and M15 (control) in the resulting snapshot.

## Blocker 2 — sweep/break dedup semantic drift

**Verified**: `dedup.py::per_class_dedup_key`/`_row_dedup_key` for `SWEEP_REJECTION`/`STRUCTURAL_BREAK` keyed on `(type, level_type, level_price, direction)` only — no `underlying_move_id` component — while `is_duplicate` scans the *entire* ledger. `DISPLACEMENT`'s own key already included `underlying_move_id`; sweep/break did not, contradicting Section 4A/4B's own text ("a duplicate... UNLESS... price has since closed back through the level in the adverse direction (a genuinely new event, not a repeat)") and permanently suppressing a level from ever originating a new episode again, even long after its originating family had closed.

**Fix**: both keys now include `underlying_move_id`, exactly mirroring DISPLACEMENT's already-correct pattern — using the already-existing, already-computed family identity (`compute_underlying_move_id`, unchanged), not a new time threshold. A re-trigger of the identical level/price/direction within the *same* still-open family (same `underlying_move_id`) still produces the identical key (still suppressed — whipsaw behavior preserved exactly). The identical level/price/direction re-triggering under a *new* family (continuity broken, or the H8 window elapsed) now produces a different key, correctly allowed through.

**New tests** (`test_dedup.py`, +5): duplicate inside the same move suppressed end-to-end (computing `underlying_move_id` and checking `is_duplicate` together, not `is_duplicate` alone with a hand-picked, always-matching id — the shape of test that would have caught the original defect), repeated same level several bars later but same move still suppressed, **the key case**: same level revisited after the move closes → new episode (`is_duplicate` returns `False`), restart preserves that exact behavior (JSON round-trip), and independent moves get distinct `underlying_move_id` values (the property `lesson_voting.py`'s one-vote-per-move counting depends on). One pre-existing test (`test_per_class_dedup_key_shape`) asserted the old, buggy 4-tuple shape — updated to the corrected 5-tuple, since it was testing the defect's own shape, not a use case; all other pre-existing dedup/episode_builder tests passed unchanged (they always used a consistent move_id on both sides of their own fixtures, so this defect never surfaced there — confirming Red Team's own "untested" finding).

## Blocker 3 — missed-move cluster restart idempotency

**Verified**: `tick.py` calls `durable_store.append_missed_move_cluster(finalized)` inside its own H1 loop; the H1 watermark is only saved after the entire loop completes. `append_missed_move_cluster` had no idempotency guard. A crash between the append and the watermark save would, on restart, reprocess the same H1 bar and deterministically re-derive and re-append the identical cluster.

**Fix**: `durable_store.append_missed_move_cluster` now checks (a fresh `read_missed_move_clusters()` call, never cached) whether a cluster with the exact same `cluster_id` — already deterministic, a hash over the cluster's own fixed semantic identity, computed once at cluster-start — has already been persisted; if so, the call is a no-op. Cluster semantics (identity, continuation, termination rules) are entirely untouched — this only prevents writing the same already-determined cluster twice. `tick.py`'s own append-then-save-watermark order was left unchanged: the idempotency guard makes that order irrelevant to correctness (a crash-and-retry can never produce a duplicate row regardless of which happens first), so reordering was unnecessary and would have touched more than the mandate authorized.

**New tests** (`test_missed_move_audit.py`, +3): the exact crash scenario (append, then a simulated restart re-derives and re-appends the same cluster — exactly one row results), a genuinely different, later cluster still persists normally (the guard doesn't over-suppress), and restart-safety via completely independent Python objects (no shared in-memory state between the "pre-crash" and "post-restart" append calls).

## Scope discipline

Not touched: any of the 4 event detectors, missed-move audit semantics (window/step/materiality/coverage/cluster-continuation rules), `scorecard.py`'s classifier or lesson thresholds, `STRUCTURAL_FINAL` resolution, `mt5_read_only_source.py`'s watermark fix, or any S5 file. Confirmed via `git status`: exactly 5 files touched (`durable_store.py`, `dedup.py`, `episode_builder.py`, `test_dedup.py`, `test_missed_move_audit.py`) plus one new file (`test_causal_truncation.py`) — matching the mandate's own 3 authorized fix areas precisely, no more.

## Test results

`ai_trader/apprenticeship_v2/tests/` via the repo's own `venv` (real MT5 terminal, live demo account): **191 passed, 0 failed, 0 skipped**, confirmed across 4 consecutive full-suite runs (up from 177/0/0 pre-fix — 14 net new tests: 6 + 5 + 3). `mypy --ignore-missing-imports`: **0 errors**.

## Files changed

```
M  ai_trader/apprenticeship_v2/durable_store.py           (Blocker 3: idempotent append_missed_move_cluster)
M  ai_trader/apprenticeship_v2/general_observer/dedup.py  (Blocker 2: underlying_move_id in sweep/break keys)
M  ai_trader/apprenticeship_v2/general_observer/episode_builder.py  (Blocker 1: h4/h1/m5 causal truncation)
M  ai_trader/apprenticeship_v2/tests/test_dedup.py        (updated 1 stale test, added 5 new)
M  ai_trader/apprenticeship_v2/tests/test_missed_move_audit.py  (added 3 new)
A  ai_trader/apprenticeship_v2/tests/test_causal_truncation.py  (6 new)
```

---

## Required Final Block

```
RT_BLOCKER_FIX_COMPLETE = YES

BEFORE_SNAPSHOT_ALL_TIMEFRAMES_CAUSALLY_TRUNCATED = YES
CATCHUP_FUTURE_LEAK_FIXED = YES
RESTART_FUTURE_LEAK_FIXED = YES

SWEEP_BREAK_DEDUP_SAME_MOVE_SUPPRESSED = YES
SWEEP_BREAK_NEW_INDEPENDENT_MOVE_ALLOWED = YES
UNDERLYING_MOVE_SEMANTICS_PRESERVED = YES

MISSED_MOVE_CLUSTER_IDEMPOTENT = YES
CRASH_RESTART_DUPLICATE_FIXED = YES

S5_CHANGED = NO
STRUCTURAL_FINAL_CHANGED = NO
SCORECARD_SEMANTICS_CHANGED = NO
LESSON_SEMANTICS_CHANGED = NO
MT5_WATERMARK_FIX_CHANGED = NO

NEW_TESTS = 14 (6 causal-truncation + 5 dedup + 3 missed-move-cluster idempotency)
FULL_GENERAL_OBSERVER_SUITE = 191 passed, 0 failed, 0 skipped (confirmed across 4 consecutive runs against the live terminal; baseline was 177/0/0)
REAL_MT5_E2E = passed (included in the 191 above -- test_mt5_e2e_integration.py's own 6 tests all ran for real, 0 failed, 0 skipped)
STATIC_CHECK = mypy --ignore-missing-imports: 0 errors

GENERAL_OBSERVER_V1_1_IMPLEMENTATION = PASS

REMAINING_BLOCKERS =
* NONE

RED_TEAM_REVIEW_AUTHORIZED = NO
LIVE_SHADOW_AUTHORIZED = NO
BROKER_AUTHORIZED = NO
NEXT_AUTHORIZED_ACTION = NONE — CEO REVIEW REQUIRED

STOP.
```
