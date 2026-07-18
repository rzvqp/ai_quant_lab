# Phase 6.10 — Implementation Checkpoint 3 Report

**Date:** 2026-07-18. **Scope:** integrate the first existing production strategy set into the
completed multi-strategy Shadow architecture — prove the infrastructure can execute multiple *existing*
strategies simultaneously, independently, and deterministically. No new strategies, no trading-logic
changes, no Signal/Scoring/Risk/Execution/competitive-portfolio changes.

---

## 1. Executive summary

Checkpoint 3 is complete, and it found and fixed a real bug. "The first existing production strategy
set" is interpreted as the full 43-strategy registered library (`S1-S31/S38-S46/S48/S50/S51` —
`registry.registered_strategy_ids()`, the only such set already established in this repository's own
history: every Wave D/Phase 6.9/6.10 competitive run has used exactly this set). Registering it via
Shadow required **zero new execution logic** — the architecture built through Checkpoint 2 is already
generic — but running validation at this real scale (rather than the 1-4-strategy scale prior
checkpoints tested) **surfaced a genuine correctness bug** in Checkpoint 1C's own entry-tracking logic,
invisible at small N, found here, root-caused, and fixed.

## 2. Architecture summary

**Already satisfied, re-verified at N=43 (not re-implemented):** concurrent multi-strategy execution,
isolated virtual portfolios/ledgers/statistics/summaries, deterministic replay, failure isolation,
byte-identical competitive execution.

**New this checkpoint:**
- `ai_trader/shadow_evidence/config.py::all_registered_strategies()` — a config-only helper returning
  the full, real, already-registered strategy set (triggers the same lazy family-registration import
  `build_runtime_handles()` already performs internally, so it never returns an accidentally-empty set).
  Not a new execution path — a one-line, discoverable way to configure `ShadowConfig`.
- **A real bug fix in `ai_trader/shadow_evidence/engine.py::_observe_one`.**

### 2.1 The bug (found empirically, not by inspection)

At N=43, over the SAME 85-day fixture window every prior test uses, `test_one_strategy_failure_among_
all_43_is_isolated` failed: two strategies (S1, S6) that were never targeted by the test's own injected
failure degraded anyway, with a genuine internal error: *"closing TradeRecord for S1/XAUUSD with no
tracked open position_id."*

**Root cause**: a strategy's shadow entry is frequently a LIMIT-priced BRACKET order (whenever its
signal carries an explicit `entry` price — `execution_engine/builder.py`'s own `OrderTypeMappingPolicy`)
that can stay WORKING for many bars before the market touches it. `LIMIT_MAX_PER_SYMBOL` only sees OPEN
positions (`PortfolioState.open_positions`), never pending orders — so the SAME dedicated RiskManager
can legitimately ALLOW a *second* entry for the same symbol while the first is still unresolved.
Checkpoint 1C's own `account.pending_entries[symbol]` bookkeeping (keyed by symbol) **silently
overwrote** the first order's own tracking record with the second's, orphaning the first order's
eventual fill — which then closed with no `position_id` this engine still recognized.

**Why this never appeared at N≤4**: the race requires a specific, narrow window (a LIMIT entry pending
for multiple bars AND the same strategy re-signaling in that window) — rare enough that none of
S10/S21/S39/S40 hit it over the 85-day window in three checkpoints of prior testing, but likely at
N=43 simply from more strategies each having their own independent chance of it.

**The fix**: `_observe_one` now checks whether an entry is already pending for a symbol before
submitting a new one. If so, the second ALLOW is recorded honestly as a shadow-internal denial
(`denied_reason_code="SHADOW_ENTRY_ALREADY_PENDING"`) rather than corrupting the bookkeeping — the
underlying RiskManager's own ALLOW is disclosed, not silently dropped. This is a **narrower divergence
from "submit every RiskManager ALLOW"** than the already-disclosed Checkpoint 1C score-reuse semantics,
and it is necessary: the real, unmodified `PortfolioSimulator` would merge two same-direction fills into
one `Position` via weighted-average scale-in, which is structurally incompatible with this engine's own
one-`position_id`-per-virtual-entry model. The real competitive path was never at risk — it has no
`pending_entries`-style side table to desynchronize.

