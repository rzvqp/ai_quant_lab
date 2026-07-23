# Learning Feedback — Phase 1: Capture Activation — DESIGN ONLY

**Status of this document**: DESIGN ONLY, per explicit CEO instruction (2026-07-23). No code was written,
no `ai_trader/` file was touched, no test was run, no repository change was made. This file is written to
disk but deliberately left uncommitted (`git status` will show it `??`) pending CEO review, same treatment
as `RECOGNITION_ENGINE_DESIGN.md` before its own acceptance.

**Explicit non-goals, honored throughout this document (verbatim from the CEO's authorization)**: no
recognition logic, no classification, no scores, no Decision Engine work, no change to Shadow Evidence's
own algorithms, no change to Portfolio Architect, no change to Decision Engine. **No Alpha, Red Team, or
Statistician module exists anywhere in this repository's scope** (`ai_quant_lab-research-main`, branch
`ai-trader-implementation`) — those names do not appear in `ai_trader/` or at repo root; this constraint is
satisfied trivially, not because anything was excluded, but because nothing by those names exists here to
touch.

**Objective**: identify the minimal changes needed so a real backtest run begins producing actual
`Outcome`/`PositionOutcome` records in the Context Memory repository — closing the gap Phase 0's diagnostic
found (zero records anywhere, because the capture pipeline has never been turned on).

---

## 1. Current architecture (traced directly from source, this session)

Learning/Research Feedback's capture wiring is **already fully built** (Sprint 1 Phase F + Sprint 2, both
CLOSED, `PROJECT_STATE_v2.md` §8.27). `SimulationHarness.__init__` (`ai_trader/simulation/harness.py:99-108`)
already accepts, among its full parameter list:

```
learning_feedback_repository_path: Path | None = None,
learning_feedback_library_path: Path | None = None,
```

