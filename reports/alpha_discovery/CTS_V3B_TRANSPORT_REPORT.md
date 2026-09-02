# CTS V3B — event-relational architecture TRANSPORT test

Transport / generalization test: the EXACT frozen CTS V3 event-relational architecture (verbatim parser, theta=2.5, window=48, event grammar,
relation graph, event n-gram model, walk-forward, controls, thresholds) applied UNCHANGED to the other two CTS V2 setups. No redesign, no theta
recalibration, no model change, no threshold change, no per-setup tuning. Frozen identities verified: `V3_EVENT_GRAMMAR_HASH_VERIFIED = YES`
(5d4dceb6…), `V3_PROTOCOL_HASH_VERIFIED = YES` (63ad1c95…). INTERNAL_GENERALIZATION only. Protections intact; no V3 artifact overwritten.

## Parser transported cleanly (frozen theta=2.5, diagnostics only — not recalibrated)
| setup | mechanism | mean legs | median | % 3–10 legs | % single-leg |
|---|---|---|---|---|---|
| SETUP_1 | liquidity-sweep | 5.69 | 4 | 71.4% | 2.4% |
| SETUP_3 | auction-value | 6.66 | 5 | 71.1% | 1.3% |

The frozen directional-change parser produces the same meaningful attack/pullback granularity on both new mechanisms (no degeneracy) — so the
architecture applies mechanically; there is no `TRANSPORT_IMPLEMENTATION_BLOCKED`.

## Result — the architecture does NOT transport (0/3 on every axis)
Retention frontier @60% winner-retention (pooled chronological TEST). On BOTH new setups, as on S3, the event-relational representation (C) is
**worse than the CTS_V2 setup-relative baseline (A)** and no better than event aggregates (B); all 0/3 folds positive.

| setup | A (baseline) | B (event agg) | C (event-relational) | C−A | ERIV | RSIV | OIV | practical |
|---|---|---|---|---|---|---|---|---|
| SETUP_1 sweep | **−0.311** | −0.350 | −0.318 | −0.007 | NO | NO | NO | NO |
| SETUP_3 auction | **−0.084** | −0.146 | −0.140 | −0.057 | NO | NO | NO | NO |
| S3 breakout-retest (V3) | **−0.281** | −0.330 | −0.332 | −0.051 | NO | NO | NO | NO |

**Controls (both setups):** destroying event ORDER changes C by ≤+0.008R (real slightly worse) → order carries no value; destroying RELATIONS
changes C by ≤+0.009R → relations carry no value. C beats matched-random-N (a weak generic lose-less signal) but the event structure adds nothing
over it. Every individual event feature separates winners from losers by |corr|<0.037 (largest across both: auction penetration +0.0364; sweep
max 0.0145) — winner/loser event-stories are again statistically indistinguishable. `CEO_PRESSURE_ATTACK_CONCEPT = NOT_SUPPORTED` for both.

## §16 market-reasoning (both setups): every event effect negligible
Adverse attack pressure, shrinking pullbacks, attack-participation progression, defensive-participation decay, repeated touches, reaction
decay, time-near-reference, adverse structure break-and-hold, favorable-structure failure, and relational combinations — none reaches the 0.03
informative threshold on the sweep setup; only auction *penetration depth* (+0.036) barely clears it, and it does not yield a positive selector.
Relational combinations do not outperform individual events (the n-gram model does not beat the aggregates or the geometry baseline).

## §23 FINAL OUTPUT
```
CTS_V3B_TRANSPORT_COMPLETE = YES
V3_EVENT_GRAMMAR_HASH_VERIFIED = YES · V3_PROTOCOL_HASH_VERIFIED = YES
SETUPS_TESTED = 2

SETUP_A_ID = SETUP_1 · SETUP_A_MECHANISM = M01_LIQUIDITY_SWEEP · SETUP_A_TRADES = 13538
SETUP_A_EVENT_RELATIONAL_INCREMENTAL_VALUE = NO
SETUP_A_RELATION_STRUCTURE_INCREMENTAL_VALUE = NO
SETUP_A_EVENT_ORDER_INCREMENTAL_VALUE = NO
SETUP_A_PRACTICALLY_USEFUL_EVENT_SELECTION = NO
SETUP_A_BASE_EXPECTANCY = -0.3143R · SETUP_A_EVENT_RELATIONAL_EXPECTANCY_60 = -0.3179R · SETUP_A_STRESS_EXPECTANCY_60 = -0.9996R
SETUP_A_WINNERS_RETAINED_60 = 50.8% · SETUP_A_LOSERS_AVOIDED_60 = 49.6%

SETUP_B_ID = SETUP_3 · SETUP_B_MECHANISM = M16_AUCTION_VALUE · SETUP_B_TRADES = 25008
SETUP_B_EVENT_RELATIONAL_INCREMENTAL_VALUE = NO
SETUP_B_RELATION_STRUCTURE_INCREMENTAL_VALUE = NO
SETUP_B_EVENT_ORDER_INCREMENTAL_VALUE = NO
SETUP_B_PRACTICALLY_USEFUL_EVENT_SELECTION = NO
SETUP_B_BASE_EXPECTANCY = -0.1757R · SETUP_B_EVENT_RELATIONAL_EXPECTANCY_60 = -0.1403R · SETUP_B_STRESS_EXPECTANCY_60 = -0.4196R
SETUP_B_WINNERS_RETAINED_60 = 54.3% · SETUP_B_LOSERS_AVOIDED_60 = 51.8%

CEO_PRESSURE_ATTACK_SETUP_A = NOT_SUPPORTED · CEO_PRESSURE_ATTACK_SETUP_B = NOT_SUPPORTED

EVENT_RELATIONAL_SUCCESS_COUNT = 0 / 3
RELATION_INCREMENTAL_COUNT = 0 / 3
ORDER_INCREMENTAL_COUNT = 0 / 3
PRACTICAL_EVENT_EDGE_COUNT = 0 / 3

FINAL_ARCHITECTURE_CLASSIFICATION = EVENT_RELATIONAL_ARCHITECTURE_NOT_SUPPORTED_ON_CTS3
BROADER_CONTEXT_EXHAUSTION_CLAIM_AUTHORIZED = NO
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

## Authorized scope of conclusion (§20)
The frozen CTS V3 event-relational architecture did not show incremental value across the three frozen CTS setups (liquidity-sweep,
breakout-retest, auction-value): 0/3 event-relational value, 0/3 relation value, 0/3 order value, 0/3 practical edge; on every setup the
setup-relative geometry baseline is the strongest representation. Nothing broader is claimed — this says nothing about price action, other
mechanisms, other representations, other markets, or whether external data is required.
```
CTS_V3B = COMPLETE — event-relational architecture NOT_SUPPORTED across the 3 CTS setups; setup-relative geometry remains the best (still lose-less)
```
