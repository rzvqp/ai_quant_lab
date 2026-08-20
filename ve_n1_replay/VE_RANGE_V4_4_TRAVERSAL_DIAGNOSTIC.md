# VE — RANGE V4.4 TRAVERSAL-GATE FAILURE DIAGNOSTIC

**Mandate**: `VE-RANGE-V4_4-TRAVERSAL-DIAG-001`. **Date**: 2026-08-21. **Division**: Validation Engine (VE).
**Scope**: diagnostic/design review of the traversal mechanism only — no implementation, no recalibration,
no threshold selection, no MB3 access, no additional blind execution, no V4.4 promotion.

Structured against the mandate's own §16 (16 required report items) + §17 (final verdict).

---

## 1 — Provenance

Authoritative source, independently re-verified (not trusted by assertion) before use:

| Artifact | Verification |
|---|---|
| `dfebe8f` — RT-RANGE-V4_4-FRESH-BLIND14-VALIDATION-001 | `git cat-file -t` confirmed; tip of `statistician-foundation`; local=remote ×4 |
| `26abd13` — FB14 dual-detector predictions freeze | exists, ancestor of `dfebe8f` |
| `845a03c` — RT-RANGE-V4_4-IMPLEMENTATION-AUDIT-001 | exists, read in full; independently re-confirmed every claim in my own `3bb61cf` delivery |
| `3bb61cf` — my own V4.4 implementation | HEAD of `discovery-mk-matrix-v1`, config_id/fingerprint cross-checked against both RT reports |
| FB14 labels (`labels_fb14.json`, escrow-opened) | sha256 independently recomputed via PowerShell: `d284fd39ee4ff8e84c4e488a7b6592fbefc714d4cd05c2f7531a18505e54ec38` — **matches** the frozen `labels_sha256` exactly |
| FB14-003/FB14-012 raw OHLC | reconstructed via `escrow_repro/canonical_corpus.py` from the tracked source CSV; `bars_sha256` independently recomputed and **matched** the escrow manifest for both windows |
| V4.3/V4.4 frozen predictions JSON | `config_id` field cross-checked, **matches** `3bb61cf`'s `23d98c07...` exactly |

I did not re-derive `window_list_sha256` (already-documented historical non-reproducibility, unrelated to
this mandate) and did not touch MB3-025→048 at any point.

**A methodological error was found and corrected during this mandate, disclosed here rather than silently
fixed**: my first reproduction attempt fed the full 24+24-bar "rendered" window (used only for `bars_sha256`
collision-avoidance per `escrow_repro/BARS_SHA256_SPEC.md`) into the detector as pre-context. This produced a
structure timeline unrelated to the frozen predictions. Cross-checking against the frozen predictions JSON
(`n_bars: 480`, exact `end_ts` values 19/83/111/144 for FB14-012) revealed the detector must run on the
**canonical 480/288 bars only**, starting fresh at canonical bar 0. Re-running this way reproduced the frozen
predictions' structure-kill bars **exactly** (19, 83, 111, 144 — all four match). All findings below use the
corrected (canonical-only) reproduction.

---

## 2 — FB14 H1–H5 result (as delivered by Red Team, re-stated for completeness)

```
H1 directional-FP reduction   : 13 -> 7    PASS
H2 TP preservation            : 15 -> 12   FAIL
H3 recall non-degradation     : 0.625 -> 0.500  FAIL
H4 total-FP non-degradation   : 19 -> 10   PASS
H5 precision/F1 quality       : 0.441->0.545 / 0.517->0.522  PASS
```
Not re-litigated — `dfebe8f`'s integrity gates (`FB14_INFERENCE_INTEGRITY_PASS`, `FB14_SCORING_INTEGRITY_PASS`)
are accepted as-is; this mandate's job is the mechanism behind H2/H3's failure, not the scoring itself.

---

## 3 — Reproduction of the three lost TP (mandate §5)

All three reproduced exactly, using `RangeSemanticEngineV44` (frozen `3bb61cf`, `config_id 23d98c07...`)
fed the byte-verified canonical bars directly, with full per-bar instrumentation (ER/traversal/RND/
alternation/boundaries/touch counts, read from the module's own exposed pure functions after each
`observe_closed_bar` — no frozen code modified).

