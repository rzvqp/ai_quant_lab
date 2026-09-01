# STAT_GC_XAU_PRICE_DISCOVERY_DATA_GATE_V1 — REPORT

**Mandate:** `GC_XAU_PRICE_DISCOVERY_DATA_GATE_V1` — data feasibility only. No strategy testing, no lag
search, no acquisition.
**Division:** Statistician. **Date:** 2026-09-01.
**Code:** `statistician/gc_gate/` — `probe.py`, `probe2.py` (data characterisation only).

## HEADLINE

**Yes, this can be tested cheaply — but not for the reason the branch list assumes.**

Using the 11-session GC sample already on disk, I measured rather than assumed the three things this
decision turns on:

| measurement (11 overlapping sessions, M15) | value | consequence |
|---|---|---|
| GC↔XAU **return** correlation | **0.9982** | GC *price* is a re-encoding of data already exhausted |
| GC↔XAU **level** correlation | 0.9996 | same |
| GC↔XAU log-**volume** correlation (R²) | **0.822 (0.676)** | **~32% of real COMEX volume is information the lab does not currently hold** |
| sd of the GC−XAU return residual | **3.92 pips = 0.4% of XAU return variance** | the whole divergence branch has almost no headroom |
| median \|residual\| vs governed cost | **2.35 pips vs 4.2 pips** | the typical dislocation is *smaller than the cost of trading it* |
| residual lag-1 autocorrelation | **−0.356** | bid-ask bounce / non-synchronous quoting, not a convergence process |

**The genuinely new information in GC is VOLUME and OPEN INTEREST, not PRICE.** Every price-based branch
(lead/lag, divergence, basis) is operating on a residual that is 0.4% of variance and mean-reverts inside
one bar in a way that looks like microstructure noise. The volume channel is untouched and cheap.

---

## 1 — EXISTING GOVERNED DATA (§2)

```
GC_DATA_ALREADY_AVAILABLE = NO  (a 2-week sample exists; it is not a governed research dataset)
```

| | |
|---|---|
| what exists | Databento GLBX.MDP3 **MBO sample**, GCQ6 outright (instrument_id 42011464) |
| location | a prior session's **temporary scratchpad** — not committed, not in any data manifest |
| raw | 11 files `glbx-mdp3-2026{0629..0710}.mbo.dbn.zst`, ~1.0 GB, verified present on disk |
| built | `gc_15m.csv`, **896 M15 bars**, sha256 `ed739fc8a280aedd3d28261ff9f6b19b…` |
| **GC_DATA_RANGE** | **2026-06-29 → 2026-07-10 — 11 sessions** |
| **GC_DATA_FIELDS** | `ts, open, high, low, close, volume (real traded contracts), ntrades` |
| timezone | UTC (Databento `ts_event`, nanoseconds) |
| contract representation | single front-month outright; **no continuous series, no roll encountered** |
| bid/ask, aggressor | **NO** (MBP-10 not carried into the build; aggressor inferable from raw MBO only) |
| open interest | **NO** |
| gaps | everything outside those 11 sessions is missing; one weekend boundary only |

**Paired XAU spot (governed):** `OANDA_XAUUSD_M15.csv`, sha256 `57f4ed95…`, **355,696 bars,
2011-07-26 → 2026-07-27**, UTC, 0 duplicates, uniform ~23,600 bars/year, no structural holes (audited two
mandates ago). Also M5 2021-07→2026-07, and H1/H4/D1 builds.

**Prior evidence that must inform this decision.** Two independent discovery runs on this exact MBO sample
(2-day, then 11-session/122,291 anchors) both returned **NEGATIVE** — no stable pre-price signal; features
flip sign day to day; 0 of 29 replicate across days. Alpha's own `GOLD_GC_DATA_AUDIT_V1` then classified
the sample **TIER_C for research** and correctly declined to run a discovery on 42 single-period events.
I confirm all of that: the sample is real, gate-clean, and scientifically unusable for this question.

---

## 2 — CAUSAL TIMESTAMP ALIGNMENT (§6) — tested, not assumed

```
CAUSAL_TIMESTAMP_ALIGNMENT_FEASIBLE = YES
```

