# Strategy Health Integration/Promotion Policy — Design Proposal (FINAL)

**Flow**: B (AI Trader Development). **Roadmap step**: 1 of 6 (Strategy Health → Portfolio Architect →
Learning/Research Feedback → Risk Integration → Execution Integration → MT5 Live). **Status of this
document**: **ACCEPTED WITH CONDITIONS** by CEO decision — general direction and all five stated
principles (Strategy Health stays a separate evaluation system; frozen modules stay frozen; Shadow
Evidence is the primary new-evidence source; Phase 6.9's ACTIVE-only lockout must not repeat; reuse
existing infrastructure where sufficient) confirmed. §§11–15 below are the requested architectural
clarifications, added before implementation begins, per explicit CEO instruction: "Nu implementa încă.
Nu modifica cod." Still no code written, no backtest run, no existing module modified — this remains a
design-only document. Follows the same design-first-then-implement pattern already used for every prior
subsystem in this project (Shadow Evidence Architecture Design, Context Memory Checkpoint 8).

---

## 1. What is actually unstarted, precisely

Two different things share the name "Strategy Health" in this project, and only one of them is
unstarted:

- **The Strategy Health System** (`ai_trader/strategy_health/`: `types.py`/`metrics.py`/`scoring.py`/
  `classifier.py`/`evaluator.py`) — **COMPLETE**, built at Wave D, frozen since. It computes, for any
  strategy at any point in time, a 0–100 Health Score and a classification into one of four bands.
- **Strategy Health integration/promotion policy** — **NOT STARTED**. Nothing today decides *what
  actually happens* to a strategy's participation in the live/competitive portfolio as a function of its
  Health state. This document proposes that policy.

This document does not touch or re-derive the scoring system itself — it is treated as a frozen,
correct, already-verified input.

## 2. The scoring system, restated precisely (grounding facts, not assumptions)

- Rolling windows: fixed 30-day-month multiples — 3m = 90 days, 6m = 180 days, 12m = 365 days (never
  calendar months).
- Per-window score: each of 8 metrics (`expectancy_r`, `profit_factor`, `net_r`, `win_rate`,
  `monthly_consistency`, `equity_stability`, `max_drawdown`, `max_losing_streak`) is percentile-ranked
  (0–100) against the cross-section of strategies with ≥1 trade in that window, shrunk toward 50 via
  Bühlmann credibility `n/(n+10)`, combined with PCA-derived weights (equal-weight fallback below 5
  strategies with evidence).