| CEO segment | n bars | `macro_reason` histogram over span | active structure(s) |
|---|---|---|---|
| FB14-003 [110,216) | 106 | `INSUFFICIENT_TRAVERSAL` ×106 (100%) | id=2 throughout |
| FB14-003 [232,288) | 56 | `INSUFFICIENT_TRAVERSAL` ×56 (100%) | id=2 throughout (**same** structure as above) |
| FB14-012 [211,480) | 269 | `INSUFFICIENT_TRAVERSAL` ×267, `INSUFFICIENT_EFFICIENCY` ×2 | id=7 throughout |

This matches Red Team's own figures exactly (267 bars `INSUFFICIENT_TRAVERSAL` for FB14-012 — confirmed
independently, not just re-cited).

**The critical, previously-unreported finding**: in every one of the three spans, the "structure" being
evaluated is the **same single, never-confirmed candidate for the entire span**, and its own boundary has
**zero price overlap** with the CEO's labeled zone:

| Candidate | Boundary | CEO zone | Price-IoU |
|---|---|---|---|
| FB14-003 id=2 | `[1687.00, 1719.90]` | `[1724, 1742]` (then `[1757,1766]`) | **0.000** (both) |
| FB14-012 id=7 | `[2514.02, 2525.85]` | `[2474, 2506]` | **0.000** |

`INSUFFICIENT_TRAVERSAL` is not describing a genuine range failing to complete a traversal *within its own,
correctly-anchored band* — it is describing traversal computed against a **boundary that no longer represents
where price has been trading for the entire duration of the labeled range.** Every trailing close falls on
one side of a stale reference, so `traversal_count` is mechanically 0 regardless of how much genuine two-sided
rotation the market is actually doing.

**Direct proof the market is genuinely rotating, not just drifting one-directionally** — I checked whether
`_detect_confirmed_swings` was finding anything at all in these spans, and whether `offer_swing` was
rejecting what it found:

- FB14-003 [97,229] (covers RANGE1, the TREND_UP transition, and the start of RANGE2): **38 swings
  detected**, alternating H/L (`LHLHLHLLHLHLHHLHLHHLHLHHLHLLHLHLLHLHLH` — predominantly alternating, with
  occasional same-side repeats consistent with genuine two-sided rotation, not a directional run). Every
  single one rejected by `offer_swing`'s tolerance check against the stale cluster center.
- FB14-012 structure 7's life (bars 220–470): **66 swings detected, 0 accepted.**

The rejection is not a bug in `offer_swing`/`Cluster` — the tolerance check
(`abs(price - center) <= tol_cluster * atr_ref`) is working exactly as designed; the touches are genuinely
too far from the *stale* center to be "the same level" by any reasonable measure. The defect is that nothing
in the current architecture allows the market to be re-evaluated by a **fresh** candidate once this happens.

---

## 4 — Exact traversal mathematics (mandate §6)

From `range_semantic_v4_4.py` (frozen, `833aedfd...`), read directly, not from memory:

- **Completed traversal** = a transition between the *outer thirds* only. `_traversal_zone()` splits
  `[boundary_lower, boundary_upper]` into three equal bands (U/M/L); a bar's close counts as `U` if
  `price >= boundary_upper - width/3`, `L` if `price <= boundary_lower + width/3`, else `M` (ignored).
  `traversal_count` increments only when the *most recent extreme visited* (`last_extreme`, tracked only
  across U/L visits, M is transparent) flips — i.e. it counts **U↔L round-trip legs**, order-agnostic, any
  number of intervening `M` bars ignored.
- **Order**: not required — U→L and L→U both count identically.
- **Repeated touches**: consecutive same-side touches do not double-count; only a genuine flip increments.
- **Window**: `W=29` bars (bounded `deque`), re-scanned in full each bar — O(W), not incremental.
- **Expiry**: implicit via the bounded deque — a touch simply ages out after `W` bars; there is no separate
  expiry concept.
