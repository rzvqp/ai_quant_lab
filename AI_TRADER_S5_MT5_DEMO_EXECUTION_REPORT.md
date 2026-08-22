# AI_TRADER_S5_MT5_DEMO_EXECUTION_REPORT

**Mandate**: `AI-TRADER-S5-MT5-DEMO-EXECUTION-001`
**Scope**: connect the existing, unmodified canonical S5 pipeline to real MetaTrader 5 DEMO-account order
submission. First mandate in the project's history authorizing any real broker connectivity.

## 1. Lineage

Reused, unmodified: `633bd5da` (independent validation), `c30b056`/`fb078b5` (canonical onboarding),
`7bea342` (generic REAL EV authority), `9cfcc5f`/`b4cb441` (Statistician/Red-Team evidence
reconciliation), `1e2af14` (REAL EV evidence packaging), `334a57f` (operational shadow validation --
this mandate's own direct predecessor, source of the superlinear-scaling finding this mandate's live loop
design specifically works around). All previously, independently, mechanically re-verified in the prior
mandate; not re-derived here.

**Newly discovered and reused** (not previously known to this mandate chain): a prior, separate "Phase
10" MT5 Demo Execution delivery already exists in this repository
(`ai_trader/mt5_demo_execution/`, `ai_trader/execution_engine/adapters/`) -- a real, tested,
DEMO-account-only MT5 connectivity layer (`MT5DemoBrokerAdapter`, `MT5Gateway`/`RealMT5Gateway`,
`verify_safety_guards`, `build_mt5_request`), 111 pre-existing tests, quarantined only for two specific
LEGACY strategies (`pdh_pdl_demo`/`multi_policy_live`, via `LEGACY_TRADING_AUTHORITY_QUARANTINED` in
`mt5_demo_execution/gating.py`) -- confirmed by direct source inspection that the quarantine is scoped to
those two legacy decision authorities specifically, not to the underlying MT5 primitives, which remain
fully available to a new, canonical caller. This mandate's own `mt5_demo_bridge/` package is exactly that
new, canonical caller -- it reuses this existing infrastructure rather than reimplementing MT5
connectivity from scratch, and never touches the quarantine flag.

## 2. Strategy scope

Mechanically re-derived, not assumed: `expected_strategy_id` is bound to the SAME `STRATEGY_ID` constant
`s5_opening_range_breakout.py` itself exports (`s5_c_2d587447_opening_range_breakout_long`).
`demo_execution_adapter.execute()` independently re-checks `hypothesis.strategy_id == expected_strategy_id`
before doing anything else -- `test_wrong_strategy_rejected` proves a mismatched identity is refused with
zero broker calls.

## 3. Account-type hard gate (sections 3-4, 31-32)

Three independent layers -- see `S5_MT5_DEMO_EXECUTION_CONTRACT.md` section 2 for the exact mechanism.
Live-verified against the actual connected terminal this session (masked, non-secret):

```
trade_mode: AccountTradeMode.DEMO
account_is_demo: true
server: FusionMarkets-Demo
terminal_build: 6090
algo_trading_status: AlgoTradingStatus.ENABLED
```

Tests: `test_demo_account_accepted`, `test_real_account_cannot_connect`, `test_contest_account_cannot_
connect`, `test_unknown_trade_mode_value_cannot_connect`, `test_missing_account_info_cannot_connect`,
`test_account_switch_demo_to_real_mid_session_blocks_next_submission`, `test_real_account_cannot_reach_
order_send_even_with_every_other_input_valid` (the mandate's own explicitly-required proof: strategy=S5,
EV=TRADE_DECISION-equivalent inputs, Risk-equivalent inputs all valid -- account type is the ONLY thing
wrong, and that alone is sufficient to refuse before `order_check`/`order_send` are ever reachable).

## 4. LIVE account safety invariant (section 4)

No override flag, no force option, no development backdoor exists anywhere in `mt5_demo_bridge/` --
confirmed both by direct code review (there is no boolean/env-var parameter on `execute()`,
`run_preflight()`, or `MT5DemoBrokerAdapter.submit_order()` that bypasses the DEMO check) and by the new
`test_broker_calls_confined_to_sanctioned_sites.py` AST guard, which proves `order_send`/`order_check`/
`order_calc_profit` are called from EXACTLY two sanctioned files and nowhere else in this package.

## 5. Execution mode (section 5)

