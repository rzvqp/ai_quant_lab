# N1–N6 PRESENCE REPORT (CEO-required verification, 2026-08-24)

Explicit verification of whether canonical N1–N6 outputs are present/computable in the blind-forward replay state. **No
approximation, no silent omission** — verified by reading the ratified code and executing each node causally (`n_probe.py`).

| Node | What | Module (wp5b/code) | Present? | Computable in replay? | Evidence |
|---|---|---|---|---|---|
| **N1** | Regime (H4) | `regime_classifier.classify_regime` | **YES** | **YES — full history** | probe: `Ok(RegimeState)` with vol/structure/direction axes at as_of 50k/150k/300k |
| **N2** | Bias (H1) | `bias_h1.compute_bias` | **YES** | **YES — full history** | probe: `Ok(BiasState)` `structure_run_h1` FactorDirection LONG/SHORT + raw magnitude |
| **N3** | Zone map (M15) | `zone_map.build_zone_map` | **YES** | **YES — full history** (cascades: needs N1&N2 available) | probe: `Ok(ZoneMap)` n_zones = 7 / 35 / 30 |
| **N4** | Confirmation (M5) | `zone_confirmation.classify_zone_confirmation` | **CODE YES / DATA-LIMITED** | **ONLY 2021-07-27 → 2026-07-27** | native M5 = `data/market/OANDA_XAUUSD_M5.csv`, that window only; pre-2021 episodes → N4 **NOT COMPUTABLE** |
| **N5** | — | — | **DOES NOT EXIST** | n/a | grep across all wp5b/code `*.py`: no N5 node/def/reference anywhere |
| **N6** | Decision/EV gate | `market_bus.decide` (minimal, conservative) + `RealEVDecisionEngine`/`ve_brain` (full, this branch) | **YES** | YES (as a DECISION, not a market-reading node) | market_bus header: "poarta N6 minimală"; full EV engine on alpha-automation-v1 |

## Honest disclosures
- **N1/N2/N3 are the canonical causal top-down state** and will be recorded in every replay observation (H4 regime → H1 bias →
  M15 zones), matching the CEO's required top-down order. They are ratified, pure, causal (internal cut asserts, cascade fail-closed).
- **N4 is confined to the native-M5 window (2021-07-27+).** For blind episodes before 2021-07 there is NO M5 data, so N4 = absent by
  data, not by omission. When an episode lies inside the M5 window, N4 will be computed and recorded; otherwise it is explicitly
  marked `N4=UNAVAILABLE(no_M5)`.
- **N5 does not exist** in this codebase — the canonical set is N1–N4 + the N6 gate. Reported as nonexistent, not silently skipped.
- **N6 is a decision, not a reading** — used only at the mechanize/validation stage (§12/§13), never as a discovery input.

## Consequence for the discovery engine
The blind-forward engine is being rebuilt (v2) to record the **canonical N1/N2/N3 state** at each candle (N4 where M5 exists) as the
causal market-reading, PLUS primitive-agnostic structural descriptors — with NO predefined setup — and to let morphologies EMERGE
(§ CEO correction). N1 regime is the primary conditioning variable for regime specialists (era-stability NOT required).
