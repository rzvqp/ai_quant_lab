# Strategy Interface v1 — Execution Contract (specification)

The **Execution Contract** is the static, versioned, machine-readable description every strategy in
`knowledge/strategies/` must expose (as its `strategy.json`). The AI Trader reads ONLY this contract plus the
runtime API (`STRATEGY_API_v1.md`). This document defines every field, the enums, required vs optional, the
versioning & compatibility policy, and the validation rules. The normative machine form is
`strategy_contract.v1.schema.json` (JSON Schema Draft 2020-12); where prose and schema differ, the schema wins.

- **interface_version:** `1.0.0`  ·  **schema:** `strategy_contract.v1.schema.json`
- **encoding:** UTF-8 JSON, one object per strategy, at `knowledge/strategies/<slug>/strategy.json`.
- **stability:** additive within a major version; breaking changes bump the major (see §5).

---

## 1. Contract shape (top level)

```
{
  "interface_version": "1.0.0",          // which interface major.minor.patch this contract conforms to
  "identity":     { ... },               // who the strategy is
  "lifecycle":    { ... },               // operational + epistemic state
  "semantics":    { ... },               // what it means / why it fires
  "execution":    { ... },               // how it would be traded
  "evidence":     { ... },               // what is known about it (metrics + validation ladder)
  "provenance":   { ... }                // where it came from (read-only audit; NOT research access)
}
```

Grouping is normative (the schema nests these objects). The CEO-requested flat field names all map into these
groups — the mapping is given per field below as `group.field`.

---

## 2. Field definitions

