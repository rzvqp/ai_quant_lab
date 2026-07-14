# Scoring Engine v1 — Implementation & Validation Report (Phase 6.4)

**Date:** 2026-07-14. **Scope:** production implementation of the Scoring Engine against the frozen
`ai_trader/scoring_engine/*.md`/`*.json` specification, following the exact process and quality bar
established for Market Scanner v1 (Phase 6.1), Strategy Manager v1 (Phase 6.2), and Signal Engine v1
(Phase 6.3): implement → test continuously → adversarial review → fix every real issue → report
honestly.
**Verdict: READY.** (see §6)

---

## 1. What was built

14 production modules under `ai_trader/scoring_engine/` (13 source `.py` files + `py.typed` +
`requirements.txt`), implementing every stage the architecture names:

| architecture component | module |
|---|---|
| Intake & Filter, Evidence Binding, Component Scoring (per-signal) | `pipeline.py` |
| Evidence Binder (read-only Strategy Manager fetch + cache) | `evidence.py` |
| Component Scorer (the 8 per-signal components) | `components.py` |
| Conflict Analyzer (the 9th, batch-wide component) | `conflict.py` |
| Aggregator (0–100 formula, band derivation) | `aggregator.py` |
| Assembler (final `OpportunityScore` construction, reason codes) | `assembler.py` |
| Ranker (deterministic ordering + `rank`) | `ranker.py` |
| Validator / Output (schema + semantic validation) | `validator.py` (+ `schema_validation.py`) |
| Public API facade + lifecycle/statistics/health | `engine.py` (`ScoringEngine`) |
| Value types (mirrors `SCORING_SCHEMA.json` 1:1) | `types.py` |
| Config / errors | `config.py`, `exceptions.py` |

**199 tests** across 12 test files (unit tests per module covering all nine components, the
aggregation formula, conflict analysis, ranking, and every fail-safe path), including
`test_engine_integration.py` against the real Strategy Manager and, through it, the real Signal
Engine's `StrategyRuntimeHandle`. `mypy --strict`: 0 errors across all 32 source files (13 production
+ its own `tests/` package). Coverage: **98%** (source only) — the remaining 15 uncovered statements
are documented, defensive-only branches (structurally-unreachable-by-construction fallbacks,
`schema_validation.py`'s file-missing/corrupt-JSON/compile-failure environment paths) — the same
class of gap every prior module's own report left uncovered, for the same reason.

## 2. Design decisions worth recording (not redesign — filling gaps the spec leaves to the implementer)

`SCORING_MODEL.md` names several inputs without fixing their exact normalization/weighting. Every
such gap is filled with an explicit, documented, honesty-preserving default and marked
"IMPLEMENTATION CHOICE" in the source:

- **`historical_confidence`'s `maturity_prior` is keyed by the Strategy Manager's own operational
  `Lifecycle` (9 values: `EXPERIMENTAL`/`EXPLORATORY`/`CANDIDATE`/`VALIDATED`/`PROMOTED`/`INVALID`/
  `NOT_IMPLEMENTED`/`DISABLED`/`RETIRED`), not the raw contract's `lifecycle.maturity` field (only 5
  values, no `EXPERIMENTAL`/`INVALID`/`NOT_IMPLEMENTED` member at all)** — `SCORING_MODEL.md` §3's own
  table vocabulary matches `Lifecycle` exactly, so the Evidence Binder fetches both `find_strategy()`
  (for `Lifecycle`) and `get_contract()` (for the rest of the evidence) from the Strategy Manager.
- **`risk_penalty`'s weights/normalization constants** (`w_dd`/`w_fr`/`w_n` = 0.4/0.3/0.3; a 10R
  drawdown cap; a 0.5 `top1_share` fragility threshold; a 100-trade full-sample-size reference) are
  explicit, documented constants in `config.py`. Missing evidence for a *specific* disclosed field
  (drawdown/fragility/sample size) contributes the WORST case for that field — but a *wholly* missing
  contract (unknown to the Strategy Manager, or no Strategy Manager configured) contributes a
  **neutral 0.5**, not the worst case: `historical_confidence` already carries the model's own
  honesty penalty for that condition (`EVIDENCE_MISSING` → 0), and forcing `risk_penalty` to 1.0 too
  would collapse `penalty_factor` to zero and silently zero every evidence-missing score regardless
  of signal quality — double-punishing the same fact through two different components and conflating
  "the Strategy Manager wasn't reachable" (an engine-operational condition) with "this strategy is
  known to be risky" (a fact about the strategy). This was caught and fixed during implementation via
  direct smoke testing before the formal test suite was written.
- **`market_alignment`'s "context's short-term price/momentum tag"** (§2 row 3, no field named) uses
  `StrategySignal.regime` — the only momentum-like tag the Signal Engine publishes — with
  `TREND_UP`/`TREND_DOWN` treated as directional and everything else neutral.
