# Simulation Framework v1 — API (definition only)

The Simulation Harness's public API. **Definition and semantics only; no implementation, no broker.** A run is a
deterministic, reproducible function of its `SimulationContext` + historical data + module versions.

- **api_version:** `1.0.0` · **produces:** `SimulationReport` (`SIMULATION_SCHEMA.json`).
- **composes:** Market Scanner, Strategy Manager, Signal Engine, Scoring Engine, Risk Manager, Execution Engine
  (UNCHANGED) + Execution Simulator, Portfolio Simulator, Performance Analyzer (sim swap-ins).
- **failure model:** config/data errors fail-fast (`FAILED` before any bar); per-bar issues resolve to
  non-actionable/deterministic outcomes; never a hidden-random result.

---

## 0. Types (summary; full shapes in the schema)
```
SimulationContext  # immutable run spec (SIMULATION_CONTEXT.md / SIMULATION_SCHEMA.json $defs)
SimulationReport   # the full result (SIMULATION_SCHEMA.json)
RunHandle          { run_id, state, progress }
RunStatus          { run_id, state, as_of, bar_index, phase, equity, open_positions, progress_pct }
BatchHandle        { batch_id, run_ids[], completed, total }
Statistics         { bars_processed, orders, fills, trades, avg_bar_ms }
FrameworkHealth    { overall, state, degraded_reasons[], module_versions }
```

---

## 1. Configuration & loading

### `configure(context: SimulationContext) -> RunHandle`
Validate and freeze the `SimulationContext`, compose the pipeline (with the Execution Simulator + Portfolio
Simulator swap-ins), and prepare the run. Idempotent per `run_id`.
- **returns:** `RunHandle { run_id, state=CONFIGURED }`.
- **failures:** invalid context (bad dates/symbols/missing data/incompatible module versions) → `FAILED` with a
  reason; nothing runs.

### `load() -> RunHandle`
Load the composed modules for the run: `Strategy Manager.load_library` → aggregated `required_context` → configure
the Replay Data Source / Market Scanner; bind the Risk config; open the Portfolio Simulator at
`starting_balance`. Transitions to WARMUP.
- **failures:** library/data load failure → `FAILED` (per-strategy failures follow the Strategy Manager's
  quarantine rules; the run proceeds with the loaded set).

---

## 2. Running

### `run() -> SimulationReport`
Run the full replay over `date_range` to completion (WARMUP → RUNNING → COMPLETED), then finalize and return the
`SimulationReport`. The normal entry point.
- **returns:** the `SimulationReport`.
- **semantics:** deterministic — identical context+data+versions ⇒ identical report. Long runs may be driven via
  `step`/`status` for progress.
- **failures:** an unrecoverable run error → `FAILED` with the partial report + reason; determinism preserved up to
  the failure.

### `step(n=1) -> RunStatus`
Advance the replay by `n` base bars (drives the per-bar pipeline). For interactive/inspectable runs and testing.
- **returns:** `RunStatus` at the new `as_of`.

### `run_batch(contexts: SimulationContext[]) -> BatchHandle`
Run many independent simulations (date/seed/strategy-set/parameter sweeps). Runs are independent and MAY execute
in parallel; each is fully reproducible from its own context. Produces one `SimulationReport` per run + an optional
batch summary (cross-run descriptive statistics — no optimization/selection).
- **returns:** `BatchHandle { batch_id, run_ids[], … }`.

### `pause(run_id) -> RunStatus` / `resume(run_id) -> RunStatus` / `stop(run_id) -> SimulationReport`
Pause/resume a run (state only; determinism preserved) or stop early (finalizes the report at the current `as_of`
per `close_at_end_policy`).

---

## 3. Results & introspection

### `report(run_id) -> SimulationReport | NotFound`
Return the finalized (or current partial) `SimulationReport` for a run.

### `status(run_id) -> RunStatus | NotFound`
Return the live run status (state, `as_of`, phase, equity, open positions, progress).

### `statistics(run_id) -> Statistics`
Engine-level counters for the run (bars, orders, fills, trades, timing). For dashboards.

### `health() -> FrameworkHealth`
Framework health, current state, degraded reasons, and the composed module versions. Reports only.

### `versions() -> { simulation_framework_version, simulation_schema_version, fill_model_version, cost_model_version, module_versions }`
All version lines (framework + models + composed pipeline) — a run report records the entire pipeline it was
produced by, for reproducibility.

---

## 4. Contract of use (invariants the caller can rely on)
1. **Deterministic & reproducible:** a run is a pure function of its `SimulationContext` + data + module versions;
   re-running yields a bit-identical `SimulationReport`.
2. **Identical pipeline:** the composed modules are the live modules, unchanged; only the Execution Simulator +
   Portfolio Simulator are sim-specific.
3. **No broker/MT5/network:** everything is offline against historical data.
4. **No research/strategy/learning mutation, no optimization:** the framework composes + measures only.
5. **Fail-fast / fail-safe:** config/data errors fail-fast; per-bar issues resolve deterministically to
   non-actionable outcomes; margin/insolvency raises a logged risk event.

## 5. What the API deliberately does NOT provide
- No broker/venue method, no live-execution path, no MetaTrader integration.
- No method that mutates a strategy, a contract, research, or a composed module.
- No optimization/parameter-search/learning method (batch runs only produce descriptive cross-run statistics).
