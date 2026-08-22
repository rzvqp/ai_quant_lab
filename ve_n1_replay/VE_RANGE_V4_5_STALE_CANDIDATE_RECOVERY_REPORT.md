# VE_RANGE_V4_5_STALE_CANDIDATE_RECOVERY_REPORT

**Mandate**: `VE-RANGE-V4-5-STALE-CANDIDATE-RECOVERY-001`
**Repo**: `ai_quant_lab-wp5b`, branch `discovery-mk-matrix-v1`
**Contract**: [`RANGE_V4_5_LIFECYCLE_CONTRACT.md`](RANGE_V4_5_LIFECYCLE_CONTRACT.md)
**v4.4 lineage baseline**: `3bb61cf` (`VE-RANGE-V4_4-IMPLEMENTATION-001`), permanently frozen, byte-untouched

> **VERDICT: `RANGE_V4_5_RECOVERY_BLOCKED` / `RANGE_LIFECYCLE_RESEARCH_REQUIRED`** (mandate section 28).
> Two candidate mechanisms were designed, each built entirely from already-frozen v4.4 values with zero
> new config fields, and each correctly reproduces the real stuck-candidate shape it targets. Mandatory
> negative-control validation against all 187 real macro structures that reached `CONFIRMED` across the
> full 2011–2026 history found both mechanisms release genuine, converging candidates far too early:
> H-ONE-SIDED before 69/187 (36.9%) real confirmations, H-PERSISTENCE before 23/187 (12.3%). A second,
> independent episode-level regression confirms this at even larger scale: **69.0% of v4.4's real
> confirmed episodes (129/187) are lost entirely under v4.5**, replaced by 1,080 fragmentary,
> mostly-spurious new confirmations — the same RANGE-context over-segmentation failure that closed the
> prior T-STALE attempt. Neither mechanism is deployed. v4.4 remains the frozen baseline, untouched. Also
> found, independent of the verdict: v4.4's real defect is far more severe than previously stated — zero
> `CONFIRMED` bars for nine straight years (2016–2024), one candidate stuck 9.7 years. Full reasoning,
> numbers, and disposition in sections 6, 6.1, and 14 below.

## 1. v4.4 lineage

`3bb61cf` froze `range-hierarchical-v4.4` as the permanent conservative RANGE research baseline
(`config_id` `23d98c07...`). A known, ACCEPTED-not-fixed limitation was carried forward at that freeze:
a candidate that never confirms can occupy the single active MACRO slot indefinitely. A first repair
attempt, T-STALE (`range_semantic_v4_4_1.py`, `4ed4eb4`), was built, calibrated, and Red-Team-validated
fresh-blind (`8e550ae`) — closed `GENERALIZATION_NOT_SUPPORTED`: it recovered real missed RANGE (recall
0.577→0.808) but doubled total false positives (8→16) and increased directional false positives (4→5),
both HARD gates, driven by its one calibrated parameter (`STALE_MIN_ALTERNATION=3`) being confirmed
`FRAGILE` — every one of 32 real firings occurred at exactly that boundary value, over-firing inside
genuine ranges (RANGE-context over-segmentation) rather than cleanly recovering stale-blocked ones. Closed
`6120b5d`; CEO froze v4.4, left a future re-examination available to a separate, later mandate. This is
that mandate.

## 2. Alpha diagnosis reproduction (mandate section 2/6A)

Alpha's diagnosis (`ALPHA-XAUUSD-RANGE-TF-AUTHORITY-PARENT-RECOVERY-001`, `79beabf`) reported: M15 is the
sole canonical RANGE authority (`RangeSemanticEngineV44(timeframe="15m")`); last CONFIRMED transition
`2020-12-31 05:45 UTC` (macro_id 131); post-2020 candidates 132/133/134, all `states=["CANDIDATE"]` only;
macro_id 133 held the slot `2021-01-06` → `2021-08-08` (~7 months); 0 CONFIRMED bars in 2021/2022/2023.

### 2.0 Methodology correction made before trusting any reproduction number (disclosed, not hidden)

This state machine is fully incremental and path-dependent: which structure is active at a given calendar
date depends on the ENTIRE causal history since the engine's own warmup start, with no lookback. An
initial reproduction attempt using a shorter, arbitrary warmup window (starting mid-2020) produced
numbers that looked superficially consistent with Alpha's own report — but three independent, deliberately
minimal trace scripts, run specifically to test this, proved that using a DIFFERENT warmup start date
(2020-06-01 vs. 2020-01-01) changes WHICH structure ID is active at the SAME calendar date. All further
reproduction in this report uses exactly ONE canonical warmup: **2011-07-26**, the true beginning of
`data/market/OANDA_XAUUSD_M15.csv` (355,696 bars total), matching Alpha's own stated "warmup from 2011"
convention. Numbers from the shorter-warmup attempt are superseded and not reported below.

### 2.1 Independently reproduced from source, canonical warmup, full history