- **Boundary migration**: `boundary_upper`/`boundary_lower` are **frozen at confirmation** (`T3`,
  `up.frozen=dn.frozen=True`); pre-confirmation, they are the LIVE cluster medians and can in principle move
  as new touches are accepted — but (§3 above) once a candidate goes stale, no new touches get accepted, so
  in practice the boundary **stops moving entirely** for an unconfirmed-and-stale candidate. This is the
  mechanism this diagnostic identifies.
- **Wick vs close/body**: traversal, like ER/RND, uses **close only** (`_trailing_closes`, pushed from
  `close` in `observe()`). Wicks affect `_detect_confirmed_swings` (which reads `high`/`low`) and hence which
  prices get *offered* as candidate touches, but not the traversal count itself.
- **Can a genuine rotating equilibrium remain permanently traversal-insufficient?** — **Yes, but not for the
  reason the mandate's opening hypothesis proposed.** It is not that a genuinely-rotating range fails to
  complete a full-amplitude round trip within a correctly-anchored `W`-bar window. It is that the *reference
  boundary itself* can freeze at a stale, pre-rotation level while the market's rotation continues elsewhere —
  making every trailing close land on one side by construction, independent of how much real rotation is
  happening.

**Separating the four evidence types the mandate asks about**, using this codebase's actual signals:

| Evidence type | Codebase signal | Status here |
|---|---|---|
| Touch evidence | `Cluster.offer()` acceptance into `up`/`dn` | **present and repeatedly rejected** — the touches exist, they just cannot join the stale cluster |
| Rotation evidence | `_detect_confirmed_swings` alternating H/L | **present** — confirmed directly, 38/66 alternating swings in the two traced spans |
| Traversal evidence | `traversal_count` (U↔L flips vs the *frozen* boundary) | **absent (0)** — because it is measured against the wrong reference, not because rotation evidence is absent |
| Two-sided-auction evidence | none explicit in this codebase; closest proxy is `alternation_rate` (supporting-only) | not diagnostic here — `alternation_rate` reads `touches_in_window`, which is *also* empty for a stale candidate (0 accepted touches), so it would show the same symptom, not a different one |

These four are **not equivalent**, and the gap between "rotation evidence exists" and "traversal evidence
registers" is exactly where this failure lives — not in the traversal *definition* itself.

---

## 5 — Sole-blocker vs multi-blocker (mandate §5's mandatory A/B/C/D distinction)

**Neither A, B, nor C in the mandate's literal framing. Closest to (D), with a specific mechanism (below).**

- **A (genuinely sole blocker in a correctly-anchored gate)** — false. The gate is not evaluating a
  correctly-anchored candidate; the boundary itself is wrong.
- **B (first-reported reason, another gate would also reject)** — not quite. ER and RND *are* computed
  against the same stale boundary throughout both spans and stay under their thresholds the whole time
  (verified directly over CEO span FB14-003 [110,216): ER 0.0009–0.337, RND 0.0010–0.549, both comfortably
  under `ER_max=0.5`/`RND_max=1.0`). They are not "also rejecting" — they simply happen not to trigger,
  somewhat coincidentally, because the stale zone is wide enough relative to the drift. This is not
  meaningful agreement between gates; it is two gates independently fed the same wrong input.
- **C (coding/semantic mismatch against the frozen design)** — no. `degeneracy_check`, `Cluster.offer`,
  `_evaluate_macro_formation`'s ER→traversal→RND priority, and `traversal_count`'s own definition all
  faithfully implement what `f241698`/`898f149` specify (independently re-confirmed by Red Team in `845a03c`,
  area-by-area). There is no drift between frozen spec and shipped code.
- **D (interaction failure)** — **yes, specifically**: `INSUFFICIENT_TRAVERSAL` is the correct, mechanically
  faithful *output* of the discrimination gate given its *input* (a stale boundary) — but the reason that
  input is stale is an **interaction between T3 and the candidate-lifecycle architecture inherited unchanged
  from V4.3.**

---

## 6 — Root-cause mechanism

