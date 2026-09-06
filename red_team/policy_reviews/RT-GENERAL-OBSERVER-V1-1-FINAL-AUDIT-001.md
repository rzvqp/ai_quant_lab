# RED TEAM — FINAL ADVERSARIAL AUDIT · AI TRADER GENERAL OBSERVER V1.1
### RT-GENERAL-OBSERVER-V1-1-FINAL-AUDIT-001 · Auditor: Red Team · 2026-09-06

Independent final audit of the General Observer V1.1 delivery (implementation head `1e099aa`, incorporating
`8bf9105` scorecard patch, `f8573b3` closure, `1e099aa` MT5 watermark fix). VE reports 177/177 PASS across 8
live runs / REMAINING_BLOCKERS=NONE. **Audited independently; the PASS framing is not accepted.** Two
blocking defects and one restart-duplicate were found and verified at source — all in code paths the 177
tests do not exercise. No code modified; nothing fixed; no runtime enabled; no broker authorized.

---

## 0 — VERDICT

```
RED_TEAM_GENERAL_OBSERVER_V1_1_AUDIT_COMPLETE = YES
CAUSALITY = FAIL
BEFORE_INTEGRITY = FAIL
STRUCTURAL_FINAL = PASS
SCORECARD = PASS
LESSON_LOOP = PASS (mechanics) — evidence base corrupted upstream by the dedup drift (Blocker 2)
MISSED_MOVE_AUDIT = PASS (audit logic) — restart-append not idempotent (Blocker 3)
DEDUP_AND_UNDERLYING_MOVE = FAIL
CHECKPOINT_RESTART = FAIL
REAL_MT5_E2E = PASS (executed; path exercised; broker structurally unreachable) — coverage-incomplete
MT5_WATERMARK_FIX = PASS
S5_BEHAVIOR_UNCHANGED_BY_SHARED_SOURCE_FIX = PASS
TEST_SUITE_ADEQUATE = NO
SEMANTIC_DRIFT_FOUND = YES
FUTURE_LEAK_FOUND = YES
DUPLICATE_EVIDENCE_RISK_FOUND = YES
RED_TEAM_VERDICT = FAIL
BLOCKERS = 3 (listed §8)
GENERAL_OBSERVER_READY_FOR_SHADOW_APPRENTICESHIP = NO
LIVE_SHADOW_AUTHORIZED = NO
BROKER_AUTHORIZED = NO
NEXT_AUTHORIZED_ACTION = NONE — CEO REVIEW REQUIRED
```

## 1 — HIGH PRIORITY: MT5 WATERMARK FIX `1e099aa` (§7) — PASS

The fix caches `(tick.time, offset)` per symbol and reuses it while `tick.time` is unchanged, recomputing
only when `tick.time` changes (`mt5_read_only_source.py:122-128`). Verified against every §7 requirement:
- **Removes quiet-tick drift:** while `tick.time` is frozen, the cached offset is reused, so ts_close no
  longer climbs against an advancing `now_fn()`. ✓
- **Does not freeze a stale incorrect offset:** the frozen offset carries only the initial polling lag (a
  few seconds at most, always ≤ measured, never over-estimated), and **self-corrects on the very next tick**
  (`cached[0] == tick_time` fails → recompute). It cannot persist a wrong offset beyond one tick. ✓
- **Updates on tick identity change / does not hide M15 transitions:** any `tick.time` change recomputes;
  a genuinely-closing bar is admitted once `now` passes its (now-stable) `ts_close`. ✓
- **Does not create future bars — causality-safe in BOTH directions:** `_bar_from_rate` sets `ts_open =
  rate.time − offset`, so a *more-negative* offset (the drift direction) makes `ts_close` climb *upward*,
  and the closed-filter `ts_close <= now` (`:161`) can then only ever **drop** genuinely-closed bars
  (under-inclusion), never admit a forming bar. The measured offset is always ≤ true (lag-biased downward),
  so `ts_close` is never under-estimated → a forming bar's computed `ts_close` is never pulled below `now`.
  No future leak is reachable via this mechanism, before or after the fix. ✓
- **Restart-safe:** `_offset_cache` is in-memory module-level → empty on process restart → recomputed fresh;
  and episode identity is keyed by the ledger composite key, not the raw watermark, so any sub-second
  cross-restart offset jitter cannot create a duplicate episode. ✓
- **Does not change S5 trading semantics:** see §2.

**MT5_WATERMARK_FIX = PASS.** (The watermark fix is clean; the blockers below are in the observer's
episode/snapshot/restart logic, not in this fix.)

