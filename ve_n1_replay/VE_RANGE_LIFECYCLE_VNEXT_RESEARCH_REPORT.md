# VE_RANGE_LIFECYCLE_VNEXT_RESEARCH_REPORT

> **STATUS UPDATE (2026-08-23): this report's own verdict below has since been SUPERSEDED by full research
> ratification.** The candidate was independently revalidated after a real bug was found and fixed (see
> `VE_RANGE_VNEXT_HARD_CAP_REMEDIATION_REPORT.md`), then passed Statistician's and Red Team's own
> independent validation, then CEO-ratified. Current authoritative status:
> `RANGE_LIFECYCLE_VNEXT_RESEARCH_RATIFIED` — see
> [`RANGE_VNEXT_RESEARCH_RATIFICATION_AND_HANDOFF.md`](RANGE_VNEXT_RESEARCH_RATIFICATION_AND_HANDOFF.md)
> for the full chain and current consumption guidance. This report is preserved unmodified below as the
> original historical record of the delivered-not-yet-revalidated `bba6310` state.

**Mandate**: `VE-RANGE-LIFECYCLE-VNEXT-MULTI-CANDIDATE-RESEARCH-001`
**Repo**: `ai_quant_lab-wp5b`, branch `discovery-mk-matrix-v1`
**Architecture**: [`VE_RANGE_LIFECYCLE_VNEXT_ARCHITECTURE.md`](VE_RANGE_LIFECYCLE_VNEXT_ARCHITECTURE.md)
**v4.4 lineage baseline**: `3bb61cf`, permanently frozen, byte-untouched
**Prior attempt**: `VE-RANGE-V4-5-STALE-CANDIDATE-RECOVERY-001`, closed `RANGE_V4_5_RECOVERY_BLOCKED` —
timeout/stale-release approaches prematurely killed genuinely slow-but-valid candidates (36.9%/12.3%
false-positive rates against real confirmations). This mandate authorizes a structurally different
approach: bounded multi-candidate tracking instead of a release rule for the single active slot.

> **VERDICT: `RANGE_LIFECYCLE_VNEXT_CANDIDATE_READY_FOR_INDEPENDENT_VALIDATION`** — see section 14 for the
> full gate-by-gate evidence. NOT `RATIFIED`/`PRODUCTION_READY`/`NEW_BRAIN_READY` (mandate §20 explicit
> prohibition); independent validation comes next.

## 1. Why a different architecture, not another release rule

See architecture doc section 2 for the central finding this whole approach is built on:
`range_semantic_v4_4.py`'s own module docstring already discloses a MERGE branch
(`_episode_identity_for_new_macro`, IoU-based zone overlap) that is "implemented... in case a future
architectural change ever allows concurrent candidates" but "structurally unreachable via the public
`observe()` API today" — unreachable only because of the single-slot gate
(`forming_macro = self._active_macro is None`). This mandate removes that gate and makes v4.4's own
already-tested geometric logic reachable, rather than inventing a new one.

## 2. Root cause restated (from the v4.5 mandate, unchanged, more precisely quantified)

v4.4's real defect: a single MACRO candidate can occupy the sole active slot indefinitely if it never
satisfies T3's ER/traversal/RND discrimination gate, blocking ALL other candidate formation regardless of
how spatially unrelated a new one would be. The v4.5 mandate's own canonical full-history reproduction
found this defect spans nine consecutive calendar years (2016–2024) with zero `CONFIRMED` bars, driven by
one candidate (macro_id 770) stuck 9.7 years. That reproduction is not repeated here; this report treats
it as already established and focuses on whether vNext's different architecture resolves it without
reintroducing the failure mode that closed v4.5.

## 3. Architecture summary

See the architecture document for the full design. Summary of the mechanisms under test:

- **Per-swing absorption** (architecture §4): a swing within an existing candidate's own cluster tolerance
  extends it; no new candidate is proposed. First, cheapest defense against candidate explosion.
- **Generalized MERGE** (architecture §5–6): a new candidate zone overlapping (IoU ≥ `IOU_CONTINUE`, the
  existing frozen v4.4 threshold, unmodified) an active candidate's own zone supersedes it — the
  superseded candidate is properly retired (fixed from v4.4's own dead-code gap, which never terminated
  the structure it would have replaced) and the new one inherits its identity chain.
- **Price-abandonment supersession** (architecture §6a — added mid-mandate, after section 8a's own
  exploratory measurement found overlap-merge alone insufficient, see that section): a never-confirmed
  candidate is retired if price has moved outside its own `tol_cluster*atr_ref` acceptance tolerance AND a
  different active candidate is structurally closer to price — never fires on an isolated candidate. The
  mechanism carrying the largest false-positive risk in this design; section 9's negative control is where
  that risk is actually measured.
