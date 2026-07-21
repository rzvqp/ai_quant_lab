# PORTFOLIO_ARCHITECT_PHASE2_DESIGN.md — Portfolio Architect Phase 2 Policy Design (Flow B roadmap step 2/6)

**Status: DESIGN ONLY. No code written, no code modified, nothing committed to `ai_trader/`.** Produced
per explicit CEO authorization following the ACCEPTED verdict on Portfolio Architect Phase 1 (PASSTHROUGH
scaffold, commits `bf41d5e`/`c1b0fd2`, CLOSED). This document defines a candidate first real Portfolio
Architect decision policy in full, deterministic detail — sufficient to implement — while explicitly
flagging every choice as a **recommendation awaiting CEO authorization**, not a decision already taken.
Nothing here changes runtime behavior; `ArchitectMode.PASSTHROUGH` remains the only mode that exists in
code. This document answers the CEO's 15 mandatory design questions, the mandatory policy separation, and
resolves — with explicit recommendations, not silent assumptions — the 7 open decisions carried forward
from `PORTFOLIO_ARCHITECT_DESIGN.md` §14.

---

## 1. Scope

Define ONE candidate policy — **portfolio-level re-ranking by strategy-concentration, using rank
reassignment only** — in enough detail to be implementable, and resolve every open question required to
implement it, each as an explicit, individually-approvable recommendation. This document does not choose
between fundamentally different policy families (e.g. correlation-matrix-based vs. strategy-share-based)
without disclosing the alternatives it rejected and why (§9).

## 2. Non-goals (explicitly out of scope for Phase 2)

Per the CEO's own governance restrictions: no implementation, no new `ArchitectMode`, no production
activation, no default-behavior change, no modification of Risk Manager/Strategy Health/Signal Engine/
Scoring Engine/Shadow Evidence, no Flow A contact, no strategy-selection optimization, no learned weights,
no correlation thresholds without their own authorization. Also explicitly out of scope for the POLICY
ITSELF (not just this design step): capital allocation, position sizing, exposure budgeting as a hard
limit, opportunity exclusion, candidate-count capping, capacity reservation, multi-symbol diversification
(deferred, §9.4), and any statistically-estimated pairwise correlation (deferred, §9.2/§9.8).

---

## 3. Mandatory design questions — explicit answers

