# STAT — INDEPENDENT VALIDATION OF COMP-CONT-L-rr2

**Mandate ID:** `STAT-COMP-CONT-L-RR2-INDEPENDENT-VALIDATION-001`
**Division:** Statistician (independent statistical validation)
**Date:** 2026-08-23
**Subject:** Alpha frozen candidate `COMP-CONT-L-rr2`, freeze commit `4082c5c`, status `FROZEN_PENDING_INDEPENDENT_VALIDATION`

**Scope directives honoured:** `VALIDATE_EXACT_FROZEN_COMP_CONT_L_RR2` · `INDEPENDENTLY_RECONSTRUCT` ·
`DO_NOT_TRUST_ALPHA_SUMMARY` · `DO_NOT_RETUNE` · `DO_NOT_REPAIR` · `AUDIT_D1_CAUSALITY_EXPLICITLY` ·
`PRESERVE_DATA_FIREWALL` · `VERIFY_EXECUTION_REALISM` · `USE_RATIFIED_COSTS` · `TEST_CROSS_ERA` ·
`TEST_DISC_CONF` · `TEST_TAIL_DEPENDENCE` · `TEST_DRAWDOWN` · `TEST_NEIGHBOR_STABILITY` ·
`TEST_S5_INDEPENDENCE` · `PRESERVE_TRUE_MULTIPLICITY`

**Nothing was modified.** No strategy parameter, rule, stop, target, filter, cost or population was changed.

---

## 0 — FINAL VERDICT

```
COMP_CONT_L_RR2_INDEPENDENT_VALIDATION_FAIL
```

**Not BLOCKED.** The identity reproduced exactly, the D1 causality is clean, and authorized cross-era evidence
was available. The candidate was fully testable, was tested, and did not survive.

**Primary reason — cross-era sign reversal on amply-populated authorized data.** Applying the frozen rule
unchanged to the lab's own governance-proven b0/b1 corpus:

| population | N | avgR (STRESS) | PF | best-10%-rem |
|---|---|---|---|---|
| **DEV 2021–2023** (selection) | 53 | **+0.443** | 1.94 | +0.246 |
| CALIB 2024 | 24 | +0.223 | 1.47 | **−0.030** |
| **b0 2011–2013** | 41 | **−0.410** | 0.45 | −0.744 |
| **b1 2016–2018** | 76 | **−0.060** | 0.91 | −0.301 |
| **b0+b1 pooled** | **117** | **−0.183** | 0.73 | −0.431 |

The contradicting sample (**N = 117**) is **2.2× larger** than the supporting one (N = 53). The lab's own
`ELIM:SIGN_REVERSAL` rule — *one era > 0 and another < −0.03, both with N ≥ 25* — **triggers**.

Two secondary findings are recorded but are **not** the basis of the verdict: a knife-edge `W` neighbourhood
(§11) and an unreported negative CALIB tail metric (§9).

---

## 1 — EXACT FROZEN IDENTITY (§1) — reconstructed mechanically

| field | value | source |
|---|---|---|
| Strategy ID | `COMP-CONT-L-rr2` | `COMP_CONT_L_STRATEGY_SPEC.md` |
| Side / class | LONG only · `REGIME_SPECIFIC_ROBUST_CANDIDATE` (D1-uptrend-only) | spec |
| Edge/entry TF · context TF | H4 · D1 | spec + code |
| Freeze commit | **`4082c5c`** | `git log` |
| Implementation | `frontier5_compcont.py` + `swing_base.py` | code |
| Implementation fingerprint | `c60357cb61f1ee3798d6d2b48c2729a6ac65277aa77f8f3b5873dba762204f95` | **reproduced** = `sha256(frontier5 ‖ swing_base)` |
| Config fingerprint | `3ceb5cd9ce7266a37ff5fdfa3a4811fb72110193db8875ca4fabfae341dad1ee` | **reproduced** = `sha256(json(config, sort_keys))` |
| Ledger fingerprint | `98a8b906dbd9e0f6e469cc02d35fe4a01c07b5d20d0532b77f46c6aefb030ae8` | **reproduced** = `sha256(json(ledger, sort_keys))` |
| Event | H4 compression: `atr < atr_ma(30)` **and** `box_range < box_ma(50)`, `W = 20`, both shifted | code |
| Context | last **completed** D1 bar, `EMA20 > EMA50` | code |
| Dedup | first compression bar per `cooldown = 20`-bar window | `sb.dedup_events` |
| Entry | `open[i+1]` — next H4 bar open | `sb.simulate` |
| Stop | `box_low[i]` (contraction floor); `risk = entry − stop` | code |
| Target / horizon | `entry + 2.0·risk`; max `H = 42` H4 bars | code |
| Cost | `AI_TRADER_SHADOW_COST_MODEL` — GROSS 0.00 / BASE 0.05 / **STRESS 0.24** round-trip USD; TICK 0.01 | `swing_base.COST` |
| Population | gated native M5 → H4; DEV 2021-07-27 → 2023-12-29; CALIB 2024-01-01 → 2024-06-20 | `m5_data` |
| Loader | `edge_research._common.load('M5', PRE_HOLDOUT_SPLIT_ID, RESEARCH_HOLDOUT_CUTOFF_UTC)` — no `read_csv` on `data/market` | code |

