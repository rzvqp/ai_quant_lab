# ALPHA_BROAD_SCREEN_RESULTS — BATCH A (cross-information-class)

Engine: `bscreen.py` on `sb.simulate`, STRESS RT 0.24, eras b0/b1(2011-18)/DEV(2021-23)/CAL(2024), event-deduped, cross-era sign-consistency. This table IS the Batch A multiplicity ledger (§36/§37): 14 hypotheses (7 mechanisms × sides), all counted, none hidden.

| # | hypothesis | info class | side | rr | poolN | poolR(STRESS) | best1 | b0 | b1 | DEV | CAL | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 | ORB_NY_L (S5 anchor) | breakout/opening-range | L | 3.0 | 1518 | **+0.074** | +0.043 | +0.111 | +0.007 | +0.115 | +0.065 | **SURVIVOR** (=S5, redundant §30) |
| A2 | ORB_NY_S | breakout/opening-range | S | 3.0 | 1500 | −0.078 | −0.109 | +0.006 | −0.115 | −0.089 | −0.241 | ELIM NEG_STRESS |
| A3 | ORB_LON_L | session/breakout | L | 2.0 | 1555 | −0.138 | −0.160 | −0.141 | −0.118 | −0.202 | +0.014 | ELIM NEG_STRESS |
| A4 | ORB_LON_S | session/breakout | S | 2.0 | 1668 | −0.021 | −0.042 | +0.030 | −0.046 | +0.023 | −0.300 | ELIM NEG_STRESS |
| A5 | PDH_break_L | ref-level/prev-day | L | 2.0 | 4807 | −0.217 | −0.239 | −0.257 | −0.102 | −0.273 | −0.369 | ELIM NEG_STRESS |
| A6 | PDL_break_S | ref-level/prev-day | S | 2.0 | 4385 | −0.215 | −0.237 | −0.112 | −0.228 | −0.352 | −0.140 | ELIM NEG_STRESS |
| A7 | PDH_fade_S | ref-level/reaction | S | 2.0 | 1589 | −0.170 | −0.192 | −0.121 | −0.193 | −0.229 | −0.075 | ELIM NEG_STRESS |
| A8 | PDL_fade_L | ref-level/reaction | L | 2.0 | 1559 | −0.153 | −0.175 | −0.161 | −0.171 | −0.149 | −0.034 | ELIM NEG_STRESS |
| A9 | PWH_break_L (CAND-0037) | ref-level/weekly | L | 2.0 | 3938 | −0.157 | −0.179 | −0.204 | −0.132 | −0.205 | +0.068 | ELIM NEG_STRESS |
| A10 | PWL_break_S (CAND-0037) | ref-level/weekly | S | 2.0 | 3135 | −0.334 | −0.358 | −0.220 | −0.463 | −0.282 | −0.455 | ELIM NEG_STRESS |
| A11 | MR_ext_L (2σ vs SMA100) | mean-reversion | L | 2.0 | 6983 | −0.741 | −0.769 | −0.594 | −0.958 | −0.776 | −0.212 | ELIM NEG_STRESS |
| A12 | MR_ext_S | mean-reversion | S | 2.0 | 7736 | −0.744 | −0.772 | −0.575 | −0.943 | −0.761 | −0.566 | ELIM NEG_STRESS |
| A13 | PB_trend_L (EMA pullback) | trend/pullback | L | 2.0 | 4307 | −0.781 | −0.809 | −1.108 | −0.747 | −0.507 | −0.394 | ELIM NEG_STRESS |
| A14 | TOD_NYopen_L (13-15h) | time-of-day | L | 2.0 | 1705 | −0.654 | −0.682 | −0.687 | −0.929 | −0.397 | −0.127 | ELIM NEG_STRESS |

## Findings
1. **Calibration PASS.** The modern multi-era screen reproduces **S5 (`ORB_NY_L`) as the sole survivor**, positive in ALL FOUR eras including 2011-2018 (out of S5's original discovery corpus) — validates the screen and shows S5 generalizes beyond its `REGIME-LIMITED` label. Redundant with frozen S5 → not new alpha.
2. **CAND-0037 falsified (multi-era).** The existing "first robust candidate" (weekly-level breakout, PWH/PWL) is NEG_STRESS across b0/b1/DEV (−0.16/−0.33). It was validated only on the single 2022-2025 bull; it does not survive cross-era + ratified cost. Exactly the falsification the original corpus could not perform.
3. **Broad class-level negatives (§40).** Under ratified STRESS cost + multi-era: reference-level break (prev-day & prev-week), level fade/reaction, mean-reversion (2σ), trend-EMA-pullback, session-time all bounded-negative, cross-era-consistent. Mean-reversion is the worst class (−0.74). No sign-flip rescues; the negatives are stable.
4. **Structure, not time.** `TOD_NYopen_L` (enter at NY open) −0.65 vs `ORB_NY_L` (enter on breakout of the NY opening range) +0.07 → the edge is opening-range **structural event**, not the clock. Confirms R12 (session time = vol-timing, not directional).
5. **Long-only ORB.** `ORB_NY_S` negative → S5's long-only spec is correct; the NY-open momentum edge is directionally asymmetric (§22).

## Ledger summary
Batch A: 14 hypotheses screened · 1 SURVIVOR (redundant=S5) · 13 ELIMINATE · 0 NEW screen-survivors → 0 to deepening. Information classes falsified-under-modern-governance this batch: reference-level (prev-day, prev-week, reaction), mean-reversion, trend-pullback, session-time, non-NY/short opening-range. Next: Batch B = untested classes (structure-break, range-rotation, momentum/HOLD-displacement, MTF-alignment, acceleration/exhaustion, volatility-onset) + bounded ORB-structure variants.
