# Learning Feedback — Dataset Audit (Phase 1 Closeout)

**Status**: audit only, per explicit CEO instruction (2026-07-24). Read-only analysis of the Stage 2
full-capture dataset (`learning_feedback_data/full_capture/`, 688 `PositionOutcome` / 688 `Outcome` / 26
`InterimRealization` / 23,639 `Observation`, `LEARNING_FEEDBACK_PHASE1_STAGE2_FULL_CAPTURE_REPORT.md`).
**Not a strategy audit** — no profitability, edge, or trading-statistic conclusion is drawn anywhere below;
every number is descriptive shape only. **Zero `ai_trader/` file touched, zero architecture change, zero
new production logic.** One throwaway, read-only analysis script
(`learning_feedback_dataset_audit_run.py`) was written to compute the statistics below — it uses only the
repository's own already-existing, already-tested public read API
(`iter_outcomes`/`iter_position_outcomes`/`iter_interim_realizations`/`iter_observations`,
`get_outcome`/`get_position_outcome`/`get_interim_realization`/`get_observation`), the same pattern every
prior diagnostic in this project has used (Phase 6.9A's funnel recorder, Portfolio Architect's
calibration/tie-break scripts). Raw results: `learning_feedback_dataset_audit_results.json`.

---

## 1. Integrity

| Check | Result |
|---|---|
| Total `PositionOutcome` | 688 |
| Total `Outcome` | 688 |
| Total `InterimRealization` | 26 |
| Total `Observation` | 23,639 |
| All records constructed without a validation error | **Yes** — `ContextMemoryRepository.rebuild()` re-parses/re-validates every line of every stream via the repository's own codec; a single malformed record would have raised. It did not. |
| `Outcome` records `RESOLVED` (complete) | **688/688 (100%)** |
| `Outcome` records `PENDING`/`UNAVAILABLE`/`INVALID` | **0** |
| Mandatory fields present | **Yes** — every contract's own `__post_init__` (unmodified) rejects any missing/empty required field at construction time; `weighted_avg_exit_price` (the one nullable field on `PositionOutcome`) is populated in all 688/688 records (0 nulls). |

**Cross-referenced links** (`PositionOutcome.terminal_outcome_id` → `Outcome`;
`PositionOutcome.constituent_interim_realization_ids` → `InterimRealization`; every record's own
`observation_id` → `Observation`):

| Link | Broken |
|---|---|
| `PositionOutcome` → terminal `Outcome` | 0 |
| `PositionOutcome` → constituent `InterimRealization` | 0 |
| `Outcome` → `Observation` | 0 |
| `PositionOutcome` → `Observation` | 0 |
| `InterimRealization` → `Observation` | 0 |

**Physical file integrity** — iterated record count vs. the JSONL file's own physical line count, per
stream (catches any silent double-append or dropped write a logical count alone could miss):

| Stream | Iterated | Physical lines | Match |
|---|---|---|---|
| `outcomes.jsonl` | 688 | 688 | Yes |
| `position_outcomes.jsonl` | 688 | 688 | Yes |
| `interim_realizations.jsonl` | 26 | 26 | Yes |
| `observations.jsonl` | 23,639 | 23,639 | Yes |

**Verdict on integrity: clean.** No missing field, no unresolved outcome, no broken link, no line-count
mismatch anywhere in the dataset.

## 2. Consistency

