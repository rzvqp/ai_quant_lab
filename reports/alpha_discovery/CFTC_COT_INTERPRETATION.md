# CFTC COT CONTEXT V1 — interpretation (post-freeze)

Unblinded only after the walk-forward, gates, and controls were frozen. Per §30 no participant category is equated with "smart/dumb money".

## What the evidence says
Adding causally-available COMEX-gold futures positioning (managed-money / producer / swap-dealer / other-reportable net levels, weekly changes,
historical extremes, cross-participant disagreement, and price×positioning interactions) to the XAU baseline changed selected expectancy by at
most +0.002R at 60% winner retention — and on the breakout setup adding COT was ~0.02R *worse*. Permuting the trade-specific COT within year
buckets (COT-destruction) did not degrade the result on any setup (on the breakout setup the real COT was slightly worse than destroyed), so
the COT features carry no trade-specific winner-vs-loser information for these setups — they behave like noise the model can only overfit.

## The specific sub-questions
- **Managed money / producer / swap-dealer:** none carried value (destroying all COT features leaves the result unchanged).
- **Level vs change vs extreme:** no positioning level, weekly change, or historical extreme separated winners from losers.
- **Cross-participant disagreement:** within the null. **Price × positioning:** within the null.
- **Report age:** the median COT is 4.5 days old at decision (weekly, ~1-week lag) — a slow aggregate that does not condition intraday XAU setup quality.

## Honest framing
A well-powered tested null on a pre-registered COT representation and three setups. Per §30 no directional-positioning claim is made
(e.g. "managed-money longs = bullish"). This says nothing about COT in general — only that this positioning representation does not add
winner-vs-loser value to these XAU setups. Combined with the GC volume and GC OI nulls, the exchange-side futures information tested so far
(volume, open interest, positioning) does not condition these three XAU mechanisms.
