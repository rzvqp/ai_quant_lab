# AI_TRADER_S5_MT5_DEMO_UNATTENDED_SOAK_REPORT

**Mandate**: `AI-TRADER-S5-MT5-DEMO-UNATTENDED-SOAK-001`
**This report's honest scope**: this mandate asks for an unattended operation that runs for up to 60
CALENDAR DAYS or 20 closed trades. That duration cannot occur within one working session -- what THIS
report documents is the complete orchestration infrastructure (built, unit-tested, and live-smoke-verified
against the real connected DEMO terminal, including one real defect found and fixed live), NOT a
completed 60-day/20-trade soak. The actual multi-week unattended run is a separate deployment step,
addressed explicitly in section 9 below rather than silently assumed.

## 1. What was built

`ai_trader/new_brain_live/strategy_platform/mt5_demo_bridge/soak/` -- 7 production modules + 1
entrypoint + 8 test files (36 new tests). Full module map and design rationale in
`S5_MT5_DEMO_UNATTENDED_SOAK_CONTRACT.md`. Builds on the prior mandate's `mt5_demo_bridge/` completely
unmodified -- `demo_execution_adapter.execute()`, the account hard gate, and the risk sizer are reused
as-is; this mandate adds continuous operation (restart reconciliation, position lifecycle, safety
monitor, checkpoints, health snapshots, termination conditions) around them.

## 2. Restart reconciliation, position lifecycle (sections 13-15)

`run_soak` calls `reconcile_in_doubt_identities` (pre-existing, unmodified) as its literal first action,
before even the bounded warmup fetch -- `test_restart_reconciliation_runs_before_any_new_processing`
proves an ambiguous in-doubt identity present at startup trips the safety monitor and terminates the run
as `C_SAFETY_BLOCKER` before any new bar is ever processed. Every poll iteration also runs `detect_new_
open_positions`/`detect_closed_positions` (`trade_lifecycle.py`) -- unconditionally, even while new
submissions are blocked, since tracking an already-open position to its own SL/TP exit is observation,
not new risk-taking (mandate section 25's own "should only be managed according to canonical protective
orders" -- nothing is done TO the position beyond watching it).

## 3. Safety-stop monitor (section 25)

13 named conditions, persisted (`SqliteStateStore`, survives restart -- `test_block_state_survives_
restart`), first-trip-wins (never silently overwritten by a later, possibly-noisier condition), and
never auto-cleared (`clear()` exists but is called nowhere in this package -- a human must investigate
and clear it). `test_pre_tripped_safety_monitor_terminates_immediately_as_blocked` proves zero
`order_send` calls occur once blocked, even mid-run.

## 4. Risk policy, idempotency, no martingale (sections 7-11, 13, 19)

Fully inherited, unmodified, from `demo_execution_adapter.execute()`/`risk_sizer.py` -- see the prior
mandate's own report for the exhaustive proof (13 sizing tests, dedup/restart tests, AST proof no
margin/leverage input). This mandate adds no new sizing or entry logic of any kind (`soak_loop.py`'s own
submission path is a direct, unmodified call to `demo_execution_adapter.execute`, identical to
`live_runtime_loop.py`'s own call site).

## 5. S5 strategy unchanged, no other strategy (sections 5, 10, 27)

`soak_loop.py` constructs exactly one `S5OpeningRangeBreakoutLong`/`catalog_entry_for_s5` pair, exactly
as `live_runtime_loop.py` does -- no S5 source file was touched by this mandate (`git diff` shows zero
changes under `s5_opening_range_breakout.py`, `real_ev_engine.py`, `s5_ev_evidence.py`).
`expected_strategy_id=STRATEGY_ID` is passed to every `demo_execution_adapter.execute()` call, unchanged.

## 6. Exit classification, execution-quality fields, metrics (sections 18-21)

`MT5ExecutionLedgerRecord` extended (additive, backward-compatible -- old rows deserialize with the new
fields defaulting to `None`) with `broker_position_ticket`/`exit_reason`/`exit_price`/`exit_timestamp`/
`gross_pl_money`/`net_pl_money`/`r_result`/`holding_seconds`. `TARGET`/`STOP` classification is
price-tolerance-based against the position's own recorded canonical SL/TP; `OTHER_BROKER_EXCEPTION`
catches anything else (never silently relabeled as normal) -- see the contract doc section 3 for why
`HORIZON` is a defined-but-currently-unproduced classification. `metrics.py` computes WR/gross-and-net-R/
avg-R/PF/equity-curve/drawdown/consecutive-streaks/exit-reason-histogram from `CLOSED` rows only --
7 tests (`test_metrics.py`) covering win/loss counting, PF math, drawdown from a real equity-curve
sequence, and streak tracking.

## 7. Historical comparison, no retuning (sections 22, 26)

`checkpoints.py`'s `_comparison_block` embeds the cited reference values (WR≈54.9%, BASE
expectancy≈+0.210R, STRESS≈+0.193R, PF≈1.61, max historical DD≈-6.44R) verbatim alongside observed DEMO
metrics, with an explicit note that this is reference-only and never a pass/fail gate --
`test_milestone_checkpoint_content_includes_comparison` proves the exact reference `win_rate=0.549`
value is present. No code path anywhere in `soak/` reads back its own metrics to adjust S5/EV/risk
parameters (confirmed by inspection -- `metrics.py`/`checkpoints.py` are write-only consumers of the
ledger, never imported by `s5_opening_range_breakout.py`, `real_ev_engine.py`, or `risk_sizer.py`).