Legend: **R** = required, **O** = optional (may be `null` but the key must be present), **enum** values are
UPPER_SNAKE. All numeric metrics are in **R units** (risk-normalised, per the library's sizing model) unless
noted. "unknown" is expressed as `null` + an explicit `*_status` of `NOT_RUN` — never as a fabricated number.

### 2.1 identity
| field | req | type | definition |
|---|---|---|---|
| `identity.id` | R | string `^S\d+$` | permanent strategy id (e.g. `S1`). Immutable for the life of the strategy. |
| `identity.name` | R | string | human name (e.g. "Confirmed Liquidity Sweep Reversal"). |
| `identity.slug` | R | string | folder slug (`S01_confirmed_liquidity_sweep_reversal`). |
| `identity.version` | R | semver | the STRATEGY's own version (bumps when its rules/metrics change; see §5). |
| `identity.class` | R | string | mechanism class (e.g. "Liquidity / stop-hunt reversal"). |

### 2.2 lifecycle
| field | req | type | definition |
|---|---|---|---|
| `lifecycle.status` | R | enum `StrategyStatus` | deployment state: `IMPLEMENTED` \| `INVALID` \| `NOT_IMPLEMENTED` \| `DEPRECATED` \| `DISABLED`. |
| `lifecycle.maturity` | R | enum `Maturity` | epistemic maturity ladder: `EXPLORATORY` \| `CANDIDATE` \| `VALIDATED` \| `PROMOTED` \| `RETIRED`. Reflects research state; NOT profitability. |
| `lifecycle.current_health` | R | enum `Health` | runtime operability, set by the Trader/monitor, defaulting from the contract: `OK` \| `DEGRADED` \| `STALE` \| `DISABLED` \| `INVALID` \| `UNKNOWN`. |
| `lifecycle.priority` | O | integer 0–100 | research/allocation priority hint (higher = more attention). Advisory only. |
| `lifecycle.last_review` | R | date `YYYY-MM-DD` | date the evidence block was last refreshed/reviewed. |

### 2.3 semantics
| field | req | type | definition |
|---|---|---|---|
| `semantics.mechanism` | R | string | the economic/behavioural reason the edge should exist (who loses). |
| `semantics.signal_reason` | R | string (template) | human template explaining WHY a signal fires; `explain_signal()` fills placeholders at runtime. |
| `semantics.market_regime` | R | object | regimes in which the strategy is intended to operate — `{ applicable: [Regime...], avoid: [Regime...] }`. `Regime` enum: `TREND_UP` \| `TREND_DOWN` \| `RANGE` \| `HIGH_VOL` \| `LOW_VOL` \| `SESSION_OPEN` \| `ANY`. |
| `semantics.required_data` | R | array\<DataReq\> | data the strategy needs to evaluate — each `{ timeframe, fields[], lookback_bars, htf?[] }`. The Trader must supply exactly this (see `required_context()`). |
| `semantics.required_confirmations` | R | array\<string\> | named confirmation conditions that must hold before a signal is valid (may be empty). |
| `semantics.dependencies` | O | array\<string\> | ids of other strategies/indicators this one depends on (usually empty; strategies are independent). |

### 2.4 execution
| field | req | type | definition |
|---|---|---|---|
| `execution.timeframe` | R | string | primary execution timeframe (e.g. `M15`). |
| `execution.sessions` | R | string | sessions in which it is active (free text + regime tags). |
| `execution.long_short` | R | enum | `LONG` \| `SHORT` \| `BOTH`. |
| `execution.entry` | R | RuleSpec | entry rule: `{ description, trigger, timing }` (`timing` = when the fill occurs, e.g. next-open). |
| `execution.exit` | R | RuleSpec | exit rule(s) (targets/timeouts/trailing options). |
| `execution.stop` | R | RuleSpec | stop-loss rule (incl. the engine stop-floor). |
| `execution.target` | O | RuleSpec | explicit profit target if distinct from `exit` (else `null`). |
| `execution.risk_model` | R | object | `{ model: "risk_normalised_1R", risk_definition, stop_floor, costs }`. |
| `execution.position_sizing` | R | object | sizing assumptions (see library); absolute size is an execution-layer decision. |
| `execution.capital_limit` | O | object | `{ max_risk_per_trade_R, max_strategy_allocation_pct }` — advisory caps the Trader may honour (null = unset by research). |
| `execution.max_concurrent_positions` | R | integer ≥1 | how many simultaneous positions this strategy may hold (research default = 1; engine suppresses overlap). |
| `execution.expected_frequency` | R | object | `{ trades_per_year, basis }` derived from historical n over the research window; advisory. |
| `execution.cooldown` | R | object | `{ bars, scope }` — minimum bars between signals (scope = `PER_STRATEGY` \| `PER_DIRECTION`). Default from the overlap rule. |
| `execution.invalid_conditions` | R | array\<string\> | conditions under which NO signal may be produced (universal engine guards + strategy-specific). |

### 2.5 evidence  (the epistemic ladder — must be truthful)
| field | req | type | definition |
|---|---|---|---|
| `evidence.confidence` | R | object | `{ level: Confidence, score?: 0–1, rationale }`. `Confidence` enum: `NONE` \| `NEGATIVE` \| `VERY_LOW` \| `LOW` \| `MEDIUM` \| `HIGH`. `score` optional, `null` if not quantified. |
| `evidence.historical_metrics` | R | Metrics | research-segment metrics: `{ n, expectancy_R, profit_factor, drawdown_R, win_rate, pos_months, months, top1_share, segment: "research_60pct" }`. |
| `evidence.oos_metrics` | R | Metrics | validation-segment metrics: `{ n, expectancy_R, segment: "validation_20pct" }` (fields may be `null` if n small). |
| `evidence.walk_forward_status` | R | enum `TestStatus` | `NOT_RUN` \| `RUNNING` \| `PASS` \| `FAIL` \| `INCONCLUSIVE`. Currently `NOT_RUN` lab-wide. |
| `evidence.matched_null_status` | R | object | `{ status: TestStatus, scope: PILOT\|WAVE1\|FULL_UNIVERSE\|NONE, p?: number, adjusted_p?: number, note }`. |
| `evidence.global_fdr_status` | R | enum `TestStatus` | `NOT_RUN` \| … . Currently `NOT_RUN` (CEO-gated). |
| `evidence.validation_status` | R | string | one-line human summary of the whole ladder (EXPLORATORY … holdout SEALED …). |
| `evidence.known_limitations` | R | array\<string\> | explicit caveats (beta confound, negative OOS, fragility, small n, invalid, etc.). Empty array only if genuinely none. |

### 2.6 provenance  (read-only audit trail; NOT a research handle)
| field | req | type | definition |
|---|---|---|---|
| `provenance.engine` | R | string | engine + version that produced the behaviour (e.g. "mstrat.py v2 (FROZEN)"). |
| `provenance.generated_from` | R | string | how the contract was produced ("frozen research; no re-backtest"). |
| `provenance.holdout_status` | R | enum | `SEALED` \| `OPENED`. Must be `SEALED` unless a CEO-gated holdout run changed it. |
| `provenance.source_ref` | O | string | opaque pointer for humans/audit (e.g. a parquet path). **The AI Trader MUST NOT dereference it** — it exists for lab audit only. |

> **CEO field-name → contract path map.** `id`→`identity.id`; `version`→`identity.version`; `status`→
> `lifecycle.status`; `maturity`→`lifecycle.maturity`; `current_health`→`lifecycle.current_health`;
> `priority`→`lifecycle.priority`; `confidence`→`evidence.confidence`; `signal`/`signal_reason`→ **runtime**
> (`generate_signal()`/`explain_signal()`, not static — see note below) with the static template in
> `semantics.signal_reason`; `mechanism`→`semantics.mechanism`; `market_regime`→`semantics.market_regime`;
> `required_data`→`semantics.required_data`; `required_confirmations`→`semantics.required_confirmations`;
> `entry`/`exit`/`stop`/`target`→`execution.*`; `risk_model`→`execution.risk_model`; `capital_limit`→
> `execution.capital_limit`; `max_concurrent_positions`→`execution.max_concurrent_positions`;
> `expected_frequency`→`execution.expected_frequency`; `cooldown`→`execution.cooldown`; `dependencies`→
> `semantics.dependencies`; `historical_metrics`/`oos_metrics`/`walk_forward_status`/`matched_null_status`/
> `global_fdr_status`/`validation_status`→`evidence.*`; `last_review`→`lifecycle.last_review`;
> `known_limitations`→`evidence.known_limitations`.

> **Static vs runtime.** `signal` (active? long/short? now?) and the concrete `signal_reason` are **runtime** —
> they depend on live market context and are answered by the API (`detect`/`generate_signal`/`explain_signal`),
> never stored in the static contract. The contract only declares the *template* and the *rules*. This keeps the
> contract stable and the strategy stateless.

---

## 3. Required vs optional (summary)
- **Required (must be present, non-null):** `interface_version`; all of `identity.*`; `lifecycle.status`,
  `.maturity`, `.current_health`, `.last_review`; all `semantics.*` except `dependencies`; all `execution.*`
  except `target`, `capital_limit`; all `evidence.*`; all `provenance.*` except `source_ref`.
- **Optional (key present, value may be null):** `lifecycle.priority`, `semantics.dependencies`,
  `execution.target`, `execution.capital_limit`, `evidence.confidence.score`, `provenance.source_ref`, and any
  individual `Metrics` field that is genuinely unavailable (must be `null`, never invented).

## 4. Validation rules (beyond the JSON Schema shapes)
1. **Enum integrity:** every enum field holds a listed value; unknown → `UNKNOWN`/`NOT_RUN`, never free text.
2. **Honesty rule:** if any metric is `null`, the corresponding `*_status` must be `NOT_RUN`/`NONE` or a
   `known_limitations` entry must explain the gap. A number MUST come from frozen research, never a guess.
3. **Direction consistency:** `execution.long_short` must be consistent with the strategy's grammar; a signal's
   direction (runtime) must be a subset of it.
4. **Maturity gate:** `maturity=VALIDATED` requires `matched_null_status.status=PASS` AND
   `walk_forward_status=PASS`; `maturity=PROMOTED` additionally requires `global_fdr_status=PASS` and a
   holdout-confirmed result. Today no strategy may exceed `EXPLORATORY`/`CANDIDATE`.
5. **Invalid strategies:** `status=INVALID` ⇒ `maturity=EXPLORATORY`, `current_health=INVALID`, and the API's
   `detect()`/`can_trade()` MUST return inactive/false regardless of context.
6. **Holdout guard:** `provenance.holdout_status` must be `SEALED` unless a CEO-gated event set it otherwise;
   the Trader treats `OPENED` results with the same skepticism until `validation_status` says confirmed.
7. **Frequency sanity:** `expected_frequency.trades_per_year` ≥ 0 and derived from `historical_metrics.n`.
8. **No research leakage:** the contract MUST NOT contain raw research handles beyond the opaque
   `provenance.source_ref`; no parquet contents, no KG nodes, no code.

## 5. Versioning policy (semver)
Two independent version lines:
- **`interface_version`** — the CONTRACT SCHEMA (this package). `MAJOR.MINOR.PATCH`:
  - **MAJOR**: a breaking change (renamed/removed required field, changed type/enum semantics). The Trader must
    opt in; old contracts do not satisfy a new major.
  - **MINOR**: additive, backward-compatible (new OPTIONAL field, new enum value that old readers can treat as
    unknown). Old Traders keep working.
  - **PATCH**: clarifications, doc fixes, non-semantic tightening.
- **`identity.version`** — each STRATEGY's own content version. Bump **MAJOR** when entry/exit/stop *rules*
  change (behaviour differs); **MINOR** when metrics/evidence refresh or optional fields added; **PATCH** for
  text/typo. A strategy MAY advance its version without an interface bump.

Every contract records the `interface_version` it targets. A registry (the manifest) records, per strategy, its
`identity.version` and the `interface_version`.

## 6. Compatibility policy
- **Reader (AI Trader) rule:** a Trader declares the max `interface_version` MAJOR it supports. It MUST accept
  any contract with the same MAJOR and MINOR ≤ its own, and MUST ignore unknown OPTIONAL fields and unknown enum
  values (treating unknown enums as `UNKNOWN`/`NOT_RUN`). It MUST reject a higher MAJOR.
- **Writer (Library) rule:** the Library never removes/renames a required field or repurposes an enum within a
  MAJOR. Deprecation path: mark a field deprecated in docs for one MINOR, keep emitting it for one MAJOR, remove
  only at the next MAJOR.
- **Deprecating a strategy:** set `lifecycle.status=DEPRECATED` (kept readable) then `RETIRED` maturity; never
  hard-delete a contract inside a MAJOR — the Trader may hold references.
- **Unknown/forward fields:** forward-compatible by construction (readers ignore unknown optional keys).
- **Validation on load:** the Trader validates every contract against the schema at load; a contract that fails
  is quarantined (loaded as `current_health=INVALID`, never traded), never silently coerced.

## 7. Relationship to the current `strategy.json` (v0 seed)
The files generated in `knowledge/strategies/` are the **v0 seed**: they already carry most `evidence`,
`execution`, `semantics`, and `provenance` content but in a flatter shape. Migrating them to fully validate
against `strategy_contract.v1.schema.json` (regrouping into identity/lifecycle/semantics/execution/evidence/
provenance and adding `interface_version`, `market_regime`, `required_data`, `cooldown`, `expected_frequency`,
`current_health`, `last_review`) is a **separate, CEO-gated task** — this document only DESIGNS the target. No
existing file is modified here.
