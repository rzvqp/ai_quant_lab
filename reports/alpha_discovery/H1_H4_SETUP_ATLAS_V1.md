# H1_H4_SETUP_ATLAS_V1 — causal multi-timeframe setup vocabulary & census

H1_H4_SETUP_M5_EXECUTION_V1 §27 deliverable. Governed OANDA XAUUSD only. Causal MTF: M15 (base) → H1 (UTC hour) → H4 (UTC 4h blocks).
At an M15 decision bar t, HTF context uses only completed H1/H4 bars (close_time ≤ t). Code: `htf_core.py`, `htf_setups.py`, `htf_atlas.py`.

## 1. Data audit (§3) — mechanically verified
```
M15_SOURCE   = OANDA XAUUSD (cur_data), 355,696 bars, 2011-07-26 → 2026-07-27, UTC, 15-min
H1_SOURCE    = causal aggregation of M15 on UTC hour boundaries → 89,549 bars
H4_SOURCE    = causal aggregation of M15 on UTC 4h blocks (00/04/08/12/16/20) → 23,990 bars
M5_SOURCE    = OANDA_XAUUSD_M5.csv (native), 354,669 bars, 2021-07-27 → 2026-07-27, UTC, 5-min, 1,555 days
TIMEZONE     = UTC ; SESSION via hour-of-day (AS<8, LN 8-13, NY 13-20, LT 20-24)
KNOWN_GAPS   = weekend gaps (normal); M5 begins 2021-07-27 (10y after M15)
CONSTRAINT   = M5-execution research restricted to native 2021-07-27+ overlap; NO synthesis of pre-M5 history
median ATR   = M15 $1.747 / H1 $3.79 / H4 $7.61 ; canonical cost 0.24R@1ATR(M15) = $0.419 round-trip
```

## 2. H4 context (frozen, causal, small set — §8)
`TREND_UP` (ema20>ema50 & close>ema50) / `TREND_DOWN` / `BALANCE`. Census over M15 bars: TREND_UP 163,040 · TREND_DOWN 136,682 ·
BALANCE 55,961. Built from EMAs on completed H4 bars — verified no lookahead (mapped H4 close_time ≤ M15 close time for all mapped bars).

## 3. Location variables (§6)
`loc` = position of price within the current H4 [50-bar low, 50-bar high] leg (0=discount, 1=premium); `room` = distance to the prior H4
swing extreme in H4-ATR (target space); H1 swing extremes (swH/swL) for structural stops. Location is applied as the H4 filter in each
setup (e.g. trend-continuation only in discount; breakout only when room>1 H4-ATR).

## 4. H1 setup families mechanized (§9) — 4 distinct causal mechanisms
| family | H4 context filter | H1 setup | direction | related failed research |
|---|---|---|---|---|
| **PBK_TREND** | TREND_UP & discount / TREND_DOWN & premium | H1 pullback then turn-bar | continuation | WUZ-1 (pullback-to-zone, FAIL −0.167) |
| **RECLAIM** | not-against-H4-trend | local sweep of 10-bar support/resist then close back | continuation | NKB sweep-reversal −0.259 / reclaim coinflip |
| **RANGE_FADE** | BALANCE | H1 pokes 50-bar extreme, closes back inside | mean-reversion | NKB generic fade net-neg |
| **TGT_BREAK** | TREND/BALANCE & room>1 H4-ATR | H1 breaks swing extreme with open target space | continuation | Contrast-Miner target-space anti-predictive |

## 5. Census (HTF_ON baseline, net-R price-cost, 2R:1R, structural stop) — full detail in the contrast report
| family | N | indep-ep | net-R | HTF_OFF net-R | WR | verdict |
|---|---|---|---|---|---|---|
| PBK_TREND | 324 | 230 | −0.084 | −0.102 | 0.380 | sign-reverses across eras → FALSIFIED |
| RECLAIM | 6,834 | 2,938 | −0.100 | −0.123 | 0.386 | all-neg except marginal O-LONG → FALSIFIED |
| RANGE_FADE | 760 | 473 | −0.146 | −0.149 | 0.361 | all cells negative → FALSIFIED |
| TGT_BREAK | 460 | 394 | −0.023 | −0.008 | 0.454 | positive only in O-era (bull) → FALSIFIED cross-era |

**Headline:** across all four families the H4-context filter (HTF_ON) changes net-R by <0.02 vs no filter (HTF_OFF), sometimes for the
worse. HTF *selection* does not create asymmetry. The only positive cells are direction×era (long-in-bull / short-in-bear) = the known
R20 era-trend artifact, present with or without HTF selection.
