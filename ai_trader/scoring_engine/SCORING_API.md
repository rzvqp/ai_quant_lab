# Scoring Engine v1 — API (definition only)

The Scoring Engine's public API. **Definition and semantics only; no implementation.** Every method is a
deterministic function of the supplied `StrategySignal`(s) + a contract-evidence snapshot + the fixed scoring
model; none open/size positions, manage risk, learn, or read research artifacts.

- **api_version:** `1.0.0` · **emits:** `OpportunityScore` (`SCORING_SCHEMA.json`).
- **inputs:** `StrategySignal` / `StrategySignal[]` (Signal Engine); contract evidence via Strategy Manager
  (read-only).
- **failure model:** expected failures are returned as low/zero `INVALID`/`SKIP` scores or typed results, never
  thrown across the boundary. One bad signal never aborts a batch.

---

## 0. Types (summary; full shapes in the schema)
```
StrategySignal   # input (SIGNAL_SCHEMA.json)
OpportunityScore # output (SCORING_SCHEMA.json)
ScoreBatch       { as_of, symbol?, scores: OpportunityScore[] (ranked), counts_by_recommendation, generated_at }
ScoreExplanation { score_id, component_scores, base_quality, penalty_factor, reason_codes[], model_version }
ValidationResult { valid, reasons[] }
Statistics       { batches, scores_total, by_recommendation, by_quality, avg_score, invalids }
EngineHealth     { overall, state, degraded_reasons[], supported_versions }
```

---

## 1. Scoring

### `score_signal(signal: StrategySignal, evidence?: ContractEvidence) -> OpportunityScore`
Score a single signal. `evidence` may be supplied by the caller or fetched read-only from the Strategy Manager.
Because `conflict_penalty` needs the batch, a lone call scores with `conflict_penalty=0` (documented in
`reason_codes` as `NO_BATCH_CONTEXT`).
- **returns:** one `OpportunityScore`.
- **failures:** invalid/corrupt signal → `total_score=0`, `recommendation=INVALID`, reason `SIGNAL_INVALID`;
  non-actionable state → `SKIP`. Never thrown.

### `score_batch(signals: StrategySignal[]) -> ScoreBatch`
Score a whole batch (the normal entry point): per-signal components + the cross-signal `conflict_penalty` +
deterministic ranking. Returns the ranked `OpportunityScore[]`.
- **returns:** `ScoreBatch` (scores ordered by the deterministic ranking key; `rank` assigned).
- **semantics:** multiple high scores may coexist; the engine ranks but never selects. Determinism guaranteed
  (§SCORING_MODEL §7). Empty input → empty batch (valid).
- **failures:** contained per signal; the batch always completes.

---

## 2. Explanation & validation

### `explain_score(score_id) -> ScoreExplanation | NotFound`
Return the structured decomposition of a produced score: every `component_score`, `base_quality`,
`penalty_factor`, the `reason_codes`, and the `scoring_model_version`. Structured only — no free-text generation.
- **returns:** `ScoreExplanation`, or `NotFound`.

### `validate(score: OpportunityScore) -> ValidationResult`
Validate a score against `SCORING_SCHEMA.json` + semantic rules (total in [0,100], components in [0,1], band ↔
quality ↔ recommendation consistency, non-actionable ⇒ SKIP/INVALID). Pure; used internally before emit and
available to consumers/tools.
- **returns:** `ValidationResult { valid, reasons[] }`.

---

## 3. Introspection

### `statistics() -> Statistics`
Per-batch and cumulative counts by recommendation/quality, average score, invalid counts. For the Performance
Monitor and dashboards.

### `health() -> EngineHealth`
Overall engine health (`OK`/`DEGRADED`/`FAILED`), current lifecycle state, degraded reasons, and the supported
version window (scoring/signal/interface schemas). Reports only; takes no action.

### `versions() -> { scoring_engine_version, scoring_schema_version, scoring_model_version, supported: { signal_schema_major, interface_major } }`
Version lines + support window for the end-to-end handshake (Signal Engine → Scoring Engine → Risk Manager).

---

## 4. Contract of use (invariants the caller can rely on)
1. **One score per input signal**, always (including SKIP/INVALID for non-actionable/failed inputs).
2. **Deterministic:** identical `(signal batch, evidence snapshot, model version)` ⇒ identical scores AND ranking.
3. **Non-ML, non-stochastic:** the score is fixed arithmetic over declared inputs; no training, no randomness.
4. **Honesty-preserving:** the engine can only lower confidence relative to a strategy's own claims, never inflate
   it; unvalidated/negative-OOS strategies are structurally capped.
5. **Quality only:** produces scores/recommendations; makes no trade, size, risk, or portfolio decision.
6. **Validated:** every emitted score conforms to `SCORING_SCHEMA.json`; failures emit `INVALID`, never a
   fabricated high score.

## 5. What the API deliberately does NOT provide
- No `open_position`, `size`, `submit_order`, or any risk/portfolio method.
- No method that mutates a strategy, its contract, its stored confidence, or research.
- No direct link to the Broker, Research Lab, Knowledge Base, Ontology, or Experiment Planner.
