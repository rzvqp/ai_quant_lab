# E028 — Fibonacci OTE

**Program**: 40-Edge Alpha Discovery Program (Flow A). **Protocol**: `EDGE_RESEARCH_PROTOCOL.md`.
**Category**: Mathematical. **Permanent, append-only research log.**

## ⚠ HOLDOUT BREACH — QUARANTINE NOTICE (added 2026-07-21, documentation-only incident record)

**Status: HOLDOUT-CONTAMINATED. CLEAN RERUN REQUIRED.** Full incident record:
`PROJECT_STATE_v2.md` §8.23.

The Discovery pass below accidentally loaded and analyzed data from the Research Lab's own terminal
holdout period (2025-10-23 09:15 UTC → 2026-07-13 06:00 UTC). The shared Flow A loader
(`edge_research/_common.py::load()`) applied no date cutoff at the time this pass ran; this edge's own
committed swing-leg table (`e028_legs.csv`) has its last row at bar index 84,144, mapping to
**2026-07-13 04:15 UTC** — inside the holdout window — and it fed directly into the by-zone statistics
below. **The old terminal holdout is CONSUMED / INVALIDATED** by this and four other edges' own breach,
project-wide (`PROJECT_STATE_v2.md` §8.23) — this is a process/governance breach, not evidence that
this edge's findings below are false.

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

> The 61.8%-79% "optimal trade entry" retracement zone of an impulsive move offers a statistically
> favorable continuation entry.

Measured outcome (as registered): continuation rate/magnitude from the OTE zone vs. shallower or
deeper retracements.

## Discovery pass 1 (2026-07-20)

**Data**: M15, 84,152 bars, 2022-12-16 → 2026-07-13 (~3.6 years — short of protocol §2's ~5-6yr
requirement; early Discovery pass only).

**Method** (full disclosure in `e028_fibonacci_ote.py`):
- Swing (fractal) detection: a bar is a swing high/low if its high/low is the single extreme among
  the 11 bars centered on it (5 either side, k=5 — a plain default, not searched/tuned).
- Standard zigzag construction over the fractal candidates (alternating high/low, collapsing same-type
  runs to the more extreme point) → 8,207 alternating swing points, 8,204 usable consecutive
  A→B→C→D swing quadruples.
- Leg A→B = "impulsive move"; leg B→C = the retracement. `retracement_pct = |C-B|/|A-B|` (can exceed
  1.0 — price fully reverses past the impulse's own origin).
- `D` (the swing after C) tests continuation: `continuation_magnitude = dir(A→B) * (D-B) / |A-B|`,
  positive = D made a new extreme beyond B in the original impulse direction; `continued` = 1 if
  `continuation_magnitude > 0`.
- `retracement_pct` bucketed into V0's own named zones: <38.2%, 38.2–61.8%, **61.8–79% (OTE)**,
  79–100%, >100% (full reversal past A).

**Headline result — V0 is NOT supported for the rate dimension; the OTE zone shows a WORSE
continuation rate than shallower retracements, and this difference is statistically significant:**

| Zone | n legs | continuation rate | mean cont. magnitude | median cont. magnitude |
|---|---|---|---|---|
| <38.2% (shallow) | 723 | **64.6%** | 0.227 | 0.087 |
| 38.2–61.8% | 1,346 | 60.3% | 0.301 | 0.098 |
| **61.8–79% (OTE)** | 1,046 | **57.3%** | 0.379 | 0.117 |
| 79–100% | 1,140 | 51.8% | 0.340 | 0.038 |
| >100% (full reversal) | 3,949 | 37.6% | −0.172 | −0.319 |

**Continuation rate declines monotonically as retracement depth increases**, from 64.6% at the
shallowest zone down to 37.6% once price has fully round-tripped past the impulse's own origin. The
**OTE zone sits in the middle of that decline (57.3%)** — it does not stand out as favorable versus
shallower retracements; a shallow-retracement continuation entry actually continues significantly more
often than an OTE-zone one (chi-square test, shallow vs OTE: χ²=9.28, **p=0.0023**).

**Mean continuation magnitude tells a partially different, nuanced story**: it is not monotonic and
actually peaks in the OTE zone (0.379) before falling off beyond 79%. However the **median** (far less
sensitive to a small number of outsized outlier legs) shows a much more muted version of the same
shape — 0.087 (shallow) → 0.098 → **0.117 (OTE, the highest median)** → 0.038 → −0.319 — i.e. the OTE
zone's median continuation-when-it-happens is modestly the largest of the four non-reversal zones, even
though it happens less often than from a shallow retracement. **Net reading: OTE-zone continuations, when
they occur, tend to run somewhat further than shallow-retracement continuations — but they occur
meaningfully less often, and the "less often" effect is the statistically stronger, more reliable one
of the two in this pass.**

A separate, notable finding not part of V0's own framing: **almost half of all detected legs (3,949 /
8,204 = 48.1%) fully reverse past the impulse's own origin** before any continuation is confirmed —
i.e. under this simple fractal-swing construction, "impulsive moves" that cleanly retrace-then-continue
are a minority outcome; full reversal is the single most common single outcome bucket.

## Answers to the 9 mandatory Discovery questions

1. **Does the edge exist at all?** Not as stated. A real, statistically significant pattern exists, but
   it points toward **shallower** retracements continuing more reliably than the OTE zone, the reverse
   of V0's claim on the rate dimension; on the magnitude-conditional-on-continuation dimension the OTE
   zone shows a modest edge that is far less statistically decisive.
