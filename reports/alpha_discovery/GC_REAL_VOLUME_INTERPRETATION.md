# GC REAL-VOLUME CONTEXT V1 — interpretation (post-freeze)

Unblinded only after the primary walk-forward results, gates, and controls were frozen. Interpretation is constrained by the measured evidence.

## What the evidence says
Across all three XAU mechanisms (liquidity-sweep, breakout-retest, auction-value), adding genuine CME GC real traded-volume context to the XAU
setup-relative baseline changed selected expectancy by only +0.003…+0.011R at 60% winner retention — an order of magnitude below the +0.05R
information gate and the +0.03R real-volume-specific gate. Critically, permuting the trade-specific GC volume within time-of-day buckets
(volume-destruction) did **not** degrade the result, and a time-of-day-only baseline matched it. So whatever faint structure the GC-volume
features carried is indistinguishable from GC's intraday volume seasonality, not from genuine trade-specific participation.

## Why the trader-intuitive stories did not hold here
- **"Participation must confirm the move"** (G5/G6): GC participation accompanying or diverging from the XAU move did not separate winners from
  losers beyond the baseline — the XAU setups' outcomes are not conditioned on whether COMEX futures volume confirmed the spot move.
- **"Sustained volume beats a spike"** (G2): persistence/streak/decay features added nothing over the null.
- **"Effort vs result"** (G3): high-volume/low-progress and low-volume/high-progress states did not mark XAU winners or losers.
- **Price vs volume:** where any tiny GC increment appeared (SETUP_3 auction), it came marginally from GC **price**, not volume — and even that
  (+0.016R) is below the gate.

## Honest framing
This is a well-powered null on a specific, pre-registered representation and three specific setups — not a statement that GC volume is
information-free in general. The GC/XAU spot-futures pair is extremely tightly coupled in price (a near-redundant re-encoding), and the earlier
microstructure gate already found the incremental channel is participation, not price; here that participation channel, tested directly against
XAU trade outcomes, does not translate into winner-vs-loser selection value for these mechanisms. Nothing broader is claimed.
