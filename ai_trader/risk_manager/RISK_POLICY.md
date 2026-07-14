# Risk Policy v1 — the deterministic rule set (design)

Every rule the Risk Manager enforces. All rules are **deterministic** — fixed thresholds from the versioned
`RiskConfig`, evaluated by exact comparison against the `OpportunityScore`, `RiskContext`, and `PortfolioState`.
No ML, no randomness, no discretion. The default thresholds below are the v1 configuration; changing any value
bumps `risk_policy_version`. A rule that fails produces a **DENY** with the named reason code; some guards also
transition the engine's global state (SUSPENDED / EMERGENCY_STOP).

- **risk_policy_version:** `1.0.0`. All monetary limits are expressed as % of account equity or in R (1R = the
  risk defined by the trade's stop). Defaults are conservative placeholders for design review, not tuned values.

---

## 1. Evaluation order (first failing gate denies)
`Global State → Opportunity Sanity → Recommendation Floor → Pre-Trade Filters → Portfolio Limits → Loss/Drawdown
Guards → Cooldowns → (ALLOW) Sizing → Constraints`. (See `RISK_MANAGER_ARCHITECTURE.md §5`.) Each rule below states
its gate, its default threshold, its reason code, and any state escalation.

---

## 2. Position-count & portfolio-structure limits
| rule | default | reason code | notes |
|---|---|---|---|
| **Maximum simultaneous positions** | 5 open | `LIMIT_MAX_POSITIONS` | across all symbols/strategies |
| **Maximum per symbol** | 1 open | `LIMIT_MAX_PER_SYMBOL` | one position per symbol (no netting/hedging in v1) |
| **Maximum correlated positions** | 2 per correlation group | `LIMIT_MAX_CORRELATED` | groups by mechanism class / instrument correlation; a new position in a full group is denied |
| **Maximum portfolio exposure** | 30% of equity at risk (sum of open-position risk in R × R-value) | `LIMIT_MAX_EXPOSURE` | total open risk budget |
| **Maximum leverage** | 3.0× notional/equity | `LIMIT_MAX_LEVERAGE` | gross notional cap |
| **Maximum overnight exposure** | 15% of equity at risk held past session close | `LIMIT_MAX_OVERNIGHT` | a new position that would breach the overnight cap near close is denied |
| **Maximum event exposure** | 0 new positions within 15 min of a HIGH-impact calendar event | `LIMIT_MAX_EVENT` | from `RiskContext.calendar.event_flags` |

## 3. Loss & drawdown guards (may escalate global state)
| rule | default | reason code | escalation |
|---|---|---|---|
| **Maximum daily loss** | −3% equity (realized+unrealized intraday) | `LOSS_DAILY` | → **SUSPENDED** for the rest of the trading day |
| **Maximum weekly loss** | −6% equity | `LOSS_WEEKLY` | → **SUSPENDED** for the rest of the week |
| **Maximum drawdown** | −12% from equity high-water mark | `DRAWDOWN_MAX` | → **SUSPENDED** until manual/recovery reset |
| (all guards) | breach at evaluation time | | new trades DENIED while suspended |

## 4. Cooldowns (deterministic clocks)
| rule | default | reason code |
|---|---|---|
| **Cooldown after a loss** | no new position on the same symbol for 4 bars after a losing exit | `COOLDOWN_AFTER_LOSS` |
| **Cooldown after consecutive losses** | after 3 consecutive losing trades (any symbol) → 60-minute global cooldown | `COOLDOWN_CONSECUTIVE` |
| **Per-strategy cooldown** | honor the strategy contract's `execution.cooldown` (bars, scope) | `COOLDOWN_STRATEGY` |
Cooldown clocks are read from the Ledger/PortfolioState (realized exits); deterministic given the state.

## 5. Pre-trade market-condition filters (from RiskContext)
| filter | default | reason code |
|---|---|---|
| **Volatility filter** | deny if ATR/price is outside [0.25×, 4×] its rolling median (too dead / too wild) | `FILTER_VOLATILITY` |
| **Spread filter** | deny if current spread > 3 × the cost-model spread assumption | `FILTER_SPREAD` |
| **Liquidity filter** | deny if the liquidity proxy (e.g. volume/ą depth) is below the configured floor | `FILTER_LIQUIDITY` |
| **News filter** | deny within the event blackout window of a HIGH-impact event (see §2 event exposure) | `FILTER_NEWS` |
| **Data-quality filter** | deny if `RiskContext.data_quality ∈ {STALE, INSUFFICIENT}` (worst-case treatment) | `DATA_DEGRADED` |

## 6. Weekend & gap rules
| rule | default | reason code |
|---|---|---|
| **Weekend rule** | no NEW positions after the Friday cut-off time; positions held over the weekend must be within the overnight cap | `RULE_WEEKEND` |
| **Gap rule** | deny new entries during the first N bars after a weekend/session gap > threshold (unstable pricing); existing stops honored | `RULE_GAP` |

## 7. Recommendation floor & opportunity sanity
| rule | default | reason code |
|---|---|---|
| **Recommendation floor** | require `recommendation ∈ {STRONG,MODERATE,WEAK}_OPPORTUNITY`; `WATCH`/`SKIP`/`INVALID` → deny | `BELOW_FLOOR` |
| **Minimum score** | require `total_score ≥ 25` (POOR band denied) | `SCORE_TOO_LOW` |
| **Opportunity sanity** | require an actionable state (BUY/SELL) with a valid `trade_context` (entry + stop) | `NOT_ACTIONABLE` / `INVALID_INPUT` |

## 8. Emergency controls
- **Emergency stop** — a hard, immediate transition to `EMERGENCY_STOP`: all new trades DENIED
  (`EMERGENCY_STOP`), and the Risk Manager signals the Execution Engine to flatten/close per the emergency policy
  (the Execution Engine performs the closing — the Risk Manager only decides). Triggers: max-drawdown breach,
  operator command, or a critical fault (e.g. PortfolioState corruption).
- **Kill switch** — an operator/monitor override that forces `EMERGENCY_STOP` regardless of metrics; only an
  operator can clear it. While engaged, every `evaluate()` returns DENY(`KILL_SWITCH`).
- **Trading suspension** — a softer stop (`SUSPENDED`) from a loss/drawdown guard: no new trades until the
  suspension window elapses or recovery conditions are met; existing positions are managed normally (stops honored).

## 9. Recovery policy (deterministic)
- **From SUSPENDED (daily/weekly loss):** auto-clears at the next trading day / week boundary IF drawdown is back
  within limits; otherwise remains suspended.
- **From SUSPENDED (drawdown):** requires an explicit reset (operator) AND drawdown recovered above the reset
  threshold (e.g. drawdown < 8% from HWM) before returning to `READY`.
- **From EMERGENCY_STOP / kill switch:** requires an explicit operator clear; on clear, re-enters `READY` only
  after re-reconciling `PortfolioState` and confirming no guard is still tripped.
- **Ramp-up (optional, config):** on recovery, an optional reduced-size window (e.g. 50% sizing for K trades)
  before full sizing resumes — deterministic and versioned; disabled by default in v1.

## 10. Determinism guarantees
- Every threshold is a fixed number in `RiskConfig`; every rule is an exact comparison. Identical
  `(OpportunityScore, RiskContext, PortfolioState, RiskConfig, risk_state)` ⇒ identical DENY/ALLOW and identical
  reason codes.
- Rules are evaluated in the fixed order (§1); the applied rules and the first failing gate are recorded in
  `RiskDecision.applied_rules` / `denied_reasons` for audit.
- No rule uses randomness, wall-clock-in-logic (only deterministic bar/time boundaries from the context), or
  learned parameters.