| Check | Result |
|---|---|
| Duplicate `Outcome` ids | 0 |
| Duplicate `PositionOutcome` ids | 0 |
| Duplicate `position_key` values across `PositionOutcome` | 0 |
| `run_id` consistency | **Fully consistent** — every one of the 688 `PositionOutcome.position_key` and all 26 `InterimRealization.position_key` values begin with exactly `LF-STAGE2-FULL-CAPTURE` (the single fixed `run_id` Stage 2 committed to), verified by parsing the position identity's own leading field, not assumed. |
| `total_net_pnl` = `total_gross_pnl` − `total_costs` arithmetic identity | **0 mismatches**, all 688 records. `total_costs` is uniformly `0.0` across the entire dataset — a pre-existing, already-disclosed limitation of this cost model (Wave D's own report: "Zero execution costs modeled, not a claim of zero real-world cost"), not new to this audit and not a data-quality defect. |

**One genuine anomaly candidate, investigated and fully explained**: `PositionOutcome.total_net_pnl`
sign vs. its own terminal `Outcome.normalized_result` sign disagree in **4 of 688 records (0.58%)**.
Investigated individually (position_key, constituent realizations, both values) — **all 4 are exactly the
positions with one non-empty `constituent_interim_realization_id` (a partial exit occurred before the
final close)**, e.g. `LF-STAGE2-FULL-CAPTURE:XAUUSD:1731333600:SHORT`: an early partial closed at
**+1.92R**, the final remaining piece closed at **−1.08R** — cumulative `total_net_pnl` is positive
(**+$4.62**) while the terminal-fill-only `Outcome.normalized_result` alone is negative. This is **not
corruption — it is `PositionOutcome`'s own designed purpose working exactly as intended**: Sprint 2
Blocker 2 created `PositionOutcome` specifically because a terminal, fill-only `Outcome` can mislead about
a multi-partial position's true cumulative result (`LEARNING_FEEDBACK_NEXT_SPRINT_DESIGN.md`'s own
two-level Level-1/Level-2 analysis, CEO-ratified). All 4 cases were re-derived by hand from the raw
records and the arithmetic checks out in every case. **Verdict on this anomaly: expected, explained,
confirms correct behavior — not a defect.**

**Verdict on consistency: clean**, with one apparent anomaly investigated to a concrete, disclosed,
non-corruption explanation.

## 3. Distributions (descriptive only — no performance interpretation)

### PositionOutcome

| Metric | STRATEGY | PORTFOLIO | Total |
|---|---|---|---|
| Count | 575 | 113 | 688 |

`total_qty_closed`: mean 0.122, median 0.12, range [0.02, 0.30], stdev 0.031 — small, tightly clustered
lot sizes.

`total_gross_pnl` / `total_net_pnl` (identical, since costs are uniformly 0): mean +0.041, median −2.05,
range [−9.93, +29.66], stdev 4.75.

`holding_time_seconds` (terminal_as_of − opened_as_of): mean 158,004s (~43.9 hours), median 25,200s (7
hours), range [900s, 6,543,900s (~75.7 days)]. The long tail (max ~76 days) is a real, disclosed shape
fact worth noting — one or a few positions were held far longer than the median.

`result sign` (count of positive vs. negative `total_net_pnl`, purely descriptive, not an edge claim):
241 positive, 447 negative.

### Outcome (per-fill terminal record)

By kind: 575 STRATEGY, 113 PORTFOLIO (mirrors `PositionOutcome`, as expected — one terminal `Outcome` per
`PositionOutcome`). `normalized_result` sign: 239 positive, 449 negative. Shape: mean +0.022, median
−1.0001, range [−1.390, +9.930], stdev 1.398 — the median sitting near −1.0 is consistent with many
positions closing at approximately a 1R stop-loss on their own final fill, a shape observation only.

### InterimRealization

26 total, all `PORTFOLIO`-kind (0 `STRATEGY`-kind interim realizations occurred in this window — Shadow
positions in this dataset always closed in one single fill). Distributed across 12 distinct strategies
(S46 highest at 10). All 26 carry a `normalized_result` (none `unavailable_reason`-flagged).

### Distribution by session, volatility regime, trend, and multi-timeframe agreement (joined via each
record's own `observation_id` → `Observation.context_snapshot`, 0 join failures)

| Dimension | STRATEGY-kind | PORTFOLIO-kind |
|---|---|---|
| Session | ny 246, asia 158, london 107, late 64 | ny 52, asia 30, london 20, late 11 |
| Volatility regime | NORMAL 286, HIGH 263, LOW 26 | NORMAL 62, HIGH 47, LOW 4 |
| Trend (M15) | DOWN 299, UP 212, FLAT 64 | DOWN 50, UP 44, FLAT 19 |
| Multi-timeframe agreement | STRONG 511, UNKNOWN 64 | STRONG 94, UNKNOWN 19 |

