# E025 — Round Numbers

**Program**: 40-Edge Alpha Discovery Program (Flow A). **Protocol**: `EDGE_RESEARCH_PROTOCOL.md`.
**Category**: Mathematical. **This file is the permanent, append-only research log for this edge —
nothing below is ever deleted or retroactively edited; refinements are new, dated, appended versions.**

## V0 (frozen, registered 2026-07-20, verbatim from `EDGE_DISCOVERY_REGISTRY_v1.md`)

> Price reacts (as support/resistance/magnet) at round psychological levels (e.g. multiples of
> $10/$50/$100).

Measured outcome (as registered): reaction rate/magnitude at each round-number granularity vs. a
matched non-round-level control.

## Discovery pass 1 (2026-07-20)

**Data**: `data/market/OANDA_XAUUSD_M15.csv`, 84,152 bars, 2022-12-16 10:45 UTC → 2026-07-13 06:00
UTC (**~3.6 years — short of the protocol's §2 ~5-6 year requirement; this is explicitly an early,
cheap Discovery pass per §2, not a Validation/Walk-Forward/Final-Verdict-eligible run**).

**Method** (full disclosure in `e025_round_numbers.py`, committed alongside this log):
- Granularities tested: $10, $50, $100.
- Round levels = multiples of the granularity. **Control levels = the same granularity's levels
  shifted by half a step** (e.g. for $50: control = ...,25,75,125,...) — identical density, identical
  price range, deliberately non-round, exactly as the registry's own "measured outcome" specifies.
- A "touch" = an M15 bar whose [low, high] range spans a level. Repeated touches of the *same* level
  are merged into one independent event only if ≥8 bars (2h) have passed since the last kept event on
  that level (reduces chop/whipsaw pseudo-replication).
- Approach direction: +1 if price was below the level the bar before the touch, −1 if above.
- Reaction, measured N bars later (N=4 ≈1h, N=16 ≈4h): `reaction = -direction * (close[N bars later]
  - level) / ATR14`. **Positive = price reversed away from the level** (round level behaved as
  support/resistance). **Negative = price continued through the level** in the approach direction.
- Round vs. control compared via bootstrap mean + 95% CI and a two-sided Mann-Whitney U test (chosen
  over an analytic t-test because this project's own established finding, `PROJECT_AUDIT.md` D1, is
  that outcome variables of this kind are heavy-tailed and analytic normal-approximation tests are
  unreliable here).
- No parameter above (N, cooldown, granularities) was chosen after looking at the outcome — these are
  the literal first-pass defaults, not a search.

**Headline result — the V0 hypothesis is NOT supported as stated; if anything, at $50 granularity the
opposite pattern is observed:**

| Granularity | n events (round / control) | Overall reaction, round vs control (N=16, ~4h) | Mann-Whitney p |
|---|---|---|---|
| $10 | 10,591 / 10,993 | round mean −0.047 vs control +0.004 (both CIs include 0) | 0.33 (n.s.) |
| $50 | 2,136 / 2,642 | **round mean −0.21 [CI −0.35,−0.07] vs control +0.08 [CI −0.05,+0.20]** | **0.0022** |
| $100 | 1,062 / 1,101 | round mean −0.16 (n.s.) vs control −0.24 [CI −0.45,−0.04] | 0.19 (n.s.) |

At $50, round levels show a **significantly more negative** reaction than the matched control — i.e.
price is *more* likely to break through a round $50 level than a matched non-round level, not less.
This is the opposite sign from V0's "magnet/support-resistance" framing. $10 and $100 show no
distinguishable round-vs-control difference.

**Direction-of-approach breakdown (g=$50, N=16)** — the $50 effect is not a symmetric "round levels
are just weaker" story; it is concentrated in one approach direction:
- Approach from below (rising into the level): round −0.287 vs control −0.092, n=1077/1272, p=0.13
  (not significant, direction consistent).
- **Approach from above (falling into the level): round −0.127 vs control +0.236, n=1059/1370,
  p=0.0059** — falling into a round $50 level, price is significantly more likely to break *down*
  through it than a matched non-round level is; the control level here shows the classically-expected
  bounce (+0.236, positive = reversal) while the round level does not.

**Session/day/volatility slices (g=$50, N=16, exploratory — no multiple-comparison correction
applied; treat individual slice p-values as suggestive, not confirmatory):**
- Round < control in every session and on every day of the week tested (consistent sign, 15/15 slices)
  — nominally significant in NY (p=0.0029) and Asia (p=0.010) sessions, and on Wednesday (p=0.011) and
  Friday (p=0.036); not significant in London or the "late" session, or on Mon/Tue/Thu.
