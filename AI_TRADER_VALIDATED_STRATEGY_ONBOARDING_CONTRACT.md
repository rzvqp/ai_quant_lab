# AI_TRADER_VALIDATED_STRATEGY_ONBOARDING_CONTRACT

**Mandate**: `AI-TRADER-NEW-BRAIN-ARCHITECTURE-IMPLEMENTATION-001`, section 44
**Goal**: a future independently validated strategy becomes a plug-in, never a core rewrite. This
document is what an Alpha team hands AI Trader Engineering once a strategy has cleared **Alpha ->
Statistician -> Red Team -> CEO** -- nothing less, nothing earlier. It authorizes NO strategy today;
delivering this document for S5, CAND-0001/0007/0019, S9, S20, S1-PDH, or DC-000x is explicitly out of
scope for this mandate (section 39).

## What must be handed over

### 1. Strategy spec
A written spec identifying: strategy family, canonical mechanism, the exact regime(s) it requires (or
`REGIME_INDEPENDENT`, section 13), entry/invalidation/exit rules in the same string vocabulary this
codebase already uses (`"pullback3"`, `"atr2"`, `"rr:3.0"`, `"time:40.0"`, `"none"` -- see
`canonical_specs.py`'s own precedent), holding window, and the exact source of every parameter (never
invented or approximated -- the same discipline that produced `INTEGRATION_BLOCKED_VE_BRAIN_STRATEGY_
CATALOG.md`'s own G0037/G0184/G0059 spec table).

### 2. Implementation
A module implementing `ai_trader.new_brain_live.strategy_platform.strategy_protocol.Strategy` --
structural typing, ONE method: `evaluate(StrategyEvaluationInput) -> TradeHypothesis | None`. Must:
- Never import anything from `mt5_demo_execution`, `execution_engine`, `new_brain_bridge.execution_
  shadow`, or any broker-facing module -- proven by this repo's own AST-guard convention
  (`test_strategies_never_reach_broker.py`'s own pattern, extend it for the new strategy's own file).
- Never construct a `TradeHypothesis` with an invented/approximated field -- every field in section 8's
  schema must trace to the strategy spec (item 1) or to `MarketState`/`tower_context` it was actually
  given.
- Be pure with respect to global/broker state: `evaluate()` reads `StrategyEvaluationInput`, returns a
  value, and does nothing else observable.

### 3. Config
An immutable configuration object/mapping (the `config` field of `StrategyEvaluationInput`), plus its
own `config_fingerprint` (a stable hash over its exact content) for `CatalogEntry.config_fingerprint`.

### 4. Validation identity
`CatalogEntry.validation_provenance` -- the exact commit/report chain (Alpha canonical rerun commit,
Statistician mandate id, Red Team PASS commit/id, CEO ratification reference) a future auditor can
follow back to the original evidence. `CatalogEntry.__post_init__` structurally REJECTS `status=
VALIDATED` with `validation_provenance=None` -- there is no way to mark a strategy VALIDATED without
supplying this.

### 5. Allowed direction / allowed context
`CatalogEntry.allowed_directions` (`("LONG",)`, `("SHORT",)`, or both) and `CatalogEntry.context_
eligibility` (a tuple of `ve_brain.SemanticRegime` value strings the strategy is eligible under, or
`None` for `REGIME_INDEPENDENT`) -- both checked by `StrategyRouter.check_eligibility` using the REAL,
canonical `ve_brain.applicable_regimes` classifier, never a reinvented one.

### 6. Expected inputs
Whether the strategy needs `tower_context` (real N2/N3/N4, via `bridge.query_tower_chain`) or only
`MarketState` -- declared explicitly, since `StrategyEvaluationInput.tower_context` is `None` unless the
Router was told to fetch it (wiring a strategy that needs Tower context into a live loop is a deliberate,
future, separately-reviewed step, not automatic).

### 7. Risk requirements
`CatalogEntry.risk_contract_reference` -- which `RiskConfig`/`RiskContext` this strategy expects to be
evaluated under (the Risk Engine, `risk_manager_live.evaluate_trade_proposal`, is NEVER modified per
strategy; a strategy that needs a genuinely different risk treatment requires a new, explicit `RiskConfig`
profile, reviewed the same way any other risk-config change is, never a strategy-specific code branch
inside the Risk Engine itself).

### 8. Fingerprints
`CatalogEntry.implementation_fingerprint` (hash of the strategy module's own source/build identity) and
`config_fingerprint` (item 3) -- both bound into every `ShadowLedgerRecord.fingerprints` this strategy
ever produces, enabling exact later reproduction (section 27).

### 9. Tests
At minimum, mirroring the section 37 matrix already proven for the mock strategies in this delivery:
positive signal on the strategy's own real fixture; refusal outside its allowed regime(s); refusal
without required Tower context (if applicable); determinism (same MarketState -> same `TradeHypothesis`,
byte for byte); the strategy never reaches a broker-facing call (AST guard); and a combined test if this
strategy could ever co-signal with another VALIDATED strategy on the same MarketState (the conflict
policy remains `POLICY_PENDING_VALIDATED_STRATEGY_PORTFOLIO` until a real, ratified arbitration rule
exists -- a new strategy does not get to invent its own).

### 10. Rollback
`CatalogEntry.rollback_identity` -- what removes this strategy from production authority instantly:
today, simply omitting its `CatalogEntry` from the next `StrategyCatalog` build (or setting `enabled=
False`/`status=DISABLED`) is sufficient, since the catalog is an immutable snapshot rebuilt, never
mutated in place.

## What does NOT need to change

Per section 28's own acceptance criterion, adding a strategy through this contract requires ONLY the
five items above (spec, implementation, config, tests, catalog registration) and never touches:
`new_brain_bridge`'s N1-N6 chain, `market_state.py`, `strategy_platform.router`, `strategy_platform.
risk_execution_adapter`, or `strategy_platform.shadow_ledger`. This is structurally true today, not
merely a promise: none of those modules import anything from a strategy module; only the reverse.

## What this contract does NOT cover

**The EV/Decision Engine.** Per `AI_TRADER_NEW_BRAIN_ARCHITECTURE.md` section 8 and `AI_TRADER_NEW_
BRAIN_IMPLEMENTATION_REPORT.md` section 7 item 1: no real, ratified `EVDecisionEngine` exists for any
strategy admitted through this catalog today. A strategy that clears this onboarding contract is
`VALIDATED` for eligibility/dispatch purposes, but reaching an actual `TRADE_DECISION` additionally
requires either (a) a new `ve_brain` release that accepts strategies from outside its own sealed
catalog, or (b) a separate, explicitly CEO/Statistician/Red-Team-ratified EV/decision-rule authority
built for this new catalog. Onboarding a strategy through this document does not, by itself, grant it a
path to `TRADE_DECISION` -- that is a second, separate, not-yet-authorized mandate.

> **Addendum (mandate `VE-AI-TRADER-GENERIC-EV-AUTHORITY-001`, closes this gap)**: option (b) above has
> now been built -- `ai_trader/new_brain_live/strategy_platform/real_ev_engine.py`,
> `RealEVDecisionEngine`. Items 1-10 above are UNCHANGED and remain the starting point for onboarding a
> strategy; see [`VE_GENERIC_STRATEGY_EV_AUTHORITY_HANDOFF.md`](VE_GENERIC_STRATEGY_EV_AUTHORITY_HANDOFF.md)
> for the one new step (constructing `RealEVDecisionEngine` and populating
> `TradeHypothesis.expected_edge`) that now carries a `VALIDATED` `CatalogEntry` the rest of the way to a
> real `TRADE_DECISION`. This paragraph is left as-written above (rather than rewritten) since it
> accurately records the state of the system before this mandate.

> **Addendum 2 (mandate `AI-TRADER-S5-CANONICAL-ONBOARDING-001`, first real strategy onboarded through
> this exact contract)**: S5 (`s5_c_2d587447_opening_range_breakout_long`,
> `ai_trader/new_brain_live/strategy_platform/s5_opening_range_breakout.py`) is the first strategy to walk
> items 1-10 above end to end with real, cited validation evidence (`AI_TRADER_S5_ONBOARDING_REPORT.md`
> has the full identity/provenance/fidelity trail). One genuine, disclosed nuance this first real
> onboarding surfaced, worth knowing before onboarding the next strategy: a strategy whose `MarketState`
> alone is insufficient to determine its own setup (S5 needs the opening range's raw high/low, tracked
> across several bars, which `MarketState` deliberately does not carry) may need its own additional,
> stateful public method beyond the bare `Strategy` protocol's one required `evaluate()` (S5's own
> `observe_bar(bar)`) -- this is allowed (the protocol's "one method" is a MINIMUM surface, not an upper
> bound) and does not require any change to `StrategyEvaluationInput`, `router.py`, or any other generic
> module; whoever wires such a strategy into a live loop is responsible for calling its extra method(s) in
> the correct order relative to the M15 context-refresh cycle, exactly as `RawAxesBuilder.observe(bar)`
> already establishes the precedent for. S5 itself remains un-wired into any live loop -- shadow/fixture
> use only, per this mandate's own explicit scope.