`ExecutionMode.{DISABLED, MT5_DEMO_ONLY}` -- `resolve_execution_mode` raises `UnknownExecutionModeError`
for any other string (including `"ENABLED"`, `"LIVE"`, wrong-case variants) rather than silently
defaulting either way (`test_unknown_value_fails_closed_never_silently_enables`, parametrized over 6 bad
values). The pre-existing `BrokerOrderSubmissionGate`/`BROKER_ORDER_SUBMISSION_DISABLED` (shadow path) is
completely unchanged and untouched by this mandate -- `pipeline.run_cycle` still always resolves
`final_decision="NO_TRADE"` exactly as before; `mt5_demo_bridge` is a wholly separate, additional
execution channel, never a replacement.

## 6. DEMO risk policy -- 5% of CURRENT equity, contract-aware (sections 6-11, 18)

Formula and rounding rules: `S5_MT5_DEMO_EXECUTION_CONTRACT.md` section 4. Proven by
`tests/test_risk_sizer.py` (13 tests): basic 5% computation, equity change moves lot size proportionally,
a wider canonical SL produces a smaller lot than a narrower one (never the reverse), minimum-lot-exceeds-
budget rejects with `MIN_VOLUME_EXCEEDS_RISK_BUDGET`, volume rounds DOWN through a non-trivial step (never
up through the budget), a volume_max cap only ever LOWERS realized risk (`test_max_lot_cap_never_exceeds_
risk_budget_and_reports_actual_risk`), zero/wrong-side SL distance rejected for both LONG and SHORT, a
broker P/L calculation failure (`order_calc_profit` returning `None`) rejects rather than falling back to
an estimate, invalid equity (zero/negative/NaN/inf) rejected, and an AST-based proof the sizing FORMULA
itself never references `margin`/`leverage` as an identifier. Live-verified this session: real
`order_calc_profit`-equivalent contract data read from the connected terminal (`XAUUSD`: `volume_min=0.01`,
`volume_max=100.0`, `volume_step=0.01`, `tick_size=0.01`, `digits=2`; current equity **10,000.34 PLN**) --
the sizing function's own inputs, all genuine, none invented.

## 7. Canonical S5 SL/entry/exit preservation (sections 7, 13-14)

`_canonical_target_price` (`demo_execution_adapter.py`) reads `hypothesis.exit_specification`/
`intended_entry`/`invalidation` directly off the strategy's own, unmodified output -- never recomputes,
widens, narrows, or replaces them. `test_canonical_s5_trade_decision_from_real_pipeline_reaches_demo_
adapter` asserts the SL sent to the broker (`sent["sl"]`) equals `hypothesis.invalidation` exactly, using
the REAL, unmodified S5 strategy and REAL `RealEVDecisionEngine` (not a fixture shortcut). A submission
with no resolvable canonical SL is structurally impossible here (`TradeHypothesis.__post_init__` already
rejects a hypothesis with invalid SL/entry ordering at construction time, before this module ever sees
it) -- there is no code path that opens a position "with the intention of adding SL later" (section 14).

## 8. Contract-aware sizing, transaction costs (sections 8, 12)

