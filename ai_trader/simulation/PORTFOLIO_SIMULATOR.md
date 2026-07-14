# Portfolio Simulator v1 — the virtual account (design)

The Portfolio Simulator is the simulation-only virtual account. It books fills from the Execution Simulator,
maintains positions, marks-to-market on every bar, and exposes the **same `PortfolioState`** the Risk Manager and
Execution Engine read live. In live trading this role is played by the Portfolio Manager + the real broker account
— the `PortfolioState` shape is identical, so nothing upstream changes. Design only — no code.

---

## 1. Purpose & contract
- Own the virtual account truth: **balance, equity, floating (unrealized) PnL, closed (realized) PnL, positions,
  margin, exposure, drawdown, trade history**.
- Provide `PortfolioState` (the shape the Risk Manager consumes) and consume `Fill` events (from the Execution
  Simulator). Deterministic: given the same fills + bars + starting capital, the account evolution is identical.
- No decisions — it is pure accounting + mark-to-market.

## 2. Account state (maintained every bar)
| quantity | definition |
|---|---|
| `balance` | realized cash: starting_balance + Σ closed PnL − Σ commissions/fees |
| `equity` | `balance + floating_pnl` (mark-to-market value of open positions) |
| `floating_pnl` | Σ over open positions of `(mark_price − entry) × dir × size × point_value` |
| `closed_pnl` | Σ realized PnL of closed positions (cumulative + per period) |
| `used_margin` | Σ position margin (per `margin_model.initial_margin_pct` × notional) |
| `free_margin` | `equity − used_margin` |
| `margin_level` | `equity / used_margin` (%) — drives margin-call/liquidation |
| `exposure` | gross + net notional across positions; per-symbol and per-correlation-group |
| `leverage` | gross notional / equity |
| `equity_hwm` | running high-water mark of equity |
| `drawdown` | `(equity_hwm − equity)` and `% = drawdown / equity_hwm`; `max_drawdown` tracked over the run |

Mark price for MTM = the current bar's close (deterministic; the same bar the pipeline evaluated).

## 3. Position lifecycle
```
OPEN (fill on an OPEN/SCALE_IN order) → position created/increased (weighted-avg entry)
   MODIFY (bracket stop/target attached; stop moved by a partial-exit plan)
   SCALE_OUT / PARTIAL_EXIT (reduce_only fill) → realized PnL booked for the closed fraction; remainder continues
   CLOSE (stop/target/close fill, or close_at_end) → realized PnL booked; position removed
```
- **Weighted-average entry** on scale-in; **FIFO/average realized PnL** on scale-out (fixed, documented
  convention, versioned).
- Each open position tracks: symbol, direction, size, avg_entry, stop, target, opened_at, strategy_id,
  correlation_group, current floating PnL.
- **Position = the unit of exposure**; the Portfolio Simulator enforces one position per symbol by default (the
  Risk Manager already gates this), and updates exposure/margin on every open/modify/close.

## 4. Margin simulation
- On open: `required_margin = notional × initial_margin_pct`; must be ≤ `free_margin` or the fill is rejected
  back (deterministic) — though the Risk Manager's leverage/exposure limits normally prevent this upstream.
- On each bar: recompute `used_margin`, `margin_level`. If `margin_level < maintenance_margin_pct` →
  **margin-call / liquidation event**: reduce/close positions per the liquidation policy (deterministic order),
  book realized PnL, log a risk event. Config decides whether the run halts on liquidation.

## 5. PnL accounting
- **Floating PnL** updates every bar from MTM (unrealized).
- **Closed PnL** is booked at each closing fill (full or partial), net of that fill's commission/spread already
  applied by the Execution Simulator, in R and in currency.
- **Fees/spread/slippage** reduce balance at fill time (the Execution Simulator computes the fill price incl.
  spread/slippage; the Portfolio Simulator deducts commission and books the net).
- Per-trade record: entry/exit price+time, size, gross & net PnL (currency + R), fees, holding time, strategy_id,
  MFE/MAE (max favorable/adverse excursion, from bar highs/lows over the hold).

## 6. Trade history & execution log
- **Trade history:** one record per closed trade (and per partial exit) with full attribution (strategy_id,
  symbol, direction, entry/exit, PnL R+currency, fees, holding bars, MFE/MAE, decision_id/signal_id refs).
- **Execution log:** the ordered stream of order events (submitted/ack/fill/partial/cancel/reject/expire) from the
  Execution Simulator, joined to the resulting position changes — the audit trail.
- Both stream to the Simulation Ledger (bounded memory; persisted per `record` config).

## 7. Exposure & capital allocation
- **Exposure:** tracked gross/net, per-symbol, per-correlation-group, per-strategy — feeds the Risk Manager's
  limit checks (via `PortfolioState`) and the Performance Analyzer's attribution.
- **Capital allocation:** the Portfolio Simulator reports how equity/risk is distributed across strategies/groups
  over time (from open positions + realized PnL). It does not DECIDE allocation (the Risk Manager sizes and the
  `capital_allocation` policy in the run config guides) — it MEASURES and exposes it.

## 8. `PortfolioState` provided to the pipeline
Each bar, the Portfolio Simulator exposes the `PortfolioState` the Risk Manager (and the Execution Engine's
consistency checks) read: open positions, pending orders, aggregate exposure, leverage, realized/unrealized PnL
(intraday/daily/weekly), equity, equity HWM, current drawdown. **This is the identical shape the future Portfolio
Manager will provide live** — the pipeline cannot tell the difference.

## 9. Determinism guarantees
- Account evolution is a pure function of `(ordered Fills, bars for MTM, starting capital, margin/cost models)`.
  No wall-clock, no RNG (all randomness is upstream in the Execution Simulator's seeded slippage, already baked
  into the fill price).
- Accounting conventions (weighted-avg entry, realized-PnL method, MTM-on-close, margin formulas) are fixed and
  versioned; identical inputs ⇒ identical equity curve, drawdown, and trade history.

## 10. Live parity (the swap)
The Portfolio Simulator provides the same `PortfolioState` contract the live Portfolio Manager will (reconciled
against a real broker account). Going live replaces the virtual account's fills-source (Execution Simulator → real
Broker Adapter) and truth-source (simulated book → broker reconciliation); the state SHAPE and the upstream
consumers are unchanged.
