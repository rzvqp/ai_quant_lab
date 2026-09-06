# MT5 Timestamp/Watermark Drift — Fix Report

Fixes the defect found and diagnosed (not fixed) in `VE_AI_TRADER_GENERAL_OBSERVER_V1_1_REAL_MT5_E2E_FINDINGS.md`, per CEO mandate.

## 1. Reproduced first

Confirmed pre-fix, via the real, live terminal: `test_no_duplicate_processing_on_second_tick_with_no_new_bars` failed 3 of 5 dedicated re-runs and 1 of 1 full-suite runs prior to any change (~60% observed failure rate this session), always with the watermark differing by exactly 1 second, never a multiple of 900 (M15's own bar duration).

## 2. Root cause, confirmed precisely (not merely inferred)

Isolated diagnostics (outside pytest, outside `GeneralObserverTick`) proved the mechanism directly:
- Holding the causal cutoff (`now_fn`) **fixed** across two `fetch_causal_closed_bars` calls, at gaps of 0.15s and 0.7s (45 combined attempts): **0 mismatches**.
- Using the **real**, advancing `now_fn=time.time` at a realistic ~0.7s gap (matching `GeneralObserverTick.tick()`'s own actual measured duration, 0.70s for its first call): **11 of 15 mismatches**, with the "last bar's" computed `ts_close` climbing by **exactly 1 second per call**, in a smooth, continuous sequence — never a ~900-second jump.

This pinpointed `mt5_read_only_source.measure_broker_offset_seconds()`: it computes `offset = tick.time - now_fn()`, where `tick.time` is the timestamp of the **last price tick**, not a continuously-advancing broker-clock reading. During a quiet market moment (no new tick between two calls), `tick.time` stays frozen while `now_fn()` (true wall-clock) keeps advancing — so every bar's offset-corrected timestamp drifts upward by approximately the real elapsed time since the market last ticked, for as long as it stays quiet.

**Independent confirmation this is a known bug class, not a novel hypothesis**: `ai_trader/live_signal_source/bar_feed.py::make_broker_offset` documents, in its own module docstring, discovering and fixing the *exact same root cause* independently, in a different part of this repository: *"a tick's `.time` is the timestamp of the LAST PRICE TICK, not a live server clock... offset estimates swinging by over 2500 seconds within the same session."* That file's own fix (caching the offset, keyed on a dedicated M1 probe bar's own identity, refreshed only when that identity changes) is the direct inspiration for the fix below — adopted at a narrower scope appropriate to this file's own, smaller, `symbol_info_tick`-based measurement, not ported wholesale (no new M1 probe, no staleness-detection/auto-recovery machinery — this file's own observed failure mode did not warrant that additional machinery, and adding it would not be the narrowest correct fix).

## 3. Fix location

`ai_trader/apprenticeship_v2/mt5_read_only_source.py::measure_broker_offset_seconds()` — the shared file **was** modified, disclosed explicitly as required. `general_observer/tick.py`'s own watermark comparison logic was **not** touched; the bug lives in the shared timestamp measurement itself, and no downstream workaround (tolerance window, weakened assertion, suppressed dedup check) could fix it without leaving the actual defect in place, which the mandate explicitly forbade.

**The fix**: cache the last successfully-measured `(tick.time, offset)` pair per symbol, in a module-level dict. As long as `tick.time` is unchanged from the last measurement, the previously-computed offset is reused, unmodified. The instant `tick.time` changes (a genuinely new price tick arrives), the offset is recomputed fresh. This is not a tolerance applied to a comparison or a result — it computes the identical formula this function always computed, from the identical input, exactly once per distinct input, instead of recomputing (and thereby drifting) against an input that has not actually changed.

`fetch_causal_closed_bars`'s own closed-bars-only filter (`b.ts_close <= now`) and `_bar_from_rate`'s own formula are both byte-unchanged — only how the offset value they consume is obtained changed.

## 4. S5 impact assessment

`S5_SOURCE_FILE_CHANGED = YES` (`mt5_read_only_source.py`). This file is used by `loop.py`/`main.py`/`s5_observer.py` (the apprenticeship_v2 S5 path) — those files are unaffected in behavior (the fix only changes offset **measurement stability**, not the causal-cutoff filter, not any trading/strategy logic, and no test exists for those three files at all — confirmed by direct repo search — so there is nothing to regress there beyond re-confirming they remain byte-unchanged, which they are).

**`broker_clock.py`/`soak_loop.py`/`live_runtime_loop.py` (the OTHER S5-adjacent live-trading stack, `mt5_demo_bridge`) are a separate, independent implementation of a similar idea and do not import from or share code with `mt5_read_only_source.py`** — confirmed by direct source inspection before making this change. They are **not applicable regression targets** for this specific fix; their own test suite (`test_broker_clock.py`, `test_soak_loop.py`, `test_live_runtime_loop.py`) was run anyway for extra diligence, not because the change could plausibly affect them.

No S5 trading/strategy/entry/exit/risk logic was touched anywhere.

## 5. A second, independent issue found and fixed: the test's own flawed assumption

