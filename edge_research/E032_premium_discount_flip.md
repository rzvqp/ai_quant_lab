# E032 — Premium Discount Flip

**Program**: 40-Edge Alpha Discovery Program (Flow A). **Protocol**: `EDGE_RESEARCH_PROTOCOL.md`.
**Category**: Mathematical. **Permanent, append-only research log.**

## ⚠ HOLDOUT BREACH — QUARANTINE NOTICE (added 2026-07-21, documentation-only incident record)

**Status: HOLDOUT-CONTAMINATED. CLEAN RERUN REQUIRED.** Full incident record:
`PROJECT_STATE_v2.md` §8.23.

The Discovery pass below accidentally loaded and analyzed data from the Research Lab's own terminal
holdout period (2025-10-23 09:15 UTC → 2026-07-13 06:00 UTC). The shared Flow A loader
(`edge_research/_common.py::load()`) applied no date cutoff at the time this pass ran; this edge's own
snapshot sampling (every 16 bars) ran through bar index 84,080, mapping to **2026-07-10 11:15 UTC** —
inside the holdout window — and it fed directly into the by-quartile statistics below. **The old
terminal holdout is CONSUMED / INVALIDATED** by this and four other edges' own breach, project-wide
(`PROJECT_STATE_v2.md` §8.23) — this is a process/governance breach, not evidence that this edge's
findings below are false.

**Consequences, effective immediately**: the statistics and headline result below are
HOLDOUT-CONTAMINATED and **cannot support promotion** to Frozen Candidate, Validation, or a Final
Verdict in their current form. This edge requires a **CLEAN RERUN**, using only the data-split period
Flow A research is actually permitted to use, once `EDGE_RESEARCH_PROTOCOL.md` §8's own centralized
holdout-exclusion enforcement is implemented (not yet done — documentation only at this stage). The V0
hypothesis below is unchanged. Every result below is preserved verbatim as an audit trail — nothing is
deleted or edited.

Registry status (`EDGE_DISCOVERY_REGISTRY_v1.md`): `DISCOVERY_IN_PROGRESS` / `HOLDOUT_CONTAMINATED` /
`CLEAN_RERUN_REQUIRED`, simultaneously.

## V0 (frozen, registered 2026-07-20, verbatim)

> Price trading above/below the 50% equilibrium of a defined range (premium/discount) is more likely
> to move toward, not away from, that equilibrium.

Registered observable variables include "range-defining logic used" — the registry itself does not fix
one definition, so this pass tests two.

## Discovery pass 1 (2026-07-20)

**Data**: M15 + D1, 84,152 M15 bars, 2022-12-16 → 2026-07-13 (~3.6 years, short of protocol §2's ~5-6yr
requirement — early Discovery pass only).

**Method** (full disclosure in `e032_premium_discount_flip.py`):
- Two independent range definitions, each lookahead-safe (shifted to the prior, already-completed
  period): **(a) previous completed calendar day's D1 [low, high]**; **(b) previous completed
  calendar week's [low, high]**. `equilibrium = (high+low)/2`, `range = high-low`.
- Snapshots taken every 16 M15 bars (~4h, not every bar) to reduce within-period autocorrelation.
  `distance_t = (close_t - equilibrium)/range` (signed; >0 premium, <0 discount).
- `movement_toward_eq = |distance_t| - |distance_{t+N}|` for N∈{16 (~4h), 64 (~16h)}, holding
  equilibrium/range fixed across the window. Positive = moved closer to equilibrium (V0-consistent);
  negative = moved further into premium/discount.
- `|distance_t|` bucketed into quartiles; compared via Spearman correlation (distance vs movement) and
  an extreme-quartile-vs-near-quartile Mann-Whitney test.

**Headline result — a strong, highly significant reversion pattern using the DAILY range definition;
a much weaker one using the WEEKLY range definition — the choice of range-defining logic changes the
answer materially, exactly the sensitivity the registry itself flagged as worth checking.**

