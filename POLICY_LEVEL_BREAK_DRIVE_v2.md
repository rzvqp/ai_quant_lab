# POLICY — Level Break-and-Drive — **v2.0 (Part B completed, screening)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0009.** One frozen, executable structural Part B for identical screening (CEO order). Single
variant, family-native, chosen BEFORE any result; composed from ratified primitives + raw OHLC; no
invention, no lookahead, no optimization. Supersedes v1.0. **Part A unchanged** (see
`POLICY_LEVEL_BREAK_DRIVE_v1.md`). **No new primitive** — v1.0 W10 block stands (`8edbf99`:
`institutional_levels` `c284fa2c…`, `market_state` `823cf66a…`, `interactions` `dafb4804…`).

## PART B — RISK MANAGEMENT — **COMPLETED (screening, single structural variant)**

Family = a daily level broken with displacement. Anchors = the broken level + the displacement.

| Field | Method · reason |
|---|---|
| **stop_loss** | **The broken level** (`PDH` for a long break-up; `PDL` for a short break-down). **Reason:** on a break-and-drive the level flips role (resistance→support); the break is falsified when price returns through the level. Structural (the level itself), not a distance. |
| **exit** | **First opposing-direction expansion bar** (`market_state.expansion`, opposite sign) → exit `open[k+1]`; else **block boundary**. **Reason:** the drive is displacement-led; it ends when an opposing displacement reverses it. |
| **management** | **DECLARED ABSENT** — screening minimalism. |
| **sizing** | **Fixed 1R**, risk-normalized to `entry − stop`; no equity-%. |
| **min_trades** | **Deferred to the Statistician.** |

**Validity guard:** no trade if the entry is already back through the level (stop). All coords known at
entry → no lookahead. **FAIL-CLOSED check:** composable from ratified primitives; method stands.

## Verdict — **DEFINED (SCREENING_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