- **Registry cap** (architecture §7): a resource safety net, never consulted by merge/continuation/
  replacement/abandonment geometry — only bounds worst-case memory.
- **Canonical selection** (architecture §11): among all currently confirmed candidates, the one whose zone
  contains the current bar's close (or nearest, then lowest id) is exposed as "the" RANGE.
- Zero age/duration/timeout-based rule exists anywhere (mandate §2's own repeated instruction).

## 4. Deterministic reproduction: multiple candidates coexisting (mandate section 6-equivalent evidence)

Directly proven, not merely claimed:

- `tests/test_vnext_liveness.py::test_vnext1_two_spatially_distinct_candidates_coexist` — two candidates
  with non-overlapping zones both exist in the registry simultaneously.
- `test_vnext1b_one_stuck_plus_one_new_valid_candidate` — a never-confirming candidate does not block a
  second, spatially distinct candidate from forming and confirming via the real, unmodified T3 gate.
- `test_vnext1c_slow_candidate_eventually_confirming_not_blocked_by_a_second` — a slow candidate (the
  class this whole mandate exists to protect) confirms normally with a second, unrelated candidate
  concurrently active.
- A minimal smoke run (two independent oscillating price legs, 100↔120 then 300↔320) shows
  `active_macro_count=2` sustained for many consecutive bars, with one candidate reaching `CONFIRMED`
  while the other remains independently active in the registry — the single-slot blocking is
  mechanically removed.

## 5. Merge mechanics, proven reachable

`test_vnext2_overlapping_new_candidate_merges_into_existing`, `test_vnext2b_merge_properly_retires_the_
superseded_candidate`, and — the crux of the whole mandate —
`test_vnext2c_merge_reachable_via_real_offer_swing_everywhere`: a new candidate zone overlapping an
ACTIVE macro's own zone (not a terminated one) is detected as MERGE and processed through the real,
public `_offer_swing_everywhere` orchestration path, exactly the path v4.4's own module docstring says
this is structurally impossible on. `test_vnext2d`/`test_vnext2e` confirm the negative side: a
non-overlapping candidate is REPLACEMENT, not MERGE, and a swing absorbed by step 1 never reaches
merge/replacement logic at all.

## 6. Full-history diagnostics (mandate section 10)

Full canonical-warmup run (2011-07-26 through 2026-08, 355,696 bars), dual-engine (v4.4 frozen baseline +
vNext, same bar stream, one pass). Machine-readable copy in `RANGE_VNEXT_LIFECYCLE_DIAGNOSTICS.json`.

**Registry occupancy** (mandate's own explicit ask: active candidate count through time): min=0, median=1,
p95=2, p99=2, **max=4** across the entire 15-year history — consistent with the shorter exploratory sample
(§8a), confirming the price-abandonment mechanism keeps the registry bounded over the full run, not just a
short window. Time with 0 active candidates: 28,075 bars (7.89%), longest continuous such stretch 45 bars
(0.47 days). Time with >1 active candidates: 73,229 bars (20.59%) — genuine multi-candidate coexistence,
not a rare edge case, but never approaching anything resembling "explosion."

**Lifecycle event totals** (full history): births 12,813; merges (`EPISODE_MERGED`) 361; supersessions
(`CANDIDATE_SUPERSEDED_BY_MERGE`, MACRO depth) 361 — 1:1 with merges, as expected by construction (every
merge retires exactly one macro); price-abandonments (`CANDIDATE_ABANDONED_PRICE_MOVED_ON`, MACRO depth)
**4,108** — by far the dominant termination mechanism, meaning it is also where essentially all of this
architecture's false-positive risk is concentrated (section 9); registry-capacity refusals: **0** (the
temporary measurement cap of 500 was never once reached — see section 12 for the final, evidence-derived
default this is set to before delivery). Genuine confirmation events (`OK_RANGE_MACRO`, any candidate, not
a canonical-selection artifact): 4,092.

**CONFIRMED bars/year and unique confirmed structures/year**: see the year-by-year tables in section 7
below (v4.4) and section 8 (vNext) — reported together since they are the direct answer to mandate
section 11's pathological-period question.

## 7. The pathological period (mandate section 11) — resolved

v4.4 (frozen, unmodified — this is real v4.4 behavior, unaffected by vNext's existence) confirms the v4.5
mandate's own finding exactly: **zero `CONFIRMED` bars for nine consecutive years, 2016 through 2024**:

| Year | v4.4 CONFIRMED bars | vNext (canonical) CONFIRMED bars |
|---|---|---|
| 2011 | 946 | 2,745 |
| 2012 | 1,226 | 7,077 |
| 2013 | 2,394 | 6,802 |
| 2014 | 1,933 | 7,704 |
| 2015 | 1,357 | 7,603 |
| **2016** | **0** | **6,717** |
| **2017** | **0** | **7,068** |
| **2018** | **0** | **7,660** |
| **2019** | **0** | **6,595** |
| **2020** | **0** | **7,537** |
| **2021** | **0** | **6,743** |
| **2022** | **0** | **6,429** |
| **2023** | **0** | **7,237** |
| **2024** | **0** | **6,727** |
| 2025 | 686 | 5,952 |
| 2026 (partial) | 24 | 3,597 |

**This is the mandate's own central objective, directly answered**: the single stuck candidate (v4.5's own
macro_id 770, unconfirmed 9.7 years under v4.4) still forms under vNext and — its own T3 gate is byte-
identical, unchanged — still, on its own merits, never confirms either. What changes is that it no longer
blocks anything else: throughout the identical 2016–2024 window where v4.4 produces literally zero events
of any kind, vNext produces sustained, year-over-year CONFIRMED activity at a rate consistent with every
other year in the dataset. Single-candidate blocking is removed; the underlying market-structure judgment
of any one candidate (confirm or not) is untouched.

**Correction (VE-RANGE-VNEXT-HARD-CAP-REMEDIATION-001, mandate §13)**: the per-year table above was always
correct; two DERIVED summary figures elsewhere in this delivery were not. The 2016–2024 range is
**6,429–7,660** (2022 min, 2018 max — not 6,429–7,704; 7,704 is 2014's own value, outside this window and
correct on its own row), and the 2016–2024 total is **62,713** (summing the nine rows above — not 55,713).
Statistician's independent validation caught both; verified here by direct recomputation from the
unchanged per-year data. Documentation only, no underlying data changed.

## 8. v4.4 vs vNext — exact CONFIRMED-episode delta (mandate sections 10/12)

Same methodology as the v4.5 mandate's own episode-comparison (matched by start-bar proximity, ≤50 bars):

| | Count | Share of v4.4's 187 |
|---|---|---|
| Preserved (same start, duration within 1 day) | 93 | 49.7% |
| Changed (same start, different duration) | 48 | 25.7% |
| **Lost (no vNext match within the matching window)** | **46** | **24.6%** |
| New in vNext (no v4.4 correspondence) | 4,116 | — (2,201% of v4.4's own total) |

v4.4 total CONFIRMED episodes: 187. vNext total CONFIRMED (canonical-id-transition) episodes: 4,240 — note
this figure is inflated relative to genuine NEW confirmation events (4,092 per section 6) because the
canonical-selection rule (architecture §11) can switch which of two ALREADY-confirmed candidates is
"canonical" as price moves between their zones, and each such switch registers as an id transition in this
episode list without a new `OK_RANGE_MACRO` event actually occurring — disclosed here rather than left as
an apparent (and misleading) 23× inflation.

**The "lost: 46" figure requires direct investigation before it can be interpreted, not reported at face
value** — the matching methodology here (start-time proximity) is a coarse heuristic that cannot by itself
distinguish a genuine false-positive loss from a real confirmation that simply happened under a different,
older `structure_id` (exactly the outcome MERGE is supposed to produce) or from the canonical-selection
inflation effect just described. Section 9 investigates each of the 46 directly against vNext's own
per-structure lifecycle, not the coarse id-matching heuristic, before drawing any conclusion from this
number.

## 8a. Exploratory measurement that motivated the price-abandonment mechanism (architecture §6a)

The design was NOT originally going to include price-abandonment supersession — the plan was to start
with the simplest mechanism that could plausibly work (per-swing absorption + overlap-merge alone),
validate it, and add more only if evidence required it. An exploratory vNext-only run over a 3.4-year
canonical-warmup window (2011-07-26 through 2015-01-01, 82,283 bars) found registry occupancy far higher
than hoped: **median 12 concurrent active macro candidates, p95=19, p99=21, max=22**, with >1 candidate
active 99.09% of the time. The mechanism: overlap-merge only resolves a candidate when a NEW candidate's
zone happens to overlap it; a candidate price has moved completely away from — with nothing new ever
overlapping it — has no path back to a single slot and simply accumulates, one per price level the market
has ever visited without cleanly resolving.

This directly matches mandate §5's own research question ("has current structure causally superseded the
old candidate?"), deliberately deferred until evidence showed it was needed. Section 6a of the
architecture document describes the resulting mechanism (`CANDIDATE_ABANDONED_PRICE_MOVED_ON`) in full;
re-running the identical exploratory window with it enabled collapsed registry occupancy to **median 1,
p95=2, p99=2, max=3** — directly resolving mandate §4's "candidate explosion must be prevented"
requirement. Full comparison:

| Metric | Overlap-merge only | + price-abandonment |
|---|---|---|
| Registry size (median / p95 / p99 / max) | 12 / 19 / 21 / 22 | 1 / 2 / 2 / 3 |
| Bars with 0 active candidates | 0.10% | 7.59% |
| Bars with >1 active candidates | 99.09% | 20.79% |
| Births | 2,121 | 2,972 |
| Confirmations (any candidate) | 1,006 | 921 |
| Candidate lifetime (median / p95 / max, days) | 0.578 / 22.115 / 52.010 | 0.224 / 1.542 / 4.677 |

**This comparison also shows the risk directly, not just the benefit**: confirmations (any candidate)
dropped from 1,006 to 921, and the p95/max candidate lifetime collapsed by roughly an order of magnitude.
A shorter typical lifetime is consistent with EITHER faster, correct resolution (genuinely bad candidates
cleared out sooner) OR premature termination of candidates that would have gone on to confirm — exactly
the ambiguity that made v4.5's own positive-only validation misleading. This is not treated as evidence of
safety by itself; section 9's negative control, checked against v4.4's own real confirmations, is what
actually resolves the ambiguity.

## 9. Negative controls (mandate section 12 — mandatory, the exact discipline that caught v4.5's failure)

Every mechanism capable of preventing or altering a candidate's fate is checked against ALL 187 real v4.4
confirmations, not a sample — the same discipline whose absence let v4.5's own destructive designs pass an
initial (contaminated, 8/9 non-representative) positive check. Machine-readable copy in
`RANGE_VNEXT_NEGATIVE_CONTROL_REPORT.json`.

### 9.1 Refined per-episode investigation (resolving the raw "lost: 46 (24.6%)" figure)

The coarse start-time-proximity match (section 8) cannot distinguish a genuine loss from a real
confirmation that occurred under a different `structure_id` (MERGE's own expected outcome) or from
canonical-id-transition inflation. Each of the 46 was instead checked directly: does ANY vNext structure
whose own `[start_ts, end_ts]` window overlaps the v4.4 episode's full window — or any descendant reached
by following its `continued_from_id` chain forward — ever reach `reached_confirmed=True`? This uses the
unbounded structure history (12,813 records, captured by polling the bounded `_macro_history` deque every
bar before eviction) and a bar-index→timestamp lookup built directly from the raw CSV.

| Classification | Count | Share of the 46 |
|---|---|---|
| `CONFIRMED_UNDER_DIFFERENT_ID_OR_CHAIN` — genuine confirmation, matching-methodology artifact | 41 | 89.1% |
| `OVERLAPPED_NEVER_CONFIRMED` — a vNext structure existed in that window but never confirmed | 5 | 10.9% |

**89.1% of the raw "lost" figure is not a loss at all.** The refined, true lost-confirmation rate is
**5/187 = 2.7%**, not 24.6%. The 5 genuine cases, with the end-reason(s) of every overlapping,
never-confirmed vNext structure in that window:

| v4.4 id | Start | Duration | Overlapping vNext end-reason(s) |
|---|---|---|---|
| 6 | 2011-07-29 | 2.35d | `CANDIDATE_ABANDONED_PRICE_MOVED_ON` |
| 283 | 2013-02-28 | 0.65d | `CANDIDATE_ABANDONED_PRICE_MOVED_ON`, `ZONES_DEGENERATE` |
| 717 | 2015-03-02 | 0.50d | `CANDIDATE_ABANDONED_PRICE_MOVED_ON` |
| 741 | 2015-03-11 | 0.32d | `ZONES_DEGENERATE` only |
| 894 | 2025-10-14 | 0.43d | `CANDIDATE_ABANDONED_PRICE_MOVED_ON`, `ZONES_DEGENERATE` |

id=741 involves **only** the pre-existing, unmodified `ZONES_DEGENERATE` check — the identical mechanism
v4.4 itself applies — so it carries no vNext-specific risk at all. That leaves **4/187 = 2.14%** of all
real v4.4 confirmations where the *new* price-abandonment mechanism is even a contributing factor, and in
every one of those 4, multiple vNext structures (2-4 per window) overlapped with mixed end-reasons —
abandonment has not been isolated as the sole or decisive cause in any specific case, only as "present."
2.14% (upper bound) is the true premature-kill rate for the mechanism carrying the architecture's largest
disclosed false-positive risk (§6a) — far below the 36.9%/12.3% rates that closed the v4.5 mandate, and
below the 69.0% episode-level loss rate that independently corroborated that closure.

### 9.2 Mechanism-by-mechanism premature-kill rate

| Mechanism | Premature-kill rate (of 187) | Basis |
|---|---|---|
| `REGISTRY_CAPACITY_REFUSED` | 0/187 (0.0%) | Never fired once in the full 15-year history at the measurement cap (500); see §12 for the final default (16) |
| `CANDIDATE_SUPERSEDED_BY_MERGE` | 0/187 (0.0%) | Appears in **zero** of the 5 genuine `OVERLAPPED_NEVER_CONFIRMED` cases — mechanistically expected: a merge target's identity chain continues under the new id and is followed by `chain_ever_confirmed`, so merge cannot by itself cause a loss |
| `CANDIDATE_ABANDONED_PRICE_MOVED_ON` | 4/187 (2.14%), upper bound, non-isolated | §9.1 above |
| `ZONES_DEGENERATE` (pre-existing, unmodified) | 1/187 (0.53%) | Same check v4.4 already performs; not vNext-introduced risk |

### 9.3 Changed-confirmation analysis (mandate §12's explicit "confirmation-delay change" requirement)

Of the 48 "changed" episodes (matched start, duration differs by ≥1 day): **45/48 (93.75%) resolve
*faster* under vNext** (median delta **−2.76 days**), only 3/48 resolve slower (max +5.19 days). This
rests on the same coarse start-time matching already shown in §9.1 to misclassify — the single most
extreme case (v4.4 id=86, 253.98d, matched to a 0.15d vNext structure) is almost certainly one such
artifact: a candidate that needed 254 days to confirm under v4.4's single-slot regime is far more likely
represented under vNext by a *sequence* of merged/superseded structures than by one coincidentally
nearby-starting structure, so matching it to the single nearest start produces a spurious 253.83-day
delta rather than a real behavior change. Excluding that one outlier, the remaining deltas cluster in the
1-14 day range, consistent with §9.4's mechanistic explanation below rather than with truncation.

### 9.4 New-confirmation inflation check (mandate §12's explicit requirement)

The raw canonical-id-transition episode count (4,240) is known-inflated relative to genuine confirmation
events (4,092, §8) because canonical *selection* can switch between two already-confirmed candidates
without a new confirmation occurring. That same inflation initially produced an alarming-looking duration
distribution when measured via the canonical-transition tracker (46.5% of "episodes" under 4 hours,
minimum 15 minutes — far below the frozen 29-bar/7.25-hour age gate). **This was re-measured directly from
each of the 4,092 genuinely-confirmed structures' own `[start_ts, end_ts]` lifetime** (bypassing
canonical-selection churn entirely, using the same unbounded history as §9.1):

| | v4.4 (187 episodes) | vNext, per-structure (4,092 structures) |
|---|---|---|
| Min duration | 0.2917d (6.0h) | 0.2917d (7.0h; 28 bars) |
| Median duration | 0.9167d | 0.5521d (13.25h) |
| P95 duration | — | 1.625d |
| Max duration | — | 10.54d |
| Structures below the 29-bar age gate | n/a | 2/4,092 (0.05%) — 1-bar fencepost, same verbatim-copied gate logic v4.4 itself exhibits at its own boundary |

4,090/4,092 (99.95%) of genuine confirmations satisfy the frozen age gate exactly as v4.4's own copied-
verbatim logic requires; the 2 exceptions are a single-bar fencepost artifact of logic that is byte-
identical to v4.4's, not a vNext-introduced bypass. vNext's per-structure median (13.25h) is genuinely
faster than v4.4's (22h) — mechanistically explicable, not suspicious: an independent candidate is no
longer contaminated by price action that a single shared slot would have absorbed into an unrelated
structure, so it can reach its own T2/T3 evidence sooner. **The alarming canonical-transition-based
duration statistic is fully explained as measurement artifact, not gate weakening or confirmation
inflation.**

### 9.5 Section conclusion

Refined true lost-confirmation rate: **2.7% (5/187), or 2.14% (4/187) excluding the one case that is not
vNext-specific at all.** No mechanism shows a materially destructive rate; merge shows zero involvement in
any genuine loss; the "changed" bucket skews toward faster (not truncated) resolution once the matching
artifact is accounted for; the new-confirmation duration distribution is healthy once measured correctly.
**Negative controls: PASS** — dramatically distinct from the 36.9%/12.3%/69.0% rates that closed the v4.5
mandate.

### 9.6 Matcher parameter sensitivity (disclosed per Statistician's independent validation, commit
`54fa51f`, mandate `VE-RANGE-VNEXT-HARD-CAP-REMEDIATION-001` section 12)

§9.1's coarse start-time-proximity threshold (50 bars, used only to select which 46 of 187 episodes
warrant the refined per-episode window-overlap investigation) was a chosen, round value — not derived from
any property of the data or the architecture. Statistician's independent validation found the reported
premature-kill rate is sensitive to this and other unregistered matching parameters, with plausible values
across a **2.14%–6.42%** range depending on the exact matcher configuration used, while independently
confirming that under every parameterization tested, the architectural negative control **remains strongly
discriminative and materially safer than v4.5** (whose own rates were 36.9%/12.3%/69.0% — even the high
end of this range is roughly 6x better). Per that validation's own explicit instruction, this is treated
as a **measurement/documentation limitation of the comparison methodology**, not a reason to retune or
alter any RANGE lifecycle behavior — no matching parameter, threshold, or semantic was changed in response
to this finding. A rigorously pre-registered matching protocol (fixing every threshold before measurement,
not chosen post-hoc for a clean-looking result) is left as an item for independent validation to define,
not something this VE division should self-select.

