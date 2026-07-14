# Scoring Engine v1 — State Machine (design)

Two state machines: (A) the **engine lifecycle** (the module's operational states) and (B) the **per-opportunity
scoring lifecycle** (the states a single score passes through inside a batch). Design only — no code.

---

## A. Engine lifecycle

| state | meaning |
|---|---|
| `UNINITIALIZED` | constructed, not configured |
| `CONFIGURING` | reading scoring config (weights, thresholds, supported versions), running handshakes |
| `READY` | idle, awaiting a StrategySignal batch |
| `SCORING` | actively processing one batch through the scoring pipeline |
| `DEGRADED` | operating with a failed handshake / missing evidence source; still scores but flags reduced confidence |
| `SHUTTING_DOWN` | draining the in-flight batch |
| `STOPPED` | terminal; holds no state |

```
UNINITIALIZED → CONFIGURING → READY ⇄ SCORING
                     │            │        │
                     └──fail──────┴───────▶ DEGRADED ⇄ SCORING
                                  │            │
                                  └── shutdown → SHUTTING_DOWN → STOPPED
```
- `READY→SCORING` on each incoming batch; `SCORING→READY` when the batch is emitted.
- Any handshake/evidence failure → `DEGRADED`; the engine keeps scoring but caps `historical_confidence` (reason
  `EVIDENCE_MISSING`) and never fabricates a high score. Recovery returns to `READY`.
- Fail-safe: with no valid input, the engine stays `READY` and emits empty batches — never a fabricated score.

---

## B. Per-opportunity scoring lifecycle (inside a batch)

Each `StrategySignal` produces exactly one `OpportunityScore`, passing through:

```
RECEIVED
   │  (parse + schema check of the incoming signal)
   ├─ signal invalid/corrupt ─────────────▶ SCORE_INVALID  (total=0, recommendation=INVALID, reason SIGNAL_INVALID)
   ▼
FILTERED
   │  classify state: actionable (BUY/SELL) · ready (LONG_READY/SHORT_READY) · pending (WAIT_CONFIRMATION) · non-actionable
   ├─ non-actionable (NO_SIGNAL/BLOCKED/NEED_CONTEXT) ─▶ SKIPPED  (total=0, recommendation=SKIP, reason mirrors state)
   ▼
EVIDENCE_BOUND
   │  fetch contract evidence (Strategy Manager, read-only)
   ├─ evidence missing ─▶ (continue with historical_confidence=0, reason EVIDENCE_MISSING)
   ▼
COMPONENTS_SCORED            (the 7 quality components + risk_penalty computed per signal)
   ▼
CONFLICT_EVALUATED          (batch barrier: conflict_penalty from the whole batch)
   ▼
AGGREGATED                  (base_quality · penalty_factor → total_score; derive confidence/quality/recommendation)
   ▼
RANKED                      (deterministic order + rank assigned)
   ▼
REASONED                    (structured reason_codes attached)
   ▼
VALIDATED
   ├─ schema/semantic fail ─▶ SCORE_INVALID  (fail-safe: total=0, recommendation=INVALID)
   ▼
EMITTED                     (OpportunityScore sent to the Risk Manager)
```

Terminal per-opportunity states: `EMITTED` (normal), `SKIPPED` (non-actionable, scored 0/SKIP), `SCORE_INVALID`
(fail-safe 0/INVALID). Every signal reaches exactly one terminal state; none is silently dropped.

## C. Determinism & fail-safe invariants
1. The batch barriers (`CONFLICT_EVALUATED`, `RANKED`) make cross-signal effects order-independent and
   reproducible; component scoring may run in parallel but the barriers re-impose the deterministic order.
2. Any abnormal transition resolves to `SKIPPED` or `SCORE_INVALID` with `total_score=0` and structured reasons —
   never an inflated score.
3. One signal's failure never affects another's score (isolation); the batch always completes.
4. Identical `(signal batch, evidence snapshot, model version)` ⇒ identical scores, ranks, and terminal states
   (replay parity).