## 2 — S5 ISOLATION (§7) — PASS

`measure_broker_offset_seconds` has exactly **one** non-test caller — `fetch_causal_closed_bars` in the same
module (`mt5_read_only_source.py:152`). Every importer of `mt5_read_only_source` is inside
`apprenticeship_v2/` (the read-only General Observer); **no `live_signal_source/`, `mt5_demo_bridge/`,
`mstrat`, or any trading path imports it.** `s5_observer.py:20` imports only the `ReadOnlyBar` **type**. The
real S5 bar feed is the separate, unchanged `live_signal_source/bar_feed.py::make_broker_offset`. The union
of all three audited commits touches **only** `apprenticeship_v2/` files + 4 VE reports — no real-S5 trading
file. Broker execution is structurally unreachable (`test_broker_execution_disabled.py`: no
`order_send`/position/order call name anywhere in `general_observer/`; MetaTrader5 imported only through the
read-only source; that source has no execution call site). **S5_BEHAVIOR_UNCHANGED = PASS.**

## 3 — ✖ BLOCKER 1: BEFORE-SNAPSHOT FUTURE LEAK (§1 CAUSALITY / BEFORE) — FAIL

The single most load-bearing causal invariant — the frozen BEFORE snapshot is the ONLY data a later
qualitative review may use, and must contain no bar post-dating the trigger — is **violated during any
multi-bar catch-up.** Verified at source:
- `tick.py:83-85` passes the **full** fetched `h4`/`h1`/`m5` arrays (only M15 is sliced to `m15[:i+1]`),
  while the loop (`tick.py:78-90`) processes **every** unprocessed M15 bar.
- `episode_builder.build_episode_record` calls `snapshot = build_snapshot(h4, h1, m15, m5)`
  (`episode_builder.py:138`) with those untruncated arrays; nothing gates `h4`/`h1`/`m5` by
  `event.trigger_bar_ts_close`.
- `build_snapshot` returns `h4[-12:]` / `h1[-24:]` / `m5[-48:]` — the **most recent** bars — and its own
  docstring states the caller MUST truncate to the trigger: *"must not extend past the trigger bar — this
  function does not itself filter by trigger timestamp; that is the caller's responsibility"*
  (`snapshot.py:36-39`). **The caller does not.**

Concrete failure: `M15_FETCH_COUNT = 100`, so the **first run** (`last_m15 is None`) processes ~100 M15 bars
(~25h); any episode created for an older trigger bar freezes a snapshot whose H1 (24 bars = 24h) / H4 (12
bars = 48h) / M5 sections are drawn from the present — **up to ~25h of post-trigger (future) data embedded in
the immutable BEFORE snapshot.** The identical leak occurs on any restart after the daemon was down long
enough for >1 M15 bar to close. In steady-state single-bar ticks the newest H1/H4/M5 ≈ the trigger's close,
so the leak is ~0 — which is exactly why the 177 tests (all single-tick or synthetic) never surface it. The
M15 slice and the major-levels (`compute_eligible_major_levels(h1, as_of_ts_close=bar.ts_close)`,
`episode_builder.py:197`) are causal; the H4/H1/M5 snapshot sections are not. **CAUSALITY = FAIL,
BEFORE_INTEGRITY = FAIL, FUTURE_LEAK_FOUND = YES.**

## 4 — ✖ BLOCKER 2: SWEEP/BREAK DEDUP DRIFT (§2) — FAIL

Spec Section 4A/4B + Section 11 require: one active episode per level-key **at a time**, and *"once that
episode's family closes … the same level may originate a new episode later"* / *"a genuinely new crossing
(price closed back to the original side first) is a legitimately new event, not a duplicate."* The
implementation suppresses such legitimately-new re-crossings:
- `per_class_dedup_key` for SWEEP_REJECTION / STRUCTURAL_BREAK = `(type, level_type, level_price, direction)`
  — **no `underlying_move_id`, no timestamp** (`dedup.py:126-129`).
- `is_duplicate` scans the **entire append-only ledger** and returns True on the first key match
  (`dedup.py:170-177`).

