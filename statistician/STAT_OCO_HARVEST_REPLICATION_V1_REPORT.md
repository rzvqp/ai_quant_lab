# STAT_INDEPENDENT_OCO_HARVEST_REPLICATION_V1 — REPORT

**Mandate:** `INDEPENDENT OCO HARVEST REPLICATION V1` — replication / falsification of Alpha's
`DIRECTION_AGNOSTIC_EXPANSION_HARVEST_V1` (anchor B, prior-day extremes, OCO continuation).
**Division:** Statistician. **Date:** 2026-09-01.
**Subject:** Alpha commit `078c136`, `reports/alpha_discovery/{dae_scan.py, dae_payoff.py}`.
**Code:** `statistician/oco/` — `rep.py` (independent re-implementation), `audit.py`, `decomp.py`,
`stack.py`, `spec.json`.

## VERDICT

```
INDEPENDENT_OCO_HARVEST_REPLICATION_V1_COMPLETE = YES
OCO_SPEC_REPRODUCIBLE   = YES
ALPHA_RESULT_REPRODUCED = YES  (exact, to the third decimal, on an independent implementation)
OCO_EXECUTION_INTEGRITY = FAIL (one specific defect: gap-through fills — §3)

STATISTICAL_VERDICT = INFORMATION_ONLY
READY_FOR_RED_TEAM  = NO
```

**Answer to the CEO's A/B/C/D question: D — a statistically non-zero but economically unusable edge —
with a mechanism correction that matters more than the classification.**

The result is real and reproduces exactly. It is **not** an outlier mirage and **not** an accounting
fabrication. But three things are true that Alpha's report does not say:

1. **The "market selects direction" mechanism is not what pays.** The edge is entirely on the long side
   (+0.086R, t +4.41); the short side is indistinguishable from zero (+0.021R, t +1.08). A plain
   **always-long** buy-stop at the prior-day high earns **+0.0553R per trade — more than the OCO's
   +0.0544R**. The architecture harvests 14 years of gold drift through its long leg; the short leg is
   noise. Direction-agnostic *selection* adds nothing over simply being long.
2. **The protected research holdout was consumed**, and it is 5× richer than the rest of the sample.
3. **Under the governed STRESS cost with realistic gap fills and the holdout removed, the edge is
   −0.011R** — i.e. gone.

---

## 1 — EXACT SPEC (§1)

```
OCO_SPEC_REPRODUCIBLE = YES
OCO_SPEC_HASH = 26827e79511e1ac58ab3dc14f9b3c4251ee92d3e8602057dbd4394e265e37c1e
SOURCE        = dae_scan.py  sha256 88f2b6771f10c762c19c2ea305a6fffe…
                dae_payoff.py sha256 18fc5c46bd55699a1ec5a848d6812539…
```

| element | exact definition recovered from code |
|---|---|
| anchor | first M15 bar of each **UTC calendar date** (`groupby(dt.date).first()`) |
| prior-day high / low | max high / min low over the **previous UTC calendar date** |
| day boundary / timezone | UTC calendar date. No session or rollover boundary. |
| order placement time | at the anchor bar `s`; scanning begins at `s+1` |
| expiry | bar `min(s+96, n−1)` — 96 M15 bars = 24h **from the anchor**, not from entry |
| first-trigger semantics | first bar with `high ≥ PDH` or `low ≤ PDL` |
| opposite-order cancellation | on the trigger bar (loop breaks) |
| same-bar ambiguity | **both activations inside one M15 bar → episode skipped entirely** (conservative) |
| entry price | **the activation level exactly** — no gap adjustment (see §3) |
| stop | the opposite activation level |
| risk (1R) | `PDH − PDL` |
| target | `entry + dir × mult × risk`, mult ∈ {1.0, 1.5, 2.0} |
| target+stop in one bar | resolved as **stop** (conservative) |
| unresolved at expiry | **marked to market** at the close of the expiry bar |
| cost | 0.419 price units/trade, converted to R as `cost / risk` |
| episode independence | one episode per UTC calendar date |
| data | `OANDA_XAUUSD_M15.csv`, **full file, no holdout truncation** |

Nothing material was ambiguous. I did not need to stop.

**Two spec properties worth flagging, neither of which is a defect on its own:**

