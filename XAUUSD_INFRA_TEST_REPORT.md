# XAUUSD Infrastructure Test — Report

**Nature of this document**: CEO-authorized 2026-08-03 ("Trimite un ordin ACUM"). **No order was sent.**
The test aborted fail-closed at the dry-run gate, before ever reaching the DEMO leg. Per explicit
instruction — "Daca ceva pica pe drum, opresti si raportezi. Nu repari in graba ca sa treaca." — I
stopped and am reporting, not attempting a fix.

## What happened

`xauusd_infra_test.py` (mirrors `btcusd_phase10_operational_test.py` line for line in structure, per
instruction — same 12 checks, same fail-closed abort pattern, no PDH-PDL recognition rule involved at
all). Checks 1 through 12 (connection, DEMO account, server=`FusionMarkets-Demo`, AlgoTrading, terminal/
account trade-allowed, symbol capabilities, live tick, market open, spread, minimum volume, safety
guards) **all passed**. The identical dry-run — required to pass before the DEMO leg is ever attempted —
was **DENIED**: `RISK_DENIED`, `VOLUME_STEP_ROUNDING_BELOW_MIN`.

Confirmed clean afterward: zero open positions, zero open orders on the XAUUSD symbol.

## Root cause, traced exactly (not guessed)

`ai_trader/risk_manager/sizing.py`: `size_units = risk_budget_currency / (stop_distance * point_value)`.
`ai_trader/risk_manager_live/engine.py`: `volume_lots = floor((size_units / contract_size) / lot_step) *
lot_step`, denied if the result is below `instrument.min_volume`.

With the account/market state actually read at test time:
- `risk_per_trade_pct` (RiskConfig default) = **0.005** (0.5%) → `risk_budget_currency ≈ 0.005 ×
  $10,026.83 ≈ $50.13`.
- `stop_distance` = `entry × 0.02` (the same 2%-of-price convention `btcusd_phase10_operational_test.py`
  used) ≈ `4052.23 × 0.02 ≈ $81.04`.
- `point_value` = `1.0` — copied directly from the BTCUSD script's own value, **not independently
  verified for XAUUSD**.
- `size_units = 50.13 / (81.04 × 1.0) ≈ 0.619`.
- `volume_lots_raw = 0.619 / contract_size(100) ≈ 0.0062` lots → floored to the `0.01` lot step →
  **`0.00` lots** → below `min_volume = 0.01` → denied.

**Why BTCUSD's identical script pattern worked and XAUUSD's does not**: BTCUSD's `contract_size` is
much smaller than XAUUSD's `100` (troy ounces per lot) — dividing by 100 is what pushes the XAUUSD
result below the rounding threshold. This is not a code defect — `VOLUME_STEP_ROUNDING` is working
exactly as designed (Comment in `engine.py`: "never grants more size than was risk-approved"). It is the
formula correctly reporting that, at this account's actual equity ($10,026.83, PLN-denominated demo
account) and the conservative 0.5% risk-per-trade default, a properly risk-sized 2%-stop XAUUSD position
is genuinely smaller than the broker's minimum tradable lot.

**Not fixed, on purpose**: `point_value=1.0` is the same value BTCUSD's own script used, but I did not
verify it is the economically correct value for XAUUSD before running this test — it may be too low (a
correct, larger `point_value` would need a *smaller* raw stop-relative position, making this worse, not
better) or the 2%-of-price stop convention itself may simply not fit a sub-$100-risk-budget account for
an instrument priced near $4,000/oz. I have not diagnosed which, or changed anything, per the explicit
instruction not to repair this in a hurry to force a pass.

## The comparison you asked for — partially available

The **entry-side spread was observed and logged before the abort** (Check 9/10, timestamped, real):

| | Value |
|---|---|
| Bid / Ask at read time | 4052.18 / 4052.23 |
| Observed spread | **$0.05** |
| Modeled round-trip cost (project constant) | $0.20 |
| Ratio (observed spread ÷ modeled) | **0.25** |

The observed spread was one quarter of the modeled round-trip constant — but this is only the
**quoted spread at one moment**, not a realized round-trip cost: no order filled, so there is no
entry/exit slippage, no realized fill price, and no genuine round-trip data point. **This does not
answer the Statistician's question** — it's a single, honest, incomplete data point, not the "first real
data point" the mandate asked for, since nothing was actually executed.

## Status

No order sent. No position opened. Account unchanged. Awaiting your direction — whether to adjust
`point_value`/the risk-per-trade convention for this test (a decision, not something I should invent),
retry with an explicitly larger test position size, or something else.
