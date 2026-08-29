# Q2_TRADE_PLAN_CONTRACT

Created 2026-08-25 per CEO Q1 audit correction, item 4 ("TRADE LEARNING MUST NOW BECOME REAL").

## Why this exists

Q1 produced exactly one simulated trade (2020-04-01, SHORT). It was directionally correct, reached
its expected destination (MFE +11.7pts), and still closed at a net loss because no plan existed for
what happens after the trade goes well — logged as `TRADER_MISTAKE_001`. The CEO has ruled: no second
trade may repeat that specific failure. This contract is the enforcement mechanism.

## The rule

M5 remains permanently unavailable for 2020 (`M5_STATUS = UNAVAILABLE_BY_DATA_COVERAGE`). That must
not block a trade when the apprenticeship's own forward-frozen M15 conditions are genuinely met.
Trades must not be forced — the state chain

```
NO_TRADE → WATCH → MARKET_ARMED → CONFIRMATION_PENDING → SIMULATED LONG / SHORT
```

is allowed to complete when, and only when, `M15_CONFIRMATION_SUFFICIENT = YES` under whatever
standard the live snapshot has itself defined (per `TOC-002`'s own evidenced threshold where
relevant — currently 5-6 consecutive M15 closes with real volume, not thin/wick-only).

## Mandatory pre-entry freeze

**No SIMULATED LONG or SIMULATED SHORT may be entered in the log without all six of the following
being frozen in the same entry snapshot, before the position is considered open:**

1. **ENTRY** — exact price/level.
2. **STRUCTURAL_INVALIDATION** — the price/close condition that proves the read was wrong (not a
   wick threshold — close-based, consistent with the discipline already validated across Q1).
3. **INITIAL_STOP** — the literal stop level tied to STRUCTURAL_INVALIDATION (may be the same price;
   must be stated explicitly, not left implicit).
4. **TARGET / OBJECTIVE_ZONE** — the destination the thesis actually expects, stated as a zone, not
   just "continuation."
5. **MANAGEMENT_PLAN** — what happens between entry and target: e.g. move stop to breakeven after
   +Npts, scale out at an interim level, trail behind a structure point. This field did not exist for
   the Q1 trade — its absence is the entire content of TRADER_MISTAKE_001, and this field's presence
   is the direct fix.
6. **REASSESSMENT_TRIGGER** — the specific condition that forces an explicit reassessment
   (full/partial exit, hold, or tighten) once TARGET / OBJECTIVE_ZONE is reached or once price
   stalls meaningfully before it. A trade may not simply run with no defined moment to revisit it.

If any of the six is missing, the entry does not happen — the state stays at CONFIRMATION_PENDING
and the snapshot must say explicitly which field is missing, exactly as the existing M15-sufficiency
rule already requires when M15_CONFIRMATION_SUFFICIENT = NO.

## Recording

Every simulated trade's six frozen fields, plus its full lifecycle, get one record in
`AI_TRADER_THESIS_PERFORMANCE_LEDGER_V1.md` (TRADE_TAKEN: YES) in addition to the narrative entry in
`lane_a_historical/2020_Q2_H4_LOG.md` and, if the outcome teaches something, an entry in
`AI_TRADER_EXPERIENCE_LEDGER.md` under the existing taxonomy.

## Status

READY — no trade has been taken under this contract yet (replay is paused). The first trade entered
after CEO authorization to resume must satisfy all six fields or must not be entered at all.