Running the SAME frozen, unmodified `RangeSemanticEngineV44` directly against the canonical CSV from
2011-07-26 through the end of available data (not re-derived from Alpha's own script) surfaces a
materially **more severe** picture than Alpha's own report describes, not a milder one:

- **v4.4 shows ZERO `CONFIRMED` bars for nine consecutive calendar years, 2016 through 2024 inclusive**
  (section 6's year-by-year table: every one of those 9 years reads `total=X FORMING=X` and nothing else
  — no `CANDIDATE`, `CONFIRMED`, `WEAKENING`, or trend-labeled bar at all). This is the single macro
  structure **macro_id 770**, which forms on **2015-07-20 02:30 UTC** and does not release the slot until
  **2025-04-07 01:00 UTC — 3548.94 days, 9.7 years later** (`INSUFFICIENT_TRAVERSAL`). Direct
  instrumentation of `up.members`/`dn.members`: BOTH sides grew substantially (up to 89 touches, dn to 67)
  within roughly the first 50 bars of the structure's life — this is NOT a one-sided-growth case;
  `n_touch` (=2) is satisfied on both sides almost immediately, and the candidate still never passes T3's
  ER/traversal/RND discrimination gate for nearly a decade. `degeneracy_check` cannot see this either —
  the zone's geometry stays valid (non-inverted, non-degenerate) throughout. Full history also surfaces 2
  more real, genuinely-never-confirmed episodes of this same both-sided shape (macro_id 969, 175.39 days;
  macro_id 945, 76.09 days, both 2025–2026) and 1 genuinely one-sided example (macro_id 893, 2025-06-29,
  106.32 days, "dn" frozen at 1 touch while "up" grew to 4) — 4 real never-confirmed episodes >30 days in
  total across 2011–2026, a materially cleaner and more precise catalog than an earlier draft of this
  section carried (see below).
- **Methodology correction, disclosed rather than silently fixed**: an earlier draft of this section cited
  macro_id 748 (113.03 days, one side frozen at 1 touch) as a "real defect example" alongside 770. Direct
  `reached_confirmed` checking of the full history shows this was WRONG: macro_id 748, and 7 OTHER
  candidates from an original list of "9 real episodes lasting >30 days" (86, 231, 399, 470, 564, 571,
  595, 748), all confirmed normally — only macro_id 770 among that original 9 was genuinely, permanently
  stuck. The original list was filtered by DURATION alone, not by whether a candidate ever actually
  reached `CONFIRMED` — a real methodological gap, not caught until the section 6.1 negative control was
  run properly against `reached_confirmed` directly. This retroactively explains a large part of why both
  v4.5 mechanisms failed that later negative control: their own design-time "9/9 coverage" validation
  (section 3) was itself unknowingly built substantially from false-positive targets.
- Distinct active-macro-id count under v4.4 across calendar years 2015–2022: **69 distinct structure ids**
  (`622`...`770`). This means v4.4 was NOT idle before getting stuck — 68 other structures were active in
  this window (mostly before 770 itself started, consistent with normal confirmation/termination activity
  through mid-2015, then the single, 9.7-year 770 episode dominating everything after). Reconciling this
  against Alpha's own specific ids (131/132/133/134) and dates (2021) is not expected to resolve to an
  exact id-for-id match — the path-dependence/warmup-sensitivity finding above (section 2.0) means
  differently-warmed-up reproductions produce genuinely different id sequences and potentially different
  specific dates for a structurally analogous event. The qualitative mechanism, and now the exact
  multi-year severity, is independently and more precisely reproduced here regardless of the exact
  calendar/id alignment with Alpha's own report, which is not pursued further than disclosed.

**Root cause, traced to exact source** (mandate section 2's own gate, confirmed byte-for-byte, and
consistent with all real never-confirmed shapes above): `forming_macro = self._active_macro is None`
(`range_semantic_v4_4.py`, `_offer_swing_everywhere`). `Cluster.offer()` (`range_semantic_v4_3.py`)
accepts a swing only within `tol_cluster * atr_ref` of the cluster's OWN current median; a rejected swing
has no side effect. Neither `degeneracy_check` (only catches inverted/too-narrow zones) nor any other
existing v4.4 exit can recognize or release either shape: `_evaluate_macro_formation` never even reaches
the T3 gates while a side is under `n_touch` (macro_id 893's shape), and even once both sides ARE past
`n_touch`, nothing in v4.4 asks "has this candidate sat T3-eligible without confirming for an
unreasonably long time" (macro_id 770's shape) — confirmation is evaluated fresh every bar with no memory
of how long the candidate has already waited.

### 2.2 Data-gap claim: resolved, NOT an artifact (mandate section 28's own explicit provision)

Alpha's own report separately disclosed "M15_v2 has a large data gap ~2021-09 → 2023 (2022 nearly
absent)" in their own pipeline, and reported 0 CONFIRMED bars in 2021/2022/2023. An earlier draft of this
report speculated, based on a non-canonical, since-superseded reproduction, that this might be
substantially a data-loading artifact rather than a genuine defect — **that speculation is RETRACTED.**
The canonical, full-history reproduction (section 2.1/6) shows v4.4 has zero `CONFIRMED` bars not just in
2021–2023, but for the entire 2016–2024 span — Alpha's finding is CONFIRMED and, if anything,
UNDERSTATED. Direct CSV inspection (section 7) separately, and still validly, confirms there is no gap in
the underlying market data itself — the "0 CONFIRMED" finding is a genuine Market Intelligence liveness
defect, not a symptom of missing data, in either Alpha's window or this mandate's wider one.

## 3. Liveness invariant, repair design, and why it is not a retune

See [`RANGE_V4_5_LIFECYCLE_CONTRACT.md`](RANGE_V4_5_LIFECYCLE_CONTRACT.md) sections 1-4 for the full
invariant statement and mechanism. Summary: `ConfigV45` adds **zero** new fields over `ConfigV44`
(mechanically verified, `test_live12b_zero_new_config_fields_vs_v4_4`). **Two** new lifecycle checks exist
— `_candidate_stagnation_reason` returns one of two reason codes, or `None` — because section 2.1 found
two structurally disjoint real shapes a single mechanism cannot both reach:

- **H-ONE-SIDED** (`CANDIDATE_ONE_SIDED_TERMINATED`): built from `d_macro`, `n_touch`, `ALT_MIN`, and the
  already-existing `alternation_rate`/`StructureV44.touches_in_window` — the identical evidence T3
  already computes as `SUPPORTING_ONLY` confirmation evidence, applied one lifecycle stage earlier.
  Targets macro_id 893's shape (one side never reaches `n_touch`).
- **H-PERSISTENCE** (`CANDIDATE_PERSISTENCE_TERMINATED`): built from `d_macro`, `n_touch`, and
  `WEAKENING_MAX_BARS` — the identical "how long is too long to sit unresolved" threshold v4.4 already
  applies POST-confirmation, applied PRE-confirmation for the first time via a new producer-level
  consecutive-bar counter (bookkeeping, not a threshold). Targets macro_id 770's shape (both sides satisfy
  `n_touch` but T3's discrimination gate never passes).

No threshold was searched, grid-tested, or tuned to a target coverage number. Both checks were designed
from the two real shapes in section 2.1 alone, then originally validated together, after the fact, against
every real macro candidate lasting more than 30 days in an early, DURATION-ONLY scan of the canonical
2011–2022 window: H-ONE-SIDED alone resolved 6 of 9, H-PERSISTENCE alone resolved 5 of 9, and their misses
were exactly disjoint — together they resolved all 9. Full per-episode firing detail, WITH the later,
corrected `reached_confirmed` finding annotated (section 2.1):

| macro_id | duration | H-ONE-SIDED | H-PERSISTENCE | resolved by | actually confirmed later? |
|---|---|---|---|---|---|
| 86  | 253.98 d | fires, delay 0.22 d  | fires, delay 94.48 d  | H-ONE-SIDED | **YES — false-positive target** |
| 231 | 114.71 d | fires, delay 111.31 d | never fires | H-ONE-SIDED | **YES — false-positive target** |
| 399 | 34.44 d  | never fires | fires, delay 33.75 d | H-PERSISTENCE | **YES — false-positive target** |
| 470 | 192.54 d | never fires | fires, delay 2.46 d | H-PERSISTENCE | **YES — false-positive target** |
| 564 | 95.17 d  | fires, delay 0.19 d | never fires | H-ONE-SIDED | **YES — false-positive target** |
| 571 | 36.14 d  | never fires | fires, delay 0.46 d | H-PERSISTENCE | **YES — false-positive target** |
| 595 | 33.20 d  | fires, delay 0.27 d | never fires | H-ONE-SIDED | **YES — false-positive target** |
| 748 | 113.03 d | fires, delay 0.23 d | never fires | H-ONE-SIDED | **YES — false-positive target** |
| 770 | 3548.94 d | fires, delay 0.47 d | fires, delay 115.73 d | H-ONE-SIDED (faster) | **NO — genuine defect** |

**This table, understood correctly, was never positive evidence at all — it was an early, unrecognized
preview of the section 6.1 failure.** 8 of these 9 candidates went on to confirm normally; only macro_id
770 is a genuine, permanently-stuck case. "9/9 coverage" against this set meant firing on 8 candidates
that should NOT have been released, and 1 that should have. The table is kept here, corrected and
annotated, specifically so this mistake is visible and instructive rather than quietly removed — it is the
clearest illustration in this whole mandate of why a duration-based positive check can look like success
while being the opposite, and why section 6.1's real, `reached_confirmed`-based negative control against
all 187 confirmations (not 9 hand-picked candidates) is the finding that actually governs this mandate's
verdict.

(A third candidate mechanism, "H2" — an instantaneous check on `ER`/`RND` against the existing
`ER_weakening`/`RND_weakening` thresholds, with no persistence counter — was also evaluated during design
and found to fire on 7 of 9 episodes, but its firings are a strict subset of H-ONE-SIDED ∪ H-PERSISTENCE
(every episode H2 catches, one of the two chosen mechanisms catches at least as fast) — it was dropped as
redundant, keeping the design to exactly two mechanisms rather than three.)

**Relationship to T-STALE (mandate section 5's own "not a retune" requirement)**: T-STALE tracked rejected
touches and fired on a NEW, calibrated alternation-count threshold over that rejection evidence. Neither
mechanism here introduces a new calibrated count: H-ONE-SIDED tracks ACCEPTED touches only (already
tracked, already used elsewhere) and asks the OPPOSITE structural question (definite ONE-SIDEDNESS via
low alternation, not "enough alternating rejections"); H-PERSISTENCE reuses `WEAKENING_MAX_BARS` — an
existing threshold governing an existing, structurally analogous POST-confirmation question, not a value
chosen for this purpose. See the lifecycle contract's own module-docstring-equivalent section for the
full comparison, including the T-STALE-specific negative-control check performed for H-PERSISTENCE
(section 6 below).

## 4. Deterministic reproduction (mandate section 6)

**A. Real historical lineage**: section 2.1 above — macro_id 893 (H-ONE-SIDED shape, 106.32 days, one
side frozen at 1 touch, genuinely never confirmed) and macro_id 770 (H-PERSISTENCE shape, 3548.94 days,
both sides well past `n_touch` yet never confirming), both from the canonical, full-history reproduction.

**B. Minimal deterministic fixtures** (`test_v4_5_liveness.py`): `test_live1_directional_stagnation_
reproduces_the_real_defect_shape` — a directly-constructed `StructureV44` fed 14 accepted touches on one
side and none beyond the founding pair on the other, past `d_macro` bars — matches macro_id 893's shape.
`test_live1c_persistence_fires_once_both_sided_but_never_confirming` — a directly-constructed
`StructureV44` with both sides satisfying `n_touch` immediately and `_trailing_closes` left empty (so
`zones()` never resolves, mirroring T3's discrimination gate never passing) — matches macro_id 770's
shape. Neither fixture depends on any strategy or profitability outcome.

## 5. Candidate lifecycle / confirmation / boundary semantics

See lifecycle contract sections 2, 5, 6 — all confirmation and boundary construction logic is inherited
from `RangeSemanticProducerV44`/`StructureV44` without override; mechanically confirmed unchanged by
`test_live6_confirmation_semantics_byte_identical_to_v4_4` and
`test_live7_boundary_construction_untouched`.

## 6. Legacy regression (2011-2020) and modern diagnostic (2021+) (mandate sections 14-18)

Dual-engine (v4.4 vs v4.5), bar-for-bar, single pass over the complete canonical history
(2011-07-26 through 2026-08, 355,696 bars). v4.4 side (the frozen baseline — this is real, unmodified
v4.4 behavior, not affected by v4.5's existence):

| Year | Total bars | CANDIDATE | FORMING | CONFIRMED | WEAKENING | trend-labeled |
|---|---|---|---|---|---|---|
| 2011 | 10,577 | 7,775 | 1,550 | 946 | 41 | 54 |
| 2012 | 24,109 | 11,601 | 10,865 | 1,226 | 71 | 81 |
| 2013 | 23,796 | 10,687 | 9,925 | 2,394 | 131 | 135 |
| 2014 | 23,801 | 12,695 | 8,698 | 1,933 | 88 | 105 |
| 2015 | 23,735 | 17,620 | 4,135 | 1,357 | 79 | 89 |
| **2016** | 23,631 | 0 | **23,631** | **0** | 0 | 0 |
| **2017** | 23,535 | 0 | **23,535** | **0** | 0 | 0 |
| **2018** | 23,616 | 0 | **23,616** | **0** | 0 | 0 |
| **2019** | 23,614 | 0 | **23,614** | **0** | 0 | 0 |
| **2020** | 23,702 | 0 | **23,702** | **0** | 0 | 0 |
| **2021** | 23,623 | 0 | **23,623** | **0** | 0 | 0 |
| **2022** | 23,659 | 0 | **23,659** | **0** | 0 | 0 |
| **2023** | 23,563 | 0 | **23,563** | **0** | 0 | 0 |
| **2024** | 23,736 | 0 | **23,736** | **0** | 0 | 0 |
| 2025 | 23,647 | 13,578 | 8,858 | 686 | 68 | 54 |
| 2026 (partial) | 13,352 | 3,221 | 10,077 | 24 | 5 | 0 |

**2016 through 2024 — nine consecutive full calendar years — show 100% `FORMING`, 0% everything else.**
This single continuous block is macro_id 770 (section 2.1): it enters `FORMING` in mid-2015 and does not
release the slot until 2025-04-07. The state machine is not merely under-producing CONFIRMED ranges in
this span — it produces ZERO events of ANY kind (no new CANDIDATE, no WEAKENING, no trend label) because
nothing else can happen while the single MACRO slot stays permanently occupied.

**v4.4 overall**: 187 CONFIRMED episodes, 153 never-confirmed episodes across the full history; only 4 of
those never-confirmed episodes last more than 30 days (770, 969, 893, 945 — section 2.1's corrected
catalog) — confirming that outside the 2016–2024 block, v4.4 functions close to normally (the 9 originally
misidentified "long episodes" in section 3's table were mostly ordinary, if slow, real confirmations).
Never-confirmed candidate lifetime distribution: min 0.01 days, median 0.20 days, p95 11.05 days, max
3548.94 days (770) — a distribution utterly dominated by one extreme outlier, not a smooth continuum.

**v4.5 side, same window** — included for completeness (mandate section 14/15), even though section 6.1
already independently establishes why it is not deployed: 1133 CONFIRMED episodes (6.1× v4.4's 187), 2150
never-confirmed episodes (14.1× v4.4's 153), 1662 distinct macro ids active in 2015–2022 alone (24× v4.4's
69). Release-reason breakdown: `ZONES_DEGENERATE` 2,204 (pre-existing, unchanged mechanism),
`BREAKOUT_ACCEPTED` 968 (pre-existing), `CANDIDATE_ONE_SIDED_TERMINATED` **634** (new),
`CANDIDATE_PERSISTENCE_TERMINATED` **207** (new) — the two new mechanisms alone account for 841
terminations, roughly a quarter of everything that happens to a v4.5 macro candidate across the full
history. This is the direct, mechanical signature of RANGE-context over-segmentation: constant premature
release and reformation, exactly as section 6.1's statistical negative control predicted.

**Exact v4.4-vs-v4.5 CONFIRMED-episode delta** (matched by start-bar proximity, ≤50 bars — mandate section
15's own "exact overlap/changed/new/lost, every difference must have an explicit lifecycle reason"):

| | Count | Share of v4.4's 187 |
|---|---|---|
| Preserved (same start, duration within 1 day) | 37 | 19.8% |
| Changed (same start, different duration) | 21 | 11.2% |
| **Lost (no v4.5 match at all)** | **129** | **69.0%** |
| New in v4.5 (no v4.4 correspondence) | 1,080 | — (580% of v4.4's own total) |

**69.0% of v4.4's real, genuine CONFIRMED episodes have no corresponding v4.5 confirmation at all.** The
explicit lifecycle reason, uniform across all 129 lost episodes, is the same one section 6.1 already
proved statistically: the real, slowly-converging candidate that would have produced that confirmation was
released early by H-ONE-SIDED or H-PERSISTENCE, and whatever candidate formed in its place, if any,
followed a different, unrelated trajectory. The 1,080 "new" v4.5-only confirmations are the other side of
the same coin — fragments of what would have been ONE coherent, slower-forming range under v4.4, now
split by premature release into multiple, smaller, spuriously-independent candidates, some of which
themselves confirm on far weaker, coincidental geometry. This episode-level view is, if anything, a
STRONGER and more concrete confirmation of the same conclusion section 6.1 reaches statistically, not a
separate finding.

### 6.1 Negative-control validation (mandate's own T-STALE lesson, applied directly)

**This is the finding that determines this mandate's verdict (section 14).** Every one of the 187 real
macro structures that reached `CONFIRMED` under the frozen, UNMODIFIED v4.4 engine across the complete
available history (2011-07-26 through 2026, 355,696 bars) was checked for whether either new v4.5
mechanism would have fired at any bar strictly BEFORE that genuine confirmation — i.e., whether v4.5 would
have released the slot on a candidate that was, in fact, converging toward a real, correct confirmation.

| Mechanism | Real confirmations at risk | Rate | Timing |
|---|---|---|---|
| H-ONE-SIDED | 69 / 187 | **36.9%** | first-fire offset past the `d_macro` age gate: min 13, median 24, max 7,337 bars |
| H-PERSISTENCE | 23 / 187 | **12.3%** | peak pre-confirmation eligible streak reached before confirming: min 23 (barely over the 22-bar threshold), up to 12,226 (over 127 days) |

Method (full scripts preserved in session scratch, reproducible): run the real, unmodified
`RangeSemanticEngineV44` over the canonical history; track, for the currently active macro structure on
every bar, whether each mechanism's OWN firing condition (exactly as implemented in
`range_semantic_v4_5.py`) would evaluate true; whenever a structure reaches `CONFIRMED`, record whether
that condition was EVER true at an earlier bar in that same structure's life. v4.4 itself is never
modified or affected by this check — it is read-only instrumentation layered over the real engine's own
decisions.

**Interpretation**: both rates are far above what closed the prior T-STALE attempt (which, on a much
smaller candidate-outcome sample, saw total false positives double from 8→16). H-ONE-SIDED's own median
first-fire offset — 24 bars, essentially the instant `d_macro=29` makes it eligible to fire at all — shows
it is not catching rare, truly-stuck candidates; it is catching the common, ordinary case where one side
of a forming range simply has not been revisited yet. H-PERSISTENCE's own extreme (12,226 bars, over
127 days) shows that reusing `WEAKENING_MAX_BARS` for a PRE-confirmation question, despite being a
principled, already-frozen, zero-new-parameter choice, does not transfer safely from its ORIGINAL
POST-confirmation domain — touch-count eligibility and price-efficiency convergence are, empirically,
largely independent properties, so "both sides satisfy `n_touch`" says very little about "how soon will
T3's ER/traversal/RND gate also be satisfied." Both findings directly reproduce T-STALE's own closure
reasoning (`GENERALIZATION_NOT_SUPPORTED`, RANGE-context over-segmentation) at materially larger scale and
higher confidence (checked against ALL real confirmations, not a sample). `tests/test_v4_5_liveness.py::
test_live1h`/`test_live1i` demonstrate the same failure class mechanically on small, fast, hand-built
fixtures for readers who want the mechanism without re-running the full validation.

**Why the OR-combination (what is actually implemented) is not safer**: `_candidate_stagnation_reason`
fires H-ONE-SIDED or H-PERSISTENCE, whichever applies. Its false-positive set is therefore a SUPERSET of
H-ONE-SIDED's own 69/187 — the combined mechanism is unsafe by at least as much as its worse component,
not an average or an improvement.

## 7. Data-gap disclosure (mandate section 17)

Verified mechanically (direct CSV parse, not inferred): `data/market/OANDA_XAUUSD_M15.csv` has **no
material gap** anywhere in 2021-2023 — every month shows 1,750-2,150 bars (full FX-session density,
consistent with every other year 2011-2025). Alpha's own diagnosis reproduction processed far fewer bars
for 2021 (15,934) and especially 2022 (873) than are actually available (23,623 / 23,659) — the gap Alpha
disclosed is specific to their own loading pipeline, not the underlying market data this mandate reads
directly. Mandate section 17's own instruction ("keep DETECTOR LIVENESS and DATA AVAILABILITY as separate
issues") is fully resolved by section 6's canonical, full-history numbers: DATA is available and
continuous throughout; the DETECTOR genuinely produces zero `CONFIRMED` bars for 2016-2024 regardless.
The two issues are confirmed separate, and the detector-liveness one is the real, sole cause of the "0
CONFIRMED" finding — not a data-availability artifact, contrary to an earlier draft of this report's own
speculation (retracted, section 2.2).

## 8. Determinism (mandate section 22)

`test_live10_deterministic_replay_same_input_same_output`: 3 independent fresh-engine runs over the same
39-bar synthetic sequence produce byte-identical `(macro_id, macro_state, macro_reason, boundaries,
events)` tuples at every bar. `test_live8_snapshot_restart_across_stagnation_termination_bar_identical`:
a snapshot taken mid-run, restored into a fresh engine, and replayed to completion produces identical
results to an uninterrupted continuous run across a stagnation-termination bar specifically.
`test_live8c_t3_eligible_streak_survives_snapshot_restore`: a targeted check for the ONE piece of new
producer-level state H-PERSISTENCE introduces (the consecutive-eligible-bar counter) — splits a replay
exactly mid-streak, captures and restores just that state, and confirms the resumed run reaches
`CANDIDATE_PERSISTENCE_TERMINATED` at the identical bar an uninterrupted run would.

## 9. Tests (mandate section 23)

**29 new tests**, `tests/test_v4_5_liveness.py`, all passing:

| Category | Tests |
|---|---|
| H-ONE-SIDED reproduction (real shape) + reachability | `test_live1_*`, `test_live1b_*` |
| H-PERSISTENCE reproduction (real shape) + reachability | `test_live1c_*`, `test_live1d_*` |
| Hand-constructed negative controls (both mechanisms — narrower than the real-data check, see below) | `test_live1e_*`, `test_live1f_*`, `test_live1g_*` |
| Real-failure-mode illustrations (mechanical demonstration of the section 6.1 finding) | `test_live1h_*`, `test_live1i_*` |
| Slot liveness | `test_live2_*` |
| Candidate release mechanics (both mechanisms) | `test_live3_*`, `test_live3b_*` |
| No explicit supersession (by design) | `test_live4_*` |
| Invalid/never-confirmed-only termination | `test_live5_*` |
| Confirmation gate unchanged + no auto-promotion (both mechanisms) | `test_live6_*`, `test_live6b_*` |
| Boundary semantics unchanged | `test_live7_*` |
| Restart determinism (incl. streak-counter round-trip, cross-version snapshot refusal) | `test_live8_*`, `test_live8b_*`, `test_live8c_*` |
| v4.4 regression (byte-untouched + behavior unchanged) | `test_live9_*`, `test_live9b_*` |
| v4.5 deterministic replay | `test_live10_*` |
| No M5 detector / M15 authority preserved | `test_live11_*`, `test_live11b_*` |
| Identity / zero-new-parameters / mechanism disjointness | `test_live12_*` through `test_live12d_*` |

**Result**: `29 passed`. Full pre-existing suite (`tests/`, 488 tests covering v3/v3.1/v4.3/v4.4/v4.4.1)
re-run after adding the v4.5 files: **488 passed, 0 failed**. Combined: **517 passed, 0 failed** —
v4.5's mere presence changes nothing about any prior version's behavior. Note what "all passing" means
here and does not mean: every test correctly documents what each mechanism DOES; none of them, individually
or together, establishes that either mechanism is SAFE to deploy — that question is answered (negatively)
only by section 6.1's real-data negative control, which is not and cannot be a unit test.

### mypy --strict

`Success: no issues found` on `range_semantic_v4_5.py` and `range_engine_v4_5.py`. The new test file has
the same 1 pre-existing `import-not-found` note as `test_v4_4_1_stale.py` (the shared
`sys.path.insert`-based cross-test-file import convention, not resolvable by static analysis without a
`MYPYPATH` config change — an existing baseline characteristic of this test directory, not introduced
here; confirmed by checking `test_v4_4_1_stale.py` shows the identical note in isolation, and that
`mypy --strict tests/` already reports over a thousand pre-existing findings across the test directory as
a whole — this directory is evidently not held to strict-clean as a batch, only the `ve_n1_replay/*.py`
implementation modules are).

## 10. Performance (mandate section 24)

Measured directly against the FINAL dual-mechanism implementation (synthetic bars, warm interpreter,
5,000-bar run, measured after the CPU-heavy background regressions above had finished, to avoid
contention skewing the numbers):

| Engine | mean | median | p95 | max |
|---|---|---|---|---|
| v4.4 | 4.777 ms | 4.843 ms | 5.874 ms | 21.847 ms |
| v4.5 | 4.803 ms | 4.864 ms | 5.899 ms | 29.718 ms |

**Incremental overhead: 0.0257 ms/bar (0.54% relative).** Both mechanisms remain cheap: H-ONE-SIDED reads
at most 64 touch tags (`StructureV44`'s own existing memory cap) and only runs for never-confirmed
candidates; H-PERSISTENCE is a single integer increment/compare. Reported here per mandate section 24's
own requirement, despite the `RECOVERY_BLOCKED` verdict — performance was never the limiting factor for
either mechanism, safety was. No optimization performed (none required or relevant given the verdict).

## 11. Rollback

v4.5 is fully additive: two new files (`range_semantic_v4_5.py`, `range_engine_v4_5.py`), one new test
file. `git diff --stat` against `range_semantic_v4_4.py`/`range_engine_v4_4.py` is empty
(`test_live9_v4_4_module_byte_untouched`, enforced as a test, not just claimed). Removing the two new
files and the new test file returns the repository to its exact pre-mandate state; no other file is
touched.

## 12. Limitations (mandate section 27, disclosed not hidden)

**Primary, disqualifying limitation** — restated here because it is the central finding, not a footnote:
both mechanisms fire far too often on real, converging, eventually-successful formations (H-ONE-SIDED
36.9%, H-PERSISTENCE 12.3% of all 187 real 2011–2026 confirmations, section 6.1). Neither is safe to
deploy. This is not a partial or borderline result — H-ONE-SIDED's own median false-positive timing (24
bars, essentially immediate) and H-PERSISTENCE's own extreme (12,226 bars past its own threshold) both
indicate the underlying evidence (early touch imbalance; touch-count eligibility) is a poor predictor of
"will never confirm" specifically because it is common in candidates that DO go on to confirm normally.

**Secondary, narrower limitation** (still real, no longer the operative blocker): a candidate that
receives zero further accepted touches on either side after its founding pair is a shared blind spot for
both mechanisms (lifecycle contract section 9) — not observed in either real lineage this mandate
reproduces, judged low-probability, not fixed here.

**Why no further tuning was attempted within this mandate**: mandate section 8 forbids arbitrary
expiry-parameter tuning and requires either deriving a needed number mechanically from existing frozen
semantic windows, or stopping. Two candidate mechanisms were built exactly that way — each reuses an
already-frozen v4.4 value for a structurally analogous purpose — and both failed decisively. The
negative-control distributions (H-PERSISTENCE's false positives span peak streaks from 23 to 12,226) give
no indication that a different existing value, or a larger/smaller version of one already tried, would
resolve this: the underlying problem is that touch-count and streak-length evidence are, empirically, poor
proxies for "will this candidate ever satisfy T3's price-efficiency gate" — no threshold on THOSE
particular quantities is likely to separate the two populations cleanly. Continuing to try combinations
until one appeared to score better on the same 9 known cases would have reproduced exactly the kind of
post-hoc overfitting mandate section 8 exists to prevent. Stopping and reporting the negative result,
per section 8's own instruction, was judged the correct response.

## 13. Validation handoff

**This artifact is NOT handed to Red Team/Statistician for a "does this generalize" fresh-blind review —
that step is what this mandate's OWN section 6.1 negative control already performed, and it already found
the answer.** T-STALE's own rejection came from exactly this kind of validation being performed by a
LATER, separate mandate; this mandate performed the equivalent validation itself, before ever presenting
the artifact as ready. There is nothing left to hand off for THIS specific pair of mechanisms — they are
closed, not pending.

What IS appropriately handed off: the disproof itself, and the open question it leaves. If Alpha Discovery
or a future VE mandate wants to pursue liveness recovery again, the negative-control METHOD used here
(check every real confirmation, not a hand-picked sample) is reusable and should be applied to ANY future
candidate mechanism before it is considered for deployment, not after. Given both of the two most natural,
zero-new-parameter designs failed, a future attempt may need either (a) a genuinely different signal not
yet tried (something other than touch-count evidence or elapsed-bar persistence), or (b) explicit CEO
authorization for a new, PROPERLY VALIDATED research parameter (mandate section 8's own escape hatch,
`RANGE_V4_5_LIFECYCLE_PARAMETER_REQUIRES_RESEARCH_AUTHORIZATION`) — which this mandate does not request on
its own initiative, consistent with section 8's own framing that this decision belongs to the CEO, not VE.

## 14. Verdict (mandate section 28)

- **`RANGE_V4_5_RECOVERY_BLOCKED`**
- **`RANGE_LIFECYCLE_RESEARCH_REQUIRED`**

Both candidate mechanisms (H-ONE-SIDED, H-PERSISTENCE) were designed using only already-frozen v4.4
values, with zero new config fields, satisfying mandate section 5's "not a retune" requirement and section
8's "no arbitrary expiry tuning" requirement in construction. Both correctly reproduce and resolve their
targeted real stuck-candidate shape (section 3/4, positive fixtures against macro_id 770 and 893). **Both
fail mandatory negative-control validation against real data, confirmed by two independent methods**:

- **Streak-level** (section 6.1): H-ONE-SIDED would have prematurely released 69 of 187 (36.9%) real,
  genuine confirmations; H-PERSISTENCE would have prematurely released 23 of 187 (12.3%).
- **Episode-level, full-history regression** (section 6): of v4.4's 187 real CONFIRMED episodes, only 37
  (19.8%) survive intact under v4.5; **129 (69.0%) are lost entirely**, replaced by 1,080 new, mostly
  fragmentary v4.5-only confirmations with no correspondence to any real v4.4 event.

Both figures describe the same underlying failure — RANGE-context over-segmentation, the identical
mechanism that closed the prior T-STALE attempt — measured two different ways, at a materially larger
scale and higher confidence than T-STALE's own rejection was based on. Per mandate section 28's own
explicit provision for this outcome ("if a non-arbitrary lifecycle rule cannot be implemented... STOP"),
this mandate does not proceed to deploy, ratify, or recommend either mechanism, does not declare v4.5 a
v4.4 replacement, and does not hand this artifact to Alpha as approved evidence. **v4.4 remains the sole,
permanently frozen RANGE baseline; its known, accepted-since-freeze liveness limitation (mandate section
4) remains open and unresolved by this mandate.**

**Also confirmed, not blocking but material**: Alpha's root-cause diagnosis is NOT falsified —
`RANGE_V4_5_ROOT_CAUSE_MISMATCH` does not apply, and an earlier draft of this report's own speculative
partial-mismatch hypothesis is explicitly RETRACTED (section 2.2). The underlying mechanism
(single-active-MACRO-slot + unmet confirmation gate) is real, independently reproduced from source, and
found to be dramatically MORE severe than Alpha's own report stated: v4.4 shows zero `CONFIRMED` bars not
for 2021-2023 alone but for nine consecutive years, 2016-2024, driven by one single candidate (macro_id
770) that does not release the slot until 2025-04-07 — 9.7 years after it formed. The underlying market
data has no gap (section 7); this is a genuine, severe, and now precisely-quantified Market Intelligence
liveness defect, exactly the kind of problem this mandate's own premise says is worth solving — the
verdict on THIS mandate's two specific repair attempts does not diminish that.

**Also disclosed, a genuine methodological lesson from this mandate's own process**: the original
9-episode "positive validation" (section 3's table) that seemed to support both mechanisms was itself
built from a duration-only filter, not a `reached_confirmed`-aware one — 8 of those 9 episodes turned out,
on later correct checking, to be real eventual confirmations, not permanently-stuck candidates. "Firing on
them" was, in retrospect, an early and unrecognized preview of exactly the failure the full negative
control later found systematically. This is recorded not to relitigate the design (which was reasonable
given what was known at the time it was proposed) but because it is a directly reusable lesson for any
future liveness-recovery attempt: duration alone does not distinguish "stuck" from "slow", and any
positive validation set for this class of problem must be filtered by actual outcome, not merely by how
long a candidate remained active.

Implementation, tests, and both documents are kept in the repository in full — not deleted — as the
institutional record of what was tried, why it looked principled, and exactly how and why it failed,
mirroring T-STALE's own disposition after its rejection.
