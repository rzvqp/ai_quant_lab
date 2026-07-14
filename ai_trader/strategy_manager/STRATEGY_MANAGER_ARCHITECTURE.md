# Strategy Manager v1 — Architecture (design)

The Strategy Manager owns the Strategy Library inside the AI Trader: load → validate → register → maintain
lifecycle → aggregate context requirements → expose active strategies. It makes no trading decision. Design only —
no code.

---

## 1. Responsibilities & boundaries

**Responsibilities**
1. Discover and load every `strategy.json` from the Strategy Library.
2. Validate each contract: JSON well-formedness → schema (`strategy_contract.v1.schema.json`) → interface version
   → MarketContext/runtime compatibility.
3. Maintain the **registry**: indices, cache, versions, health, lifecycle state.
4. Maintain **lifecycle status** per strategy and enforce legal transitions.
5. **Aggregate context requirements**: `UNION(required_context())` over ACTIVE strategies → the Market Scanner
   specification.
6. **Expose** ACTIVE, compatible strategies (as interface handles) to the Signal Engine.
7. Report **health** and statistics.

**Hard boundaries (what it must never do)**
- Never generate signals, score, size, or execute orders.
- Never read Research-Lab artifacts (`code/`, `results/`, `knowledge/experiments/`, `knowledge/ontology/`, the
  knowledge base). Its ONLY view of a strategy is the Contract + the interface API.
- Never mutate a strategy's internals or its contract file (read-only over the Library).
- Never fetch market data or build MarketContext (that is the Market Scanner).

---

## 2. Components (internal modules)

```
                       ┌──────────────────────── STRATEGY MANAGER ────────────────────────┐
 Strategy Library ────▶│  Strategy Loader        (discover · parse · validate)            │
 (knowledge/           │        │ ValidatedContract | LoadError                            │
  strategies/*.json)   │        ▼                                                          │
                       │  Compatibility Checker  (interface · schema · MarketContext · ver)│
                       │        │ Compatible | Incompatible(reasons)                        │
                       │        ▼                                                          │
                       │  Strategy Registry      (indices · cache · versions · health)     │
                       │        │                                                          │
                       │        ├─ Lifecycle Controller  (state machine, legal transitions)│
                       │        ├─ Context Aggregator     (UNION required_context → Scanner)│
                       │        └─ Health Monitor          (loaded/disabled/invalid/…)      │
                       │        │                                                          │
                       │        ▼                                                          │
                       │  Public API             (load/reload/validate/list/active/…)      │
                       └───────────────┬───────────────────────────────┬──────────────────┘
                    required_context() │                               │ ACTIVE handles
                                       ▼                               ▼
                                 Market Scanner                   Signal Engine
```

- **Strategy Loader** — discovery, parsing, structural validation (§4).
- **Compatibility Checker** — interface/schema/MarketContext/runtime/version checks (§5).
- **Strategy Registry** — the in-memory store + indices + cache + version/health tracking (see
  `STRATEGY_REGISTRY_SCHEMA.json`).
- **Lifecycle Controller** — owns each strategy's lifecycle state and enforces the state machine
  (`STRATEGY_MANAGER_STATE_MACHINE.md`).
- **Context Aggregator** — computes the union of `required_context()` over ACTIVE strategies (§6).
- **Health Monitor** — classifies and reports per-strategy and aggregate health (§8).
- **Public API** — the only surface other AI-Trader modules touch (`STRATEGY_MANAGER_API.md`).

---

## 3. Data flow
```
load_library()
  Loader.discover() → files[]
  for each file: parse → schema-validate → Compatibility.check() → Registry.upsert(entry, lifecycle)
Registry indices built (by id / status / lifecycle / symbol / required-field / health)
activate(strategy) → Lifecycle transition → Context Aggregator recompute
Context Aggregator → required_context (union) → Market Scanner.register_requirements()
Signal Engine → active_strategies() → interface handles → (Signal Engine calls the strategies with MarketContext)
Health Monitor ⟲ continuously classifies; statistics()/health() expose it
```
The Manager is the ONLY producer of the Market Scanner's requirements and the ONLY provider of active strategy
handles to the Signal Engine.

---

