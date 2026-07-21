# PORTFOLIO_ARCHITECT_TIEBREAK_EVIDENCE_REPORT.md — Tie-Break Bias Evidence (Flow B roadmap step 2/6)

**Status: EVIDENCE GENERATION ONLY. No code implemented or modified, no runtime behavior change, no new
`ArchitectMode`.** Produced per explicit CEO authorization of Candidate 1 ("genuine-tie round-robin
fairness," `PORTFOLIO_ARCHITECT_POLICY_RESEARCH.md`) for evidence generation only. Determines whether
deterministic alphabetical tie-breaking in the Scoring Engine's own Ranker produces a measurable
systematic allocation bias, using one offline, deterministic, zero-production-diff instrumented
simulation over the CEO-approved, non-holdout 12-month window (2024-10-23 → 2025-10-23,
`phase69a_funnel_run.py`'s own established precedent — not a new or enlarged window invented for this
study).

**Headline finding**: exact score ties are frequent (38.7% of multi-candidate bars, 3,217 tied groups
over the year), alphabetical `strategy_id` is empirically confirmed as the effective tie-break in 100% of
cases, and there is a measurable systematic bias favoring early-alphabet strategies. The bias's effect on
FINAL real allocations is small in absolute count (2 of 3,065 replayed tie-bars would see a different
real winner) but the underlying mechanism is genuine, reproducible, and — separately — round-robin
resolution can, in rare cases (6 of 3,065), shift which specific denial reason a *third, uninvolved*
candidate receives, a real and disclosed nuance to Q6/Q7 below.

---

## Method and data source

Zero-file-diff instrumentation (same precedent as `phase69a_funnel_recorder.py`/`ceo_strategy_
constraint_root_cause_study.py`/`portfolio_architect_phase2a_calibration.py`): `harness._scoring_
engine.score_batch` and `harness._risk_manager.evaluate` monkey-patched post-`load()`, each wrapper
calling the original implementation and returning its result unchanged, only additionally recording it.
Zero lines changed in any `ai_trader/` source file. Shadow Evidence was disabled this run (not needed
for this question, and Phase 1 already proved Shadow's presence/absence doesn't affect Signal/Scoring/
Risk Manager behavior) to reduce runtime. Full 43-strategy universe, single symbol (XAUUSD), 23,839 bars
processed (200-bar warmup + the full 12-month window).

**Genuine tie** is defined as an EXACT match, across ≥2 actionable (`BUY`/`SELL`) candidates in the same
`(symbol, as_of)` batch, on all three fields the Scoring Engine's own Ranker uses ahead of `strategy_id`
(`scoring_engine/ranker.py:13-26`): `total_score`, `component_scores.historical_confidence`,
`component_scores.signal_strength`. A dedicated negative control (§7) confirms near-ties (differing by as
little as 1 point) are never counted.

---

## Q1 — How often do exact score ties occur?

- 7,916 bars had ≥2 actionable candidates on the same symbol/bar (the necessary precondition for a tie).
- **3,065 of those bars (38.7%) contained at least one genuine, exact tie** — a substantial, not
  marginal, share.
- 3,217 distinct tied groups occurred (some bars had more than one simultaneous tied group). Group-size
  distribution: 2,751 pairs, 399 triples, 59 groups of 4, 7 groups of 5, 1 group of 6.

## Q2 — Which production strategies participate?

**25 of the 43 registered strategies** appeared in at least one tied group over the year:
`S2, S4, S5, S6, S8, S10, S12, S13, S14, S18, S21, S22, S24, S26, S28, S29, S39, S40, S41, S44, S45,
S46, S48, S50, S51`. Participation is highly uneven — `S40` (1,158 occurrences), `S26` (985), `S51`
(777), `S50` (694), `S12` (570), `S44` (434) account for the large majority of tie-group memberships;
several strategies (`S8`, `S14`, `S29`, `S21`, `S2`) appear only a handful of times. This reflects each
strategy's own signal-generation frequency/pattern, not the tie-break mechanism itself.

## Q3 — Is alphabetical ordering the effective final tie-break?

**Yes, confirmed empirically in 3,217 of 3,217 tied groups (100%)** — the candidate holding the best
(lowest-number) `rank` within every tied group was, without exception, the alphabetically-first
`strategy_id` among the tied members. This directly confirms, empirically and not just by reading the
source, that `scoring_engine/ranker.py`'s own documented tie-break (`strategy_id` ascending, as the last
resort after `total_score`/`historical_confidence`/`signal_strength`) is the actual, effective mechanism
deciding these cases in production data.

## Q4 — Over long historical simulation, does alphabetical ordering systematically favor early strategy IDs?

**Yes.** Assigning each strategy an ordinal position (0 = alphabetically first, sorted over the 25
strategies that ever participated in a tie), the mean ordinal of tie WINNERS (20.37) is measurably below
the mean ordinal of the overall tie-PARTICIPANT pool (27.22) — a gap of ~6.85 ordinal positions. This
comparison is the correct one for isolating the tie-break's own effect (not just which strategies happen
to generate tied signals more often): if ties were resolved with no ID-based bias at all (e.g. purely
randomly), the expected mean winner ordinal would converge to the mean participant ordinal; the observed,
consistent gap below that baseline is evidence of a genuine systematic bias, not sampling noise from
participation frequency alone.

## Q5 — Does this affect only identical-score opportunities?

**Yes, by construction and confirmed by a dedicated negative control.** The tie-detection logic requires
an EXACT match on all three fields; a separate scan found 3,277 bars with a NEAR-tie (score differs by
exactly 1 point) that were correctly excluded from every count above. No near-tie was ever treated as a
genuine tie.

