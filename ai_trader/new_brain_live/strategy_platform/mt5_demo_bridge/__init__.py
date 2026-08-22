"""S5 MT5 DEMO-ONLY execution bridge (mandate `AI-TRADER-S5-MT5-DEMO-EXECUTION-001`).

Connects the existing, unmodified canonical S5 pipeline (`strategy_platform.pipeline.run_cycle` with a
`RealEVDecisionEngine`) to real MetaTrader 5 DEMO-account order submission, reusing the already-built,
already-tested `ai_trader.mt5_demo_execution`/`ai_trader.execution_engine.adapters.mt5_adapter`
primitives (`MT5DemoBrokerAdapter`, `verify_safety_guards`, `build_mt5_request`) rather than
reimplementing MT5 connectivity from scratch. New here: contract-aware 5%-equity risk sizing, S5-specific
deterministic order identity, a persisted execution ledger, restart reconciliation, and the incremental
live runtime loop -- see `AI_TRADER_S5_MT5_DEMO_EXECUTION_REPORT.md` for the full design/safety
rationale."""
