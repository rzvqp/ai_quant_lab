# E014 — Inside Bar False Breakout

**Program**: 40-Edge Alpha Discovery Program (Flow A). **Protocol**: `EDGE_RESEARCH_PROTOCOL.md` §§1-8
only — §9 (Immediate Scalping Response / Protocol v2) explicitly NOT performed, per the CEO's own
priority-shift instruction. **Category**: Price Action / Structure. **This file is the permanent,
append-only research log for this edge — nothing below is ever deleted or retroactively edited;
refinements are new, dated, appended versions.**

**Second edge run under the reordered Tier-1 sequence** (`NEXT_SESSION_FLOW_A.md`, 2026-07-21 priority
audit). Only E014 authorized this session — no other edge started in parallel. Data loaded exclusively
via `_common.load()` (holdout-enforced); no direct CSV read anywhere in
`e014_inside_bar_false_breakout.py`.

## V0 (frozen, verbatim from `EDGE_DISCOVERY_REGISTRY_v1.md`)

> A false breakout of an inside-bar range frequently reverses back through the range, offering a fade
> entry.

Measured outcome (as registered): false-breakout rate and magnitude of the reverse move. Observable
variables: inside-bar range width, breakout direction, time-to-reversal, volatility regime.

## Definitions predeclared BEFORE any outcome was inspected

1. **Inside bar**: a bar whose high ≤ the immediately preceding bar's ("mother bar") high AND whose low
   ≥ the mother bar's low (strict containment, parameter-free).
2. **Nested/overlapping inside bars**: only the FIRST inside bar of a compression chain is used as a
   primary event; later bars in the same chain are not counted separately (avoids within-chain
   pseudo-replication, the same rationale as E006's/E015's "first instance only" conventions).
3. **Breakout**: the first bar after the inside bar whose CLOSE is beyond the inside bar's own range.
4. **False breakout (fade-through)**: read V0's own wording literally ("reverses back **through** the
   range") — the primary definition requires a subsequent CLOSE beyond the **opposite** boundary within
   the response horizon, not merely a return to neutral. A weaker "returns inside at all" metric is
   also tracked internally but is not the primary test.
5. **Response horizon**: 50 bars — the shared ceiling of `_profile.HORIZONS`, avoiding a second,
   arbitrary time parameter.
6. **Invalidation**: if price never breaks out within 200 bars, or the inside bar has zero range, or
   the ATR reference is invalid, the event is excluded (NO_BREAKOUT — never triggered).
7. **Dual-side (whipsaw) breakouts**: handled naturally by definition (4) — a close beyond the opposite
   boundary at any later point IS a confirmed fade-through, no special case needed.
8. **First vs. repeated breakout attempt**: after attempt 1 resolves as not-a-confirmed-fade (either the
   horizon expires, or price returns inside without confirming), a 2nd attempt is tracked if a new
   close beyond either boundary occurs within the remaining horizon. Bucketed 1st vs. 2nd-or-later.

## Controls (distinguishing 4 candidate explanations, per explicit requirement)

- **Primary**: real inside bars (strict containment).
- **Control B — generic single-bar breakout**: a random sample of ordinary bars (no compression or
  containment condition at all) as the reference range.
- **Control C — generic compression**: bars in the lowest tercile of (own range / prior ATR14), with NO
  containment requirement.
- **Control D — ordinary mean-reversion baseline**: fully synthetic, ATR-sized random-matched ranges at
  random points (seed=42) — the same convention as E010/E012/E015's own random-matched control.

Timeframes tested: M15, H1, H4 (all three registered for E014, all present in the clean dataset).

## Results — primary (attempt 1 only)

| Timeframe | n events | Fade rate | Sustained rate | Median time-to-fade |
|---|---|---|---|---|
| M15 | 9,091 | 72.4% | 27.6% | 8 bars |
| H1 | 2,386 | 71.6% | 28.4% | 8 bars |
| H4 | 683 | 71.3% | 28.7% | 8 bars |

