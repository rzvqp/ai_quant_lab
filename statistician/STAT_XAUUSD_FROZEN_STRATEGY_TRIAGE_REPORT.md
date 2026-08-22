# STAT — XAUUSD FROZEN STRATEGY INVENTORY + VALIDATION PRIORITY TRIAGE

**Mandate ID:** `STAT-XAUUSD-FROZEN-STRATEGY-TRIAGE-001`
**Division:** Statistician (independent statistical validation)
**Date:** 2026-08-22
**Repositories inspected:** `ai_quant_lab-alpha-automation` @ `0c5d10e` (branch `alpha-automation-v1`),
`ai_quant_lab-research-main`, `ai_quant_lab`

**Scope directives honoured:** `INVENTORY_FIRST` · `NO_NEW_ALPHA_DISCOVERY` · `NO_STRATEGY_RETUNING` ·
`NO_PARAMETER_SEARCH` · `AUDIT_EXISTING_FROZEN_STRATEGIES` · `S5_IS_BENCHMARK` · `S5_NOT_REOPENED` ·
`EVIDENCE_QUALITY_OVER_HEADLINE_WR` · `FREQUENCY_REPORTED` · `PORTFOLIO_COMPLEMENTARITY_REPORTED` ·
`NO_AI_TRADER` · `NO_MT5` · `NO_DEMO` · `NO_LIVE`

---

## 0 — TERMINAL STATUS

```
FROZEN_STRATEGY_TRIAGE_COMPLETE
VALIDATION_WORTHY_EXISTING_CANDIDATES_FOUND
N_VALIDATION_WORTHY = 1
```

**Tier A (validation-ready): EMPTY.** The single validation-worthy candidate is `H4-bo-raw-S`, and it is
**Tier B (audit-worthy)**, not Tier A — two required risk metrics were never computed by Alpha, and its
headline win rate is published inconsistently across two artifacts in the same commit.

I deliberately name **one** priority, not three (§19). A second and third are listed as *blocked*, with
their blocker identified, and I state explicitly that further Statistician or Red Team work on them cannot
proceed until the CEO resolves an evidence-availability question that is not mine to decide.

---

## 1 — OFFICIAL INVENTORY AND ITS FIRST DEFECT

Alpha's reports assert, verbatim and repeatedly, that *"the 9 frozen strategies are unaltered"* — in at
least seven separate reports, citing *"§31"* of a mandate.

**No enumeration of those nine exists in any repository artifact.** I searched every `.md`, `.py` and
`.json` in the Alpha repo. The count is asserted; the list is not recorded. There is no strategy registry,
no frozen-candidate manifest, and no catalog entry for any of them.

**Governance finding (non-blocking, but real):** a portfolio referred to by count and never by identity
cannot be audited by anyone but its author. I reconstructed the inventory from named references across the
report corpus and verified each against code and machine-written records. The reconstruction below is my
best mechanical recovery; it is **not** an authoritative list, because none exists.

Corroborating fact: in `ai_quant_lab-research-main`, `ai_trader/new_brain_live/strategy_platform/` contains
**exactly one** implemented strategy — `s5_opening_range_breakout.py`. No Alpha candidate has a runtime
identity anywhere.

### 1.1 Reconstructed inventory (12 strategy-level objects found)

| # | ID | Side | Edge TF | Source commit | Machine record |
|---|---|---|---|---|---|
| 1 | `H4-bo-raw-S` | SHORT | H4 | interim H4/H1 campaign | `econ_campaign.json`, `deepen_econ.json` |
| 2 | `H1-hllh-S` | SHORT | H1 | same | `deepen_econ.json` |
| 3 | `H1-B-bo-acc-SHORT` | SHORT | H1 | H1 pro-trend mandate | superseded by #1 |
| 4 | `HR-TU-pb-L` | LONG | H1 + M5 entry | `ALPHA_..._M5_ENTRY_ONLY_HTF_RISK` | `deepen_htfrisk.json` |
| 5 | `IR-DIR-L-mid` | LONG | H1 (range) | `4f668c8` | `intra_records.json` (see §1.2) |
| 6 | `MT-H4-efficiency-L` | LONG | H4 | `e1b08d8` | `deepen_multitf.json` |
| 7 | `MT-H4-dispaccept-L` | LONG | H4 | `e2e975c` | `deepen_multitf.json` |
| 8 | `TR-H4-rng2trend_disponly-L` | LONG | H4 | `fd80040` | `deepen_transition.json` |
| 9 | `H4-DISP-FOLLOW-L-COOLDOWN6` | LONG | H4 | `696e46b` / `a4bf24a` | `calib_cooldown6.py` |
| 10 | `S5` (`C_2d587447`) | LONG | M15 | validated | RT ledger (escrow) |
| 11 | `S20` | LONG | M15 | failed validation | RT ledger (escrow) |
| 12 | `TREND-CONT-SHORT-PB-BREAK` | SHORT | M15 | `d2c6577` | weak lead, never frozen |

