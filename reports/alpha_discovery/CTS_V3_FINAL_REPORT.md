# CONTEXTUAL TRADE SELECTION V3 — event-relational market reasoning (one setup)

The exact CEO question — *can AI distinguish winning from losing instances of the same setup by understanding the causal market EVENTS and
RELATIONSHIPS that occurred before the trade?* — was tested with a genuine event-relational pipeline (deterministic causal event parser →
attack/pullback legs → inter-leg relationships → structural attack/defense relative to trade direction → reference weakening → ordered event
sequence + relation graph → an order- and relation-sensitive event n-gram model). No proxy substitution; no raw-bar nearest-centroid used for
representation C. INTERNAL_GENERALIZATION only (history materially exposed). One setup; no auto-scale; protections intact.

## Answer: on this setup, NO — event/relationship reasoning did not beat setup-relative geometry
- `EVENT_RELATIONAL_INCREMENTAL_VALUE = NO`. At 60% winner-retention the event-relational model (C, −0.332R) is **worse** than the CTS_V2
  setup-relative baseline (A, −0.281R) by −0.051R (all 3 folds negative), and no better than event aggregates (B, −0.330R). The mandate's bar
  (≥+0.08R over A, ≥+0.05R in 2/3 folds, and beat B) is missed on every count.
- `RELATION_STRUCTURE_INCREMENTAL_VALUE = NO`. Destroying the relations between events changes C by only +0.006R (real −0.332 vs
  relation-destroyed −0.326) — relations carry no information here. Destroying event ORDER likewise costs nothing (−0.332 vs −0.321).
- Every individual causal event feature separates winners from losers by **|corr| < 0.03** (largest: defensive decay +0.022, adverse
  structure break −0.021). Winner and loser event-stories are statistically indistinguishable (see autopsy).
- `PRACTICALLY_USEFUL_EVENT_SELECTION = NO` — 0 retention points reach +0.10R base at ≥60% winner-retention.
- `NEGATIVE_CONTROL_GATE = PASS` in the narrow sense that C beats matched-random-N (a weak, generic lose-less signal exists) but it does **not**
  clear the label-permutation 95th percentile, and it is the *same* lose-less signal the simpler representations already capture.

## Representation frontier @60% winner-retention (pooled chronological TEST)
| representation | selected exp | losers avoided | folds positive |
|---|---|---|---|
| A — CTS_V2 setup-relative + generic | **−0.281R** | 34% | 0/3 |
| B — event aggregates | −0.330R | 43% | 0/3 |
| C — event-relational sequence (n-gram) | −0.332R | 47% | 0/3 |
(base setup expectancy −0.374R; the STRESS column is strongly negative, −1.8R, because this breakout-retest runs tight structural stops that are cost-sensitive.)

## §27 CEO pressure-attack concept
`CEO_PRESSURE_ATTACK_CONCEPT = NOT_SUPPORTED`. The composite "adverse attacking pressure into the setup (adverse breaks + shrinking pullbacks +
rising attack participation + closes-through)" correlates with net_R at **−0.018** — the *sign* is exactly as the CEO hypothesized (more adverse
pressure → weaker setup), but the magnitude is negligible and well below any usable threshold.

## §28 market-reasoning answers (all from event contrasts, not marginal correlation alone — but every effect is negligible)
1. Increasing attack pressure → failure? **NO** (+0.007). 2. Shrinking pullbacks → failure? **NO** (+0.002). 3. Increasing attack
participation → failure? **NO** (+0.010). 4. Declining defensive participation → failure? **NO** (defense decay +0.022, sub-threshold).
5. Repeated touches weaken? **NO** (−0.008). 6. Reaction-magnitude decay → failure? **NO** (~0). 7. Time near level matters? **NO** (−0.010).
8. Adverse break-and-hold matters? **weakly, right sign** (−0.021) but sub-threshold → NO. 9. Failure to produce opposite structure? **NO**
(+0.016). 10. Do combinations matter more than individuals? **NO** — the n-gram model that captures event combinations/order did not beat the
per-feature aggregates or the geometry baseline.

## §33 FINAL OUTPUT
```
CONTEXTUAL_TRADE_SELECTION_V3_COMPLETE = YES
V3_PREFLIGHT_END_TO_END = PASS
SETUP_ID = SETUP_2 (S3 :: M03_BREAKOUT_RETEST, rep 7aafa506c507, BOTH)
SETUP_FREEZE_HASH = 819a986c02002893fc0e · EVENT_GRAMMAR_HASH = 5d4dceb6c65f0bfb3eec · PROTOCOL_HASH = 63ad1c95de95703ee2a3
TOTAL_TRADES = 11719 · WINNERS = 5454 · LOSERS = 6265
BASE_SETUP_EXPECTANCY = -0.3736R
CTS_V2_BASELINE_EXPECTANCY_AT_60_RETENTION = -0.281R
EVENT_AGGREGATE_EXPECTANCY_AT_60 = -0.330R
EVENT_RELATIONAL_EXPECTANCY_AT_60 = -0.332R · EVENT_RELATIONAL_STRESS_EXPECTANCY_AT_60 = -1.821R
EVENT_RELATIONAL_INCREMENTAL_VALUE = NO
RELATION_STRUCTURE_INCREMENTAL_VALUE = NO
WINNERS_RETAINED_AT_PRIMARY_POINT = 55% · LOSERS_AVOIDED_AT_PRIMARY_POINT = 47%
ATTACK_PRESSURE_INFORMATION = NO · PULLBACK_SHRINKAGE_INFORMATION = NO · ATTACK_PARTICIPATION_INFORMATION = NO
DEFENSE_DECAY_INFORMATION = NO · REPEATED_TOUCH_INFORMATION = NO · STRUCTURAL_ATTACK_INFORMATION = NO (weak right-sign, sub-threshold) · ACCEPTANCE_INFORMATION = NO
CEO_PRESSURE_ATTACK_CONCEPT = NOT_SUPPORTED (correct sign, negligible magnitude -0.018)
NEGATIVE_CONTROL_GATE = PASS (beats matched-random-N; does not clear label-perm 95th pct)
HUMAN_COHERENT_EVENT_REASONING_FOUND = NO (winner/loser event-stories statistically indistinguishable)
NEW_NONOBVIOUS_EVENT_RELATION_FOUND = NO
PRACTICALLY_USEFUL_EVENT_SELECTION = NO
EFFECTIVE_SELECTED_TRADES_PER_YEAR = ~330 (but negative) · TIME_TO_50_FUTURE_INDEPENDENT = ~2 months (nothing positive to validate)
READY_FOR_PROSPECTIVE_FREEZE = NO
BROADER_CONTEXT_EXHAUSTION_CLAIM_AUTHORIZED = NO
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

## Authorized scope of conclusion (§29)
On THIS one frozen setup (breakout-retest), THIS event-relational representation did not distinguish winners from losers, did not beat the
setup-relative geometry baseline, and event order/relations added nothing. The winning and losing instances arrive via statistically
indistinguishable causal event sequences. No broader claim — that price action, all contextual reasoning, all trader reasoning is exhausted,
that AI cannot outperform humans, or that external information is required — is made or supported by this single-setup experiment.
```
CTS_V3 = COMPLETE — event-relational reasoning did NOT beat setup-relative geometry on the breakout-retest setup; winner/loser event-stories indistinguishable
```
