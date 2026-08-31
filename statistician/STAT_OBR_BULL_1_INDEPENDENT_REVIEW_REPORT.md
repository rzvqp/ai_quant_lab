# STAT — INDEPENDENT STATISTICAL REVIEW: OBR-BULL-1 (`ORDER_BLOCK_RETEST_FACTORY_V1`)

**Mandate:** CEO independent statistical validation of `OBR-BULL-1`
**Division:** Statistician (independent statistical validation)
**Date:** 2026-08-31
**Alpha commit:** `40657d7` (merge) — substantive content at **`427a418`**, `SURVIVED = 1`

**OBR-BULL-1 was not modified, retuned, promoted, or sent anywhere.**

---

## 0 — HEADLINE

Every Alpha figure reproduces **exactly**. The candidate nonetheless fails, on a single mechanical defect
that §2 of this mandate told me to hunt for:

> **`ob_contrast.limit_fill` decides whether a resting limit order was filled using the bar's CLOSE.**
> For a long it evaluates, on the same bar `k`: `if c[k] < block_low: return None` **before**
> `if l[k] <= level: return k`. A resting limit BUY at `block_high` fills the instant
> `low[k] <= block_high`, whatever the bar does afterwards. Conditioning the *fill* on the *close* is
> end-of-bar information.

Correcting only that ordering — no parameter, level, stop, target, session or cost changed:

| | frozen (as tested) | causal limit semantics |
|---|---|---|
| N | 2,122 | 2,486 |
| **net-R / trade** | **+0.1536** | **−0.0673** |
| WR | 0.482 | 0.412 |
| PF | 1.86 | 1.40 |
| era D / C / O | +0.123 / +0.166 / +0.206 | −0.092 / −0.081 / +0.003 |
| DEV / OOS | +0.123 / +0.186 | −0.093 / −0.042 |
| **years positive** | **13 / 16** | **5 / 16** |
| 95% CI (episode-clustered) | [+0.083, +0.225] | **[−0.132, −0.003]** |

**The 364 trades the frozen semantics silently drops have mean net-R = −1.3552 and a win rate of 0.005
(2 winners in 364).** The construction excludes near-certain losers by looking at where the bar closed.

This is the direct analogue of the intrabar-selection artifact Alpha itself caught and correctly discarded
for retest *depth*. The same defect class survived in the *fill* function.

---

## 1 — CANDIDATE SPEC FREEZE (§1)

```
CANDIDATE_SPEC_FROZEN = YES
SPEC_HASH = e32e04f2361e5cce52de4c0b2fe35db31d6287481e51b79090582018194f55a2
```

| file | sha256 (16) |
|---|---|
| `ob_core.py` | `a2acf03bbd0c9718` |
| `ob_candidate.py` | `a3c66bd56dca21d1` |
| `ob_contrast.py` | `b91ca4f94854fcfa` |
| `ob_falsify.py` | `c22db5615103890b` |
| `ob_m5.py` | `d8b65424cbd912ca` |
| `htf_core.py` | `fc0ca6e96ee0f4d7` |

Frozen parameters: `K=20` causal swing, `DL=10` origin lookback, `RETEST_WIN=192`, `FLOOR_ATR=0.1`,
`disp_min=1.5`, `tgtR=2.0`, sessions `LN+NY` (08:00–20:00 UTC), LONG only, entry = resting limit BUY at
frozen `block_high`, stop = `block_low − 0.1·ATR` floored to risk ≥ 0.5·ATR, `COST_PRICE = 0.419`,
`PIP = 0.10`. Data: M15 OANDA XAUUSD, 355,696 bars, 2011-07-26 → 2026-07-27.

**`DEFINITION_AMBIGUITIES`:** one, and it is the decisive one — the specification says "resting limit BUY at
frozen block high", which has an unambiguous market meaning (fill on touch). The implementation adds an
unstated close-conditioned veto. The prose and the code disagree, and the code is more favourable.

---

## 2 — ANTI-LOOKAHEAD AUDIT (§2)