### 1.2 Identity defect on `IR-DIR-L-mid`

`range_intra.py` generates **12** IDs: `IR-{bos,compexp,failcounter}-{L,S}-{mid,opp}`. **`IR-DIR-L-mid` is
not among them.** Its published metrics correspond to the `A_coarse` arm, which I verified is
**mechanism-independent by construction** (`run()` uses `legfn` only on the `B` arm) — and indeed
`A_coarse` is stored *byte-identically* under all three mechanism keys in `intra_records.json`.

So the candidate's numbers are real and reproducible, but its published ID has **no counterpart in any
machine-written record**, and the same figures are filed three times under three different mechanism names.
A reader of the records alone cannot identify which row is the candidate.

Second, and more substantive: `range_intra.py`'s own docstring designates arm A as the **CONTROL**
("*Control A(coarse H1-directional entry) vs B(M5 mechanism entry)*"). The candidate Alpha forwarded is the
**control arm**, which beat all three treatments the campaign was designed to test. That is not fraud and
the arm is causally valid — but it was **not a pre-registered hypothesis**, and it should be labelled as a
post-hoc selection from within its own campaign.

*One thing I checked and did not find:* I suspected the A arm might omit the directional confirmation the
report claims. It does not — `range_intra.py:78-79` applies `h1c[i] > h1o[i]` exactly as described. The
description matches the implementation.

---

## 2 — INCLUSION / EXCLUSION CRITERIA APPLIED

**Included** (§2): objects with a defined parent, entry, stop, target/horizon, cost semantics, and a
reproducible evidence trail. **Not included:** signal-only artifacts and features, however interesting.

**Excluded per §4** — full reasons in the Appendix (§16): `S5` (benchmark), `S20` (failed gate G),
London PLH clean-short, PDH clean-short, `EARLY-TRAP-E1`, `POST-E1-CLEAN-P2`, all research-local RANGE
failures, every `NO_ROBUST` / `NOT_SUPPORTED` family.

---

## 3 — S5 BENCHMARK (reference only; not reopened)

| metric | S5 | S20 |
|---|---|---|
| population | 2023-07-24 → 2025-10-12 (52,572 bars) | same |
| trades | **295** | 553 |
| **trades/month** | **11.1** | 20.8 |
| WR | 0.549 | — |
| avg R BASE / STRESS | +0.210 / +0.193 | — |
| PF | **1.609** | — |
| maxDD | **−6.44 R** | **−23.59 R → gate G FAIL** |
| max loss | −1.03 R | −1.04 R |
| median target | 373 pips | 143 pips |

**The bar this sets is not the expectancy — it is the completeness.** S5 carries a hashed 295-row ledger,
PF, maxDD, max loss, holding distribution, and a validated EV aggregate. **S20 was killed by exactly one
metric — maxDD — that no Alpha candidate has ever computed.**

---

## 4 — MECHANICAL REPRODUCTION (§5, integrity check)

I re-executed each candidate's own generator and evaluator against its own loader
(`file_sha = cbb6eebe1a189ebb…`, DEV: M5 121,949 / M15 40,649 / H1 10,168 / H4 2,652 bars).

| candidate | published | reproduced | |
|---|---|---|---|
| `MT-H4-efficiency-L` | n46 / WR 0.435 / +0.3798 / PF 2.007 / b10 +0.2668 | identical | **MATCH** |
| `MT-H4-dispaccept-L` | n41 / WR 0.341 / +0.1972 / PF 1.477 / b10 +0.0491 | identical | **MATCH** |
| `TR-H4-rng2trend_disponly-L` | n33 / WR 0.455 / +0.4431 / PF 2.503 / DD 2.95 | identical | **MATCH** |
| `HR-TU-pb-L-rr1.5` (M5 arm) | n51 / WR 0.627 / +0.3311 / PF 1.733 / DD 5.12 | identical | **MATCH** |
| `HR-TU-pb-L-rr2` (M5 arm) | n51 / WR 0.510 / +0.4506 / PF 1.926 / DD 4.62 | identical | **MATCH** |
| `IR-DIR-L-mid` | n46 / WR 0.435 / +0.523 / PF 1.858 / DD 5.58 / b10 +0.1211 | identical | **MATCH** |
| `H4-bo-raw-S-rr1.5` | n125 / +0.2876 STRESS / +0.3133 BASE / b5 +0.2269 / b10 +0.160 / maxYr 0.354 / CALIB +0.1523 n20 / b0 +0.2306 b1 +0.5345 | identical | **MATCH** |

