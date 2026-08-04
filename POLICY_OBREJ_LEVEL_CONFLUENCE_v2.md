# POLICY — OB Sweep-Rejection × PDH/PDL Confluence — **v2.0 (Part B completed, screening)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0012.** One frozen, executable structural Part B for identical screening (CEO order). Single
variant, family-native, chosen BEFORE any result; composed from ratified primitives + raw OHLC; no
invention, no lookahead, no optimization. Supersedes v1.0. **Part A unchanged** (see
`POLICY_OBREJ_LEVEL_CONFLUENCE_v1.md`). **No new primitive** — v1.0 W10 block stands (`8edbf99`:
`order_flow` `728fa557…`, `institutional_levels` `c284fa2c…`, `interactions` `dafb4804…`).

## PART B — RISK MANAGEMENT — **COMPLETED (screening, single structural variant)**

Family = two-structure confluence containing a daily level.

| Field | Method · reason |
|---|---|
| **stop_loss** | **Below BOTH structures — the deeper floor:** long → `min(Low_OB, low[touch_idx])`; short → `max(High_OB, high[touch_idx])`. **Reason:** a confluence is not falsified until the aligned zone is comprehensively broken (both the OB breaker floor and the level-test bar). |
| **exit** | **The opposite prior-day level** (range reversion, applicable because a level is present): PDL-long → `PDH`; PDH-short → `PDL`; else same-day **time-stop** (`day_index` boundary). |
| **management** | **DECLARED ABSENT** — screening minimalism. |
| **sizing** | **Fixed 1R**, risk-normalized; no equity-%. |
| **min_trades** | **Deferred to the Statistician.** |

**Validity guard:** no trade if entry is already beyond the combined stop or the opposite level. Coords
known at entry → no lookahead. **FAIL-CLOSED check:** composable (min/max of ratified floors + an
already-produced level); method stands.

## Verdict — **DEFINED (SCREENING_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
