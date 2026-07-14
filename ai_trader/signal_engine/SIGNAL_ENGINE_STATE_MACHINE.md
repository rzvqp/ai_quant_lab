# Signal Engine v1 — Signal State Machine (design)

Every evaluated (strategy, symbol) yields exactly one `StrategySignal` per cycle, whose `state` is one of the nine
states below. The state is the terminal outcome of the fixed evaluation pipeline (`SIGNAL_ENGINE_ARCHITECTURE.md
§3`). This document defines each state, exactly when it is produced, and the decision machine that assigns it.
Design only — no code.

---

## 1. The nine signal states

| state | actionable? | meaning | produced when |
|---|---|---|---|
| `BUY` | yes (enter now) | actionable long entry this bar | setup present + confirmations met + LONG + entry trigger is NOW |
| `SELL` | yes (enter now) | actionable short entry this bar | setup present + confirmations met + SHORT + entry trigger is NOW |
| `LONG_READY` | ready (pending trigger) | valid long setup, entry not yet triggered | setup present + confirmations met + LONG + entry pending (e.g. next-open / limit not yet touched) |
| `SHORT_READY` | ready (pending trigger) | valid short setup, entry not yet triggered | setup present + confirmations met + SHORT + entry pending |
| `WAIT_CONFIRMATION` | not yet | setup forming, required confirmations not all met | `detect.setup_forming=true` but `required_confirmations` not fully satisfied |
| `NEED_CONTEXT` | no | context insufficient to evaluate this strategy | MarketContext `sufficiency=INSUFFICIENT` / missing required field / warmup not met |
| `BLOCKED` | no | strategy prevented from signaling regardless of setup | `can_trade.allowed=false`: cooldown, out-of-session/regime, an `invalid_conditions` holds, health `DISABLED`, or kill-switch |
| `INVALID` | no | the strategy/contract is invalid at eval, or the produced signal failed validation | health `INVALID`/inactive, eval timeout, or Signal Validation failure (schema/direction/confidence/…) |
| `NO_SIGNAL` | no | strategy evaluated cleanly, no setup | `detect.setup_forming=false` OR `generate_signal.present=false` |

Only `BUY`/`SELL` are "enter now"; `LONG_READY`/`SHORT_READY` are "armed, awaiting the trigger"; the remaining
five are non-actionable. The Scoring Engine decides what to do with actionable/ready states — the Signal Engine
only reports them.

---

## 2. Decision machine (pipeline → state)

```
                         evaluate(strategy, MarketContext, trader_state)
                                              │
                                              ▼
                         ┌──────── health() ─────────┐
                 INVALID/DISABLED?                    OK
                        │                              │
                     STATE=INVALID (health)            ▼
                     (or BLOCKED if DISABLED)   ┌─ can_trade() ─┐
                                          allowed=false      allowed=true
                                                │                 │
                                          STATE=BLOCKED            ▼
                                     (invalid_conditions)  ┌ context sufficient? ┐
                                                          no                    yes
                                                           │                     │
                                                    STATE=NEED_CONTEXT           ▼
                                                    (missing_context)     ┌ detect() ─┐
                                                                    setup_forming=false  true
                                                                          │             │
                                                                    STATE=NO_SIGNAL      ▼
                                                                               ┌ generate_signal() ┐
                                                                        present=false          present=true
                                                                               │                    │
                                                                        STATE=NO_SIGNAL             ▼
                                                                                         ┌ confirmations met? ┐
                                                                                        no                   yes
                                                                                         │                    │
                                                                              STATE=WAIT_CONFIRMATION          ▼
                                                                                                    ┌ entry trigger NOW? ┐
                                                                                                   yes                  no
                                                                                                    │                    │
                                                                                          STATE=BUY/SELL         STATE=LONG_READY/
                                                                                          (by direction)         SHORT_READY
                                                                                                    │                    │
                                                                                                    └────────┬───────────┘
                                                                                                             ▼
                                                                                                     Signal Validation
                                                                                                    fails → STATE=INVALID
                                                                                                    ok    → emit
```

Precedence (highest first): **INVALID (health/eval) → BLOCKED → NEED_CONTEXT → NO_SIGNAL → WAIT_CONFIRMATION →
READY/actionable → INVALID (validation)**. The pipeline short-circuits at the first gate that fails, so exactly one
state is assigned. Signal Validation can override a would-be actionable state to `INVALID` (fail-safe: a malformed
actionable signal is never emitted as actionable).

---

## 3. State ↔ Strategy API mapping

| pipeline stage | Strategy API call | result → state |
|---|---|---|
| Precondition | `health()` | `INVALID`/`DISABLED` → INVALID/BLOCKED |
| Precondition | `can_trade(ctx, state)` | `allowed=false` → BLOCKED |
| Context | (engine checks `MarketContext.sufficiency` vs `required_context()`) | insufficient → NEED_CONTEXT |
| Signal | `detect(ctx)` | `setup_forming=false` → NO_SIGNAL |
| Signal | `generate_signal(ctx)` | `present=false` → NO_SIGNAL; `present=true` → continue |
| Signal | `Signal.required_confirmations_met` | false → WAIT_CONFIRMATION |
| Signal | `Signal.direction` + entry-trigger timing | now → BUY/SELL; pending → LONG_READY/SHORT_READY |
| Validation | engine Signal Validation | fail → INVALID |

Note: `get_score()` is **never** called here (scoring is downstream). The state depends only on the strategy's
descriptive evaluation, never on any ranking.

---

## 4. Determinism & fail-safe
- The decision machine is a pure function of `(MarketContext, handle, trader_state)`; identical inputs → identical
  state (replay parity).
- Every abnormal path resolves to a **non-actionable** state (`INVALID`/`BLOCKED`/`NEED_CONTEXT`/`NO_SIGNAL`),
  each carrying structured `quality_flags` + `Explanation`, so downstream can always tell WHY. A missing/duplicate/
  corrupted output becomes `INVALID` — never a fabricated `BUY`/`SELL`.
- A strategy that times out or errors internally is isolated: its state is `INVALID` (`EVAL_TIMEOUT`/
  `CORRUPTED_OUTPUT`); the rest of the batch is unaffected.
