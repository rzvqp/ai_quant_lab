> **SUPERSEDED by POLICY_OB_MITIGATION_v3.md** — the v2 exit's third term was a discovery-only 'block boundary' that never fires on a live forward account. Kept for the record; do not use.

# POLICY — Order-Block Mitigation Reaction — **v2.0 (Part B completed, screening)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0014.** One frozen, executable structural Part B for identical screening (CEO order). Single
variant, family-native, chosen BEFORE any result; composed from ratified primitives + raw OHLC; no
invention, no lookahead, no optimization. Supersedes v1.0. **Part A unchanged** (see
`POLICY_OB_MITIGATION_v1.md`). **No new primitive** — v1.0 W10 block stands (`8edbf99`: `order_flow`
`728fa557…`).

## PART B — RISK MANAGEMENT — **COMPLETED (screening, single structural variant)**

Family = order-block reaction (same anchors as CAND-0011; the mitigation is a different reaction *type*,
so the risk uses the OB's own ratified levels).

| Field | Method · reason |
|---|---|
| **stop_loss** | **The OB whole-bar floor `Low_OB = low[formation_idx]`** (bullish) / `High_OB` (bearish). **Reason:** the mitigation-reaction fails when the OB **breaks** (close beyond `Low_OB`/`High_OB` = ratified `track_breaker`). |
| **exit** | **The OB body far edge in the reaction direction:** bullish → `zone_upper`; bearish → `zone_lower`; else **block boundary**. **Reason:** a respected OB reacts back out of its body zone. |
| **management** | **DECLARED ABSENT** — screening minimalism. |
| **sizing** | **Fixed 1R**, risk-normalized; no equity-%. |
| **min_trades** | **Deferred to the Statistician.** |

**Validity guard:** no trade if `next-open` is already beyond `Low_OB`/`High_OB` (stop) or the body far
edge (target). Coords known at entry → no lookahead. **FAIL-CLOSED check:** composable from ratified
primitives; method stands.

## Verdict — **DEFINED (SCREENING_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
