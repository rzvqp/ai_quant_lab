# Risk Manager v1 — Operational Sequences (design)

How the Risk Manager behaves over time. Sequences only — no implementation. Actors: `ORCH`=orchestrator,
`SC`=Scoring Engine, `PM`=Portfolio Manager, `RM`=Risk Manager, `EX`=Execution Engine.

---

## 1. Startup
```
ORCH → RM.configure(RiskConfig, supported {scoring_schema_major, risk_schema_major, interface_major})
RM → SC.versions() ; RM → EX handshake (risk_schema major) ; RM → PM (PortfolioState availability)
RM reconcile initial risk_state from PM.PortfolioState:
     daily/weekly loss or drawdown already breached → SUSPENDED ; kill switch on → EMERGENCY_STOP ; else READY
RM: IDLE → READY (or SUSPENDED/EMERGENCY_STOP)
```

## 2. Single trade (READY)
```
SC → RM.evaluate([OpportunityScore], RiskContext, PortfolioState):
   Global State = READY
   opportunity: sanity → floor/min-score → pre-trade filters → portfolio limits → loss/drawdown guards → cooldowns
        all pass → ALLOW → position_size → constraints → RiskDecision(ALLOW, sizing, constraints)
RM → EX.submit(RiskDecision ALLOW)     # EX executes; RM does NOT
```

## 3. Multiple signals (ranked batch, running portfolio view)
```
SC → RM.evaluate([opp1(rank1), opp2(rank2), opp3(rank3)], RiskContext, PortfolioState)
RM processes in rank order against a RUNNING portfolio view:
   opp1 → ALLOW (consumes a position slot + risk budget) → running view updated
   opp2 → limits re-checked against the UPDATED view → ALLOW or DENY(LIMIT_*)
   opp3 → e.g. now at LIMIT_MAX_POSITIONS → DENY(LIMIT_MAX_POSITIONS)
RM → EX (allowed decisions) ; caller (denied, with reasons)
```
Deterministic because the order is the Scoring Engine's fixed rank and the running view is applied in that order.

## 4. Portfolio full
```
PortfolioState already at LIMIT_MAX_POSITIONS (or LIMIT_MAX_EXPOSURE):
   every new opportunity → DENY(LIMIT_MAX_POSITIONS / LIMIT_MAX_EXPOSURE)
existing positions are unaffected (RM manages new entries only; stops/exits are honored by EX)
```

## 5. Daily stop hit
```
during evaluate(): Loss/Drawdown Guard detects daily loss ≤ −3% equity
   → current opportunity DENY(LOSS_DAILY)
   → global state READY → SUSPENDED (transition G5)
   → all subsequent evaluate() this day → all DENY(SUSPENDED) until recovery (G6 at day boundary if within limits)
RM.health() reports SUSPENDED ; PM/Performance Monitor notified
```

## 6. Kill switch / emergency
```
operator/monitor → RM.emergency_stop("kill switch")   (or max-drawdown breach detected)
   → global state → EMERGENCY_STOP (G7)
   → every evaluate() → all DENY(KILL_SWITCH / EMERGENCY_STOP)
   → RM MAY emit an emergency instruction to EX to flatten per policy (EX performs the closes; RM only decides)
```

## 7. Recovery
```
from SUSPENDED (loss): auto @ next day/week boundary IF drawdown within limits → READY (G6); optional reduced-size ramp
from SUSPENDED (drawdown) / EMERGENCY_STOP: operator → RM.resume()/clear_emergency()
   guard: PortfolioState reconciled AND no guard tripped AND (drawdown < reset threshold) → READY (G6/G8)
   else remains SUSPENDED/EMERGENCY_STOP (fail-safe)
```

## 8. Degraded dependency
```
PM.PortfolioState unavailable/stale at evaluate():
   → all DENY(PORTFOLIO_UNAVAILABLE) ; engine health = DEGRADED (READY overlay)
   → recovers to normal DENY/ALLOW evaluation once PortfolioState is fresh again
RiskContext data_quality = STALE/INSUFFICIENT: pre-trade filters treat worst-case → typically DENY(DATA_DEGRADED)
```

## 9. Shutdown
```
ORCH → RM.shutdown()
RM: stop accepting evaluations ; finish/deny in-flight batch ; emit final statistics()/health()
    release snapshots (RM holds no truth of fills) → SHUTDOWN
```

## 10. End-to-end (condensed)
```
configure → reconcile state → READY →
[per batch] SC.OpportunityScore[] + RiskContext + PortfolioState → global gate → per opp (rank order):
   filters → limits → guards → cooldowns → ALLOW(size+constraints) | DENY(reasons) → running view update →
   EX.submit(ALLOW) / caller(DENY) → …
guards may escalate → SUSPENDED/EMERGENCY_STOP (all DENY) → recovery → … → shutdown.
```
Throughout, the Risk Manager: reads opportunities + portfolio + passed-in risk context (never research, never the
broker), decides ALLOW/DENY + sizing deterministically, defaults to DENY under any uncertainty, and never signals,
scores, executes, or learns.