`loss_for_one_lot` calls the broker's own `order_calc_profit` (added to the Gateway Protocol specifically
for this mandate, section 8's own explicit preference) -- no hardcoded `$/pip`, contract size, or tick
value for XAUUSD anywhere in the sizing code. The REAL EV validation cost model
(`S5_REAL_EV_EVIDENCE_V1`'s STRESS `round_trip_price=0.24`) and the broker execution risk-sizing path are
kept structurally separate -- `risk_sizer.py` never imports or reads `s5_ev_evidence.py`, and
`s5_opening_range_breakout.py` is untouched by this mandate. No double-counting: the EV cost model
answers "is this trade's edge real"; `order_calc_profit` answers "how much would 1 lot lose to this SL" --
two independent questions, never combined into one number.

## 9. Broker symbol verification, quote freshness (sections 15-16)

`preflight.run_preflight` calls `verify_safety_guards` (pre-existing, unmodified -- checks
`is_market_open_for_symbol` via tick recency against `MT5DemoConfig.market_staleness_threshold_seconds`,
default 120s) and independently reads a fresh tick itself (`NO_TICK` if bid/ask unavailable). Live-
verified this session: the connected terminal's XAUUSD tick was **~11.2 hours stale** at test time
(market closed -- see section 15 below) -- `verify_safety_guards.all_passed` correctly evaluated `False`
(`market_open=False`), which the live loop honestly reported rather than overriding.

## 10. Broker preflight (section 17)

`run_preflight` checks, independently, all reported together in `PreflightResult.reasons`: connected,
safety guards (demo/algo-trading/server/max-volume/market-open, all rolled into `verify_safety_guards`),
duplicate identity (ledger presence check, excluding the one deliberate `RECONCILED_NEVER_ACCEPTED`
retry-allowed state), fresh tick available. `MT5DemoBrokerAdapter.submit_order` additionally runs
`order_check` before `order_send` (pre-existing, unmodified) -- a failed check never reaches send.
Margin sufficiency is implicitly covered by `order_check`'s own broker-side computation (`MT5OrderCheck
Result.margin`/`margin_free` fields, normalized but not independently re-derived here -- the broker is
the authority on its own margin arithmetic, never re-implemented client-side).

## 11. No leverage-based risk sizing / no martingale (sections 18-19)

Section 6/18 above. No averaging/martingale/grid/loss-recovery logic exists anywhere in this package --
every canonical S5 trade independently computes `5% * current_equity` at ITS OWN decision time
(`compute_risk_sized_volume` takes no history/prior-trade-outcome parameter of any kind -- structurally
incapable of scaling with a prior loss).

## 12. Idempotent order identity, magic/comment (sections 20-22)

`duplicate_hypotheses`/`duplicate_decisions`/`duplicate_shadow_orders`-equivalent proof: `test_duplicate_
signal_rejected_same_process` (same process) and `test_restart_duplicate_rejected_via_persisted_ledger`
(fresh adapter/gateway/ledger instances against the SAME on-disk db) both assert exactly one real
`order_send` call across two attempts for the identical canonical event. Maximum concurrent modeled risk
observed in testing: **one** open position at a time (S5's own concurrency semantics -- unchanged, no new
portfolio cap invented, per section 20's own explicit instruction). See `order_identity.py`'s and `S5_MT5_
DEMO_EXECUTION_CONTRACT.md` section 3 for the disclosed magic/comment departure from `mt5_demo_execution`'s
own (restart-unstable, over-length) scheme.

## 13. `order_send` handling, no blind retries (sections 23-24)

Every field section 23 lists is recorded in `MT5ExecutionLedgerRecord`: timestamp (`as_of`), strategy
identity, decision identity, `account_trade_mode`, symbol, side, requested entry, actual quote
(bid/ask), SL, TP, requested volume, modeled risk $/%, `order_request_id`, and (on ack)
`broker_order_ticket`/`filled_volume`/`avg_price`; on rejection, `reason`. No blind retry exists: this
package never calls `submit_order` a second time for an identity already present in the ledger (any
state) except the one explicit `RECONCILED_NEVER_ACCEPTED` case, which is reached ONLY after
`reconciliation.py` has mechanically checked real broker positions/orders/deals and found zero matches.

## 14. Restart reconciliation (sections 24-26)

`reconcile_in_doubt_identities` runs BEFORE any warmup fetch or new submission is permitted
(`test_reconciliation_blocked_prevents_any_warmup_or_processing`: while blocked, `gateway.copy_rates_
from` is never even called). Zero broker candidates → `RECONCILED_NEVER_ACCEPTED` (fresh attempt
permitted); exactly one plausible match → `RECONCILED_EXISTING` (never resubmitted,
`test_reconciled_existing_identity_blocks_fresh_submission`); more than one → `RECONCILIATION_AMBIGUOUS`,
blocked, never guessed (`test_multiple_ambiguous_candidates_blocks_and_never_guesses`). This package
manages only positions it can identify as its own via this reconciliation matching (symbol/side/
volume/approximate price/time-window against its OWN persisted ledger rows) -- it never touches a
position/order it did not itself record an attempt for (section 26).

## 15. Genuine signal only, no forced order (sections 28-30)

**Live-verified this session** (see section 20 below for the full transcript): today (2026-08-22) is a
Saturday; the connected terminal's XAUUSD tick was ~11.2 hours stale at test time (last trade Friday's
close) -- FX/gold markets are closed weekends. `verify_safety_guards`/`is_market_open_for_symbol`
correctly evaluated the market as NOT open; the live loop's own bounded 60-second run genuinely found
zero new closed M15 bars (the market was not producing any) and made zero submission attempts -- this is
the honest, disclosed, `AWAITING_GENUINE_S5_DEMO_SIGNAL` outcome the mandate's own section 29 explicitly
names as valid, achieved without manipulating market data, strategy logic, or the EV/evidence path in
any way. `test_canonical_s5_trade_decision_from_real_pipeline_reaches_demo_adapter` separately proves
(off-line, via the REAL unmodified pipeline/strategy/EV engine, not a live connection) that the full
positive path genuinely reaches this adapter and would submit when a real signal DOES occur -- the
mandate's own required proof that the wiring works, decoupled from whether the live market happened to
cooperate during this bounded session.

## 16. No REAL order under any circumstance, account-switch test (sections 31-32)

Section 3/4 above; `test_account_switch_demo_to_real_mid_session_blocks_next_submission` is the literal
section 32 scenario (start DEMO → underlying account flips to REAL → next submission blocked, zero
`order_send` calls). Both connect-time and submit-time checks re-read the gateway fresh every single
call -- no field anywhere in this package is cached across the DEMO verification boundary.

## 17. Evidence integrity, REAL EV authority (sections 33-34)

`execute()` independently re-checks `decision.evidence_fingerprint == S5_REAL_EV_EVIDENCE_V1.evidence_
fingerprint` before proceeding (`test_wrong_evidence_fingerprint_rejected`) and `decision.decision ==
TRADE_DECISION` (`test_no_trade_decision_never_submits`) -- a bare strategy signal or a NO_TRADE verdict
never reaches sizing/preflight/submission. This module never constructs its own `RealEVDecisionEngine`
call independently of the existing, unmodified pipeline -- it only ever consumes an `EVDecision` the
existing `pipeline.run_cycle` already produced (see `S5_MT5_DEMO_EXECUTION_CONTRACT.md`/module docstrings
for why this makes "genuine REAL EV authority" true by construction rather than by convention).

## 18. Incremental runtime, event cadence (sections 35-36, 42)

**Directly responds to `334a57f`'s own disclosed finding**: a 40-day synthetic replay took ~5m04s (vs.
3.4s for 8 days) -- markedly superlinear growth with total accumulated bar history within one process,
most likely in `RawAxesBuilder`'s own incremental computation. `live_runtime_loop.py` never replays
historical data on every tick/bar: exactly ONE bounded startup warmup (`STARTUP_WARMUP_BARS=60`, fetched
once), then each genuinely new closed M15 bar is fed to `RawAxesBuilder.observe`/`S5.observe_bar` exactly
once, tracked by `ts_close` (monotonic) -- never re-processing an already-seen bar (`test_same_closed_
bar_never_processed_twice_across_poll_iterations`) and never evaluating the broker decision on every
tick (polls for a newly CLOSED bar only, section 36). No full-history-recomputation blocker was found
during this mandate -- had one been found, this module would have stopped and reported it per section
35's own explicit instruction, rather than working around it with faster hardware.

**Performance measurements** (section 42): live-verified this session --

| Measurement | Value |
|---|---|
| Live warmup fetch (60 bars, real terminal) | part of a single `copy_rates_from` call, sub-second |
| Steady-state poll iteration (no new bar) | not separately isolated as a distinct cycle in this run (zero new bars arrived -- market closed); the synthetic 40-day operational replay (`334a57f`) already measured full-cycle latency at real bar cadence: mean 5.24ms, p95 8.34ms |
| Real `RealEVDecisionEngine.decide()` | mean ~1.9ms (measured in `334a57f`'s microbenchmark, unchanged code path) |
| Order-check + order-send latency | not exercised live this session (no genuine signal occurred -- section 15); `demo_execution_adapter.execute()`'s own preflight+sizing overhead measured against the fake gateway in this mandate's own test suite: sub-millisecond |
| Live reconciliation pass (empty ledger, first-ever run) | sub-second (0 in-doubt identities) |
| Memory growth during the bounded 60s live run | not separately instrumented -- run duration (60s, 0 new bars) too short for this to be a meaningful measurement; flagged as a genuine gap for a future, longer-duration live session, not fabricated here |

## 19. Deliverables (section 43)

This report, `S5_MT5_DEMO_EXECUTION_CONTRACT.md`, and the full `mt5_demo_bridge/` package (10 production
modules + `run_live_demo.py` entrypoint + 8 test files, 54 tests).

## 20. Live DEMO connection transcript (this session, masked)

```
$ python -m ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.run_live_demo 60

ACCOUNT_PROOF: {"trade_mode": "AccountTradeMode.DEMO", "account_is_demo": true,
                "server": "FusionMarkets-Demo", "terminal_build": 6090,
                "algo_trading_status": "AlgoTradingStatus.ENABLED"}
SIZING_CONTEXT: {"equity_used_for_sizing": 10000.34, "currency": "PLN",
                 "symbol_contract": {"min_qty": 0.01, "max_qty": 100.0, "lot_step": 0.01,
                                     "tick_size": 0.01, "digits": 2}}
LIVE_LOOP_REPORT: {
  "duration_seconds": 60.02,
  "startup_warmup_bars": 60,
  "cycles_processed": 0,
  "trade_decisions": 0,
  "demo_orders_submitted": 0,
  "reconciliation_blocked": false,
  "exceptions": []
}
{"final_status": "S5_MT5_DEMO_ORDER_PATH_READY_AWAITING_GENUINE_S5_DEMO_SIGNAL"}
```

Account number, password, and any token/credential were never read, logged, or printed -- `BrokerCredentials()`
was constructed with every field `None` (attaches to the already-open, already-authenticated terminal,
`mt5_demo_execution`'s own pre-existing, verified mode -- see `connection.py`'s own docstring).

## 21. Security (section 39)

No credentials in source, tests, reports, logs, or this document. `run_live_demo.py` never accepts or
constructs a login/password/token -- it relies exclusively on the already-open terminal session, exactly
as `MT5_CONNECTIVITY_PROBE_REPORT.md`'s own verified mode. `MetaTrader5` is not yet in `requirements.txt`
(same disclosed gap that report itself named) -- left as-is, a deployment/packaging decision outside this
mandate's scope.

## 22. Tests / regression (section 40)

`pytest ai_trader/new_brain_live/strategy_platform/` → **228 passed** (174 pre-existing, unchanged +
54 new in `mt5_demo_bridge/`). `pytest ai_trader/mt5_demo_execution/ ai_trader/execution_engine/adapters/`
→ **103 passed, 2 skipped** (the 2 skips are the pre-existing, explicitly real-terminal-gated
`MT5_REAL_DEMO_ORDER_TEST=1`-only test, correctly not run by default) -- zero regression in the reused
packages.

One EXISTING test required a scope update, disclosed not silently patched around:
`test_strategies_never_reach_broker.py::test_no_strategy_platform_module_calls_a_broker_function_
directly` previously asserted NO file anywhere under `strategy_platform/` calls `order_send`/
`order_check`/`order_calc_profit` -- true before this mandate, no longer true by design after it. Fixed
by excluding `mt5_demo_bridge/` from that scan (with an explicit docstring explaining why) and adding a
NEW, equally strict, appropriately-scoped AST guard
(`mt5_demo_bridge/tests/test_broker_calls_confined_to_sanctioned_sites.py`, 4 tests) proving broker calls
inside the new package are confined to exactly the two sanctioned wrapper sites.

## 23. Static checks (section 41)

`mypy --strict ai_trader/new_brain_live/strategy_platform/` → **Success: no issues found in 52 source
files** (51 pre-existing/touched + `run_live_demo.py` checked separately, also clean). No new static
errors.

## 24. Limitations

- No genuine S5 DEMO order occurred during this mandate's bounded live session (market closed --
  section 15/18). The full positive path IS proven end-to-end via the real, unmodified pipeline
  (section 15), and the live connection itself IS proven genuine (section 20) -- what remains untested
  live is specifically the `order_send`/fill/reconciliation leg for a REAL signal, which requires the
  market to be open AND a genuine breakout to occur naturally.
- `mt5_demo_execution`'s own `magic`/`comment` scheme is restart-unstable/over-length for S5's own
  identity (section 3/12 in the contract doc) -- disclosed, worked around, not fixed upstream.
- Memory growth over a long-duration live session was not measured (session 20's own 60-second run is too
  short to be meaningful) -- a genuine open item for a future, longer live deployment.
- `order_check`'s margin-sufficiency verdict is trusted as broker-authoritative, never independently
  re-derived client-side (section 10) -- consistent with "prefer the broker's own calculation" (section 8),
  disclosed as a design choice, not an oversight.

## 25. Rollback

Set `ExecutionMode` to `DISABLED` (or simply never wire `live_runtime_loop.run_live_loop` into any
scheduled/running process) -- `mt5_demo_bridge/` is purely additive; nothing in the existing pipeline,
Risk Engine, or shadow path was modified, so removing/disabling this package's own entrypoint fully
reverts to the pre-mandate state instantly.

## Final verdict

Per mandate section 44, "implementation and verified DEMO connection succeed but no natural S5 signal
occurs" branch:

- `S5_MT5_DEMO_EXECUTION_INTEGRATION_PASS`
- `S5_MT5_DEMO_ACCOUNT_HARD_GATE_PASS`
- `S5_DEMO_5PCT_EQUITY_RISK_SIZER_PASS`
- `S5_MT5_DEMO_RESTART_RECONCILIATION_PASS`
- `S5_MT5_DEMO_ORDER_PATH_READY`
- `AWAITING_GENUINE_S5_DEMO_SIGNAL`

`BROKER_ORDER_SUBMISSION_DISABLED` (shadow path) remains disabled and untouched. Live-verified this
session: `order_send` was called zero times; no REAL-account path exists anywhere in this package
(sections 3-4, 16). Per the CEO's own final directive: STOP here -- no further strategy, no live account,
no unattended/unbounded live loop, without a new, separate mandate.