**Regression coverage added**: a fast, hand-traced unit test
(`test_a_second_allow_while_the_first_entry_is_still_pending_does_not_corrupt_bookkeeping`) reproduces
the exact race deterministically (a bar price that never touches the entry's own limit, a second ALLOW
in between, then a fill) — no longer dependent on 43-strategy scale to catch a regression here.

## 3. Strategies integrated

All 43 currently-registered production strategies: `S1–S31, S38–S46, S48, S50, S51` (S32–S37
NOT_IMPLEMENTED, S47/S49 technically invalid — per `PROJECT_STATE_v2.md` §2, unchanged, not touched by
this checkpoint). None hand-picked; the full set, verified by `len(all_registered_strategies()) == 43`.

## 4. Files modified

| File | Nature of change |
|---|---|
| `ai_trader/shadow_evidence/config.py` | `all_registered_strategies()` helper (new function). |
| `ai_trader/shadow_evidence/engine.py` | Bug fix in `_observe_one` (§2.1) — the only execution-affecting change. |
| `ai_trader/shadow_evidence/types.py` | Docstring update documenting the new `SHADOW_ENTRY_ALREADY_PENDING` denial reason. |

**Not modified**: `ai_trader/simulation/harness.py`, Signal Engine, Scoring Engine, Risk Manager,
Execution Engine, competitive portfolio, `strategy_health/` — confirmed empty diff via `git diff --stat`
before committing.

## 5. Validation results

```
pytest ai_trader/ -q                          -> 1653 passed (Checkpoint 2 baseline 1646 + 7 net new)
mypy --strict ai_trader/ --exclude 'tests/'   -> Success: no issues found in 170 source files
coverage --omit="*/tests/*":
  shadow_evidence/{aggregation,config,engine,types}.py: ALL 100%
  TOTAL 10043 stmts, 432 miss, 96%  (baseline: 10035/432/96% -- zero new net misses)
```

**Timing (empirical, not the formal Design §13 test 8 benchmark — see §7)**: a 7-day quick check found
only a **1.17x slowdown** at N=43 vs. Shadow disabled (43 accounts constructed, only 6 positions/6
trade legs opened in 7 days — consistent with Phase 6.9A's own finding that most signals are low-
frequency). The full 85-day validation runs in low single-digit minutes per test.

## 6. Test results

- `test_all_43_production_strategies_execute_concurrently_with_byte_identical_competitive_execution`:
  competitive parity at N=43; multiple strategies traded concurrently; every trading strategy's own
  positions/legs/summary checked exhaustively for cross-contamination — none found.
- `test_all_43_production_strategies_replay_is_deterministic`: two runs of the identical
  `(run_id, config)`, full shadow-ledger fingerprint byte-identical.
- `test_one_strategy_failure_among_all_43_is_isolated`: one specific strategy (S12) force-failed;
  confirmed only it degrades, every other strategy (including ones that actually traded) continues,
  competitive execution unaffected. **This test is what found the bug in §2.1** — it failed on its
  first run (extra, unintended degradations from S1/S6), was root-caused rather than loosened, and
  passes cleanly against the fix.
- `test_a_second_allow_while_the_first_entry_is_still_pending_does_not_corrupt_bookkeeping` (new, fast
  unit test): deterministic regression coverage for the fix itself.
- 3 new `test_config.py` tests for `all_registered_strategies()`.

## 7. Remaining limitations

- The formal Design §13 test 8 runtime/memory benchmark (full 13-month/23,639-bar window at N=43) was
  **not run** — this checkpoint validates CORRECTNESS at N=43 over the established 85-day window, per
  its own stated objective ("prove the infrastructure CAN execute... not to optimize"), not throughput
  at full historical scale. The 1.17x-at-7-days empirical data point (§5) is informative but not a
  substitute for that formal benchmark, which remains separate, not-yet-authorized work.
- Strategy Health integration, capital/portfolio allocation: unchanged, untouched, still unselected.
- The `SHADOW_ENTRY_ALREADY_PENDING` divergence (§2.1) is a new, narrow, disclosed addition to Shadow's
  own already-established "does not reconstruct isolated re-scoring" semantics (Checkpoint 1C's own
  CEO-ratified ruling) — not a new category of concern, but worth naming explicitly for future sessions.

## 8. Final state

- **Commit**: see chat report (this file is committed alongside that state).
- **Branch**: `ai-trader-implementation`.
- **Working tree**: clean.