The raw fade rate is real, high, and remarkably stable across all three timeframes.

## Results — control ladder (attempt 1 only, real vs. each control)

| Comparison | M15 | H1 | H4 |
|---|---|---|---|
| Real (72.4/71.6/71.3%) vs. **Control D** (67.7/67.6/64.7%) | p=5.4e-12 | p=0.0028 | p=0.0107 |
| Real vs. **Control B** (67.9/67.9/67.3%) | p=5.3e-11 | p=0.0067 | p=0.127 (n.s.) |
| Real vs. **Control C** (75.3/76.3/71.9%) | p=6.6e-6 (real **lower**) | p=0.00025 (real **lower**) | p=0.857 (n.s.) |

Real inside bars beat the fully synthetic baseline (D) on all three timeframes, and beat the generic
uncompressed-bar control (B) on two of three — but do **not** beat generic compression (C); if
anything, Control C's fade rate matches or **exceeds** real inside bars on every timeframe.

**Decisive cross-control test — is compression (not mere "real market bar-ness") the actual driver?**

| Comparison | M15 | H1 | H4 |
|---|---|---|---|
| Control C (compression) vs. Control D (random) | **p=4.2e-30** | **p=2.6e-11** | **p=0.0053** |
| Control B (generic bar) vs. Control D (random) | p=0.751 (n.s.) | p=0.804 (n.s.) | p=0.331 (n.s.) |

Compression alone beats the random baseline decisively on all three timeframes. An ordinary,
uncompressed real bar does **not** beat the random baseline at all, on any timeframe. This isolates the
effect cleanly: it is bar-range **compression relative to volatility** that drives the fade tendency,
not the realness of the bar, and not the specific strict-containment ("inside bar") condition.

## Falsification of the most dramatic-looking pattern — attempt 1 vs. attempt 2

Attempt-1 fade rate (~71-72%) collapses to ~11-13% on a 2nd attempt, an enormous, highly significant
decay (p≈0 on M15, p=6.6e-92 on H1, p=4.7e-26 on H4) — initially the most striking number in this
analysis. **This does not survive a control check.** All three controls (B, C, and — critically —
**D, the fully synthetic random-matched control with no connection to real market structure at all**)
show the identical collapse, at least as extreme (e.g. Control D on H1: p=1.1e-99). This proves the
decay is a **generic, mechanical artifact of the attempt-selection process itself** — attempt 2 only
exists for events where price already broke out, returned, and broke out again, a population
structurally enriched for sustained moves regardless of what the reference range is. **This is not an
edge of any kind and is explicitly not proposed as a V1 candidate**, despite its striking p-values.

## Context slices (attempt 1 only)

| Variable | M15 | H1 | H4 | Replicates? |
|---|---|---|---|---|
| Direction (down > up fade rate) | up=69.6% p=0.0007, down=75.4% p=0.0002 | up=67.8% p=0.018, down=76.2% p=0.0056 | up=66.8% p=0.13, down=77.7% p=0.048 | Yes (M15, H1 clearly; H4 weaker, same direction) |
| Mother-bar size (smaller → more fade) | low=76.0% p<0.001, high=67.5% p<0.001 | low=76.7% p=0.0054, high=65.4% p=0.0012 | not significant | Yes (M15, H1) |
| Volatility regime (low vol → more fade) | low=78.9% p<1e-12, high=64.1% p<1e-18 | low=75.4% p=0.060, high=67.9% p=0.039 | not significant | Partially (M15 strong, H1 borderline) |
| Compression ratio (own tercile) | low=74.3% p=0.041, high=69.8% p=0.008 | not significant | not significant | No |
| Session | significant on M15 only (all p<1e-4) | all p>0.29 | all p>0.22 | **No** — M15-only, not robust |
| Day of week | not significant anywhere | not significant anywhere | not significant anywhere | No effect found |

## Robustness

- Yearly stability: fade rate stable across years on all three timeframes (no single-year
  concentration; full figures in `e014_inside_bar_false_breakout_results.json`).