## 4. Strategy Loader
- **Discovery:** enumerate `knowledge/strategies/*/strategy.json` (the Library layout). Deterministic ordering by
  `identity.id`. NOT_IMPLEMENTED stubs are discovered but registered in that lifecycle (never activated).
- **Loading & parsing:** read the file; parse JSON. A parse failure → `CORRUPTED` (no registry entry beyond an
  error record).
- **JSON validation:** structural well-formedness (UTF-8, object root).
- **Schema validation:** validate against `knowledge/interface/strategy_contract.v1.schema.json`. A failure lists
  the offending path(s) → `INVALID`.
- **Interface validation:** `interface_version` present and within the Manager's supported MAJOR (delegated to the
  Compatibility Checker, §5).
- **Duplicate detection:** two contracts with the same `identity.id` → the later one is rejected as `DUPLICATE`;
  the first-loaded wins; both are reported. IDs are unique keys.
- **Version mismatch:** `interface_version` MAJOR > supported → `INCOMPATIBLE` (unsupported version). `identity.
  version` is recorded for tracking; a lower patch/minor is accepted.
- **Corrupted contracts:** unreadable/invalid JSON → `CORRUPTED`, quarantined, never activated.
- **Missing required fields:** any Contract required field absent → `INVALID` with the missing path.
- **Output:** a `ValidatedContract` (registry entry) or a typed `LoadError`. The Loader never throws across the API
  boundary for expected failures — every failure becomes a classified registry/health record.

---

## 5. Compatibility Checker
Verifies, for each loaded contract, all of:
1. **Strategy Interface version:** `interface_version` MAJOR == Manager's supported MAJOR; MINOR ≤ supported.
   Higher MAJOR → `INCOMPATIBLE`. Unknown optional fields are ignored (forward-compatible).
2. **Contract version:** `identity.version` is valid semver and recorded; used for change tracking and migration.
3. **MarketContext compatibility:** every field in the contract's `required_data.fields` must exist in the Market
   Scanner's `feature_dictionary` at a compatible MAJOR (queried via `MarketScanner.get_provided_features()`), and
   every required timeframe must be one the scanner can produce. A missing field/timeframe → `INCOMPATIBLE`
   (`missing_field`/`missing_timeframe`) → the strategy is quarantined (never handed to the Signal Engine).
4. **Runtime compatibility:** the contract declares an interface it conforms to; the Manager confirms the runtime
   Strategy API version it supports matches (api_version MAJOR).
5. **Deprecated fields:** fields marked deprecated in the current interface MINOR are accepted but flagged
   `DEPRECATED` in health (a warning, not a rejection) for one MAJOR, per the interface deprecation policy.
6. **Unsupported versions:** any version line beyond the Manager's support window → `INCOMPATIBLE`, with the exact
   unsupported version reported. Never silently coerced.

**Compatibility rules (summary):** accept iff `schema_valid ∧ interface_major_ok ∧ runtime_major_ok ∧
all_required_fields_provided ∧ all_required_timeframes_provided`. Otherwise quarantine with reasons. Deprecated =
accept + warn. The result is stored on the registry entry as a `compatibility` block.

---

## 6. Context Aggregator (one of the most important)
Computes the Market Scanner specification automatically as the **union of `required_context()` over ACTIVE
strategies** (never over inactive/invalid/incompatible ones).

- **Aggregation rules:** for each ACTIVE strategy, take its `required_context()` (timeframes, fields per
  timeframe, lookback per timeframe, htf, symbols). Union the timeframes; union the field sets per timeframe;
  take the **max** lookback per timeframe; union the symbols. Warmup = max warmup across strategies.
- **Deduplication:** identical (timeframe, field) requirements collapse to one; the same feature requested by many
  strategies is provided once. Lookback dedup = max wins.
- **Conflict resolution:** the feature namespace is standardized and versioned, so two strategies cannot demand
  different *definitions* of the same field name within a feature-dictionary MAJOR. If two ACTIVE strategies
  require **incompatible feature-dictionary MAJORs**, that is a hard conflict → the lower-priority / lower-maturity
  strategy is deactivated (`INCOMPATIBLE`) and reported; the aggregate targets one feature-dictionary MAJOR.
  Timeframe/lookback differences are not conflicts (max wins).