- **The "mechanism class" for `conflict_penalty`'s correlated-stacking rule** (§4) uses
  `contract.identity.klass` (the schema's own renamed `class` field) — the only category/family field
  the contract exposes.
- **`historical_confidence` → `confidence` enum band thresholds** (§6 says only "mirrors the contract
  tiers") are centered on the `maturity_prior` anchor values (0.15/0.30/0.45/0.75/1.00), since a
  realistic `historical_confidence` sits at or below its strategy's own prior.
- **`SCORING_MODEL.md`'s prose mentions a "WATCH/ARM" recommendation for READY states, but
  `SCORING_SCHEMA.json`'s own `recommendation` enum has no `ARM` value.** Since the schema is the
  binding, machine-validated contract (the same precedent every prior module followed), both
  `LONG_READY`/`SHORT_READY` and `WAIT_CONFIRMATION` map to the one schema-valid non-actionable-but-
  live tier, `WATCH`. Flagged here for the record, not silently resolved.
- **Deterministic rounding is genuinely half-up**, not Python's `round()` (which uses round-half-to-
  even — `round(2.5) == 2`, silently violating `SCORING_MODEL.md` §5's explicit "half-up" requirement
  had it been used). `aggregator.round_half_up` implements `floor(x + 0.5)` instead.
- **No wall-clock anywhere in this module** (unlike Signal Engine, which had one narrowly-scoped
  exception for an informational timing field). `SCORING_SCHEMA.json` has no equivalent field at all,
  so `timestamp` is always the scored signal's own `as_of`, and no module reached from `engine.py`
  imports `time`.

## 3. Independent adversarial review — 4 real bugs found and fixed

Following the same technique that caught bugs in all three prior modules, a fresh-eyes review agent
(no memory of writing the code) read all 7 frozen spec documents in full, then all 13 source files
(plus the upstream `StrategySignal`/`Contract`/`Evidence` types), hunting specifically for arithmetic
deviations from `SCORING_MODEL.md`, fail-safe violations, and batch-barrier correctness. It found 4
issues (2 CRITICAL, 1 HIGH, 1 MEDIUM); all were real and fixed with regression tests.

| # | bug | file | severity | fix |
|---|---|---|---|---|
| 1 | `_is_malformed()`'s defensive boundary only checked `as_of`/`symbol`/`strategy_id` truthiness — a `StrategySignal` with `context_ref=None` or `explanation=None` (a caller bypassing the type system, e.g. via `dataclasses.replace`) slipped past it and crashed with `AttributeError` deep inside component/assembler code that reads `signal.context_ref.*`/`signal.explanation.*` — aborting the WHOLE containing `score_batch()` list comprehension, not just the one bad signal | `pipeline.py` (`_is_malformed`) | **CRITICAL** | Now checks `signal.context_ref is None or signal.explanation is None` in addition to the `isinstance` check — the two required nested objects every downstream read depends on. |
| 2 | The fail-safe reassembly path in `engine.py`'s `_finalize_one()` never re-validated its OWN reassembled `INVALID` score — and that reassembly copies identity fields (`strategy_version`, `refs`, ...) straight from the SAME signal that caused the original schema failure. A signal with a malformed `strategy_version` (violating the schema's version pattern) would still carry that same malformed field into the "fixed" score, which could still be schema-invalid and was emitted anyway | `engine.py` (`_finalize_one`) | **CRITICAL** | Re-validates the reassembled score; if STILL invalid, falls back to the fully placeholder-based `assemble_invalid_score(None, ...)` (schema-valid by construction, carries no unvalidated data from the offending signal), while preserving the diagnostic `SCHEMA_MISMATCH` reason codes either way. |
| 3 | `regime_alignment()` awarded a full `1.0` when a contract's `applicable` list was the wildcard `Regime.ANY`, instead of the `0.5` neutral value `SCORING_MODEL.md` §2 row 4 explicitly specifies ("1.0 if current regime ∈ contract applicable; **0.5 if ANY**/unknown; 0.0 if ∈ avoid") — an unintentional inversion of the spec's own literal wording, not a documented gap-fill | `components.py` (`regime_alignment`) | **HIGH** | Removed the `or Regime.ANY in spec.applicable` clause from the 1.0 branch. `regime in spec.applicable` alone naturally falls through to the neutral 0.5 default when `applicable == (ANY,)` and the signal's specific regime isn't literally in it — matching the spec exactly, no special-casing needed. |
| 4 | `_is_malformed()` treated `as_of == 0` as "missing," rejecting the signal as `SCORE_INVALID` — but `0` is the Signal Engine's OWN documented sentinel for "context missing `meta.as_of`" (its `_missing_as_of_signal` fallback), always paired with `state=SignalState.INVALID`: a legitimately-typed signal reporting an upstream failure, not a Scoring-Engine-level parsing failure | `pipeline.py` (`_is_malformed`) | **MEDIUM** | Dropped the `as_of`/`symbol`/`strategy_id` truthiness checks entirely (fixed together with #1, same function) — such a signal now correctly falls through to the ordinary non-actionable-state routing (→ `SKIPPED`), while any other semantically-broken-but-well-typed value is caught by schema validation + the now-safe reassembly path (fix #2). |

