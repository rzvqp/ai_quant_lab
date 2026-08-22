# STAT — H4-bo-raw-S INDEPENDENT VALIDATION AUDIT

**Mandate ID:** `STAT-H4-BO-RAW-S-INDEPENDENT-VALIDATION-001`
**Division:** Statistician (independent statistical validation)
**Date:** 2026-08-22
**Subject:** `ALPHA-H4-BO-RAW-S-VALIDATION-PACKAGE-COMPLETION-001`, Alpha commit `07e0f4424eb5771e24f1287ca14781561bfec8d6`
**Prior Statistician triage:** `f890b0ecb99440c0d7c9911f91af60ac01fd0d3e`

**Scope directives honoured:** `H4_BO_RAW_S_ONLY` · `INDEPENDENT_AUDIT` · `NO_RETUNING` · `NO_NEW_ALPHA` ·
`NO_M5_ADDITION` · `NO_EXECUTION_OPTIMIZATION` · `SEPARATE_WR_DEFINITIONS` ·
`PROGRAM_LEVEL_EVIDENCE_INDEPENDENCE` · `DO_NOT_REUSE_CONSUMED_DATA_AS_OOS` ·
`RECOVER_S5_S20_VALIDATION_GATES` · `NO_PROTECTED_DATA_CONSUMPTION_WITHOUT_AUTHORIZATION` ·
`NO_AI_TRADER` · `NO_MT5` · `NO_DEMO` · `NO_LIVE`

---

## 0 — TERMINAL VERDICT — OUTCOME B

```
H4_BO_RAW_S_PACKAGE_AUDIT_PASS
H4_BO_RAW_S_INDEPENDENT_VALIDATION_BLOCKED_NO_UNTOUCHED_EVIDENCE
```

Plus one finding the mandate's menu does not provide for, reported separately because it is material and
because suppressing it to fit the menu would be dishonest:

```
H4_BO_RAW_S_D1_TREND_FILTER_LOOKAHEAD_CONFIRMED
```

**No independent validation was performed, because no untouched authorized evidence exists.** I did not
re-use DEV or CALIB and call it validation, and I did not touch any protected 2024/2025+ region.

Two corrections to my own prior triage (`f890b0e`) are recorded in §4 and §9. **One of them reverses a claim
I made against this candidate**, and it reverses in the candidate's favour.

---

## 1 — LINEAGE

| element | value | verified |
|---|---|---|
| Alpha package commit | `07e0f4424eb5771e24f1287ca14781561bfec8d6` | ✓ |
| Package artifacts | `H4_BO_RAW_S_STRATEGY_SPEC.md`, `h4boraws_package.json` (1,696 lines), `h4boraws_package.py` (142 lines), report | ✓ read in full |
| Frozen source of truth | `econ_campaign.py`, mechanism `bo-raw-S` = `mk_breakout(up=False, lb=20, accept=False)` | ✓ |
| Engine | `mstrat.simulate` (`ai_quant_lab-wp5b/code/mstrat.py`) | ✓ read |
| Cost contract | `AI_TRADER_SHADOW_COST_MODEL_v1` — BASE RT 0.05 / STRESS RT 0.24 | ✓ |
| Prior triage | `f890b0e` (`N_VALIDATION_WORTHY = 1`) | ✓ |

**Equivalence audit — the package re-implements rather than imports the frozen code.** `h4boraws_package.py`
copies the generator, signal builder and evaluator instead of importing `econ_campaign.py`. I therefore
compared them line by line rather than accepting the "copied VERBATIM" claim:

- `mk_breakout_raw_short` vs `mk_breakout(False, 20, False)` — identical: same `rmin(lo,20).shift(1)`, same
  `range(22, len-2)`, same `cl[i] < L[i]` test, same emitted tuple. (The guard order differs —
  `cl[i]<L[i] and isfinite(L[i])` vs `not brk or not isfinite(lvl)` — but `cl[i] < NaN` is False, so the two
  are equivalent on all inputs.)
- `build_signals` — identical, with `up` hard-bound to False and an added `etime` field that affects nothing.
- `realized` — identical, with `blocks` parameterised instead of fixed to `DEVB`.
- `load_tf` / `slices` — character-for-character identical.

**Claim verified, not accepted.**

---

## 2 — IDENTITY REPRODUCTION (§3) — **PASS, all four fingerprints**

Recovered by executing the package script myself:

| fingerprint | expected (Alpha, abbreviated) | recovered (full) | |
|---|---|---|---|
| implementation | `5dc24217…` | `5dc242171d23cda82e160394be04bd09af147baa8cfdc44d3a52bbfb7f7279b1` | **MATCH** |
| data (H4 CSV sha256) | `f8f23f6e…` | `f8f23f6e5c2fb2e402c54f0624252c896f578b92283772a8cb67c4b3e06ffee5` | **MATCH** |
| config | `3fe952ae…` | `3fe952ae181195ba4cfc646caaac1e8953ced84bfcba931bae90024b32558f4c` | **MATCH** |
| trade ledger | `498ee294…` | `498ee2949b6c4f0a429f5e7b5e862da3c518fe3e9e630ea208f59702799591d1` | **MATCH** |
| cost identity | `AI_TRADER_SHADOW_COST_MODEL_v1`, BASE 0.05 / STRESS 0.24 | read from the JSON at runtime, not hard-coded | **MATCH** |

**Stronger check: I regenerated `h4boraws_package.json` and it is byte-identical to the committed file**
(sha256 `4587139a45d29f30…` both). No `H4_BO_RAW_S_IDENTITY_MISMATCH`.

**One identity gap, non-blocking:** `implementation_fingerprint` is the sha256 of **`econ_campaign.py`** —
a file that was *not executed* to produce the ledger. The code that actually generated it,
`h4boraws_package.py`, is not covered by any fingerprint. Since I verified the two are functionally
equivalent (§1) this does not invalidate anything, but the fingerprint does not seal what it appears to seal.
**Recommendation: fingerprint the executing file as well.**

---

## 3 — LEDGER REPRODUCTION (§4) — **PASS, N = 125 exactly**

125 rows, each carrying `block, etime, entry_utc, side, entry, sl_usd, sl_pips, tp_pips, R_gross, R_base,
R_stress`. Reproduced identically. **No trade added, removed, or reclassified.**

Exit-outcome decomposition (STRESS), computed from the ledger:

```
  R >= +1.45 (target hit)          55
  0 < R < +1.45 (target hit, net)  11     <- see §4
  R <= -0.90 (full stop)           59
  -0.90 < R <= 0                    0
  min -1.0861   max +1.4932
```

**Every one of the 125 trades resolved at either the target or the stop. Zero horizon exits**, despite the
engine's 48-bar timeout. The outcome distribution is effectively binary, which is what makes the R statistics
well-behaved.

---

## 4 — WR-SEMANTICS AUDIT (§5) — **and a correction of my own prior report**

Six definitions, kept strictly separate as directed:

| # | definition | value |
|---|---|---|
| **A** | GROSS reached-target (`R_gross ≥ k−0.05 = 1.45`) | **0.5280** |
| **B** | BASE reached-target (`R_base ≥ 1.45`) | **0.5280** |
| **C** | STRESS reached-target (`R_stress ≥ 1.45`) | **0.4400** |
| **D** | positive-net-R — GROSS / BASE / **STRESS** | 0.5280 / 0.5280 / **0.5280** |
| **E** | `R_stress ≥ +1.0` | 0.5280 |
| **E** | `R_stress ≥ 0` (break-even or better) | 0.5280 |

### 4.1 What the 0.44 actually is

I isolated the 11 trades that are A-positive but C-negative and read their returns directly:

```
  R_gross  : all exactly +1.500
  R_stress : 1.431 1.449 1.449 1.445 1.445 1.440 1.445 1.434 1.438 1.423 1.433
  SL pips  : 34.9  47.4  46.8  43.9  43.8  40.2  43.3  36.5  38.4  31.1  36.0
  outcome changed to a loss?  0 of 11
```

**All eleven still hit the target.** They fall below 1.45 only because they have unusually tight stops
(31–47 pips), so the fixed 0.24 round-trip cost consumes 5.1–7.7% of R. The `k − 0.05` band was calibrated
for *gross* returns; applying it to *net* returns is a threshold-calibration artifact.

**Not a single trade changes outcome between GROSS and STRESS.** 66 winners / 59 losers in every scenario.

### 4.2 ★ Correction to `f890b0e` §8.1

In my triage I wrote: *"Under the ratified STRESS cost the flagship's win rate is 0.44, not 0.528 — 8.8
points lower, and further from Profile A than the report concludes."*

