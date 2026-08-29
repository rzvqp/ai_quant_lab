# CAUSAL_REPLAY_ACCELERATOR_V1 — DESIGN / FEASIBILITY ONLY

**No implementation performed. No bar 379 consumed. This document is a design artifact only.**

Frozen reference point: `LAST_CONSUMED_BAR = 378`, `NEXT_UNSEEN_BAR = 379`, per
`Q4_GOVERNANCE_SCOPE_BREACH_001.md`.

---

## 1. Problem statement

Q4 2020 is ~8,832 M15 bars. 378 are consumed (~4.3%); ~8,454 remain. The current method costs
roughly 2 external tool round-trips per bar (`replay_step`, then a parallel `data_get_ohlcv` +
`data_get_pine_tables` read), plus amortized overhead for periodic timestamp verification and log
writes (~0.25 calls/bar). Observed throughput this session: **~90-130 bars per long invocation**
(bars 288-378 = 91 bars consumed in one continuous turn). At that pace, completing the remainder
needs on the order of **~70-90 more invocations** of this length — a real, disclosed structural
constraint, not a discretionary pacing choice (see the prior turn's checkpoint for the underlying
arithmetic).

The goal is to reduce external-call and per-bar token overhead **without** relaxing the causal
guarantee this whole apprenticeship depends on: no bar's market-reading decision may ever be made
with access to a later bar's data.

## 2. Architecture options

### Option A — Current method (baseline)
`replay_step` → `data_get_ohlcv(count=1)` + `data_get_pine_tables` (parallel) → reasoning → (every
~8 bars or on a trigger) persist to the M15 log / pattern ledger / thesis ledger.

- EXTERNAL_CALLS_PER_BAR: ~2.25 (2 round trips + amortized verification/write overhead)
- BARS_PER_LONG_INVOCATION: ~90-130 (observed)
- EXPECTED_INVOCATIONS_TO_COMPLETE_Q4: ~65-90
- IMPLEMENTATION_COMPLEXITY: none (already exists)
- INTEGRITY_RISK: none (already proven — see the bars 288-378 audit)
- APPRENTICESHIP_INFORMATION_LOSS: none

### Option B — Atomic single-bar step
Add one new composite MCP tool (e.g. `replay_step_full`) to the existing `tradingview-mcp` server
that, in one external call, does: advance exactly one bar, then internally call the existing
`data_get_ohlcv(count=1)` and `data_get_pine_tables` logic server-side, and return one bundled
response (OHLCV + `AI_TRADER_CONTEXT_V1` table + optionally the ICT labels) for the bar just
revealed. No new information is exposed that isn't already exposed today — this only consolidates
message envelopes.

- EXTERNAL_CALLS_PER_BAR: ~1 (down from ~2)
- BARS_PER_LONG_INVOCATION: ~150-220 (estimated ~1.5-2x current, order-of-magnitude)
- EXPECTED_INVOCATIONS_TO_COMPLETE_Q4: ~40-55
- IMPLEMENTATION_COMPLEXITY: LOW — additive endpoint in the existing MCP server, composes two
  already-working internal calls; no change to replay semantics
- INTEGRITY_RISK: LOW — identical causal exposure to Option A, just packaged together
- APPRENTICESHIP_INFORMATION_LOSS: NONE — every bar still individually reaches the reasoning layer

### Option C — Sealed internal sequential runner
Multiple bars stepped server-side in one external call; the LLM decision layer is only re-entered
once each preceding bar's "decision" has been frozen internally.

