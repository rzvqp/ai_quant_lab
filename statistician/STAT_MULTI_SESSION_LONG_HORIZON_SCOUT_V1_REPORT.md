# STAT_MULTI_SESSION_LONG_HORIZON_ALPHA_SCOUT_V1 — REPORT

**Mandate:** `MULTI_SESSION_LONG_HORIZON_ALPHA_SCOUT_V1` — independent discovery, change of horizon.
**Division:** Statistician. **Date:** 2026-09-01.
**Code:** `statistician/longhorizon/` — `PREREG.md` (budget declared before scoring), `FREEZE.md`
(top-5 frozen before OOS), `engine.py`, `scan.py`, `pc.py`, `post.py`, `power.py`, `confound.py`,
`audit.py`, `dev_scan.json`, `post.json`.

## HEADLINE

**Changing the horizon did not unblock Strategy #2, and the reason is not the horizon.**

Across 14.2 years of governed M15 — **9.2 years more history than native M5** — and 60 pre-declared
hypotheses at 6h/12h/24h/48h, measured on **strictly non-overlapping independent episodes**:

| target class | tests | best \|z\| | tests with \|z\| > 2 |
|---|---|---|---|
| **DIRECTION** | 18 | **1.98** | **0** |
| MAGNITUDE | 31 | 3.58 | 10 |
| TIMING | 3 | 1.55 | 0 |
| TAIL | 6 | 3.64 | 2 |

**Not one directional hypothesis reached \|z\| = 2.** On native M5, Scout V2's best of 80 direction tests
was \|z\| = 1.51. Direction is null at five minutes and null at forty-eight hours. Four independent scans,
four directional nulls.

Of the five phenomena frozen before OOS, **four failed** the post-freeze battery and **one survives as
INFORMATION_ONLY**. `STRATEGY_HYPOTHESES_WORTH_TESTING = 0`.

But the scan produced one clear affirmative that changes what the next question should be — see §6.

---

## 1 — DATA AUDIT (§2)

```
LONG_HORIZON_DATA_AUDIT_PASS = YES
```

| | |
|---|---|
| series | `OANDA_XAUUSD_M15.csv`, **native** (not derived, no M5 synthesis, no new acquisition) |
| sha256 | `57f4ed9544993c8fbba28d9c1e3319f2…` |
| full file | 355,696 bars, 2011-07-26 → 2026-07-27, **0 duplicate timestamps** |
| step integrity | 98.9% of steps are exactly 15 min; every remaining gap is a weekend or a holiday long weekend |
| gaps > 3 days | 27, **all** Easter / Christmas / New-Year closures. **No structural hole.** |
| bars per year | 23,535–24,109 for every complete year 2012–2025 — uniform |
| timezone | UTC throughout, from the file's unix-second `time` column |

**A prior program note warned of an "unratified 2013–2016 gap".** I checked it directly: 2013 = 23,796,
2014 = 23,801, 2015 = 23,735, 2016 = 23,631 bars — indistinguishable from every other year. **That gap is
not present in this raw M15 series**; it belongs to a derived HTF-context feature build, not here.

**Holdout firewall honoured.** The program constant `RESEARCH_HOLDOUT_CUTOFF_UTC = 2025-10-23T09:15:00Z`
(`edge_research/_common.py:43`) is a standing escrow. This mandate did not authorise consuming it, so I
truncated there and **did not touch the 17,792 bars beyond it**. Cost: ~9 months of the most recent data.
I judged preserving the program's only untouched holdout worth more than 9 months of a 14-year sample.

```
HISTORY_RANGE_USED = 2011-07-26 -> 2025-10-23   (337,904 M15 bars, 14.2 years)
native M5 for comparison        = 5.0 years     -> +9.2 years of history
```

---

## 2 — INDEPENDENCE UNIT (§3) — declared first, and it changed the answers

This is where recent leads died, so the design starts here.

```
INDEPENDENCE_RULE = one anchor per trading day at a single FIXED UTC hour;
                    non-overlapping forward windows (stride = 1 day for 6/12/24h, 2 days for 48h);
                    anchors whose forward window spans a weekend/holiday are dropped;
                    primary N = INDEPENDENT_EPISODES; inference = month-cluster-robust (CR1).
```

Two consequences worth stating plainly:

1. **Time-of-day is exact by construction.** Every conditional episode and every baseline episode sits at
   the same clock hour. The session-composition confound that closed V2-4 **cannot arise here**. It is not
   controlled for — it is designed out.
