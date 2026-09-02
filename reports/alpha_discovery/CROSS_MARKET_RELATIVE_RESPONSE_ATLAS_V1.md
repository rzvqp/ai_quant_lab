# CROSS_MARKET_RELATIVE_RESPONSE_ATLAS_V1 — data audit + relative-response census

CROSS_MARKET_RELATIVE_RESPONSE_FACTORY_V1 §23 deliverable. Code: `cm_core.py`, `cm_scan.py`. Reuses the ratified DXY causal join
(`dxy_data.py`). No new data acquired (§3).

## 1. §3 data audit — CROSS_MARKET_DATA_AUDIT_PASS = YES (scoped)
```
XAUUSD   = OANDA governed M15/H1/H4/D1 (full 2011-2026)
DXY      = ICE DXY H1, THREE governed slices only:  b0 2011-07-26→2013-09-27 (13,397 XAU-H1 matched)
                                                     b1 2016-01-11→2018-04-06 (13,213)
                                                     y2123 2021-07-27→2023-12-29 (6,777)
           2024+ PROTECTED (not accessed). same-hour DXY match 97.4 / 97.8 / 99.9%. Contract: DXY available at time+3600, backward asof.
OTHER MARKETS = NONE on disk (no NDX/SPX/VIX/yields/oil/silver) -> family F (dual-confirmation) NOT testable.
```
**Limitation (disclosed):** single cross-market series (DXY), H1 resolution, ~7 years in 3 disjoint blocks, no 2024+, no risk proxy. This
is sufficient to test the relative-response mechanism (families A–E) but not a definitive cross-market answer. Not DATA_BLOCKED (the core
mechanism is testable); a fuller test needs a governed risk-market series + 2024+ DXY.

## 2. The NEW variable — relative-response residual (not the falsified simple DXY impulse, §4)
Trailing beta W=120 of XAU 1h return on DXY 1h return (strictly past). `EXPECTED = beta·DXY_move`; `RESIDUAL = XAU_move − EXPECTED`;
`z-residual = RESIDUAL / trailing std(XAU_move)`. `implied-z (ez4)` = expected 4h move in vol units; `actual-z (az4)` = actual 4h move.
Positive z = XAU stronger than DXY implies; negative = weaker. All causal.

## 3. Families (dedup 20 raw → 5 distinct; F excluded for lack of data)
| family | dislocation state | prediction | direction |
|---|---|---|---|
| A CATCH-UP | DXY implied a move (\|ez4\|>1), XAU under-reacted (\|actual\|<0.5·implied) | XAU catches up in implied dir | both |
| B RELATIVE-STRENGTH | XAU opposes the implied move (z4>1 vs ez4<0, or mirror) | XAU's own strength continues | both |
| C OVERSHOOT | XAU over-reacted (\|az4\|>2 and >1.8·implied) | partial reversal (fade) | both |
| D LEAD-LAG | DXY displacement then delayed XAU repricing | implied dir after delay | both (via t+1 entry / impulse control) |
| E SESSION-RESOLUTION | dislocation (\|z4\|>1) before London/NY | active session resolves toward implied | both |

## 4. Results (next-H1-open entry, 1×ATR stop, 2R, conservative same-bar, cost 0.419/risk)
| family | N | net-R | D (b0+b1) | O (y2123) | verdict |
|---|---|---|---|---|---|
| A catch-up | 473 | −0.084 | +0.031 | −0.359 | FALSIFIED (era-unstable) |
| B relative-strength | 354 | −0.240 | −0.333 | −0.013 | FALSIFIED |
| C overshoot-fade | 1,776 | −0.125 | −0.162 | +0.043 | FALSIFIED |
| E session-resolution | 156 | −0.058 | −0.047 | −0.087 | FALSIFIED |
| **CONTROL simple-DXY-impulse** | 2,149 | −0.069 | −0.020 | −0.188 | (reference; already negative) |

No family is net-positive; all era-unstable. The decisive comparison is in the contrast report.