| check | result |
|---|---|
| `ORDER_BLOCK_KNOWN_BEFORE_RETEST` | **YES** — origin is the last bearish candle in `[i−10, i−1]` |
| `BOS_KNOWN_BEFORE_RETEST` | **YES** — `c[i] > swH[i]` and `c[i−1] ≤ swH[i−1]` |
| `BLOCK_COORDINATES_FROZEN` | **YES** — coords taken at bar `oj < i`, never updated |
| `SWING_DEFINITION_CAUSAL` | **YES** — `rolling(20).max().shift(1)` |
| `NO_CENTERED_PIVOT_LOOKAHEAD` | **YES** |
| `NO_FUTURE_H1/H4_INFORMATION` | **YES** — M15-only cell |
| `FIRST_RETEST_CAUSAL` | **YES** — scan strictly `k > i` |
| `ENTRY_KNOWN_BEFORE_OUTCOME` | level yes — **but the FILL DECISION is not** (below) |
| `STOP_KNOWN_BEFORE_OUTCOME` | **YES** |
| `TARGET_KNOWN_BEFORE_OUTCOME` | **YES** |
| **`FILL_DECISION_CAUSAL`** | **NO — FAIL** |

### 2.1 The defect, measured

```
  frozen fill semantics : N=2122  ie= 954  net=+0.1536  WR=0.482  PF=1.86
  causal fill semantics : N=2486  ie=1019  net=-0.0673  WR=0.412  PF=1.40
  delta: +364 trades, -0.2209 R/trade
  the 364 dropped trades: mean net-R = -1.3552, win rate 0.005
```

The mechanism is transparent. A bar that dips to `block_high` and then closes below `block_low` is a bar in
which price sliced straight through the block. A real resting limit is filled near the top of that collapse
and is stopped out at ≈ −1R (−1.36R after cost). The engine records no trade at all.

**`ANTI_LOOKAHEAD = FAIL`.** Every other causality check passes; this one is decisive on its own.

---

## 3 — DATA / EVENT POPULATION (§3) — **`DATA_INTEGRITY = PASS`**

```
  causal OB events  bull 8,985  + bear 8,447 = 17,432   (Alpha census: 17,432)   MATCH
  fresh first retests bull 6,796 + bear 6,341 = 13,137  (Alpha census: 13,137)   MATCH
  OBR-BULL-1 eligible (disp>=1.5, LN+NY, 2R): N = 2,122   independent episodes = 954   MATCH
```

Alpha's census is exact; my earlier apparent discrepancy was direction scope (Alpha's totals are both
directions). Episode clustering: 2,122 trades over **954** independent episodes ⇒ ~2.2 trades per episode.
All uncertainty below uses an **episode-clustered** standard error, not nominal N.

---

## 4 — BASELINE REPRODUCTION (§4) — **EXACT**

| metric | reproduced | Alpha | |
|---|---|---|---|
| N | 2,122 | 2,122 | MATCH |
| independent episodes | 954 | 954 | MATCH |
| net-R / trade | **+0.1536** | +0.154 | MATCH |
| WR | 0.4816 | 0.482 | MATCH |
| PF | 1.8591 | 1.86 | MATCH |
| best-trade-removed | +0.1527 | +0.153 | MATCH |
| gross-R | +0.4449 | — | new |
| median R | −1.0454 | — | new |
| maxDD | −49.18 R | — | new |
| median risk | 17.3 project pips | ~20 | close |
| median cost_R | 0.2427 | 0.24 | MATCH |

**Alpha's arithmetic is exact on every published figure.** Nothing in this report questions the computation.

---

## 5 — COST / EXECUTION ACCOUNTING (§5)

Verified from `ob_core.retest_outcome` and `htf_core`: stop-wins-same-bar-ties (`if hit_s and hit_t:
res = −1.0`), round-trip cost charged once as `COST_PRICE / risk`, horizon exit at close, R denominator =
`|entry − stop|` after the 0.5·ATR execution floor. **These are correct and conservative.**

The single execution defect is the fill decision (§2). Cost stress:

```
  FROZEN : +0.00R -> +0.1536 · +0.05 -> +0.1036 · +0.10 -> +0.0536 · +0.15 -> +0.0036 · +0.20 -> -0.0464
           expectancy crosses ZERO at +0.1536R additional cost
  CAUSAL : already negative at +0.00R
```

Alpha's disclosure that "+0.15R extra stress brings it to ~break-even" is **confirmed exactly** (+0.0036R).

---

## 6 — CROSS-ERA AND YEAR ROBUSTNESS (§6)