**Every published figure reproduced exactly. Alpha's arithmetic is sound throughout.** The problems found
below are of a different kind: metrics never computed, a label never disambiguated, and an evidence base
that cannot support the next step.

---

## 5 — SUMMARY TABLE (§21)

STRESS = ratified round-trip 0.24. `—` = **NOT RECOVERED** (never computed by Alpha); values I derived
myself are marked **†**.

| Strategy | Mechanism | Side | TFs | Status | N | Tr/mo | WR | RR | AvgR BASE | AvgR STRESS | PF | MaxDD | Best10%-rem | DISC/DEV | CONF/CALIB | 2021 | 2022 | 2023 | S5 overlap | Tier | Primary blocker | Next owner |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **H4-bo-raw-S** | H4 20-bar-low breakdown, D1-down aligned, structural stop | **SHORT** | H4 (M5 pending) | frozen | **125** | **2.36** | **0.528 gross / 0.44 STRESS** | 1:1.5 | +0.3133 | **+0.2876** | **1.590†** | **9.27 R†** | **+0.160** | b0 +0.231 / b1 +0.535 | **+0.152 (n20)** | n/a | n/a | n/a | **LOW** | B | PF/maxDD never computed; WR published two ways; no evidence after 2021-09 | **Alpha** → Statistician |
| HR-TU-pb-L (rr2) | H1 TREND_UP pullback, M5-timed entry, H1 swing stop | LONG | H1+M5 | frozen | 51 | 1.75 | 0.510 | 1:2 | — | +0.4506 | 1.926 | 4.62 R | +0.2827 | +0.4506 | +0.2446 (n13) | +1.8 | +6.0 | +15.1 | MODERATE | C | no clean OOS region; CALIB n=13 | **CEO** (evidence) |
| IR-DIR-L-mid | H1 range, loc≤0.60 + H1 up-close → midpoint | LONG | H1 | frozen | 46 | 1.58 | 0.435 | ≈2.5 | — | +0.523 | 1.858 | 5.58 R | +0.1211 | +0.523 | +0.612 (n19) | +9.0 | −0.1 | +15.1 | LOW–MOD | C | no clean OOS region; ID not in records; control arm | **CEO** (evidence) |
| TR-H4-rng2trend_disponly-L | was-range → break + ≥1.2·ATR displacement | LONG | H4 | frozen | 33 | 1.13 | 0.455 | 1:1.5 | — | +0.4431 | 2.503 | 2.95 R | +0.3284 | +0.4431 | +0.658 (n9) | −1.3 | +1.7 | +14.2 | MODERATE | C | n=33 DEV / n=9 CALIB; 96.9% of P&L in 2023 | CLOSED-pending |
| MT-H4-dispaccept-L | H4 ≥1.0·ATR up bar + higher close | LONG | H4 | frozen | 41 | 1.41 | 0.341 | 1:1.5 | — | +0.1972 | 1.477 | — | +0.0491 | +0.1972 | +0.223 (n13) | +0.5 | **−1.0** | +8.6 | MODERATE | C | b10 +0.049 ≈ 0; 2022 negative; 106% of P&L in 2023 | CLOSED-pending |
| MT-H4-efficiency-L | H4 path efficiency > 0.4 | LONG | H4 | frozen | 46 | 1.58 | 0.435 | 1:1.5 | — | +0.3798 | 2.007 | — | +0.2668 | +0.3798 | +0.357 (n12) | **−1.7** | +3.1 | +16.1 | MODERATE | **D** | Alpha's own `GATE_M_FAIL_H4_TREND_BETA` | CLOSED |
| H4-DISP-FOLLOW-L-COOLDOWN6 | H4 displacement + follow-through, K=6 cooldown | LONG | H4 | frozen | — | — | — | 1:1.5 | — | +0.092 CALIB | — | — | −0.064 CALIB | positive | **CALIB_FAIL** | — | — | — | MODERATE | **D** | multi-gate CALIB failure; negative median | CLOSED |
| H1-hllh-S | H1 HL/LH structure continuation | SHORT | H1 | frozen | — | — | — | 1:3 | — | +0.187 | — | — | b1-rem +0.165 | b0 +0.232 / b1 +0.128 | **−0.139** | — | — | — | LOW | **D** | CALIBRATION negative | CLOSED |
| H1-B-bo-acc-SHORT | H1 breakout + acceptance, HTF-down | SHORT | H1 | superseded | — | — | — | — | — | — | — | — | **−0.028** | — | +0.057 | — | — | — | LOW | **D** | strictly dominated by `H4-bo-raw-S`; same edge — do not double-count | CLOSED |

