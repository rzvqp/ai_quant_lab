# VOLTIME_LEDGER — NON_DIRECTIONAL_VOLATILITY_TIMING_DISCOVERY_V1 (CEO mandate 2026-08-24)

Question: NOT up/down, but WHEN a tradeable move comes, how large, how fast, and what causal state precedes it. Direction is NOT
predicted; the market event (breakout/acceptance/displacement) supplies it. Info-first; strict causal; S5 frozen.

## VOLTIME-1 (info-first, `voltime_info.py`) — compression predicts expansion, CROSS-ERA-STABLE (strong)
Forward non-directional targets over K=32 bars vs causal compression state (all bars<=T). Baseline: fwdRange=7.26ATR, P(2R either
dir)=0.888, medT2R=6b, P(3R)=0.737.
- **Compression DURATION (consecutive ATR<ATR_ma) is the standout, monotonic:** dur[0,1) 6.69ATR/P2R0.844 -> dur[10,25) 7.70/0.959
  -> **dur[25+) 9.39ATR/P2R0.990/P3R0.922/medT2R5b.** Longer compression -> larger, faster, more-certain forward expansion.
- **Cross-era stable:** compressed-bin (ATR_ratio<0.70) P(2R) = D 0.949 / C 0.963 / O 0.966; fwdRange 7.75/7.80/8.07. UNLIKE direction
  (era-trend), volatility expansion after compression is stable across all eras — confirms R26 quantitatively.
- ATR_ratio quintile monotone (compressed Q1 7.84/0.957 -> expanded Q5 5.53/0.763); Donchian-width weaker.
- **FOUNDATION:** the move reliably COMES after compression. Open crux (R26): does a breakout capture it after costs + whipsaw?
  -> VOLTIME-2 tests the tradeable compression-breakout (direction supplied by the break). Info-first threshold MET; proceeding to
  mechanize + falsify (not yet an edge — path/cost is the decisive test).
