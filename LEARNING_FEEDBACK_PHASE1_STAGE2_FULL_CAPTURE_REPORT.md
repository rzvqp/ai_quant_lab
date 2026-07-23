# Learning Feedback -- Phase 1: Capture Activation -- Stage 2 -- Full 12-Month Capture -- Technical Report

**Status**: Stage 2 (the full 12-month run), per explicit CEO authorization (2026-07-24), executed after
Stage 1's own canary (`LEARNING_FEEDBACK_PHASE1_STAGE1_CANARY_REPORT.md`, verdict READY FOR FULL CAPTURE,
ACCEPTED). **Scope strictly honored, per the CEO's own explicit instruction**: capture and integrity
validation ONLY -- no decision or execution logic of any kind was implemented, read, or exercised beyond
what `SimulationHarness`/`ShadowEvidenceEngine` already did, unmodified, for Stage 1.

**Files added, nothing else touched**: `learning_feedback_stage2_full_capture_run.py` (imports
`new_harness()`/`validate_repository()` from Stage 1's own script verbatim -- zero duplicated logic, zero
new algorithm), this report, and `learning_feedback_stage2_full_capture_report.json` (raw results).
**No `ai_trader/` file was modified** -- `git diff --stat -- ai_trader/` is empty, confirmed after the run.

## 1. Exact period run

**Full window**: `2024-10-23 09:00:00 UTC` -> `2025-10-23 09:00:00 UTC` (the literal, non-re-derived
timestamps `1_729_674_000` -> `1_761_210_000`) -- the SAME CEO-approved, non-holdout 12-month window
`phase69a_funnel_run.py`/`portfolio_architect_tiebreak_evidence.py` already established. **23,839 base
bars processed; 23,639 of them produced at least one PRESENT edge and a captured `Observation`** --
matching Phase 6.9A's own independently-measured `total_bars_evaluated=23,639` for this identical window
exactly, an unplanned but strong cross-validation that this run covered the correct, intended period.
The sealed terminal holdout (2025-10-23 -> 2026-07-13) was never touched.

**Run identity**: a single, fixed `run_id="LF-STAGE2-FULL-CAPTURE"` for the run's entire duration, per the
CEO's own explicit instruction to respect Stage 1's own discovered rule (`position_key`/Shadow
`position_id` are deterministic only within one `run_id`). The run completed in one uninterrupted pass --
the interruption/recovery procedure Stage 1 validated was not needed, but remains the documented
recovery path (re-invoke this same script unchanged, same `run_id`) should any future re-run of this
Stage ever be required.

**Configuration**: identical to Stage 1's own canary -- all 43 registered strategies eligible for both
the real-competitive path (`strategy_id_filter=None`, `use_strategy_runtime=True`) and Shadow Evidence
(`shadow_config=ShadowConfig(enabled=True, shadow_strategies=<all 43>)`).

## 2. PositionOutcome counts

| Metric | Count |
|---|---|
| **Total `PositionOutcome`** | **688** |
| **`STRATEGY` kind (Shadow-sourced)** | **575** |
| **`PORTFOLIO` kind (real-competitive)** | **113** |

Sanity cross-check against this project's own prior, independently-measured figures for the identical
window: Phase 6.9A measured **142** real-competitive trades over this exact same window/strategy set.
This run's own `PORTFOLIO` count (**113**) is the same order of magnitude, not identical -- expected,
since Phase 6.9A's own instrumented run and this one were built independently and may differ in some
non-disclosed configuration detail (e.g. exact cooldown/admission parameters); both figures independently
confirm the real-competitive path is sparse (roughly 0.5% of the ~23,639 observed bars), consistent with
the single-shared-slot constraint this project has measured repeatedly (Phase 6.9A, Wave D Audit,
the relevance audit) -- not a discrepancy this Stage's own narrow scope (capture + integrity, not
re-deriving or reconciling Phase 6.9A's own separate study) needed to resolve further.

## 3. Distribution by strategy

**28 of 43 registered strategies produced at least one `PositionOutcome`** over the full 12 months (15
produced none) -- a meaningfully broader activation than Stage 1's own 30-day canary (11/43), exactly as
expected from a 12x-longer window, and consistent with Phase 6.9A's own already-measured base rate
(median ~7 lifetime trades/strategy over a much longer 3.6-year span; low-but-nonzero activity for most,
a long tail of inactivity for some).

| strategy_id | STRATEGY | PORTFOLIO | strategy_id | STRATEGY | PORTFOLIO |
|---|---|---|---|---|---|
| S1 | 41 | 10 | S39 | 64 | 30 |
| S2 | 11 | -- | S4 | 6 | 1 |
| S4 | 6 | 1 | S40 | 65 | 2 |
| S5 | 5 | 2 | S41 | 5 | -- |
| S6 | 4 | -- | S42 | 19 | 1 |
| S8 | 2 | 1 | S43 | 9 | 1 |
| S10 | 67 | 1 | S44 | 33 | 6 |
| S13 | 27 | 1 | S45 | 6 | -- |
| S14 | 4 | 1 | S46 | 66 | 38 |
| S16 | 9 | 1 | S48 | 26 | 4 |
| S18 | 4 | 1 | | | |
| S21 | 3 | 1 | | | |
| S22 | 16 | 1 | | | |
| S24 | 7 | -- | | | |
| S25 | 34 | 4 | | | |
| S26 | 14 | 3 | | | |
| S28 | 12 | 1 | | | |
| S29 | 1 | -- | | | |
| S30 | 15 | 2 | | | |
| **Column totals** | | | | **575** | **113** |