- Event counts scale sensibly across timeframes (9,091 M15 → 2,386 H1 → 683 H4), consistent with
  inside-bar frequency scaling roughly with bar count.

## Headline result — V0 NOT SUPPORTED as an inside-bar-SPECIFIC mechanism; a real, replicated,
## compression-driven effect exists instead

The raw fade phenomenon V0 describes is real, large (~71-76%), and — unusually for this program —
**replicates cleanly across all three tested timeframes** with a clean, predeclared control ladder
that isolates the actual driver. The strict "inside bar" containment condition, however, does not add
discriminating power beyond generic compression — Control C (compression only, no containment) matches
or exceeds real inside bars on every timeframe, while an uncompressed real bar (Control B) performs no
better than a fully synthetic random range (Control D). **Compression relative to recent volatility,
not the inside-bar definition specifically, is the genuine driver.**

## V1 candidate proposed

**"Compressed-bar false-breakout fade"**: a bar whose range falls in the lowest tercile of
(range / ATR14-prior) — not requiring strict containment within the preceding bar — when broken out of
and failing to sustain, closes back through the opposite boundary at a rate significantly and robustly
above a random/synthetic baseline, replicated across M15, H1, and H4. This satisfies the governance
criteria for a V1 candidate:
- **Not explained by controls**: it beats the "ordinary mean reversion" baseline (Control D) decisively
  on all three timeframes (p=4.2e-30, 2.6e-11, 0.0053) — a real effect exists, distinct from generic
  mean reversion.
- **Replicates across the required timeframes**: yes, all three.
- **Not a post-hoc/optimized finding**: Control C was one of four controls predeclared before any
  result was inspected, per the CEO's explicit method requirement — this is a disclosed outcome of a
  predeclared falsification design, not a search for a favorable definition.

No further optimization, parameter search, or Validation-stage work is performed here — this is a
Discovery-stage V1 candidate only, per protocol.

## Answers to the 9 mandatory Discovery questions

1. **Does the edge exist at all (signal distinguishable from noise)?** Yes, for compression broadly —
   real, replicated, well above a random-matched baseline on all three timeframes. Not specifically for
   the strict "inside bar" containment condition, which adds no discriminating power beyond compression.
2. **Frequency?** 9,091 M15 events / 2,386 H1 / 683 H4 over ~2.85 years — inside bars are common
   (roughly 1 in a small number of bars, scaling with timeframe).
3/4. **Days it works/fails?** No day-of-week heterogeneity found on any timeframe.
5. **Sessions?** Significant on M15 only; does not replicate on H1 or H4 — not treated as robust.
6. **Volatility regimes?** Low volatility → higher fade rate, significant on M15, borderline on H1, not
   significant on H4 (smaller sample).
7. **Filters that improve it?** Not searched — the boundary/tercile constructions used were disclosed,
   predeclared control definitions, not a search for a favorable threshold.
8. **Conditions that invalidate it?** The specific "inside bar" (strict containment) framing is
   invalidated as the active mechanism — generic compression explains the effect at least as well.
   Direction (down-breakouts fade more) and mother-bar size (smaller → more fade) are real, replicated
   conditioning factors worth carrying into any future Validation-stage design.
9. **Out-of-sample?** Not tested via an explicit time-split in this pass; yearly stability is reported
   instead and shows no single-year concentration.

## Current status

**Discovery stage complete. V0 NOT SUPPORTED as an inside-bar-specific mechanism. V1 PROPOSED:
compression-driven false-breakout fade, replicated across M15/H1/H4.** This is a
**structural-behavior Discovery** result only (Protocol v2 §9's own labeling requirement) — no
scalping validation performed, no claim about tradability. No Validation-stage work has begun.

## Scope clarification (`EDGE_RESEARCH_PROTOCOL.md` §9)

This Discovery pass answers §§1-8 only. No Immediate Scalping Response (§9) check was performed —
per the CEO's explicit priority-shift instruction, §9 work is deferred project-wide, not attempted here.
