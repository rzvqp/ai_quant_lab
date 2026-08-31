# GOLD_BEHAVIOR_ATLAS_V1 — XAUUSD behavioral event families (causal, cost-aware)

Market represented as bounded behavioral events, not arbitrary candles. Measured on cur_data M15 (2011-2026, causal). Outcome/context
per family. **A family is interesting only where the SAME behavior becomes ASYMMETRIC in some causal context** — none did directionally.

| EVENT FAMILY | N (approx) | forward behavior (causal) | directional asymmetry / tradeability |
|---|---|---|---|
| STRUCTURAL_BREAK (break prior-20 extreme) | 15,962 | WR 0.272 @2R:1R; base netR −0.425 | NONE — no ex-ante discriminator flips sign (contrast miner) |
| FAILED_BREAK (wick beyond, close back) | 21,379 | fade-to-mid netR −0.256 all eras | NONE — mean-reversion efficient |
| SWEEP → OPPOSITE_BREAK (liquidity-grab reversal) | 1,905 | reversal netR −0.259 all eras | NONE |
| COMPRESSION_EXPANSION | 4,304 (VOLPATH) | expansion REAL + cross-era-stable (P(2R)=0.99) | magnitude YES / DIRECTION symmetric (unmonetizable) |
| DOUBLE_BREAK / WHIPSAW | 47% of compression events | break→recross→opposite break | the core hazard; kills breakout & straddle |
| RECLAIM (break fail then re-break) | — | continuation ~coinflip | NONE (SF-1, VOLPATH) |
| RANGE_EDGE_REJECTION (Asia/London extreme) | 3,211 (SF-1) | continuation/reversal ~0.49-0.53 | NONE — session extremes coinflip |
| SESSION_EXPANSION (US macro/NYSE open) | 1,995 / 1,393 | ORB net −0.39 / −0.46 | NONE beyond S5's narrow config |
| POST_EVENT_DISPLACEMENT (impulse) | — | displacement break gross −0.046 | NONE — move already spent |
| TREND_PULLBACK (zone reaction) | 453 (chrono) | net-neg 23/27 quarters | NONE |
| CHoCH / STRUCTURAL_BREAK (transition) | 18,825 | EXACT null 0.334 | NONE — zero directional info |
| TARGET_SPACE (room to 100b extreme) | 15,962 | more room = WORSE (−0.49 vs −0.34) | NONE (counter to intuition: room = late-stage) |

**Non-directional cross-era-stable structure that DOES exist (information assets, not edges):**
- Compression duration → expansion magnitude/timing (VOLTIME-1). DXY-impulse → +expansion magnitude (DXY-NDX1). Session-phase whipsaw
  map (SF-3: US-session cleanest 0.088, macro choppiest 0.42). Path geometry: whipsaw-dominant + symmetric (VOLPATH). HTF-alignment
  reduces (but never flips) the structural-break loss (−0.379 vs −0.493).

**Atlas verdict:** every event family's DIRECTIONAL outcome is efficient in price-only features (no context makes it asymmetric enough
to beat cost). The stable structure is non-directional (magnitude/timing/whipsaw). S5 is the singular exception (session-timed break).
