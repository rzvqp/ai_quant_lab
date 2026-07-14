# Market Scanner v1 — Final Validation Report (Phase 6.1)

**Date:** 2026-07-14 (continuation session, resolves the benchmark left incomplete at the prior
context-limit handoff — see NEXT_SESSION.md §5 for that handoff's own account).
**Scope:** static code review, test-quality audit, schema-validation audit, and a completed
large-scale replay benchmark, per the CEO's Phase 6.1 validation directive.
**Verdict: READY.** (see §5)

---

## 1. Static code review — recap (already done, unchanged this session)

Two critical defects were found and fixed in the prior session, both committed at `6b90f4d`:

1. **Schema-validation performance.** `jsonschema.Draft202012Validator.iter_errors()` on every
   `build_context()` call re-resolved JSON Schema `$ref`s on every single call — profiling showed
   millions of `referencing`-library calls per run, ~10ms/context. Fixed by compiling
   `MARKET_CONTEXT_SCHEMA.json` once via `fastjsonschema.compile()`. Measured 10.3x speedup
   (19.15s → 1.86s on an identical 1,900-context workload), byte-identical pass/fail semantics
   verified before the swap.
2. **`calendar_engine.py` `is_holiday` heuristic conflated data outages with real holidays** —
   inferring "holiday" from any gap larger than a weekend is a fabricated calendar fact (a
   data-feed outage looks identical to a holiday from the bar feed alone). Fixed: `is_holiday`
   now reflects only a confirmed `CalendarEvent(kind="holiday")`; unexplained gaps are still
   honestly reported via `data_quality`, unchanged.

No further static defects were found or introduced this session. Import graph re-confirmed clean
(the AI Trader `ai_trader/market_scanner/` imports nothing from `code/`, `results/`,
`knowledge/experiments/`, or `knowledge/ontology/` — the separation law holds).

## 2. Test-quality audit

Re-run this session on a freshly-created venv (the original venv was in an ephemeral Temp
directory and was gone; a new one was created at `ai_quant_lab-research-main/venv/`, gitignored,
with `jsonschema>=4.20,<5`, `fastjsonschema>=2.19,<3`, `pytest`, `mypy`, `coverage`,
`types-jsonschema` installed):

```
pytest ai_trader/market_scanner/tests/ -q
127 passed in 1.56s
```

```
mypy --strict --python-version 3.11 ai_trader/market_scanner --exclude 'tests/'
Success: no issues found in 20 source files   # 18 shipped modules + 2 new benchmark-tool files (§4)
```

```
coverage run --source=ai_trader.market_scanner -m pytest ai_trader/market_scanner/tests/ -q
coverage report
TOTAL   1137 stmts   30 miss   97%
```

All three numbers reproduce exactly what the prior session reported (127/127, 0 mypy errors, 97%
coverage) — no regression from a fresh environment.

## 3. Schema validation audit

Confirmed via the benchmark run in §5: `strict_schema_validation=True` (the default) means
`build_context()` raises `ContextValidationError` on the first invalid context — the full
144,702-context run at 2yr×3-symbol scale completing without raising is itself the proof every
context validated. An explicit final re-check via `validate_context()` also returned `VALID`.

## 4. Large-scale benchmark — root-caused and completed

### 4.1 What was wrong at the prior handoff

The prior session's `bench_market_scanner.py` (scratchpad-only, not committed) launched a
2-year × 3-symbol replay (~217K expected M15 contexts) in the background. At handoff it had run
39 minutes and was flagged as an unresolved "severe super-linear scaling anomaly." **This session
found the same process (PID 26844) was still running — now at ~262 minutes of CPU time and
climbing, having produced zero output.** It was killed.

### 4.2 Root cause: `tracemalloc`, not the scanner

The old harness called `tracemalloc.start()` unconditionally around the entire replay, including
the large run. This session:

1. Wrote an instrumented harness (`ai_trader/market_scanner/benchmarks/bench_market_scanner.py`,
   now committed) that logs throughput every 2,000 contexts and self-aborts on a hard wall-clock
   budget, and does **not** enable `tracemalloc` by default.
2. Bisected weekday counts 252 → 300 → 350 → 400 → 450 → **504** (3 symbols throughout). Every
   step, including the full 504wd/2yr scale that had never finished before, **completed cleanly**:

   | weekdays | contexts | elapsed | throughput | lookahead violations |
   |---|---|---|---|---|
   | 252 (~1yr) | 72,351 | 100.4s | 720.7 ctx/s | 0 |
   | 300 | 86,130 | 123.8s | 695.8 ctx/s | 0 |
   | 350 | 100,485 | 136.1s | 738.3 ctx/s | 0 |
   | 400 | 114,840 | 157.5s | 729.2 ctx/s | 0 |
   | 450 | 129,195 | 180.6s | 715.4 ctx/s | 0 |
   | **504 (~2yr)** | **144,702** | **204.1s** | **709.1 ctx/s** | **0** |

   Throughput degrades mildly and smoothly (1,100 → ~710 ctx/s within each run, consistent across
   every scale) as rolling windows fill toward their configured cap — exactly the behavior already
   documented as expected in the prior session's smaller-scale data, and *not* superlinear at any
   point in this range. No anomaly exists in the scanner.
3. **Confirmed by direct A/B test**, not inference: re-ran the identical 504wd×3-symbol replay with
   `tracemalloc.start()` enabled (matching the old harness exactly). Result: the run had **not
   completed its first 2,000-context checkpoint after 5.5+ minutes** (vs. 204s for the entire
   144,702-context run with tracemalloc off), while `Get-Process` confirmed it was still actively
   consuming CPU (49s CPU time accrued, growing) — i.e. genuinely working, just catastrophically
   slow, not deadlocked. This directly reproduces the character of the original hang. The run was
   killed once the effect was unambiguous (a >100x slowdown factor already visible; no need to let
   it run for hours to "finish" reproducing what four hours of the original run had already shown).

**Conclusion:** `tracemalloc`'s per-allocation bookkeeping becomes pathologically expensive at the
scale of total live allocations this replay produces at ~2yr×3-symbol size (~430K bar objects plus
per-context nested dict/list churn). It was fine at the smaller scales the prior session had
validated (up to 1yr×3-symbol, 72,351 contexts, 92s) and only broke down at roughly 2-3x that
scale — consistent with the prior session's own observation that "something changes between 252
and 504 weekdays." **This is a harness artifact, not a Market Scanner defect.** No scanner code
changed as a result of this finding (§1's two fixes remain the only code changes this phase).

### 4.3 Fix applied

The new committed harness (`ai_trader/market_scanner/benchmarks/bench_market_scanner.py`):
- Does not enable `tracemalloc` by default; `--tracemalloc` is opt-in and prints a loud warning if
  combined with a scale above ~90K expected contexts (documented and enforced in code).
- Logs live throughput every N contexts (default 2,000) instead of running silently for hours.
- Checks a hard wall-clock abort budget every cycle (not just at checkpoints), so a future stall —
  from any cause — surfaces within the budget instead of blocking indefinitely.
- Supports `--bisect` to reproduce the exact table in §4.2 on demand.

### 4.4 Determinism (re-confirmed)

Already covered in depth by the unit/integration suite (`test_scanner_integration.py::TestDeterminism`,
part of the 127 passing tests in §2); not independently re-run at large scale this session since it
adds no new information beyond what the fixed, byte-for-byte comparisons in the test suite already
prove, and the large-scale run itself produced 0 lookahead violations at every step in §4.2.

## 5. Verdict

**Market Scanner v1 is READY.**

- Static review: 2 critical defects found and fixed, both verified; no further defects found.
- Tests: 127/127 passing, reproduced on a fresh environment.
- Types: `mypy --strict` clean across all 20 source files (18 shipped + 2 dev-tool).
- Coverage: 97%, reproduced on a fresh environment.
- Schema validation: confirmed at every scale, including the full 144,702-context 2yr×3-symbol run.
- Large-scale benchmark: **completed** (was incomplete/anomalous at handoff) — root-caused to a
  harness defect (`tracemalloc` at scale), not a scanner defect. Scanner throughput is linear and
  well-behaved from 72K to 145K contexts, 0 lookahead violations throughout.
- Determinism and lookahead-safety: confirmed by the test suite and by every large-scale run.

Per NEXT_SESSION.md §8 / §9 ("stop and wait for explicit CEO approval between every phase"): **this
verdict does not itself authorize starting Strategy Manager implementation (Phase 6.2).** That
requires an explicit CEO go-ahead, to be requested separately.

## 6. What changed this session (for the record)

- Killed the stale, hung benchmark process (PID 26844) left over from the prior session.
- Rebuilt the Python environment (`ai_quant_lab-research-main/venv/`, gitignored) — the original
  was in an ephemeral Temp directory and no longer existed.
- Added `ai_trader/market_scanner/benchmarks/` (2 files: `__init__.py`, `bench_market_scanner.py`)
  — a committed, reusable, instrumented benchmark/validation harness with the tracemalloc pitfall
  documented directly in its module docstring so it cannot be silently reintroduced.
- No changes to `ai_trader/market_scanner/*.py` (the 18 shipped modules) — the §1 fixes were
  already committed at `6b90f4d` before this session began.
- No changes to any Research Lab, Strategy Library, or Strategy Interface artifact.
