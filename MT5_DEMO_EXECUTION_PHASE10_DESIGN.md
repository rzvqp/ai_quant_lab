# Phase 10 — MT5 Demo Execution — Design

**CEO scope**: extend Broker Adapter with minimal DEMO operations; `order_check` before `order_send`;
re-verify DEMO account; verify `trade_allowed`; if AlgoTrading disabled, fail-closed and report — never
auto-activate; implement DEMO order send/confirm/reconcile; test with minimal configurable volume; never
send an order until the same intent's dry-run has passed; keep emergency stop + daily risk lock active;
structurally refuse REAL/CONTEST accounts; final automated safety-guard verification before the very
first real DEMO trade — if any control fails, do not send.

## 0. Architecture-change finding, reported and authorized before this doc was written

Investigation found `order_manager.types.OrderExecutionResult.dry_run` was a hard, `__post_init__`
-enforced `True`-only invariant, and `process_approved_intent`'s `adapter` parameter was typed to the
concrete `DryRunBrokerAdapter` class — meaning no adapter, real or not, could ever produce a non-dry-run
result through Order Manager as built in Phase 3. This was reported to the CEO before any Phase 10 code
was written (per the standing "stop and report" rule) and an explicit, additive fix was authorized
(2026-07-25): `dry_run` now reflects `isinstance(adapter, DryRunBrokerAdapter)` rather than a hardcoded
constant, and `process_approved_intent` accepts the general `BrokerAdapter` protocol. `DryRunBrokerAdapter`
still always yields `dry_run=True`, byte-identical to Phase 3 -- all 43 pre-existing Order Manager tests
pass unchanged (confirmed: `pytest ai_trader/order_manager -q` → 44 passed after adding one new test for
the `dry_run=False` case).

## 1. Investigation finding: MT5 gateway/adapter can be extended additively, zero modification

`MT5Gateway`/`RealMT5Gateway` (`execution_engine/adapters/mt5_gateway.py`, Phase 1, frozen) declare zero
order-related methods. `MT5ReadOnlyBrokerAdapter` (`mt5_adapter.py`, frozen) already has the exact DEMO/
server verification logic (`_do_connect`) and the exact `MT5AdapterStatus`/`AccountTradeMode`/
`AlgoTradingStatus` types Phase 10 needs to REUSE, not reimplement. `RealBrokerAdapterBase._submit_with_
idempotency`/`_call_with_retry` (Phase 1) are venue-agnostic and already written for exactly this reuse.

## 2. New package: `ai_trader/mt5_demo_execution/`, additive only

- `gateway.py`: `RealMT5DemoGateway(RealMT5Gateway)` -- a SUBCLASS adding exactly two methods,
  `order_send(request: dict) -> Any` / `order_check(request: dict) -> Any`, calling the ALREADY-SET
  `self._mt5` attribute the parent's own `__init__` establishes (`mt5_gateway.py`'s own `self._mt5 = mt5`
  line) -- this file contains no `import MetaTrader5` of its own at all; it is not a second entry point
  into the library, only a second METHOD SET on the same, already-approved gateway object. Zero
  modification to `mt5_gateway.py`.
- `types.py`: `MT5OrderSendResult`/`MT5OrderCheckResult` (normalized, mirroring the `NormalizedMT5Error`
  pattern), `MT5DemoConfig` (`max_order_volume`, `deviation_points`, `magic_number_range`).
