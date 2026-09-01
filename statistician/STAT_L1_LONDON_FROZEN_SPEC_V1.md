# STAT_L1_LONDON_FROZEN_SPEC_V1

**Purpose:** freeze the exact statistical phenomenon `L1` discovered in Statistician Alpha Scout V1, so it
can be reproduced without reading Statistician discovery code and without guessing.

**This artifact contains NO strategy content** — no entry, stop, target, sizing or trading rule. It freezes
a measurement, not a trade.

```
PHENOMENON_ID   = L1-LONDON-WINDOW-PATH-ASYMMETRY-V1
SPEC_HASH       = b2bc79c6f7d91aa613657a3ad6e9374b3b0edbe34348e0bf7562c3658f8b3af2
DATASET_HASH    = cbb6eebe1a189ebb20972318a8d98a36bfa461d2cd030bbaa7ba5430cc9f3814
CODE_ENTRYPOINT = statistician/l1/repro.py    (self-contained; reproduces every number below)
ORIGIN          = Statistician Alpha Scout V1, commit cd274f8
                  (statistician/scout/scan.py, run2.py, run3.py)
```

---

## 1 — THE THREE THINGS MOST LIKELY TO BE MISREAD

These are stated first because they are the reason an independent reconstruction diverged.

1. **L1 is a WINDOW, not an OPEN EVENT.** It is **every M5 bar whose UTC hour is in {8, 9, 10, 11, 12}** —
   77,393 bars, 21.8% of the dataset. It is **not** one event per day at the London open, and there is no
   open-bar, first-bar or session-start condition of any kind.

2. **The headline statistic is a PROBABILITY, not a time.** `0.4663 → 0.4286, z = −3.59` is
   **P(+100 project pips touched before −80 project pips)** within 24 hours. It is not a timing statistic.

3. **The timing figure `3.4h vs 6.9h` is a CONDITIONAL median of the UP barrier only.** It is the median
   first-touch time of the **+100p up barrier**, computed **only over observations that reached it within
   24 hours** (censored cases are *dropped*, not censored). It is **not** "time to ±100p".
   Touch rates differ between the groups (L1 60.7% vs baseline 63.1%), so this median is conditional on a
   slightly different denominator in each group.

---

## 2 — DATA

| field | value |
|---|---|
| instrument | OANDA XAUUSD |
| file | `OANDA_XAUUSD_M5.csv` (native governed M5; **no synthesis, no M15→M5 fabrication**) |
| sha256 | `cbb6eebe1a189ebb20972318a8d98a36bfa461d2cd030bbaa7ba5430cc9f3814` |
| bars | 354,669 |
| span | 2021-07-27 15:45:00Z → 2026-07-27 17:55:00Z |
| loader | `m5_data.load_m5()` — de-dupes on `time`, sorts ascending, resets index |
| timezone | **UTC throughout**. `pd.to_datetime(time, unit="s", utc=True)` |
| **DST handling** | **NONE.** Fixed UTC hour buckets. No local-time conversion, no DST shift. |
| missing data | weekend/holiday gaps left as-is. The forward window walks **bar index**, not wall clock, so a 24h horizon = 288 bars regardless of gaps. |
| pip | 1 project pip = **0.10 USD** of XAU price |

---

## 3 — ELIGIBILITY CONDITION (the L1 population)

```python
t  = pd.to_datetime(df["time"], unit="s", utc=True)
hr = t.dt.hour.to_numpy()
sess = np.where(hr < 8, "AS", np.where(hr < 13, "LN", np.where(hr < 20, "NY", "LT")))
L1 = (sess == "LN")            # UTC hour in {8,9,10,11,12}
```

- **No other variable, lookback, threshold or state condition is used.** L1 has no volatility filter, no
  trend filter, no range filter, no price condition.
- **Event deduplication: NONE.** Every eligible M5 bar is one observation. Observations overlap heavily
  (each carries a 288-bar forward window).
- **Baseline population:** the **complement** — every M5 bar with UTC hour outside [8, 13), i.e. AS ∪ NY ∪ LT.
  It is **not** "all bars" and **not** a matched sample.

```
L1_EVENTS       = 77,393 eligible bars   (73,796 resolved for the headline statistic, over 1,289 days)
BASELINE_EVENTS = 277,276 eligible bars  (261,974 resolved for the headline statistic)
```

---

## 4 — THE FORWARD MEASUREMENT (the ±100p race)

For each bar `t`:

```python
ref = close[t]                       # reference price = the CLOSE of bar t
U   = ref + 100 * 0.10               # up barrier   = +100 project pips
D   = ref -  80 * 0.10               # down barrier =  -80 project pips

hit_up = first j in 1..288 with high[t+j] >= U     (else infinity)
hit_dn = first j in 1..288 with low[t+j]  <= D     (else infinity)

T1 = 1.0   if hit_up <  hit_dn
     0.0   if hit_dn <= hit_up        # TIE RULE: both inside one M5 bar -> ADVERSE (0)
     NaN   if both are infinity       # CENSORING: unresolved -> EXCLUDED from the mean
```

