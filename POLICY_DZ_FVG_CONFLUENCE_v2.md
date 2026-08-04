> **SUPERSEDED by POLICY_DZ_FVG_CONFLUENCE_v3.md** — the v2 exit's third term was a discovery-only 'block boundary' that never fires on a live forward account. Kept for the record; do not use.

# POLICY — Demand-Zone Re-entry × FVG-CE50 Confluence — **v2.0 (Part B completed, screening)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0017.** One frozen, executable structural Part B for identical screening (CEO order). Single
variant, family-native, chosen BEFORE any result; composed from ratified primitives; no invention, no
lookahead, no optimization. Supersedes v1.0. **Part A unchanged** (see `POLICY_DZ_FVG_CONFLUENCE_v1.md`).
**No new primitive** — v1.0 W10 block stands (`8edbf99`: `order_flow` `728fa557…`, `imbalance_mechanics`
`45f8937e…`, `interactions` `dafb4804…`).

## PART B — RISK MANAGEMENT — **COMPLETED (screening, single structural variant)**

Family = two-zone confluence (demand zone × FVG; no daily level → the two zones supply the risk).

| Field | Method · reason |
|---|---|
| **stop_loss** | **Below BOTH — the deeper floor:** long → `min(DemandZone.zone_lower, FVG.lower)`; short → `max(DemandZone.zone_upper, FVG.upper)`. **Reason:** the confluence holds until both zones' far edges are broken. |
| **exit** | **The far side of the combined zone in the reaction direction:** long → `max(DemandZone.zone_upper, FVG.upper)`; short → `min(DemandZone.zone_lower, FVG.lower)`; else **block boundary**. |
| **management** | **DECLARED ABSENT** — screening minimalism. |
| **sizing** | **Fixed 1R**, risk-normalized; no equity-%. |
| **min_trades** | **Deferred to the Statistician.** |

**Validity guard:** no trade if entry is already beyond the combined stop or target. Coords known at entry
→ no lookahead. **FAIL-CLOSED check:** composable (min/max of ratified zone edges); method stands.

## Verdict — **DEFINED (SCREENING_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
