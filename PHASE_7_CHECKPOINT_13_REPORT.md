# Phase 7 — Checkpoint 13: Contextual Evidence Aggregation

**Validation label: TARGETED VALIDATION PASSED.** Per the Checkpoints 10–13 batch's own validation
policy, only the `context_memory` package's own tests, `mypy --strict` scoped to the package, and
targeted coverage were run at this checkpoint's own close. The one combined-batch Context Memory
validation and the single full-repository suite run happen next, now that all four checkpoints are
implemented.

## 1. Input Boundary

`aggregate_evidence(index, retrieval, strategy_id, policy=None)` consumes an already-computed
Checkpoint 12 `RetrievalResult` and a `HistoricalIndex` — it never re-runs retrieval, never queries live
market data, and never imports `decision_intelligence` (re-confirmed by the AST-based
`test_import_independence.py`, which globs every module in the package). `aggregate_all_present_edges`
is a thin, deterministic wrapper producing one report per distinct PRESENT `strategy_id` across the
retrieval's own matches, sorted by `strategy_id` — never a ranked comparison between edges.

## 2. Output Contract

`ContextualEvidenceReport` (frozen dataclass, 30 fields) covers every category the CEO's mission
requires: query/target identity (`query_context_id`, `target_strategy_id`), version provenance
(`retrieval_policy_version`, `evidence_policy_version`, `outcome_definition_version`), cutoff/tier
(`as_of_cutoff`, `selected_relaxation_tier`), raw vs. episode-aware counts (`raw_outcome_count`,
`episode_count`, `resolved_outcome_count`, `unresolved_outcome_count`, `invalid_outcome_count`,
`excluded_incompatible_outcome_count`), compatibility metadata (`horizon`, `cost_model_ref`),
freshness/coverage (`evidence_freshness_newest_age`, `evidence_freshness_oldest_age`,
`time_coverage_span`), point/dispersion/uncertainty statistics (`contextual_win_rate`,
`mean_normalized_result`, `median_normalized_result`, `result_dispersion_stdev`,
`confidence_interval_95`, sign counts, `evidence_consistency`), the controlled status
(`evidence_status`, `evidence_status_reason`), `limitations`, and full provenance
(`source_episode_ids`, `source_observation_ids`). **Only metrics supported by the real `Outcome`
contract are computed** — no `pnl_r`/ATR-normalized-return field exists on the approved `Outcome`
contract (Checkpoint 9), so only `normalized_result`-derived statistics are produced; this is a
disclosed scope limitation, not an oversight.

## 3. Controlled Evidence Status Vocabulary

`EvidenceStatus`: `SUFFICIENT`, `LIMITED`, `CONTRADICTORY`, `STALE`, `UNAVAILABLE`, `INCOMPATIBLE` — the
CEO's own five proposed names plus `INCOMPATIBLE` (structural — the underlying retrieval itself did not
succeed). Never manually set; always derived by `_classify()`'s fixed priority chain (design doc §10.1,
adopted verbatim): zero resolved evidence → `UNAVAILABLE`; staleness threshold configured and exceeded →
`STALE`; 95% CI straddles zero → `CONTRADICTORY`; below the SUFFICIENT threshold → `LIMITED`; otherwise
`SUFFICIENT`. Every classification carries a deterministic, human-readable `evidence_status_reason`.

## 4. Sufficiency Policy — Grounded in an Already-Validated Research Layer Convention

Per the mission's own explicit instruction ("inspect existing Research Layer statistical conventions
before deciding"), `code/alpha_lab.py`, `code/mstrat.py`, `code/mtf.py`, `code/s1.py`, and
`code/campaign.py` were read directly — all five already gate on one shared, long-live constant:
`CFG['MINTR'] = 25` (`code/alpha_lab.py:14`), a minimum-trade-count requirement used unmodified across
the Research Layer for the project's own entire history. `EvidencePolicy.min_episodes_sufficient`
defaults to this exact value (`_RESEARCH_LAYER_MINTR = 25`), reused verbatim rather than reinvented.
`EvidencePolicy` is an explicit, versioned (`EVIDENCE_POLICY_VERSION`), caller-overridable dataclass —
never a hidden constant — and every report carries its own `evidence_policy_version`, satisfying
"explicit, versioned, appear in output, sensitivity-testable." `test_policy_default_uses_research_layer_mintr`
pins the value directly; `test_sufficient_status_at_or_above_research_layer_threshold` /
`test_limited_status_below_threshold` prove the boundary behavior at 30 vs. 5 episodes.