| Range def | N (window) | near-quartile mean movement | extreme-quartile mean movement | Spearman r | p |
|---|---|---|---|---|---|
| **Daily** | 16 (~4h) | −0.138 (moves away) | **+0.093 (moves toward)** | **0.527** | ~4e-299 |
| Daily | 64 (~16h) | −0.285 | +0.010 | 0.447 | ~1e-205 |
| Weekly | 16 (~4h) | −0.026 | −0.008 (still net away, just less so) | 0.039 | 0.0049 |
| Weekly | 64 (~16h) | −0.085 | −0.033 (still net away) | 0.074 | ~1e-7 |

With the daily-range definition, price starting in the most extreme premium/discount quartile
genuinely moves NET TOWARD equilibrium over the following 4h (+0.093) while price already near
equilibrium drifts NET AWAY (−0.138) — a real, strongly monotonic, highly significant pattern (n=4,206
snapshots). With the weekly-range definition, the *direction* of the correlation is the same sign, but
far weaker in magnitude and, notably, price in every quartile shows net movement AWAY from equilibrium
on average (all four quartile means negative at N16) — the "extreme quartile moves less far away" is a
much weaker claim than "extreme quartile reverses toward equilibrium."

**Central falsification concern raised by this pass, not resolved (this is the most important caveat
in this log)**: the daily-range result may be substantially a restatement of a very generic, already
well-documented market property — **extended moves tend to partially mean-revert** — rather than
something specific to the ICT "50% equilibrium" construct. Because `equilibrium`/`range` here are fixed
at a SINGLE historical scale (yesterday's completed range), a bar showing a large `|distance|` is, by
construction, simply a bar that has moved a large amount relative to a fixed recent yardstick — the
same underlying fact that drives E026's (ADR Exhaustion) upside-continuation finding and any generic
"stretched price reverts somewhat" effect. This pass did not test whether the premium/discount framing
adds anything **beyond** a generic distance-from-a-recent-reference-point control (e.g., distance from
a simple moving average of the same recent lookback) — until that control is run, "premium/discount
equilibrium reversion" and "garden-variety overextension reversion" cannot be distinguished from each
other with the evidence gathered so far.

## Answers to the 9 mandatory Discovery questions

1. **Does the edge exist at all?** A statistically overwhelming pattern exists with the daily-range
   definition; a much weaker one with the weekly-range definition — but see the falsification concern
   above: it is not yet established that this is more than generic overextension mean-reversion.
2. **Frequency?** Every ~4h snapshot has a well-defined distance (continuous, not an event-count
   concept the way E025/E026/E029 were) — 4,206 daily-range snapshots and 5,149 weekly-range snapshots
   over the sample.
3/4/5/6. **Days/sessions/volatility regimes it works or fails in?** Not sliced in this pass (deferred
   — the range-definition sensitivity and the mean-reversion-confound question were higher priority
   given the time available this session).
7. **Filters that improve it?** Not searched (protocol prohibition at Discovery).
8. **Conditions that invalidate it?** The choice of range-defining logic itself is such a condition —
   weekly range shows a much weaker effect than daily range, and the registry's own listing of
   "range-defining logic used" as an observable variable is validated as genuinely load-bearing.
9. **Out-of-sample?** Not tested via an explicit time-split in this pass.

## Current status

**Version: V0 (no refinement written yet — blocked on the overextension-confound control before any
responsible V1 wording).** **Verdict: NONE ISSUED** — per protocol §2, below the ~5-6yr horizon.
Remains in **Stage 2 — Discovery, first pass complete**.

**Next steps if revisited**: (a) build the overextension-confound control (distance from a simple
moving average of matched lookback) to test whether "equilibrium" adds anything beyond generic
mean-reversion; (b) test additional range definitions the registry's own wording suggests (e.g. a
rolling swing-based range akin to `s1.py`'s `rmax20/rmin20`, deliberately NOT imported per the two-flow
separation but reproducible independently); (c) session/volatility/day slices; (d) formal out-of-time
split; (e) Tier-0 history extension before any Frozen Candidate/Validation/Walk-Forward/Final Verdict.

**Artifacts**: `e032_premium_discount_flip.py`, `e032_premium_discount_flip_results.json`.
