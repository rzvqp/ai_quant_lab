# ATTRIBUTION_V2_COVERAGE_REPORT — universe, identity, regeneration coverage (EXECUTED)

Alpha independent execution of STRATEGY_OUTCOME_ATTRIBUTION_EDGE_RESCUE_V2 against the Statistician-frozen package. Blocker resolved: the
blinded feature-VALUE matrix was supplied and hashed. No object omitted; FAILED_REGENERATION kept in all denominators.

## §1 Identity — 7/7 hashes exact (independently recomputed)
```
MANIFEST_HASH             = 433f1cec…   ✓  EXECUTION_UNIVERSE_HASH = 78ea539f…   ✓  PROTOCOL_CORE_HASH = 4488f0e8…  ✓
BLINDED_FEATURE_VALUES    = 2ea066c6…   ✓  HANDOFF_MANIFEST        = edf196e5…   ✓  TRADE_LEVEL_SPEC   = 03e63663…  ✓
STAGE1_ELIGIBLE_FEATURES  = 8a629d7d…   ✓  →  IDENTITY_VERIFIED = YES
```

## §2 Coverage of all 115 analysis objects (denominators frozen: families 102, objects 115, mechanisms 25)
```
TIER                          objects   regeneration outcome (this cycle)
T1_LOG_EXISTS                    14     ANALYSED — Alpha V1 causal ledger (HTF×4, OBEXEC×4, SESS×6)
T1_REGENERATE_SLIB               56     ANALYSED — mstrat.REGISTRY(20)+mstrat_ext.EXT_REGISTRY(25) grammars; 56 eligible reps simulated
T2_REGENERATE_EDGERESEARCH       25     FAILED_REGENERATION — bespoke edge_research generators, not regenerable this cycle
T2_REGENERATE_FACTORY            14     FAILED_REGENERATION — alpha_discovery factory generators, not regenerable this cycle
T2_REGENERATE_FROZEN_SPEC         6     FAILED_REGENERATION — frozen-spec generators, not regenerable this cycle
------------------------------------------------------------------------------------------------
ANALYSED = 70   FAILED_REGENERATION = 45   TOTAL = 115   (45 failures retained in every rescue-rate denominator)
```

## Trade join (causal integrity)
- Blinded panel (355,696 rows, frozen bin indices f001..f046) verified **index-aligned** with `mstrat.load()` — `BAR_OPEN_TIME == d.time`
  elementwise. **`INDEX_ALIGNED = YES`**.
- Join rule (frozen HANDOFF_MANIFEST `edf196e5`): each trade joined on its **DECISION bar** — S-library on the signal bar `si`; T1 on
  `entry_bar − 1`; **never the entry bar**. f029 (needs the next-bar fill) excluded upstream from eligibility.
- **505,794 trades joined across 70 objects, 0 unmatched.** `TOTAL_VALID_TRADES_ANALYSED = 505794`.

## What was tested
45 Stage-1-eligible features (f029 excluded per CEO ruling, AT_FILL_POST_DECISION) × 70 objects, restricted to frozen bins with N≥30 and
≥20 independent days → **2,887 (object,feature) omnibus tests**, BH-FDR at the declared multiplicity **m=5,175**. Blind results frozen +
hashed (`8988448a…`) before unblinding. Placebo hard gate PASS.

## Blinding discipline
`BLINDING_DISCIPLINE_PRESERVED = YES` — the value matrix carries only blind ids; primary scoring used blind f-ids exclusively; the
name→id map (`feature_map_SECRET.csv`) was opened **only after** the blind results were frozen and hashed, per §22. No threshold scanning was
possible (values are frozen bin indices). See `ATTRIBUTION_V2_UNBLINDED_FEATURE_REPORT.md` for the post-freeze semantic mapping.
```
COVERAGE_STATUS = COMPLETE — 70 ANALYSED / 45 FAILED_REGENERATION / 115 TOTAL; 505,794 trades; identity + placebo + blinding all PASS
```