| | frozen | causal |
|---|---|---|
| era D (≤2018) | +0.123 (n1084) | **−0.092 (n1260)** |
| era C (2019–22) | +0.166 (n540) | **−0.081 (n647)** |
| era O (2023+) | +0.206 (n498) | +0.003 (n579) |
| `SIGN_STABLE_ACROSS_ERAS` | **YES** | **NO** |
| years positive | **13 / 16** (neg 2014, 2018, 2019) | **5 / 16** |
| best year share of total | 2024 = 14.6% | — |
| top-3 years share | 39.4% | — |

Under frozen semantics the cross-era claim is **verified exactly**, including the 13/16 and the specific
negative years — genuinely not an era-beta effect, and the year concentration is mild (best year 14.6%).
Under causal semantics it inverts: only 2011, 2016, 2022, 2024, 2025 are positive.

---

## 7 — DEV / OOS (§7)

```
  FROZEN : DEV(<=2018) +0.1231 (n1084)   OOS(2019+) +0.1855 (n1038)     matches Alpha (+0.123 / +0.185)
  CAUSAL : DEV          -0.0925 (n1260)   OOS        -0.0415 (n1226)
```

`OOS_INTEGRITY = PASS`. The split is chronological and pre-declared; the candidate definition (disp ≥ 1.5,
LN+NY, 2R) is fixed in `ob_candidate.py` independently of the OOS slice, and the factory's own register
shows the cell grid was declared before scoring. I found no evidence of OOS re-querying or of thresholds
selected from OOS.

---

## 8 — DISPLACEMENT DOSE-RESPONSE (§8) — `DISPLACEMENT_DOSE_RESPONSE_REPRODUCED = YES`

| disp ≥ | Alpha | frozen (mine) | **causal (mine)** |
|---|---|---|---|
| 1.00 | +0.099 | **+0.0991** | −0.0878 |
| 1.25 | +0.112 | **+0.1121** | −0.0896 |
| 1.50 | +0.154 | **+0.1536** | −0.0673 |
| 1.75 | +0.184 | **+0.1840** | −0.0468 |
| 2.00 | +0.226 | **+0.2264** | −0.0243 |
| 2.50 | +0.239 | **+0.2392** | −0.0285 |

Reproduced to three decimals at every bucket. **A genuinely interesting nuance: the monotone gradient
survives the causality correction — it simply sits entirely below zero.** Higher displacement means
*less bad*, not profitable. So the dose-response is **not** the artifact; the fill semantics shift the whole
curve by roughly +0.22R. The gradient is real evidence of impulse-quality information; it is not evidence of
a tradeable edge. No threshold was optimized; the frozen candidate remains ≥ 1.5 ATR.

---

## 9 — MATCHED CONTROLS, INCLUDING THE STOP-MATCHED CONTROL (§9, major gate)

All controls run on the **same events, same fill semantics, same target, same session filter**.

**Frozen semantics**

| arm | N | net-R | OB incremental |
|---|---|---|---|
| OB level (OBR-BULL-1) | 2,122 | +0.1536 | — |
| CONTROL_C generic pullback | 2,389 | −0.1048 | **+0.2584** |
| CONTROL_SHIFT height-matched | 1,265 | +0.4146 | **−0.2611** |
| **CONTROL_STOPMATCHED (risk = OB risk)** | 2,389 | −0.0856 | **+0.2391** |

**Causal semantics**

| arm | N | net-R | OB incremental |
|---|---|---|---|
| OB level (OBR-BULL-1) | 2,486 | −0.0673 | — |
| CONTROL_C generic pullback | 2,466 | −0.1415 | +0.0742 |
| CONTROL_SHIFT height-matched | 2,378 | −0.1569 | +0.0895 |
| **CONTROL_STOPMATCHED (risk = OB risk)** | 2,466 | −0.1249 | **+0.0575** |

**`OB_INCREMENTAL_INFORMATION_FOUND = YES` — and it is not an artifact of stop placement.**
The stop-matched control (my construction, forcing the control's risk equal to the OB trade's risk at the
same level geometry) still leaves the OB level ahead by **+0.239 frozen / +0.058 causal**. This directly
answers the question Alpha itself raised in its caveat 3 and could not answer.

**But the increment sits on a negative base.** Under causal fills the OB level is better than the controls
and still loses money. Level information exists; a tradeable strategy does not.

*One divergence from Alpha, flagged as mine not theirs:* my `CONTROL_SHIFT` (level shifted down by one block
height, stop shifted correspondingly) **beats** the OB under frozen semantics by 0.26R, where Alpha reports
the OB beating its own CONTROL_SHIFT by +0.21R. These are different constructions and I do not present this
as contradicting Alpha's number — only as evidence that the height-matched comparison is construction-sensitive
and should not be leaned on.