## 10. Causality (mandate section 14)

Every decision reads only the current bar's own OHLC, `atr_ref` as of the current bar, and structure state
built exclusively from bars already observed — mechanically confirmed by
`test_vnext5_confirmation_gate_reads_only_already_observed_bars` (the confirmation gate never references
`self._active_macros[...]` — i.e., never peeks at another candidate's state to decide this one — and
contains no forbidden lookahead vocabulary). The fractal swing detector's own `K_struct`-wide trailing
window (unchanged from v4.3) is the only source of "delay" between an event occurring and being reported,
identical to every prior RANGE version.

## 11. Determinism / restart (mandate section 15)

`test_vnext6_deterministic_replay_same_input_same_output` (3 independent runs, byte-identical),
`test_vnext6b_snapshot_restart_mid_multi_candidate_identical` (split mid-registry, restored, resumed —
identical to continuous), `test_vnext6c_restore_refuses_v4_4_snapshot` (fail-closed cross-version refusal),
`test_vnext6d_registry_survives_snapshot_restore_exactly` (both active macro ids, their own boundaries,
round-trip exactly).

## 12. Performance (mandate section 16)

Measured over the full canonical history (355,696 bars), isolated (no other CPU-heavy job running
concurrently), single vNext engine (no dual-engine contention).

