# E026 — ADR Exhaustion

**Program**: 40-Edge Alpha Discovery Program (Flow A). **Protocol**: `EDGE_RESEARCH_PROTOCOL.md`.
**Category**: Mathematical. **Permanent, append-only research log.**

## ⚠ HOLDOUT BREACH — QUARANTINE NOTICE (added 2026-07-21, documentation-only incident record)

**Status: HOLDOUT-CONTAMINATED. CLEAN RERUN REQUIRED.** Full incident record:
`PROJECT_STATE_v2.md` §8.23.

The Discovery pass below accidentally loaded and analyzed data from the Research Lab's own terminal
holdout period (2025-10-23 09:15 UTC → 2026-07-13 06:00 UTC). The shared Flow A loader
(`edge_research/_common.py::load()`) applied no date cutoff at the time this pass ran; this edge's own
committed event tables (`e026_events_up.csv`, `e026_events_down.csv`) contain rows dated
**2026-07-08 and 2026-07-09**, both well inside the holdout window, and both fed directly into the
by-threshold statistics below. **The old terminal holdout is CONSUMED / INVALIDATED** by this and four
other edges' own breach, project-wide (`PROJECT_STATE_v2.md` §8.23) — this is a process/governance
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

> Once price has moved a large fraction of its Average Daily Range, further continuation in the same
> direction becomes statistically less likely for the remainder of the session.

Measured outcome (as registered): continuation-rate change conditioned on % of ADR already used.

## Discovery pass 1 (2026-07-20)

**Data**: D1 (for ADR14) + M15 (for intraday path), 1,111 calendar days, 2022-12-16 → 2026-07-13
(~3.6 years — short of the protocol's §2 ~5-6yr requirement; early Discovery pass only).

**Method** (full disclosure in `e026_adr_exhaustion.py`):
- `ADR14` = rolling 14-day mean of D1 (high−low), **shifted 1 day** so a given day's budget uses only
  the trailing 14 already-closed days (lookahead-safe).
- Per day, per direction (up/down): `consumed = (running extreme − day open) / ADR14`, tracked bar by
  bar through the day (UTC calendar day).
- For each of 6 thresholds (0.3, 0.5, 0.7, 0.9, 1.1, 1.3 × ADR), the FIRST bar in the day crossing that
  threshold is one event (one per day per threshold per direction — avoids massive within-day
  autocorrelation from testing every bar).
- At that event, `continuation = max(0, day's eventual further extreme beyond this point) / ADR14` —
  strictly ≥0, "how much more room the day's range used, in the same direction, after this point."
  V0 predicts this should fall as the crossed threshold rises.

**Headline result — real, but direction-asymmetric: present and significant for UP moves, absent for
DOWN moves.**

| Direction | n events | continuation mean, th=0.3 → th=1.1 | Spearman r (threshold vs continuation) | low(≤0.5) vs high(≥1.1) Mann-Whitney p |
|---|---|---|---|---|
| **Up** | 1,182 | 0.357 → 0.324 → 0.302 → 0.260 → **0.247** (monotonic decline) | **r=−0.137, p=2.4e-6** | **p=0.00021** (low mean 0.344 > high mean 0.258) |
| **Down** | 1,057 | 0.362 → 0.338 → 0.319 → 0.349 → 0.354 (non-monotonic, ticks back up) | r=−0.058, p=0.059 (n.s.) | p=0.79 (n.s.; low mean 0.353 ≈ high mean 0.396) |

Continuation-*rate* (fraction of events where the day pushed at least a further +0.1×ADR) tells the
same story: **up** falls cleanly 0.746 → 0.683 → 0.665 → 0.607 → 0.552 as the threshold rises from 0.3
to 1.1; **down** is non-monotonic (0.706 → 0.662 → 0.583 → 0.635 → 0.569 → **0.750** at the most extreme
threshold, 1.3×ADR) — extreme downside ADR consumption in this sample is associated with, if anything,
*more* not less further continuation.

**Caveat found while investigating the "up" effect further (an active falsification attempt, not
accepted at face value)**: splitting the up-direction events by session shows the pooled effect is not
uniform — Spearman r is only individually significant in the **Asia session** (r=−0.100, n=391,
p=0.049); London (r=+0.099, n=248, p=0.12, wrong sign), NY (r=−0.012, n=478, p=0.79, ~zero), and "late"
(n=65, ~zero) show no reliable within-session effect. This raises a real possibility that part of the
pooled significance is a **confound between session-of-day and which threshold gets crossed first**
(e.g. Asia-session moves that reach high thresholds early may systematically differ from NY-session
moves reaching the same threshold later in the day) rather than a pure ADR-consumption mechanism. This
is recorded as an open falsification concern, not resolved in this pass.

Day-of-week (up direction): continuation mean is fairly flat across Mon/Tue/Wed/Thu (0.29–0.37, n=279–
300 each); Sunday's 30 events (thin, likely session-open artifacts at the week's very first bars) show
a much lower 0.097 — too small an n to draw a conclusion, flagged as a thin-data exception, not a
finding.