- **The "prior day" for a Monday is the Sunday re-open stub.** 783 traded episodes (19.4%) have a prior
  day with fewer than 40 bars (median **8 bars ≈ 2 hours**); 760 of them are Mondays. Their risk unit is
  a median 4.56 USD versus 18.89 USD on normal days. **I checked whether this drives the result: it does
  not.** Stub episodes return +0.0598R versus +0.0531R on normal days and contribute 21.3% of PnL while
  being 19.4% of episodes — proportional. A wart, not the engine.
- **1R is enormous.** Median risk is **16.3 USD = 163 pips**. Everything reported in R is denominated in
  a 163-pip unit, which makes the 4.2-pip cost look negligible in R terms. §11 restates the economics in
  pips for this reason.

---

## 2 — REPRODUCTION (§2)

I ran Alpha's own `dae_payoff.py` **and** wrote an independent implementation from the spec table above.
Both agree with Alpha's report to the third decimal.

| | 1.0R | 1.5R | 2.0R |
|---|---|---|---|
| RAW_N / INDEPENDENT_EPISODES | 4,033 | 4,033 | 4,033 |
| candidate episodes / no-trigger / ambiguous | 4,665 / 624 (13.4%) / 8 (0.17%) | — | — |
| trades per year | ~268 | ~268 | ~268 |
| **gross expectancy** | +0.0723 | +0.0860 | +0.0952 |
| **BASE net** | **+0.0316** | **+0.0453** | **+0.0544** |
| Alpha claimed | +0.032 | +0.045 | +0.054 |
| | **MATCH** | **MATCH** | **MATCH** |
| **STRESS net (2× cost)** | −0.0092 | +0.0045 | **+0.0137** |
| win rate | 0.510 | 0.485 | 0.473 |
| profit factor | 1.111 | 1.147 | 1.171 |
| DEV (≤2019) | +0.0189 | +0.0290 | +0.0426 |
| OOS (2020+) | +0.0474 | +0.0657 | +0.0693 |
| PRE-2021 | +0.0222 | +0.0339 | +0.0477 |
| POST-2021 | +0.0471 | +0.0641 | +0.0656 |

```
ALPHA_RESULT_REPRODUCED = YES
```

**One reported figure does not reproduce.** Alpha's verdict block states
`BEST_STRESS_NET ≈ +0.045R (2× cost)`. Doubling the cost removes `mean(cost/risk) = 0.0408R`, so the
correct 2R stress figure is **+0.0137R**, not +0.045R. (+0.045 is the *BASE* 1.5R number.) This is a
transcription error, not a code error — `dae_payoff.py` never computes a stress figure — but it
overstates cost robustness by a factor of three, and cost robustness is the binding constraint here.

---

## 3 — OCO EXECUTION AUDIT (§3)

Most of the OCO logic is genuinely conservative and I confirm it:

| ambiguity | Alpha's handling | my assessment |
|---|---|---|
| both activations in one M15 bar | episode **skipped** (8 episodes, 0.17%) | correct and conservative |
| activation + stop in one bar | cannot occur — that is the skipped case | sound |
| activation + target in one bar | booked as a win | sound: price must cross the entry to reach the target |
| target + stop in one later bar | resolved as **stop** | conservative |
| day / session boundary | none applied; index walk | consistent, documented |
| weekend | forward window walks bar index, so it spans weekends | consistent, documented |
| cost application | per trade, converted at that trade's own risk | correct |

**The defect: gap-through fills.**

```
episodes where the trigger bar OPENED beyond the activation level : 349  (8.65%)
   Alpha fills at the LEVEL. A real stop order fills at the OPEN.
   slippage if filled at the open : median 0.0943R · mean 0.1696R · p95 0.5588R
   concentrated on Mondays (153) and the Sunday re-open (97) — i.e. weekend gaps
```

```
AMBIGUOUS_EPISODES                          = 357  (8 same-bar-both + 349 gap-through)
EXPECTANCY_WITH_AMBIGUOUS_EPISODES_REMOVED  = +0.0460 R   (n = 3,684)
EXPECTANCY_WITH_WORST_CASE_ORDERING         = +0.0390 R   (gap fills at the open)
OCO_EXECUTION_INTEGRITY = FAIL
```

I call this FAIL rather than PASS because filling a gapped stop order at the untouched level is not a
modelling simplification — it books a price that was never available, on 8.65% of trades, worth **28% of
the entire edge**. Everything else in the OCO logic passes.

