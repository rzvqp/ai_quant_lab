# E006 — Asia Range Expansion Failure

**Program**: 40-Edge Alpha Discovery Program (Flow A). **Protocol**: `EDGE_RESEARCH_PROTOCOL.md` §§1-8
only — §9 (Immediate Scalping Response / Protocol v2) explicitly NOT performed, per the CEO's own
priority-shift instruction. **Category**: Session Timing. **This file is the permanent, append-only
research log for this edge — nothing below is ever deleted or retroactively edited; refinements are
new, dated, appended versions.**

**Reordered ahead of E013/E016 per the CEO-approved priority audit (2026-07-21)** — selected via an
explicit, pre-committed scoring framework as the highest-priority Tier-1 edge (see
`NEXT_SESSION_FLOW_A.md` for the audit). Data loaded exclusively via the centralized `_common.load()`
loader (holdout-enforced, `EDGE_RESEARCH_PROTOCOL.md` §8); no direct CSV read anywhere in
`e006_asia_range_expansion.py`.

## V0 (frozen, verbatim from `EDGE_DISCOVERY_REGISTRY_v1.md`)

> Breakouts of the Asia session range fail more often under certain conditions than others.

Measured outcome (as registered): breakout failure rate (price returns inside the Asia range within a
defined window) vs. sustained-breakout rate. Observable variables listed in the registry: Asia range
width, breakout direction, day of week, volatility regime, which later session the breakout occurs in.

Note on V0's own wording: this is explicitly a **heterogeneity** claim ("fail more often under certain
conditions than **others**"), not a claim that breakouts mostly fail in absolute terms — so the primary
test throughout is whether failure rate varies significantly across the stated observables, not merely
whether the overall failure rate exceeds 50%.

## Discovery pass 1 (2026-07-21)

### Method (disclosed, exploratory — Discovery stage only, no tuning/optimization)

1. **Asia session range**: per UTC calendar date, the high/low spanned by all M15 bars tagged
   `session=='asia'` by `_common.load()` (hour < 8 UTC — the same session-tagging convention every
   other edge in this program uses, not redefined here). A date's range is only used if ≥87.5% of the
   session's expected bars are present (disclosed, not tuned — guards against a partial/gapped session
   producing a spuriously narrow or wide range).
2. **Breakout**: the FIRST bar after the Asia session ends that day whose CLOSE is beyond the Asia
   range. Only the first breakout per calendar day is used (avoids within-day pseudo-replication from
   repeated crossings — the same "first instance only" convention used elsewhere, e.g. E015's visit-1
   priority).
3. **Failure / sustained classification**: observed over a fixed, disclosed window — the remainder of
   the calendar day following the breakout (up to 16 hours). FAILURE = price's close crosses back onto
   the opposite side of the broken level at any point in that window. SUSTAINED = no such close occurs.
4. **Context features**: Asia range normalized by M15 ATR14 at the breakout bar, breakout direction, day
   of week, `_common.vol_regime()` tercile, breakout session (london/ny/late), year — exactly the
   registry's own listed observables.
5. **Structural control**: identical breakout/failure logic applied to a random, non-Asia 8-hour window
   per date (uniform random start hour, seed=42) instead of the real 00:00-07:59 window — tests whether
   any heterogeneity found is Asia-specific or a generic property of "any overnight/session-sized
   range," directly addressing the generic-mean-reversion confound already flagged in
   `NEXT_SESSION_FLOW_A.md` for E026/E032.
