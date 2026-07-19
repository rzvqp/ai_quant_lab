# Phase 7 — Checkpoint 12: Deterministic Context Retrieval

**Validation label: TARGETED VALIDATION PASSED.** Per the Checkpoints 10–13 batch's own validation
policy, only the `context_memory` package's own tests, `mypy --strict` scoped to the package, and
targeted coverage were run at this checkpoint's own close — the one combined-batch full-suite run
happens once, after Checkpoint 13.

## 1. Query Contract

`RetrievalQuery` (`ai_trader/context_memory/retrieval.py`, frozen dataclass): `context_snapshot` (the
current market context, need not itself be a stored `Observation`), `as_of_cutoff` (explicit, required —
never inferred from `context_snapshot.as_of`, so a caller must deliberately choose it), `edge_scope`
(optional non-empty tuple of `strategy_id`s narrowing which PRESENT-edge episodes are eligible),
`max_candidates` (optional cap on returned matches — never on the counts reported), and
`retrieval_policy_version` (defaults to this module's own `RETRIEVAL_POLICY_VERSION`). Every field is
validated in `__post_init__`. The current observation can never retrieve itself: this is not a
special-cased check but falls out structurally from the strict `end_as_of < as_of_cutoff` filter shared
with Checkpoint 11's own convention (proven by `test_as_of_cutoff_excludes_future_and_self`).

## 2. Result Contract

`RetrievalResult` reports every field the CEO's mission requires: `status` (§2), `query_context_id`,
`retrieval_policy_version`, `as_of_cutoff`, `index_max_as_of` (how far the index's own data actually
extends, distinct from the query's requested cutoff), `selected_relaxation_tier` (`None` when no tier
was ever reached — INCOMPATIBLE/DEGRADED_DATA/UNSUPPORTED_VERSION short-circuit before the ladder runs),
`raw_eligible_observation_count`, `eligible_episode_count` (post-quality-gate, post-cutoff,
pre-similarity — the denominator similarity was applied to), `returned_count`, `matches` (ordered),
`exclusion_reasons`, `limitations` (e.g. `max_candidates` truncation), and `no_sufficient_history_reason`
(populated only for `NO_ELIGIBLE_HISTORY`/`NO_SUFFICIENTLY_SIMILAR`). Six explicit statuses:
`SUCCESSFUL`, `NO_ELIGIBLE_HISTORY` (no episode passes the quality/cutoff/instrument gate at all, before
any similarity constraint), `NO_SUFFICIENTLY_SIMILAR` (eligible episodes existed but none matched even
at the relaxation floor), `INCOMPATIBLE` (query's `retrieval_policy_version` isn't one this module
supports), `DEGRADED_DATA` (the query's OWN snapshot is not `data_quality_state == OK` — garbage-in
refused before any retrieval work happens), `UNSUPPORTED_VERSION` (the query snapshot's own
`market_intelligence_schema_version` isn't the one this module was validated against).

## 3. Hierarchical Relaxation Ladder

Adopted the accepted Checkpoint 8 design doc's own §8 proposed order **verbatim, not re-derived**:
`session_state → expansion_state → liquidity_state → momentum_d1 → momentum_h4 → momentum_h1 →
momentum_m15 → trend_d1 → trend_h4 → trend_h1 → trend_m15`, relaxed one dimension at a time,
**cumulatively** (Tier N drops the first N ladder entries from the match requirement — never a sparse
"only the actually-differing dimensions" set; `test_trend_d1_requires_relaxing_every_earlier_ladder_entry_too`
proves this explicitly). The floor (never relaxed): `instrument` (a query-scope gate, not a ladder
entry — retrieval never crosses instruments, `test_never_crosses_instruments`) plus `structure_state`,
`volatility_regime`, `multi_timeframe_agreement` — the three dimensions the design doc identifies as
carrying the most information about contextual resemblance. No Euclidean/cosine/embedding/k-NN/
clustering/random/adaptive-optimization/hidden-scoring mechanism exists anywhere in this module — the
relaxation path itself IS the explanation (§5). `test_floor_reached_without_match_is_no_sufficiently_similar`
is the design doc's own §14 "synthetic false-neighbor" test: two contexts differing only on a FLOOR
dimension are proven to never match at any tier, confirming the order is enforced, not just documented.

## 4. Minimum-Sample Floor — Disclosed, Deliberately Unresolved Threshold

The design doc's own §17 leaves the exact numeric minimum-sample threshold unresolved ("a reasoned
starting point, not final"), and Checkpoint 12's own mission explicitly forbids inventing an arbitrary
one. **The smallest, non-arbitrary, conservative choice was made**: a tier is accepted as soon as it
yields *at least one* eligible episode — the smallest meaningful non-zero count, not a sufficiency
judgment. `SUCCESSFUL` here means "some evidence was found at this tier," nothing more; whether that
evidence is *enough* to act on is explicitly deferred to Checkpoint 13's own versioned sufficiency
policy, per the mission's own instruction ("leave sufficiency classification to Checkpoint 13").

## 5. Match Explanation

Every `RetrievalMatch` reports `matched_dimensions` (`instrument` plus every floor/not-yet-relaxed
ladder dimension at the tier reached), `relaxed_dimensions` (the ladder prefix dropped), and
`unavailable_dimensions` (always `()` — no `ContextSnapshot` field is ever `UNKNOWN`/missing in the
approved contract, a disclosed structural fact rather than an unimplemented feature). No opaque numeric
similarity score exists anywhere — `test_match_explanation_reports_matched_and_relaxed` confirms every
field is populated correctly for a one-dimension-relaxed match.

## 6. NO SUFFICIENT HISTORY as a First-Class Result

Two distinct, explicitly-reasoned outcomes cover this: `NO_ELIGIBLE_HISTORY` (nothing passed the basic
quality/cutoff/instrument/edge-scope gate — similarity was never even attempted) and
`NO_SUFFICIENTLY_SIMILAR` (eligible episodes existed but none matched at any tier, including the floor).
Both populate `no_sufficient_history_reason` with the exact cause. No fixed neighbor count is ever
forced; the ladder simply stops relaxing the moment ANY match is found, and returns one of these two
statuses only if the floor tier is fully exhausted with zero matches.

## 7. Deterministic Ordering

Matches are sorted by `(-episode.end_as_of, episode_id.value)` — most-recent-episode-first (recency
weighting, matching the design doc's own §8 default in-bucket tie-break), with the deterministic
`EpisodeId` as the final tie-break on an exact recency tie. `test_deterministic_recency_ordering` and
`test_retrieval_is_deterministic_across_repeated_calls` confirm both the ordering itself and that two
identical queries against the same index always return byte-identical match sequences. `volatility_rank`
decile tie-breaking (the design doc's own *secondary* tie-break, only applicable when recency ties
exactly) was **not implemented** — no such continuous rank field exists on the approved `ContextSnapshot`
contract, a disclosed limitation rather than an invented one.

## 8. Version Compatibility Policy

Two explicit, disclosed structural gates, both checked before any retrieval work begins:
`retrieval_policy_version` mismatch → `INCOMPATIBLE`; `market_intelligence_schema_version` mismatch on
the query's own snapshot → `UNSUPPORTED_VERSION`. Candidate episodes are additionally filtered to only
those whose own `market_intelligence_schema_version` matches the supported constant — never silently
mixed across versions (consistent with Checkpoint 11's own episode-boundary rule, which already splits
episodes on a version change).

## 9. Tests

198 tests total in the package (170 carried through Checkpoint 11 + 3 gap-closing tests already
committed at Checkpoint 11's own close = 173, + 25 new `test_retrieval.py` tests this checkpoint = 198
total passing). Categories covered: query contract validation (cutoff, edge_scope, max_candidates,
wrong-type snapshot, wrong-type policy version); Tier 0 exact match; single- and multi-dimension
relaxation stepping (including the cumulative-ladder proof); floor-reached synthetic false-neighbor;
no-eligible-history (empty index, wrong instrument only); temporal safety (cutoff excludes future AND
self, strict exclusivity); instrument-never-crossed; edge-scope filtering; `max_candidates` cap with
`limitations` disclosure; deterministic recency ordering and tie-break; result determinism across
repeated identical queries; `retrieval_policy_version` mismatch → INCOMPATIBLE;
`market_intelligence_schema_version` mismatch → UNSUPPORTED_VERSION; degraded query data quality →
DEGRADED_DATA; degraded candidate excluded via the Checkpoint 11 episode-collapsing quality gate; match
explanation field correctness; independent relaxation of trend vs. momentum dimensions; and a white-box
defense-in-depth test of the internal instrument-mismatch guard.

## 10. Targeted Coverage / mypy Result

```
coverage report (--source=ai_trader.context_memory, --omit tests/):
    __init__.py          10 stmts   0 miss   100%
    codec.py              62 stmts   0 miss   100%
    contracts.py         145 stmts   0 miss   100%
    enums.py               59 stmts   0 miss   100%
    episodes.py            85 stmts   0 miss   100%
    identities.py          28 stmts   0 miss   100%
    index.py               67 stmts   0 miss   100%
    repository.py         185 stmts   0 miss   100%
    retrieval.py          106 stmts   0 miss   100%
    validation.py          32 stmts   0 miss   100%
    TOTAL                 779 stmts   0 miss   100%

mypy --strict ai_trader/context_memory/ --exclude 'tests/'
    -> Success: no issues found in 10 source files (up from 9 at Checkpoint 11)
```

A first coverage run surfaced 3 missed lines in `retrieval.py` (the `context_snapshot`/
`retrieval_policy_version` wrong-type `__post_init__` guards, and the internal `_episode_matches`
instrument-mismatch branch — structurally unreachable through `retrieve()` alone since
`HistoricalIndex.episodes(instrument=...)` already filters by instrument upstream), closed with 3
additional targeted tests (two `__post_init__` type tests + one white-box test of `_episode_matches`
directly, matching Checkpoint 10's own precedent for defense-in-depth internal-guard testing) before
reaching the 100% above.

## 11. Deferred Aggregation / Decision Intelligence Integration (explicit confirmation, Checkpoint 12 §J)

**No contextual outcome statistics, win-rate/mean-result calculation, evidence-sufficiency
classification, uncertainty quantification, or Decision Intelligence integration was implemented
anywhere in this checkpoint.** `retrieve()` returns episodes and a similarity explanation only — it
never reads or reports `Outcome` data at all. `retrieval.py` imports only `contracts.py`, `enums.py`,
`episodes.py`, `identities.py`, `index.py`, `validation.py` (all within this package) plus the standard
library — re-confirmed by the existing static AST-based `test_import_independence.py`, which passed with
zero forbidden imports and zero `"harness"` string reference. `git status --porcelain` before staging
showed only the files listed below — nothing under `code/`, `results/`, `knowledge/`, or any other
`ai_trader/` package.

**Files changed this checkpoint**: New — `ai_trader/context_memory/retrieval.py`,
`ai_trader/context_memory/tests/test_retrieval.py`. Modified — `ai_trader/context_memory/__init__.py`
(new exports: `RETRIEVAL_POLICY_VERSION`, `RetrievalQuery`, `RetrievalMatch`, `RetrievalResult`,
`RetrievalStatus`, `retrieve`), `ai_trader/context_memory/tests/test_public_api.py` (expanded expected
export set).

## 12. Unresolved Design Decisions Carried Forward

- The design doc's own §8 relaxation order is adopted verbatim as "a reasoned starting point, not
  final" (§17) — not re-derived or re-justified here, exactly as instructed.
- No minimum-sample sufficiency threshold exists in this checkpoint (§4 above) — deferred to
  Checkpoint 13 by design.
- `volatility_rank`-decile secondary tie-break (design doc §8) not implemented — no such field exists on
  the approved contract.

## 13. Commit Hash / Branch / Working Tree Status

- Branch: `ai-trader-implementation`
- Parent commit: `9d273c4` (Checkpoint 11)
- This checkpoint's commit hash: recorded after commit, see final session output.
- Working tree: clean after commit, verified before Checkpoint 13 begins.