- Overall score: `12m×0.60 + 6m×0.25 + 3m×0.15` (missing windows' weight redistributed proportionally).
- Bands: **ACTIVE ≥ 65**, **WATCHLIST 45–65**, **PROBATION 25–45**, **DISABLED < 25**.
- Trend adjustment: a ±15-point 3m-vs-12m swing bumps the tier up or down by one (capped at
  ACTIVE/DISABLED).
- **No trades in any window → `overall_score = None` → automatically WATCHLIST, never penalized.** This
  is the existing, safe cold-start behavior.
- Current one-time static evaluation (2026-07-13, whole-lifetime, competitive-trade evidence): 2 ACTIVE
  (S40, S46), 34 WATCHLIST, 7 PROBATION (S1, S5, S13, S14, S22, S28, S30), **0 DISABLED**.

## 3. Why the one prior integration attempt failed — the central fact this design must not repeat

Phase 6.9 (`PHASE_6_9_ROLLING_HEALTH_GATED_BACKTEST_REPORT.md`) already tried an integration policy:
monthly re-evaluation, **ACTIVE-only strategies allowed to generate new signals** (via
`ai_trader/simulation/harness.py`'s existing `strategy_id_filter`), everything else excluded. Result: a
**VALID NEGATIVE RESULT** — the ACTIVE roster was empty at all 32 post-bootstrap monthly checkpoints; the
portfolio traded only during the 12-month bootstrap (71 trades) then went completely silent for the
remaining ~2.6 years.

**Precise mechanism, two phases**:
1. Even at the single best checkpoint in the whole backtest (2023-12-16), only 4 of 43 strategies had
   *any* trade in their 12-month window (S46: 48, S39: 17, S1: 4, S25: 1) — none crossed the ACTIVE
   bar (≥65) even before shrinkage.
2. **Absorbing lockout**: once the bootstrap window's own trades aged out of the 365-day lookback
   (~2025-01-09), every one of the 43 strategies simultaneously fell to `overall_score = None` → the
   safe-default WATCHLIST state — but since only ACTIVE was permitted to open new trades, no new trades
   meant no new evidence meant no possible recovery, for the rest of the backtest.

Population context: median lifetime trades/strategy = 7 over 3.6 years; only 13/43 strategies ever reach
the `n=10` credibility floor; 14/43 never traded at all in the whole period. **This is not a Strategy
Health scoring defect — it is what happens when a binary, hard-cutoff eligibility policy is layered on
top of a strategy population whose own signal frequency and (per the separate, more recent
`CEO_STRATEGY_CONSTRAINT_ROOT_CAUSE_REPORT.md`) shared-single-XAUUSD-slot contention already produce
very few realized trades.**

**The direct connection to this session's own most recent finding, worth stating explicitly**: the
Root-Cause Study (committed `2650c3b`) found that all six current A-Candidate strategies are
PORTFOLIO-LIMITED — their realized (competitive) trade count is suppressed by the shared-slot rule and
the Scoring Engine's cross-strategy conflict penalty, not by an absence of underlying opportunity. Phase
6.9's evidence-starvation problem and the Root-Cause Study's constraint-diagnosis problem are **the same
underlying mechanism, observed independently, roughly two sessions apart**: competitive trade counts are
a scarce, shared, contested resource — not a fair per-strategy sample of each strategy's own quality.
Any Health-integration design that scores strategies **only** on competitive-trade evidence inherits this
same scarcity and is at meaningful risk of the same lockout failure mode, even under a softer policy than
Phase 6.9's.

Phase 6.9's own report (§14) already lists 8 candidate fixes, **none selected, none implemented**:
differentiated-risk WATCHLIST, hierarchical/Bayesian pooling, longer windows, minimum exploration
allocation, portfolio-level scoring, shadow-mode evidence accumulation, regime-conditioned evidence, and
"keep incumbents eligible until negative evidence accumulates." This design proposal draws directly on
several of these, now that Shadow Evidence (unavailable at Phase 6.9's own time) is complete.

## 4. Two separate decisions this policy must make

**Decision 1 — what evidence feeds the Health score used for live integration** (competitive trades,
Shadow Evidence trades, or both, labeled). **Decision 2 — what the Health state actually controls** in
the live portfolio (new-signal eligibility, risk sizing, ranking priority, or some combination). These
are independent axes; the options below are compared separately, then combined into one recommendation.

### 4.1 Decision 1 — evidence source

| Option | Description | Assessment |
|---|---|---|
| **A. Competitive-only** (what `rolling_gate.py` computes today, unmodified) | Health score is computed purely from real, executed competitive trades. | Simplest, already exists, needs zero new code. **But this is exactly the evidence source that produced Phase 6.9's absorbing lockout** — competitive trades are scarce and shared-slot-contested (§3); reusing it for a new policy carries a known, demonstrated failure risk, softened only by whatever policy is chosen in §4.2. |
| **B. Shadow-Evidence-only** | Health score computed from each strategy's own Shadow Evidence virtual trade ledger (`ai_trader/shadow_evidence/`, Phase 6.10, COMPLETE for all 43 strategies) — a continuously-running, per-strategy virtual execution that is NOT gated by the shared XAUUSD slot. | Directly solves the evidence-scarcity mechanism behind Phase 6.9's failure — every strategy accumulates its own trade history regardless of whether it currently wins the real slot. **Caveat, must be disclosed, not glossed over**: Checkpoint 1C's own CEO ruling established that Shadow Evidence reflects "how a configured strategy would execute from the conflict-adjusted `score_batch` produced inside the competitive run" — not a truly isolated result. It is richer than competitive-only, but still not identical to true single-strategy isolation. |
| **C. Dual, explicitly labeled** (both computed, both exposed, never silently blended) | Compute and expose BOTH a competitive-evidence Health score and a Shadow-Evidence Health score per strategy, clearly labeled by source, with disclosed sample sizes for each. | Matches this project's own explainability standard (Decision Intelligence, Context Memory: "no opaque algorithm," "every attachment discloses why"). Was already the preferred option in `PHASE_6_10_SHADOW_EVIDENCE_ARCHITECTURE_DESIGN.md` §11 when the same competitive-vs-shadow evidence question first arose — never authorized at the time because there was no consuming policy yet. This document is that consuming policy. |

**Recommendation: C**, using Shadow Evidence as the PRIMARY signal for eligibility decisions (since it
solves the scarcity problem that actually broke Phase 6.9), while keeping competitive-evidence Health
scores computed and visible for audit/reference and as an eventual convergence check ("does the strategy
also look healthy once it actually gets slot time").

### 4.2 Decision 2 — what the Health state controls

| Option | Description | Assessment |
|---|---|---|
| **A. Binary new-signal eligibility gate, ACTIVE-only** (Phase 6.9's own policy) | Only ACTIVE strategies generate new signals; everything else excluded. | **Already falsified** (§3). Not proposed again in any form. |
| **B. Risk-scaled tiering** | All non-DISABLED strategies remain ELIGIBLE to generate new signals (no evidence lockout); Health tier instead scales down risk/position size — e.g. ACTIVE = full size, WATCHLIST = full size, PROBATION = reduced/exploration-only size, DISABLED = excluded entirely. | Directly implements Phase 6.9's own unimplemented fix #1 ("differentiated-risk WATCHLIST") and #4 ("minimum exploration allocation"). Preserves evidence flow for every non-DISABLED strategy — the exact property Phase 6.9's own report identified as missing. **Implementation note**: `ai_trader/risk_manager/sizing.py` already has a directly analogous, precedented mechanism — `quality_factor = config.quality_factor_for(opportunity.quality)` scales `risk_per_trade_pct` by the Scoring Engine's own `quality` band. A Health-based scaling factor would be a structurally identical, small extension of an existing pattern — but Risk Manager is a currently FROZEN module (`PROJECT_STATE_v2.md` §9/§10); touching it requires its own explicit, separate CEO decision to lift that freeze specifically for this purpose. **Not assumed granted by this document.** |
| **C. Health-aware ranking priority in shared-slot contention** | When multiple strategies' signals compete for the same symbol on the same bar, Health state becomes an input (alongside the existing `total_score`/`historical_confidence`/`signal_strength`) to `ai_trader/scoring_engine/ranker.py::rank_scores`'s tie-break, so a healthier strategy is more likely to win the shared slot. | Directly targets the dominant constraint this session's own Root-Cause Study just quantified (shared-slot contention). Genuinely new — not named in any prior design document. **Scoring Engine is also a currently FROZEN module** — same caveat as B: requires its own separate, explicit unfreezing decision. Materially more invasive than B (changes a ranking outcome other strategies depend on, not just one strategy's own size). |
| **D. Eligibility-only, default-in / exclude-on-proof** | ACTIVE and WATCHLIST strategies retain full real-portfolio eligibility (no change from today); PROBATION and DISABLED are excluded from generating NEW real trades but continue trading in Shadow Evidence, unconditionally (via the existing, already-proven-safe `strategy_id_filter` mechanism, applied to the real portfolio only). No sizing or ranking change. | Touches **no frozen module at all** — `strategy_id_filter` already exists exactly for this purpose and was already proven safe by Phase 6.9 itself (overlay/exit management for open positions is always unfiltered, so a later-demoted strategy's open position still closes normally). Directly implements Phase 6.9 report's own fix #8 ("keep incumbents eligible until negative evidence accumulates") for the ACTIVE/WATCHLIST population, while giving PROBATION/DISABLED a genuine, evidence-only recovery path via uninterrupted Shadow tracking (§14). Weakest lever of the four in terms of differentiating among the eligible population (never scales size or ranking) but by far the lowest-risk, since it changes nothing about how winners are chosen among eligible strategies — that remains entirely the existing, unmodified, frozen Scoring Engine/Risk Manager behavior. |

## 5. Recommended v1 design (this document's own proposal)

**Evidence source: C (dual, Shadow-Evidence-primary, competitive-evidence-secondary/audit).**
**Policy: D (default-in eligibility gate for ACTIVE/WATCHLIST; PROBATION/DISABLED are Shadow-only) as
the v1 integration** — deliberately the least invasive option, touching zero frozen modules, reusing the
exact, already-proven-safe `strategy_id_filter` mechanism. **B and C (§4.2) are named as explicit,
separate, FUTURE candidate escalations** — not part of this v1 recommendation, not to be bundled in
without their own dedicated CEO decision to unfreeze Risk Manager (for B) or Scoring Engine (for C). The
exact per-state real/Shadow eligibility is specified precisely in §11–§12 (added after CEO review;
supersedes any looser wording elsewhere in this document).

### 5.1 What this concretely means, mechanically

- A new, thin, additive module (same pattern as `ai_trader/strategy_health/rolling_gate.py`) computes
  Health reports from Shadow Evidence's own already-existing per-strategy trade ledgers
  (`ai_trader/shadow_evidence/aggregation.py`/`research.py`, both COMPLETE, both already produce
  `WindowMetrics`-shaped statistics `strategy_health.metrics.compute_window_metrics()` was designed to
  reuse) rather than from `rolling_gate.py`'s own competitive-trade source.
- A periodic re-evaluation (cadence is an open parameter, §6) computes `real_eligible_strategy_ids_at()`
  = every strategy whose Shadow-Evidence-sourced Health state is ACTIVE or WATCHLIST (PROBATION and
  DISABLED excluded from this set, per §11–§12).
- That eligible set is passed to `SimulationHarness`'s existing `strategy_id_filter` parameter, exactly
  as Phase 6.9 already did — new REAL-signal eligibility only; overlay/exit handling stays unfiltered,
  unchanged; **Shadow Evidence itself is never filtered by this or any Health state, for any strategy**
  (§13's own load-bearing invariant) — every strategy keeps generating Shadow trades regardless of its
  real-portfolio eligibility.
- Competitive-evidence Health scores continue to be computed in parallel (reusing `rolling_gate.py`
  unmodified) and reported alongside the Shadow-Evidence ones for every strategy, clearly labeled by
  source — never silently merged into one number.
- **No change to `ai_trader/scoring_engine/`, `ai_trader/risk_manager/`, or any other currently-frozen
  module.** The only new code is: one new evidence-computation module (parallel to, not replacing,
  `rolling_gate.py`) and the harness wiring already proven safe by Phase 6.9's own precedent.

### 5.2 Why this directly fixes Phase 6.9's own failure mode

Phase 6.9 failed for two compounding reasons (§3): (1) competitive evidence was too scarce for most
strategies to ever score at all, and (2) the ACTIVE-only cutoff meant zero new evidence once the
bootstrap aged out. This design addresses both: (1) Shadow Evidence's own trade counts are — per Phase
6.10 Checkpoint 3's own real-scale validation — the same order of magnitude richer than competitive
trades that the isolated-vs-competitive gap the Root-Cause Study measured implies (isolated-slot trade
counts summed across all 43 strategies were 5.8× the competitive count in the Phase 6.9A audit); (2)
Shadow Evidence tracking is never gated by Health state for ANY strategy, in ANY state — including
PROBATION and DISABLED (§11–§14) — so there is no absorbing state to fall into, by construction: even a
fully-excluded-from-real-trading strategy keeps accumulating the exact evidence needed to recover.

## 6. Explicitly left open — not decided unilaterally by this document

- **Re-evaluation cadence.** Phase 6.9 used a fixed 30-day re-check. Shadow Evidence's richer trade
  volume may support a different cadence, but that is itself a parameter to test, not something this
  document should assert as "correct" without a controlled comparison — consistent with the Root-Cause
  Study's own closing recommendation to run controlled experiments rather than assume an answer.
- **Whether/when to escalate to Option B (risk-scaled sizing) or C (ranking priority)** — both require
  their own separate, explicit decision to unfreeze Risk Manager or Scoring Engine respectively; this
  document deliberately does not bundle that decision into the v1 recommendation.
- **The exact real-eligible roster this policy would produce once recomputed on Shadow Evidence** — the
  competitive-sourced snapshot to date shows 0/43 DISABLED but 7/43 PROBATION (both now excluded from
  real trades under §11–§12); the Shadow-sourced figures may differ materially — see §7 risk analysis.

## 7. Red-team / risk analysis (self-adversarial, before proposing acceptance)

- **Risk: this v1 policy's real-world effect size is currently uncertain, not zero.** DISABLED is
  currently 0/43 strategies (competitive-evidence-sourced, one static evaluation), but PROBATION is
  currently 7/43 (S1, S5, S13, S14, S22, S28, S30) under that same evidence source — and PROBATION is now
  also excluded from real trades under the refined §11–§12 policy. **The exact roster under the
  Shadow-Evidence-sourced scoring this design actually proposes cannot be asserted without a live
  recomputation** (§15) — it may differ materially from the competitive-sourced snapshot, in either
  direction. This is disclosed as a genuine open empirical question, not assumed to be small.
- **Risk: eligibility is necessary, not sufficient, for a strategy to actually trade.** Under this
  design, real-eligible only means a strategy's signals are considered at all for the shared slot; which
  eligible strategy actually wins a contested slot remains entirely governed by the existing, unmodified,
  frozen Scoring Engine ranking. A strategy could be persistently real-eligible (WATCHLIST) yet
  realistically almost never win a slot against consistently higher-scoring competitors — this design
  does not change that dynamic, by design (§5, "touches no frozen module"). If the CEO's actual intent
  for "Strategy Health integration" is that Health should meaningfully change WHO WINS contested slots,
  not just who is allowed to compete, Option C (§4.2) is the one that does that — and it requires its own
  separate unfreezing decision, explicitly not assumed here.
- **Risk: Shadow Evidence's own disclosed semantic limitation (Checkpoint 1C) means its trade ledger is
  not a true isolated-performance measurement.** A strategy could show artificially inflated or deflated
  Shadow-sourced health purely as an artifact of the competitive run's own cross-strategy conflict
  penalties at the times it happened to be evaluated — the same caveat this session's own Root-Cause
  Study already had to account for when using `conflict_penalty` to explain BELOW_FLOOR denials. This
  should be disclosed in every Shadow-sourced Health report, not silently treated as ground truth.
  Competitive-evidence Health scores are reported alongside specifically so this gap is visible, not
  hidden.
- **Risk: "default-in" could look like it contradicts the whole point of a promotion policy** (why
  compute Health at all if almost nothing gets excluded?). Answered directly by §7's first point: this
  v1 is intentionally conservative, proves the underlying mechanism safely, and creates the exact
  foundation (dual, Shadow-sourced Health reporting, wired safely into the harness) that a future,
  separately-authorized Option B/C escalation would build on rather than rebuild from scratch.

## 8. What this design explicitly does NOT do

- Does not modify `ai_trader/strategy_health/` — the scoring system itself is reused entirely as-is.
- Does not modify `ai_trader/scoring_engine/`, `ai_trader/risk_manager/`, or any other frozen module.
- Does not modify `ai_trader/shadow_evidence/` — reuses its already-existing aggregation/research
  outputs as a read-only evidence source.
- Does not implement Portfolio Architect, Learning/Research Feedback, Risk Integration, Execution
  Integration, or MT5 Live — those remain later, separate roadmap steps.
- Does not run any backtest or write any code — this is a design proposal only.
- Does not decide re-evaluation cadence, nor whether to later escalate to risk-scaled sizing or
  ranking-priority integration (§6).

## 9. Proposed validation plan, if this design is accepted (NOT executed by this document)

If accepted, the next step (a separate, explicit implementation checkpoint, mirroring every prior
subsystem's own pattern) would: (1) build the new Shadow-Evidence-sourced Health-computation module,
additive only; (2) prove byte-identical competitive execution when the new eligibility filter is
disabled (the same parity-proof convention Shadow Evidence Checkpoints 1B/1C/3 already established);
(3) run one instrumented comparison — current static all-43 baseline vs. this policy's eligible-subset
roster — over the same window this session's own studies already used, to observe (not yet judge)
whether trade volume/composition changes as expected; (4) report findings, with no strategy eliminated
and no threshold changed, exactly like every prior CEO-directed research study this session ran.

## 11. Explicit lifecycle (CEO-requested clarification 1)

Five states, exactly as named by the CEO. **`NEW` is a policy-layer label, not a fifth classifier
band** — the frozen `ai_trader/strategy_health/classifier.py` still only ever emits `ACTIVE`/
`WATCHLIST`/`PROBATION`/`DISABLED` (unchanged, untouched). `NEW` is derived, additively, entirely outside
that frozen module: it is `state == WATCHLIST AND overall_score is None AND n_trades == 0` in every
window — precisely the classifier's own existing, already-safe "no evidence yet" default, given a
distinct name so a promotion-policy reader can tell "genuinely untested" apart from "tested and landed
in the WATCHLIST band" at a glance. This changes zero classifier behavior; it is a read-only
re-labeling of an output the frozen system already produces.

**The states are NOT a strict one-way pipeline** — evidence moves scores up and down continuously, so
every non-terminal state has both a promotion and a demotion edge. The CEO's own diagram (NEW → WATCHLIST
→ ACTIVE → PROBATION → DISABLED) is the canonical *maturation path a strategy is expected to typically
travel*, not the only legal transition — the full graph is bidirectional, by design, to satisfy
clarification 4 (no absorbing states).

| State | Entry condition | Exit condition(s) | Can do | Cannot do |
|---|---|---|---|---|
| **NEW** | Strategy registered in the Library with zero trade history in both Shadow Evidence and the competitive ledger (or: any strategy whose Shadow+competitive evidence has literally never produced ≥1 trade in any of the 3/6/12m windows). | Any single trade recorded (Shadow or competitive) in any window → immediately re-evaluated as whatever real classifier output that produces (typically WATCHLIST, since n=1 is heavily shrunk toward 50 by the frozen Bühlmann-credibility mechanism — could occasionally land elsewhere, not asserted here). | Generate new signals in **both** Shadow Evidence and the real competitive portfolio — full eligibility, identical to WATCHLIST/ACTIVE. This is required: a strategy that can never trade can never leave `NEW`. | Nothing is restricted. `NEW` is purely informational (flags "zero track record — weight any single observation about this strategy proportionally more cautiously"), never an operational gate. |
| **WATCHLIST** | Computed `overall_score` lands in `[45, 65)`; OR demotion from `ACTIVE` (score drops below 65, net of the frozen trend-adjustment hysteresis); OR promotion from `PROBATION` (score rises to ≥45). | Score ≥65 (or a +15 trend bump) → `ACTIVE`. Score <45 → `PROBATION`. | Generate new signals in **both** Shadow Evidence and the real competitive portfolio — full eligibility, unchanged from today's system for every strategy that isn't explicitly demoted further. | Nothing is restricted relative to `ACTIVE` — the distinction from `ACTIVE` is purely informational/monitoring severity, not an operational difference, under this v1 policy. |
| **ACTIVE** | Computed `overall_score` ≥65; OR a −15-to-+15 trend bump from `WATCHLIST`. | Score drops below 65 (net of hysteresis) → `WATCHLIST`. | Competes normally for the shared XAUUSD slot exactly as every strategy does today — **zero change** from current system behavior. | Nothing is restricted. |
| **PROBATION** | Computed `overall_score` lands in `[25, 45)`; OR demotion from `WATCHLIST` (score <45); OR promotion from `DISABLED` (score rises to ≥25). | Score ≥45 → `WATCHLIST` (recovery). Score <25 → `DISABLED`. | Continues running in Shadow Evidence, unconditionally and without restriction — full virtual execution, full evidence accumulation, exactly as every other state. | **Cannot open new REAL/competitive positions.** New-signal eligibility for the real portfolio is revoked (via `strategy_id_filter`, §5.1) — this directly answers clarification 2's "poate rămâne doar în Shadow?": **yes, exactly that.** Any already-open real position at the moment of demotion is unaffected and closes normally (overlay/exit management is never filtered, per the existing, already-proven-safe harness behavior). |
| **DISABLED** | Computed `overall_score` <25; OR demotion from `PROBATION`. | Score ≥25 (recomputed from **genuinely new** Shadow Evidence trades accumulated while disabled) → `PROBATION`. **Never time-based, never automatic-by-expiry** — see §14. | Continues running in Shadow Evidence, unconditionally and without restriction — identical treatment to `PROBATION` on this axis, specifically so recovery evidence keeps accumulating. | **Cannot open new REAL/competitive positions** — same mechanism as `PROBATION`. This directly answers clarification 2's "este exclusă complet?": **no, not completely** — excluded from the real portfolio only, never from Shadow. A strategy excluded from Shadow too would have no path back (see §14). |

## 12. Exact influence per state on the AI Trader (CEO-requested clarification 2, answered directly, zero ambiguity)

Answering the CEO's own named examples literally:

- **ACTIVE — poate concura normal?** Yes. Full, unrestricted competition for the shared slot, identical
  to every strategy's current behavior. No change from today's system.
- **WATCHLIST — poate produce semnale? poate câștiga Shadow Evidence?** Yes to both. WATCHLIST has
  identical operational rights to ACTIVE under this v1 policy — it generates real signals AND accumulates
  Shadow Evidence exactly like ACTIVE. The only difference is a monitoring label, never an eligibility
  restriction. (This is deliberate: Phase 6.9's failure came from restricting exactly this population —
  see §3/§15.)
- **PROBATION — poate rămâne doar în Shadow?** Yes, precisely. PROBATION strategies generate signals
  and trade ONLY inside Shadow Evidence; they are excluded from generating new REAL competitive trades.
  Shadow tracking is never interrupted.
- **DISABLED — este exclusă complet?** No. DISABLED excludes a strategy from the REAL competitive
  portfolio only (no new real trades, same as PROBATION). It is never excluded from Shadow Evidence —
  Shadow tracking must continue unconditionally for every strategy in the Library, in every state,
  forever, specifically so that a genuine recovery path always exists (§14). A strategy excluded from
  Shadow too would have no way to ever generate the evidence needed to leave DISABLED.

**Summary table** (the single unambiguous reference):

| State | New signals: Shadow | New signals: Real portfolio | Existing real positions |
|---|---|---|---|
| NEW | Yes | Yes | n/a (none possible yet) |
| WATCHLIST | Yes | Yes | Unaffected |
| ACTIVE | Yes | Yes | Unaffected |
| PROBATION | Yes | **No** | Closed normally via existing unfiltered overlay/exit management |
| DISABLED | Yes | **No** | Closed normally via existing unfiltered overlay/exit management |

## 13. Module contracts (CEO-requested clarification 3 — interfaces only, no implementation)

- **Shadow Evidence → Strategy Health.** Contract: for every strategy_id in the Library, unconditionally
  (never gated by that strategy's own Health state — this is the load-bearing invariant the rest of this
  design depends on), Shadow Evidence exposes a per-strategy virtual trade ledger / `WindowMetrics`-shaped
  summary via its already-existing `aggregation.py`/`research.py` read-only query surface. Strategy
  Health's new Shadow-sourced evidence path consumes this as its primary input, read-only, at any
  `as_of`. Direction: Shadow Evidence → Strategy Health only; Strategy Health never writes to or
  configures Shadow Evidence.
- **Strategy Health → [new] Eligibility Policy layer.** Contract: at each re-evaluation `as_of`, Strategy
  Health (both Shadow-sourced primary and competitive-sourced secondary/audit) exposes one `HealthReport`
  per strategy (state, score, trend, evidence counts, source label). The (not-yet-built) eligibility
  policy layer consumes these reports and derives one set: `real_eligible_strategy_ids_at(as_of)` = every
  strategy NOT in `{PROBATION, DISABLED}`. Direction: Strategy Health → Eligibility Policy only.
- **Eligibility Policy layer → Risk Manager / Signal Engine (via `harness.py`).** Contract: the derived
  eligible set is passed as `strategy_id_filter` to `SimulationHarness`, gating NEW-signal generation
  ONLY (`build_runtime_handles(..., only_ids=...)`) — exactly the existing, already-proven-safe mechanism
  Phase 6.9 already used. **Risk Manager's own contract is completely unchanged**: it still receives
  whatever `OpportunityScore`s are handed to it (now a subset, for excluded strategies) and applies its
  existing 8-stage gate chain exactly as today, with no awareness of *why* a given strategy's
  opportunities are or aren't present. No new gate is added inside `risk_manager/pipeline.py`.
- **Strategy Health / Eligibility Policy → Decision Engine.** In this v1 design, **no contract exists —
  deliberately.** Decision Intelligence (v1/v2) answers "which currently-PRESENT edge deserves execution
  right now," using its own four gates (contract status, maturity, confidence, expectancy) — none of
  which reference Health state today. This design does not add a fifth gate. Whether Decision
  Intelligence should someday also check real-trade eligibility (so it never recommends a
  PROBATION/DISABLED strategy) is an open, explicitly out-of-scope question for a future, separate
  decision — not resolved here, and not assumed.
- **Strategy Health / Eligibility Policy → Portfolio Architect.** Portfolio Architect does not exist yet
  (next roadmap step). Expected contract, stated for foresight only, not implemented: Strategy Health
  answers "who is allowed to generate new real signals right now" (`real_eligible_strategy_ids_at`);
  Portfolio Architect (once built) would consume that already-filtered eligible set as one of its own
  inputs when deciding capital allocation/sizing/diversification across the strategies Health has already
  allowed to compete — Portfolio Architect does not reach past or override Strategy Health's own
  exclusions in this contract.
- **"Edge Selection AI"** — this exact term has no existing, named module in this project's own
  vocabulary. The closest existing concept is Decision Intelligence (v1/v2), which selects/ranks/
  recommends one edge for execution from currently-PRESENT edges. This document treats "Edge Selection
  AI" as referring to Decision Intelligence unless the CEO clarifies it means something else — flagged
  explicitly rather than silently assumed.
- **What does NOT change**: Risk Manager, Scoring Engine, Execution Engine, Decision Intelligence v1/v2,
  Context Memory, Shadow Evidence's own internal engine — none of their existing contracts are modified
  by this design. The only genuinely new contract is Strategy Health (Shadow-sourced) → Eligibility
  Policy → `strategy_id_filter`, all additive.

## 14. Recovery from PROBATION and DISABLED — no absorbing states (CEO-requested clarification 4)

**The mechanism that makes recovery genuinely possible, stated once, precisely**: Shadow Evidence tracks
every strategy in the Library, in every state, unconditionally, forever (§11–§13's own load-bearing
invariant). A strategy in PROBATION or DISABLED is excluded from the REAL portfolio, but its Shadow
Evidence engine keeps evaluating every bar, keeps producing virtual entries/exits, and keeps
contributing fresh trades to that strategy's own Shadow-sourced trade ledger — exactly as if it were
still fully active, just without real capital at risk. Because Strategy Health's primary evidence source
is this Shadow ledger (not the real ledger it's excluded from), **new genuine evidence keeps arriving for
excluded strategies at the same rate as for eligible ones** — recovery is driven by real, new,
positive Shadow-Evidence outcomes, never by a timer or by old evidence simply expiring out of the
window.

- **PROBATION → WATCHLIST**: triggered when a re-evaluation recomputes `overall_score` ≥45 from the
  (now-updated) blended Shadow+competitive evidence — i.e., the strategy's own recent Shadow-tracked
  trades were good enough to lift its score back into the WATCHLIST band.
- **DISABLED → PROBATION**: same mechanism, ≥25 threshold.
- **Explicitly NOT how recovery happens**: NOT by old bad trades aging out of the rolling window with
  nothing to replace them (that would be recovery-by-forgetting, not recovery-by-evidence, and was
  flagged as a weaker, not-preferred mechanism during this design's own reasoning). Because Shadow
  Evidence never stops for excluded strategies, the window is never empty for them the way Phase 6.9's
  competitive-only windows went empty — there is always fresh evidence to be judged on.
- **Consequence, stated as the direct answer to "no absorbing states"**: there is no state a strategy
  can enter from which zero exit path exists. `DISABLED` is not a terminal/removal state; it is the
  strictest tier of the SAME lifecycle, with the SAME unconditional Shadow tracking as every other
  state, and the SAME evidence-driven re-evaluation cadence.

## 15. Performance-impact argument (CEO-requested clarification 5 — architectural, not yet empirical)

Per the CEO's own explicit instruction ("Nu implementa încă"), no backtest was run to produce numeric
proof — the argument below is structural, derived from the design's own properties, with an empirical
confirmation named as the natural first validation step once implementation is authorized (§9,
unchanged).

- **Does not reduce the number of opportunities reaching the real portfolio, for the great majority of
  strategies.** Under this policy, only `PROBATION`/`DISABLED` strategies lose real-trade eligibility;
  `ACTIVE`/`WATCHLIST` strategies are completely unaffected — full eligibility, identical to today. In
  the one static lifetime evaluation to date (competitive-evidence-sourced), that would have meant 36 of
  43 strategies (2 ACTIVE + 34 WATCHLIST) fully unaffected; **the exact roster under Shadow-sourced
  scoring cannot be asserted without a live recomputation — a controlled next-step experiment, not
  claimed here.**
- **Does not produce starvation.** Starvation in Phase 6.9's sense meant the ELIGIBLE roster's own
  evidence source went to zero. Under this design, the evidence source (Shadow Evidence) is structurally
  decoupled from real-trade eligibility — Shadow runs unconditionally regardless of who is currently
  eligible for the real portfolio, so the population that determines FUTURE eligibility changes never
  itself depends on CURRENT eligibility. This is the specific property Phase 6.9 lacked (its only
  evidence source, competitive trades, WAS the same gated resource its own policy restricted).
- **Cannot re-enter a Phase 6.9-style lockout, by construction, not merely by observation.** Phase 6.9's
  failure required: (a) a hard cutoff excluding most of the population from generating new signals, and
  (b) that same excluded population being the only possible source of new evidence. This design breaks
  precondition (b) unconditionally (Shadow Evidence has no Health-state gate anywhere in its own
  contract, §13) — so even in the worst case (every strategy simultaneously PROBATION/DISABLED), Shadow
  Evidence continues generating fresh evidence for all 43, and the population can recover. There is no
  configuration of this design under which the absorbing state Phase 6.9 hit can recur.
- **Likely secondary effect, named as a hypothesis, not asserted as proven**: per the separate
  Root-Cause Study (§8.19 of `PROJECT_STATE_v2.md`), the dominant constraint on the current top
  candidates is shared-slot contention for one XAUUSD position. Removing genuinely low-quality
  (PROBATION/DISABLED) strategies from that contention should, if the Root-Cause Study's own diagnosis is
  correct, free real slot-contention capacity for the remaining eligible strategies — a plausible,
  well-motivated hypothesis given this session's own prior research, but **not claimed as demonstrated
  here**; it is exactly the kind of question the proposed validation run (§9) would actually measure.

## 16. Verdict (updated)

**Status: ACCEPTED WITH CONDITIONS** (CEO decision, this session) — general direction and all five
stated principles confirmed. **§§11–15 above are the requested architectural clarifications**,
completing the lifecycle definition, the per-state influence table, the inter-module contracts, the
non-absorbing recovery mechanism, and the structural performance-impact argument. No code has been
written, no backtest has been run, no existing module has been modified. Per the CEO's own explicit
instruction, implementation does not begin until this clarified architecture is reviewed as complete —
that review is the immediate next step, not assumed granted by this update.
