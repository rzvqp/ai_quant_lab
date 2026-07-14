# Scoring Engine v1 — Architecture (design)

The Scoring Engine turns `StrategySignal`s into standardized, deterministic 0–100 `OpportunityScore`s and ranks
them. It only evaluates signal quality: no execution, no risk management, no learning, no strategy/contract/
research mutation. Design only — no code.

---

## 1. Purpose
Answer, for every signal produced this cycle, "**how good is this opportunity, on a fixed 0–100 rubric, right
now?**" and provide a **deterministic ranking** of concurrent opportunities. The score is a transparent, rule-based
composite — **not** a machine-learning prediction and **not** a trade decision.

## 2. Responsibilities & boundaries
**Responsibilities**
1. Consume the `StrategySignal` batch from the Signal Engine.
2. For each signal, read the strategy's **contract evidence** (via Strategy Manager, read-only) for the historical
   component.
3. Compute the nine components (`SCORING_MODEL.md`), aggregate them into a 0–100 `total_score`, derive a
   `recommendation` and structured `reason_codes`.
4. Compute cross-signal **conflict** penalties (only the Scoring Engine sees all signals at once).
5. **Rank** the opportunities deterministically and emit `OpportunityScore`s to the Risk Manager.
6. Validate every score against the schema; report health/statistics.

**Hard boundaries (never)**
- Never open, size, or route positions; never touch the Broker.
- Never manage risk (the `risk_penalty` is a *quality discount*, not position risk — see §model).
- Never learn/adapt; weights are fixed per version, not trained.
- Never change a strategy's parameters, its contract, or the confidence stored inside the strategy/contract.
- Never read Research-Lab artifacts (`code/`, `results/`, `knowledge/experiments/`, `knowledge/ontology/`, KB).

## 3. Inputs & outputs
**Inputs**
- `StrategySignal[]` (Signal Engine, `SIGNAL_SCHEMA.json`): state, direction, `signal_strength`, `confidence`,
  `confirmations`, `context_ref` (incl. `data_quality`, regime), `explanation`, `trade_params`.
- Contract **evidence** per strategy (Strategy Manager `get_contract()`, read-only): maturity, OOS metrics,
  historical metrics (drawdown, PF, fragility), validation ladder, `confidence`.
- (Optional) the strategy's `Score` self-assessment via the Strategy API `get_score()` — the Scoring Engine is its
  sanctioned caller; if used, it is ONE input to the composite, never the whole score.
- Fixed **scoring config**: component weights + band thresholds (versioned, non-learned).

**Outputs**
- `OpportunityScore[]` (`SCORING_SCHEMA.json`): `total_score` (0–100), `component_scores`, `confidence`,
  `quality`, `recommendation`, `reason_codes`, deterministic `rank`, versions, references.

## 4. Pipeline (per batch)
```
StrategySignal[]                                   (from Signal Engine)
   │
1. Intake & Filter        bind batch ; separate actionable/ready vs non-actionable states
   │
2. Evidence Binding       for each signal, fetch contract evidence (Strategy Manager, read-only, cached)
   │
3. Component Scoring       compute the 9 normalized components per signal (SCORING_MODEL §components)
   │
4. Conflict Analysis       cross-signal: opposite-direction / correlated-stacking → conflict_penalty per signal
   │
5. Aggregation             combine components → total_score (0–100) ; derive confidence, quality, recommendation
   │
6. Ranking                 deterministic sort (total_score desc, tie-breaks) → rank per (symbol, as_of)
   │
7. Reason Codes            attach structured reason_codes (why this score/recommendation)
   │
8. Validation & Output     schema-validate each OpportunityScore → emit to Risk Manager
```

## 5. Components (internal modules)
- **Intake & Filter** — binds the batch, tags actionable/ready/non-actionable; a non-actionable signal still gets
  a score (usually 0 / SKIP) for completeness.
- **Evidence Binder** — read-only fetch + cache of contract evidence per strategy (stable within a cycle).
- **Component Scorer** — the nine deterministic component functions (`SCORING_MODEL.md`).
- **Conflict Analyzer** — the only cross-signal stage; computes `conflict_penalty` from the full batch.
- **Aggregator** — the fixed 0–100 formula → `total_score`, `confidence`, `quality`, `recommendation`.
- **Ranker** — deterministic ordering + `rank` assignment (ties broken deterministically).
- **Reason Coder** — structured `reason_codes` (enumerated), no free-text generation.
- **Validator / Output** — schema validation + emission.
- **Health Monitor / Statistics** — per-cycle counts, timings, invalid counts.

## 6. Data flow
```
Signal Engine → OpportunityScoreBatch = Scoring.score_batch(StrategySignal[])
   per signal: Evidence Binder → Component Scorer → (Conflict Analyzer across batch) → Aggregator → Reason Coder
   Ranker orders the batch → Validator → OpportunityScore[]
→ Risk Manager
Health/Statistics updated per cycle.
```
The Scoring Engine holds no cross-cycle state that changes results; each batch is a fresh pure evaluation
(caches — e.g. contract evidence — are content-addressed and do not alter determinism).