Consequence: after a full round-trip (price closes back through the level → `compute_underlying_move_id`
correctly mints a NEW family), a second sweep/break of the **same** level price/direction is still
suppressed, because the sweep/break key ignores the move id and the old closed episode's row persists
forever. The function's own docstring (`dedup.py:160-167`) claims the new move id resolves this — but the
sweep/break key never consults the move id (only DISPLACEMENT's key does, `dedup.py:130-131`). Reachable in
normal intraday operation (e.g. two sweeps of the same PDH with a round-trip between). This **under-counts
independent underlying moves**, distorting the very evidence base the lesson ladder counts (≥10 independent
moves + ≥70% support). No test covers it — `test_dedup.py` uses a *displacement*, not a re-sweep, for the
independent-move-after-continuity-break case. **DEDUP_AND_UNDERLYING_MOVE = FAIL, SEMANTIC_DRIFT_FOUND =
YES.** (The lesson-voting mechanics themselves are correct — one vote per move, retrospective→zero votes,
Section 19.7 ladder — but they count a corrupted population.)

## 5 — ✖ BLOCKER 3 (lower severity): RESTART CLUSTER DUPLICATE + CATCH-UP HINDSIGHT (§5) — FAIL

- **Missed-move cluster duplicate on crash-before-save:** `append_missed_move_cluster` appends
  unconditionally with **no idempotency guard** (`durable_store.py:241-258`, unlike the scorecard's
  `already_scored`). In `tick.py` the finalized cluster is appended mid-loop (`tick.py:104`) but the H1
  watermark / active-cluster state is persisted only after the loop (`tick.py:108+`). A crash between the two
  re-processes the same H1 bars on restart, regenerates the deterministic `cluster_id`, and re-appends → a
  duplicate cluster row. Bounded (clusters never feed lesson votes, Section 10) but a genuine restart
  re-emit.
- **Pending-BEFORE rebuilt, not reloaded:** there is no persisted pending-BEFORE snapshot; a crash before an
  episode is appended causes the next tick to rebuild the snapshot from the then-current fetch — the same
  future leak as §3, now realized as hindsight-on-restart. `episode_builder.py:157-162` explicitly discloses
  *"A restart-recovery path that might re-freeze a partially-built shell is not yet implemented."*

Episode/score/vote re-emission is otherwise correctly blocked by fresh ledger reads (`is_duplicate`,
`already_scored`). **CHECKPOINT_RESTART = FAIL, DUPLICATE_EVIDENCE_RISK_FOUND = YES.**

## 6 — AREAS THAT PASS (independently confirmed)

- **STRUCTURAL_FINAL = PASS:** `structural_resolution.py:75` inspects only `frozen_ts < bar.ts_close <=
  window_end_ts`; horizon scoring per-horizon bounded (`resolution.py:59`, `scorecard.py:82`). Causal,
  window-bounded, immutable once set.
- **SCORECARD = PASS:** `classify_expectation_correct` (`scorecard.py:115-160`) is a line-for-line
  transcription of Section 19.14 (YES/NO/PARTIAL/NOT_SCORABLE, STRUCTURAL_FINAL mapping, the six expectation
  branches, ROUND_TRIP `>=1.0/>0/==0` boundaries). Corrected VE's earlier `1..9` lesson boundary to the
  Section 19.7 `{0,1}`/`[2,9]`.
- **LESSON_LOOP mechanics = PASS:** one vote per `underlying_move_id` (canonical-episode selection,
  `lesson_voting.py:68-83`), retrospective missed-move clusters never enter the episode ledger or lesson
  inputs (Section 10). (Its input population is corrupted by Blocker 2.)
- **MISSED_MOVE_AUDIT logic = PASS:** H1 rolling window (4 bars), causal ATR as-of window start, exact
  close-to-close direction match, coverage rule A–D with class restriction, cluster continuation only for
  the immediately-next material uncovered same-direction candidate, canonical identity fixed to the first
  candidate. (Persistence idempotency is Blocker 3.)
- **REAL_MT5_E2E = PASS but coverage-incomplete:** the suite ran 177/177/0-skipped against the live terminal
  (I reproduced it); the E2E test walks the required path (closed bars → detector → snapshot → episode →
  BEFORE → resolution → scorecard → lesson eligibility) and broker execution is structurally unreachable.
  But it exercises only single-tick steady state — never the multi-bar catch-up where Blocker 1 manifests.
- **§8 TEST FALSIFICATION:** the revised `test_no_duplicate_processing...` assertion (`delta == 0 or delta %
  900 == 0`) does **not** mask the drift defect: the defect's signature (delta=1, or any non-900-aligned
  delta) still fails, and because the two ticks are back-to-back (~ms apart) a drift can only flip the
  rounded ts_close by ~0–1s — it is physically impossible for a drift to reach a clean 900 multiple, which
  requires a genuine bar close straddling the calls. The revised test is sound.