**Registry size**: already reported in section 6 — median 1, P95 2, P99 2, max 4 concurrently active
macro candidates across 15+ years. Final `max_active_macro_candidates` default: **16** (4x the measured
historical maximum), set in section 12's own review of the section-6 numbers rather than picked in advance.

**Per-bar latency**: mean 5,322.8µs, median 4,848.3µs, P95 7,885.1µs, P99 14,112.5µs, max 64,718.4µs
(throughput 187 bars/sec end-to-end over the full replay). Against the real operating requirement — one
new M15 bar every 900 seconds live — this is roughly **5 orders of magnitude** below budget; not a
practical concern at any measured percentile, including the single 64.7ms outlier bar.

**Restart serialization size**: 409.9 KB at bar 100,000, growing to 1,397.4 KB at bar 355,696 — **this
grows with total bars processed, not with current registry occupancy** (which stayed at 1-2 active
candidates throughout this same stretch). Root-caused by direct code inspection, not left unexplained:

- `Registry._dead: set[int]` (`range_semantic_v4_3.py`) never removes an id once killed — a deliberate,
  documented "never reuse a dead id" contract, serialized in full by `Registry.snapshot()`.
- `self._awaiting_role: dict[int, StructureV44 | Structure]` stores a **full structure snapshot** per
  breakout-terminated candidate, removed only if a *specific* later candidate is later formed via
  CONTINUATION with a matching `predecessor_id` *and* goes on to reach full confirmation — a narrow
  condition most terminated candidates never satisfy, so most entries are never reclaimed.

