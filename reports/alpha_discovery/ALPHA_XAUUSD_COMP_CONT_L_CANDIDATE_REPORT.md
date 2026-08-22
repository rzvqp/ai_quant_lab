# ALPHA_XAUUSD_COMP_CONT_L_CANDIDATE_REPORT

**Mandate:** `ALPHA-XAUUSD-CONTINUOUS-RESEARCH-LOOP-001` · **Date:** 2026-08-22.
**Terminal status:** `CONTINUOUS_ALPHA_RESEARCH_CHECKPOINT` · **`NEW_ROBUST_STRATEGY_CANDIDATE_FOUND`** · **`READY_FOR_INDEPENDENT_VALIDATION`**.
**Scope:** continuous autonomous research loop. Price-only XAUUSD; gated M5 -> H4/D1 causal; DEV selection; CALIB robustness-only; no 2025+/N4/V1/protected-2024/exogenous; no MI/S5 change; no AI Trader/MT5/demo/live; broker disabled. **Alpha does not self-ratify (§35/§17-equivalent).**

---

## 0. Headline
- The loop opened **five materially-distinct NEW frontiers** at the swing horizon (the horizon the prior program never converted). F1 (volatility expansion-breakout), F2 (exhaustion reversion), F3 (temporal/calendar) **falsified**; F4 (time-drift) a **near-miss = frozen trend-beta**; **F5 (compression-timed trend continuation) produced a genuine robust LONG survivor.**
- **`COMP-CONT-L-rr2`** (LONG, D1-uptrend regime-specific): STRESS avgR **+0.443**, PF **1.94**, **best-10%-removed +0.246** (not tail-carried), DISC **+0.52** / CONF **+0.33** (both positive), **all 3 DEV years positive**, and **CALIB 2024 out-of-selection POSITIVE** (+0.223). N=53, 2.79 trades/month, median SL 190p / TP 379p.
- Frozen, packaged, and handed to the **Statistician for independent validation**. Honest limitations (W-sensitivity, dedup-dependence, trend-beta correlation, multiple-testing lineage) fully disclosed. **STOP active search (§35).**

## 1. Frontier sequence this loop (§32, §40 — full, no hidden research)
| frontier | economic question | screen verdict | why closed / kept |
|---|---|---|---|
| F1-VOL-EXP | compression -> directional expansion breakout, swing | **FALSIFIED** | path symmetric (MFE≈MAE), best10<0, shorts neg, N tiny, 300p stops |
| F2-EXH-REV | over-extension exhaustion reversion, swing | **FALSIFIED** | wrong-way path (MAE>>MFE, advFirst 0.80–0.92) — fades get run over |
| F3-TEMPORAL | day-of-week drift / weekly-gap continuation-fade | **FALSIFIED** | DOW weak; gap-cont best10<0 & 2021<0 |
| F4-DRIFT | trend-drift per regime onset, horizon payoff | **NEAR-MISS** | LONG D1-aligned clean but horizon-fragile + arbitrary stop = frozen trend-beta |
| F5-COMPCONT | compression as low-risk re-entry timing WITH the D1 trend, structural stop | **SURVIVOR (LONG)** | robust across H & rr, best10>0, DISC/CONF+, CALIB+ |

**Hypotheses this loop:** ~13 materially-distinct rules across 5 frontiers (see `ALPHA_HYPOTHESIS_REGISTRY.md`). **Prior program:** 60+ falsified hypotheses (see `ALPHA_GRAVEYARD.md`). The survivor is **not** hypothesis #1 — full lineage disclosed (§20).

## 2. §41 — required candidate fields
| field | value |
|---|---|
| `STRATEGY_ID` | `COMP-CONT-L-rr2` |
| `MECHANISM` | H4 volatility compression (ATR<atr_ma AND box<box_ma) inside confirmed D1 uptrend -> re-enter LONG next H4 open, stop at compression floor, target 2R |
| `SIDE` | LONG only (SHORT mirror NOT_SUPPORTED — regime-locked) |
| `TIMEFRAMES` | D1 context / H4 signal + entry (M5 not required) |
| `DATA_IDENTITY` | gated M5 -> H4, DEV 2021-07-27..2023-12-29; loader sha `cbb6eebe…`, manifest 2.7.94 |
| `N` / `EFFECTIVE_N` | 53 trades / 53 unique compression events (event-dedup, ~daily+ spacing) |
| `TRADES_PER_MONTH` | 2.79 (LONG, D1-uptrend regime only) |
| `WR` | reached-2R 0.396 · positive-rate 0.509 |
| `RR / payoff` | fixed 1:2 structural (rr1.5 also robust); low-WR/high-payoff (§9-compliant) |
| `AVG_R_BASE` / `AVG_R_STRESS` | +0.460 / **+0.443** |
| `PF` | 1.94 (STRESS) |
| `MAX_DD` / `MAX_LOSS` | −6.19R / −1.114R |
| `BEST_1/5/10PCT_REMOVED` | +0.414 / +0.350 / **+0.246** (all positive) |
| `DISC` / `CONF` | +0.52 (n≈31) / +0.33 (n≈22) — both positive |
| `TEMPORAL_BLOCKS` | 2021 +0.053(n10) · 2022 +1.000(n8) · 2023 +0.428(n35); CALIB 2024 +0.223(n24) |
| `MEDIAN_SL_PIPS` / `MEDIAN_TARGET_PIPS` | 190 / 379 |
| `S5_OVERLAP` | S5 = 2021–2023 M5 intraday, different mechanism/horizon — conceptually independent |
| `H4_BO_RAW_S_OVERLAP` | different population (2011–2018) + opposite side — independent |
| `IMPLEMENTATION_FINGERPRINT` | `c60357cb61f1ee3798d6d2b48c2729a6ac65277aa77f8f3b5873dba762204f95` |
| `CONFIG_FINGERPRINT` | `3ceb5cd9ce7266a37ff5fdfa3a4811fb72110193db8875ca4fabfae341dad1ee` |
| `LEDGER_FINGERPRINT` | `98a8b906dbd9e0f6e469cc02d35fe4a01c07b5d20d0532b77f46c6aefb030ae8` |

