# CROSS_MARKET_RELATIVE_RESPONSE_FACTORY_V1_REPORT — final

One bounded cycle: does a causal XAU-vs-cross-market DISLOCATION (relative-response residual) predict subsequent XAU direction? Not the
falsified simple DXY impulse. **SURVIVED 0.** Governed data only (DXY, no acquisition); no M5 (§21). S5/Q4/AI-Trader/P007/MGMT-004/MT5/
StrategyCatalog untouched. Code: `cm_core.py`, `cm_scan.py`. Docs: atlas, contrast report, hypothesis register, this report.

## §23 SCOREBOARD
```
CROSS_MARKET_RELATIVE_RESPONSE_FACTORY_V1_COMPLETE = YES
DATA_AUDIT_PASS = YES (scoped: DXY-only H1, 3 governed slices, no 2024+, no risk proxy; family F not testable)

RAW_HYPOTHESES = 20 · DEDUPED_HYPOTHESES = 5 · TESTED = 5 · FALSIFIED = 5 · SURVIVED = 0

CATCHUP_TESTED = YES · RELATIVE_STRENGTH_TESTED = YES · OVERSHOOT_TESTED = YES · LEAD_LAG_TESTED = YES · SESSION_RESOLUTION_TESTED = YES

CROSS_MARKET_INCREMENTAL_INFORMATION_FOUND = NO   (relative-response residual does NOT beat the simple DXY impulse; all families negative)
CROSS_ERA_STABLE_SURVIVOR = NO
OOS_SURVIVOR = NO
OOS_INTEGRITY = PASS (5 families pre-specified; 3-block design; no OOS-driven redefinition)

NEW_STRATEGY_CANDIDATES = 0
READY_FOR_STATISTICIAN_REVIEW = NO
```

## Findings
1. **All five relative-response families are net-negative** (A −0.084, B −0.240, C −0.125, D ≈ control, E −0.058) and sign-unstable across
   the three governed DXY blocks.
2. **The residual adds nothing over the raw impulse.** The catch-up family (the most natural residual play) is *worse* than the simple-DXY-
   impulse control (−0.084 vs −0.069); no family beats it. `CROSS_MARKET_INCREMENTAL_INFORMATION_FOUND = NO`.
3. This is a **stronger** negative than the OB-level and session-state cycles: there, the structural condition beat its control (info
   present, not monetizable). Here the new cross-market residual beats nothing — no incremental information even in the informational sense.

## Data limitation (honest scope)
The only governed cross-market series is DXY (H1, 3 disjoint blocks ~7 years, 2024+ protected). No risk-market proxy (NDX/SPX/VIX) exists
in-project, so family F (dual-confirmation) could not be tested and the recent 2024-2026 gold regime is uncovered. The negative is robust
*within available data*, but a definitive cross-market verdict would require acquiring a governed risk-market series and 2024+ DXY — a CEO
data-acquisition decision, not started here.

## §25 PROTECTION
```
S5_UNTOUCHED=YES · Q4_UNTOUCHED=YES · AI_TRADER_UNTOUCHED=YES · P007_UNTOUCHED=YES · MGMT004_UNTOUCHED=YES · MT5_UNTOUCHED=YES
STRATEGY_CATALOG_UNTOUCHED=YES · NO_LIVE_PROMOTION=YES
```

## §24/§26 close + next-space ranking (NOT started)
SURVIVED = 0 → cycle closed; NKB updated. Ten price-only/exogenous-price frontiers now converge on: **XAU direction is efficient to
price-only and price-derived cross-market information; the only stable incremental signal ever found was exogenous-but-informational
(DXY-NDX1), and it does not monetize directionally.** Genuinely-distinct remaining spaces, ranked:
1. **EXOGENOUS NON-PRICE DATA — real yields (US 10y TIPS / real-rate series).** The standing #1. Every price and price-cross-market
   frontier is now exhausted; the one untested axis is the *non-price* macro driver (real yields) that DXY only reflects. **Requires a
   governed real-rate series that does not exist in-project → a CEO data-acquisition decision.**
2. **Acquire a governed risk-market series (NDX/SPX) + 2024+ DXY** to complete THIS cross-market family properly (F + recent era).
3. **Non-directional use of confirmed information** — OB-level + session-state information are confirmed real; use them as an S5
   risk/sizing/no-trade overlay (no new directional edge required).

## Honest note
The price-only and price-cross-market search space is now substantially exhausted (S5 remains the sole tradeable edge). The two
value-bearing directions both require a decision only the CEO can make: **acquire non-price exogenous data (real yields) or a risk-market
series**, or **pivot to monetizing the confirmed structural information non-directionally around S5.** Continuing to test price-derived
directional mechanisms has low expected value.

NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```
READY_FOR_STATISTICIAN_REVIEW = NO
```