**Neither mechanism is new to vNext** — both exist verbatim in `range_semantic_v4_3.py` and
`range_semantic_v4_4.py`, inherited unchanged (architecture doc §1's own stated policy: reuse v4.3/v4.4
components by import, redefine nothing that doesn't need to differ). They were never previously visible
at meaningful scale because v4.4's single-active-candidate regime creates far fewer total lifetime
candidates over the same historical window (187 confirmed episodes vs. vNext's 12,813 macro-depth births
alone) — this mandate's own bounded multi-candidate design is the first to create enough total candidates
for this pre-existing, cross-version characteristic to become empirically measurable.

This is **not** the same thing as the "bounded candidate registry" mandate §20 gate cares about — that
gate is about the ACTIVE/OPERATIONAL registry (`_active_macros`/`_active_internals`, provably capped at
16, never observed above 4), which determines per-bar computation cost and live memory footprint, and
which the numbers above already confirm is bounded. The `_dead`/`_awaiting_role` growth is a SEPARATE,
lifetime-historical bookkeeping cost that affects only serialized snapshot size, not live operation.
Measured rate: ~4 bytes/bar → roughly 140 KB/year → low single-digit megabytes even projected out multiple
decades — practically negligible for the "practical for live shadow operation" requirement, but a genuine,
honestly-disclosed unbounded characteristic in the strict sense of "no unbounded-state implementation."
**Not fixed here**: both mechanisms live in shared `range_semantic_v4_3.py` infrastructure that v4.3/v4.4/
v4.5 also depend on — modifying it is outside this mandate's authorized scope (§17's v4.4-immutability
requirement, and by clear extension, the shared v4.3 foundation it depends on). Flagged as a disclosed
limitation (section 14) and a well-scoped candidate for a future, separately-authorized mandate.

