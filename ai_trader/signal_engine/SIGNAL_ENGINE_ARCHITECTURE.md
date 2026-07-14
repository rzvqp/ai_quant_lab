# Signal Engine v1 — Architecture (design)

The Signal Engine evaluates every ACTIVE strategy against the current `MarketContext` and emits standardized,
self-explaining `StrategySignal`s. It is a pure evaluation engine: deterministic, isolated per strategy, no
decisions, no scoring, no risk, no learning, no research access. Design only — no code.

---

## 1. Responsibilities & boundaries

**Responsibilities**
1. Receive the current `MarketContext` (per symbol, per `as_of`) from the Market Scanner (via the orchestrator).
2. Receive the ACTIVE strategy handles from the Strategy Manager (`active_strategies()`).
3. Evaluate each active strategy **independently and deterministically** through the fixed evaluation pipeline.
4. Produce a standardized `StrategySignal` (schema) per (strategy, symbol) with a structured `Explanation`.
5. Validate every emitted signal against `SIGNAL_SCHEMA.json` and the semantic rules.
6. Emit the validated signals to the Scoring Engine. Report health/statistics.

**Hard boundaries (never)**
- Never execute or route trades; never touch the Broker Connector.
- Never rank or score strategies (no `get_score()` call); never compare strategies against each other.
- Never perform risk management or sizing.
- Never modify a strategy, its contract, or the Strategy Manager registry.
- Never learn or adapt.
- Never read Research-Lab artifacts (`code/`, `results/`, `knowledge/experiments/`, `knowledge/ontology/`, KB).
- Never fetch market data or build `MarketContext`.

---

## 2. Internal components

```
                     ┌──────────────────────────── SIGNAL ENGINE ────────────────────────────┐
 MarketContext ─────▶│  Intake            (bind MarketContext + active handles for as_of)     │
 (Market Scanner)    │        │                                                                │
 active handles ────▶│        ▼                                                                │
 (Strategy Manager)  │  Strategy Selection  (scope active strategies to the symbol)           │
                     │        ▼                                                                │
                     │  Evaluation Pipeline (per strategy, isolated):                          │
                     │     Precondition → Context → Signal → Explanation → Signal Validation   │
                     │        ▼                                                                │
                     │  Signal Assembler   (build StrategySignal + Explanation, stamp versions)│
                     │        ▼                                                                │
                     │  Output Collector   (schema-validate, dedupe, batch)                    │
                     │        ▼   Health Monitor ⟲   Statistics ⟲                              │
                     └───────────────┬────────────────────────────────────────────────────────┘
                                     ▼
                               StrategySignal[]  →  Scoring Engine
```

- **Intake** — binds the `MarketContext` for a symbol with the active handles for this `as_of`; rejects a stale/
  mismatched context (fail-safe).
- **Strategy Selection** — filters the active set to strategies scoped to the symbol (the Manager/handle declares
  scope). No ordering effect on results (evaluation is independent), but the order is fixed for determinism (§5).
- **Evaluation Pipeline** — the fixed per-strategy stages (§ evaluation pipeline below). Each strategy runs in
  isolation with its own copy/read-only view of the context.
- **Signal Assembler** — composes the `StrategySignal` (state, direction, strength, confidence, entry/stop/target,
  Explanation) and stamps versions + references.
- **Output Collector** — validates each signal against the schema, dedupes, and batches for the Scoring Engine.
- **Health Monitor / Statistics** — per-cycle counts by state, evaluation timings, failures. Report only.

---

## 3. Evaluation pipeline (the fixed stages)
For each selected strategy, in order. Each stage can short-circuit to a terminal signal STATE (see the state
machine). Every strategy always yields exactly one `StrategySignal` (even NO_SIGNAL/BLOCKED/NEED_CONTEXT).

```
MarketContext
   │
1. Strategy Selection        active + scoped to this symbol ; else the strategy is simply not evaluated
   │
2. Precondition Validation   call health(); call can_trade(context, trader_state)
   │   health INVALID/DISABLED → STATE=INVALID/BLOCKED ; can_trade.allowed=false → STATE=BLOCKED (cooldown/scope/
   │   invalid_conditions/kill-switch), Explanation.invalid_conditions filled → STOP
   │
3. Context Validation        check MarketContext sufficiency vs the strategy's required_context()
   │   sufficiency INSUFFICIENT / missing required field / warmup not met → STATE=NEED_CONTEXT,
   │   Explanation.missing_conditions filled → STOP
   │
4. Signal Evaluation         call detect(context); if setup_forming → call generate_signal(context)
   │   detect.setup_forming=false OR generate_signal.present=false → STATE=NO_SIGNAL → STOP
   │   setup present but required_confirmations not all met → STATE=WAIT_CONFIRMATION → STOP
   │   present + confirmations met:
   │        entry trigger is NOW              → STATE=BUY / SELL (by direction)
   │        setup complete, entry pending     → STATE=LONG_READY / SHORT_READY
   │
5. Signal Explanation        call explain_signal(context); map to the structured Explanation object
   │
6. Signal Validation         validate the assembled StrategySignal (schema + semantics, §7)
   │   fails → STATE=INVALID, quality_flags set → the signal is emitted as INVALID (never silently dropped)
   │
7. Signal Output             emit the validated StrategySignal to the Output Collector → Scoring Engine
```