All 4 fixed issues got dedicated regression tests proving the fix (e.g.
`test_missing_context_ref_is_score_invalid_not_a_crash`,
`test_a_signal_whose_own_bad_field_causes_the_schema_failure_still_emits_a_valid_score`,
`test_any_applicable_is_neutral_not_a_match`,
`test_as_of_zero_with_invalid_state_is_skipped_not_score_invalid`). The review found **no** issues
with the aggregation arithmetic (base_quality weights, penalty_factor formula, half-up rounding), the
`historical_confidence` maturity-tier honesty cap, the Conflict Analyzer's order-independent use of
each signal's pre-conflict provisional quality, the deterministic ranking key, the quality/confidence/
recommendation banding, or the engine lifecycle/shutdown state machine — all matched the frozen
specification exactly.

One additional design note surfaced and fixed proactively during implementation (before the formal
adversarial review, via direct smoke testing): `risk_penalty`'s wholly-missing-contract case
originally forced the worst-case 1.0, which — combined with `historical_confidence` also going to 0
for the same condition — collapsed `total_score` to exactly 0 for EVERY evidence-missing signal
regardless of live signal quality. Documented and fixed in §2 above.

## 4. Final numbers (after all fixes)

```
pytest ai_trader/scoring_engine/tests/ -q
199 passed in 0.67s

mypy --strict ai_trader/scoring_engine
Success: no issues found in 32 source files

coverage run --source=ai_trader.scoring_engine -m pytest ai_trader/scoring_engine/tests/ -q
coverage report --omit="*/tests/*"
TOTAL   768 stmts   15 miss   98%

pytest ai_trader/ -q   (Market Scanner + Strategy Manager + Signal Engine + Scoring Engine together)
758 passed in 3.57s

mypy --strict ai_trader/market_scanner ai_trader/strategy_manager ai_trader/signal_engine ai_trader/scoring_engine --exclude 'tests/'
Success: no issues found in 61 source files   (no regression in any prior module)
```

## 5. Protected invariants — confirmed untouched

- **Research Lab** (`code/`, `results/`, `data/`), **Strategy Library** (`knowledge/strategies/`),
  **Strategy Interface v1** (`knowledge/interface/`) — read-only; zero files modified.
- **Market Scanner**, **Strategy Manager**, **Signal Engine** implementations — zero files modified.
  The Scoring Engine only *imports* already-published types (`StrategySignal`/`SignalState`/
  `Direction` from Signal Engine; `Contract`/`Evidence`/`Lifecycle`/`Regime` from Strategy Manager;
  `DataQualityLevel` from Market Scanner) and reads contract evidence read-only via the Strategy
  Manager's own `find_strategy()`/`get_contract()` — never touches their source, never calls a
  mutating method.
- **No broker code, no MT5, no live trading, no Risk Manager, no Execution Engine, no Learning
  Engine, no ML** — none exist anywhere in this diff, per the CEO directive's explicit exclusion list.
- **The Scoring Engine never opens, sizes, or routes a position; never manages risk** (`risk_penalty`
  is a quality discount, never position risk); **never learns or adapts** (all weights/bands are fixed
  `ScoringConfig` constants, never trained); **never mutates a strategy's contract or confidence** —
  verified by the module's own scope (a pure `(signal, evidence) → OpportunityScore` function, no
  side effects beyond internal statistics bookkeeping) and confirmed by the adversarial review.

## 6. Verdict

**Scoring Engine v1 is READY.**

- Implementation: every architecture component built, matching the frozen spec exactly (no redesign
  — every design decision in §2 fills a genuine spec gap or resolves a spec-internal inconsistency,
  never contradicts documented behavior).
- Tests: 199/199 passing, covering all nine scoring components, the aggregation formula, conflict
  analysis (opposing + correlated, order-independence), deterministic ranking, every fail-safe path
  (malformed input, missing evidence, non-actionable states, schema-validation-failure reassembly),
  and a real-Strategy-Manager/real-Signal-Engine integration test.
- Types: `mypy --strict` clean across all 32 source files (13 production + test package).
- Coverage: 98%, remaining gaps are documented defensive/environment-only or structurally-
  unreachable-by-construction branches.
- Independent adversarial review: completed, found 4 real issues (2 CRITICAL, 1 HIGH, 1 MEDIUM), all
  fixed and regression-tested, no outstanding findings.
- Protected invariants: confirmed untouched. Full `ai_trader/` suite (758 tests, 61 source files)
  green with no regressions in Market Scanner, Strategy Manager, or Signal Engine.

Per the standing "stop between every phase" directive and the CEO's explicit instruction for this
task: **this verdict does not itself authorize starting Risk Manager, Execution Engine, Simulation,
Learning Engine, Broker Adapter, or MT5 integration.** That requires an explicit new CEO go-ahead.