| field | value |
|---|---|
| measurement start | bar `t+1` (the bar after the reference bar; the reference bar's own range is not used) |
| maximum horizon | **288 M5 bars = 24 hours** |
| tie rule | both barriers inside one M5 bar → **adverse** (conservative) |
| censoring | unresolved within 288 bars → **excluded**, counted neither way |
| day/session boundary | **none applied** — the forward window is allowed to run past the end of the London window and across the day boundary |

The same construction with `(200, 100)` gives **T2** and with `(300, 150)` gives **T3**.

---

## 5 — THE STATISTIC AND ITS UNCERTAINTY

```python
lift = mean(T[L1 & finite]) - mean(T[~L1 & finite])
# standard error: clustered by CALENDAR DAY (UTC), on the L1 group
g = groupby(day[L1 & finite]).agg(sum, count)
resid = g.sum - g.count * mean_L1
se = sqrt( sum(resid^2) / N^2 * (G / (G-1)) )        # N = L1 observations, G = distinct L1 days
z  = lift / se
```

---

## 6 — REPRODUCED RESULTS (all verified against Scout V1)

### 6.1 Headline probability statistic

| statistic | baseline | L1 | lift | z | V1 claim | |
|---|---|---|---|---|---|---|
| **T1 P(+100 before −80)** | **0.4663** | **0.4286** | **−0.0377** | **−3.59** | (0.4663, 0.4286, −3.59) | **MATCH** |
| T2 P(+200 before −100) | 0.3260 | 0.2993 | −0.0267 | −2.32 | (0.3260, 0.2993, −2.32) | **MATCH** |
| T3 P(+300 before −150) | 0.3036 | 0.2817 | −0.0219 | −1.57 | (0.3036, 0.2817, −1.57) | **MATCH** |

N = 73,796 over 1,289 distinct days (T1).

### 6.2 Timing figure

```
  L1       : n =  46,963   median time to +100p UP = 3.42 h    (V1 reported 3.4 h)
  baseline : n = 174,918   median time to +100p UP = 6.92 h    (V1 reported 6.9 h)
  share reaching +100p within 24h:  L1 0.607  vs  baseline 0.631
```

**This figure was descriptive in Scout V1.** It was **not** subjected to the year, non-overlap or
multiple-testing checks. Those checks were applied to the probability statistics only.

### 6.3 Year-by-year

```
  T3 per-year lift (the original basis of the "6/6" claim):
    2021 -0.052 · 2022 -0.014 · 2023 -0.032 · 2024 -0.027 · 2025 -0.010 · 2026 -0.020   -> 6/6 negative

  T1 per-year lift (headline; computed here as a provenance clarification, not in V1):
    2021 -0.039 · 2022 -0.029 · 2023 -0.035 · 2024 -0.048 · 2025 -0.044 · 2026 -0.026   -> 6/6 negative
```

### 6.4 Non-overlap robustness

Sampling rule: walk bars in order, keep a bar only if it is at least 288 bars after the last kept bar.

| | N | lift | z | V1 claim | |
|---|---|---|---|---|---|
| T1 | 246 | −0.0736 | −2.38 | (−0.0736, −2.38) | **MATCH** |
| T2 | 209 | −0.0610 | −1.98 | (−0.0610, −1.98) | **MATCH** |
| T3 | 150 | −0.0977 | −2.85 | (−0.0977, −2.85) | **MATCH** |

### 6.5 Multiple testing

Scout V1 declared and scored **44** tests. T1's z = −3.59 → two-sided p = 3.3 × 10⁻⁴ →
Bonferroni × 44 = **0.0145 < 0.05**. **Survives.**

---

## 7 — WHY AN INDEPENDENT RECONSTRUCTION DIVERGED

A reconstruction reported ≈ 5.3 h vs 6.6 h and 4/6 years. Both differences are explained by definition, not
by data:

| dimension | frozen L1 | a "London open" reconstruction |
|---|---|---|
| population | **every M5 bar** with UTC hour ∈ [8,13) — 77,393 bars | one event per day at/near the open — ~1,300 events |
| timing statistic | median time to **+100p UP only**, censored cases **dropped** | median time to **±100p** (either side) |
| year claim | 6/6 on the **probability** statistic (T3, and also T1) | 4/6 on a **timing** statistic |
| baseline | complement of the window | typically "all other bars" or a different window |

**Any of these four alone changes the numbers.** The frozen definition above is the one that produced the
Scout V1 result.

---

## 8 — SCOPE AND LIMITS OF WHAT IS FROZEN

- The dataset is **one macro-era** (native M5 begins 2021-07-27). No cross-era claim is available.
- Observations **overlap** heavily; the non-overlap check in §6.4 is the honest sample-size statement
  (N = 150–246, not 73,796).
- The phenomenon is **directional-path asymmetry within a clock window**. No economic mechanism is asserted
  here beyond the observation that the 08:00–13:00 UTC window is the fastest-expanding part of the XAUUSD
  day in this dataset.
- **Nothing in this artifact is validated.** L1 is a frozen phenomenon awaiting independent replication.

---

*Statistician division. Frozen for provenance and reproducibility only. No strategy content, no promotion.*