---

## 4. Data flow
```
orchestrator: ctx = MarketScanner.scan(as_of)[symbol] ; handles = StrategyManager.active_strategies()
Signal Engine.evaluate(ctx, handles):
   for each handle scoped to ctx.symbol (fixed order):
        run pipeline (isolated) → StrategySignal(+Explanation)
   validate + batch → StrategySignal[]
→ Scoring Engine
Health/Statistics updated per cycle.
```
The Signal Engine's output is the SOLE input it gives the Scoring Engine; it holds no state that influences the
next cycle's evaluation (stateless w.r.t. results; any cross-bar state such as cooldown lives in the Strategy
Manager / trader_state passed in).

---

## 5. Strategy evaluation (isolation, determinism, policies)
- **Evaluation order:** a fixed, deterministic order (by `strategy_id`). Order does not affect results — strategies
  are independent — but a fixed order guarantees reproducible batches and logs.
- **Deterministic execution:** for identical `(MarketContext, handle, trader_state)`, the produced signal is
  identical. No randomness, no wall-clock in the logic (only `evaluation_time_ms` is measured, not used in logic).
- **Isolation between strategies:** each strategy evaluates against a read-only view of the same context; one
  strategy's evaluation (including a failure/exception) can NEVER affect another's result or the shared context.
  **Strategies must never influence each other.**
- **Timeout policy:** each strategy evaluation has a bounded time budget; on timeout the strategy yields
  `STATE=INVALID` with `quality_flags:[EVAL_TIMEOUT]` and the batch continues. A slow/hung strategy cannot stall
  the cycle or other strategies.
- **Missing data policy:** handled at Context Validation → `NEED_CONTEXT`; never fabricated, never guessed.
- **Incomplete MarketContext:** if the context itself is degraded (scanner `data_quality != OK`), strategies
  whose required fields are present still evaluate; those needing the missing fields get `NEED_CONTEXT`.
- **Replay/live parity:** the pipeline is identical in LIVE and REPLAY; because it is a pure function of the
  context, replay reproduces live signals exactly (given the same context stream).
- **Multi-symbol evaluation:** the engine evaluates per symbol using that symbol's `MarketContext`; symbols are
  fully isolated (a `MarketContextBatch` is processed symbol-by-symbol). A strategy scoped to multiple symbols is
  evaluated once per symbol, producing one signal per (strategy, symbol).

---

## 6. Explainability (structured, no free-text generation)
Every `StrategySignal` carries a structured `Explanation` (`SIGNAL_EXPLANATION_SCHEMA.json`) composed from the
strategy's `explain_signal()` output plus the evaluation facts. It uses **structured fields and enumerated
condition codes — the engine generates no novel prose**. Any human-readable string is either copied verbatim from
the contract (e.g. `mechanism`) or rendered from a fixed template id + params. The Explanation records:
- **why the signal exists** — the satisfied triggering conditions (codes + labels).
- **why it failed / did not fire** — the unsatisfied conditions, for NO_SIGNAL/WAIT_CONFIRMATION/NEED_CONTEXT/
  BLOCKED.
- **required conditions / missing conditions / invalid conditions** — three explicit structured lists.
- **triggering mechanism** — the mechanism code + the contract's `mechanism` text (copied, not generated).
- **confirmations** — `{required[], met[], pending[]}`.
- **context summary** — a structured digest of the context used (symbol, as_of, regime, session, data-quality),
  never the raw context.
This makes every signal auditable back to `contract_ref{id,version}` and the exact conditions, with no research
internals exposed.

---

## 7. Signal validation & fail-safe
Every assembled `StrategySignal` is validated before output. Checks:
| check | failure → |
|---|---|
| schema conformance (`SIGNAL_SCHEMA.json`) | STATE=INVALID, `quality_flags:[SCHEMA_MISMATCH]` |
| direction consistent with state (BUY⇒LONG, SELL⇒SHORT, etc.) and with the contract `long_short` | INVALID `[INVALID_DIRECTION]` |
| timestamp / `as_of` present and equal to the context `as_of` | INVALID `[MISSING_TIMESTAMP]` |
| unknown/inactive strategy id | INVALID `[UNKNOWN_STRATEGY]` |
| context reference present (context_schema + feature_dict versions) | INVALID `[MISSING_CONTEXT]` |
| confidence in enum / strength in [0,1] | INVALID `[INVALID_CONFIDENCE]` |
| duplicate (same strategy_id + symbol + as_of already emitted this cycle) | dropped-duplicate `[DUPLICATE_SIGNAL]` (one kept) |
| corrupted/absent output from the strategy | INVALID `[CORRUPTED_OUTPUT]` |

**Fail-safe policy:** a failed validation NEVER silently drops or fabricates a tradeable signal — it emits an
`INVALID` signal with `quality_flags` so the Scoring Engine and audit see it and the downstream simply ignores
non-actionable states. The default resting state of any abnormal evaluation is a non-actionable state
(NO_SIGNAL/BLOCKED/NEED_CONTEXT/INVALID). One strategy's failure never aborts the batch.

