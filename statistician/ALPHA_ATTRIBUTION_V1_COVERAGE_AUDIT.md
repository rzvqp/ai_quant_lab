# ALPHA_ATTRIBUTION_V1_COVERAGE_AUDIT

**Subject:** Alpha's `STRATEGY_OUTCOME_ATTRIBUTION_EDGE_RESCUE_V1` (commit `270622a`).
**Question:** did it analyse the complete strategy graveyard, or the part that was easiest to load?
**Division:** Statistician. **Date:** 2026-09-02. Companion to
`COMPLETE_STRATEGY_GRAVEYARD_MANIFEST_V1` (hash `433f1cec…`).

## VERDICT

```
DID ALPHA V1 ANALYSE THE COMPLETE STRATEGY GRAVEYARD? = NO

COVERAGE_BY_FAMILY             = 13.5%   (14 of 104 attribution-eligible objects)
COVERAGE_BY_DISTINCT_MECHANISM = 23.1%   (6 of 26)
COVERAGE_BY_VALID_TRADES       = 27.9%   (30,703 of ~110,000 readily available)
```

**The evidence is a single import statement.** `attr_run.py:8`:

```python
import ob_core as OB, ob_exec as EX, htf_setups as HS, sess_core as SC, sess_scan as SS
```

Those five modules generate all 14 objects. The run analysed **the strategies whose generators were already
importable from its own working directory** — `reports/alpha_discovery/`. The Executable Strategy Library
lives in `code/` and was never imported.

---

## 1 — THE 14 EXACT OBJECTS (§11)

Recovered mechanically from `STRATEGY_ATTRIBUTION_MASTER_TABLE.csv` (30,703 rows).

| # | OBJECT_ID | generator | mechanism | trades | pooled net R | MFE/MAE path |
|---|---|---|---|---|---|---|
| 1 | `HTF_PBK_TREND` | `htf_setups.py` | M07 trend continuation | 324 | −0.0842 | yes |
| 2 | `HTF_RECLAIM` | `htf_setups.py` | M11 structure-break reversal | 6,834 | −0.1002 | yes |
| 3 | `HTF_RANGE_FADE` | `htf_setups.py` | M12 range rotation | 760 | −0.1463 | yes |
| 4 | `HTF_TGT_BREAK` | `htf_setups.py` | M03 breakout-retest | 460 | −0.0229 | yes |
| 5 | `OBR_A_limit` | `ob_core`+`ob_exec` | M14 reference level | 2,486 | −0.0673 | **no** |
| 6 | `OBEXEC_B` | `ob_exec.py` | M14 reference level | 2,160 | −0.2657 | **no** |
| 7 | `OBEXEC_C` | `ob_exec.py` | M14 reference level | 1,896 | −0.2057 | **no** |
| 8 | `OBEXEC_D` | `ob_exec.py` | M14 reference level | 955 | −0.1853 | **no** |
| 9 | `SESS_A` | `sess_scan.py` | M06 session/time | 3,293 | **+0.0098** | yes |
| 10 | `SESS_B` | `sess_scan.py` | M06 session/time | 3,056 | −0.3656 | yes |
| 11 | `SESS_C` | `sess_scan.py` | M06 session/time | 1,748 | −0.2791 | yes |
| 12 | `SESS_D` | `sess_scan.py` | M06 session/time | 2,784 | −0.0267 | yes |
| 13 | `SESS_E` | `sess_scan.py` | M06 session/time | 989 | −0.1707 | yes |
| 14 | `SESS_Fc` | `sess_scan.py` | M06 session/time | 2,958 | −0.1937 | yes |

Two structural observations, neither of which Alpha's report makes:

- **Half the pool is one mechanism.** 6 of 14 objects and 14,828 of 30,703 trades (48%) are
  `M06_SESSION_TIME`. A cross-strategy conclusion about *sessions* drawn from a pool that is half
  session-specialist strategies is close to circular. The reported "NY is consistently the least-bad
  session" is being measured largely on strategies whose entry condition is a session.
