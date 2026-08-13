# AI Trader — Mandate 2 Preparation: Runtime Inventory

**Scope**: what exists TODAY, traced through actual code, not assumed. No artifact received, none
integrated. This document describes the current pre-Mandate-2 architecture only — it changes nothing.

## 1. Full path from feed to Risk Manager

Both live entrypoints (`pdh_pdl_demo`, `multi_policy_live`) share an identical downstream pipeline from
`LiveBarFeed.poll()` through the Risk Manager. Only the top layer (recognition rule → orchestrator
instance) differs by policy.

1. `LiveBarFeed.poll()` (`live_signal_source/bar_feed.py:468`) — newly closed bars only.
2. **Loop-level circuit-breaker gate**, before any bar is evaluated: `load_persisted_circuit_state`
   (`risk_manager_live/circuit_breaker.py:129`). `pdh_pdl_demo` reads its own state file;
   `multi_policy_live` reads CAND-0001's state file fresh every tick — one genuinely shared, account-wide
   breaker across all 4 policies. Default (nothing ever persisted) is `READY` — confirmed empirically:
   no `risk_manager_live.circuit_breaker` log entries exist in the live state store, so the gate is open
   by default, not by an explicit approval record.
3. **Recognition**: `rule.evaluate(bar)` → `LiveCandidate | None` + `rule.last_trigger()` →
   `PdhPdlTrigger`.
4. **Submission**: `orchestrator.submit_candidate(candidate, trigger, market_context)` —
   `PdhPdlOrchestrator.submit_candidate` (`pdh_pdl_demo/orchestration.py:101`) or `PolicyOrchestrator
   .submit_candidate` (`multi_policy_live/orchestration.py:115`, one independent instance per
   CAND-0007/0009/0019). `market_context` is built via `build_market_context(symbol, ts_close, [bar])`
   (`pdh_pdl_demo/market_context.py:17`) — **always `m15_features={}`, empty** (see §3).
5. **The gate**: `send_after_dry_run_gate(...)` (`mt5_demo_execution/gating.py:39`), config
   `_NO_CONFIDENCE_CONFIG = OrchestratorConfig(recognition_pattern_id=None)` (identical constant,
   independently defined in both orchestration modules). DRY_RUN leg first (never touches the broker —
   `DryRunBrokerAdapter`); only if `approved` AND `ACKNOWLEDGED` AND `safety_guard_report.all_passed`
   does the DEMO leg run, against the one real, shared `MT5DemoBrokerAdapter` each entrypoint's `main()`
   constructs once (`gating.py:68-69` enforces identity, `ValueError` otherwise).
6. Inside `orchestrate()` (`execution_orchestrator/engine.py:73`), run for BOTH legs, in order:
   daily-state reset → circuit-state check (**structurally skipped** here — `orchestrate()` is never
   called with `circuit_state=`, so the REAL breaker lives entirely at step 2, not inside this function)
   → `LIVE` mode refused unconditionally → `DEMO_ACCOUNT_CHECKED` (demo leg only) → freshness check
   (300s default) → `build_context_snapshot(...)` (**this is where `market_intelligence` executes — §3**)
   → Recognition Engine **skipped** (`recognition_pattern_id is None`) → Confidence Engine
   (`assess_confidence`, reads `context.market_intelligence.confidence.score` as its sole component,
   since `recognition=None`) → **if `not eligible_for_risk_evaluation`, denied here, before Risk Manager
   is ever called** → **Risk Manager**: `evaluate_trade_proposal(proposal, account, portfolio,
   instrument, risk_context, risk_config)` (`risk_manager_live/engine.py:94`) — a pure function, no I/O,
   reusing the frozen `risk_manager/` package's guards/limits/sizing unmodified; can `RISK_DENIED`
   (data-incompleteness, wrong-sided stop, guard/cooldown/limit/filter failure, invalid sizing,
   sub-minimum volume, insufficient margin) or approve with `calculated_volume`/`monetary_risk`/etc. — a
   **hard gate, both legs, every candidate, no bypass** → Portfolio Manager (can also deny) → Order
   Manager → `process_approved_intent` → `submit_built_order` → `_validate_and_submit` →
   **`adapter.submit_order(order)`**.
