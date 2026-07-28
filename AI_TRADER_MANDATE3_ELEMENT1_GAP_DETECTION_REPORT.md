# AI Trader — Mandate 3, Element 1: Gap Continuity Detection — Report

**Scope**: exactly what item #7's own verification flagged — a bar whose `ts_open` is not exactly
`bar_seconds` after the previous emitted bar is now detected, classified, and journaled. No loop, no
scheduler, no imputation, no interpolation. Shadow mode remains blocked pending Element 2.

## `code/gapfind.py`'s MAINTENANCE rule, reused verbatim

Read the exact source before writing anything: `code/gapfind.py:11` —
```python
if mins<=75 and t0.hour in (20,21): continue
```
where `mins = d[i]/60` is the raw open-to-open difference between the last good bar and the next one,
and `t0` is the LAST GOOD bar's own timestamp (not a "nominal gap start"). `gap_classification.
_is_maintenance_window(gap_start, duration_seconds)` reproduces this exact boolean expression on the
exact same two quantities — `GapRecord.gap_start` IS that `t0`, `duration_seconds` IS that raw
open-to-open difference in seconds. Not reinterpreted, not rewritten.

## WEEKEND, a new decision (no prior rule existed to reuse)

No CEO-specified formula existed for this one, unlike MAINTENANCE. Decision, disclosed: a gap is
WEEKEND if its span contains any UTC calendar day that is a Saturday (`_spans_a_saturday`). Robust to
the exact Friday-close/Sunday-open time varying slightly by broker, and by construction never confused
with MAINTENANCE — a real weekend closure (~48h) is always far longer than the 75-minute allowance, so
checking WEEKEND first is a clarity choice, not a correctness-critical one (proven by
`test_weekend_takes_priority_even_if_it_happens_to_start_at_hour_20`, which shows the ordering doesn't
actually change the outcome, but makes the code's intent explicit).

## Design: report, never fill

`GapRecord` (`types.py`) carries `symbol`, `gap_start`, `gap_end`, `duration_seconds`, `classification`
— nothing else. No estimated/interpolated bar is ever constructed for the missing span. `LiveBarFeed.
poll()` computes gaps by comparing each newly emitted bar's `ts_open` against the running "previous"
reference (starting from `_last_emitted_ts_open`, including a value LOADED from Mandate 2's persisted
watermark — so a gap that occurred while the process was down is detected the same way as one that
occurred mid-run, no special-casing needed). `last_gaps()` exposes whatever was found during the MOST
RECENT `poll()` only; `CandidateSignalProducer.run_once()` is what durably records each one, via the
journal's new `record_gap()`/`gaps` (Mandate 2's exact same persistence discipline — a separate log,
`f"{log_name}.gaps"`, so gap rows are never confused with observation rows).

## Test discipline: fails before, passes after, `git stash`-verified

Four cycles, one per file with real new behavior:
1. `gap_classification.py` (new file) — stashed, genuine `ModuleNotFoundError`, restored, 8/8 passed.
2. `bar_feed.py` (`last_gaps()` + continuity check in `poll()`) — stashed, all 8 new tests failed with
   `AttributeError: 'LiveBarFeed' object has no attribute 'last_gaps'`, restored, 20/20 passed.
3. `journal.py` (`record_gap()`/`gaps`) — stashed, all 5 new tests failed with the same `AttributeError`
   shape for `LiveSignalJournal`, restored, 15/15 passed.
4. `producer.py` (wiring `last_gaps()` into the journal) — stashed, the one test that actually exercises
   the connection failed (`0 == 1`, the gap was detected by the feed but never reached the journal),
   restored, 6/6 passed.

## Validation-scope rule applied, re-verified after the change

`grep -rl "live_signal_source" ai_trader --include="*.py"` outside `live_signal_source/`'s own directory
still returns only `persistent_state/store.py`'s own docstring (naming its three consumers in prose, not
an import) — unchanged from Mandate 2. Reduced scope (the established package list) remains correct.

## Validation

```
pytest ai_trader/live_signal_source/ -q
-> 54 passed

pytest ai_trader/risk_manager_live ai_trader/execution_orchestrator ai_trader/mt5_demo_execution \
  ai_trader/order_manager ai_trader/execution_engine ai_trader/risk_manager ai_trader/portfolio_manager_live \
  ai_trader/mt5_pnl_source ai_trader/mt5_account_bridge ai_trader/live_signal_source ai_trader/persistent_state -q
-> 788 passed, 2 skipped (gated real-terminal tests, unaffected), 0 failed

mypy --strict ai_trader/risk_manager_live ai_trader/execution_orchestrator ai_trader/mt5_demo_execution \
  ai_trader/order_manager ai_trader/portfolio_manager_live ai_trader/mt5_pnl_source ai_trader/mt5_account_bridge \
  ai_trader/live_signal_source ai_trader/persistent_state
-> Success: no issues found in 108 source files
```

## Exact diff surface

New: `ai_trader/live_signal_source/gap_classification.py` + its test file. Modified: `types.py` (2 new
types), `bar_feed.py` (continuity check + `last_gaps()`), `journal.py` (`record_gap()`/`gaps`),
`producer.py` (wiring), plus their own test files. No file outside `live_signal_source/` touched.

## Disclosed limitations / observations (not silently deferred)

- **Gap detection is a per-symbol, per-feed concern.** A `LiveBarFeed` only ever compares its own
  sequence to itself; nothing cross-checks against a second data source.
- **The MAINTENANCE window is a fixed rule (20:00-21:00 UTC, ≤75 min), reused verbatim from
  `code/gapfind.py` for XAUUSD/OANDA — not parameterized per-symbol or per-broker.** If a different
  instrument/broker needs a different maintenance window, that is a future, separate decision — this
  step deliberately did not generalize beyond what was asked.
- **`last_gaps()` is not cumulative** — it reflects only the immediately preceding `poll()`. The
  cumulative, durable record is `LiveSignalJournal.gaps` (via the producer), not the feed itself.

**Stopping here per instruction — publishing before starting Element 2.**
