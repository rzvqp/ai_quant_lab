# Phase 7 Checkpoint 8 — Context Memory Architecture and Data Contract (DESIGN ONLY)

**Status: DESIGN REVIEW COMPLETED.** No production code was implemented, modified, or planned for
implementation in this checkpoint. Nothing here is authorized for construction — every proposal below,
including the "smallest safe implementation sequence" in §15, requires its own separate, explicit CEO
authorization before any code is written.

---

## 1. Executive Conclusion

The smallest useful Context Memory system is **an append-only, immutable log of Context Snapshots and
Edge Outcomes, retrieved by a fixed-priority hierarchical categorical filter (never a weighted or
learned model), producing a Contextual Evidence Report with a fully-derived, non-opaque sufficiency
status** — never a decision, never a score fed silently into one.

Three design choices carry the whole architecture and are stated up front because everything else
follows from them:

1. **Similarity must be built from Market Intelligence's own already-discretized regime labels**
   (`TrendDirection`, `StructureState`, `MomentumState`, `VolatilityRegime`, `LiquidityState`,
   `ExpansionState`, `AgreementLevel`) — never from raw continuous features (price, ATR, RSI, volume).
   Continuous features are non-stationary over a 3.6-year dataset and invite exactly the "high-
   dimensional false similarity" the CEO's directive warns against. The categorical state vector is
   low-dimensional, already validated by Checkpoints 5–6, and every dimension is independently
   explainable by construction.
2. **Persistent regimes must be collapsed into episodes before they are counted as evidence.** A
   15-minute base timeframe under a sticky multi-bar regime (e.g. a multi-hour STRONG uptrend) would
   otherwise produce dozens of near-identical, highly autocorrelated "observations" from a single market
   event — silently inflating apparent sample size and confidence. This is the single most important
   mechanism in this design and is treated as such throughout (§3, §9.3, §12).
3. **Outcome measurement is decoupled from Shadow Evidence by default.** Context Memory can compute a
   self-contained, strategy-agnostic forward-return outcome directly from the same lookahead-safe bars
   Market Intelligence already reads — zero external coupling, zero new dependency. A richer,
   strategy-native outcome (real entry/exit, real R) MAY later be supplied by a caller who already has
   Shadow Evidence data, using the same "caller-adapts-into-a-local-type" pattern Decision Intelligence
   already established for `ResearchStats` (Checkpoint 7) — Context Memory itself never imports
   `ai_trader.shadow_evidence`.

**Final recommendation (§16): APPROVE the architecture direction, with staged re-authorization.** The
design is sound and internally consistent with this repository's own established conventions
(lookahead-safety, append-only-plus-derived-index, local-type caller-adaptation, "never fabricate,"
disclosed IMPLEMENTATION CHOICE comments). It is explicitly NOT a blanket approval to build all of it —
§15 proposes seven small, independently-gated checkpoints, and only the first (immutable contracts and
IDs) is realistically ready to be proposed for authorization next; every later checkpoint depends on
evidence this repository does not yet have (a live, running system producing bars over time) and on
open questions in §17 that should be revisited before implementation, not resolved by assumption now.

---

## 2. Current Architecture Boundary