6. **Timeframes**: M15 (primary — finest granularity available; some session-boundary precision is
   lost without M1 data, per the roadmap's own disclosed caveat, but the core question is testable).
   H1 run as a secondary, coarser-resolution robustness check.
7. **Robustness**: Asia-boundary sensitivity (narrower 01:00-05:59 and wider 00:00-08:59 UTC
   variants), and yearly stability.

### Results — overall

| Timeframe | n events | Failure rate | Sustained rate | Median time-to-failure |
|---|---|---|---|---|
| M15 | 682 | 82.1% | 17.9% | 3 bars (45 min) |
| H1 | 651 | 63.4% | 36.6% | 2 bars (2h) |

Date range: 2022-12-16 to 2025-10-23 (pre-holdout-cutoff, `pre_holdout_2025-10-23T09-15-00Z_v1`).

### Results — context slices vs. overall baseline (M15; H1 consistent unless noted)

| Slice | Finding |
|---|---|
| Range width (tercile) | No significant heterogeneity (p=0.40, 0.21, 0.80) |
| Breakout direction (up/down) | No significant heterogeneity (p=0.63, 0.54) |
| Day of week | No significant heterogeneity (all p>0.19) |
| Volatility regime | Not significant on M15 (p≈0.12 both directions); **significant on H1** (low-vol→higher failure p=0.0055, high-vol→lower failure p=0.0008) — **does not replicate across timeframes**, not treated as robust |
| **Breakout session (london/ny/late)** | **Large, statistically significant on BOTH timeframes** — M15: london=87.4% (p=0.014), ny=63.3% (p=1.3e-6); H1: london=70.4% (p=0.017), ny=46.7% (p=7.0e-5). London-hour breakouts fail substantially more than NY-hour breakouts, robustly, in both timeframes. |

Breakout session is the one observable that shows real, replicated heterogeneity — directly matching
V0's own wording. Every other stated observable (range width, direction, day-of-week) showed no
significant heterogeneity; volatility regime showed heterogeneity on only one of two timeframes.

### Falsification attempt — is the session heterogeneity actually Asia-specific?

The raw "real Asia vs. random-window control" comparison initially looked like strong support for V0 as
an Asia-specific mechanism (M15: 82.1% vs. 70.4%, p=9.9e-6; H1: 63.4% vs. 51.5%, p=0.0002). **This does
not survive a same-session, composition-controlled comparison.** The random-window control's own
breakouts show the SAME session ordering (London > NY failure rate: M15 control 78.7% vs. 68.9%; H1
control 62.7% vs. 49.8%) — meaning most of the raw gap is explained by real Asia's sample being
compositionally weighted much more heavily toward London-session breakouts (79% of M15 events) than the
control's more evenly-distributed sample (37% London), not by anything specific to the Asia range
itself.

Same-session (composition-controlled) comparison, real Asia vs. random-window control:

| Session | M15 (real vs. control, p) | H1 (real vs. control, p) |
|---|---|---|
| London | 87.4% vs. 78.7%, **p=0.0105** | 70.4% vs. 62.7%, p=0.119 |
| NY | 63.3% vs. 68.9%, p=0.317 | 46.7% vs. 49.8%, p=0.603 |

Only ONE of four same-session tests reaches conventional significance (M15 London), and it does not
replicate at conventional significance on H1 (same direction, weaker). NY-session comparison is null on
both timeframes.

### Robustness

- **Asia-boundary sensitivity**: failure rate stays in a plausible range across three boundary
  definitions (M15: 78.9%-85.5%; H1: 58.7%-67.8%) — no wild swings from the exact hour cutoff chosen.
- **Yearly stability**: reasonably stable across 2023-2025 (M15: 76.5%-88.8%; H1: 62.4%-64.1%); 2022
  has only n=9 on M15 (data starts mid-December 2022) and is not weighted heavily.
- **Standard directional movement profile** (`_profile.py::movement_profile`, breakout direction as the
  predicted direction): continuation ≈ reversal ≈ 50/50 on both timeframes (M15: 49.4%/50.4%; H1:
  52.4%/47.6%) — no net directional continuation edge from the breakout itself, independent of the
  return-to-range question above.

## Headline result — V0 is NOT supported as an Asia-specific mechanism; the raw heterogeneity is real
## but is substantially a generic session-timing property

The heterogeneity V0 predicts ("fail more often under certain conditions than others") is genuinely
present and replicates across two independent timeframes — but it is driven almost entirely by WHICH
SESSION the breakout occurs in, and that session effect is present just as strongly in a structural
control with no connection to the Asia range at all. Once session composition is controlled for, only a
weak, inconsistently-replicated (significant on M15, not on H1) excess effect remains specific to the
real Asia range. This mirrors the pattern already seen in E010/E012/E017: a real surface-level pattern
exists, but the named mechanism does not survive a proper structural control.

**No V1 candidate is proposed.** The one candidate excess effect (Asia-then-London breakouts failing
somewhat more than a generic-window equivalent) reaches significance on only one of the two tested
timeframes — below this program's own established replication bar for a V1 candidate (cf. E015, where
the visit-1 pattern was strong and consistent on both M15 and H1 before being offered as V1).

## Answers to the 9 mandatory Discovery questions

1. **Does the edge exist at all (signal distinguishable from noise)?** A real, replicated signal
   exists for breakout-failure heterogeneity by session — but it is not Asia-specific; a structural
   control (random reference window) shows the same session ordering nearly as strongly.
2. **Frequency?** 682 Asia-range breakout events on M15 (~239/yr) and 651 on H1 (~236/yr) over
   ~2.85 years of clean data — effectively one event most trading days, since the detector takes the
   first breakout of the day only.
3/4. **Days it works/fails?** Day-of-week showed no significant heterogeneity in failure rate on
   either timeframe.
5. **Sessions?** Yes — the one robust finding. London-hour breakouts fail significantly more than
   NY-hour breakouts on both timeframes, but this effect is present almost as strongly in the
   structural control, so it is not attributable to the Asia range specifically.
6. **Volatility regimes?** Significant on H1 only (low vol → more failure, high vol → less failure);
   does not replicate on M15 — not treated as robust.
7. **Filters that improve it?** Not searched — searching for a filter/threshold that produces a
   favorable result would be exactly the "optimize until profitable" behavior the protocol forbids.
   The boundary-sensitivity sweep was run as a disclosed robustness check, not a search for a
   favorable value, and does not change the conclusion.
8. **Conditions that invalidate it?** The core "Asia range specifically" framing is invalidated by the
   structural control: the same session-dependent failure-rate pattern is present in a random
   reference window with no connection to the Asia session at all.
9. **Out-of-sample?** Not tested via an explicit time-split in this pass; yearly stability (2023-2025)
   is reported instead and shows no single-year concentration, consistent with several earlier edges.

## Current status

**Discovery stage complete. V0 NOT SUPPORTED as an Asia-specific mechanism. No V1 candidate offered.**
Structural pattern (session-dependent breakout-failure heterogeneity) is real and replicated but
attributed to generic session timing, not the Asia range. This is a **structural-behavior Discovery**
result only (per Protocol v2 §9's own labeling requirement) — no scalping validation performed, no
claim about tradability. E006 does not require revisiting unless new data (M1/M5) becomes available to
retest the same-session comparison with finer granularity.

## Scope clarification (`EDGE_RESEARCH_PROTOCOL.md` §9)

This Discovery pass answers §§1-8 only. No Immediate Scalping Response (§9) check was performed —
per the CEO's explicit priority-shift instruction, §9 work is deferred project-wide pending a future
decision, not attempted here.