**All three published fingerprints reproduce exactly.** Identity is fully reconstructible from repository
artifacts alone.

---

## 2 — FREEZE INTEGRITY (§2) — **PASS, no drift**

`git diff 4082c5c..HEAD` is **empty** for `frontier5_compcont.py`, `swing_base.py` and
`COMP_CONT_L_STRATEGY_SPEC.md`. No parameter, entry rule, stop, target or context filter changed since the
freeze. The cached frames (`__swing_cache__/*.parquet`) were checked against a fresh `build_frames(use_cache=False)`
rebuild: **identical OHLC/time on H4 and D1** — no silent data-population substitution.

---

## 3 — D1 CAUSALITY DETERMINATION (§3) — **`D1_CAUSALITY_SAFE_VERIFIED`**

This is the defect class that blocked `H4-bo-raw-S`. It does **not** apply here, and I verified that
mechanically rather than reading the spec's claim.

`swing_base.align_context` attaches higher-TF columns by
`searchsorted(hi.close_time, lo.time, 'right') − 1` — the last D1 bar whose **close_time ≤ the H4 bar's
open time**. Column semantics were confirmed from `m5_data.aggregate` / `swing_base._agg_d1`:
`time` = bucket-start epoch, `close_time` = last M5 epoch in the bucket.

Measured over all 3,369 alignable H4 bars:

```
  causal margin (H4 open − D1 context close_time):
    min = +0.08h (= exactly 300s)   p1 = +0.08h   median = +12.08h   max = +6214h
    NEGATIVE margins (context from the future) : 0
    ZERO margins                               : 0
    margins < 300s                             : 0
    => strictly causal at every H4 bar: TRUE
```

Contrast with the known legacy defect (`merge_asof` on bar-**open** stamps, as in `econ_campaign.py`):

```
  legacy margin: min = -23.92h   median = -12.92h   NEGATIVE = 3312 / 3375 = 98.1%
  bars where the causal flag differs from the legacy flag: 89 / 3377 = 2.635%
```

The defect would have been **material** (2.6% of bars) had it been present. It is not. The tightest case
(+300s) is the 23:55 → 00:00 boundary, where the D1 bar's final M5 candle closes exactly as the next H4 bar
opens; and the binding margin is not that one — the signal is only evaluated at the H4 bar's *close* and the
entry is the *following* bar's open, so the context precedes the decision by ≥ 4 hours in every case.

The same check on the b0/b1 corpus: min margin **+0.25h, zero negatives**.

---

## 4 — DATA / EVIDENCE MAP (§4)

| region | role | status |
|---|---|---|
| 2021-07-27 → 2023-12-29 (gated M5 → H4) | **DEV — selection** | CONSUMED by discovery. Not independent. |
| 2024-01-01 → 2024-06-20 | **CALIB — out-of-selection robustness** | Consumed once as a forward check; usable as supporting, not as independent holdout |
| ≥ 2025-01-01 | protected | **NOT TOUCHED.** `build_frames` asserts no bar ≥ 2025 |
| b0 2011-07-26 → 2013-09-27 | historical, **authorized** | governance-proven loader `hist_m15_data`; **never used for COMP-CONT** |
| b1 2016-01-11 → 2018-04-06 | historical, **authorized** | same; **never used for COMP-CONT** |
| 2013-09 → 2016-01 manifest gap | unratified | excluded by loader assertion |

