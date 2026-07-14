# Strategy Manager v1 — API (definition only)

The Strategy Manager's public API — the only surface other AI-Trader modules use. **Definition and semantics
only; no implementation.** The Manager returns registry/interface data and lifecycle results; it never returns a
trading signal, score, or order, and never exposes research internals.

- **api_version:** `1.0.0` · **registry:** `STRATEGY_REGISTRY_SCHEMA.json` · **depends on:** Strategy Interface v1,
  Strategy Library (read-only), Market Scanner v1.
- **Purity/determinism:** query methods are deterministic given the current registry; load/validation are
  deterministic given the Library + supported versions.
- **Failure model:** expected failures (missing file, invalid contract, incompatibility, unknown id) are returned
  as typed results, not thrown across the boundary. A single bad contract never aborts a bulk operation.

---

## 0. Result types (summary; registry shapes in the schema)
```
LoadReport      { loaded, failed[], duplicates[], counts_by_lifecycle, counts_by_health, registry_version }
ValidationReport{ id?, ok, schema_valid, interface_ok, runtime_ok, context_ok, deprecated[], reasons[] }
StrategyView    { id, name, slug, lifecycle, health, identity_version, interface_version, maturity, active }
                # a READ-ONLY projection of the contract + registry state — NOT a runtime strategy handle
StrategyHandle  { id, contract (read-only), api }   # interface handle passed to the Signal Engine ONLY
AggregatedContext  # UNION(required_context()) → the Market Scanner spec (schema $defs/AggregatedContext)
Statistics      { totals, by_lifecycle, by_health, active_count, aggregated_context_summary }
ManagerHealth   { overall, counts_by_health, active_count, aggregated_context_ready, notes[] }
```

---

## 1. Loading & validation

### `load_library(path?: str) -> LoadReport`
Discover, parse, schema-validate, and compatibility-check every `strategy.json` under the Library path, populate
the registry, assign initial lifecycles, apply the admission policy, and (re)compute the aggregated context.
- **params:** `path` optional (defaults to configured Library path).
- **returns:** `LoadReport` (what loaded, what failed and why, duplicates, counts).
- **failures:** none thrown; per-strategy failures appear in `failed[]`/`duplicates[]`. If the path is missing →
  `LoadReport` with `loaded=0` and a top-level error note; the Manager stays READY with an empty active set.

### `reload(id?: str) -> LoadReport`
Re-load the whole Library (`id` omitted) or a single strategy. Detects contract changes via `content_hash`,
re-validates, re-checks compatibility, applies lifecycle transitions (incl. maturity changes from a new contract
version, gate-checked), and re-aggregates context if the active set changed.
- **returns:** `LoadReport` scoped to what changed.
- **failures:** a now-invalid contract transitions the strategy to `INVALID`/`INCOMPATIBLE` (removed from active),
  never a crash; the rest of the registry is untouched.

### `validate(id?: str) -> ValidationReport | ValidationReport[]`
Validate one strategy (or all) WITHOUT changing lifecycle/activation — a dry check (schema + interface + runtime +
MarketContext-compatibility + deprecation). Used before a reload or by tooling.
- **returns:** a report (or list) with the exact pass/fail per check and reasons.
- **failures:** unknown `id` → `ValidationReport{ ok=false, reasons:["unknown id"] }`.

---

## 2. Querying the registry

### `list_strategies(filter?: {lifecycle?, health?, symbol?, maturity?}) -> StrategyView[]`
Return read-only views of registered strategies, optionally filtered. Includes quarantined ones (so operators can
see INVALID/INCOMPATIBLE). Never returns runtime handles.
- **returns:** `StrategyView[]` (may be empty).
- **failures:** an unknown filter value → empty list (not an error).

