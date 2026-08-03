# POLICY — OB Sweep-Rejection × FVG-CE50 Confluence — **v2.0 (Part B completed, screening)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0015.** One frozen, executable structural Part B for identical screening (CEO order). Single
variant, family-native, chosen BEFORE any result; composed from ratified primitives; no invention, no
lookahead, no optimization. Supersedes v1.0. **Part A unchanged** (see
`POLICY_OBREJ_FVG_CONFLUENCE_v1.md`). **No new primitive** — v1.0 W10 block stands (`8edbf99`:
`order_flow` `728fa557…`, `imbalance_mechanics` `45f8937e…`, `interactions` `dafb4804…`).

## PART B — RISK MANAGEMENT — **COMPLETED (screening, single structural variant)**

Family = two-imbalance confluence (no daily level → the risk uses the two imbalance zones).

| Field | Method · reason |
|---|---|
| **stop_loss** | **Below BOTH structures — the deeper floor:** long → `min(Low_OB, FVG.lower)`; short → `max(High_OB, FVG.upper)`. **Reason:** the confluence holds until both the OB breaker floor and the FVG far edge are broken. |
| **exit** | **The far side of the combined zone in the reaction direction:** long → `max(OB.zone_upper, FVG.upper)`; short → `min(OB.zone_lower, FVG.lower)`; else **block boundary**. **Reason:** no level here — a respected confluence reacts back out of both imbalance zones. |
| **management** | **DECLARED ABSENT** — screening minimalism. |
| **sizing** | **Fixed 1R**, risk-normalized; no equity-%. |
| **min_trades** | **Deferred to the Statistician.** |

**Validity guard:** no trade if entry is already beyond the combined stop or the combined target. Coords
known at entry → no lookahead. **FAIL-CLOSED check:** composable (min/max of ratified zone edges); method
stands.

## Verdict — **DEFINED (SCREENING_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
