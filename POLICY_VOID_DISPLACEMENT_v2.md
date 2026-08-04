# POLICY — Gap-and-Go: Displacement out of a Liquidity Void — **v2.0 (Part B completed, screening)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0008.** One frozen, executable structural Part B for identical screening (CEO order). Single
variant, family-native, chosen BEFORE any result; composed from ratified primitives + raw OHLC; no
invention, no lookahead, no optimization. Supersedes v1.0. **Part A unchanged** (see
`POLICY_VOID_DISPLACEMENT_v1.md`). **No new primitive** — v1.0 W10 block stands (`8edbf99`:
`code/market_state.py` `823cf66a…`, `code/order_block_void.py` `6ec7adbf…`).

## PART B — RISK MANAGEMENT — **COMPLETED (screening, single structural variant)**

Family = displacement (a gap immediately driven). Anchors = the displacement bar `i`.

| Field | Method · reason |
|---|---|
| **stop_loss** | **Opposite extreme of the displacement bar `i`**: long → `low[i]`; short → `high[i]`. **Reason:** the gap-and-go thesis fails when price returns through the displacement bar. Event-anchored, not a distance. (Raw OHLC at the ratified expansion index.) |
| **exit** | **First opposing-direction expansion bar** (`market_state.expansion` with opposite `sign(close-open)`) → exit `open[k+1]`; else **block boundary** time-stop. **Reason:** a driven gap runs until an opposing displacement reverses it — the entry family's own primitive. |
| **management** | **DECLARED ABSENT** (no partials/breakeven/trailing) — screening minimalism. |
| **sizing** | **Fixed 1R**, risk-normalized to `entry − stop`; no equity-%. |
| **min_trades** | **Deferred to the Statistician.** |

**Validity guard:** no trade if `open[i+1]` is already beyond the stop. All coords known at entry → no
lookahead. **FAIL-CLOSED check:** composable from ratified primitives; method stands.

## Verdict — **DEFINED (SCREENING_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