7. On the DEMO leg: `MT5DemoBrokerAdapter.submit_order` (`mt5_demo_execution/adapter.py:73`) — after its
   own connected/algo-trading/demo-account/expected-server/max-volume checks — calls `order_check` then
   `order_send` → `RealMT5DemoGateway.order_send` (`gateway.py:29-30`) → the genuine MetaTrader5 API call.

**Risk Manager's exact position**: consulted once per leg, strictly after Context Engine and Confidence
Engine, strictly before Portfolio/Order Manager — the single authoritative approve/deny step; nothing
downstream overrides a denial, nothing upstream of `submit_order` bypasses it.

## 2. The three active recognition rules

| CAND | Class | File | Feeds | Enabled? |
|---|---|---|---|---|
| 0001 | `PdhPdlRecognitionRule` | `pdh_pdl_demo/recognition_rule.py:74` | `PdhPdlOrchestrator.submit_candidate` | Always — own dedicated process, no `PolicyControl` gate |
| 0007 | `LevelFvgConfluenceRecognitionRule` | `multi_policy_live/recognition_level_fvg_confluence.py:47` | `PolicyOrchestrator.submit_candidate` (magic 100_002) | **Enabled** — persisted `1.0` |
| 0019 | `DzLevelConfluenceRecognitionRule` | `multi_policy_live/recognition_dz_level_confluence.py:44` | same (magic 100_004) | **Enabled** — persisted `1.0` |

Each consumes the accumulated M15 OHLC bar arrays from `LiveBarFeed` plus a live tick
(`LiveMT5TickReader.read()`) for `effective_spread`/`executable_stop_price` at trigger time.

**CAND-0009** (`LevelBreakDriveRecognitionRule`, `recognition_level_break_drive.py:56`) — fully wired
(own `PolicyOrchestrator`, magic 100_003, own `MechanicalCloseCheck`), confirmed **INACTIVE**: code
default `PolicyControl.is_enabled(id, default=False)`, and the persisted `kv_state` table has no row for
CAND-0009 at all (not even an explicit `0.0`) — falls through to the code default. Recognition still
fires and is journaled every bar; `submit_candidate` is structurally unreachable
(`multi_policy_live/entrypoint.py:216`).

## 3. `market_intelligence` — verified independently, and the prior "VE" report needs a correction

**The code executes on every live order attempt and its output IS consumed by a real gate** — this
contradicts a blanket "never reaches a live decision" claim. Full chain: `orchestrate()` →
`build_context_snapshot()` (`context_engine/engine.py:27`) → `build_market_intelligence(context)`
(`market_intelligence/engine.py:33`, line 36) → `MarketContextSnapshot.market_intelligence` →
`confidence_engine/engine.py:52-53`: `context.market_intelligence.confidence.score` becomes the **sole**
component of the confidence score (recognition is skipped on this path) → gates
`eligible_for_risk_evaluation` → **can structurally deny a candidate before Risk Manager is ever called.**

**But the qualifier that actually matters**: `build_market_context()` hardcodes `m15_features={}` (empty,
by its own docstring) on every call from both live entrypoints. Traced through every analyzer that feeds
the score: `analyze_trend` → every timeframe `UNKNOWN` (no features present) → `analyze_multi_timeframe
_agreement` → `agreement_score=None` → `analyze_volatility` → `regime=UNKNOWN`, penalty `0.0` →
`compute_context_confidence`: `components=[1.0 (hardcoded data_quality_ok), 1.0]` (the `None` agreement
term excluded) → **`score=1.0`, deterministically, on every single call** → grade A always →
`eligible_for_risk_evaluation=True` always.

**Correct, precise statement for the record**: `market_intelligence`'s code is live and its output is
read by a real eligibility gate ahead of Risk Manager (contradicting "never reaches a live decision" as
a reachability claim) — but under the current wiring it is a **structural always-pass constant**, because
the feature data it needs is never populated live, so it has had **zero actual effect on any live
decision to date**. Both halves are true simultaneously; neither alone is the accurate summary.