**Episode independence is weaker than claimed.** 4,644 of 4,664 consecutive anchors (99.6%) sit closer
than 96 bars apart, because a UTC trading day holds ~92 M15 bars while the horizon is 96 — and a Friday
anchor's window reaches into Monday. Episodes overlap slightly and, across weekends, substantially. All
inference below is therefore **week-clustered**, not iid.

---

## 4 — IS EXPECTANCY ACTUALLY > 0? (§4)

```
PRACTICALLY_PLAUSIBLE_POSITIVE_EXPECTANCY = YES
```

| target | mean net R | iid SE (t) | **week-clustered SE (t)** | **CI95** |
|---|---|---|---|---|
| 1.0R | +0.0316 | 0.0112 (+2.81) | 0.0107 (**+2.96**) | [+0.0106, +0.0525] |
| 1.5R | +0.0453 | 0.0129 (+3.52) | 0.0125 (**+3.62**) | [+0.0207, +0.0698] |
| 2.0R | +0.0544 | 0.0140 (+3.89) | 0.0136 (**+4.00**) | [+0.0278, +0.0811] |

Week-block bootstrap (4,000 resamples of 784 weeks): mean +0.0544, CI95 [+0.0270, +0.0814],
**P(mean ≤ 0) = 0.000**.

Clustering does not weaken this — the SE is slightly *smaller* than iid, so the dependence is not
inflating the result. **The expectancy is statistically positive and I will not soften that.** What
follows attacks the mechanism and the economics, not the sign.

---

## 5 — TAIL DEPENDENCE (§5) — and a correction to the diagnostic itself

```
TAIL_CLASSIFICATION = LEGITIMATE_POSITIVE_SKEW
```

| | 2R |
|---|---|
| net-R range | −1.647 … **+1.998 (wins are CAPPED at the target)** |
| top 0.5% (20 trades) of PnL | 18.1% |
| top 1.0% (40) | 36.2% |
| top 2.0% (80) | 72.2% |
| top 5.0% (201) | 179.9% |
| top 10% (403) | 351.0% |
| drop-best-1% | **+0.0346** |
| drop-best-2% | +0.0150 |
| drop-best-3% | −0.0050 |
| drop-best-5% | −0.0463 |
| **winsorized at 5th/95th pct** | **+0.0556** (vs +0.0544 raw — unchanged) |
| median net-R | −0.0442 |

**Alpha's `drop-best-5%` diagnostic is not valid for this payoff structure, and I can demonstrate it.**
I simulated a strategy with a *known, genuine, broad, completely tail-free* +0.057R edge and this exact
bounded payoff (win capped at +2R, loss −1R, win rate set to reproduce the edge):

```
true edge by construction : +0.0570 R
its drop-best-5%          : -0.0479 R   — negative in 97% of 400 simulations
```

Removing 5% of trades from a payoff capped at +2R mechanically removes ≈ 5% × 2R = **0.10R per trade,
about twice the entire edge**. Any strategy of this shape fails the test. The concentration figures
above (top 2% = 72% of PnL) are the same artefact: when the mean is 0.054R and a single win is 2R, a
handful of wins *must* dominate the sum.

The diagnostics that *are* valid here both pass: **winsorizing changes nothing** (+0.0556 vs +0.0544),
and the **maximum single trade is +2.0R** — there is no extreme observation to depend on. So this is a
genuine asymmetric-payoff distribution (WR 0.473, +2/−1) working as designed, not tail dependence.

**Alpha's conclusion ("thin, not fake") was right; the reasoning was wrong.** The edge is not thin
because of tails — it is thin because it is small.

---

## 6 — WHERE EXPECTANCY IS LOST (§6)

```
first-side-only (opposite extreme never reached after entry) : 0.782
opposite-side-after-trigger (stopped out)                    : 0.218
median hours from entry to the opposite extreme, when reached: 7.50 h
median hours from anchor to first activation                 : 4.25 h
resolved by target 9.9% · by stop 20.4% · UNRESOLVED AT 24h EXPIRY 69.7%
cost drag: mean 0.0408 R/trade — 43% of the gross expectancy
```

**Answer: neither of the two options the mandate offers.** It is not "many small whipsaws plus occasional
large continuation", and it is not "broadly favourable first-side persistence". At 2R, **69.7% of trades
never resolve at all** — they are marked to market at the 24h horizon, and that segment returns +0.1202R
while target-and-stop cancel out. The first side persists enough to avoid the opposite extreme 78% of the
time, but only 9.9% of trades ever reach the target.