## Answers to the 9 mandatory Discovery questions

1. **Does the edge exist at all?** Direction-dependent. **Yes, for upside ADR consumption** (monotonic
   decline in continuation as threshold rises, p=2.4e-6 on the Spearman correlation, p=0.00021 on the
   low-vs-high split). **No, for downside ADR consumption** (no monotonic pattern, p=0.06–0.79
   depending on the test).
2. **Frequency?** ~1.06 up-threshold-crossing-events/day and ~0.95 down-threshold-crossing-events/day
   pooled across all 6 thresholds (i.e., most days cross at least the 0.3× threshold in both
   directions; only a minority reach 1.1–1.3×).
3/4. **Days it works / fails (for the up-direction effect)?** No clear day-of-week dependency found in
   the days with adequate sample size (Mon–Thu); Sunday's small subsample is inconclusive, not a
   negative finding.
5. **Sessions?** The up-direction effect is only individually significant in the **Asia session**;
   London and NY show no reliable within-session relationship — see the confound caveat above. This is
   the single most important open question for any future revisit of this edge.
6. **Volatility regimes?** Not yet sliced in this pass (deferred — the session-confound finding took
   priority as the more load-bearing falsification check for this pass).
7. **Filters that improve it?** Not searched (would risk exactly the "optimize until profitable"
   behavior the protocol forbids at Discovery).
8. **Conditions that invalidate it?** Yes — direction matters a great deal: the hypothesis, as
   registered, does not distinguish up vs down, but the data does. The down-direction data does not
   support V0 at all in this sample.
9. **Out-of-sample?** Not tested via an explicit time-split in this pass (unlike E025); flagged as a
   gap to close before this edge is revisited, in addition to the session-confound question.

## Current status

**Version: V0 → informal V1 candidate framing recorded below (not frozen; Stage 3 not entered).**
**Verdict: NONE ISSUED** — per protocol §2, no Final Verdict may be issued below the ~5-6yr horizon;
current data is ~3.6 years. Remains in **Stage 2 — Discovery, first pass complete**.

**V1 candidate framing (tentative, unfrozen)**: "ADR exhaustion (declining continuation likelihood as
% of ADR consumed rises) is present for **upside** moves in XAUUSD but not demonstrated for downside
moves in this sample — and the upside effect itself may be partly session-composition-driven rather
than a pure consumption effect; this must be disentangled before any Frozen Candidate is written."

**Next steps if revisited**: (a) resolve the session/threshold confound directly (e.g. condition on
session at a FIXED threshold rather than pooling across sessions); (b) run the volatility-regime slice
not completed in this pass; (c) add an explicit out-of-time split check (as done for E025); (d) acquire
the Tier-0 history extension before any Frozen Candidate/Validation/Walk-Forward/Final Verdict.

**Artifacts**: `e026_adr_exhaustion.py`, `e026_adr_exhaustion_results.json`, `e026_events_up.csv`,
`e026_events_down.csv`. **This original run is HOLDOUT-CONTAMINATED — see the quarantine notice at the
top of this file and the clean rerun below.**

