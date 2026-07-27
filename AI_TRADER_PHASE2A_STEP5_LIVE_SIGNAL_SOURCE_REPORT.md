# Phase 2A, Step 5 — Live Signal Source (#6) — Report

**Scope**: exclusively #6, the CEO's three named pieces (Piesa 1 bar feed, Piesa 2 candidate producer
with injected `NullRecognitionRule`, Piesa 3 append-only journal). No wiring into `orchestrate()` or any
other caller. No real `RecognitionRule` implementation. No strategy logic anywhere. No order submission
anywhere.

## New package: `ai_trader/live_signal_source/`

- **`types.py`** — `Bar` (one CLOSED live bar; deliberately NOT `simulation.types.Bar`, which is
  documented as backtest-only and off-limits for this live path); `BarFeedError`; `LiveCandidate` (this
  package's own equivalent of `CandidateSignal`, see design note below); `RecognitionRule` (Protocol) +
  `NullRecognitionRule` (the one implementation shipped, always returns `None`); `LiveSignalJournalEntry`.
- **`bar_feed.py`** — `LiveBarFeed` (Piesa 1): `poll()` returns every newly CLOSED bar since the last
  call, never a forming one.
- **`producer.py`** — `CandidateSignalProducer` (Piesa 2): drives one poll cycle through the injected
  `RecognitionRule`, journaling every bar either way.
- **`journal.py`** — `LiveSignalJournal` (Piesa 3): append-only, in-memory.

## Design decision requiring disclosure: `LiveCandidate`, not `CandidateSignal`

The CEO's own instruction requires "the producer never receives the execution adapter, statically
enforced." Before writing any code, I read `execution_orchestrator/types.py` (where `CandidateSignal`
lives) and found it imports the execution-capable broker-adapter type from `ai_trader.execution_engine`
and `ai_trader.order_manager.*` **at module level** — meaning `from ai_trader.execution_orchestrator.
types import CandidateSignal` would execute that whole module body, transitively pulling
execution-capable machinery into this package's own import graph, even though no code here would ever
construct or hold an adapter instance.

To keep the "never receives the execution adapter" guarantee true of the entire transitive import
closure — not just of the lines I wrote — this package defines its own `LiveCandidate`: identical
fields, identical direction-vs-stop invariant (enforced at construction, matching the established
defense-in-depth pattern already present in `CandidateSignal`/`TradeProposal`/the risk gate), zero
dependency on `execution_orchestrator`. Converting `LiveCandidate` into a real `CandidateSignal` is a
1:1 field mapping for whichever future, separately-authorized step wires this producer into the
orchestrator.

## Design decision requiring disclosure: what "reuse `shadow_evidence/types.py`" means here

The CEO's instruction: "jurnal append-only: reutilizeaza tipurile din ai_trader/shadow_evidence/
types.py." I read all six of that module's dataclasses before deciding. None fits without fabricating
fields: `ShadowOpportunityRecord`/`ShadowRejectionRecord`/etc. all require an already-scored,
already-risk-decided shadow BACKTEST evaluation (`score_recommendation: Recommendation`,
`shadow_risk_decision: "ALLOW"|"DENY"`, position-leg tracking) — none of which exist at this
pre-risk-evaluation live pipeline stage; forcing a bar-observed-nothing-happened event into that schema
would mean inventing meaningless values to satisfy fields that don't apply yet.

The reuse instead takes the concrete form both packages already establish: `LiveSignalJournalEntry`'s
`candidate` field is typed through `LiveCandidate.direction`, which reuses `ai_trader.signal_engine.
types.Direction` directly — the exact same shared type `shadow_evidence.types` itself imports rather
than redefining its own. No new `Direction` enum was invented anywhere in this package. This is
disclosed as a genuine interpretation call, not a literal one-type-to-one-type mapping, because none
existed to map to.

## Piesa 1: the forming-bar test the CEO specifically required

Motivated by today's data-acquisition finding: the TradingView replay cursor's own bar carries a
provisional close/volume while active, corrupting 1,186 of 355,716 bars in one file. `LiveBarFeed.poll()`
computes each candidate bar's own close time (`ts_open + bar_seconds`) against the injected clock; a bar
whose close time has not yet passed is filtered out silently (not an error — it just is not closed yet).
`test_a_forming_bar_can_never_be_emitted` proves this directly: a bar 800 seconds from closing is fed in,
`poll()` returns nothing. A companion test proves the boundary case (`ts_close == now`) IS emitted — the
boundary belongs to "closed."

## Piesa 2: acceptance test, verbatim