---

## 7 — PAYOFF MONOTONICITY (§7)

```
PAYOFF_MONOTONICITY_INTERPRETATION =
  NOT greater exposure to rare extreme winners. The rise +0.032 -> +0.045 -> +0.054 is a progressive
  REPLACEMENT of the target/stop mechanism by the 24h TIME EXIT. Widening the target simply stops
  truncating the holds that carry the drift.
```

Gross expectancy decomposed by exit type:

| target | hit target | hit stop | 24h expiry | target contrib | stop contrib | **expiry contrib** | total |
|---|---|---|---|---|---|---|---|
| 1.0R | 25.9% | 17.5% | 56.6% | +0.2589 | −0.1753 | −0.0112 | +0.0723 |
| 1.5R | 15.2% | 19.4% | 65.4% | +0.2287 | −0.1939 | +0.0512 | +0.0860 |
| 2.0R | 9.9% | 20.4% | 69.7% | +0.1979 | −0.2036 | **+0.1009** | +0.0952 |

At 2R the target and the stop **cancel exactly** (+0.198 − 0.204 = −0.006) and the entire gross edge sits
in the time-exit. Combined with §5's winsorization result, this is *inconsistent* with "rare extreme
winners" and *consistent* with a small persistent drift being held for 24 hours.

**A labelling consequence the CEO should have:** at 2R this is not a "2R-target strategy". It is
"enter at the first-touched prior-day extreme, exit 24h after the day-open anchor, with a wide stop at
the opposite extreme" — the 2R target fires on one trade in ten.

---

## 8 — TEMPORAL STABILITY (§8)

```
CROSS_ERA_MECHANISM_STABLE = NO
```

| block | N | net R | WR | PF | top-1% PnL | week-clustered t |
|---|---|---|---|---|---|---|
| 2011–2013 | 649 | **+0.0827** | 0.470 | 1.268 | 0.22 | **+2.52** |
| 2014–2016 | 789 | +0.0280 | 0.464 | 1.085 | 0.63 | +0.87 |
| 2017–2019 | 805 | +0.0245 | 0.468 | 1.073 | 0.80 | +0.82 |
| 2020–2022 | 817 | +0.0351 | 0.457 | 1.106 | 0.55 | +1.11 |
| 2023–2026 | 973 | **+0.0981** | 0.499 | 1.333 | 0.19 | **+3.70** |

The sign is positive in all five blocks — that much of Alpha's claim holds. But the magnitude varies
**4×**, and across the nine years 2014–2022 the effect is +0.025 … +0.035 with t < 1.2, i.e. not
distinguishable from zero. The two strong blocks are the two strongest gold bull phases in the sample,
which is exactly what §9 predicts. **The sign is stable; the mechanism, as stated, is not.**

---

## 9 — CONTROLS (§9) — the decisive section

```
MARKET_SELECTION_INCREMENTAL_VALUE = YES vs random direction (+0.0377 R)
                                     NO  vs always-long      (-0.0009 R per trade)
```

| strategy (same anchors, same levels, same risk, same cost) | N | net R/trade | WR |
|---|---|---|---|
| **market-selected direction (the candidate)** | 4,033 | **+0.0544** | 0.473 |
| random direction, matched | 2,438 | +0.0167 | 0.456 |
| **always LONG at the prior-day high** | 2,524 | **+0.0553** | 0.483 |
| always SHORT at the prior-day low | 2,388 | −0.0090 | 0.426 |

And the candidate's own trades split by the side the market selected:

| target | LONG (n=2,073) | SHORT (n=1,960) | LONG − SHORT |
|---|---|---|---|
| 1.0R | +0.0599 (**t +3.89**) | +0.0016 (t +0.10) | +0.0583 |
| 1.5R | +0.0783 (**t +4.35**) | +0.0104 (t +0.57) | +0.0679 |
| 2.0R | +0.0857 (**t +4.41**) | +0.0214 (t +1.08) | +0.0644 |

**The entire edge lives on the long side at every payoff. The short side is statistically zero.** A plain
always-long buy-stop at the prior-day high matches the OCO's per-trade expectancy (+0.0553 vs +0.0544)
using only 63% of the trades. The OCO's extra ~1,500 short trades contribute nothing per trade.

