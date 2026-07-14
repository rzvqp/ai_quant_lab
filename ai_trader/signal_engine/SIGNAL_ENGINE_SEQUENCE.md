# Signal Engine v1 — Operational Sequences (design)

How the Signal Engine behaves over time. Sequences only — no implementation. Actors: `ORCH`=AI Trader
orchestrator, `SCAN`=Market Scanner, `SM`=Strategy Manager, `SE`=Signal Engine, `SCORE`=Scoring Engine.
Per-strategy Strategy API calls: `health`/`can_trade`/`detect`/`generate_signal`/`explain_signal`.

---

## 1. Startup
```
ORCH → SE.configure(supported {interface_major, context_schema_major, signal_schema_major}, eval_timeout, parallelism)
SE → SM.versions() ; SE → SCORE handshake (supported signal_schema major)
SE READY (awaits (MarketContext, active handles) per cycle)
```
Fail-safe: if a handshake fails, SE starts DEGRADED and only emits when valid inputs arrive; otherwise empty
batches (never malformed).

## 2. Normal per-bar cycle (single symbol)
```
SCAN.scan(as_of) → MarketContextBatch ; ORCH picks ctx = batch[symbol]
SM.active_strategies() → handles[]  (already filtered to activatable lifecycles)
ORCH → SE.evaluate(ctx, handles, trader_state):
   Intake: bind ctx + handles ; verify ctx.as_of aligned (else all-INVALID batch, flagged)
   Strategy Selection: keep handles scoped to ctx.symbol ; fixed order by strategy_id
   for each handle (isolated; may run in parallel, output re-ordered):
        health()                → INVALID/DISABLED → STATE=INVALID/BLOCKED → assemble → next
        can_trade(ctx,state)    → allowed=false     → STATE=BLOCKED (invalid_conditions) → assemble → next
        context sufficient?     → no                → STATE=NEED_CONTEXT (missing_context) → assemble → next
        detect(ctx)             → setup_forming=false→ STATE=NO_SIGNAL → assemble → next
        generate_signal(ctx)    → present=false      → STATE=NO_SIGNAL → assemble → next
                                  present, confirmations not met → STATE=WAIT_CONFIRMATION → assemble → next
                                  present + confirmations met:
                                       entry now      → STATE=BUY/SELL
                                       entry pending  → STATE=LONG_READY/SHORT_READY
        explain_signal(ctx)     → map to structured Explanation
        Signal Validation       → fail → STATE=INVALID (quality_flags)
        assemble StrategySignal (stamp signal_engine/schema versions, context_ref, strategy_version)
   Output Collector: schema-validate each ; dedupe (strategy_id|symbol|as_of) ; order by strategy_id
   → SignalBatch { as_of, symbol, signals[], counts_by_state }
SE → SCORE.consume(SignalBatch)      # the ONLY output consumer
SE.Health/Statistics updated
```
SE holds no result state into the next cycle; each `as_of` is a fresh pure evaluation.

## 3. Multi-symbol cycle
```
ORCH → SE.evaluate_all(MarketContextBatch, handles, trader_state):
   for each symbol (isolated): evaluate(ctx_symbol, handles scoped to symbol, trader_state) → SignalBatch
   → SignalBatch[]  (deterministic order by symbol)
SE → SCORE (one batch per symbol)
```
Symbols never interact; one symbol's degraded context never affects another's signals.

## 4. Cross-timeframe / context-quality handling
```
ctx.data_quality = DEGRADED/STALE (scanner flagged gaps/staleness):
   strategies whose required fields are all present → evaluate normally (quality_flags:[DEGRADED_CONTEXT])
   strategies needing the missing fields           → STATE=NEED_CONTEXT
ctx warmup not satisfied (early session/replay start): all needing those fields → NEED_CONTEXT
```
The engine never fabricates data; sufficiency drives NEED_CONTEXT deterministically.

## 5. Per-strategy failure isolation
```
strategy evaluation exceeds eval_timeout → STATE=INVALID, quality_flags:[EVAL_TIMEOUT] ; batch continues
strategy returns malformed/absent output → STATE=INVALID, quality_flags:[CORRUPTED_OUTPUT]
assembled signal fails schema/semantics  → STATE=INVALID, quality_flags:[SCHEMA_MISMATCH|INVALID_DIRECTION|…]
duplicate (same strategy|symbol|as_of)   → keep one ; drop extra with [DUPLICATE_SIGNAL]
```
Invariant: one strategy's failure is contained; the rest of the batch is emitted normally; no failure yields a
fabricated actionable signal.

## 6. Determinism & replay parity
```
mode=LIVE:   ORCH feeds live MarketContext each bar close
mode=REPLAY: ORCH feeds the historical MarketContext stream (from SCAN replay)
Because SE is a pure function of (context, handles, trader_state), REPLAY reproduces LIVE signals exactly.
Parallel evaluation is allowed; the Output Collector re-imposes strategy_id order before emit → identical batches.
```

## 7. Shutdown
```
ORCH → SE.shutdown()
SE: stop accepting new cycles ; drain in-flight cycle (finish or per-strategy timeout)
    emit final statistics()/health() ; release context views + batch (hold no state)
```

## 8. End-to-end (condensed)
```
configure → handshake SM + SCORE → READY →
[per as_of] receive MarketContext + active handles → per-strategy pipeline (isolated, deterministic) →
one StrategySignal per (strategy,symbol) → validate + batch → SCORE.consume(batch) → …
→ shutdown (drain, hold no state).
```
Throughout, the Signal Engine: reads only the MarketContext + active handles (never research), evaluates each
strategy independently, explains every signal with structured fields, and makes **no** trading decision, ranking,
or risk call.