**Rejected as primary.** The core problem: in this system, "decisions" (thesis updates, P007
classifications, NO_TRADE judgments) are not made by server-side code — they are made by the
model in this conversation. For the server to process bar N+1 "after bar N's decision is frozen"
without exposing bar N+1's raw data to the outer reasoning loop, it would need either (a) no
market-reading judgment at all for the skipped bars — impossible, since that's the entire
apprenticeship — or (b) a second, hidden LLM call making those decisions in its place. Option (b)
may be causally sound (still strictly sequential, no batch reveal) but it substitutes a different
reasoning process for the one this whole exercise exists to develop and evidence (the pattern
ledger, trigger classifications, and thesis snapshots are records of *this* apprenticeship's
judgment, not a black-box proxy's). Rejected primarily on **apprenticeship-quality** grounds, not
integrity grounds — this matches the request's own instruction to reject if "the LLM/model
ultimately sees the future batch" only in spirit: the deeper issue is that the wrong LLM would be
doing the seeing.

### Option D — Causal event-gated replay
Deterministic, non-adaptive code steps bars server-side and maintains simple derived state (price
vs. a pre-registered level, volume vs. a rolling threshold, session boundary, EMA-vs-price flip).
It returns to the reasoning layer only when a pre-registered event fires; skipped stretches are
summarized (e.g. "42 bars, session X→Y, range A-B, volume stayed under threshold, no event") rather
than shown bar-by-bar.

- EXTERNAL_CALLS_PER_BAR (routine stretches): near 0 (batched into the gate's summary)
- BARS_PER_LONG_INVOCATION: potentially 1,000+ for quiet stretches
- EXPECTED_INVOCATIONS_TO_COMPLETE_Q4: as low as ~10-15 if gates are well-tuned
- IMPLEMENTATION_COMPLEXITY: MEDIUM — needs a stateful gate (rolling volume percentile, level
  registry synced with the thesis ledger, session calendar) living either in the MCP server or a
  wrapper script
- INTEGRITY_RISK: MEDIUM — safe **only** if gate criteria are fixed *before* being applied to any
  unseen bar and never retuned adaptively during the run (retuning based on how many/few events
  are firing would itself be a form of using future-bar information to shape future-bar exposure).
  This document does not propose specific thresholds, since even proposing them now would risk
  being implicitly informed by bars already seen in a way that isn't disclosed and auditable.
- APPRENTICESHIP_INFORMATION_LOSS: **real and disclosed**. A pure per-bar-threshold gate can miss:
  gradual momentum/slow acceptance (a drift that never trips a single-bar threshold but is
  cumulatively meaningful), regime-transition recognition (the whole point of Q4 per the original
  mandate), location awareness during quiet consolidation, and session-development texture. This
  is the central risk of Option D used alone.

### Option E — Hybrid (recommended; see §6)
Option B's atomic tool as the stepping primitive (every bar still reaches the reasoning layer in
full — no server-side filtering, no hidden LLM), combined with the **compact-vs-full logging
discipline already demonstrated live in this session** (bars 191-378): every bar is read and
reasoned about individually and causally, but only bars with a state change, a pre-registered
trigger, or a periodic ~8-bar cadence checkpoint receive full narrative persistence; routine bars
get a one-line compact record (`BAR/TIMESTAMP/STATE_CHANGE=NONE/DECISION=NO_TRADE/INTEGRITY=OK`).
The acceleration is in *how much is written and reasoned about per bar*, not in *whether every bar
is seen* — this is the key difference from C/D.

- EXTERNAL_CALLS_PER_BAR: ~1 (via Option B's atomic tool)
- BARS_PER_LONG_INVOCATION: ~250-400 (order-of-magnitude estimate: fewer round trips per bar, plus
  materially less reasoning/writing token cost for the majority-routine bars, which this session's
  own data suggests are roughly 60-70% of bars — e.g. the 191-198, 279-286, 295-302 stretches had
  zero material state changes)
- EXPECTED_INVOCATIONS_TO_COMPLETE_Q4: ~20-35
- IMPLEMENTATION_COMPLEXITY: LOW-MEDIUM — Option B's tool, plus formalizing (not automating) the
  compact/full logging split already in use
- INTEGRITY_RISK: LOW — identical causal exposure to Option A/B; the compact-logging choice is a
  reasoning-layer (model) decision made *after* seeing the bar, never a pre-filter that hides it
- APPRENTICESHIP_INFORMATION_LOSS: NONE in terms of exposure (every bar reached the model); a
  **disclosed, bounded** risk that compact one-liners under-capture texture for bars later found
  retrospectively interesting — mitigated by the fixed ~8-bar full-snapshot cadence already in
  place, which guarantees no stretch longer than ~2 hours goes without a full market read

### Option F — Other
Not proposed; A-E span the reasonable design space for this tool architecture.

## 3. Apprenticeship-quality assessment matrix

| Risk | A | B | C | D | E |
|---|---|---|---|---|---|
| Gradual momentum information lost | No | No | Possible | **Yes (disclosed)** | No |
| Slow acceptance missed | No | No | Possible | **Yes (disclosed)** | No |
| Regime-transition recognition impaired | No | No | Possible | **Yes (disclosed)** | No |
| Location awareness reduced | No | No | Possible | Partial | No |
| Session-development texture lost | No | No | Possible | Partial | No |
| NO_TRADE judgment delegated away from this apprenticeship | No | No | **Yes** | No (judgment stays with model, only exposure is filtered) | No |
| New-pattern discovery capacity reduced | No | No | Possible | Partial | No |

## 4. Non-negotiable strict events — how each option satisfies §9

Trade entry, P007 preclassification, MGMT-004 eligibility/trigger, active-thesis trigger
resolution, new-pattern freeze, a genuine-setup NO_TRADE, and regime-transition declarations must
remain fully prospective under every option:

- **A, B, E**: trivially satisfied — every bar reaches the model before any of these can be
  declared, exactly as bars 1-378 already demonstrate.
- **D**: satisfied *only if* every one of these seven event types is included in the gate's
  trigger list (i.e. the gate can never suppress a bar that would otherwise produce one of them) —
  this is achievable in principle but adds real design/verification burden and is a plausible
  source of a subtle gate-definition bug that silently drops a genuine trigger.
- **C**: not reliably satisfiable without delegating the judgment itself (see §2 above) — rejected.

## 5. Required no-lookahead test plan (design only — not implemented)

For whichever architecture is eventually authorized, before any real Q4 bar is processed under it:

1. **FUTURE_BAR_INACCESSIBLE** — assert the tool/wrapper's return value for bar N contains no
   field derived from bar N+1 or later (schema/field-level check against a held-out synthetic
   fixture).
2. **CURRENT_POINTER_ONLY** — assert `replay_status`-equivalent pointer advances by exactly one
   bar per invocation of the new stepping primitive, never more.
3. **NO_FUTURE_OHLC** — replay a known fixture sequence; assert OHLC values returned at step N
   exactly match the fixture's bar N, never bar N+k.
4. **NO_FUTURE_INDICATORS** — same, for `AI_TRADER_CONTEXT_V1`/ICT values.
5. **NO_FUTURE_PINE_STATE** — same, for any Pine-drawn state (labels/tables/lines).
6. **DECISION_BEFORE_POINTER_ADVANCE** — assert the tool cannot be called twice before a
   round-trip response is consumed (prevents accidental double-step/skip).
7. **CRASH_RESTART_NO_SKIP** — kill the process mid-sequence; assert resume continues from the
   last *persisted* bar, not the last *requested* bar (guards against a bar being silently marked
   consumed without its evidence being written).
8. **CRASH_RESTART_NO_DUPLICATE** — same scenario; assert the resumed bar is not re-emitted if its
   evidence was already durably persisted.
9. **TIMESTAMP_MONOTONICITY** — assert every consecutive pair of bar timestamps is either exactly
   +900s or matches a logged, verified gap type (daily rollover / weekend / holiday).
10. **SOURCE_GAP_HANDLING** — inject a fixture gap; assert it is classified and logged before the
    next bar is exposed, exactly as GAP-151..154 were handled live.
11. **TRADE_CONTRACT_FROZEN_BEFORE_NEXT_BAR** — if a trade is opened, assert every required §8
    contract field is present and immutable before the next bar's data is requested.
12. **P007_PRECLASSIFIED_BEFORE_RESOLUTION** — assert a P007 registration event is always written
    before the bar that resolves it is exposed (exactly the pattern demonstrated for Q4-P007-001/
    002/003).
13. **MGMT004_CAUSAL_TRIGGER** — assert MGMT-004's trigger evaluation never references a bar later
    than the one that supposedly triggered it.
14. **NO_TRADE_CAUSALITY** — assert a NO_TRADE decision's stated rationale references only
    already-revealed bars.

**Adversarial tests**: a fixture engineered to tempt lookahead — e.g. a bar sequence where the
*correct-looking* trade decision at bar N depends on knowing bar N+3 reverses; assert the
architecture still produces the causally-blind (and, by fixture design, "wrong in hindsight")
decision at bar N. Also: a fixture with a deliberately malformed/missing gap boundary, to assert
the gap-handling path fails closed (flags an integrity incident) rather than silently continuing.

## 6. Recommendation

**RECOMMENDED_ARCHITECTURE = E (Hybrid: Option B's atomic tool + the compact/full logging
discipline already in live use).**

Priority order applied: (1) causal integrity — A, B, and E are causally identical, all proven live
across 378 bars; (2) apprenticeship quality — E preserves full model exposure to every bar, unlike
C (judgment delegation) and D (disclosed information loss); (3) throughput — E gives a real,
order-of-magnitude improvement (~2-4x fewer invocations) without the larger but riskier gains of D;
(4) implementation simplicity — E is a small additive tool plus formalizing an already-proven
practice, not a new stateful subsystem.

Option D is not rejected outright — it could be revisited later, explicitly, for narrowly-scoped
stretches (e.g. only the historically-thinnest sessions) with disclosed information-loss accepted
by CEO decision, and only after E's ceiling is reached. It is not the default.

```
CAUSAL_REPLAY_ACCELERATOR_FEASIBLE = YES
RECOMMENDED_ARCHITECTURE = E (Hybrid)
EXPECTED_SPEEDUP = ~2-4x fewer invocations (order-of-magnitude estimate, not measured)
EXPECTED_Q4_COMPLETION_INVOCATIONS = ~20-35 (down from ~65-90 under Option A)
STRICT_CAUSALITY_PRESERVED_BY_DESIGN = YES
APPRENTICESHIP_QUALITY_PRESERVED = YES
```

## 7. Implementation ownership (if and when authorized — not authorized by this document)

```
OWNING_COMPONENT     = tradingview-mcp server (this repo) — the composite `replay_step_full`
                       tool is additive to the existing MCP tool set
LIKELY_FILES_MODULES = the MCP server's replay/step handler and its OHLCV/study-value read paths
                       (wherever `replay_step`, `data_get_ohlcv`, and `data_get_pine_tables` are
                       currently implemented) — new composite endpoint only, no changes to existing
                       tool behavior
IMPLEMENTING_DEPARTMENT = TradingView MCP tooling (this repo's own maintainers) — not an AI Trader/
                       Alpha/VE-department concern, since it touches only the replay tool surface,
                       not any strategy, validation, or execution logic
REQUIRED_TESTS       = the 14-item no-lookahead suite in §5, plus standard MCP tool contract tests
                       (schema validation, error handling on replay-not-started, etc.)
RED_TEAM_REVIEW_REQUIRED = YES — any change to the causal information-exposure surface of a
                       replay tool used for prospective evidence generation warrants an
                       independent adversarial check, consistent with this lab's standing practice
                       for measurement-integrity-adjacent code (see `red-team-conformance-gate`)
VE_REVIEW_REQUIRED   = NO — this tool has no interaction with ve_brain/ve_tower/RANGE/strategy
                       validation surfaces; it is a pure data-plane replay utility
```

## 8. Explicit non-actions

This document does not implement anything. `NEXT_UNSEEN_BAR = 379` remains unconsumed. No MCP
server code was modified. No accelerator was run. Resuming Q4 replay — under Option A (unchanged)
or under a newly authorized architecture — requires a separate, explicit instruction.
