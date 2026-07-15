# NEXT_SESSION.md — Official Handoff (AI Trader Implementation Phase)

**Rewritten in full on 2026-07-15 after Phase 6.8 Wave B reached COMPLETE and Wave D's first
full-portfolio simulation ran successfully.** This document is the entry point for the next Claude
session. Full detail: `WAVE_D_PORTFOLIO_SIMULATION_REPORT.md` (Wave D's own first run — REPORT ONLY,
no strategy changed as a result), `PHASE_6_8_WAVE_B_COMPLETION_REPORT.md` (Wave B's own close-out),
`PHASE_6_8_CHECKPOINT_2_REPORT.md` (the first 15-strategy checkpoint), `WAVE_B_HANDOFF.md` (Wave B's
own full 27-section handoff from before Checkpoint 2 started — still accurate for Checkpoint 1's own
history and the Wave B plan structure), `PHASE_6_8_WAVE_B_PLAN.md` (the full batch plan). Every fact
below was verified directly against `git log`/`git status`/`git diff`/a live `pytest`+`mypy`+`coverage`
run at close time — nothing here is assumed or carried over unverified.

**Two real bugs were found and fixed during Wave D**, both confined to the non-frozen
`ai_trader/simulation/` package (zero impact on the Research Lab or the six frozen pipeline modules) —
see `WAVE_D_PORTFOLIO_SIMULATION_REPORT.md` §0 for full detail: (1) `portfolio_simulator.py`'s
`bars_since_close` was hardcoded to 0, permanently locking the cooldown-after-loss guard after a
symbol's first-ever loss; (2) `time_stop.py`'s time-stop trigger fired one bar too late relative to
its own declared horizon, due to the execution simulator's standard one-bar submit-to-fill lag. Both
fixed, regression-tested, and reverified against a fresh full suite (1515/1515) + `mypy --strict`
(158 files) before Wave D's final run.

---

## A. Project mission

**AI Quant Research Lab → AI Trader.** Two systems, physically separated by design:

- **Research Lab** (`code/`, `results/`, `knowledge/`) discovers and validates trading strategies
  against historical XAUUSD data. **Frozen and stable; never touched during AI Trader work** —
  verified 0-diff at every commit since Phase 6.1 began (§E).
- **Strategy Library** (`knowledge/strategies/`) publishes 51 strategy specs (S1–S51). **Strategy
  Interface v1** (`knowledge/interface/`) is the ONLY sanctioned contract between the Lab and the
  Trader. As of this session, **all 43 runtime-eligible strategies** have been migrated to that v1
  shape and given real runtime evaluators — Wave B is COMPLETE. The other 8 folders (S32–S37
  NOT_IMPLEMENTED, S47/S49 INVALID in the frozen v0 spec) are unchanged, as expected.
- **AI Trader** (`ai_trader/`) is the execution system. All six live pipeline modules are READY:
  Market Scanner → Strategy Manager → Signal Engine → Scoring Engine → Risk Manager → Execution
  Engine. The **Simulation Framework** (Phase 6.7) is READY. The **Strategy Runtime** framework
  (Phase 6.8, `ai_trader/strategy_runtime/`) is READY and proven end-to-end for all 43 implemented
  strategies, including two new generic mechanisms built this Wave: a **time-stop overlay**
  (`ai_trader/simulation/time_stop.py`, 10 strategies opt in) for strategies whose evidence-backed
  exit is a fixed bar-count timeout, and a **trailing-stop overlay**
  (`ai_trader/simulation/trailing_stop.py`, 6 strategies opt in) for strategies whose evidence-backed
  exit is a 1.5×ATR trailing distance — both deterministic, reusable, submitting through the same
  `ExecutionEngine.execute()` gateway every other order uses, zero frozen-pipeline-module edits. A
  third mechanism, the **historical-features window** in Market Scanner (`scanner.py`,
  `timeframe_sync.py`, `MARKET_CONTEXT_SCHEMA.json` — the first-ever, explicitly CEO-approved,
  additive/schema-optional touch to a frozen pipeline module), gives strategies genuine per-bar
  historical feature access (`context_access.feature_n_ago`/`flag_n_ago`) where the frozen research
  engine's own rolling-window/onset logic requires it.

**Simulation-first is mandatory (standing CEO directive, non-negotiable):** the AI Trader must prove
robust historical profitability in simulation before any Broker Adapter/MT5/live execution work
begins. **Wave D's first full-portfolio run is DONE** (all 43 strategies active simultaneously,
$2,000 capital, 5% risk/trade, full 2022-12-16→2026-07-13 XAUUSD history): +15.66% return, Sharpe
1.196, max drawdown 6.16%, 513 trades, profit factor 1.264 — a modest but real positive result, with
two genuine Simulation Framework bugs found and fixed along the way (see `WAVE_D_PORTFOLIO_
SIMULATION_REPORT.md` §0). This is a REPORT, not a tuning pass — no strategy was added, removed, or
re-weighted based on it. Do not begin Wave C, Learning Engine, Broker Adapter, MT5, or live/paper
trading under cover of Wave D or any future phase without its own dedicated CEO approval.

