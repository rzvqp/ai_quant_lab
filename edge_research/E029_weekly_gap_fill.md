# E029 — Weekly Gap Fill

**Program**: 40-Edge Alpha Discovery Program (Flow A). **Protocol**: `EDGE_RESEARCH_PROTOCOL.md`.
**Category**: Mathematical. **Permanent, append-only research log.**

## ⚠ HOLDOUT BREACH — QUARANTINE NOTICE (added 2026-07-21, documentation-only incident record)

**Status: HOLDOUT-CONTAMINATED. CLEAN RERUN REQUIRED.** Full incident record:
`PROJECT_STATE_v2.md` §8.23.

The Discovery pass below accidentally loaded and analyzed data from the Research Lab's own terminal
holdout period (2025-10-23 09:15 UTC → 2026-07-13 06:00 UTC). The shared Flow A loader
(`edge_research/_common.py::load()`) applied no date cutoff at the time this pass ran; this edge's own
committed gap-event table (`e029_gap_events.csv`) has its last row dated **2026-07-12** (a Sunday
week-open gap), inside the holdout window, and it was counted in the 108 weekly gaps feeding the
overall fill-rate statistic below. **The old terminal holdout is CONSUMED / INVALIDATED** by this and
four other edges' own breach, project-wide (`PROJECT_STATE_v2.md` §8.23) — this is a process/governance
breach, not evidence that this edge's findings below are false.

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

> A price gap between Friday's close and Sunday/Monday's open tends to be filled within the following
> sessions.

Measured outcome (as registered): fill rate and time-to-fill distribution.

## Discovery pass 1 (2026-07-20)

**Data**: M15, 84,152 bars, 2022-12-16 → 2026-07-13 (~3.6 years — short of protocol §2's ~5-6yr
requirement; early Discovery pass only).

**Method** (full disclosure in `e029_weekly_gap_fill.py`):
- Week-boundary detection: any bar-to-bar gap in the M15 series exceeding 20 hours (normal spacing is
  15 minutes) is a week-open bar — 191 such boundaries found, 183 of them landing on a Sunday-labeled
  bar, consistent with the expected weekly market closure.
- **Data-quality finding, disclosed before any edge conclusion**: of those 191 boundaries, **83 (43%)
  have a gap of exactly $0.00–0.05** — i.e. the feed's Sunday-reopen "open" price is identical to
  Friday's last close to the cent. A real, continuously-quoted OTC/CFD instrument reopening after ~49
  hours essentially never reopens at the literal same tick; this is far more consistent with the data
  provider stamping the reopening bar's `open` with the prior close as a placeholder (no real quote yet)
  than with 43% of weeks genuinely having zero gap. **These 83 are excluded from the analysis below as
  non-events**, not counted as "instantly filled" gaps (counting them would have artificially inflated
  the fill rate). This is a new, disclosed data-quality caveat for this dataset, in the same spirit as
  `PROJECT_AUDIT.md`'s own D-series defect log for the Research Lab, though this document does not edit
  that log (Flow A keeps its own).
- Of the remaining **108 genuine gaps**: `filled` = the first bar (within a 5-trading-day/480-M15-bar
  horizon) whose [low,high] range reaches back to the pre-gap close. `time_to_fill` in hours.

**Headline result — a real, clean, monotonic pattern by gap size; present in this sample:**

| Slice | n | fill rate | median time-to-fill |
|---|---|---|---|
| **Overall** | 108 | **88.9%** | 1.0h |
| Gap down | 48 | 93.75% | 1.0h |
| Gap up | 60 | 85.0% | 1.0h |
| Small tercile | 36 | **100%** | 0h (same bar) |
| Medium tercile | 36 | 88.9% | 1.375h |
| **Large tercile** | 36 | **77.8%** | **11.0h** |

Fill rate falls and time-to-fill rises monotonically and substantially from the small to the large
gap-size tercile — the cleanest, most internally consistent pattern found across the edges studied in
this session so far. Down-gaps (against the sample's prevailing bull trend) fill somewhat more
reliably than up-gaps (with-trend) — directionally sensible (a trend-following market has less need to
revisit a gap that agrees with its own direction) but the two direction subsamples are small (n=48/60)
and this was not formally significance-tested in this pass. Week-of-month shows no material variation
(84.6%–100% across the month's five weeks; week 5's n=8 is too thin to weigh).

**Open interpretive caution (an active falsification concern, not resolved in this pass)**: an 88.9%
fill rate with a 1-hour median time-to-fill is also roughly what would be expected from ordinary
intraday chop revisiting a nearby prior level, independent of anything specific to *weekly* gaps — this
pass did **not** build a matched control (e.g., comparably-sized intraday price excursions on a normal
weekday, asking how often *those* levels get revisited within the same horizon) to check whether the
weekly-gap fill rate is actually elevated versus that baseline. Without that control, "gaps get filled"
cannot yet be distinguished from "prices in general get revisited most of the time at this ATR scale."
This is the single most important gap in this pass, flagged for the next revisit.

## Answers to the 9 mandatory Discovery questions

1. **Does the edge exist at all?** A clean rate/size/speed pattern exists in the raw data, but whether
   it is *specific to weekly gaps* (vs. generic level-revisitation) is unresolved (see caution above) —
   answer: **not enough evidence yet to distinguish from a generic base rate.**
2. **Frequency?** ~108 genuine weekly gaps over ~189 weeks in the sample (≈0.57/week — i.e., a genuine,
   non-artifact gap occurs roughly every other week; the rest show the near-zero data-quality pattern
   above).
3/4. **Days it works/fails?** Not day-of-week sliced beyond week-of-month (no material variation
   found across the month's weeks); a finer weekday-of-fill breakdown was not run in this pass.
5. **Sessions?** Not sliced in this pass (deferred — gap-size and direction were higher-priority first
   cuts given the small overall n=108).
6. **Volatility regimes?** Not sliced in this pass.
7. **Filters that improve it?** Not searched (protocol prohibition on optimizing at Discovery).
8. **Conditions that invalidate it?** Yes — large gaps fill markedly less reliably (77.8% vs 100% for
   small) and much more slowly (11h vs same-bar) — "tends to be filled" as stated in V0 is a much
   weaker claim for large gaps specifically.
9. **Out-of-sample?** Not tested via an explicit time-split in this pass; flagged as a gap to close,
   along with the matched-control question above, before any further stage.

## Current status

**Version: V0 (no refinement written yet — the gap-size-conditional pattern is a promising direction
for a V1 but is blocked on the matched-control question above before it can be responsibly framed).**
**Verdict: NONE ISSUED** — per protocol §2, below the ~5-6yr horizon; current data is ~3.6 years.
Remains in **Stage 2 — Discovery, first pass complete**.

**Next steps if revisited**: (a) build the matched intraday-revisitation control before drawing any
directional conclusion — this is the load-bearing open question for this edge, more so than for any
other edge studied this session; (b) slice by session and volatility regime; (c) formal out-of-time
split check; (d) Tier-0 history extension before any Frozen Candidate/Validation/Walk-Forward/Final
Verdict.

**Artifacts**: `e029_weekly_gap_fill.py`, `e029_weekly_gap_fill_results.json`, `e029_gap_events.csv`.
