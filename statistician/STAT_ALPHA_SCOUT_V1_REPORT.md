# STAT — INDEPENDENT STATISTICAL ALPHA SCOUT V1

**Mandate:** CEO — independent statistical discovery scout, blind complement to Alpha
**Division:** Statistician
**Date:** 2026-08-31
**Nature:** DISCOVERY, not validation. Nothing promoted, nothing validated by me.

**Protected and untouched:** S5, Q4, AI Trader, P007, MGMT-004, MT5, StrategyCatalog.

---

## 0 — HEADLINE

One bounded scan of the governed native M5 series. The single most consequential finding is not any
conditional state — it is a property of the **unconditional** path distribution that reframes the whole
Strategy-#2 search:

```
  barriers (U,D)     observed P(+U before -D)   driftless benchmark D/(U+D)      gap        z
    (+100, -100)              0.5192                    0.5000                +0.0192    +2.54
    (+200, -200)              0.5268                    0.5000                +0.0268    +2.41
    (+300, -300)              0.5372                    0.5000                +0.0372    +2.63
    (+200, -100)              0.3201                    0.3333                -0.0133    -1.56
    (+300, -150)              0.2987                    0.3333                -0.0346    -3.29
  buy-and-hold over the same window: 1800.70 -> 4076.51 = +126.4% in 5.0 years
```

**Gold's upward drift is real and shows up cleanly in symmetric races (all above 0.5). But every
asymmetric 2:1 race lands BELOW its driftless benchmark, and the (+300,−150) race does so at z = −3.29.**

The lab's entire strategy inventory is built on fixed ~2:1 geometry — S5 (rr3), H4-bo-raw-S (rr1.5),
COMP-CONT-L (rr2), OBR-BULL-1 (rr2), CRS-1 (rr2). This measurement says that on XAUUSD M5, a 2:1
first-touch geometry is **structurally disadvantaged relative to a driftless walk**, in a market that rose
126%. The drift is there; it simply does not arrive in a path shape that 2:1 stops can harvest.

---

## 1 — DATA AND METHOD

```
  governed native M5 (m5_data.load_m5, no synthesis): 354,669 bars
  span 2021-07-27 15:45Z .. 2026-07-27 17:55Z   sha256 cbb6eebe1a189ebb
  modal step 5 min · gaps>60min: 1,290 (weekends/holidays)
  per-year bars: 2021 30,821 · 2022 70,963 · 2023 70,684 · 2024 71,208 · 2025 70,922 · 2026 40,071
```

**COVERAGE CAVEAT, carried on every finding:** native M5 exists only from 2021-07-27 — **one macro-era**.
No cross-era claim is possible. Year-by-year and DEV/OOS stability are the strongest checks available, and
I do not pretend otherwise.

**Preregistered chronological split (declared before scoring):** DEV ≤ 2024-06-30, OOS after.

**Information-first design (§5):** I measured forward *path distributions* — first-touch races, MFE, MAE,
time-to-expansion — never a forced entry/stop/2R trade. Same-bar ambiguity is resolved **against** the
hypothesis (if both barriers fall inside one M5 bar, the adverse side wins).

---

## 2 — BOUNDED SEARCH SPACE (§8) — declared before scoring

**6 causal state variables**, each computed only from bars ≤ t:
`S1 speed` = (c[t]−c[t−12])/ATR · `S2 vol_state` = ATR/mean(ATR,288) · `S3 range_loc` = position in the
trailing 24h range · `S4 session` (AS/LN/NY/LT) · `S5b breakout` = close beyond the 48-bar extreme
(*direction revealed*) · `S6 path_order` = adverse-first vs favourable-first over the last 2h.

**3 targets × 2 sides**, over a 288-bar (24h) forward horizon: P(+100 before −80), P(+200 before −100),
P(+300 before −150), plus MFE/MAE and time-to-first-100p.

```
  DECLARED BUDGET : 6 states x 3 targets x 2 sides = 36  +  8 preregistered interactions  =  44
  ACTUALLY SCORED : 44        (plus 6 descriptive baseline benchmark races, not hypothesis tests)
  Bonferroni at alpha=0.05 over 44 -> per-test 0.0011 -> |z| > 3.26 required
```