- **4 of 14 objects carry no MFE/MAE path** (all four order-block executions, 7,497 trades = 24%). The §21
  post-entry management finding therefore rests on the 10 objects that do — a restriction the report does
  not state.

---

## 2 — WHAT WAS MISSED, AND WHY (§12)

```
VALID_FAMILIES_MISSED_BY_ALPHA_V1 = 90 attribution-eligible objects
```

| reason (mandate §12 classes) | count | what |
|---|---|---|
| **GENERATOR_NOT_CALLABLE** — the S-library engine is never imported by `attr_run.py` | **43** | the entire valid Executable Strategy Library (S1–S31, S38–S51 minus S47/S49) |
| **NOT_DISCOVERED_BY_ALPHA** — the series was never enumerated | **25** | `edge_research` E-series and candidate series |
| **FORMAT_INCOMPATIBLE** — different panel/timeframe | **16** | later factories (M5, DXY-joined, 24h, daily OCO, contrast-miner, chrono, BFSD…) |
| **NO_TRADE_LOG** — frozen spec only | **6** | frozen candidates (H4-bo-raw-S, COMP-CONT-L-rr2, CRS-1, HR-TU-pb-L, MT-H4-dispaccept-L, E015) |

**On the 16 FORMAT_INCOMPATIBLE objects, Alpha was honest** — its §2 explicitly names "M5 Family E,
cross-market DXY, long-horizon 24h, direction-agnostic OCO (daily), temporal-sequence, contrast-miner
H1/H2/H3" as valid-but-not-pooled, and gives a real reason (a coherent shared M15 feature space). That is a
legitimate scoping decision, disclosed.

**On the 43 + 25 = 68 others it is silent**, and those are the ones that matter. The 43 S-library families
are *on the M15 panel*, so the stated scoping reason does not apply to them. So:

> **"Alpha analysed only 14 because only 14 scientifically valid populations exist" is FALSE.**
> **"Alpha analysed the 14 it happened to have loaded" is, on the evidence, TRUE.**

---

## 3 — MECHANISM COVERAGE

Covered (6 of 26): `M03_BREAKOUT_RETEST`, `M06_SESSION_TIME`, `M07_TREND_CONTINUATION`,
`M11_STRUCTURE_BREAK_REVERSAL`, `M12_RANGE_ROTATION`, `M14_REFERENCE_LEVEL`.

**Missed entirely (20):**

```
M01_LIQUIDITY_SWEEP            M02_FAILED_BREAKOUT_FADE      M04_VOLATILITY_COMPRESSION_EXPANSION
M05_OPENING_RANGE              M08_EXTENSION_MEAN_REVERSION  M09_MTF_ALIGNMENT
M10_DISPLACEMENT_CONTINUATION  M13_IMBALANCE_FVG             M15_GAP
M16_AUCTION_VALUE              M17_VOLUME_PARTICIPATION      M18_OSCILLATOR_DIVERGENCE
M19_SEQUENCE_RUNLENGTH         M20_CANDLESTICK_PATTERN       M21_META_ROUTER
M23_CROSS_MARKET               M24_EVENT_REVEALED_RESPONSE   M25_DIRECTION_AGNOSTIC_OCO
M26_CONTRAST_MINING            M27_EDGE_RESEARCH_PATTERN
```

Notable among the missed: **M04 volatility compression/expansion** (8 objects) — the mechanism class the
lab's own timing research says is where XAU structure lives; **M01 liquidity sweep** — S1, historically the
highest-expectancy family in the old registry; and **M24 event-revealed response** — the architecture class
of S5, the only validated edge.

---

## 4 — CEO QUESTIONS (§16)

**1. Did Alpha V1 analyse the complete strategy graveyard?**
**NO.** 13.5% by family, 23.1% by mechanism, 27.9% by trades.

**2. What percentage of valid distinct mechanisms did it cover?** **23.1%** (6 of 26).

