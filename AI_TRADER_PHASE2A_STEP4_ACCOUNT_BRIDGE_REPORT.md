# Phase 2A, Step 4 — Live MT5 Account/Instrument Bridge (#5) — Report

**Scope**: exclusively #5 (live MT5 bridge projecting account and instrument data into
`risk_manager_live.types.AccountState`/`InstrumentSpecification`), per the CEO's exact specification. No
gateway extension (unlike Step 3, `account_info`/`symbol_select`/`symbol_info` were already part of the
frozen Phase 1 `MT5Gateway` Protocol). No wiring into `orchestrate()` — the CEO's authorization for this
step named only the bridge itself, not its consumption; wiring an `AccountState`/`InstrumentSpecification`
source into the orchestrator is a separate, not-yet-authorized decision. No live signal source built. No
5%-sizing logic implemented.

## New package: `ai_trader/mt5_account_bridge/`

- **`types.py`** — `AccountDataUnavailableError`, this package's own fail-closed signal (same rationale as
  `mt5_pnl_source.types.PortfolioDataUnavailableError`, applied to account/instrument data instead of P&L).
- **`source.py`** — `MT5AccountBridge`, taking a raw `MT5Gateway` directly (no subclassed extension
  needed): `read_account_state() -> AccountState` and `read_instrument_specification(symbol) ->
  InstrumentSpecification`, both fail-closed and stateless.

No new gateway file was needed or written — `account_info()`, `symbol_select()`, and `symbol_info()` were
already declared on the frozen Phase 1 `MT5Gateway` Protocol before this step began (confirmed by reading
`execution_engine/adapters/mt5_gateway.py` first, not assumed).

## Constraints honored, one at a time

1. **Read-only, never the execution-capable adapter.** `MT5AccountBridge` is constructed with a bare
   `MT5Gateway` — the same read-only Protocol `mt5_pnl_source` already depends on. A dedicated static test
   (`test_import_independence.py`, the same 5-check pattern as `mt5_pnl_source`'s own precedent) confirms:
   no `MetaTrader5` import anywhere in this package; no import of `execution_engine.broker_adapter`,
   `order_manager`, `mt5_demo_execution`, or `execution_orchestrator`; no order-submission vocabulary; the
   literal type names `BrokerAdapter`/`DryRunBrokerAdapter`/`MT5DemoBrokerAdapter` never appear.
2. **Fail-closed on missing/incomplete data — never estimates.** `account_info()` or `symbol_info()`
   returning `None`, or either result missing any field this bridge reads (`trade_mode`, `currency`,
   `balance`, `equity`, `margin`, `margin_free`, `leverage` for the account; `trade_tick_size`,
   `volume_step`, `volume_min`, `volume_max`, `trade_contract_size`, `trade_tick_value`,
   `currency_margin` for the instrument), raises `AccountDataUnavailableError` — confirmed by 4 dedicated
   tests. A zero `trade_tick_size` (which would otherwise divide-by-zero computing `point_value`) is
   treated as the same fail-closed case, not a crash.
3. **Never caches.** No constructor-time snapshot, no memoized field, no instance state beyond the
   gateway and clock references. Every call to either method performs a fresh `account_info()`/
   `symbol_info()` read — proven by two dedicated tests that change the fake gateway's underlying data
   between two calls on the same bridge instance and assert the second call reflects the new value, with
   the fake's own call-count tracking confirming the gateway was genuinely re-read (not served from a
   cache).
4. **Symbol-select-before-read**, replicating the established precedent in
   `execution_engine/adapters/mt5_adapter.py` (`MT5ReadOnlyBrokerAdapter`'s own symbol-capabilities
   lookup): a symbol not already on the terminal's own Market Watch list can otherwise report stale or
   missing data. `read_instrument_specification()` calls `symbol_select(symbol, True)` before
   `symbol_info(symbol)`, confirmed by a dedicated test asserting the call order.

## Test discipline: fails before, passes after, `git stash`-verified

This step built an entirely new, previously-uncommitted package — there was no existing committed
behavior to break, so the git-stash proof was applied to the new code itself (the same method used for
Step 3's own new-package pieces): `tests/test_source.py` (16 tests total, including the import-
independence checks) was written before `source.py` existed. `source.py` was stashed with
`git stash push -u -- ai_trader/mt5_account_bridge/source.py` and the suite re-run, producing a genuine
`ModuleNotFoundError: No module named 'ai_trader.mt5_account_bridge.source'` at collection time (not a
stub or placeholder failure). `git stash pop` restored the implementation; the full 16-test suite then
passed, including 11 tests for `source.py`'s own behavior found only after this proof (one fixture bug
was found and fixed in the process: `FakeMT5AccountGateway(account=None)` originally fell back to a
default account object instead of genuinely returning `None`, silently defeating the
"account_info() returned None" test until corrected with an explicit unset-sentinel).

## Validation

```
pytest ai_trader/risk_manager_live ai_trader/execution_orchestrator ai_trader/mt5_demo_execution \
  ai_trader/order_manager ai_trader/execution_engine ai_trader/risk_manager ai_trader/portfolio_manager_live \
  ai_trader/mt5_pnl_source ai_trader/mt5_account_bridge -q
-> 714 passed, 2 skipped (gated real-terminal tests, unaffected), 0 failed

mypy --strict ai_trader/risk_manager_live ai_trader/execution_orchestrator ai_trader/mt5_demo_execution \
  ai_trader/order_manager ai_trader/portfolio_manager_live ai_trader/mt5_pnl_source ai_trader/mt5_account_bridge
-> Success: no issues found in 89 source files
```

## Exact diff surface

Only the new `ai_trader/mt5_account_bridge/` package (6 source files including tests) plus the
dependency-graph document update recording the two new not-authorized items (equity high-water-mark
restart survival, consecutive-loss window extension). No existing file was modified — nothing was wired
into `orchestrate()` or any other caller this step.

## Disclosed limitations / observations (not silently deferred)

- **Not wired anywhere yet.** `MT5AccountBridge` exists as a standalone, tested capability; no caller in
  this codebase constructs or consumes it. Whether/how it feeds `orchestrate()`'s `account`/`instrument`
  inputs is a separate decision, not made here.
- **`is_demo` derivation** treats any `trade_mode` other than `AccountTradeMode.REAL` (i.e. `DEMO` or
  `CONTEST`) as demo — matching `AccountState`'s own documented "audit only" purpose; this bridge does not
  gate behavior on it.
- **Two new dependency-graph items added per CEO instruction (Step 3 approval), not built this step**:
  equity high-water-mark restart survival, and consecutive-loss detection beyond the 7-day window — both
  recorded under the #5 entry, positioned before Phase 3, "not authorized to build now."

**Stopping here per instruction.** Report, commit, push, and remote-hash verification follow. Awaiting
approval before the next step in the approved order (#6 — live signal source).
