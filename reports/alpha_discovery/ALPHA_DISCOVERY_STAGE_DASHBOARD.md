# ALPHA_DISCOVERY_STAGE_DASHBOARD — multi-stage depth (replaces the single coverage number)

CEO mandate 2026-08-23 (§15): a branch is NOT "deeply explored" merely because one formula was backtested. Depth is now tracked in
six stages. The 14-module taxonomy (ALPHA_STRATEGY_MODULE_REGISTRY_V1) remains the classification MAP; this dashboard grades how far
each module has been taken through the pipeline.

## Stages
1. **VISUAL_FORWARD_EXPLORED** — subjected to STRICT candle-by-candle blind-forward replay observation (bfsd_engine.py).
2. **MORPHOLOGIES_IDENTIFIED** — recurring causal morphologies clustered from blind observations (bfsd_score.py).
3. **MECHANIZED** — a recurring, above-baseline morphology preregistered + translated to deterministic rules.
4. **QUANT_TESTED** — subjected to the fast causal quant screen (info-first + tradeable + era-partition). *(The prior campaign.)*
5. **DEEP_VALIDATED** — passed the full quant-falsification gate (DISC/CONF/OOS, costs, STRESS, 2×cost, tail, LOYO, LOEO, effN,
   delay, neighbor, dedup, regime, portfolio independence) + independent validation.
6. **SURVIVORS** — deployed/validated edges.

## Module × stage matrix  (✔ done · ◐ partial · · not yet)
| module | VIS_FWD_EXPL | MORPH_ID | MECHANIZED | QUANT_TESTED | DEEP_VALID | SURVIVOR |
|---|---|---|---|---|---|---|
| M01 trend | ◐ (as H4/H1 context) | ◐ | · | ✔ (4/4) | · | · |
| M02 pullback | ◐ (H1-correction leg) | ◐ | · | ✔ (4/4) | · | · |
| M03 breakout | · | · | ✔ (S5) | ✔ (4/4) | ✔ (S5) | **S5** |
| M04 range | · | · | · | ✔ (4/4) | · | · |
| M05 liquidity | · | · | · | ✔ (3/4+D2) | · | · |
| M06 volatility | · | · | · | ✔ (4/4) | · | · |
| M07 session | · | · | ✔ (S5) | ✔ (4/4) | ✔ (S5) | **S5** |
| M08 auction | ◐ (PDH/PDL zones) | ◐ | · | ✔ (4/4) | · | · |
| M09 cross-scale | ◐ (H4×H1×M15 top-down) | ◐ | · | ✔ (4/4) | · | · |
| M10 transition | · | · | · | ✔ (4/4) | · | · |
| M11 hazard | · | · | · | ✔ (4/4) | · | · |
| M12 event-seq | · | · | · | ✔ (4/4) | · | · |
| M13 imbalance/FVG | ◐ (FVG demand/supply zones) | ◐ | · | ✔ (4/4) | · | · |
| M14 order-block | ◐ (OB demand/supply zones) | ◐ | · | ✔ (4/4) | · | · |

## Stage tallies
- **QUANT_TESTED:** 14/14 modules (56/56 branches) — the prior campaign; now demoted from "coverage" to just this one stage.
- **VISUAL_FORWARD_EXPLORED:** started (BFSD-BATCH-1). Touched M01/M02/M08/M09/M13/M14 via the trend-pullback-to-zone morphology
  (they supply the H4/H1 context, pullback leg, and M15 zones). M03/M04/M05/M06/M07/M10/M11/M12 not yet blind-forward explored —
  they need their own morphology grammars (sweep→reclaim→retest for M05/M12; compression→failed-break→expansion for M06/M03/M10; etc.).
- **MORPHOLOGIES_IDENTIFIED:** (a) predefined SMC family (n=599) ≈ baseline (retained as one negative test). (b) BFSD3 open-ended
  top-down reading surfaced ONE emergent regime-specialist CANDIDATE: `BULLISH|weak_up|normal|long|DISCOUNT|ASIA` P2R=0.562 (n=32,
  under-powered) — accumulate to n>=50-100 before verdict. Readiness score found anti-calibrated (recalibrate from outcomes).
- **MECHANIZED:** S5 only (pre-existing).  **DEEP_VALIDATED:** S5 only.  **SURVIVORS:** S5 only.

## Honest status
The single "100% coverage" claim is retired. Correct reading: **the QUANT_TESTED stage is complete; the VISUAL_FORWARD_EXPLORED and
MORPHOLOGIES_IDENTIFIED stages have just begun** and are the current work.

**CEO correction (2026-08-24):** BFSD-BATCH-1 (predefined SMC trend-pullback-zone) was **one negative hypothesis test only** — it is
NOT open-ended discovery and does NOT support "no morphology qualifies" or "campaign confirmed." The real campaign is engine v2:
canonical N1–N3 state (verified present, see N1_N6_PRESENCE_REPORT.md) + primitive-agnostic structural symbols, morphology EMERGES
from observed recurring sequences, outcomes conditioned by N1 regime (**regime specialists valid; era-stability NOT required**). S5
remains the only *validated* edge; that is a statement about validation to date, not a claim that morphology discovery is exhausted.
