# Phase 2A, Step 3 — Real `PortfolioStateSource` Implementation (#2) — Report

**Scope**: exclusively #2 (automatic P&L computation from position/deal history), per the CEO's exact
specification. No refactor beyond what the specification itself required (the orchestrator's fail-closed
wiring for a raising data source — required by the spec's own constraint #3, not scope creep). No live
signal source built. No virtual/shadow `PortfolioStateSource` implementation built (explicitly deferred,
constraint #4). No 5%-sizing logic implemented.

## New package: `ai_trader/mt5_pnl_source/`

- **`types.py`** — `DealRecord` (pure, MT5-independent: `profit`, `close_time`); `PortfolioDataUnavailableError`.
- **`computation.py`** — pure functions, no MT5 dependency, no I/O, no wall-clock: `compute_realized_pnl_pct`,
  `compute_unrealized_pnl_pct`, `compute_consecutive_losses`.
- **`gateway.py`** — `MT5HistoryGateway(MT5Gateway, Protocol)` + `RealMT5HistoryGateway(RealMT5Gateway)`,
  mirroring Phase 10's `RealMT5DemoGateway` precedent exactly: a SUBCLASS adding exactly one new method
  (`history_deals_get`), calling the parent's own already-set library reference, no new import of the
  underlying trading library, zero modification to the frozen Phase 1 gateway.
- **`source.py`** — `MT5PortfolioStateSource`, the **one** real implementation of `risk_manager_live.
  types.PortfolioStateSource` (constraint #1). Structurally satisfies the `Protocol` (duck-typed, no
  inheritance, matching this codebase's own convention) — the interface itself is untouched, so a later
  virtual/shadow implementation can satisfy it without any change here (constraint #4).

## Constraints honored, one at a time

1. **One implementation, not two.** `MT5PortfolioStateSource` is the only concrete class satisfying
   `PortfolioStateSource` in this repository. The Step 1 docstring's "never two parallel
   implementations" is unchanged and still holds.
2. **No new path to MT5, never the execution adapter.** `RealMT5HistoryGateway` extends `RealMT5Gateway`
   (Phase 1's own gateway) by subclassing — the same gateway object, one more method, not a second
   connection. A dedicated static test (`test_import_independence.py`, 5 checks) confirms: no
   `MetaTrader5` import outside the gateway file; no import of `execution_engine.broker_adapter`,
   `order_manager`, `mt5_demo_execution`, or `execution_orchestrator`; no order-submission vocabulary
   anywhere in this package; and the literal type names `BrokerAdapter`/`DryRunBrokerAdapter`/
   `MT5DemoBrokerAdapter` never appear.
3. **Fail-closed on missing/incomplete data — never defaults, never estimates.** Every one of
   `account_info()`/`positions_get()`/`history_deals_get()` returning `None` (MT5's own documented
   failure signal), or a position/deal record missing its `profit`/`time` field, or non-positive equity,
   raises `PortfolioDataUnavailableError` — confirmed by 5 dedicated tests, each independently checking
   one failure mode. The circuit breaker's own caller (`execution_orchestrator.orchestrate()`) now
   catches this (or any exception from the injected source) and denies with the new
   `CIRCUIT_DATA_UNAVAILABLE` reason code — absence of data is treated as a reason not to trade, never
   silently read as "no losses."
4. **Virtual/shadow variant not built.** Nothing here — the `Protocol`'s method signature, the
   `TradingCircuitState`/`evaluate_circuit_state` contract, the `orchestrate()` wiring — assumes
   anything about WHERE `PortfolioState` comes from. A future shadow-journal-backed implementation slots
   in identically, unchanged interface.

## The exact bug this closes, and the one it would have opened without the wiring fix

Before this step: `realized_pnl_pct_daily` and the other P&L fields were caller-supplied with a `0.0`
default — Risk Audit #1's own finding, "the most permissive result possible exactly when nothing is
known." `MT5PortfolioStateSource` closes that by computing them from real data.

But building a REAL, raising source immediately exposed a second, adjacent gap: `execution_orchestrator.
orchestrate()` called `evaluate_circuit_state(...)` — which calls the injected `pnl_source` — with no
`try/except` around it. A raising source (exactly what constraint #3 requires) would have propagated an
uncaught exception straight out of `orchestrate()`, violating its own documented "any exception at any
stage aborts the run, never propagates" contract. This is now wrapped, matching every other stage's
identical pattern in the same function, denying with `CIRCUIT_DATA_UNAVAILABLE` instead of crashing.

## Test discipline: fails before, passes after, `git stash`-verified

1. **Pure computation** (`test_computation.py`, 10 tests) — written first, failed with
   `ModuleNotFoundError`, passed after implementing `computation.py`.
2. **Real source** (`test_source.py`, 12 tests) — written first (same failure mode), passed after
   implementing `source.py`/`gateway.py`, including the exact scenario Risk Audit #1 named: a test
   (`test_never_defaults_to_zero_on_incomplete_data_does_not_swallow_the_exception`) explicitly proving
   the source never returns a result when data is missing.
3. **Orchestrator wiring** (`test_circuit_data_unavailable.py`) — written first, confirmed to genuinely
   fail with an **uncaught `RuntimeError` propagating out of `orchestrate()`** (not a stub/import error —
   the real defect the fix closes), verified via `git stash` (stashed `execution_orchestrator/
   {engine,reason_codes}.py`, re-ran, 2 genuine failures with the uncaught exception visible in the
   traceback, `git stash pop` restored the fix, both tests passed).

## Validation

```
pytest ai_trader/risk_manager_live ai_trader/execution_orchestrator ai_trader/mt5_demo_execution \
  ai_trader/order_manager ai_trader/execution_engine ai_trader/risk_manager ai_trader/portfolio_manager_live \
  ai_trader/mt5_pnl_source -q
-> 698 passed, 2 skipped (gated real-terminal tests, unaffected), 0 failed

mypy --strict ai_trader/risk_manager_live ai_trader/execution_orchestrator ai_trader/mt5_demo_execution \
  ai_trader/order_manager ai_trader/portfolio_manager_live ai_trader/mt5_pnl_source
-> Success: no issues found in 82 source files
```

## Exact diff surface

```
 ai_trader/execution_orchestrator/engine.py       | 26 +++++++++++++++++++----
 ai_trader/execution_orchestrator/reason_codes.py |  7 +++++++
 2 files changed, 29 insertions(+), 4 deletions(-)
```
Plus the entirely new `ai_trader/mt5_pnl_source/` package (10 source files including tests) — the
authorized new capability for #2, not a fix to any existing file. No other package touched.

## Disclosed limitations (not silently deferred)

- **Equity high-water mark** is tracked from whichever equity value `MT5PortfolioStateSource` first
  observes (or an optionally-seeded starting value), ratcheting upward only. It does not reconstruct the
  account's true all-time-high from history MT5 does not expose as a single queryable value. If a real
  historical peak exceeds what's been observed since this object's construction and no seed was
  supplied, drawdown will read smaller than reality until enough live observation accumulates.
- **`open_positions`/`recent_closed_positions`/`gross_notional`** are left at `PortfolioState`'s own
  empty defaults — they feed `limits.py`'s position-count/correlation/leverage checks, a separate
  concern from the loss/drawdown P&L this step was authorized to fix. Reconstructing them would require
  mapping MT5 position/order tags back onto `strategy_id`/`risk_pct`/`correlation_group`, out of this
  step's scope.
- **Consecutive-loss detection** only looks back over the same 7-day window fetched for weekly P&L (one
  MT5 call, reused, rather than a second wider query) — sufficient in practice for the default
  3-consecutive-loss cooldown threshold, but a streak older than 7 days would not be seen in full.
- **Day/week windows are UTC calendar day / trailing 7×24h**, not the broker's own trading-day or
  ISO-week convention — the same disclosed-simple-default pattern already used for `reset_if_new_day`.

**Stopping here per instruction.** Report, commit, push, and remote-hash verification follow. Awaiting
approval before the next step (#5 — live MT5 account/instrument/equity bridge).