---

## 6 — TIER A — **EMPTY**

No candidate satisfies Tier A. Every one fails at least one Tier-A requirement:

- the four 2021–2023 candidates have **no unconsumed out-of-sample region** (§9);
- `H4-bo-raw-S` has no Alpha-computed PF or maxDD and an ambiguous headline WR (§8);
- all have N between 33 and 125 against S5's 295.

---

## 7 — TIER B — **`H4-bo-raw-S`** (the only entry)

**Why it is the one:**

1. **It is the only SHORT.** Every other surviving candidate is LONG. S5 is LONG. This is the only object
   in the inventory that could diversify direction.
2. **Its evidence base is not in the consumed region.** DEV = `b0` 2011-07-26→2013-09-27 and `b1`
   2016-01-11→2018-04-06; CALIB = 2020-08-11→2021-09-05. This is a *different* population from the
   2021–2023 M5 window whose out-of-sample regions are exhausted. **The blocker that stops the other four
   does not apply to it.**
3. **It is the only candidate positive on best-10%-removed with both blocks positive and out-of-DEV CALIB
   positive**: +0.160 / (+0.231, +0.535) / +0.152. Not tail-carried.
4. **Per-block evaluation is correct.** `b0` ends 2013-09 and `b1` starts 2016-01 — they straddle but never
   enter the unratified 2013–2016 manifest gap, and the campaign evaluates per block with no cross-gap
   bridging. Credit where due: this is the discipline whose absence I flagged in the historical-HTF
   migration.
5. **Economic profile is right.** Median SL 75 pips, median TP 113 pips, 87.4% of targets ≥70 pips. Not
   micro-scalping.

---

## 8 — `H4-bo-raw-S` SPECIAL AUDIT (§12) — two defects found, one metric cleared

### 8.1 The win rate is published two different ways in the same commit

| artifact | line | definition | value |
|---|---|---|---|
| `econ_campaign.py` | 168 | `(rg >= k-0.05).mean()` on **GROSS** R | **0.528** |
| `deepen_econ.py` | 76 | same test on **STRESS**-net R | **0.44** |

I measured all three scenarios directly:

```
  WR on GROSS  R = 0.528     <- the number in the flagship table
  WR on BASE   R = 0.528
  WR on STRESS R = 0.44      <- the number in deepen_econ.json, the run that awarded ROBUST
```

The flagship table (report §2) lists **"win rate 0.528"** on the line immediately above **"avg realized R
+0.288 (STRESS)"**, with no label distinguishing the cost scenarios. Report §5 then reasons from
*"max WR ≈ 0.53 (flagship)"* to its Profile-A conclusion.

**Under the ratified STRESS cost the flagship's win rate is 0.44, not 0.528** — 8.8 points lower, and
further from Profile A than the report concludes. Both numbers are correctly computed; the defect is that
one is presented as *the* win rate beside a STRESS expectancy. **Fix is a labelling correction, not a
re-run.**

### 8.2 PF and maxDD were never computed — I computed them

`grep` over every Alpha discovery script: `profit_factor` / `max_dd` / `maxDD` appear in
`deepen_htfrisk.py`, `deepen_multitf.py`, `deepen_transition.py`, `deepen_intra.py`, `calib_cooldown6.py`,
`campaign.py` — **and in neither `econ_campaign.py` nor `deepen_econ.py`.** The single candidate Alpha calls
*"the most robust candidate in the entire program"* is the one candidate with no drawdown figure.

Derived here from the reproduced trade sequence (chronological within blocks, concatenated across the
b0/b1 gap):

```
  profit factor (STRESS) = 1.590        vs S5 1.609
  max drawdown  (STRESS) = 9.27 R       vs S5 -6.44R ;  S20 FAILED gate G at -23.59R (limit 15R)
  max single loss        = -1.086 R     vs gate G limit 2.0R
  median R               = +1.4342      (reproduces the published median exactly)
```

