# VE-RANGE-V4_4-DESIGN-001 — RANGE V4.4 Design & Pre-Registration

**DESIGN ONLY · NO IMPLEMENTATION · NO PARAMETER FISHING · ZERO VALIDATION WEIGHT ON MB3-001→024**
**MB3-025→048 remain SEALED — not accessed, not decrypted, not inspected, at any point in this mandate.**

No line of `range_semantic_v4_3.py`/`range_engine_v4_3.py` was touched. No threshold was chosen. No config was
built. This document is a specification to be reviewed, not a patch to be applied.

---

## 1 — Plain-language explanation

V4.3 decides "this is a RANGE" using three checks: is the box wide enough, has enough time passed, has price
touched each side twice. Nothing in that decision asks *how* price got there — a market that ground steadily
downward for a month, happening to pause twice near two levels along the way, passes exactly the same test as
a market that spent a month genuinely oscillating between those levels. V4.4 adds a second, independent
question on top of the first: not just "did price touch both sides," but "did price actually go back and
forth, without a persistent net direction, doing so more than once." It answers that with four different,
individually-defensible measurements of the *shape* of the price path (not one fragile threshold), gives a
confirmed RANGE an explicit way to quietly stop being one once the market starts trending again, and stops
several genuinely-continuous market episodes from being counted as separate, competing detections just
because internal rotations kept re-opening new candidates.

---

## 2 — Exact V4.3 defects being corrected (from VE-RANGE-DIAG-001, `071fbd7`)

| # | Defect | Diagnostic evidence |
|---|---|---|
| D1 | MACRO confirmation has no directional-displacement check | Code-traced: `evaluate_candidate`/`degeneracy_check` gate only on width, duration, touch-count |
| D2 | The one signal built for this (`normalized_drift`/`s_max`) is wired only to INTERNAL, as a label, never to MACRO | Code comment at `range_semantic_v4_3.py:1041` |
| D3 | That signal, even if naively wired to MACRO, does not cleanly separate TP from FP | Falsification: naive gate rejects 63.3% of directional FP but also 56.5% of matched TP |
| D4 | Confirmation quality depends mechanically on window length, not on evidence | Median confirm-delay at L=480 (77.5 bars) exceeds L=96's entire eligible-bar budget (67 bars); "more time to fire," not better recognition |
| D5 | No lifecycle concept between CONFIRMED and terminated — a confirmed RANGE cannot quietly weaken | V4.3's only post-confirmation states are the binary excursion/sweep/breakout machinery; there is no "still nominally ranging but degrading" state |
| D6 | One genuine macro episode can fragment into several independently-confirmed, competing structures | 9/39 FP sit over genuine CEO RANGE ground truth; MB3-021 has 4 sequential RANGE-dominant structures, MB3-024 has 5 |
| D7 | 12 FN are entirely confirmation-timing failures (0 are boundary/IoU-quality failures) | Full per-bar categorization: 4 window-truncation, 5 touch-insufficient, 3 zones-degenerate |

D1–D3 are the dominant, well-characterized cluster (30/39 FP). D6 is the secondary, distinct,
under-characterized cluster (9/39 FP). D4/D7 are the same underlying timing-mechanics problem viewed from the
recall side. D5 is the mechanism this design adds to prevent a *future* version of D1's failure mode from
persisting indefinitely once a structure is already confirmed.

---

## 3 — Required conceptual model (mandate §5)

| Property | Classification | Why |
|---|---|---|
| Boundedness (finite, non-degenerate width) | **REQUIRED** | Already enforced (`degeneracy_check`, kept unchanged) |
| Repeated two-sided interaction (≥2 touches/side) | **REQUIRED** | Already enforced (`n_touch`, kept unchanged); strengthened below by alternation |
| Sufficient internal traversal | **REQUIRED** | New — touches alone don't require price to have actually crossed between the two sides; without this, two isolated edge-touches during a slow drift pass today's gate |
| Lack of persistent directional efficiency | **REQUIRED** | New, central fix — the direct answer to "auction vs. channel-that-fits" |
| Persistence long enough to be meaningful | **REQUIRED** | Kept (`d_macro` floor), but reframed: floor is necessary, no longer sufficient by itself (§7 below) |
| Alternating control | **SUPPORTING** | Reinforces the efficiency signal; not independently gating (a real range can show clumped, non-strictly-alternating touches — see §12 self-falsification) |
| Boundary respect/rejection | **SUPPORTING** | Reuses the existing, unchanged excursion/sweep machinery; feeds `WEAKENING` (§6) rather than gating `CONFIRMED` |
| Failed directional progress | **consolidated into** Relative Net Displacement, below (mandate §4: consolidate rules addressing the same phenomenon) |
| Raw `normalized_drift`/slope | **DIAGNOSTIC_ONLY** | Kept as a reported field (cheap, already computed) but demoted from any gating role — falsified in VE-RANGE-DIAG-001 |
| Boundary migration rate | **DIAGNOSTIC_ONLY** at formation; becomes a `WEAKENING` input post-confirmation (§6) |
| Promoted-to-TREND rate | **DIAGNOSTIC_ONLY** — a downstream consequence, not an independent cause |

---

## 4 — Directional-discrimination mechanism (mandate §6): four signals, not one