Both default to `None`. `learning_feedback_repository_path=None` means Learning Feedback is **fully inert**
this run (`harness.py:246-247`, the constructor's own comment). `learning_feedback_library_path=None` does
**not** mean inert — it means "use the real Strategy Library's own default path" (`harness.py:193-197`),
passed straight through to Market Intelligence/Edge Intelligence's own contract loading exactly as
`context.strategy_library_path` already works for the Strategy Manager. **This is not a second gate** — it
is a sensible default already pointed at the real library.

**Two independent config surfaces must both be active simultaneously** to get the full Outcome population
this Phase's objective wants:

1. `learning_feedback_repository_path` (a `SimulationHarness` constructor argument) — non-`None` makes
   `self._lf_repo` a real `ContextMemoryRepository`, gating every capture call site (`harness.py:459, 473,
   656, 690, 703-756, 890, 906`, all `if self._lf_repo is not None`).
2. `context.shadow_config` (a `SimulationContext` field, `ai_trader/simulation/config.py:158`,
   `ShadowConfig(enabled=True, shadow_strategies=<ids>)`) — non-empty `active_strategy_ids()` is what makes
   `harness.py:346-356` construct `self.shadow_engine` at all, itself a precondition for any `STRATEGY`-kind
   (Shadow-sourced) capture. `PORTFOLIO`-kind (real-competitive) capture needs only (1); `STRATEGY`-kind
   needs both (1) and (2).

**Both fully-wired terminal-capture chains, traced end to end this session, confirmed already correct**:

- **Real-portfolio (`PORTFOLIO`-kind)**: a position zeroing on a bar → `_lf_process_fills_for_bar`
  (`harness.py:890-891`, gated on `self._lf_repo is not None`) → `RealPositionRegistry.observe()` diffs
  positions (`harness.py:568`) → a death's last trade → `_lf_capture_terminal` (`harness.py:602`) →
  `capture_portfolio_terminal` (`ai_trader/learning_feedback/capture.py:544-588`) → `Outcome` appended
  (`repository.append_outcome`, `capture.py:578`) → `PositionOutcome` built and appended if not `None`
  (`capture.py:583-584`) → `ContextMemoryRepository.append_position_outcome`
  (`repository.py:494-497`) → `position_outcomes.jsonl`.
- **Shadow (`STRATEGY`-kind)**: `ShadowEvidenceEngine.observe()` (`shadow_evidence/engine.py:222-224`,
  reached only if `self.shadow_engine is not None`) → consumed at `harness.py:703-722` (gated on
  `self._lf_repo is not None and lf_observation_id is not None`) → `register_shadow_position(...,
  OutcomeKind.STRATEGY)` → on settlement, `_lf_process_shadow_trade_legs` (called from both
  `harness.py:898-907` per-bar and `harness.py:465-474` at run end, each independently gated on
  `self._lf_repo is not None`) → `_lf_capture_shadow_terminal` (`harness.py:544-546`) →
  `capture_strategy_terminal` (`capture.py:636-679`) → same `Outcome`+`PositionOutcome` append pattern.

**Both chains are complete and correct today.** Nothing in either chain needs to change.

## 2. Where the flow breaks

Not a bug in the capture logic — a **structural absence of any caller that turns it on**:

1. **`ai_trader/simulation/api.py`, the one production-facing facade, cannot express this at all.**
   `SimulationAPI.__init__` (`api.py:94-102`) takes only `symbol_meta`, `data_dir`, `results_dir`,
   `generated_at` — no `learning_feedback_*` parameter anywhere. Its own `configure()`
   (`api.py:107-113`) hard-codes `SimulationHarness(context, self._symbol_meta, self._data_dir)` — three
   positional arguments only. There is no way for any external caller of `SimulationAPI` to request
   Learning Feedback capture; the parameter is structurally unreachable through this facade, not merely
   defaulted off.
2. **No generic backtest runner exists to fix this in one place.** There is no `run_backtest.py`/
   `run_prod.py`/CLI `__main__` anywhere at repo root. Every historical backtest
   (`phase69_rolling_backtest.py`, `phase69a_funnel_run.py`, `phase610_checkpoint1b_s10_validation.py`,
   `phase610_checkpoint1c_s10_validation.py`, `portfolio_architect_phase2a_calibration.py`,
   `portfolio_architect_tiebreak_evidence.py`, `relevance12m_run.py`) constructs `SimulationHarness`
   directly, **bypassing `api.py` entirely**, and none of them passes `learning_feedback_repository_path`.
   One of them (`portfolio_architect_phase2a_calibration.py:71`) already passes
   `shadow_config=ShadowConfig(enabled=True, ...)` for its own unrelated purpose (calibration evidence),
   proving that surface already works in practice — it simply was never paired with a repository path in
   any of these scripts, because none of them existed to produce Learning Feedback data; they existed for
   their own, different, already-closed research questions.
3. **The only place both surfaces are ever exercised together is a test** —
   `ai_trader/simulation/tests/test_harness_learning_feedback.py:109-135` (`tmp_path`, discarded at process
   exit) — confirming the wiring genuinely works when both switches are set, just that nothing in
   production ever sets them.

**No third gap exists.** `learning_feedback_library_path` is not a blocker (§1). `portfolio_architect_config`
and `health_eligible_ids` are unrelated to Learning Feedback and need no change. The capture functions
themselves (`capture_portfolio_terminal`/`capture_strategy_terminal`) have their own correctness guards
(silently returning without a `PositionOutcome` if `entry.outcome_kind` doesn't match, or if the
adapter builders return `None`) — these are deliberate, already-tested behaviors from Sprint 2, not bugs to
fix, but worth disclosing (§5) since a strategy producing zero captured records could mean either "this
gate is working correctly" or "this strategy genuinely never traded" (Phase 6.9A already found 14/43
strategies never trade at all in the real competitive path) — not evidence of a new defect.

## 3. All modifications necessary (minimal set)

**Modification A — a new, standalone capture-activation script. Zero existing files touched.**

