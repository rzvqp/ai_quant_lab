# E027 — Midnight Open Anchor

**Program**: 40-Edge Alpha Discovery Program (Flow A). **Protocol**: `EDGE_RESEARCH_PROTOCOL.md` §§1-8
only — §9 (Immediate Scalping Response / Protocol v2) explicitly NOT performed, per the CEO's own
priority-shift instruction. **Category**: Mathematical (per `EDGE_DISCOVERY_REGISTRY_v1.md`).
**This file is the permanent, append-only
research log for this edge — nothing below is ever deleted or retroactively edited; refinements are
new, dated, appended versions.**

**Sixth edge run under the reordered Tier-1 sequence** (`NEXT_SESSION_FLOW_A.md`, 2026-07-21 priority
audit) — deliberately selected as a second, methodologically-continuous test of the "reference level
acts as a magnet" mechanism class E017 already tested (and refuted) for swing highs/lows, per the
priority audit's own reasoning. Only E027 authorized this session. Data loaded exclusively via
`_common.load()` (holdout-enforced); no direct CSV read anywhere in `e027_midnight_open_anchor.py`.

## V0 (frozen, verbatim from `EDGE_DISCOVERY_REGISTRY_v1.md`)

> The midnight (00:00) candle open acts as a reference/anchor level that price frequently revisits or
> reacts to during the following session.

Measured outcome (as registered): revisit rate and reaction magnitude relative to the midnight open
level. Observable variables: distance from midnight open, time-to-revisit, reaction magnitude, session.

## Definitions predeclared BEFORE any outcome was inspected

1. **Midnight open**: the `open` price of the first bar of each UTC calendar day — exact, unambiguous.
2. **Departure**: the first subsequent bar that day whose |close − midnight_open| ≥ 0.25×ATR14
   (disclosed, not tuned). Its own ATR-normalized distance is recorded.
3. **Revisit**: from the departure bar onward, does any later bar's range touch back to midnight_open
   within the remainder of that day? Reach rate + time-to-revisit recorded.
4. **Reaction magnitude**: `_profile.movement_profile()` at the revisit bar, direction = away from
   midnight_open in the original departure direction.
5. **Session**: the departure bar's own session tag.
6. **No-departure exclusion**: days where price never departs 0.25×ATR are excluded.

## Control — reused directly from E017 (not reinvented)

**Random-matched-distance**: for a random point in time (seed=42), sample a real observed departure
distance (and direction) from the actual midnight-open population, construct a synthetic target at
that distance, and run the identical revisit-detection logic — the exact same construction as
`e017_equal_highs_lows.py::random_matched_control()`, reused for direct comparability rather than a
new, independently-designed control that could differ for incidental reasons.

Timeframes: M15, H1, H4 — all three registered for E027, all present in the clean dataset.

## Results — primary vs. control

| Timeframe | n events | Real reach rate | Control reach rate | p (real vs. control) |
|---|---|---|---|---|
| M15 | 886 | 82.2% | 86.1% | **0.027** |
| H1 | 725 | 75.4% | 91.9% | **5.3e-17** |
| H4 | 715 | 53.1% | 90.8% | **4.5e-56** |

**The random-matched-distance control reaches its synthetic target MORE reliably than price reaches
the real midnight-open level, on all three timeframes, all statistically significant — the same
"opposite of a magnet" signature E017 found for swing highs/lows.** This is not merely a second null;
it is a second instance of the SAME qualitative refutation pattern, strengthening the growing
program-wide finding that structural reference levels do not act as magnets on this instrument at this
data resolution — if anything the reverse holds.

## Context slices

- **Distance tercile**: a strong, monotonic, highly significant pattern on all three timeframes — the
  closer the departure stayed to midnight_open, the more likely a revisit (M15: low-tercile 89.8% →
  high-tercile 67.8%, both p<0.003; H1: 84.3%→64.9%, p<0.006; H4: 75.2%→30.3%, p<1e-8). This is
  expected, mechanical behavior (a nearer target is easier to reach for any reason) present in both the
  real and control populations by construction, not evidence of a magnet-specific effect on its own —
  the load-bearing comparison remains the real-vs-control gap above.
