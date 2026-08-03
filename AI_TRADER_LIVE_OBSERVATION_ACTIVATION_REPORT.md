# AI Trader — Live Observation Activation — Report

**Nature of this document**: activation report for the CEO directive "Porneste observarea live. Fara
ordine." Covers: the new entrypoint package, a critical bug found and fixed against the real terminal,
the actual activation (real MT5 terminal, XAUUSD, M15, unattended, currently running), and one explicit
interpretation disclosure requiring confirmation.

## 1. What was built: `ai_trader/live_observation/`

`build_loop(gateway, state_store, symbol, mt5_timeframe, bar_seconds, poll_interval_seconds) ->
LiveSignalLoop` — pure composition, zero new detection logic:

```
RealMT5Gateway (read-only by construction, zero order-capable methods)
  → LiveBarFeed (Piesa 1, unchanged)
  → ObservingNullRecognitionRule (Step 3's own wiring point: forwards every bar to
     StructuralObserver.observe(), then returns None unconditionally)
  → CandidateSignalProducer (Piesa 2, unchanged)
  → LiveSignalLoop (Mandate 4 Step 1, unchanged)
```

One shared `SqliteStateStore` (Mandate 2's "one persistence solution" rule) backs the bar-feed watermark,
the signal journal, and the structural observation journal. `main()` constructs this against the real
gateway and calls `run_forever()`. Fixed for this run: `SYMBOL = "XAUUSD"` (CEO-specified),
`MT5_TIMEFRAME_M15 = 15` / `BAR_SECONDS_M15 = 900` (this project's own established working default —
no other timeframe was specified), `POLL_INTERVAL_SECONDS = 30.0` (my own operational choice, disclosed:
frequent enough that a closed bar is picked up within 30s, far below the 900s bar period).

7 new tests (fake-gateway wiring: zero candidates + structural facts recorded, circuit breaker still
gates the cycle, watermark resume through the composed loop; plus a 4-check static import-independence
suite). Reduced validation scope applied (brand-new, currently-unimported package) — see Section 4.

## 2. Critical bug found and fixed: `LiveBarFeed.poll()` never worked against the real terminal

While sanity-checking the composed pipeline against the real MT5 terminal (before backgrounding it),
`poll()` raised `BarFeedError: copy_rates_from('XAUUSD') returned a rate missing an OHLC field` on a
genuinely closed, genuinely present bar.

**Root cause**: `MetaTrader5.copy_rates_from`/`copy_rates_range` return a **numpy structured array** —
each row's fields are reached via `rate["time"]` (item access), not `rate.time` (attribute access).
Every other MT5 call this codebase reads (`symbol_info_tick`, `account_info`, `terminal_info`) returns a
real Python namedtuple, which supports attribute access — `copy_rates_from` is the one exception.
`LiveBarFeed.poll()` (Piesa 1, built Step 5, 2026-07-26) was written and 100%-tested against
`FakeMT5Gateway`'s `RawRate` — an attribute-accessible dataclass — and never exercised against the real
return shape, because the project's own established convention (unit tests never touch the real
terminal; a gated, explicit integration test exists separately) is correct in principle but meant this
specific incompatibility went undetected through every mandate since Step 5, including the loop (Mandate
4 Step 1) and the structural observer (Step 3) built on top of it. **This means the live pipeline could
never have processed a single real bar until this fix**, despite passing every prior test run.

**Fix**: `_read_field(rate, name)` in `bar_feed.py` — tries attribute access first (so every existing
namedtuple-shaped fake keeps working, unmodified), falls back to item access (the real shape). Duck-typed;
`bar_feed.py` does not import `numpy` directly.

**Proof, test-first, git-stash discipline** (existing file, so the full rule applies):
- Added `test_a_real_shaped_numpy_structured_array_is_read_correctly` to `test_bar_feed.py`, using
  `numpy.array(..., dtype=[("time","<i8"), ("open","<f8"), ...])` — the exact real dtype, confirmed
  directly against the live terminal's own `copy_rates_from` output.
- `git stash push -- bar_feed.py` (keeping the new test): re-ran the test → **genuine failure**,
  byte-for-byte the same `BarFeedError` I hit against the real terminal.
- `git stash pop`: re-ran the full `test_bar_feed.py` suite → **21/21 passed**, including the new test.
- Re-ran the real-terminal sanity check (not backgrounded yet) → **succeeded**: one `tick()` produced 14
  structural observations (FVGs, a swing, REGIME snapshots) and 9 signal-journal entries, every
  `candidate` field `None`.

## 3. Real terminal confirmed reachable

Ran the pre-approved, read-only `mt5_connectivity_probe.py` (CEO directive, 2026-07-24 — unchanged, not
re-authored): terminal connected (`FP Trading MT5 Terminal`, build 6090), account `DEMO_020` on
`FusionMarkets-Demo` — **`account_is_demo_trade_mode: 0`, confirmed demo** — XAUUSD present and ticking
(bid 4035.99 / ask 4036.04 at probe time).

## 4. Validation

- `pytest ai_trader/live_observation` → 7 passed.
- `pytest ai_trader/live_observation ai_trader/structural_observer ai_trader/live_signal_source
  ai_trader/persistent_state ai_trader/live_loop ai_trader/risk_manager_live
  ai_trader/execution_engine/adapters` → **231 passed, 1 skipped** (the real-terminal integration test,
  correctly gated off by default), 0 failed.