### Distribution by direction and close reason — real, disclosed data-model gaps

**Direction is not a stored field on `Outcome`/`PositionOutcome`/`InterimRealization`.** It is
recoverable, best-effort, **only for `PORTFOLIO`-kind**, by parsing `position_key`'s own 4th
colon-separated field (`{run_id}:{symbol}:{opened_as_of}:{direction}` —
`learning_feedback/position_registry.py`'s own pre-existing format): **69 LONG, 44 SHORT**, all 113
`PORTFOLIO` records parsed successfully. **Shadow's own `position_id` carries no direction field at all**
(`{run_id}:{strategy_id}:{symbol}:{as_of}:{decision_id}`), so direction cannot be recovered for any of the
575 `STRATEGY`-kind records without reaching into execution internals Context Memory's own contracts
never persist — explicitly out of this audit's scope (`no new logic`) and, more importantly, **not
possible without a schema change**, since no such information is captured at write time either.

**Close reason (TP/SL/time-stop/trailing-stop/end-of-run) is not captured anywhere in Context Memory's
Learning Feedback contracts today.** It exists transiently inside Shadow's own client-order-id-based
classification (`shadow_evidence/engine.py`) and the real-portfolio's own execution ledger, but is never
written into `Outcome`/`PositionOutcome`/`InterimRealization`. This is a genuine, disclosed **schema
coverage gap**, not a defect in the 688 records that do exist — flagged as a recommendation (§6), not
something this audit can retroactively compute from data that was never captured.

## 4. Coverage

| Metric | Count |
|---|---|
| Total registered strategies | 43 |
| Strategies with ≥1 `PositionOutcome` | **28** |
| Strategies ever `PRESENT` (Edge Intelligence) at least once | **36** |
| Strategies never `PRESENT` at all, the entire 12 months | **7** — S7, S9, S11, S15, S20, S27, S38 |
| Strategies `PRESENT` at least once but zero `PositionOutcome` | **8** — S3, S12, S17, S19, S23, S31, S50, S51 |

`28 + 8 + 7 = 43` — every registered strategy accounted for in exactly one of the three buckets.

**Why only 28/43 produced output — investigated, not assumed:**

- **The 7 "never present" strategies** never had Edge Intelligence's own rule-based declared-condition
  check (directional trend alignment, session suitability, etc.) return a match, in any of the 23,639
  observed bars, across the full year. This is a stronger, more specific finding than "never traded" —
  their own declared contract conditions simply never held in this particular 12-month market regime. Not
  investigable further without inspecting each of the 7 contracts' own declared conditions individually
  (out of this audit's scope — would require re-opening Edge Intelligence's own per-strategy evidence,
  not a Learning Feedback dataset question).
- **The 8 "present but zero outcome" strategies** did have real opportunities (Edge Intelligence found
  their conditions PRESENT at least once) but none of those opportunities completed the full
  Signal→Scoring→Risk→fill→close lifecycle within the window. This is fully consistent with this
  project's own already-established, independently-measured funnel behavior (Phase 6.9A: only 145 of
  1,016,477 evaluated opportunities were ever ALLOWed portfolio-wide across all 43 strategies, 0.48%; 14/43
  strategies had zero real trades across a much longer 3.6-year span) — **not a new anomaly, a
  re-confirmation of an already-documented, structural low-conversion-rate property of this system.**
- **The 28 "produced output" strategies'** own activity concentration (S46/S39/S40/S10 accounting for
  roughly half of all 688 records, per the Stage 2 report's own distribution table) is likewise consistent
  with this project's own repeatedly-measured strategy-activity heterogeneity.

**Verdict on coverage: legitimate, explained, consistent with prior independently-established findings —
not a data problem.**

## 5. Anomalies