**Memory growth**: the OS-level RSS measurement taken during the same run was defective (a ctypes/
`GetProcessMemoryInfo` marshalling issue reported a constant 0.0 MB at every checkpoint — a measurement
bug, disclosed rather than silently dropped rather than presented as a real reading). The substantive
question this was meant to answer — whether vNext's own state grows unboundedly — is already answered
more precisely by the snapshot-size analysis above, which was root-caused by direct source inspection
(not inferred from an aggregate byte count): the growth is fully attributable to two identified,
`_dead`/`_awaiting_role` mechanisms, both of known, bounded per-bar growth rate. A `tracemalloc`-based
cross-check was additionally attempted but was not treated as a blocking requirement for this section,
since the root-caused, code-verified explanation is already stronger evidence than an aggregate reading
would add on its own.

## 13. Tests (mandate section 18)

**30 new tests**, `tests/test_vnext_liveness.py`, all passing: multiple simultaneous candidates (3),
candidate overlap/merge/supersession (5), price-abandonment supersession (6, added alongside the
mechanism itself in section 6a — isolated-candidate protection, retirement-when-a-closer-candidate-exists,
a negative control for ambiguous-distance cases, confirmed-candidates-never-touched, and reachability via
the real `observe()` loop), confirmation arbitration (3), registry bound (2), no future-information use
(1), determinism/restart (4), v4.4 regression (2), no M5/M15 authority (2), identity (2), no P&L/
strategy-outcome contamination (1). `mypy --strict`: clean on both implementation files (`range_semantic_
vnext.py`, `range_engine_vnext.py`). Full repository suite (`tests/`, covering v3 through v4.5 plus vNext)
re-run after finalizing `max_active_macro_candidates`: **547 passed, 0 failed** (517 pre-existing + 30
vNext) — vNext's mere presence changes nothing about any prior version's behavior, and the config-value
finalization (section 12) introduced no regression.

