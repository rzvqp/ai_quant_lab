# Simulation Framework v1 — State Machine (design)

Two levels: (A) the **run lifecycle** (a single simulation run) and (B) the **per-bar cycle** (the sub-states of
one replayed bar). Design only — no code.

---

## A. Run lifecycle

| state | meaning |
|---|---|
| `UNINITIALIZED` | constructed, no context |
| `CONFIGURED` | `SimulationContext` validated + frozen; pipeline composed (with EXSIM/PSIM swap-ins) |
| `LOADING` | Strategy Manager loads the library; Replay Data Source / Scanner configured; Portfolio Simulator opened |
| `WARMUP` | replaying leading bars until scanner/feature warmup satisfied (NO trades; excluded from stats) |
| `RUNNING` | replaying the date range through the full pipeline; producing fills/positions/metrics |
| `PAUSED` | run halted mid-replay (state preserved; determinism intact on resume) |
| `COMPLETED` | reached `date_range.end`; positions closed/marked; `SimulationReport` finalized |
| `FAILED` | config/data/unrecoverable error; partial report + reason; determinism preserved up to the fault |
| `STOPPED` | terminal; ledger/logs persisted, no live state |

```
UNINITIALIZED → CONFIGURED → LOADING → WARMUP → RUNNING ⇄ PAUSED
                    │            │         │        │
                    └── fail ────┴─────────┴────────┼──▶ FAILED
                                                    │
                                          end-of-range / stop
                                                    ▼
                                                COMPLETED ──▶ (persist) ──▶ STOPPED
```
- `configure→load→warmup→running` is the normal path; any error before/within → `FAILED` (fail-fast at config/
  load; deterministic partial at run).
- `RUNNING↔PAUSED` preserves state; resume is deterministic.
- `COMPLETED`/`FAILED`/`STOPPED` are terminal for the run; a batch holds many independent runs.

### Transitions
| # | from | to | trigger | guard |
|---|---|---|---|---|
| R1 | UNINITIALIZED | CONFIGURED | `configure(context)` | context valid + module versions compatible |
| R2 | CONFIGURED | LOADING | `load()` | — |
| R3 | LOADING | WARMUP | library+data loaded | at least the data/scanner ready |
| R4 | WARMUP | RUNNING | warmup satisfied | scanner warmup complete for the required windows |
| R5 | RUNNING | PAUSED / RUNNING | `pause` / `resume` | — |
| R6 | RUNNING | COMPLETED | reached `date_range.end` or `stop` | positions closed/marked per policy; report finalized |
| R7 | any | FAILED | config/data/unrecoverable error | — |
| R8 | COMPLETED/FAILED | STOPPED | finalize + persist | — |

## B. Per-bar cycle (sub-states within RUNNING)
```
CLOCK_TICK → CONTEXT_BUILD (Scanner) → SIGNAL (Signal Engine) → SCORE (Scoring Engine) →
RISK (Risk Manager) → ORDER (Execution Engine) → FILL (Execution Simulator) →
ACCOUNT (Portfolio Simulator: apply fills + mark-to-market) → RECORD (Performance Analyzer) →
[ROLLUP at session/day/month boundary] → NEXT_BAR
```
- Each sub-state is the corresponding live module call; the cycle is deterministic and ordered.
- A per-bar issue (gap/insufficient context/no fill) resolves within its sub-state to a deterministic
  non-actionable outcome (NEED_CONTEXT / no order / order stays working) — the cycle always completes and advances.
- The MARGIN/insolvency check runs inside `ACCOUNT`; a breach raises a deterministic risk event and, per config,
  may drive the run to `COMPLETED`/`FAILED`.

## C. Determinism & fail-safe invariants
1. A run is a pure function of `(SimulationContext, historical data, module versions)`; re-running reproduces every
   state transition and the identical `SimulationReport`.
2. WARMUP bars never trade and are excluded from stats; the RUNNING phase alone defines performance.
3. Every per-bar cycle completes deterministically; no hidden randomness, no wall-clock; slippage is seeded.
4. Errors fail-fast (config/load) or produce a deterministic partial report (run); no run ends in an undefined
   state.
