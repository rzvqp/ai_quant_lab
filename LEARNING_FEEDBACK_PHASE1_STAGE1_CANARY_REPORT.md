# Learning Feedback -- Phase 1: Capture Activation -- Stage 1 Canary -- Technical Report

**Status**: Stage 1 (canary implementation + run), per explicit CEO authorization (2026-07-23), executed
against `LEARNING_FEEDBACK_PHASE1_CAPTURE_ACTIVATION_DESIGN.md`'s own accepted READY FOR IMPLEMENTATION
verdict. **Stage 2 (the full 12-month run) was explicitly NOT started**, per the CEO's own instruction.

**Files added, nothing else touched**: `learning_feedback_capture_activation_run.py` (the new script),
this report, the design document (now committed alongside, having been accepted), and
`learning_feedback_capture_activation_canary_report.json` (the raw machine-readable results this report
is built from). **No existing `ai_trader/` file was modified** -- `SimulationHarness`, `SimulationContext`,
Shadow Evidence, Portfolio Architect, Decision Intelligence, and every Context Memory contract are
byte-for-byte unchanged, confirmed by `git diff --stat` against the full frozen-module list (empty) and
re-confirmed by the full regression below.

---

## 1. Exact period run

**Canary window**: `2024-10-23 09:00:00 UTC` -> `2024-11-22 09:00:00 UTC` (30 days) -- the first 30 days
of the SAME CEO-approved, non-holdout 12-month window `phase69a_funnel_run.py`/
`portfolio_architect_tiebreak_evidence.py` already established. Unix timestamps: `1_729_674_000` ->
`1_732_266_000`. **2,221 base bars processed.** The sealed terminal holdout
(2025-10-23 -> 2026-07-13) was never touched.

**Configuration**: all 43 currently-registered strategies eligible for both the real-competitive path
(`strategy_id_filter=None`, `use_strategy_runtime=True`, matching Wave D's own baseline) and Shadow
Evidence (`shadow_config=ShadowConfig(enabled=True, shadow_strategies=<all 43>)`, via the existing,
unmodified `all_registered_strategies()` helper). `learning_feedback_repository_path` set to a real,
on-disk directory for the first time in this repository's history.

## 2. PositionOutcome counts

| Metric | Count |
|---|---|
| **Total `PositionOutcome`** | **31** |
| **`STRATEGY` kind (Shadow-sourced)** | **25** |
| **`PORTFOLIO` kind (real-competitive)** | **6** |

Both kinds are non-zero -- canary criteria 3 and 4 both satisfied (criterion 4 was conditional on
"decizii eligibile" occurring; 6 real-competitive positions closed within the 30-day window, confirming
eligible decisions did occur, not just Shadow-sourced ones).

## 3. Distribution by strategy

11 of 43 registered strategies produced at least one `PositionOutcome` in this 30-day window; the other
32 produced none. Consistent with this project's own already-measured base rate (Phase 6.9A: median 7
lifetime real trades/strategy over 3.6 years, 14/43 strategies with zero trades ever) -- a 30-day window
producing activity from roughly a quarter of the registered strategies, dominated by a handful, is the
expected shape, not an anomaly:

| strategy_id | STRATEGY | PORTFOLIO |
|---|---|---|
| S10 | 7 | -- |
| S46 | 5 | 2 |
| S39 | 3 | 3 |
| S40 | 3 | -- |
| S13 | 1 | -- |
| S2 | 1 | -- |
| S25 | 1 | -- |
| S26 | 1 | -- |
| S4 | 1 | -- |
| S42 | 1 | 1 |
| S44 | 1 | -- |
| **Total** | **25** | **6** |

## 4. Complete vs incomplete records

At the underlying `Outcome` layer (the per-fill record `PositionOutcome` aggregates over): **31 total
`Outcome` records, all 31 `RESOLVED` (100% complete). Zero `PENDING`, zero `UNAVAILABLE`, zero
`INVALID`.** Every `PositionOutcome` is, by its own contract, produced exactly once at position-close
(`contracts.py` Sec Position Outcome docstring) -- there is no partial/incomplete `PositionOutcome` state by
construction; completeness is a property of the `Outcome` layer, reported here at that layer as the CEO's
own question actually concerns.

Also produced: **1 `InterimRealization`** (one partial, non-terminal exit somewhere in the window --
confirms multi-leg exits do occur for at least one strategy's contract, resolving the "unknown" the design
document's own Section8 flagged) and **2,021 `Observation`** records (one per bar with at least one
present edge, the base Decision4 orchestration layer every capture call depends on).

