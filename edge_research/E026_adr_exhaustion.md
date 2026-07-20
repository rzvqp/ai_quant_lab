# E026 — ADR Exhaustion

**Program**: 40-Edge Alpha Discovery Program (Flow A). **Protocol**: `EDGE_RESEARCH_PROTOCOL.md`.
**Category**: Mathematical. **Permanent, append-only research log.**

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
`e026_events_down.csv`.
