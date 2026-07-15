# Phase 6.8 — Checkpoint 2 Report: Wave B Batches B1 + B2 (14 Strategies)

**Date:** 2026-07-15. **Scope:** Wave B Checkpoint 2 (per `PHASE_6_8_WAVE_B_PLAN.md` §4) — migrate and
implement mechanism batches B1 (session/calendar, 9 strategies) and B2 (liquidity/sweep/reversal,
5 strategies), the first real batches beyond the S1 reference slice, per the CEO's explicit
authorization to begin Wave B this session. **Verdict: CHECKPOINT 2 ACHIEVED.**

---

## 1. What was built

14 new real, evidence-faithful runtime evaluators (`ai_trader/strategy_runtime/families/`),
alongside S1's own Checkpoint 1 reference slice, all composing with the six frozen pipeline modules
via the SAME structural-typing pattern Checkpoint 1 established — **zero lines of any of the six
frozen pipeline modules were modified**:

| batch | strategies | mechanism |
|---|---|---|
| B1 | S6, S16, S17, S18, S19, S24, S29, S30, S31 (9) | session/calendar/time-based |
| B2 | S2, S11, S12, S21, S22 (5) | liquidity/sweep/reversal (extends S1's own proven pattern) |

Each strategy implements EXACTLY its own contract's `executable_default` parameter tuple — verified
against the frozen research engine's own grammar functions (`code/mstrat.py`, `code/mstrat_ext.py`,
read-only reference, never imported), not just the v0 JSON's prose. Two genuine, non-obvious
fidelity details were caught only by reading the frozen grammar directly (exactly the discipline
that caught Checkpoint 1's own two bugs):
- **S12**'s own `target=='center'` field silently OVERRIDES its literal `exit=rr2` grammar value to
  a fixed **1.5R** target (`code/mstrat.py::s12_setups`: `if h['target']=='center': ek,ep=('rr',1.5)
  if exit!='time' else ('time',24)`) — implemented as the frozen engine actually behaves, not as
  the v0 JSON's own `exit` field alone would naively suggest.
- **S12**'s own stop is `beyond_ext` (2 ticks past the rolling extreme), NOT the `atr`-based formula
  most other strategies in this batch use — the specific branch NOT taken matters.

## 2. Research/runtime parity gap found and resolved: the generic time-stop mechanism

Five of B1's own evidence-backed `executable_default` selections (S16, S17, S18, S19, S24) chose
the frozen research engine's own `exit=time` grammar option (`_exitmap`: `exit_kind=='time' -> 24`
bars) — a fixed-bar-count forced exit independent of price, confirmed to have NO corresponding
mechanism anywhere in the AI Trader runtime before this session (`STRATEGY_API_v1.md`'s own `Signal`
schema carries only entry/stop/target; `execution_simulator.py` only ever adjudicates STOP vs.
LIMIT(target) orders). Per the CEO's explicit design mandate (deterministic, reusable, configurable,
no strategy-specific code, preserving frozen Research Lab semantics, single Execution Engine
gateway, no duplicated execution path), a generic, additive time-stop overlay was built:

- `RuntimeEvaluator.time_stop_bars: int | None` (new, additive Strategy Runtime field) — a strategy
  opts in purely by declaring its own bar count (24, sourced read-only from `code/mstrat.py`'s own
  `_exitmap` convention); every other strategy is unaffected (defaults to `None`).
- `ai_trader/simulation/time_stop.py` (new, non-frozen Simulation Framework module) — a pure
  `positions_due_for_time_stop()` function plus `build_time_stop_decision()`, which synthesizes an
  ordinary, reduce-only `RiskDecision` (the exact same shape every real opportunity produces) and
  submits it through `ExecutionEngine.execute()` — **the single, unmodified gateway every other
  order in the system already uses**. No `emergency_flatten` reuse (which would have permanently
  latched the engine's lifecycle state and silently blocked every other strategy's future entries —
  a real regression caught and avoided during design, not glossed over) and no direct Simulation
  Framework submission bypassing Execution Engine.
- `ai_trader/simulation/harness.py` (already-established extensible orchestrator, extended once more
  with an opt-in `enable_time_stops` constructor flag, default `False`, Phase 6.7's original
  behavior unchanged).
- **Zero edits to any of the six frozen pipeline modules or to `knowledge/interface/`'s own contract
  schema** — the entire mechanism lives in already-extensible Phase 6.8 code, reusing pre-existing,
  already-tested frozen building blocks (`build_order`'s own `reduce_only` handling, already built
  for exactly this shape of decision).

Proven end-to-end (§4): the mechanism enforces real 24-bar force-closes over real historical data,
with determinism intact.

## 3. Migration (v0 → v1), all 14 strategies

`knowledge/strategies/{folder}/strategy.json` converted from the Research Lab's v0 export shape to
Strategy Interface v1 for all 14 strategies (originals preserved as `strategy.v0.json` in each
folder, never deleted), via a one-off migration script (not committed, output only) reusing
`ai_trader.strategy_runtime.migration.build_v1_contract_dict` — the same mapper Checkpoint 1 built.
Every migrated contract is schema-valid (`validate_contract`) and matches the exact strategy_id.