## 7. Failure modes & fail-safe
| condition | handling |
|---|---|
| signal fails to parse / schema mismatch | `OpportunityScore` with `total_score=0`, `recommendation=INVALID`, reason `SIGNAL_INVALID` |
| non-actionable state (NO_SIGNAL/BLOCKED/NEED_CONTEXT/INVALID) | scored 0 / low; `recommendation=SKIP`; reason mirrors the state |
| WAIT_CONFIRMATION / LONG_READY / SHORT_READY | scored with reduced `execution_readiness`; `recommendation=WATCH`/`ARM` |
| contract evidence missing (strategy unknown to Manager) | `historical_confidence=0`; reason `EVIDENCE_MISSING`; score capped |
| degraded/stale `data_quality` in `context_ref` | `data_quality` component reduced; reason `DATA_DEGRADED` |
| conflict with a higher-ranked opposing signal | `conflict_penalty` applied; reason `CONFLICT_OPPOSING`/`CONFLICT_CORRELATED` |
| aggregation/validation error | fail-safe `total_score=0`, `recommendation=INVALID`; batch continues |

**Fail-safe policy:** any abnormal input yields a **low/zero, non-actionable** score with structured reasons —
never an inflated or fabricated high score. One bad signal never aborts the batch; the Scoring Engine can only
lower confidence, never manufacture it.

## 8. Determinism
- Pure function of `(StrategySignal batch, contract-evidence snapshot, fixed weights/thresholds, version)`.
- **No ML, no randomness, no wall-clock in the logic.** Component functions and the aggregation formula are fixed
  arithmetic (`SCORING_MODEL.md`).
- **Ranking is deterministic:** primary key `total_score` (desc), tie-breaks `historical_confidence` (desc) →
  `signal_strength` (desc) → `strategy_id` (asc). No stochastic tie-breaking. Identical batches ⇒ identical scores
  AND identical order.
- Replay parity: given the same signal stream + evidence snapshot, replay reproduces live scores exactly.

## 9. Performance model
- **Batching:** scores are computed per batch (one Signal Engine batch → one OpportunityScore batch); the Conflict
  Analyzer needs the whole batch, so scoring is batch-oriented (not per-signal streaming).
- **Caching:** contract evidence is cached per strategy per cycle (content-addressed by contract version/hash);
  component sub-results are not cached across cycles.
- **Parallelism:** component scoring per signal MAY run in parallel; the Conflict Analyzer and Ranker are batch
  barriers that re-impose deterministic order, so parallelism never changes results.
- **Deterministic ordering:** output always ordered by the ranking key above.
- **Latency/memory:** bounded per batch; holds only the current batch + the per-cycle evidence cache; no unbounded
  history. (Concrete latency numbers are a build-time tuning concern; the design fixes only that budgets exist.)

## 10. Versioning
- **`scoring_engine_version`** — module implementation/spec version.
- **`scoring_schema_version`** — `OpportunityScore` shape (`SCORING_SCHEMA.json`). MAJOR = breaking; MINOR =
  additive optional field / new reason code / new recommendation value; PATCH = clarification.
- **`scoring_model_version`** — the component set, weights, and formula (`SCORING_MODEL.md`). A weight/formula
  change bumps this (MINOR for a re-weight within the same components, MAJOR for a component change) so that any
  score is reproducible against the exact model that produced it.
- Echoes consumed `signal_schema_version` and `interface_version` for the end-to-end handshake.
- **Compatibility:** the Risk Manager declares the `scoring_schema_version` MAJOR it supports; the Scoring Engine
  emits a compatible MAJOR; unknown optional fields are ignored (forward-compatible). **Migration:** a schema
  MAJOR ships with a field mapping. **Deprecation:** deprecated fields/reason codes emitted for one MAJOR with a
  note, removed at the next MAJOR.

## 11. Module interaction (who may talk to whom)
| module | may the Scoring Engine talk to it? | direction / purpose |
|---|---|---|
| **Signal Engine** | YES | ← `StrategySignal[]` (its input). |
| **Strategy Manager** | YES | ← read-only contract evidence (`get_contract`); sanctioned caller of `get_score()`. |
| **Risk Manager** | YES | → ranked `OpportunityScore[]` (its output consumer). |
| **Broker Connector** | NO | never — zero venue contact. |
| **Research Lab / Knowledge Base / Ontology / Experiment Planner** | NO | never — no research artifact access. |
| **Portfolio Manager / Execution Engine / Learning Engine** | NO (direct) | reached downstream via the Risk Manager, not directly by the Scoring Engine. |

Rule (CEO-fixed): allowed direct = **Signal Engine, Strategy Manager, Risk Manager**; forbidden = **Broker,
Research Lab, Knowledge Base, Ontology, Experiment Planner**.

## 12. Startup & shutdown
**Startup**
```
1. read scoring config (weights, band thresholds, supported signal/scoring schema versions)
2. handshake Signal Engine (signal_schema major) and Risk Manager (scoring_schema major)
3. handshake Strategy Manager (evidence availability)
4. READY — awaits a StrategySignal batch per cycle
```
**Shutdown**
```
1. stop accepting new batches
2. finish the in-flight batch (or drop it cleanly)
3. emit final statistics()/health() ; release the batch + evidence cache (hold no state)
```
Fail-safe: if a handshake fails, the engine starts DEGRADED and scores only when valid inputs arrive; with no
input it emits empty batches — never a fabricated score.
