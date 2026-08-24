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

## VOLTIME-2/3 (`voltime_breakout.py`, `voltime_resolution.py`) — expansion NOT capturable by generic breakout (whipsaw=null)
Compression-range breakout (D=12,M=24,RR=2, STRESS 0.24), direction supplied by the break:
- RAW: 7,323 signals, **winrate 0.333 = EXACT 2R:1R null, gross +0.000**, net −0.240. Every era/session (incl NY)/neighbor negative.
- Direction-resolutions (mandate's list) ALL fail: DISPLACEMENT gross −0.046 (WORSE — a big break has already spent the move),
  ACCEPTANCE +0.012 (best gross, still net −0.228, not cross-era+), RETEST −0.005. Winrate pinned ~0.33 regardless of confirmation.
- **The real, cross-era-stable expansion (VOLTIME-1) is DIRECTIONALLY SYMMETRIC and uncapturable by generic break-confirmation** —
  the whipsaw exactly cancels the expansion. Confirms R26 from the volatility angle: predictable magnitude, unmonetizable direction.
  Note 82% of raw signals are Asian-session low-liquidity compressions. S5's NY-open session-timing remains the unique surviving
  direction-resolution. VOLTIME-4 next: S5-style opening-range breakout at the LONDON open (the most-principled second-edge location).

## VOLTIME-4 (`voltime_session.py`) — no generic second session-timing edge
Opening-range breakout (first-1h OR, both directions) at each session open, STRESS 0.24:
- ASIA(00h) net −0.246 (RR2)/−0.372 (RR3); LONDON(07h/08h) −0.290/−0.285 (RR2), −0.44/−0.41 (RR3); all net-negative, WR ~0.32, gross ~0.
- RR3 far worse everywhere (WR 0.13-0.22 — whipsaw dominates a distant target).
- **NY-ref caveat:** my NAIVE both-direction NY-13h ORB is ALSO negative (−0.459) — this does NOT contradict S5. S5 is LONG-ONLY with
  its specific OR/rr3/stop config (the "NY long-momentum" episode, mstrat.py:260-278); a generic both-direction ORB is not S5. This
  reinforces that S5's edge is NARROW and non-generalizable, not a generic "session ORB works" phenomenon.
- **VOLTIME frontier interim (4 families):** volatility expansion is REAL + predictable + cross-era-stable (VOLTIME-1), but NOT
  independently tradeable — generic breakout (V2), any direction-resolution (V3), and any session ORB (V4) all pin at the ~null 0.33
  winrate / net-negative after costs. Confirms R26 from the volatility angle: predictable magnitude, unmonetizable symmetric direction;
  S5's narrow NY-long config is the unique surviving direction-resolution. Next distinct angle: path-asymmetry / first-move fade after
  compression (does the first break reverse = liquidity grab?), the last non-breakout volatility-timing mechanism.