Over the 11-session overlap: **896 GC bars, 896 XAU bars, 896 exact UTC stamp matches (100%).** Both
series bucket on the same 15-minute UTC grid; a same-stamp join is exact with no resampling. The GC bar
spacing shows 886 × 15 min, 8 × 75 min (the daily ~1h CME maintenance halt) and 1 × 3195 min (the
weekend) — and XAU carries the same holes, because both follow the same NY-close convention.

Requirements for a real build:

- **Compare on bar CLOSE time (stamp + 15 min), via a backward as-of join** — the convention this codebase
  has already ratified (`merge_asof(direction="backward")` on `close_time`). Both files stamp the bar
  **open**, so a naive same-stamp join of a *derived* quantity would leak.
- Keep an explicit **session mask**: CME Globex Sun 18:00 ET → Fri 17:00 ET with a 17:00–18:00 ET daily
  halt; OANDA XAU has its own rollover break. Both are ET-anchored, so both shift with **US DST** — never
  hard-code a UTC hour for a session boundary.
- **Caveat I must flag:** this sample contains **one** weekend boundary. Weekly-open alignment (CME reopens
  before OANDA in some conventions) is therefore **under-tested**. It is a first-class acceptance gate for
  any acquired dataset, not something this probe settled.

---

## 3 — MINIMUM VIABLE DATASET (§3, §11)

```
IS_TICK_DATA_REQUIRED    = NO   (for the tradeable formulation; YES only for a literal sub-second lead measurement)
IS_MBO_REQUIRED          = NO
IS_VOLUME_REQUIRED       = YES  (it is the entire point — see §1 headline)
IS_OPEN_INTEREST_REQUIRED = NO for the first cycle; YES for branch E
```

**The distinction that decides the budget.** Two different questions hide behind "GC → XAU price
discovery":

1. *"Does GC print the move first, by milliseconds to seconds?"* — Almost certainly yes; it is the standard
   futures-lead result for a liquid pair, and arbitrage desks close the gap immediately. **M15/M5 bars
   cannot resolve a lead measured in seconds** — at bar scale the two series are contemporaneous (return
   correlation 0.9982). Testing it needs tick data. **And it is not monetizable by this lab**: no
   colocation, retail MT5 execution, and a governed round-trip cost of ~4.2 pips against a median
   dislocation of 2.35 pips.
2. *"Does GC **state** — volume, participation, impulse — condition the XAU path over the next 15 min to
   24 h?"* — This runs entirely on **M15 OHLCV + volume**, needs no microstructure data, and is the
   formulation that matches the lab's one validated edge (S5 is event-revealed, not
   direction-predictive).

**The cheap data cannot answer the classic question, and the classic question is not the tradeable one.**
Question 2 is the one to fund.

---

## 4 — CONTINUOUS FUTURES (§4)

```
CONTINUOUS_SERIES_SAFE_FOR_LEAD_LAG = YES   (returns only, roll days excluded, causal roll rule)
CONTINUOUS_SERIES_SAFE_FOR_BASIS    = NO
```

Back-adjustment (panama/ratio) applies a constant offset to the *past* at each roll. Within any non-roll
segment the adjusted **returns are identical** to the actual contract's returns, so a return-based
lead/lag or volume study is unaffected — provided (a) no return is computed *across* a splice from raw
levels, and (b) roll days are excluded from the episode set, which is the cheap and robust fix.

**Levels are a different matter.** The adjusted price is not a tradable price; the offset is arbitrary
(anchored to the most recent contract) and **is rewritten retroactively every time a new roll occurs** — a
series built today will not equal a series built next quarter. Any basis, EFP, or futures-minus-spot study
computed on an adjusted continuous series is measuring an artefact.

| research object | continuous adjusted | needs actual contract prices |
|---|---|---|
| GC→XAU lead/lag on returns (A) | **safe** | no |
| GC volume state → XAU response (D) | **safe** (volume is never adjusted) | no |
| GC−XAU return divergence (B) | safe on returns | no |
| **futures/spot basis (C)** | **UNSAFE** | **yes** + expiry date + a rate series |
| open-interest state (E) | n/a — OI is per contract | **yes** |
| price-discovery classification (F) | safe on returns | no |

**Additional warning for basis (C):** the GC−XAU spread is dominated by the deterministic **cost of carry**
(≈ rate × time-to-expiry). My probe shows it directly: mean basis **+11.77 USD**, drifting **−5.99 USD over
11 sessions** as expiry approaches. A basis study that does not remove the carry term first will simply
rediscover the policy rate and the roll cycle.