**b0/b1 are legitimately authorized, not protected, and not previously consumed by this candidate.** The
lab's own `ALPHA_BROAD_DISCOVERY_V2_CONTRACT` designates them the standard cross-era corpus ("*b0/b1 give the
cross-era falsification the original single-regime corpus could not*") and its loader prints a governance
proof: `protected(>=2024)=0 · CALIB=0 · gap(2013-2016)=0 · outside_b0b1=0`.

**Why the cross-era test had never been run:** `COMP-CONT-L-rr2` was frozen at checkpoint #1 (`4082c5c`);
the b0/b1 corpus was authorized at checkpoints #4/#8 (`8bf501b`, `206a3dd`) — *after* the freeze — and Alpha
then correctly declined to retest a frozen object ("*removed from active research; no retune/retest/clone*").
Procedurally right for Alpha; it leaves the cross-era falsification to the validator. **No independence was
manufactured and no protected region was consumed.**

---

## 5 — INDEPENDENT REPRODUCTION (§5) — **EXACT**

I re-derived the signal set and recomputed **every** metric from the trade ledger rather than trusting the
frozen reporting layer.

```
  raw triggers (DEV, LONG, D1-up, compression) : 275
  after cooldown-20 dedup                      :  53
  after risk>0 filter (effective trades)       :  53
```

| metric | reproduced | frozen spec | |
|---|---|---|---|
| N | 53 | 53 | **MATCH** |
| avgR (STRESS) | +0.4434 | +0.443 | **MATCH** |
| PF | 1.9372 | 1.94 | **MATCH** |
| positive rate | 0.5094 | 0.509 | **MATCH** |
| median R | +0.2566 | +0.257 | **MATCH** |
| max loss | −1.1140 | −1.114 | **MATCH** |
| maxDD | −6.1876 | −6.19 | **MATCH** |
| best-1 / 5 / 10%-removed | +0.4136 / +0.3505 / +0.2458 | +0.414 / +0.350 / +0.246 | **MATCH** |
| median SL / TP / hold | 189.6p / 379.2p / 8 bars | 190p / 379p / 8 | **MATCH** |
| BASE avgR | +0.4604 | +0.46 | **MATCH** |
| DISC / CONF | +0.524 / +0.329 | +0.52 / +0.33 | **MATCH** |
| per-year 2021/2022/2023 | +0.053(10) / +1.000(8) / +0.428(35) | identical | **MATCH** |
| CALIB 2024 | N=24, +0.2230, PF 1.474, posRate 0.500 | N=24, +0.223, PF 1.47, 0.50 | **MATCH** |

The frozen 53-row ledger matches mine trade-for-trade on `(t_entry, R)` **to the stored 5-decimal precision**.

### 5.1 Two reporting-layer definitions that must be restated (not reproduction failures)

1. **`WR_target` is understated.** `swing_base.metrics` computes it as `(R ≥ rr − 0.05)` on **net** R.
   Trades with small risk lose more than 0.05R to the fixed round-trip cost and drop out of the band even
   though they hit the target. Counting actual target exits gives **22/53 = 0.415**, not 0.396 — a
   *gross*-calibrated tolerance band applied to *net* returns. **This is the same artifact I identified in
   the H4-bo-raw-S audit, and here it cuts in the candidate's favour.**
2. **`trades_per_month` is overstated for portfolio purposes.** It divides by the number of *distinct months
   containing a trade* (19), giving 2.79. Over the DEV span (29.1 months) the calendar rate is
   **1.89/month**. The frozen figure is "trades per active month" and overstates portfolio-relevant
   frequency by ~48%.

---

## 6 — EXECUTION REALISM (§6) — **PASS**

| check | finding |
|---|---|
| entry timing | `entry = open[i+1]` — **no same-bar fill** |
| stop / target derivation | both from `entry` and `risk`, fixed at entry; no future information |
| same-bar ordering | `hit_stop` tested **before** `hit_targ` — **stop wins ties**, conservative |
| horizon exit | at close of the last in-window bar |
| cost | round-trip charged **once**: `net = gross − COST[scenario]`, then `/risk` — no double count |
| tick / spread | ratified constants read from `swing_base.COST`, not re-declared |
| deduplication | `cooldown = 20` on signal index — causal (time-since-last only), not outcome-based |
| lookahead via HTF | none — see §3 |
| event reuse | none; each event enters once |