## 4. Every path that can produce a decision or order today

Structurally, there is exactly **one** production call site of `.submit_order(` in the whole `ai_trader/`
tree (`execution_engine/pipeline.py:122`), reached only via `order_manager/engine.py:78` →
`execution_orchestrator/engine.py:287`. Exactly **one** production call site of `order_send(`
(`mt5_demo_execution/adapter.py:96`), whose only real implementation
(`RealMT5DemoGateway.order_send`) is the actual MetaTrader5 API call. Both are constructed and wired only
in `pdh_pdl_demo/entrypoint.py:main()` and `multi_policy_live/entrypoint.py:main()`.

| Path | Process | Enabled? |
|---|---|---|
| CAND-0001 | `pdh_pdl_demo` | **ENABLED** |
| CAND-0007 | `multi_policy_live` | **ENABLED** |
| CAND-0019 | `multi_policy_live` | **ENABLED** |
| CAND-0009 | `multi_policy_live` | Wired, **INACTIVE** |

`live_observation`, `spread_collection`, `zone_observer` are structurally incapable: all three construct
only the read-only `RealMT5Gateway`, never `MT5DemoBrokerAdapter`; their recognition rules are all
`*NullRecognitionRule` variants that return `None` unconditionally — no candidate is ever produced for
any orchestrator to submit.

No other package or manually-runnable script in the tree can reach either call site today.
`mandate2_readiness/broker_gate.py` (new, this mandate) defines `BrokerOrderSubmissionGate` but has zero
importers anywhere outside its own package — inert, prepared, not wired into anything.

## 5. Existing static "no direct trading call" guards, and kill-switch precursors

`execution_engine/adapters/tests/test_static_no_trading_calls.py` proves the **read-only base**
(`MT5ReadOnlyBrokerAdapter`/`MT5Gateway`/`RealMT5Gateway`) never defines order-submission methods at all
— scoped to `execution_engine/adapters/` only, by design does not (and should not) constrain
`mt5_demo_execution` (a separate, legitimately order-capable package CAND-0001/0007/0019 need).

Every OTHER package with a live-reachable or brain-adjacent role has its OWN, independently-authored
static guard (`tests/test_import_independence.py`, forbidding `order_send`/`order_check`/`submit_order`/
`cancel_order`/`close_position` text, sometimes more): `execution_orchestrator`, `live_loop`,
`live_signal_source`, `multi_policy_live`, `pdh_pdl_demo`, `spread_collection`, `zone_observer`,
`structural_observer`, `live_observation` (most comprehensive — whitelist-based package imports, plus
"only `*NullRecognitionRule` may ever be constructed"), `risk_manager_live`, `recognition_engine`,
`recognition_engine_live`, and eight more narrower packages. None of these is a single global guard —
each proves "this package doesn't reach the broker directly," not "no order can ever be submitted
system-wide."

**No global "is order submission allowed" flag existed anywhere before this mandate.** The closest things
to a kill switch were: (a) the account-wide persisted circuit breaker (gates all 4 policies uniformly,
but per-process-file, not one global flag), (b) per-policy `PolicyControl.set_enabled(...)` (CAND-0007/
0009/0019 individually, not CAND-0001, and doesn't stop the process from running/evaluating), (c) killing
the process outright. `mandate2_readiness/broker_gate.py`'s `BrokerOrderSubmissionGate` is the first
single, explicit, default-closed primitive of this kind — see the Mandate 2 prep report for its design
and tests.

## CEO amendment A1 (2026-08-14) cross-reference

N1-N6/EV can legitimately reach `SHADOW_TRADE_CANDIDATE`, and Risk Manager/Execution Adapter can process
it IN SHADOW — this inventory's own §1 confirms the CURRENT Risk Manager is already positioned exactly
where a shadow-processing step would sit (after Confidence Engine, before Order Manager), and §4 confirms
the broker-submission choke point is a single, narrow, already-enumerated surface — both are reassuring
preconditions for the amendment's own framing ("dreptul de ANALIZA... nu e acelasi lucru cu dreptul de
EXECUTIE") to be enforceable by a single last-mile gate, once wired.