## 4. End-to-end proof (Checkpoint 2's own bar)

`ai_trader/strategy_runtime/tests/test_checkpoint2_end_to_end.py`, run against real historical
XAUUSD M15 data (2023-01 → 2026-07, $2,000 starting capital, 5% risk/trade — the Wave D account
parameters) through the real Market Scanner → Strategy Manager → all 15 real evaluators → Signal
Engine → Scoring Engine → Risk Manager → Execution Engine → Execution Simulator → Portfolio
Simulator → Performance Analyzer, `enable_time_stops=True`:

- All 15 strategies (S1 + 14) reach real runtime handles before the run.
- At least one real order submitted, at least one real fill, at least one real closed trade.
- Every trade's `pnl_r` is sane (downside bounded near -1R by its own real stop; upside capped near
  +2R/+3R only for rr-exit strategies, uncapped for the 5 time-exit strategies, which is the
  economically correct behavior for an exit with no price target).
- Every time-exit strategy's own trade `holding_bars <= 24`, by construction.
- The full `SimulationReport` is schema-valid and internally consistent.
- **Determinism holds** with all 15 real strategies AND the new time-stop mechanism active:
  identical `(SimulationContext, seed)` produces a byte-identical report.

## 5. Pre-existing tripwires updated (documented, not a regression)

Exactly the same "tripwire fires, get updated deliberately" pattern Checkpoint 1's own S1 migration
already established for these same two files:

- `ai_trader/strategy_manager/tests/test_real_library_integration.py` — `report.loaded` now asserts
  the real 15-strategy set (verified live, not assumed); `len(report.failed)` updated from 51 to 46
  (36 still-v0 INVALID + 10 schema-valid-but-INCOMPATIBLE under the test's own minimal `FakeScanner`
  fixture — 5 of the 15, S18/S22/S29/S30/S31, are fully COMPATIBLE even under that fixture since
  their own `required_data` needs only `m_atr`); overall health updated from FAILED to DEGRADED.
- `ai_trader/strategy_runtime/tests/test_s1_end_to_end.py` — no longer asserts S1 is the ONLY active
  handle or that every trade belongs to S1 (both stopped being true the moment Checkpoint 2 shares
  the single-position-per-symbol slot across 15 strategies); still asserts S1 itself produces at
  least one real, sane trade with its own rr2 upside cap.

## 6. Global implementation statistics (verified live this session)

```
pytest ai_trader/ -q
1367 passed

mypy --strict ai_trader/market_scanner ai_trader/strategy_manager ai_trader/signal_engine \
              ai_trader/scoring_engine ai_trader/risk_manager ai_trader/execution_engine \
              ai_trader/simulation ai_trader/strategy_runtime --exclude 'tests/'
Success: no issues found in 126 source files

coverage run --source=ai_trader -m pytest ai_trader/ -q
coverage report --omit="*/tests/*"
TOTAL   8121 stmts   361 miss   96%
```

## 7. Protected areas — confirmed live

- `code/`, `results/` (Research Lab) — still 0-diff since Phase 6.1 (`git diff cef57c1~1 -- code/
  results/` empty).
- The six live pipeline modules' production code — byte-identical to `af00953`; only ONE additional
  test file changed this session (`strategy_manager/tests/test_real_library_integration.py`, a
  documented tripwire), alongside `strategy_runtime/tests/test_s1_end_to_end.py` (also a documented
  tripwire, not a frozen pipeline module).
- `knowledge/` — changes confined EXACTLY to the 15 migrated strategy folders (S1 + the 14 this
  session); every other one of the 51 strategy folders, and `knowledge/interface/` itself, untouched.
- Terminal holdout — SEALED, untouched. No broker code, no MT5, no Learning Engine anywhere.

## 8. Checkpoint 2 verdict

**ACHIEVED.** 15 of 43 runtime-eligible strategies now have real, evidence-faithful evaluators,
tested (unit + contract-migration + registry + end-to-end), `mypy --strict` clean, 96% covered,
zero regressions, every protected invariant verified live. A genuine research/runtime parity gap
(the `exit=time` mechanism) was found, disclosed, designed with explicit CEO sign-off, and resolved
with a generic, reusable, zero-frozen-module-edit mechanism — not silently worked around.

**Not yet started: the remaining 8 Wave B groups** (B3 VWAP/value, B4 imbalance, B5 candlestick, B6
order-flow, B7 breakout/compression, B8 trend/momentum, B9 mean-reversion, B10 composite/meta — 28
more strategies) per `PHASE_6_8_WAVE_B_PLAN.md`'s own migration order. Per the CEO's own Wave B
approval, Wave B may continue family-by-family or in small mechanism batches without re-asking
approval per batch, except for the same standing triggers (frozen-contract change, semantic
ambiguity, missing data, research/runtime parity failure) — reporting this checkpoint now, as that
approval anticipated, rather than continuing unsupervised into 28 more strategies in the same pass.