**Gate G, the gate that killed S20, would PASS**: 9.27 R < 15 R and 1.086 R < 2.0 R. This is the most
important positive result in the triage — but note it is **my** computation, not Alpha's, derived across a
2.3-year data gap, and it must be recomputed on a proper single-sequence ledger before any validation.

### 8.3 Year composition — and a gap the report does not mention

```
  per-year n    : 2011: 12 · 2012: 33 · 2013: 46 · 2016: 17 · 2017: 17 · 2018: 0
  per-year sumR : 2011 +0.3 · 2012 +6.0 · 2013 +12.7 · 2016 +9.9 · 2017 +7.0
```

No single year exceeds 35.4% of P&L — genuinely unconcentrated, and materially better than every LONG
candidate (§10). But **2018 contributes zero trades** despite `b1` running to 2018-04, and **the most
recent evidence of any kind ends 2021-09-05**.

### 8.4 The blocker the report does not treat as one

Alpha's own H1/H4 SHORT-specialist mandate states, verbatim: *"the frozen `H4-bo-raw-S` short — from the
earlier 2011–2018 population — … **does not exist on this 2021–2024 population's mechanisms**"*, and the
bearish-mining report locates it in *"2011–2013 … this campaign's 2021–2024 window is structurally
long-biased."*

**This is a regime-conditional short with no supporting evidence in the modern market.** That is not
disqualifying — gold genuinely was in a bear market in 2011–2013 and a validated bear-regime short has real
portfolio value — but it must be stated as what it is, and any validation must be explicit that the
candidate is being certified on a regime that has not recurred in the last four years.

**Verdict on §12: audit-worthy, not validation-ready.**

---

## 9 — TIER C — the four 2021–2023 candidates and their shared hard blocker

`HR-TU-pb-L` · `IR-DIR-L-mid` · `TR-H4-rng2trend_disponly-L` · `MT-H4-dispaccept-L`

**All four received `FRESH_VALIDATION_EVIDENCE_REQUIRED` from me in prior mandates** (`6d4430a`, `90dec40`,
`6f8c922`, `c028eb2`). The blocker is identical and is not statistical — it is evidence availability:

```
  V1  2024-07-10 -> 2025-10-23   PARTIALLY_CONSUMED  (>=17 Flow-A studies on the same calendar)
  V2  2025-10-23 -> 2026-02-17   CONSUMED            (terminal holdout invalidated, CEO ruling, PROJECT_STATE_v2 §8.23)
  V3  2026-03-10 -> 2026-06-20   CONSUMED
  V4  2026-07-13 -> 2026-07-27   CLEAN               -- 2,904 bars
```

**There is no clean out-of-sample region large enough to validate anything.** Their CALIB blocks (n = 9 to
19 trades) are already spent as robustness checks. Red Team cannot run an independent validation for them
the way it did for S5, because the population S5 used does not exist for them.

**This is a CEO decision about evidence, not a Statistician or Red Team task.** Sending these to validation
now would produce an underpowered verdict on a compromised region.

---

## 10 — TREND-CONTINUATION FAMILY AUDIT (§13) — they are **not** independent strategies

Trade-level, from ledgers I reproduced myself — not from narrative similarity (§11).

### 10.1 Year concentration is severe and shared

| candidate | n | total R | 2021 | 2022 | 2023 | **2023 share of P&L** |
|---|---|---|---|---|---|---|
| MT-H4-efficiency-L | 46 | +17.47 | −1.7 | +3.1 | +16.1 | **92.3%** |
| MT-H4-dispaccept-L | 41 | +8.09 | +0.5 | **−1.0** | +8.6 | **106.2%** |
| TR-H4-rng2trend_disponly-L | 33 | +14.62 | −1.3 | +1.7 | +14.2 | **96.9%** |
| HR-TU-pb-L rr2 | 51 | +22.98 | +1.8 | +6.0 | +15.1 | 65.9% |
| IR-DIR-L-mid | 46 | +24.06 | +9.0 | −0.1 | +15.1 | 62.8% |

**The three H4 LONG candidates are 2023 phenomena.** Two are negative in 2021; one is negative in 2022.
Strip 2023 and the H4 family collapses to roughly nothing.

### 10.2 Same-day Jaccard (trade-day sets)

|  | MT-eff | MT-disp | TR-d2t | HR-TU1.5 | HR-TU2 | IR-DIR |
|---|---|---|---|---|---|---|
| **MT-eff** | — | 0.169 | 0.213 | 0.148 | 0.148 | 0.048 |
| **MT-disp** | 0.169 | — | **0.327** | 0.095 | 0.095 | 0.036 |
| **TR-d2t** | 0.213 | **0.327** | — | 0.092 | 0.092 | 0.013 |
| **HR-TU1.5** | 0.148 | 0.095 | 0.092 | — | **1.000** | **0.000** |
| **IR-DIR** | 0.048 | 0.036 | 0.013 | **0.000** | 0.000 | — |

