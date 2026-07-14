# Signal Engine v1 — Implementation & Validation Report (Phase 6.3)

**Date:** 2026-07-14. **Scope:** production implementation of the Signal Engine against the frozen
`ai_trader/signal_engine/*.md`/`*.json` specification, following the exact process and quality bar
established for Market Scanner v1 (Phase 6.1) and Strategy Manager v1 (Phase 6.2): implement → test
continuously → adversarial review → fix every real issue → report honestly.
**Verdict: READY.** (see §6)

---

## 1. What was built

11 production modules under `ai_trader/signal_engine/` (10 source `.py` files + `py.typed` +
`requirements.txt`), implementing every stage the architecture names:

| architecture component | module |
|---|---|
| Fixed evaluation pipeline (Precondition → Context → Signal Evaluation → Explanation) | `pipeline.py` |
| Context Validation (per-strategy sufficiency, not the Scanner's aggregate) | `context_check.py` |
| Explanation Builder | `explanation.py` |
| Signal Assembler | `assembler.py` |
| Output Collector (schema validation, semantic checks, dedup) | `validator.py` (+ `schema_validation.py`) |
| Public API facade + timeout/isolation enforcement | `engine.py` (`SignalEngine`) |
| Value types (mirrors `SIGNAL_SCHEMA.json`/`SIGNAL_EXPLANATION_SCHEMA.json` 1:1) | `types.py` |
| Config / errors | `config.py`, `exceptions.py` |

**181 tests** across 11 test files (unit tests per module, covering all 9 signal states and every
fail-safe path, plus `test_engine_integration.py` against the real Strategy Manager's
`StrategyRuntimeHandle`). `mypy --strict`: 0 errors across all 26 source files (Signal Engine's 10 +
its own `tests/` package). Coverage: **99%** (source only, test files excluded from the denominator)
— the remaining 6 uncovered statements are `schema_validation.py`'s file-missing/corrupt-JSON/
compile-failure defensive branches, the exact same class of gap Market Scanner's and Strategy
Manager's own reports left uncovered, for the same reason (environment failures, not exercised by a
healthy test run).

## 2. Design decisions worth recording (not redesign — filling gaps the spec leaves to the implementer)

- **No strategy anywhere has real, executable `detect`/`generate_signal`/etc. logic.** The Strategy
  Manager's only concrete `StrategyHandle.api` (`StrategyRuntimeHandle`) deliberately implements only
  `required_context()` and raises `StrategyApiNotImplementedError` for the other five methods this
  pipeline calls (`STRATEGY_MANAGER_VALIDATION_REPORT.md` §2). The Signal Engine's job is the fixed
  ORCHESTRATION machinery around whatever those methods return — it is generic, protocol-typed
  (`StrategyApiLike`/`StrategyHandleLike` in `pipeline.py`), and handles today's "every real strategy
  raises" reality exactly like any other strategy-side failure: isolated, classified, never fabricated.
  `test_engine_integration.py` proves this against the real Strategy Manager end-to-end.
- **BUY/SELL, not LONG_READY/SHORT_READY, for every present+confirmed signal in v1.**
  `runtime_responses.v1.schema.json`'s `Signal` shape has no field distinguishing "trigger now" from
  "armed, awaiting trigger" — v1 treats every present+confirmed signal as immediately actionable,
  matching the frozen research engine's own "signal at bar close, fill at next open" convention (the
  next-open fill is an execution-layer mechanic, not a "still pending" setup state). `LONG_READY`/
  `SHORT_READY` remain fully implemented, reachable states, ready for a future interface MINOR that
  adds an explicit pending/trigger field — documented in `pipeline.py`'s own module docstring.
- **`missing_context_items()` judges sufficiency against THIS strategy's own `required_context()`**,
  never the Market Scanner's aggregate `context["sufficiency"]` field (which reflects the union of
  every active strategy's requirement, and can read `PARTIAL` even when one particular strategy's own,
  smaller requirement is fully satisfied).
- **`timestamp`/`generated_at`/`as_of` are always the evaluated context's own `as_of`, never
  wall-clock** — the one thing that makes "identical `(context, handle, trader_state)` ⇒ identical
  signal" hold bit-for-bit across replays. Only `evaluation_time_ms` uses real wall-clock
  (`time.perf_counter()`), and it is purely informational, never fed back into any STATE decision.
- **`EngineConfig.max_workers` defaults to `1`** (fully sequential) — the simplest, always-correct
  implementation of "strategies are isolated and independent, evaluations MAY run in parallel"
  (architecture §9); raising it opts into real concurrency, safe given strategy isolation.

## 3. Independent adversarial review — 5 real bugs found and fixed

