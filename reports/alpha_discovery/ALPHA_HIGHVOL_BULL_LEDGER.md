# HIGHVOL_BULL-Regime Specialist Program — Ledger

Mandate: MULTI-REGIME SPECIALIST PORTFOLIO (CEO 2026-08-23), regime #2. CRS-1/RANGE frozen & off-limits.

## FROZEN regime: HIGHVOL_BULL_V1 (highvol_bull_regime.py, BEFORE any P&L)
`fp=HIGHVOL_BULL_V1|H4|volratioTRAIL360|VHI1.20|VLO0.90|Ebull0.30|Nenter4|causal-trailing`. Persistent causal state machine:
enter after 4 consecutive H4 bars of (ema20>ema50 & effic>0.30 & atr/trailing-median360>=1.20); hold while (ema20>ema50 &
effic>0 & vol_ratio>=0.90); exit on trend break or vol collapse. STRUCTURAL not calendar. Causal at every timestamp (bounded
efficiency + trailing vol baseline shift(1), no global percentile). Population 6.6% of H4 (1588 bars), 77 episodes, median 2.7d,
recurs every year (peaks 2020 COVID-surge 13%, 2025 melt-up 16%). Disjoint from RANGE_REGIME_V1 (low |effic|) and CRS-1 (down).

## Information test (hb_info.py) — forward direction is ERA-SPLIT
Regime ON forward path: DISC<=2021 up-dn **-0.39** / fwdRet -0.36 ATR (melt-up REVERTS: 2011/2020 blowoffs); CONF 22-24 up-dn
**+1.50** / +1.46 (continues up); OOS 25-26 up-dn +0.71 / +1.16 (continues up). The SAME structural regime precedes reversal
pre-2021 and continuation post-2022 = R20 at regime level.

## RE-SCREEN old LONG-continuation (hb_rescreen.py, gated, unchanged) — FAIL DISC
(A) pure regime LONG: avgR -0.014, DISC **-0.087** / CONF -0.002 / OOS +0.169. (B) pullback3 LONG in-regime: avgR -0.017,
DISC **-0.082** / CONF +0.055 / OOS +0.081. Both fail DISC (as info predicted). Old verdicts stand.

## NEW DISCOVERY — cross-scale D1 confluence (hb_xscale.py, CRS-1 lesson, not clone) — does NOT resolve era-split
HB & D1-UP LONG: DISC **-0.053** / CONF +0.003 / OOS +0.169 (still DISC-negative). HB & D1-UP SHORT control: -0.058 (also loses).
D1 confluence does not distinguish blowoff-top (reverts) from continuation. Info by D1 state confirms DISC negative regardless.

## HIGHVOL_BULL conclusion — NO SURVIVOR (directionally era-ambiguous)
No consistent-direction specialist exists: LONG fails DISC (pre-2021 blowoffs revert), SHORT fails CONF/OOS (post-2022 continues),
D1 cross-scale doesn't separate them. The regime is real/causal/persistent but directionally era-ambiguous. Per §6 (DISC>0
required) no survivor; not mined. Per §8 -> select next distinct regime immediately.