Plus same-**week** Jaccard within the H4 trio: 0.396 / 0.452 / **0.500**; and ±1 H4 bar proximity 24% / 24% /
**39%**.

### 10.3 Conclusions

- **`HR-TU-pb-L` rr1.5 and rr2 are the same strategy** (Jaccard **1.000**, 18 of 20 shared loss-days,
  identical n=51). They are one object at two RR settings, **never two portfolio slots.**
- **The three H4 LONG candidates are one economic family**: same edge TF, same H4 structural swing stop
  (`min(low[i−4..i]) − 0.15·ATR` for MT; `i−3..i` for TR), same RR 1.5, same LONG bias, overlapping
  triggers (`dispaccept` needs a ≥1.0·ATR up bar + higher close; `rng2trend_disponly` needs a ≥1.2·ATR up
  bar breaking structure), 33–50% same-week co-firing, and **all three earning ~all their P&L in 2023.**
  This independently confirms both Alpha's own autonomous-loop conclusion (*"low-WR/high-payoff LONG
  trend-beta"*) and my prior `GATE_M_FAIL_H4_TREND_BETA` on `MT-H4-efficiency-L`. **Count them as ONE
  family slot, not three.**
- **`HR-TU-pb-L` vs the H4 family**: same-day Jaccard 0.09–0.15, loss-day Jaccard ≤ 0.03. Distinct enough
  to be a separate slot, but both are LONG trend-continuation on the same instrument and both are
  2023-heavy.
- **`IR-DIR-L-mid` vs `HR-TU-pb-L`: Jaccard 0.000 — Alpha's regime-disjointness claim is independently
  reproduced and correct.** Zero shared trade-days, zero shared loss-days. This is the genuine
  complementarity in the inventory. It is also the only LONG candidate with a strongly positive 2021.

---

## 11 — FREQUENCY (§9)

| candidate | trades/month | median days between trades | portfolio note |
|---|---|---|---|
| S5 (benchmark) | **11.1** | ~2.7 | |
| H4-bo-raw-S | 2.36 | ~12.9 | |
| HR-TU-pb-L | 1.75 | ~17 | |
| IR-DIR-L-mid | 1.58 | ~19 | |
| MT-H4-efficiency-L | 1.58 | ~19 | family duplicate |
| MT-H4-dispaccept-L | 1.41 | ~21 | family duplicate |
| TR-H4-rng2trend_disponly-L | 1.13 | ~27 | family duplicate |

**All six 2021–2023 candidates run together** over the 29.1-month DEV window: 268 trades = **9.21/month =
0.424 per trading day**, on **152 of ~632 trading days (24.1%)**.

Against the CEO's ~2–3 effective trades/day target that is a **~6× shortfall**, and that figure already
double-counts the H4 family. Counting one slot per family it is worse. **Reported honestly, not used to
reject anything** (§9) — but the CEO should know that the entire existing frozen inventory, fully deployed,
does not approach the portfolio frequency objective. S5 alone supplies more trades than all six combined.

Max no-trade streak: **NOT RECOVERED** (would require per-candidate gap analysis on a single live sequence).

---

## 12 — S5 OVERLAP (§10)

**Trade-level overlap with S5 is not computable and would not be meaningful.** S5's validated population is
2023-07-24 → 2025-10-12; the Alpha DEV window is 2021-07-27 → 2023-12-29. They share ~5 months, and S5's
ledger is sealed in `escrow_red_team/`. Assessed on mechanism, direction, and regime instead:

| candidate | direction vs S5 | mechanism | regime dependence | **redundancy** |
|---|---|---|---|---|
| **H4-bo-raw-S** | **opposite (SHORT)** | H4 breakdown vs M15 NY opening-range up-breakout | bear regime vs any | **LOW** |
| IR-DIR-L-mid | same (LONG) | H1 intra-range → midpoint | RANGE vs breakout | **LOW–MODERATE** |
| HR-TU-pb-L | same (LONG) | H1 trend pullback, M5 entry | TREND_UP; S5 is NY-session-gated | **MODERATE** |
| H4 LONG family (×3) | same (LONG) | H4 continuation | 2023 uptrend | **MODERATE** |