### `active_strategies() -> StrategyHandle[]`
Return the **interface handles** for strategies in the live active set (`EXPLORATORY`+ and admitted). **This is the
ONLY method that yields runtime handles, and it is intended for the Signal Engine only.** Each handle exposes the
read-only contract + the Strategy API; it carries no research internals.
- **returns:** `StrategyHandle[]` (possibly empty — the pipeline then produces no signals; that is valid).
- **failures:** none; a strategy that just went unhealthy is simply absent from the list.

### `find_strategy(id: str) -> StrategyView | NotFound`
Look up a single strategy's view by id.
- **returns:** `StrategyView`, or `NotFound{ id }`.
- **failures:** unknown id → `NotFound` (typed, not thrown).

### `get_contract(id: str) -> Contract | NotFound`
Return the read-only, schema-validated contract for a strategy (for the Risk Manager reading `capital_limit`, the
Explainability Engine reading `mechanism`, etc.). Read-only; no mutation path exists.

---

## 3. Context aggregation (feeds the Market Scanner)

### `required_context() -> AggregatedContext`
Compute/return `UNION(required_context())` over the ACTIVE strategies: unioned timeframes/fields, max lookback,
unioned symbols, required-vs-optional split, target `feature_dictionary_major`, and the contributor ids. **This is
the Market Scanner specification** — the Manager (not the scanner) is its sole producer.
- **returns:** `AggregatedContext` (schema `$defs/AggregatedContext`).
- **semantics:** recomputed on every active-set change; stable/deterministic given the active set. If the active
  set is empty, returns an empty-but-valid spec (the scanner then tracks nothing).
- **failures:** a feature-dictionary MAJOR conflict among active strategies is resolved per the architecture (§6):
  the lower-priority strategy is deactivated and listed in the report; the returned spec targets one MAJOR.

---

## 4. Lifecycle control (operator / Learning-Engine control channel)

### `activate(id) -> LifecycleResult` / `deactivate(id) -> LifecycleResult`
Admit a strategy to / withdraw it from the live active set (transitions T4/T5/T10/T11 per the state machine),
subject to the admission policy and compatibility. Re-aggregates context on success.
- **returns:** `LifecycleResult{ id, from, to, ok, reason }`.
- **failures:** activating an `INVALID`/`INCOMPATIBLE`/`NOT_IMPLEMENTED`/`RETIRED` strategy → `ok=false` with a
  reason; state unchanged.

### `disable(id, reason) -> LifecycleResult` / `enable(id) -> LifecycleResult`
Operational kill-switch overlay (→ `DISABLED`) and restore. `enable` re-validates before restoring.

### `retire(id, reason) -> LifecycleResult`
Terminal withdrawal within the interface MAJOR (→ `RETIRED`). Idempotent; not reversible except by a new Library
release + reload.

> The Learning Engine may call `enable`/`disable`/`activate`/`deactivate`/`reload` (allocation control) but has
> **no** method to mutate a contract — none exists. Maturity advances only via a new contract version from the
> Library.

---

## 5. Introspection & health

### `statistics() -> Statistics`
Aggregate counts by lifecycle and health, active count, and an aggregated-context summary. For dashboards and the
Performance Monitor.

### `health() -> ManagerHealth`
Overall Manager health (`OK`/`DEGRADED`/`FAILED`), counts per health state, whether the aggregated context is
ready, and notes. Reports only; takes no action.

### `versions() -> { manager_version, registry_version, supported: { interface_major, runtime_api_major, feature_dictionary_major } }`
The Manager's version lines and support window, for the end-to-end compatibility handshake (Scanner ↔ Manager ↔
contracts).

---

## 6. What the API deliberately does NOT provide
- No `generate_signal`, `score`, `size`, `submit_order`, or portfolio state — those belong downstream.
- No method that reads Research-Lab artifacts or a strategy's internals beyond the Contract.
- No method to write/mutate a contract or the Library.
- No direct link to the Broker Connector, Execution Engine, or Risk Manager (see the interaction matrix in the
  architecture).