- **Session**: population sizes are heavily skewed toward the 'asia' session (departures shortly after
  midnight UTC naturally fall in the 0-8 UTC asia window on M15/H1), leaving london/ny/late slices too
  thin to interpret reliably (n=0-4 on M15/H1 for london/ny/late). The one exception, M15's 'late'
  slice (n=151, 35.8% reach rate, p=6.6e-34), is **not treated as a genuine session effect** — it most
  likely reflects that departures occurring very late in the day mechanically have less remaining time
  before the day-bounded horizon ends, not a distinct behavioral regime. Disclosed as a limitation of
  the day-scoped horizon, not investigated further in this pass.
- **Volatility regime**: significant on M15 (all p<0.01) but not on H1 (all p>0.36) or H4 (all p>0.07)
   — not treated as robust given the lack of cross-timeframe replication.

## Headline result — V0 NOT SUPPORTED, generalizing E017's own refutation to a second level-type

The midnight-open level does not act as a magnet — it is reached significantly LESS reliably than a
synthetic random-matched-distance reference, on all three tested timeframes. This directly parallels
and reinforces E017's own finding for swing highs/lows, now shown for a structurally distinct,
time-anchored (not price-structure-anchored) level. **No V1 candidate is proposed**, consistent with
E017's own precedent for this mechanism class.

**Note for future cross-edge synthesis** (not acted on here, per standing governance — new cross-edge
candidates require separate CEO authorization, per the CEC-001 precedent): E017 and E027 now
independently agree that reference levels of two structurally different kinds (price-structure swing
points, and a time-anchored daily open) both show the SAME "random beats real" refutation signature.
This may be worth a future, separately-authorized cross-edge synthesis in the same spirit as CEC-001,
but is disclosed here only as an observation, not pursued.

## Answers to the 9 mandatory Discovery questions

1. **Does the edge exist at all (signal distinguishable from noise)?** No — real reach rate is
   significantly LOWER than a synthetic random baseline, the opposite of what V0 predicts, on all
   three timeframes.
2. **Frequency?** 886 events (M15) / 725 (H1) / 715 (H4) over ~2.85 years (~1/trading day, as expected).
3/4. **Days it works/fails?** Not sliced by day-of-week in this pass (session and distance were
   prioritized as the registry's own stated observables, and the primary result is already a clean,
   directionally opposite finding).
5. **Sessions?** Population too thin outside 'asia' to interpret reliably; the one apparent late-session
   effect is attributed to the day-bounded horizon, not a genuine session effect.
6. **Volatility regimes?** Significant on M15 only; does not replicate on H1/H4 — not treated as robust.
7. **Filters that improve it?** Not searched — would be exactly the "optimize until profitable"
   behavior the protocol forbids, and there is no positive base result to refine.
8. **Conditions that invalidate it?** The core "magnet" claim is invalidated broadly and in the
   specific direction opposite to V0 — real levels underperform a synthetic baseline, not just fail to
   beat it.
9. **Out-of-sample?** Not tested via an explicit time-split; yearly stability is recorded in
   `e027_midnight_open_anchor_results.json` instead, consistent with earlier edges.

## Current status

**Discovery stage complete. V0 NOT SUPPORTED. No V1 proposed.** This is a **structural-behavior
Discovery** result only (Protocol v2 §9's own labeling requirement) — no scalping validation
performed, no claim about tradability.

## Scope clarification (`EDGE_RESEARCH_PROTOCOL.md` §9)

This Discovery pass answers §§1-8 only. No Immediate Scalping Response (§9) check was performed —
per the CEO's explicit priority-shift instruction, §9 work is deferred project-wide, not attempted here.
