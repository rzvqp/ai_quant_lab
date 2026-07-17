# PROJECT_STATE — AI Quant Research Lab → AI Trader — v2 (UPDATED: OFFICIAL CHECKPOINT SAVE, 2026-07-17)

**Purpose**: this is the single, authoritative, consolidated state document for the ENTIRE project —
both the frozen Research Lab and the AI Trader built on top of it — current as of this checkpoint
save. A brand-new chat, with no access to any prior conversation, must be able to reconstruct the
complete project from this document plus the ones it points to. Every fact below was verified directly
against `git log`/`git status`/`git diff` at this checkpoint's own close, and against the `pytest`/
`mypy --strict`/`coverage` run from Implementation Checkpoint 1B's own validation (still current: `git
diff --stat <Checkpoint-1B-commit> HEAD -- ai_trader/` is empty — zero `ai_trader/` code has changed
since that validation, confirmed live, not assumed) — nothing here is carried forward unverified. This
document supersedes no prior report — `PROJECT_STATE_v1.0.md`, `ROLLING_HEALTH_BACKTEST_HANDOFF.md`,
and every phase's own dedicated report remain the authoritative, detailed sources for their own
respective scopes; this document exists to make the CURRENT, FULL state reachable in one place.
**This update's own scope: documentation and repository-freeze only — no code implemented, no
architecture changed, Checkpoint 1C not started (§7.6).**

---

## 0. Official state (authoritative, verify live before trusting)

```
Repository path:  C:\Users\MEDION GAMING\ai_quant_lab-research-main
Branch:           ai-trader-implementation
HEAD:             c4707d30944c3be0168ce425800373048378242c
                  "Phase 6.10 architectural re-frame: Edge Portfolio direction (documentation only, no code)"