- Round < control in all three volatility terciles (low/mid/high), none individually significant
  (smaller per-slice n); the pooled/overall $50 effect is the more reliable number here.

**Split-sample check (informal, in lieu of a full 5-6yr Validation-stage split — this is a Discovery-
stage robustness check, not Stage 4 Validation)**: the dataset was split into two ~1.8-year halves
(2022-12-16→2024-09-29 and 2024-09-29→2026-07-13). The **direction** of the $50 effect (round more
negative than control) replicates in both halves (half1: round −0.19 vs control +0.11, n=445/761,
p=0.24; half2: round −0.21 vs control +0.06, n=1690/1881, p=0.0059). Statistical significance is
concentrated in the second, larger-n half; the first half's smaller event count (fewer $50-multiple
crossings when gold traded in the lower ~$1700-2000 range) limits its own power, but the sign is
consistent, not reversed — this is the strongest single piece of evidence in this pass that the
finding is not a one-period artifact.

## Answers to the 9 mandatory Discovery questions

1. **Does the edge exist at all (signal distinguishable from noise)?** Granularity-dependent. No at
   $10 or $100 in this pass. Yes at $50 — but the signal found is the *reverse* of V0's stated
   direction (breakthrough, not support/resistance).
2. **Frequency?** $10 ≈ 8.1 events/day; $50 ≈ 1.6 events/day; $100 ≈ 0.8 events/day (per grid, both
   round and control, over 3.6 years).
3. **On which days does it work (for the $50 effect, in its own — reversed — direction)?** Consistent
   sign every day; nominally significant Wednesday and Friday only.
4. **On which days does it fail?** No day showed the opposite (V0-consistent, positive/support) sign
   at $50; Monday/Tuesday/Thursday were directionally consistent but not individually significant.
5. **In which sessions does it work?** NY and Asia (nominally significant); not London or "late".
6. **In which volatility regimes does it work?** Consistent sign across low/mid/high vol terciles; no
   individual tercile reaches significance alone (power-limited by smaller per-slice n).
7. **Are there filters that improve it?** Not searched in this pass — searching for a filter that
   flips the sign back toward V0's original claim would itself be exactly the "optimize until
   profitable" behavior §7/Stage 2 of the protocol forbids. Not attempted.
8. **Are there conditions that invalidate it?** Yes — the effect is absent at $10 and $100 granularity,
   and (within $50) markedly weaker/non-significant when approaching from below vs. from above.
9. **Does it survive out-of-sample testing?** Partial answer only, at Discovery-pass level (not the
   protocol's own formal Stage 4 Validation, which requires the full 5-6yr horizon this dataset does
   not yet have): the direction of the $50 effect replicates in an out-of-time split-half check; formal
   significance is present only in the second, higher-event-count half.

## Current status

**Version: V0 → informal V1 candidate framing recorded below (not yet a Frozen Candidate — Stage 3
has not been entered).** **Verdict: NONE ISSUED.** Per `EDGE_RESEARCH_PROTOCOL.md` §2, no Final
Verdict may be issued on less than the full ~5-6 year horizon; the available M15 history (~3.6 years)
is short of that requirement, so this edge remains in **Stage 2 — Discovery, first pass complete**,
not Early-Refuted and not promoted.

**V1 candidate framing (a refinement suggested by this pass's own evidence, not yet frozen, not yet
tested against unseen data)**: "At $50-multiple round levels in XAUUSD, price falling into the level
from above is more likely to break through than a matched non-round control, particularly in NY/Asia
sessions" — i.e. a tentative **liquidity-sweep/breakthrough** framing, which is the opposite mechanism
from V0's **magnet/support-resistance** framing. Both $10 (too fine-grained/too frequent to carry
distinct psychological weight) and $100 (too coarse/too few events in this sample for power) show no
distinguishable effect either way.

**Next steps, if this edge is revisited**: (a) acquire the Tier-0 history extension so a genuine
5-6yr Frozen-Candidate/Validation/Walk-Forward can run; (b) if revisited, the Frozen Candidate should
be written as the reversed, direction-specific $50 hypothesis above, not V0's original wording,
per §1's requirement that refinements are new appended versions; (c) explicitly test whether the
"breakthrough" pattern is itself tradeable net of costs (this pass measured statistical reaction only,
no cost model, no execution simulation — consistent with Discovery scope, per protocol §0.2 "not to be
made profitable").

**Artifacts**: `e025_round_numbers.py` (analysis script), `e025_round_numbers_results.json` (full
output incl. all slices).