2. **N collapses honestly.** 337,904 bars become **2,918** independent 24h episodes and **1,084** 48h
   episodes. Every z below is on that basis. No raw-bar z is used anywhere.

**A design defect I caught and fixed before scoring.** My first anchor was 22:00 UTC. It exists on only
~46% of trading days, because the daily rollover moves between 21:00 and 22:00 UTC with US DST — the anchor
would have been *seasonally sampled*, reintroducing exactly the composition problem I was designing out.
Hours 00:00–16:00 have ~100% coverage; the scan uses **00:00 UTC** (branches A/B/C/E/F) and **08:00 UTC**
(branch D). Also fixed before scoring: `.astype("int64")` on a tz-aware column silently produced garbage
timestamps, which had corrupted every day-derived feature.

---

## 3 — POSITIVE CONTROL (§15)

```
POSITIVE_CONTROL = PASS
```

My first control run **failed**, and the failure was real: the difference-in-means estimator I had used in
Scout V1/V2 clusters only the conditional group and treats the baseline mean as fixed. Its null
false-positive rate here was **10.0%** at a nominal 5% — **anti-conservative**. I replaced it with a
CR1 month-cluster-robust regression, which is the correct estimator for this design.

| target | injected δ | mean recovered | bias | detection rate |
|---|---|---|---|---|
| direction (24h return) | 0 | 0.28 | +0.28 | **6.7%** ← null FP rate |
| | 15 | 15.28 | +0.28 | 42.0% |
| | 30 | 30.28 | +0.28 | 90.3% |
| | 80 | 80.28 | +0.28 | 100.0% |
| magnitude (24h \|return\|) | 0 | 0.34 | +0.34 | **5.0%** ← null FP rate |
| | 30 | 30.34 | +0.34 | 99.7% |

Recovery is unbiased at every δ, power rises monotonically, and the null rate sits at nominal. Measured over
**300 seeds per cell** — a single-seed pass/fail is not a valid control on a calibrated estimator, since ~5%
of random states *must* exceed \|z\| = 1.96. My first script used a single seed; that criterion was wrong,
not the estimator.

---

## 4 — SEARCH BUDGET (§14)

```
TOTAL_EFFECTIVE_HYPOTHESES = 60 declared, 60 scored, 58 estimable
```

Declared by branch in `PREREG.md` **before scoring**: A 12 · B 10 · C 12 · D 8 · E 12 · F 6.
After the Scout V2 breach (60 declared, 80 scored) the budget is now **enforced in code** — `score()` raises
on hypothesis 61. It was not approached. Two hypotheses (`C2-DIR-24`, `C2-MAG-24`) were not estimable —
"large trailing move that fully retraced" is rare at daily anchors (n = 31). Disclosed, not replaced.
Multiplicity assessed at **m = 60** → Bonferroni requires \|z\| > 3.02. Positive controls were 3 declared
runs plus calibration, outside the 60.

---

## 5 — TOP 5 (§19) — frozen before OOS, then tested once

`FREEZE.md` was written before any OOS inspection; selection rule was mechanical (top 5 by \|DEV z\|).
It recorded at freeze time that #1 rested on a 0/57 zero cell and was expected to be fragile.

### TOP_1 — `F1-P500-48` — **NOISE**
5d/20d realised-vol ratio in bottom 20% → P(\|excursion\| ≥ 500p) over 48h. Branch F, TAIL.
DEV n_cond 57, lift −0.070, **z −3.64** (the only other Bonferroni survivor). OOS/FULL **z −0.89**;
controls absorb it entirely; stride×2 **z −0.23**. The DEV z was a zero-cell artefact, exactly as flagged
at freeze. **Dead.**

### TOP_2 — `B3-EXC-48` — **NOISE**
Same state → largest 48h excursion. DEV lift −53.1p, **z −3.58**. OOS z −1.30, FULL z −0.92.
Era blocks negative in only **2 of 4** estimable. Drop-best-1% → z −1.14 (**weakens**).
Dependence (stride×2, 544 episodes) → lift −3.7p, **z −0.15** — the point estimate collapses, not just the
power. Notably the matched control makes it *stronger* (z −2.83), but that cannot rescue a phenomenon that
disappears on an independent subsample of its own episodes. **Dead.**