---

## 5 — CAUSAL CONTRACT SELECTION (§5)

```
RECOMMENDED_CAUSAL_CONTRACT_SELECTION =
  the outright whose PRIOR-SESSION open interest is highest (volume as tie-break), applied with a
  ONE-DIRECTIONAL LATCH (never roll back), with a deterministic fallback: force the roll by the last
  business day before First Notice Day. All inputs lagged one full session. Roll days excluded from
  episodes.
```

Why: OI-based selection tracks where the market actually is, uses only information published before the
session opens (CME preliminary OI is released the following morning — so it must be lagged one session,
not used same-day), and the latch prevents a liquidity wobble from rolling the series back and forth.
Volume alone is noisier day to day; a pure calendar rule is fully causal but ignores real liquidity
migration and would hold a dying contract. The FND fallback guarantees the series never sits in a
delivery-eligible contract.

**Explicitly rejected: any "highest volume/OI over the contract's life" or "most active in hindsight"
selection.** That reads the future and is exactly the class of error this division exists to catch.

---

## 6 — HISTORY REQUIREMENT (§7)

```
MINIMUM_ACCEPTABLE_HISTORY = 10 years (2015 -> present) -- spans pre-2021 and post-2021 and 3+ regimes
PREFERRED_HISTORY          = 14+ years (2011 -> present) -- matches the governed XAU M15 exactly
```

| horizon | independent daily episodes | regime coverage | verdict |
|---|---|---|---|
| 5 years | ~1,300 | post-2021 only | **insufficient** — cannot answer pre-2021, the failure mode of every native-M5 result |
| 10 years | ~2,600 | 2015-2019 range, 2020 shock, 2021-2025 bull | **acceptable** |
| **14+ years** | **~3,650** | + 2011-2013 bear, 2013-2015 grind | **preferred** — and it pairs 1:1 with the existing XAU M15 |

The 14-year target is not ambition, it is symmetry: the governed XAU M15 starts 2011-07-26, and matching
it means every GC episode has a spot counterpart and the whole existing DEV/OOS and era-block machinery
transfers unchanged.

---

## 7 — FUTURE RESEARCH BRANCHES (§8) — ranked, with two demotions

```
TOP_3_FUTURE_GC_XAU_BRANCHES = D (volume-confirmed move -> XAU response)
                               A (GC impulse -> delayed XAU response)
                               E (GC open-interest state x price move)
```

| rank | branch | plausibility | data need | value | confound risk |
|---|---|---|---|---|---|
| **1** | **D — GC volume-confirmed move → XAU response** | HIGH | M15 OHLCV+volume (Tier 1) | HIGH | moderate |
| **2** | **A — GC impulse → delayed XAU response** | MEDIUM | M15 OHLCV (Tier 1) | MEDIUM | **HIGH** |
| **3** | **E — GC open-interest state × price move** | MEDIUM | + daily OI (Tier 1) | MEDIUM | moderate |
| 4 | C — futures/spot basis state | MEDIUM | actual contracts + expiry + rates (Tier 2) | MEDIUM | **HIGH** (carry) |
| 5 | B — GC−XAU divergence → convergence | **LOW** | Tier 1 | **LOW** | HIGH |
| 6 | F — GC-first / XAU-first classification | HIGH (as physics) | **tick (Tier 3)** | **LOW** (unmonetizable) | low |
| — | **G — macro-window GC→XAU transmission** | — | **BLOCKED** | — | — |