So the claim *"market-selected direction beats random direction"* is **true** (+0.038R). But the claim it
was taken to support — that direction-agnostic selection is the source of the edge — is **not**. The
source is long-side drift over a 14-year gold bull market, which the OCO picks up through its long leg.
That also explains §8: the two strong era blocks are the two strongest trend phases.

**A comparison I withdraw.** I first ran a *paired* version of this — candidate versus always-long on the
2,524 episodes where the prior-day high was touched — which gave a dramatic −0.1385R for market
selection. That figure is confounded: conditioning on "the prior-day high was eventually touched" selects
days that reversed upward, which unfairly penalises the candidate's short trades. It should not be cited,
and I am not citing it. The unpaired strategy-level comparison and the side decomposition above are both
clean, and they carry the finding on their own.

---

## 10 — COST ROBUSTNESS (§10)

```
BASE_NET (2R)             = +0.0544 R
STRESS_NET (2R, 2x cost)  = +0.0137 R      <- Alpha reported +0.045; not reproducible
BREAK_EVEN_COST           = 0.979 price units/trade = 2.34x BASE, 1.17x STRESS
additional adverse execution that erases the edge = 0.560 USD = 5.6 pips/trade
```

Cost already consumes **43% of gross expectancy** at BASE. The apparent comfort — "only 2.3× cost" — is an
artefact of the 163-pip risk unit; in absolute terms the whole buffer is **5.6 pips per trade**.

**Stacked with the other governed corrections (§3, §11), the buffer disappears:**

| variant (2R) | N | net R | week-t | CI95 |
|---|---|---|---|---|
| as Alpha ran it | 4,033 | +0.0544 | +4.00 | [+0.0278, +0.0811] |
| + research holdout removed | 3,820 | +0.0442 | +3.16 | [+0.0168, +0.0717] |
| + gap fills at the bar open | 3,820 | +0.0313 | +2.24 | [+0.0039, +0.0586] |
| + **STRESS cost** | 3,820 | **−0.0113** | −0.81 | [−0.0388, +0.0162] |

Holdout-clean with realistic fills, **break-even cost = 0.785 USD = 0.94 × STRESS**. The governed stress
assumption alone erases the edge; **3.7 pips of additional adverse execution** does it.

---

## 11 — ECONOMIC SIGNIFICANCE (§11)

```
trades/year               ~268
net R/year                median +9.52 · mean +10.86
worst year -7.92 R · best year +38.42 R · negative years 3 of 16
max drawdown              22.83 R  (total +219.58 R over 4,033 trades)
longest losing sequence   13 consecutive losers
MaxDD / median annual R   2.4x   <- ~2.4 years of median profit to recover one drawdown
```

**And the unit matters.** 1R here is a median **163 pips**. +0.054R per trade is **8.8 pips per trade**
against a 4.2-pip modelled cost — an edge-to-cost ratio of 2.1×, before the §3 and §10 corrections. On
holdout-clean data with realistic fills it is **5.1 pips per trade against 4.2 pips of cost**.

```
STANDALONE_ECONOMIC_VALUE = NONE
PORTFOLIO_SLEEVE_VALUE    = MARGINAL
```

**Standalone: NONE.** A strategy whose entire buffer is ~1 pip per trade over modelled cost, that needs
2.4 years to recover a drawdown, and that turns negative at the *governed* stress assumption, cannot be
Strategy #2 at any size.

**Sleeve: MARGINAL, not zero — but for a reason that reduces its value further.** §9 shows this is a
long-gold drift harvester. Its diversification value against any other long-biased sleeve is therefore
low, and the lab's one deployed edge (S5) would need to be checked for exactly that overlap before this
could be called complementary. A sleeve that is a proxy for "long gold" adds beta, not alpha.

---

## 12 — GOVERNANCE FINDING: THE RESEARCH HOLDOUT WAS CONSUMED

Alpha's loader `cur_data.load_m15()` reads the full M15 file with **no truncation**, so the scan ran
through 2026-07-27. The program constant `RESEARCH_HOLDOUT_CUTOFF_UTC = 2025-10-23T09:15:00Z`
(`edge_research/_common.py:43`) marks everything after that date as escrowed. I respected this firewall in
my own long-horizon scan one mandate ago, at the cost of nine months of data.

