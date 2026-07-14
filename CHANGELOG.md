# CHANGELOG — AI Quant Research Lab

## Session 2026-07-15 (Phase 6.6) — Execution Engine v1 implemented, adversarially reviewed, READY
- CEO approval granted; implemented the Execution Engine production module against the frozen
  `ai_trader/execution_engine/*.md`/`ORDER_SCHEMA.json` specification — no redesign. 13 source modules
  (value types, config, exceptions, schema validation, the abstract Broker Adapter `Protocol`, Order
  Builder, Order Validator, Order Ledger, Lifecycle Tracker, Reconciler, the fixed per-decision
  pipeline, Result/Reporter, public API facade), 198 tests, `mypy --strict` clean, 99% coverage. Full
  writeup: `EXECUTION_ENGINE_VALIDATION_REPORT.md`.
- Resolved the Portfolio Manager gap flagged in the Phase 6.5 session-close handoff
  (`EXECUTION_ENGINE_HANDOFF.md`) by reusing `ai_trader.risk_manager.types.PortfolioState` directly
  (documented IMPLEMENTATION CHOICE #1) rather than designing a parallel type. Designed a pull-based
  abstract Broker Adapter `Protocol` (`submit_order`/`cancel_order`/`query_status`/`query_open_orders`/
  `capabilities`) matching `EXECUTION_SEQUENCE.md`'s own query-based calls exactly — no real venue
  integration exists anywhere in this diff; a deterministic fake test double implements the Protocol
  for the test suite only.
- **Independent adversarial review** (same technique that caught bugs in all five prior modules) found
  **7 real issues (2 CRITICAL, 1 HIGH, 3 MEDIUM, 1 LOW)**, all fixed with regression tests: (1) the
  pipeline validated an order BEFORE checking the duplicate guard, so a retry of an already-FILLED order
  evaluated against a since-changed `PortfolioState` could fail validation and have its Ledger record
  silently overwritten with a bogus REJECTED, corrupting the record of an order that had genuinely
  executed; (2) the Reconciler and `engine.cancel()` had no exception handling around Broker Adapter
  calls — a single flaky broker call aborted reconciling every other open order, and a broker exception
  during `shutdown()`'s draining reconciliation propagated out of the public API entirely, violating the
  documented "never thrown across the boundary" contract; (3) `emergency_flatten()` silently no-op'd
  (empty report, no degraded signal) when called before any portfolio had ever been observed — dangerous
  for a method that exists specifically as an emergency safety mechanism; (4) the Order Validator had no
  "time restrictions" check at all despite the architecture naming one; (5) an advisory broker-transition
  sanity-check function was written but never actually wired in anywhere; (6) `emergency_flatten()`'s
  build stage had no exception safety net even though its submit stage already did; (7) a broker
  reporting a fill without a price had that price silently fabricated as `0.0` instead of falling back
  to the order's own reference price.
- Fixes: the duplicate guard now runs FIRST in `pipeline.py`, before validation, so an idempotent retry
  never re-evaluates against a possibly-different portfolio; every Broker Adapter call in
  `reconciler.py` is now wrapped (degrading to "treat as unresolved" on exception, never propagating),
  and a new `reconciler.request_cancel()` is the one exception-safe boundary `engine.cancel()` uses
  instead of calling the adapter directly; `emergency_flatten()` now marks the engine DEGRADED with an
  explicit reason when no portfolio has ever been observed, and wraps its build stage in the same
  exception safety its submit stage already had; `validator.py` gained a documented
  `_check_time_restrictions()`; the dead transition-check function is now wired into
  `lifecycle.py::apply_broker_update()` as an advisory warning log; a malformed fill now falls back to
  the order's own `limit_price` before ever falling back to `0.0`.
- Confirmed via the real Risk Manager (`test_engine_integration.py`): the full pipeline from a real,
  schema-valid `RiskDecision` (built through Risk Manager's own fixtures against a real Scoring Engine)
  through to a validated, FILLED `OrderStatus` works end-to-end, deterministically; the real-strategy
  DENY chain (Signal Engine → Scoring Engine → Risk Manager → Execution Engine) degrades to a no-op
  `REJECTED` status end-to-end, never a crash, with no regressions in Market Scanner, Strategy Manager,
  Signal Engine, Scoring Engine, or Risk Manager (full `ai_trader/` suite: 1165 tests passing).

## Session 2026-07-15 (Phase 6.5) — Risk Manager v1 implemented, adversarially reviewed, READY
- CEO approval granted; implemented the Risk Manager production module against the frozen
  `ai_trader/risk_manager/*.md`/`RISK_SCHEMA.json` specification — no redesign. 13 source modules
  (pre-trade filters, portfolio limits, loss/drawdown guards + cooldowns, position sizer, constraint
  builder, the fixed 9-stage per-opportunity pipeline, decision assembler, output-collector validator,
  schema validation, public API facade, types, config, exceptions), 209 tests, `mypy --strict` clean,
  99% coverage (`engine.py` itself 100%). Full writeup: `RISK_MANAGER_VALIDATION_REPORT.md`.
- **Independent adversarial review** (same technique that caught bugs in all four prior modules) found
  **8 real issues (2 CRITICAL, 1 HIGH, 3 MEDIUM, 2 LOW)**, all fixed with regression tests: (1) no
  exception safety net anywhere in the pipeline call chain — a runtime-malformed `OpportunityScore`
  field (e.g. `total_score=None`) could crash the WHOLE `evaluate()` batch instead of degrading to one
  classified `DENY`; (2) `evaluate()`'s `PORTFOLIO_UNAVAILABLE` branch bypassed the decision-validation/
  reassembly path entirely, unlike the normal per-opportunity loop; (3) `POSITION_SIZING.md`'s
  correlation-group sub-budget (trades sharing a correlation group must share a smaller, deterministic
  slice of the aggregate exposure cap) was never implemented — only the aggregate cap was enforced; (4)
  `allow_trade()`'s `portfolio_impact` for its own ALLOW didn't reflect its own effect, inconsistent
  with `evaluate()`'s behavior for the identical opportunity; (5) `health()`'s DEGRADED status never
  cleared after a stale/missing portfolio was followed by a fresh, valid one, contradicting the
  documented recovery behavior; (6) a module docstring inaccurately implied a sizing-time clamp applies
  to leverage/overnight limits, when the spec only defines that mechanism for exposure (documentation-
  only, no functional gap); (7) the fail-safe fallback decision hardcoded `engine_state=READY`
  regardless of the actual global state, producing internally-inconsistent output while
  SUSPENDED/EMERGENCY_STOP; (8) the pre-trade filter chain checked data-quality FIRST instead of LAST,
  contradicting the policy document's own table order and changing which reason code surfaces when
  multiple filters fail together.
- Fixes: a new `_evaluate_one()` helper in `engine.py` wraps the pipeline call + portfolio update +
  decision finalization in `try/except Exception`, reused by BOTH `evaluate()`'s batch loop and
  `allow_trade()`'s single-opportunity path (closing findings #1 and #4 together); the
  `PORTFOLIO_UNAVAILABLE` branch now routes through the same validated path (#2); `sizing.py` now
  clamps to `min(aggregate_remaining, group_remaining)` where `group_budget = max_exposure_pct /
  max_correlated` (#3); `evaluate()` clears portfolio-availability degraded reasons on a fresh,
  non-stale portfolio (#5); `limits.py`'s docstring corrected (#6); `assemble_invalid_decision()` takes
  and threads through the actual `engine_state` (#7); `filters.py`'s fixed chain reordered to Volatility
  → Spread → Liquidity → News → Data-quality → Weekend → Gap (#8).
- One additional test-design issue found and fixed during the module's own test-writing pass (before
  the formal review): tuning `signal_strength` alone cannot reliably produce a below-floor `total_score`
  through the real Scoring Engine (its `EVIDENCE_MISSING` fallback defaults to a neutral 0.5, not 0) —
  resolved with a dedicated `make_below_floor_opportunity()` fixture that forces the needed fields
  directly instead of relying on that cross-engine arithmetic coincidence.
- Confirmed via the real Scoring Engine (`test_engine_integration.py`): the full pipeline from a real
  `OpportunityScore` through to a validated `RiskDecision` works end-to-end, deterministically, with no
  regressions in Market Scanner, Strategy Manager, Signal Engine, or Scoring Engine (full `ai_trader/`
  suite: 967 tests passing).

## Session 2026-07-14 (Phase 6.4) — Scoring Engine v1 implemented, adversarially reviewed, READY
- CEO approval granted; implemented the Scoring Engine production module against the frozen
  `ai_trader/scoring_engine/*.md`/`SCORING_SCHEMA.json` specification — no redesign. 13 source
  modules (pipeline, evidence binder, 8 per-signal components, conflict analyzer, aggregator,
  assembler, ranker, output-collector validator, schema validation, public API facade, types,
  config, exceptions), 199 tests, `mypy --strict` clean, 98% coverage. Full writeup:
  `SCORING_ENGINE_VALIDATION_REPORT.md`.
- **Independent adversarial review** (same technique that caught bugs in all three prior modules)
  found **4 real bugs (2 CRITICAL, 1 HIGH, 1 MEDIUM)**, all fixed with regression tests: (1)
  `pipeline.py`'s malformed-input guard only checked `as_of`/`symbol`/`strategy_id` truthiness, not
  the required nested `context_ref`/`explanation` objects — a signal with either set to `None` slipped
  past it and crashed the WHOLE containing batch with `AttributeError`, not just the one bad signal;
  (2) the fail-safe reassembly path in `engine.py` never re-validated its own reassembled `INVALID`
  score, and that reassembly copied identity fields straight from the same signal that caused the
  original schema failure — a signal with a malformed `strategy_version` could still produce a
  schema-invalid "fixed" score that got emitted anyway; (3) `components.py`'s `regime_alignment`
  awarded a full match (1.0) when a contract's applicable-regime list was the wildcard `ANY`, instead
  of the `0.5` neutral value `SCORING_MODEL.md` explicitly specifies for that case — an unintentional
  inversion of the spec's literal wording; (4) the malformed-input guard also rejected `as_of == 0` as
  invalid, but `0` is the Signal Engine's own documented sentinel for a missing-timestamp signal
  (always paired with `state=INVALID`) — a legitimately-typed signal that should route through the
  ordinary non-actionable-state path (`SKIPPED`), not be rejected as garbage input.
- Fixes: `_is_malformed()` now checks `context_ref`/`explanation` presence instead of scalar-field
  truthiness (fixing both the crash and the `as_of==0` misclassification together); `_finalize_one()`
  re-validates its reassembled fallback and, if still invalid, falls back to a fully placeholder-based
  score carrying no data from the offending signal; `regime_alignment()`'s `ANY`-applicable case no
  longer short-circuits to a match, correctly falling through to the neutral default.
- One additional design correction made proactively during implementation (via direct smoke testing,
  before the formal adversarial review): `risk_penalty`'s wholly-missing-contract case originally
  forced the worst-case value (1.0), which — combined with `historical_confidence` also going to 0 for
  the same condition — collapsed `total_score` to exactly 0 for every evidence-missing signal
  regardless of live signal quality, double-punishing the same underlying fact through two components.
  Changed to a neutral 0.5, letting `historical_confidence` alone carry the honesty penalty.
- Confirmed via the real Strategy Manager + real Signal Engine (`test_engine_integration.py`): every
  real strategy's signal is currently `INVALID`/`CORRUPTED_OUTPUT` (Signal Engine's own documented,
  unmigrated scope boundary) — the Scoring Engine degrades this to a classified `SKIP`/`INVALID` score
  end-to-end, never crashes, and stays fully queryable. Also exercised a real, interesting fail-safe
  case: for every real (quarantined) strategy, `find_strategy()` succeeds (`Lifecycle.INVALID`) while
  `get_contract()` fails (`NotFound`) — the Evidence Binder correctly treats this partial lookup as
  wholly evidence-missing, never a fabricated partial result.
- **Verdict: Scoring Engine v1 = READY.** Does not self-authorize Risk Manager (Phase 6.5) — still
  CEO-gated; work stopped immediately after the verdict per the CEO's explicit directive for this
  task. No changes to Research Lab, Strategy Library, Strategy Interface, Market Scanner, Strategy
  Manager, or Signal Engine. Full `ai_trader/` suite green: 758 tests, 61 source files, mypy --strict
  clean, no regressions.

## Session 2026-07-14 (Phase 6.3) — Signal Engine v1 implemented, adversarially reviewed, READY
- CEO approval granted; implemented the Signal Engine production module against the frozen
  `ai_trader/signal_engine/*.md`/`SIGNAL_SCHEMA.json`/`SIGNAL_EXPLANATION_SCHEMA.json` specification —
  no redesign. 10 source modules (pipeline, context validation, explanation builder, assembler,
  output-collector validator, schema validation, public API facade, types, config, exceptions), 181
  tests, `mypy --strict` clean, 99% coverage. Full writeup: `SIGNAL_ENGINE_VALIDATION_REPORT.md`.
- **Independent adversarial review** (same technique that caught 2 critical Market Scanner bugs and 6
  Strategy Manager bugs) found **7 issues (2 CRITICAL, 3 HIGH, 2 MEDIUM)**; 6 were real and fixed with
  regression tests, 1 confirmed correct-as-designed: (1) `_collect()` read a handle's `contract`
  property *before* its exception boundary — a broken read would crash the whole batch's evaluation,
  not just one strategy's; (2) the documented default `max_workers=1` plus `Future.result(timeout=...)`'s
  inability to actually interrupt a hung thread meant one truly-hung (not merely slow) strategy would
  permanently wedge the engine's shared worker pool, silently starving every later cycle and deadlocking
  `shutdown()`; (3) a `required_context()` exception during symbol-scoping silently dropped a
  genuinely-scoped strategy with zero trace instead of producing a classified signal; (4) a context
  missing `meta.as_of` produced an empty batch instead of one INVALID signal per scoped strategy, per
  the API doc's explicit "all signals INVALID/NEED_CONTEXT, never a crash" text; (5) the documented
  Output Collector deduplication (same strategy_id+symbol+as_of → keep one, drop extra) was entirely
  unimplemented; (6) `validator.py`'s `MISSING_TIMESTAMP` check tested `as_of is None`, permanently
  unreachable dead code since the field is typed plain `int` and the real "missing" sentinel is `0`.
  The 7th finding (`UNKNOWN_STRATEGY` validation never exercised) was investigated and found to be
  correct as designed — the frozen `validate_signal(signal) -> ValidationResult` API has no
  `known_strategy_ids` parameter, and the engine is explicitly "no research access" with no persistent
  strategy registry to check against.
- Fixes: moved the contract read inside `_collect()`'s try/except; added `_refresh_executor()` (fresh
  worker pool every cycle, bounding a hang's blast radius to the cycle it occurred in — the best a
  pure-thread design can do without process isolation); `_is_scoped_to_symbol()` now fails OPEN
  (treats a scoping exception as scoped, routing it into the full classified pipeline) instead of
  silently dropping; added `_missing_as_of_signal()` (classified INVALID/MISSING_TIMESTAMP fallback,
  wired into both `evaluate()` and `evaluate_strategy()`); added `_dedupe()` (keeps the first
  occurrence, records drops in `degraded_reasons`); tightened the dead `is None` check to `not
  signal.as_of`.
- Confirmed via the real Strategy Manager (`test_engine_integration.py`): every real strategy's
  `StrategyRuntimeHandle` still raises `StrategyApiNotImplementedError` for every method except
  `required_context()` (Strategy Manager's own documented, unmigrated scope boundary) — the Signal
  Engine degrades this to a classified `INVALID`/`CORRUPTED_OUTPUT` signal end-to-end, never crashes,
  and stays fully queryable.
- **Verdict: Signal Engine v1 = READY.** Does not self-authorize Scoring Engine (Phase 6.4) — still
  CEO-gated; work stopped immediately after the verdict per the CEO's explicit directive for this task.
  No changes to Research Lab, Strategy Library, Strategy Interface, Market Scanner, or Strategy Manager.
  Full `ai_trader/` suite green: 559 tests, 47 source files, mypy --strict clean, no regressions.

## Session 2026-07-14 (deep validation) — Market Scanner v1: CPU profile, memory, parity vs frozen engine
- Filled the three gaps a later CEO directive asked for that the original Phase 6.1 validation never
  captured: a real `cProfile` capture (120wd x 3-symbol, 34,440 contexts) confirms schema validation
  still dominates wall-clock (~73-74%) with no new hotspot -- the existing `fastjsonschema` fix already
  addressed the real bottleneck; a formal external-process memory measurement (`Get-Process` sampling,
  not `tracemalloc`, which is the already-identified root cause of the original hang) shows flat ~101 MB
  RSS across the full 2yr x 3-symbol run, no growth; and the first-ever parity check against the frozen
  research engine (`code/mstrat.py`), run against the full real 84,152-bar historical XAUUSD M15 series
  (not synthetic data).
- **Parity result**: M15-native features match the frozen engine exactly (including the two features
  with a documented deliberate divergence -- EMA/RSI seeding -- which converge well within the warmup
  window used). `or_high`/`or_low` match exactly once mstrat's own documented usage gate
  (`bar_in_sess>=4`) is applied to both sides -- the scanner's version is lookahead-safe by construction
  where the raw research-engine column is not, without that gate. One real, non-blocking finding:
  HTF-derived (`h1_`/`h4_`/`d1_` `trend_up`/`volrank`/`rsi`) and D1-derived level features
  (`pdh`/`pdl`/`pd_open`/`pd_close`/`pd_mid`/`pw_high`/`pw_low`) diverge at genuine gaps in the
  underlying H1/H4/D1 feed (root-caused to a specific missing Friday D1 bar), where the two systems use
  different but individually valid, individually lookahead-safe conventions for when a bar's data
  becomes usable across a gap. Rare (isolated to actual data gaps, confirmed 0 lookahead violations
  throughout), does not affect determinism, added to the backlog as a design decision for a future
  directive -- not fixed reactively, since no defect was found, only a legitimate convention difference.
- **No Market Scanner source code changed.** Full writeup: `MARKET_SCANNER_VALIDATION_REPORT.md` §7.
  **Verdict unchanged: READY.** Full test suite still green (378 tests, 36 files, mypy --strict clean,
  97%/99% coverage) -- confirmed no regressions from this investigation.

## Session 2026-07-14 (Phase 6.2) — Strategy Manager v1 implemented, adversarially reviewed, READY
- CEO approval granted; implemented the Strategy Manager production module against the frozen
  `ai_trader/strategy_manager/*.md`/`STRATEGY_REGISTRY_SCHEMA.json` specification and the frozen
  `knowledge/interface/strategy_contract.v1.schema.json` contract — no redesign. 16 source modules
  (loader, compatibility checker, registry, lifecycle controller, context aggregator, health monitor,
  public API facade, typed contract mirror, schema validation x2, config, exceptions, handle,
  required_context), 251 tests, `mypy --strict` clean, 99% coverage. Full writeup:
  `STRATEGY_MANAGER_VALIDATION_REPORT.md`.
- **Independent adversarial review** (same technique that caught 2 critical Market Scanner bugs) found
  **6 real bugs**, all fixed and regression-tested: (1) `reload()` silently cleared an operator's
  `DISABLED` kill-switch on any unrelated content change; (2) `MISSING_DEPENDENCY` was reported as
  health but never actually enforced at `activate()` time, and dependents weren't re-evaluated when a
  dependency deactivated; (3) `reload_transition()` checked compatibility before `NOT_IMPLEMENTED`
  status, opposite of `initial_lifecycle()`'s order, misclassifying stubs; (4)
  `compute_required_context()` silently collapsed multiple `required_data` entries sharing a
  timeframe, dropping fields compatibility had already validated; (5) `auto_admit_min_maturity` only
  applied to brand-new strategies, never an existing one whose reloaded contract cleared the bar; (6)
  `retire()` rejected `INVALID`/`NOT_IMPLEMENTED` sources though the transition table says "from: any".
- **Confirmed, documented, pre-existing gap** (not a Strategy Manager defect): the real
  `knowledge/strategies/*/strategy.json` files are "v0 seed" shape and do not validate against the
  frozen v1 contract schema (already flagged in `STRATEGY_INTERFACE_v1.md` §7 as a separate,
  CEO-gated migration task). Pointed at the real Library, the Manager correctly discovers all 51
  strategies and quarantines every one as `INVALID`, reaching a fully queryable `READY` state with an
  empty active set — the documented fail-safe design working as intended. A dedicated integration test
  asserts this exact outcome as a tripwire against silently regressing once that migration eventually
  happens.
- `StrategyHandle.api` deliberately implements only `required_context()` (the one Strategy API method
  that's a pure function of the contract); the six behavioral methods
  (`detect`/`generate_signal`/`get_score`/`can_trade`/`can_open_position`/`explain_signal`/`health`)
  raise a typed `StrategyApiNotImplementedError` — that logic requires per-strategy rule evaluation
  that doesn't exist anywhere in this repo and belongs to the Signal Engine (Phase 6.3, not started).
- **Verdict: Strategy Manager v1 = READY.** Does not self-authorize Signal Engine (Phase 6.3) — still
  CEO-gated. No changes to Research Lab, Wave 1, Strategy Library, Strategy Interface, or Market
  Scanner (confirmed via full combined test suite + mypy — 378 tests, 36 files, zero regressions).

## Session 2026-07-14 (resolution) — Market Scanner v1 large-scale benchmark: root-caused, READY
- Resolved the benchmark left incomplete at the `ai-trader-implementation` handoff (commit `14bef43`) and the
  further "retracted, unknown" correction committed concurrently by a second session (`f61edfb`) — see
  NEXT_SESSION.md §5's RESOLVED note and `MARKET_SCANNER_VALIDATION_REPORT.md` for the full account.
- **Root cause found by direct A/B experiment**: `tracemalloc.start()`, called unconditionally around the old
  benchmark's full run, becomes catastrophically slow at ~2yr x 3-symbol scale (~217K contexts) — confirmed by
  re-running the identical replay with and without it (204s complete vs. >5.5min to not even finish the first
  2,000-context checkpoint). Harness artifact, not a Market Scanner defect; no scanner source changed.
- Full bisection (252/300/350/400/450/504 weekdays x 3 symbols) completed cleanly at every step with real,
  reproducible numbers (204.1s / 709 ctx/s / 0 lookahead violations at the full 2yr scale) using a new,
  instrumented, self-limiting harness now **committed** at `ai_trader/market_scanner/benchmarks/` (previously
  scratchpad-only, lost between sessions). `mypy --strict` clean across all 20 source files; 127/127 tests;
  97% coverage — all reproduced on a freshly-created venv (the original was in an ephemeral Temp dir and gone).
- **Verdict: Market Scanner v1 = READY.** Does not self-authorize Strategy Manager (Phase 6.2) — still CEO-gated.
- Housekeeping: killed a stale orphaned benchmark process left running since the original handoff (PID 26844,
  ~262 minutes CPU time and climbing when found).

## Session 2026-07-14 (close) — OFFICIAL SESSION CLOSE PRE-WAVE1 (consolidation)
- Consolidated master + matched-null-validation + family-implementation-s21-s40 + strategy-development into ONE
  official branch **research-main**. Engine byte-identical across all branches (zero code conflict); only CHANGELOG
  unioned + 2 report files (S1–S40 canonical, S1–S20 variants preserved). BRANCH_CONSOLIDATION_AUDIT.md.
- Integrity verified: portable path (no Temp), 84,152 bars, engine parity+smoke PASS, matched-null tests PASS,
  generator 54, planner 54→52, all JSON/parquet valid, tree CLEAN (196 files).
- Created SESSION_CLOSE_PRE_WAVE1.md, BRANCH_CONSOLIDATION_AUDIT.md, ARTIFACT_INVENTORY_PRE_WAVE1.md, WAVE1_HANDOFF.md;
  rewrote PROJECT_STATE_v1.0.md, updated PROJECT_AUDIT.md + NEXT_SESSION.md. Portable archive + SHA256 + restore instructions.
- **Wave 1 = PLANNED, FROZEN, NOT STARTED.** Nothing implemented/run; holdout SEALED; no FDR. Next session starts with Wave 1 execution (CEO-gated).

## Session 2026-07-14 — Experiment Planner v1 (54 HGv1 -> 10-experiment falsifiable plan, no backtest)
- Built knowledge/experiments/: EXPERIMENT_REGISTRY.jsonl/.md, HYPOTHESIS_DEDUPLICATION.md, EXPERIMENT_PRIORITY_MATRIX.md,
  WAVE_1/2/3_SPEC.md, CLAUDE_CODEX_REVIEW.md; code/experiment_planner_v1.py (structural-valid + dedup + type + info-value).
- Funnel: 54 hypotheses -> 54 structurally valid -> 52 after semantic dedup -> all T0 -> **10 selected** (2 mechanism,
  2 contradiction, 2 beta, 2 placebo, 2 alpha) in 3 waves. Prioritized by INFORMATION VALUE (not expectancy/prior).
- Codex inline: merged HGv1-044+004 into a 2x2 factorial (EXP-07); required explicit control/ablation arms per
  experiment; shared matched-null + label-shuffle harness; hierarchical family-wise multiplicity plan (top risk).
  CODEX FILESYSTEM REVIEW PENDING.
- Read-only; engine + S1-S51 byte-frozen; nothing implemented/run; holdout SEALED; no FDR. Stop after planning.

## Session 2026-07-13 (h) — Hypothesis Generator v1 (architecture + logic, no backtest)
- Built knowledge/generator/: HYPOTHESIS_GENERATOR_V1.md (architecture), code/hypothesis_generator_v1.py (logic),
  GENERATED_HYPOTHESES_v1.jsonl/.md (54 demo candidates), CLAUDE_CODEX_REVIEW.md, generator_summary.json.
- Recombines ONLY existing KB/Ontology (primitives/conditions/invariants/contradictions) — no new primitives,
  NO backtest. 7 operators (O1 transfer, O2 stacked-selectivity, O3 cross-level-type, O4 contradiction-resolver,
  O5 beta-deconfound, O6 placebo, O7 boundary/counterfactual). Hard novelty gate vs S1-S51 signatures: every
  candidate auto-states why-new / contradiction / mechanism / differs-from-all-S1-S51 + refinement-vs-genuinely-new.
- Codex inline review adopted: observational novelty is necessary-not-sufficient (v2 semantic signature),
  O2 anti-inflation guards encoded, added O7, prior->prior_plausibility (hidden from validators). CODEX FS REVIEW PENDING.
- Read-only; engine + S1-S51 byte-frozen; nothing implemented/validated; holdout SEALED; no FDR.

## Session 2026-07-13 (g) — lab ONTOLOGY + knowledge graph + hypothesis generator
- Built knowledge/ontology/: ONTOLOGY.md, INVARIANTS.md (9 invariants), RELATIONS.md (38 observational edges),
  HYPOTHESIS_GENERATOR.md, KNOWLEDGE_GRAPH.json/.jsonl, GENERATED_HYPOTHESES.jsonl, CLAUDE_CODEX_REVIEW.md.
- 42 nodes (19 primitives + 14 conditions + 9 invariants); graph-driven generator emitted **19 candidate
  hypotheses** (11 alpha-candidates, 3 experiments, 2 beta-diagnostics, 3 mechanism-tests). Proposals only.
- Codex inline review adopted: relations made OBSERVATIONAL (one-family evidence can't support causal edges);
  P001-vs-P011 relabelled a matched-contrast; invariant wording softened; hypotheses tagged by kind; added
  Codex's placebo/mechanism-invariance rule (F). CODEX FILESYSTEM REVIEW PENDING.
- Read-only; engine + S1-S51 byte-frozen; no strategy implemented/validated; holdout SEALED; no FDR.

## Session 2026-07-13 (f) — knowledge/ base (behavioral primitives from S1-S51)
- Built official `knowledge/` folder (read-only synthesis; engine + S1-S51 untouched): README, BEHAVIOR_REGISTRY
  (.md/.jsonl), MECHANISM_REGISTRY (copy), STRATEGY_EVIDENCE_MAP, NEGATIVE_EVIDENCE_REGISTRY, CONTRADICTION_REGISTRY
  (10 contradictions), VALIDATION_STATUS, CLAUDE_CODEX_REVIEW, and primitives/ (13 files).
- **19 behavioral primitives** distilled from the CEO's 23 candidates (5 merged): 6 SUPPORTED-EXPLORATORILY
  (confirmed-sweep, failed-breakout-fade, opening-range, round-number, trend-efficiency, short-term-overreaction),
  4 MIXED, 1 INCONCLUSIVE, 8 REPEATEDLY-NEGATIVE. Status never "VALIDATED".
- Codex inline review (mapping/consistency): adopted P014→MIXED, P019 renamed (two subtypes), +4 contradictions
  (C7-C10). CODEX FILESYSTEM REVIEW PENDING (stale sandbox). No strategy/engine change; holdout SEALED; no FDR.

## Session 2026-07-13 (e) — S21-S40 family implementation + Lab Knowledge System (branch family-implementation-s21-s40)
- Implemented 14 new families (Tier A: S21,S23,S26,S38,S39,S40; Tier B: S22,S24,S25,S27,S28,S29,S30,S31) in
  `code/mstrat_ext.py`, reusing the FROZEN engine (mstrat.py byte-identical to 1bc0ffb). 328 hyps; 2 genuine
  positives with +OOS: **S22 (round-number momentum), S39 (trend-efficiency continuation)**. Others negative or
  calendar-overfit (S29/S31 screen-RW but OOS-refuted). No optimization; definitional fixes only (pre-PnL).
- **Lab Knowledge System** built (Claude + Codex inline collaboration): STRATEGY_REGISTRY (2300/375/139),
  dedup 139 RW → 22 distinct, MECHANISM_REGISTRY (13 mechanisms), KNOWLEDGE_REGISTRY (5 falsifiable claims),
  STRATEGY_PROFILES, TOP_STRATEGIES_SHORTLIST (~8 distinct), EXPLORATORY_PORTFOLIO_DIAGNOSTICS, CLAUDE_CODEX_REVIEW.
- Codex consulted via compact inline prompts (TASKs 2-5 complete); its filesystem snapshot is STALE → CODEX
  FILESYSTEM REVIEW PENDING. Shortlist for future matched-null→global-FDR: S5, S2, S1-short, S1-low/swing(prov),
  one momentum rep, S22 (+ S1-low/pdh, S17-pwlow reserve). Calendar excluded (family-wise selection). Nothing
  validated; holdout SEALED; no global-FDR. Not merged.

## Session 2026-07-13 (c) — Matched-null remediation & validation (branch matched-null-validation, consolidated)
- Diagnosed old miscalibration (bare synthetic R vs real-price null); rebuilt Test B on synthetic PRICE series
  through mstrat.simulate. Adversarial battery exposed a 2nd defect (absolute-risk bootstrap → FPR 0.975 under
  drift); fixed via risk/ATR rescaling (drift FPR 0.975→0.00). Calibration+power+adversarial+parity all PASS.
- Pilot on 10 pre-registered real hyps: rejects losers; only S5 survives research+OOS; most fail OOS.
  **ENGINE VERDICT A — MATCHED-NULL VALIDATED** (unstratified). docs/MATCHED_NULL_VALIDATION.md. Global-FDR/holdout CEO-gated.

## Session 2026-07-13 (b) — Portability fix + reproducibility test (CEO-approved, scope-limited)
- **Git checkpoint:** folder was un-versioned → `git init` + baseline commit `85857234bad5172634e9c2b603e873976a204470` (pre-fix, 58 files). Added `.gitignore` (venv/, __pycache__/).
- **Portability (class A only):** `code/mtf.py` `D` repointed from hardcoded Temp → `Path(__file__).resolve().parents[1]/"data"/"market"` (str-typed, env override `AI_QUANT_DATA_DIR`). This single constant feeds the whole campaign chain (mstrat/s1/mtf). Secondary Temp paths (data-rebuild + GC-foundation scripts) classified and DEFERRED as debt D8 (not on campaign path).
- **Environment:** created `venv` (Python 3.14.6); installed requirements + pyarrow (parquet engine missing from requirements = debt D9). Versions newer than original (pandas 3.0.3/numpy 2.5.1/pyarrow 25.0.0).
- **Reproduction = EXACT (Verdict A):** re-ran `run_full_campaign.py` (ENGINE v2) into `results/reproduction_v2/` → bit-exact vs baseline: 1972/1800/357/130/14/9; per-hypothesis parquet max abs diff 0.0; total trades 1,300,740 identical; boolean verdicts identical; 0 Temp reads; holdout SEALED; baseline untouched.
- **Data note (D10):** M15 file has 84,152 bars (docs said 84,151 = wc off-by-one, no trailing newline); proven identical to baseline data. No data/result change.
- New artifacts: PORTABILITY_AUDIT.md, REPRODUCIBILITY_AUDIT.md, results/reproduction_v2/{full.log, FAMILY_RESULTS.parquet, ENGINE_RUNTIME_PATHS.json, comparison.json}. Marked stale (non-destructive): results/PROJECT_STATE_v1.0.json, docs/ALPHA_REGISTRY.md.
- **Unchanged:** methodology, S1–S20 definitions, thresholds, holdout, p-value engine. Matched-null NOT started (awaits a new CEO gate).

---

## Session 2026-07-12 → 2026-07-13 (AI Quant Research Lab)

Chronological, verified from code/logs. Earlier foundation (COMEX GC) summarized; main work is the pivot to alpha discovery.

## Foundation (closed)
- COMEX GC MBO acquired (Databento, legacy normalization, GCQ6 iid=42011464, 2026-06-29→07-10).
- Phase B: order-book reconstruction validated **bit-exact vs MBP-10** (foundation_gc/engine.py); dual-compatible legacy/new parser.
- MBO micro-structure discovery (trajectory-divergence design): **NEGATIVE** — no reproducible pre-price MBO edge (60k+ hypotheses).

## Pivot → AI Quant Research Lab (alpha discovery)
- Designed 6-AI separation-of-powers architecture (Director/Generator/Backtest/Statistician/RedTeam/Portfolio).
- Built MVP alpha pipeline (code/alpha_lab.py, families.py, campaign.py, run_mtf.py, mtf.py); validated with positive/negative controls.

## Data (XAUUSD)
- Built M15 history 2023→2026 via TradingView **Replay** (pullers/pull_replay_m15.mjs): 84,151 bars.
- Gap-filled ~5,000 missing M15 bars at replay-window boundaries (pull_gapfill.mjs).
- Resampled H1/H4/D1 anchored **17:00 NY (DST-aware)** (code/resample_ny.py).
- **Cross-check vs native TradingView OANDA = PASS** (0 OHLC mismatches, 2023-2026, all DST changes).

## Multi-strategy campaign
- Built ONE common engine `code/mstrat.py` (shared simulate + simulate_ref parity + 20 families + shared null).
- Implemented families **S1-S20**; grammar = 1,972 canonical hyps; parity + smoke PASS; lookahead-safe.
- Discovery Screen V1 **FROZEN**: n≥25, exp_research>0, PF≥1.02, maxDD≤25R, research-only (no OOS). Development-tuned.
- **Engine v1 → v2**: added pre-registered stop-floor `executable_stop=max(strategy_stop, max(2×spread,5×tick,0.10×ATR))`.
- Ran **full S1-S20 historical backtest on engine v2** → results/FAMILY_RESULTS.parquet + full.log:
  **1,972 gen · 1,800 valid · 357 HIST-PROFITABLE · 130 RESEARCH-WORTHY · 14 families profitable · 9 research-worthy.**

## Statistical remediation (in progress)
- Proved **analytic normal-approx p-value INVALID in tail** (S6: 2.1e-54 analytic vs ~0.12 empirical) → retracted from verdicts.
- **S6 audit**: extreme p caused by tiny-stop outliers + profit concentration (skew 8.3, kurt 77.6; top-5=71% profit) = R-normalization artifact.
- **S1-rep robustness**: NOT tiny-stop (risk/ATR 2.12) but outlier/time-concentrated (remove top-1→exp −0.02; edge only 2024). NOT rejected.
- Pilot p-engine (docs/MONTE_CARLO_AUDIT.md): block-bootstrap well-calibrated (synthetic controls) but METHOD UNDER VALIDATION; matched-null miscalibrated (fix pending).
- Pre-registered stop-floor spec (docs/MIN_STOP_FLOOR_PREREG.md); frozen primary statistic = expectancy, one-sided (docs/EMPIRICAL_PVALUE_SPEC.md).

## Retractions
- "S1=drift", "S1/S5/S9 decorrelated", "no RC significant", S1-standalone "6 candidates" — all RETRACTED/superseded (see PROJECT_STATE §9).

## Session close (2026-07-13)
- Consolidated lab (code + data + docs + results + pullers) to durable `C:\Users\MEDION GAMING\ai_quant_lab\`.
- Wrote PROJECT_STATE_v1.0.md, PROJECT_AUDIT.md, NEXT_SESSION.md, CHANGELOG.md, SESSION_CLOSE_S1_S20.md.
