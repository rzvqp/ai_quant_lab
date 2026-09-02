# CTS V2 — Failure autopsy (§29)

What the contextual selector recognized, what it missed, grounded in the frozen walk-forward results and the measured idea-class
discrimination. No example was used to retune any model (interpretation only).

## What the model RECOGNIZED (the real, controlled signal)
Across all three setups the selector's discrimination is carried by **participation / volatility STATE at the decision** — `gA_volrank`
(higher → better), `atr_vs_atrma` (expansion → better), `compress_flag` (compressed → worse), and the **relative-participation** channel
(`vol_persist_toward` higher → better, `progress_per_vol` higher → worse). These beat random-N selection (3/3 setups) and label-permutation
(2/3), so the selector genuinely separates: it SKIPS trades reached in a **compressed, low-participation** state and TAKES trades reached with
**genuine expanding participation**. The market story is coherent: a setup fired into a quiet, low-volume drift resolves worse than the same
setup fired when real participation is behind the move. `TRUE_SKIP_LOSERS` cluster in compression/low-volume; `TRUE_TAKE_WINNERS` in expansion.

## What the model MISSED
1. **It cannot make the setups positive.** Even its best selection (SETUP_3 auction, B-static @60% retention) is −0.072R — the participation
   signal is *necessary-not-sufficient*. `FALSE_TAKE_LOSERS` are the large residual: trades with good participation/expansion context that still
   lost — participation raises the odds but does not remove the base strategy's negative edge.
2. **`FALSE_SKIP_WINNERS`**: a substantial fraction of winners arrive in quiet/compressed conditions the model skips — so pushing selection
   harder (to avoid more losers) also discards these winners, which is why the winner-retention frontier degrades and no ≥60%-retention point
   turns positive.
3. **Arrival ORDER and STRUCTURE carry little.** Destroying bar order costs only +0.006…+0.035R (below the +0.05 bar), and HH/LL structural
   pressure is the weakest idea class (0.0093). The model that sees the ordered sequence does not beat the one that sees only the setup-relative
   static state — the *state* the market is in at the decision dominates the *path* by which it arrived, for these three mechanisms.

## What differentiates FALSE TAKES from TRUE TAKES
Within the high-participation TAKE region, the surviving separator is thin and setup-specific (e.g. distance-to-reference and penetration for
the auction/breakout setups) — not a further path/sequence pattern. That is the honest limit: once the participation/expansion state is known,
the ordered approach geometry adds no material further separation on these setups.