`min_episodes_limited` defaults to `1` — the smallest meaningful non-zero count, not an arbitrary choice
— and `EvidencePolicy.__post_init__` rejects `min_episodes_limited > min_episodes_sufficient` as an
invalid configuration. **`staleness_threshold_seconds` defaults to `None`** — no existing Research Layer
convention defines an evidence-age threshold (as distinct from trade-count sufficiency), so per the same
"do not invent arbitrary thresholds" discipline, `STALE` is simply never produced unless a caller
explicitly supplies a threshold; `evidence_freshness_newest_age`/`_oldest_age` are still always reported
raw regardless, so a caller can apply their own judgment (`test_no_staleness_check_when_threshold_not_configured`).

## 5. Episode-Level Counting (No Overlapping-Sample Inflation)

An episode's own outcome evidence is drawn exclusively from the outcome attached to its FIRST member
observation (`episode.observation_ids[0]`) — the same "episode's resolution point is the first bar of
the run" convention Checkpoint 8 design §9.3 and Checkpoint 11's own `Episode.representative_context_snapshot`
already establish. This makes `resolved_outcome_count` structurally at-most-one-per-episode by
construction — no separate de-duplication pass is needed, and `test_episode_aware_count_never_exceeds_episode_count`
proves the invariant directly. `raw_outcome_count` additionally reports the naive sum across EVERY
member observation's own outcome (for transparency only) — every statistic in the report is computed
from the episode-collapsed set exclusively, never from the raw one.

## 6. Multiple PRESENT Edges

`aggregate_evidence` computes one report for exactly one `strategy_id`, filtering `retrieval.matches` to
only episodes where that edge was PRESENT — different edges' evidence is never mixed.
`aggregate_all_present_edges` produces the full, deterministically `strategy_id`-sorted collection for
every distinct edge present across the retrieval — `test_aggregate_all_present_edges_is_sorted_and_independent`
confirms both the sort order and that each report is computed independently (never a cross-edge ranking).

## 7. Outcome Compatibility — Partition, Never Silent Pooling

Resolved outcomes are grouped by their `(outcome_definition_version, horizon, cost_model_ref)` triple;
the most-common triple (deterministic tie-break: version namespace/version, horizon, cost ref) becomes
the "dominant" one used for every statistic, and any outcome under a different triple is EXCLUDED and
reported via `excluded_incompatible_outcome_count` plus an explicit `limitations` entry — never silently
pooled across incompatible definitions. `test_incompatible_outcome_definition_version_is_excluded_and_disclosed`
proves this directly with a mixed `od-v1`/`od-v2` scenario.

## 8. Statistical Safety

`mean_normalized_result` AND `median_normalized_result` are both always reported (the median is
outlier-resistant — `test_median_resistant_to_single_outlier` proves it stays low while a single 100.0
outlier drags the mean up), `result_dispersion_stdev` (sample stdev, `n>=2`), a 95%
`confidence_interval_95` (stdlib `statistics.NormalDist`, no third-party dependency), sign counts
(`positive_sign_count`/`negative_sign_count`/`zero_sign_count`) and `contextual_win_rate` (fraction
positive), and `evidence_consistency` (fraction of episodes agreeing in sign with the pooled mean's
sign). **Every report's `limitations` unconditionally discloses that the CI is a normal-approximation,
not a validated bootstrap** — `PROJECT_AUDIT.md` D1 already documents this project's own prior discovery
that analytic normal-approximation p-values can be badly miscalibrated on heavy-tailed R distributions;
that exact caveat is repeated verbatim here rather than silently assumed safe. **This module never
computes a p-value, never claims causal edge validation, and never labels evidence as strategy proof** —
`evidence_status`/`evidence_status_reason` describe evidence quality only.

## 9. Freshness / Contradiction

`evidence_freshness_newest_age`/`_oldest_age` (in seconds relative to `as_of_cutoff`) and
`time_coverage_span` are always computed from the dominant-triple contributing episodes. Contradiction
detection reuses — rather than reinvents — this project's own already-established convention:
`PROJECT_AUDIT.md` §28 documents a live "min-trades + UNRESOLVED-if-CI-straddles" rule for small-n
strategies; `CONTRADICTORY` fires under the identical condition (95% CI straddles zero),
`test_contradictory_status_when_ci_straddles_zero` proving it directly with an alternating +1/-1 result
set. No separate "recent vs. older subgroup" comparison was implemented — the design doc's own §17
leaves its exact statistical support unresolved, and inventing one here would violate the same
no-arbitrary-threshold discipline; `evidence_freshness_newest_age`/`_oldest_age` are reported raw so a
future checkpoint (or a caller) can build that comparison without this checkpoint pre-deciding it.

