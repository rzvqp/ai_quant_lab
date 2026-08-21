# AI_TRADER_NEW_BRAIN_ARCHITECTURE

**Mandate**: `AI-TRADER-NEW-BRAIN-ARCHITECTURE-IMPLEMENTATION-001`
**Date**: 2026-08-21
**Status**: `AI_TRADER_NEW_BRAIN_ARCHITECTURE_IMPLEMENTED`, `STRATEGY_PLUGIN_FRAMEWORK_READY`, `STRATEGY_CATALOG_FRAMEWORK_READY`, `LIVE_SHADOW_BROKER_DISABLED_READY`, `READY_FOR_FUTURE_VALIDATED_STRATEGY_ONBOARDING`

## 1. System diagram

```
MARKET DATA (MT5, read-only)
    |
    v
CANONICAL MARKET INTELLIGENCE  N1 -> N2 -> N3 -> N4  (ve_brain 0.1.3 + new_brain_bridge, UNCHANGED)
    |
    v
CANONICAL MARKET STATE  (new_brain_live.market_state.MarketState == dual_clock.CachedUpstreamContext)
    |
    v
STRATEGY CATALOG  (strategy_platform.catalog.StrategyCatalog -- AI-Trader-owned, NOT ve_brain's sealed one)
    |
    v
STRATEGY ROUTER  (strategy_platform.router.StrategyRouter -- eligibility + dispatch, never profitability)
    |
    v
STRATEGY EVALUATION  (strategy_platform.strategy_protocol.Strategy.evaluate -> TradeHypothesis | None)
    |
    v
EV / DECISION ENGINE  (strategy_platform.ev_engine.EVDecisionEngine -- MockEVDecisionEngine ships; a
    |                   real, ratified implementation is BLOCKED, see section 8)
    v
RISK ENGINE  (risk_manager_live.evaluate_trade_proposal -- UNCHANGED, reused verbatim)
    |
    v
EXECUTION ADAPTER  (new_brain_bridge.execution_shadow.attempt_shadow_execution + BrokerOrderSubmissionGate
    |                -- UNCHANGED, reused verbatim; gate.enabled=False, structurally, always, this mandate)
    v
BROKER  <-- UNREACHABLE while BROKER_ORDER_SUBMISSION = DISABLED

    Every stage also writes into: SHADOW LEDGER (strategy_platform.shadow_ledger.ShadowLedger)
```

`NO VALID STRATEGY` or `NO VALID EDGE` -> `NO_TRADE` at every stage. `NO_TRADE` is a first-class,
tested, expected outcome -- see section 12.

## 2. N1-N6 integration