---

## 8. Invariants
1. **Pure function:** signals are a deterministic function of `(MarketContext, active handles, trader_state)`.
2. **Isolation:** strategies cannot influence each other or the shared context.
3. **One signal per (strategy, symbol) per cycle**, always — including non-actionable states.
4. **No scoring/ranking/risk/execution/learning** anywhere in the engine.
5. **Contract-only view:** no research artifact is ever read.
6. **Everything explainable + versioned:** each signal references `contract_ref{id,version}`, the signal schema
   version, the engine version, and the context reference.
7. **Fail-safe:** abnormal → non-actionable + flagged, never a fabricated actionable signal.

---

## 9. Performance model
- **Batching:** one evaluation cycle per `as_of` produces one batch of signals for all (active strategy × symbol)
  pairs; the Scoring Engine consumes batches, not individual signals.
- **Caching:** `required_context()` per strategy is cached (it is static); precondition results that depend only on
  the context (e.g. session/regime scope) may be memoized within a cycle. Signal results are NOT cached across
  cycles (each `as_of` is fresh).
- **Parallel evaluation:** because strategies are isolated and independent, evaluations MAY run in parallel; the
  Output Collector re-imposes the deterministic order before emitting, so parallelism never changes results
  (determinism preserved).
- **Deterministic ordering:** output is always ordered by `strategy_id` (then symbol), regardless of execution
  parallelism.
- **Replay reproducibility:** identical context stream ⇒ identical signal batches (LIVE == REPLAY).
- **Latency targets:** the per-cycle budget is bounded; each strategy has a per-evaluation timeout (§5) so the
  cycle latency is bounded even if a strategy misbehaves. (Concrete numbers are an implementation-tuning concern,
  set at build; the design only fixes that budgets exist and are enforced.)
- **Memory policy:** the engine holds only the current cycle's context views and signal batch; no unbounded
  history. Context views are read-only and released at cycle end.

---

## 10. Module interaction (who may talk to whom)
| module | may the Signal Engine talk to it? | direction / purpose |
|---|---|---|
| **Market Scanner** | YES | Signal Engine ← MarketContext (via the orchestrator handing it the batch/context). |
| **Strategy Manager** | YES | Signal Engine ← `active_strategies()` handles; may read a handle's contract (read-only). |
| **Scoring Engine** | YES | Signal Engine → `StrategySignal[]` (its sole output consumer). |
| **Learning Engine** | NO (direct) | never; learning is downstream and never mutates evaluation. |
| **Risk Manager** | NO | never. |
| **Execution Planner / Engine** | NO | never. |
| **Portfolio Manager** | NO | never. |
| **Broker Connector** | NO | never — the Signal Engine has zero venue contact. |
| **Research Lab** | NO | never — no research artifact access. |

Rule (CEO-fixed): the Signal Engine communicates ONLY with the **Market Scanner**, the **Strategy Manager**, and
the **Scoring Engine**. It NEVER communicates directly with the Broker, Portfolio, Risk, or the Research Lab.

---

## 11. Versioning
Version lines, all semver, all stamped on every signal:
- **`signal_engine_version`** — this module's implementation/spec version.
- **`signal_schema_version`** — the `StrategySignal` shape (`SIGNAL_SCHEMA.json`). MAJOR = breaking field change;
  MINOR = additive optional field / new enum value (e.g. a new non-actionable state); PATCH = clarification.
- **`explanation_schema_version`** — the `Explanation` shape.
- It also echoes the consumed `interface_version`, `context_schema_version`, and `feature_dictionary_version` (via
  the context reference) so the whole chain (Scanner ↔ Manager ↔ Strategy ↔ Signal Engine ↔ Scoring) is
  version-checkable end to end.

**Compatibility:** the Scoring Engine declares the `signal_schema_version` MAJOR it supports; the Signal Engine
must emit a compatible MAJOR. Unknown optional signal fields are ignored by consumers (forward-compatible).
**Migration policy:** a signal-schema MAJOR bump ships with a documented field mapping; consumers upgrade their
supported MAJOR in lockstep or via an adapter. **Deprecation policy:** a field/state marked deprecated is emitted
for one MAJOR with a `DEPRECATED` note, then removed at the next MAJOR.

---

## 12. Startup & shutdown
**Startup**
```
1. read config (supported interface/signal-schema/context-schema versions, eval timeout, parallelism)
2. handshake Strategy Manager (versions) and confirm the interface/runtime API MAJOR it will call
3. handshake Scoring Engine (supported signal_schema MAJOR)
4. READY — awaits (MarketContext, active handles) per cycle
```
**Shutdown**
```
1. stop accepting new evaluation cycles
2. drain the in-flight cycle (finish or time out per-strategy budgets)
3. emit final statistics()/health()
4. release the current context views + batch; hold no state
```
Startup is fail-safe: if the Scoring-Engine or Manager handshake fails, the engine starts DEGRADED and produces
signals only when a valid context + active handles are supplied; if none are, it emits empty batches (no signals),
never a malformed one.