**Why D is first.** It is the only branch that uses the channel my probe shows is actually new (real
traded volume, ~32% of its variation absent from the lab's tick-count series), and its shape —
*an event in GC reveals direction, the XAU response is then measured* — is the conditional-response frame
that produced S5, the lab's only validated edge, and that four direction-prediction scans have failed to
beat.

**Why B is demoted from third to fifth.** The measurements above bound it before anyone spends a cycle:
the GC−XAU return residual is **0.4% of XAU return variance**, its **median absolute value (2.35 pips) is
smaller than the governed round-trip cost (4.2 pips)**, and its lag-1 autocorrelation is **−0.356** — the
signature of bid-ask bounce and non-synchronous quoting between two venues, not of a convergence process
a trade could ride. The lab has also already closed `CROSS_MARKET_RELATIVE_RESPONSE_FACTORY_V1`
(XAU-vs-DXY dislocation residual) with `SURVIVED=0` and `CROSS_MARKET_INCREMENTAL_INFORMATION = NO`. GC is
a *tighter* pair than DXY, so its residual is smaller and faster, not richer.

**Why G is blocked.** Branch G requires the economic calendar. I established two mandates ago
(`8488ab7`) that the governed calendar and every governed XAU price file **overlap by zero events**.
G cannot be run at all until that is fixed, regardless of what GC data is acquired.

---

## 8 — MATCHED CONTROLS (§9) — the mandatory distinction

**Requirement: separate "GC LEADS XAU" from "BOTH RESPOND TO THE SAME INFORMATION".** This is not a
robustness check to add later; it is the identifying restriction, and it must be built before the first
result is looked at. My own scheduled-event gate made the same point in reverse and it cost that branch
nothing to state early.

The identifying control, stated concretely:

> **Condition on XAU's own bar-*t* return and volume.** If GC moved by *x* in bar *t* and XAU already moved
> by *y* in the same bar, the question is whether *x* adds information about XAU's move in *t+1…t+k*
> **once *y* is held fixed**. If it adds nothing, the two venues simply responded to the same information
> and there is no price discovery to harvest.

Mandatory alongside it:

| control | why |
|---|---|
| **XAU bar-*t* return and volume** | the identifying restriction above — without it every result is co-movement |
| **placebo lead**: repeat with GC *lagged* instead of led | a symmetric effect proves contemporaneity, not lead |
| **reverse test**: does XAU lead GC by the same measure? | if symmetric, there is no discovery, only correlation |
| **time-of-day** | fix the anchor to one clock hour, as in the long-horizon scan — designs the session confound out rather than controlling it |
| **trailing volatility** | GC volume and XAU movement are both volatility-driven; without this, any volume result is a volatility result |
| **trend state** | the OCO replication showed how easily 14 years of gold drift masquerades as a mechanism |
| **roll-day exclusion** | roll days have anomalous volume and a price discontinuity |

Independence: **one anchor per session at a fixed UTC hour, non-overlapping forward windows, primary
N = independent episodes, month- or week-cluster-robust inference** — the discipline established in
`74541e7`, which showed the program's earlier |z| values were inflated by overlap.

---

## 9 — ACQUISITION OPTIONS (§10) — nothing acquired

| source | fields | history | contracts | vol | OI | access model | limitations |
|---|---|---|---|---|---|---|---|
| **Databento GLBX.MDP3, `ohlcv-1m` + `definition` + `statistics`** | OHLCV per instrument_id; definitions give expiry/contract identity; statistics carry daily OI/settlement | GLBX advertised from **2010** (confirm against the availability endpoint before purchase) | **individual outrights** — build the continuous series yourself, causally | **real** | **yes** (statistics) | usage-based $/GB; **the lab already has an account, a validated DBN parser and a working ingest** | OHLCV schema has no bid/ask; you must build the roll |
| CME DataMine | official OHLCV, settlement, OI | deep | individual | yes | yes | subscription/licence | heavier licensing and tooling; slower to first result |
| CFTC **Commitments of Traders** | positioning by trader category | 1986→ | aggregate | — | **yes, weekly** | **free, authoritative** | weekly and lagged 3 days — a slow positioning state, not a bar-scale signal |
| Barchart / FirstRate / Kibot | intraday OHLCV, continuous + individual | 10-20y typical | both | yes | varies | one-off or subscription | roll methodology often opaque — a disqualifier under §12 unless documented |
| Norgate | continuous futures, OI | deep | continuous-focused | yes | yes | annual subscription | intraday depth limited; equities/futures EOD orientation |
| **TradingView (already owned)** | GC1! / individual contracts, OHLCV | plan-dependent, intraday depth limited | continuous + individual | yes | no | **zero marginal cost — the lab drives it over MCP today** | roll rule not documented; intraday history usually too shallow for 14 years; **verifying it would mean changing the symbol on the CEO's live working chart, which I did not do** |

**Not recommended:** scraping retail sites for futures data. Undocumented roll rules and unverifiable
provenance fail §12 before any research starts.

---

## 10 — ACCEPTANCE GATES FOR ANY ACQUIRED DATASET (§12)

No research begins until all of these pass, and they are cheap to run:

1. **Timestamp integrity** — strictly increasing, UTC, no duplicates, bar spacing exactly the nominal
   interval except at documented session halts.
2. **No duplicate bars** — on (instrument_id, timestamp).
3. **OHLC validity** — `low ≤ min(open, close)`, `high ≥ max(open, close)`, `high ≥ low`, no zero/negative
   prices.
4. **Volume semantics** — real traded contracts, not tick count; documented whether it includes block/EFP
   trades; sanity-check the daily total against CME published volume for a sample of days.
5. **Contract identity** — every bar carries an instrument identifier resolvable to a contract month and
   an expiry date via a definitions file.
6. **Roll transparency** — the roll rule is code the lab wrote, causal, and reproducible; a vendor's
   undocumented continuous series is **rejected**.
7. **Timezone** — UTC storage, with DST-aware session boundaries derived from ET, never hard-coded UTC
   hours.
8. **Missing bars** — quantified per year; a session-calendar reconciliation against the CME holiday
   calendar; **explicit weekly-open alignment check against XAU** (the gap this probe could not close).
9. **Source provenance** — vendor, dataset, schema, query, extraction date recorded.
10. **Hash/freeze** — sha256 of every file, recorded in a manifest, with a declared research holdout
    **before** the first look. *(The XAU holdout is already compromised for the OCO architecture —
    see `94dff78`. Do not repeat that here.)*

---

## 11 — TIERS AND RECOMMENDATION (§13)

### TIER_1 — minimum-cost falsification dataset
**Databento GLBX.MDP3 `ohlcv-1m` for GC outrights, 2011→present, + `definition` + `statistics` (daily OI).**
Aggregate to M15 in-house.
- **Enables:** branches **D, A, E**, the full matched-control battery, roll construction, 14-year DEV/OOS
  and era blocks paired 1:1 with the governed XAU M15.
- **Cannot answer:** sub-second lead-lag (F), true basis without a rate series (C), anything
  aggressor/order-flow.
- **Justified now: YES.**

### TIER_2 — preferred research-quality dataset
Tier 1 **+** a rate/carry series and CFTC COT (both free or near-free) **+** `ohlcv-1s` or `trades` for a
**bounded** subset of high-information windows.
- **Enables:** branch C properly (carry removed), tighter timing resolution where it matters.
- **Justified now: NO — only if Tier 1 finds something in D or A worth resolving more finely.**

### TIER_3 — advanced microstructure dataset
Full-history MBO / MBP-10.
- **Enables:** branch F, aggressor-side and book-state work.
- **Justified now: NO, and with evidence rather than on cost grounds.** This lab has already run *two*
  independent microstructure discovery experiments on GC MBO — 2 days, then 11 sessions and 122,291
  anchors — and both returned **NEGATIVE**: no stable pre-price signal, features flipping sign day to day,
  0 of 29 replicating across days. Buying more of the same data class to re-ask a question it has already
  answered twice is the weakest use of the budget on this list.

```
RECOMMENDED_DATA_TIER = TIER_1
```

---

## 12 — CEO QUESTIONS (§14)

**Can we test a meaningful GC→XAU price-discovery hypothesis with material historical depth without buying
expensive tick/MBO data?**

**YES — for the formulation worth testing.** GC *state* (volume, impulse, participation) → XAU forward
path runs on M15 OHLCV+volume with 14 years of depth, at Tier-1 cost, on infrastructure the lab already
has. **NO** for the literal microsecond lead-lag question — and that question is not monetizable here
anyway: the median M15 dislocation is 2.35 pips against a 4.2-pip governed cost.

**Is this a genuinely new information source relative to the exhausted price-only XAU research?**

**PARTIALLY — and the part that is new is not the part the branch list emphasises.**

- **GC price: NOT new.** Return correlation 0.9982, level correlation 0.9996. GC price is, to a very good
  approximation, XAU price re-encoded. Branches built on GC price (A on returns alone, B, F) are re-running
  the exhausted price-only campaign in a second coordinate system.
- **GC volume: GENUINELY NEW.** The lab has never held a real traded-volume series — OANDA "volume" is a
  tick count from one retail broker. Real COMEX volume shares only **R² = 0.676** with it, so roughly a
  third of its variation is information the lab does not currently possess, from the venue where gold's
  price is actually formed.
- **Open interest: GENUINELY NEW**, and unavailable anywhere in the lab today.

So the honest framing is not "GC leads XAU". It is: **for the first time the lab could observe how much
gold is actually being traded, and by how many participants.** That is the new variable. Everything else
on offer is a second copy of the price.

**Estimated research value: MEDIUM.** Not HIGH — the price channel is a near-duplicate, the residual has
no headroom, three of the seven branches are bounded or blocked, and the microstructure route already has
two negatives against it. Not LOW — the volume and OI channels are real, previously unavailable, cheap,
and they fit the one architectural frame (event-revealed conditional response) that has ever worked here.

---

## 13 — REQUIRED OUTPUT (§17)

```
GC_XAU_PRICE_DISCOVERY_DATA_GATE_V1_COMPLETE = YES

GC_DATA_ALREADY_AVAILABLE = NO   (2-week ungoverned sample only)
GC_DATA_RANGE  = 2026-06-29 .. 2026-07-10 (11 sessions, 896 M15 bars, GCQ6 outright)
GC_DATA_FIELDS = ts, OHLC, volume (real traded contracts), ntrades ; no bid/ask, no OI, no roll

CAUSAL_TIMESTAMP_ALIGNMENT_FEASIBLE = YES  (896/896 exact UTC stamp matches; join on bar CLOSE via
                                            backward as-of; weekly-open alignment still to be gated)

IS_TICK_DATA_REQUIRED     = NO   (YES only for a literal sub-second lead measurement, which is not monetizable here)
IS_MBO_REQUIRED           = NO
IS_VOLUME_REQUIRED        = YES  (it is the only genuinely new channel)
IS_OPEN_INTEREST_REQUIRED = NO for cycle 1; YES for branch E

MINIMUM_ACCEPTABLE_HISTORY = 10 years (2015 -> present)
PREFERRED_HISTORY          = 14+ years (2011 -> present, pairing 1:1 with the governed XAU M15)

TOP_3_FUTURE_GC_XAU_BRANCHES = D (GC volume-confirmed move -> XAU response)
                               A (GC impulse -> delayed XAU response, same-bar XAU control mandatory)
                               E (GC open-interest state x price move)
   demoted with evidence: B (residual = 0.4% of variance, median 2.35p < 4.2p cost, lag-1 AC -0.356)
                          C (dominated by cost of carry; needs actual contracts + rates)
                          F (needs tick; unmonetizable at 4.2p cost)
   BLOCKED: G (requires the economic calendar, which is DATA_BLOCKED per 8488ab7)

TIER_1_DATASET = Databento GLBX.MDP3 ohlcv-1m (GC outrights) + definition + statistics(OI), 2011->present
TIER_2_DATASET = Tier 1 + rate/carry series + CFTC COT + ohlcv-1s/trades on bounded windows
TIER_3_DATASET = full-history MBO / MBP-10   [NOT justified: already NEGATIVE in two prior experiments]

RECOMMENDED_DATA_TIER    = TIER_1
DATA_ACQUISITION_REQUIRED = YES
ESTIMATED_RESEARCH_VALUE  = MEDIUM
READY_FOR_GC_XAU_ALPHA_SCOUT = NO  (blocked on Tier-1 acquisition + the §10 acceptance gates)

NEXT_AUTHORIZED_ACTION = NONE -- CEO DECISION REQUIRED
```

**Disclosure.** The characterisation in §1/§2/§7 used the 11-session GC sample and the overlapping XAU
M15 bars. Those sessions (2026-06-29 → 07-10) fall **inside** the research-holdout window
(`RESEARCH_HOLDOUT_CUTOFF_UTC = 2025-10-23`). What I ran on them is data characterisation — series
correlations, stamp alignment, residual magnitude — **not a hypothesis test**, and it consumes no DEV/OOS
structure. I flag it because the holdout's status matters and it should be recorded, not assumed.

**Limits of these measurements.** 11 sessions, one weekend, a single volatility regime. The price and
volume correlation structure is a market-structure property and is unlikely to move much; the **residual
magnitude will scale with volatility**, so the 3.92-pip figure is indicative, not a constant. None of
these numbers is a research result and none should be cited as one.

**Protection (§15, §16).** No strategy backtest, no lag search, no lead/lag optimisation, no GC strategy.
No data acquired. DXY, OCO, L1, P2, V2-4 and Family E not reopened. Not modified: S5, Q4, AI Trader, P007,
MGMT-004, MT5, StrategyCatalog. The CEO's live TradingView chart was **not** touched. No promotion.