---

## 10 — OUTLIER / DEPENDENCE ROBUSTNESS (§10) — `OUTLIER_ROBUST = YES`

```
  FROZEN : N=2122 episodes=954  net=+0.1536  clustered SE=0.0362  95% CI [+0.0826, +0.2246]
           drop-best-1% (22) -> +0.1347 (Alpha claims +0.135  MATCH)   drop-best-trade -> +0.1527
  CAUSAL : N=2486 episodes=1019 net=-0.0673 clustered SE=0.0329  95% CI [-0.1319, -0.0028]
           drop-best-1% -> -0.0879   drop-best-trade -> -0.0681
```

The candidate is genuinely **not** outlier-driven under either semantics — creditable, and Alpha's
drop-best-1% figure reproduces exactly. Note that the **causal 95% CI excludes zero on the negative side**:
the corrected candidate is not merely unprofitable, it is significantly so at the episode-clustered level.

---

## 11 — SESSION ROBUSTNESS (§11)

```
  FROZEN : LN N=984 net=+0.1194   NY N=1138 net=+0.1832
  CAUSAL : LN N=1146 net=-0.0933  NY N=1340 net=-0.0451
```

Not produced by one narrow clock slice — both sessions carry the same sign under both semantics. No session
boundary was optimized.

---

## 12 — THRESHOLD NEIGHBOURHOOD (§12) — `THRESHOLD_SURFACE_STABLE = YES`

The displacement surface (§8) is smooth and monotone at every pre-existing bucket under both semantics.
The frozen 1.5 ATR point sits on a stable surface, not a spike. No new threshold was selected.

---

## 13 — M5 EXTENSION (§13) — `M5_EXTENSION_VALID = INCONCLUSIVE`

`ob_m5.py` line 22 calls **the same `limit_fill`**. The M5 refinement therefore operates on the **same
non-causally-filtered entry population** as the baseline and inherits the identical defect. Its reported
improvement (+0.23 → +0.93R) cannot be assessed while its entry set is contaminated, and it is moot for
promotion while the baseline fails. **I did not evaluate it further, and no M5 result is used anywhere in
this verdict.** Per the mandate, M5 failure does not invalidate a valid baseline — but here the baseline is
the thing that fails, and M5 inherits its defect rather than curing it.

---

## 14 — MULTIPLE TESTING / DISCOVERY BIAS (§14) — `MULTIPLE_TESTING_CONCERN = MEDIUM`

From Alpha's own register: **20 raw cells → 6 after dedup → 1 survivor**, inside a factory that follows
**6 prior failed frontiers**, within a program of many dozens of hypotheses. Alpha discloses all of this
openly and does not present OBR-BULL-1 as hypothesis #1 — creditable.

I record explicitly that **multiplicity is not the binding constraint**. The frozen result
(+0.154R, clustered SE 0.036, z ≈ 4.2) would survive a conservative adjustment over even a few hundred
tests. Had the fill been causal, the multiple-testing burden would not have been what killed it.
**Causality is.**

---

## 15 — PRACTICAL MAGNITUDE (§15)

Median risk = **17.3 project pips**; median cost_R = 0.243.

```
  FROZEN : +0.1536 R  x  17.3 pips  =  +2.66 project pips per trade
  CAUSAL : -0.0673 R  x  17.3 pips  =  -1.16 project pips per trade
```

Even at face value the frozen edge is ~2.7 pips per trade against a round-trip cost of 4.19 pips — real but
thin, exactly as Alpha's caveat 1 says.

---

## 16 — REQUIRED VERDICT BLOCK

