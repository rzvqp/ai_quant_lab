# S5_MT5_DEMO_UNATTENDED_SOAK_CONTRACT

**Mandate**: `AI-TRADER-S5-MT5-DEMO-UNATTENDED-SOAK-001`
**Package**: `ai_trader/new_brain_live/strategy_platform/mt5_demo_bridge/soak/`
**Builds on**: `mt5_demo_bridge/` (mandate `AI-TRADER-S5-MT5-DEMO-EXECUTION-001`, commit `8ea79b9`) --
`demo_execution_adapter.execute()`, the account-type hard gate, and the risk sizer are reused completely
unmodified. This package adds continuous operation on top: restart reconciliation before any submission,
position lifecycle tracking, a persisted safety-stop monitor, checkpoints, and health snapshots.

## 1. Module map

| Module | Purpose |
|---|---|
| `trade_lifecycle.py` | Detects a `SUBMITTED_ACK` order actually becoming a live position (`OPEN_CONFIRMED`), and a tracked position closing (`CLOSED`, with exit classification/P&L/R-result). Read-only observation only -- never issues its own broker call (own AST guard: `test_soak_never_calls_broker_directly.py`). |
| `metrics.py` | Cumulative WR/PF/avg-R/drawdown/streaks from `CLOSED` ledger rows. Observation only -- never fed back into S5/EV/risk. |
| `safety_monitor.py` | 13 named safety-stop conditions (mandate section 25). Persisted (`SqliteStateStore`); once tripped, blocks NEW submissions until a human calls `clear()` -- never auto-cleared. |
| `health_state.py` | Overwritten-each-cycle JSON snapshot (mandate section 29 fields). No secrets. |
| `checkpoints.py` | First-trade / 5-closed / 10-closed checkpoints + final report, each carrying a reference-only comparison against the validated S5 population (mandate section 22 -- never a pass/fail verdict). |
| `soak_loop.py` | The orchestrator: restart reconciliation → bounded warmup → continuous poll loop (lifecycle tracking + checkpoint + health-snapshot + conditional new-signal processing) → section-23 termination conditions. |
| `run_soak_live.py` | Operational entrypoint -- connects to the real terminal, verifies DEMO, runs `soak_loop.run_soak`. |

## 2. Position lifecycle states (extends `mt5_execution_ledger.py`, additive, backward-compatible)

`SUBMITTED_ACK` → `OPEN_CONFIRMED` (a matching live position found via `positions_get`) → `CLOSED` (the
tracked position ticket vanished from `positions_get` and a matching `entry=1`/OUT deal was found in
`history_deals_get`, via `position_id`). A vanished position with no yet-visible closing deal stays
`OPEN_CONFIRMED` -- never guessed closed (mandate section 15's "no blind retry" discipline extended to
position tracking too).

## 3. Deliberate scope boundary: no active horizon-based closing

S5's own `max_hold=48`-bar research parameter is **not** operationally enforced by this package --
`trade_lifecycle.py` never issues a closing `order_send` of any kind. The immediately-prior mandate
established "broker SL/TP executes the canonical strategy... it does not reinterpret" as the sole exit
mechanism; adding an active time-based close would be a materially new broker-mutating capability this
mandate's text asks for as *classification* (section 20), not as a new closing mechanism. A position
therefore remains open, protected by its own SL/TP, until the market hits one of them.
`past_horizon_still_open` is tracked in `HealthSnapshot` for visibility but never acted on. `HORIZON`
remains a valid exit-classification value (vocabulary completeness) but will not be produced by this
module's own logic.

## 4. Safety-stop conditions (mandate section 25)

`ACCOUNT_NOT_DEMO`, `STRATEGY_IDENTITY_MISMATCH`, `EVIDENCE_IDENTITY_MISMATCH`, `MISSING_PROBABILITY_
INPUTS`, `REAL_EV_FAILURE`, `BROKER_RECONCILIATION_AMBIGUITY`, `DUPLICATE_IDENTITY_CONFLICT`, `SL_
UNAVAILABLE`, `INVALID_SYMBOL_CONTRACT`, `RISK_CALCULATION_INVALID`, `RISK_EXCEEDS_5_PERCENT`,
`PERSISTENT_BROKER_API_CORRUPTION`, `LEDGER_CORRUPTION`. Any trip blocks new submissions but leaves
already-open positions alone (still protected by their own SL/TP). Reactive mapping from concrete
rejection reasons is `soak_loop._maybe_trip_from_reason`; `BROKER_RECONCILIATION_AMBIGUITY` also covers
the mandate's separately-named "duplicate identity conflict" concept (a multi-candidate reconciliation
match is the only mechanically-observable evidence of possible duplication this package currently has --
disclosed consolidation, not a silently-dropped condition).

## 5. Termination conditions (mandate section 23)

Checked every poll iteration, in order: **A** (≥20 closed trades AND ≥20 distinct UTC trading days
observed), **B** (≥`max_calendar_days`, default 60), **C** (safety monitor blocked), **D** (`should_stop()`
callback -- the hook a Scheduled Task's own stop mechanism, or a human, uses to end the soak early).

## 6. A real defect found and fixed via this mandate's own live smoke test

`copy_rates_from` returns a **numpy structured array** in production (unlike `positions_get`/
`orders_get`/`history_deals_get`, which return plain tuples) -- `array or []` raises `ValueError: The
truth value of an array with more than one element is ambiguous` for any multi-bar result. The initial
`soak_loop.py` poll-fetch used exactly this unsafe pattern; `live_runtime_loop.py`'s own (already-shipped,
already-correct) `is not None` pattern was NOT what this new file copied. A fake-gateway-only test suite
structurally cannot catch this (Python lists have no such truthiness ambiguity) -- only the live
smoke-test against the real terminal surfaced it. Fixed to the same `is not None` pattern; re-verified
clean against the real terminal afterward. See the full report for the before/after transcript.