**One structural observation (not a defect, but it qualifies the reported risk metrics):** there is **no
one-position-at-a-time lock**. `cooldown = 20` bars but `horizon = 42` bars, so positions can overlap —
**15 of 53 entries (28.3%)** occur while a previous trade is still open, with up to **3 concurrent
positions**. `maxDD` is computed on a sequential `cumsum(R)`, which implicitly assumes single-position
accounting. The reported −6.19R is therefore an approximation of a concurrent-book drawdown, and the
"53 opportunities" are not 53 sequentially-capitalised trades.

---

## 7 — BASE / STRESS RESULTS (§7)

Cost semantics verified mechanically from `swing_base.COST` = `{GROSS 0.00, BASE 0.05, STRESS 0.24}`,
matching `AI_TRADER_SHADOW_COST_MODEL`. All headline numbers are STRESS.

| scenario | avgR | note |
|---|---|---|
| GROSS | +0.4648 | |
| BASE | +0.4604 | |
| **STRESS** | **+0.4434** | cost-robust on DEV: only −0.021R from gross |

Cost robustness is genuine and follows from the wide structural stop (median 190 pips): 0.24 USD on a
~19 USD risk is ~1.3% of R.

---

## 8 — CORE METRICS (§8, DEV, STRESS)

```
  raw triggers 275 · effective trades 53 · unique trading days 53 · trades/month 1.89 (calendar)
  WR (target reached) 0.415 · positive rate 0.509 · avgR +0.443 · median R +0.257 · PF 1.937
  maxDD -6.188R · max single loss -1.114R · largest winner +1.993R · longest losing streak 6
  best-1/5/10%-removed +0.414 / +0.350 / +0.246 · largest winner = 8.5% of total P&L
  exits: 22 target / 23 stop / 8 horizon
  geometry: median SL 190p · median TP 379p · median hold 8 H4 bars
  entry hours (UTC): 0:12 · 4:18 · 8:10 · 12:5 · 16:4 · 20:3 · 22:1
```

Market Operating Mode is **not used** by this strategy (§15) — and none was added.

---

## 9 — CROSS-ERA ROBUSTNESS (§9) — **FAIL. The decisive finding.**

The frozen rule was applied **unchanged** — same `W=20`, `H=42`, `cooldown=20`, `rr=2.0`, D1 `EMA20>EMA50`
causal context, `box_low` stop, next-bar-open entry, stop-wins-ties, STRESS cost — to the authorized b0/b1
corpus via `hist_m15_data` (governance proof printed: only authorized timestamps).

| era | raw | N | avgR | PF | posRate | WR-tgt | maxDD | best-1% | best-5% | best-10% | med SL |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **b0 2011–2013** | 440 | 41 | **−0.410** | 0.45 | 0.220 | 0.146 | −18.82 | −0.470 | −0.600 | −0.744 | 209p |
| **b1 2016–2018** | 877 | 76 | **−0.060** | 0.91 | 0.382 | 0.237 | −16.74 | −0.088 | −0.174 | −0.301 | 119p |
| **pooled** | 1,317 | **117** | **−0.183** | 0.73 | 0.325 | 0.205 | −23.41 | −0.221 | −0.301 | −0.431 | 142p |
| *DEV 2021–2023* | 275 | 53 | *+0.443* | 1.94 | 0.509 | 0.415 | −6.19 | +0.414 | +0.350 | +0.246 | 190p |

Per-year within b0/b1: 2011 −0.321(12) · 2012 −0.446(24) · 2013 −0.454(5) · **2016 +0.170(34)** ·
2017 −0.241(32) · 2018 −0.265(10). **Five of six historical years negative.**

**This is a sufficiently-populated same-context sign reversal, not an absence-of-event result.** The event is
amply present historically — 1,317 raw triggers versus DEV's 275 — and every one of those events is by
construction inside a confirmed D1 uptrend with an H4 compression, i.e. exactly the declared mechanism. The
`REGIME_SPECIFIC` label does not rescue this: the regime *is* the entry condition, and within that same
regime in other eras the edge is negative.

**The lab's own elimination rule fires:**
```
  ELIM:SIGN_REVERSAL = one era >0 and another < -0.03, both N>=25
    positive, N>=25 : DEV (53, +0.443)
    negative, N>=25 : b0 (41, -0.410) · b1 (76, -0.060) · pooled (117, -0.183)
    TRIGGERED: TRUE
```

