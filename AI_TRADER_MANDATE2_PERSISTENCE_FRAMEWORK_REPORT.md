# AI Trader — Mandate 2: Persistence Framework — Report

**Scope**: exactly the three components named — `LiveBarFeed`'s watermark, `LiveSignalJournal`'s
history, `MT5PortfolioStateSource`'s equity high-water mark — with ONE shared persistence engine, not
three separate mechanisms. No loop, no scheduler, no gap detection, no virtual P&L source, no HMM
integration. Shadow mode remains blocked until this mandate closes; nothing here starts a live loop.

## New package: `ai_trader/persistent_state/`

- **`types.py`** — `PersistenceError`, the fail-closed signal matching this repository's own convention
  (`PortfolioDataUnavailableError`, `AccountDataUnavailableError`).
- **`store.py`** — `SqliteStateStore`: one class, one SQLite file, two tables (`kv_state` for
  upsert-latest-value, `append_log` for append-only rows keyed by a caller-supplied `log_name`).

## Why SQLite, not hand-rolled binary files with a hash check

Justification, since the choice was left open:

1. **Stdlib.** `sqlite3` ships with Python — no new dependency.
2. **Atomicity without hand-rolling it.** SQLite's own transaction log makes every write atomic by
   construction. A crash mid-write leaves the last COMMITTED state intact — never a torn write. Getting
   the same guarantee from raw binary files requires hand-rolling atomic rename-and-checksum logic
   myself: more custom code, more edge cases, on the exact correctness-critical path ("no duplicate
   bars, no emptied journal, no reset metrics") this mandate cares about most.
3. **One engine, two access patterns, three consumers.** The watermark and equity high-water mark both
   need upsert-latest-value; the journal needs append-only. SQLite's two small tables serve both from
   one file — which is what makes this genuinely ONE solution rather than three bespoke ones.
4. **Integrity verification, the same intent under a different mechanism.** `SqliteStateStore.
   verify_integrity()` runs SQLite's own built-in `PRAGMA integrity_check` at construction time and
   raises `PersistenceError` if it fails (proven by `test_raises_persistence_error_on_a_corrupt_file`,
   which writes garbage bytes to a `.db` path and confirms the store refuses to open). This plays the
   same role a hash check would have played for a binary format, using the database engine's own native
   corruption detection rather than a custom scheme.

## Wiring: additive, backward-compatible, per consumer

Each of the three consumers gained one new optional constructor parameter (`state_store:
SqliteStateStore | None = None`). Omitting it preserves the exact prior in-memory-only behavior —
confirmed because every pre-Mandate-2 test in all three files still passes completely unmodified.

1. **`LiveBarFeed`** (`bar_feed.py`) — watermark key `f"live_signal_source.bar_feed:{symbol}:
   {mt5_timeframe}"`. Loaded at construction (`_load_persisted_watermark`), written through at the end
   of every `poll()` that emits new bars. Two different symbols on the same store never collide
   (`test_watermark_is_scoped_per_symbol_and_timeframe`).
2. **`LiveSignalJournal`** (`journal.py`) — every entry (a `LiveSignalJournalEntry`, `candidate` field
   included) is JSON-serialized (`_serialize_entry`/`_deserialize_entry`) and appended to a `log_name`
   -scoped row set. Loaded IN FULL at construction — not just what this instance itself observes — and
   written through on every `record()`. A real `LiveCandidate` (not just `None`) round-trips intact,
   including the `Direction` enum (`test_a_candidate_round_trips_through_persistence`).
3. **`MT5PortfolioStateSource`** (`source.py`) — key `"mt5_pnl_source.equity_high_water_mark"`. At
   construction, a PERSISTED value takes precedence over `initial_equity_high_water_mark` (a real prior
   observation outranks a caller-supplied seed); the seed remains the fallback only when nothing has
   been persisted yet. Every upward ratchet writes through immediately.

## Consecutive-loss count: verified, not touched

Re-read `source.py` before touching anything: `compute_consecutive_losses` is called fresh, every single
`current_portfolio_state()` call, over a live 7-day `history_deals_get()` query — there is no in-memory
attribute for it anywhere in the class, unlike `_equity_high_water_mark`. A restart does not reset
anything here, because nothing about it is retained between calls in the first place. Its own,
already-disclosed limitation ("only sees the same 7-day window fetched for weekly P&L") is a
DATA-WINDOW question, not a persistence one — a different, already-separately-flagged, still-not-
authorized graph item ("consecutive-loss detection beyond the weekly window"). Building a persisted
running counter to extend that window would be new scope beyond what this mandate authorized ("Nu
detectarea de goluri" reads on this the same way); nothing was added here, consistent with "no test
that fails = don't touch it."

## Determinism, proven per component

Every consumer has a dedicated "simulated restart" test: construct a first instance against a real
on-disk `SqliteStateStore`, observe/record something, then construct a SECOND, brand-new instance
against the SAME store (never the same object) — proving genuine cross-instance persistence, not just
one connection's own lifetime:

- `test_watermark_survives_a_simulated_restart` — the second `LiveBarFeed` does not re-emit a bar the
  first one already emitted.
- `test_history_survives_a_simulated_restart` — the second `LiveSignalJournal` sees both prior entries
  immediately, not an empty history.
- `test_high_water_mark_survives_a_simulated_restart` — the second `MT5PortfolioStateSource`, even after
  equity has since DROPPED, still reports the higher, persisted peak — not a false new peak from the
  post-restart low.

## Test discipline: fails before, passes after, `git stash`-verified

Four separate stash cycles, each proving a genuine failure (not a stub):
1. `persistent_state/store.py` stashed alone — `ModuleNotFoundError` for the whole new package, all 10
   `test_store.py` tests uncollectable. Restored, all 10 passed.
2. `live_signal_source/bar_feed.py`'s modification stashed — the 2 new persistence tests failed with
   `TypeError: LiveBarFeed.__init__() got an unexpected keyword argument 'state_store'` (not an import
   error — the exact missing capability). Restored, all 12 passed.
3. `live_signal_source/journal.py`'s modification stashed — the same `TypeError` shape for
   `LiveSignalJournal`, 4 new tests failed. Restored, all 9 passed.
4. `mt5_pnl_source/source.py`'s modification stashed — the same `TypeError` shape for
   `MT5PortfolioStateSource`, 4 new tests failed. Restored, all 16 passed.

## Validation-scope rule applied, and re-verified after the change (not just before)

Per the rule this mandate itself asked to be added at Step 5: an existing file only forces full-tree
validation when something OUTSIDE the current scope imports it. Re-checked directly, AFTER making the
changes (not assumed from before): `grep -rl "live_signal_source.bar_feed\|live_signal_source.journal\|
mt5_pnl_source.source" ai_trader` outside those two packages' own directories returns exactly one hit —
`persistent_state/store.py`'s own docstring, listing its three consumers by name in prose, not an
import. `persistent_state` is the dependency direction those three files point AT, never the reverse.
Reduced scope — the same established package list plus the new `persistent_state` package — is
therefore the correct choice, re-confirmed rather than re-asserted.

## Validation

```
pytest ai_trader/risk_manager_live ai_trader/execution_orchestrator ai_trader/mt5_demo_execution \
  ai_trader/order_manager ai_trader/execution_engine ai_trader/risk_manager ai_trader/portfolio_manager_live \
  ai_trader/mt5_pnl_source ai_trader/mt5_account_bridge ai_trader/live_signal_source ai_trader/persistent_state -q
-> 764 passed, 2 skipped (gated real-terminal tests, unaffected), 0 failed

mypy --strict ai_trader/risk_manager_live ai_trader/execution_orchestrator ai_trader/mt5_demo_execution \
  ai_trader/order_manager ai_trader/portfolio_manager_live ai_trader/mt5_pnl_source ai_trader/mt5_account_bridge \
  ai_trader/live_signal_source ai_trader/persistent_state
-> Success: no issues found in 106 source files
```

## Exact diff surface

New: `ai_trader/persistent_state/` (7 source files including tests). Modified: `live_signal_source/
bar_feed.py`, `live_signal_source/journal.py`, `mt5_pnl_source/source.py` (the three wired consumers,
each an additive, backward-compatible optional parameter), plus their own test files and
`test_import_independence.py` allow-lists (added `ai_trader.persistent_state`). No other file touched.

## Disclosed limitations / observations (not silently deferred)

- **Nothing is wired into a caller yet.** No production code constructs a `SqliteStateStore` or passes
  one to any of the three consumers — that requires deciding a database file path/location, which was
  not part of this mandate's scope (persistence mechanism only, not deployment wiring).
- **Single-writer design.** No multi-process locking beyond SQLite's own default file locking was built
  or is needed — this system runs as one process; concurrent writers were never in scope.
- **Bar/gap continuity detection remains unbuilt** (explicitly out of scope this mandate, per "Nu
  detectarea de goluri") — persistence means a restart resumes exactly where it left off; it does not by
  itself detect a gap that occurred for a reason OTHER than a restart (a mid-run connection drop still
  falls under the already-disclosed, not-yet-authorized item from the #7 verification).
- **Consecutive-loss count, disclosed above**: verified to have nothing to persist; not touched.

**Stopping here per instruction.** Report, commit, push, and remote-hash verification follow. Order
remains as instructed: persistence first, loop after — the loop itself remains unbuilt and unauthorized.
