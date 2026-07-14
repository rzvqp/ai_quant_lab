# Simulation Framework v1 — Operational Sequences (design)

How the simulator runs over time. Sequences only — no implementation, no broker. The per-bar loop IS the live
pipeline; only the Execution Simulator (broker) + Portfolio Simulator (account) are sim-specific. Actors:
`HARNESS`, `CLK`=Replay Clock, `DS`=Replay Data Source, `SCAN`=Market Scanner, `SM`=Strategy Manager, `SIG`=Signal
Engine, `SCO`=Scoring Engine, `RM`=Risk Manager, `EE`=Execution Engine, `EXSIM`=Execution Simulator, `PSIM`=
Portfolio Simulator, `PERF`=Performance Analyzer.

---

## 1. Startup / warmup
```
HARNESS.configure(SimulationContext) → freeze spec ; compose pipeline (EE→EXSIM as Broker Adapter ; PSIM as account)
HARNESS.load(): SM.load_library → aggregated required_context → DS/SCAN.configure ; PSIM.open(starting_balance)
state → WARMUP:
   for each warmup bar: CLK.tick(as_of) → DS feeds SCAN → MarketContext (sufficiency may be INSUFFICIENT)
   NO trades during warmup (excluded from stats)
warmup satisfied → state → RUNNING
```

## 2. The per-bar loop (the exact live pipeline)
```
CLK.tick → as_of
DS → SCAN.advance/ingest(as_of) → MarketContextBatch (per symbol, lookahead-safe)
SM.active_strategies() → handles
for each symbol:
   ctx = batch[symbol]
   SIG.evaluate(ctx, handles) → StrategySignal[]
   SCO.score_batch(signals) → OpportunityScore[] (ranked, deterministic)
   RiskContext ← assembled from ctx ; PortfolioState ← PSIM.state()
   RM.evaluate(scores, RiskContext, PortfolioState) → RiskDecision[] (ALLOW/DENY, rank order, running view)
   for each ALLOW: EE.execute(decision, PortfolioState) → OrderRequest → EXSIM (Broker Adapter contract)
EXSIM.match(orders, bars at/after as_of) → Fill/OrderStatus events (deterministic; spread/commission/slippage/partials)
PSIM.apply(fills) → update positions/balance ; PSIM.mark_to_market(bar close) → equity/floating PnL/drawdown/margin
PERF.record(trades, equity point, exposure, risk events)
(at session/day/month boundary) PERF.rollup()
```
Every module call is the SAME one live would make; the harness only supplies the clock, DS, EXSIM, PSIM, PERF.

## 3. Order filling across bars
```
market order @ as_of → EXSIM fills at NEXT bar open ± spread ± seeded slippage → FILLED → PSIM books position
limit/stop order → stays working across bars until price touches/triggers (deterministic) or TIF expires
bracket → parent fill activates OCO(stop,target); intrabar stop-before-target (engine-parity) → closing fill → PSIM realizes PnL
partial fill → PARTIALLY_FILLED + Fill(partial) → PSIM updates incrementally → remainder per TIF
```

## 4. Multi-symbol
```
DS streams all symbols on ONE clock → SCAN.MarketContextBatch{symbol→ctx}
pipeline runs per symbol (fixed symbol order) ; PSIM holds ONE account across all symbols (cross-symbol exposure/margin)
RM sees the shared PortfolioState → portfolio-level limits apply across symbols
```

## 5. Margin / insolvency event
```
PSIM.mark_to_market each bar → margin_level = equity/used_margin
margin_level < maintenance → MARGIN_CALL/LIQUIDATION (deterministic order): close positions, realize PnL, log risk event
config: halt run on liquidation, or continue with reduced equity
```

## 6. End of run / completion
```
at date_range.end (or stop): close_at_end_policy → close_at_last (close open positions at last bar) | hold_and_mark
PERF.finalize → SimulationReport (portfolio_summary, performance, attribution, allocation, risk_events, stats)
persist trade_history / execution_log / equity_curve per record config
state → COMPLETED ; report returned
```

## 7. Batch runs (thousands of simulations)
```
HARNESS.run_batch([ctx_1..ctx_N]):
   each run independent + fully reproducible from its (context + seed) → may run in parallel
   → one SimulationReport per run + optional batch summary (cross-run distributions: return/drawdown/PF)
   batch summary = descriptive statistics only (NO optimization, NO selection)
```

## 8. Determinism throughout
```
same SimulationContext + data + module versions ⇒ bit-identical fills, equity curve, trades, report
slippage seeded from hash(run_seed, client_order_id, as_of) ; no wall-clock ; fixed processing order
parallel batch runs never share state ; within a run, parallel per-strategy eval re-imposes deterministic order
```

## 9. Shutdown / failure
```
config/data error at configure/load → FAILED (fail-fast) before any bar
unrecoverable run error → FAILED with partial report + reason (determinism preserved up to failure)
HARNESS.shutdown → finalize/persist ; hold no live state → STOPPED
```

## 10. End-to-end (condensed)
```
configure(freeze) → load(compose + warmup) → RUNNING:
[per bar] CLK→DS→SCAN→SIG→SCO→RM→EE→EXSIM→PSIM→PERF (+ rollups) →
end-of-range → finalize SimulationReport → COMPLETED.
The ONLY live/sim difference: EXSIM↔Broker Adapter, PSIM↔real account. Everything else identical.
```
