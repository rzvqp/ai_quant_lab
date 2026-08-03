# XAUUSD Infrastructure Test — Report (Attempt 2: point_value corrected)

**Nature of this document**: follow-up to the first attempt (dry-run denied on `VOLUME_STEP_ROUNDING_BELOW_MIN`
due to an unverified `point_value=1.0` copied from the BTCUSD script). CEO instruction, 2026-08-03:
correct `point_value` from real `symbol_info`, don't assume, don't touch risk% or stop distance. **No
order was sent on this attempt either — for a different, precisely quantified reason, not a
configuration bug.**

## 1. Real values read from `symbol_info` (not assumed, not copied)

| Field | Source | Value |
|---|---|---|
| `trade_contract_size` | `symbol_info(XAUUSD)` | **100.0** (troy ounces / lot) |
| `trade_tick_value` | `symbol_info(XAUUSD)` | **3.74601** (account currency — PLN — per lot per tick) |
| `trade_tick_size` | `symbol_info(XAUUSD)` | **0.01** |

## 2. `point_value` corrected — two distinct fields, traced to their actual consumers

Confirmed by reading every consumer (`grep`, not assumed):

- **`RiskConfig.sizing.point_value[symbol]`** — the ONE that feeds `risk_manager/sizing.py`'s actual
  sizing formula (`config.point_value_for(symbol)` → `self.sizing.point_value.get(symbol, 1.0)`).
  `risk_manager_live/engine.py`'s own comment documents that `compute_sizing`'s `size_units` output is
  "base units (e.g. troy ounces)" — meaning this `point_value` must be **per UNIT (ounce)**, not per lot:
  `tick_value / tick_size / contract_size = 3.74601 / 0.01 / 100 = 3.74601`.
- **`InstrumentSpecification.point_value`** — a SEPARATE field, used ONLY for a `> 0` sanity check
  (`risk_manager_live/engine.py:112`), never in the sizing math itself. Set to match the already-
  established convention `mt5_account_bridge/source.py::read_instrument_specification` already uses for
  this exact field: `tick_value / tick_size = 374.601` (per lot).

Both are now genuinely derived from this run's own live `symbol_info` read — not assumed, not copied
from BTCUSD.

## 3. Result: dry-run denied again — `RISK_DENIED` / `VOLUME_STEP_ROUNDING_BELOW_MIN`

Same reason code as attempt 1, but now for a **verified, quantified, real economic constraint**, not a
configuration bug:

| | Value |
|---|---|
| Broker minimum volume | 0.01 lots |
| Stop distance (2% of entry, unchanged) | $81.05 |
| `point_value` (corrected, per-unit) | 3.746 PLN/oz per $1 |
| Risk required for the MINIMUM tradable position (0.01 lots) at this stop | **303.60 PLN** |
| Account equity | 10,026.83 PLN |
| **Required risk-per-trade % for 0.01 lots** | **≈ 3.03%** |
| Configured `risk_per_trade_pct` (untouched, per instruction) | 0.5% |

**Neither `risk_per_trade_pct` nor the stop distance was changed** — the 3.03% figure above is computed
and reported only, never applied. No order was sent; the dry-run denies before the DEMO leg is ever
reached. Confirmed after: zero open positions, zero open orders on XAUUSD.

## 4. What this means, stated plainly

At this account's actual equity and the project's own 0.5% risk-per-trade default, a 2%-of-price stop on
XAUUSD (~$81 at current prices) cannot be sized down to the broker's minimum tradable lot (0.01) without
risking roughly six times the configured budget. This is not a bug in `point_value` (now corrected and
verified) — it is the sizing formula correctly reporting a genuine mismatch between this account's size,
the 0.5% risk convention, and gold's per-lot economics at a 2% stop.

## 5. Stopping for a decision, per instruction

Three ways forward exist, none of which I have applied:
- Widen `risk_per_trade_pct` for this one test (you explicitly forbade this).
- Use a tighter stop distance than 2% (you explicitly forbade changing this too).
- Accept that the infrastructure test cannot exercise the FULL AI Trader risk-sizing pipeline at this
  account size without one of the above, and instead test the send/close mechanics directly (bypassing
  `compute_sizing`, submitting the broker's own minimum volume explicitly) — a different kind of test
  than "exact ca testul BTCUSD," since BTCUSD's own script happened to size correctly by coincidence of
  BTC's much smaller contract_size, not because it tested this same constraint.

**No order sent. No position opened. Account unchanged. Awaiting your decision.**
