# PROJECT_STATE — AI Quant Research Lab → AI Trader — v2 (OFFICIAL SESSION CLOSE, 2026-07-17)

**Purpose**: this is the single, authoritative, consolidated state document for the ENTIRE project —
both the frozen Research Lab and the AI Trader built on top of it — current as of this session's own
close. A brand-new chat, with no access to any prior conversation, must be able to reconstruct the
complete project from this document plus the ones it points to. Every fact below was verified directly
against `git log`/`git status`/`git diff`/a live `pytest`+`mypy --strict`+`coverage` run at close time
— nothing here is assumed or carried forward unverified. This document supersedes no prior report —
`PROJECT_STATE_v1.0.md`, `ROLLING_HEALTH_BACKTEST_HANDOFF.md`, and every phase's own dedicated report
remain the authoritative, detailed sources for their own respective scopes; this document exists to
make the CURRENT, FULL state reachable in one place.

---

## 0. Official state (authoritative, verify live before trusting)

```
Repository path:  C:\Users\MEDION GAMING\ai_quant_lab-research-main
Branch:           ai-trader-implementation
HEAD (pre-close): b33c548af3f29857992434697e10c5b9b7339985 (last commit before this session's own close commit)
Working tree:     clean (verified live at this document's own close)
```

**Note**: this session's own close commit (this document + `PHASE_6_10_PREPARATION.md` +
`NEXT_SESSION.md` + `CHANGELOG.md` + `ROLLING_HEALTH_BACKTEST_HANDOFF.md` updates) lands ONE commit
after `b33c548` — run `git log -1` to see the exact current HEAD; do not assume it is still `b33c548`
in any future session. Re-verify `git branch --show-current`/`git log -1`/`git status --porcelain`
directly before trusting any git-state claim anywhere in this project's documentation.

**Verified live at this close:**
```
pytest ai_trader/ -q            -> 1576 passed
mypy --strict ai_trader/ --exclude 'tests/'  -> Success: no issues found in 165 source files
coverage run --source=ai_trader -m pytest ai_trader/ -q
coverage report --omit="*/tests/*"           -> TOTAL 9649 stmts, 432 miss, 96%
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
  essentially all work across Phases 6.1–6.9A (§3–§6) took place.

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

## 7. Modules implemented (`ai_trader/`)

| Module | Status | Notes |
|---|---|---|
| `market_scanner/` | FROZEN (READY) | one disclosed, additive, CEO-approved touch from Wave B (optional `feature_history` field) |
| `strategy_manager/` | FROZEN (READY) | loads the Strategy Library, tracks contract Health/Lifecycle (schema/maturity — unrelated to trading performance) |
| `signal_engine/` | FROZEN (READY) | runs registered runtime evaluators; `SignalState` 9-state machine (`SIGNAL_ENGINE_STATE_MACHINE.md`) |
| `scoring_engine/` | FROZEN (READY) | scores/ranks signals; `Recommendation` enum + conflict resolution |
| `risk_manager/` | FROZEN (READY) | sizing, guards, cooldowns, portfolio limits (incl. the single-shared-symbol-slot `LIMIT_MAX_PER_SYMBOL` constraint) |
| `execution_engine/` | FROZEN (READY) | order construction/execution |
| `simulation/` | NOT frozen, extensible | `SimulationHarness`/`ExecutionSimulator`/`PortfolioSimulator`/`PerformanceAnalyzer`; `time_stop.py`/`trailing_stop.py` generic overlays; TWO disclosed fixes to date: the Phase 6.9 overlay-isolation fix, the Phase 6.9A `RiskEventRecord.strategy_id` field |
| `strategy_runtime/` | NOT frozen | `families/` — all 43 real evaluators; `registry.py`; `context_access.py`; `migration.py` |
| `strategy_health/` | NOT frozen, scoring UNCHANGED since its own build | `types.py`/`metrics.py`/`scoring.py`/`classifier.py`/`evaluator.py` (frozen scoring, never touched by any phase after its own build) + `rolling_gate.py` (Phase 6.9 addition, thin wrapper) |

## 8. What must NOT be modified (standing, cumulative across every phase)

- `code/`, `results/`, `knowledge/` (Research Lab) — frozen, 0-diff confirmed at every close.
- Every strategy contract, evaluator, and parameter.
- `ai_trader/strategy_health/`'s own scoring methodology (percentile-rank, Bühlmann shrinkage,
  PCA-derived weights, `WINDOW_PRIORITY`, classification bands) — frozen since its own build; only
  `rolling_gate.py` was ever added alongside it (a thin, permanent wrapper, no scoring logic).
- Scoring Engine weights, Risk Policy, Execution Engine rules — untouched except the two disclosed
  Simulation Framework fixes above (neither touches these frozen modules themselves).
- The sealed terminal holdout (2025-10-23 09:15 UTC → 2026-07-13 06:00 UTC) — never opened by anything.
- No strategy has ever been, or should be, permanently eliminated based on any AI Trader analysis.

## 9. Diagnostic artifacts preserved (cumulative, all committed, all referenced by name in their own reports)

- Phase 6.9: `phase69_rolling_backtest.py`, `phase69_analysis.py`, `phase69_analysis2.py`,
  `phase69_results.json`, `phase69_analysis.json`, `phase69_analysis2.json`.
- Relevance audit: `relevance12m_run.py`, `relevance12m_run_bcd.py`, `relevance12m_perstrategy.py`,
  `relevance12m_portfolioA.json`, `relevance12m_portfolioBCD.json`, `relevance12m_perstrategy.json`.
- Phase 6.9A: `phase69a_funnel_recorder.py`, `phase69a_funnel_run.py`, `phase69a_isolated_run.py`,
  `phase69a_analysis.py`, `phase69a_competitive_funnel.json`, `phase69a_isolated_funnel.json`,
  `phase69a_analysis.json`.

All of the above are deliberately preserved (a CEO-instructed exception to the repository's earlier
"delete scratch scripts after report capture" discipline, first established at Phase 6.9's own close),
so every phase's own findings stay fully reproducible without re-running anything from scratch.

## 10. Reading order for a brand-new session

1. This document (`PROJECT_STATE_v2.md`) — the complete current state.
2. `PHASE_6_10_PREPARATION.md` — the open question this project is currently sitting in front of.
3. In detail, in order: `PHASE_6_9_ROLLING_HEALTH_GATED_BACKTEST_REPORT.md` →
   `CURRENT_XAUUSD_12M_RELEVANCE_REPORT.md` → `PHASE_6_9A_STRATEGY_EVIDENCE_FLOW_AUDIT_REPORT.md`.
4. `ROLLING_HEALTH_BACKTEST_HANDOFF.md` for the Strategy Health System's own full methodology (§5
   there) and Phase 6.9's own original specification (§8 there, now marked CLOSED).
5. `PROJECT_STATE_v1.0.md` for the Research Lab's own frozen state (unchanged since 2026-07-14).
6. `CHANGELOG.md`'s own top entries for verified, dated, session-by-session detail.
7. `NEXT_SESSION.md` for the exact next-session procedure and git-state re-verification steps.

**Do not begin Phase 6.10, Wave C, Learning Engine, Broker Adapter, MT5, live/paper trading,
multi-position trading, Shadow Mode, or WATCHLIST activation without its own dedicated CEO approval —
this document does not grant it.**