Comparing V4.4 against V4.3 on the **identical canonical bars** (same loader, same config family, same
`degeneracy_check`/`Cluster`/`offer_swing` — byte-identical, imported not reimplemented) is the single most
informative check performed in this mandate:

```
FB14-003, structure "id=2" (same swings, same starting boundary in both — both start bar 44):
  V4.3: confirms quickly, later BREAKOUT_ACCEPTED at bar 85 -> slot freed -> structures 3,4 cycle fast
        (ZONES_DEGENERATE at 111, 122) -> structure 5 forms bar 129 at [1724.36, 1735.49]
        (near-exact match to the CEO's stated lower_approx=1724) -> stays active to bar 221 (BREAKOUT) ->
        this IS V4.3's matched TP.
  V4.4: NEVER confirms (T3 correctly rejects it during its early, genuinely-directional CHANNEL_UP-era
        formation) -> NEVER killed (degeneracy_check has no staleness dimension) -> _active_macro stays
        occupied by this one candidate for the rest of the 288-bar window -> no fresh candidate (V4.4's
        equivalent of V4.3's structure 5) ever gets a chance to form.
```

`degeneracy_check` (verified by direct re-read, `range_semantic_v4_3.py:403-415`) checks only
`bu < bl` (inversion) and `(bu - bl) <= 2*w_atr*atr_ref` (width floor) — **nothing about whether the boundary
still reflects recent price action.** This has been true since V4.3 and is unchanged in V4.4. It was never
consequential in V4.3 because V4.3's confirmation criterion (width+touch+duration only) either confirms a
candidate quickly or the same width/touch conditions that block confirmation tend to also produce
`ZONES_DEGENERATE` fairly promptly, cycling the slot. **V4.4's discrimination gate is a fundamentally
different kind of blocking condition: it can hold a *wide, non-degenerate* candidate in perpetual
non-confirmation indefinitely**, and nothing else in the shared architecture was ever designed to handle that
case, because it essentially could not arise before V4.4 existed.

**Answering the mandate's central question directly**: no, a valid MACRO RANGE does not semantically require
a complete outer-band-to-outer-band traversal — and the three CEO segments *do* qualify, evidenced by V4.3
successfully matching them via a correctly-anchored structure on the same bars. The weaker, more causal
concept traversal was meant to approximate is closest to **bidirectional rotation** / **two-sided boundary
participation** — and that evidence genuinely exists in all three spans (§4 table). It simply never reaches
the traversal calculation, because the *candidate holding the boundary* is the wrong one, and there is no
mechanism to replace it.

---

## 7 — Preservation analysis for H1/H4/H5 (mandate §8)

| | Current V4.4 | What this diagnostic implicates | Preserved? |
|---|---|---|---|
| ER/RND/MIN_TRAVERSALS/W numeric values | unchanged | not touched by this finding | yes — unchanged |
| Directional discrimination (T3 itself) | unchanged | not touched — the gate rejected the FB14-003 candidate *correctly* during its genuinely-directional early life | yes — unchanged |
| Candidate replacement (`degeneracy_check`, `forming_macro` gate) | no staleness dimension | **implicated** — this is the actual gap | needs a new, additive condition |
| WEAKENING / confirmed-structure lifecycle | unchanged | out of scope — only unconfirmed candidates are implicated | yes — unchanged |
| Episode identity (MERGE/CONTINUATION/REPLACEMENT) | unchanged | out of scope for FB14-003; a *related but distinct* observation surfaced for FB14-012 (§8 below), not fixed here | yes — unchanged in this mandate |

Because a candidate fix in this family (§10 below) operates **entirely upstream of T3** — it only decides
*whether a candidate is still eligible to be evaluated by T3 at all*, never *how T3 evaluates it* — it cannot
by construction weaken the directional discrimination that produced H1 (13→7) or H4/H5 (FP −9,
precision/F1 up). It can only affect cases where a candidate would otherwise sit unconfirmed indefinitely,
which is exactly and only the failure class observed here.

---

## 8 — A related, distinct observation surfaced in FB14-012 (disclosed, not fixed here)

