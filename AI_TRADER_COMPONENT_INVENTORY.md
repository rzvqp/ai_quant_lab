# AI Trader — Component Inventory

**Last updated**: 2026-07-25. **Scope**: every component actually reachable from the live AI Trader
decision chain (Phases 1-10) plus the components it directly reuses. The older batch/research pipeline
(`scoring_engine`'s scoring logic, `strategy_manager`, `strategy_health`, `decision_intelligence*`,
`simulation`, `portfolio_architect`, `shadow_evidence`, `learning_feedback`) is **out of scope here** —
`AI_TRADER_KNOWLEDGE_TRANSFER_AUDIT.md` §3 already establishes precisely which of those the live chain
does and does not touch, and it is documented in the older `PROJECT_STATE_v2.md`/`PROJECT_AUDIT.md`
family, not duplicated here.

---

### `execution_engine/adapters/mt5_gateway.py` — `RealMT5Gateway`
- **Responsibility**: sole `import MetaTrader5` entry point in the whole repo; thin, direct passthrough
  to the MT5 Python API (`account_info`, `symbol_info`, `positions_get`, `orders_get`, etc.).
- **In**: MT5 terminal connection (local, CDP-less — MT5's own Python API talks to the running terminal).
- **Out**: raw MT5 native objects/namedtuples, unwrapped.
- **Depends on**: `MetaTrader5` package only.
- **Tests**: `execution_engine/adapters/tests/test_mt5_gateway.py` + real-terminal gated test.
- **Status**: IMPLEMENTED, TESTED, VALIDATED (real terminal).

### `execution_engine/adapters/mt5_adapter.py` — `MT5ReadOnlyBrokerAdapter`
- **Responsibility**: DEMO/server verification, `AccountTradeMode`/`AlgoTradingStatus` classification,
  `symbol_capabilities()` (tick_size/lot_step/min/max_qty/digits/spread/trade_mode/description).
- **In**: `RealMT5Gateway` (or a fake in tests).
- **Out**: `MT5AdapterStatus`, `MT5SymbolCapabilities`.
- **Depends on**: `execution_engine.adapters.mt5_gateway`, `execution_engine.broker_adapter` (base class).
- **Tests**: `execution_engine/adapters/tests/test_mt5_adapter.py`.
- **Status**: IMPLEMENTED, TESTED, VALIDATED (real terminal, read-only ops).

### `risk_manager/sizing.py` — `compute_sizing`
- **Responsibility**: the actual position-sizing formula — `risk_budget_currency = risk_per_trade_pct *
  portfolio.equity`; `size_units = risk_budget_currency / (stop_distance * point_value)`, clamped by
  notional/min-allocation caps. Pre-existing, frozen, reused unmodified by `risk_manager_live`.
- **In**: `OpportunityScore` (synthetic adapter), `PortfolioState`, `RiskConfig`.
- **Out**: `Sizing` (method, size_units, size_lots, risk_budget_currency, stop_distance, etc.).
- **Depends on**: `risk_manager.types`, `risk_manager.config`.
- **Tests**: `risk_manager/tests/test_sizing.py` (pre-existing suite).
- **Status**: IMPLEMENTED, TESTED. Not itself independently re-validated this session (unchanged).

### `risk_manager_live/engine.py` — `evaluate_trade_proposal` (Phase 2)
- **Responsibility**: live risk gate — stop-distance/point-value/equity sanity check, runs frozen
  `risk_manager` guards/limits/filters, calls `compute_sizing`, converts to broker lots
  (`InstrumentSpecification.contract_size`/`lot_step`), checks free margin.
- **In**: `TradeProposal`, `AccountState`, `PortfolioState`, `InstrumentSpecification`, `RiskContext`,
  `RiskConfig`.
- **Out**: `LiveRiskDecision` (approved, calculated_volume, monetary_risk, stop_distance, margin_estimate,
  calculation_trace, reason_codes).
- **Depends on**: `risk_manager.sizing`, `risk_manager.types`, `risk_manager.config`.
- **Tests**: `risk_manager_live/tests/` (37 tests).
- **Status**: IMPLEMENTED, TESTED (fixture-driven only — no live `AccountState`/`InstrumentSpecification`
  source exists yet, see `AI_TRADER_PROJECT_STATE.md` §8).

### `order_manager/engine.py` — `process_approved_intent` (Phase 3)
- **Responsibility**: builds and submits the broker order for an already risk-approved, already-sized
  `ApprovedTradeIntent`; reuses `execution_engine.pipeline.submit_built_order` (validate + dup-guard +
  submit + track).
- **In**: `ApprovedTradeIntent`, a `BrokerAdapter` (Dry-run or real).
- **Out**: `OrderExecutionResult` (dry_run flag now reflects the adapter used, not hardcoded).
- **Depends on**: `execution_engine.pipeline/validator/ledger/types`, `order_manager.builder/journal`.
- **Tests**: `order_manager/tests/` (43 tests).
- **Status**: IMPLEMENTED, TESTED, VALIDATED (BTCUSD real send).

### `order_manager/builder.py` — `build_order_request`
- **Responsibility**: price normalization only (rounds entry/stop/target to `instrument.tick_size`);
  volume arrives pre-sized/pre-rounded from `risk_manager_live`, passed through unchanged.
- **In**: `ApprovedTradeIntent`, `InstrumentSpecification`.
- **Out**: `execution_engine.types.OrderRequest`.
- **Status**: IMPLEMENTED, TESTED.

### `portfolio_manager_live/` — `evaluate_portfolio_authorization` (Phase 4)
- **Responsibility**: exposure/heat aggregation across already-sized positions (by symbol/direction/
  strategy/asset-class), long/short conflict detection (reuses `RiskConfig.correlation_group_for`).
- **In**: `PortfolioAuthorizationRequest` (carries `approved_risk_pct`/`monetary_risk` from
  `LiveRiskDecision`), `PortfolioDailyState`.
- **Out**: `PortfolioDecision`, `ExposureSnapshot`.
- **Depends on**: `risk_manager.config` (correlation groups) only — no equity/sizing math of its own.
- **Tests**: `portfolio_manager_live/tests/` (37 tests).
- **Status**: IMPLEMENTED, TESTED.

### `telegram_notifier/` — `notify` / `notify_fire_and_forget` (Phase 5)
- **Responsibility**: best-effort outcome notification. Zero trading-domain dependency (verified by its
  own strictest-in-repo import-independence test).
- **In**: `NotificationEvent` (plain strings + flat string map).
- **Out**: none (fire-and-forget) / delivery result.
- **Depends on**: stdlib `urllib.request` only. Credentials via `TELEGRAM_BOT_TOKEN`/
  `TELEGRAM_CHAT_ID_PRIMARY`/`_SECONDARY` env vars (`credentials.py`).
- **Tests**: `telegram_notifier/tests/` (34 tests).
- **Status**: IMPLEMENTED, TESTED. Not operationally validated against a real Telegram bot this session.

### `context_engine/engine.py` — `build_context_snapshot` (Phase 6)
- **Responsibility**: thin wrapper combining `market_intelligence.build_market_intelligence` +
  `edge_intelligence.evaluate_edges`, unmodified, into one `MarketContextSnapshot`.
- **In**: raw OHLCV/market data (via `market_scanner`), symbol/strategy contracts.
- **Out**: `MarketContextSnapshot` (`market_intelligence`, `edge_intelligence`, `Provenance`).
- **Depends on**: `market_intelligence.engine`, `edge_intelligence.engine`.
- **Tests**: `context_engine/tests/` (19 tests).
- **Status**: IMPLEMENTED, TESTED. `edge_intelligence` output is computed here but never consumed
  downstream (see `edge_intelligence` entry below and `AI_TRADER_KNOWLEDGE_TRANSFER_AUDIT.md` §3.2).

### `market_intelligence/` — `build_market_intelligence` (pre-existing, reused unmodified)
- **Responsibility**: trend/momentum/volatility/liquidity/expansion/session-behavior analyzers +
  structure (swing/BOS/CHoCH) + agreement/confidence combination.
- **Out**: `ContextConfidence` (consumed directly by `confidence_engine`, unmodified).
- **Status**: IMPLEMENTED, TESTED (pre-existing suite). Live-wired via `context_engine`.

### `edge_intelligence/` — `evaluate_edges`, `contracts.load_strategy_contracts` (pre-existing, reused)
- **Responsibility**: per-strategy real-time `EdgeState` (PRESENT/POSSIBLE/ABSENT) gate from live evidence
  (data availability, directional alignment, session suitability, context confidence, MTF agreement,
  volatility regime). **Not** a lookup into the Research-Lab Edge Discovery Registry (E001-E040) despite
  the shared name — see `AI_TRADER_KNOWLEDGE_TRANSFER_AUDIT.md` §3.2 for the full, code-verified
  distinction.
- **In**: `contracts.py` loads the real 51-file `knowledge/strategies/*.json` Strategy Library via
  `strategy_manager.loader.load_all` — reads `execution`/`semantics.required_data` fields only; the
  `evidence` block (matched-null/global-FDR/walk-forward/holdout status) is parsed but never read by
  `verdict.py`'s `determine_edge_state`.
- **Out**: `EdgeIntelligenceSnapshot` — attached to `MarketContextSnapshot.edge_intelligence`, then never
  read by any downstream live package (`confidence_engine`, `risk_manager_live`, etc.) — confirmed by
  repo-wide grep, zero hits outside tests.
- **Status**: IMPLEMENTED, TESTED, but functionally a dead-end in the live chain — output computed, never
  consumed.

### `recognition_engine_live/` — `recognize` (Phase 7)
- **Responsibility**: `AUTHORIZED_PATTERNS` catalog (`patterns.py`) — 15 entries, one per
  `ContextDimension` (SESSION, TREND×4 timeframes, STRUCTURE_STATE, MOMENTUM×4, VOLATILITY_REGIME,
  LIQUIDITY_STATE, EXPANSION_STATE, MULTI_TIMEFRAME_AGREEMENT, DATA_QUALITY_STATE), IDs literally
  `f"REC-{dimension.value}-STRATEGY"`. Buckets market context and queries `ContextMemoryRepository` for
  conditional statistics keyed by `(strategy_id, dimension)`.
- **In**: `RecognitionCandidate` (`strategy_id`, `pattern_id`, `as_of`, `correlation_id` — `strategy_id`
  is free-form, **not validated against any registry**), `MarketContextSnapshot`.
- **Out**: `RecognitionResult` (context_bucket_value, statistics, sufficiency, pattern_authorized,
  reason_codes, calculation_trace). **No field for an edge ID / source-experiment reference exists.**
- **Depends on**: `recognition_engine._bucket_value` (private, reused for bucketing consistency with the
  batch engine), `context_memory`.
- **Tests**: `recognition_engine_live/tests/` (23 tests).
- **Status**: IMPLEMENTED, TESTED. No Research-Lab edge-specific structure/logic exists here — generic
  dimension-bucket machinery only.

### `context_memory/` — `ContextMemoryRepository` (Phase 8, pre-existing package extended)
- **Responsibility**: append-only context/observation/outcome repository, episode collapsing, deterministic
  retrieval, contextual evidence aggregation.
- **Status**: IMPLEMENTED, TESTED (own Checkpoint history, pre-existing before Phases 2-10).

### `confidence_engine/engine.py` — `assess_confidence` (Phase 8)
- **Responsibility**: `Grade` (A-D) from exactly two components — `context_confidence_component` (from
  `market_intelligence.ContextConfidence.score`) and `recognition_component` (from
  `RecognitionResult.statistics.favorable_rate` when sufficient, else 0.0). `strategy_health_component` is
  a permanent, explicitly disclosed `None` placeholder.
- **In**: `MarketContextSnapshot`, `RecognitionResult`.
- **Out**: `ConfidenceAssessment` (grade, quality, score_components, eligible_for_risk_evaluation —
  structurally impossible to be `True` for grades C/D).
- **Depends on**: `scoring_engine.types.Quality` (bare enum reuse only, zero scoring logic).
- **Tests**: `confidence_engine/tests/` (23 tests).
- **Status**: IMPLEMENTED, TESTED. No p-value, Red Team verdict, or holdout/global-FDR status is read
  anywhere in this component.

### `execution_orchestrator/engine.py` — `orchestrate` (Phase 9)
- **Responsibility**: pure sequencing/bridging — calls every engine above, unmodified, in order. `LIVE`
  mode refused unconditionally, first.
- **In**: `CandidateSignal` (strategy_id, symbol, direction, entry, stop, target, session, magic_number,
  comment, as_of) — **constructed nowhere in production code, only in
  `execution_orchestrator/tests/_fixtures.py:31`**.
- **Out**: `OrchestrationResult`.
- **Depends on**: every Phase 2-8 engine + `order_manager` + a `BrokerAdapter`.
- **Tests**: `execution_orchestrator/tests/` (18 tests, including one full end-to-end integration test).
- **Status**: IMPLEMENTED, TESTED, structurally dormant — no live signal source exists to invoke it in
  production (`AI_TRADER_PROJECT_STATE.md` §7).

### `mt5_demo_execution/` — `send_after_dry_run_gate`, `MT5DemoBrokerAdapter`, `build_mt5_request` (Phase 10)
- **`gating.py::send_after_dry_run_gate`**: runs DRY_RUN leg first (separate ledger/journal); only
  proceeds to DEMO leg (separate ledger/journal) if approved AND `ACKNOWLEDGED`.
- **`adapter.py::MT5DemoBrokerAdapter(MT5ReadOnlyBrokerAdapter)`**: subclass adding `submit_order`
  (re-verifies AlgoTrading + DEMO + volume ceiling on every call, `order_check` before `order_send`),
  `capabilities`, `query_status`, `query_open_orders`. No `cancel_order` (disclosed).
- **`request_builder.py::build_mt5_request`**: pure, deterministic dict builder;
  `_COMMENT_MAX_LENGTH = 27` (conservative, broker-specific, disclosed — §6 of `AI_TRADER_PROJECT_STATE.md`).
- **`safety.py::verify_safety_guards`/`is_market_open_for_symbol`**: tick-recency market-open heuristic;
  `SafetyGuardReport.all_passed` fails closed on `market_open is not True` (including `None`).
- **`types.py::MT5DemoConfig`**: `max_order_volume=0.01` (hard ceiling, currently in tension with any
  future dynamic-sizing feature — see `RISK_SIZING_5PCT_XAUUSD_DESIGN.md` §4).
- **Tests**: `mt5_demo_execution/tests/` (42 unit + 1 gated real-terminal).
- **Status**: IMPLEMENTED, TESTED, VALIDATED (BTCUSD real send, once, manually).