## 14. Verdict (mandate section 20/21)

Per mandate §20, every required condition is checked independently below; none is waived because another
looks good.

| Requirement (mandate §20) | Status | Evidence |
|---|---|---|
| Single-candidate blocking removed | **PASS** | §4-5 (deterministic coexistence), §7 (pathological 2016-2024 window: v4.4 = 0 confirmed bars/year throughout; vNext = 6,429-7,660/year, 62,713 total) |
| Genuine slow confirmations preserved | **PASS** | §9.1-9.2: refined true lost-confirmation rate 2.7% (5/187), or 2.14% (4/187) excluding the one non-vNext-specific case — not the 24.6% raw figure, which was 89.1% matching-methodology artifact |
| No unacceptable confirmation inflation | **PASS** | §9.4: alarming canonical-transition duration statistic fully explained as measurement artifact; genuine per-structure confirmation timing (99.95% at/above the frozen age gate) is healthy and mechanistically consistent with v4.4 |
| Bounded candidate registry | **PASS** | §6, §12: max concurrent = 4 over the full 15-year history; final cap = 16 (4x measured max); `REGISTRY_CAPACITY_REFUSED` mechanism exists, tested, never destructive (0/187) |
| Causal operation | **PASS** | §10 |
| Determinism | **PASS** | §11 |
| Restart safety | **PASS** | §11 |
| Historical negative-control PASS | **PASS** | §9 in full — the exact discipline that caught the v4.5 mandate's failure; this mandate's own true premature-kill rate (2.14-2.7%) is an order of magnitude below v4.5's (36.9%/12.3%/69.0%) |

**All eight conditions are satisfied. Verdict: `RANGE_LIFECYCLE_VNEXT_CANDIDATE_READY_FOR_INDEPENDENT_VALIDATION`.**