**3. What important valid families were missed?**
The whole **Executable Strategy Library** — 43 valid families, 2,420 valid variants, every one
lookahead-audited and ledger-capable. Within it, the families most worth having in an attribution study:
**S1** (liquidity sweep — the old registry's best expectancy, +0.253R/141 trades), **S4/S21/S26/S48**
(volatility regime & transition), **S9** (MTF momentum), **S10** (displacement continuation), **S13**
(imbalance/FVG), **S16/S17** (daily/weekly reference levels), **S38–S43** (volume, order-flow proxy,
oscillator, sequence). Plus all **25** `edge_research` families.

**4. Can we build trade populations for those missed families?**
**YES, and cheaply — this is the strongest finding of the audit.** `simulate()` already returns a per-trade
ledger (`R`, `si`, `ei`), `backtest()` is a two-line call over a frozen grammar, and `results/full.log`
records `lookahead_safe=True · ledger_ok=True` for **every** family. No new research, no new data, no
re-derivation: a loop over the frozen grammar produces the populations. 88 of the 90 missed objects are
class B; only the 6 frozen-spec candidates and 2 information-only objects need more work.

**5. Is a complete winner/loser attribution audit scientifically feasible?**
**YES**, with two conditions that must be settled *before* it runs:
(a) **a pre-registered variant-selection rule** — 2,420 variants pooled is 1.9M overlapping variant-trades,
which is pseudo-N, not evidence; one representative variant per family gives ~79,500 trades across 42
families, and the choice of "representative" is itself a researcher degree of freedom;
(b) **day-clustered inference** — trades from one strategy on one day are not independent.

**6. How many distinct mechanisms can actually be included?**
**26 of 27** — everything except `M22_EXOGENOUS_DATA` (S32–S37, not implemented). Practically, expect
**~25** in a first pass, since `M27_EDGE_RESEARCH_PATTERN` still needs decomposition into real mechanism
classes before its 25 families can be mapped properly.

---

## 5 — FROZEN ATTRIBUTION UNIVERSE (§13)

```
ATTRIBUTION_UNIVERSE_V2  (class A — trade logs exist today; 16 objects)
  HTF_PBK_TREND · HTF_RECLAIM · HTF_RANGE_FADE · HTF_TGT_BREAK
  OBR_A_limit · OBEXEC_B · OBEXEC_C · OBEXEC_D
  SESS_A · SESS_B · SESS_C · SESS_D · SESS_E · SESS_Fc
  OB_CAUSAL_EXECUTION_FACTORY_V1 · SESSION_SPECIALIST_FACTORY_V1

REGENERATION_REQUIRED  (class B — frozen spec + callable generator; 88 objects)
  43  S-library families S1-S31, S38-S51  (excluding S47, S49)   <- the priority block
  25  edge_research E-series / candidate series
  16  later factories on other panels
   4  frozen candidates with recoverable specs

UNUSABLE (16)
  class C (8): S32-S37 (external data, not implemented) · S47 (n<25) · S49 (non-selective)
  class D (8): S5 (PROTECTED by mandate, not ineligible) · RANGE v4.4 · RANGE vNext ·
               L1_LONDON · P2_RANGE_LOW (overlap artifact) · V2_4_COILED (session confound) ·
               D4_ASIA_CLOSE_EDGE · GOLD_ORDER_FLOW_DISCOVERY_V1 (data-blocked)
```

Selection was mechanical — attribution class, computed from artifacts. **Alpha does not choose these.**

---

## 6 — RECOMMENDED SEQUENCE (not authorised, stated for the CEO's decision)

1. Decompose `M27` into real mechanism classes (read the 25 `edge_research` modules). Cheap.
2. **Pre-register** the variant-selection rule and the feature inventory, in writing, before any scoring —
   with the §8 anti-seeding protocol from the manifest.
3. Regenerate trade ledgers for the 43 S-library families from the frozen grammar.
4. Only then run attribution, on ~59 objects across ~25 mechanisms, with day-clustered inference.

**This audit establishes coverage only.** Nothing here implies the missed families would have changed
Alpha's conclusion, and I have not looked. No promotion, nothing modified.
