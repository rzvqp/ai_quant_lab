# Broker Adapter — Layer A (Foundation) + Layer B (MT5 Read-Only) — Implementation Report

**Scope executed**: exactly the CEO's own two-layer authorization (2026-07-24), building on
`BROKER_ADAPTER_DESIGN.md` (ACCEPTED) and the earlier read-only MT5 connectivity probe
(`MT5_CONNECTIVITY_PROBE_REPORT.md`, commit `15d29a9`). **Stop point honored**: no `order_send`, no
Execution Integration, no Risk Integration, no AlgoTrading activation, no demo trades.

---

## 1. Files created / modified

**New subpackage `ai_trader/execution_engine/adapters/`** — 13 production/test files, zero existing
`execution_engine` file modified:

```
adapters/__init__.py            -- public exports
adapters/connection.py          -- BrokerConnectionLifecycle, ConnectionState, ConnectionResult, BrokerCredentials
adapters/exceptions.py          -- RealBrokerAdapterError hierarchy
adapters/base.py                -- RealBrokerAdapterBase, RetryPolicy, TransientOperationError
adapters/null_adapter.py        -- NullBrokerAdapter (Layer A reference implementation)
adapters/mt5_gateway.py         -- MT5Gateway Protocol + RealMT5Gateway (Layer B)
adapters/mt5_types.py           -- AccountTradeMode, AlgoTradingStatus, MT5AdapterStatus, MT5SymbolCapabilities
adapters/mt5_adapter.py         -- MT5ReadOnlyBrokerAdapter (Layer B)
adapters/tests/__init__.py
adapters/tests/_fixtures.py           -- FakeMT5Gateway (no real terminal needed)
adapters/tests/_fixtures_order.py     -- OrderRequest builder for NullBrokerAdapter tests
adapters/tests/test_protocol_compliance.py
adapters/tests/test_lifecycle.py
adapters/tests/test_demo_detection.py
adapters/tests/test_mt5_reads.py
adapters/tests/test_retry_idempotency.py
adapters/tests/test_credential_safety.py
adapters/tests/test_static_no_trading_calls.py
adapters/tests/test_import_independence.py
adapters/tests/test_mt5_real_terminal_integration.py   -- gated, skipped by default
```

**Modified**: `ai_trader/execution_engine/requirements.txt` (added `MetaTrader5==5.0.5735`, exact pin).

**A latent, pre-existing bug found and fixed during integration**: `ai_trader/recognition_engine/tests/`
(from the earlier, already-CEO-accepted Recognition Engine Phase 1A) had no `__init__.py`, unlike every
other `tests/` directory in this project. Adding `adapters/tests/test_import_independence.py` — same
basename as `recognition_engine/tests/test_import_independence.py` — triggered a pytest module-identity
collision the moment both ran in the same session (`import file mismatch`, a well-known pytest behavior
for same-named test modules across `__init__.py`-less directories). Fixed by adding the missing
`ai_trader/execution_engine/adapters/tests/__init__.py` and `ai_trader/recognition_engine/tests/
__init__.py` (both empty, zero behavior change) — matching the convention every other `tests/` directory
in this repository already follows.

**Confirmed unchanged (`git diff --stat`, empty)**: `ai_trader/execution_engine/broker_adapter.py` (the
pre-existing `BrokerAdapter` Protocol) and `ai_trader/simulation/execution_simulator.py`. Every other file
in the repository outside this new package, the `requirements.txt` line, the two `__init__.py` fixes, and
the design/report documents is also confirmed byte-identical.

## 2. Final architecture

```
BrokerAdapter (Protocol, UNCHANGED)     BrokerConnectionLifecycle (Protocol, NEW)
  capabilities() / submit_order() /       connect() / disconnect() / is_connected() /
  cancel_order() / query_status() /       heartbeat() / last_heartbeat_as_of()
  query_open_orders()
        |                                          |
        +-------------------+  +-------------------+
                            |  |
                  RealBrokerAdapterBase (NEW, abstract)
                  -- connection state, RetryPolicy, client_order_id idempotency,
                     credential injection with redacted repr
                       |                                    |
                       v                                    v
              NullBrokerAdapter                    MT5ReadOnlyBrokerAdapter
              (implements BOTH protocols,           (implements BrokerConnectionLifecycle
               safe in-memory reference)             ONLY -- deliberately no submit_order/
                                                       cancel_order/capabilities/query_*
                                                       at all; read-only status/data
                                                       surface instead: status(),
                                                       symbol_capabilities(), read_tick(),
                                                       list_symbols())
                                                              |
                                                              v
                                                       MT5Gateway (Protocol) / RealMT5Gateway
                                                       -- the ONLY file importing MetaTrader5;
                                                          exactly the CEO's authorized
                                                          read-only operation list, nothing else
```

