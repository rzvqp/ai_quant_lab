# POLICY — Demand/Supply-Zone Re-entry Reaction — **v2.0 (Part B completed, screening)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0013.** One frozen, executable structural Part B for identical screening (CEO order). Single
variant, family-native, chosen BEFORE any result; composed from ratified primitives; no invention, no
lookahead, no optimization. Supersedes v1.0. **Part A unchanged** (see `POLICY_DEMAND_ZONE_v1.md`).
**No new primitive** — v1.0 W10 block stands (`8edbf99`: `order_flow` `728fa557…`, `interactions`
`dafb4804…`).

## PART B — RISK MANAGEMENT — **COMPLETED (screening, single structural variant)**

Family = non-consumable full-bar zone reaction. Anchors = the zone's own edges (`zone_lower`=Low,
`zone_upper`=High of the anchor bar).

| Field | Method · reason |
|---|---|
| **stop_loss** | **The zone's FAR edge:** bullish demand → `zone_lower`; bearish supply → `zone_upper`. **Reason:** the zone-hold thesis fails when price trades through the far edge of the zone. Structural (the zone's own boundary). |
| **exit** | **The zone's NEAR edge in the reaction direction:** bullish → `zone_upper`; bearish → `zone_lower`; else **block boundary**. **Reason:** a respected zone reacts back out of itself. |
| **management** | **DECLARED ABSENT** — screening minimalism. |
| **sizing** | **Fixed 1R**, risk-normalized; no equity-%. |
| **min_trades** | **Deferred to the Statistician.** |

**Validity guard:** no trade if entry is already beyond the far edge (stop) or near edge (target). Coords
known at entry → no lookahead. **FAIL-CLOSED check:** composable from ratified `DemandZone` edges; method
stands.

## Verdict — **DEFINED (SCREENING_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
