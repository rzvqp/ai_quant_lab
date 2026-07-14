# Strategy Manager v1 — Operational Sequences (design)

How the Strategy Manager behaves over time. Sequences only — no implementation. Actors: `ORCH`=AI Trader
orchestrator, `SM`=Strategy Manager, `LOADER`/`COMPAT`/`REG`/`LIFE`/`AGG`/`HEALTH`=internal components,
`LIB`=Strategy Library (read-only), `SCAN`=Market Scanner, `SIGENG`=Signal Engine, `LEARN`=Learning Engine.

---

## 1. Startup / `load_library()`
```
ORCH → SM.configure(library_path, supported {interface_major, runtime_major, feature_dict_major}, admission_policy)
SM → SCAN.get_provided_features(), SCAN.versions()          # handshake for MarketContext compatibility
SM.load_library():
  LOADER.discover(LIB) → files[] (sorted by id)
  for each file:
     parse JSON ── fail → REG.upsert(CORRUPTED); continue
     schema-validate vs strategy_contract.v1.schema.json ── fail → REG.upsert(INVALID, reasons); continue
     COMPAT.check(contract, scanner_features) → {interface_ok, runtime_ok, context_ok, deprecated[]}
        incompatible → REG.upsert(INCOMPATIBLE); continue
     duplicate id? → reject later copy (DUPLICATE), keep first
     REG.upsert(ValidatedContract)
     LIFE.initial_state(contract) → {NOT_IMPLEMENTED | EXPERIMENTAL | …}
  REG.build_indices()  (by_id / by_lifecycle / by_health / by_symbol / by_required_field / active)
  LIFE.apply_admission_policy() → ACTIVE set (EXPLORATORY+ admitted)
  AGG.recompute() → AggregatedContext
SM → SCAN.register_requirements(AggregatedContext)          # the Manager tells the scanner what to produce
HEALTH.publish()  →  SM READY   (active_strategies() available to SIGENG)
ORCH ← LoadReport
```
Best-effort: one bad contract never aborts the others. If nothing valid loads, SM is READY with an empty active
set (no signals produced — a valid, safe state).

## 2. Normal operation (per heartbeat) — the Manager's role
```
SCAN.scan(as_of) → MarketContextBatch          # scanner produces context from SM's requirements
SIGENG → SM.active_strategies() → StrategyHandle[]
SIGENG: for each handle, evaluate against the symbol's MarketContext (calls the Strategy API)
# The Strategy Manager itself does nothing per-tick beyond serving active_strategies() and health();
# it does not evaluate strategies, score, or trade.
HEALTH ⟲ marks STALE if a contract's last_review ages or a newer Library release is detected (until reload)
```

## 3. Reload (Library changed / operator request)
```
ORCH or LEARN → SM.reload(id?)
SM: recompute content_hash per contract; unchanged → skip
    changed/new → parse → schema → COMPAT → LIFE.transition:
        maturity raised (new version) → gate-check (T7 needs matched-null+walk-forward PASS; T8 adds global-FDR+holdout)
             gate satisfied → reflect higher tier ; gate NOT satisfied → hold at highest supportable + health warning
        maturity lowered / now invalid → downgrade / INVALID (remove from active)
    if the ACTIVE set changed → AGG.recompute() → SCAN.register_requirements(new spec)
ORCH ← LoadReport(changed)
```

## 4. Activation / deactivation (context re-aggregation)
```
ORCH/operator/LEARN → SM.activate(id)
SM: guard (compatible ∧ activatable lifecycle ∧ admission policy) ── fail → LifecycleResult{ok=false, reason}
    LIFE.transition EXPERIMENTAL→EXPLORATORY (T4)  (or enable DISABLED→prior, T11)
    REG.indices.active += id
    AGG.recompute() → SCAN.register_requirements(new spec)
ORCH ← LifecycleResult{ok=true, from, to}
# deactivate/disable/retire mirror this and also trigger AGG.recompute() + register_requirements()
```

## 5. Context aggregation (detail)
```
AGG.recompute():
  active = REG.indices.active
  timeframes = ⋃ strat.required_context.timeframes
  for tf: required_fields[tf] = ⋃ strat.fields[tf](required) ;  optional_fields[tf] = ⋃ strat.fields[tf](optional)
          lookback[tf] = max strat.lookback[tf]
  symbols = ⋃ strat.symbols ;  warmup = max strat.warmup
  feature_dict_major = the single supported MAJOR
      conflict (an active strat needs a different feature-dict MAJOR) →
          deactivate the lower-priority/lower-maturity strat (INCOMPATIBLE) ; record in report ; retry
  → AggregatedContext { timeframes, required/optional fields, lookback, symbols, feature_dict_major,
                        interface_version, contributor_ids }
SM → SCAN.register_requirements(AggregatedContext)
```

## 6. Failure handling (fail-safe)
```
invalid JSON            → CORRUPTED   (quarantine; error record)          never active
schema/required-field   → INVALID     (offending path reported)           never active
unsupported version     → INCOMPATIBLE (unsupported version reported)      never active
duplicate id            → DUPLICATE   (later copy rejected; first wins)    first may be active
MarketContext field/tf  → INCOMPATIBLE (missing_field/missing_timeframe)   never active
missing dependency      → MISSING_DEPENDENCY                               not activatable until resolved
unknown id on lookup    → NotFound (typed)                                 no crash
scanner handshake fails → load with degraded compatibility info; strategies needing unknown features quarantined
```
Invariant: the resting state of anything abnormal is **NOT in the active set**; a malformed/incompatible contract
can never reach the Signal Engine or cause a trade.

## 7. Shutdown
```
ORCH → SM.shutdown()
SM: stop accepting reload/activation requests
    LIFE.deactivate_all()  → REG.indices.active = ∅   (SIGENG stops receiving handles)
    AGG.recompute() (empty) → SCAN.register_requirements(empty)   # scanner left in a defined state
    HEALTH.publish(final) ; statistics() emitted ; optional registry snapshot flushed
    release resources
```

## 8. End-to-end (condensed)
```
configure → handshake SCAN → load_library (discover→parse→schema→compat→register→lifecycle) →
apply admission → aggregate context → register_requirements(SCAN) → READY →
[per heartbeat] SIGENG pulls active_strategies(); SM serves handles + health only →
reload/activate/deactivate → re-aggregate → re-register → … → shutdown (deactivate all, empty spec).
```
Throughout, the Strategy Manager: reads only contracts (never research), produces the scanner spec and the active
handles, maintains lifecycle/health — and makes **no** trading decision.