- **§9 SPEC FIDELITY:** the known Section 11 citation/provenance defect (cross-references citing the wrong
  section number, e.g. "Section 11" for structural resolution, which is the Dedup Contract) is **cosmetic** —
  every actual contract (dedup keys, `underlying_move_id`, structural resolution, restart composite key) is
  concretely specified in the text, so it creates no semantic ambiguity. Non-blocking, as the mandate
  anticipated. (The genuine semantic drift is Blocker 2, in the code vs Section 4/11, not a citation error.)

## 7 — TEST SUITE ADEQUACY (§8) — NO

177/177 is genuine, but the suite has **zero** coverage of all three defect scenarios: (a) multi-bar
catch-up snapshot causality — no test passes an over-long H1/H4/M5 for an older trigger bar; (b) a
re-sweep/re-break of the same level after a price round-trip (test_dedup uses a displacement instead); (c) a
crash between the cluster append and the runtime-state save. The `test_snapshot` "prefix invariance" test
only proves `build_snapshot` doesn't read past its own list — not that the caller truncates. VE's 8 green
runs are real but blind to exactly the paths that fail. **TEST_SUITE_ADEQUATE = NO.**

## 8 — BLOCKERS

```
1. BEFORE-SNAPSHOT FUTURE LEAK (causality) — the frozen BEFORE snapshot's H4/H1/M5 sections are not
   truncated to the trigger bar's ts_close, so during multi-bar catch-up (first run: up to ~25h; any
   post-downtime restart) an older trigger bar freezes post-trigger (future) bars into its immutable BEFORE
   context. tick.py:83-85 → episode_builder.py:138,218-219,230-231 → build_snapshot (snapshot.py:33-45,
   docstring says the caller must truncate; the caller does not). Untested.
2. SWEEP/BREAK DEDUP DRIFT (semantic infidelity) — SWEEP_REJECTION/STRUCTURAL_BREAK dedup key
   (dedup.py:126-129) omits underlying_move_id/timestamp and is_duplicate (dedup.py:170-177) scans the whole
   ledger, so a legitimately-new re-crossing of the same level after a round-trip is wrongly suppressed,
   contradicting spec Section 4A/4B + Section 11 and under-counting independent moves for lesson evidence.
   Untested (test_dedup uses a displacement, not a re-sweep).
3. RESTART CLUSTER DUPLICATE (restart idempotency, lower severity) — append_missed_move_cluster
   (durable_store.py:241-258) has no idempotency guard and is appended mid-loop (tick.py:104) before the H1
   watermark is persisted (tick.py:108+); a crash between re-emits the deterministic cluster on restart.
   Bounded (clusters never feed lesson votes). Same root cause also gives pending-BEFORE hindsight on restart
   (episode_builder.py:157-162, disclosed as "not yet implemented").
```

## 9 — CONCLUSION

The MT5 watermark fix (`1e099aa`) is correct, causality-safe, restart-safe, and cleanly isolated from S5
trading — the high-priority target passes. But the General Observer as a whole is **not causal** (the frozen
BEFORE snapshot leaks up to ~25h of future H1/H4/M5 during any multi-bar catch-up) and **not semantically
faithful** (the sweep/break dedup drops legitimately-new re-crossings the frozen Section 4/11 contract
requires be kept), with an additional restart-duplicate in the missed-move cluster ledger. All three are in
paths the 177 green tests never exercise, which is precisely why VE's PASS framing missed them. The system
is **not** ready for shadow apprenticeship.

```
RED_TEAM_VERDICT = FAIL
GENERAL_OBSERVER_READY_FOR_SHADOW_APPRENTICESHIP = NO
LIVE_SHADOW_AUTHORIZED = NO   BROKER_AUTHORIZED = NO
NEXT_AUTHORIZED_ACTION = NONE — CEO REVIEW REQUIRED
```

Read-only audit; no code modified, no finding fixed, no runtime enabled, no broker authorized. Control
returned to CEO.

---

*Red Team · General Observer V1.1 final audit · watermark fix PASS (causality-safe, S5-isolated) · 3 blockers
found in untested paths: BEFORE-snapshot future leak (up to ~25h on catch-up), sweep/break dedup drift
(Section 4/11), missed-move cluster restart-duplicate · SCORECARD/MISSED-MOVE/STRUCTURAL_FINAL logic sound ·
177/177 real but coverage-blind · VERDICT FAIL · LEDGER E113 (prev E112).*