`H4-bo-raw-S` is the only genuine diversifier in the inventory.

---

## 13 — HARD BLOCKERS (§17), by candidate

| candidate | hard blocker(s) |
|---|---|
| **H4-bo-raw-S** | PF/maxDD absent from Alpha's own artifacts; WR published two ways; **no evidence after 2021-09**; mechanism confirmed absent on 2021–2024; CALIB n=20 |
| HR-TU-pb-L | **no clean OOS evidence region**; CALIB n=13; rr1.5 negative in 2021 |
| IR-DIR-L-mid | **no clean OOS evidence region**; ID absent from records; is the campaign's *control* arm; median R **−1.041** (median trade loses) |
| TR-H4-rng2trend_disponly-L | N=33 DEV / **9** CALIB; 96.9% of P&L in 2023; family duplicate |
| MT-H4-dispaccept-L | best-10%-removed **+0.049 ≈ 0** (tail-dependent); 2022 negative; family duplicate |
| MT-H4-efficiency-L | Alpha's own `GATE_M_FAIL_H4_TREND_BETA` |
| H4-DISP-FOLLOW-L-COOLDOWN6 | `CALIB_FAIL` on four gates; negative median (−0.508); negative incremental vs plain trend exposure |
| H1-hllh-S | CALIBRATION **negative** (−0.139) |
| H1-B-bo-acc-SHORT | strictly dominated by `H4-bo-raw-S`; same edge — double-counting risk |

**Universal blocker:** no Alpha candidate has a hashed trade ledger. S5's validation was possible because
`cd4e8d4a…` fixes 295 rows. Nothing comparable exists for any candidate here.

---

## 14 — RANKED VALIDATION PRIORITIES (§18)

### PRIORITY 1 — `H4-bo-raw-S` (RR 1:1.5)

**Why worth the work:** the only SHORT; the only inventory item whose evidence base sits outside the
consumed region; positive under STRESS (+0.288) with best-10%-removed positive (+0.160), both DEV blocks
positive, out-of-DEV CALIB positive (+0.152), no year exceeding 35% of P&L; economic target (median 113
pips); and on my own computation it would **pass** the maxDD gate that killed S20.

**What remains unproven:** (a) PF and maxDD must be computed by the owner on a proper single-sequence
ledger — mine are derived across a 2.3-year data gap; (b) the WR labelling must be corrected to 0.44 STRESS
/ 0.528 gross-and-BASE, and the Profile-A reasoning in §5 of Alpha's report revisited; (c) a hashed trade
ledger must exist before Red Team can validate anything; (d) **no evidence after 2021-09** — the CEO must
decide whether a bear-regime short certified on 2011–2018 is acceptable; (e) CALIB n=20 is thin.

**NEXT OWNER: Alpha** — mechanical completion only (ledger export, PF/maxDD, WR label). **No retuning
whatsoever.** Then **Statistician** for a validation protocol.

### PRIORITY 2 — `IR-DIR-L-mid` — **BLOCKED, not queued**

**Why it is next in line:** the only candidate with genuinely balanced years (2021 **+9.0**), tail-robust
(best-10%-removed +0.121), CALIB-positive (+0.612), and **Jaccard 0.000 against `HR-TU-pb-L`** — the one
independently verified complementarity in the inventory.

**What remains unproven:** no clean OOS region exists to test it; n=46/19; **median R is −1.041**, so it is
carried by winners; its ID does not exist in the records; it is the control arm of a campaign designed to
test three other things.

**NEXT OWNER: CEO** — an evidence-region decision, not a validation task. Statistician and Red Team cannot
proceed.

### PRIORITY 3 — **NONE. I decline to name one.**

Per §19, I will not manufacture a third. `HR-TU-pb-L` is blocked identically to Priority 2 and is the
weaker of the two on temporal balance. The H4 LONG trio is one 2023-concentrated family, not three
candidates, and its best member already failed Alpha's own Gate M.

---

## 15 — RECOMMENDED NEXT ACTIONS

1. **Enumerate the "9 frozen strategies" in a repository artifact.** A portfolio referenced by count and
   never by identity is not auditable. Owner: Alpha, on CEO mandate.
2. **Alpha: mechanical completion of `H4-bo-raw-S`** — export a hashed ledger, compute PF/maxDD/max-loss,
   correct the WR labelling. No retuning, no new thresholds.