A new root-level script (proposed name: `learning_feedback_capture_activation_run.py`, matching this
project's own established naming convention for one-off data-generating runs) that:
- Constructs a `SimulationContext` with `shadow_config=ShadowConfig(enabled=True,
  shadow_strategies=frozenset(all_registered_strategies()))` — reusing `shadow_evidence.config
  .all_registered_strategies()` exactly as `portfolio_architect_phase2a_calibration.py:71` already does,
  zero new logic.
- Constructs `SimulationHarness(context, symbol_meta, data_dir, ...,
  learning_feedback_repository_path=Path("learning_feedback_data"))` — a new, proposed, durable directory
  at repo root (name open to CEO preference; `ContextMemoryRepository.__init__` auto-creates it via
  `root_path.mkdir(parents=True, exist_ok=True)`, `repository.py:436-440` — no manual setup needed).
  `learning_feedback_library_path` left at its default (`None` → real Strategy Library path, §1).
- Runs over a historical window. **Recommendation: reuse the SAME CEO-approved, non-holdout 12-month
  window `portfolio_architect_tiebreak_evidence.py` already used** (a window already cleared for this kind
  of instrumented run, avoiding any fresh holdout/data-governance question — the sealed terminal holdout,
  `PROJECT_STATE_v2.md` §1.1, remains untouched either way).
- Uses `use_strategy_runtime=True` (every other real-data backtest script already does this — real
  evaluators, not a bare pass-through) and no `strategy_id_filter` (all 43 strategies eligible for the
  real-competitive side too, matching Wave D's own baseline configuration).

This modification requires **no change to any existing `ai_trader/` file** — every parameter it uses
already exists and is already tested (Sprint 2's own 825-test regression). It is architecturally identical
in kind to every other one-off research/calibration script already in this repository (Wave D, Phase 6.9,
the relevance audit, Phase 6.9A, every Phase 6.10/Portfolio Architect instrumented run) — none of which
required a production code change to run, either.

**Modification B — OPTIONAL, deferred, small additive change to `SimulationAPI` (2-3 lines, NOT required
for Modification A to work, presented for completeness since it is the one genuine structural gap found in
§2.1).**

Add `learning_feedback_repository_path: Path | None = None` and `learning_feedback_library_path: Path |
None = None` to `SimulationAPI.__init__`, stored and passed straight through at `api.py:110`'s own
`SimulationHarness(...)` construction. Every existing `SimulationAPI(...)` call site (its own test suite,
any future caller) already omits these arguments, so they'd stay `None` — **zero behavior change for any
existing caller**, purely additive. This is not required for Modification A's own first real data-collection
run (which bypasses `api.py` entirely, matching every historical precedent), but would close the structural
gap permanently for any FUTURE official run through the production facade. **Recommend deferring this to a
separate, later, explicitly-authorized step** — it touches `api.py`, a file this diagnostic did not
otherwise need to touch, and bundling it into Phase 1 would slightly widen this Sprint's own footprint
beyond "one new script."

**No other modification is necessary.** No change to `harness.py`, `capture.py`, `repository.py`,
`contracts.py`, `shadow_evidence/`, `portfolio_architect/`, `decision_intelligence*/`, or any contract.

## 4. Impact of each modification

- **Modification A (new script)**: zero impact on any existing file, test, or behavior — it is pure
  addition of a new, independent script. The only "impact" is the new data it produces: real
  `Outcome`/`PositionOutcome`/`InterimRealization` records written to a new, previously-nonexistent
  directory. Competitive execution results are provably unaffected (Sprint 1/2's own byte-identical
  parity proofs, re-affirmed, not re-derived, by this design).
- **Modification B (optional `api.py` passthrough)**: zero impact on any existing `SimulationAPI` caller
  (additive, default `None`). Impact is purely "future callers gain an option they don't have today."

## 5. Risks

1. **Silent failure-isolation risk (the one genuine open risk).** `harness.py:658-665` wraps the
   Market-Intelligence-snapshot + Observation-build step (needed before any capture call) in a broad
   `except Exception` that logs a warning and continues — deliberate, correct failure isolation (a
   Learning Feedback bug must never crash or alter competitive execution). But it also means: if
   `build_market_snapshot`/`build_decision_observation` fail for ANY reason in the real execution
   environment (e.g. a relative-path assumption in the default Strategy Library path resolution that
   behaves differently outside of test fixtures), capture could silently produce **zero** records even
   with both switches correctly set — indistinguishable, from the outside, between "correctly gated off"
   and "silently broken." **Mitigation, built into the plan (§6), not a blocker**: run Modification A first
   over a short window (a few days) as a canary, inspect the produced repository directly (record counts,
   not just "no exceptions raised" or the log output), THEN scale to the full window once confirmed
   non-zero.
2. **Evidence sparsity/skew is expected, not a defect.** Phase 6.9A already measured real-competitive
   trade frequency as heavily skewed (median 7 lifetime trades/strategy over 3.6 years; 14/43 strategies
   never traded at all). A strategy producing zero captured `PositionOutcome` records after the activation
   run is not evidence of a capture bug — it may simply be a low-frequency strategy, exactly as already
   measured. Do not mistake this for a regression when reviewing the activation run's own results.
3. **Run-interruption risk — directly relevant given this exact session's own recent power outage.**
   `_JsonlStream.append` (`repository.py:372`) creates its parent directory defensively per write but a
   crash mid-write could in principle corrupt the final line of a stream file. This is a pre-existing,
   already-understood property of the append-only JSONL design (not introduced by this Phase), mitigated
   by the repository's own idempotent-append and `rebuild()` machinery (Checkpoint 10/11) — but worth an
   explicit post-run integrity check (confirm the file parses cleanly end to end) after any long
   activation run, especially an unattended one.
4. **Performance overhead, unmeasured.** Building a Market Intelligence snapshot + Edge Intelligence
   Observation on every bar `_lf_repo is not None` (in addition to whatever the competitive path already
   computes) adds CPU cost per bar. Every existing usage of `build_market_snapshot`/`build_decision_
   observation` to date has been at small/test scale or short instrumented-run scale
   (`test_harness_learning_feedback.py`, `portfolio_architect_phase2a_calibration.py`'s 85-day window) —
   none at a full 12-month/23,000+-bar scale with Learning Feedback capture simultaneously active.
   Recommend timing the canary run (risk 1's own mitigation) to also confirm acceptable wall-clock cost
   before committing to the full window.
5. **`api.py`'s structural gap remains, if Modification B is deferred.** Any future backtest run through
   the "official" production facade still cannot capture Learning Feedback data until Modification B (or
   equivalent) lands — a disclosed, deliberate scope choice for this Phase, not an oversight, and worth
   the CEO's explicit sign-off on timing (now vs. later).

## 6. Compatibility with existing architecture

Fully compatible, by construction — every element reused here (`ShadowConfig`, `all_registered_
strategies()`, `learning_feedback_repository_path`, `learning_feedback_library_path`, the whole capture
chain) already exists, already passed its own Sprint 1/2 validation (825/825), and is used here exactly as
designed, with no new parameter, no new contract, no new algorithm. Modification A is architecturally
indistinguishable from every prior one-off instrumented research script in this repository's own history.
The standing frozen-module list (`code/`, `results/`, `knowledge/`, every strategy contract/evaluator,
Scoring Engine weights, Risk Policy, Execution Engine rules, the sealed terminal holdout) is untouched by
either modification.

## 7. Phased implementation plan (design only — not executed)

**Stage 1 — canary run.** Write Modification A's script; run it over a short window (a few real trading
days, e.g. 5-10 trading days) with `learning_feedback_repository_path` pointed at a throwaway directory.
Inspect the produced JSONL files directly (record counts per stream, at least one record round-trips
through `iter_outcomes()`/`iter_position_outcomes()`) — confirms risk 1 (§5) is not occurring, before
spending compute on the full window.

**Stage 2 — full activation run.** Re-run Modification A's script over the full recommended 12-month
window (§3), pointed at the real, durable `learning_feedback_data/` directory. Confirm the full regression
suite still passes afterward (no production code changed, so this is a sanity re-confirmation, not an
expectation of finding anything) and record wall-clock duration (risk 4).

**Stage 3 — inventory and report.** Re-run the same kind of diagnostic Phase 0 already performed
(`RECOGNITION_ENGINE_PHASE0_DIAGNOSTIC_REPORT.md`'s own method) against the now-populated repository:
total record counts per `OutcomeKind`, per-strategy distribution, completeness (RESOLVED vs. PENDING vs.
INVALID/UNAVAILABLE `Outcome.status`), and time coverage. This closes the loop directly back to
Recognition Engine's own Phase 0 gate — the CEO can then decide, with real numbers, whether Recognition
Engine implementation is finally ready to authorize.

**Stage 4 (optional, separately authorized) — `api.py` passthrough.** Only if the CEO wants the
production facade itself capable of Learning Feedback capture going forward, independent of Stage 1-3's
own one-off script.

## 8. Estimated data volume for a typical backtest window

Grounded in this project's own already-verified, real figures — not invented:

- **`PORTFOLIO`-kind (real-competitive)**: Phase 6.9A measured **142 completed trades** over its own
  13-month/23,639-bar window, all 43 strategies competing for the single shared XAUUSD slot (the same
  structural constraint that made real trades this sparse, `PROJECT_STATE_v2.md` §6, still applies
  unchanged). Wave D's own full 3.6-year/all-43-static run produced **513 trades** total. **Estimate for a
  12-month activation window: roughly 100-150 `PositionOutcome` records of `PORTFOLIO` kind** — sparse by
  construction, not a capture defect.
- **`STRATEGY`-kind (Shadow-sourced)**: Phase 6.9A's own isolated-slot counterfactual (structurally
  analogous to Shadow's own always-empty-per-edge-portfolio design, §7.4 of `PROJECT_STATE_v2.md`) summed
  **823 positions across all 43 strategies** over the same 13-month window — but this is heavily
  skewed, not uniform: the same Phase 6.9A data shows a median of roughly 7 trades per strategy over a
  3.6-year span at the competitive level, and 14/43 strategies with zero trades ever; Shadow Evidence's
  own Checkpoint 1C S10 validation separately found 68 shadow trades for that ONE strategy over the same
  13 months — on the high end, not necessarily representative of the median strategy. **Estimate for a
  12-month activation window: order-of-magnitude 600-900 `PositionOutcome` records of `STRATEGY` kind,
  unevenly distributed — a plausible range bracketed by the 823-position isolated-counterfactual figure,
  not a precise prediction.** Some strategies will contribute dozens; several will likely contribute zero,
  matching already-measured behavior, not a new finding.
- **`InterimRealization` records** (partial exits, pre-terminal): volume unknown — depends on how many of
  the 43 strategies' contracts use multi-leg/scaled exits vs. single all-or-nothing exits, a fact not
  measured by any prior phase. Disclosed as a genuine unknown, not estimated by assertion; Stage 3's own
  inventory will resolve it with real numbers.

---

## 9. Verdict

**READY FOR IMPLEMENTATION** (Modification A + Stages 1-3; Modification B/Stage 4 optional and separable).

Justification: every element Modification A needs already exists and is already validated by Sprint 1/2's
own 825-test regression; the only structural gap (§2) is the complete absence of any production caller
that turns the capture switches on, not a defect in the capture logic itself; the one genuine open risk
(§5.1, silent failure isolation) has a cheap, already-designed-in mitigation (the Stage 1 canary run) rather
than requiring a design revision; no frozen module, contract, or existing behavior is touched. This is
architecturally the same shape as every other "one new instrumented script" precedent already accepted in
this project (Phase 6.9A's funnel recorder, Portfolio Architect's Phase 2A calibration run) — none of which
needed a second design round before their own implementation was authorized.

**Await CEO approval before Stage 1 begins. No code has been written. No repository change has been made.**