Canonical chain is `new_brain_bridge.bridge.evaluate_bar`/`query_tower_chain` + the installed `ve_brain`
0.1.3 package (N1 RawAxes/Router, N2/N3/N4 via the isolated `ve_tower_worker` subprocess). **Nothing in
this mandate touches, retunes, or duplicates this chain.** The generic platform consumes its OUTPUT
(`CachedUpstreamContext`/`MarketState`) and, for regime eligibility, reuses `ve_brain.applicable_
regimes(axes)` verbatim -- never a second classifier. N1's own separately-isolated incremental
replay path (`new_brain_live.n1_incremental`, `ve_n1_replay 0.1.1`, now running in its own
`.ai_trader_n1_venv`, isolated from Alpha's `.alpha_n1_venv` per `N1_ALPHA_AI_TRADER_RUNTIME_ISOLATION_
COMPLETE`) is unaffected by anything in this document.

## 3. MarketState contract

`ai_trader/new_brain_live/market_state.py`. **No new class.** `MarketState` is a type alias for the
already-real, already-produced `dual_clock.upstream_context.CachedUpstreamContext` -- frozen, fully
typed, carrying its own `context_id` identity. Schema version: `MARKET_STATE_SCHEMA_VERSION =
"market-state-v1"`. See that module's own docstring for the full field-by-field N1-N6 provenance table,
and for which mandate-example categories (price levels, session/time context, a first-class range
field) are deliberately absent because no ratified N1-N6 contract produces them at this layer.

## 4. Strategy Catalog

`ai_trader/new_brain_live/strategy_platform/catalog.py`. `StrategyCatalog` (immutable snapshot of
`CatalogEntry` tuples) + 6-way `StrategyStatus` (`MOCK_TEST_ONLY`/`RESEARCH_ONLY`/`ALPHA_CANDIDATE`/
`VALIDATED`/`DISABLED`/`RETIRED`). `EMPTY_CATALOG` is the shipped default -- zero entries, section 10's
own required behavior.

**Why this catalog, not `ve_brain`'s own**: `ve_brain.n6._SEALED_CATALOG` is internal, sealed, and
contains exactly 4 hardcoded strategies -- adversarially proven (8 tests, `ai-trader-three-strategies`
branch, `INTEGRATION_BLOCKED_VE_BRAIN_STRATEGY_CATALOG.md`, 2026-08-18) to reject ANY other
`strategy_id` with `UNKNOWN_STRATEGY`, unconditionally, before eligibility/N3/N4/probability_inputs are
even examined. Building an AI-Trader-owned catalog, independent of that sealed registry, is the direct,
generic fix for the hot-add requirement (section 28) -- a future strategy is admitted HERE, never by
waiting for a new `ve_brain` release.

## 5. Strategy contract

`ai_trader/new_brain_live/strategy_platform/strategy_protocol.py`. `Strategy` is a `typing.Protocol`
(structural typing) with one method: `evaluate(StrategyEvaluationInput) -> TradeHypothesis | None`. A
strategy module needs no import from this package beyond this interface -- the hot-add promise (section
28). `StrategyEvaluationInput` bundles `market_state`, an optional `tower_context` (N2/N3/N4, only when
the strategy's own contract needs it), and its own immutable `config` mapping.

## 6. Strategy Router

`ai_trader/new_brain_live/strategy_platform/router.py`. Reads MarketState + enabled catalog entries,
checks eligibility (`allowed_instruments` + `context_eligibility` regime match, or `None` =
`REGIME_INDEPENDENT` -- section 13's own explicit "not every strategy requires a regime"), invokes only
eligible strategies, collects `TradeHypothesis` outputs. **Never decides profitability.** Catches any
exception a strategy raises during `evaluate()` per-strategy (`RouterOutcome.invalid_output`) so one
strategy's bug can never crash the cycle for every other strategy (section 26/37).

## 7. TradeHypothesis schema

`ai_trader/new_brain_live/strategy_platform/trade_hypothesis.py`. Every field from section 8's own list;
`direction` reuses `signal_engine.types.Direction` verbatim (the same vocabulary the existing Risk Engine
already expects, so no translation layer is needed at that boundary). `dedup_key` = `(strategy_id,
instrument, market_state_identity)` -- section 23's own required identity, derived, not invented.

## 8. EV Engine

`ai_trader/new_brain_live/strategy_platform/ev_engine.py`. **The disclosed mismatch (section 15's own
explicit instruction)**: the only ratified EV/decision authority in this repository is
`ve_brain.decide_n6`, and it is sealed to the same 4 hardcoded strategies (section 4). A real, ratified
`EVDecisionEngine` for anything admitted through the new Strategy Catalog is therefore **BLOCKED**
pending either a new `ve_brain` release that accepts external strategies, or a separate,
CEO/Statistician/Red-Team-ratified decision-rule authority for this catalog. `MockEVDecisionEngine`
ships as the only concrete implementation -- deterministic, test-only, computes no real expected value,
reads one explicit fixture flag off `TradeHypothesis.expected_edge`.

> **Addendum (mandate `VE-AI-TRADER-GENERIC-EV-AUTHORITY-001`)**: the blocker described above is closed --
> `real_ev_engine.py`'s `RealEVDecisionEngine` is the separate, versioned decision-rule authority this
> paragraph anticipated, composing AI-Trader's own `StrategyCatalog` admission gate with `ve_brain`'s
> public, generic `run_ev`. `ve_brain.decide_n6` and its sealed catalog remain untouched. See
> `VE_GENERIC_STRATEGY_EV_AUTHORITY_ARCHITECTURE.md` for the full design and
> `VE_GENERIC_STRATEGY_EV_AUTHORITY_HANDOFF.md` for how a validated strategy reaches it. The paragraph
> above is left as-written since it accurately records the state of the system before this mandate.

## 9. Risk Engine

Reused verbatim: `risk_manager_live.engine.evaluate_trade_proposal`. Already fully generic (no
`ve_brain` dependency); `strategy_platform.risk_execution_adapter.py`'s only job is mapping
`TradeHypothesis` -> `TradeProposal`. A strategy may propose a stop (`TradeHypothesis.invalidation`); it
may never override risk policy -- `evaluate_trade_proposal` independently recomputes sizing/limits/
guards from `RiskContext`/`RiskConfig`, never trusting the strategy's own numbers. **Known pre-existing
gap, not introduced by this mandate**: `new_brain_bridge.risk_gate.submit_new_brain_candidate`'s own
circuit-breaker check is opt-in via a parameter, not unconditionally enforced by that function's own
default -- noted for a future hardening pass, not fixed here (out of this mandate's scope; the generic
platform calls `evaluate_trade_proposal` directly and does not go through that wrapper at all).

## 10. Execution Adapter

Reused verbatim: `new_brain_bridge.execution_shadow.attempt_shadow_execution` +
`mandate2_readiness.broker_gate.BrokerOrderSubmissionGate` (`enabled: bool = False` by construction,
AST-guard-proven no code path can flip it). **Two structurally distinct broker gates exist in this
repository** (found during this mandate's own audit): this one (new-brain path) and
`mt5_demo_execution.gating.send_after_dry_run_gate` (the legacy CAND-000x demo-order path, now
additionally hard-quarantined by `LEGACY_TRADING_AUTHORITY_QUARANTINED = True`, see section 15 of the
implementation report). The generic platform in this document exclusively uses the first.

## 11. Shadow mode

`new_brain_live.entrypoint`'s existing `LIVE_SHADOW` runtime (Scheduled Task `AITraderLiveShadow`) is
the main runtime integration mode, per section 20 -- **unmodified by this mandate**. This mandate builds
the generic pipeline (`strategy_platform.pipeline.run_cycle`) that a future wiring step would call from
that same runtime loop, exactly the way `M5DecisionLoop` already calls `ve_brain.decide_n6` today; wiring
`run_cycle` into the actual live poll loop is deliberately NOT done in this delivery (no real strategies
exist to route yet -- section 39's own "architecture implementation only").

## 12. NO_TRADE semantics

`ai_trader/new_brain_live/strategy_platform/reason_codes.py` -- the canonical, closed vocabulary
(section 22): `NO_VALIDATED_STRATEGY`, `NO_ELIGIBLE_STRATEGY`, `NO_STRATEGY_SIGNAL`, `EV_BELOW_
THRESHOLD`, `RISK_REJECTED`, `DATA_NOT_READY`, `MARKET_STATE_INVALID`, `BROKER_DISABLED`, `CONFLICT_
POLICY_BLOCK`, `STALE_INPUT`, `INTEGRITY_FAILURE`. `pipeline.run_cycle`'s own decision tree (documented
in its module docstring) maps every branch to exactly one of these -- never a free-text reason, never a
silent decision. `final_decision` is structurally always `"NO_TRADE"` in this delivery (broker globally
disabled); `hypothetical_order_intent` is a SEPARATE field, populated whenever Risk approved, so shadow
mode still records what WOULD have been sent.

## 13. Strategy lifecycle

`StrategyStatus`: `MOCK_TEST_ONLY` (engineering only, section 11) -> `RESEARCH_ONLY` -> `ALPHA_CANDIDATE`
-> `VALIDATED` (only status ever eligible for future production decision authority, section 9) ->
`DISABLED`/`RETIRED`. `VALIDATED` requires a non-`None` `validation_provenance`, enforced at
`CatalogEntry` construction (`ValueError` otherwise) -- a "validated" entry with no disclosed evidence is
structurally impossible to construct.

## 14. Fingerprints

Every `ShadowLedgerRecord` (section 21) carries `StrategyPlatformFingerprints`: `market_intelligence_
fingerprint` (MarketState's own `n1_output_fp`), `market_state_schema_version`, `catalog_version`,
`ev_engine_version`, `risk_engine_version`, `execution_adapter_version` -- section 27's own required
binding, enabling exact later reproduction of any recorded decision.

## 15. Restart / dedup

`strategy_platform/dedup.py`: identity = `(strategy, instrument, market_state_identity)`. No separate
dedup store -- the `ShadowLedger`'s own persisted, append-only history (`SqliteStateStore`, same engine
`LiveShadowJournal`/`NewBrainTelemetryLog` already use) IS the dedup source of truth. Reopening a
`ShadowLedger` against the same state file (a real process restart) reloads every prior record;
re-processing the identical MarketState returns the EXISTING record, never re-attempts Risk/Execution,
never appends a duplicate row -- proven by `test_dedup_restart_replay_never_reprocesses_the_same_market_
state` against a genuinely reopened `SqliteStateStore`.

## 16. Fail-closed behavior

`pipeline.run_cycle`'s first two checks, before anything else runs: (1) an invalid MarketState
(`atr`/`entry_price` is `None`) -> `NO_TRADE`/`MARKET_STATE_INVALID`, never reaches the Router; (2)
already-processed MarketState -> the existing record, never re-processed. A strategy that raises during
`evaluate()` is caught per-strategy (`INTEGRITY_FAILURE`), never crashes the cycle. Multiple simultaneous
`TRADE_DECISION`s on one MarketState are refused entirely (`CONFLICT_POLICY_BLOCK`), never arbitrated by
an invented rule. Broker submission is unreachable by construction (`BrokerOrderSubmissionGate.enabled =
False`), independent of anything in this document.

## 17. Future validated-strategy onboarding procedure

See `AI_TRADER_VALIDATED_STRATEGY_ONBOARDING_CONTRACT.md` for the complete, standalone handoff contract.
In outline: a strategy module implementing `Strategy`, a `CatalogEntry` (with real fingerprints and
`validation_provenance`), and its own tests are the ONLY new artifacts required -- no change to N1-N6,
`MarketState`, `StrategyRouter`, the Risk Engine, or the Execution Adapter (section 28's own acceptance
criterion, proven structurally: none of those modules import anything from `strategy_platform`, only the
reverse).
