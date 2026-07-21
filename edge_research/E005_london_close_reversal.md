# E005 — London Close Reversal

**Program**: 40-Edge Alpha Discovery Program (Flow A). **Protocol**: `EDGE_RESEARCH_PROTOCOL.md` §§1-8
only — §9 (Immediate Scalping Response / Protocol v2) explicitly NOT performed, per the CEO's own
priority-shift instruction. **Category**: Session Timing. **This file is the permanent, append-only
research log for this edge — nothing below is ever deleted or retroactively edited; refinements are
new, dated, appended versions.**

**Fifth edge run under the reordered Tier-1 sequence** (`NEXT_SESSION_FLOW_A.md`, 2026-07-21 priority
audit). Only E005 authorized this session. Data loaded exclusively via `_common.load()`
(holdout-enforced); no direct CSV read anywhere in `e005_london_close_reversal.py`.

## V0 (frozen, verbatim from `EDGE_DISCOVERY_REGISTRY_v1.md`)

> The London session close produces recurring reversals.

Measured outcome (as registered): reversal rate and magnitude in a fixed post-London-close window.
Observable variables: pre-close trend direction/strength, day of week, size of the reversal, duration
until reversal exhausts.

## Definitions predeclared BEFORE any outcome was inspected

1. **London close boundary**: 13:00 UTC — `_common.load()`'s own session tag transition point
   (london→ny), reused exactly, not redefined.
2. **Pre-close window**: UTC hour [11, 13) — last 2 hours of London.
3. **Post-close window**: UTC hour [13, 15) — first 2 hours of NY. Fixed, symmetric, disclosed.
4. **Pre-close trend direction/strength**: sign and ATR-normalized magnitude of the pre-close window's
   own net move.
5. **Reversal**: the post-close window's net move opposes the pre-close window's direction. Rate =
   fraction of days where this holds; magnitude = ATR-normalized post-close net move, recorded for
   reversal days.
6. **Duration until reversal exhausts**: `_profile.movement_profile()`'s own adverse-time-to-hit at the
   1.0×ATR threshold, called at the close-boundary bar with `direction = -pre_close_direction`.
7. **Window completeness**: ≥75% of expected bars required in each 2-hour window.

## Controls

- **Control A — generic session boundary**: the identical logic applied to the Asia→London boundary
  (08:00 UTC) and the NY→late boundary (21:00 UTC) — tests whether any reversal tendency is
  London-close-specific or a generic "any session transition" property.
- **Control B — random-matched baseline**: a random UTC hour (seed=42, excluding the three real
  boundary hours) as a synthetic "boundary," same window construction.

**Data note discovered during this pass**: `OANDA_XAUUSD_M15` has a real, substantial daily bar-count
drop at UTC hour 21 (896 bars vs. ~2,900+ at every other hour) — a genuine daily rollover/maintenance
gap in the feed, not a bug. This made the NY→late (21:00) control boundary untestable (0 qualifying
events after the completeness filter) and is disclosed as a data limitation rather than worked around.

Timeframes: M15 (primary), H1 (secondary) — both registered for E005; M1/M5 unavailable in this
project's data.

## Results — primary

| Timeframe | n events | Reversal rate | Reversal magnitude (mean/median, ATR) | Duration to exhaust (median, bars) |
|---|---|---|---|---|
| M15 | 730 | 52.1% | 2.76 / 1.85 | 1.0 |
| H1 | 720 | 52.1% | 1.39 / 1.00 | 0.0 |

The reversal rate sits at essentially a coin flip on both timeframes. Reversals that do occur have a
real, non-trivial size (median ≥1×ATR) and resolve quickly (median 0-1 bars) — but this describes the
subset that already reversed, not evidence that reversal is more likely than chance in the first place.

## Results — controls

| Comparison | M15 rate | M15 p vs. London close | H1 rate | H1 p vs. London close |
|---|---|---|---|---|
| Control A: Asia→London (08:00) | 48.3% | 0.166 | 48.3% | 0.171 |
| Control A: NY→late (21:00) | untestable (daily data gap, see above) | — | untestable | — |
| Control B: random hour (02:00 UTC) | 49.9% | 0.432 | 49.6% | 0.370 |

London close's ~52% rate is not significantly different from the Asia→London boundary or from a
random reference hour, on either timeframe. Every tested boundary — real or synthetic — sits in the
same 48-52% chance band.

## Context slices

No significant heterogeneity found on either timeframe for day of week (all p>0.27), volatility
regime (all p>0.72), or pre-close trend strength tercile (all p>0.44).

## Headline result — V0 NOT SUPPORTED

London close shows no elevated reversal tendency compared to another real session boundary or a
random reference hour, on either tested timeframe, and no heterogeneity was found across any examined
context variable. This is a clean null, similar in character to E011's. **No V1 candidate is
proposed** — there is no residual effect anywhere in this analysis to build one from.

## Answers to the 9 mandatory Discovery questions

1. **Does the edge exist at all (signal distinguishable from noise)?** No — reversal rate is
   statistically indistinguishable from a random reference hour and from another real session
   boundary, on both timeframes.
2. **Frequency?** 730 events (M15) / 720 (H1) over ~2.85 years (~1/trading day, as expected).
3/4. **Days it works/fails?** No day-of-week heterogeneity found on either timeframe.
5. **Sessions?** The core question here IS the session-boundary comparison — London close performs no
   differently than the Asia→London boundary or a random hour.
6. **Volatility regimes?** No tercile shows a meaningfully elevated reversal rate.
7. **Filters that improve it?** Not searched — would be exactly the "optimize until profitable"
   behavior the protocol forbids, and there is no positive base result to refine.
8. **Conditions that invalidate it?** The core mechanism (a distinctly reversal-prone London close) is
   invalidated broadly — it performs identically to controls with no special claim to London-specific
   behavior.
9. **Out-of-sample?** Not tested via an explicit time-split in this pass; yearly stability is recorded
   in `e005_london_close_reversal_results.json` instead, consistent with earlier edges.

## Current status

**Discovery stage complete. V0 NOT SUPPORTED. No V1 proposed.** This is a **structural-behavior
Discovery** result only (Protocol v2 §9's own labeling requirement) — no scalping validation
performed, no claim about tradability.

## Scope clarification (`EDGE_RESEARCH_PROTOCOL.md` §9)

This Discovery pass answers §§1-8 only. No Immediate Scalping Response (§9) check was performed —
per the CEO's explicit priority-shift instruction, §9 work is deferred project-wide, not attempted here.
