# Scoring Engine v1 — Operational Sequences (design)

How the Scoring Engine behaves over time. Sequences only — no implementation. Actors: `ORCH`=orchestrator,
`SE`=Signal Engine, `SM`=Strategy Manager, `SC`=Scoring Engine, `RM`=Risk Manager.

---

## 1. Startup
```
ORCH → SC.configure(weights, band_thresholds, supported {signal_schema_major, scoring_schema_major, interface_major})
SC → SE.versions() ; SC → RM handshake (supported scoring_schema major) ; SC → SM (evidence availability)
SC state: UNINITIALIZED → CONFIGURING → READY   (or DEGRADED if a handshake fails)
```

## 2. Single symbol, single/few strategies
```
SE → SC.score_batch(StrategySignal[] for symbol@as_of):
   for each signal (RECEIVED → FILTERED):
        actionable/ready → EVIDENCE_BOUND (SM.get_contract evidence, read-only, cached) → COMPONENTS_SCORED
        non-actionable   → SKIPPED (total=0, SKIP)
   CONFLICT_EVALUATED (batch barrier; here trivial if one signal) → AGGREGATED → RANKED → REASONED → VALIDATED → EMITTED
SC → RM.consume(ScoreBatch)   # ranked OpportunityScore[]
```

## 3. Multi-symbol
```
ORCH → SC.score_batch per symbol (symbols isolated; one ScoreBatch each)
each batch ranked independently within its (symbol, as_of)
SC → RM (one ScoreBatch per symbol)
```
Cross-symbol comparison is NOT the Scoring Engine's job (ranking is within a symbol/as_of); portfolio-level
cross-symbol decisions are downstream.

## 4. Multiple strategies (concurrent high scores)
```
batch has several actionable signals on the same symbol:
   each scored independently on the 7 quality components + risk_penalty
   CONFLICT_EVALUATED: opposing higher-quality signal → conflict_penalty 0.5 on the contradicted one ;
                       correlated same-direction → conflict_penalty 0.2 each (cap 0.4)
   RANKED deterministically (total_score desc, tie-breaks) → multiple may still score high
SC → RM: the full ranked set (SC ranks, does NOT choose/execute)
```

## 5. Missing / degraded data
```
signal.context_ref.data_quality = DEGRADED/STALE/INSUFFICIENT:
   data_quality component reduced (OK1 / DEGRADED0.6 / STALE0.3 / INSUFFICIENT0) ; reason DATA_DEGRADED
signal.state = NEED_CONTEXT (scanner insufficiency): SKIPPED (total=0, SKIP, reason NEED_CONTEXT)
contract evidence unavailable (strategy unknown to SM): historical_confidence=0, reason EVIDENCE_MISSING ; SC → DEGRADED
```
No data is fabricated; missing inputs only lower the score.

## 6. Conflicting signals
```
BUY(S_a, quality 0.7) and SELL(S_b, quality 0.5) on the same symbol@as_of:
   provisional base_quality compared (order-independent) → S_b is opposed by a higher-quality S_a
   → conflict_penalty(S_b) += 0.5 ; S_b total_score drops sharply, reason CONFLICT_OPPOSING
   S_a unaffected (it is the higher-quality side)
SC ranks both, emits both to RM (resolution/selection is downstream, NOT here)
```

## 7. Low confidence (honesty path)
```
signal from an EXPLORATORY strategy with negative OOS:
   historical_confidence ≈ maturity_prior(0.30) · oos_factor(0.4) · 0.8 ≈ 0.10  (reason NEGATIVE_OOS_CAP)
   even with strong live components, total_score is held out of the PREMIUM band
   confidence enum → LOW/VERY_LOW ; quality typically MODERATE/WEAK
```
The Scoring Engine cannot upgrade this from live behaviour (that would be learning) — it only reflects the
contract's evidence.

## 8. Shutdown
```
ORCH → SC.shutdown()
SC: SCORING/READY → SHUTTING_DOWN (finish or drop the in-flight batch) → STOPPED
    emit final statistics()/health() ; release batch + evidence cache (hold no state)
```

## 9. End-to-end (condensed)
```
configure → handshake SE + SM + RM → READY →
[per batch] SE.StrategySignal[] → per-signal (filter→evidence→components) → conflict barrier → aggregate(0-100) →
rank (deterministic) → reason codes → validate → RM.consume(ranked OpportunityScore[]) → …
→ shutdown (drain, hold no state).
```
Throughout, the Scoring Engine: consumes signals + read-only contract evidence (never research), scores quality
deterministically (no ML, no randomness), ranks without choosing, and makes **no** trade, size, risk, or learning
decision.