## Q6 — Would replacing the alphabetical fallback with a deterministic round-robin preserve all existing architectural contracts?

**Mostly yes, with one disclosed, empirically-observed exception that must not be hidden.**

- **Confirmed preserved**: Strategy Health eligibility, Scoring Engine's own scores/quality/
  recommendation fields, sizing methodology, and the overall gate ORDER are untouched in every one of
  3,065 replayed tie-bars — the round-robin mechanism, as specified, only ever reassigns `rank` within an
  already-exactly-tied subset (`dataclasses.replace(score, rank=...)`, mirroring the Phase 2 design's own
  §5 discipline), never any other field.
- **Confirmed preserved, empirically**: across all 3,065 replayed bars, the shared slot's own
  OCCUPANCY status (whether a real ALLOW happens at all this bar) never flipped — in the 2 bars where
  the WINNER changed, a real ALLOW still occurred in both the actual and round-robin scenario, just for a
  different strategy. Aggregate ALLOW-count-per-bar neutrality holds in 100% of observed cases.
- **The disclosed exception**: in 6 of 3,065 replayed tie-bars (0.20%), the WINNER did NOT change, but a
  *different, uninvolved* candidate elsewhere in the same batch received a DIFFERENT denial-reason code
  under round-robin than under the actual run (e.g. `LIMIT_MAX_PER_SYMBOL` vs. `SIZE_BELOW_MIN`). Root
  cause, confirmed by inspection: Risk Manager evaluates opportunities sequentially against a *running*
  portfolio view that updates after each ALLOW (`risk_manager/engine.py:136-153`) — swapping WHICH member
  of a tied group occupies the group's own best rank-slot does not change any OTHER candidate's own
  `rank`, but it CAN change whether a bystander candidate positioned between the tied group's original
  and reassigned rank values sees the shared slot as already-occupied (by the time Risk Manager reaches
  it) versus still-open, changing which specific gate it fails at. **This is a genuine, structural,
  second-order interaction with Risk Manager's own sequential evaluation — not a flaw in the round-robin
  mechanism's own logic, but a real limit on the claim "nothing else ever changes."**

## Q7 — Could such a policy be implemented without changing any score, eligibility, or risk decision?

**Score and eligibility: yes, unconditionally** — confirmed structurally (only `rank` is ever
reassigned) and empirically (no score/eligibility field ever differed in any replayed bar).
**Risk decision, in the narrowest sense of "the final ALLOW/DENY outcome and identity": yes, for 3,059 of
3,065 bars (99.8%)** — the winner and the DENY/ALLOW status of every other tied member is unchanged.
**Risk decision, in the fuller sense of "the exact denial-reason code every candidate in the batch
receives": no, not unconditionally** — the 6-bar exception in Q6 is a real, if narrow and second-order,
counterexample. Any future implementation proposal must disclose this exception rather than claim a
blanket guarantee that does not hold.

---

## Required outputs

- **Tie frequency**: 3,065 / 7,916 multi-candidate bars (38.7%); 3,217 tied groups over the 12-month
  window.
- **Affected strategies**: 25 of 43 (§Q2), highly uneven participation.
- **Bias measurements**: mean winner ordinal 20.37 vs. mean participant-pool ordinal 27.22 (§Q4);
  alphabetical order confirmed as the effective tie-break in 3,217/3,217 cases (100%, §Q3).
- **Simulations comparing alphabetical vs. round-robin**: 3,065 tie-bars replayed through a freshly-
  constructed, isolated `RiskManager` instance (same config, captured `risk_context`/`portfolio_state`
  snapshots — shadow evaluation only, never fed back into the completed run); 2 bars (0.065%) show a
  different real ALLOW winner; 6 bars (0.20%) show a bystander denial-reason-type shift (§Q6).
- **Invariants** (proposed, for any future specification, not implemented here): output remains a
  permutation of the same objects; only `rank` differs, and only within an EXACTLY-tied subset (verified,
  not near-ties, §Q5); the shared slot's own occupancy status must remain unaffected in aggregate (holds,
  100% of observed bars); round-robin state must be a pure function of the sequence of past genuine ties
  only (no look-ahead — this replay methodology itself never used data at or after each bar's own
  `as_of`).
- **Negative controls**: near-tie exclusion (3,277 correctly excluded, §Q5); alphabetical-tiebreak
  confirmation (3,217/3,217, §Q3) doubles as a control that the detection logic itself is sound (if
  alphabetical were NOT the effective mechanism, this count would be less than 100%).
- **Recommendation**: see below.

---

## Recommendation

The evidence supports Candidate 1 as **architecturally sound and empirically real** (frequent ties,
confirmed alphabetical bias, mechanism behaves almost entirely as specified) but **not yet a clean,
zero-exception specification** — the Q6/Q7 bystander denial-type drift (6/3,065 bars) must be resolved or
explicitly accepted as a bounded, disclosed limitation before any implementation is authorized. This
report does not resolve that question; it surfaces it for CEO decision, per the CEO's own explicit
instruction not to implement. Two honest paths forward, neither decided here: (a) accept the 0.20%
bystander-drift rate as an acceptable, disclosed limitation and proceed to a full Phase-2-style
implementation design; or (b) investigate whether a stricter round-robin variant (e.g. one that also
preserves the exact SET of rank values every non-tied candidate is evaluated relative to, not just their
own individual rank) eliminates the drift entirely — itself unexplored, unimplemented, and not proposed
as a given here.

---

## Governance confirmation

No code was written or modified. No `ArchitectMode` was added. No harness change. Zero diff confirmed
against every frozen module and every Flow A artifact — verified directly via `git status`/`git diff
--stat` before this document's own commit.