## 8. Live smoke verification -- a genuine defect found and fixed

Two short (~65s), bounded (`max_calendar_days≈0.0007`, terminating via condition B) live-connected runs
against the real, mechanically-verified DEMO terminal (`FusionMarkets-Demo`, `AccountTradeMode.DEMO`,
`AlgoTradingStatus.ENABLED`, equity 10,000.34):

**Run 1** (before fix): 13 exceptions, one per poll iteration --
`ValueError: The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()`.
Root cause: `soak_loop.py`'s poll-fetch used `gateway.copy_rates_from(...) or []` -- the real MT5
`copy_rates_from` returns a **numpy structured array** (unlike `positions_get`/`orders_get`/`history_
deals_get`, which return plain tuples), and `bool(array)` raises for any multi-element array. The
already-shipped `live_runtime_loop.py` uses the correct `is not None` pattern throughout and was never
affected -- this was a new mistake in THIS mandate's own code, not inherited. **A fake-gateway-only test
suite cannot catch this** (Python lists have no such truthiness ambiguity) -- this is exactly why the
live smoke test matters as its own, distinct verification layer, not merely a formality.

**Fix**: replaced with the same `is not None` pattern `live_runtime_loop.py` already used correctly.

**Run 2** (after fix): 0 exceptions, 0 submitted orders (market closed -- Saturday, same as the prior
mandate's own live run), `health.json` and `final_soak_report.json` written correctly with real,
non-fabricated data (real equity, real server identity, real last-bar timestamp matching the actual
stale weekend market). Final status for this bounded smoke run: `S5_MT5_DEMO_UNATTENDED_SOAK_COMPLETE` /
`NO_GENUINE_S5_SIGNAL_OBSERVED` -- honest for the ~65-second window actually run, NOT a claim about the
mandate's real 60-day/20-trade horizon.

## 9. What is NOT yet true, and the actual deployment decision this mandate surfaces

No genuine DEMO trade has occurred (market has been closed -- Saturday -- for both this mandate's live
verification and the prior mandate's). The soak has NOT run for its real 60-day/20-trading-day horizon --
that requires a process that survives well beyond this conversation, across session ends and machine
restarts, which this turn cannot itself provide. `run_soak_live.py` is built and live-verified as
correct, but nothing has yet been registered to keep it running unattended for weeks -- this is a
distinct action (provisioning a persistent, standing service) from writing the code that such a service
would run, and is being surfaced to the user directly rather than assumed.

## Regression tests

`pytest ai_trader/new_brain_live/strategy_platform/` → **264 passed** (228 pre-existing unchanged + 36
new in `soak/`). `pytest ai_trader/mt5_demo_execution/ ai_trader/execution_engine/adapters/` → **103
passed, 2 skipped** (unchanged, zero regression in reused packages).

## Static checks

`mypy --strict ai_trader/new_brain_live/strategy_platform/` → **Success: no issues found in 67 source
files**. No new errors.

## Current status (honest, for THIS turn's deliverable specifically)

- `S5_MT5_DEMO_SOAK_INFRASTRUCTURE_IMPLEMENTED`
- `S5_MT5_DEMO_SOAK_LIVE_SMOKE_VERIFIED` (one real defect found and fixed live, re-verified clean)
- `S5_MT5_DEMO_UNATTENDED_SOAK_NOT_YET_LAUNCHED` -- the real 60-day/20-trade horizon has not begun;
  see section 9 and the accompanying deployment question.

`BROKER_ORDER_SUBMISSION_DISABLED` (shadow path) remains untouched. No REAL-account path exists anywhere
in `mt5_demo_bridge/` or `soak/` (unchanged from the prior mandate, re-confirmed: this mandate added zero
new broker-call sites -- `soak/`'s own AST guard, `test_soak_never_calls_broker_directly.py`, proves it).
