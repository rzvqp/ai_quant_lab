# PROJECT_STATE — AI Quant Research Lab → AI Trader — v2 (UPDATED: OFFICIAL PROJECT SAVE, 2026-07-20, official bifurcation into Flow A / Flow B)

**Purpose**: this is the single, authoritative, consolidated state document for the ENTIRE project —
the frozen Research Lab, the AI Trader built on top of it, and (as of this save) the newly-opened Alpha
Discovery Laboratory — current as of this official save. A brand-new chat, with no access to any prior
conversation, must be able to reconstruct the complete project from this document plus the ones it
points to. Every fact below was verified directly against `git log`/`git status`/`git diff` at this
save's own close — nothing here is carried forward unverified. This document supersedes no prior
report — `PROJECT_STATE_v1.0.md`, `ROLLING_HEALTH_BACKTEST_HANDOFF.md`, and every phase's own dedicated
report remain the authoritative, detailed sources for their own respective scopes; this document exists
to make the CURRENT, FULL state reachable in one place.

**This update's own scope (this is the FIFTH official save; the prior one, §8.17, closed after
Checkpoints 14–15): (1) documents three interim, non-checkpoint research artifacts produced since the
Checkpoints 14–15 save — the Strategy Historical Performance Study, the Strategy Constraint
Root-Cause Study, and the CEO Strategy Performance Atlas (§8.19); (2) records the official opening of
the 40-Edge Alpha Discovery Program (§8.20); (3) formalizes, per explicit CEO decision, the project's
development going forward as TWO independent, non-conflicting parallel flows — Flow A (Alpha Discovery
Laboratory) and Flow B (AI Trader Development) — see §1.1. No code was implemented, no backtest was
run, no strategy or production module was modified, and no Phase 7 checkpoint beyond 14–15 was opened
by any of this save's own scope.**

---

## 0. Official state (authoritative, verify live before trusting)

```
Repository path:  C:\Users\MEDION GAMING\ai_quant_lab-research-main
Branch:           ai-trader-implementation
HEAD (pre-save):  d60fa63 "docs: launch 40-Edge Alpha Discovery Program infrastructure"
Working tree:     clean (verified live at this official save, before its own commit)
```

**Commits since the Checkpoints 14–15 save (`028b620`), in order** — all documentation/research
artifacts, zero `ai_trader/` diff, detailed in §8.19–§8.20:
```
7c3eb62  research: preserve strategy historical performance study
2650c3b  research: diagnose candidate strategy constraints
f4eba6b  docs: enrich strategy performance atlas with evidence levels
d60fa63  docs: launch 40-Edge Alpha Discovery Program infrastructure
```

**Re-verify `git branch --show-current`/`git log -1`/`git status --porcelain` directly before trusting
any git-state claim anywhere in this project's documentation** — the standing discipline every prior
handoff has followed, re-confirmed at this save.

**Verified live, at the close of the Checkpoints 14–15 batch (2026-07-20) — the ONE full-repository run
this batch's own validation policy authorizes (two checkpoints closing together):**
```
pytest ai_trader/ -q                                    -> 2101 passed
mypy --strict ai_trader/ --exclude 'tests/'              -> Success: no issues found in 222 source files
coverage run --source=ai_trader -m pytest ai_trader/ -q
coverage report --omit="*/tests/*"                       -> TOTAL 12087 stmts, 432 miss, 96%
```
(Baseline for comparison, the Checkpoints 10–13 batch's own close, the last figure this document
previously cited: 2051 passed, 210 mypy-clean source files, 11813 stmts/432 miss/96%. The 432-miss
figure is UNCHANGED end to end since — every one of the +274 statements added by
`decision_intelligence_v2`/`decision_comparison` reaches 100% targeted coverage individually, §8.16.)

**Combined Context Memory + Decision Intelligence validation** (`ai_trader/context_memory/` +
`ai_trader/decision_intelligence/` + `ai_trader/decision_intelligence_v2/` +
`ai_trader/decision_comparison/`, re-confirmed at §8.16):
```
pytest ai_trader/context_memory/ ai_trader/decision_intelligence/ ai_trader/decision_intelligence_v2/ ai_trader/decision_comparison/ -q  -> 303 passed
mypy --strict (same four packages) --exclude 'tests/'    -> Success: no issues found in 28 source files
```

