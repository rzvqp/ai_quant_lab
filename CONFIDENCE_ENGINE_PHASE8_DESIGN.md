# Phase 8 — Confidence Engine — Design

**CEO scope**: full scoring/grade infrastructure, configurable (not hardcoded) thresholds; grades A/B
may become eligible for risk evaluation but never automatically executable; undefined rules become
explicit disabled placeholders.

## 1. Investigation finding: genuinely new -- no letter-grade concept exists anywhere

A repo-wide search (before writing any code) found: **zero** existing A/B/C/D letter-grade concept
anywhere in this codebase; **zero** existing live composition of Context Engine's `ContextConfidence` +
Recognition Engine's `ConditionalStatistics`; **zero** live "eligible for risk evaluation" gate (the only
two eligibility precedents, `decision_intelligence.eligibility`'s ACCEPT/REJECT gate and
`strategy_health`'s health-state gate, are both batch/historical and coupled to `strategy_manager.
Contract`/trade-history windows -- neither is wired into, or reusable by, the live pipeline). Phase 8 is
therefore a genuinely new module, not a wrapper.

`risk_manager_live/types.py:33`'s own docstring explicitly names this phase: *"`confidence_quality` is
optional -- Phase 8 (Confidence Engine) does not exist yet; a proposal built before it is wired carries
`None`, and the live Risk Manager applies an explicit, disclosed, conservative default."* Confirmed via
grep: nothing in the live pipeline built so far (`order_manager`, `portfolio_manager_live`,
`context_engine`, `recognition_engine_live`) ever populates this field -- it is always `None` today,
falling back to `Quality.MODERATE`. Confidence Engine is the thing that finally computes a real value.

## 2. Reused vs. new

**Reused, unmodified (values only, zero engine coupling)**: `scoring_engine.types.Quality`
(PREMIUM/STRONG/MODERATE/WEAK/POOR) -- reusing `scoring_engine.engine`/`aggregator`/`pipeline` themselves
was rejected because they are coupled to the OLD `signal_engine.StrategySignal`/`strategy_manager`
evidence machinery, not to `MarketContextSnapshot`/`RecognitionResult`. `market_intelligence.confidence`'s
own METHODOLOGY (a simple, disclosed mean of named, independently-inspectable components, never an
opaque/ML score) is reused as the pattern for the new grade formula, not as code.

**Structural precedent only (not code)**: `decision_intelligence.eligibility`'s disclosed ACCEPT/
REJECT-with-mandatory-reasons gate shape -- mirrored for `eligible_for_risk_evaluation`, without
importing `decision_intelligence` itself (wrong input types: `Contract`/`StrategyEdgeReading`, not
`MarketContextSnapshot`/`RecognitionResult`).

**`scoring_engine.config.QualityBands`'s own pattern** (a frozen, injectable dataclass of numeric
thresholds, not module-level hardcoded constants) is the reused CONVENTION for "configurable, not
hardcoded" thresholds -- mirrored as `GradeBands`, a new but conventionally-shaped config object.

**Genuinely new**: `Grade` enum (A/B/C/D -- CEO's own explicit letters, no existing scale to reuse),
`GradeBands`/`ConfidenceEngineConfig`, `ScoreComponents`, `ConfidenceAssessment`, `assess_confidence()`.

## 3. Grading formula (disclosed in full, IMPLEMENTATION CHOICE, never tuned against results)

```
score = mean(non-None components)
components = {
  context_confidence_component: MarketContextSnapshot.market_intelligence.confidence.score  (0..1),
                                 None if market_intelligence itself is None (build failed upstream)
  recognition_component:        RecognitionResult.statistics.favorable_rate  (0..1) if statistics is
                                 present AND sufficiency is SUFFICIENT, else 0.0 (conservative -- no
                                 evidence never boosts a score) -- None only if no RecognitionResult
                                 was supplied to this assessment at all (recognition is optional input)
  strategy_health_component:    ALWAYS None -- an EXPLICIT, DISABLED placeholder (CEO: "undefined rules
                                 become explicit disabled placeholders"). No authorized live strategy-
                                 health signal exists in this pipeline today (strategy_health's own
                                 scoring is batch/historical, not wired live, per this phase's own
                                 investigation) -- deliberately left disabled, not fabricated.
}
grade = A if score >= bands.a_threshold else B if >= b_threshold else C if >= c_threshold else D
```

`Grade -> Quality` mapping (disclosed, for populating `TradeProposal.confidence_quality`, the exact
field Phase 2 reserved for this phase): `A->PREMIUM, B->STRONG, C->MODERATE, D->WEAK`.

## 4. Eligibility ("grades A/B may become eligible... never automatically executable")

`eligible_for_risk_evaluation: bool` is `True` only when ALL of: `grade in {A, B}`, the source
`MarketContextSnapshot.data_quality is OK`, `not MarketContextSnapshot.is_stale`, and (if a
`RecognitionResult` was supplied) `pattern_authorized is True`. This is descriptive ONLY -- Confidence
Engine does not itself construct or submit anything; a caller (the future Execution Orchestrator, Phase
9) decides whether and how to build a `TradeProposal` from an eligible assessment, which then still
must pass Risk Manager AND Portfolio Manager unmodified, exactly like every other candidate (CEO rule
8). Confidence Engine has no import of, or reachable path to, `execution_engine`/`order_manager` at all
-- "never automatically executable" is structural, not merely a naming choice.

## 5. Public entry point

```python
def assess_confidence(
    strategy_id: str, correlation_id: str, context: MarketContextSnapshot,
    recognition: RecognitionResult | None, config: ConfidenceEngineConfig | None = None,
) -> ConfidenceAssessment: ...
```

`recognition` is optional (a caller may not always have run Recognition Engine for this candidate) --
its absence degrades `recognition_component` to `None` (excluded from the mean), never fabricated as 0.
Fail-closed: any exception degrades to `Grade.D`, `eligible_for_risk_evaluation=False`, never raises.