All four are computed over a **bounded trailing window** `W` (not the structure's unbounded whole life).
Justification for bounded-not-unbounded, independent of any MB3 finding: a range that was genuinely choppy
100 bars ago but has been trending for the last 20 should be judged on its *current* character, not diluted
by ancient history — the same recency logic that motivates the new `WEAKENING` state (§6) applies equally to
formation. `W` is a new parameter — see provenance table below.

### 4.1 Efficiency Ratio (ER) — REQUIRED, ceiling

```
ER(S, t) = |close[t] - close[t-W]| / Σ_{i=t-W+1}^{t} |close[i] - close[i-1]|      (Kaufman efficiency ratio)
```

Range `[0,1]`. `ER→0`: pure chop, no net progress. `ER→1`: pure trend. **Gate: `ER(S, t) ≤ ER_max`.**
Deliberately a *different construction* from the falsified `normalized_drift` (which is an OLS-slope fit,
multiplicatively duration-sensitive, and externally ATR-normalized): ER uses the raw cumulative path length
(so noise/chop directly inflates its denominator) and is **self-normalized** — a dimensionless ratio of the
structure's own price data, no ATR dependency at all. This is the primary, best-established candidate for
"lack of persistent directional efficiency."

### 4.2 Traversal count — REQUIRED, floor

Split the current `[boundary_lower, boundary_upper]` band into UPPER/MID/LOWER thirds. A traversal is counted
each time the zone sequence crosses fully from UPPER to LOWER or LOWER to UPPER (touching MID and bouncing
back does not count). **Gate: `traversal_count(S, W) ≥ MIN_TRAVERSALS`.** Directly answers "sufficient
internal traversal" — distinguishes genuine two-sided testing from two isolated edge touches with a drift in
between.

### 4.3 Alternation rate — SUPPORTING (feeds confidence/labeling), not independently gating `CONFIRMED`

Over the confirmed-touch sequence (tagged HIGH/LOW by which cluster accepted them) within the trailing
window, `alternation_rate = (adjacent pairs with different tags) / (pairs total)`, defined only for ≥3
touches in-window (fewer: `ALTERNATION_INSUFFICIENT_EVIDENCE`, treated as non-blocking, not a fail). Kept
supporting rather than required because a real range can legitimately show clumped touches (three lows then
two highs) without ever failing to be a range — see §12.

### 4.4 Relative Net Displacement (RND) — REQUIRED, ceiling

```
RND(S, t) = |close[t] - close[t-W]| / (boundary_upper - boundary_lower)
```

**Gate: `RND(S, t) ≤ RND_max`.** Fully self-referential — no ATR, no external constant at all: net
displacement expressed in units of the structure's *own* width. Directly answers "has this thing migrated
further than its own size."

### 4.5 Combination rule

For `FORMING → CONFIRMED`, ALL of: existing width (`degeneracy_check`, unchanged) AND existing duration
(`d_macro` floor, unchanged) AND existing touch-count (`n_touch`, unchanged) AND `ER ≤ ER_max` AND
`traversal_count ≥ MIN_TRAVERSALS` AND `RND ≤ RND_max`. Alternation is reported and feeds `WEAKENING`
sensitivity but does not block confirmation on its own.

### 4.6 Parameter provenance

| Parameter | Value | Provenance | Confidence |
|---|---|---|---|
| `ER_max` | 0.5 | Natural midpoint of ER's own `[0,1]` scale — "less than half the cumulative path was net progress" requires no external calibration | Principled starting anchor; candidate for tightening under a calibration mandate |
| `RND_max` | 1.0 | Self-referential: net displacement should not exceed the structure's own width, by definition | Strongest of the four derivations — a genuine tautology-adjacent floor, not a fitted number |
| `ALT_MIN` (advisory, non-gating) | 0.5 | Same natural-midpoint logic as `ER_max`, for consistency | Weakest of the anchors — flagged for likely refinement (§12) |
| `MIN_TRAVERSALS` | ≥1 (floor only) | Zero traversals means price never crossed its own middle — logically indefensible as a range | **`UNRESOLVED_PARAMETER`** — the *exact* minimum (1 vs. 2+) is not derived here |
| `W` (trailing window length) | — | Bounded-trailing-window *mechanism* is justified (recency relevance); the *length* is not | **`UNRESOLVED_PARAMETER`** |

No threshold above was chosen by testing values against MB3 and picking a winner (mandate §12 forbidden
list). Where a value could not be derived from a scale-invariant or self-referential argument, it is left
unresolved rather than manufactured.

---

## 5 — State model (mandate §3.C, §7)

```
CANDIDATE → FORMING → CONFIRMED → WEAKENING → TERMINATED
                ↑___________________|              ↑
                (weakening recovers)                |
                FORMING ─────────────────────────── (degenerate / inverted, unchanged from V4.3)
                CONFIRMED ────────────────────────── (breakout accepted, unchanged from V4.3)
```

| State | Meaning | V4.3 analog |
|---|---|---|
| `CANDIDATE` | A swing pair identified; cluster(s) not yet populated | pre-`ESTABLISHING_FEW_SWINGS` |
| `FORMING` | Width/touch satisfied OR duration satisfied, but the §4 discrimination gate (ER/traversal/RND) not yet all-clear | `ESTABLISHING_FEW_SWINGS`/`TOO_SHORT_MACRO`, **merged and reframed** — see §7 |
| `CONFIRMED` | All required gates (existing three + new three) satisfied | `RANGE_CONFIRMED` |
| `WEAKENING` | Confirmed, boundaries still frozen, but current evidence (excursion in progress, or trailing-window ER/RND degrading) says the two-sided character may be ending | **new** |
| `TERMINATED` | Closed via breakout-accepted, zones-degenerate, or (new) weakening-persistence | `EPISODE_CLOSED`/`BREAKOUT_ACCEPTED` |

A `FORMING` structure is never reported downstream as equivalent to `CONFIRMED` (mandate §7 explicit
requirement) — see the new `RANGE_CANDIDATE_PRESENT` quality event, §7.

---

## 6 — Lifecycle: confirmation timing, weakening, invalidation (mandate §3.B/C, §8, §9)

### 6.1 Confirmation is evidence-gated, not merely time-gated

`d_macro` remains a **necessary floor**, not a trigger. Once width+touch+duration clear (today's full
confirmation condition), V4.4 additionally requires the §4 discrimination gate. A genuinely choppy structure
that packs sufficient traversal/efficiency evidence into few bars can still confirm close to the `d_macro`
floor; a structure that is mechanically "old enough" but shows no real two-sided character stays `FORMING`
indefinitely (or is later invalidated) rather than force-confirming. This is the direct mechanism answer to
"we need earlier correct recognition, not merely eventual recognition" — earlier confirmation becomes
possible in genuine cases and impossible in spurious ones, rather than uniform in both.

### 6.2 `RANGE PRESENT` vs. `RANGE FIRST CONFIRMED NOW` (mandate §8 explicit requirement)

The instant width+touch clear (today's `TOO_SHORT_MACRO`-eligible point), V4.4 emits a new, **non-authoritative**
quality event `RANGE_CANDIDATE_PRESENT` — visible to consumers as "a candidate exists," explicitly distinct
from `OK_RANGE_MACRO` (still reserved for full confirmation). This also gives truncated episodes an honest
output: a window that ends mid-`FORMING` reports *why* (`RANGE_CANDIDATE_PRESENT` seen, discrimination gate
never cleared, or duration never reached) instead of silently registering as an unexplained miss — directly
answering D7's 4 window-truncation FN with a transparency improvement, not a fabrication of bars that were
never observed.

**Explicitly acknowledged, not solved:** a range genuinely underway *before* the observation window began has
no earlier bars to reconstruct from; `start_ts` remains anchored to whatever is first detectable inside the
window, same limitation V4.3 has. Correcting this needs cross-window context, which is out of scope for a
per-window detector redesign — documented here rather than silently ignored (mandate §8 "treatment of a
RANGE already underway at window start" — the honest treatment is disclosure, not a fix this design can make).

### 6.3 `WEAKENING` (new, addresses mandate §3.C/§9 directly)

A `CONFIRMED` structure enters `WEAKENING` when **either**:

- **(a)** An excursion beyond the (still-frozen) boundary opens and has not yet resolved to
  `SWEEP_CONFIRMED`/`BREAKOUT_ACCEPTED` — this reuses the existing, unmodified `Excursion` state machine; the
  only change is a new state *label* applied to the structure while the excursion is unresolved, not new
  excursion logic; **or**
- **(b)** The trailing-window §4 measures degrade past a separate, more permissive ceiling than the
  confirmation gate (`ER_weakening > ER_max`, `RND_weakening > RND_max`) while price is still nominally
  inside the boundary — genuinely new logic, the direct answer to "directional displacement after
  confirmation must not allow stale RANGE state to persist indefinitely" for the case where character erodes
  *without* a clean boundary excursion.

`WEAKENING → CONFIRMED` (recovery): measures recover past the confirmation-grade thresholds again.
Boundaries stay frozen throughout (V4.3's "zones freeze at `confirm_ts`" rule is unchanged) — only the state
label and invalidation eligibility change.

`WEAKENING → TERMINATED` (new pathway, reason code `WEAKENING_PERSISTENCE_TERMINATED`): weakening persists
beyond a bound without recovery. Path (a)'s bound reuses the existing `Excursion`/`K_reentry` mechanics
unchanged; path (b)'s bound is a new, explicit duration parameter — **`UNRESOLVED_PARAMETER`**.

### 6.4 Full termination pathway set

`ZONES_DEGENERATE`/`ZONES_INVERTED` (unchanged) · `BREAKOUT_ACCEPTED` (unchanged) ·
`WEAKENING_PERSISTENCE_TERMINATED` (new). No existing pathway is removed.

---

## 7 — Over-segmentation control (mandate §3.D, §10)

Reuses the scorer's own IoU concept (`_iou`, `blind_runner/scoring.py`) — one construct, two roles, per
mandate §12's "prior ratified conventions."

- **CONTINUATION**: a new `CANDIDATE`'s initial zone has `IoU ≥ IOU_CONTINUE` against the late-life zone of a
  structure that just `TERMINATED` (or is `WEAKENING`), within a small bar-gap `≤ GAP_MAX`. The new candidate
  **inherits** the prior structure's identity rather than opening a competing one.
- **MERGE**: two concurrently-forming `CANDIDATE`/`FORMING` structures with `IoU ≥ IOU_CONTINUE` between
  their zones collapse into one (same test, applied to the concurrent rather than sequential case).
- **REPLACEMENT**: a genuinely new, independent episode — large gap, low zone `IoU`, **or** the prior
  structure closed via `BREAKOUT_ACCEPTED` (a clean regime change is treated as a strong signal *against*
  continuation, distinct from a `WEAKENING_PERSISTENCE_TERMINATED` close, which is more ambiguous and leans
  toward allowing continuation if the new zone is close).
- **NESTING**: **unchanged** — `assign_level`/`DEPTH_LIMIT_EXCEEDED`/parent-containment is a MACRO/INTERNAL
  *depth* mechanism; the diagnosed over-segmentation is a same-depth, sequential/concurrent identity problem,
  not implicated by nesting logic. Not touched.
- **TERMINATION**: §6.4's set, unchanged by this section.

`IOU_CONTINUE`, `GAP_MAX`: **`UNRESOLVED_PARAMETER`** — mechanism defined, exact values deferred.

This directly targets the empirically observed cases (MB3-021: 4 sequential RANGE-dominant structures;
MB3-024: 5) — temporally-close, zone-overlapping sequential episodes would collapse under continuation/merge
rather than standing as separate, competing detections.

---

## 8 — Architecture requirements (mandate §13)

| Element | Specification |
|---|---|
| **Inputs** | Same causal bar inputs as V4.3: `ts_close, open, high, low, close, atr` per bar. No new external input. |
| **Persistent state (new fields on `Structure`)** | `c0` (close at `start_ts`, for RND); bounded trailing-window buffer for ER/RND (deque of closes, length `W`, O(1) push/evict via a running `Σ|Δclose|` accumulator — the same rolling-buffer pattern already validated at `IncrementalRawAxesBuilder`'s 460-bar horizon); zone-transition tracker for traversal count (current zone + counter, O(1)); alternation counters (pairs-total, pairs-flipped, last tag — O(1), updated only on new touch acceptance); episode-continuation linkage (`continued_from_id: int \| None`) |
| **States** | `CANDIDATE, FORMING, CONFIRMED, WEAKENING, TERMINATED` (§5) |
| **Transitions** | §5 diagram; priority order: KILL conditions (degenerate/inverted, unchanged) → excursion/breakout resolution (unchanged `Excursion` machinery) → discrimination gate evaluation → duration/touch gate — same fail-closed-first ordering principle as V4.3's `evaluate_candidate` (input/KILL checked before duration, C15's already-ratified convention, kept) |
| **Outputs** | MACRO structures (existing fields + `state`, `weakening_reason`, `continued_from_id`) and events (existing kinds + new ones below) |
| **Reason codes (new, additive)** | `INSUFFICIENT_EFFICIENCY`, `INSUFFICIENT_TRAVERSAL`, `INSUFFICIENT_ALTERNATION_EVIDENCE`, `EXCESSIVE_NET_DISPLACEMENT`, `RANGE_CANDIDATE_PRESENT`, `RANGE_WEAKENING`, `WEAKENING_RECOVERED`, `WEAKENING_PERSISTENCE_TERMINATED`, `EPISODE_CONTINUATION`, `EPISODE_MERGED`, `EPISODE_REPLACEMENT` — each tied to exactly one mechanism above (mandate §4: every rule has a reason code) |
| **Identity** | New `contract_version = "range-hierarchical-v4.4"`. `config_id()` **not computed in this mandate** — it would require final values for every `UNRESOLVED_PARAMETER`, which §12/§2 forbid choosing here. New `implementation_fingerprint` reserved for the eventual implementation commit. |
| **Snapshot** | New versioned schema (`range-hierarchical-v4.4-snapshot`), extending V4.3's fields with the new persistent state above; fail-closed refusal on `contract_version`/`config_id`/`implementation_fingerprint` mismatch — the exact, already-validated pattern from the F1-only remediation (`bc6b9dc`), reused not reinvented. |
| **Fail-closed behavior** | Corrupt/incompatible snapshot: refuse (unchanged discipline). Unresolved parameter reaching a live config: **must** raise at construction, mirroring `ConfigV43.__post_init__`/`validate()` — a V4.4 config object literally cannot be built while any `UNRESOLVED_PARAMETER` lacks a value. |
| **Complexity** | Every new computation is O(1)/bar or O(1)/touch-event (§4 trailing-window via rolling accumulator; traversal via a single counter; alternation via two counters). No unbounded re-scan is introduced — consistent with the project's established bounded-incremental-computation discipline (RT-RANGE-0004's O(1) slope fix is the direct precedent). |

---

## 9 — Mathematical invariants (mandate §14)

All of V4.3's existing invariants (no lookahead, prefix invariance, deterministic replay, chunk invariance,
snapshot/restart invariance, config identity sensitivity) **carry over unchanged in kind** — every new
computation above is causal (uses only `≤t` data) and either O(1)-incremental or bounded-window, so none of
these proofs need to change in form, only be re-verified against the new state. Additional invariants specific
to V4.4:

- **No simultaneous logically contradictory terminal events**: a structure cannot be both
  `BREAKOUT_ACCEPTED` and `WEAKENING_PERSISTENCE_TERMINATED` in the same bar (priority order in §8 makes
  excursion/breakout resolution strictly precede weakening-persistence evaluation).
- **Bounded V4.4-owned memory**: the trailing-window buffer is capped at `W`; alternation/traversal state is
  O(1) regardless of structure lifetime — no field introduced here can grow unboundedly with `n_bars`.
- **No stale RANGE after accepted directional termination**: once `WEAKENING_PERSISTENCE_TERMINATED` or
  `BREAKOUT_ACCEPTED` fires, the structure's `state` is authoritatively `TERMINATED` — no code path may
  report it as `CONFIRMED` afterward (this is the invariant D5/§3.C exists to guarantee).
- **No duplicate confirmed macro episode from the same continuing structure unless explicitly allowed**: a
  `CONTINUATION` (§7) inherits the prior `structure_id`'s lineage via `continued_from_id`; a downstream
  consumer following that chain sees one episode, not two competing ones, unless `EPISODE_REPLACEMENT`
  explicitly declares a new, independent lineage.
- **Discrimination-gate monotonicity under recovery**: `WEAKENING → CONFIRMED` requires the *same* measures
  that gate `FORMING → CONFIRMED` to clear again — no separate, weaker "re-confirmation" path exists.

---

## 10 — Mandatory adversarial test design (mandate §15) — 20 scenarios, expected chronology

| # | Scenario | Expected chronology (state sequence / key events) |
|---|---|---|
| 1 | Clean horizontal RANGE | `CANDIDATE→FORMING` (touches accumulate, ER low, traversals accrue) `→CONFIRMED` at/near `d_macro` floor, since evidence is available early; stays `CONFIRMED` |
| 2 | Noisy RANGE | Same as #1 but slower touch accumulation; `FORMING` may extend past `d_macro` if the discrimination gate lags; still confirms once evidence clears |
| 3 | Wide volatile RANGE | Width comfortably clears `degeneracy_check`; ER/RND unaffected by absolute width (self-referential); confirms same as #1 |
| 4 | Shallow upward CHANNEL | Touches on both sides possible, but ER trends toward 1 and RND toward/above 1 as the "boundaries" migrate with price → `INSUFFICIENT_EFFICIENCY`/`EXCESSIVE_NET_DISPLACEMENT`, stays `FORMING`, never `CONFIRMED` (this is D1's direct fix — MB3-007-style case) |
| 5 | Shallow downward CHANNEL | Mirror of #4 |
| 6 | Strong TREND_UP | `degeneracy_check` likely never stabilizes a width at all (boundaries chase price); if it somehow does, ER≈1 blocks confirmation immediately |
| 7 | Strong TREND_DOWN | Mirror of #6 (MB3-020-style negative control) |
| 8 | Stair-step trend | Each "step" may briefly look like `FORMING`, but low traversal-count (price doesn't cross back) and high RND per step block confirmation at every step — this is the case the mandate specifically flags as `directional move that temporarily fits between boundaries` (item 12), addressed by the SAME mechanism, not a special case |
| 9 | Compression then breakout | `FORMING→CONFIRMED` during compression (genuine low-ER phase); `CONFIRMED→WEAKENING` (path a, excursion opens) `→TERMINATED` via `BREAKOUT_ACCEPTED` once the excursion resolves — boundary freeze at `confirm_ts` unchanged |
| 10 | RANGE → accepted breakout | Same as #9 |
| 11 | RANGE → failed breakout | `CONFIRMED→WEAKENING`(a)`→CONFIRMED` (`WEAKENING_RECOVERED`) on re-entry within `K_reentry` — reuses unchanged `Excursion`/`sweep_reversal_confirmed` machinery |
| 12 | Directional move temporarily fitting between boundaries | Covered by #8's mechanism directly — `INSUFFICIENT_EFFICIENCY`/`TRAVERSAL` block confirmation regardless of transient width/touch/duration satisfaction |
| 13 | Slow boundary migration | Trailing-window RND is the primary sensor — sustained migration eventually exceeds `RND_max` even if per-bar migration is individually small; blocks confirmation, or triggers `WEAKENING`(b) if migration begins post-confirmation |
| 14 | One-sided touch concentration | Alternation stays low but is **supporting only** — does not block confirmation alone; ER/traversal/RND are the deciding gates; flagged in reported metadata as low-alternation even if confirmed (see §12 counterexample — deliberate, not an oversight) |
| 15 | RANGE beginning before observation window | `start_ts` anchors to first-detectable-in-window swing, same as V4.3; documented limitation (§6.2), not solved |
| 16 | RANGE ending near observation-window end | If still `FORMING`/discrimination-pending at window end: `RANGE_CANDIDATE_PRESENT` reported, no `OK_RANGE_MACRO`, honest truncation (§6.2) — no fabricated confirmation |
| 17 | Two consecutive independent ranges | Large gap and/or low zone-`IoU` between them → `EPISODE_REPLACEMENT`; two structures, two identities, correctly |
| 18 | One long RANGE with internal rotations | Rotations stay within the same zone → each new internal candidate's zone has high `IoU` against the still-`CONFIRMED`/`WEAKENING` parent episode → `EPISODE_CONTINUATION`/`EPISODE_MERGED`, one macro structure, not several (direct fix for D6) |
| 19 | Sweep without range termination | Excursion opens (`WEAKENING`(a)) and resolves `SWEEP_CONFIRMED` within `K_reentry` → `WEAKENING_RECOVERED`, structure remains the same identity throughout — unchanged from V4.3's existing sweep semantics |
| 20 | Genuine range containing temporary directional displacement | Trailing-window `W` matters most here: a brief displacement inside a long genuine range should stay within `ER_max`/`RND_max` if `W` is short enough not to be dominated by the blip, but could trigger `WEAKENING`(b) if the blip is large relative to `W` — the *exact* sensitivity depends on the unresolved `W`, explicitly flagged as the scenario most exercising that unresolved parameter |

Scenarios 4, 5, 6, 7, 8, 12 are the direct adversarial re-statement of D1 (the dominant defect); 9, 10, 11, 19
exercise the preserved excursion/sweep machinery under the new state labels; 13, 14, 20 stress-test the new
discrimination signals' edge behavior; 15, 16 exercise the honest-truncation design; 17, 18 exercise
over-segmentation control (D6).

---

## 11 — V4.3 behavior preservation matrix (mandate §16)

| V4.3 behavior | KEEP / CHANGE | Reason | V4.4 replacement | Regression test |
|---|---|---|---|---|
| `degeneracy_check` (width floor, inversion) | **KEEP** | Not implicated by any diagnosed defect | unchanged | re-run existing width/inversion adversarial cases unmodified |
| `d_macro`/`d_internal` duration floors | **KEEP as floor** | Still necessary; no longer sufficient alone | duration floor + discrimination gate (§4) | existing duration-boundary tests unmodified; add discrimination-gate-still-pending case at floor |
| `n_touch` touch-count gate | **KEEP** | Not falsified; strengthened, not replaced | unchanged, plus traversal/alternation as additional signals | existing touch-count tests unmodified |
| `Cluster`/`_RunningMedian` boundary geometry | **KEEP** | Not implicated | unchanged | unchanged |
| `Excursion`/sweep/breakout state machine | **KEEP** | Not implicated; reused as the `WEAKENING`(a) trigger | unchanged mechanics, new state *label* applied on top | all existing sweep/breakout/reversal tests unmodified |
| Promotion (`promotion_check`, `IS_TREND_MACRO`) | **KEEP** | Not implicated — promotion is a downstream, diagnostic-only signal (§3) | unchanged | unchanged |
| `assign_level`/`DEPTH_LIMIT_EXCEEDED` (MACRO/INTERNAL nesting) | **KEEP** | Explicitly not implicated by the diagnosed same-depth over-segmentation problem | unchanged | unchanged |
| INTERNAL classification (`_channel_or_state_label`, `INT_CHANNEL_*`) | **KEEP, untouched** | Mandate §19: F4/INTERNAL is a separate research problem, not coupled into this release | unchanged | unchanged |
| Snapshot/restore fail-closed pattern | **KEEP pattern, extend schema** | Pattern already validated (F1-only remediation); reused, not redesigned | new `contract_version`/fields, same refusal logic | reuse the exact refusal-matrix test pattern from `test_f1_only_macro_identity.py` |
| `normalized_drift`/`s_max` at INTERNAL | **KEEP, unchanged** | Mandate §19 — do not touch INTERNAL | unchanged | unchanged |
| MACRO confirmation = width+duration+touch only | **CHANGE** | D1/D2/D3 | + discrimination gate (§4) | scenarios #4-8, #12-14, #20 |
| No post-confirmation erosion detection | **CHANGE (addition)** | D5 | `WEAKENING` state (§6.3) | scenarios #9-11, #19 |
| Each new candidate gets an independent identity | **CHANGE** | D6 | continuation/merge/replacement (§7) | scenarios #17-18 |

No behavior is changed without a row in this table; nothing is silently dropped.

---

## 12 — TP protection and mandatory self-falsification (mandate §11, §21)

For each new mechanism:

### ER / traversal / RND (the confirmation gate)
```
target defect: D1 (directional false positives confirming as RANGE)
expected FP reduction: the 30 directional-GT FP class (§2) — these show persistent one-directional
  slope through their whole formation; ER/RND should sit high for exactly this population
TP at risk: matched structures with legitimately high ER over their unbounded life (§0 diagnostic
  showed TP `normalized_drift` mean 2.09, comparable to FP's 2.28 — a WHOLE-LIFE measure) — bounded-
  trailing-window ER is a DIFFERENT construction and has NOT been tested against this same MB3 data
  under this mandate's own no-fishing rule, so this risk is NOT empirically cleared, only mitigated
  by construction (recency-windowing should reduce whole-life dilution, but this is a hypothesis)
why TP should survive: a genuine range's trailing-window ER should stay low at ANY point in its life,
  not just on average over its whole (possibly long) formation — the bounded window removes the
  averaging-over-a-long-history effect that could have been inflating whole-life measures
counterexample (self-falsification, FALSE REJECT risk): a slow, drifting-equilibrium range (the
  "equilibrium" itself migrates gradually, e.g. a rising staircase of mini-ranges) could show
  elevated RND over ANY window length if the migration rate is comparable to the window — genuinely
  ranging locally, still flagged. Not resolved here; flagged as a real, open risk requiring
  falsification against fresh evidence before freeze, not before this design proposal.
counterexample (self-falsification, FALSE ACCEPT risk): a violent, large-amplitude "sawtooth" zigzag
  that nets near-zero displacement with plentiful crossings could pass ER/traversal/RND favorably
  while a human would not call it a clean, tradeable range (a volatility/quality dimension this
  design does not address at all — explicitly out of scope, not solved, not claimed solved)
```

### Alternation (supporting, non-gating)
```
target defect: contributes to WEAKENING sensitivity and reported metadata quality
expected FP reduction: none directly (not gating) — diagnostic value only
TP at risk: none by construction (non-gating)
why TP should survive: trivially, since it cannot reject anything on its own
counterexample: a genuine range with clumped touches (three lows, then two highs) shows LOW
  alternation despite being a valid range — this is exactly why it was deliberately kept
  SUPPORTING rather than REQUIRED; had it been made a hard gate, this would be a real FALSE REJECT
  risk. Explicitly the weakest of the four signals (§4.6) for this reason.
```

### WEAKENING / episode continuation
```
target defect: D5 (stale confirmed RANGE persisting after character changes), D6 (over-segmentation)
expected FP reduction: prevents a structure from remaining reportable as CONFIRMED once it has
  quietly started trending post-confirmation; collapses spurious multi-structure fragmentation of
  one genuine episode
TP at risk: a genuine range that has one large, quickly-reverting excursion (a real sweep, #19) must
  NOT be mistakenly terminated — protected by reusing the EXISTING, already-validated K_reentry/
  sweep-reversal machinery unchanged for path (a); path (b)'s risk is the same open question as
  above (unresolved trailing-window sensitivity)
why TP should survive: the recovery path (WEAKENING→CONFIRMED) exists precisely so a temporary wobble
  does not destroy a still-valid range; only PERSISTENT weakening terminates
counterexample: if the weakening-persistence duration bound (unresolved) is set too short, a
  legitimate, larger-than-usual pullback within a real range could be wrongly terminated — this is
  exactly why that bound is left UNRESOLVED_PARAMETER rather than guessed
```

**Overall self-falsification verdict**: the design survives conceptual attack in the sense that every
identified false-reject/false-accept risk is either (a) mitigated by an explicit, argued design choice
(bounded window, supporting-not-gating alternation, reused sweep machinery), or (b) honestly disclosed as an
open risk requiring empirical falsification on evidence this mandate did not touch, not silently assumed away.
No mechanism claims to be a complete, closed-form solution to CHANNEL/TREND discrimination — each is a
falsifiable hypothesis about a real, distinct signal.

---

## 13 — Failure-mode closure table (mandate §20)

| Failure mode | V4.3 mechanism | Evidence | V4.4 response | Expected benefit | Risk | Adversarial test | Regression test |
|---|---|---|---|---|---|---|---|
| Directional FP confirms as RANGE | `evaluate_candidate` has no drift check | 30/39 FP, MB3-007/020 traces | §4 combination gate | reduces directional FP | may also reject some genuine TP (unresolved, §12) | #4-8,#12 | #1-3 |
| Naive single-drift-threshold fix fails | N/A (hypothetical) | §12 falsification (63.3%/56.5%) | multi-signal combination, not single threshold | avoids the specific failure mode already falsified | new signals individually untested on real data | #13,#14,#20 | #1-3 |
| Confirmation timing = window-length artifact | mechanical `d_macro` trigger | median confirm-delay 77.5 (L=480) vs. 67-bar budget (L=96) | evidence-gated confirmation (§6.1) | earlier correct recognition, not merely eventual | UNRESOLVED `W` controls sensitivity | #1,#2,#16 | duration-boundary cases |
| Truncated episode reports as unexplained miss | no partial-formation reporting | 4/12 FN window-truncation | `RANGE_CANDIDATE_PRESENT` (§6.2) | honest, explained non-confirmation | none (purely additive reporting) | #16 | — |
| Stale CONFIRMED persists after directional resumption | no post-confirmation erosion check | mechanism gap (D5), not directly measured in MB3 | `WEAKENING` state (§6.3) | bounds how long a confirmed RANGE can outlive its own validity | UNRESOLVED persistence bound | #9-11 | #19 |
| One episode fragments into several structures | independent structure_id per candidate | 9/39 FP, MB3-021 (4)/MB3-024 (5) | continuation/merge/replacement (§7) | fewer, more coherent macro episodes | UNRESOLVED `IOU_CONTINUE`/`GAP_MAX`; risk of over-merging genuinely distinct episodes | #17,#18 | — |
| INTERNAL discrimination coupled into MACRO release | (not a V4.3 defect — a scope-discipline risk) | mandate §19 | explicitly NOT touched | keeps MACRO fix isolated, auditable | none if discipline holds | — | full INTERNAL suite unmodified |

Every material V4.3 MACRO failure mode identified in VE-RANGE-DIAG-001 appears above; none is silently
deferred without the explicit "unresolved" markers already stated.

---

## 14 — Comparison with Red Team audit (mandate §22)

**`RT-RANGE-DIAG-AUDIT-001` has not been delivered as of this design's completion** (verified: no commit
referencing it exists on any of the four mirrors as of this writing). Per mandate §2, this design therefore
**cannot be frozen** — the convergence table below is structurally empty because there is nothing to converge
against yet, not because the check was skipped.

| RT finding | VE design assumption | MATCH/CONFLICT | required amendment |
|---|---|---|---|
| *(pending)* | *(pending)* | *(pending)* | *(pending)* |

This section must be completed, and only then may a freeze decision be revisited, once the audit lands —
either in a follow-up turn of this same mandate or a successor mandate. Until then the formal verdict below
reflects this gap honestly rather than fabricating a convergence result.

---

## 15 — Remaining risks

1. All four `UNRESOLVED_PARAMETER`s (`W`, `MIN_TRAVERSALS`, weakening-persistence bound, `IOU_CONTINUE`/`GAP_MAX`) need a dedicated, pre-registered calibration mandate evaluated on evidence this mandate never touched.
2. The bounded-trailing-window ER/RND construction is a *hypothesis*, not yet empirically checked even descriptively — §12's slow-drift-equilibrium counterexample is open.
3. The "violent zigzag" false-accept risk (§12) is explicitly unaddressed — this design narrows but does not close the CHANNEL/TREND confusion problem.
4. Over-segmentation control could, if `IOU_CONTINUE` is set too loosely, wrongly merge genuinely distinct sequential episodes (§10/§13) — the opposite failure mode from the one being fixed.
5. `config_id()` cannot be computed until every unresolved parameter is resolved — this design is not yet instantiable as running code, by construction (consistent with "design only").

---

## 16 — Explicitly unchanged from V4.3 (mandate §24 item 19)

`degeneracy_check`, `n_touch` gate, `Cluster`/`_RunningMedian`, the full `Excursion`/sweep/breakout/reversal
machinery, `promotion_check`/`IS_TREND_MACRO`, `assign_level`/nesting/`DEPTH_LIMIT_EXCEEDED`, all INTERNAL-depth
logic (`_channel_or_state_label`, `INT_CHANNEL_*`, `normalized_drift`/`s_max` as used today), the
snapshot/restore fail-closed *pattern*, ATR provenance/computation, and every one of the 29 existing reason
codes (all remain valid; V4.4 only adds new ones, per §11's matrix).

---

## 17 — Implementation plan (not executed in this mandate)

1. Resolve `UNRESOLVED_PARAMETER`s via a dedicated pre-registration mandate (hypothesis → rationale →
   pre-registration → freeze → evaluation on evidence not used to derive it), per mandate §12's own required
   procedure for any future threshold work.
2. Only then: implement as new, additive files (`range_semantic_v4_4.py`/`range_engine_v4_4.py`), mirroring
   the V4.3-over-V4.2 pattern — V4.3 files stay byte-untouched, exactly as every prior version transition in
   this project has done.
3. Port the 20 adversarial scenarios (§10) into an executable adversarial suite BEFORE any construction-corpus
   or MB3 re-evaluation.
4. Full mypy --strict, snapshot fail-closed matrix, chunk/restart invariance — same discipline as every prior
   delivery.
5. Red Team static + construction-only audit (mirroring RT-RANGE-0006's role for V4.3).
6. Only after that: a fresh, independent blind batch (never MB3) for actual validation.

## 18 — Rollback plan

V4.4 is additive, new-namespace, exactly like every prior version jump in this codebase (`0.3.1`→`0.4.0`,
`f224e7d`→`bc6b9dc`, etc.) — V4.3 files remain byte-identical and available; rollback is "stop routing to
V4.4," not "undo a patch." Snapshot fail-closed refusal (§8) prevents any cross-version state corruption in
either direction, the same guarantee every prior transition has carried.

---

## 19 — Formal design verdict (mandate §23)

```
V4_4_DESIGN_NOT_READY
```

Not because the design itself is known-defective — self-falsification (§12) found real, honestly-disclosed
open risks but no fatal flaw — but because mandate §2 and §22 make Red Team convergence a **precondition for
freeze**, and `RT-RANGE-DIAG-AUDIT-001` does not yet exist to converge against (§14). This design is complete
and internally self-falsified; it is **not** yet eligible to be called ready-to-freeze under this mandate's
own explicit gate. Once that audit lands, §14's table can be completed and the verdict revisited — plausibly
to `V4_4_DESIGN_READY_FOR_RED_TEAM_REVIEW` if no decisive conflict emerges, or `_REQUIRES_AMENDMENT` if one
does.

`ZERO_VALIDATION_WEIGHT` on everything above derived from MB3-001→024. `MB3-025→048`: not accessed, not
decrypted, not inspected — this mandate needed no bar-level data at all, only the already-committed diagnostic
findings and the frozen V4.3 source, both already legitimately in hand. No implementation, no parameter
fishing, no threshold chosen, no V4.3 file touched. Next owner: **CEO** (schedule the Red Team convergence
step once `RT-RANGE-DIAG-AUDIT-001` exists), then **Red Team** (review this design directly, independent of
timing).
