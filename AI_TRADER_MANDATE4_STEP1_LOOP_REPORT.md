# AI Trader — Mandate 4, Step 1: The Unattended Loop — Report

**Scope**: exactly item #7 from the dependency graph, the last piece REMAINS-OPEN since the #7
verification established it was not subsumed by #6. No real orders. No execution adapter. The producer
this loop drives is still constructed with `NullRecognitionRule` — nothing here changes what candidates
get produced.

## New package: `ai_trader/live_loop/`

`LiveSignalLoop` orchestrates `CandidateSignalProducer` (Step 5) at interval-based scheduling. It adds
exactly two things none of the underlying pieces already provide — everything else is inherited for free
from work already proven in Mandates 2 and 3:

- **Interval-based scheduling** (`tick()`/`run_forever()`).
- **Circuit-breaker consultation before every cycle's action**, from the persisted state (Mandate 3,
  Element 2) — never cached, re-read fresh on every single `tick()`.

## What is inherited, not rebuilt

- **Restart-correct resume from the persisted watermark** — `LiveBarFeed`'s own Mandate 2 behavior. The
  loop only needs to construct the feed with a `state_store`; `test_restart_resumes_from_the_persisted_
  watermark_through_the_loop` proves this holds through the loop's own `tick()`, not just at the feed's
  own unit-test level.
- **Gaps journaled with their classification** — `CandidateSignalProducer.run_once()`'s own Mandate 3,
  Element 1 behavior (calls `feed.last_gaps()`, journals each via `journal.record_gap()`).
  `test_gaps_are_journaled_through_the_loop` proves this holds end-to-end through the loop.

## Circuit-breaker consultation, exact semantics

`tick()` calls `load_persisted_circuit_state(state_store)` FRESH every time — not read once at
construction. If the state is not `READY`, the cycle's action (`producer.run_once()`) is skipped
entirely: no bars processed, no journal entries, nothing. `test_circuit_breaker_is_consulted_from_the_
persisted_store_not_a_stale_snapshot` proves a suspension applied BETWEEN two `tick()` calls (on the same
loop object, nothing about the loop itself changed) takes effect on the very next tick.

This loop does **not** itself run `evaluate_circuit_state` — that requires a live `PortfolioStateSource`,
which stays out of scope here exactly as Mandate 2's "Fara sursa de P&L virtual" already established. It
only consults whatever is already persisted; something else (not yet built) is responsible for actually
evaluating breaches and persisting transitions.

## Clean stop

`stop()` sets a plain flag — safe to call from a signal handler, another thread, or a test.
`install_default_signal_handlers()` wires `SIGINT`/`SIGTERM` to it for a real deployment; not called
automatically (registering OS signal handlers is a deployment decision, not a constructor side effect).
`run_forever()` closes the state store in a `finally` block on the way out, regardless of how the loop
exits — `SqliteStateStore` commits every write immediately (its own autocommit design, Mandate 2), so
`close()` here is about releasing the file handle cleanly, not flushing anything unsaved.

## Disclosed, not built

A single `tick()` raising (e.g. `BarFeedError` from a transient MT5 disconnect) propagates out of
`run_forever()` uncaught — there is no retry/backoff. A months-long unattended run needs SOME answer to
this eventually, but the actual policy (immediate retry vs. backoff, attempt limits, what counts as an
escalation) is a real design decision this mandate did not specify; building one unrequested would be
inventing a policy, not implementing a specification.

## Test discipline: fails before, passes after, `git stash`-verified

`loop.py` stashed alone (a brand-new file in a brand-new package) — genuine
`ModuleNotFoundError: No module named 'ai_trader.live_loop.loop'`, all 10 tests uncollectable. Restored,
all 10 passed, plus 5 import-independence checks (15/15 total).

## Validation-scope rule: full tree, per your explicit instruction to apply it the same way

The loop imports from `live_signal_source`, `persistent_state`, and `risk_manager_live` — existing
packages. Per your instruction ("bucla va importa din pachete existente, deci probabil arbore intreg...
aplic-o la fel"), ran the full `ai_trader/` tree rather than negotiating scope narrower.

```
pytest ai_trader/ -q
-> 2886 passed, 2 skipped, 0 failed, in 16629.44s (4h37m09s). Clean on the first run -- no fix needed,
   unlike Mandate 3 Element 2 (which found one forgotten allow-list entry).

mypy --strict ai_trader/
-> 227 pre-existing errors, all in simulation/shadow_evidence/strategy_runtime test files -- confirmed
   via grep against every package touched this whole mandate series (risk_manager_live,
   execution_orchestrator, persistent_state, live_signal_source, live_loop, mt5_pnl_source,
   mt5_account_bridge, mt5_demo_execution, order_manager, execution_engine, risk_manager,
   portfolio_manager_live): zero matches. Same 227, same files, as Mandate 3 Element 2's own run --
   nothing regressed, nothing new broken.
```

## Exact diff surface

New: `ai_trader/live_loop/` (5 source files including tests). No existing file modified.

**Stopping here per instruction.** Report, commit, push, and remote-hash verification follow. Awaiting
approval before Mandate 4's remaining steps (the structural-detector investigation report and, pending
your direction, the observer wiring).
