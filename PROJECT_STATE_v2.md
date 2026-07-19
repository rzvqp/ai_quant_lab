# PROJECT_STATE — AI Quant Research Lab → AI Trader — v2 (UPDATED: OFFICIAL PROJECT SAVE, 2026-07-19)

**Purpose**: this is the single, authoritative, consolidated state document for the ENTIRE project —
both the frozen Research Lab and the AI Trader built on top of it — current as of this official save. A
brand-new chat, with no access to any prior conversation, must be able to reconstruct the complete
project from this document plus the ones it points to. Every fact below was verified directly against
`git log`/`git status`/`git diff` at this save's own close, and against the `pytest`/`mypy --strict`/
`coverage` run from Phase 7 Checkpoint 6's own validation (still current: `git diff --stat
b94c93f1748f71a08657b5fb348ac240def5f17e HEAD -- ai_trader/` is empty — zero `ai_trader/` code has
changed since that validation, confirmed live, not assumed) — nothing here is carried forward
unverified. This document supersedes no prior report — `PROJECT_STATE_v1.0.md`,
`ROLLING_HEALTH_BACKTEST_HANDOFF.md`, and every phase's own dedicated report remain the authoritative,
detailed sources for their own respective scopes; this document exists to make the CURRENT, FULL state
reachable in one place.
**This update's own scope: documentation and repository-freeze only — no code implemented, no
architecture changed, Phase 7 Checkpoint 7 not started (§8.4).**

---

## 0. Official state (authoritative, verify live before trusting)

```
Repository path:  C:\Users\MEDION GAMING\ai_quant_lab-research-main
Branch:           ai-trader-implementation
HEAD:             6e3c4ce922baaa2f4008214021e34da7d062b746
                  "Record Checkpoint 6 commit hash in the final report"
                  (documentation-only follow-up to b94c93f, Phase 7 Checkpoint 6's own implementation commit)
Working tree:     clean (verified live at this official save, before its own commit)
```

**Re-verify `git branch --show-current`/`git log -1`/`git status --porcelain` directly before trusting
any git-state claim anywhere in this project's documentation** — the standing discipline every prior
handoff has followed, re-confirmed at this save.

**Verified live, Phase 7 Checkpoint 6's own validation (2026-07-19) — still current, since zero
`ai_trader/` code has changed since that commit (`b94c93f`), confirmed via `git diff --stat b94c93f
HEAD -- ai_trader/` returning empty (only this save's own documentation commit follows it):**
```
pytest ai_trader/ -q            -> 1798 passed
mypy --strict ai_trader/ --exclude 'tests/'  -> Success: no issues found in 194 source files
coverage run --source=ai_trader -m pytest ai_trader/ -q
coverage report --omit="*/tests/*"           -> TOTAL 10776 stmts, 432 miss, 96%
```
(Baseline for comparison, Implementation Checkpoint 1B's own close, the last figure this document
previously cited: 1606 passed, 169 source files, 9783 stmts/432 miss/96%. The 432-miss figure is
UNCHANGED end to end across Checkpoints 1C/2/3/4 and Phase 7 Checkpoints 5/6 despite +993 statements
added since — every new statement across five checkpoints' worth of work is covered.)

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

## 8. Phase 7 — AI Trader Intelligence Layer (Checkpoints 5–6, 2026-07-19)

**Official direction**: a deliberate pivot from infrastructure to intelligence, per the CEO's own Phase
7 opening framing (preserved verbatim in `PHASE_7_CHECKPOINT_5_REPORT.md` §1 and in memory): "We are NOT
building a rule-based trading bot. We are NOT building a collection of independent strategies. We are
building an AI Trader" that must OBSERVE, UNDERSTAND, EVALUATE, DECIDE and continuously LEARN, targeting
~2–4 trades/day, high win rate, quality over quantity, never trading just because a setup exists.
Checkpoints 5 and 6 are the first two components of that reasoning process — both purely read-only
recognition layers, neither trades, neither is wired into `harness.py` or any execution path.

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

### 8.3 Official Project Save (2026-07-19, this document's own current update)

CEO-directed, before any further Phase 7 implementation: a documentation and repository-freeze
checkpoint synchronizing every official state document (this one, `NEXT_SESSION.md`,
`RECONSTRUCTION_PROMPT.md`, `CHANGELOG.md`, `PROJECT_AUDIT.md`) to reflect the completion of Phase 6.10
in full and Phase 7 Checkpoints 5–6. No code implemented, no architecture changed. Full detail:
`PHASE_7_OFFICIAL_PROJECT_SAVE_REPORT.md`.

### 8.4 Current authorized next step

**Phase 7 Checkpoint 7 is NOT STARTED and NOT AUTHORIZED.** The CEO's own explicit closing instruction
after Checkpoint 6 named the next, not-yet-authorized component as **Decision AI** — the layer that
would actually consume `present_strategy_ids()`/`EdgeIntelligenceSnapshot` to choose whether/what to
trade — but this is a recommended direction from prior context, not a pre-approval; no scope for
Checkpoint 7 has been proposed or accepted. Also explicitly named as future, NOT-yet-authorized
components (from the Checkpoint 5 authorization text): Strategy Health integration/promotion policy,
Portfolio Architect, Learning Engine, Live AI Trader. No code changes of any kind are authorized until
the CEO explicitly authorizes the next checkpoint.

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
- **Phase 7 additions (standing since Checkpoint 5)**: `market_intelligence/` and `edge_intelligence/`
  must remain pure and read-only — no BUY/SELL, no order submission, no optimization, no portfolio
  decision, no health/scoring classification, ever, in either package. Neither package may be wired into
  `harness.py` or any execution path without its own explicit CEO approval. Decision AI, Strategy Health
  integration/promotion policy, Portfolio Architect, Learning Engine, and Live AI Trader are all
  explicitly named future components, NOT authorized by Checkpoints 5 or 6. `edge_intelligence/` must
  not import `shadow_evidence` (a deliberate isolation choice, not an oversight — re-verify with
  `grep -r "shadow_evidence" ai_trader/edge_intelligence/` before any future change touches that package).
- Phase 7 Checkpoint 7 (or any further implementation) must not begin without its own, separate,
  explicit CEO approval — Checkpoint 6 being complete is not itself that approval.

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
- Phase 7: no standalone diagnostic scripts — both Checkpoints 5 and 6 validated entirely through their
  own committed test suites (`ai_trader/market_intelligence/tests/`, `ai_trader/edge_intelligence/tests/`,
  including each package's own real-data integration test), nothing scratch-generated to preserve.

All of the above are deliberately preserved (a CEO-instructed exception to the repository's earlier
"delete scratch scripts after report capture" discipline, first established at Phase 6.9's own close),
so every phase's own findings stay fully reproducible without re-running anything from scratch.

## 12. Reading order for a brand-new session

1. This document (`PROJECT_STATE_v2.md`) — the complete current state.
2. `RECONSTRUCTION_PROMPT.md` — if starting a genuinely new conversation with no prior context, this is
   the single entry point; it directs the same reading order as below.
3. `NEXT_SESSION.md` — the exact next-session procedure and git-state re-verification steps.
4. `PHASE_7_CHECKPOINT_6_REPORT.md` → `PHASE_7_CHECKPOINT_5_REPORT.md` — the current official
   architectural frontier (Edge Intelligence built on Market Intelligence), most-recent-first.
5. `PHASE_6_10_EDGE_PORTFOLIO_DIRECTION.md` — the architectural direction behind the now-CLOSED Phase
   6.10 (generic Edge Portfolio, S10 as validation edge only) — background, not the current frontier.
6. `PHASE_6_10_PRE_SCOPE_DIAGNOSTIC.md` → `PHASE_6_10_SHADOW_EVIDENCE_ARCHITECTURE_DESIGN.md`
   (including its own §17 adversarial review and §19 Checkpoint 1C correction) — the diagnostic and
   design behind Checkpoints 1A–1C.
7. In detail, if deeper Phase 6.9A background is needed:
   `PHASE_6_9_ROLLING_HEALTH_GATED_BACKTEST_REPORT.md` → `CURRENT_XAUUSD_12M_RELEVANCE_REPORT.md` →
   `PHASE_6_9A_STRATEGY_EVIDENCE_FLOW_AUDIT_REPORT.md`.
8. `ROLLING_HEALTH_BACKTEST_HANDOFF.md` for the Strategy Health System's own full methodology (§5
   there) and Phase 6.9's own original specification (§8 there, now marked CLOSED).
9. `PROJECT_STATE_v1.0.md` for the Research Lab's own frozen state (unchanged since 2026-07-14).
10. `CHANGELOG.md`'s own top entries for verified, dated, session-by-session detail.

**Do not begin Phase 7 Checkpoint 7 (Decision AI or any other component), Wave C, Learning Engine,
Broker Adapter, MT5, live/paper trading, multi-position trading, Strategy Health integration, capital
allocation across edges, or WATCHLIST activation without its own dedicated CEO approval — this document
does not grant it.**
