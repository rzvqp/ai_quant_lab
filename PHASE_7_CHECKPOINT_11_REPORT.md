# Phase 7 — Checkpoint 11: Episode Collapsing and Historical Index

**Validation label: TARGETED VALIDATION PASSED.** Per the Checkpoints 10–13 batch's own validation
policy, only the `context_memory` package's own tests, `mypy --strict` scoped to the package, and
targeted coverage were run at this checkpoint's own close — the one combined-batch full-suite run
happens once, after Checkpoint 13.

## 1. Index Structure

`HistoricalIndex` (`ai_trader/context_memory/index.py`) is a **rebuildable, in-memory derived
structure**, never itself persisted to disk and never a second source of truth. It is constructed from
a `ContextMemoryRepository` (Checkpoint 10) and calls `rebuild()` in `__init__`; calling `rebuild()`
again at any later point re-derives every internal structure entirely from the repository's *current*
on-disk state, discarding whatever the index held before. It holds: the full set of `Observation`s
sorted by `(as_of, instrument, observation_id)`, a by-ID lookup, the derived tuple of `Episode`s
(via `episodes.py`), and a by-observation-ID map of `Outcome`s. Nothing in the index is ever written
back to the repository.

## 2. Indexed Dimensions

Every categorical field actually present on the approved `ContextSnapshot` contract: `instrument`,
`session_state`, `trend_m15/h1/h4/d1`, `structure_state`, `momentum_m15/h1/h4/d1`,
`volatility_regime`, `liquidity_state`, `expansion_state`, `multi_timeframe_agreement`,
`data_quality_state`; plus `as_of` (via the `as_of_before` cutoff) and PRESENT-edge `strategy_id`.
**No `timeframe` dimension is indexed** — no such field exists on `ContextSnapshot` (a Checkpoint 9
design choice, since Market Intelligence's own top-level snapshot carries no single timeframe either,
only the four per-sub-reading `trend_*`/`momentum_*` values already indexed individually). Outcome
`status`/horizon fields are reachable via `outcomes_for_observation()` but are not separate filter
kwargs on `observations_matching()` — Checkpoint 11 builds structural retrieval only, not outcome-aware
filtering, which belongs to Checkpoints 12/13.

## 3. Rebuild Rules

`rebuild()` performs a full, deterministic re-derivation: `sorted(repository.iter_observations(), ...)`,
then `collapse_into_episodes(...)` over that same sorted sequence, then a fresh pass over
`repository.iter_outcomes()`. Two independent `HistoricalIndex` instances built from the same repository
path always produce identical `statistics()` and identical `observations_matching()` results (proven by
`test_deterministic_index_rebuild` and `test_rebuild_equivalence_after_repository_reopen`, the latter
using two separate `ContextMemoryRepository` instances against the same directory). Indexing never
mutates the repository (`test_source_repository_remains_unchanged_after_indexing` checks
`count_observations()` and `verify_integrity().ok` before/after).

## 4. Episode Contract

`Episode` (`episodes.py`, frozen dataclass): `instrument`, `state_fingerprint`, `start_as_of`,
`end_as_of`, `representative_context_snapshot` (the run's FIRST observation's own snapshot —
Checkpoint 8 design §9.3's own choice: the episode's resolution point is the moment the context first
became this shape), `present_edges`, `observation_ids` (as_of-ordered by construction). `__post_init__`
enforces `end_as_of >= start_as_of`, non-empty `observation_ids`, and that `state_fingerprint` is
actually a `StateFingerprint` instance. `EpisodeId` is a deterministic SHA-256 hash of a canonical
payload (`_canonical_episode_payload`) covering every field above — same content always produces the
same ID (`test_episode_id_is_deterministic`), different content always differs
(`test_episode_id_differs_on_content`), and one fixed, independently-precomputed expected hash is
hardcoded in `test_episode_id_fixed_expected_value` to catch future accidental algorithm drift.

## 5. Episode-Boundary Rules

A boundary occurs between two `as_of`-consecutive observations for one instrument the moment ANY of:

- `state_fingerprint` changes — the fingerprint already folds in `instrument` and `session_state`, so
  instrument changes and session changes are automatically boundaries with **no separate rule needed**
  for either (verified explicitly: `test_instrument_isolation`, `test_session_change_splits_episode_via_fingerprint`);
- the PRESENT-edge set changes (`test_present_edge_set_change_splits_episode`) — Checkpoint 8 design
  §9.3's own explicit requirement, a strategy becoming/ceasing PRESENT always starts a new episode;
- `market_intelligence_schema_version` changes (`test_market_intelligence_schema_version_change_splits_episode`)
  — a disclosed, conservative choice: mixing evidence produced under two different upstream schema
  versions inside one episode could be semantically wrong even where categorical values happen to print
  identically;
- `data_quality_state != OK` — that observation is excluded from every episode entirely (neither starts
  nor extends one) and ends whatever episode preceded it
  (`test_degraded_data_quality_excludes_observation_and_splits`,
  `test_degraded_data_quality_as_final_observation_yields_no_trailing_empty_episode`).

**No maximum temporal gap is enforced.** `ContextSnapshot` carries no declared bar-interval/timeframe
field (a disclosed Checkpoint 9 design choice), so there is no non-arbitrary way to define "too large a
gap" without inventing an unvalidated threshold — forbidden by this whole project's own repeated
discipline ("do not select arbitrary thresholds without justification," Checkpoint 8 design §17).
Episode continuity is defined entirely by fingerprint/edge-set/version/quality equality across
as_of-consecutive observations, never by elapsed wall-clock time. This is verified as a **disclosed
limitation**, not an oversight: `test_no_gap_based_split_disclosed_limitation` confirms a ~116-day gap
with an identical fingerprint on both sides is currently treated as one continuous episode. Flagged as
an open question for a future checkpoint.

## 6. PRESENT-Edge-Set Policy

A change in the PRESENT-edge set (by `strategy_id`, order-independent — `sorted()` before hashing, see
`test_fingerprint_ignores_present_edge_order`) always splits the episode; it is folded directly into
`state_fingerprint` itself rather than tracked as a separate boundary condition, so the same equality
check that handles regime changes also handles edge-set changes with no duplicated logic.

## 7. As-Of-Time / Temporal-Safety Policy

Every observation-returning query method accepts an explicit `as_of_before` cutoff and excludes any
observation/episode whose own `as_of`/`end_as_of` is not strictly before it (`test_as_of_cutoff_is_strict_exclusive`
proves a cutoff *equal to* an observation's own `as_of` excludes it — the current query moment can never
retroactively become its own history). `outcomes_for_observation(observation_id, visible_as_of=...)`
implements the outcome-side half: an outcome is visible iff `resolution_as_of is None or
resolution_as_of <= visible_as_of` — a resolved-in-the-future outcome is entirely OMITTED at an earlier
cutoff, never re-labeled as a synthetic "still pending" projection
(`test_future_outcome_resolution_excluded_when_not_yet_visible` proves 0 results at a cutoff before
resolution and 1 result at/after it; `test_pending_outcome_always_visible_regardless_of_cutoff` confirms
a genuinely-unresolved outcome is always visible, since it never leaks a future numeric result — only
the already-true fact that resolution is still pending).

## 8. Raw vs. Episode Count Interpretation

`IndexStatistics` reports `raw_observation_count` (every stored `Observation`) separately from
`episode_count` (collapsed runs), plus `resolved_outcome_count`/`unresolved_outcome_count`.
`episode_count` is explicitly documented and tested as **a conservative effective-observation proxy,
never claimed to be a mathematically exact effective sample size** — that determination, if ever made,
is left to Checkpoint 13's own statistical-sufficiency layer. `test_episodes_query` demonstrates the
distinction directly: 3 raw observations (2 sharing one regime, 1 different) collapse to 2 episodes.

## 9. Tests