## 3. Robustness evidence (§26) — what passed
- **Cost:** BASE +0.46 -> STRESS +0.44 (cost impact small; not a cost-fragile edge).
- **Best-k%-removed:** +0.41/+0.35/+0.25 (1/5/10) — **the edge is not carried by a few trades.** (This is the property the entire graveyard failed.)
- **Chronological DISC/CONF:** both positive, no shuffle, no rescue-after-CONF.
- **Year consistency:** all 3 DEV years positive.
- **Out-of-selection CALIB 2024:** positive (+0.223 avgR, PF 1.47) — not used for any parameter choice.
- **Parameter neighborhood (full grid reported):** stable in horizon (H30/42/60) and RR (1.5/2.0); the a-priori core W20/H42/rr2 sits inside a positive region.
- **Path-first:** median MFE 1.35R > median MAE 1.03R (favorable-before-adverse asymmetry).
- **Mechanistically distinct:** 6% overlap with H4-`TREND_UP` bars (fires in intra-trend consolidations).

## 4. Honest limitations (§37 — bounded; forwarded, NOT hidden)
1. **W-band:** robust W≈14–20, **collapses at W=28**. The claim is bounded to compression windows ~14–20 H4 bars.
2. **Dedup-material:** requires principled event-dedup (cooldown 20); dense re-entries (cd12) degrade best-10%-removed. Causal, but disclosed.
3. **Direction correlation:** LONG trend-beta -> correlated P&L with frozen LONG survivors; adds frequency, not a new direction. Overlap vs their actual ledgers must be measured at validation.
4. **Sample:** N=53 (2022 n=8); low absolute count. 2021 is the weak year (+0.05).
5. **Multiple testing:** survivor of ~13 loop hypotheses + 60+ prior — disclosed; the independent validator should apply its own multiplicity accounting.
6. **M5 execution not modeled** (next-H4-open proxy; conservative stop-wins-ties -> lower-bound WR/expectancy).

## 5. Package artifacts
- `COMP_CONT_L_STRATEGY_SPEC.md` — self-contained frozen spec (reproduce without this report).
- `comp_cont_L_package.json` — config + metrics + fingerprints + full 53-trade ledger.
- `frontier5_compcont.py` (discovery) + `frontier5_vet.py` (neighborhood/CALIB/ledger) + `swing_base.py` + `m5_data.py` (harness).
- Living artifacts: `ALPHA_RESEARCH_FRONTIER_REGISTRY.md`, `ALPHA_HYPOTHESIS_REGISTRY.md`, `ALPHA_GRAVEYARD.md`, `ALPHA_FAILURE_MODE_MAP.md`, `ALPHA_DISCOVERY_CHECKPOINTS.md`.

## 6. CEO recommendation
1. **`NEW_ROBUST_STRATEGY_CANDIDATE_FOUND` — `COMP-CONT-L-rr2`** is the first genuinely new candidate this loop produced. It clears the internal robustness pipeline (best-10%-removed, DISC/CONF, year-consistency, CALIB out-of-selection) that the entire graveyard failed, on a coherent causal mechanism.
2. **Alpha does not ratify.** No `VALIDATED`/`PRODUCTION_READY`/`AI_TRADER_READY`. Handed to **Statistician** for independent validation (multiplicity, overlap-vs-frozen-LONG, holdout); Red Team thereafter.
3. **Classification:** `REGIME_SPECIFIC_ROBUST_CANDIDATE` (D1-uptrend only), LONG-only. Portfolio value = added *opportunities* in bullish regimes (correlated with existing LONG beta, not a new direction). The SHORT / new-direction gap in the portfolio remains open.
4. **Loop status:** per §35 active search **STOPS** on this candidate and returns to CEO. Global program remains **ACTIVE**; on validation result the CEO may restart the loop (queued next frontiers recorded). No MI/S5/frozen-strategy change; broker disabled; DEV-selection honored.

**Terminal status:** `CONTINUOUS_ALPHA_RESEARCH_CHECKPOINT` · `NEW_ROBUST_STRATEGY_CANDIDATE_FOUND` · `READY_FOR_INDEPENDENT_VALIDATION`. **STOP.**