**Limitation stated honestly:** b0/b1 H4 bars are aggregated from M15, DEV H4 bars from native M5. This is a
construction difference. I judge it insufficient to explain a **−0.63R** swing: both aggregate into the same
4-hour buckets, high/low/close are near-identical by construction, and the effect is present in *both*
historical eras and in five of six years. The differing median stop (209p / 119p / 190p) reflects genuine
volatility regimes, not bar construction.

This finding also aligns with the lab's own later meta-conclusion, reached independently after this freeze:
*"within-period stability is insufficient; state→path is regime-conditional; **cross-population is the real
gate**"* and *"state→path is era-dependent even WITHIN a fixed causal regime."*

---

## 10 — DISC / CONF (§10) — reproduces, and is not the problem

Chronological 60/40 on the frozen definition, split not redefined after viewing results:

| split | N | avgR | PF | posRate | maxDD | best-10%-rem |
|---|---|---|---|---|---|---|
| DISC | 31 | +0.524 | 2.14 | 0.548 | −6.19 | +0.307 |
| CONF | 22 | +0.329 | 1.67 | 0.455 | −4.47 | **+0.067** |

Both positive, reproducing the frozen claim (+0.52 / +0.33) exactly. Note CONF's best-10%-removed is
**+0.067** — only marginally positive on 22 trades. **DISC→CONF stability is real but is a within-population
check; it cannot detect the cross-era reversal of §9.**

---

## 11 — TAIL DEPENDENCE (§11) — **passes on DEV; fails out-of-selection**

```
  remove best-1%  (k=1)  -> +0.4136
  remove best-5%  (k=3)  -> +0.3505
  remove best-10% (k=6)  -> +0.2458
  remove best-20% (k=11) -> +0.0385
  largest winner = 8.5% of total P&L · top 3 winners = 25.4%
```

On DEV the edge is **genuinely not tail-carried** — best-10%-removed retains 55% of the full expectancy, and
no single trade dominates. Interpreted against the payoff geometry (rr = 2.0, 22 target / 23 stop / 8
horizon), this is a healthy positively-skewed profile, and I do not penalise the skew itself.

**However — and the frozen package does not report this — CALIB 2024 best-10%-removed is −0.030.**
Out-of-selection, the edge *is* tail-dependent. The package reports CALIB avgR/PF/posRate but omits the tail
metric it reports for DEV.

---

## 12 — DRAWDOWN / LOSS GEOMETRY (§12)

```
  maxDD -6.188R at trade #27/53; drawdown ran from trade #21, recovered 4 trades later (#31)
  max single loss -1.114R (>1R: the round-trip cost sits on top of a full stop)
  longest losing streak: 6 trades
  by year: 2021 -4.05R (N=10) · 2022 -1.01R (N=8) · 2023 -6.19R (N=35)
  b0/b1: maxDD -18.82R and -16.74R (pooled -23.41R)
```

Against the S5 independent-validation governance thresholds (gate G: maxDD ≤ 15R, maxLoss ≤ 2.0R) the DEV
figures **PASS** (6.19R, 1.114R). No threshold was introduced after seeing results. **On b0/b1 the same
strategy breaches gate G** (−18.82R / −16.74R / −23.41R).

---

## 13 — NEIGHBOUR STABILITY (§13) — robustness probe only; **the `W` neighbourhood is knife-edge**

The frozen candidate is unchanged; no neighbour was selected.

| perturbation | N | avgR | PF | best-10%-rem | maxDD |
|---|---|---|---|---|---|
| **FROZEN W=20, cd=20, rr=2** | 53 | **+0.443** | 1.94 | **+0.246** | −6.19 |
| W=14 | 73 | +0.013 | 1.02 | **−0.230** | −15.36 |
| W=16 | 63 | +0.136 | 1.23 | **−0.096** | −14.18 |
| W=18 | 57 | +0.288 | 1.55 | +0.088 | −5.29 |
| W=22 | 47 | +0.053 | 1.10 | **−0.178** | −7.12 |
| W=24 | 44 | +0.068 | 1.13 | **−0.179** | −6.60 |
| W=28 | 42 | −0.110 | 0.81 | **−0.393** | −8.85 |
| cooldown 10 / 12 / 16 / 24 / 30 | 80 / 74 / 60 / 47 / 42 | +0.304 / +0.256 / +0.275 / +0.288 / +0.124 | — | +0.116 / +0.046 / +0.084 / +0.086 / −0.128 | — |
| rr 1.5 / 2.5 / 3.0 | 53 | +0.298 / +0.429 / +0.513 | — | +0.146 / +0.166 / +0.197 | — |
| horizon 30 / 60 / 84 | 53 | +0.392 / +0.412 / +0.337 | — | +0.188 / +0.211 / +0.126 | — |

