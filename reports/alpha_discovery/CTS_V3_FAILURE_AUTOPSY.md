# CTS V3 — Failure autopsy (§26)

Grounded in the frozen walk-forward and the winner-vs-loser event-feature contrasts. No example was used to retune any model.

## The central autopsy finding: winner and loser event-stories are statistically indistinguishable
Across 11,719 breakout-retest trades (5,454 winners / 6,265 losers), **every causal event feature separates winners from losers by |corr| <
0.03** — attack-size progression (+0.007), pullback shrinkage (+0.002), attack participation (+0.010), defensive decay (+0.022), repeated
touches (−0.008), penetration depth (+0.0005), time-near-level (−0.010), adverse structure break (−0.021), favorable structure (+0.016). The
event *grammar* of the winning trades is, to first order, the same as the losing trades. This is why the event n-gram model at 60% retention
(−0.332R) is no better than the setup-relative baseline (−0.281R) and no better than its own order-destroyed (−0.321R) or relation-destroyed
(−0.326R) controls: there is no event motif that reliably marks the winners.

## What each group looked like (profiles, since N is large and stories converge)
- **TRUE_TAKE_WINNERS**: arrive after roughly balanced attack/pullback legs with slightly higher defensive participation and fewer adverse
  structure breaks — but only *slightly*; the same profile also describes many losers.
- **FALSE_TAKE_LOSERS** (the large residual): the model's selected trades that still lost look almost identical to the true takes — same
  ~3-4 attacks / ~3 pullbacks, same size progressions, same touch counts. The event story did not warn of the loss.
- **TRUE_SKIP_LOSERS**: skewed very mildly toward more adverse structure breaks and deeper penetration against the trade — the only weakly
  real signal (adverse_break corr −0.021, in the CEO-hypothesized direction) — but far too weak to build a selector on.
- **FALSE_SKIP_WINNERS**: winners with adverse-looking approaches (adverse breaks, deep penetration) that won anyway — abundant, which is
  exactly why the weak adverse-break signal cannot be pushed harder without discarding many winners.

## What caused false takes / false skips
Both are caused by the same thing: **the causal event sequence before a breakout-retest decision does not encode which instances will win.**
The order of events (destroying it costs nothing), the relations between legs (destroying them costs nothing), and the individual event
descriptors (all |corr| < 0.03) carry essentially no winner-vs-loser information for this setup. The CEO's pressure-attack concept has the
correct sign (adverse attacking pressure → marginally lower R, corr −0.018) but a magnitude far below anything tradeable.

## Interpretation (scope-limited)
For THIS setup and THIS event-relational representation, the winning and losing instances are not separable by event reasoning. This says
nothing about other setups or other representations (§29).
