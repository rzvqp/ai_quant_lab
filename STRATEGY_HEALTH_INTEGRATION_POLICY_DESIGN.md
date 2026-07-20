# Strategy Health Integration/Promotion Policy — Design Proposal

**Flow**: B (AI Trader Development). **Roadmap step**: 1 of 6 (Strategy Health → Portfolio Architect →
Learning/Research Feedback → Risk Integration → Execution Integration → MT5 Live). **Status of this
document**: DESIGN PROPOSAL ONLY — no code written, no backtest run, no existing module modified. Per
CEO decision, this follows the same design-first-then-implement pattern already used for every prior
subsystem in this project (Shadow Evidence Architecture Design, Context Memory Checkpoint 8) rather than
implementing directly.

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
| **D. Eligibility-only, default-in / exclude-on-proof** | Only DISABLED strategies are excluded from new-signal generation (via the existing, already-proven-safe `strategy_id_filter` mechanism); ACTIVE, WATCHLIST, AND PROBATION are all eligible. No sizing or ranking change. | Touches **no frozen module at all** — `strategy_id_filter` already exists exactly for this purpose and was already proven safe by Phase 6.9 itself (overlay/exit management for open positions is always unfiltered, so a later-DISABLED strategy's open position still closes normally). Directly implements Phase 6.9 report's own fix #8 ("keep incumbents eligible until negative evidence accumulates") — inverted from Phase 6.9's own "default-out, prove-in" framing to "default-in, prove-out." Weakest lever of the four (only ever removes strategies, never differentiates among the eligible ones) but by far the lowest-risk, since it changes nothing about how winners are chosen among eligible strategies — that remains entirely the existing, unmodified, frozen Scoring Engine/Risk Manager behavior. |

## 5. Recommended v1 design (this document's own proposal)

**Evidence source: C (dual, Shadow-Evidence-primary, competitive-evidence-secondary/audit).**
**Policy: D (default-in eligibility gate, DISABLED-exclusion only) as the v1 integration** — deliberately
the least invasive option, touching zero frozen modules, reusing the exact, already-proven-safe
`strategy_id_filter` mechanism. **B and C are named as explicit, separate, FUTURE candidate escalations**
— not part of this v1 recommendation, not to be bundled in without their own dedicated CEO decision to
unfreeze Risk Manager (for B) or Scoring Engine (for C).

### 5.1 What this concretely means, mechanically

- A new, thin, additive module (same pattern as `ai_trader/strategy_health/rolling_gate.py`) computes
  Health reports from Shadow Evidence's own already-existing per-strategy trade ledgers
  (`ai_trader/shadow_evidence/aggregation.py`/`research.py`, both COMPLETE, both already produce
  `WindowMetrics`-shaped statistics `strategy_health.metrics.compute_window_metrics()` was designed to
  reuse) rather than from `rolling_gate.py`'s own competitive-trade source.
- A periodic re-evaluation (cadence is an open parameter, §6) computes `eligible_strategy_ids_at()` =
  every strategy whose Shadow-Evidence-sourced Health state is NOT DISABLED (i.e. ACTIVE, WATCHLIST, or
  PROBATION all pass).
- That eligible set is passed to `SimulationHarness`'s existing `strategy_id_filter` parameter, exactly
  as Phase 6.9 already did — new-signal eligibility only; overlay/exit handling stays unfiltered,
  unchanged.
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
counts summed across all 43 strategies were 5.8× the competitive count in the Phase 6.9A audit); (2) the
default-in/exclude-on-DISABLED-only policy means WATCHLIST and PROBATION strategies keep generating
signals and keep accumulating fresh Shadow evidence indefinitely — there is no absorbing state to fall
into, by construction.

## 6. Explicitly left open — not decided unilaterally by this document

- **Re-evaluation cadence.** Phase 6.9 used a fixed 30-day re-check. Shadow Evidence's richer trade
  volume may support a different cadence, but that is itself a parameter to test, not something this
  document should assert as "correct" without a controlled comparison — consistent with the Root-Cause
  Study's own closing recommendation to run controlled experiments rather than assume an answer.
- **Whether/when to escalate to Option B (risk-scaled sizing) or C (ranking priority)** — both require
  their own separate, explicit decision to unfreeze Risk Manager or Scoring Engine respectively; this
  document deliberately does not bundle that decision into the v1 recommendation.
- **Whether the DISABLED band's current real-world rarity (0/43 in the one static evaluation to date)
  means this v1 policy would, in practice, exclude nobody at first** — see §7 risk analysis.

## 7. Red-team / risk analysis (self-adversarial, before proposing acceptance)

- **Risk: this v1 policy may be a no-op in practice.** DISABLED is currently 0/43 strategies. If the
  Shadow-Evidence-sourced score never produces a DISABLED verdict either, this integration changes
  nothing observable at first. **This is treated as a feature, not a bug, for a v1**: it is the
  lowest-risk possible first integration (proves the plumbing — Shadow-sourced health computation, the
  dual-evidence reporting, the harness wiring — without any strategy's real trading being affected yet),
  and gives a clean baseline to measure any FUTURE, more aggressive policy against.
- **Risk: eligibility is necessary, not sufficient, for a strategy to actually trade.** Under this
  design, "eligible" only means a strategy's signals are considered at all; which eligible strategy
  actually wins a contested shared slot remains entirely governed by the existing, unmodified, frozen
  Scoring Engine ranking. A strategy could be persistently "eligible" (WATCHLIST/PROBATION) yet
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

## 10. Verdict (for CEO review)

**Status**: PROPOSED. Awaiting CEO review: ACCEPTED / ACCEPTED WITH CONDITIONS / NEEDS REVISION /
REJECTED. No further roadmap progress (Portfolio Architect or beyond) is assumed until Strategy Health
integration is either implemented per an accepted design, or the CEO redirects this step.