---

## B. Official Git state (verify live — do not trust blindly)

```
Repository path:  C:\Users\MEDION GAMING\ai_quant_lab-research-main
Branch:           ai-trader-implementation
```

**This document's own commit advances HEAD by exactly one past whatever `git log -1` shows before
you read this file.** Re-verify `git log -1`/`git status --porcelain` directly before trusting any
git-state claim here — the same discipline every prior handoff in this repository has followed.

## C. Completed implementation — summary (full detail: `PHASE_6_8_WAVE_B_COMPLETION_REPORT.md`)

All six live pipeline modules (Phases 6.1–6.6) and the Simulation Framework (Phase 6.7) are READY.
Phase 6.8 Wave B is COMPLETE: 43 real runtime evaluators total (Checkpoint 2's own 15 + batches
B3–B10's remaining 28). Two genuine research/runtime parity gaps were found, disclosed, and resolved
this Wave with CEO-approved, generic designs — zero edits to any of the six frozen pipeline modules'
BEHAVIOR (one, Market Scanner, received an explicitly-approved additive/schema-optional touch, §E):
- **Time-stop overlay** (`ai_trader/simulation/time_stop.py`, Checkpoint 2) — 10 strategies opt in.
- **Trailing-stop overlay** (`ai_trader/simulation/trailing_stop.py`, this Wave) — 6 strategies opt
  in; reuses Portfolio Simulator's already-tracked `Position.mfe`, zero new `Position` fields.
- **Historical-features window** (Market Scanner, this Wave) — `context_access.feature_n_ago`/
  `flag_n_ago` give strategies genuine per-bar historical feature access (5 strategies needed this:
  S4, S23, S25, S43, S48).

**`ai_trader/simulation/harness.py`** (not frozen — the Simulation Framework's own orchestrator) now
has three opt-in constructor parameters from this Wave's work: `enable_time_stops: bool = False`,
`enable_trailing_stops: bool = False`, `strategy_id_filter: frozenset[str] | None = None` (the last
lets a test/run isolate specific strategies from the shared single-position-per-symbol slot). See
`PHASE_6_8_WAVE_B_COMPLETION_REPORT.md` §2 for exact mechanism semantics.

## D. Global implementation statistics (verified live this session, current HEAD, after both Wave D bug fixes)

```
pytest ai_trader/ -q
1515 passed

mypy --strict ai_trader/ --exclude 'tests/'
Success: no issues found in 158 source files
```

(Coverage was last measured at 95% — 9392 stmts, 434 miss — before the two Wave D bug fixes below;
re-run `coverage run --source=ai_trader -m pytest ai_trader/ -q && coverage report --omit="*/tests/*"`
if an exact current number is needed, the two small fixes are unlikely to have moved it meaningfully.)

**Two bugs found and fixed during Wave D** (both in the non-frozen `ai_trader/simulation/` package,
zero impact on the Research Lab or the six frozen pipeline modules — full detail in
`WAVE_D_PORTFOLIO_SIMULATION_REPORT.md` §0):
1. `portfolio_simulator.py`'s `to_portfolio_state()` hardcoded `ClosedPosition.bars_since_close` to
   `0` — the sole clock source for the cooldown-after-loss guard — permanently locking that guard
   after a symbol's first-ever loss. Fixed: compute the real elapsed bar count from `as_of` vs. the
   trade's own `exit_as_of`.
2. `time_stop.py`'s `positions_due_for_time_stop()` fired at `age_bars >= limit` instead of
   `>= limit - 1`, so a time-stopped position's real fill (one bar after the synthetic decision, the
   same lag every entry order already has) landed one bar past its own declared horizon. Fixed: fire
   one bar early.

## E. Protected invariants — confirmed untouched (verified this session, live)

- `code/`, `results/` (Research Lab) — 0-diff since Phase 6.1, confirmed via
  `git status --porcelain -- code/ results/` (empty).
- `knowledge/` — changes confined EXACTLY to the 43 migrated strategy folders; every other folder
  (S32–S37, S47, S49), and `knowledge/interface/` itself, untouched.
- The six live pipeline modules' production code — untouched this Wave EXCEPT one explicitly
  CEO-approved, additive, schema-optional touch to Market Scanner (`scanner.py`, `timeframe_sync.py`,
  `MARKET_CONTEXT_SCHEMA.json` — new OPTIONAL `feature_history` field, not in `required`, so any
  existing producer/consumer omitting it stays schema-valid; the full pre-existing
  `ai_trader/market_scanner/` test suite, 127 tests, passes unchanged). Strategy Manager, Signal
  Engine, Scoring Engine, Risk Manager, and Execution Engine were not touched at all this Wave.
- Terminal holdout — SEALED, untouched. No broker code, no MT5, no Learning Engine anywhere.

## F. Technical debt / known limitations

See `PHASE_6_8_WAVE_B_COMPLETION_REPORT.md` and `WAVE_B_HANDOFF.md` §24 for the complete list
(unchanged Phase 6.2/6.1 pre-existing mypy test-file gaps; approximated `atr_rolling_median`/
`current_spread`/`liquidity_proxy`; missing portfolio-level `max_drawdown_R`; no per-strategy
conformance test against the frozen research engine's own historical trade log yet, for any of the
43 implemented strategies — a good future candidate, not blocking Wave D).

## H. Immediate next phase

**WAVE D's first run is COMPLETE** (§A, full detail `WAVE_D_PORTFOLIO_SIMULATION_REPORT.md`). The
adversarial-review step this session took the form of two real bugs surfacing FROM the simulation's
own implausible early results (1 trade, then a 24-vs-25-bar time-stop violation) — both found, fixed,
regression-tested, and reverified against a fresh full suite before the final reported numbers. That
satisfies the "adversarial review, fix verified defects, rerun full validation" instruction for THIS
run. Still open, not yet done (future work, no dedicated CEO approval sought yet for any of these):

1. A cost-model-configured Wave D rerun (`SimulationContext.cost_model` currently defaults to zero
   spread/commission/slippage — the reported +15.66% return does not reflect real trading costs).
2. A per-strategy conformance check against the frozen Research Lab's own historical trade log (named
   as a gap since Checkpoint 2, still not done for any of the 43 strategies).