### TOP_3 — `E1-MAG-24` — **INFORMATION_ONLY (weak)**
Previous UTC day's range in the bottom 20% of its own trailing 20-day history → \|24h move\|.
DEV n_cond 389, lift −14.4p, z −3.00 · OOS lift −6.2p, z −0.71 (**sign agrees**) · FULL −9.9p, z −2.00.
PRE_2021 −13.9p (z −2.95) · POST_2021 −5.4p (z −0.50). **Era blocks 6/6 negative**
(−28.0, −13.5, −8.2, −11.5, −9.7, −0.7). Outliers benign: top-1% of episodes carry 7.9% of total movement;
**drop-best-1% HOLDS** (z −3.07), drop-best-5% holds (z −3.02).
**But the matched control absorbs it** — with trailing volatility, recent-move size, range position and
20-day volatility as covariates, z falls to −1.70: **ADDS INFORMATION = NO**. It is trailing volatility
wearing a daily-range costume. Its half-sample estimate also flips (+0.8, z +0.10). Real, monotone,
decaying, and **not incremental**.

### TOP_4 — `D4-MAG-6` — **INFORMATION_ONLY — the only phenomenon that survived everything**
**Causal definition:** at the 08:00 UTC anchor, the 00:00–08:00 UTC window is complete. If its close sits in
the **top or bottom 20% of that window's own high–low range**, the state is on. Target: **\|net move\| over
the next 6h**. Branch D, MAGNITUDE. Source timeframe M15, forecast horizon 6h.

| | |
|---|---|
| raw N (bars) | reported secondarily only |
| **INDEPENDENT_EPISODES** | **1,455 conditional of 3,673** (DEV 720 / OOS 735), 90 month clusters |
| DEV (2011–2018) | base 57.4p → cond 49.1p, lift **−8.26p**, z **−2.87** |
| OOS (2019–2025) | base 88.1p → cond 79.5p, lift **−8.61p**, z **−1.94** — **sign agrees, size agrees** |
| FULL | lift **−7.08p**, z **−2.72** (−10% of the 71.5p base) |
| PRE_2021 | −7.68p, z −2.79 |
| POST_2021 | −8.77p, z −1.57 |
| era blocks | **6/6 negative**: −21.9 · −7.3 · −2.4 · −7.7 · −6.1 · −12.3 |
| matched control | −7.08 → **−6.06, z −2.35** (only 14.4% absorbed) → **ADDS INFORMATION = YES** |
| outliers | top-1% carry 7.1% of movement; **drop-best-1% holds** (z −2.16); drop-best-5% weakens (−1.60) |
| dependence | stride×2 (1,837 episodes) → **z −2.29**, holds |
| multiple testing | \|z\| 2.87 DEV — **does not clear Bonferroni m=60 (3.02)** |
| MFE / MAE / P100 / P300 | conditional 6h: base P(exc≥100p) 18.5%, P(exc≥300p) 1.8%; state shifts magnitude ~−10%, not the tail shape |
| **DIRECTION** | `D4-DIR-6`, the pre-registered companion: lift **+0.22p, z +0.06**. **Zero.** |

**Confound audit (beyond the mandated control set).** The obvious alternative is that this is just "the Asia
range was small". **It is not** — and the data says the opposite: mean Asia range is *larger* in the state
(12.04 vs 10.58 USD), and adding the Asia-range percentile as a covariate makes the effect **stronger**
(z −2.80; with the full control set −2.94). Stratified by Asia-range tercile the sign is negative in all
three (low z −1.68, mid −0.88, high −2.32).

**Verdict: INFORMATION_ONLY, and it is the honest ceiling of this scan.** It predicts that the next six
hours will move about **10% less** than usual, and it predicts **nothing** about direction. Under mandate
§12 that is INFORMATION_ONLY unless a second causal event reveals direction — and none is offered here.
A −7 pip change in expected 6h movement is a horizon/expectation modifier, not a trade, and I will not
dress it up as one.

### TOP_5 — `E1-EXC-48` — **NOISE**
Low-range previous day → largest 48h excursion. DEV lift −34.7p, z −2.68 · **OOS lift +15.1p, z +0.71 —
the sign flips.** Eras 4/6. Matched control leaves +4.4p (z +0.31). **Dead.**

```
STATISTICALLY_MEANINGFUL_PHENOMENA = 1 (D4-MAG-6, INFORMATION_ONLY)
STRATEGY_HYPOTHESES_WORTH_TESTING  = 0
STRONGEST_LONG_HORIZON_LEAD        = D4-MAG-6 -- and it is not a strategy lead
NEW_LONG_HORIZON_LEADS             = 0 tradeable / 1 informational
READY_FOR_ALPHA_REPLICATION        = NO
```

