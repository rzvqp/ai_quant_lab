# AI_TRADER_NEW_BRAIN_IMPLEMENTATION_REPORT

**Mandate**: `AI-TRADER-NEW-BRAIN-ARCHITECTURE-IMPLEMENTATION-001`
**Date**: 2026-08-21
**Branch**: `ai-trader-implementation`, remote `trader`
**Commits** (in order): `4b4c7b6` (console-window fix), `e469628` (legacy quarantine), `7963c4d` (N1 drift audit), `78bfeed` (N1 environment isolation), `91c9387` (strategy_platform core), `51989f8` (soak harness + architecture doc)

## 1. Files changed / added

**New package** `ai_trader/new_brain_live/strategy_platform/` (20 files): `__init__.py`, `trade_hypothesis.py`, `strategy_protocol.py`, `catalog.py`, `router.py`, `ev_engine.py`, `mock_strategies.py`, `risk_execution_adapter.py`, `shadow_ledger.py`, `dedup.py`, `pipeline.py`, `reason_codes.py`, `soak/{__init__,harness,run_soak_cli}.py`, `tests/{__init__,_fixtures,test_catalog,test_router,test_market_state_and_trade_hypothesis,test_pipeline,test_strategies_never_reach_broker,test_soak_harness}.py`.

**New**: `ai_trader/new_brain_live/market_state.py` (MarketState contract, no new class -- alias).

**New (environment isolation)**: `ai_trader/new_brain_bridge/no_console_window.py`, `.ai_trader_n1_venv` (a real, fresh Python venv on disk, not a repo file), `ai_trader/new_brain_live/n1_incremental/tests/test_environment_isolation.py`.

**Modified**: `ai_trader/new_brain_bridge/tower_launcher.py`, `ai_trader/new_brain_live/{singleton,watchdog,entrypoint}.py`, `ai_trader/new_brain_live/n1_incremental/{client,worker_script,runtime_loop,__init__}.py`, `ai_trader/new_brain_live/n1_incremental/tests/{test_incremental_integration,test_runtime_loop}.py` (console-window suppression + N1 environment rewiring), `ai_trader/mt5_demo_execution/{gating,reason_codes}.py` + `tests/{test_gating,test_legacy_quarantine_ast_guard(new)}.py`, `ai_trader/pdh_pdl_demo/__init__.py`, `ai_trader/multi_policy_live/__init__.py`, `ai_trader/pdh_pdl_demo/tests/test_orchestration.py`, `ai_trader/multi_policy_live/tests/test_orchestration.py`, `ai_trader/mandate2_readiness/tests/test_e2e_readiness.py` (legacy quarantine).

**New documents**: `N1_REPLAY_VERSION_DRIFT_AUDIT.md`, `AI_TRADER_NEW_BRAIN_ARCHITECTURE.md`, this file, `AI_TRADER_VALIDATED_STRATEGY_ONBOARDING_CONTRACT.md`.

## 2. Code paths

See `AI_TRADER_NEW_BRAIN_ARCHITECTURE.md` section 1 for the full pipeline diagram. In one line: `MarketState -> StrategyCatalog -> StrategyRouter -> Strategy.evaluate -> EVDecisionEngine -> risk_manager_live.evaluate_trade_proposal -> execution_shadow.attempt_shadow_execution -> ShadowLedger`, fail-closed at every stage, `BrokerOrderSubmissionGate.enabled=False` throughout.

## 3. Tests / counts / type checks

| Scope | Tests | Result |
|---|---|---|
| `strategy_platform/` (new) | 36 | all pass |
| `no_console_window.py` (new) | 7 | all pass |
| `n1_incremental/` (env isolation, new) | 9 | all pass |
| `mt5_demo_execution` + legacy quarantine (`pdh_pdl_demo`/`multi_policy_live`/`mandate2_readiness`) | 294 | all pass (1 pre-existing, unrelated failure noted separately in the legacy-quarantine commit, `mandate2_readiness` import-independence drift) |
| Broader regression: `new_brain_live/` + `new_brain_bridge/` + `risk_manager_live/` | 362 | all pass |

mypy `--strict`: clean on every touched/added file across all six commits (verified individually per commit, re-verified together in section 6 below).

## 4. E2E