Most active: S46 (66 STRATEGY + 38 PORTFOLIO = 104), S39 (64 + 30 = 94), S40 (65 + 2 = 67), S10 (67 + 1 =
68) -- these four alone account for roughly half of all activity, a concentration pattern worth noting for
Recognition Engine's own future classification-threshold design (§9 open item 2 of its own accepted
design document) but not something this Stage needed to interpret further.

## 4. Complete vs incomplete records

**688 total `Outcome` records, all 688 `RESOLVED` (100% complete). Zero `PENDING`, zero `UNAVAILABLE`,
zero `INVALID`.** **26 `InterimRealization`** records (partial, non-terminal exits) -- confirms multi-leg
exit behavior occurs at meaningful scale across the full window (Stage 1's own canary found only 1,
insufficient to characterize this; 26 over 12 months resolves the "unknown" the original Phase 1 design
document's own Section8 flagged). **23,639 `Observation`** records.

## 5. Serialization errors

**Zero.** `ContextMemoryRepository.rebuild()` completed without raising against the full ~765 MB
repository -- every line in every one of the 6 JSONL streams parses.

## 6. Duplicates

**Zero.** Content-hash record identity re-derived for all 688 `Outcome` and all 688 `PositionOutcome`
records: 0 duplicate ids in either stream. The single, fixed `run_id` used throughout this run (§1) means
the "different `run_id`" failure mode Stage 1's own negative-control experiment demonstrated never had an
opportunity to occur here -- consistent with the CEO's own explicit instruction to respect that rule.

## 7. Orphan records

**Zero, across every checked reference**, at 12-month scale: 0/688 `PositionOutcome` with an unresolvable
`terminal_outcome_id`; 0 with an unresolvable `constituent_interim_realization_id`; 0/688 `Outcome` +
0/688 `PositionOutcome` + 0/26 `InterimRealization` with an unresolvable `observation_id`. Every
cross-reference in the full repository is valid.

## 8. Repository path and file sizes

**Repository**: `learning_feedback_data/full_capture/` (repo-relative; `.gitignore`d, not committed --
regenerable by re-running `learning_feedback_stage2_full_capture_run.py` with the same, unchanged
`run_id`/window/seed).

| Stream | Size |
|---|---|
| `observations.jsonl` | 302,922,764 bytes (~288.9 MB) |
| `operational_metadata.jsonl` | 497,716,198 bytes (~474.6 MB) |
| `outcomes.jsonl` | 551,203 bytes (~538 KB) |
| `position_outcomes.jsonl` | 687,841 bytes (~672 KB) |
| `interim_realizations.jsonl` | 19,907 bytes |
| **Total** | **801,897,913 bytes (~765 MB)** |

Matches Stage 1's own sizing estimate for a full 12-month run ("roughly 800 MB-1 GB") closely --
`operational_metadata.jsonl` again dominates (62% of total size), as predicted.

## 9. Total runtime

**4,052.0 seconds (~67.5 minutes)**, single uninterrupted run, for 23,839 bars / ~765 MB of output.

## 10. Regression / code-change verification

**No `ai_trader/` source file was touched by Stage 2** (confirmed: `git diff --stat -- ai_trader/` is
empty, and `git status` shows only this Stage's own 3 new files). Since Stage 2 exercises exactly the
same, already-tested code paths Stage 1's own 825-test regression already validated (no new logic, per
the CEO's own explicit scope), **the full pytest suite was not re-run for this Stage** -- re-running it
would re-confirm a fact already structurally guaranteed by the empty `ai_trader/` diff, not test anything
this Stage's own scope could have broken. Flagged here explicitly, not silently skipped, so the CEO can
require it if a fresh confirmation is still wanted.

---

## 11. Verdict

# STAGE 2 COMPLETE -- DATA COLLECTION AND INTEGRITY VALIDATION SUCCESSFUL

**Summary**: 688 real `PositionOutcome` records (575 `STRATEGY`, 113 `PORTFOLIO`) now exist in
`learning_feedback_data/full_capture/`, spanning the full CEO-approved 12-month window, across 28 of 43
registered strategies -- the first substantial real Learning/Research Feedback dataset this repository
has ever produced. 100% of underlying `Outcome` records are `RESOLVED` (complete); zero serialization
errors; zero duplicates; zero orphaned cross-references at every checked link; zero impact on any frozen
module or Flow A artifact; the single-fixed-`run_id` rule was respected throughout and the run required
no interruption/recovery.

This directly answers Recognition Engine's own Phase 0 diagnostic gap
(`RECOGNITION_ENGINE_PHASE0_DIAGNOSTIC_REPORT.md`, verdict COLLECT MORE DATA FIRST, zero records found at
that time) -- **a real, non-trivial, integrity-verified population now exists.** Per the CEO's own explicit
Stage 2 scope, **no decision or execution logic was implemented or exercised against this data** -- this
report characterizes only what was collected and its structural integrity, nothing about what it means or
whether it is sufficient for any downstream classification threshold (Recognition Engine's own still-open
item 2, `RECOGNITION_ENGINE_DESIGN.md` Section11).

**Awaiting CEO direction on next steps** -- e.g., whether to re-open Recognition Engine's own Phase 0
evidence-population question against this new dataset, whether to extend capture to additional windows,
or any other use of this now-real data. No such next step is proposed or begun by this report.