Mandate §20 does not trigger: nothing qualified as `STRATEGY_HYPOTHESIS_WORTH_TESTING`, so no minimal
causal trade interpretation is offered. Proposing one would be manufacturing a strategy from a magnitude
result with a measured direction z of +0.06.

---

## 6 — THE ONE AFFIRMATIVE FINDING: the moves are there

Unconditional payoff geometry on independent episodes — this is descriptive, not a hypothesis:

| horizon | mean \|net move\| | mean MFE | mean MAE | mean largest excursion | **P(exc ≥ 100p)** | **P(exc ≥ 300p)** |
|---|---|---|---|---|---|---|
| 6h | 44p | 46p | 45p | 73p | 18.5% | 1.8% |
| 12h | 70p | 72p | 72p | 114p | 40.7% | 4.5% |
| **24h** | **119p** | 119p | 121p | 191p | **73.1%** | **15.1%** |
| **48h** | **172p** | 173p | 173p | 274p | **91.0%** | **30.0%** |

The lab's standing economic-profile directive asks for **70–80+ pip targets**. At 24h a XAUUSD window
touches ±100 pips **73% of the time**, and at 48h **91%**. The move sizes the program needs are **structurally
present** at these horizons and are *not* present at M5 scale. That is a real, useful, affirmative result.

**What is missing is not the move. It is the direction.** Unconditional drift is negligible: 24h mean
+4.7p (z +1.27, P(up) 0.510), 48h +1.5p (z +0.20, P(up) 0.503). The 6h +3.4p (z +2.54) is the 14-year gold
bull market, worth 8% of a typical 6h move — not a trade.

---

## 7 — HOW BIG AN EFFECT COULD THIS SCAN HAVE SEEN? (the limit of my null)

A null is only meaningful if the scan was powered. Minimum detectable directional lift, α .05 / 80% power,
for a state at ~20% of episodes:

| horizon | episodes | min detectable direction | as % of the typical move |
|---|---|---|---|
| 6h | 3,673 | 8.3p | 19% |
| 12h | 3,672 | 12.5p | 18% |
| 24h | 2,918 | 23.8p | 20% |
| 48h | 1,084 | 52.4p | 31% |

**State this precisely: I can rule out directional edges worth ≳20% of the typical move. I cannot rule out
smaller ones.** A state shifting the 24h distribution by 10 pips would be invisible here and could still be
economically meaningful at scale. The directional null is strong, repeatedly reproduced, and **bounded**.
This is a limit of the independent-episode discipline, not a reason to abandon it — the pseudo-N designs
that "found" small directional effects were finding their own overlap.

---

## 8 — CEO QUESTIONS (§21)

**1. Is the Strategy-2 blockage partly caused by searching too short?**
```
SEARCHING_TOO_SHORT_SUPPORTED = NO
```
Nine extra years of history, four longer horizons, six orthogonal branches, and direction got *no* better —
best \|z\| 1.98 versus 1.51 on M5, both null. Horizon was a reasonable hypothesis and it is now tested and
rejected. The blockage is in the **target representation** (pre-move direction), not the time scale.

**2. Does XAU show stronger robust information over 6–48h than native M5?**
**NO — and the comparison the program has been making is not valid.** Scout V2's \|z\| up to 8.89 came from
*overlapping* M5 bars. Its own non-overlap check on its best lead gave **z −2.40** on 150–246 effective
observations. This scan's best surviving effect gives **z −2.72** on **1,455** independent episodes. On the
only comparable basis, long-horizon and M5 structure are the **same order of magnitude**. The apparent M5
superiority was a pseudo-N artefact. The long-horizon result is, if anything, better *evidenced* — same
strength on ten times the independent sample.

**3. Is direction more predictable at longer horizons?**
**NO.** 18 directional hypotheses, best \|z\| 1.98, none above 2, none near Bonferroni. Direction is null at
5 minutes and null at 48 hours — subject to the power bound in §7.

**4. Are 100–300 pip moves more naturally monetizable at these horizons?**
**The moves are there; the direction is not.** P(exc ≥ 100p) rises 18.5% → 73.1% → 91.0% across 6h → 24h →
48h, and P(exc ≥ 300p) reaches 30% at 48h. So the horizon is *right* for the program's target sizes — this is
the strongest argument yet for building at 24–48h rather than M5. It only becomes monetizable once something
reveals direction.

