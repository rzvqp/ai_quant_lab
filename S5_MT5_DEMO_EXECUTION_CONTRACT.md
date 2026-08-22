# S5_MT5_DEMO_EXECUTION_CONTRACT

**Mandate**: `AI-TRADER-S5-MT5-DEMO-EXECUTION-001`
**Package**: `ai_trader/new_brain_live/strategy_platform/mt5_demo_bridge/`
**Status**: DEMO-account-only. `BROKER_ORDER_SUBMISSION_DISABLED` (the existing shadow gate) is
UNCHANGED and stays disabled forever; this package is a second, separate, explicitly-authorized
execution mode (`ExecutionMode.MT5_DEMO_ONLY`), never a replacement for the first.

## 1. What this package reuses vs. what is new

**Reused, unmodified**: `ai_trader.mt5_demo_execution` (`MT5DemoBrokerAdapter`, `MT5DemoGateway`/
`RealMT5DemoGateway`, `MT5DemoConfig`, `verify_safety_guards`, `build_mt5_request`) and
`ai_trader.execution_engine.adapters` (`MT5ReadOnlyBrokerAdapter`, `MT5Gateway`/`RealMT5Gateway`,
`RealBrokerAdapterBase`, `AccountTradeMode`/`AlgoTradingStatus`/`MT5AdapterStatus`) -- both already built,
already tested (111 pre-existing tests between them, re-run clean by this mandate), and already the sole
choke point (`RealMT5Gateway.__init__`) importing the real `MetaTrader5` package. Neither package was
modified.

**New in this mandate**:

| Module | Purpose |
|---|---|
| `gateway_ext.py` | Additive `MT5BridgeGateway` Protocol -- adds `order_calc_profit` (risk sizing) and `history_deals_get` (reconciliation), the two MT5 primitives nothing in this repo had wrapped yet. |
| `execution_mode.py` | `ExecutionMode.{DISABLED,MT5_DEMO_ONLY}` -- fail-closed on any unrecognized value. |
| `risk_sizer.py` | 5%-of-current-equity, contract-aware sizing via `order_calc_profit` (never a hardcoded $/pip). |
| `order_identity.py` | Deterministic (sha256-based) `client_order_id`/`decision_id`/comment-tag, stable across restarts. |
| `mt5_execution_ledger.py` | Persisted, append-only, one row per state transition (`PENDING_SUBMISSION`→terminal). |
| `reconciliation.py` | Restart-time matching of in-doubt identities against real broker positions/orders/deals. |
| `preflight.py` | Consolidated pre-submission gate (connected, safety guards, dedup, fresh tick). |
| `demo_execution_adapter.py` | Orchestrator: genuine-signal gates → preflight → sizing → `MT5DemoBrokerAdapter.submit_order`. |
| `live_runtime_loop.py` | Incremental, bar-close-driven live loop wiring real MT5 market data into the unmodified `pipeline.run_cycle`. |
| `run_live_demo.py` | Operational entrypoint used for this mandate's own live-connected run. |

## 2. Account-type hard gate -- three independent layers

1. **Connect-time** (`MT5ReadOnlyBrokerAdapter._do_connect`, unmodified): raises `NonDemoAccountError` for
   any `account.trade_mode != AccountTradeMode.DEMO.value` (covers REAL=2, CONTEST=1, and any other
   integer value alike) -- the adapter never even reaches `CONNECTED` state for a non-DEMO account.
2. **Preflight** (`preflight.run_preflight`, new): re-reads `verify_safety_guards(adapter, ...)`
   fresh -- `account_is_demo` re-derived from a fresh `account_info()` call, never cached.
3. **Submit-time** (`MT5DemoBrokerAdapter.submit_order`, unmodified): re-checks `status.account_is_demo
   is not True` immediately before `order_check`/`order_send`, independent of both layers above.

No layer trusts a cached flag; no override parameter exists anywhere in this chain. `test_
real_account_cannot_reach_order_send_even_with_every_other_input_valid` and `test_account_switch_demo_
to_real_mid_session_blocks_next_submission` (`tests/test_demo_execution_adapter.py`) prove this with
strategy/EV/Risk otherwise fully valid.

## 3. Order identity -- a disclosed, deliberate departure from `mt5_demo_execution`'s own scheme

`mt5_demo_execution.request_builder._magic_number_for` derives MT5's `magic` field via Python's builtin
`hash()`, which is **not stable across process restarts** (string-hash randomization). `_comment_for`
truncates `f"{strategy_id}:{decision_id}"` to 27 chars -- S5's real `strategy_id`
(`s5_c_2d587447_opening_range_breakout_long`, 44 chars) alone already exceeds that, so every S5 order's
broker-side comment is an identical, non-distinguishing prefix. Both are genuine, disclosed findings, not
fixed (out of this mandate's scope to modify a different, already-shipped package). This package's own
`order_identity.py` uses `hashlib.sha256` (stable across restarts/machines) for `client_order_id`, and
treats the broker-side `magic`/`comment` as non-authoritative decoration only -- `mt5_execution_ledger.py`
is the sole authority for identity/reconciliation. See `order_identity.py`'s own module docstring for the
full reasoning.

## 4. Risk sizing formula

```
risk_budget = current_equity * 0.05
loss_per_1_lot = abs(order_calc_profit(side, symbol, 1.0, entry, canonical_SL))   # broker-authoritative
raw_volume = risk_budget / loss_per_1_lot
volume = floor_to_step(raw_volume, volume_step)                                   # never rounds up
if volume < volume_min: NO_ORDER (MIN_VOLUME_EXCEEDS_RISK_BUDGET)
if volume > volume_max: volume = floor_to_step(volume_max, volume_step)           # only ever LOWERS risk
```

Canonical S5 SL/TP are never adjusted to hit this budget; margin/leverage are never inputs to this
formula (`test_never_uses_leverage_or_margin_in_sizing_source`, AST-based). `MT5DemoConfig.max_order_
volume` (this run: `1.0` lot) is an ADDITIONAL, independent hard ceiling on top of the 5%-derived volume
-- a deliberate extra circuit breaker for this first-ever live integration, disclosed in the report, not
required by the mandate itself.

## 5. Reconciliation states (`mt5_execution_ledger.py`)

`PENDING_SUBMISSION` → one of `SUBMITTED_ACK` / `SUBMITTED_REJECTED` / `SUBMISSION_FAILED` (normal path),
or, if a restart finds an identity still at `PENDING_SUBMISSION` with no later row (the one genuine
"in-doubt" window, a crash between `order_send` returning and this ledger recording it):
`RECONCILED_EXISTING` (a matching broker position/order/deal found -- never resubmitted),
`RECONCILED_NEVER_ACCEPTED` (zero matching broker candidates -- mechanically proven never accepted, a
fresh attempt for the SAME identity is permitted), or `RECONCILIATION_AMBIGUOUS` (more than one
plausible candidate -- blocked, never guessed, retried on every subsequent reconciliation pass).

## 6. Live runtime loop event model

One bounded (`STARTUP_WARMUP_BARS=60`) warmup fetch at process start, then polls for a newly-closed M15
bar every `poll_interval_seconds` -- each genuinely new bar is fed into `RawAxesBuilder`/
`S5OpeningRangeBreakoutLong` exactly once (tracked by `ts_close`, monotonic), never replaying older bars.
See `AI_TRADER_S5_MT5_DEMO_EXECUTION_REPORT.md` for the full rationale (the operational shadow
validation's own discovered superlinear-scaling finding is what this design specifically avoids).