**Q1. What exact problem does Phase 2 solve?**
Among a bar's already-eligible (Strategy Health), already-scored (Scoring Engine) opportunities, the
Scoring Engine's own within-bar `rank` reflects opportunity QUALITY only — it has no notion of portfolio-
level CONTEXT (e.g. "this strategy already accounts for a disproportionate share of recent real
allocations"). When two or more opportunities compete for the same scarce resource (chiefly the shared
per-symbol slot, `LIMIT_MAX_PER_SYMBOL=1`, the Root-Cause Report's own Mechanism A), Risk Manager
currently has no portfolio-level signal to prefer a more diversified pick — it purely honors the
Scoring-Engine rank. Phase 2 solves this narrowly: adjust the PRIORITY ORDER (never the accept/reject
outcome) opportunities are handed to Risk Manager in, biased toward reducing single-strategy dominance of
scarce shared resources — nothing else.

**Q2. What inputs may Portfolio Architect use?**
- `risk_opportunities: Sequence[OpportunityScore]` — the already-eligible, already-scored set (unchanged
  from Phase 1's own input contract).
- `portfolio_state: PortfolioState` — read-only, for CONTEXT only (never to compute an ALLOW/DENY-
  equivalent verdict, §3 Q7).
- `as_of: int` — for point-in-time correctness.
- **NEW for Phase 2**: a read-only, point-in-time-filtered view of Shadow Evidence's own accumulated
  `trade_legs`/`positions` (the same evidence source Strategy Health already reads, per its own module
  docstring's own precedent of Shadow as the shared, unconditional evidence source) — restricted to
  records strictly before `as_of`. This is the proposed sole source of the "recent strategy allocation
  share" signal (§9.8 below).
- `PortfolioArchitectConfig` — policy parameters (window length, down-rank strength) — none of the
  concrete values are fixed by this document (§9.6).

**Q3. What information is explicitly forbidden?**
Any data at or after `as_of` (no look-ahead, ever); `RiskDecisionBatch`/`RiskDecision` internals from any
bar (reading Risk Manager's own past decisions to infer capacity would duplicate its authority, §3 Q7);
Strategy Health's internal scoring numbers (percentile ranks, shrinkage weights) — only the already-
filtered eligible SET may be consumed, never re-derived or second-guessed; Strategy Manager's contract/
maturity/lifecycle data (no new cross-reference); Decision Intelligence v1/v2 outputs (remain
disconnected, per every prior restriction in this roadmap step).

**Q4. What decisions may it make?**
Exactly one: the relative PRIORITY ORDER (expressed as a `rank` reassignment on cloned
`OpportunityScore` objects, mirroring `scoring_engine/ranker.py`'s own `dataclasses.replace` technique)
among the opportunities it receives. Nothing else.

**Q5. What decisions remain exclusively Risk Manager's?**
All of them, unconditionally: ALLOW/DENY, every `portfolio_limits` field (`max_positions`,
`max_per_symbol`, `max_correlated`, `max_exposure_pct`, `max_leverage`, `max_overnight_exposure_pct`),
loss/drawdown guards, cooldowns, pre-trade filters, all sizing methods, constraint building. Phase 2's
policy touches none of these and reads none of Risk Manager's own config to decide anything.

**Q6. May it: exclude / reorder / cap / prioritize / size / reserve?**

| Capability | Recommended for Phase 2 | Rationale |
|---|---|---|
| Exclude opportunities | **NO** | Would duplicate Risk Manager's own DENY authority outside its audited gate chain — an excluded opportunity would never even reach `risk_manager.evaluate()`, so no `RiskEventRecord`/`AppliedRule` audit trail would ever be created for it, breaking this project's own established attribution convention (`test_shared_slot_denial_is_attributed_to_the_real_denied_strategy_not_the_slot_holder`'s own precedent). |
| Reorder opportunities | **YES** | The one lever that changes nothing about WHETHER an opportunity is accepted, only the ORDER Risk Manager considers them in — Risk Manager's own greedy, rank-ordered gate chain (`risk_manager/engine.py:264`) already re-sorts by `rank` regardless of list order, so this is the natural, minimally-invasive integration point. |
| Cap candidate count | **NO** | Structurally equivalent to exclusion for opportunities beyond the cap — same objection as above. |
| Assign portfolio-level priority | **YES** | Synonymous with "reorder" here — `rank` IS the priority signal Risk Manager consumes. |
| Suggest sizing | **NO** | Sizing is exclusively Risk Manager's frozen `sizing.py`; an unconsumed "suggestion" is either dead code or an invitation to future scope creep into Risk Manager's own domain. |
| Reserve capacity | **NO** | Requires a new stateful mechanism (holding back a slot across bars) that doesn't exist today and would likely require its own Risk Manager change — explicitly a later, separately-authorized escalation, not "the first real policy." |

**Q7. How are shared-slot conflicts handled without duplicating Risk Manager logic?**
Portfolio Architect never reads, counts, or reasons about any `RiskConfig.portfolio_limits` value (not
`max_per_symbol`, not `max_positions`, nothing). It computes a portfolio-level PREFERENCE ordering among
opportunities, entirely oblivious to how much capacity actually exists — Risk Manager remains the sole
party that knows and enforces "how many can actually be allowed," using whatever rank order it's handed,
exactly as it does today for the Scoring-Engine-only rank. This is the load-bearing non-duplication
guarantee: Portfolio Architect answers "who should go first if there's a race," never "is there a race"
or "who wins the race."

**Q8. How is correlation represented?**
**Recommended: strategy identity only (a rolling recent-allocation-share metric per `strategy_id`), NOT
a statistical pairwise correlation.** Full analysis and alternatives in §9.8 below — this sidesteps two
real problems with every richer alternative: `RiskConfig.correlation_groups` is empty by default across
this entire repository (confirmed by this roadmap step's own research), so a static-group-based policy
would be a functional no-op without new out-of-band operator configuration; and a return-history/factor-
based empirical correlation estimator is new, non-trivial statistical machinery this document declines to
propose building and validating as part of "the first real policy" (§9.8, Option B).

**Q9. What happens when correlation or exposure data is missing?**
Fail toward neutral, not toward penalty: a strategy with no prior Shadow-observed allocation history
(most plausibly a genuinely `NEW` strategy under Strategy Health's own classification) receives no boost
and no down-rank — it retains its Scoring-Engine-assigned rank position relative to opportunities with
data, and ties against another zero-history opportunity fall through to Q10's tie-break. This mirrors
Strategy Health's own "no evidence → neutral (WATCHLIST-equivalent)" convention (`classifier.py:19-21`),
reused here rather than reinvented.

**Q10. Deterministic tie-break rules?**
When the proposed strategy-share signal is EQUAL for two or more opportunities (including the "both zero
history" case), tie-break falls back to the Scoring Engine's own original `rank` field — never a new,
independently-invented rule. This mirrors `scoring_engine/ranker.py`'s own tie-break chain
(`total_score → historical_confidence → signal_strength → strategy_id`) and Decision Intelligence's own
`ranking.py` precedent of always terminating in a deterministic, non-arbitrary total order.

**Q11. Behavior in named scenarios:**
- *Only one opportunity exists*: no-op — a single opportunity's relative order is meaningless; its
  `rank` must be unchanged (already proven as a Phase 1 invariant, re-confirmed for Phase 2).
- *All opportunities highly correlated (concretely: all from strategies with a high recent-allocation
  share)*: all down-ranked by the same rule relative to a hypothetical low-share opportunity — but since
  Risk Manager still independently enforces `LIMIT_MAX_PER_SYMBOL`/`LIMIT_MAX_CORRELATED`, re-ranking can
  only change WHICH ONE is considered first, never how many ultimately get allowed. Risk Manager's own
  limits remain the sole enforcement of "how many" (Q7).
- *Portfolio state is empty*: the proposed signal is Shadow-Evidence-history-based, not open-position-
  based, so an empty `portfolio_state` does not remove the signal — but if Shadow history is ALSO empty
  (a fresh run), every opportunity is neutral (Q9) and the policy is effectively PASSTHROUGH for that
  bar.
- *Portfolio state is at capacity*: Portfolio Architect does not know what "capacity" means (Q7) — it
  re-ranks identically regardless; Risk Manager denies whatever doesn't fit, exactly as it does today.
- *Strategy Health returns no eligible strategies*: `risk_opportunities` is already empty — Portfolio
  Architect must return empty (unchanged Phase 1 invariant).
- *Risk Manager later rejects Portfolio Architect's own top-ranked pick*: expected and correct — re-
  ranking is a PREFERENCE, never a guarantee. Risk Manager's own gate chain (spread/liquidity/score
  floor/limits/guards/cooldowns/sizing) can still deny the top-ranked opportunity for entirely unrelated
  reasons, exactly as it already can for the Scoring-Engine-only rank today. No special-casing is needed.

**Q12. What diagnostics and reason codes are required?**
Per re-ranked opportunity: `original_rank`, `new_rank`, a `reason_code` (proposed set:
`NO_CHANGE`, `INSUFFICIENT_EVIDENCE_NEUTRAL`, `STRATEGY_CONCENTRATION_DOWNRANK`), and the raw
recent-allocation-share value that drove the decision — mirroring Risk Manager's own `AppliedRule`/
`DeniedReason` audit-trail convention (rule/passed/detail) and Decision Intelligence's own `explanation`
field precedent. Diagnostics remain strictly read-only/non-influencing, per the Phase 1 invariant already
proven (`ArchitectDiagnostics` is never read by the harness to make a decision) — extended, not relaxed.

**Q13. What invariants must always hold?**
- Output is always a PERMUTATION of the exact same opportunity objects present in the input — never
  fabricated, never dropped (Phase 2 proposes no exclusion capability, §3 Q6).
- Only `rank` may differ between an input and its corresponding output opportunity — every other field
  (`strategy_id`, `symbol`, `signal_id`, `score_id`, `total_score`, `component_scores`, `recommendation`,
  etc.) must be byte-identical to what Scoring Engine produced.
- A strategy/opportunity with no prior Shadow-observed history is never penalized relative to one with
  data (Q9).
- No look-ahead: every input to the concentration computation is strictly prior to `as_of`.
- Determinism: identical inputs (including identical Shadow Evidence history up to `as_of`) always
  produce identical re-ranking output.
- Shadow Evidence's own `observe()` tap remains entirely unaffected and keeps its Phase-1-accepted
  placement (before Portfolio Architect) — not reopened by this design.
- **Aggregate capacity neutrality** (the single most important invariant): across a full run, the TOTAL
  number of Risk-Manager ALLOWs must be identical whether Portfolio Architect re-ranks or passes through
  — only WHICH strategy fills a given shared slot may differ, never HOW MANY slots get filled. This is
  what structurally separates "prioritization" from an exclusion/sizing policy in Q6's sense.

**Q14. Negative controls (each a required test, §5):**
- **Not recreating Scoring Engine**: `total_score`/`component_scores`/`recommendation` are byte-identical
  between input and output for every opportunity — Phase 2 computes no new quality/opportunity score.
- **Not recreating Strategy Health**: the SET of `strategy_id`s present is identical between input and
  output (only relative order may change) — Phase 2 cannot promote or demote eligibility.
- **Not overriding Risk Manager**: aggregate ALLOW count and the DENY-reason-type distribution across a
  full run are identical between POLICY mode and PASSTHROUGH — only strategy identity within a shared
  slot may differ (Q13's aggregate-capacity-neutrality invariant, directly tested).
- **Not introducing hidden optimization**: the policy is a pure, stateless, deterministic function of
  disclosed inputs only — no ML, no numerical solver, no fitted/learned weight; every re-ranking decision
  traces to an explicit, human-readable `reason_code` (Q12).

**Q15. Tests required before implementation acceptance** (to be written AT implementation time — none
exist yet, this is a specification, not a test plan already executed):
1. PASSTHROUGH regression: all of Phase 1's own 16 tests remain green, unmodified.
2. Aggregate capacity neutrality (Q13): total ALLOW count identical, POLICY vs. PASSTHROUGH, over a full
   multi-bar run.
3. Structural permutation proof: output is exactly a re-ordering of input objects; only `rank` differs.
4. Missing-data-neutral: a strategy with zero Shadow history is never down-ranked relative to one with
   data (Q9).
5. Deterministic tie-break: two opportunities with equal concentration share fall back to Scoring-Engine
   rank order (Q10).
6. No-look-ahead: the standard point-in-time proof (two runs identical up to `as_of`, diverging only
   after, must produce identical Portfolio Architect output at `as_of`).
7. Single-opportunity no-op (Q11).
8. Empty-eligible-set no-op (Q11, re-confirm Phase 1's own invariant).
9. Risk-Manager-rejects-the-top-pick does not misbehave (Q11) — full pipeline continues normally.
10. Diagnostics are deterministic and complete for every re-ranked opportunity (Q12).
11. All four negative controls (Q14), each its own dedicated test.
12. Full regression: `ai_trader/strategy_health/` (72), `ai_trader/risk_manager/` +
    `ai_trader/scoring_engine/` + `ai_trader/signal_engine/` (589), `test_shadow_disabled_parity.py`
    (28, including the 43-strategy parity run), `test_health_eligible_ids.py` (8), the small harness
    suite (9) — all must remain green.

---

## 4. Mandatory policy separation — responsibility matrix

| Layer | Owns | Confirmed unchanged by this design |
|---|---|---|
| **A. Eligibility** | Strategy Health (`shadow_gate.py`) | Portfolio Architect only ever consumes the already-`health_eligible_ids`-filtered set; cannot restore an excluded strategy (Phase 1's own proven invariant, unchanged) |
| **B. Opportunity quality/rank (pre-portfolio)** | Signal Engine + Scoring Engine | `total_score`/`component_scores`/`recommendation` are read-only inputs to Phase 2's policy, never recomputed (Q14 negative control) |
| **C. Portfolio-level prioritization** | **Proposed: Portfolio Architect** | The ONLY new authority this design proposes — expressed strictly as a `rank` reassignment, nothing else (Q4/Q6) |
| **D. Risk approval, sizing, limits, final admission** | Risk Manager | Untouched; Phase 2's policy reads none of Risk Manager's own config and computes no ALLOW/DENY-equivalent verdict of its own (Q5/Q7) |

No responsibility is duplicated: (A) is consumed, never re-derived; (B) is read-only, never recomputed;
(D) is never reached into. (C) is the sole new authority, and it is scoped narrowly enough (ordering only,
provably capacity-neutral in aggregate, Q13) that it cannot substitute for (D)'s own authority even if the
policy were buggy — a wrong re-rank produces a wrong PRIORITY, never a wrong ALLOW/DENY.

---

## 5. Proposed policy — deterministic decision procedure

**Recommended v1 policy name: `STRATEGY_CONCENTRATION_REORDER`** (a new `ArchitectMode` value, NOT added
to code by this design — this is a specification for a future, separately-authorized implementation).

```
for each opportunity o in risk_opportunities (this bar, this symbol):
    share(o) = recent_allocation_share(o.strategy_id, trade_legs, as_of, config.window)
    # recent_allocation_share: count of this strategy's own Shadow-observed real-eligible allocations
    # (or shadow positions, §9.8) within [as_of - config.window, as_of), divided by the total count of
    # ALL eligible strategies' allocations in the same window. 0.0 if the strategy has zero history in
    # the window (Q9 -- neutral, not zero-is-worst).

priority_key(o) = (
    -1 if share(o) is UNDEFINED (no history) else share(o),   # neutral strategies sort with the pack
    o.rank,                                                    # deterministic tie-break, Q10
)

new_order = sorted(risk_opportunities, key=priority_key)       # ascending share = higher priority
output = [dataclasses.replace(o, rank=i + 1) for i, o in enumerate(new_order)]
```

This is intentionally the simplest possible re-ranking rule that satisfies every invariant in §3 Q13:
pure, deterministic, missing-data-neutral, tie-break-safe, and — because it only ever reorders opportunities
that were ALREADY going to be handed to Risk Manager — provably capacity-neutral in aggregate (Q13's last
invariant; Risk Manager still evaluates every opportunity in the set, just in a different order).

**Reason codes** (per opportunity, in `ArchitectDiagnostics`): `NO_CHANGE` (share tied with original
rank position, or only one opportunity), `INSUFFICIENT_EVIDENCE_NEUTRAL` (this or a competing opportunity
had no Shadow history), `STRATEGY_CONCENTRATION_DOWNRANK` (moved later due to a higher recent-allocation
share than a competitor).

---

## 6. Lifecycle placement, input/output contract

Unchanged from Phase 1 (§4/§6 of `PORTFOLIO_ARCHITECT_DESIGN.md`, ACCEPTED, not reopened): after Signal
Engine, after Scoring Engine, after Shadow Evidence has observed the full score batch, after Strategy
Health's `health_eligible_ids` filter, before `risk_manager.evaluate()`. Input/output contract also
unchanged in SHAPE (`Sequence[OpportunityScore] → PortfolioArchitectResult`); Phase 2 only proposes a
new, additive `config.mode = STRATEGY_CONCENTRATION_REORDER` value and a `trade_legs`/`as_of`-derived
concentration input alongside the existing `opportunities`/`portfolio_state`/`as_of`/`config` parameters.

---

## 7. Interaction with Risk Manager, Strategy Health, Shadow Evidence

- **Risk Manager**: receives the re-ranked sequence in place of today's pass-through sequence; its own
  gate chain, config, and ALLOW/DENY/sizing authority are entirely unaware anything upstream changed
  (Q5/Q7). No Risk Manager code is read or modified by the policy's own logic beyond consuming its
  already-public `PortfolioState` type for context.
- **Strategy Health**: Portfolio Architect's policy input (`risk_opportunities`) is exactly Strategy
  Health's own output — Phase 2 adds no new coupling and cannot override an exclusion (Q14 negative
  control).
- **Shadow Evidence**: becomes, for the first time, a SECOND consumer of `trade_legs` alongside Strategy
  Health's `shadow_gate.py` — both read-only, both restricted to point-in-time-safe history, neither
  writes to or gates the other. Shadow's own `observe()` tap remains entirely unaware Portfolio Architect
  or its policy exist, exactly as today.

---

## 8. Failure behavior, missing-data behavior

Covered in full under Q9/Q11 above. Summary: any missing or degraded input (no Shadow history for a
strategy, an empty `portfolio_state`, an empty opportunity set) degrades toward NEUTRAL/PASSTHROUGH
behavior for the affected opportunity(ies), never toward exclusion or an arbitrary penalty. If the
concentration computation itself raises an unexpected exception, the recommended (not yet implemented)
behavior mirrors Shadow Evidence's own established defense-in-depth convention (`harness.py`'s own
outer `try/except` around `shadow_engine.observe()`): catch, log, and fall back to `PASSTHROUGH` for that
bar rather than failing the run — Portfolio Architect must never be able to fail competitive execution,
matching the "Shadow must never affect competitive execution" precedent applied to this layer too.

---

## 9. Open policy decisions (carried forward from `PORTFOLIO_ARCHITECT_DESIGN.md` §14, resolved here with
explicit recommendations — NONE adopted without separate CEO authorization)

### 9.1 Which arbitration policy to authorize

- **Options**: (a) static correlation-group cap (original §7 option 2); (b) rolling max-share-of-
  allocations per strategy (original §7 option 3, refined into §5's concrete procedure above); (c) both
  combined; (d) a different mechanism entirely.
- **Advantages**: (a) reuses existing Risk Manager config surface; (b) requires no new operator
  configuration, functions immediately from Shadow's own unconditional evidence; (c) most complete
  coverage; (d) unbounded, unexplored.
- **Failure modes**: (a) is a no-op given `correlation_groups` is empty by default across this repo
  (confirmed by research); (b) only captures single-strategy dominance, not genuine cross-strategy
  correlation under different labels; (c) compounds both failure modes and doubles the surface to
  validate; (d) unknown risk.
- **Architectural impact**: (b) is the smallest, most self-contained addition — a single new read path
  into Shadow Evidence, no new Risk Manager config dependency.
- **Recommended option**: **(b)**, as specified in §5.
- **Confidence level**: Medium — the mechanism is simple and provably safe (Q13), but its real-world
  usefulness (does it actually reduce the dominance the Root-Cause Report measured?) is UNVALIDATED —
  no backtest/simulation of this policy's own effect has been run.
- **Evidence still missing**: an actual run comparing S1/S13/S39/S40/S46/S48's own shared-slot-denial
  rates under this policy vs. PASSTHROUGH — this document proposes the mechanism, not its measured
  effect.

### 9.2 Correlation source

- **Options**: (a) `RiskConfig.correlation_groups` (static, declared); (b) a new incremental Shadow-
  Evidence-sourced empirical estimator (return-series correlation or co-occurrence); (c) strategy
  identity only, no correlation model at all (§5/§9.8).
- **Advantages**: (a) zero new computation; (b) statistically grounded; (c) simplest, needs no config
  population, functions immediately.
- **Failure modes**: (a) empty by default, functional no-op without operator work; (b) new, unvalidated
  statistical machinery, real look-ahead risk if built carelessly, meaningful engineering effort; (c)
  does not capture genuine cross-strategy correlation (two differently-labeled strategies trading the
  same underlying edge would not be flagged).
- **Architectural impact**: (c) is smallest; (b) is largest (a genuinely new subsystem).
- **Recommended option**: **(c)** for Phase 2's first policy (matches §5/§9.8); explicitly flag (b) as a
  plausible richer Phase 3+ escalation, not decided here.
- **Confidence level**: Medium-high for (c) as a SAFE first step; low for whether (c) alone is
  SUFFICIENT to meaningfully address the Root-Cause Report's own findings (it targets Mechanism A's
  single-strategy-dominance framing more than genuine cross-strategy redundancy).
- **Evidence still missing**: whether S1/S13/S39/S40/S46/S48 (the six A-Candidates) are dominated by a
  small number of DISTINCT strategies or by few genuinely-correlated CLUSTERS — this distinguishes
  whether (c) alone would help meaningfully or whether (a)/(b) are actually required.

### 9.3 Down-ranking vs. exclusion

- **Options**: (a) down-rank (§5's proposal); (b) exclude entirely once a concentration cap is exceeded.
- **Advantages**: (a) Risk Manager retains final say, no new DENY path outside its own audit trail; (b)
  more forcefully enforces a hard cap.
- **Failure modes**: (a) a sufficiently bad ranking could still let an over-concentrated strategy win
  most races if no competing opportunity exists that bar; (b) recreates the exact audit-trail gap Q6
  already rejected exclusion for.
- **Architectural impact**: (a) stays within Portfolio Architect's own narrow (C)-layer authority
  (§4); (b) would reach into (D)'s territory.
- **Recommended option**: **(a)**, per Q6's own analysis — already resolved as part of this design's
  own §3/§5, not left open.
- **Confidence level**: High — this follows directly and structurally from the responsibility matrix
  (§4), not from empirical evidence.
- **Evidence still missing**: none for the architectural choice itself; empirical effectiveness is the
  same open question as §9.1.

### 9.4 Whether multi-symbol diversification is in scope for v1

- **Options**: (a) in scope; (b) deferred.
- **Advantages**: (a) more complete; (b) avoids exercising the architecturally-present but functionally
  untested multi-symbol code path this project's own research confirmed (every fixture/test/dataset in
  the repo uses `symbols=("XAUUSD",)` only).
- **Failure modes**: (a) would be validated against a code path with zero real precedent of actually
  running with more than one symbol — high risk of an undiscovered bug; (b) leaves the single-symbol
  case as the only proven one, which is also the only case this project's own data supports today.
- **Architectural impact**: §5's proposed procedure is symbol-agnostic in principle (the per-bar loop
  already calls Portfolio Architect once per symbol) but has never been exercised cross-symbol.
- **Recommended option**: **(b)**, deferred — matches the original design doc's own recommendation,
  unchanged.
- **Confidence level**: High.
- **Evidence still missing**: multi-symbol market data and fixtures do not exist in this repository
  today — this is a data/infrastructure gap, not a policy question.

### 9.5 Whether a diagnostics-only audit record is worth building in v1

- **Options**: (a) build it now (§5's `reason_code` proposal); (b) defer until a real policy exists to
  audit.
- **Advantages**: (a) auditability from day one, matches this project's own established convention
  (Risk Manager's `AppliedRule`, Decision Intelligence's `explanation`); (b) less to build/validate now.
- **Failure modes**: (a) small additional surface to test (Q15 item 10); (b) a policy running with zero
  audit trail would be very hard to debug or trust.
- **Architectural impact**: minor either way — `ArchitectDiagnostics` already exists from Phase 1.
- **Recommended option**: **(a)** — a real policy without diagnostics would itself violate this
  project's own repeated "no hidden decision-making" convention; the cost is genuinely small since the
  scaffold already exists.
- **Confidence level**: High.
- **Evidence still missing**: none.

### 9.6 Exact numeric thresholds (window length, down-rank strength)

- **Options**: any concrete value is a guess without calibration evidence — this document deliberately
  does NOT propose specific numbers.
- **Advantages / failure modes / architectural impact**: not applicable — no option is proposed.
- **Recommended option**: **none** — recommend a small, dedicated calibration pass (offline, over
  existing Shadow Evidence history from a completed run) BEFORE fixing any threshold, rather than
  inventing a number in a design document.
- **Confidence level**: N/A.
- **Evidence still missing**: everything — this is the least-ready-to-decide item in this document.

### 9.7 Whether Strategy Health's `MIN_EVIDENCE_TRADES=25` convention should be reused

- **Options**: (a) reuse `MIN_EVIDENCE_TRADES=25` verbatim as the minimum window sample size before
  trusting a strategy's own share signal; (b) define a separate, independently-justified threshold.
- **Advantages**: (a) reuses an already-CEO-reviewed, cross-referenced convention (this project's own
  `PROJECT_AUDIT.md` note on `MINTR=25` being reused a second time already, from Strategy Health's own
  build); (b) tailored to this specific statistic's own variance properties, which may differ from
  Strategy Health's own window-metrics use case.
- **Failure modes**: (a) may be too strict or too loose for a SHARE metric (a ratio) vs. Strategy
  Health's own WIN-RATE-style metrics; (b) risks inventing an unjustified number (same objection as
  §9.6).
- **Architectural impact**: negligible either way.
- **Recommended option**: **(a)**, provisionally — reuse `MIN_EVIDENCE_TRADES=25` as the starting point
  (a defensive floor below which a strategy's own share is treated as `UNDEFINED`/neutral, Q9), subject
  to revision once the §9.6 calibration pass has real numbers to inspect.
- **Confidence level**: Medium.
- **Evidence still missing**: whether 25 trades is enough for a stable SHARE estimate specifically
  (as opposed to Strategy Health's own win-rate/expectancy metrics, which is what `MINTR=25` was
  originally validated against).

### 9.8 Correlation representation — full analysis (referenced from Q8/§9.2)

- **Option A — strategy identity / rolling allocation share** (recommended, §5): simplest, needs no
  operator config, functions immediately from Shadow's own unconditional evidence, structurally cannot
  duplicate any frozen module's own logic. Limitation: does not detect two DIFFERENT strategies that are
  genuinely correlated (same underlying edge, different labels).
- **Option B — empirical pairwise correlation over Shadow trade legs** (deferred): more complete,
  directly reuses the CONCEPT (not the code — confirmed not reusable as-is) from
  `shadow_evidence/portfolio_research.py::correlation_matrix()`. Would require building a genuinely new,
  incremental, point-in-time-safe estimator — real engineering and validation effort, explicitly not
  proposed as part of "the first real policy."
- **Option C — static `correlation_groups`** (rejected for v1): cheapest in code, but a functional no-op
  given the config is empty by default across this repo; would require an operator to populate it before
  the policy could do anything, which is a governance/config-management step outside this design's own
  scope.
- **Recommendation**: Option A now; Option B as a disclosed, plausible future escalation once Option A's
  own real-world effect has been measured (§9.1's missing evidence).

---

## 10. Rollout plan (if/when authorized)

Mirrors Phase 1's own accepted convention: implement `STRATEGY_CONCENTRATION_REORDER` as a new
`ArchitectMode`, default `PortfolioArchitectConfig` remains `PASSTHROUGH` (no behavior change until a
caller explicitly opts in), full test suite from §3 Q15 written and green, aggregate-capacity-neutrality
(§3 Q13) proven before any wider validation, then a dedicated CEO review step (mirroring this roadmap's
own repeated pattern) before any production-facing use.

## 11. Rollback plan

Identical in shape to every prior harness touch's own rollback story: omitting
`portfolio_architect_config` (or leaving it `None`) reverts to today's exact behavior, already proven
byte-identical (Phase 1). No data migration, no schema change, no irreversible state — rollback is
simply not passing the new config value.

---

## 12. Recommendation to CEO

This document recommends, but does not request authorization for, `STRATEGY_CONCENTRATION_REORDER` (§5)
as the shape of Phase 2's first real policy — narrowly scoped to re-ranking only, provably incapable of
duplicating any frozen module's authority (§4/§14), with every remaining open numeric/scope decision
(§9.1, §9.2, §9.6, §9.7) explicitly flagged as unresolved and requiring either further calibration
evidence or its own separate authorization. Implementation itself — and adoption of this specific policy
over the alternatives disclosed in §9 — remains for CEO decision, per this step's own explicit
restriction.

---

## Governance confirmation

No code was written or modified. No `ArchitectMode` was added to `ai_trader/portfolio_architect/`. No
default behavior changed. Zero diff confirmed against Risk Manager, Strategy Health (frozen modules and
`shadow_gate.py`), Signal Engine, Scoring Engine, Shadow Evidence, and every Flow A artifact — verified
directly via `git status`/`git diff --stat` before this document's own commit.