`test_pipeline.py` exercises the full `market fixture -> N1/Router (real) -> MarketState -> StrategyRouter -> mock strategy -> TradeHypothesis -> EVDecisionEngine -> risk_manager_live (real) -> execution_shadow+BrokerOrderSubmissionGate (real, disabled) -> ShadowLedger` path end to end (section 38's own example), plus the companion `market fixture -> N1/Router -> no validated/eligible strategy -> NO_TRADE` path (empty catalog + ineligible-regime tests). Nothing in this chain is mocked except the Strategy layer itself (`MOCK_TEST_ONLY`, by design).

## 5. Soak result / procedure

Section 36's own required disclosure format. A 6-hour run was started (background OS process, `python -m ai_trader.new_brain_live.strategy_platform.soak.run_soak_cli --duration-seconds 21600`) at the time of this report's own delivery. **Its 6-hour completion had not yet elapsed when this report was written** -- the harness itself, its design rationale (component/integration soak, never live-MT5, never touching `AITraderLiveShadow`), and its short-run functional proof (3s/5s smoke runs, 0 exceptions, 0 `order_send`, ledger:cycle parity, N1 subprocess genuinely exercised and succeeding) are documented in `AI_TRADER_NEW_BRAIN_ARCHITECTURE.md` section 11 and `soak/harness.py`'s own docstring. The final report (`soak_report.json`, written to `new_brain_live_state/strategy_platform_soak/`) will be delivered as a follow-up once the real 6 hours complete -- **not fabricated here.**

## 6. Console/subprocess audit

Full findings and fix in commit `4b4c7b6`. Six production `subprocess.run`/`Popen` call sites across `new_brain_bridge`/`new_brain_live` carried zero Windows window-suppression flags; the highest-frequency one (`singleton.query_process_command_line`'s `powershell` call, invoked every watchdog tick) is the strongest candidate for the user-reported recurring transient CMD window. Fixed additively (`NO_CONSOLE_WINDOW_CREATIONFLAGS`, a single shared constant, `getattr(subprocess, "CREATE_NO_WINDOW", 0)`) at all six sites, proven by 7 new tests that capture the actual kwargs passed to `subprocess.run`/`Popen`, not just the source line. Zero behavior change beyond OS-level window visibility.

## 7. Known blockers (disclosed, not routed around)

1. **`ve_brain.decide_n6`'s sealed catalog** -- no real, ratified EV/decision authority exists for any strategy outside the 4 hardcoded ones (`INTEGRATION_BLOCKED_VE_BRAIN_STRATEGY_CATALOG.md`, 2026-08-18). `EVDecisionEngine` ships as a Protocol + `MockEVDecisionEngine` only; a real implementation is blocked pending a new `ve_brain` release or a separately-ratified decision-rule authority. Reported per section 15's own explicit instruction.
2. **`risk_gate.py`'s circuit-breaker check is opt-in**, not unconditionally enforced by that wrapper's own default (pre-existing, not introduced or fixed by this mandate; `strategy_platform` bypasses that wrapper entirely and calls `evaluate_trade_proposal` directly, so this gap does not affect the new pipeline, but is worth a future hardening pass on the legacy path).
3. **`mandate2_readiness` import-independence test failure** -- pre-existing architectural drift (many `new_brain_live`/`n1_replay` files import `mandate2_readiness` directly, violating that package's own "only `new_brain_bridge` may import this" test), unrelated to and not caused by this mandate, not investigated or fixed here (out of scope).
4. **The 6-hour soak's real-time completion** -- see section 5.

## 8. Compatibility decisions (section 40 migration table)

| Current component | New role | Decision |
|---|---|---|
| `new_brain_bridge` (`bridge.py`/`tower_client`/`tower_launcher`/`raw_axes_builder`) | Canonical N1-N6 chain | **PRESERVE**, unchanged |
| `ve_brain` 0.1.3 (sealed catalog) | EV/Decision authority for the 4 existing canonical strategies only | **PRESERVE**, unchanged; its sealed-catalog limit is exactly why a new EV layer exists for future strategies |
| `dual_clock.upstream_context.CachedUpstreamContext` | `MarketState` contract | **ADAPT** -- re-exported verbatim as `MarketState`, zero code change |
| `dual_clock.m5_decision_loop.M5DecisionLoop` | M15/M5 decision loop for the 4 canonical strategies | **PRESERVE**, unchanged; not wired to `strategy_platform` this mandate |
| `n1_incremental` (`worker_script`/`client`/`runtime_loop`) | N1 incremental hydration for the dual-clock path | **PRESERVE**, now environment-isolated (`.ai_trader_n1_venv`) |
| `risk_manager_live.evaluate_trade_proposal` | Risk Engine | **PRESERVE**, reused verbatim by `strategy_platform` |
| `execution_shadow` + `BrokerOrderSubmissionGate` | Execution Adapter | **PRESERVE**, reused verbatim |
| `live_shadow_journal.LiveShadowJournal` + `telemetry.NewBrainTelemetryLog` | Legacy-path shadow telemetry | **PRESERVE**, unchanged; `strategy_platform.shadow_ledger` is a separate, new, analogous mechanism for the new pipeline only |
| `execution_orchestrator` + Phase 1-10 chain (`context_engine`/`recognition_engine_live`/`confidence_engine`/`order_manager`) | Older, separate decision pipeline; `orchestrate()` refuses `LIVE` mode unconditionally, no live production caller found | **PRESERVE for audit**; flagged as a candidate for a future CEO retirement decision, not touched this mandate |
| `pdh_pdl_demo` (CAND-0001) / `multi_policy_live` (CAND-0007/CAND-0019) | Independent legacy recognition->risk->order paths | **PRESERVE / QUARANTINE** -- `LEGACY_NON_AUTHORITY`, commit `e469628` |
| `mt5_demo_execution.gating.send_after_dry_run_gate` | Legacy demo-order gate | **PRESERVE / QUARANTINED** -- `LEGACY_TRADING_AUTHORITY_QUARANTINED = True`, commit `e469628` |
| `structural_observer` + `live_observation`/`zone_observer`/`spread_collection` | N1 input (`structural_observer`) / pure record-only observers | **PRESERVE**, unchanged; confirmed no decision authority |
| `singleton.py`/`watchdog.py`/`heartbeat.py` | Process/restart safety infra | **PRESERVE**, extended (console-window suppression only) |
| `strategy_platform/*` | Generic Strategy Catalog/Router/EV/Risk/Execution/Shadow-Ledger pipeline | **NEW**, purely additive |

## 9. Rollback

Every commit in this mandate is **purely additive or defense-in-depth** with one deliberate exception:

- `strategy_platform/` + `market_state.py`: zero risk to revert -- nothing in the existing, running codebase imports or calls into this package; `git revert`/checkout removes it with no other effect.
- Console-window fix (`4b4c7b6`): zero trading-semantic risk either direction; reverting only restores the prior (window-flashing) behavior.
- N1 environment isolation (`78bfeed`): **not recommended to revert** -- reverting would point AI Trader's N1 client back at the shared/`.alpha_n1_venv`-adjacent state that caused the original drift incident, immediately reintroducing the exact blocker `N1_REPLAY_VERSION_DRIFT_AUDIT.md` documents. Forward-only in practice.
- **Legacy quarantine (`e469628`) must NEVER be reverted without a fresh, explicit CEO decision** -- reverting it would silently re-enable real `order_send` capability in `pdh_pdl_demo`/`multi_policy_live` via `send_after_dry_run_gate`. This is the one commit in this mandate where "rollback" and "safety" point in opposite directions; treat it as a one-way gate, not a checkpoint.

`AITraderLiveShadow` (the actual running LIVE_SHADOW process, HEAD `255eee6`, far behind every commit in this mandate) is unaffected by any of this work regardless of rollback decisions -- it does not import `strategy_platform`, was never restarted, and its own runtime behavior is unchanged.

## 10. Broker-disabled proof

- `BrokerOrderSubmissionGate.enabled: bool = False` by construction (`mandate2_readiness/broker_gate.py:57`), AST-guard-proven unreachable to flip via any code path in `new_brain_live`.
- `strategy_platform.risk_execution_adapter.evaluate_and_attempt` calls `attempt_shadow_execution(risk_decision, gate=deps.gate)` -- the SAME, unmodified, default-disabled gate.
- `pipeline.run_cycle`'s `final_decision` is structurally always `"NO_TRADE"` in this delivery (see architecture doc section 12) -- proven by every positive-path test in `test_pipeline.py` asserting exactly that.
- The soak harness's own `order_send_calls_total` field, tracked across every cycle, is asserted `== 0`.
- `mt5_demo_execution`'s separate, legacy order-submission path is independently hard-quarantined (`LEGACY_TRADING_AUTHORITY_QUARANTINED = True`), proven by 3 dedicated tests plus a source-level AST guard.

## 11. Final status

`AI_TRADER_NEW_BRAIN_ARCHITECTURE_IMPLEMENTED`, `STRATEGY_PLUGIN_FRAMEWORK_READY`, `STRATEGY_CATALOG_FRAMEWORK_READY`, `LIVE_SHADOW_BROKER_DISABLED_READY`, `READY_FOR_FUTURE_VALIDATED_STRATEGY_ONBOARDING`. **Not** `VALIDATED_STRATEGIES_INSTALLED` -- 0 VALIDATED strategies shipped, deliberately, per section 45's own explicit acceptance of that count.
