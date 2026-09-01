# STAT — INDEPENDENT STATISTICAL ALPHA SCOUT V2

**Mandate:** CEO — orthogonal discovery branches, find Strategy #2
**Division:** Statistician · **Date:** 2026-09-01 · **Nature:** DISCOVERY, not validation

**Excluded as hypotheses throughout (§2):** L1 London, P2 24h-range-base, S5, OBR-BULL-1, M5 Family E,
order blocks, generic BOS/sweep/pullback/session-breakout, simple DXY impulse. **Session is used only as a
matched control.** I did not read Alpha's active L1 replication work (§23).

**Protected and untouched:** S5, Q4, AI Trader, P007, MGMT-004, MT5, StrategyCatalog.

---

## 0 — HEADLINE

Eighty tests across eight branches, and **every one of the twelve strongest results is a TIMING result.
Not one directional or tail target reached |z| > 2.9.**

```
  target class            best |z| across all 80 tests
  SPEED (time to +-100p)          8.89      <- top 12 results are ALL this target
  RARE-EVENT TAIL P(MFE>=300p)    2.86
  DIRECTION P(+100 before -100)   1.51
  TIME ASYMMETRY (t_up - t_dn)    2.21
```

Causally observable volatility- and range-state **transitions** move the expected time-to-±100p by
**0.9 to 1.9 hours on a ~9.2-hour baseline (10–21%)**, with z up to 8.9, 6/6 years of sign consistency,
OOS sign-consistency on all five frozen phenomena, and no outlier dependence. The same states move the
**direction** probability by ±0.01 (|z| ≤ 1.2) — i.e. nothing.

**But the matched control is not clean:** session-stratified, all five effects are **sign-mixed**. The
pooled speed effects are materially confounded with *when* these states occur. That is the honest limit on
the finding and it is why I classify four of the five as `INFORMATION_ONLY`.

---

## 1 — DATA AND CONTROLS

```
  native governed M5, no synthesis: 354,669 bars, 2021-07-27 15:45Z .. 2026-07-27 17:55Z, UTC
  sha256 cbb6eebe1a189ebb · modal step 5min · gaps>60min 1,290 (weekends/holidays)
  DEV (<= 2024-06-30) 207,676 bars | OOS 146,993 bars
  cost convention carried (not applied to information tests): round-trip ~4.19 project pips
  COVERAGE CAVEAT on every finding: M5 is 2021-07+ only = ONE macro-era. No cross-era claim.
```

**POSITIVE CONTROL = PASS** (§16). Synthetic drift injected into the real series after a random 3% causal
state, full pipeline re-run:

| dose | P(+100 before −100) | base | lift | z |
|---|---|---|---|---|
| 0 p (null) | 0.5226 | 0.5191 | **+0.0035** | **+0.38** |
| 40 p | 0.5697 | 0.5230 | +0.0467 | +5.90 |
| 120 p | 0.5984 | 0.5533 | +0.0452 | +7.58 |

Monotone recovery, clean null. The engine is sensitive and does not fabricate.

**DEV/OOS discipline (§17):** all 80 tests were scored on **DEV only**. The top 5 were then written down and
frozen, and OOS was inspected **once**. No condition was modified after seeing OOS.

---

## 2 — SEARCH DISCIPLINE, AND A BUDGET BREACH I MUST DISCLOSE

I declared a budget of **60 tests**. I scored **80** — 20 states × 4 targets, because I added three
multi-time-scale (Branch H) states after declaring 17. **That is my own discipline breach, not a rounding
issue**, and I report it rather than quietly re-declaring the budget.