After the fix above, the same test still failed intermittently (once in 4 full-suite re-runs). Investigated before assuming the fix was incomplete: the failing delta was **exactly 900** — one full M15 bar duration, not a small or arbitrary number. This is a **genuine M15 bar closing** between the two back-to-back `tick()` calls — an unavoidable race against live, uncontrolled market data (the test's own two calls take on the order of 0.7-1.5s combined; if that window happens to straddle a real bar boundary, a new bar legitimately appears). The mandate's own required field `GENUINE_NEW_BAR_DETECTED` anticipates exactly this case.

The test's own assertion (`second == first`, unconditionally) did not distinguish "the watermark drifted with no real cause" (the actual defect, now fixed) from "a genuine bar closed" (correct, required behavior) — it treated both as failures. Corrected the assertion to accept **either** outcome precisely: unchanged, **or** advanced by an exact positive multiple of `BAR_SECONDS[TIMEFRAME_M15]` (900) — imported from the same authoritative constant `mt5_read_only_source.py` itself already defines, not a new number. This is not a tolerance window (which would accept "close enough" values); it is an exact match against one of exactly two legitimate outcomes, and it still fails on the original defect's own signature (a delta of 1, or any non-multiple-of-900 value).

## 6. Test results (all against the real, live terminal, via the repo's own `venv`)

- The specific previously-failing test, re-run 5 times immediately after the code fix (before the test-assertion correction): **5/5 passed**.
- After discovering and correcting the test's own assertion: re-run **30/30 passed** (targeted), plus **8 consecutive full-suite runs, 177/177 passed each time** (0 failed, 0 skipped, every time).
- `mypy --ignore-missing-imports` across every new/modified file (including `mt5_read_only_source.py`): **0 errors**.
- `test_broker_clock.py`/`test_soak_loop.py`/`test_live_runtime_loop.py` (independent stack, not part of this fix's applicable scope per Section 4 -- run anyway for extra diligence): still running in the background at the time of this report (slow suite, exceeded a 60s check); not blocking this delivery on it, since it cannot affect the verdict above -- the changed function shares no code with this stack.

## 7. Not done

No tolerance window was added anywhere. No assertion was weakened without a precise, non-arbitrary replacement (see Section 5). No duplicate check was suppressed — `is_duplicate`'s own level/price/direction-keyed logic is completely untouched. No market-semantic threshold was introduced — `900` is `BAR_SECONDS[TIMEFRAME_M15]`, an already-authoritative, pre-existing constant, not a new calibrated value. S5 strategy/entry/exit/risk logic, General Observer event/scorecard/lesson/`STRUCTURAL_FINAL` semantics, and broker execution were not touched anywhere.

## Files changed

```
M  ai_trader/apprenticeship_v2/mt5_read_only_source.py   (measure_broker_offset_seconds: added per-symbol offset cache)
M  ai_trader/apprenticeship_v2/tests/test_mt5_e2e_integration.py   (corrected the watermark assertion, see Section 5)
```

---

## Required Final Block

```
MT5_WATERMARK_DRIFT_FIX_COMPLETE = YES

ROOT_CAUSE_CONFIRMED = measure_broker_offset_seconds() computed `tick.time - now_fn()` fresh every call; tick.time only updates on a new price tick, so during a quiet market the offset (and every bar's own computed ts_close) drifted upward by ~1s per real second elapsed while now_fn() kept advancing against a frozen tick.time. Verified directly via a fixed-now_fn vs. real-now_fn isolated comparison against the live terminal.

FIX_LOCATION = ai_trader/apprenticeship_v2/mt5_read_only_source.py::measure_broker_offset_seconds() -- per-symbol cache of (tick.time, offset), reused unchanged while tick.time is unchanged, recomputed the instant tick.time changes

S5_SOURCE_FILE_CHANGED = YES
S5_TRADING_SEMANTICS_CHANGED = NO

NO_NEW_BAR_STABLE_WATERMARK = YES
GENUINE_NEW_BAR_DETECTED = YES -- confirmed directly: a real 900s (one M15 bar) transition was observed and correctly reflected in the watermark, both in a raw diagnostic and in the corrected test's own assertion

CLOSED_BARS_ONLY_CONFIRMED = YES
NO_FUTURE_LEAK_CONFIRMED = YES
NO_DUPLICATE_PROCESSING_CONFIRMED = YES
RESTART_CONTINUITY_CONFIRMED = YES

REAL_MT5_E2E_RESULT = passed (177 passed, 0 failed, 0 skipped -- confirmed across 8 consecutive full-suite runs after the fix)

GENERAL_OBSERVER_REGRESSION = 177 passed, 0 failed, 0 skipped (ai_trader/apprenticeship_v2/tests/, 8 consecutive runs)
S5_REGRESSION = no test suite exists for loop.py/main.py/s5_observer.py (confirmed by repo search, unchanged finding from the prior report); mt5_read_only_source.py itself has no independent unit-test file of its own beyond ai_trader/apprenticeship_v2/tests/ (above, 177/177 across 8 runs); the separate, independent broker_clock.py/soak_loop.py/live_runtime_loop.py stack (mt5_demo_bridge) does not share code with the changed function and is not an applicable regression target -- its own suite was started anyway for extra diligence but ran long (>60s) and was not blocked on, since it cannot affect this fix's verdict
STATIC_CHECK = mypy --ignore-missing-imports: 0 errors (mt5_read_only_source.py + all general_observer/*.py + schemas.py + durable_store.py + resolution.py + checkpoint.py)

GENERAL_OBSERVER_V1_1_IMPLEMENTATION = PASS

REMAINING_BLOCKERS =
* NONE

RED_TEAM_REVIEW_AUTHORIZED = NO
LIVE_SHADOW_AUTHORIZED = NO
BROKER_AUTHORIZED = NO
NEXT_AUTHORIZED_ACTION = NONE — CEO REVIEW REQUIRED

STOP.
```
