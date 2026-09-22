# SECOND-EDGE SEARCH V1 — full-history, matched-timing-null gate

CEO directive: find a second tradeable edge beyond S5, don't stop. Method driven by the Statistician's decisive lesson (2026-09-22): the correct
null for a directional strategy holds regime/direction/rr/risk fixed and randomises ONLY entry timing (the sole thing these strategies claim to
supply); long-timing-beta is captured by that null, a real edge is not.

## Infrastructure fix (root cause of the first batch's failure)
The Statistician found `mstrat.load()` reads a **2023+ D1 file**, so `pdh/pdl/h4/h1/d1` context is only 23.7% non-null (all from 2023-01-03) —
which is why S9/S20 were 2023-only and un-validatable across eras. Built `fh_panel.py`: full-history causal overrides from M15 (pdh/pdl = prev
completed UTC-day, pw = prev ISO-week, h4/h1/d1 trend = causal resample, all lookahead-free) → **100% coverage from 2011-07-27, 0 leak bars,
causal spot-check 8/8**. This unlocks the whole governed grammar for TRUE calendar-era validation.

## Method
Re-ran the governed S1–S51 grammar (2,448 configs) on the full-history panel at real cost (BASE 0.05 / STRESS 0.24, TICK 0.01), gated by the
decisive discriminator: **positive in ALL THREE calendar eras** (2011-16 / 2017-21 / 2022-26) — the S5 property a current-regime long-beta candidate
cannot have. Survivors then tested against the **matched-timing null** (400 reps). Null harness validated on S5: S5 real +0.092 vs null +0.034,
**null captures only 37%, p=0.013 → genuine timing edge** (this is why the null captured 83-92% of S9/S20 but only 37% of S5).

## Result — 5 calendar-era survivors, 4 are the S49 artifact, 1 real
`gov` screen: only 5 of 2,448 are positive in all three calendar eras. **4 are S49** (the inverted-stop / same-bar fill artifact — 97.2% wrong-side
stop, R max +225.7 — rejected by Alpha, confirmed by the Statistician; the calendar-era gate does not catch a fake-profit mechanism). **1 genuine:
S17 weekly-level breakout.**

## THE SECOND EDGE — S17 weekly-high breakout (LONG), ATR stop, rr3
`mstrat.s17_setups(level=pw_high, mode=breakout, stop=atr, exit=rr3)` — trade WITH a break through the previous week's high.
| property | value | vs S5 |
|---|---|---|
| N (/yr) · WR | 1,202 (~80/yr) · 33.8% | S5 2006 (~133/yr) · 47% |
| BASE / STRESS expectancy | +0.131 / **+0.063R** | S5 +0.092 / +0.063 (tie at stress) |
| PF (stress) | 1.09 | S5 1.16 |
| **matched-timing null** | real +0.131, null +0.054, **captures 41%, p=0.0500** | S5 captures 37%, p=0.013 |
| STRESS calendar eras | +0.031 / +0.008 / +0.147 (all > 0) | S5 +0.026 / +0.033 / +0.139 |
| corroboration | = **CAND-0037** (independently flagged "FIRST ROBUST-EDGE CANDIDATE") | — |

**It clears the bar that killed S9/S20** (beats the matched-timing null; captures only 41% vs their 83-92%), is positive in all three calendar eras
at stress, is long-only asymmetric (the pw_low SHORT breakout is absolutely negative at stress — not tradeable), robust to exit (rr2 +0.046 / rr3
+0.063; only the ATR stop works, the "level" stop fails), and matches a mechanism the campaign independently flagged robust.

## HONEST WEAKNESSES (load-bearing — this is a WEAKER edge than S5)
1. **Marginal significance:** matched-null p = **0.0500** exactly (borderline; S5 is 0.013).
2. **Fat-tail / trend-dependent:** at STRESS, **drop-best-5% = −0.090R, drop-best-10% = −0.258R** (negative) — the +0.063R is carried by the top
   ~5-10% of trades. This is intrinsic to a trend-continuation breakout (it earns in the few big trending moves), and the big years RECUR across
   eras (2015-16, 2019, 2023-25) rather than being one outlier year — but it is a materially fat-tailed, boom-in-trend / bleed-in-chop profile.
3. **Only 9/16 years positive** at stress; volatile year-to-year (2014 −0.20, 2017 −0.13, 2022 −0.21, 2026 −0.32 vs 2024 +0.51, 2016 +0.30).
4. **Multiplicity:** 1 of 2,448 (S17 has 24 configs; only the pw_high/atr/rr configs work) — grammar-wide FWER/BH-FDR applies.
5. In-sample / materially-exposed (data ends 2026-07-27) — needs prospective or independent-venue confirmation.

## Verdict
```
SECOND_EDGE_SEARCH_V1_COMPLETE = YES
INFRA_FIX = full-history causal panel (fh_panel.py), 100% coverage from 2011, 0 leak
NULL_GATE_VALIDATED = YES (S5 beats matched-timing null, captures 37%, p=0.013)
CALENDAR_ERA_SURVIVORS = 5 (4 = S49 artifact REJECTED, 1 genuine)
SECOND_EDGE_FOUND = YES (weak) -> S17 weekly-high breakout LONG (pw_high/atr/rr3), = CAND-0037 corroborated
  BASE +0.131 / STRESS +0.063R, PF 1.09, all-3-calendar-eras positive, matched-null p=0.0500 captures 41%
QUALITY vs S5 = MATERIALLY WEAKER (p 0.05 vs 0.013; fat-tail db5 -0.090 vs S5 non-outlier; 9/16 yrs; trend-dependent)
OTHER LEADS (secondary, weaker) = S1 PDL-displacement SHORT (all-era +, but db5 strongly negative = outlier-dependent); S5-asia session (weak sibling)
STATUS = ALPHA_SECOND_EDGE_CANDIDATE -> READY_FOR_STATISTICIAN
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

**Bottom line:** there IS a genuine second directional-timing edge — the weekly-high breakout — and it survives the exact test that exposed the last
batch as long-beta. But it is materially weaker and more fat-tailed than S5: a trend-continuation edge that earns in trending years and bleeds in
choppy ones, marginal at p=0.05. It is a legitimate candidate for the Statistician's formal gate (and directly corroborates the pre-existing
CAND-0037), not a validated edge. S5 remains the single robust edge; this would be a diversifying, higher-variance second. No promotion; protections intact.
```
SECOND_EDGE_SEARCH_V1 = WEEKLY-HIGH BREAKOUT is the second edge — real (beats matched-timing null, all 3 eras) but weaker/fat-tailed vs S5; -> Statistician
```