`ExecutionSimulator` remains outside this diagram entirely — untouched, unreferenced, still the sole
existing real `BrokerAdapter` implementation wired into `ExecutionEngine`.

## 3. Public contracts

- **`BrokerConnectionLifecycle`** (new Protocol): `connect() -> ConnectionResult`, `disconnect() -> None`,
  `is_connected() -> bool`, `heartbeat() -> bool`, `last_heartbeat_as_of() -> int | None`.
- **`ConnectionResult`**: `accepted: bool`, `reason: str | None`, `connected_as_of: int`.
- **`ConnectionState`**: `DISCONNECTED | CONNECTING | CONNECTED | REFUSED`.
- **`BrokerCredentials`**: `login`/`password`/`server`/`path`/`expected_server`, all optional; `__repr__`/
  `__str__` unconditionally redact `password`.
- **`RetryPolicy`**: `max_attempts=3`, `base_delay_seconds=0.1`, `backoff_multiplier=2.0` — bounded by
  construction (`max_attempts >= 1` enforced), never infinite.
- **`RealBrokerAdapterError`** hierarchy: `NotConnectedError`, `RetryExhaustedError`,
  `SafetyRefusalError` → `NonDemoAccountError` / `UnexpectedServerError` / `TerminalNotConnectedError` /
  `AccountValidationError`.