**Context-Memory-scoped validation** (`ai_trader/context_memory/`, run independently at each of
Checkpoints 9–13's own close and re-confirmed once combined at §8.12):
```
pytest ai_trader/context_memory/ -q                     -> 221 passed
mypy --strict ai_trader/context_memory/ --exclude 'tests/'  -> Success: no issues found in 11 source files
coverage report --source=ai_trader.context_memory --omit tests/  -> TOTAL 934 stmts, 0 miss, 100%
```

---

## 1. Mission and the two-system architecture

**AI Quant Research Lab → AI Trader.** Two systems, physically separated by design, at different
levels of maturity:

- **Research Lab** (`code/`, `results/`, `knowledge/`) — discovers and validates trading strategies
  against historical XAUUSD data using a frozen backtesting engine. **FROZEN AND STABLE since before
  the AI Trader work began; confirmed 0-diff at every single phase close since, including this one.**
  Its own official state as of its last session close (2026-07-14, pre-Wave-1) is
  `PROJECT_STATE_v1.0.md` — summary in §2 below. Nothing in this document changes that state.
- **AI Trader** (`ai_trader/`) — the execution/simulation system built ON TOP of the Research Lab's
  own discovered strategies, consuming its Strategy Library as a frozen contract. This is where
  essentially all work across Phases 6.1–6.9A (§3–§6), Phase 6.10's own Edge Portfolio Evidence System
  (§7, now CLOSED in full), and Phase 7's own AI Trader Intelligence Layer (§8, Checkpoints 5–6) took
  place.

### 1.1 Official bifurcation, this save: Flow A / Flow B (a THIRD stream, added to the two above)

Per explicit CEO decision at this official save, all future development is organized into **two
independent, parallel flows**, in addition to (not replacing) the frozen Research Lab described above.
Both flows may proceed without waiting on or conflicting with the other:

- **Flow A — Alpha Discovery Laboratory.** A brand-new, separate research program: the systematic
  study of 40 raw, unvalidated Alpha Edge hypotheses (`EDGE_DISCOVERY_REGISTRY_v1.md`), all currently
  `Status = UNSTUDIED`/`Version = V0`, following one shared protocol
  (`EDGE_RESEARCH_PROTOCOL.md`: V0 → Discovery → Frozen Candidate → Validation → Walk Forward → Final
  Verdict) and one recommended sequencing (`EDGE_DISCOVERY_ROADMAP.md`). Full detail: §8.20. **Status
  as of this save: READY TO START** — the program is opened and its next action is authorized (begin
  systematic Discovery-stage study of the registry, starting from the Roadmap's Tier 1), but no
  individual edge has entered Discovery yet, no edge has been implemented, and reaching a Final Verdict
  on any edge does NOT itself authorize implementation (`EDGE_RESEARCH_PROTOCOL.md` §5) — every stage
  gate the protocol defines still applies per edge.
- **Flow B — AI Trader Development.** The pre-existing main roadmap (Phases 6.1 onward, §3–§8 of this
  document) continues, unsuspended, unchanged in direction. **Status: ACTIVE.** Remaining order, per
  explicit CEO instruction at this save: **Strategy Health (integration/promotion policy) → Portfolio
  Architect → Learning / Research Feedback → Risk Integration → Execution Integration → MT5 Live.**
  §8.18's own standing "no further Phase 7 checkpoint without explicit authorization" rule continues to
  govern exactly which of these steps may begin next.

**Why these two flows cannot conflict**: Flow A's artifacts to date are markdown documents at the repo
root plus (once Discovery begins) a future `edge_research/` directory of per-edge logs
(`EDGE_RESEARCH_PROTOCOL.md` §6) — it touches no file inside `ai_trader/`, `code/`, `results/`, or
`knowledge/`, and produces no strategy, no `RuntimeEvaluator`, no code change of any kind unless and
until a specific edge earns a Final Verdict AND a separate, explicit CEO decision authorizes turning it
into an implemented strategy (at which point it would join Flow B's own Strategy Library exactly like
any of S1–S51, not create a rival system). Flow B continues to own every file already listed in §9/§10.
Neither flow's own standing prohibitions (Flow A's protocol rules; Flow B's frozen-module list) apply to
the other.

**Standing, non-negotiable CEO directives that govern ALL AI Trader work:**
- **Simulation-first**: the AI Trader must prove robust historical profitability in simulation before
  any Broker Adapter/MT5/live execution work begins.
- **Terminal holdout SEALED**: the last 20% of the M15 series (16,831 bars, 2025-10-23 09:15 UTC →
  2026-07-13 06:00 UTC) has never been opened by anything — Research Lab or AI Trader — and requires
  its own dedicated CEO gate to open. No phase to date has opened it.
- **No strategy is ever permanently eliminated** based on any AI Trader analysis — every negative
  finding to date (Phase 6.9, the relevance audit, Phase 6.9A) is diagnostic, not a verdict on any
  strategy's own inherent worth.

---

## 2. Research Lab state (frozen; summary — full detail in `PROJECT_STATE_v1.0.md`)

- Official engine: `code/mstrat.py` (v2, pre-registered stop-floor) — FROZEN, byte-identical since
  baseline.
- Dataset: OANDA XAUUSD M15/H1/H4/D1, 2022-12-16 → 2026-07-13 (84,152 M15 bars). Split: research
  (first 60%, ~50,491 bars) / validation-OOS (next 20%, ~16,830 bars) / **sealed holdout (last 20%,
  16,831 bars, NEVER opened)**.
- Strategies: S1–S51 defined (2,432 hypotheses tested pre-AI-Trader). 383 historically profitable, 143
  research-worthy (all EXPLORATORY, no statistical verdicts issued at the Research Lab level).
  S32–S37 NOT_IMPLEMENTED (need external data, CEO-gated); S47/S49 technically invalid.
- Statistical validation: matched-null engine VALIDATED (Verdict A) on a 10-hypothesis pilot only;
  global-FDR and walk-forward/Red Team NOT RUN on the full universe.
- Knowledge system: 19 behavioral primitives, 9 invariants, a 42-node knowledge graph, a Hypothesis
  Generator v1 (54 candidates), an Experiment Planner v1 (10 experiments selected). Research Lab's own
  "Wave 1" (EXP-01…EXP-06) — a DIFFERENT "Wave" concept from the AI Trader's own Wave B/Wave D below —
  is PLANNED, FROZEN, NOT STARTED, NOT AUTHORIZED past planning.
- **Confirmed 0-diff (`git status --porcelain -- code/ results/ knowledge/`) at every AI Trader phase
  close to date, including this session's own close.**

## 3. AI Trader — completed phases (6.1 through Wave D Audit)

| Phase | Status | Report |
|---|---|---|
| 6.1–6.6 (Market Scanner, Strategy Manager, Signal Engine, Scoring Engine, Risk Manager, Execution Engine) | READY | pre-dates the handoff documents |
| 6.7 (Simulation Framework) | READY | pre-dates the handoff documents |
| 6.8 Checkpoint 1 (S1 reference slice) | READY | — |
| 6.8 Checkpoint 2 (15 strategies) | READY | `PHASE_6_8_CHECKPOINT_2_REPORT.md` |
| 6.8 Wave B (all 43 runtime-eligible strategies migrated) | COMPLETE | `PHASE_6_8_WAVE_B_COMPLETION_REPORT.md` |
| Wave D (first full-portfolio simulation, all 43, static) | COMPLETE | `WAVE_D_PORTFOLIO_SIMULATION_REPORT.md` |
| Wave D Audit (per-strategy tiering, correlation, 3 static variants) | COMPLETE | `WAVE_D_PORTFOLIO_AUDIT_REPORT.md` |
| Strategy Health System (rolling-window scoring, build + first static evaluation) | COMPLETE | `STRATEGY_HEALTH_SYSTEM_REPORT.md` |

**Wave D headline result** (all 43 strategies, static, no gating, full 2022-12-16→2026-07-13 range,
$2,000 capital, 5% risk/trade, `run_seed=1`): **513 trades, +$313.21 net profit (+15.66%), Sharpe
1.196, Sortino 1.372, max drawdown 6.16%, profit factor 1.264, win rate 39.77%, expectancy +0.179R.**
Zero execution costs modeled (disclosed limitation, not a claim of zero real-world cost). Two real
Simulation Framework bugs were found and fixed reaching this result (cooldown-clock hardcoded to 0;
time-stop firing one bar late) — both confined to `ai_trader/simulation/`, zero impact on the Research
Lab or the six frozen pipeline modules. **This exact result was independently reproduced, fresh, byte-
for-byte, during both Phase 6.9 and the Current XAUUSD 12-Month Relevance Audit** (via the static
all-43 baseline in each) — the strongest possible confirmation of both the original result and every
later phase's own reconstructed configuration.

**Wave D Audit key finding**: the single-shared-XAUUSD-slot architecture makes results highly
composition-sensitive in a NON-ADDITIVE way — removing/adding a strategy does not simply add/remove
its own trades; it changes which OTHER strategy's signals occupy the freed/taken slot. **This finding
recurs and is precisely quantified three more times** across Phase 6.9 (§4), the relevance audit (§5),
and Phase 6.9A (§6) — by Phase 6.9A it is the single most load-bearing, empirically measured fact in
the whole project.

**Strategy Health System**: a rolling-window (3/6/12-month), percentile-rank + Bühlmann-credibility-
shrinkage + PCA-derived-weight scoring system, classifying strategies ACTIVE/WATCHLIST/PROBATION/
DISABLED. First (one-time, full-lifetime, static) evaluation as of 2026-07-13: **2 ACTIVE (S40, S46),
34 WATCHLIST, 7 PROBATION (S1, S5, S13, S14, S22, S28, S30), 0 DISABLED.** Its own scoring methodology
(`ai_trader/strategy_health/types.py`/`metrics.py`/`scoring.py`/`classifier.py`/`evaluator.py`) has
been READ from but never modified, by any later phase, ever.

## 4. Phase 6.9 — Rolling Health-Gated Backtest — CLOSED, VALID NEGATIVE RESULT

**Objective**: test whether a TIME-EVOLVING, Health-gated strategy roster (re-evaluated monthly,
ACTIVE-only trading) outperforms the static all-43 baseline, over the FULL 3.6-year Wave D range.

**CEO-approved methodological fix along the way (Option B)**: `ai_trader/simulation/harness.py`'s
`strategy_id_filter` was found, before any run, to conflate two concerns — it fed both NEW-signal
eligibility AND time-stop/trailing-stop overlay eligibility for already-open positions, meaning a
demoted strategy's own open position would have silently lost its declared exit protection. Fixed:
overlay eligibility is now derived from the UNFILTERED runtime strategy set; `strategy_id_filter` gates
new-signal eligibility only. Additive, backward-compatible, byte-identical when `strategy_id_filter is
None` (proven by construction and empirically by the full pre-existing regression suite).

**Mechanism**: ONE continuous `SimulationHarness` (never re-instantiated, preserving Market Scanner's
own multi-year session/anchor state) over the full range; 12-month ungated bootstrap; then 32 monthly
(fixed 30-day) re-evaluation checkpoints gating the ACTIVE roster via a new, thin, permanent library
addition, `ai_trader/strategy_health/rolling_gate.py` (`active_strategy_ids_at()`/`health_reports_at()`
— no new scoring logic, pure wrapper around the unmodified `evaluate_strategy_health()`).

**Result**: the ACTIVE roster was **empty at all 32 post-bootstrap checkpoints**. The rolling-gated
portfolio traded only during the 12-month bootstrap (71 trades, 2022-12→2023-12) then went **completely
silent for the remaining ~2.6 years** (0 trades, 2024-01→2026-07-13), vs the static baseline's 513
trades over the same full range. **Root cause: a self-reinforcing lockout** — this strategy population
trades too rarely (median 7 lifetime trades/strategy over 3.6 years; 14/43 never traded at all) to
populate rolling (vs lifetime) windows; once the roster emptied at month 13, no new trades meant no new
Health evidence meant no possible recovery. Confirmed exactly: by 2025-01-09, all 43 strategies show
zero trades in every rolling window simultaneously, for the rest of the backtest. Both the static
baseline (exact reproduction of Wave D) and the rolling-gated run (byte-for-byte across two independent
passes) were proven deterministic. **Classification: VALID NEGATIVE RESULT — METHODOLOGY NOT
OPERATIONALLY VIABLE AS SPECIFIED.** No threshold/weight/shrinkage was changed to reach this
conclusion. Full detail: `PHASE_6_9_ROLLING_HEALTH_GATED_BACKTEST_REPORT.md`.

## 5. Current XAUUSD 12-Month Relevance Audit — CLOSED, VALID NEGATIVE, UNDER-SAMPLED RESULT

**Objective**: a narrower, current-market-only snapshot (NOT a rolling gate, NOT a multi-year
aggregate) — which strategies are relevant to the CURRENT market, using only the most recent complete
12 months.

**Window** (decided before running anything, disclosed conflict-resolution): the literal "most recent
12 months" (ending at the dataset's own last bar, 2026-07-13) would overlap ~87% with the sealed
holdout, so this audit used the most recent COMPLETE 12 months lying entirely OUTSIDE it instead:
**2024-10-23 → 2025-10-23** (365 days, 23,639 M15 bars). Disclosed as NOT fully out-of-sample relative
to strategy discovery (~71% of it is the Research Lab's own validation/OOS segment, ~29% is inside its
own research/fitting segment — only the sealed holdout itself is genuinely unseen, and it was not
used).

**Result**: **0 CURRENTLY_STRONG, 0 CURRENTLY_USABLE, 4 CURRENTLY_WEAK (S1, S39, S44, S46 — the only
strategies with enough recent evidence to be judged at all), 39 INSUFFICIENT_EVIDENCE (20 of which took
literally ZERO trades in the entire 12-month window).** Portfolio tests (A=all 43 / B=STRONG-only /
C=STRONG+USABLE / D=all-except-WEAK, identical $2,000/5%-risk/cost-model/seed=1 config): B and C are
trivially empty (0 qualifying strategies); D numerically beats A on every metric but **94.4% of D's net
profit comes from ONE strategy (S40, itself INSUFFICIENT_EVIDENCE) trading 26× more often purely
because excluding the 4 WEAK strategies freed up the single shared XAUUSD slot** — the third
observation of the Wave D Audit's own non-additive path-dependence finding; A's own result is dominated
by 3 outlier trades (>100% of its net profit) and one outlier month (October 2025 alone = 126% of the
year's total). **No current deployment roster can be justified from this audit.** No strategy was
changed, promoted, or eliminated; the sealed holdout was not opened. Full detail:
`CURRENT_XAUUSD_12M_RELEVANCE_REPORT.md`.

## 6. Phase 6.9A — Strategy Evidence Flow Audit — CLOSED, ROOT CAUSE CONFIRMED

**Objective**: determine WHY strategies fail to accumulate evidence — genuine market rarity, or
suppression at some specific pipeline stage (Signal Engine, Scoring Engine, Risk Manager, execution) —
using the SAME 2024-10-23→2025-10-23 window as the relevance audit, for direct comparability.

**CEO-approved additive instrumentation** (a permanent, tested library change):
`ai_trader/simulation/types.py`'s `RiskEventRecord` gained an optional
`strategy_id: str | None = None` field; `PortfolioSimulator.record_risk_event()` and the two DENY call
sites in `harness.py::_run_one_bar` now forward the triggering decision's own already-existing
`strategy_id`. Additive, backward-compatible, no ALLOW/DENY/sizing/execution change — proven by 5 new
regression tests including a real end-to-end proof (a genuine `DENY_LIMIT_MAX_PER_SYMBOL` event over
4,000 real bars, correctly attributed). No schema version bump needed (internal type only).

**Zero-file-diff funnel-measurement technique** (`phase69a_funnel_recorder.py`, NOT a permanent library
change): monkey-patches an ALREADY-CONSTRUCTED harness instance's own bound methods
(`_signal_engine.evaluate`/`_scoring_engine.score_batch`/`_risk_manager.evaluate`) to tap already-
computed return values — zero lines changed in any `ai_trader/` source file, proven behaviorally
invisible via a full-`SimulationReportData` parity check (an adversarial review caught and this session
fixed a gap where the FIRST version of that check compared only 2 of the report's 6 fields — corrected
and re-verified before the report was finalized).

**Measured, for all 43 strategies**: raw setup detections, the full Signal Engine state breakdown
(actionable/no-signal/wait-confirmation/need-context/blocked/invalid), Scoring Engine conversion, Risk
Manager ALLOW/DENY (shared-slot reason tracked separately from every other denial), order-level fill/
reject/expire/partial counts, completed trades, PLUS an isolated-slot counterfactual (every one of the
43 strategies additionally run completely ALONE, same window/config — 43 more full backtests).

**Result — the single-position XAUUSD architecture is the dominant, measured bottleneck:**
- Only **145 of 1,016,477** Risk-Manager-evaluated opportunities were ever ALLOWED portfolio-wide
  (0.48%).
- The shared-slot constraint (`LIMIT_MAX_PER_SYMBOL`) is the **sole principal suppression cause for
  11/43 strategies** and a contributing factor in 20 of the 22 "mixed" strategies — far more than
  scoring suppression (sole principal cause for only 2/43), genuine risk-policy suppression (0/43), or
  execution suppression (0/43 — zero rejected/expired orders were recorded at all).
- Isolated-slot trade counts summed across all 43 strategies (823) are **5.8× the actual competitive
  count (142)** over the identical market data and window.
- Only 8/43 strategies are genuinely low-frequency at the raw-setup level; the other 35 have
  substantial to massive signal volume that mostly never converts to a trade.

**No governance model was selected or implemented** — this is an observation about where future design
effort has the most measured leverage, not a decision. Full detail, every strategy's own complete
funnel, and honest answers to all 8 CEO-required questions:
`PHASE_6_9A_STRATEGY_EVIDENCE_FLOW_AUDIT_REPORT.md`.

## 7. Phase 6.10 — Edge Portfolio Evidence System — CLOSED (pre-scope diagnostic through Implementation Checkpoint 4)

**Official direction (re-confirmed at this checkpoint)**: Phase 6.10's objective is a generic **Edge
Portfolio** evidence-collection architecture — capable of supporting any validated market edge (New
York Reversal, Opening Range Breakout, London Breakout, Trend Continuation, Asia Range Sweep, Mean
Reversion, Liquidity Reversal, future discoveries) without architectural change — not a system built
around any one strategy. **"Edge" is the same unit the codebase already calls a strategy**: one
`RuntimeEvaluator` subclass registered under one `strategy_id` in `strategy_runtime/registry.py`; S1–S51
already are 43 such edges. **S10 has been used throughout as the first validation target only** —
nothing in any Phase 6.10 artifact names S10 in production code; every claim below was verified
generically (tested with 1 and with 4 simultaneously-configured strategies) before being accepted.

### 7.1 Pre-scope diagnostic — CLOSED

`PHASE_6_10_PRE_SCOPE_DIAGNOSTIC.md` (+ `phase610_prescope_analysis.py`/`.json`) measured same-bar
competition, persistent-position blocking, holding-period structure, signal redundancy, and an
independent-evidence estimate — entirely from existing Phase 6.9A JSON artifacts, no new simulation.
Headline, corrected findings (a CEO consistency check found one real defect, disclosed and fixed, not
hidden — §4.1 of that document): of the 691-position gap between isolated (758) and competitive (117)
positions, persistent blocking is present in **90.4%** of the gap (alone or combined with same-bar
conflict) and same-bar conflict in **45.7%** — these are NOT disjoint; 39.5% of the gap shows both
simultaneously, corrected from an earlier draft that wrongly implied a clean partition. An estimated
**~74% of isolated positions remain economically distinct** even after strict deduplication (the
degenerate upper-bound estimate, 52, is explicitly flagged as unreliable and must not be used).
Recommendation: shadow-mode evidence accumulation as the first concrete design target.

### 7.2 Shadow Evidence Architecture Design + adversarial review — CLOSED, verdict ACCEPTED WITH CONDITIONS

`PHASE_6_10_SHADOW_EVIDENCE_ARCHITECTURE_DESIGN.md` designs (originally, not implements) a system
letting every eligible edge accumulate independent evidence via a per-edge virtual lifecycle, strictly
separated from the real competitive portfolio, reusing `RiskManager`/`ExecutionEngine`/
`ExecutionSimulator`/`PortfolioSimulator` completely unmodified — one fully independent instance set per
edge. Its own §17 adversarial review (direct source inspection, not a plausibility check) found and
corrected, IN the design document itself: `RiskManager` is stateful (not "stateless-per-call" as first
drafted) and requires one dedicated instance per edge, never shared; a silent data-race risk if shadow
code ever touched `RuntimeEvaluator`/handle objects directly (now explicitly prohibited); a silent
order-collision risk if `ExecutionEngine` were ever shared across paths (now a hard per-edge duplication
requirement + a `SHADOW-` id-prefix defense-in-depth); a missing failure-isolation section (added, §10.1);
data contracts revised to extend existing repository types (`TradeRecord`, the `RiskEventRecord`
pattern, `strategy_health`'s own frozen `WindowMetrics`/`ClosedTrade`) rather than reinventing parallel
schemas. **Final verdict: ACCEPTED WITH CONDITIONS** — the architecture is sound and validated against
the real codebase; the conditions are corrections already incorporated into the design, not future work.

### 7.3 Implementation Checkpoint 1A — DONE (structural, behavior-inert)

Added `ai_trader/shadow_evidence/` (new package): `config.py::ShadowConfig` (`enabled: bool = False`);
`types.py`: `ShadowOpportunityRecord`/`ShadowPositionRecord`/`ShadowTradeLegRecord` (the latter embeds
`TradeRecord` verbatim + 2 additive fields), each with `__post_init__` identity-invariant enforcement.
One additive field on `SimulationContext` (`shadow_config`, defaults disabled, no existing caller
affected). No opportunity tap, no virtual risk/execution/position logic — contracts and configuration
surface only. An adversarial self-review found the identity invariant was documented but not enforced;
fixed with `__post_init__` validation + 8 tests proving each invalid combination is rejected.
Commit: `17c312b0818e2ffbb35ed7e81473eb3b8d30fe26`.

### 7.4 Implementation Checkpoint 1B — DONE (the generic, read-only pipeline tap)

Added `ai_trader/shadow_evidence/engine.py::ShadowEvidenceEngine`: for every edge in `ShadowConfig.
active_strategy_ids()` (a plain `frozenset[str]`, no edge named in code), taps the already-computed
`score_batch`/`risk_context` (Signal/Scoring Engine remain called exactly once per bar, unchanged — no
`RuntimeEvaluator` call, no re-scoring) and evaluates a dedicated per-edge `RiskManager` against a
structurally empty per-edge `PortfolioState` (no virtual position exists in this checkpoint by design).
Produces `ShadowOpportunityRecord` for every score and `ShadowRejectionRecord` on DENY. Two-layer
failure isolation (a per-edge try/except inside `observe()`, plus an outer defense-in-depth try/except
at the harness call site, the latter added after this checkpoint's own adversarial review found the
inner boundary alone insufficient). The one existing frozen-pipeline file touched: `ai_trader/
simulation/harness.py` (one import, one attribute, one guarded construction site, one tap call site).

**Proven, not asserted, generic**: `test_shadow_enabled_for_multiple_strategies_still_produces_byte_
identical_competitive_execution` enables Shadow for `("S10","S21","S39","S40")` simultaneously and
passes identically to the single-edge case. Competitive execution (full `SimulationReportData`, trade
ledger, risk events, orders) is byte-identical whether Shadow is disabled, enabled for one edge, or
enabled for four, at both an 85-day pytest-fixture scale and the full 13-month/23,639-bar Phase 6.9A
window (142 competitive trades both ways, matching Phase 6.9A's own published count exactly).

**S10's own shadow funnel, validated against Phase 6.9A** (`phase610_checkpoint1b_s10_validation.py`/
`.json`, full window): 23,639 opportunities (exactly `total_bars_evaluated`); NOT_ACTIONABLE (22,136),
BELOW_FLOOR (588), INVALID_INPUT (61) match the competitive run bit-for-bit (confirming shadow reuses
competitive-context scoring, never re-scores in isolation); LIMIT_MAX_PER_SYMBOL and
COOLDOWN_AFTER_LOSS are exactly zero (confirming the always-empty per-edge portfolio never sees a
shared-slot or cooldown denial — vs. competitive's 706/14 and isolated's own 50/5). The one unpredicted
figure, SIZE_BELOW_MIN (780 vs. competitive's 128, isolated's 1261), was fully explained via
`risk_manager/sizing.py` by exact arithmetic reconciliation (854 = 74 ALLOW + 780 SIZE_BELOW_MIN = 1503
actionable − 588 − 61; 134 = 6 + 128 = 854 − 720 portfolio-gate denials shadow never experiences) — not
forced or asserted away. Commit: `52446324cf5c1307d9ff05fde75da67aceb7c7f0`.

### 7.5 Edge Portfolio direction — architectural re-frame (documentation only, no code)

`PHASE_6_10_EDGE_PORTFOLIO_DIRECTION.md`: confirms, with evidence rather than assertion, that
Checkpoints 1A/1B already ARE the generic Edge Portfolio architecture, and walks the scaling story 1
edge → 5 → 43 strategies → N edge families (config-only changes at every step; zero code change,
provided a new edge is registered the same way S1–S51 already are). Maps the required 7-stage lifecycle
(opportunities/virtual positions/virtual executions/trade history/statistics/health/portfolio
contribution) onto: **DONE** (opportunities), **designed, not implemented** (positions/executions/
statistics — contracts exist since 1A, `ShadowStrategySummary` designed to reuse `strategy_health`'s
own frozen metrics code), **unselected** (health — 3 options compared in the design doc §11, none
chosen), **undesigned** (capital allocation across edges — the largest remaining gap to the stated
"AI Portfolio Manager" end goal; no document to date proposes an architecture for this). Commit:
`c4707d30944c3be0168ce425800373048378242c`.

### 7.6 Official Phase 6.10 project checkpoint save (2026-07-17, documentation only)

Commit `32705567b228ee7de36bf6d2342d946f8ef06221`. The checkpoint save this document's own §0 previously
described as current: refreshed `PROJECT_STATE_v2.md` §0/§7, rewrote `NEXT_SESSION.md` in full, created
`RECONSTRUCTION_PROMPT.md` for the first time, created `PHASE_6_10_CHECKPOINT_SAVE_REPORT.md`. No code
implemented. Checkpoint 1C confirmed NOT STARTED, NOT AUTHORIZED as of this save.

### 7.7 Implementation Checkpoint 1C — DONE (full virtual position lifecycle) — CEO-CLOSED WITH A
DOCUMENTED SEMANTIC LIMITATION

**Authorization**: after a CEO-presented implementation plan was reviewed and approved (no code written
until that approval), Checkpoint 1C was officially authorized to implement the complete generic Shadow
Virtual Execution lifecycle — virtual entry/exit/position tracking/failure isolation — reusing the
frozen `RiskManager`/`ExecutionEngine`/`ExecutionSimulator`/`PortfolioSimulator` classes unmodified, one
fully independent instance set per edge, never touching the real competitive path.

**Implementation** (commit `1f0ec84596951ea83dc65df053c2a9a7ee4e594c`): `ai_trader/shadow_evidence/
engine.py` gained `_ShadowAccount` (dedicated risk_manager/execution_engine/execution_simulator/
portfolio_simulator/pending_entries/open_position_id per edge), a `SHADOW-CID`/`SHADOW-REQ` client/
order-id discriminator prefix (`ExecConfig`), deferred opportunity resolution (`_PendingEntry` — entry
price unknown until fill confirmed), exit-reason classification purely from client_order_id markers
(`-TP`/`-SL`/`TIMESTOP-`/`TRAILSTOP-`/`CLOSE-AT-END-`, never inferred ambiguously), and the full
observe/apply_time_stops/apply_trailing_stops/settle_bar/finalize_at_end lifecycle. `ai_trader/
simulation/harness.py` gained two new shadow call sites (time-stop/trailing-stop overlays, and
settle_bar after mark-to-market), each independently failure-isolated; `_finalize_at_end()` restructured
so the shadow engine's own finalization runs even when the real competitive portfolio holds zero open
positions. **Position-identity invariant enforced throughout**: one `ShadowOpportunityRecord` maps to
zero-or-one `ShadowPositionRecord`; all legs of one position share one `position_id`.

**Validated**: competitive execution byte-identical throughout (full `SimulationReportData` parity, 1
and 4 simultaneously-shadowed edges, 85-day and full 13-month scales). An S10 isolated-ledger validation
script (`phase610_checkpoint1c_s10_validation.py`/`.json`) compared the shadow S10 ledger against Phase
6.9A's own independently-verified isolated-run ground truth and found a REAL divergence (only 2 of 117
trades matched exactly; 68 shadow trades total) — disclosed, not hidden.

**CEO ruling on the divergence (2026-07-18, binding on all future work in this package)**: Checkpoint
1C is **ACCEPTED WITH A DOCUMENTED SEMANTIC LIMITATION**, not a defect. The validated semantics: "Shadow
Evidence evaluates how a configured strategy would execute from the conflict-adjusted `score_batch`
produced inside the competitive run. It does not reconstruct how that strategy would score and trade in
a fully isolated run with no same-bar strategy conflicts." Standing constraints from this ruling: do NOT
add isolated re-scoring to `ShadowEvidenceEngine`; do NOT modify competitive scoring/execution to chase
closer isolated-ledger agreement; exact isolated-strategy equivalence is a separate future research/
architecture question, only if the CEO ever chooses to open it. A required documentation-only follow-up
commit (`888986d69330078263d7e1a5238ced341384a272`) corrected `PHASE_6_10_CHECKPOINT_1C_REPORT.md` and
struck the original design doc's own §7/§14 language implying the divergence was bounded by a "minor
cooldown tolerance" (§19 of `PHASE_6_10_SHADOW_EVIDENCE_ARCHITECTURE_DESIGN.md` records the correction
verbatim). Checkpoint 1C closed only after this clarification commit landed.

### 7.8 Implementation Checkpoint 2 — DONE (generic multi-edge statistics + aggregation layer)

Commit `fdab31dcce50c35596ad9a5898e7507f6bf1d70d`. Evolved Shadow Evidence from single-edge virtual
execution into a generic multi-edge evidence platform: `ai_trader/shadow_evidence/aggregation.py` (new)
— pure functions (`strategy_ids_observed`, `summary_for`, `all_summaries`) taking already-recorded
public engine lists as explicit arguments, never touching engine internals; `ShadowStrategySummary`
(new type, `__post_init__`-guarded) reusing `strategy_health.metrics.compute_window_metrics()`
unmodified — pure statistics only, never `scoring.py`/`classifier.py`/`evaluator.py`, never
`HealthState`/`WindowScore` (that boundary was explicit and verified by grep before committing). Most of
Checkpoint 2's own named requirements (concurrent multi-strategy execution, isolation, determinism) were
already satisfied by Checkpoint 1C — re-verified, not re-implemented; only the statistics/aggregation
piece was genuinely new. `harness.py` NOT touched (the aggregation layer is a pull-based query, already
reachable via the public `harness.shadow_engine` attribute).

### 7.9 Implementation Checkpoint 3 — DONE (first production strategy set: all 43, at real scale)

Commit `e360da2d1ec8344aef9ad268d0dc92805df36ab3`. Registered the first production strategy set — all 43
currently-registered strategies (`shadow_evidence.config.all_registered_strategies()`, new helper,
imports `strategy_runtime.families` then calls `registry.registered_strategy_ids()` — no strategy
hand-picked). **Running Shadow at real scale (vs. the 1–4-strategy scale every prior checkpoint tested)
found and fixed a genuine bug invisible at small N**: a strategy's shadow entry is often a LIMIT-priced
BRACKET order that can stay pending for many bars; `LIMIT_MAX_PER_SYMBOL` only sees OPEN positions,
never pending orders, so the same `RiskManager` could legitimately ALLOW a second entry for the same
symbol while the first was still unresolved — `_observe_one`'s own `account.pending_entries[symbol]`
dict used to silently overwrite the first order's tracking record, orphaning its eventual fill
(manifesting as "closing TradeRecord with no tracked open position_id" for strategies S1/S6). Fixed by
denying the second entry with a new, disclosed reason code `SHADOW_ENTRY_ALREADY_PENDING` (never
silently dropped) — the real competitive portfolio was never at risk (it has no equivalent side table).
**Standing lesson for this project: an architecture proven correct at N=1/N=4 is not automatically
correct at N=43 — race conditions in bookkeeping-only code can hide behind low signal density until
scale exposes them.**

### 7.10 Implementation Checkpoint 4 — DONE (Strategy Research & Comparison layer)

Commit `b1bd95314cf6d3d3bd8d07ac57bc4c3099ed0669`. Three new, standalone, pure-function modules built ON
TOP of the Shadow platform, entirely read-only/pull-based: `shadow_evidence/research.py`
(`StrategyResearchSummary` — 12 named metrics: 7 reused from `strategy_health.metrics`'s own frozen
`WindowMetrics`, 5 new — Sharpe ratio, best/worst month, long-vs-short split, longest winning streak),
`comparison.py` (`rank_by`/`compare`/`leaderboard`/`export_summary` — single-metric deterministic sorts
ONLY, never a weighted composite — the whole point of this checkpoint's scope boundary vs. Strategy
Health's own scoring), `portfolio_research.py` (correlation matrix, trade overlap, simultaneous
exposure, diversification — no PCA/eigen-decomposition anywhere, deliberately). Because this layer never
touches engine internals, `engine.py`/`harness.py` are BOTH byte-for-byte unchanged by this checkpoint.
N=43 genericity verified with fast SYNTHETIC fixtures rather than paying for another real 43-strategy
harness run (this layer's correctness doesn't depend on how the underlying data was produced, already
proven at N=43 by Checkpoint 3).

### 7.11 Phase 6.10 status: CLOSED

**Every sub-phase of Phase 6.10 (Edge Portfolio Evidence System) is now CLOSED/DONE**: pre-scope
diagnostic, Shadow Evidence Architecture Design + adversarial review (ACCEPTED WITH CONDITIONS), the
official checkpoint save, Implementation Checkpoints 1A/1B/1C/2/3/4, the Edge Portfolio direction
re-frame. The generic Shadow Evidence platform is feature-complete for its own originally-scoped 7-stage
lifecycle through "statistics" (opportunities → virtual positions → virtual executions → trade history →
statistics/research/comparison are all DONE; Strategy Health integration policy remains UNSELECTED;
capital allocation across edges remains UNDESIGNED — both explicitly out of scope for every Phase 6.10
checkpoint and never authorized). **Phase 6.10 requires no further checkpoints unless the CEO explicitly
reopens it** (e.g. to select a Health integration policy or design capital allocation) — Phase 7 (§8
below) is a deliberate pivot to a different layer of the system (market/edge understanding, not
statistics/allocation), not a continuation of Phase 6.10's own remaining gaps.

## 8. Phase 7 — AI Trader Intelligence Layer (Checkpoints 5–7, 2026-07-19)

**Official direction**: a deliberate pivot from infrastructure to intelligence, per the CEO's own Phase
7 opening framing (preserved verbatim in `PHASE_7_CHECKPOINT_5_REPORT.md` §1 and in memory): "We are NOT
building a rule-based trading bot. We are NOT building a collection of independent strategies. We are
building an AI Trader" that must OBSERVE, UNDERSTAND, EVALUATE, DECIDE and continuously LEARN, targeting
~2–4 trades/day, high win rate, quality over quantity, never trading just because a setup exists.
Checkpoints 5, 6, and 7 are the first three components of that reasoning process: Market Intelligence
(OBSERVE/UNDERSTAND) and Edge Intelligence (recognize) are purely read-only recognition layers; Decision
Intelligence (EVALUATE/DECIDE) is the first layer that actually produces a recommendation rather than a
description — but it still never trades, and none of the three is wired into `harness.py` or any
execution path.

**Naming disambiguation (read carefully — these are two different concepts sharing similar words)**:
Phase 6.10's "**Edge Portfolio**" (§7 above) is the generic multi-strategy Shadow virtual-execution and
statistics PLATFORM — "edge" there means "one registered `strategy_id`/`RuntimeEvaluator`," and the
system's job is running/tracking many of them independently. Phase 7's "**Edge Intelligence**" (§8.2
below) is a NEW, separate, read-only RECOGNITION layer built on top of that platform's own already-
registered strategy set — its job is answering "which of those strategies' statistical edges currently
exist in THIS market moment," never executing or tracking anything itself. They are architecturally
unrelated beyond both reading from the same Strategy Library; `edge_intelligence/` does not import
`shadow_evidence` at all (by deliberate design, verified by grep — see §8.2).

### 8.1 Checkpoint 5 — Market Intelligence layer — DONE

Commit `8e2748a7980d2447fc3b33b8c9d96192d17f3450` (implementation) + `a68ac1fe1b429acb7b471eaf3705fc57354f0478`
(documentation-only follow-up recording the commit's own hash in its report). Adds `ai_trader/
market_intelligence/` (12 source files + 13 test files) — a pure, read-only function,
`build_market_intelligence(context) -> MarketIntelligenceSnapshot`, answering exactly one question,
continuously: **"What is the market doing right now?"** — never "what trade should I take?" No BUY, no
SELL, no execution, no optimization, no portfolio decisions, no health classification.

Nine market dimensions, each independent and explainable: Trend (per M15/H1/H4/D1 timeframe), Market
Structure (fractal swing-point detection + BOS/CHoCH break classification — **the one genuinely new
algorithm in this checkpoint**, since nothing centralized existed for it), Momentum (per timeframe RSI-
based), Volatility regime, Liquidity behaviour, Expansion vs. Compression, Session behaviour,
Multi-timeframe agreement, Context confidence. Every dimension except Structure reuses this repo's own
already-computed `market_scanner` features verbatim (`m_trend_up`/`h1_trend_up`/etc., `m_rsi`, `m_atr`/
`atr_ma`, `m_volrank`, `compress`/`disp`, `session`/`or_high`/`or_low`/`vwap`/`gap`) — never a new
indicator invented. Deliberately did NOT import concepts from the sibling `AI-Research-Lab`/
`ai_quant_lab` project's own Trend/Volatility/Structure research (standing repo-reconstruction rule
against using other repos, plus this layer is intentionally more mechanical/technical-analysis-style
than that project's own slow, human-verified epistemology).

**Validated**: `pytest ai_trader/ -q` → 1752 passed (Checkpoint 4 baseline 1690 + 62 net new, zero
regressions); `mypy --strict ai_trader/ --exclude 'tests/'` → clean, 185 source files (up from 173);
coverage 96% package-wide unchanged despite +363 new statements, every new module 100% individually. A
real-data integration test drives the actual `MarketScanner`/`ReplayDataSource` over real XAUUSD data
(`ai_trader/market_intelligence/tests/test_integration.py`). Full detail: `PHASE_7_CHECKPOINT_5_REPORT.md`.

### 8.2 Checkpoint 6 — Edge Intelligence layer — DONE

Commit `b94c93f1748f71a08657b5fb348ac240def5f17e` (implementation) + `6e3c4ce922baaa2f4008214021e34da7d062b746`
(documentation-only follow-up recording the commit's own hash). Adds `ai_trader/edge_intelligence/` (9
source files + 11 test files) — a pure, read-only function, `evaluate_edges(context) ->
EdgeIntelligenceSnapshot`, answering: **"Which validated statistical edges currently exist?"** — for
every one of the 43 registered production strategies, independently. `present_strategy_ids(snapshot)`
is the clean, execution-decoupled query surface a future Decision AI is meant to call.

For each strategy, produces a `StrategyEdgeReading` carrying one of three states — **PRESENT / POSSIBLE
/ ABSENT** — plus the exact tuple of six `EdgeEvidenceItem`s (each with a concrete, disclosed
explanation string) that produced it: `data_availability`, `directional_trend_alignment` (the strategy's
own DECLARED `Contract.execution.long_short` vs. the Market Intelligence trend reading on its own
execution timeframe), `session_suitability` (`Contract.execution.sessions` free text vs. the current
session — only a small, disclosed set of known session-name tokens is parsed; anything unparseable
honestly reports UNKNOWN, never guessed), `context_confidence`, `multi_timeframe_agreement`,
`volatility_regime`. **Verdict rule (deterministic, disclosed)**: any CONTRADICTS → ABSENT; else any
UNKNOWN → POSSIBLE; else any SUPPORTS → PRESENT; all-NEUTRAL → POSSIBLE (never PRESENT on zero real
supporting evidence). **Deliberately does NOT produce per-strategy Structure/Liquidity evidence**
(despite both being named in the CEO's own example list) because `Contract.semantics.market_regime.
applicable/avoid` is universally `["ANY"]`/`[]` across all 43 real contracts (grep-verified empirically,
not assumed) — inventing a mapping from free-text `mechanism`/`klass` prose would itself be the "AI
guess" the CEO's own directive explicitly forbade; both dimensions remain fully available on the Market
Intelligence snapshot for a future checkpoint once/if strategies declare real requirements for them.

Reads strategy contracts via `ai_trader.strategy_manager.loader.load_all` directly (never
`StrategyManager` — no Market Scanner handshake needed for a read-only layer) and gets registered ids
via `strategy_runtime.registry.registered_strategy_ids()` directly (never imports `shadow_evidence` at
all — tighter isolation than even Checkpoint 3's own `all_registered_strategies()` helper).

**Validated**: `pytest ai_trader/ -q` → 1798 passed (Checkpoint 5 baseline 1752 + 46 net new, zero
regressions); `mypy --strict ai_trader/ --exclude 'tests/'` → clean, 194 source files (up from 185);
coverage 96% package-wide unchanged despite +164 new statements, every new module 100% individually (2
real coverage gaps found on the first full-suite run — `context.py`'s `score is None` branch, `types.py`'s
empty-evidence guard — both closed with targeted tests before the final, reported run). A real-data
integration test drives `evaluate_edges()` against the REAL Strategy Library (not a synthetic override)
over real XAUUSD data and confirms all three `EdgeState` values genuinely appear (not a silently-
collapsed verdict). Full detail: `PHASE_7_CHECKPOINT_6_REPORT.md`.

### 8.3 First Official Project Save (2026-07-19, after Checkpoint 6)

CEO-directed, before any further Phase 7 implementation: a documentation and repository-freeze
checkpoint synchronizing every official state document (this one, `NEXT_SESSION.md`,
`RECONSTRUCTION_PROMPT.md`, `CHANGELOG.md`, `PROJECT_AUDIT.md`) to reflect the completion of Phase 6.10
in full and Phase 7 Checkpoints 5–6. No code implemented, no architecture changed. Commit
`952b2c73e4833c084b3b8e43dae749037f9d8e34`. Full detail: `PHASE_7_OFFICIAL_PROJECT_SAVE_REPORT.md`.

### 8.4 Checkpoint 7 — Decision Intelligence layer — DONE

Commit `0346e070967228b35c87659a34a829f4aa5cda8f` (implementation) + `d2d75de509087892241b6ade4f78de18b7051ea7`
(documentation-only follow-up recording the commit's own hash). Adds `ai_trader/decision_intelligence/`
(5 source files + 8 test files) — the AI Trader's **first reasoning layer**. Market Intelligence
describes the market; Edge Intelligence identifies which edges are currently PRESENT; Decision
Intelligence answers: **"Which edge, if any, deserves execution?"** Public entry point
`make_decision(context) -> DecisionReport`; `recommended_or_no_trade(report)` is the clean,
execution-decoupled query surface — "what is the best decision right now?"

For every currently-PRESENT edge (Edge Intelligence's own scope, reused as-is, never modified), applies
**four disclosed, deterministic eligibility gates, all sourced from already-declared metadata, none
invented**: `Contract.lifecycle.status` must be IMPLEMENTED; `lifecycle.maturity` must not be RETIRED
(reusing the existing `maturity_rank()` helper from `strategy_manager.contract`, never a new ordering);
`evidence.confidence.level` must not be NONE or NEGATIVE; and — only if the caller supplies research
statistics for that strategy — historical `expectancy_r` must not be non-positive (a strategy with zero
recorded trades never trips this gate, since absent evidence is a different fact from negative evidence).
A candidate that clears every gate is **ACCEPT**; the first gate that trips produces **REJECT** with a
concrete, disclosed explanation. ACCEPT candidates are then ranked by a fully deterministic tie-break
chain — maturity → declared confidence → historical expectancy_r → strategy_id ascending (the same
final-tie-break convention `shadow_evidence/comparison.py` established at Checkpoint 4) — and the
top-ranked candidate becomes the recommendation, or explicitly **NO TRADE** (a valid decision, never an
error) when zero candidates ACCEPT. `comparison_notes()` narrates, pairwise, WHY each ranked candidate
outranks the next (or discloses a genuine tie), satisfying the CEO's own "why stronger/weaker than
competing edges" requirement without any invented scoring.

**Key design decision, worth remembering precisely**: "research statistics" is deliberately NOT sourced
via `shadow_evidence.types.StrategyResearchSummary` — the CEO's own Checkpoint 7 directive requires
`decision_intelligence` to be "completely independent from ... Shadow Evidence," so a new, LOCAL,
minimal `ResearchStats` type (`n_trades`/`win_rate`/`expectancy_r`/`sharpe_ratio`) was defined instead; a
caller with richer Shadow-Evidence-derived statistics is responsible for adapting them into this shape
before calling `make_decision()` — this package never imports `ai_trader.shadow_evidence` at all
(grep-verified). The same independence was verified for Signal Engine, Scoring Engine, Risk Manager,
Execution Engine, and MT5 — zero imports of any of them, zero reference to `decision_intelligence` in
`harness.py`.

**Validated**: `pytest ai_trader/ -q` → 1830 passed (Checkpoint 6 baseline 1798 + 32 net new, zero
regressions); `mypy --strict ai_trader/ --exclude 'tests/'` → clean, 199 source files (up from 194);
coverage 96% package-wide unchanged despite +103 new statements, every new module 100% individually (3
real coverage gaps found on the first full-suite run — a ranking comparison-notes branch, both
`ResearchStats`/`DecisionCandidate` `__post_init__` guards — all closed with targeted tests before the
final, reported run). A real-data integration test drives `make_decision()` against the REAL Strategy
Library (no synthetic override, no `research_stats` supplied) over real XAUUSD data and confirms both
ACCEPT and REJECT outcomes genuinely occur among real candidates (NO TRADE itself did not occur within
that particular 20-bar window — disclosed as expected given the current Library's static contract
metadata, not a defect; separately proven reachable by the unit-level `test_engine.py` tests). Full
detail: `PHASE_7_CHECKPOINT_7_REPORT.md`.

### 8.5 Second Official Project Save (2026-07-19, this document's own current update, after Checkpoint 7)

CEO-directed, before any further Phase 7 implementation: a documentation and repository-freeze
checkpoint synchronizing every official state document (this one, `NEXT_SESSION.md`,
`RECONSTRUCTION_PROMPT.md`, `CHANGELOG.md`, `PROJECT_AUDIT.md`) to reflect the completion of Checkpoint
7 (Decision Intelligence). No code implemented, no architecture changed. Full detail:
`PHASE_7_CHECKPOINT_7_OFFICIAL_SAVE_REPORT.md`.

### 8.6 Checkpoint 8 — Context Memory architecture design — DESIGN ONLY, ACCEPTED

Commit `263b950d498c2f431e958c3ce09c85676d85838f`. CEO authorization: design (not implement) a **Context
Memory** system letting future components compare the current market context against historical
contexts and retrieve contextual evidence about edge performance — explicitly excluding any final
similarity algorithm, production code, or modification of any existing package. Deliverable:
`PHASE_7_CHECKPOINT_8_CONTEXT_MEMORY_DESIGN.md` (17 sections + 10 Q&A) — Context Snapshot/Outcome
contracts, storage architecture, identity/versioning scheme, a comparison of 6 similarity approaches
(recommending deterministic hierarchical relaxation, explicitly rejecting weighted-distance and k-NN),
temporal-safety/leakage rules, the Contextual Evidence output contract, the Decision Intelligence v2
integration boundary, a 13-item failure-mode/red-team analysis, sample-sufficiency discussion, a testing
plan, and a proposed Checkpoint 9–13 decomposition. **Core architectural principle, binding on every
later checkpoint: Context Memory must NEVER output BUY/SELL/entry/stop/target/size/execution/a final
recommendation — evidence only.** No code was written; no existing package was touched. Verdict:
**ACCEPTED** as the governing architecture for Checkpoints 9–13.

### 8.7 Checkpoint 9 — Context Memory immutable contracts and deterministic identities — DONE

Commit `30213d0adf5c3fb6f2d860a84c8a81bc4b848cb2`. First implementation slice, authorized only after
Checkpoint 8's design was committed. New, fully isolated package `ai_trader/context_memory/` (5 source
files: `__init__.py`, `enums.py`, `contracts.py`, `validation.py`, `identities.py`) — immutable public
data contracts (`ContextSnapshot`, `PresentEdgeReference`, `Observation`, `Outcome`), controlled
vocabularies LOCALLY mirroring Market Intelligence's 7 regime enums / Edge Intelligence's `EdgeState` /
`market_scanner`'s `DataQualityLevel` (never imported live — package independence + historical
interpretability across future upstream schema changes), a generic `SchemaVersion(namespace, version)`
type serving all 6 version kinds, and deterministic SHA-256-over-canonical-JSON identity generation
(`hashlib` only — never Python's built-in `hash()`, never `uuid`, never clock/filesystem state). Not
wired into `harness.py` or any other package; storage/retrieval/similarity/aggregation explicitly NOT
implemented. **Validated (TARGETED, not full-suite)**: 92 tests, 100% coverage, `mypy --strict` clean (5
source files), import-independence AST scan clean.

### 8.8 Checkpoint 10 — Append-Only Context Repository — DONE

Commit `486aa61de180d8d0daca0b4bd14fe1938d5f566c`. First of the CEO's batch-authorized Checkpoints
10–13 ("Context Memory Functional Buildout," executed sequentially without re-authorization between
them, each independently validated and committed). Adds `codec.py` (canonical encode/decode for every
contract) and `repository.py` (`ContextMemoryRepository` — append-only, one JSON Lines file per record
type: `context_snapshots.jsonl`/`observations.jsonl`/`outcomes.jsonl`; `PresentEdgeReference`
deliberately NOT independently persisted — it only has meaning nested inside an `Observation`).
Integrity IS identity (no separate hash field — verification recomputes each record's own ID from its
decoded payload); idempotent-exact-duplicate / `ConflictingDuplicateError`-on-conflict policy; a
documented single-writer-process contract plus in-process `threading.Lock` per stream. **Validated**:
132 tests, 100% coverage (7 modules, 518 stmts), `mypy --strict` clean.

### 8.9 Checkpoint 11 — Episode Collapsing and Historical Index — DONE

Commit `9d273c49b000d6aaa1c0361c92c131225b04465d`. Adds `episodes.py` (deterministic episode collapsing:
a maximal contiguous run of `as_of`-sorted Observations per instrument sharing the same categorical
`StateFingerprint` AND the same PRESENT-edge set is one Episode — prevents a persistent multi-hour
regime from inflating apparent sample size) and `index.py` (`HistoricalIndex` — a rebuildable, in-memory
derived structure over the Checkpoint 10 repository: deterministic AND-filter observation queries,
episode queries, and `outcomes_for_observation(..., visible_as_of=...)` implementing temporal safety — a
resolved-in-the-future outcome is invisible before its own resolution time, never re-labeled as
pending). Deliberately NO maximum-temporal-gap split rule (no bar-interval field exists on
`ContextSnapshot` to define one without an arbitrary threshold — disclosed limitation, not an
oversight). `IndexStatistics.episode_count` explicitly labeled a conservative effective-observation
proxy, never claimed to be a mathematically exact effective sample size. **Validated**: 173 tests, 100%
coverage (9 modules, 672 stmts), `mypy --strict` clean.

### 8.10 Checkpoint 12 — Deterministic Context Retrieval — DONE

Commit `cf36e9879aed56c61011aad7d538e9ee48a53f2e`. Adds `retrieval.py`: `retrieve(index, query) ->
RetrievalResult` implementing the Checkpoint 8 design's own §8 fixed-priority relaxation ladder
**verbatim** — `session_state → expansion_state → liquidity_state → momentum_d1 → momentum_h4 →
momentum_h1 → momentum_m15 → trend_d1 → trend_h4 → trend_h1 → trend_m15`, floor = `instrument` +
`structure_state`/`volatility_regime`/`multi_timeframe_agreement` (never relaxed) — no weighted
distance, no k-NN, no embeddings, no clustering anywhere. Six explicit result statuses (`SUCCESSFUL`,
`NO_ELIGIBLE_HISTORY`, `NO_SUFFICIENTLY_SIMILAR`, `INCOMPATIBLE`, `DEGRADED_DATA`,
`UNSUPPORTED_VERSION`). **The minimum-sample sufficiency threshold is deliberately left unresolved here**
(the accepted design's own §17 open question) — a tier is accepted as soon as it yields ≥1 eligible
episode; whether that evidence is *enough* is explicitly deferred to Checkpoint 13. Deterministic
recency-first ordering with `EpisodeId` as the final tie-break. **Validated**: 198 tests, 100% coverage
(10 modules, 779 stmts), `mypy --strict` clean.

### 8.11 Checkpoint 13 — Contextual Evidence Aggregation — DONE

Commit `24457858c9c0da7d3b6b65f1e16d0589575c37df`. Adds `evidence.py`: `aggregate_evidence(index,
retrieval, strategy_id, policy) -> ContextualEvidenceReport` — per-edge, episode-collapsed outcome
statistics (mean/median/sample stdev/95% normal-approximation CI via stdlib `statistics.NormalDist`/
win-rate/sign counts) and a controlled `EvidenceStatus` (`SUFFICIENT`/`LIMITED`/`CONTRADICTORY`/
`STALE`/`UNAVAILABLE`/`INCOMPATIBLE`) derived by a fixed priority chain. **Both thresholds are grounded
in already-validated project convention, not invented**: the `SUFFICIENT` boundary reuses
`code/alpha_lab.py`'s own live `MINTR = 25` minimum-trade-count gate verbatim (`EvidencePolicy` is an
explicit, versioned, caller-overridable object); `CONTRADICTORY` reuses this project's own established
"UNRESOLVED if the CI straddles zero" convention (`PROJECT_AUDIT.md` §A0/§28) rather than a new rule; no
staleness threshold is invented (disabled unless a caller explicitly supplies one). Every report
unconditionally discloses that its CI is a descriptive normal-approximation, not a validated bootstrap
(`PROJECT_AUDIT.md` D1's own prior finding about this exact class of approximation error, reused as a
caveat here). **Produces evidence reports only — never a BUY/SELL/entry/stop/target/size/execution
output, never an edge ranking.** `aggregate_evidence`/`aggregate_all_present_edges`/
`ContextualEvidenceReport`/`EvidencePolicy`/`EvidenceStatus` are the only names exported for future
Decision Intelligence v2 consumption. **Validated**: 221 tests, 100% coverage (11 modules, 934 stmts),
`mypy --strict` clean.

### 8.12 Combined Context Memory validation + full-repository validation — PASSED

After all four Checkpoints 10–13 closed independently (each its own commit, each its own targeted
validation), one combined check ran across the whole `context_memory` package (all 221 tests, `mypy
--strict` on 11 source files, 100% package-wide coverage — 934/934 statements, zero exceptions needed)
— **TARGETED CONTEXT MEMORY VALIDATION PASSED**. Then, justified once because four checkpoints were
closing together as a batch, the complete repository suite ran ONCE: `pytest ai_trader/ -q` → **2051
passed** (zero failures, zero regressions against the Checkpoint 7 baseline of 1830), `mypy --strict
ai_trader/ --exclude 'tests/'` → clean on 210 source files (up from 199), `coverage run --source=
ai_trader -m pytest ai_trader/ -q` then `coverage report` → **TOTAL 11813 stmts, 432 miss, 96%** — the
432-miss figure is the exact same absolute count carried since Implementation Checkpoint 1B, unchanged
across every phase since, confirming zero coverage regression anywhere outside the newly-added,
100%-covered Context Memory package — **FULL REPOSITORY VALIDATION PASSED**.

### 8.13 Third Official Project Save (2026-07-20, this document's own current update, after Checkpoints 10–13)

CEO-directed, before any further Phase 7 implementation: a documentation and repository-freeze
checkpoint synchronizing every official state document (this one, `NEXT_SESSION.md`,
`RECONSTRUCTION_PROMPT.md`, `CHANGELOG.md`, `PROJECT_AUDIT.md`) to reflect the completion of the full
Context Memory subsystem (Checkpoints 8–13). No code implemented, no architecture changed, no existing
package modified. Full detail: `PHASE_7_CHECKPOINTS_10_13_OFFICIAL_SAVE_REPORT.md`.

### 8.14 Checkpoint 14 — Decision Intelligence v2 — Context Memory Integration — DONE

Commit `dbcdb666ab7bbaffc3d19675fea13685844562e5`. CEO batch authorization ("Phase 7 Checkpoints 14–15,
authorized consecutively"). New, SEPARATE package `ai_trader/decision_intelligence_v2/` (5 source files:
`adapters.py`, `types.py`, `explanation.py`, `engine.py`, `__init__.py`) wraps Decision Intelligence v1
(`ai_trader/decision_intelligence/`, called UNCHANGED) and attaches, per candidate, an explainable
Context Memory evidence report. **Decision Intelligence v1 is neither modified nor replaced** — 0-diff
confirmed since Checkpoint 7. `DecisionReportV2.__post_init__` structurally enforces
`recommended_strategy_id == v1_report.recommended_strategy_id` — not a convention, a construction-time
invariant, proven live over 20 real XAUUSD bars. `adapters.py::build_context_snapshot` bridges a real
`MarketIntelligenceSnapshot` into Context Memory's own local `ContextSnapshot` (the adapter Checkpoint
9's own `PresentEdgeReference` docstring anticipated). Per the CEO's own explicit rules, Context Memory
in this integration never changes eligibility, ranking, scoring, Risk, Position Sizing, or Execution, and
never generates BUY/SELL — verified structurally (embedding v1's own candidates by reference) and by a
5-test static scan (no forbidden import, no repository-write call, no order/BUY/SELL vocabulary
anywhere in the package). Every attachment discloses why the context was found, what evidence exists,
what limitations apply, and why the evidence status is what it is — no opaque algorithm. **Disclosed
limitation**: Context Memory's own repository holds no real AI Trader historical observations yet — this
checkpoint validates the integration MECHANISM with synthetic repository data; real historical
population is a separate, unauthorized future undertaking. **Validated**: 26 tests, 100% coverage (5
modules, 95 stmts), `mypy --strict` clean.

### 8.15 Checkpoint 15 — Decision Intelligence v1 vs v2 Falsification Study — DONE

Commit `069c47948982a82f3a2b801ff60954f28a931d8c`. New, read-only package `ai_trader/decision_comparison/`
builds the complete comparison framework across every CEO-named dimension (final recommendation, NO
TRADE frequency, edge selection, expectancy, win rate, drawdown, false positives, false negatives,
stability, regime robustness, confidence calibration, explanation quality) — never modifies v1, v2, or
Context Memory. **Central finding, a proof rather than an assumption**: under Checkpoint 14's own
architecture, v2's recommendation stream is construction-time-identical to v1's, so every trade-outcome
dimension (recommendation, NO TRADE frequency, edge selection, expectancy, win rate, drawdown, false
positive/negative rate, recommendation-level regime robustness) is PROVABLY identical between v1 and v2
— stated explicitly in `trade_outcome_proof.py` rather than re-confirmed via a redundant multi-hour
backtest, and verified directly (not assumed) over 20 real XAUUSD bars: 0 divergences. Two dimensions
that genuinely CAN differ were measured for real: explanation quality (v2 strictly richer whenever
Context Memory evidence attaches, since v1 has zero such content) and confidence calibration (machinery
built and tested with synthetic data; `n_samples=0` on real data today, since no real historical Context
Memory population exists — the same disclosed Checkpoint 14 limitation). **Falsification verdict:
`V1_REMAINS_ACTIVE`** — per the CEO's own explicit rule, absent proof of a v2 benefit, v1 remains the
active system; `V2_SUPERIOR_CONFIRMED` exists in the type vocabulary but is not reachable under the
current architecture. **Validated**: 24 tests, 100% coverage (7 modules, 179 stmts), `mypy --strict`
clean.

### 8.16 Combined Context Memory + Decision Intelligence validation + full-repository validation — PASSED

After both Checkpoints 14–15 closed independently (each its own commit, each its own targeted
validation), one combined check ran across `context_memory`/`decision_intelligence`/
`decision_intelligence_v2`/`decision_comparison`: 303 tests passing, `mypy --strict` clean on 28 source
files — **TARGETED CONTEXT MEMORY + DECISION INTELLIGENCE VALIDATION PASSED**. Then, justified once
because two checkpoints were closing together as a batch, the complete repository suite ran ONCE: `pytest
ai_trader/ -q` → **2101 passed** (zero failures, zero regressions against the Checkpoints 10–13 baseline
of 2051), `mypy --strict ai_trader/ --exclude 'tests/'` → clean on 222 source files (up from 210),
`coverage run --source=ai_trader -m pytest ai_trader/ -q` then `coverage report` → **TOTAL 12087 stmts,
432 miss, 96%** — the 432-miss figure is the exact same absolute count carried since Implementation
Checkpoint 1B, unchanged across every phase since, confirming zero coverage regression anywhere outside
the newly-added, 100%-covered `decision_intelligence_v2`/`decision_comparison` packages — **FULL
REPOSITORY VALIDATION PASSED**. Protected-path verification: `code/`/`results/`/`knowledge/` 0-diff
confirmed; `ai_trader/decision_intelligence/` 0-diff since Checkpoint 7; `ai_trader/context_memory/`
0-diff since Checkpoint 13's own close.

### 8.17 Fourth Official Project Save (2026-07-20, this document's own current update, after Checkpoints 14–15)

CEO-directed, before any further Phase 7 implementation: a documentation and repository-freeze
checkpoint synchronizing every official state document (this one, `NEXT_SESSION.md`,
`RECONSTRUCTION_PROMPT.md`, `CHANGELOG.md`, `PROJECT_AUDIT.md`) to reflect the completion of Decision
Intelligence v2 and the v1-vs-v2 falsification study (Checkpoints 14–15). No code implemented, no
architecture changed, no existing package modified. Full detail:
`PHASE_7_CHECKPOINTS_14_15_OFFICIAL_SAVE_REPORT.md`.

### 8.18 Current authorized next step

**No further Phase 7 checkpoint is authorized.** The CEO's own Checkpoints 14–15 batch authorization
ends with an explicit stop instruction: "Nu incepe niciun checkpoint ulterior fara autorizatie explicita
a CEO." Decision Intelligence v1 (`ai_trader/decision_intelligence/`) remains the sole active
recommendation system — unmodified since Checkpoint 7, and confirmed by Checkpoint 15's own
falsification study to have no measured or measurable competitor today. Decision Intelligence v2
(`ai_trader/decision_intelligence_v2/`) exists, is fully tested, and is available for future use, but
is not wired into `harness.py` or any execution path, same as v1. `ai_trader/decision_comparison/`
exists as reusable, tested infrastructure for any FUTURE re-run of the falsification study (e.g. once
real Context Memory historical data exists, or if a future checkpoint authorizes Context Memory to
actually influence a decision). Other explicitly named, still-not-authorized future components: Strategy
Health integration/promotion policy, Portfolio Architect, Learning Engine, Live AI Trader, real Context
Memory historical population, and any future checkpoint letting Context Memory influence eligibility/
ranking/scoring. No code changes of any kind are authorized until the CEO explicitly authorizes a next
step.

### 8.19 Interim research artifacts (between the Checkpoints 14–15 save and this one) — not a checkpoint

Three CEO-directed research studies ran after §8.17's save, none of them a Phase 7 checkpoint, none
modifying `ai_trader/`, each its own committed artifact set:

- **Strategy Historical Performance Study** (commit `7c3eb62`) — `ceo_strategy_performance_study.py` +
  `CEO_STRATEGY_PERFORMANCE_STUDY_REPORT.md` + `ceo_strategy_performance_study_tables.md` +
  `ceo_strategy_performance_study_data.json`. Reconstructs, for all 43 strategies, isolated-vs-competitive
  performance (Win Rate/PF/Expectancy/Average RR/Recovery Factor/Sharpe where available), a 5-category
  classification (A-Candidate/B-Promising/C-Reliable-unprofitable/D-Inactive/E-Inconclusive: 6/10/4/14/9
  strategies respectively — the six A-Candidates are S1, S13, S39, S40, S46, S48), and a corrected
  blocking-reason breakdown (24/43 strategies principally shared-slot-limited, 7/43 principally
  BELOW_FLOOR-limited including 3 of the 6 candidates, 12/43 neither — a self-caught correction of an
  earlier draft's overstated "always shared-slot" claim, disclosed in the report itself). No production
  file modified; reused only already-saved Phase 6.9A funnel/trade JSON, no fresh backtest.
- **Strategy Constraint Root-Cause Study** (commit `2650c3b`) — `ceo_strategy_constraint_root_cause_study.py`
  + `CEO_STRATEGY_CONSTRAINT_ROOT_CAUSE_REPORT.md` + `ceo_strategy_constraint_root_cause_tables.md` +
  `ceo_strategy_constraint_root_cause_data.json`. One fresh, deeply-instrumented (zero-file-diff
  monkey-patch, same technique as `phase69a_funnel_recorder.py`) competitive-scenario re-run of the same
  six A-Candidates, reproduced twice byte-for-byte (sha256-identical). **Major correction made during
  this study's own build**: `BELOW_FLOOR` is the Scoring Engine's Recommendation-Floor gate, not a
  sizing gate — sizing never runs for a BELOW_FLOOR denial; the real driver is the Scoring Engine's own
  cross-strategy `conflict_penalty` (`ai_trader/scoring_engine/conflict.py`), structurally impossible in
  true single-strategy isolation. **Result: all six A-Candidates verdict as PORTFOLIO-LIMITED** — for
  S40/S46/S48, 100% of BELOW_FLOOR events are conflict-penalty-caused (would have cleared the
  recommendation floor without it); for S1/S13/S39, the shared-slot rule blocks 169–1,270 episodes each
  with positive matched-subset expectancy. **Recommendation issued (closed-choice, per the study's own
  mandate): C — run a controlled sizing experiment and a controlled portfolio-slot experiment,
  separately** (not combined, to avoid confounding which mechanism produced any later observed change).
  No production file modified.
- **CEO Strategy Performance Atlas** (commit `f4eba6b`) — `CEO_STRATEGY_PERFORMANCE_ATLAS.md`. A
  pure consolidation (no new metric, no recalculation) of the two studies above into one master table of
  all 43 strategies plus an Evidence Level column (A: >100 isolated trades / B: 50–99 / C: 25–49 /
  D: 10–24 / E: <10 — a confidence label only, never a ranking or penalty) and Top-10 leaderboards
  (Expectancy, Profit Factor, Robustness, Total Realized R), each annotated with its Evidence Level.
  Cross-checked: only S1 and S39 combine a Top-10 Expectancy result with "Well supported" (B-level)
  evidence; all ten of the atlas's own PROMISING-classified strategies carry D/E evidence, corroborating
  (not contradicting) their original "under-sampled" classification.

None of the three studies opened the sealed holdout, eliminated any strategy, or changed any threshold/
parameter/algorithm.

### 8.20 Fifth Official Project Save (2026-07-20, this document's own current update) — official
bifurcation into Flow A / Flow B

CEO-directed. Two things happened in this save, both documentation-only:

1. **Flow A opened**: the 40-Edge Alpha Discovery Program's founding infrastructure was created (commit
   `d60fa63`) — `EDGE_DISCOVERY_REGISTRY_v1.md` (all 40 edges across 6 categories — Session Timing
   E001-E008, Price Action/Structure E009-E016, Liquidity E017-E024, Mathematical E025-E032, Intermarket
   E033-E036, News E037-E040 — every one `Status=UNSTUDIED`/`Version=V0`), `EDGE_RESEARCH_PROTOCOL.md`
   (the shared six-stage pipeline + permanent-record rules, §1.1 above), and `EDGE_DISCOVERY_ROADMAP.md`
   (a data-availability-driven sequencing: the project's actual data inventory was checked live —
   XAUUSD OHLCV exists 2022-12-16→2026-07-13 at M15 finest resolution, ~3.5-4 years vs. the protocol's
   ~5-6 year target; no M1/tick data; a `volume` column of unconfirmed/likely-proxy provenance; no
   DXY/US10Y/XAGUSD/USDJPY/SPX data; no economic calendar — 23 of 40 edges are startable today, 17 need
   a data-acquisition decision not made by this save).
2. **The two-flow structure formalized** (§1.1): `PROJECT_STATE_v2.md` (this document), `PROJECT_AUDIT.md`,
   and `NEXT_SESSION.md` all updated to state explicitly that Flow A (Alpha Discovery Laboratory, status
   READY TO START) and Flow B (AI Trader Development, status ACTIVE, roadmap: Strategy Health → Portfolio
   Architect → Learning/Research Feedback → Risk Integration → Execution Integration → MT5 Live) are
   independent, non-conflicting, parallel streams.

No code implemented, no backtest run, no strategy or production module touched, no existing document's
content removed — `git status --porcelain -- ai_trader/ code/ results/ knowledge/` confirmed empty
immediately before this save's own commit.

### 8.21 Flow B resumed: Strategy Health integration/promotion policy — DESIGN PROPOSED, awaiting CEO review

CEO-directed: continue Flow B in this conversation, per the official roadmap (§1.1), starting with
Strategy Health. Status check performed first, per explicit instruction: the underlying Strategy Health
System (scoring/classification, §3/§9) is COMPLETE and unchanged; the **integration/promotion policy**
(what a Health state actually does to the live/competitive portfolio) was confirmed **NOT STARTED**
(never selected — §8.18, §10). Per CEO decision, a design proposal was drafted before any
implementation — `STRATEGY_HEALTH_INTEGRATION_POLICY_DESIGN.md` — rather than implementing directly,
matching the design-first pattern already used for Shadow Evidence and Context Memory.

**The design's own central finding**: Phase 6.9's prior integration attempt (monthly ACTIVE-only
gating) failed via an absorbing lockout — once its own bootstrap evidence aged out of the 365-day
window, the ACTIVE roster stayed empty for the remaining ~2.6 years, because competitive trades were too
scarce for most strategies to ever score, and the binary ACTIVE-only cutoff meant zero new evidence once
that happened. The design connects this directly to the separate, more recent Root-Cause Study
(§8.19/`2650c3b`): both findings trace to the same mechanism — competitive trade counts are a scarce,
shared-slot-contested resource, not a fair per-strategy sample. **Recommended v1 design**: (1) evidence
source — dual, Shadow-Evidence-primary/competitive-evidence-secondary, both labeled, never blended
(Shadow Evidence decouples per-strategy evidence accumulation from shared-slot contention, directly
targeting Phase 6.9's own failure mechanism); (2) policy — default-in eligibility (ACTIVE/WATCHLIST/
PROBATION all remain eligible for new signals; only DISABLED is excluded), reusing the existing,
already-proven-safe `strategy_id_filter` mechanism in `ai_trader/simulation/harness.py` exactly as Phase
6.9 already used it (overlay/exit management stays unfiltered). **Deliberately touches zero frozen
modules** — two more invasive options (risk-scaled sizing via `sizing.py`'s existing `quality_factor`
pattern; Health-aware ranking priority via `scoring_engine/ranker.py`) are named as explicit, separate,
FUTURE escalations requiring their own dedicated decision to unfreeze Risk Manager/Scoring Engine
respectively — neither bundled into this v1 recommendation. A self-adversarial risk section is included
(the design may be a practical no-op today since DISABLED is currently 0/43 strategies — treated as an
intentional, low-risk v1 property, not a flaw).

**Status: PROPOSED, awaiting CEO review (ACCEPTED / ACCEPTED WITH CONDITIONS / NEEDS REVISION /
REJECTED).** No implementation has begun. Flow B's roadmap does not advance to Portfolio Architect until
Strategy Health integration is implemented per an accepted design (or the CEO redirects this step).

### 8.22 Strategy Health design — ACCEPTED WITH CONDITIONS; five architectural clarifications added

CEO verdict on `STRATEGY_HEALTH_INTEGRATION_POLICY_DESIGN.md`: **ACCEPTED WITH CONDITIONS** — general
direction and all five stated principles confirmed (Strategy Health stays a separate evaluation system;
frozen modules stay frozen; Shadow Evidence is the primary new-evidence source; Phase 6.9's ACTIVE-only
lockout must not repeat; reuse existing infrastructure where sufficient). Before implementation, the CEO
required five architectural clarifications, added to the same document as §§11–15 (no new file, per
instruction: "pregătește versiunea finală a designului"):

1. **Explicit lifecycle** (§11): five states — `NEW` (a policy-layer label only, derived from the frozen
   classifier's own existing "no evidence → WATCHLIST" default, never a fifth classifier band) →
   `WATCHLIST` → `ACTIVE` → `PROBATION` → `DISABLED` — as a bidirectional state machine (not a one-way
   pipeline), each with precise entry/exit conditions and capabilities.
2. **Per-state influence, zero ambiguity** (§12): ACTIVE and WATCHLIST both retain full real-portfolio
   competition (identical to today); PROBATION and DISABLED are both Shadow-only (excluded from new REAL
   trades, but Shadow Evidence tracking continues unconditionally for both) — **this refines the original
   v1 recommendation**, which had only excluded DISABLED; PROBATION is now excluded from real trades too,
   directly answering the CEO's own question ("PROBATION — poate rămâne doar în Shadow?" → yes).
3. **Module contracts** (§13, interfaces only, no implementation): Shadow Evidence → Strategy Health
   (unconditional, per-strategy, read-only); Strategy Health → a new Eligibility Policy layer (not yet
   built); Eligibility Policy → `harness.py`'s existing `strategy_id_filter` (Risk Manager's own contract
   unchanged — it never sees why an opportunity is or isn't present); **no contract to Decision
   Intelligence in v1** (deliberately, flagged as a future open question); Portfolio Architect's expected
   future contract stated for foresight only. "Edge Selection AI" has no existing named module — treated
   as referring to Decision Intelligence, flagged rather than silently assumed.
4. **Non-absorbing recovery** (§14): the load-bearing invariant is that Shadow Evidence tracks every
   strategy, in every state, forever, regardless of real-portfolio eligibility — so PROBATION/DISABLED
   strategies keep accumulating genuine new evidence and can recover (PROBATION→WATCHLIST at ≥45,
   DISABLED→PROBATION at ≥25) via real improved Shadow performance, never via a timer or evidence simply
   expiring.
5. **Performance-impact argument** (§15, structural/architectural, not empirical — no backtest run):
   ACTIVE/WATCHLIST strategies are completely unaffected; the lockout mechanism is broken by construction
   (Shadow Evidence has no Health-state gate anywhere, so the population whose exclusion could otherwise
   cause a Phase-6.9-style lockout keeps generating fresh evidence regardless); the exact roster shift is
   explicitly NOT claimed without a live recomputation (disclosed: PROBATION is 7/43 under the old
   competitive-evidence snapshot, not necessarily the same under Shadow-sourced scoring).

Reconciled: the document's own earlier sections (§4.2 Option D, §5, §6, §7) were corrected to match the
refined PROBATION-is-Shadow-only policy, so no internal contradiction remains between the early
recommendation and the later clarifications. **Status: ACCEPTED WITH CONDITIONS, clarifications
delivered, implementation still not started** — the CEO's own next step is to review the completed
architecture before implementation begins.

## 9. Modules implemented (`ai_trader/`)

| Module | Status | Notes |
|---|---|---|
| `market_scanner/` | FROZEN (READY) | one disclosed, additive, CEO-approved touch from Wave B (optional `feature_history` field) |
| `strategy_manager/` | FROZEN (READY) | loads the Strategy Library, tracks contract Health/Lifecycle (schema/maturity — unrelated to trading performance) |
| `signal_engine/` | FROZEN (READY) | runs registered runtime evaluators; `SignalState` 9-state machine (`SIGNAL_ENGINE_STATE_MACHINE.md`) |
| `scoring_engine/` | FROZEN (READY) | scores/ranks signals; `Recommendation` enum + conflict resolution |
| `risk_manager/` | FROZEN (READY) | sizing, guards, cooldowns, portfolio limits (incl. the single-shared-symbol-slot `LIMIT_MAX_PER_SYMBOL` constraint) |
| `execution_engine/` | FROZEN (READY) | order construction/execution |
| `simulation/` | NOT frozen, extensible | `SimulationHarness`/`ExecutionSimulator`/`PortfolioSimulator`/`PerformanceAnalyzer`; `time_stop.py`/`trailing_stop.py` generic overlays; THREE disclosed touches to date: the Phase 6.9 overlay-isolation fix, the Phase 6.9A `RiskEventRecord.strategy_id` field, the Phase 6.10 Checkpoint 1A/1B `shadow_config` field + Checkpoint 1B's tap call site in `harness.py` |
| `strategy_runtime/` | NOT frozen | `families/` — all 43 real evaluators; `registry.py`; `context_access.py`; `migration.py` |
| `strategy_health/` | NOT frozen, scoring UNCHANGED since its own build | `types.py`/`metrics.py`/`scoring.py`/`classifier.py`/`evaluator.py` (frozen scoring, never touched by any phase after its own build) + `rolling_gate.py` (Phase 6.9 addition, thin wrapper) |
| `shadow_evidence/` | COMPLETE for its own scoped lifecycle (Phase 6.10, Checkpoints 1A–4, CLOSED) | `config.py::ShadowConfig`/`all_registered_strategies()`, `types.py` (data contracts incl. `ShadowStrategySummary`), `engine.py::ShadowEvidenceEngine` (full virtual position lifecycle since 1C), `aggregation.py` (Checkpoint 2 statistics), `research.py`/`comparison.py`/`portfolio_research.py` (Checkpoint 4) — generic over any configured edge/strategy set; Strategy Health integration/capital allocation remain UNSELECTED/UNDESIGNED, out of scope |
| `market_intelligence/` | NEW (Phase 7 Checkpoint 5, DONE) | `engine.py::build_market_intelligence()` — pure, read-only "what is the market doing" snapshot (Trend/Structure/Momentum/Volatility/Liquidity/Expansion/Session/Agreement/Confidence); not wired into `harness.py` |
| `edge_intelligence/` | NEW (Phase 7 Checkpoint 6, DONE) | `engine.py::evaluate_edges()` — pure, read-only "which edges currently exist" per-strategy PRESENT/POSSIBLE/ABSENT verdict, built on Market Intelligence + each strategy's own declared Contract; not wired into `harness.py` |
| `decision_intelligence/` | NEW (Phase 7 Checkpoint 7, DONE) | `engine.py::make_decision()` — "which edge deserves execution": 4 disclosed eligibility gates (contract status/maturity/confidence/optional expectancy) + deterministic ranking → one recommended strategy_id or NO TRADE; independent of Signal/Scoring/Risk/Execution/Shadow/MT5 (verified by grep); not wired into `harness.py` |
| `context_memory/` | NEW (Phase 7 Checkpoints 9–13, DONE) | 11 source files: `contracts.py`/`enums.py`/`validation.py`/`identities.py` (Checkpoint 9 — immutable contracts + deterministic SHA-256 identities), `codec.py`/`repository.py` (Checkpoint 10 — append-only JSONL storage), `episodes.py`/`index.py` (Checkpoint 11 — deterministic episode collapsing + rebuildable historical index), `retrieval.py` (Checkpoint 12 — fixed-priority hierarchical relaxation ladder, no k-NN/weighted-distance), `evidence.py` (Checkpoint 13 — per-edge `ContextualEvidenceReport`, sufficiency threshold reused from `code/alpha_lab.py`'s own `MINTR=25`); produces evidence reports only, NEVER BUY/SELL/entry/stop/target/size/execution/an edge ranking; fully independent of Decision Intelligence/Signal/Scoring/Risk/Execution/Shadow Evidence/MT5 (verified by grep + a static AST import-independence scan at every checkpoint's close); not wired into `harness.py` or `decision_intelligence/` |
| `decision_intelligence_v2/` | NEW (Phase 7 Checkpoint 14, DONE) | `engine.py::make_decision_v2()` — wraps v1's own `make_decision()` UNCHANGED and attaches, per candidate, an explainable Context Memory evidence report; `types.py::DecisionReportV2` structurally enforces its own recommendation equals v1's; `adapters.py` bridges live Market Intelligence snapshots into Context Memory's own local types; `explanation.py` narrates why context was found/what evidence exists/limitations/why status; never changes eligibility/ranking/scoring/Risk/Sizing/Execution, never generates BUY/SELL (verified by static scan); not wired into `harness.py` |
| `decision_comparison/` | NEW (Phase 7 Checkpoint 15, DONE) | Read-only v1-vs-v2 falsification framework — `recommendation.py`/`trade_outcome_proof.py`/`explanation_quality.py`/`calibration.py`/`falsification.py`; never modifies v1/v2/Context Memory; current verdict `V1_REMAINS_ACTIVE` (§8.15) — recommendation-stream metrics provably identical by construction, confirmed over real data; explanation-quality/confidence-calibration are the only genuinely differing dimensions, the latter awaiting real historical Context Memory data; not wired into `harness.py` |

## 10. What must NOT be modified (standing, cumulative across every phase)

- `code/`, `results/`, `knowledge/` (Research Lab) — frozen, 0-diff confirmed at every close.
- Every strategy contract, evaluator, and parameter.
- `ai_trader/strategy_health/`'s own scoring methodology (percentile-rank, Bühlmann shrinkage,
  PCA-derived weights, `WINDOW_PRIORITY`, classification bands) — frozen since its own build; only
  `rolling_gate.py` was ever added alongside it (a thin, permanent wrapper, no scoring logic).
- Scoring Engine weights, Risk Policy, Execution Engine rules — untouched except the two disclosed
  Simulation Framework fixes above (neither touches these frozen modules themselves).
- The sealed terminal holdout (2025-10-23 09:15 UTC → 2026-07-13 06:00 UTC) — never opened by anything.
- No strategy has ever been, or should be, permanently eliminated based on any AI Trader analysis.
- **Phase 6.10 (CLOSED, standing constraints remain in force)**: no edge/strategy-specific architecture
  may be introduced into `shadow_evidence/` — the generic, config-driven design (§7 above) is the
  standing requirement, not an optional style choice. No Strategy Health integration policy may be
  selected, and no capital-allocation-across-edges architecture may be built, without its own separate,
  explicit CEO decision — neither was authorized by any Checkpoint 1A–4 closing.
- **Phase 7 additions (standing since Checkpoint 5)**: `market_intelligence/`, `edge_intelligence/`, and
  `decision_intelligence/` must remain pure and read-only in the sense that matters for each — no BUY/
  SELL, no order submission, no risk sizing, no optimization, no portfolio decision, no health/scoring
  classification, ever, in any of the three (Decision Intelligence produces a RECOMMENDATION, never an
  executed action — that distinction is the whole point of the layer and must not blur). None of the
  three may be wired into `harness.py` or any execution path without its own explicit CEO approval.
  Strategy Health integration/promotion policy, Portfolio Architect, Learning Engine, and Live AI Trader
  are all explicitly named future components, NOT authorized by any Checkpoint 5–7 closing.
  `edge_intelligence/` must not import `shadow_evidence`; `decision_intelligence/` must not import
  `signal_engine`/`scoring_engine`/`risk_manager`/`execution_engine`/`shadow_evidence` (deliberate
  isolation choices, not oversights — re-verify with `grep -r` before any future change touches either
  package). `decision_intelligence/`'s own `ResearchStats` type is deliberately LOCAL, never the
  `shadow_evidence.types.StrategyResearchSummary` type — do not "simplify" this by importing the Shadow
  Evidence type directly; that would violate the standing independence requirement.
- **Phase 7 Context Memory (standing since Checkpoint 8, CLOSED through Checkpoint 13)**: `ai_trader/
  context_memory/` must NEVER output BUY/SELL/entry/stop/target/size/execution/a final recommendation —
  evidence only, by the accepted Checkpoint 8 design's own core architectural principle. It must not
  import `decision_intelligence`/`signal_engine`/`scoring_engine`/`risk_manager`/`execution_engine`/
  `shadow_evidence` (deliberate isolation, re-verify with the package's own AST-based
  `test_import_independence.py` before any future change), must not be wired into `harness.py`, and must
  not have its relaxation ladder order (§8.10) or its evidence-sufficiency policy (§8.11) silently
  changed — both are explicit, versioned, disclosed choices, not implementation details to "clean up."
- **Phase 7 Decision Intelligence v2 + falsification study (standing since Checkpoint 14, CLOSED through
  Checkpoint 15)**: Decision Intelligence v1 (`ai_trader/decision_intelligence/`) is the sole active
  recommendation system and must NEVER be modified to accommodate v2 — v2 is additive only.
  `ai_trader/decision_intelligence_v2/` must not change eligibility, ranking, scoring, Risk, Position
  Sizing, or Execution, must never generate a BUY/SELL/order-submission token, and
  `DecisionReportV2.__post_init__`'s own recommendation-equality invariant must never be relaxed or
  bypassed. `ai_trader/decision_comparison/` must remain read-only — it must never modify v1, v2, or
  Context Memory's repository. The Checkpoint 15 falsification verdict (`V1_REMAINS_ACTIVE`) must not be
  silently overridden or reinterpreted as "v2 is better" without a genuinely new, separately-authorized
  study measuring a real difference on real data.
- **Phase 7 Checkpoint 16+ (any checkpoint letting Context Memory influence a decision, any real
  historical Context Memory population, any Decision Intelligence v2 promotion to active status) must not
  begin without its own, separate, explicit CEO approval** — Checkpoint 15 being complete is not itself
  that approval; the CEO's own Checkpoints 14–15 batch authorization ends with an explicit stop
  instruction and names no next topic.

## 11. Diagnostic artifacts preserved (cumulative, all committed, all referenced by name in their own reports)

- Phase 6.9: `phase69_rolling_backtest.py`, `phase69_analysis.py`, `phase69_analysis2.py`,
  `phase69_results.json`, `phase69_analysis.json`, `phase69_analysis2.json`.
- Relevance audit: `relevance12m_run.py`, `relevance12m_run_bcd.py`, `relevance12m_perstrategy.py`,
  `relevance12m_portfolioA.json`, `relevance12m_portfolioBCD.json`, `relevance12m_perstrategy.json`.
- Phase 6.9A: `phase69a_funnel_recorder.py`, `phase69a_funnel_run.py`, `phase69a_isolated_run.py`,
  `phase69a_analysis.py`, `phase69a_competitive_funnel.json`, `phase69a_isolated_funnel.json`,
  `phase69a_analysis.json`.
- Phase 6.10: `phase610_prescope_analysis.py`/`.json` (the pre-scope diagnostic's own analysis),
  `phase610_checkpoint1b_s10_validation.py`/`.json` (Checkpoint 1B's own full-scale S10-vs-Phase-6.9A
  validation), `phase610_checkpoint1c_s10_validation.py`/`.json` (Checkpoint 1C's own isolated-ledger
  comparison, the source of the documented semantic-limitation finding, §7.7).
- Phase 7: no standalone diagnostic scripts — Checkpoints 5, 6, and 7 all validated entirely through
  their own committed test suites (`ai_trader/market_intelligence/tests/`,
  `ai_trader/edge_intelligence/tests/`, `ai_trader/decision_intelligence/tests/`, each including its own
  real-data integration test), nothing scratch-generated to preserve. Checkpoints 8–13 (Context Memory)
  likewise: no standalone diagnostic scripts — validated entirely through `ai_trader/context_memory/
  tests/` (221 tests across 9 files, 100% coverage), the Checkpoint 8 design doc, and each checkpoint's
  own `PHASE_7_CHECKPOINT_N_REPORT.md`.

All of the above are deliberately preserved (a CEO-instructed exception to the repository's earlier
"delete scratch scripts after report capture" discipline, first established at Phase 6.9's own close),
so every phase's own findings stay fully reproducible without re-running anything from scratch.

## 12. Reading order for a brand-new session

**First, decide which flow the session is continuing** (§1.1) — Flow A and Flow B have almost entirely
disjoint reading lists below.

1. This document (`PROJECT_STATE_v2.md`) — the complete current state, both flows.
2. `RECONSTRUCTION_PROMPT.md` — if starting a genuinely new conversation with no prior context, this is
   the single entry point; it directs the same reading order as below.
3. `NEXT_SESSION.md` — the exact next-session procedure and git-state re-verification steps for
   whichever flow the session continues.

**If continuing Flow A (Alpha Discovery Laboratory):**

4A. `EDGE_DISCOVERY_ROADMAP.md` — which edge(s) to start with and why (data-availability-driven
    sequencing).
5A. `EDGE_RESEARCH_PROTOCOL.md` — the mandatory six-stage pipeline and permanent-record rules every edge
    must follow.
6A. `EDGE_DISCOVERY_REGISTRY_v1.md` — the specific edge's own V0 hypothesis, category, and required
    data/timeframes/instruments/variables.

**If continuing Flow B (AI Trader Development):**

4B. `PHASE_7_CHECKPOINT_15_REPORT.md` → `PHASE_7_CHECKPOINT_14_REPORT.md` — the current official
   architectural frontier: Decision Intelligence v2 (a separate, additive system whose recommendation is
   construction-time-guaranteed identical to v1's, wrapping v1 with an explainable Context Memory
   evidence attachment) and the v1-vs-v2 falsification study (verdict: `V1_REMAINS_ACTIVE`).
5B. `PHASE_7_CHECKPOINT_13_REPORT.md` → `PHASE_7_CHECKPOINT_12_REPORT.md` → `PHASE_7_CHECKPOINT_11_REPORT.md`
   → `PHASE_7_CHECKPOINT_10_REPORT.md` → `PHASE_7_CHECKPOINT_9_REPORT.md` →
   `PHASE_7_CHECKPOINT_8_CONTEXT_MEMORY_DESIGN.md` — the complete Context Memory subsystem
   (deterministic per-edge Contextual Evidence Aggregation, built on deterministic hierarchical-
   relaxation Retrieval, built on a deterministic episode-collapsed Historical Index, built on an
   append-only Repository, built on immutable contracts and deterministic identities), most-recent-first
   — the foundation Checkpoint 14 consumes.
6B. `PHASE_7_CHECKPOINT_7_REPORT.md` → `PHASE_7_CHECKPOINT_6_REPORT.md` → `PHASE_7_CHECKPOINT_5_REPORT.md`
   — Decision Intelligence v1 built on Edge Intelligence built on Market Intelligence — still current,
   unmodified, and the sole active recommendation system (§8.15/§8.18).
7B. `CEO_STRATEGY_CONSTRAINT_ROOT_CAUSE_REPORT.md` → `CEO_STRATEGY_PERFORMANCE_STUDY_REPORT.md` →
   `CEO_STRATEGY_PERFORMANCE_ATLAS.md` — the interim research on why the current six A-Candidate
   strategies are constrained (all six: PORTFOLIO-LIMITED) and how all 43 strategies compare — directly
   relevant background for the next Flow B step, Strategy Health integration/promotion policy (§1.1).
8B. `PHASE_6_10_EDGE_PORTFOLIO_DIRECTION.md` — the architectural direction behind the now-CLOSED Phase
   6.10 (generic Edge Portfolio, S10 as validation edge only) — background, not the current frontier.
9B. `PHASE_6_10_PRE_SCOPE_DIAGNOSTIC.md` → `PHASE_6_10_SHADOW_EVIDENCE_ARCHITECTURE_DESIGN.md`
   (including its own §17 adversarial review and §19 Checkpoint 1C correction) — the diagnostic and
   design behind Checkpoints 1A–1C.
10B. In detail, if deeper Phase 6.9A background is needed:
   `PHASE_6_9_ROLLING_HEALTH_GATED_BACKTEST_REPORT.md` → `CURRENT_XAUUSD_12M_RELEVANCE_REPORT.md` →
   `PHASE_6_9A_STRATEGY_EVIDENCE_FLOW_AUDIT_REPORT.md`.
11B. `ROLLING_HEALTH_BACKTEST_HANDOFF.md` for the Strategy Health System's own full methodology (§5
    there) and Phase 6.9's own original specification (§8 there, now marked CLOSED).

**Common to both flows:**

12. `PROJECT_STATE_v1.0.md` for the Research Lab's own frozen state (unchanged since 2026-07-14).
13. `CHANGELOG.md`'s own top entries for verified, dated, session-by-session detail.

**Flow A**: systematic Discovery-stage study of the Alpha Edge registry is authorized to begin, starting
from `EDGE_DISCOVERY_ROADMAP.md`'s Tier 1 — but every stage gate in `EDGE_RESEARCH_PROTOCOL.md` still
applies per edge, and a Final Verdict never itself authorizes implementation (§1.1).

**Flow B: do not begin** any Phase 7 Checkpoint 16 (Context Memory influencing a decision, real Context
Memory historical population, Decision Intelligence v2 promotion — none proposed, none authorized), Wave
C, Learning Engine, Broker Adapter, MT5, live/paper trading, multi-position trading, capital allocation
across edges, or WATCHLIST activation without its own dedicated CEO approval — this document does not
grant it. **Strategy Health integration/promotion policy is the next named step in Flow B's own roadmap
(§1.1)** but still requires its own explicit CEO authorization to begin, same as every prior checkpoint.