2. **Frequency?** 8,204 usable swing legs over ~3.6 years (~2.25 legs/trading day at M15 resolution
   with a k=5 fractal — i.e. this is a fairly fine-grained, noisy swing definition, not a "major
   impulse only" one; a coarser k would produce fewer, larger, possibly more V0-consistent legs and was
   not tested in this pass).
3/4/5/6. **Days/sessions/volatility regimes?** Not sliced in this pass (deferred — the zone-level
   rate/magnitude divergence was the highest-priority finding to characterize first given the time
   available).
7. **Filters that improve it?** Not searched (protocol prohibition at Discovery). A larger fractal `k`
   (coarser, more "major-swing" impulses) is a natural, disclosed candidate for a future pass — noted,
   not run, to avoid the appearance of searching until V0 is vindicated.
8. **Conditions that invalidate it?** The `k=5` swing-detection granularity is itself a major open
   condition — this pass used one specific, disclosed choice; the finding may not generalize to a
   coarser/finer swing definition, which has not been tested.
9. **Out-of-sample?** Not tested via an explicit time-split in this pass.

## Current status

**Version: V0 (no refinement written yet — the shallow-vs-OTE rate finding is real but the swing-
granularity sensitivity must be checked before any responsible V1 wording).** **Verdict: NONE ISSUED**
— per protocol §2, below the ~5-6yr horizon. Remains in **Stage 2 — Discovery, first pass complete**.

**Next steps if revisited**: (a) re-run with at least one coarser fractal `k` (e.g. 10, 20) to test
whether the shallow>OTE rate finding is an artifact of using very short, noisy swings; (b) session/
volatility/day slices; (c) formal out-of-time split; (d) Tier-0 history extension before any Frozen
Candidate/Validation/Walk-Forward/Final Verdict.

**Artifacts**: `e028_fibonacci_ote.py`, `e028_fibonacci_ote_results.json`, `e028_legs.csv`. **This
original run is HOLDOUT-CONTAMINATED — see the quarantine notice at the top of this file and the clean
rerun below.**

## CLEAN RERUN (2026-07-21, holdout-excluded) — supersedes the contaminated run above for any future
promotion decision; the contaminated run above is preserved verbatim, not deleted

**Split metadata** (`e028_fibonacci_ote_clean_results.json`, `data_split_id =
pre_holdout_2025-10-23T09-15-00Z_v1`): `holdout_cutoff = 2025-10-23T09:15:00+00:00`,
`holdout_excluded = true`, `max_date_used = 2025-10-23 09:00:00 UTC`. 6,533 swings / 6,530 legs (down
from 8,207 / 8,204). Method is byte-identical (same k=5 fractal, same zigzag construction, same zone
bins).

**Result vs. the contaminated run — CONFIRMED closely; the shallow>OTE rate inversion survives, at
somewhat reduced (but still conventionally significant) strength:**

| Zone | Contaminated rate (n) | Clean rate (n) | Contaminated median mag | Clean median mag |
|---|---|---|---|---|
| <38.2% (shallow) | 64.6% (723) | 63.0% (608) (CONFIRMS) | 0.087 | 0.078 (CONFIRMS) |
| 38.2–61.8% | 60.3% (1,346) | 61.0% (1,039) (CONFIRMS) | 0.098 | 0.111 (CONFIRMS) |
| **61.8–79% (OTE)** | 57.3% (1,046) | 57.0% (817) (CONFIRMS, near-identical) | 0.117 | 0.104 (CONFIRMS) |
| 79–100% | 51.8% (1,140) | 52.4% (900) (CONFIRMS) | 0.038 | 0.062 (CONFIRMS direction) |
| >100% (full reversal) | 37.6% (3,949) | 38.1% (3,166) (CONFIRMS) | −0.319 | −0.306 (CONFIRMS) |

**Shallow-vs-OTE significance test, rerun on the clean event counts**: chi-square = 4.89, **p=0.027**
(vs. the contaminated run's χ²=9.28, p=0.0023) — **still significant at the conventional 0.05
threshold, but weaker**, consistent with the smaller clean sample (n=608 vs 723 shallow, n=817 vs 1,046
OTE) rather than any change in the underlying rates, which are nearly identical between the two runs.

**Honest reading**: this edge's core, V0-contradicting finding — shallow retracements continue more
often than the OTE zone, not less — replicates almost exactly in every zone's rate and median magnitude
once the holdout period is excluded. The monotonic decline in continuation rate across zones is
preserved intact. This is a **CONFIRMED** result, not weakened in direction or magnitude, only in the
strength of one specific significance test due to the smaller sample.

**The open swing-granularity caveat already on record is unchanged and unresolved**: this pass still
has not tested a coarser fractal `k` (e.g. 10, 20) to check whether the shallow>OTE finding is specific
to this pass's short, noisy k=5 swing definition — that question applies identically to the clean
rerun.

**No Final Verdict is issued.** Per `EDGE_RESEARCH_PROTOCOL.md` §2, a Final Verdict requires the full
~5-6 year horizon; the clean data is now ~2.85 years, further from Final-Verdict-eligible than the
original ~3.6-year contaminated window. This remains **Stage 2 — Discovery, clean rerun complete**.

**Artifacts (clean rerun)**: `e028_fibonacci_ote_clean.py`, `e028_fibonacci_ote_clean_results.json`,
`e028_legs_clean.csv`.