Working tree:     clean (verified live at this checkpoint save)
```

**Re-verify `git branch --show-current`/`git log -1`/`git status --porcelain` directly before trusting
any git-state claim anywhere in this project's documentation** — the standing discipline every prior
handoff has followed, re-confirmed at this checkpoint.

**Verified live, Implementation Checkpoint 1B's own validation (2026-07-17) — still current, since zero
`ai_trader/` code has changed since that commit (`5244632`), confirmed via `git diff --stat 5244632
HEAD -- ai_trader/` returning empty:**
```
pytest ai_trader/ -q            -> 1606 passed
mypy --strict ai_trader/ --exclude 'tests/'  -> Success: no issues found in 169 source files
coverage run --source=ai_trader -m pytest ai_trader/ -q
coverage report --omit="*/tests/*"           -> TOTAL 9783 stmts, 432 miss, 96%
```
(Baseline for comparison, Phase 6.9A's own close: 1576 passed, 165 source files, 9649 stmts/432 miss/
96%. The 432-miss figure is unchanged end to end despite +134 statements added since — every new
statement Phase 6.10 has added to date is covered.)

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
  essentially all work across Phases 6.1–6.9A (§3–§6) and Phase 6.10's own Edge Portfolio Evidence
  System (§7, currently through Implementation Checkpoint 1B) took place.

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

## 7. Phase 6.10 — Edge Portfolio Evidence System (pre-scope diagnostic through Implementation Checkpoint 1B)

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

### 7.6 Current authorized next step

**Checkpoint 1C is NOT STARTED and NOT AUTHORIZED.** Recommended scope (not yet approved): virtual
execution for one edge (S10, as the second proof point for the Edge Portfolio's own evidence lifecycle
— chosen because it is the one edge with independently-verified Phase 6.9A isolated-run ground truth to
validate against, not because the architecture favors it), following the same generic, multi-edge-tested
pattern Checkpoint 1B already established. No Strategy Health integration, no capital allocation, no
multi-position live trading, no code changes of any kind are authorized until the CEO explicitly
approves Checkpoint 1C.

## 8. Modules implemented (`ai_trader/`)

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
| `shadow_evidence/` | NEW (Phase 6.10, Checkpoints 1A/1B) | `config.py::ShadowConfig`, `types.py` (4 frozen data contracts), `engine.py::ShadowEvidenceEngine` — generic over any configured edge/strategy set; no virtual execution/positions yet (Checkpoint 1C+) |

## 9. What must NOT be modified (standing, cumulative across every phase)

- `code/`, `results/`, `knowledge/` (Research Lab) — frozen, 0-diff confirmed at every close.
- Every strategy contract, evaluator, and parameter.
- `ai_trader/strategy_health/`'s own scoring methodology (percentile-rank, Bühlmann shrinkage,
  PCA-derived weights, `WINDOW_PRIORITY`, classification bands) — frozen since its own build; only
  `rolling_gate.py` was ever added alongside it (a thin, permanent wrapper, no scoring logic).
- Scoring Engine weights, Risk Policy, Execution Engine rules — untouched except the two disclosed
  Simulation Framework fixes above (neither touches these frozen modules themselves).
- The sealed terminal holdout (2025-10-23 09:15 UTC → 2026-07-13 06:00 UTC) — never opened by anything.
- No strategy has ever been, or should be, permanently eliminated based on any AI Trader analysis.
- **Phase 6.10 additions (standing since Checkpoints 1A/1B)**: Checkpoint 1C (or any further
  implementation) must not begin without its own, separate, explicit CEO approval — Checkpoint 1B being
  complete, or the Edge Portfolio direction re-frame being accepted, is not itself that approval. No
  virtual execution, virtual positions/exits, shadow portfolio state, Strategy Health integration,
  capital allocation across edges, multiple real XAUUSD positions, Portfolio Orchestrator, or Consensus
  Engine has been authorized to date. No edge/strategy-specific architecture may be introduced into
  `shadow_evidence/` — the generic, config-driven design (§7 above) is the standing requirement, not an
  optional style choice.

## 10. Diagnostic artifacts preserved (cumulative, all committed, all referenced by name in their own reports)

- Phase 6.9: `phase69_rolling_backtest.py`, `phase69_analysis.py`, `phase69_analysis2.py`,
  `phase69_results.json`, `phase69_analysis.json`, `phase69_analysis2.json`.
- Relevance audit: `relevance12m_run.py`, `relevance12m_run_bcd.py`, `relevance12m_perstrategy.py`,
  `relevance12m_portfolioA.json`, `relevance12m_portfolioBCD.json`, `relevance12m_perstrategy.json`.
- Phase 6.9A: `phase69a_funnel_recorder.py`, `phase69a_funnel_run.py`, `phase69a_isolated_run.py`,
  `phase69a_analysis.py`, `phase69a_competitive_funnel.json`, `phase69a_isolated_funnel.json`,
  `phase69a_analysis.json`.
- Phase 6.10: `phase610_prescope_analysis.py`/`.json` (the pre-scope diagnostic's own analysis),
  `phase610_checkpoint1b_s10_validation.py`/`.json` (Checkpoint 1B's own full-scale S10-vs-Phase-6.9A
  validation).

All of the above are deliberately preserved (a CEO-instructed exception to the repository's earlier
"delete scratch scripts after report capture" discipline, first established at Phase 6.9's own close),
so every phase's own findings stay fully reproducible without re-running anything from scratch.

## 11. Reading order for a brand-new session

1. This document (`PROJECT_STATE_v2.md`) — the complete current state.
2. `RECONSTRUCTION_PROMPT.md` — if starting a genuinely new conversation with no prior context, this is
   the single entry point; it directs the same reading order as below.
3. `NEXT_SESSION.md` — the exact next-session procedure and git-state re-verification steps.
4. `PHASE_6_10_EDGE_PORTFOLIO_DIRECTION.md` — the current official architectural direction (generic
   Edge Portfolio, S10 as validation edge only).
5. `PHASE_6_10_PRE_SCOPE_DIAGNOSTIC.md` → `PHASE_6_10_SHADOW_EVIDENCE_ARCHITECTURE_DESIGN.md`
   (including its own §17 adversarial review) — the diagnostic and design behind Checkpoints 1A/1B.
6. In detail, if deeper Phase 6.9A background is needed:
   `PHASE_6_9_ROLLING_HEALTH_GATED_BACKTEST_REPORT.md` → `CURRENT_XAUUSD_12M_RELEVANCE_REPORT.md` →
   `PHASE_6_9A_STRATEGY_EVIDENCE_FLOW_AUDIT_REPORT.md`.
7. `ROLLING_HEALTH_BACKTEST_HANDOFF.md` for the Strategy Health System's own full methodology (§5
   there) and Phase 6.9's own original specification (§8 there, now marked CLOSED).
8. `PROJECT_STATE_v1.0.md` for the Research Lab's own frozen state (unchanged since 2026-07-14).
9. `CHANGELOG.md`'s own top entries for verified, dated, session-by-session detail.

**Do not begin Phase 6.10 Implementation Checkpoint 1C, Wave C, Learning Engine, Broker Adapter, MT5,
live/paper trading, multi-position trading, Strategy Health integration, capital allocation across
edges, or WATCHLIST activation without its own dedicated CEO approval —
this document does not grant it.**