Uncertainty is **day-clustered** throughout, never nominal-N.

---

## 3 — POSITIVE CONTROL (§9) — **PASS**

End-to-end: a synthetic drift injected into the real price series after a random 3% causal state, then the
full pipeline re-run.

| injected drift | P given state | base | lift | z |
|---|---|---|---|---|
| 0 p (null) | 0.4578 | 0.4581 | **−0.0002** | **−0.02** |
| 30 p | 0.4830 | 0.4685 | +0.0145 | +2.14 |
| 60 p | 0.5166 | 0.4752 | +0.0414 | +6.05 |
| 150 p | 0.5946 | 0.4930 | +0.1016 | +14.3 |

**Monotone recovery with a clean null at dose 0.** The engine detects real effects and does not fabricate
them. *Disclosure:* my pre-set pass flag demanded lift > 0.05, which the +60p dose does not reach — the
threshold was miscalibrated to the injected dose, not an engine failure. The z-curve is the substantive
evidence and I report the miscalibration rather than quietly relaxing the flag.

---

## 4 — TOP 5 PHENOMENA

### P1 — LONDON-SESSION PATH ASYMMETRY  *(strongest)*

| field | value |
|---|---|
| causal definition | `session == LN` (UTC hour ∈ [8,13)) — known at bar open |
| timeframe | M5 native, 24h forward horizon |
| direction known | **before** the event (a clock, not a price event) |
| N | 73,796 (T1) · **1,290 days** |
| baseline / conditional | P(+100 before −80): 0.4663 → **0.4286** |
| effect size | **−0.0377 (z = −3.59)** · T2 −0.0267 · T3 −0.0219 |
| **non-overlapping sample** | T1 −0.0736 (z −2.38) · T2 −0.0610 (z −1.98) · **T3 −0.0977 (z −2.85)** — *strengthens* |
| DEV / OOS | −0.0269 / −0.0174 — **sign-consistent** |
| year stability | **6 / 6 years same sign** (−0.052, −0.014, −0.032, −0.027, −0.010, −0.020) |
| MFE / MAE | median MFE 137p vs 142p; **MAE 130p vs 122p**; MFE/MAE **1.048 vs 1.161** |
| time-to-100p | **3.4h vs 6.9h baseline** — London reaches ±100p twice as fast |
| multiple-testing | **clears Bonferroni over 44** (only phenomenon that does) |
| mechanism | London is the liquidity handover into the European session: fastest expansion of the day, and on this instrument that expansion is adversely skewed for long-side path races |

**Classification: `STRATEGY_HYPOTHESIS_WORTH_TESTING`** — but as a **conditioning variable / overlay**,
not a standalone strategy. It is the only phenomenon that gets *stronger* under the strictest sampling.

### P2 — BOTTOM-OF-24h-RANGE DOWNSIDE CONTINUATION

| field | value |
|---|---|
| causal definition | `range_loc < 0.1` — close in the lowest decile of the trailing 288-bar range |
| N | 14,336 (T3) · 534 days |
| baseline / conditional | P(+300 before −150): 0.3030 → **0.2427** |
| effect size | **−0.0603 (z = −3.12)**; T2 −0.0460 (z −2.59) |
| with fast-down (`speed < −1.5 ATR`) | T3 **−0.0549 (z −3.27)**, T2 −0.0416 |
| DEV / OOS | −0.0527 / −0.0367 — sign-consistent (and −0.0539 / −0.0339 for the interaction) |
| year stability | **5 / 6** same sign (interaction: **6 / 6**) |
| MFE / MAE | MFE 130p vs 142p; MFE/MAE 1.085 vs 1.143 |
| non-overlapping | **N too small to test — a real, unresolved limitation** |
| multiple-testing | z −3.27 for the interaction ≈ the Bonferroni line (3.26) |
| mechanism | downside continuation from range lows; consistent with the asymmetric path shape in §0 |

**Classification: `STRATEGY_HYPOTHESIS_WORTH_TESTING`**, conditional on the overlap caveat being resolved.