- **`rr`, `horizon` and `cooldown` are genuinely stable** — the spec's claims there reproduce.
- **`W` is not.** W = 20 is the maximum of every column, and best-10%-removed goes **negative at W = 14, 16,
  22, 24 and 28** — on *both* sides, one to two steps away. Only W = 18 and W = 20 survive the spec's own
  tail criterion.
- The spec states the edge is *"present at W = 14–20"*. **At W = 14 and W = 16 best-10%-removed is negative
  (−0.230 and −0.096)** — by the spec's own robustness standard those are not "present". The genuine window
  is **W ∈ {18, 20}**, a two-point plateau, not a band.

Reported as robustness evidence, not as a reason to prefer a neighbour. It is corroborating, not decisive.

---

## 14 — TEMPORAL / SESSION CONCENTRATION (§14)

```
  by year         : 2023 contributes 63.7% of P&L over 35/53 trades (proportionate)
  by quarter      : 2022Q1 contributes 38.3% of P&L over  7/53 trades  <- disproportionate
  by entry hour   : 00 UTC contributes 50.1% of P&L over 12/53 trades  <- disproportionate
  2022 (N=8, avgR +1.000) contributes 34.0% of P&L from 15% of trades
```

Two genuine concentrations: **2022Q1** (13% of trades → 38% of P&L) and the **00 UTC** H4 bucket (23% of
trades → 50% of P&L). Neither is inherent to the declared mechanism — nothing in "H4 compression inside a D1
uptrend" privileges the Asian-session bucket or one quarter. I record these as **fragility indicators**, not
as an independent failure, and I applied **no post-hoc filter**.

---

## 15 — MARKET MODE (§15)

`COMP-CONT-L-rr2` does **not** use `MARKET_OPERATING_MODE_V1`. None was added, and no mode-based rescue was
attempted.

---

## 16 — INDEPENDENCE FROM S5 (§16) — `PARTIALLY_REDUNDANT`

| dimension | finding |
|---|---|
| direction | **Both LONG** — same directional exposure |
| timeframe / mechanism | S5 = M15 NY opening-range up-breakout; COMP-CONT = H4 volatility-compression re-entry — mechanically distinct |
| population overlap | S5's validated window is 2023-07-24 → 2025-10-12; COMP-CONT's DEV is 2021-07 → 2023-12 — **~5 months of calendar overlap** |
| session | S5 fires in the NY opening window (~13:30 UTC). COMP-CONT's entry hours are H4 boundaries, only 9/53 trades (17%) in the 12/16 UTC buckets — **low session overlap** |
| incremental frequency | +1.89 calendar trades/month against S5's 11.1/month |
| trade-level overlap / return correlation | **NOT COMPUTABLE** — S5's ledger is sealed in `escrow_red_team/`, and the populations barely overlap |

**Classification: `PARTIALLY_REDUNDANT`.** Mechanically and session-wise distinct, but the same directional
LONG trend-beta exposure, and Alpha's own checkpoint records it as *"P&L-correlated with the frozen LONG
survivors"* within a family it describes as **saturated**. Nothing was changed to improve independence.

---

## 17 — MULTIPLICITY / DISCOVERY LINEAGE (§17)

From `ALPHA_MULTIPLE_TESTING_LEDGER.md` and `ALPHA_DISCOVERY_CHECKPOINTS.md`, verbatim:

- This loop cycle: **5 frontiers** (F1-VOL-EXP, F2-EXH-REV, F3-TEMPORAL, F4-DRIFT, **F5-COMPCONT**),
  **14 hypotheses** (H01–H14), plus *"F5 full W × H × cd × rr grid + CALIB"*.