Following the same technique that caught 2 bugs in Market Scanner and 6 in Strategy Manager, a
fresh-eyes review agent (no memory of writing the code) read all 7 frozen spec documents in full, then
all 10 source files (plus the upstream Strategy Manager types it consumes), hunting specifically for
fail-safe violations, determinism/isolation breaks, and schema-conformance gaps. It found 7 issues (2
CRITICAL, 3 HIGH, 2 MEDIUM); 5 were real, actionable bugs and were fixed with regression tests, 1
MEDIUM was a real gap and was fixed, and 1 MEDIUM was verified to be correct-as-designed (see below).

| # | bug | file | severity | fix |
|---|---|---|---|---|
| 1 | `_collect()` read `handle.contract` **before** entering its try/except — any `StrategyHandleLike` whose `contract` property raises (a legitimate structural possibility per the Protocol) would crash the exception raises out of `_collect`, aborting `evaluate()`'s entire batch-building `tuple()` for **every** strategy in the batch, not just the broken one | `engine.py` (`_collect`) | **CRITICAL** | Moved the `contract = handle.contract` read inside the existing `try:` block, so a broken read is caught by the same `except Exception` → `CORRUPTED_OUTPUT` path every other strategy-side failure already uses. |
| 2 | With the documented default `max_workers=1`, `Future.result(timeout=...)` can only stop *waiting* on a hung strategy call — Python cannot forcibly interrupt a running thread. A genuinely-hung (not merely slow) strategy permanently occupies the sole worker; every later cycle sharing that same, engine-lifetime executor would queue forever behind it, and `shutdown()`'s `wait=True` would deadlock | `engine.py` (`configure`, `_collect`, `shutdown`) | **CRITICAL** | Added `_refresh_executor()`: the worker pool is discarded (non-blockingly, never waiting on whatever may be stuck) and replaced with a fresh one at the start of every `evaluate()`/`evaluate_strategy()` call that actually submits work. Bounds a hang's blast radius to the single cycle it occurred in — the best a pure-thread-based design can do without process-level isolation (out of scope for this phase). |
| 3 | `_is_scoped_to_symbol()` treated a `required_context()` exception the same as "not scoped" (`return False`) — a genuinely-scoped strategy whose scoping call happened to raise would silently vanish from the batch with **zero trace**: no signal, no quality flag, nothing in statistics, violating "one signal per (strategy, symbol), always" | `engine.py` (`_is_scoped_to_symbol`) | **HIGH** | Changed to fail OPEN: exception → `return True` (treat as scoped). The strategy is then routed into the full pipeline call, whose own timeout+exception boundary correctly classifies it as `INVALID`/`CORRUPTED_OUTPUT` — a visible, disclosed failure instead of a silent omission. |
| 4 | `evaluate()`'s missing-`as_of` fallback returned an **empty** batch (`signals=()`) regardless of how many handles were passed — contradicting `SIGNAL_ENGINE_API.md` §1's explicit text: "the batch is produced with all signals INVALID/NEED_CONTEXT ... never a crash." `evaluate_strategy()` had no such guard at all, silently defaulting to `as_of=0` | `engine.py` (`evaluate`, `evaluate_strategy`) | **HIGH** | Added `_missing_as_of_signal()`: every scoped handle now gets one classified `INVALID`/`MISSING_TIMESTAMP` signal via the assembler's safest (`contract=None`) fallback path, in both `evaluate()` and `evaluate_strategy()`. |
| 5 | The Output Collector's documented deduplication ("dedupe (strategy_id\|symbol\|as_of); keep one, drop extra with `[DUPLICATE_SIGNAL]`" — architecture §7, SEQUENCE.md §2) was entirely unimplemented; two handles sharing a `strategy_id` would produce two identical-`signal_id` signals in the same batch, double-counted in `counts_by_state` | `engine.py` (new `_dedupe()`, wired into `evaluate()`) | **HIGH** | Added `_dedupe()`: after evaluation, duplicates (same `strategy_id`+`symbol`+`as_of`) are collapsed to the first occurrence (deterministic, given the already-stable-sorted handle order); every dropped extra is recorded in `degraded_reasons` for observability rather than silently vanishing. |
| 6 | `validator.py`'s `MISSING_TIMESTAMP` check tested `signal.as_of is None` — but `StrategySignal.as_of` is typed plain `int` (never `Optional`) and the real "missing" representation, per `assembler.assemble_signal`'s own `meta.get("as_of", 0)` fallback, is the sentinel `0`. The check was permanently unreachable dead code | `validator.py` | **MEDIUM** | Changed to `if not signal.as_of:`, which catches the real `0` sentinel (and would also catch a stray `None` if the field's type were ever loosened later — defense in depth). |

One additional MEDIUM finding — `validator.py`'s `UNKNOWN_STRATEGY` check is never exercised because
no call site (internal or the public `validate_signal(signal) -> ValidationResult`) ever supplies
`known_strategy_ids` — was investigated and found to be **correct as designed, not a bug**:
`SIGNAL_ENGINE_API.md` §3 documents `validate_signal(signal: StrategySignal) -> ValidationResult`
with no second parameter, and the engine is explicitly "no research access" (architecture §1) — it has
no persistent registry of active strategy ids to check against; it only ever receives handles per-cycle.
The parameter exists in `validator.py` as forward-compatible, reusable plumbing (mirroring the same
function's use inside the engine's own internals), correctly unexercised by the frozen public API as
written today. No code change was made for this finding; it is recorded here for the audit trail.

All 6 fixed issues got dedicated regression tests proving the fix (e.g.
`test_broken_contract_property_does_not_crash_the_whole_batch`,
`test_a_hung_strategy_does_not_wedge_the_next_cycle`,
`test_handle_whose_required_context_raises_is_still_evaluated_and_classified`,
`test_missing_as_of_produces_one_invalid_signal_per_scoped_handle`,
`test_duplicate_strategy_id_in_the_same_cycle_is_deduped_keeping_one`,
`test_as_of_zero_sentinel_is_flagged_missing_timestamp`). The review found **no** issues with pipeline
stage ordering (health → can_trade → context sufficiency → detect → generate_signal → confirmations,
exactly matching `SIGNAL_ENGINE_STATE_MACHINE.md` §2), direction/state schema `allOf` consistency,
`trade_params` null-ness for non-actionable states, determinism (no wall-clock/randomness anywhere in
business logic), or `evaluate`/`evaluate_all` ordering guarantees.

## 4. Final numbers (after all fixes)

```
pytest ai_trader/signal_engine/tests/ -q
181 passed in 0.67s

mypy --strict ai_trader/signal_engine
Success: no issues found in 26 source files

coverage run --source=ai_trader.signal_engine -m pytest ai_trader/signal_engine/tests/ -q
coverage report --omit="*/tests/*"
TOTAL   693 stmts   6 miss   99%

pytest ai_trader/ -q   (Market Scanner + Strategy Manager + Signal Engine together)
559 passed in 3.21s

mypy --strict ai_trader/market_scanner ai_trader/strategy_manager ai_trader/signal_engine --exclude 'tests/'
Success: no issues found in 47 source files   (no regression in either prior module)
```

## 5. Protected invariants — confirmed untouched

- **Research Lab** (`code/`, `results/`, `data/`), **Strategy Library** (`knowledge/strategies/`),
  **Strategy Interface v1** (`knowledge/interface/`) — read-only; zero files modified.
- **Market Scanner** (`ai_trader/market_scanner/`) and **Strategy Manager**
  (`ai_trader/strategy_manager/`) implementations — zero files modified. The Signal Engine only
  *imports* Strategy Manager's already-published types (`Contract`, `ConfidenceLevel`, `Regime`,
  `RequiredContext`, `StrategyHandle`/`StrategyRuntimeHandle` via the `StrategyHandleLike` Protocol)
  and Market Scanner's `DataQualityLevel` — never touches their source.