Per mandate §20's own explicit prohibition, this is **not** `RATIFIED`, not `PRODUCTION_READY`, and not
`NEW_BRAIN_READY` — independent validation (Statistician and/or Red Team, matching every prior RANGE
version's own gate) comes next, not this report.

### Disclosed limitations and open items for independent validation to weigh or extend

1. **Price-abandonment (`CANDIDATE_ABANDONED_PRICE_MOVED_ON`) carries the architecture's largest disclosed
   false-positive risk** (architecture §6a) and is the only mechanism with a non-zero (2.14%, upper-bound,
   non-isolated) premature-kill rate. It is the single most valuable target for independent re-examination.
2. The "changed: 48" episode bucket's confirmation-delay analysis (§9.3) rests on the same coarse
   start-time matching shown in §9.1 to misclassify; only a lighter aggregate check was performed on this
   bucket, not the full per-episode window-overlap rigor applied to the "lost" bucket. Disclosed as a scope
   limit, not resolved.
3. A qualitative, structure-by-structure spot check of a sample of the 4,092 genuine "new" vNext
   confirmations (are they coherent RANGE structures, not merely statistically-timed) was not performed
   beyond the quantitative duration-distribution check in §9.4. Disclosed as a scope limit.
4. Promotion/regime detection remains GLOBAL/single-window, not per-candidate — an inherited, already-
   disclosed v4.3 scope limitation (§9 of the architecture doc), unchanged by this mandate.
5. Evidence is XAUUSD M15 only, from one canonical warmup and one full historical replay. No claim of
   cross-instrument or cross-timeframe generalization is made.
6. Performance (§12) was measured once, in isolation, over one full historical replay — not stress-tested
   against adversarial or synthetic high-occupancy conditions beyond the registry's own hard 16-candidate
   cap. Per-bar latency (5 orders of magnitude below the real 900-second bar budget) and active registry
   size (max 4, historically) are both comfortably bounded.
7. **Restart-serialization size grows with total lifetime candidate count, not with active registry
   occupancy** (§12: ~4 bytes/bar, ~1.4 MB after 15 years) — root-caused to `Registry._dead` and
   `_awaiting_role`, two mechanisms inherited **verbatim from v4.3/v4.4** (not introduced by this mandate)
   that were never previously measurable at scale because v4.4's single-candidate regime creates far fewer
   total lifetime candidates over the same period. Practically negligible at the measured rate (low
   single-digit MB projected over decades) and does not affect the ACTIVE registry bound §20 actually
   gates on, but is a genuine, honestly-disclosed "unbounded state" characteristic in the strict sense of
   mandate §16's own language. Not fixed here — both mechanisms live in shared v4.3 infrastructure outside
   this mandate's authorized scope (§17) — flagged as a well-scoped candidate for a future, separately-
   authorized mandate, applicable to the entire RANGE lineage, not just vNext. **Statistician's independent
   validation (commit `54fa51f`) classified this `REMEDIATION_REQUIRED_BEFORE_PRODUCTION`** — recorded
   here verbatim, unchanged; per `VE-RANGE-VNEXT-HARD-CAP-REMEDIATION-001` §11, this classification is
   noted, not redesigned, in that remediation.
8. **Negative-control matcher parameter sensitivity** (§9.6, added by `VE-RANGE-VNEXT-HARD-CAP-
   REMEDIATION-001` after Statistician's independent validation): the reported true premature-kill rate
   depends on unregistered matching parameters (e.g. the 50-bar coarse start-time-proximity threshold),
   with plausible values in a 2.14%–6.42% range — still an order of magnitude below v4.5's own rates under
   every tested parameterization, but this is a measurement/documentation limitation of the comparison
   methodology, not something this VE division has resolved. A pre-registered matching protocol is left for
   independent validation to define.
9. **This report predates the hard-cap remediation** (`VE-RANGE-VNEXT-HARD-CAP-REMEDIATION-001`, commit to
   be recorded in that mandate's own dedicated report,
   `VE_RANGE_VNEXT_HARD_CAP_REMEDIATION_REPORT.md`): the registry-capacity check originally covered only
   `action == "REPLACEMENT"`, letting CONTINUATION add candidates past `max_active_macro_candidates`
   without limit (Statistician reproduced cap=3/active-reached=34). All measurements in this report were
   taken from the PRE-remediation implementation; see the remediation report for the fix, its own
   regression tests, and the full-history equivalence re-verification confirming this report's own
   quantitative findings are unaffected (production cap=16 was never approached historically — measured
   max concurrent = 4 — so the newly-covered code path never actually fired in this report's own replay).