## 10. Failure Outputs

Explicit, tested scenarios, each returning a fully-populated report (never an exception, never a bare
`None`): underlying retrieval not `SUCCESSFUL` → `INCOMPATIBLE` (for INCOMPATIBLE/UNSUPPORTED_VERSION/
DEGRADED_DATA retrieval statuses) or `UNAVAILABLE` (for NO_ELIGIBLE_HISTORY/NO_SUFFICIENTLY_SIMILAR);
target edge not PRESENT in any retrieved episode → `UNAVAILABLE`; edge PRESENT but zero outcomes
recorded at all → `UNAVAILABLE`; edge PRESENT with only PENDING/INVALID/UNAVAILABLE outcomes (no
RESOLVED) → `UNAVAILABLE`; empty `strategy_id` → `ContextMemoryValidationError` (a caller programming
error, not a data condition).

## 11. Tests

221 tests total in the package (198 carried through Checkpoint 12 + 21 new `test_evidence.py` tests + 2
gap-closing tests added during this checkpoint's own coverage closure = 221 total passing). Categories
covered: `EvidencePolicy` validation (default value pinning, invalid-ordering rejection, non-positive
staleness rejection, wrong-type rejection); every failure-output scenario from §10; SUFFICIENT/LIMITED/
CONTRADICTORY/STALE classification boundaries; no-staleness-check-by-default; episode-aware vs. raw
counting; win-rate and sign-count correctness; median outlier-resistance; unconditional normal-
approximation disclosure; outcome-triple incompatibility partitioning; multi-edge independence and
sort order; and full-report determinism across repeated calls with identical inputs. One white-box
defense-in-depth test (`_classify` with `n=0`, structurally unreachable through the public API) matches
Checkpoint 10/12's own established convention for internal-guard coverage.

## 12. Targeted Coverage / mypy Result

```
coverage report (--source=ai_trader.context_memory, --omit tests/):
    __init__.py          11 stmts   0 miss   100%
    codec.py              62 stmts   0 miss   100%
    contracts.py         145 stmts   0 miss   100%
    enums.py               59 stmts   0 miss   100%
    episodes.py            85 stmts   0 miss   100%
    evidence.py           154 stmts   0 miss   100%
    identities.py          28 stmts   0 miss   100%
    index.py               67 stmts   0 miss   100%
    repository.py         185 stmts   0 miss   100%
    retrieval.py          106 stmts   0 miss   100%
    validation.py          32 stmts   0 miss   100%
    TOTAL                 934 stmts   0 miss   100%

mypy --strict ai_trader/context_memory/ --exclude 'tests/'
    -> Success: no issues found in 11 source files (up from 10 at Checkpoint 12)
```

A first coverage run surfaced 2 missed lines in `evidence.py` (the "edge PRESENT but zero outcomes
recorded at all" early-return branch, and the `_classify` `n < min_episodes_limited` defensive guard —
structurally unreachable via `aggregate_evidence` since `_classify` is only ever invoked after
confirming at least one RESOLVED, dominant-triple outcome exists), closed with 2 additional targeted
tests before reaching the 100% above.

## 13. Public API

`aggregate_evidence`, `aggregate_all_present_edges`, `ContextualEvidenceReport`, `EvidencePolicy`,
`EvidenceStatus`, `EVIDENCE_POLICY_VERSION` — the only names exported for future Decision Intelligence
v2 consumption. No repository/index internals, no `_classify`/`_unavailable_report`/`_sign` helper is
exported (`test_no_internal_canonicalization_helpers_are_exported` covers this generically across the
whole package).

## 14. Files Changed / Commit Hash / Working Tree Status

New: `ai_trader/context_memory/evidence.py`, `ai_trader/context_memory/tests/test_evidence.py`.
Modified: `ai_trader/context_memory/__init__.py` (new exports), `ai_trader/context_memory/tests/test_public_api.py`
(expanded expected export set). `git status --porcelain` before staging showed only these 4 files —
nothing under `code/`, `results/`, `knowledge/`, or any other `ai_trader/` package.

- Branch: `ai-trader-implementation`
- Parent commit: `cf36e98` (Checkpoint 12)
- This checkpoint's commit hash: recorded after commit, see final session output.
- Working tree: clean after commit, verified before the combined Context Memory validation begins.