- Program lineage: *"**42 hypotheses / 19 frontiers** across 2021-2023 native + historical b0/b1 SWING +
  b0/b1 M15 intraday + external S2/S4 → **1 survivor COMP-CONT-L-rr2**"*.
- Prior program: 60+ economic hypotheses.

**COMP-CONT-L-rr2 is the sole survivor of ~42 hypotheses across 19 frontiers, plus a full four-dimensional
parameter grid on the surviving frontier.** It is emphatically **not** a preregistered single hypothesis, and
Alpha states so plainly ("*Not hypothesis #1*") — creditable disclosure.

**What the evidence can support given that lineage:** at most *"one configuration out of a large search
showed a positive DEV result that also held on a 24-trade forward window."* Given ~42 hypotheses × a
multi-point parameter grid, a DEV avgR of +0.44 on N=53 with a two-point-wide `W` plateau is **well within
what selection over that search space can produce**. The cross-era test (§9) is precisely the out-of-search
evidence that resolves it — and it resolves it negatively.

---

## 18 — BLOCKERS AND LIMITATIONS

1. **b0/b1 H4 is M15-derived; DEV H4 is M5-derived.** A construction difference, argued in §9 to be far too
   small to explain a −0.63R reversal, but it is a real caveat on the cross-era comparison.
2. **S5 trade-level overlap not computable** — ledger in escrow, populations barely overlap. §16 is a
   structural assessment and is labelled as such.
3. **Overlapping positions** (28.3% of entries) mean the reported `maxDD` is a sequential approximation.
4. **CALIB is a single 24-trade window** and was already consumed once; it is supporting evidence, not an
   independent holdout.
5. **Nothing was repaired.** No parameter, rule, era, filter, cost or timeframe was altered. Any corrected
   variant would be a **new research identity owned by Alpha under a new mandate**.

---

## 19 — FINAL VERDICT

```
COMP_CONT_L_RR2_INDEPENDENT_VALIDATION_FAIL
```

**What passed, and deserves saying plainly:** the frozen identity reconstructs exactly from repository
artifacts, all three fingerprints reproduce, the ledger matches trade-for-trade, freeze integrity is intact,
the execution semantics are conservative and correct, the cost treatment is right, the DEV tail robustness is
genuine, the drawdown geometry passes S5's own gate G, and — most importantly — **the D1 causality defect
that blocked `H4-bo-raw-S` is genuinely absent here** (`D1_CAUSALITY_SAFE_VERIFIED`, zero negative margins
against 98.1% under the legacy path). Alpha's package is honest, well-documented and self-critical.

**Why it fails:** applied unchanged to 117 amply-populated events in the lab's own authorized historical
corpus, inside the same declared D1-uptrend regime, the strategy produces **−0.183R with PF 0.73** against
**+0.443R with PF 1.94** on the selection window. Five of six historical years are negative. The lab's own
`ELIM:SIGN_REVERSAL` gate triggers with the contradicting sample more than twice the size of the supporting
one. The `W` neighbourhood is a two-point plateau, and the sole survivor of ~42 hypotheses is exactly the
object for which such a reversal is most diagnostic.

**Per §20, no PASS ⇒ no Red Team handoff.** Not sent to AI Trader, not promoted, `StrategyCatalog` untouched.

**Recommended disposition (CEO decision, not mine to take):** record `COMP-CONT-L-rr2` as
`INDEPENDENT_VALIDATION_FAIL — CROSS_ERA_SIGN_REVERSAL` in the registry, alongside `H4-bo-raw-S`
(`INDEPENDENT_VALIDATION_BLOCKED`). **S5 remains the only independently validated strategy.**

---

## 20 — ARTIFACTS

`statistician/comp_cont/` — `d1causal.py`, `repro.py`, `crossera.py`, `battery.py`, and the reproduced
ledgers. **Environment:** Python 3.14; loader `edge_research._common.load('M5', PRE_HOLDOUT_SPLIT_ID,
RESEARCH_HOLDOUT_CUTOFF_UTC)`, file_sha256 `cbb6eebe…`, manifest 2.7.94; freeze commit `4082c5c`;
impl fp `c60357cb…`; config fp `3ceb5cd9…`; ledger fp `98a8b906…`; cost `{GROSS 0.00, BASE 0.05, STRESS 0.24}`.

---

*Statistician division — independent statistical validation. Verdicts are scoped strictly to the evidence
examined and are not transferable to adjacent claims.*