```
episodes inside the protected holdout : 213 of 4,033 (5.28%)
expectancy on holdout episodes        : +0.2374 R
expectancy excluding the holdout      : +0.0442 R
```

The holdout period runs at **5.4× the expectancy of the rest of the sample** and inflates the headline by
+0.0102R at every payoff (1R +0.0316→+0.0224, 1.5R +0.0453→+0.0349, 2R +0.0544→+0.0442). I report this as
a finding, not an accusation — the loader is shared infrastructure and the truncation is not automatic. It
does mean the program's holdout is **no longer clean for this architecture**, and any future validation of
it needs a fresh escrow.

---

## 13 — VERDICT

```
INDEPENDENT_OCO_HARVEST_REPLICATION_V1_COMPLETE = YES

OCO_SPEC_REPRODUCIBLE   = YES   (OCO_SPEC_HASH 26827e79511e1ac5…)
ALPHA_RESULT_REPRODUCED = YES   (exact, independent implementation)
OCO_EXECUTION_INTEGRITY = FAIL  (gap-through fills, 8.65% of trades, 28% of the edge)

BASE_EXPECTANCY_1R      = +0.0316 R   (holdout-clean +0.0224)
BASE_EXPECTANCY_1_5R    = +0.0453 R   (holdout-clean +0.0349)
BASE_EXPECTANCY_2R      = +0.0544 R   (holdout-clean +0.0442)
STRESS_EXPECTANCY_2R    = +0.0137 R   (holdout-clean +0.0016; with realistic fills -0.0113)
                                       Alpha's reported +0.045 does not reproduce.
CI95_2R                 = [+0.0278, +0.0811] as run
                          [+0.0168, +0.0717] holdout-clean
                          [+0.0039, +0.0586] holdout-clean + realistic fills

PRACTICALLY_PLAUSIBLE_POSITIVE_EXPECTANCY = YES  (week-clustered t +4.00; bootstrap P(<=0) = 0.000)

MARKET_SELECTION_INCREMENTAL_VALUE = YES vs random (+0.0377 R)
                                     NO  vs always-long (+0.0553 vs +0.0544 per trade)
                                     -> the stated mechanism is REFUTED; the edge is long-side drift
                                        (LONG +0.0857 t +4.41 · SHORT +0.0214 t +1.08)

TAIL_CLASSIFICATION       = LEGITIMATE_POSITIVE_SKEW
                            (winsorized mean unchanged; max trade +2.0R; drop-best-5% is an invalid
                             diagnostic for a capped payoff — demonstrated on a tail-free simulation)

CROSS_ERA_MECHANISM_STABLE = NO  (sign stable 5/5; magnitude varies 4x; 2014-2022 all t < 1.2)

STANDALONE_ECONOMIC_VALUE = NONE
PORTFOLIO_SLEEVE_VALUE    = MARGINAL

STATISTICAL_VERDICT = INFORMATION_ONLY
READY_FOR_RED_TEAM  = NO
```

**Why INFORMATION_ONLY and not FAIL:** it reproduces exactly, it is statistically positive with clustered
inference and a block bootstrap, it is not outlier-dependent, and it is positive in all five era blocks.
Calling it FAIL would misdescribe a real measurement.

**Why not REPLICATION_PASS:** the mechanism Alpha named is refuted (long drift, not direction selection);
the execution model books unavailable prices on 8.65% of trades; the protected holdout was consumed and
carries 5× the expectancy; the reported stress figure is wrong by 3×; and on holdout-clean data with
realistic fills at the governed stress cost the expectancy is **−0.011R**.

**Why not READY_FOR_RED_TEAM:** Red Team's time should not be spent adjudicating an architecture whose
own mechanism claim has already failed and whose economics vanish under the lab's own governed stress
assumption. If the CEO wants this pursued, the honest next object is not this OCO — it is the question
**§9 exposes**: *is there a persistent long-side drift harvest at the prior-day high, and is it anything
more than gold beta?* That is a different, simpler, and more testable claim.

**No promotion.** Not added to StrategyCatalog. Not called Strategy #2. Nothing modified: S5, Q4,
AI Trader, P007, MGMT-004, MT5, StrategyCatalog. No closed factory reopened. No self-improvement of the
architecture was attempted — no anchor, level, filter, regime, hour, stop, target or time-stop was
changed, and it was not combined with S5.

```
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```