- **Optional vs required context:** a strategy MAY mark some `required_data` as optional (nice-to-have). The
  aggregator separates **REQUIRED** (must be provided or the strategy cannot evaluate) from **OPTIONAL** (provided
  if any active strategy wants it, but its absence only lowers that strategy's confidence, never blocks it). The
  Scanner spec carries both sets, tagged.
- **Version handling:** the aggregated spec records the target `feature_dictionary_version` (MAJOR) and the
  `interface_version`. Recomputed on every activation/deactivation/reload; emitted to
  `MarketScanner.register_requirements()`.
- **Output = the Market Scanner specification.** This is the ONLY sanctioned way the scanner learns what to
  produce; the scanner never inspects strategies directly.

---

## 7. Invariants
1. **Single owner:** the Manager is the only AI-Trader module that reads Library contract files; everything else
   uses the Manager's API / interface handles.
2. **Contract-only view:** no research artifact is ever read; a strategy is known only by its Contract + API.
3. **Quarantine, never coerce:** an invalid/incompatible/duplicate/corrupted contract is registered in a
   non-active lifecycle and NEVER handed to the Signal Engine; it is never silently fixed.
4. **Active ⇒ compatible:** only strategies that pass every validation and are in an activatable lifecycle appear
   in `active_strategies()` and contribute to the aggregated context.
5. **Deterministic registry:** given the same Library + versions, the registry, indices, and aggregated context
   are identical every load.
6. **Maturity gates exposure, not the Manager's job to score:** the Manager exposes maturity/validation truthfully
   and may restrict which lifecycles are activatable (policy), but never invents confidence.
7. **Read-only over the Library:** the Manager never writes to `knowledge/strategies/`.

---

## 8. Health Monitor
Classifies each registry entry and the aggregate. Per-strategy health states (reported, not mutating the
contract):
`LOADED` · `DISABLED` · `INVALID` · `INCOMPATIBLE` · `DUPLICATE` · `DEPRECATED` · `STALE` · `MISSING_DEPENDENCY`
· `CORRUPTED`.
- `LOADED` — valid, compatible, in an activatable lifecycle.
- `DISABLED` — operationally turned off (operator/kill-switch) though otherwise valid.
- `INVALID` — failed schema/required-field validation.
- `INCOMPATIBLE` — interface/runtime/MarketContext/version incompatibility.
- `DUPLICATE` — id collision (rejected copy).
- `DEPRECATED` — uses a deprecated field/version (accepted + warned).
- `STALE` — `lifecycle.last_review` older than a configured threshold, or contract version behind a newer Library
  release not yet reloaded.
- `MISSING_DEPENDENCY` — a declared `semantics.dependencies` id is absent/inactive.
- `CORRUPTED` — unreadable/unparseable file.

Aggregate health (`health()`): counts per state, total loaded/active, aggregated-context readiness, and the
overall status (`OK` / `DEGRADED` / `FAILED`). The Health Monitor reports; it does not act (activation/deactivation
is the Lifecycle Controller's, driven by policy/operator).

---

## 9. Error handling & fail-safe policy
Every failure is a **classified, non-fatal registry/health outcome**, never an unhandled throw across the API.

| failure | classification | effect |
|---|---|---|
| missing strategy (referenced id not found) | `MISSING` (lookup) | API returns not-found; no crash |
| invalid JSON / unreadable file | `CORRUPTED` | quarantined; error record kept |
| schema mismatch / missing required field | `INVALID` | quarantined; offending path reported |
| unsupported interface/runtime version | `INCOMPATIBLE` | quarantined; unsupported version reported |
| duplicate `identity.id` | `DUPLICATE` | later copy rejected; first wins; both reported |
| missing contract (empty folder) | `MISSING` | skipped; logged |
| invalid interface (no `interface_version`) | `INVALID`/`INCOMPATIBLE` | quarantined |
| MarketContext field/timeframe not provided | `INCOMPATIBLE` | quarantined (not evaluated) |
| missing declared dependency | `MISSING_DEPENDENCY` | strategy not activatable until resolved |

**Fail-safe policy:** the default resting state of anything abnormal is **NOT ACTIVE**. A strategy is exposed to
the Signal Engine only if it passed all checks and is in an activatable lifecycle. A malformed/incompatible
contract can never cause a trade. A load failure of one strategy never aborts the load of the others (best-effort
load; report the failures).

---

## 10. Module interaction (who may talk to whom)
| module | may the Strategy Manager talk to it? | direction / purpose |
|---|---|---|
| **Market Scanner** | YES | Manager → Scanner: `register_requirements(UNION required_context)`; Manager ← Scanner: `get_provided_features()`/`versions()` for compatibility. |
| **Signal Engine** | YES | Manager → Signal Engine: provides `active_strategies()` handles; Signal Engine passes each strategy the MarketContext (from the Scanner) and calls the Strategy API. The Manager does NOT call the Strategy API itself to trade. |
| **Scoring Engine** | INDIRECT | via the Signal Engine only; the Manager does not talk to Scoring directly. |
| **Learning Engine** | LIMITED | Learning Engine → Manager: may request lifecycle/allocation-relevant metadata and propose ENABLE/DISABLE or reload; it may NEVER mutate a contract. Contract changes come only from the Library (research-gated). |
| **Risk Manager** | NO (direct) | no direct link; policy limits (capital) are read from the contract by the Risk Manager via the interface, not brokered by the Manager. |
| **Execution Engine** | NO | never. |
| **Portfolio Manager** | NO (direct) | consumes signals downstream; no direct Manager link. |
| **Broker Connector** | NO | never — the Manager has no market/venue contact whatsoever. |

Rule: the Manager communicates directly ONLY with the **Market Scanner** (requirements/version handshake) and the
**Signal Engine** (active handles), plus a **restricted control channel** from the Learning Engine (enable/disable/
reload requests, never contract mutation). All downstream trading modules are isolated from it.

---

## 11. Versioning
Version lines, all semver, all recorded in the registry:
- **`strategy_manager_version`** — this module's implementation/spec version.
- **`registry_version`** — the shape of the internal registry object (`STRATEGY_REGISTRY_SCHEMA.json`). MAJOR =
  breaking registry-field change; MINOR = additive; PATCH = clarification.
- **`supported_interface_major`** — the Strategy Interface MAJOR the Manager accepts (currently `1`).
- **`supported_feature_dictionary_major`** — the Market Scanner feature-dictionary MAJOR it targets.

**Compatibility policy:** the Manager accepts contracts with `interface_version` MAJOR == supported and MINOR ≤
supported; higher MAJOR rejected. It requires the Scanner's `feature_dictionary` MAJOR to match its supported
value.
**Upgrade policy:** raising `supported_interface_major` is a Manager MAJOR bump; it must ship with a migration for
the registry and a re-validation pass over the whole Library.
**Migration policy:** on a registry-schema MAJOR change, the Manager migrates persisted registry state (if any) or
rebuilds it from the Library; contracts are re-validated against the new interface support window.
**Deprecation policy:** a field/version marked deprecated is accepted with a `DEPRECATED` health flag for one
interface MAJOR, then rejected at the next MAJOR. Strategies whose only issue is deprecation keep running until
that MAJOR.

---

## 12. Startup & shutdown
**Startup**
```
1. read config (Library path, supported interface/feature-dict MAJORs, activation policy)
2. handshake Market Scanner: get_provided_features(), versions()  (for compatibility checks)
3. load_library(): discover → parse → schema → compatibility → Registry.upsert per strategy
4. Lifecycle Controller assigns each entry an initial lifecycle (derived from contract status/maturity, §state-machine)
5. apply activation policy → set the ACTIVE set
6. Context Aggregator computes UNION(required_context) → Market Scanner.register_requirements()
7. Health Monitor publishes initial health; Manager READY (exposes active_strategies() to Signal Engine)
```
**Shutdown**
```
1. stop accepting reload/activation requests
2. deactivate all strategies (drain: Signal Engine stops receiving handles)
3. emit final statistics()/health(); flush any registry snapshot
4. release resources; the Market Scanner requirements are left in a defined last-known state
```
Startup is fail-safe: if the Scanner handshake or Library load partially fails, the Manager starts with only the
strategies that passed, reports the rest, and never activates a failed strategy. If NOTHING loads, the Manager is
READY with an empty ACTIVE set (the pipeline produces no signals rather than misbehaving).