- **No broker code, no MT5, no live trading, no Scoring Engine, no Risk Manager, no Learning Engine**
  — none exist anywhere in this diff, per the CEO directive's explicit exclusion list.
- **The Signal Engine never trades, scores, sizes, or executes** — verified by its own scope (pure
  `(context, handle, trader_state) → StrategySignal` evaluation, no side effects beyond internal
  statistics bookkeeping) and confirmed by the adversarial review.

## 6. Verdict

**Signal Engine v1 is READY.**

- Implementation: every architecture component built, matching the frozen spec exactly (no redesign —
  every design decision in §2 fills a genuine spec gap, never contradicts documented behavior).
- Tests: 181/181 passing, covering all 9 signal states, every fail-safe path (malformed response,
  exception, timeout, missing context, missing as_of, duplicate strategy id, broken contract read),
  determinism, multi-symbol isolation, and a real-Strategy-Manager integration test.
- Types: `mypy --strict` clean across all 26 source files (10 production + test package).
- Coverage: 99%, remaining gaps are documented defensive/environment-only branches.
- Independent adversarial review: completed, found 7 issues (5 real bugs fixed + regression-tested, 1
  real gap fixed + regression-tested, 1 verified correct-as-designed), no outstanding findings.
- Protected invariants: confirmed untouched. Full `ai_trader/` suite (559 tests, 47 source files)
  green with no regressions in Market Scanner or Strategy Manager.

Per the standing "stop between every phase" directive and the CEO's explicit instruction for this
task ("Stop immediately after Signal Engine receives its final READY / NOT READY verdict"): **this
verdict does not itself authorize starting Scoring Engine, Risk Manager, Learning Engine, Broker
Adapter, or MT5 integration.** That requires an explicit new CEO go-ahead.