- `adapter.py`: `MT5DemoBrokerAdapter(MT5ReadOnlyBrokerAdapter)` -- a SUBCLASS adding `submit_order`/
  `capabilities`/`query_status`/`query_open_orders` on top of the already-approved, unmodified DEMO/
  server verification in the parent's `_do_connect`. `cancel_order` is deliberately NOT implemented this
  phase (disclosed -- CEO's Phase 10 list names send/confirm/reconcile, not cancel).
- `gating.py`: `send_after_dry_run_gate(...)` -- the ONE new orchestration wrapper enforcing "never send
  until the same intent's dry-run has passed": runs `execution_orchestrator.orchestrate(...,
  mode=DRY_RUN)` first, against its OWN, separate ledger/journal; only if that run is `approved` AND its
  `order_result.state is ACKNOWLEDGED` does it then run `orchestrate(..., mode=DEMO)` against a SEPARATE
  ledger/journal (never the same one -- reusing the dry-run's own ledger would hit the ledger's own
  idempotency guard on the SAME deterministic `client_order_id` and silently short-circuit the real
  attempt to the cached dry-run record, never actually calling the demo adapter -- a genuine correctness
  requirement, not a style choice).

## 3. Safety gates, in order, every one fail-closed

1. **AlgoTrading check** (re-read on EVERY `submit_order` call, not just at connect time):
   `self.status().algo_trading_status is AlgoTradingStatus.ENABLED`, else refuse with
   `TRADING_DISABLED_AT_TERMINAL` -- never auto-activates anything.
2. **DEMO re-verification** (re-read on EVERY `submit_order` call): `self.status().account_is_demo is
   True`, else refuse with `NON_DEMO_ACCOUNT_REFUSED` -- independent of, and in addition to, the parent
   class's own connect-time check (defense in depth against a reconnect to a different account mid-run).
3. **Minimal configurable volume**: `MT5DemoConfig.max_order_volume` (default `0.01` lots -- the
   broker's own confirmed minimum, `MT5_CONNECTIVITY_PROBE_REPORT.md`) is a hard ceiling; `submit_order`
   REFUSES (never silently clamps) any order above it.
4. **`order_check` before `order_send`**: `submit_order` calls `self._gateway.order_check(request)`
   first; only a normalized-OK result proceeds to `order_send`. A failing `order_check` is reported and
   never followed by a send attempt.
5. **Idempotency + retry**: reused, unmodified, via `self._submit_with_idempotency`.
6. **Dry-run-must-pass-first**: enforced by `gating.send_after_dry_run_gate`, not by the adapter itself
   (the adapter has no visibility into "was a dry run already attempted for this intent" -- that is
   orchestration-level state, correctly owned by the orchestration layer).
7. **Emergency stop / daily risk lock**: already enforced, unmodified, by `execution_orchestrator.
   orchestrate` (`emergency_stop` parameter, checked first) and `portfolio_manager_live` (`PortfolioDailyState.
   trades_opened_today`/`daily_heat_used_pct` limits) -- Phase 10 does not bypass either; `send_after_dry_
   run_gate` calls `orchestrate()` unmodified for both the dry-run and demo legs, so every existing gate
   applies to both.
8. **REAL/CONTEST refusal**: structural -- `MT5ReadOnlyBrokerAdapter._do_connect` (Phase 1, unmodified)
   already raises `NonDemoAccountError` for any non-DEMO `trade_mode`; `MT5DemoBrokerAdapter` never
   overrides `_do_connect`, only adds methods on top.

## 4. Final automated safety-guard verification

`verify_safety_guards(adapter, config) -> SafetyGuardReport` -- a single function checking, ALL of:
connected, `account_is_demo is True`, `algo_trading_status is ENABLED`, `config.max_order_volume > 0`,
server matches `expected_server` if configured. Returns a report with one boolean per guard plus an
overall `all_passed: bool`. `send_after_dry_run_gate` calls this immediately before ever attempting the
DEMO leg -- if `all_passed` is `False`, the demo attempt is refused before `order_check` is even called.

## 5. What this phase does NOT do (disclosed, matching every prior phase's own discipline)

- Does not enable AlgoTrading, change any terminal setting, or alter account credentials -- if disabled,
  it fails closed and reports `TRADING_DISABLED_AT_TERMINAL`, exactly as required.
- Does not implement `cancel_order` -- disclosed, out of this phase's named scope.
- **Does not, itself, execute a live send against the real, currently-open MT5 terminal.** Per this
  session's own operating rules around hard-to-reverse actions against a live external system, the new
  gated real-terminal test (`test_mt5_demo_real_terminal_integration.py`, mirroring Phase 1's own
  `MT5_REAL_TERMINAL_TEST=1`-gated precedent exactly) is written, skipped by default, and left for the
  CEO's own explicit, in-the-moment action to run -- not run automatically as part of this phase's
  delivery. The full unit test suite (below) proves every safety gate and the full send/order_check/
  idempotency logic correct using a fully-faked gateway, with zero real-terminal interaction.
- **Current real-terminal state** (per `MT5_CONNECTIVITY_PROBE_REPORT.md`): AlgoTrading is confirmed
  DISABLED at the terminal level today. Even if the gated real-terminal test were run, it would correctly
  fail-closed at guard #1 before ever reaching `order_check`/`order_send` -- disclosed, not assumed.
