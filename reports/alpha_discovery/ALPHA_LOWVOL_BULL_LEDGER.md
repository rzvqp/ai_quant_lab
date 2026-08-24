# LOWVOL_BULL-Regime Specialist Program — Ledger (regime #3)

## FROZEN regime: LOWVOL_BULL_V1 (lowvol_bull_regime.py, before P&L)
`fp=LOWVOL_BULL_V1|H4|volratioTRAIL360|VLOhi0.95|Ebull0.30|Nenter4|causal-trailing`. Low causal vol (atr/trailing-median<=0.95)
+ ema-up + effic>0.30; persistent state machine. 8.2% of H4 (1956 bars), 141 episodes, ~2.0d median, recurs every year. Causal
(trailing baseline, bounded effic, no global pct). Distinct from HIGHVOL_BULL (high vol), RANGE (low effic), CRS-1 (down).

## Information test — UNIQUE era-CONSISTENT positive drift
Regime ON fwdRet(96): DISC +0.21 / CONF +0.23 / OOS +1.06 ATR — POSITIVE in ALL partitions (first era-consistent directional
signal in the multi-regime search; unlike HIGHVOL_BULL's era-split). BUT up-dn slightly negative & P(upFirst)~0.50 (coinflip
path) -> the drift is a slow net-up-grind, not a first-move edge.

## Re-screen + wide-stop + D1 cross-scale (lb_screen.py, lb_xscale.py) — ALL FAIL
LONG at 1.5/2.5/3.0 ATR stops, rr 1.5/2/3, pullback, and D1-UP confluence: avgR -0.12..+0.015, DISC NEGATIVE in every config
(D1-UP LONG 2ATR: DISC -0.029/CONF +0.198/OOS +0.011). The drift (~0.2 ATR/24h) is TOO SMALL vs the ATR-bracket stop + STRESS
costs + coinflip path (WR 0.30-0.41) -> un-bracketable. No survivor.

## LOWVOL_BULL conclusion — NO SURVIVOR (drift real & era-consistent but SUB-COST)
The one regime with consistent direction, but the direction is a low-vol drift smaller than costs+noise; not extractable via
directional bracket. Fundamental low-vol economic constraint (consistent with R26: low-vol regime's signal magnitude too small).
Not mined. Per §8 -> next regime.
