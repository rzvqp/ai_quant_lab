# ALPHA_H4_PARENT_STATE_CONTRACT (FROZEN)

**Mandate:** `ALPHA-XAUUSD-H4-M15-PATH-SHAPE-DISCOVERY-001`, §3-4. Frozen BEFORE any M15 path-shape outcome is evaluated (`h4_parent.py`). Causal, price-only. Reuses the already-frozen `state_regime.regime()` taxonomy applied to the causal H4 frame. All later path-shape lifts (§8) are measured vs the per-H4-state M15 base rates below, **within the same era**.

## H4 parent-state definition (frozen)
`regime(H4frame)` — priority QUIET > UP > DOWN > CHOP > TRANSITION; all inputs causal (known at H4 bar close), aligned to each M15 bar by `close_time <= M15.time` (last completed H4 bar, no lookahead):
- `eff` = directional efficiency(20); `tr` = (EMA20-EMA50)/ATR; `vr` = ATR/ATR_ma.
- **UP**: eff>0.35 & tr>0.2. **DOWN**: eff<-0.35 & tr<-0.2. **QUIET**: vr<0.9 & |eff|<0.25 (research-local neutral; **NOT canonical RANGE_CONFIRMED**, §4 — independent research identity). **CHOP**: |eff|<0.25 (not QUIET). **TRANSITION**: else.

## Occurrence & N-sufficiency (event-deduped EffN in the base-rate tables)
| state | DEV % | b0 % | b1 % | DEV EffN | b0 EffN | b1 EffN |
|---|---|---|---|---|---|---|
| UP | 14.7 | 13.4 | 15.7 | 764 | 896 | 1056 |
| DOWN | 10.4 | 14.3 | 10.6 | 544 | 959 | 716 |
| QUIET | 17.5 | 21.7 | 15.2 | 904 | 1444 | 1029 |
| CHOP | 35.5 | 29.5 | 34.7 | 1858 | 1986 | 2357 |
| TRANSITION | 21.1 | 20.4 | 23.2 | 1114 | 1367 | 1588 |

All five states have EffN >= 500 in every era -> the same-H4-state cross-era gate (§10) is viable for all states. Distributions reproducible per-year (2021/2022/2023).

## Per-H4-state M15 base rates (P(+X/-Y) 8h, event-deduped) — the §8 comparison baselines
**Two structural facts these tables lock in:**
1. **Era-dependence of absolute levels:** b1 (2016-2018 low-vol) has markedly lower P and smaller MFE/MAE across ALL states (MFE med ~31p vs ~44-56p in DEV/b0). => absolute P is NOT comparable across eras; only LIFTS within the same state/era are.
2. **Instantaneous H4 state alone = era-dependent directional bias** (not cross-era-stable): UP-state DEV mildly SHORT-favoring (pullback) but b1 mildly LONG; DOWN-state DEV mildly LONG (mean-revert) but b0 strongly SHORT (continuation); QUIET ~symmetric all eras; CHOP DEV LONG / b0 SHORT / b1 symmetric.

### DEV 2021-2023
| state | L 50/50 | L 70/50 | L 100/70 | L advF | S 50/50 | S 70/50 | S 100/70 | S advF | MFE med/P75 | MAE med/P75/P90 |
|---|---|---|---|---|---|---|---|---|---|---|
| UP | 0.37 | 0.27 | 0.18 | 0.48 | 0.45 | 0.31 | 0.24 | 0.41 | 44/86 | 54/101/163 |
| DOWN | 0.43 | 0.29 | 0.17 | 0.40 | 0.37 | 0.26 | 0.16 | 0.46 | 49/86 | 41/80/134 |
| QUIET | 0.41 | 0.30 | 0.19 | 0.45 | 0.42 | 0.31 | 0.18 | 0.44 | 50/90 | 51/93/139 |
| CHOP | 0.41 | 0.27 | 0.18 | 0.37 | 0.34 | 0.23 | 0.14 | 0.44 | 46/83 | 40/74/127 |
| TRANSITION | 0.38 | 0.25 | 0.13 | 0.40 | 0.38 | 0.27 | 0.18 | 0.40 | 42/76 | 43/87/137 |

### b0 2011-2013
| state | L 70/50 | L 100/70 | S 70/50 | S 100/70 | MFE med | MAE med |
|---|---|---|---|---|---|---|
| UP | 0.26 | 0.20 | 0.26 | 0.19 | 47 | 51 |
| DOWN | 0.31 | 0.22 | **0.35** | **0.28** | 56 | 64 |
| QUIET | 0.27 | 0.20 | 0.34 | 0.25 | 49 | 54 |
| CHOP | 0.27 | 0.18 | 0.31 | 0.23 | 46 | 49 |
| TRANSITION | 0.30 | 0.21 | 0.28 | 0.20 | 50 | 46 |

### b1 2016-2018 (low-vol era — all levels compressed)
| state | L 70/50 | L 100/70 | S 70/50 | S 100/70 | MFE med | MAE med |
|---|---|---|---|---|---|---|
| UP | 0.20 | 0.10 | 0.17 | 0.08 | 33 | 31 |
| DOWN | 0.16 | 0.08 | 0.19 | 0.08 | 30 | 35 |
| QUIET | 0.16 | 0.10 | 0.19 | 0.11 | 33 | 34 |
| CHOP | 0.17 | 0.08 | 0.16 | 0.08 | 31 | 31 |
| TRANSITION | 0.16 | 0.07 | 0.15 | 0.07 | 32 | 30 |

**Frozen. Next:** M15 path-shape / sequence information conditional on each H4 parent state, measured as lift vs these per-state/per-era base rates, LONG/SHORT separate, event-deduped, same-H4-state cross-era gate.