- **`MT5AdapterStatus`** (the CEO's own required exposed shape): `connected`, `terminal_connected`,
  `account_trade_mode` (`AccountTradeMode`), `account_is_demo`, `account_trade_allowed`,
  `terminal_algo_trading_allowed`, `algo_trading_status` (`ENABLED`/`TRADING_DISABLED_AT_TERMINAL`/
  `UNKNOWN`), `server`, `terminal_build`, `last_heartbeat`, `last_error_normalized`.
- **`MT5ReadOnlyBrokerAdapter`** public surface: `connect()`/`disconnect()`/`is_connected()`/`heartbeat()`
  (via `RealBrokerAdapterBase`), `status() -> MT5AdapterStatus`, `symbol_capabilities(symbol) ->
  MT5SymbolCapabilities | None`, `read_tick(symbol) -> Any | None`, `list_symbols() -> tuple[str, ...] |
  None`. **No `submit_order`/`cancel_order`/`capabilities`/`query_status`/`query_open_orders` method
  exists on this class at all.**

## 4. Test results — the CEO's own 18-item mandatory list

All 57 new tests pass (`pytest ai_trader/execution_engine/adapters -q` → 57 passed, 1 skipped):

1. **Protocol compliance** — `test_protocol_compliance.py`: `NullBrokerAdapter` satisfies both
   `BrokerAdapter` and `BrokerConnectionLifecycle`; `MT5ReadOnlyBrokerAdapter` satisfies
   `BrokerConnectionLifecycle` only, and is explicitly asserted to NOT satisfy `BrokerAdapter` (no
   `submit_order`/`cancel_order` attribute exists). **PASS.**
2. **Correct lifecycle** — `test_lifecycle.py`: DISCONNECTED → CONNECTED → DISCONNECTED transitions,
   heartbeat state. **PASS.**
3. **Repeatable connect/disconnect** — 5 and 3 consecutive cycles (Null and MT5-fake adapters). **PASS.**
4. **Refusal while disconnected** — `submit_order`/`cancel_order` return `accepted=False,
   reason="NOT_CONNECTED"`, never raise; `heartbeat()` returns `False`. **PASS.**
5. **DEMO account detection** — `test_demo_detection.py`: `trade_mode=0` correctly reported as
   `AccountTradeMode.DEMO`/`account_is_demo=True`. **PASS.**
6. **Non-DEMO account refusal via mock/fake** — both `REAL` (2) and `CONTEST` (1) `trade_mode` values
   raise `NonDemoAccountError`, connection never established. **PASS.**
7. **AlgoTrading=False detection** — `terminal_info().trade_allowed=False` correctly surfaces as
   `algo_trading_status=TRADING_DISABLED_AT_TERMINAL` (does NOT block the read-only adapter's own
   connect — it is reported, never auto-corrected, per the CEO's own explicit instruction). **PASS.**
8. **account_info read/normalized** — `test_mt5_reads.py`: trade_mode/is_demo/trade_allowed/server all
   correctly mapped into `MT5AdapterStatus`. **PASS.**
9. **terminal_info read/normalized** — connected/build correctly mapped. **PASS.**
10. **XAUUSD capabilities read** — `tick_size=0.01`, `lot_step=0.01`, `min_qty=0.01`, `max_qty=100.0`,
    `digits=2` all correctly extracted via `symbol_capabilities("XAUUSD")`. **PASS.**
11. **Tick read, no side effects** — reading the same tick twice is idempotent; gateway
    `initialize`/`shutdown` call counts and connection state are unchanged by a read. **PASS.**
12. **Bounded retry** — `test_retry_idempotency.py`: succeeds within the configured bound; exhausts and
    raises `RetryExhaustedError` (never hangs) when failures exceed it; a permanent (non-transient)
    failure is never retried at all. **PASS.**
13. **Idempotency for the common foundation** — a duplicated `client_order_id` submission returns the
    IDENTICAL original `BrokerAck`, never a second independent one; `query_open_orders()` never shows a
    duplicate. **PASS.**
14. **Zero credential leakage** — `test_credential_safety.py`: password absent from `repr()`/`str()`/any
    raised exception's own message, across 6 explicit scenarios. **PASS.**
15. **Zero trading calls** — `test_static_no_trading_calls.py`: `order_send`/`order_check`/
    `order_calc_margin`/`order_calc_profit` absent from every production file's own text; structurally
    confirmed absent as real methods on `MT5Gateway`/`RealMT5Gateway`/`MT5ReadOnlyBrokerAdapter`. **PASS.**
16. **Zero changes in frozen modules** — `git diff --stat` empty for `broker_adapter.py`/
    `execution_simulator.py` and every other pre-existing file; `test_import_independence.py` confirms no
    forbidden package import, `MetaTrader5` referenced only in `mt5_gateway.py`, no `execution_simulator`/
    `harness` reference anywhere in the new package. **PASS.**
17. **Full regression green** — see Section5. **PASS.**
18. **mypy strict clean** — see Section5. **PASS.**

**The CEO's own mandatory static control (dynamic indirect access)**: `test_no_dynamic_indirect_access_
patterns_in_production_code` confirms zero occurrences of `getattr(`/`importlib`/`eval(`/`exec(` anywhere
in the new package's production code — an outright ban, not a judgment call, since this design never
legitimately needs any of them (direct attribute access on real MT5 namedtuples throughout).

## 5. Full regression + mypy + static control results

- **Full regression** (`pytest ai_trader/execution_engine ai_trader/simulation ai_trader/context_memory
  ai_trader/decision_intelligence_v2 ai_trader/decision_comparison ai_trader/learning_feedback
  ai_trader/market_intelligence ai_trader/edge_intelligence ai_trader/shadow_evidence
  ai_trader/recognition_engine -q`) → **1,113 passed, 0 failed, 1 skipped** (the gated real-terminal
  integration test), 3:22:02 wall-clock. This is the first time `ai_trader/execution_engine`'s own
  pre-existing 255 tests ran within this session's own "full regression" scope (previously always
  excluded) — all 255 pass unchanged, confirming zero regression there either. 1,113 = 858 (the
  previously-established baseline) + 255 (execution_engine, newly included).
- **mypy strict** (`mypy ai_trader/execution_engine/adapters`, production + tests, 19 files) →
  **Success: no issues found.** One necessary, localized suppression: `# type: ignore[import-untyped]`
  on the single `import MetaTrader5` line (the package ships no type stubs/`py.typed` marker) — this
  project's own established per-line suppression convention, not a new mypy config file.
- **Static control** — all `test_static_no_trading_calls.py` checks pass (Section4 item 15).

**A genuine, unrelated hang scare during this Sprint, investigated and resolved**: the first full-
regression attempt appeared stuck at "over 2 hours" per the CEO's own direct observation. Diagnosed via
(a) two CPU-time samples 15 seconds apart on the live process (6449.5s → 6464.4s, ~99% continuous CPU
utilization — the direct signature of active computation, not a blocked/deadlocked wait), and (b) an
isolated, fresh, verbose, 5-minute-timeout-bounded run of `ai_trader/execution_engine` alone (the only
package containing any MT5-related code) — completed in **1.00 second**, 255 passed + 1 skipped, zero
issues. Conclusively ruled out any MT5/network/terminal wait. The actual cause: this was the first
session run to include `execution_engine`'s own suite alongside the historically-already-slow (~3.3-3.5h)
`ai_trader/simulation` suite in the same invocation — a real, expected duration, not a hang. The
`test_import_independence.py` collision (Section1) was found and fixed during this same investigation,
before the successful re-run reported above.

## 6. Confirmation: the adapter is read-only

- `MT5ReadOnlyBrokerAdapter` has no `submit_order`/`cancel_order` method — not a refusing stub, an
  ABSENT method (`hasattr(adapter, "submit_order") is False`, asserted by test).
- `MT5Gateway`/`RealMT5Gateway` declare and wrap exactly the CEO's own authorized read-only operation
  list; no order-submission/modification method is defined anywhere in either.
- Static scan (`test_static_no_trading_calls.py`) confirms zero occurrence of `order_send`/`order_check`/
  `order_calc_margin`/`order_calc_profit` anywhere in production code, plus zero dynamic-access pattern
  that could reach them indirectly.

## 7. Confirmation: a real account is refused

`test_real_account_is_refused_via_fake_gateway` and `test_contest_account_is_also_refused_not_only_real`
(`test_demo_detection.py`): a fake gateway reporting `trade_mode=REAL` (2) or `trade_mode=CONTEST` (1)
causes `connect()` to raise `NonDemoAccountError` immediately — the adapter never reaches `CONNECTED`
(`connection_state()` becomes `REFUSED`), and no automatic fallback to any other account is ever
attempted (no such logic exists anywhere in `_do_connect`). Additionally verified: an explicitly-
configured `expected_server` mismatch (`UnexpectedServerError`), a disconnected terminal
(`TerminalNotConnectedError`), and unreadable account/terminal data (`AccountValidationError`) are all
independently refused, never silently bypassed.

## 8. Known limitations

- **`query_status`/`query_open_orders`/`capabilities()` are not implemented in Layer B**, a deliberate
  scope-narrowing decision (`mt5_adapter.py`'s own module docstring) — no reconciliation consumer exists
  yet (Execution Integration, the only thing that would need them, has not begun), and nothing in the
  CEO's own mandatory 18-item test list requires them. `MT5Gateway` already wraps `positions_get`/
  `orders_get` at the gateway level, ready for that future, separately-scoped need.
- **`copy_rates_*`/`copy_ticks_*` are wrapped at the gateway level but not yet called by
  `MT5ReadOnlyBrokerAdapter`** — available, unused this phase; `symbol_info_tick` alone covered every
  market-data requirement this phase's own test list needed.
- **The non-interactive credential-injection mode (`login`/`password`/`server` passed to `connect()`)
  remains unverified against a real terminal** — this session's own real probe and this Sprint's own real
  terminal integration test (`test_mt5_real_terminal_integration.py`, gated, not run) both rely on the
  terminal already being open/authenticated, exactly as originally verified
  (`MT5_CONNECTIVITY_PROBE_REPORT.md`). The credential-injection code path is exercised only by
  `FakeMT5Gateway`-based tests, not against a real venue.
- **`BrokerCapabilities`'s own single-global-scalar shape doesn't fit MT5's genuinely per-symbol tick/
  lot/qty limits** — resolved by NOT implementing the Protocol's own `capabilities()` method in Layer B
  at all, using the adapter-local `MT5SymbolCapabilities`/`symbol_capabilities()` instead; disclosed as a
  design choice, not a gap, but worth revisiting if a future phase needs the Protocol's own
  `capabilities()` shape specifically (e.g. for `ExecutionEngine.configure()` compatibility, which
  requires the real `BrokerAdapter` Protocol in full — not attempted this phase, by design).
- **Idempotency/retry are demonstrated on `NullBrokerAdapter`, not yet exercised end-to-end on
  `MT5ReadOnlyBrokerAdapter`** — the read-only adapter never calls `_submit_with_idempotency` (it submits
  nothing), so this machinery's own MT5-specific behavior remains unverified until a future,
  order-submitting phase actually needs it.

## 9. Commits

1. `44d3d4d` — design/documentation (`BROKER_ADAPTER_DESIGN.md`, now committed following CEO acceptance).
2. `33ddf96` — Layer A common foundation.
3. `5477a18` — Layer B MT5 read-only adapter + dependency.
4. (this commit) — all tests + this report.

---

**Per the CEO's own explicit instruction: stopping here.** No `order_send` implemented or called. No
Execution Integration begun. No Risk Integration begun. No AlgoTrading activation attempted. No demo (or
any) trade executed. Awaiting CEO approval.