## 5. Serialization errors

**Zero.** `ContextMemoryRepository.rebuild()` (which re-parses every line of every JSONL stream via the
repository's own codec) completed without raising, both immediately after the baseline run and after the
interruption/resume experiment below. Every line in every stream file parses.

## 6. Duplicates

**Zero, in the scenario this architecture actually supports and the CEO's own canary scope is asking
about.** Record identity is a deterministic content hash (`identities.py`'s
`compute_edge_evidence_id`/`compute_position_outcome_id`, both unmodified) re-derived from every record in
the baseline repository: 0 duplicate `Outcome` ids, 0 duplicate `PositionOutcome` ids out of 31/31.

**One important, disclosed finding from the interruption/resume experiment (Section8)**: `position_key`
(real-portfolio, `learning_feedback/position_registry.py:36-41`) and Shadow's own `position_id`
(`shadow_evidence/engine.py:334`) are BOTH deterministic only *within the same `run_id`*, by explicit,
pre-existing design ("reproducible across identical replays of the SAME run_id/config" -- both modules'
own docstrings, unmodified by this work). Re-running the identical window under a **different** `run_id`
therefore does NOT deduplicate against a prior run's own records -- not a defect, but a real operational
constraint: **any future recovery from an interrupted run must reuse the exact same `run_id`**, never
start a fresh one, or the repository will legitimately accumulate separate, non-deduplicated records for
what a human would consider "the same" window. Confirmed empirically in both directions (Section8).

## 7. Orphan records

**Zero, across every checked reference.** For all 31 `PositionOutcome` records: 0 with a
`terminal_outcome_id` that fails to resolve to a real `Outcome` in the repository; 0 with a
`constituent_interim_realization_id` that fails to resolve to a real `InterimRealization`. For all 31
`Outcome` + 31 `PositionOutcome` + 1 `InterimRealization` records: 0 with an `observation_id` that fails
to resolve to a real `Observation`. Every cross-reference in the repository is valid.

## 8. Interruption + resume experiment (canary criteria 8 and 9)

**Method**: a first harness was stepped manually (`harness.step()` in a loop, never `run_to_completion()`)
for exactly 900 bars (chosen to land comfortably past the 200-bar warmup, so real capture activity had
already occurred -- an earlier attempt at 40 bars was found, on inspection, to land entirely inside
warmup with zero records written yet, a materially weaker test; corrected before this final run), then
simply abandoned -- no `stop()`, no finalize, no `drain_pending()` -- faithfully simulating an uncontrolled
process kill, directly relevant given this exact session's own earlier recovery from a real power outage.

**Partial state, immediately after the abort**: 700 `Observation`, 6 `Outcome`, 6 `PositionOutcome`, 0
`InterimRealization`, 30,537 `OperationalMetadata` -- **fully parseable** (`rebuild()` succeeded).

**Resume**: a second, fresh harness, using the **identical `run_id`**, re-ran the SAME full 30-day window
into the SAME (already partially-populated) repository path -- the only recovery procedure this
architecture supports (no mid-run checkpoint/resume capability exists by design).

**Final state, after resume completed**: 2,021 `Observation`, 31 `Outcome`, 31 `PositionOutcome`, 1
`InterimRealization` -- **exactly matching the clean single-run baseline in every count, zero
duplicates, fully parseable.** Interruption followed by same-`run_id` resume is provably safe.

A second experiment (different `run_id` for the abort phase vs. the resume phase, the mistake a human
operator could plausibly make) was run as a deliberate negative control: final `PositionOutcome` count
was 37 = 31 (the resumed run's own full, clean set) + 6 (the aborted run's own 6 records, never
superseded because their `run_id`-embedded identity differs) -- precisely explained, not a mystery, and
disclosed in full in Section6/the raw JSON report. This is why Section6 above states the "same `run_id`"
requirement explicitly as an operational constraint for any future Stage 2/production recovery procedure.

## 9. Flow A / frozen-module impact (canary criterion 10)

**Zero diff.** `git diff --stat` against every frozen module (`context_memory/evidence.py`,
`retrieval.py`, `index.py`, `codec.py`, `simulation/portfolio_simulator.py`, `execution_simulator.py`,
`execution_engine/`, `risk_manager/`, `decision_intelligence_v2/`, `market_intelligence/`,
`edge_intelligence/`, `shadow_evidence/`, `portfolio_architect/`, `decision_intelligence/`,
`simulation/harness.py`, `simulation/api.py`, and every `context_memory`/`learning_feedback` contract
file) is empty. `git status --porcelain -- NEXT_SESSION_FLOW_A.md edge_research
EDGE_DISCOVERY_REGISTRY_v1.md EDGE_RESEARCH_PROTOCOL.md EDGE_DISCOVERY_ROADMAP.md` is empty. Only a brand
new script, this report, the design document, the raw JSON results, and a `.gitignore` addition (to
exclude the generated data directory itself, never a source change) exist in the working tree.

## 10. Repository path and file sizes

**Baseline repository**: `learning_feedback_data/canary/` (repo-relative; `.gitignore`d, not committed --
regenerable by re-running the script with the same window/seed/`run_id`).

| Stream | Size |
|---|---|
| `observations.jsonl` | 25,900,769 bytes (~24.7 MB) |
| `operational_metadata.jsonl` | 42,421,785 bytes (~40.5 MB) |
| `outcomes.jsonl` | 24,811 bytes |
| `position_outcomes.jsonl` | 30,807 bytes |
| `interim_realizations.jsonl` | 762 bytes |
| **Total** | **68,378,934 bytes (~65.2 MB), for 30 days** |

**Growth-rate flag for Stage 2 planning (not a defect, a disclosed sizing fact)**: `operational_metadata`
dominates (62% of total size) -- one row per `(observation, strategy)` pair, up to 43 x per bar. Linearly
scaled (not a strict guarantee, but the best available estimate), a full 12-month window would produce
roughly **12x this canary's volume -- order-of-magnitude 800 MB-1 GB total**, `operational_metadata.jsonl`
alone accounting for roughly 500 MB+. This is a real, disclosed planning input for Stage 2's own
authorization, not something this Stage 1 canary needed to solve.

## 11. Total runtime

- Baseline canary run (2,221 bars, all validation queries): **346.6 seconds (~5.8 minutes)**.
- Interruption experiment (900-bar partial run + full same-`run_id` resume run): **~486 seconds
  (~8.1 minutes)**, estimated from the baseline's own measured bars/second rate (900-bar partial phase
  proportional to baseline's 346.6s/2221 bars, plus one full resume pass at the same rate).
- **Combined Stage 1 canary wall-clock: under 15 minutes** for both required experiments together.

## 12. Regression and tests

Full regression, unchanged scope from every prior Sprint's own validation
(`pytest ai_trader/context_memory ai_trader/decision_intelligence_v2 ai_trader/decision_comparison
ai_trader/learning_feedback ai_trader/market_intelligence ai_trader/edge_intelligence
ai_trader/shadow_evidence ai_trader/simulation -q`): **825 passed, 0 failed, 3:31:10 wall-clock.** Run
AFTER the canary (both experiments) completed, confirming the canary run itself introduced zero
regressions -- expected, since no `ai_trader/` source file was touched, but re-confirmed rather than
assumed, per this project's own standing discipline.

---

## 13. Verdict

# READY FOR FULL CAPTURE

**Justification**: every one of the CEO's own 10 canary criteria is satisfied, with real, non-trivial
data (not a degenerate all-zero result): the repository is created on disk (Section10); both streams are
populated with real records (Section2); both `STRATEGY` and `PORTFOLIO` kind `PositionOutcome`s exist
(Section2); zero duplicates in the architecture's own supported recovery scenario (Section6); zero
serialization errors (Section5); all cross-references resolve, zero orphans (Section7); a genuinely
mid-capture uncontrolled interruption, followed by a same-`run_id` resume, reproduces the clean-run state
exactly (Section8); zero impact on Flow A or any frozen module (Section9); zero regressions across the
full 825-test suite (Section12).

**One operational constraint to carry into Stage 2, not a blocker**: any real Stage 2 run must commit to
a single, fixed `run_id` for its own full duration and must not be restarted under a different `run_id`
if interrupted -- reuse the same one, exactly as validated in Section8, or duplicate/orphaned records
will accumulate exactly as the disclosed negative-control experiment demonstrated.

**One sizing fact for Stage 2 planning, not a blocker**: expect roughly 800MB-1GB of repository data for
a full 12-month run at this same 43-strategy/both-kind configuration (Section10) -- worth confirming
available disk space before Stage 2 begins, but not a reason to withhold this canary's own READY verdict.

**Await CEO approval before Stage 2 (the full 12-month run) begins.**