While tracing FB14-012, before finding the sole stale-id=7 pattern was the *actual* cause of the scored 267-
bar failure, an **earlier version of my reproduction (later found to be based on the wrong bar-context
methodology, §1) showed a second, different pattern**: multiple sub-structures (my mistaken trace's ids 3, 7)
confirming and then being forced into `EPISODE_REPLACEMENT` (not `CONTINUATION`) after each
`BREAKOUT_ACCEPTED`, because the episode-identity priority rule (`f241698` §6, implemented in
`_episode_identity_for_new_macro`) **forces REPLACEMENT regardless of IoU/gap whenever the prior termination
was via `BREAKOUT_ACCEPTED`.** The CEO's own label for this exact span explicitly describes "doua excursii/
sweep-uri descendente profunde si reveniri in interior" (two deep descending excursions/sweeps and returns to
the interior) as part of the *same* range's character, not as episode-ending events.

This pattern **did not reproduce** in the corrected (canonical-bars-only) run — the corrected trace shows a
single stale candidate (id=7), not the fragmented multi-structure picture. I am disclosing the earlier,
now-superseded observation anyway, honestly, rather than discarding it silently, because it identifies a
**second, structurally real question** (independent of the stale-candidate mechanism, and independent of
whether it was the actual cause of this specific scored miss): does the forced-REPLACEMENT-after-breakout rule
correctly handle a "sweep" that a human labeler would call part of the same range's normal character rather
than a genuine episode-ending breakout? This is **not** resolved by anything in this diagnostic and is
explicitly out of scope for the traversal-focused mandate — flagged as a candidate topic for a **separate**
future mandate, not folded into the traversal correction below.

---

## 9 — Interaction with ER/RND/directional gates (mandate §9)

Traversal is **not** independently redundant with ER/RND in the cases observed — all three signals are
computed from the same trailing window and would, in a correctly-anchored candidate, be somewhat correlated
(a genuinely directional move tends to show high ER, low traversal, and high RND together) but they are not
measuring the same thing: ER measures path-efficiency (net/total-distance), RND measures net displacement
relative to width, traversal measures *how many times* price crosses the full band. A candidate could
plausibly fail ER while passing traversal (a noisy but net-directional move that still happens to touch both
thirds), or vice versa (this diagnostic's own cases: near-zero ER at many bars, since price is genuinely
chopping around, while traversal stays 0 because of the *reference* problem, not a *behavior* problem).

**Traversal is not "carrying too much responsibility" in a redundancy sense.** The actual overload is
architectural, not signal-theoretic: T3 is the **only** thing standing between "candidate" and "confirmed,"
and nothing downstream of a T3 rejection ever asks "should this candidate still exist at all." Under V4.3,
that question was implicitly, accidentally answered by `degeneracy_check` cycling candidates fast. V4.4 needs
an explicit answer, because it made confirmation harder without adding anything that makes *abandonment*
correspondingly easier. This is a role-architecture gap, not a case for demoting traversal to
`SUPPORTING_ONLY` (which would reopen exactly the directional-FP problem V4.4 was built to close — the
`normalized_drift` whole-life measure was already falsified as a substitute, and demoting traversal without a
replacement hard gate would have the same effect as disabling it).

---

## 10 — Self-falsification of the candidate correction family

**Candidate family**: an additive, unconfirmed-candidate **staleness abandonment** — a new termination
pathway, parallel to but separate from `degeneracy_check`, that frees `_active_macro` when an unconfirmed
candidate's recent evidence no longer supports its own boundary (repeated *rejected* touches over a bounded
trailing window, price persistently outside a tolerance band around the candidate's *current* center). This
does **not** touch ER/RND/traversal/alternation/`MIN_TRAVERSALS`/`W`, WEAKENING, episode identity beyond the
one new termination reason, confirmation timing, or snapshot/reason-code architecture beyond one new code.

Run against all 12 mandate-required scenarios:

1. **Clean horizontal RANGE** — touches are accepted normally (in-tolerance); no rejections accumulate; no
   abandonment. Safe.
2. **Genuine RANGE occupying only a sub-band for long periods** — as long as later touches stay within
   tolerance of the *current* median, they are accepted, not rejected; no false trigger. Safe.
