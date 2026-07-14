# Risk Manager v1 — Phase 5.5 (design)

The **Risk Manager** is the fifth module of the AI Trader and its permanent risk-control authority. It receives
ranked `OpportunityScore`s from the Scoring Engine and decides, deterministically, whether each trade is
**ALLOWED** and — if allowed — the **execution constraints** (position size and limits). It is the last gate
before execution.

**This package is documentation, architecture, and JSON Schema only.** No runtime code, no executable logic, no
research, no backtests. It modifies nothing: Research Lab, engine, Strategy Library, Strategy Interface, Market
Scanner, Strategy Manager, Signal Engine, Scoring Engine, S1–S51, Wave 1, Knowledge Graph, holdout are all
untouched. Everything is additive inside `ai_trader/risk_manager/`.

## Responsibilities
- Receive ranked `OpportunityScore`s (Scoring Engine) plus the current portfolio/account state (Portfolio
  Manager) and a passed-in risk context.
- Apply the deterministic **risk policy** (`RISK_POLICY.md`) → ALLOW or DENY, with reasons.
- For allowed trades, compute the **position size** and execution constraints (`POSITION_SIZING.md`).
- Maintain the global risk state (READY / SUSPENDED / EMERGENCY_STOP) and enforce the kill-switch.
- Emit standardized `RiskDecision`s (`RISK_SCHEMA.json`) to the Execution Engine (allowed) / back to the caller
  (denied). Report health/statistics.

## What it is — and is NOT
| the Risk Manager DOES | the Risk Manager does NOT |
|---|---|
| decide ALLOW/DENY per opportunity, deterministically | produce signals |
| size positions + set execution constraints | evaluate strategies or compute opportunity scores |
| enforce portfolio/exposure/loss/drawdown limits, cooldowns, filters | learn or adapt |
| own the emergency stop / kill switch / suspension / recovery | execute or route orders (that is the Execution Engine) |
| read portfolio/account state (Portfolio Manager) | access Research Lab / Knowledge Base / Strategy Library |
| emit `RiskDecision`s to the Execution Engine | fetch market data or talk to the broker directly |

It is a **pure, deterministic decision function**: `RiskDecision = f(OpportunityScore, RiskContext, PortfolioState,
config, risk_state)`. Same inputs ⇒ same decision. No stochastic behavior.

## Boundaries
- **Never** produces signals, evaluates strategies, or scores opportunities (upstream jobs).
- **Never** learns or adapts (weights/limits are fixed config, versioned — not trained).
- **Never** executes or routes orders, and **never** talks to the broker (the Execution Engine does that).
- **Never** reads Research-Lab artifacts, the Knowledge Base, the Strategy Library, or the Signal Engine directly.
- **Never** fetches market data itself — the market-risk context is passed in (assembled upstream), so the
  Risk Manager stays a pure decision function on its inputs.

## Pipeline position
```
… Scoring Engine → [Risk Manager] → Execution Engine
        OpportunityScore[]     RiskDecision[] (ALLOW + size/constraints | DENY + reasons)
             ▲
   PortfolioState (Portfolio Manager, read)
```

## Module interaction (fixed)
- **Allowed direct:** Scoring Engine (input), Portfolio Manager (read portfolio/account state), Execution Engine
  (output: allowed decisions).
- **Forbidden (never direct):** Research Lab, Knowledge Base, Strategy Library, Signal Engine, Broker, Learning
  Engine.

## Failure policy (fail-safe = DENY)
The safe resting decision is **DENY**. Any missing input, invalid opportunity, unavailable portfolio state, breached
limit, degraded data, or internal error resolves to **DENY** with structured reasons — never a fabricated ALLOW.
A global fault escalates to `SUSPENDED` or `EMERGENCY_STOP` (all-DENY). One bad opportunity never affects the
evaluation of the others; the batch always completes.

## Package contents
| file | purpose |
|---|---|
| `README.md` | this overview |
| `RISK_MANAGER_ARCHITECTURE.md` | purpose, responsibilities, inputs/outputs, components, risk pipeline, validation, failure modes, data flow, startup/shutdown, performance model, versioning, interaction matrix |
| `RISK_POLICY.md` | every deterministic risk rule (limits, filters, cooldowns, emergency stop, kill switch, recovery) |
| `POSITION_SIZING.md` | risk-per-trade, portfolio risk, fixed-fractional, volatility/ATR scaling, allocation caps, scaling in/out, partial exits, pyramiding, Kelly (future) |
| `RISK_SCHEMA.json` | JSON Schema (Draft 2020-12) for the `RiskDecision` |
| `RISK_API.md` | the public API (evaluate/allow_trade/position_size/portfolio_limits/health/statistics) — definition only |
| `RISK_SEQUENCE.md` | single trade, multiple signals, portfolio full, daily stop, kill switch, recovery, startup/shutdown |
| `RISK_STATE_MACHINE.md` | the risk lifecycle (IDLE/READY/EVALUATING/ALLOW/DENY/SUSPENDED/EMERGENCY_STOP/SHUTDOWN) |

## Status
DESIGN (Phase 5.5). Deliverables complete for review. **The Execution Engine is NOT begun** and must wait for
explicit CEO approval.
