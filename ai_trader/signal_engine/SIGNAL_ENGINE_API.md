# Signal Engine v1 — API (definition only)

The Signal Engine's public API. **Definition and semantics only; no implementation.** Every method is a
deterministic function of the supplied `MarketContext` + active strategy handles; none rank, size, execute, learn,
or read research artifacts.

- **api_version:** `1.0.0` · **emits:** `StrategySignal` (`SIGNAL_SCHEMA.json`) with `Explanation`
  (`SIGNAL_EXPLANATION_SCHEMA.json`).
- **inputs:** `MarketContext` (Market Scanner), `StrategyHandle[]` (Strategy Manager), `trader_state` (owned by the
  Strategy Manager / orchestrator, passed in for cooldown/positions).
- **failure model:** expected failures are returned as non-actionable signals or typed results, never thrown
  across the boundary. One strategy's failure never aborts a batch.

---

## 0. Types (summary; full shapes in the schemas)
```
StrategySignal   # SIGNAL_SCHEMA.json (state, direction, strength, confidence, explanation, quality_flags, …)
Explanation      # SIGNAL_EXPLANATION_SCHEMA.json (structured; no free text)
SignalBatch      { as_of, symbol?, signals: StrategySignal[], counts_by_state, generated_at }
ValidationResult { valid, reasons[], quality_flags[] }
Statistics       { cycles, signals_total, by_state, avg_eval_ms, timeouts, invalids }
EngineHealth     { overall, last_cycle_ok, degraded_reasons[], supported_versions }
```

---

## 1. Evaluation

### `evaluate(context: MarketContext, handles: StrategyHandle[], trader_state) -> SignalBatch`
Evaluate every handle scoped to `context.symbol` against the single-symbol `context`, in deterministic order,
each in isolation, and return one `StrategySignal` per handle (including non-actionable states). This is the
normal per-symbol entry point.
- **returns:** `SignalBatch` for that symbol/`as_of` (schema-validated signals).
- **failures:** a mismatched/stale context (context.as_of not aligned) → the batch is produced with all signals
  `INVALID`/`NEED_CONTEXT` and a batch-level flag; never a crash. An empty `handles` list → an empty batch (valid).

### `evaluate_all(batch: MarketContextBatch, handles: StrategyHandle[], trader_state) -> SignalBatch[]`
Evaluate across all symbols in a `MarketContextBatch` (one `evaluate()` per symbol, symbols isolated). Returns one
`SignalBatch` per symbol.
- **returns:** `SignalBatch[]` (deterministic order by symbol).
- **failures:** per-symbol failures are contained within that symbol's batch.

### `evaluate_strategy(context: MarketContext, handle: StrategyHandle, trader_state) -> StrategySignal`
Evaluate a single strategy against a single-symbol context (the atomic unit). Used for targeted re-evaluation,
testing, or explanation.
- **returns:** exactly one `StrategySignal`.
- **failures:** health `INVALID`/timeout/validation failure → a non-actionable `StrategySignal` with
  `quality_flags`; never thrown.

---

## 2. Retrieval

### `get_signal(strategy_id, symbol, as_of) -> StrategySignal | NotFound`
Return the signal produced for a (strategy, symbol, as_of) in the most recent matching cycle (if retained).
- **returns:** the `StrategySignal`, or `NotFound`.
- **failures:** unknown combination → `NotFound` (typed).

### `get_signals(filter?: {as_of?, symbol?, state?, strategy_id?}) -> StrategySignal[]`
Return the signals of the current/last cycle matching the filter (e.g. all `BUY`/`SELL` for a symbol).
- **returns:** `StrategySignal[]` (possibly empty).
- **failures:** unknown filter value → empty list.

---

## 3. Validation & explanation

### `validate_signal(signal: StrategySignal) -> ValidationResult`
Validate a signal against `SIGNAL_SCHEMA.json` + the semantic rules (direction↔state consistency, timestamp/as_of
present, confidence enum, strength range, non-duplicate). Pure; used internally before emit and available to
consumers/tools.
- **returns:** `ValidationResult { valid, reasons[], quality_flags[] }`.
- **failures:** a structurally corrupt input → `valid=false` with `CORRUPTED_OUTPUT`.

### `explain(strategy_id, symbol, as_of) -> Explanation | NotFound`
Return the structured `Explanation` for a produced signal (the same object embedded in the signal). No free-text
generation — structured fields only.
- **returns:** `Explanation`, or `NotFound`.

---

## 4. Introspection

### `statistics() -> Statistics`
Per-cycle and cumulative counts by state, average evaluation time, timeout/invalid counts. For the Performance
Monitor and dashboards.

### `health() -> EngineHealth`
Overall engine health (`OK`/`DEGRADED`/`FAILED`), last-cycle status, degraded reasons, and the supported version
window (signal/interface/context schemas). Reports only; takes no action.

### `versions() -> { signal_engine_version, signal_schema_version, explanation_schema_version, supported: { interface_major, context_schema_major } }`
Version lines + support window, for the end-to-end compatibility handshake (Scanner ↔ Manager ↔ Signal Engine ↔
Scoring Engine).

---

## 5. Contract of use (invariants the caller can rely on)
1. **One signal per (strategy, symbol) per cycle**, always (including non-actionable states).
2. **Deterministic:** identical `(context, handle, trader_state)` ⇒ identical signal (replay parity).
3. **Isolated:** a strategy's evaluation cannot affect another's result or the shared context.
4. **Validated:** every emitted signal conforms to `SIGNAL_SCHEMA.json`; failures are emitted as `INVALID`, never
   as fabricated actionable signals.
5. **Bounded:** each strategy evaluation is time-bounded; a slow strategy cannot stall the cycle.
6. **No scoring/risk/execution/learning/research** anywhere in the API.

## 6. What the API deliberately does NOT provide
- No `score`/`rank`, no `size`, no `submit_order`, no portfolio/risk methods.
- No `get_score()` call to strategies (scoring is the Scoring Engine's job).
- No method that reads Research-Lab artifacts or mutates a strategy/contract/context.
- No direct link to the Broker Connector, Execution Engine, Portfolio Manager, or Risk Manager.