| Check | Result |
|---|---|
| Timestamps outside the configured window (`opened_as_of`/`terminal_as_of`/`observation_as_of`/`resolution_as_of` vs. `[1_729_674_000, 1_761_210_000]`) | **0** |
| `PositionOutcome` with an unusually large constituent-realization count (>5) | **0** |
| `total_qty_closed` ≤ 0 (structurally impossible per `__post_init__`, sanity re-checked independently) | **0** |
| Non-`RESOLVED` `Outcome` records | **0** |
| `InterimRealization`s whose `position_key` never resolves to any `PositionOutcome` (a partial exit with no later terminal close — legitimate if the window ended first, corruption if not) | **0** — every partial-exit position in this dataset also fully closed within the window; none were left dangling. |
| Sign mismatch between `PositionOutcome` and its own terminal `Outcome` | 4/688 (0.58%) — **investigated in §2, fully explained, confirms correct multi-partial-position behavior, not corruption.** |

**No possible corruption found.** Every anomaly check either returned zero, or (in the one non-zero case)
was individually traced to a concrete, correct, by-design explanation, not an unexplained discrepancy.

## 6. Dataset quality

**Question**: is this dataset sufficiently clean to become the official Learning Feedback data source for
future AI Trader stages?

# READY

**Justification**: every structural integrity check is clean (0 broken links, 0 duplicates, exact
line-count matches, 100% `RESOLVED` completeness); the `run_id` consistency rule Stage 1/2 established is
verified, not assumed; the one apparent anomaly (4 sign mismatches) was investigated to a concrete root
cause that confirms the architecture behaves exactly as designed, not a defect; coverage gaps (15/43
strategies with no output) are fully explained and consistent with this project's own already-established
independent measurements (Phase 6.9A); zero timestamp violations; zero dangling records; zero impact on
any frozen module, Flow A, or Flow B beyond this Stage's own additive, gitignored data.

**Issues found (none blocking, both are schema-coverage recommendations, not defects in the existing 688
records)**:
1. **Direction is not a first-class stored field** — recoverable only for `PORTFOLIO`-kind via
   `position_key` string parsing; unavailable for `STRATEGY`-kind entirely. A future consumer needing
   direction for Shadow-sourced records would need a schema extension (out of this audit's own scope to
   propose in detail).
2. **Close reason is not captured anywhere in Context Memory's Learning Feedback contracts** — a genuine
   information gap for any future consumer wanting to distinguish TP-hit vs. SL-hit vs. time-stop vs.
   trailing-stop vs. end-of-run closes. Also a schema-extension recommendation, not a defect.

Neither issue affects the cleanliness, completeness, or trustworthiness of the 688 records that DO exist
today — they describe information the schema was never designed to capture in Sprint 1/2, not information
that was captured incorrectly.

---

## Executive summary

- **Verdict: READY.** The Learning Feedback dataset (688 `PositionOutcome`, 688 `Outcome`, 26
  `InterimRealization`, 23,639 `Observation`, full 12-month CEO-approved window) is structurally clean,
  fully cross-referenced, 100% complete at the `Outcome` layer, and free of duplicates, orphans, or
  unexplained anomalies.
- **Issues found**: none blocking. Two disclosed schema-coverage gaps (direction not stored for
  Shadow-sourced records; close reason not stored at all) are recommendations for a possible future
  schema extension, not defects in the existing data.
- **Recommendations**: (1) if a future stage needs direction/close-reason breakdowns, scope a separate,
  explicitly-authorized schema extension rather than inferring them from `position_key` parsing, which
  works today only by incidental string structure, not a documented contract; (2) the 7
  never-`PRESENT` and 8 present-but-inactive strategies are legitimate and explained, not worth
  re-investigating unless a future stage specifically needs deeper per-strategy diagnosis.
- **Can Learning Feedback become the official base for the next stages of the AI Trader?** **Yes, on data
  quality grounds** — this audit finds no reason the 688-record dataset cannot serve as the official
  Learning Feedback source going forward. This audit does not itself authorize any downstream use
  (Recognition Engine, Statistics Engine, Decision Engine, or any other consumer) — per the CEO's own
  explicit scope, that remains a separate, not-yet-made decision.

**Awaiting CEO approval.**