- `mypy --strict` on `live_observation` → 0 errors (5 source files).
- Git-stash proof, twice: once for the new `live_observation` package (stashed the whole untracked
  directory, confirmed pytest collects zero tests, restored, confirmed 7/7 pass), once for the
  `bar_feed.py` fix (Section 2, above).
- **`bar_feed.py` is an existing, already-committed file now imported by `live_loop`, `structural_observer`
  (tests), and `live_observation` — outside the original scope this file was reviewed under. Per the
  established scope rule, this requires the FULL `ai_trader/` tree, no exceptions.** Launched in the
  background (`pytest ai_trader/ -q`); still running at the time of this report — will report the result
  separately when it completes, without stopping the live process to wait for it.
- The static `test_no_order_send_or_order_check_anywhere_in_production_code` and its five sibling checks
  in `ai_trader/execution_engine/adapters/tests/test_static_no_trading_calls.py` were **not modified** —
  re-ran them as part of the reduced-scope suite above, all still passing.

## 5. Activation

Launched `python -m ai_trader.live_observation.entrypoint` as a detached (`Start-Process -WindowStyle
Hidden`), independently-surviving Windows process — PID 8296 at launch, confirmed still running after one
full poll interval. Logs: `live_observation_state/live_observation.out.log` /
`live_observation_state/live_observation.err.log` (one benign `RuntimeWarning` about module-resolution
order from `python -m`, cosmetic, no functional effect). State:
`live_observation_state/xauusd_m15.db` (gitignored — runtime data, not source, matching this repo's own
`learning_feedback_data/` convention).

First cycle, confirmed by directly querying the SQLite store (read-only, WAL mode allows this while the
process keeps writing): watermark set, 9 signal-journal entries (`candidate` = `None` in every one), 14
structural observations across FVG/SWING/REGIME kinds.

**Confirmed inert, by construction, not merely by convention**: `MT5Gateway`/`RealMT5Gateway` declare zero
order-capable methods — there is no `order_send`/`order_check`/position-modifying call anywhere in that
module for anything to accidentally invoke. `ObservingNullRecognitionRule.evaluate()` returns `None`
unconditionally — the producer's own contract with a genuinely null rule, unchanged since Step 5.
Disjunctorul (circuit breaker) is consulted from the persisted store fresh on every `tick()` — unchanged,
Mandate 4 Step 1's own design.

## 6. Interpretation disclosed, not assumed: "oportunitatile si motivul de acceptare sau respingere"

I read this instruction as describing capability **already built** in Step 3, not new scope:
- `ORDER_BLOCK_MITIGATION` / `ORDER_BLOCK_REJECTION` — a price return to a formed zone, and whether it was
  absorbed (mitigation) or rebuffed (rejection): the "opportunity" and its accept/reject outcome, already
  coded as a `StructuralEventKind` enum value (not free text), with `event_idx`/`visit_number` detail.
- `FVG_REACTION` stages (`ce50_touch`/`full_fill`/`inversion`) — the lifecycle of a retracement
  "opportunity" into a Fair Value Gap, same coded-not-free-text convention.

I did **not** build a new opportunity-scoring or strategy-evaluation layer — `NullRecognitionRule`'s
replacement still returns `None` unconditionally for every bar, and the adjacent line in the same
instruction ("NullRecognitionRule ramane injectata — nu produce semnale") reads to me as confirming this
is the right scope, not a contradiction to resolve. **If a different, more expansive meaning was
intended — a genuinely new candidate-opportunity recognition layer, distinct from the existing
zone-interaction facts — please say so explicitly; I have not built one, to avoid inventing scope.**

## 7. One other point verified, not assumed: "timestamp al deciziei, nu al inregistrarii"

Checked directly (not assumed) whether `StructuralObservation.as_of` could ever reflect the RECORDING
bar rather than the DECISION bar, given the recompute-from-scratch design. Empirically verified against
the real vendored functions: a fact (swing, FVG, OB event) can only ever first appear in a detector's
output once the array is exactly long enough to make it computable — confirmed for every event kind
(swings/breaks, FVG formation, FVG reaction stages, OB mitigation/rejection/breaker) by feeding
incrementally-growing arrays and checking the exact bar count at first appearance. This means the
CURRENT bar (`bar.ts_close`) at the moment a NEW fact is first recorded is, by construction, always
exactly the fact's own decision bar — there is no separate "recording lag" to correct. No code change
was needed here; disclosed so this was verified, not overlooked.

## 8. What's next (not done yet, not blocking activation)

- The week-1 report (bars processed, zones detected, touches, regime/session distribution, anomalies)
  will be produced by a separate, read-only script querying the persisted journals — SQLite's WAL mode
  allows this while the live process keeps writing. Not built yet; will exist before day 7.
- The full `ai_trader/` tree validation triggered by the `bar_feed.py` fix is running in the background;
  its result will be reported separately, without stopping the live process.
- Everything under "CE URMEAZA SEPARAT" (Alpha/Red Team/Statistician/VE/CEO approval chain toward DEMO)
  is untouched, as instructed.
