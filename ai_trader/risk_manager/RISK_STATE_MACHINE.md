# Risk Manager v1 — State Machine (design)

Two levels: (A) the **global engine lifecycle** (the module's operational risk state, which gates every decision)
and (B) the **per-decision outcome** (ALLOW/DENY for one opportunity). Design only — no code.

---

## A. Global engine states

| state | meaning | new trades |
|---|---|---|
| `IDLE` | constructed, not configured | none |
| `READY` | operating normally; evaluates each opportunity on its merits | ALLOW/DENY per policy |
| `EVALUATING` | actively processing an opportunity batch (transient sub-state of READY) | producing decisions |
| `SUSPENDED` | a loss/drawdown guard tripped, or a soft operator halt | all DENY (existing positions managed) |
| `EMERGENCY_STOP` | hard stop: max-drawdown breach, kill switch, or critical fault | all DENY; may instruct Execution to flatten |
| `SHUTDOWN` | draining/stopped; terminal | none |

`ALLOW` and `DENY` are **per-decision outcomes** produced while in `READY/EVALUATING` (see part B), not global
engine states. `SUSPENDED` and `EMERGENCY_STOP` are global and force every decision to DENY.

## B. State diagram

```
IDLE ──configure/handshake──▶ READY ⇄ EVALUATING
                               │  ▲        │ (per opportunity → ALLOW | DENY)
                               │  │        │
     loss/drawdown guard trip  │  │ recovery (auto @ day/week boundary within limits,
        (LOSS_DAILY/WEEKLY/     │  │        or operator reset)
         DRAWDOWN_MAX)          ▼  │
                            SUSPENDED ──────┘
                               │  ▲
   max-drawdown breach /       │  │ operator CLEAR + PortfolioState reconciled + no guard tripped
   kill switch / critical fault▼  │
                          EMERGENCY_STOP
                               │
             shutdown (from any state) ──▶ SHUTDOWN
```

### Transitions
| # | from | to | trigger | guard | effect |
|---|---|---|---|---|---|
| G1 | IDLE | READY | configure + handshakes ok | no guard tripped in initial PortfolioState | begin normal evaluation |
| G2 | IDLE | SUSPENDED/EMERGENCY_STOP | configure | a guard already tripped / kill switch on | start in the safe state (all DENY) |
| G3 | READY | EVALUATING | opportunity batch arrives | — | process batch |
| G4 | EVALUATING | READY | batch emitted | — | idle again |
| G5 | READY/EVALUATING | SUSPENDED | LOSS_DAILY / LOSS_WEEKLY / DRAWDOWN_MAX breach | — | all new trades DENY; existing managed |
| G6 | SUSPENDED | READY | recovery | day/week boundary AND drawdown within limits, or operator reset | resume (optional reduced-size ramp) |
| G7 | any | EMERGENCY_STOP | max-drawdown breach / kill switch / critical fault | — | all DENY; may instruct Execution to flatten |
| G8 | EMERGENCY_STOP | READY | operator CLEAR | PortfolioState reconciled AND no guard tripped | resume |
| G9 | any | SHUTDOWN | shutdown | — | drain in-flight; hold no truth of fills |
| G10 | DEGRADED overlay | — | Portfolio/Execution dependency unavailable | — | all DENY(PORTFOLIO_UNAVAILABLE) until restored (not a distinct state; a health flag over READY) |

## C. Per-decision outcome (inside EVALUATING, per opportunity)
```
opportunity
   │  Global State != READY → DENY(SUSPENDED | EMERGENCY_STOP | KILL_SWITCH)
   ▼ READY
   Opportunity Sanity → fail → DENY(NOT_ACTIONABLE/INVALID_INPUT)
   Recommendation Floor / Min Score → fail → DENY(BELOW_FLOOR/SCORE_TOO_LOW)
   Pre-Trade Filters → fail → DENY(FILTER_*/DATA_DEGRADED)
   Portfolio Limits → fail → DENY(LIMIT_*)
   Loss/Drawdown Guards → breach → DENY(LOSS_*/DRAWDOWN_*)  [+ escalate global → SUSPENDED]
   Cooldowns → active → DENY(COOLDOWN_*)
   → ALLOW
   Sizing → size < min → DENY(SIZE_BELOW_MIN) ; else size (clamped)
   Constraints → build → emit RiskDecision(ALLOW)
```
The running portfolio view is updated after each ALLOW (slots/budget consumed) so later opportunities in the same
batch see the effect — evaluated in deterministic rank order.

## D. Determinism & fail-safe invariants
1. The global state is a deterministic function of `PortfolioState` + guards + operator inputs; the per-decision
   outcome is a deterministic function of `(opportunity, RiskContext, running PortfolioState, RiskConfig, state)`.
2. The safe resting outcome is **DENY**; global faults escalate to `SUSPENDED`/`EMERGENCY_STOP` (all-DENY). The
   Risk Manager can only become MORE conservative under uncertainty.
3. Recovery is deterministic and, for drawdown/emergency, requires an explicit operator clear — never automatic.
4. Identical inputs ⇒ identical states, decisions, and reason codes (replay parity).