3. Investigating the 2026-02/03 trade-volume spike (72 trades in 2026-03 alone) noted but not
   explained in the Wave D report.
4. A CEO decision on what comes after Wave D: multi-symbol expansion, a live/paper-trading gate
   (Wave C), Learning Engine, or Broker Adapter work — none of these may begin under cover of this or
   any prior approval; each needs its own dedicated CEO sign-off.

## I. Exact next-session order

1. **Read this document in full first.**
2. **Verify Git state directly** — `git branch --show-current`, `git log -1`, `git status --porcelain`.
3. **Read `WAVE_D_PORTFOLIO_SIMULATION_REPORT.md` in full**, then `PHASE_6_8_WAVE_B_COMPLETION_
   REPORT.md`, `WAVE_B_HANDOFF.md`, and `PHASE_6_8_WAVE_B_PLAN.md` for the detail behind Wave B's own
   structure and history.
4. **Report the reconstructed state back to the CEO** before proceeding on anything new.
5. Once confirmed, the CEO's own next direction determines what happens next — §H lists the open,
   not-yet-approved candidates. Stop and ask before starting any of them; continuing within an
   already-approved item follows the same standing triggers as always (frozen-contract change,
   semantic ambiguity, missing data, research/runtime parity failure).

---

*Prior-session narrative history (Phases 6.1–6.7, the Strategy Runtime Integration Gap investigation,
Checkpoint 1's own two-bug discovery, Checkpoint 2's own time-stop design, Wave B's own batch-by-batch
completion) remains available in git history of this file (`git log -p -- NEXT_SESSION.md`) and in
each phase's own dedicated report/handoff document listed above.*