**5. If you had to continue discovery in ONE horizon, which?**
**24h, daily-anchored.** It has the best joint properties: 2,918 independent episodes over 14.2 years,
P(±100p) = 73%, a mean move of 119p that matches the program's economic profile, and full use of the long
history. 6h is too small (P(±100p) = 18.5%); 48h halves the episode count for little extra geometry.
**But horizon is not the binding constraint** — I would not spend another cycle searching for a *state* that
predicts direction at any horizon.

---

## 9 — PRE-2021 (§16, §17)

```
PRE_2021_INFORMATION_FOUND = YES  -- but only MAGNITUDE information, not direction
```

Because DEV is entirely 2011–2018, every DEV discovery is by construction a pre-2021 discovery — the exact
question native M5 cannot address. What exists pre-2021: `D4-MAG-6` (−7.7p, z −2.79) and `E1-MAG-24`
(−13.9p, z −2.95), both with 6/6 negative era blocks spanning 2011–2025. **What does not exist pre-2021 is
any directional information** — the directional null is uniform across all six era blocks and both regimes.

```
PRE_2021_SUPPORT:  D4-MAG-6 YES  |  E1-MAG-24 YES  |  B3-EXC-48 NO  |  E1-EXC-48 NO  |  F1-P500-48 NO
```

No phenomenon here exists *only* in the recent gold regime, and none was retained on that basis.

---

## 10 — RECOMMENDED NEXT RESEARCH ACTION

```
RECOMMENDED_NEXT_RESEARCH_ACTION =
  Stop searching for a causally-observable STATE that predicts direction. Four independent scans across
  two timeframes, two representations and 200+ hypotheses have returned the same null, now bounded at
  ~20% of a typical move. Instead port the EVENT-REVEALED-DIRECTION paradigm -- the only paradigm that
  has ever produced a validated edge in this program -- to the 24h horizon, using the 14.2-year M15
  history and the independent-episode discipline established here, where P(+-100p) = 73% and the mean
  move is 119 pips.
```

The logic is narrow and I want it stated as such: this scan does not prove that paradigm will work at 24h.
It establishes two things that make it the best-supported next step — that the **payoff geometry at 24h fits
the program's stated economic profile**, and that the **alternative paradigm (state-predicts-direction) is
now rejected over 14 years and four horizons with a quantified detection floor**.

---

## 11 — FINAL

```
MULTI_SESSION_LONG_HORIZON_ALPHA_SCOUT_V1_COMPLETE = YES
LONG_HORIZON_DATA_AUDIT_PASS = YES
POSITIVE_CONTROL             = PASS

HISTORY_RANGE_USED           = 2011-07-26 -> 2025-10-23 (337,904 native M15 bars, 14.2 y, holdout respected)
INDEPENDENCE_RULE            = fixed-UTC-hour daily anchors, non-overlapping forward windows,
                               weekend-spanning windows dropped, month-cluster-robust (CR1) inference,
                               primary N = INDEPENDENT_EPISODES
TOTAL_EFFECTIVE_HYPOTHESES   = 60 declared / 60 scored / 58 estimable  (budget enforced in code)

STATISTICALLY_MEANINGFUL_PHENOMENA = 1
STRATEGY_HYPOTHESES_WORTH_TESTING  = 0

TOP_1 = F1-P500-48  NOISE            (DEV z -3.64 -> OOS -0.89; zero-cell artefact, flagged at freeze)
TOP_2 = B3-EXC-48   NOISE            (DEV z -3.58 -> OOS -1.30; collapses on subsample, z -0.15)
TOP_3 = E1-MAG-24   INFORMATION_ONLY (6/6 eras, drop-best holds; matched control absorbs it -> not incremental)
TOP_4 = D4-MAG-6    INFORMATION_ONLY (survives OOS sign, 6/6 eras, matched control, confound audit,
                                      outliers and dependence -- but is MAGNITUDE-only, -10%, direction z +0.06)
TOP_5 = E1-EXC-48   NOISE            (OOS sign flips)

STRONGEST_LONG_HORIZON_LEAD  = D4-MAG-6 (INFORMATION_ONLY -- not a strategy lead)
PRE_2021_INFORMATION_FOUND   = YES (magnitude only)
SEARCHING_TOO_SHORT_SUPPORTED = NO
READY_FOR_ALPHA_REPLICATION  = NO

NEXT_AUTHORIZED_ACTION = NONE -- CEO DECISION REQUIRED
```

**Protection (§22).** Not researched: L1, P2, V2-4, scheduled events, Family E, S5. Not modified: Q4,
AI Trader, P007, MGMT-004, MT5, StrategyCatalog. Alpha's active P2 work not inspected. No promotion.
Nothing validated by me — I do not validate my own discoveries.