3/4. **Shallow CHANNEL_UP/DOWN** — today, correctly never confirms (T3 rejects it the whole time, unaffected
   by this fix). If it also goes stale, it gets abandoned and a fresh candidate tries — which will also
   correctly fail T3. No new false-accept path is created; churn increases, confirmation behavior does not.
5. **Stair-step trend** — same as 3/4.
6. **Violent zigzag** — confirms today via genuine two-sided touches (a *disclosed*, accepted risk,
   unrelated to staleness — its cluster keeps accepting touches on both sides, so it never goes stale).
   Unaffected by this fix either way.
7. **One-sided oscillation** — touches on the populated side stay accepted; no spurious rejections from the
   quiet side alone (staleness requires *rejected*, not merely *absent*, evidence). Needs the exact trigger
   condition to be phrased as "repeated rejections," not "low touch count," to avoid a false-positive here —
   noted explicitly as a required property of any future concrete design, not resolved numerically here.
8. **Repeated midline crossings without real boundaries** — midline activity does not, by construction,
   generate rejected *outer*-touch swings; unaffected.
9. **Widening range** — the *current* mechanism's blind spot too (a widening range's early narrow anchor can
   itself go stale the same way). This fix would let a fresh, correctly-wider candidate form — an
   **improvement**, not a new risk.
10. **Migrating range** — this is the exact failure class demonstrated in §3/§6. The fix directly targets it.
11. **Range with infrequent outer-boundary touches** — infrequent-but-in-tolerance touches are accepted, not
   rejected; the mechanism is keyed on rejection, not frequency, so a genuinely slow-but-relevant range is not
   penalized. Needs verification once implemented (marked as a required test, §12), not assumed safe by
   argument alone.
12. **Directional market with frequent pullbacks** — pullback swings genuinely outside a directional
   candidate's zone would be rejected and could trigger abandonment — correctly, since a directional market
   should not hold a stale range-candidate hostage either; the fresh candidate that forms after abandonment
   is subject to the *same* T3 gate and will correctly fail to confirm on genuinely directional evidence.

