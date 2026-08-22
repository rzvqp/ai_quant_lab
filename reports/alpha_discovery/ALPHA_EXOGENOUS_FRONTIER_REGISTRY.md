# ALPHA_EXOGENOUS_FRONTIER_REGISTRY

Mandate `ALPHA-XAUUSD-EXOGENOUS-CONTINUOUS-LOOP-001`. Economic exogenous frontiers (mechanism-first, §7). ALL currently `BLOCKED_NO_DATA` — no authorized exogenous dataset exists (see `ALPHA_EXOGENOUS_EVIDENCE_MAP.md`). Frozen frontier definitions ready to run the instant ratified data is provisioned.

| FRONTIER_ID | economic question | required data | status |
|---|---|---|---|
| X1-USD-IMPULSE | does a causal DXY move create an asymmetric subsequent XAUUSD path (USD-strength->gold-weakness / USD-weakness->gold-strength, L/S separate)? | DXY intraday | **BLOCKED_NO_DATA** (DXY_DATA_NOT_AVAILABLE) |
| X2-REALYIELD | does a causal real-yield (DFII10) impulse alter forward gold path probability? | TIPS real yield daily | **BLOCKED_NO_DATA** |
| X3-USD+YIELD-AGREE | does simultaneous USD+yield pressure give cleaner gold direction than either alone (incremental over each)? | DXY + UST yields | **BLOCKED_NO_DATA** |
| X4-CROSS-DIVERGENCE | does XAUUSD diverging from its usual USD/yield relationship predict convergence vs continuation? | DXY + yields | **BLOCKED_NO_DATA** |
| X5-MACRO-POSTEVENT | after a major scheduled release, does gold response + external confirmation + acceptance give a robust second-leg? | ratified historical release timestamps + vintage values covering b0/b1 | **BLOCKED_NO_DATA** (only 2026 quarantined calendar/news exists) |
| X6-POSITIONING-REGIME | does positioning (COT) identify regimes where a price-only mechanism becomes materially more reliable (incremental)? | CFTC COT with release timestamps | **BLOCKED_NO_DATA** |

**No hypotheses tested (0)** — the mechanism-first screens (§10) cannot run without data. When data is provisioned, each frontier is bounded to ~10-20 hypotheses / <=6 variants (§22), price-structure owns invalidation (§16), incremental-over-price-only required (§11), overlap-vs-frozen required for any survivor (§23).