Consequence, applied: multiplicity is assessed against **m = 80**, not 60. Bonferroni at α = 0.05 requires
**|z| > 3.48**. All five frozen phenomena clear that on DEV (8.89, 8.60, 6.91, 5.43, 5.37). The one
non-timing candidate (V2-5's tail effect, z 2.86) does **not**.

---

## 3 — TOP 5 NEW PHENOMENA

All share: target **A1 = hours to the first ±100p touch**, baseline **≈ 9.2 h**; native M5; day-clustered SE.

### V2-1 — RANGE ALREADY EXPANDED → SLOWER  *(Branch D)*

| field | value |
|---|---|
| causal definition | 48-bar range width ÷ ATR14, percentile-ranked over the trailing 2000 bars, **> 0.80** |
| N (DEV) | 34,969 · 791 days |
| baseline → conditional | 8.91 h → **10.40 h** |
| effect | **+1.484 h (z +8.89)** — the largest effect in the whole scan |
| DEV → OOS | +1.484 → **+0.644 (z +4.12)** — same sign |
| year consistency | **6 / 6** (+1.49, +1.27, +2.12, +1.11, +0.62, +0.12) |
| overlap robustness | non-overlapping N=208: **+0.942 h (z +2.17)** — survives |
| outlier robustness | winsorised at p99: +1.049 h — unchanged |
| matched control (session) | AS −1.02 · LN −0.50 · **NY +1.75** · LT +0.94 — **MIXED** |
| direction / tail | B2 +0.012 (z +1.20) · G1 −0.001 (z −0.06) — nothing |
| interpretation | the move has already happened; realised range is large relative to current ATR, and the next 100p takes longer |

**Classification: `INFORMATION_ONLY`** — largest and most robust effect found, but session-confounded and
directionally empty.

### V2-2 — SUSTAINED LOW VOLATILITY → SLOWER  *(Branch C)*

ATR percentile < 0.20 both now and 24 bars ago. N = 13,389 (686 days). 9.10 h → **10.50 h**,
**+1.406 h (z +8.60)**. OOS +0.385 (z +1.98), same sign. **6/6 years.** Winsorised +0.660. Non-overlap N too
small. Session: AS +1.70 · **LN −2.75 · NY −3.34** · LT −0.10 — **strongly mixed**. Direction B2 +0.011
(z +0.82).

**Classification: `INFORMATION_ONLY`.** The session split is the most adverse of the five: the pooled
positive lift reverses inside London and New York.

### V2-3 — LOW → EXPANSION TRANSITION → FASTER  *(Branch C)*

ATR percentile < 0.20 twenty-four bars ago and > 0.50 now. N = 9,234 (664 days). 9.26 h → **8.07 h**,
**−1.190 h (z −6.91)**. OOS −0.454 (z −3.23), same sign. **6/6 years** (−1.15, −1.15, −1.19, −0.95, −0.60,
−0.18 — a clean monotone decay). Winsorised −1.149. Session: AS +0.02 · LN −0.06 · **NY −5.21 · LT −4.78**
— **effect lives entirely in NY/late**.

**Classification: `INFORMATION_ONLY`** — a genuine volatility-transition→speed effect, but it is an NY/late
phenomenon rather than a session-independent one.

### V2-4 — RANGE COILED (ATR-rich, range-poor) → FASTER  *(Branch D)*  **strongest new lead**

| field | value |
|---|---|
| causal definition | 48-bar range ÷ ATR14, percentile-ranked over 2000 bars, **< 0.20** — i.e. volatility is high relative to the range actually travelled |
| N (DEV) | 36,036 · 802 days |
| baseline → conditional | 9.38 h → **8.49 h**; **−0.894 h (z −5.43)** |
| DEV → OOS | −0.894 → **−0.553 (z −4.49)** — same sign, **strongest OOS z of the five** |
| year consistency | **6 / 6** (−0.94, −0.86, −1.01, −0.76, −0.65, −0.20) |
| overlap robustness | non-overlapping N=220: **−0.958 h (z −2.40)** — survives, magnitude *increases* |
| outlier robustness | winsorised: −0.752 h — unchanged |
| matched control | AS +0.45 · LN +0.17 · **NY −2.15 · LT −2.79** — mixed, but the two negative buckets are large |
| direction / tail | B2 −0.007 (z −0.66) · G1 +0.008 (z +0.72) — nothing |
| interpretation | price is coiled: ATR says the market can move, the realised 48-bar range says it hasn't. Energy without displacement resolves faster. |

**Classification: `STRATEGY_HYPOTHESIS_WORTH_TESTING`** — the only phenomenon that survives *both*
non-overlapping sampling *and* OOS at |z| > 2, with 6/6 years. **But as a horizon/timing parameter, not an
entry.**

### V2-5 — VOLATILITY EXTREME → NORMALISATION → SLOWER, WITH A FATTER TAIL  *(Branches C + G)*

ATR percentile > 0.90 twenty-four bars ago, < 0.60 now. N = 2,827 (400 days). 9.17 h → **11.10 h**,
**+1.929 h (z +5.37)** — the largest *magnitude* in hours. OOS +0.520 (z +2.26), same sign. **6/6 years.**
Non-overlap N too small.

**Uniquely, it is the only frozen state with a non-timing signal:** P(MFE ≥ 300p) **+0.053 (z +2.86)**, and
median MFE 158p vs 140p baseline. Slower to the first 100p, but a fatter right tail when it does move.

**Classification: `INFORMATION_ONLY`** — the tail effect does not clear Bonferroni at m = 80 (needs 3.48).

### Best non-timing result in the entire scan, for the record

`M5 failed-expansion-up × H1 high-volatility` → time-asymmetry (t_up − t_dn) **−2.50 h (z −2.21)**, N = 237.
That is the strongest *directional-flavoured* result across 80 tests, and it is weak and small-N.
**Classification: `NOISE`.**

---

## 4 — WHAT THE MATCHED CONTROL SHOWS (§14)

This is the most important qualification in the report. Re-measuring each frozen effect **within** session
buckets:

| phenomenon | AS | LN | NY | LT | verdict |
|---|---|---|---|---|---|
| V2-1 expanded → slower | −1.02 | −0.50 | +1.75 | +0.94 | mixed |
| V2-2 sustained low → slower | +1.70 | −2.75 | −3.34 | −0.10 | mixed |
| V2-3 low→expansion → faster | +0.02 | −0.06 | −5.21 | −4.78 | mixed |
| V2-4 coiled → faster | +0.45 | +0.17 | −2.15 | −2.79 | mixed |
| V2-5 extreme→normalise → slower | −2.97 | −2.01 | +0.86 | −1.68 | mixed |

**None of the five is session-independent.** The pooled effects are partly a statement about the
time-of-day composition of these states. Two readings are defensible and I give both: (a) the effects are
genuine but *conditional on session*, concentrated in NY/late for the "faster" states; (b) part of the
pooled magnitude is a composition artifact. **I cannot separate these without treating session as a
hypothesis, which §2 forbids in this mandate.** This is the single largest open question I am handing back.

---

## 5 — BRANCH RANKING (§21)

| rank | branch | evidence | value |
|---|---|---|---|
| 1 | **VOLATILITY_TRANSITIONS (C)** | z 8.60 / 6.91 / 5.37, 6/6 years, OOS-consistent | **highest** |
| 2 | **RANGE_STATE (D)** | z 8.89 / 5.43, only branch surviving non-overlap twice | **highest** |
| 3 | **TIME_TO_EVENT (A)** | the *target representation* that made C and D visible at all | **enabling** |
| 4 | REGIME_CONDITIONAL (F) | F3 z −4.67, but ≈ C1 conditioned on trend — largely duplicate | moderate |
| 5 | MULTI_TIME_SCALE (H) | H2 duplicates D1; H1 is the best directional result but weak | low-moderate |
| 6 | SEQUENTIAL_TRANSITIONS (E) | best z −4.15 (E3), mostly duplicating C-states | low |
| 7 | RARE_EVENT_SKEW (G) | only V2-5 at z +2.86; fails Bonferroni | low |
| 8 | PAYOFF_GEOMETRY (B) | **no conditional effect at all** (best |z| 1.51) | lowest, conditionally |

```
MOST_PROMISING_UNDEREXPLORED_BRANCH = TIME_TO_EVENT / HAZARD
```

**WHY:** it is not that timing states are more numerous — it is that **timing is the only target
representation in which this instrument shows large, year-consistent, OOS-surviving conditional structure**.
Every one of the twelve strongest results across eight branches landed on the speed target; the direction
target produced nothing above |z| 1.51 in eighty attempts. Branch B (payoff geometry) ranks last
*conditionally* while V1 showed its *unconditional* form is the program's biggest structural finding — the
geometry is a property of the instrument, not something states modulate.

---

## 6 — SPECIAL CEO QUESTIONS (§22)

### If L1 London did not exist, what would your strongest new Strategy-2 lead be?

**V2-4, range COILED → faster.** It is the only phenomenon that clears every hurdle I can apply:
DEV z −5.43 → OOS z −4.49 (same sign, the strongest OOS of the five), 6/6 years, non-overlapping sample
**strengthens** the effect (−0.958 h, z −2.40), winsorising changes nothing, and N is large (36,036 over
802 days).

**Its honest limitation:** it predicts *when*, not *which way* (B2 lift −0.007, z −0.66). It cannot be a
standalone entry. Its minimal trade interpretation is a **horizon/time-stop modifier**: when the 48-bar
range is coiled relative to ATR, an existing directional entry should expect its ±100p resolution ~10%
sooner, so a shorter time-stop is appropriate; when the range has already expanded (V2-1), a longer one is.
I have **not** built, optimised or tested that.

### Where is Strategy #2 more likely to come from? (ranked by the evidence in this scan)

1. **TIMING** — the only place large, robust conditional structure appears. z up to 8.9.
2. **PATH GEOMETRY** — V1's unconditional 2:1 penalty (z −3.29) remains the largest single actionable fact
   the program has; not modulated by states, but it conditions every strategy the lab builds.
3. **VOLATILITY TRANSITION** — real, but expresses itself through timing, not direction.
4. **REGIME CONDITIONALITY** — useful as a stratifier; produced no independent effect here.
5. **RARE POSITIVE SKEW** — one candidate (V2-5), fails multiplicity.
6. **EVENT-REVEALED RESPONSE** — V1 found the 48-bar breakout frame null; V2's failed-expansion variants add
   nothing. **Two independent scans have now failed to find it.**
7. **DIRECTION PREDICTION** — last. Eighty tests, best |z| = 1.51. Nothing.

---

## 7 — FINAL REPORT BLOCK (§25)

```
INDEPENDENT_STATISTICAL_ALPHA_SCOUT_V2_COMPLETE = YES
POSITIVE_CONTROL                                = PASS

BRANCHES_TESTED          = 8 (A time-to-event, B payoff geometry, C vol transitions, D range state,
                              E sequential transitions, F regime conditionality, G rare-event skew,
                              H multi-time-scale)
TOTAL_STATISTICAL_TESTS  = 80   (declared budget 60 -- OVERRUN DISCLOSED, multiplicity assessed at m=80)

STATISTICALLY_MEANINGFUL_NEW_PHENOMENA = 5   (all clear Bonferroni at m=80 on DEV and hold OOS in sign)
STRATEGY_HYPOTHESES_WORTH_TESTING      = 1   (V2-4)

TOP_1 = V2-4 range COILED (w48/ATR pct<.2) -> time-to-+-100p FASTER by 0.89h
        DEV z -5.43 / OOS z -4.49 / 6-of-6 years / non-overlap SURVIVES   STRATEGY_HYPOTHESIS_WORTH_TESTING
TOP_2 = V2-1 range EXPANDED (pct>.8) -> SLOWER by 1.48h   z +8.89 / OOS +4.12 / 6-of-6 / non-overlap survives
                                                                            INFORMATION_ONLY
TOP_3 = V2-3 low->EXPANSION transition -> FASTER by 1.19h  z -6.91 / OOS -3.23 / 6-of-6   INFORMATION_ONLY
TOP_4 = V2-2 sustained LOW vol -> SLOWER by 1.41h          z +8.60 / OOS +1.98 / 6-of-6   INFORMATION_ONLY
TOP_5 = V2-5 extreme->NORMALISE -> SLOWER by 1.93h + fatter tail (P(MFE>=300p) +0.053)
                                                           z +5.37 / OOS +2.26 / 6-of-6   INFORMATION_ONLY

STRONGEST_NEW_LEAD                   = V2-4 (range coiled -> faster resolution)
MOST_PROMISING_UNDEREXPLORED_BRANCH  = TIME_TO_EVENT / HAZARD
SEARCH_REPRESENTATION_BLIND_SPOTS_FOUND = YES
   (1) the program has never used TIME as a target -- it is where all the structure is;
   (2) direction targets are near-empty: 80 tests, best |z| 1.51;
   (3) the "event-revealed response" frame is now null in two independent scans.

READY_FOR_INDEPENDENT_REPLICATION    = YES  (V2-4 only)
NEXT_AUTHORIZED_ACTION               = NONE -- CEO DECISION REQUIRED
```

---

## 8 — LIMITATIONS

1. **Session confound unresolved (§4).** All five effects are session-mixed. Separating them requires
   treating session as a hypothesis, which this mandate excludes. **This is the first thing to settle.**
2. **Budget overrun** 60 → 80, disclosed; multiplicity assessed at m = 80.
3. **One macro-era.** Native M5 is 2021-07+. Year consistency is the strongest available check.
4. **Overlap** untestable for V2-2, V2-3, V2-5 (non-overlapping N too small). Only V2-1 and V2-4 are proven
   overlap-robust.
5. **OOS effects attenuate** roughly by half versus DEV on all five. Signs hold; magnitudes do not.
6. **No costs applied.** These are information findings; none has been shown to survive transaction costs,
   and a timing signal with no directional content cannot be costed in isolation.
7. **I did not validate any of this**, and I must not — a different owner is required.

---

## 9 — ARTIFACTS

`statistician/scout_v2/` — `v2_targets.py` (preregistration, data audit, targets, positive control),
`v2_scan.py` (80-test DEV scan), `v2_oos.py` (frozen top-5, OOS, controls, robustness),
`v2_dev_scan.json`, `v2_oos.json`.

**Environment:** Python 3.14 · native M5 `cbb6eebe1a189ebb`, 354,669 bars · horizon 288 M5 bars ·
PIP = 0.10 USD · DEV ≤ 2024-06-30.

---

*Statistician division — independent statistical discovery. Nothing here is validated, and no phenomenon may
be treated as a strategy without independent validation by another owner.*