**No counterexample found that would make this correction reintroduce a directional false-accept.** The
weakest point, flagged honestly: scenario 7/11 both depend on the exact trigger being phrased as
*rejected-evidence accumulation*, not *touch scarcity* — a naive "N bars without ANY new touch" trigger would
be measurably weaker (risking false abandonment of a genuinely slow, low-touch-frequency but valid range) than
"N *rejected* touches" (which by construction requires the market to be actively probing outside the
candidate's tolerance, not merely calm). This distinction is recorded as a **binding design constraint**, not
an optional preference, for whoever eventually specifies this mechanism.

---

## 11 — Correction classification (mandate §12)

```
TRAVERSAL_FAILURE_CLASS = D — INTERACTION_FAILURE
```
Specifically: the discrimination gate (T3, new in V4.4) interacts incorrectly with the candidate-replacement
architecture (`degeneracy_check` + the `forming_macro = _active_macro is None` single-slot invariant,
unchanged from V4.3) — the latter was never designed to free a candidate that fails to confirm *without* also
failing width/inversion, because under V4.3 that combination was rare enough not to matter. V4.4 made it
common. Not A (no numeric retuning of traversal fixes a wrong-boundary problem), not B (ER/RND are not
independently also rejecting for their own reasons — they are fed the same wrong input), not C (no
spec-vs-code drift found; Red Team's own independent audit, `845a03c`, already confirmed T3/`degeneracy_check`
faithfully implement the frozen design). A secondary, related-but-distinct question about the
forced-REPLACEMENT-after-breakout episode-identity rule was surfaced (§8) but explicitly **not** folded into
this classification — it did not reproduce as the cause of the corrected trace's actual failure and is flagged
separately for a future mandate, not claimed as part of this diagnosis.

---

## 12 — Candidate amendment family (design only — mandate §13)

**Not implemented. Not parameterized with any new numeric value.**

- **Semantic objective**: allow an unconfirmed MACRO candidate to be abandoned when its own recent evidence
  no longer supports its boundary, freeing the slot for a fresh candidate — without altering how any candidate
  is *evaluated* once formed.
- **Signal definition**: a bounded, trailing count of *rejected* `offer_swing` outcomes for the currently-
  forming candidate (touches detected via the existing `_detect_confirmed_swings` but refused by
  `Cluster.offer`'s tolerance check) — `UNRESOLVED_PARAMETER` for the exact window length and rejection-count
  threshold. Must be **rejection-count-based, not touch-scarcity-based** (§10's binding constraint).
- **Role**: `LIFECYCLE` — not a confirmation gate, not `SUPPORTING_ONLY` in the T3 sense; a termination
  condition parallel to `degeneracy_check`, evaluated only for `reached_confirmed=False` structures (never
  touches confirmed/WEAKENING structures at all).
- **Causal calculation**: purely a count of rejected touches within a bounded trailing window — no new
  price/ATR computation beyond what `offer_swing` already performs.
- **State required**: one small bounded counter (or a bounded deque of rejection bar-indices) on
  `StructureV44`, analogous in spirit to `_weakening_bars`. Bounded by construction, same discipline as every
  other V4.4 counter.
- **Bounded memory**: yes, by construction (fixed-size trailing window, same pattern as `_trailing_closes`).
- **Interaction with ER/RND**: none — evaluated entirely independently, before `_evaluate_macro_formation` is
  even reached (parallel to, and checked at the same priority tier as, `degeneracy_check`, i.e. before T2/T3).
- **Transition impact**: one new edge, `CANDIDATE`/`FORMING → TERMINATED`, via a new reason code (name
  `UNRESOLVED_PARAMETER` — e.g. `CANDIDATE_ABANDONED_STALE`, not fixed here). Does not touch T4–T9 (those are
  exclusively post-confirmation) or any existing edge.
- **Reason-code impact**: +1 new code, additive to the existing 40 (per the established `REASONS_V44`
  discipline — reachability would need its own mechanical proof, same pattern as the 11 codes already
  delivered).
- **Snapshot impact**: +1 small bounded field on `StructureV44`'s snapshot/restore (same pattern already used
  for `_weakening_bars`/`weakening_reason`). No contract/config identity impact beyond whatever version bump
  is chosen (§13 below).
- **Config impact**: at minimum one new field (rejection-count threshold) and possibly a trailing-window
  length (could reuse `W` — `UNRESOLVED_PARAMETER` whether it should be independent or shared).
- **Known risks**: (a) too-aggressive a threshold could abandon genuinely slow-to-confirm candidates
  prematurely, effectively re-narrowing the discrimination gate's own patience — needs calibration on evidence
  never used to derive it; (b) interacts with episode identity's `GAP_MAX`/`IOU_CONTINUE` — an abandoned
  candidate is not the same as a `TERMINATED`-via-breakout one for continuation-eligibility purposes; whether
  it should be treated as "non-breakout" (eligible for `CONTINUATION`) or excluded entirely is an open design
  question, not resolved here; (c) the §8 episode-identity observation, if it turns out to matter on fresh
  evidence, may need its own separate correction, not assumed subsumed by this one.

---

## 13 — Unresolved parameters

- Rejection-count threshold for staleness abandonment.
- Trailing-window length for counting rejections (reuse `W=29`, or independent — open).
- Minimum candidate age before staleness-eligibility (to avoid abandoning a candidate before it has had a
  fair chance — flagged in §10 as necessary but not specified).
- Whether an abandoned (never-confirmed) candidate counts as "non-breakout" for episode-continuation purposes.
- The exact new reason-code name.

None of these were chosen, ranked, or swept in this mandate. FB14 and MB3-001→024 were used only to *observe*
the failure and its mechanism, never to select or narrow any of the above.

---

## 14 — Required new tests (for whichever future mandate implements this)

- Every scenario in §10, as an automated adversarial test (12 minimum, matching the existing V4.4 adversarial
  suite's own convention).
- A direct reproduction of all three FB14 lost-TP spans as regression fixtures (synthetic reconstructions of
  the same *shape* — stale early candidate, later genuine rotation at a displaced level — not the real FB14
  bars themselves, to keep FB14 zero-future-validation-weight honored).
- A test proving an abandoned-but-never-confirmed candidate cannot itself be scored as a false TP (i.e., the
  fix must not accidentally let an under-evidenced candidate slip through as `OK_RANGE_MACRO`).
- A mutation test disabling the new abandonment condition, confirming the relevant regression tests fail
  (matching the non-vacuity discipline used throughout V4.4's own delivery).
- V4.3 regression suite unchanged and green (no V4.3 file touched by this family of fixes).

---

## 15 — Versioning recommendation (mandate §14)

```
RECOMMEND: V4.4.1
```
The core 5-state machine is unchanged (no new state; one new *edge* into the existing `TERMINATED` state).
The directional/discrimination architecture (ER/RND/traversal/alternation, `MIN_TRAVERSALS`, `W`) is
completely untouched — not "amended," not even read differently. Only the candidate-lifecycle layer gains one
additive, parallel termination pathway. This is narrower in scope than what the mandate's own guidance
describes as the V4.4.1 threshold ("only traversal semantics/role is amended") — this correction does not
even touch traversal's semantics or role; it touches what happens *before* traversal is ever computed.

---

## 16 — Fresh-evidence plan (mandate §15, design only — not authorized here)

**Recommend (B): analytically-derived/synthetic calibration, followed directly by a fresh blind batch.**
Reasoning: the unresolved parameters (§13) are lifecycle-timing values (how many rejections, how large a
window, what minimum age), not directional-discrimination thresholds — the kind of value the calibration
mandate for V4.4's own `ER_max`/`RND_max`/etc. already showed can be derived from synthetic construction
scenarios (known-ground-truth price paths exercising staleness directly) without needing a fresh
development-window pass first. A fresh blind batch (genuinely independent of this diagnostic, this design, and
any calibration derived from it — never FB14, never MB3) would then test the corrected mechanism exactly as
FB14 tested V4.4 itself. No selection, labeling, or execution of that batch is authorized or performed by this
mandate.

---

## 17 — Explicitly preserved V4.4 components

ER mechanism, RND mechanism, alternation's `SUPPORTING_ONLY` role, `MIN_TRAVERSALS`/`W`/`ER_max`/`RND_max`/all
9 calibrated values, WEAKENING lifecycle (all of T4–T9), confirmation timing/invariance architecture, episode
identity's MERGE/CONTINUATION/REPLACEMENT priority (the §8 observation is flagged, not amended), snapshot/
versioning architecture, the existing 40 reason codes and their semantics, `config_id`/implementation-
fingerprint identity mechanics. Every one of these was read, exercised, or cross-checked during this mandate
and none is implicated by the finding.

---

## 18 — Exact next recommended CEO action

Authorize a **separate, scoped design/calibration mandate** for the candidate-lifecycle staleness-abandonment
family (§12–§13), explicitly barred from touching anything in §17's preserved list, producing a frozen design
+ calibrated parameters (via synthetic/analytical derivation, §16) — followed by its own implementation
mandate, its own Red Team implementation audit, and only then a **fresh** blind batch (never FB14, never MB3)
to test whether TP/recall (H2/H3) recover while H1/H4/H5 hold. Separately, and independently of whether that
mandate is pursued: consider whether the §8 episode-identity observation (forced-REPLACEMENT-after-breakout
possibly over-fragmenting a range the CEO considers continuous through internal sweeps) warrants its own
future diagnostic — not decided here, flagged only.

---

## FINAL DIAGNOSTIC VERDICT

```
TRAVERSAL_FAILURE_DIAGNOSED_READY_FOR_FOCUSED_DESIGN
```

No implementation authorized by this mandate. `MB3-025→048` sealed and untouched throughout. FB14 used only
diagnostically (`FB14 = DIAGNOSTIC_ONLY_ZERO_FUTURE_VALIDATION_WEIGHT`), never to select or rank any numeric
value. Not authorized by anything here: Strategy Catalog, Alpha, AI Trader, LIVE_SHADOW, broker, live trading,
V4.4 promotion.