`test_null_rule_produces_zero_candidates_end_to_end` — the system runs cap-coada (feed → producer →
`NullRecognitionRule`) and produces zero candidates. `test_null_rule_still_journals_every_observed_bar`
proves the journal grows anyway — the "eyes" the CEO described: the system observes the market and does
nothing with what it sees, provably.

## Piesa 3: append-only, disclosed as in-memory only

`LiveSignalJournal.record()` is the only mutator; `entries` returns an immutable tuple, never the
backing list (`test_entries_is_a_tuple_not_the_backing_list` proves a returned snapshot is unaffected by
a later `record()`); no remove/clear/delete method exists at all
(`test_has_no_remove_or_clear_method`). No disk/database persistence was authorized or built — a
restarted process starts with an empty journal. The CEO's Step 5 specification did not name persistence
as a requirement here, unlike Step 1's suspension state, which explicitly needed to survive a restart.

## Test discipline: fails before, passes after, `git stash`-verified

Three separate stash cycles, one per meaningfully new behavior:
1. **`bar_feed.py`** stashed alone — re-ran `test_bar_feed.py`, got a genuine
   `ModuleNotFoundError: No module named 'ai_trader.live_signal_source.bar_feed'` (not a stub failure),
   `git stash pop` restored it, all 9 tests passed.
2. **`producer.py` + `journal.py`** stashed together — re-ran the full suite, got the same genuine
   `ModuleNotFoundError` for `journal` (imported first in `__init__.py`), pop restored both, all 17
   tests (bar feed + journal + producer) passed.
3. One fixture bug found and fixed in the process, same recurring pattern as Steps 3/4:
   `FakeMT5Gateway(rates=None)` originally fell back to `[]` instead of genuinely returning `None` from
   `copy_rates_from()`, silently defeating `test_raises_when_gateway_returns_none` until corrected with
   an explicit unset-sentinel (identical fix shape to Step 4's `mt5_account_bridge` fixture bug).

## New validation-scope rule applied (CEO decision, this step)

Per the rule just added to `AI_TRADER_PHASE2A_DEPENDENCY_GRAPH.md`: `live_signal_source` is a brand-new
package nothing imports yet (confirmed: `grep -rl "live_signal_source" ai_trader` outside its own
directory returns nothing), and no existing file was modified except the dependency-graph document
itself. Reduced scope — the same named package list Steps 3/4 used, plus `live_signal_source` — is
therefore the CORRECT choice under the new rule, not a judgment call.

## Validation

```
pytest ai_trader/risk_manager_live ai_trader/execution_orchestrator ai_trader/mt5_demo_execution \
  ai_trader/order_manager ai_trader/execution_engine ai_trader/risk_manager ai_trader/portfolio_manager_live \
  ai_trader/mt5_pnl_source ai_trader/mt5_account_bridge ai_trader/live_signal_source -q
-> 736 passed, 2 skipped (gated real-terminal tests, unaffected), 0 failed

mypy --strict ai_trader/risk_manager_live ai_trader/execution_orchestrator ai_trader/mt5_demo_execution \
  ai_trader/order_manager ai_trader/portfolio_manager_live ai_trader/mt5_pnl_source ai_trader/mt5_account_bridge \
  ai_trader/live_signal_source
-> Success: no issues found in 100 source files
```

## Exact diff surface

Only the new `ai_trader/live_signal_source/` package (9 source files including tests) plus the
dependency-graph document (new validation-scope rule, #6 marked DONE). No existing file modified.

## Disclosed limitations / observations (not silently deferred)

- **Not wired anywhere.** No caller constructs a `LiveBarFeed`/`CandidateSignalProducer` in production;
  no scheduler/loop drives `run_once()` repeatedly yet. This is exactly the CEO's own framing for this
  step: give the system eyes, not hands.
- **`LiveCandidate` vs `CandidateSignal`** — a genuinely new type, not the one named in the original
  Demo Readiness graph entry, for the transitive-import reason above. Converting it 1:1 is a small,
  well-defined future step, not a design risk, but it is a step that does not yet exist.
- **Journal is in-memory only** — see Piesa 3 above.
- **`LiveBarFeed`'s dedup state (`_last_emitted_ts_open`) does not survive a process restart** — same
  class of problem already logged for the equity high-water mark (Step 3) and consecutive-loss window
  (Step 3): a restarted feed would re-emit whatever bars are still within its `lookback_count` window on
  its first `poll()` after restart. Not itemized by the CEO for this step; recorded here as an
  observation, matching the established "long-running process robustness" graph item this already falls
  under (item 15, not authorized to build).

**Stopping here per instruction.** Report, commit, push, and remote-hash verification follow. Awaiting
approval before the next step in the approved order (#7 — confirm whether a separate scheduler/loop is
still needed once #6 exists, or whether bar-close events already satisfy it).
