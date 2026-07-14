# Position Sizing v1 — the deterministic sizing model (design)

How the Risk Manager turns an ALLOWED opportunity into a concrete position size and the associated constraints.
All sizing is **deterministic** — fixed formulas over the account equity, the trade's stop distance, and the
volatility context. No ML, no discretion, no randomness. Documentation only — the formulas are the specification.

- **risk_policy_version:** `1.0.0` (sizing parameters live in the same versioned config as the policy). Sizing runs
  ONLY after the risk policy returns ALLOW.

---

## 1. Core concept — R-normalized, risk-first
The Strategy Library defines each trade in **R units**: `1R = |entry − stop|` (after the engine stop-floor). The
Risk Manager sizes so that **1R = a fixed fraction of account equity**:
```
risk_budget_currency = risk_per_trade_pct × account_equity           (the money put at risk on this trade)
stop_distance        = |entry − stop|   (price units, from trade_context; must be > 0)
size_units           = risk_budget_currency / (stop_distance × point_value)
```
The trade's monetary risk equals `risk_budget_currency` by construction. Position size is derived FROM risk, never
the other way around.

## 2. Risk per trade
- **`risk_per_trade_pct`** (default **0.5%** of equity) — the fraction of equity risked on a single trade.
- Optionally scaled by opportunity quality within a bounded band (deterministic): e.g.
  `effective_risk_pct = risk_per_trade_pct × quality_factor`, `quality_factor ∈ [0.5, 1.0]` mapped from
  `total_score` bands (POOR/WEAK→0.5 … STRONG→1.0). Bounded so a high score can never exceed the base risk cap.

## 3. Portfolio risk
- **Aggregate open risk** must stay within `LIMIT_MAX_EXPOSURE` (RISK_POLICY §2). If sizing a new trade at the
  computed size would breach the aggregate cap, the size is **reduced** to fit the remaining budget; if the
  remaining budget < `min_allocation`, the trade is DENIED (`SIZE_BELOW_MIN`).
- **Correlation-aware:** trades in the same correlation group share a sub-budget (deterministic split), so
  correlated positions cannot collectively exceed the group cap.

## 4. Fixed fractional (default method)
The default sizing method is **fixed-fractional risk** (§1 with a constant `risk_per_trade_pct`). It is simple,
deterministic, and robust; it is the v1 method.

## 5. Volatility / ATR scaling (optional, deterministic)
- **Volatility scaling:** scale the risk fraction inversely to current volatility so that dollar-volatility of
  positions is more uniform: `risk_pct_vol = risk_per_trade_pct × clamp(target_vol / current_vol, vmin, vmax)`.
- **ATR scaling:** when a strategy's stop is ATR-based, the stop_distance already embeds ATR, so §1 naturally
  scales size down in high volatility. Explicit ATR scaling (adjusting `risk_pct` by an ATR ratio) is available as
  a config option, bounded and deterministic. Disabled by default (fixed-fractional is the v1 default).

## 6. Allocation caps
- **Maximum capital allocation** per position: `max_position_notional_pct` (default **20%** of equity notional) —
  the size is clamped so notional never exceeds this, even if the risk budget would allow more (protects against
  tiny-stop over-sizing beyond the engine floor).
- **Minimum allocation:** `min_allocation` (default the broker min lot, or 0.1% risk) — below this the trade is
  DENIED (`SIZE_BELOW_MIN`) rather than taking a meaningless position.

## 7. Scaling in / pyramiding (policy)
- **Scaling in:** adding to a winning position. v1 policy = **disabled by default**. If enabled (config), each
  add-on is a fresh sized tranche subject to the SAME per-symbol/portfolio limits and to a max number of tranches;
  the aggregate risk across tranches must stay within `risk_per_trade_pct` (adds do not increase total trade risk
  beyond the cap). Deterministic tranche schedule.
- **Pyramiding policy:** more than N tranches on one position is disallowed; total pyramided risk ≤ the single-
  trade risk cap. v1 default: **no pyramiding**.

## 8. Scaling out / partial exits (policy)
- **Scaling out / partial exits:** reducing a position before the final target (e.g. take 50% at 1R, move stop to
  breakeven). v1 policy = **documented, deterministic, config-driven**; the Risk Manager specifies the partial-
  exit *plan* as constraints (levels + fractions) in the `RiskDecision`; the **Execution Engine performs** the
  partial exits. The Risk Manager never executes them itself.
- Partial exits reduce open risk and update the running portfolio view deterministically.

## 9. Kelly (future — NOT used in v1)
- **Kelly sizing** is documented as a FUTURE option and is **not used in v1** (it requires reliable edge/variance
  estimates, which the current EXPLORATORY, unvalidated strategies do not provide — honesty rule). If ever
  enabled, it would be a bounded fractional-Kelly with a hard cap ≤ `risk_per_trade_pct`, deterministic given the
  contract evidence, and gated behind a matured validation ladder. v1 uses fixed-fractional only.

## 10. Output (into RiskDecision.sizing)
```
sizing = {
  method: "FIXED_FRACTIONAL",           // v1 default (VOL_SCALED / ATR_SCALED optional, config)
  risk_per_trade_pct, quality_factor,   // the fraction applied
  risk_R: 1.0,                          // by construction
  risk_budget_currency,                 // money at risk
  stop_distance, size_units, size_lots, // the concrete size
  max_size, min_size,                   // caps applied
  notional, leverage,                   // resulting exposure
  partial_exit_plan?                    // optional deterministic scale-out levels+fractions
}
```

## 11. Determinism guarantees
- Given `(trade_context, account_equity, RiskContext volatility, RiskConfig)`, the size is a fixed arithmetic
  result — identical inputs ⇒ identical size. No randomness, no learned parameters.
- All caps/floors are exact clamps; the applied method and parameters are recorded in `RiskDecision.sizing` for
  audit and reproducibility (tied to `risk_policy_version`).