173 tests total in the package (170 carried forward through Checkpoint 10 unchanged + 3 gap-closing
tests added during this checkpoint's own coverage closure; 22 new in `test_episodes.py` + 17 new in
`test_index.py` = 39 new tests this checkpoint, 173 total passing). Every category from Checkpoint 11
§G/§H is covered: fingerprint exclusion of `as_of`/inclusion of every categorical dimension/order- and
confidence/quality-insensitivity; Episode contract validation (end<start, empty observation_ids,
wrong-type fingerprint, immutability); single-persistent-regime collapse; context-change split;
session-boundary policy (via fingerprint); instrument isolation; present-edge-set-change split;
schema-version-change split; degraded-data-quality exclusion+split (including the trailing-observation
edge case); disclosed no-gap-split limitation; caller-order independence; empty-input handling;
deterministic/differing/fixed-value episode IDs; deterministic index rebuild; rebuild-after-reopen
equivalence; rebuild-reflects-new-appends; exact single-filter and multi-filter intersection; PRESENT-edge
filtering; `as_of_before` cutoff exclusion (strict, exclusive); future-outcome-resolution exclusion;
pending-outcome always-visible; episode query + edge filter + instrument filter + as-of cutoff;
observation-by-ID lookup; and confirmation the underlying repository is never mutated by indexing.

## 10. Targeted Coverage / mypy Result

```
coverage report (--source=ai_trader.context_memory, --omit tests/):
    __init__.py          9 stmts   0 miss   100%
    codec.py             62 stmts   0 miss   100%
    contracts.py        145 stmts   0 miss   100%
    enums.py              59 stmts   0 miss   100%
    episodes.py           85 stmts   0 miss   100%
    identities.py         28 stmts   0 miss   100%
    index.py              67 stmts   0 miss   100%
    repository.py        185 stmts   0 miss   100%
    validation.py         32 stmts   0 miss   100%
    TOTAL                672 stmts   0 miss   100%

mypy --strict ai_trader/context_memory/ --exclude 'tests/'
    -> Success: no issues found in 9 source files (up from 7 at Checkpoint 10)
```

A first coverage run surfaced 3 missed lines (`episodes.py` — the `isinstance(state_fingerprint, ...)`
type-guard branch and the `_flush()` early-return-on-empty branch when a degraded observation is the
*last* item in the sequence; `index.py` — the `instrument`-mismatch `continue` branch in `episodes()`),
closed with 3 additional targeted tests
(`test_episode_rejects_non_state_fingerprint_type`,
`test_degraded_data_quality_as_final_observation_yields_no_trailing_empty_episode`,
`test_episodes_instrument_filter`) before reaching the 100% above.

## 11. Deferred Retrieval / Aggregation Logic (explicit confirmation, Checkpoint 11 §J)

**No similarity retrieval, relaxation ladder, contextual outcome statistics, evidence sufficiency
classification, or Decision Intelligence integration was implemented anywhere in this checkpoint.**
`observations_matching()`/`episodes()`/`episodes_with_edge()` perform plain, deterministic AND-filter
intersection over already-sorted candidate lists — never a ranked or scored result, never a k-NN or
distance computation. `index.py` and `episodes.py` import only `contracts.py`, `enums.py`,
`identities.py`, `repository.py`, `validation.py` (all within this package) plus the standard library —
re-confirmed by the existing static AST-based `test_import_independence.py` (Checkpoint 9, automatically
covers new files since it globs the whole package directory), which passed with zero forbidden imports
and zero `"harness"` string reference. `git status --porcelain` before staging showed only the files
listed below — nothing under `code/`, `results/`, `knowledge/`, or any other `ai_trader/` package.

**Files changed this checkpoint**: New — `ai_trader/context_memory/episodes.py`,
`ai_trader/context_memory/index.py`, `ai_trader/context_memory/tests/test_episodes.py`,
`ai_trader/context_memory/tests/test_index.py`. Modified — `ai_trader/context_memory/__init__.py` (new
exports: `StateFingerprint`, `EpisodeId`, `Episode`, `compute_state_fingerprint`, `compute_episode_id`,
`collapse_into_episodes`, `HistoricalIndex`, `IndexStatistics`),
`ai_trader/context_memory/tests/test_public_api.py` (expanded expected-export set).

- Branch: `ai-trader-implementation`
- Parent commit: `486aa61de180d8d0daca0b4bd14fe1938d5f566c` (Checkpoint 10)
- This checkpoint's commit hash: recorded after commit, see final session output.
- Working tree: clean after commit, verified before Checkpoint 12 begins.