```
STATISTICIAN_OBR_BULL_1_REVIEW_COMPLETE = YES

CANDIDATE_SPEC_FROZEN            = YES   (SPEC_HASH e32e04f2361e5cce…)
ANTI_LOOKAHEAD                   = FAIL  (fill decision conditioned on the bar's close)
DATA_INTEGRITY                   = PASS

N_REPRODUCED                     = 2122  (causal semantics: 2486)
INDEPENDENT_EPISODES             = 954   (causal: 1019)

NET_R_PER_TRADE                  = +0.1536 frozen  /  -0.0673 causal
PF                               = 1.86 frozen     /  1.40 causal
WR                               = 0.482 frozen    /  0.412 causal
MAX_DD                           = -49.18 R frozen

DEV_NET_R                        = +0.1231 frozen  /  -0.0925 causal
OOS_NET_R                        = +0.1855 frozen  /  -0.0415 causal
OOS_INTEGRITY                    = PASS

CROSS_ERA_STABLE                 = YES frozen  /  NO causal
YEAR_ROBUSTNESS                  = PASS frozen (13/16)  /  FAIL causal (5/16)

DISPLACEMENT_DOSE_RESPONSE_REPRODUCED = YES (exact; gradient survives correction, level does not)

OB_INCREMENTAL_INFORMATION_FOUND = YES (+0.058R causal, stop-matched)
STOP_MATCHED_CONTROL_SURVIVES    = YES

OUTLIER_ROBUST                   = YES
COST_ROBUST                      = NO   (frozen crosses zero at +0.154R; causal already negative)
MULTIPLE_TESTING_CONCERN         = MEDIUM  (explicitly NOT the binding constraint)

M5_EXTENSION_VALID               = INCONCLUSIVE (inherits the same limit_fill defect)

BLOCKING_FINDINGS:
  B1  ob_contrast.limit_fill conditions the limit-order FILL on the bar's CLOSE, for every trade.
      Correcting only the ordering: net-R +0.1536 -> -0.0673; years positive 13/16 -> 5/16;
      eras D/C/O +0.123/+0.166/+0.206 -> -0.092/-0.081/+0.003; causal 95% CI [-0.132, -0.003].
      The 364 excluded trades average -1.3552 R with a 0.005 win rate.
  B2  ob_m5.py reuses the same limit_fill, so the M5 refinement inherits B1.

NONBLOCKING_FINDINGS:
  N1  Spec prose ("resting limit BUY at frozen block high") and implementation disagree; the code is the
      more favourable of the two readings.
  N2  Displacement dose-response is genuine as a GRADIENT but sits entirely below zero once fills are causal.
  N3  My height-matched CONTROL_SHIFT construction beats the OB under frozen fills (opposite sign to Alpha's
      own CONTROL_SHIFT); different constructions, reported as a caution about that comparison, not as a
      contradiction.
  N4  Cost head-room is thin even at face value: +2.66 project pips per trade against a 4.19-pip round trip.

STATISTICAL_VERDICT              = FAIL
READY_FOR_RED_TEAM               = NO
NEXT_AUTHORIZED_ACTION           = NONE — CEO DECISION REQUIRED
```

---

## 17 — WHAT IS GENUINELY CREDITABLE

Stated plainly, because a fair review reports both directions:

- **Every published figure reproduces exactly** — N, episodes, net-R, WR, PF, drop-best-1%, all six
  dose-response buckets, era D/C/O, DEV/OOS, 13/16 years, and the exact +0.15R break-even stress point.
- The census (17,432 OBs / 13,137 retests) is **exactly right**.
- The order-block construction is **genuinely causal** in every respect except the fill: causal swing,
  close-BOS, frozen coordinates, no centered pivots, strictly forward retest scan, stop-wins-ties.
- Alpha **caught and discarded** the analogous intrabar artifact for retest depth, and said so prominently.
- Alpha **disclosed** the cost thinness, the control-disentanglement gap, and the M5 window limitation, and
  explicitly asked for the stop-matched control — which I ran, and which the OB level **passes**.
- Alpha did **not** self-promote and performed no handoff.

**The order-block level does carry incremental information over risk-matched controls. That finding
survives and is worth keeping.** What does not survive is the claim that it constitutes a positive-expectancy
strategy.

---

## 18 — LIMITATIONS

1. My causal fill rule is one defensible convention (fill on touch; invalidation only on bars strictly
   before the fill). It is the standard meaning of a resting limit order, and it is the convention the
   spec's own prose implies.
2. `CONTROL_SHIFT` and `CONTROL_STOPMATCHED` are my constructions; Alpha's controls differ in detail.
3. Bear mirror (`OBR-BEAR-1`) was not evaluated — out of scope.
4. M5 not assessed beyond confirming it inherits B1.
5. **Nothing was modified, repaired or retuned.** Any corrected version is a **new candidate identity**
   owned by Alpha under a new mandate and must not inherit OBR-BULL-1's evidence.

---

*Statistician division — independent statistical validation. Verdicts are scoped strictly to the evidence
examined and are not transferable to adjacent claims.*