**Confirmed official baseline** (re-verified live for this checkpoint, not assumed):
- `git log -1` → `6fb07ad447de59a3cdd429fe4c3319b6abf783c2` ("Official Project Save: synchronize all
  documentation after Phase 7 Checkpoint 7"), branch `ai-trader-implementation`, working tree clean.
- Market Intelligence (`ai_trader/market_intelligence/`), Edge Intelligence
  (`ai_trader/edge_intelligence/`), and Decision Intelligence v1 (`ai_trader/decision_intelligence/`)
  are all CLOSED and ACCEPTED, per `PROJECT_STATE_v2.md` §8.1/§8.2/§8.4.
- None of the three is wired into `harness.py` or any execution path.

**Target future pipeline** (this checkpoint designs the third box only — the box itself is not built):

```
Market Intelligence -> Edge Intelligence -> Context Memory -> Decision Intelligence v2 -> Risk -> Execution
```

Decision Intelligence remains the ONLY component that ever produces a final edge recommendation or NO
TRADE. Context Memory's public output, end to end, is historical evidence — never a trading primitive.

**This checkpoint's own scope discipline, verified before writing this report**: `git status --porcelain
-- ai_trader/` was checked and is empty; no file under `ai_trader/`, `code/`, `results/`, or `knowledge/`
was read for any purpose other than inspecting already-public contracts (Market Intelligence, Edge
Intelligence, Decision Intelligence, `shadow_evidence.types`, `strategy_health.types`,
`strategy_manager.contract`, `market_scanner.types`) to ground this design in real field names rather
than invented ones. No import boundary was crossed; no test was run.

---

## 3. Context Snapshot Contract

### 3.1 Design principle

A Context Snapshot is a **pure, immutable record of what Market Intelligence already computed** at one
`as_of`/`symbol` — it adds no new computation, no new indicator, no new threshold. Every field is either
copied verbatim from an existing `MarketIntelligenceSnapshot` field or is Context-Memory-owned identity/
quality metadata. Fields fall into three classes, and the class determines whether a field participates
in similarity matching at all:

- **Similarity dimensions** — categorical or ordinal-bucketed, stable, low-cardinality. These are the
  ONLY fields the retrieval mechanism (§6–§8) ever compares.
- **Descriptive metadata** — continuous or free-form values kept for human explanation and diagnostics,
  never used to compute similarity.
  **Quality/identity fields** — govern eligibility (is this snapshot even usable as evidence?),
  freshness, and reproducibility; never describe "what the market looked like."

### 3.2 Field-by-field evaluation

| Field | Source | Class | Type | Normalization | Leakage risk | Stable across versions? | Decision |
|---|---|---|---|---|---|---|---|
| `symbol` | `MarketIntelligenceSnapshot.symbol` | Quality/identity | categorical | none | none | yes | **INCLUDE** |
| `as_of` | `MarketIntelligenceSnapshot.as_of` | Quality/identity | continuous (unix time) | none | HIGH if used as a similarity feature (time never repeats — see below) | yes | **INCLUDE, excluded from similarity** |
| `trend_direction[tf]` for tf in {M15,H1,H4,D1} | `snapshot.trend[tf].direction` (`TrendDirection`) | Similarity | categorical (4 values + UNKNOWN) | none needed | none — already lookahead-safe (§9.1) | Stable only while `TrendDirection`'s enum values are unchanged; a new member would require a new `market_intelligence_schema_version` (§5) | **INCLUDE** |
| `trend_strength[M15]` | `snapshot.trend["M15"].strength` | Descriptive | continuous, `float\|None` | none stored (raw); NOT bucketed for v1 | none | fragile — depends on `_FLAT_STRENGTH_THRESHOLD`, an undisclosed-tunable internal to `trend.py` | **INCLUDE as descriptive only, EXCLUDE from similarity** (a continuous, single-timeframe-only field would asymmetrically weight M15 vs. the other three timeframes, which have no strength value at all — comparing across a field only half the timeframes populate is a coherence risk, not just a leakage one) |
| `structure_state[M15]` | `snapshot.structure.state` (`StructureState`) | Similarity | categorical (6 values incl. UNKNOWN) | none | none | same caveat as trend | **INCLUDE** |
| `momentum_state[tf]` for tf in {M15,H1,H4,D1} | `snapshot.momentum[tf].state` (`MomentumState`) | Similarity | categorical (4 values) | none | none | same caveat | **INCLUDE** |
| `momentum_rsi[M15]` | `snapshot.momentum["M15"].rsi` | Descriptive | continuous, `float\|None` | none stored | none | stable formula, but a raw RSI value from 2023 and one from 2026 are not directly comparable without knowing the surrounding regime, which the categorical state already encodes | **EXCLUDE even as descriptive in v1** (adds no information the categorical `momentum_state` doesn't already carry for this design's own purposes; can be added later without a schema break since it changes nothing about identity) |
| `volatility_regime` | `snapshot.volatility.regime` (`VolatilityRegime`) | Similarity | categorical (5 values) | none | none | same caveat | **INCLUDE** |
| `volatility_rank` | `snapshot.volatility.volatility_rank` | Descriptive | continuous `float\|None`, 0–1 (Parkinson percentile rank) | already normalized (percentile) by `market_scanner` | none | depends on `market_scanner`'s own rolling window, external to this design | **INCLUDE as descriptive only** — already normalized, genuinely useful for later refinement (e.g. an ordinal-bucketed secondary tie-break, §8), but NOT a v1 similarity dimension (adding a second, correlated volatility signal alongside `volatility_regime` risks double-counting one underlying phenomenon as if it were two independent dimensions) |
| `liquidity_state` | `snapshot.liquidity.state` (`LiquidityState`) | Similarity | categorical (4 values) | none | none | same caveat | **INCLUDE** |
| `expansion_state` | `snapshot.expansion.state` (`ExpansionState`) | Similarity | categorical (4 values) | none | none | same caveat | **INCLUDE** |
| `session_name` | `snapshot.session.session_name` | Similarity | categorical, `str\|None` | none | none | depends on `market_scanner`'s own session feature vocabulary | **INCLUDE** |
| `inside_opening_range` / `above_session_vwap` | `snapshot.session.*` | Descriptive | boolean/`None` | none | none | stable | **EXCLUDE from v1** — genuinely useful session-microstructure signals, but adding two more binary similarity dimensions on top of nine categorical ones widens the combinatorial state space further, worsening the "too few exact matches" problem §6 already flags as the dominant risk of exact matching; deferred to a later refinement once the base design's own retrieval yield is measured against real data |
| `multi_timeframe_agreement.level` | `snapshot.multi_timeframe_agreement.level` (`AgreementLevel`) | Similarity | categorical (4 values) | none | none | same caveat | **INCLUDE** |
| `multi_timeframe_agreement.agreement_score` | same field, `.agreement_score` | Descriptive | continuous `float\|None`, 0–1 | already normalized | none | derived, same caveat as trend_strength | **EXCLUDE from similarity** — `level` already discretizes this |
| `context_confidence.score` | `snapshot.confidence.score` | Quality/identity | continuous `float\|None`, 0–1 | already normalized | none directly, but see below | derived from a disclosed 3-component formula (`confidence.py`) — the formula itself could change | **INCLUDE as an eligibility/quality gate, never a similarity dimension** — confidence describes how much to TRUST this reading of the market, not what the market itself looked like; conflating the two would let two markets that looked nothing alike "match" only because both happened to have equally low confidence |
| `data_quality_level` | `context_access.data_quality_level(context)` (`DataQualityLevel`) | Quality/identity | categorical (4 values) | none | none | stable | **INCLUDE as an eligibility gate** — a snapshot with `INSUFFICIENT`/`STALE` data quality is never eligible to be stored as evidence at all (§9.4) |
| `present_edge_ids` | Edge Intelligence's `EdgeIntelligenceSnapshot.readings` where `state is PRESENT` | *(belongs to Observation, not Context Snapshot — see §4.1)* | — | — | — | — | **NOT a Context Snapshot field** |

### 3.3 The resulting v1 Context Snapshot similarity vector

Nine categorical dimensions, all sourced verbatim from already-computed, already-tested Market
Intelligence fields:

```
(trend_direction_M15, trend_direction_H1, trend_direction_H4, trend_direction_D1,
 structure_state, momentum_state_M15, momentum_state_H1, momentum_state_H4, momentum_state_D1,
 volatility_regime, liquidity_state, expansion_state, session_name, multi_timeframe_agreement_level)
```

(14 dimensions total once momentum is counted per-timeframe — the table above groups "trend" and
"momentum" as one row each per timeframe for readability, but every timeframe's own value is a
separate, independent dimension.) Plus quality/identity metadata: `symbol`, `as_of`, `context_confidence
.score`, `data_quality_level`. Plus descriptive-only metadata kept for explanation but never compared:
`trend_strength_M15`, `volatility_rank`.

---

## 4. Outcome and Evidence Contract

### 4.1 What constitutes an Observation

An **Observation** = one Context Snapshot (§3) **plus** the exact, disclosed set of `strategy_id`s Edge
Intelligence classified `PRESENT` at that same `as_of`/`symbol` (`EdgeIntelligenceSnapshot.readings`
filtered to `EdgeState.PRESENT`, per Checkpoint 6's own established scope — "evaluate every PRESENT
edge"). Context Snapshot and Observation are kept as two distinct, linked records rather than one
merged record, deliberately: the Context Snapshot's own identity depends only on Market Intelligence's
schema; the Observation's own identity additionally depends on Edge Intelligence's schema and the
Strategy Library's own state at that moment. Versioning the two independently (§5) means a future Market
Intelligence change and a future Edge Intelligence change can each be reasoned about without conflating
their blast radius.

An Observation with zero PRESENT edges is still a valid, storable Observation (Edge Intelligence's own
"if zero are present, report zero" precedent) — it usefully records "the market looked like X and NO
edge was present," which is itself evidence for a future NO-TRADE base rate, not a null result to
discard.

### 4.2 What constitutes an Outcome

An **Outcome** is the resolved (or not-yet-resolved) result of ONE `(observation, strategy_id, horizon)`
triple. One Observation with three PRESENT edges over two horizons produces up to six Outcome rows —
Outcomes are always plural per Observation, never one Outcome per Observation.

### 4.3 Outcome horizons

Two DISTINCT horizon families, deliberately kept separate and separately labeled so they are never
silently averaged together:

1. **Price-only forward horizons (default, self-contained, zero external coupling)** — a small, fixed
   set of forward bar-counts on the base timeframe (e.g. +20 and +80 M15 bars — illustrative only, the
   exact counts are an open question, §17), computed directly from the same lookahead-safe bars Market
   Intelligence already reads. Requires no external input at all; Context Memory can compute this
   entirely from its own stored `as_of` plus a read of historical bars.
2. **Strategy-native horizons (optional, caller-supplied enrichment)** — the REAL entry-to-exit window a
   specific strategy's own Shadow Evidence position actually used (`TradeRecord.entry_as_of` /
   `.exit_as_of`, `.pnl_r`, `.holding_bars`). Never computed by Context Memory itself; a caller who
   already has Shadow Evidence data adapts it into a local, minimal `RealizedOutcome` type Context Memory
   defines (mirroring `decision_intelligence.types.ResearchStats`'s own established pattern of a LOCAL
   echo type rather than an import of the producing package's own type) — `ai_trader.shadow_evidence` is
   never imported by Context Memory itself.

### 4.4 Return / R-multiple representation

The two horizon families use two DIFFERENT, separately labeled return conventions, precisely because
they mean different things:

- Price-only horizons have no strategy-defined stop-loss, so there is no true "R" to divide by. Report
  the forward return **normalized by that observation's own `volatility.atr`** (an ATR-normalized
  return, e.g. `(close[as_of + horizon] - close[as_of]) / atr[as_of]`, signed by the edge's own declared
  `execution.long_short` direction where meaningful) — a standardized, comparable, strategy-agnostic
  magnitude, explicitly labeled `atr_normalized_return`, never called "R" to avoid the CEO's own
  documented, project-wide confusion risk (Research Lab defect D2 — "R-normalization / tiny-stop
  explosion" — a directly analogous, already-experienced failure mode this design must not repeat by
  reusing the same ambiguous vocabulary for a different quantity).
- Strategy-native horizons report the REAL `pnl_r` Shadow Evidence's own frozen `RiskManager`/
  `ExecutionSimulator` computed — genuine R, inheriting whatever cost model that simulator used
  (disclosed via a `cost_model_ref` field, §4.8).

Both report `gross_pnl`/`net_pnl` is NOT computed by Context Memory for the price-only horizon (no
position size, no cost model exists at that layer) — only the normalized magnitude.

### 4.5 Unresolved observations

An Outcome whose horizon has not yet elapsed as of the current evaluation time (`observation.as_of +
horizon > now`) is `status = PENDING`, never a fabricated 0 or an omitted row. Retrieval (§6–§8) MUST
exclude `PENDING` outcomes from any aggregated statistic — a still-open outcome has an unknown sign and
including it either way would bias the aggregate in an undisclosed direction.

### 4.6 Duplicate-event prevention

Solved structurally, not by a dedup pass after the fact: see §9.3 (episode collapsing). The Context
Snapshot's own deterministic `state_fingerprint` (§5) is the key episode-boundary detector — a new
episode begins exactly when the fingerprint (or the PRESENT-edge set) changes from the immediately
preceding bar's own Observation.

### 4.7 Multiple edges in the same context

Recorded as described in §4.1–§4.2: one Observation carries the full PRESENT set; Outcome rows fan out
one-per-edge-per-horizon. Aggregation (a future checkpoint, §15) always groups by `strategy_id` first —
"how has S7 performed after contexts like this" is always a well-formed, single-edge question even when
the historical Observation itself had other edges PRESENT simultaneously.

### 4.8 Edge version, contract version, cost model, and missing evidence

- **Edge/contract version**: every Observation stores `contract_content_hash` (reusing
  `strategy_manager.loader`'s own existing `_content_hash()` — a SHA-256 of the raw `strategy.json`
  bytes, already computed today for change-detection in `reload()`) and `contract_version`
  (`Contract.identity.version`) for every PRESENT edge, captured AT OBSERVATION TIME, never updated
  retroactively.
- **Cost model identification**: price-only horizons are tagged `cost_model_ref = "GROSS_NO_COSTS"` (a
  disclosed, versioned constant, never silently implied); strategy-native horizons are tagged with
  whatever cost/slippage identifier the supplying Shadow Evidence run itself used (an open question for
  the caller-adapter contract to define precisely, §17).
- **Missing evidence**: every optional field is `None`, never a sentinel number, never a silently-omitted
  row — the same "never fabricate" convention `WindowMetrics`, `MarketIntelligenceSnapshot`, and
  `EdgeIntelligenceSnapshot` all already follow.

### 4.9 No live learning loop

This checkpoint designs a passive, queryable historical record. Nothing here re-trains, re-weights, or
adapts any threshold from outcomes. That distinction is structural, not just a stated intention: the
similarity mechanism (§6–§8) reads only the Context Snapshot's own fields, never an Outcome — outcomes
are aggregated only AFTER a set of similar historical contexts has already been retrieved by a rule that
never looked at any outcome to decide what counted as "similar."

---

## 5. Storage Architecture

### 5.1 Alternatives compared

| Option | Fit |
|---|---|
| Append-only event store | Matches the CEO's own "source evidence must remain immutable and reproducible" requirement directly; matches this repository's own established precedent (Shadow Evidence's `opportunities`/`rejections`/`trade_legs` lists are the append-only source of truth; `aggregation.py` is a pure, rebuildable function over them — Checkpoint 2). **Recommended as the source-of-truth layer.** |
| Normalized (relational) records | A reasonable IMPLEMENTATION of an append-only store (e.g. one table per record type with foreign keys) — not a competing architecture, a compatible physical layout choice, deferred to implementation (§15). |
| Immutable context snapshots | This IS the append-only event store's own content, not a separate option — folded into the recommendation above. |
| Derived indexes | Necessary for retrieval to be fast at scale; MUST be rebuildable from the append-only log alone (a required test, §14.9) — never hand-edited, never the only copy of anything. **Recommended as a second, explicitly non-authoritative layer.** |
| Materialized contextual aggregates | Same treatment as derived indexes — a cache of `(state_fingerprint, strategy_id) -> outcome statistics`, rebuildable, versioned by `similarity_model_version` + `outcome_definition_version` so a version bump never silently mixes stale and fresh aggregates. |

### 5.2 Recommended architecture

**Two layers, one direction of dependency:**

```
Layer 1 (authoritative, append-only, immutable):
  ContextSnapshot records
  Observation records
  Outcome records (price-only + strategy-native)
        |
        | (pure, deterministic, rebuildable functions — no new information created)
        v
Layer 2 (derived, rebuildable, disposable):
  state_fingerprint -> [observation_id, ...]        (retrieval index)
  (state_fingerprint, strategy_id, horizon) -> outcome aggregate statistics
```

Layer 2 can be deleted and regenerated from Layer 1 at any time with an identical result — this is the
"rebuild equivalence" property the CEO's own testing-plan requirement (§14.9) exists to prove, and it is
the same discipline already proven in this repository by `shadow_evidence/aggregation.py`'s own pure
functions over already-recorded lists (Checkpoint 2's own precedent, directly reusable as an
architectural template, not just an analogy).

---

## 6. Context Identity and Versioning

| Identity | Deterministic rule |
|---|---|
| `state_fingerprint` | A stable hash (e.g. SHA-256 of a canonically-ordered, canonically-serialized tuple) of ONLY the similarity-dimension fields from §3.3 — deliberately excludes `as_of` and `symbol`, so two Observations at different times with an identical market "shape" produce the SAME fingerprint (this is the whole point: the fingerprint is the retrieval key). |
| `context_snapshot_id` | A hash of `(symbol, as_of, state_fingerprint, market_intelligence_schema_version)` — unique per snapshot instance, distinct from `state_fingerprint` which is intentionally NOT unique per instance. |
| `observation_id` | A hash of `(context_snapshot_id, sorted(present_edge_ids), edge_intelligence_schema_version)`. |
| `edge_evidence_id` (Outcome row identity) | A hash of `(observation_id, strategy_id, horizon_label, outcome_definition_version)`. |
| `strategy_version` | `Contract.identity.version` + `contract_content_hash` (§4.8) — both stored; the content hash is the ground truth (catches an un-bumped `version` field), the declared version is the human-readable label. |
| `market_intelligence_schema_version` | A Context-Memory-OWNED constant (e.g. `"mi-v1"`), NOT read from `MarketIntelligenceSnapshot` itself (that type carries no self-declared version today — an explicit gap, §17, Q8). Context Memory bumps this constant by hand whenever a future change to Market Intelligence's own field shape is detected during integration, never automatically. |
| `edge_intelligence_schema_version` | Same treatment, a second Context-Memory-owned constant (e.g. `"ei-v1"`), independent of the Market Intelligence one — Edge Intelligence's own evidence-dimension set (Checkpoint 6 §3) could change independently. |
| `similarity_model_version` | A Context-Memory-owned constant identifying the exact hierarchical-filter tier definitions and relaxation order (§8) that produced a given derived index/aggregate. Retrieval refuses to mix results computed under two different `similarity_model_version`s in one report — a version bump requires a full Layer 2 rebuild, never an in-place partial update. |
| `outcome_definition_version` | A separate constant covering the horizon set, the ATR-normalization convention, and the cost-model labeling scheme (§4) — versioned independently of the similarity model, since these can evolve on different schedules. |

**Why evidence stays interpretable after contracts or strategies evolve**: every identity above is
computed and frozen AT OBSERVATION TIME and never recomputed retroactively. When a strategy's contract
changes, OLD Observations keep pointing at the OLD `contract_content_hash` — they remain truthfully
labeled "evidence about strategy version X," not silently reinterpreted as evidence about the current
version. A future retrieval can choose to (a) restrict to the CURRENT contract version only (likely
sparse for a strategy that changed recently — an honest, disclosed limitation, not hidden), or (b)
include cross-version evidence with an explicit, visible warning in the Contextual Evidence Report
(§10) — but it may NEVER silently pool across versions as if nothing changed (failure mode, §12).

---

## 7. Similarity Architecture Comparison

| Approach | Deterministic? | Explainable? | Resistant to arbitrary weights? | Resistant to high-dim false similarity? | Can return NO SUFFICIENT HISTORY? | Verdict |
|---|---|---|---|---|---|---|
| 1. Exact categorical matching | Yes | Yes (trivially — an exact match on N dimensions) | Yes (no weights exist) | Yes | Yes, and often — the combinatorial state space (§3.3: up to 4×4×6×4×4×5×4×4×N-sessions×4 ≈ tens of thousands of theoretical combinations) means exact matches will frequently be rare or absent | Excellent primary FILTER; too brittle alone |
| 2. Weighted feature distance | Yes (given fixed weights) | Only as explainable as the weights are justified | **NO** — this is precisely what the CEO's directive forbids unless the weights are principled and disclosed, and any principled derivation of weights from historical outcome data reintroduces exactly the "live learning loop" §4.9 explicitly rules out | No — continuous-feature distance is the classic vector for high-dimensional false similarity | Only via an arbitrary distance threshold, itself another tunable | **REJECTED** as the primary v1 mechanism |
| 3. Hierarchical filtering then ranking | Yes | Yes — the relaxation path itself IS the explanation | Yes (a fixed, disclosed priority order, not a fitted weight vector) | Yes (relaxation only ever removes ONE categorical constraint at a time, in a fixed order — never blends continuous distances) | Yes, cleanly, when even the most relaxed tier fails the minimum-sample floor (§9) | **Recommended core mechanism** |
| 4. Regime-bucket matching | Yes | Yes | Yes | Yes | Yes | Effectively the same idea as #3, formalized as the top (strictest) tier — not a separate alternative, folded into the recommendation |
| 5. Nearest-neighbor retrieval | Only given a fixed seed/tie-break, and even then the RESULT is sensitive to feature scaling choices that are themselves a hidden weighting decision | Poor — "these are your 10 nearest neighbors" does not explain WHY without exposing per-dimension contributions, which reintroduces weights | No | **No** — the exact CEO-named risk ("high-dimensional false similarity") | Only via a distance threshold, another tunable | **REJECTED** |
| 6. Hybrid deterministic retrieval | Yes | Yes | Yes, if the "hybrid" part is a small, FIXED, disclosed tie-break over already-bucketed ordinal features (e.g. `volatility_rank` decile) rather than a learned blend | Yes, under the same condition | Yes | **This is what "hierarchical filtering + regime-bucket matching" (options 3+4) already is** when a disclosed, non-learned secondary tie-break is added for in-bucket ranking — recommended as the full design, not a distinct sixth option |

---

## 8. Recommended Deterministic Retrieval Design

A fixed-priority **relaxation ladder** over the nine categorical similarity dimensions (§3.3), applied
in a single disclosed order, never re-ordered per query:

**Tier 0 (strictest — exact match on all 14 dimensions).** If the number of matching, resolved,
eligible Observations (§9.4) meets the minimum-sample floor (§9), stop here.

**Tier 1.** Relax the LEAST information-bearing dimension first — proposed order (open to revision,
§17): drop `session_name`, then `expansion_state`, then `liquidity_state`, then higher-timeframe
`momentum_state` (D1, then H4, then H1 — M15 momentum is kept longest since it is closest to the
decision timeframe), then higher-timeframe `trend_direction` (same order), retaining `structure_state`,
`volatility_regime`, and `multi_timeframe_agreement_level` the longest (these three carry the most
information about whether the CURRENT setup resembles a past one at all). Each relaxation step is one
dimension dropped from the match requirement, re-checked against the minimum-sample floor before
relaxing further.

**Tier N (floor).** If even the maximally-relaxed tier this design permits (never "relax everything" —
a hard floor on how many dimensions may ever be dropped, itself disclosed and versioned) fails to reach
the minimum sample size, retrieval returns **NO SUFFICIENT HISTORY** with the exact tier and dimension
counts reached — never a best-effort, low-confidence match presented as if it were adequate.

**In-bucket ranking** (once a tier's candidate set is fixed): a small, fixed, disclosed tie-break —
recency-weighted (more recent episodes ranked first, since regime character can drift, §12) as the
default; `volatility_rank` decile distance as a secondary tie-break ONLY if recency ties exactly. No
weight is ever fitted to outcome data.

**Similarity explanation** (required per query, per the CEO's own directive): for every retrieved
historical context, report exactly which of the 14 dimensions matched, which were relaxed (and in what
tier), and which were `UNKNOWN`/unavailable in either the query or the historical record — never a bare
"here are your matches."

---

## 9. Temporal Safety and Leakage Controls

### 9.1 Inherited lookahead safety

Market Intelligence's own inputs are already lookahead-safe by construction —
`ai_trader.strategy_runtime.context_access`'s own documented guarantee: every value comes from
`select_lookahead_safe_bars`-produced data for the context's own `as_of`, with "no way to peek ahead
without bypassing this module entirely." Context Memory inherits this guarantee FOR FREE as long as
every Context Snapshot is built exclusively from a real `MarketContext`/`MarketIntelligenceSnapshot`
produced through that same path — a hard, disclosed invariant, never bypassed to backfill history faster.

### 9.2 The hard as-of cutoff rule

For a query issued "as of" time `T`: an Outcome row is eligible evidence if and only if its
`resolution_as_of` (`observation.as_of + horizon`) is `<= T`. This is the single rule that prevents
future-data leakage into retrieval, and it is enforced as a hard filter inside the retrieval mechanism
itself (§8), never left to a caller's discretion. The exact value of `T` used is always reported back as
the **memory cutoff timestamp** (§10) — a self-describing, auditable boundary on every report.

### 9.3 Overlapping/duplicate-sample prevention (episode collapsing)

A maximal contiguous run of consecutive base-timeframe bars sharing the SAME `state_fingerprint` AND the
SAME `present_edge_ids` set is one **episode**, not N independent Observations. The episode's own
"resolution point" for outcome measurement is the FIRST bar of the run (the moment the context first
became this shape) — later bars inside the same episode are still stored as individual Observations
(nothing is deleted, the append-only log stays complete), but evidence aggregation and sample-size
counting (§9, §12) operate on episodes, never on raw Observation rows, specifically to prevent a single
multi-hour regime from being double-, triple-, or dozens-of-times counted as if it were that many
independent pieces of evidence.

### 9.4 Sealed holdout respected

This project maintains a standing, CEO-gated SEALED terminal holdout (2025-10-23 09:15 UTC →
2026-07-13 06:00 UTC, the last 20% of the M15 series) that "no phase to date has opened"
(`PROJECT_STATE_v2.md` §1). Context Memory MUST NOT build ContextSnapshot/Observation/Outcome records
from bars inside that window until the CEO explicitly opens it for this purpose — the exact same
discipline already governing every prior AI Trader phase, inherited without modification, not
reinvented.

### 9.5 No self-referential evidence

Because retrieval only ever considers evidence with `resolution_as_of <= T` (§9.2), and the CURRENT
query's own observation has, by definition, not yet resolved at time `T`, the current context can never
appear in its own evidence set — this falls out of the as-of rule structurally rather than needing a
separate special-case check, which is itself a robustness property (nothing to forget to implement).

### 9.6 Train/validation/evaluation contamination

Deferred as an explicit open question (§17) rather than resolved here: this concern applies most
directly to a FUTURE statistical validation of Context Memory itself (§15's own falsification study),
not to the retrieval mechanism's own runtime behavior, which the as-of rule already protects. A future
validation checkpoint should define its own held-out evaluation window, analogous to but not necessarily
identical to the Research Lab's own research/validation/holdout split.

---

## 10. Contextual Evidence Output Contract

Every field the CEO's directive lists, with its source:

| Field | Meaning |
|---|---|
| `query_context_id` | The querying `context_snapshot_id` (or a fresh one built for an as-yet-unstored live query). |
| `retrieval_timestamp` | When this report was produced (a Context-Memory-internal audit field, distinct from `as_of`). |
| `memory_cutoff_timestamp` | The exact `T` used for the §9.2 as-of filter. |
| `total_eligible_historical_contexts` | Count of Observations passing the quality gate (§3.2's `data_quality_level`/`confidence.score` eligibility) and the as-of cutoff, before any similarity filtering — the denominator similarity was applied to. |
| `similar_contexts_retrieved` | Count of episodes (not raw Observations, §9.3) matched at the tier retrieval stopped at. |
| `retrieval_tier_reached` | Which tier of the relaxation ladder (§8) produced the result, and the exact dimensions relaxed. |
| `similarity_quality` | A qualitative label derived from the tier reached (Tier 0 = HIGH, deeper relaxation = progressively lower) — always DERIVED from `retrieval_tier_reached`, never a separately-set opaque value. |
| `evidence_sufficiency` | The controlled-vocabulary status, §10.1. |
| `evidence_freshness` | Age of the most recent contributing episode relative to `memory_cutoff_timestamp`, plus the age of the OLDEST — both reported, since a wide age range is itself informative (regime drift risk, §12). |
| `evidence_consistency` | A measure of sign/direction agreement across contributing episodes (§12's "contradictory subgroups" check) — e.g. the fraction of episodes whose outcome sign agrees with the pooled average. |
| `per_edge_contextual_statistics` | For each `strategy_id` that was PRESENT in at least one retrieved episode: episode count, resolved-outcome count, mean/median `atr_normalized_return` (and, if available, real `pnl_r`), a bootstrap confidence interval (§13), win-rate-equivalent (fraction of positive-sign outcomes). |
| `uncertainty_and_limitations` | Free-text, structured disclosure list — e.g. "only 4 independent episodes," "outcome definition version mismatch excluded N candidate episodes," "sealed holdout excludes the most recent 20% of history entirely." |
| `no_sufficient_history_reason` | Populated (only) when `evidence_sufficiency = UNAVAILABLE` — the exact tier/threshold that was not met. |

### 10.1 Evidence sufficiency: recommended controlled vocabulary

The CEO's own five proposed names (`SUFFICIENT`, `LIMITED`, `CONTRADICTORY`, `STALE`, `UNAVAILABLE`) are
adopted, with one structural change: **they are not five independent flags a report can carry
simultaneously — they are a single, priority-ordered status**, derived deterministically (never manually
set) by evaluating, in this fixed order, the first condition that applies:

1. `UNAVAILABLE` — retrieval reached the relaxation floor without meeting the minimum-sample threshold
   (§9). (`no_sufficient_history_reason` is populated.)
2. `STALE` — enough episodes exist, but the most recent contributing episode is older than a disclosed
   staleness threshold (an open numeric question, §17) — the market's own character may have drifted
   since.
3. `CONTRADICTORY` — enough recent episodes exist, but `evidence_consistency` (§10) falls below a
   disclosed agreement threshold, OR the confidence interval (§13) straddles zero while a naive point
   estimate looks decisively signed — reusing this project's own already-established "UNRESOLVED if the
   CI straddles" convention (`PROJECT_AUDIT.md` §A0) rather than inventing a new rule.
4. `LIMITED` — evidence exists, is recent, and is directionally consistent, but the episode count is
   below a stronger "high-confidence" threshold, above the bare minimum — real evidence, held to a
   visibly lower confidence than `SUFFICIENT`.
5. `SUFFICIENT` — none of the above conditions apply.

This keeps the vocabulary the CEO proposed (it was already well-chosen) while making every status fully
DERIVABLE from disclosed numbers in the same report — never an opaque label a reader has to trust blind.

---

## 11. Decision Intelligence v2 Integration Boundary

Context Memory exposes exactly one read function returning a `ContextualEvidenceReport` (§10). It never
calls into Decision Intelligence, Edge Intelligence, or Market Intelligence — only the reverse. It never
touches a `Contract`'s own fields, never writes to the Strategy Library, never produces a `DecisionOutcome`
value, never computes a position size.

**Integration mode evaluation** (per the CEO's own six options):

- **Gate** (evidence can silently eliminate a candidate) — REJECTED for v1: this would let an
  unproven, un-falsified evidence source silently override Edge Intelligence's own already-disclosed
  PRESENT verdict, exactly the "silently eliminate edges" behavior the CEO's own boundary explicitly
  forbids.
- **Veto** — same rejection, same reasoning, a harder version of "gate."
- **Ranking modifier** / **Confidence modifier** — both premature for v1: either would let Context
  Memory's own untested reliability directly change WHICH edge gets recommended or how strongly, before
  §15's own falsification study has ever measured whether doing so helps or hurts.
- **Controlled combination** — the eventual likely destination once evidence justifies it, but
  specifying its exact mechanics now (before any real retrieval has ever run) would be designing against
  data that does not exist yet — deferred, named as an explicit open question (§17).
- **Explanatory input** — **RECOMMENDED as the safest initial integration mode.** Decision Intelligence
  v2 would attach the `ContextualEvidenceReport` (or a compact summary of it) to each ACCEPT candidate's
  own `evidence`/`explanation` fields, purely for human/CEO visibility — zero effect on any ACCEPT/
  REJECT gate (`eligibility.py`, unchanged), zero effect on ranking (`ranking.py`, unchanged). This
  answers **Q9** directly: the safest initial mode is one where Context Memory can be wrong, sparse, or
  even completely absent, and Decision Intelligence v2's own recommendation is byte-for-byte identical
  to v1's — only the DISPLAYED explanation grows richer. Promotion beyond explanatory input requires its
  own future CEO authorization plus the v1-vs-v2 falsification study (§15, Checkpoint 8g) actually
  showing a measured benefit — never assumed in advance.

---

## 12. Failure Modes and Red-Team Analysis

| Failure mode | Prevention / detection / disclosure |
|---|---|
| Sparse-history bias | Minimum-sample floor (§9) blocks any statistic below threshold from ever being reported as `SUFFICIENT`; `UNAVAILABLE`/`LIMITED` are first-class, expected outcomes, not edge cases to suppress. |
| False-neighbor retrieval | Categorical-only matching (§7) with a disclosed relaxation order (§8) — no continuous-distance blending that could rank a superficially-close-but-substantively-different context as a "neighbor." |
| Regime drift | `evidence_freshness` (§10) surfaces episode age explicitly; `STALE` status (§10.1) fires on old-dominant evidence; recency-weighted in-bucket ranking (§8) prefers recent episodes when ties allow. |
| Survivorship bias | Every retired/DEPRECATED/DISABLED strategy's OWN historical Observations remain in the append-only log (§5) forever — nothing is deleted when a strategy's lifecycle status changes; `strategy_version`/`contract_content_hash` (§6) keep old evidence correctly attributed rather than silently dropped. |
| Strategy-version contamination | `contract_content_hash`/`contract_version` stamped per Observation, never updated retroactively (§6); cross-version pooling requires an explicit, visible warning, never silent (§6). |
| Overlapping-sample inflation | Episode collapsing (§9.3) is the primary, structural defense — sample counts are always episode counts, never raw bar counts. |
| Multiple-comparison bias | Named explicitly as an open statistical question for the future validation checkpoint (§15, Checkpoint 8g) — with ~43 strategies × many possible context buckets, a large number of `(strategy, context)` pairs will be evaluated over time; any future promotion of Context Memory beyond "explanatory input" (§11) must account for this the same way the Research Lab's own global-FDR discipline does (`PROJECT_AUDIT.md` — "hierarchical family-wise plan mandatory... no per-experiment significance hunting"), not treat each `(strategy, context)` lookup as an independent test. |
| Stale evidence | `STALE` status (§10.1), `evidence_freshness` field (§10). |
| High win rate with negative expectancy | `per_edge_contextual_statistics` (§10) always reports BOTH a win-rate-equivalent AND the mean/median return/R — never win-rate alone; a future consumer that looks only at win-rate is a display/consumption risk, not a data-contract gap, and is called out explicitly in `uncertainty_and_limitations` whenever the two diverge sharply. |
| Excessive specialization | The relaxation floor (§8) caps how many dimensions a query may require simultaneously — an over-specialized query (e.g. requiring an exact match on all 14 dimensions AND a rare session) naturally starves itself into `UNAVAILABLE` rather than returning a spuriously "perfect" single-episode match presented with false confidence; the minimum-sample floor (§9) is the actual backstop. |
| Overly broad similarity | The relaxation floor also caps how FEW dimensions may ever remain required — retrieval never relaxes to "any market state at all," a hard, disclosed lower bound on Tier N. |
| Feedback loops | §4.9's structural separation (similarity never reads outcomes) plus §11's "explanatory input only" integration mode together mean no decision made using Context Memory can currently change what Context Memory itself later retrieves as evidence about that same decision — there is no loop to close in this design. |
| Self-confirming selection bias | Directly a consequence of the "no live learning loop" (§4.9) and "gate/veto rejected for v1" (§11) decisions — Context Memory cannot yet influence which trades are taken, so it cannot yet bias which outcomes it later observes. |

---

## 13. Evidence Sufficiency Framework

Per the CEO's own instruction, no threshold is proposed without justification, and several are
explicitly left as open numeric questions (§17) rather than invented here without data to ground them.

- **Minimum observation counts**: reuse, rather than reinvent, this project's own already-CEO-blessed
  small-sample discipline — `PROJECT_AUDIT.md` §A0 already establishes "min-trades + UNRESOLVED-if-CI-
  straddles rules" as the standing convention for exactly this kind of small-n concern elsewhere in the
  project. Context Memory should adopt the SAME philosophy (a floor count AND a CI-straddle check, not
  either alone) rather than a novel one; the exact floor number is an open question (§17) pending real
  data on how many episodes typically accumulate per `(state_fingerprint, strategy_id)` bucket — a
  number this design cannot honestly produce without first observing real retrieval yield.
- **Effective independent sample size**: episode count (§9.3), never raw bar/Observation count — this is
  the design's own answer to "effective independent sample size," not a separate statistical adjustment
  layered on top.
- **Confidence intervals**: a nonparametric bootstrap over episodes (not over raw bars, for the same
  autocorrelation reason), consistent with this project's own already-validated block-bootstrap
  machinery for Test A robustness (`PROJECT_AUDIT.md` §B) — reusing an already-proven-calibrated
  methodology rather than a new, unvalidated one.
- **Expectancy/win-rate uncertainty**: reported directly as the bootstrap CI width on
  `atr_normalized_return`/`pnl_r` and on the win-rate-equivalent fraction (§10) — no point estimate is
  ever reported without its own interval alongside it.
- **Regime coverage**: `total_eligible_historical_contexts` (§10) vs. `similar_contexts_retrieved` makes
  the coverage ratio visible in every report; a future refinement could bucket coverage by symbol/session
  explicitly (open question, §17).
- **Stability across time / sensitivity to similarity thresholds / contradictory subgroups**: this is
  precisely what `evidence_consistency` and the `CONTRADICTORY` status (§10.1) are for — a split-half
  time check (do episodes from the first vs. second half of available history agree in sign) is the
  concrete mechanism recommended, deferred to implementation detail in a future checkpoint rather than
  fully specified here.

---

## 14. Testing and Validation Plan (design intent only — no tests written this checkpoint)

| Test category | Intent |
|---|---|
| Deterministic replay | Running the same historical bar sequence through Context Snapshot construction twice must produce byte-identical records — same discipline as every prior checkpoint's own `test_..._is_deterministic` tests. |
| Temporal leakage | Construct a synthetic Observation at time `T`; assert retrieval at query time `T' < T` never returns it, and retrieval at `T' >= resolution_as_of` does. |
| Identity/versioning | Two Observations with identical similarity dimensions but different `as_of` get the same `state_fingerprint` but different `context_snapshot_id`; a synthetic contract-content change produces a different `contract_content_hash` and old evidence keeps citing the old one. |
| Duplicate prevention | A synthetic run of N consecutive bars sharing one fingerprint collapses to exactly one episode, never N. |
| Exact-match retrieval | A hand-built query with a known, planted Tier-0 match retrieves it with `retrieval_tier_reached = 0`. |
| Degraded-data | A synthetic Observation with `data_quality_level != OK` is never stored/never eligible — verified by construction, not by a runtime guard alone. |
| Sparse-history | Fewer episodes than the minimum floor anywhere in history → `UNAVAILABLE`, with the correct `no_sufficient_history_reason`. |
| Contradictory-history | A synthetic evidence set with exactly 50/50 sign split produces `CONTRADICTORY`, never a falsely-confident `SUFFICIENT`. |
| Rebuild equivalence | Deleting Layer 2 (§5) and rebuilding from Layer 1 alone reproduces byte-identical derived indexes/aggregates. |
| Similarity explanation | Every retrieved episode's own explanation lists exactly the dimensions that matched/relaxed/were unavailable, verified against a hand-traced fixture, same pattern as `edge_intelligence`'s own `EdgeEvidenceItem.explanation` tests. |
| Historical cutoff | The sealed-holdout boundary (§9.4) is never crossed by a synthetic fixture that includes bars from inside it. |
| Integration-boundary | Grep-verified zero imports of `shadow_evidence`/`signal_engine`/`scoring_engine`/`risk_manager`/`execution_engine`/`decision_intelligence`/`market_intelligence` INTERNALS beyond the public snapshot type, `harness.py` — same discipline every prior checkpoint's own adversarial review already applied. |
| Negative controls | A synthetic "random noise" context (no genuine regime structure) should retrieve, at best, weak/`LIMITED` evidence — never a spuriously strong signal, proving the mechanism isn't finding patterns in noise. |
| Synthetic false-neighbor | Two contexts that differ on exactly the highest-priority dimension (`structure_state`) but agree on every lower-priority one must NOT be treated as Tier-0 equivalent — proves the relaxation order (§8) is actually enforced, not just documented. |

---

## 15. Proposed Implementation Checkpoint Sequence (NOT authorized by this design)

Seven small, independently-gated checkpoints, each requiring its own separate, explicit CEO
authorization — none of the following is approved by this document:

1. **Immutable contracts and IDs** — `types.py` for `ContextSnapshot`/`Observation`/`Outcome`, plus the
   deterministic identity functions (§6). No storage, no retrieval, no I/O. The only checkpoint
   realistically ready to be proposed for authorization next.
2. **Append-only context store** — a real, persistent Layer 1 (§5), fed by a read-only adapter from
   `MarketIntelligenceSnapshot`/`EdgeIntelligenceSnapshot`. No retrieval yet.
3. **Historical indexing** — Layer 2 (§5), built and proven rebuildable from Layer 1.
4. **Deterministic retrieval** — the relaxation ladder (§8), tested against real accumulated history from
   Checkpoints 2–3, likely the point where the open numeric thresholds (§17) get their first
   real-data-informed answers rather than remaining placeholders.
5. **Evidence aggregation** — the bootstrap/sufficiency machinery (§13), producing real
   `ContextualEvidenceReport`s.
6. **Decision Intelligence v2 integration** — wiring `ContextualEvidenceReport` into Decision
   Intelligence's own `explanation` field ONLY (§11's "explanatory input" mode) — `eligibility.py`/
   `ranking.py` byte-for-byte unchanged.
7. **v1-vs-v2 falsification study** — a genuine experiment (not an assumption) testing whether v2's
   presence changes anything measurable, and if a future promotion beyond "explanatory input" is ever
   proposed, whether it would have helped or hurt historically — the direct answer to **Q10**, and the
   gate every future integration-mode promotion (§11) must pass before being proposed.

---

## 16. Explicit Unresolved Questions

- **Exact horizon bar-counts** (§4.3) — the illustrative +20/+80 M15 figures need real-data-informed
  selection, not an arbitrary a-priori choice.
- **Exact relaxation order weighting** (§8) — the proposed drop-order is a reasoned starting point, not
  empirically validated; Checkpoint 4 (§15) is where it should first be measured against real retrieval
  yield.
- **Exact minimum-sample floor, staleness threshold, and CONTRADICTORY agreement threshold** (§9, §10.1,
  §13) — deliberately left as open numeric questions rather than invented without data, per the CEO's own
  "do not select arbitrary thresholds without justification" instruction.
- **Cross-instrument evidence pooling** — this repository is XAUUSD-only today; whether/how Context
  Memory should ever pool evidence across instruments (if the AI Trader expands) is unaddressed and
  should stay unaddressed until it is a real question, not a hypothetical one.
- **The exact mechanics of a future "controlled combination" integration mode** (§11) — deliberately
  deferred rather than designed against data that does not yet exist.
- **The precise caller-adapter contract for strategy-native Outcomes** (§4.3) — analogous to
  `decision_intelligence.types.ResearchStats`, but the exact field set and cost-model labeling scheme
  needs its own short design pass once a real caller (presumably the harness or a dedicated backfill
  script) is specified.
- **Whether/how `market_intelligence_schema_version` and `edge_intelligence_schema_version` should
  eventually become self-declared fields on those packages' own types**, rather than externally-tracked
  constants Context Memory alone maintains (§6) — flagged as a possible, but out-of-scope-for-this-
  checkpoint, improvement to Checkpoints 5/6 themselves, requiring its own separate authorization since
  this checkpoint is explicitly forbidden from modifying either package.

---

## 17. Final Recommendation

**APPROVE the architecture direction, with staged re-authorization.** The design is internally
consistent, grounded in this repository's own already-validated conventions (lookahead safety,
append-only-plus-rebuildable-derived-layer, local-type caller adaptation for cross-package data, "never
fabricate," disclosed IMPLEMENTATION CHOICE reasoning, reuse of the project's own existing small-sample
and bootstrap discipline rather than inventing new statistical machinery), and satisfies every
architectural principle the CEO's authorization named — determinism, explainability, auditability, a
first-class `NO SUFFICIENT HISTORY` outcome, and a hard structural boundary preventing Context Memory
from ever becoming (or silently drifting into) an autonomous decision-maker.

This is NOT a recommendation to build all seven proposed checkpoints (§15). It is a recommendation that
the DIRECTION is sound enough to be worth building incrementally, starting with the single lowest-risk,
highest-confidence checkpoint (immutable contracts and IDs) — and that every subsequent checkpoint should
be re-evaluated against real, accumulated evidence rather than assumed to still be the right design once
real data exists to check it against.

---

## Mandatory Questions

**Q1. What is the smallest useful Context Memory system that adds real evidence without becoming a
machine-learning black box?** An append-only log of categorically-fingerprinted Context Snapshots +
Observations + Outcomes, retrieved by a fixed-priority hierarchical exact-match relaxation (§7–§8) —
never a fitted weight, never an embedding, never a learned distance. Every retrieval decision traces to a
disclosed rule, not a trained parameter. §1, §7, §8.

**Q2. What information must be stored at observation time so the historical record remains
reproducible?** The full similarity vector (§3.3), the exact PRESENT edge set (§4.1), every identity/
version stamp (§6) — `contract_content_hash`, `market_intelligence_schema_version`,
`edge_intelligence_schema_version` — and the data-quality/confidence gate values (§3.2) that determined
eligibility. Nothing derivable later (an aggregate, an index) needs to be stored at observation time;
everything NOT derivable later (what the contract looked like, what Edge Intelligence said, what quality
gate applied) must be.

**Q3. What information must never be included because it creates future leakage?** Nothing from bars
after `as_of` (inherited for free from Market Intelligence's own lookahead-safety guarantee, §9.1);
nothing from inside the sealed terminal holdout until the CEO opens it (§9.4); no outcome whose horizon
has not yet elapsed treated as resolved (§4.5); no retroactively-revised strategy-native outcome
overwriting an already-written row in place (§9's discussion of immutability — corrections must be new,
superseding rows, never in-place edits).

**Q4. How should contexts be compared without arbitrary or unstable similarity weights?** By NEVER using
a weight at all — a fixed-priority relaxation ORDER (§8) over categorical dimensions replaces the concept
of a weight entirely; "importance" is expressed as "how late in the relaxation order a dimension is
dropped," a disclosed ordinal choice, not a numeric coefficient fitted to anything. §7, §8.

**Q5. How should the system distinguish genuine contextual evidence from coincidental historical
resemblance?** Episode collapsing (§9.3) prevents one persistent regime from masquerading as many
independent confirmations; the minimum-sample floor plus bootstrap CI (§13) prevents a handful of
episodes from being reported with unwarranted confidence; `evidence_consistency`/`CONTRADICTORY` (§10.1)
catches historical resemblance that doesn't actually predict a consistent outcome; the eventual
falsification study (§15, Checkpoint 8g) is the only mechanism that can ever PROVE the distinction holds
rather than merely assert it by design.

**Q6. How should multiple simultaneously PRESENT edges be recorded and evaluated?** One Observation
carries the full PRESENT set (never one Observation per edge); Outcome rows fan out one per
`(observation, strategy_id, horizon)`; every aggregation groups by `strategy_id` first, so "how has S7
performed" is always answerable independently of what else happened to be PRESENT alongside it in the
same historical moment. §4.1, §4.7.

**Q7. What happens when no sufficiently similar historical contexts exist?** Retrieval returns
`evidence_sufficiency = UNAVAILABLE` with a populated `no_sufficient_history_reason` naming the exact
tier and threshold not met — a first-class, expected, fully-specified output, never an exception, a
crash, or a silently-omitted report. §8, §10, §10.1.

**Q8. How should version changes in strategies, Market Intelligence, and outcome definitions be
handled?** Every Observation/Outcome is permanently stamped, at write time, with the exact version of
each that was active — `contract_content_hash`/`contract_version` (strategy), `market_intelligence_
schema_version` (Market Intelligence's own field shape, externally tracked since MI carries no
self-declared version today — an open question, §16), `outcome_definition_version` (horizon/return
convention). Old evidence is never silently reinterpreted under a new version; cross-version pooling, if
ever used, must be explicit and visibly disclosed. §6.

**Q9. What is the safest initial way for Decision Intelligence v2 to consume Context Memory evidence?**
As a pure explanatory input attached to each ACCEPT candidate's own explanation — zero effect on
`eligibility.py`'s gates or `ranking.py`'s ordering. Decision Intelligence v2's actual recommendations
would be byte-for-byte identical to v1's until a future, separately-authorized checkpoint promotes
Context Memory to any mode with real influence, and only after the falsification study (§15, Checkpoint
8g) has measured whether that influence would help. §11.

**Q10. How can we experimentally prove that Context Memory improves decisions rather than merely adding
complexity?** Checkpoint 8g (§15): run Decision Intelligence v1 and a v2 that consumes Context Memory
evidence (initially in explanatory-input-only mode, later — only if separately authorized — in an
influencing mode) over the SAME historical window, and compare. This is a genuine held-out comparison,
not a retrospective narrative — the same evidentiary standard this project already applies to every
Research Lab claim (matched-null validation, block-bootstrap robustness, global-FDR discipline) rather
than a new, lower bar invented just for this component.
