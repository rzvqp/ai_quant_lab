"""AI Trader's generic strategy plugin/decision platform (AI Trader New Brain Architecture mandate,
AI-TRADER-NEW-BRAIN-ARCHITECTURE-IMPLEMENTATION-001, 2026-08-21).

MARKET DATA -> canonical N1-N6 (`new_brain_bridge`/`ve_brain`, UNCHANGED) -> `MarketState`
(`new_brain_live.market_state`) -> `StrategyCatalog` -> `StrategyRouter` -> `Strategy.evaluate` ->
`EVDecisionEngine` -> Risk Engine (`risk_manager_live`, UNCHANGED) -> Execution Adapter
(`new_brain_bridge.execution_shadow`, UNCHANGED) -> `ShadowLedger`.

Status at delivery: `STRATEGY_PLUGIN_FRAMEWORK_READY`, `STRATEGY_CATALOG_FRAMEWORK_READY`. Zero
VALIDATED strategies shipped (deliberate -- see `catalog.EMPTY_CATALOG` and section 10); five
`MOCK_TEST_ONLY` strategies (`mock_strategies.py`) exist solely to exercise the pipeline end to end.
`BROKER_ORDER_SUBMISSION` remains globally DISABLED -- `pipeline.run_cycle`'s `final_decision` is
structurally always `"NO_TRADE"` in this delivery (see `pipeline.py`'s own docstring). No canonical
N1-N6 code was retuned, redesigned, or duplicated; no real Alpha strategy was promoted or integrated.

See `AI_TRADER_NEW_BRAIN_ARCHITECTURE.md` (repo root) for the full design, `AI_TRADER_NEW_BRAIN_
IMPLEMENTATION_REPORT.md` for what was actually built/tested, and `AI_TRADER_VALIDATED_STRATEGY_
ONBOARDING_CONTRACT.md` for what a future validated strategy must hand this platform to become a
plug-in."""