3. **CEO decision required — the binding constraint on this entire program is not strategy quality, it is
   evidence supply.** Four of six candidates are frozen and reproducible and cannot be validated because no
   unconsumed region remains. Until that is resolved, further Alpha discovery on the 2021–2023 window
   produces candidates that cannot be certified — which is precisely what the last three Alpha mandates
   reported (`SEARCH_SPACE_EXHAUSTED_WITHOUT_ROBUST_ALPHA`).
4. **Do not count the H4 LONG trio as three portfolio strategies.** One family slot.
5. **Recognise the frequency gap explicitly.** The full inventory delivers ~0.42 trades/trading-day against
   a 2–3/day objective. Closing it is a different problem from validating what exists.

---

## 16 — APPENDIX: EXCLUSIONS (§4), with exact reasons

| item | exclusion reason |
|---|---|
| **S5** (`C_2d587447`) | Benchmark. Independently validated (RT), EV evidence reconciled (`9cfcc5f`). Not reopened. |
| **S20** | Formally failed independent validation — gate G, maxDD −23.59R > 15R limit. |
| **London PLH clean-short** | Signal, not a strategy. `PLH_ASIA_SPATIAL_FEATURE_NOT_SUPPORTED` (`6892bc6`); Alpha's own fixed-80p relabel (`c3b286b`) confirmed the falsification — AUC 0.12/0.23 → 0.579, P(CLEAN)=0.060. Graveyard. |
| **PDH clean-short** | Signal-only artifact; no entry/stop/target defined. §2 forbids elevating it. |
| **EARLY-TRAP-E1** | Signal only; `SIGNAL_SUPPORTED` (`de35453`) but execution explicitly unsolved by Alpha. |
| **POST-E1-CLEAN-P2** | `IDENTITY_AMBIGUOUS` + `SIGNAL_WEAK` (`16fee06`). |
| **RANGE M15/M5 families** | `NO_ROBUST_RANGE_M15_M5_ALPHA_FOUND` (`4d8920f`); every family net-negative after costs. |
| **RANGE boundary rotation** | Empty parent — V4.4 confirms **zero** macro ranges on 2021–2023 (`11425fd`, `79beabf`). |
| **M15 consolidation trend-continuation** | `SIGNALS_WEAK`; `TREND-CONT-SHORT-PB-BREAK` best-10%-rem −0.022, DISC-weak. Never frozen. |
| **High-WR autonomous portfolio search** | `N_SURVIVORS = 0` (`d723555`). |
| **Autonomous discovery loop** | `SEARCH_SPACE_EXHAUSTED_WITHOUT_ROBUST_ALPHA` (`0c5d10e`). |
| **All `NO_ROBUST_*` / `NOT_SUPPORTED` families** | Formally closed by their own mandates. |

---

## 17 — LIMITATIONS

1. **The inventory is a reconstruction.** No authoritative frozen-strategy list exists. I may have missed a
   candidate that is never named in a report.
2. **`H4-bo-raw-S`'s PF (1.590) and maxDD (9.27 R) are mine, not Alpha's**, and were computed by
   concatenating `b0` and `b1` across a 2.3-year gap. They are indicative, not certifiable. A real ledger
   must replace them.
3. **Whether the 2011–2013 and 2016–2018 blocks sit inside ratified manifest segments is NOT RECOVERED.**
   I verified only that they do not *enter* the unratified 2013–2016 gap and that evaluation is per-block.
4. **S5 trade-level overlap could not be computed** — different population, ledger in escrow. §12 is a
   mechanism-and-direction assessment, and is labelled as such.
5. **Max no-trade streak NOT RECOVERED** for any candidate.
6. **PF and maxDD are NOT RECOVERED for `MT-H4-efficiency-L` and `MT-H4-dispaccept-L`** — `deepen_multitf.py`
   computes PF but not maxDD. Both are Tier C/D and this does not change their ranking.
7. **No strategy was executed, retuned, or modified.** All runs re-executed Alpha's own frozen code against
   Alpha's own frozen loader. No threshold, entry, stop, target, filter, or combination was created or
   altered. No CALIB or holdout region was opened.

---

## 18 — TERMINAL STATUS

```
FROZEN_STRATEGY_TRIAGE_COMPLETE
VALIDATION_WORTHY_EXISTING_CANDIDATES_FOUND
N_VALIDATION_WORTHY = 1
```

The one is **`H4-bo-raw-S`**, at **Tier B**, next owner **Alpha** for mechanical completion, then
**Statistician**. **No execution authorization. No promotion. No AI Trader, no MT5, no demo, no live.**

---

*Statistician division — independent statistical validation. Verdicts are scoped strictly to the evidence
examined and are not transferable to adjacent claims.*