**That was wrong, and it was wrong against the candidate.** 0.44 is not a win rate under cost; it is the
fraction of net returns clearing a gross-calibrated threshold. By every definition of *winning* — positive
net R, ≥ +1.0R, break-even-or-better — the win rate is **0.528 at BASE and at STRESS alike**. Cost does not
cost this strategy a single winner.

My *defect identification* stands (the number was published two ways, unlabelled, beside a STRESS
expectancy). My *interpretation* of which number was "the" win rate did not. **Alpha's package resolves this
correctly** — three labelled definitions plus the exact explanation ("stress cost pushes marginal
target-hitters below +1.45-net; positive-rate unchanged"). That explanation is right and I confirm it.

---

## 5 — ECONOMICS (§6) — **PASS, every figure reproduced**

| metric | expected | reproduced | |
|---|---|---|---|
| N | 125 | 125 | **MATCH** |
| GROSS avgR | — | **+0.3200** | new |
| BASE avgR | +0.3133 | +0.3133 | **MATCH** |
| STRESS avgR | +0.2876 | +0.2876 | **MATCH** |
| GROSS PF | — | 1.6780 | new |
| BASE PF | — | 1.6591 | new |
| STRESS PF | 1.5896 | 1.5896 | **MATCH** |
| maxDD (STRESS) | −9.273 R | 9.273 R | **MATCH** |
| max single loss | −1.086 R | −1.0861 R | **MATCH** |
| median R (STRESS) | — | +1.4342 | **MATCH** to my triage |
| max consecutive losses | — | **9** | new |
| CALIB | +0.1523 (n 20) | +0.1523 (n 20) | **MATCH** |

My own triage-derived PF (1.590) and maxDD (9.27 R) are confirmed to 4 significant figures by an
independently constructed single-sequence ledger. **9 consecutive losses** is a new figure and is the
sharpest risk number in the package — at a 0.528 win rate, a 9-loss run is a tail event worth flagging to
anyone sizing this.

---

## 6 — ROBUSTNESS (§7) — **PASS**

```
  best-1%-removed  (STRESS) = +0.2779
  best-5%-removed  (STRESS) = +0.2269
  best-10%-removed (STRESS) = +0.1600
```

All reproduce exactly. Removing the best 10% of trades leaves **+0.160 R/trade — 56% of the full
expectancy**. Profitability remains **materially positive**; the edge is broad-based, not tail-carried.
This remains the single strongest evidential property of the candidate.

---

## 7 — TEMPORAL BLOCKS (§8) — **PASS, no favourable re-partitioning**

Original blocks only. No new partitions created.

| block | trade span | N | WR-tgt GROSS | WR-tgt STRESS | WR-pos STRESS | avgR STRESS | PF | maxDD |
|---|---|---|---|---|---|---|---|---|
| b0 | 2011-09-26 → 2013-09-24 | 91 | 0.495 | 0.462 | 0.495 | +0.2091 | 1.402 | 7.18 R |
| b1 | 2016-05-27 → 2017-12-12 | 34 | 0.618 | 0.382 | 0.618 | +0.4978 | 2.236 | 2.11 R |
| **ALL** | | **125** | 0.528 | 0.440 | 0.528 | **+0.2876** | 1.590 | 9.27 R |

Per populated year:

| year | N | avgR STRESS | PF | maxDD | WR-pos |
|---|---|---|---|---|---|
| 2011 | 12 | +0.0234 | 1.039 | 3.05 R | 0.417 |
| 2012 | 33 | +0.1824 | 1.344 | 3.66 R | 0.485 |
| 2013 | 46 | +0.2766 | 1.562 | 7.18 R | 0.522 |
| 2016 | 17 | +0.5818 | 2.583 | 1.04 R | 0.647 |
| 2017 | 17 | +0.4139 | 1.945 | 2.11 R | 0.588 |

**The "all populated years positive" claim is verified TRUE.** But three qualifications belong beside it:
2011 is +0.023 — statistically indistinguishable from zero on 12 trades; b1 contributes only 34 trades; and
**2018 has zero trades** although block b1 runs to 2018-04-06.

---

## 8 — DATA GAPS (§9) — **PASS, and a structural finding about the blocks**

### 8.1 The frozen "blocks" were not chosen — the file's holes chose them

The H4 source is itself discontinuous. Segmenting it mechanically:

| # | available data segment | bars | maps to |
|---|---|---|---|
| S1 | 2011-07-26 → 2013-09-27 | 3,379 | **b0** (DEV / discovery) |
| S2 | 2016-01-11 → 2018-04-06 | 3,449 | **b1** (DEV / discovery) |
| S3 | 2020-08-11 → 2021-09-03 | 1,647 | **calib** (robustness) |
| S4 | 2022-12-16 → 2025-10-10 | 4,357 | **never touched by this campaign** |

**b0, b1 and calib coincide with S1, S2 and S3 to within three days.** They are not selected windows — they
are simply everything the file contains. This is materially reassuring: it removes any suspicion that the
evaluation windows were picked, and it is a fact neither Alpha's report nor my triage stated.

### 8.2 The 975.7-day streak

Confirmed: the maximum inter-trade interval, 975.7 days, is exactly the S1→S2 hole (2013-09-24 → 2016-05-27).
**It is a DATA GAP, not strategy inactivity**, and must never be reported as a no-trade streak.

The genuine within-data no-trade streaks are the other long gaps: **157.0, 132.9, 126.7 and 111.3 days**.
The honest maximum observed-market dry spell is therefore **≈157 days (5.2 months)** — a real and material
disclosure that the 975-day figure obscures in both directions.

### 8.3 No trade crosses a gap; no warmup leaks across an invalid boundary

- Signals are generated per block and `mstrat.simulate` runs on the block's own frame; the exit search is
  `range(ei, min(ei+48, n))` with `n = len(block)`. **Crossing is structurally impossible.** b0: 91 trades,
  b1: 34, spanning: 0.
- **Warmup:** `rmin(lo, 20)` is recomputed *per block*. `m_atr` (rolling 14 TR) is computed on the **full,
  gap-spanning file** before slicing — so the first ~14 bars of b1 and calib do carry a contaminated ATR
  (the TR across a 836-day hole). **But signal generation starts at block-local index 22**, and
  22 > max(20, 14), so every indicator value reaching a signal is computed entirely within its own block.
  **Checked specifically because it is the obvious failure mode here — CLEAN.**

---

## 9 — EFFECTIVE SAMPLE SIZE (§10)

```
  raw N = 125          unique calendar days = 98          trades/day = 1.28
  days with 1 trade 76 · 2 trades 18 · 3+ trades 4 · max 4
  lag-1 autocorrelation of R_stress = -0.1813
  median days between trades 2.2  (P25 0.62 · P75 8.1)
  trades opened within 1 day of the previous: 46 of 124 = 0.371
```

**Does 125 overstate the independent evidence? Modestly, yes.** 37% of trades open within a day of the
previous one and 27 trades share a day with another. A day-clustered reading gives **98 effective
observations**.

Two things cut the other way and I state them for balance: lag-1 autocorrelation is **negative** (−0.18), so
the usual clustering variance-inflation does not apply — clustered trades are not repeating the same
outcome; and `mstrat.simulate` enforces one position at a time (`last = xi`), which already suppresses
genuine overlap.

**The consequence that matters:** the canonical gate A threshold is **n ≥ 100**. Raw N = 125 clears it;
**day-clustered effective N = 98 does not.** The candidate sits directly on that boundary, and any future
validation should pre-register which count governs.

★ **Second correction to `f890b0e`:** my triage recorded H4-bo-raw-S trade-day clustering as NOT RECOVERED.
It is recoverable and is recovered here.

---

## 10 — OPPORTUNITY GEOMETRY (§11) — **PASS**

| metric | reproduced | Alpha |
|---|---|---|
| SL pips P25 / P50 / P75 | 58.2 / **76.0** / 127.5 | 58.2 / 76.0 / 127.5 |
| TP pips P25 / P50 / P75 | 87.3 / **113.9** / 191.3 | median 113.9 |
| % TP ≥ 70 / 80 / 100 pips | 0.872 / 0.816 / 0.600 | 0.874 / 0.813 / 0.604 |
| median MFE | 278.0 pips | 278.0 |

Verified, not assumed. The median stop (76 pips) sits inside the CEO's stated 70–100 pip structural zone and
the median target (114 pips) is squarely in the economic-profile regime. **This is not micro-scalping.**

---

## 11 — FREQUENCY (§12) — computed over observed evidence only

```
  OBSERVED market coverage (b0 + b1, data gap EXCLUDED) = 1,610 days = 52.9 months = 4.41 years
    trades / month  = 2.36
    trades / year   = 28.4
    median OBSERVED-market days between trades = 2.2
    max  OBSERVED-market no-trade streak = 157.0 days
```

**Wall-calendar figure, reported separately as directed:** 2011-07-26 → 2018-04-06 is 80.3 months →
**1.56 trades/month**. **This figure is misleading and must not be used** — 34.2% of that span is a data gap
during which the strategy was observing nothing.

Alpha computed frequency on observed coverage (excluding the gap). **Correct, and credited.**

Against the ~2–3 trades/**day** portfolio objective this is roughly **0.11 trades/day** — about 25× short on
its own. Per §24 that is not a reason to reject it, and I do not; it is a reason not to promote it for
strategy-count reasons either.

---

## 12 — EXECUTION ASSUMPTIONS (§13)

Read directly from `mstrat.simulate`.

| aspect | implementation | assessment |
|---|---|---|
| signal availability | `cl[i] < rmin(lo,20).shift(1)[i]` — the level uses lows i−20…i−1 | **causal** |
| entry | `entry = o[ei]`, `ei = i+1` — next H4 bar's open | **causal, no same-bar fill** |
| stop construction | `max(\|entry − brk\| + 0.3·ATR[i], 0.8·ATR[i])`, ATR known at close of i | **causal** |
| executable stop floor | `min_exec = max(2·spread·TICK, 5·TICK, 0.10·ATR[si])`; tiny stops widened | conservative |
| target | `entry + dir·1.5·risk`, fixed at entry | fine |
| **intrabar ordering** | stop tested **before** target within each bar (`mstrat.py:66-71`) | **conservative — stop wins ties** |
| exit loop | `range(ei, min(ei+48, n))` — starts on the entry bar | correct; entry is that bar's open |
| horizon | 48 H4 bars, then exit at close | never triggered (§3) |
| serialization | `last = xi`; setups with `ei ≤ last` skipped | one position at a time; **population is endogenous** |
| cost | `cost = (spread+slip)·TICK` with `slip = RT/(2·TICK)`, `spread = 0`; `R = (dir·(ex−entry) − 2·cost)/risk` | round trip charged **exactly once** |

**No optimistic fill assumption, no favourable intrabar ordering, no off-by-one in the signal→entry chain.**
Those were the four things §13 asked me to hunt for, and three of them are clean.

### 12.1 ★ The fourth: confirmed lookahead in the D1 trend filter

`load_tf` builds the D1 alignment flag as:

```python
x = pd.read_csv("OANDA_XAUUSD_D1_from_M15_v2.csv")
e20 = x["close"].ewm(span=20).mean(); e50 = x["close"].ewm(span=50).mean()
x["trend_up"] = (e20 > e50).astype(float)          # <- uses that D1 bar's CLOSE
d = pd.merge_asof(d_H4, x[["time","trend_up"]], ..., direction="backward")
```

**Both files are stamped with BAR-OPEN times.** I verified this directly: the D1 row at
`2011-07-27 21:00Z` is followed by `2011-07-28 21:00Z`, so its close is only known 24 hours after its
timestamp. `merge_asof(direction="backward")` therefore attaches to each H4 bar a `trend_up` derived from a
D1 close **that has not yet occurred**.

Measured:

```
  H4-bar age within its matched D1 bar : min 0h · median 8h · max 20h
  H4 bars whose matched D1 bar had already closed : 15 of 12,832 = 0.1%
  H4 bars where as-used trend_up != causally-available trend_up : 260 of 12,832 = 2.03%

  OF THE 125 FROZEN TRADES:
    pass the as-used D1 filter          : 125 / 125
    also pass the causally-available one: 116 / 125
    qualified ONLY via future D1 info   :   9  (7.2%)
```

**The defect is real and confirmed.** Its impact on this candidate's headline economics, however, is small
and *adverse* to the result: those 9 trades averaged **+0.0712 R** against **+0.3044 R** for the other 116,
contributing **+0.64 R of the +35.95 R total (1.8%)**. The leak did not inflate the edge; if anything it
diluted it.

Three things follow, and I separate them deliberately:

1. The defect **does not explain** H4-bo-raw-S's performance.
2. It **must still be fixed** before any validation is run, because a validation that certifies a
   non-causal filter certifies something unimplementable.
3. It is **not the package's defect**. It lives in `econ_campaign.py`'s loader, predates this mandate, and
   affects **all 184 strategies** that campaign produced. Alpha was mandated to do mechanical completion
   only and had no authority to change it.

**I have not evaluated, proposed, or offered a corrected variant** (§22). The 116-trade figure above is a
defect measurement, not a candidate.

---

## 13 — COST SEMANTICS (§15) — **PASS**

```
  RT = {GROSS: 0.0, BASE: 0.05, STRESS: 0.24}   read at runtime from AI_TRADER_SHADOW_COST_MODEL_v1.json
  cfg["spread_ticks"] = 0.0
  cfg["slip_ticks"]   = RT[scen] / (2·TICK)
  cost = (spread_ticks + slip_ticks)·TICK = RT/2
  R    = (dir·(exit − entry) − 2·cost) / risk = (dir·(exit − entry) − RT) / risk
```

The round-trip total is deducted **exactly once**, in price units, before normalising by risk. **No
gross/net mixing, no double-counting, no missing component.** The spread is folded into the slip term
rather than modelled separately — consistent with the ratified contract, which fixes only the totals.
`risk` is the pre-widened executable risk, and the same `risk` normalises both the P&L and the cost.
Internally consistent.

One consequence, already visible in §4: because cost is a *fixed price amount*, its cost-in-R varies
inversely with stop size — 0.032 R at the median 76-pip stop, but 0.077 R at the smallest 31-pip stop. That
is correct modelling, and it is the entire origin of the 0.528-vs-0.44 confusion.

---

## 14 — M5-CLAIM AUDIT (§14)

Alpha states: *"M5 execution pending; WR/expectancy are conservative lower bounds."* The claim has two parts
and they do not have the same status.

**(a) "conservative" — VERIFIED TRUE.** `mstrat.simulate` resolves intrabar stop-vs-target with the stop
winning ties (`mstrat.py:66-71`). Any trade whose bar touched both levels is booked as a loss. The reported
figures are genuinely a lower bound *with respect to intrabar ambiguity*.

**(b) "an M5 entry layer would improve WR/expectancy" — UNSUPPORTED. Treated as UNKNOWN.**

I go further than merely withholding assent, because the program contains evidence pointing the other way:

- `d2c6577` (M15 consolidation trend-continuation): *"M5 entry timing adds NO value to these M15
  continuation parents"*; M5-confirmation was **rejected** — it made SHORT DISC −0.170 and 2022 −0.247.
- `4f668c8` (H1 intra-range): *"M5-timed entry is worse than coarse on every LONG-mid mechanism"* and
  tail-inferior.
- `b75269a` (H1 RANGE): the earlier "M5 helps" reading was **retracted** as a re-entry artifact.

M5 timing has demonstrated value in exactly one place in this program (`HR-TU-pb-L`, a *pullback* parent),
and has been measured as neutral-to-harmful on breakout/continuation parents — which is what H4-bo-raw-S is.

**NO CLAIM IS MADE THAT M5 WILL IMPROVE PERFORMANCE.** No M5 layer was added, tested, or designed.

---

## 15 — EVIDENCE-CONSUMPTION MAP (§16)

Built mechanically from the data file's own structure and the program's recorded activity.

| region | status | consumer |
|---|---|---|
| S1 2011-07-26 → 2013-09-27 | **CONSUMED — DISCOVERY** | b0, H4-bo-raw-S's own DEV |
| S2 2016-01-11 → 2018-04-06 | **CONSUMED — DISCOVERY** | b1, H4-bo-raw-S's own DEV |
| S3 2020-08-11 → 2021-09-03 | **CONSUMED — ROBUSTNESS** | calib, out-of-DEV check (n=20) |
| S4 2022-12-16 → 2023-12-29 | **CONSUMED — SELECTION** | Alpha M5/M15/H1/H4 DEV window (`m5_data.DEV_END = 2023-12-29`) |
| ↳ *within it* | **SAME MECHANISM SCREENED** | `MT-H4-breakout-S` — H4 20-bar-low breakdown SHORT — tested here: **n=36, avgR −0.0777, PF 0.849 → rejected** |
| S4 2024-01-01 → 2024-06-20 | **CONSUMED — ROBUSTNESS** | Alpha CALIB, spent on HR-TU / MT / TR / IR |
| S4 2023-07-24 → 2025-10-12 | **CONSUMED — VALIDATION** | Red Team S5/S20 independent validation, 52,572 bars, ledger `cd4e8d4a…` |
| V1 2024-07-10 → 2025-10-23 | **PROTECTED / PARTIALLY CONSUMED** | ≥17 Flow-A studies on the same calendar |
| V2 2025-10-23 → 2026-02-17 | **CONSUMED** | terminal holdout invalidated — CEO ruling, `PROJECT_STATE_v2 §8.23` |
| V3 2026-03-10 → 2026-06-20 | **CONSUMED** | |
| V4 2026-07-13 → 2026-07-27 | **CLEAN** | 2,904 M5 bars ≈ **121 H4 bars** |

**The union of the two large S4 consumers (2022-12-16 → 2023-12-29 and 2023-07-24 → 2025-10-12) covers S4
end to end. Residual unconsumed portion of S4: NONE.** All 4,357 of its H4 bars sit inside at least one
consumer.

The `MT-H4-breakout-S` row deserves emphasis: the *same economic mechanism on the same timeframe in the same
direction* was screened on the modern window and rejected. That is program-level consumption **for selection
on this very hypothesis** — the strongest possible form of contamination for a would-be OOS test.

**Alternative source check.** An H4 series resampled from the native M5 file would span 2021-07-27 →
2026-07-27, adding only 2025-10-10 → 2026-07-27 — which is V1-tail, V2 and V3 (protected or consumed) plus
V4 (~121 H4 bars ≈ 0.5 months ≈ **one expected trade**). No usable evidence there either.

---

## 16 — CANONICAL VALIDATION PROTOCOL (§17) — recovered, unchanged

Recovered verbatim from `RT_S5_S20_CLEAN_INDEPENDENT_VALIDATION_REPORT.md`:

| gate | criterion | S5 | S20 |
|---|---|---|---|
| **A** sample | n ≥ 100 | PASS (295) | PASS (553) |
| **B** BASE | BASE net > 0 | PASS (0.2098) | PASS (0.1485) |
| **C** STRESS | STRESS net > 0 @ RT 0.24 | PASS (0.1925) | PASS (0.1027) |
| **D** temporal | ≥2/3 chronological thirds > 0, none < −0.10 | PASS | PASS |
| **E** tail | best-1%-removed BASE > 0 | PASS (0.1907) | PASS (0.1225) |
| **F** delay | +1-bar entry BASE > 0 | PASS (0.1581) | PASS (0.0876) |
| **G** risk | **maxDD ≤ 15R ∧ maxLoss ≤ 2.0R** | PASS (−6.44R, −1.03R) | **FAIL (−23.59R)** |
| **H** fidelity | exact spec/config, engine reproduced | PASS | PASS |

**These gates are adopted unchanged. No easier gate has been invented for H4-bo-raw-S.** They must be
applied on an *independent population*; DEV/CALIB performance against them is not a validation and is not
presented as one.

---

## 17 — UNTOUCHED-EVIDENCE DETERMINATION (§18, §19) — **NONE EXISTS**

**Answer: NO.** There is no currently authorized, scientifically untouched evidence population suitable for a
genuine independent validation of H4-bo-raw-S.

- The only segment its campaign never touched is **S4**, and S4 is **fully consumed** at program level (§15)
  — including a selection-stage screening of the same mechanism on the same timeframe in the same direction.
- The regions that remain formally sealed (**V1 partial, V2, V3**) are either **protected** or already
  consumed by CEO ruling, and **§19 forbids me from consuming them absent explicit authorization for this
  exact purpose. That authorization is not present in this mandate.**
- **V4** is clean but ~121 H4 bars — an expected yield of about **one trade** at 2.36/month. Statistically
  meaningless against a gate requiring n ≥ 100.

Per §18 I therefore **did not** re-use DEV or CALIB and call it validation, and per §19 I **stopped rather
than contaminate** protected evidence.

### 17.1 What authorization would be required

For the CEO, stated concretely so the decision is actionable:

1. **A ratified extension of the H4 series past 2025-10-10** from a source not yet consumed — the binding
   constraint is *data supply*, not analysis.
2. **Or** explicit authorization to consume a named protected region (V1 tail / V2 / V3) **for this exact
   validation**, with dates, source, timeframe, cost contract and gates A–H frozen **before** any outcome is
   viewed. I would need that freeze recorded in writing first.
3. **Or** acceptance that H4-bo-raw-S can never be independently validated on this instrument, and a
   decision on whether a package-audited-but-unvalidated SHORT has any authorized use.

**Prerequisite in every case: the §12.1 D1 lookahead must be repaired at source first.** Validating a
non-causal filter would certify something that cannot be traded.

---

## 18 — INDEPENDENT-VALIDATION RESULTS

**None. No independent validation was performed.** No strategy was executed on any population other than the
already-consumed b0/b1/calib blocks that constitute the frozen package I was auditing. No protected region
was read, and no gates were scored against a would-be OOS sample.

---

## 19 — S5 COMPARISON (§23, context only)

| | **S5** (validated) | **H4-bo-raw-S** (package-audited) |
|---|---|---|
| side | LONG | **SHORT** |
| timeframe | M15 | **H4** |
| mechanism | NY opening-range up-breakout | 20-bar-low breakdown, D1-down aligned |
| population | 2023-07-24 → 2025-10-12 (independent) | 2011-2013 + 2016-2018 (own DEV) |
| N | 295 | 125 |
| BASE / STRESS avgR | +0.2098 / +0.1925 | **+0.3133 / +0.2876** |
| PF | 1.609 | 1.590 |
| maxDD | −6.44 R | 9.27 R |
| max loss | −1.03 R | −1.086 R |
| WR | 0.549 | 0.528 |
| median target | 373 pips | 114 pips |
| **trades/month** | **11.1** | **2.36** |
| evidence status | **independently validated** | **not validated; no population available** |

On DEV, H4-bo-raw-S's expectancy exceeds S5's by ~50% and its PF is comparable. **That comparison is not
meaningful**: S5's numbers come from an independent population, H4-bo-raw-S's from its own discovery data.
An in-sample expectancy exceeding an out-of-sample one is the expected ordering, not a finding.

Its genuine potential portfolio value is **structural**: it is SHORT, on H4, on an economically distinct
mechanism, with roughly zero overlap with S5. That value is unrealised while it is unvalidated.

---

## 20 — LIMITATIONS

1. **This is a package audit, not a validation.** Nothing here says the edge is real out-of-sample.
2. **The lookahead quantification depends on my causal reconstruction** (`trend_up.shift(1)` on the D1
   series). A different but equally defensible causal convention could shift the 9/125 count somewhat. The
   *existence* of the leak does not depend on that choice; its exact magnitude does.
3. **maxDD 9.27 R is computed across the b0→b1 data gap** by chronological concatenation. There is no
   alternative given the data, but it is not a true single-equity-curve drawdown.
4. **Whether S1/S2 sit inside ratified manifest segments is NOT RECOVERED.** I verified only that they do
   not enter the unratified 2013–2016 hole and that evaluation is strictly per-block.
5. **Effective-N is reported as a range** (98 day-clustered ↔ 125 raw), not a single number. The negative
   lag-1 autocorrelation argues against heavy discounting; the day clustering argues for some.
6. **The consumption map is as good as the program's own records.** If a campaign touched S4 without leaving
   a record, my map understates consumption — it cannot overstate it.
7. **No strategy was executed, retuned, or modified**; no threshold, entry, stop, target, filter, RR,
   lookback, or cost was changed; no M5 was added; no protected region was read.

---

## 21 — FINAL VERDICT

```
H4_BO_RAW_S_PACKAGE_AUDIT_PASS
H4_BO_RAW_S_INDEPENDENT_VALIDATION_BLOCKED_NO_UNTOUCHED_EVIDENCE
H4_BO_RAW_S_D1_TREND_FILTER_LOOKAHEAD_CONFIRMED   (reported outside the mandate's menu)
```

**Package audit — PASS.** Identity, configuration, data and ledger fingerprints all match; the JSON
regenerates byte-identically; the re-implementation is provably equivalent to the frozen source; every
economic, robustness, temporal and geometric figure reproduces exactly; the WR ambiguity my triage flagged is
correctly and completely resolved by Alpha; gap handling is clean and no warmup contamination reaches any
signal. **Alpha's mechanical-completion mandate was executed faithfully and well.**

**Independent validation — BLOCKED.** No untouched authorized population exists. The only never-touched data
segment has been consumed at program level three separate ways, one of which screened and rejected this very
mechanism on this very timeframe. The sealed regions are protected and unauthorized for this purpose. I
declined to manufacture a validation from consumed data.

**Lookahead — CONFIRMED, and must be fixed before any validation.** 7.2% of the frozen trades qualified on
D1 information not yet available. The leak did **not** inflate the result — it diluted it — but it is a
causality defect in the frozen strategy, inherited from the campaign loader, and it affects far more than
this candidate.

**Not validated. Not supported for promotion. No Red Team ratification. No execution authorization.**

---

*Statistician division — independent statistical validation. Verdicts are scoped strictly to the evidence
examined and are not transferable to adjacent claims.*