## CLEAN RERUN (2026-07-21, holdout-excluded) — supersedes the contaminated run above for any future
promotion decision; the contaminated run above is preserved verbatim, not deleted

**Split metadata** (`e026_adr_exhaustion_clean_results.json`, `data_split_id =
pre_holdout_2025-10-23T09-15-00Z_v1`): D1 and M15 both loaded with `holdout_cutoff =
2025-10-23T09:15:00+00:00`, `holdout_excluded = true`; M15 `max_date_used = 2025-10-23 09:00:00 UTC`,
887 calendar days (down from 1,111). Method is byte-identical to the contaminated run (same THRESH
list, same event/continuation construction — `e026_adr_exhaustion_clean.py` differs only in how D1/M15
are loaded).

**Result vs. the contaminated run — CONFIRMED, and if anything strengthened, for the upside effect;
the downside null and the session-confound caveat both replicate essentially unchanged:**

| Metric | Contaminated (original) | Clean (holdout-excluded) |
|---|---|---|
| Up: low(≤0.5) vs high(≥1.1) continuation | 0.344 vs 0.258, **p=0.00021** | 0.348 vs 0.181, **p=9.2e-7** (CONFIRMS, stronger) |
| Up: Spearman r (threshold vs continuation) | r=−0.137, **p=2.4e-6** | r=−0.171, **p=8.4e-8** (CONFIRMS, stronger) |
| Up: continuation rate, th 0.3→1.1 | 0.746→0.683→0.665→0.607→0.552 | 0.736→0.706→0.673→0.613→0.517 (CONFIRMS, same monotonic shape) |
| Down: low vs high | 0.353 vs 0.396, p=0.79 (n.s.) | 0.333 vs 0.376, p=0.79 (n.s.) (CONFIRMS the null, essentially identical) |
| Down: Spearman r | r=−0.058, p=0.059 (n.s.) | r=−0.069, **p=0.047** (borderline flips to nominally significant, but still far weaker than the up-direction effect and non-monotonic at the threshold level — see the th=1.3 bucket below) |
| Down: th=1.3 (most extreme) continuation rate | 0.750 (highest of any bucket — "more continuation, not less") | 0.789 (n=19, thin — same anomalous "more not less" pattern replicates) |

**Session-confound caveat re-checked and CONFIRMED to persist**: re-running the up-direction,
per-session Spearman check on the clean event set gives Asia r=−0.190 (n=296, **p=0.0010**), London
r=+0.125 (n=219, p=0.066, still wrong sign), NY r=−0.068 (n=409, p=0.171, still ~zero), late (n=50,
p=0.83). This is the same pattern as the contaminated run (Asia was the only session individually
significant there too) — **the open question of whether the pooled up-direction effect is partly a
session-composition confound is NEITHER resolved NOR weakened by holdout removal; it stands exactly as
before** and remains the single most important open item for any future revisit.

**Honest reading**: this edge's finding is robust — the upside ADR-exhaustion effect is not an artifact
of the holdout-period data; if anything it is slightly stronger in the clean sample. The downside null
and the Asia-session-only significance pattern both replicate essentially unchanged.

**No Final Verdict is issued.** Per `EDGE_RESEARCH_PROTOCOL.md` §2, a Final Verdict requires the full
~5-6 year horizon; the clean data is now ~2.85 years (887 days), further from Final-Verdict-eligible
than the original ~3.6-year contaminated window. This remains **Stage 2 — Discovery, clean rerun
complete**.

**V1 candidate framing is unchanged by this clean rerun** (see the pre-remediation framing above) — the
clean rerun confirms rather than revises it; the session-confound question remains open and unresolved,
exactly as flagged originally.

**Artifacts (clean rerun)**: `e026_adr_exhaustion_clean.py`, `e026_adr_exhaustion_clean_results.json`,
`e026_events_up_clean.csv`, `e026_events_down_clean.csv`.