### P3 — TOP-OF-24h-RANGE UPSIDE CONTINUATION — **the era-beta trap**

Pooled it looks strong: `range_loc > 0.9` → P(+300 before −150) 0.2915 → **0.3463 (+0.0548, z +2.56)**; with
fast-up, +0.0541 (z +2.70).

**It does not survive:**
- year stability **2 / 6** same sign (2021 −0.057, 2022 −0.014); the interaction is **1 / 6**
- DEV +0.0156 vs OOS +0.0570 — almost entirely the recent period
- **non-overlapping sample flips sign** (T1 −0.0301)
- 2025 alone contributes +0.089

**Classification: `NOISE` (era-beta).** This is precisely the hindsight-era artifact §4E warns against: it
is a restatement of "gold went up in 2024–25", not a conditional edge. Reported prominently *because* it is
the most seductive-looking number in the scan.

### P4 — PATH-ORDER (ADVERSE-FIRST) → FORWARD RANGE COMPRESSION

`adverse-first over the last 2h` → P(+300 before −150) 0.2999 → 0.2698 (−0.0300, z −2.33).

Directionally it fails: **DEV −0.0140 vs OOS +0.0045 — sign-inconsistent**, 4/6 years.

But the *path shape* is a clean, non-directional finding: median **MFE 119p vs 142p** and **MAE 107p vs
125p** — both tails compress, and time-to-first-100p rises to 7.6h vs 5.7h. Adverse-first states predict a
**quieter forward 24 hours**, not a direction.

**Classification: `INFORMATION_ONLY`** — a causal volatility/quiescence predictor, potentially useful as a
sizing or stand-aside input. Not a directional edge.

### P5 — 48-BAR BREAKOUT UP ("direction revealed") — **the conditional-response frame, and it is null**

`close > max(high[t−48:t])` → P(+200 before −100) +0.0165 (z +1.45); P(+300 before −150) +0.0195 (z +1.33).

Year stability **1 / 6** same sign; DEV +0.0326 decaying to OOS +0.0062.

**Classification: `NOISE` on this scan.** I report it deliberately: the "let price reveal direction, then
harvest continuation" frame — the one the program's own architecture review nominated as the most promising
unexplored representation — **does not deliver** on a plain 48-bar breakout at M5. That is a genuine
negative result about the favoured hypothesis, not a gap in the scan.

---

## 5 — ANSWERS TO THE CEO'S SPECIAL QUESTION (§12)

### Is the failure to find Strategy #2 efficiency, search-representation failure, or insufficient information?

**A MIXTURE — but not in equal parts. My reading, in order of weight:**

1. **PAYOFF-REPRESENTATION FAILURE (largest single contributor).** §0 is the evidence: symmetric races are
   above 0.5, asymmetric 2:1 races are below their benchmark, and (+300,−150) at z = −3.29. Every strategy
   the lab has built imposes ~2:1 geometry. The search has been looking for edge *through a lens that the
   instrument's path shape penalises*. This is not efficiency — it is the wrong payoff representation.

2. **INSUFFICIENT INFORMATION (second).** The conditional lifts I can find are 2–6 percentage points on
   probabilities near 0.3–0.47. Against a round-trip cost of ~4 project pips and stops of 15–25 pips, a
   4-point probability lift is thin. The states I scanned genuinely do not carry large conditional
   information.

3. **MARKET EFFICIENCY (real but smallest).** The unconditional path is close to a martingale in the
   symmetric race, and the state variables move it only modestly. But "close to efficient" is not the same
   as "efficient": London shows a 6/6-year, Bonferroni-clearing, non-overlap-strengthening asymmetry, and
   range-location shows a 5–6/6-year continuation asymmetry. Those are not what an efficient market looks
   like.

4. **SEARCH-REPRESENTATION FAILURE beyond payoff (present).** Note that the frame the program most wanted
   to work — "direction revealed, then harvest continuation" (P5) — is null here, while a *clock* variable
   (London) is the strongest effect found. The search has been over-invested in price-structure events and
   under-invested in time-of-day and path-shape conditioning.

### What statistical behavior looks most underexploited?

**The reward-to-risk geometry itself.** In order:

1. **The 2:1 penalty (§0).** Symmetric geometry beats the benchmark; 2:1 geometry loses to it. Nothing in
   the inventory tests near-1:1 or adaptive-R geometry on M5. This is measurable, large, and untouched.
2. **Time-to-expansion as a target rather than direction.** London reaches ±100p in 3.4h vs 6.9h baseline —
   a factor-of-two difference in *speed*, far larger than any directional lift I found. The program has
   never traded speed.
3. **Forward-range compression (P4).** MFE and MAE both shrink ~15% conditional on adverse-first path
   order, with no directional content — a sizing/stand-aside input the program does not use.
4. **Session conditioning as an overlay** rather than as a strategy family.

---

## 6 — LEADS AND DISPOSITION (§11)

```
NEW_DISCOVERY_LEADS        = 2
  L1  LONDON PATH ASYMMETRY  (P1)  -- STRATEGY_HYPOTHESIS_WORTH_TESTING
  L2  RANGE-LOW DOWNSIDE CONTINUATION, with fast-down interaction (P2)
                                   -- STRATEGY_HYPOTHESIS_WORTH_TESTING (overlap caveat unresolved)

STRONGEST_LEAD             = L1 (London path asymmetry)
READY_FOR_ALPHA_REPLICATION = YES
NEXT_AUTHORIZED_ACTION      = NONE — CEO DECISION REQUIRED
```

**Frozen causal phenomena (not strategies), with the simplest possible trade interpretation, unoptimised:**

- **L1** — *phenomenon:* during 08:00–13:00 UTC the forward first-touch race is adversely skewed for the
  long side (P(+100 before −80) 0.429 vs 0.466) and expansion is ~2× faster.
  *Simplest interpretation:* a **short-side or stand-aside overlay on London hours**, or a session filter on
  any existing long-side entry. **Not** a standalone entry rule.
- **L2** — *phenomenon:* `range_loc < 0.1` (and more strongly with `speed < −1.5 ATR`) reduces
  P(+300 before −150) from 0.303 to 0.243.
  *Simplest interpretation:* a **short at the low decile of the trailing 24h range**, stop above the range
  low, target ~2× the stop. Its own §0 caveat applies — 2:1 geometry is exactly what the data penalises,
  so a near-1:1 or MFE-based exit should be tested first.

**I have deliberately not built entries, stops, targets, sizing or filters for either.** Per §1 and §11 I
freeze the phenomena and hand them back. **I must not and will not perform their independent validation.**

---

## 7 — LIMITATIONS

1. **One macro-era.** Native M5 is 2021-07+ only. No cross-era falsification is possible; the 2022 and 2026
   sign flips in the symmetric race show the era-dependence is real.
2. **Overlap.** Observations are 288-bar-overlapping. I used day-clustered SEs throughout and a
   non-overlapping (1-per-24h) robustness check, but that check has adequate N only for the session
   phenomenon. **L2's overlap robustness is unresolved and must be settled before any further work.**
3. **44 declared tests.** Only L1 clears Bonferroni outright; L2's interaction sits on the line. I ranked
   by coherence (year stability, DEV/OOS sign, non-overlap survival) rather than by p, as §8 directs.
4. **No costs applied.** This is an information scan; no phenomenon here has been shown to survive
   transaction costs, and the thinness of the lifts against ~4-pip round trips is the central practical
   doubt.
5. **Bounded by construction.** Six state variables is a small representation. A null here bounds *this*
   representation, not the space.

---

## 8 — ARTIFACTS

`statistician/scout/` — `scan.py` (preregistration, data verification, barrier engine),
`run2.py` (positive control + 44-test scan), `run3.py` (dose-response control + top-5 deep dive),
`run4.py` (baseline path asymmetry), `scan_results.json`.

**Environment:** Python 3.14 · native M5 `cbb6eebe1a189ebb`, 354,669 bars, 2021-07-27 → 2026-07-27 ·
horizon 288 M5 bars · PIP = 0.10 USD.

---

*Statistician division — independent statistical discovery. Nothing in this report is validated, and no
phenomenon here may be treated as a strategy without independent validation by another owner.*
