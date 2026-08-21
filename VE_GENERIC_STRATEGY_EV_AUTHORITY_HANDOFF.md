# VE_GENERIC_STRATEGY_EV_AUTHORITY_HANDOFF

**Mandate**: `VE-AI-TRADER-GENERIC-EV-AUTHORITY-001`
**Audience**: whoever onboards the first real `VALIDATED` strategy (expected: S5, per a future, separate,
not-yet-authorized mandate — this document grants no strategy any authority by itself)
**Companion documents**: [`AI_TRADER_VALIDATED_STRATEGY_ONBOARDING_CONTRACT.md`](AI_TRADER_VALIDATED_STRATEGY_ONBOARDING_CONTRACT.md)
(items 1–10: spec, `Strategy` implementation, config, tests, catalog registration — unchanged, still the
starting point), [`VE_GENERIC_STRATEGY_EV_AUTHORITY_ARCHITECTURE.md`](VE_GENERIC_STRATEGY_EV_AUTHORITY_ARCHITECTURE.md)
(why this is built the way it is), [`VE_GENERIC_STRATEGY_EV_AUTHORITY_IMPLEMENTATION_REPORT.md`](VE_GENERIC_STRATEGY_EV_AUTHORITY_IMPLEMENTATION_REPORT.md)
(exact test/mypy/performance evidence).

## What changed since the onboarding contract was written

`AI_TRADER_VALIDATED_STRATEGY_ONBOARDING_CONTRACT.md`'s closing section stated: *"reaching an actual
TRADE_DECISION additionally requires... a separate, explicitly CEO/Statistician/Red-Team-ratified EV/
decision-rule authority built for this new catalog... a second, separate, not-yet-authorized mandate."*

That authority now exists: `ai_trader/new_brain_live/strategy_platform/real_ev_engine.py`,
`RealEVDecisionEngine`. Items 1–10 of the onboarding contract are **unchanged** — a strategy still becomes
`VALIDATED` exactly the way that document describes. What follows is the one new step: how a `VALIDATED`
`CatalogEntry` actually reaches a real `TRADE_DECISION`, now that the authority exists.

## The end-to-end sequence

```
validated strategy artifact
        |
        v
StrategyCatalog registration  (CatalogEntry, status=VALIDATED, real fingerprints + provenance)
        |
        v
StrategyRouter.route(catalog, market_state)   -- regime/direction eligibility, via ve_brain.applicable_regimes
        |
        v
Strategy.evaluate(StrategyEvaluationInput) -> TradeHypothesis
        |
        v
RealEVDecisionEngine.decide(hypothesis)       -- THE NEW STEP -- admission re-check + ve_brain.run_ev
        |
        v
risk_execution_adapter.evaluate_and_attempt() -- Risk Engine (unmodified) + shadow Execution (broker gate DISABLED)
        |
        v
ShadowLedger.record()
```

### Step 1–2: unchanged, per the onboarding contract

Build the strategy module (`Strategy` protocol, one method, `evaluate(StrategyEvaluationInput) ->
TradeHypothesis | None`) and its `CatalogEntry` exactly per that document's items 1–10. Nothing about
`RealEVDecisionEngine`'s existence changes what a `CatalogEntry` needs to contain — `config_fingerprint`,
`implementation_fingerprint`, and `validation_provenance` are exactly as required there, and
`RealEVDecisionEngine` re-checks them independently (below) rather than trusting them a second time.

### Step 3: construct the real engine once per run, alongside the catalog and market_state

```python
from ai_trader.new_brain_live.strategy_platform.real_ev_engine import CostModel, RealEVDecisionEngine

cost_model = CostModel(
    cost_model_id="<ratified-cost-model-id>",   # NOT invented ad hoc -- the same cost identity Risk/
    full_spread_price=...,                       # Execution already use for this instrument/session
    entry_slippage_price=...,
    exit_slippage_price=...,
)

ev_engine = RealEVDecisionEngine(
    catalog=catalog,          # the SAME StrategyCatalog StrategyRouter routed against
    market_state=market_state,
    cost_model=cost_model,
)
```

`RealEVDecisionEngine.__post_init__` fails closed (`RealEVAuthorityError`) if the installed
`ve_brain.VE_BRAIN_VERSION` is not in its pinned, verified set (today: `("0.1.3",)`). If `ve_brain` is
ever upgraded, that tuple must be deliberately reviewed and extended — this is a feature, not friction: an
un-reviewed `ve_brain` upgrade must not silently start feeding a different decision core into production.

### Step 4: pass it to `pipeline.run_cycle` exactly where `MockEVDecisionEngine` went before

```python
result = pipeline.run_cycle(
    market_state=market_state, catalog=catalog, ev_engine=ev_engine,
    risk_execution_deps=deps, ledger=ledger, router=StrategyRouter(),
)
```

No other call site, no other parameter, changes. `pipeline.run_cycle`'s own code does not know or care
whether `ev_engine` is `MockEVDecisionEngine` or `RealEVDecisionEngine` — both satisfy the same
`EVDecisionEngine` Protocol. `result.record.fingerprints.ev_engine_version` will correctly read
`"real-ev-engine-v1"` for every cycle in which `ev_engine.decide()` actually ran.

### What `RealEVDecisionEngine.decide()` does with your hypothesis (nothing to configure — described for
### auditability)

1. Looks up `(hypothesis.strategy_id, hypothesis.strategy_version)` in `catalog` — **your** `CatalogEntry`
   must already be in there, `enabled=True`, `status=StrategyStatus.VALIDATED`. Anything else fails closed
   (`UNKNOWN_STRATEGY` / `STRATEGY_DISABLED` / `NO_ELIGIBLE_STRATEGY`).
2. Re-verifies `hypothesis.strategy_config_fingerprint == entry.config_fingerprint` — a tampered or stale
   hypothesis fails closed (`STRATEGY_POLICY_MISMATCH`), even if the strategy_id/version matched.
3. Re-verifies `hypothesis.market_state_identity` against the `market_state` the engine itself was built
   with, and checks `axes.n1_contract_version` — a hypothesis built against a different or incompatible
   `MarketState` fails closed (`MARKET_STATE_MISMATCH` / `INCOMPATIBLE_N1_CONTRACT`).
4. Validates geometry (no NaN/inf, sane timestamp ordering, a parseable `exit_specification`) and decodes
   `hypothesis.expected_edge` as a `real-ev-expected-edge-v1` payload (below) — malformed input fails
   closed (`SCHEMA_VALIDATION_FAILED` / `MISSING_PROBABILITY_INPUTS`).
5. Builds a `ve_brain.DecisionRequest` and calls the **same, ratified, public** `ve_brain.run_ev()` every
   other decision in this project is measured against — never a bespoke EV formula.
6. Returns `TRADE_DECISION` (reason `REAL_EV_VALIDATED_EDGE`) or `NO_TRADE`
   (`NEGATIVE_EXPECTED_VALUE`/`INFEASIBLE_GEOMETRY`).

### The one thing your strategy must supply that mock strategies didn't: `expected_edge`

`RealEVDecisionEngine` needs real probability inputs to call `ve_brain.run_ev` — it cannot invent them.
Your `Strategy.evaluate()` must populate `TradeHypothesis.expected_edge` as:

```python
expected_edge = {
    "edge_schema": "real-ev-expected-edge-v1",
    "n": <float>,               # total historical sample count backing this edge
    "n_target": <float>,        # count that reached target
    "n_horizon": <float>,       # count that reached the holding-window horizon without target/stop
    "sum_horizon_r": <float>,   # sum of R-multiples realized by the horizon-outcome subset
    "credibility": <float>,     # 0.0-1.0, this evidence's own credibility weight (drives the LCB guard)
}
```

These five numbers must come from the strategy's own ratified validation evidence (Alpha → Statistician →
Red Team → CEO chain, per the onboarding contract's item 4/9) — **never estimated, approximated, or
invented at integration time**. This is the one field `real_ev_engine.py` cannot validate for
truthfulness (it can only validate *shape*) — that truthfulness is exactly what the Alpha/Statistician/Red
Team chain exists to establish before a strategy's `CatalogEntry.status` is ever set to `VALIDATED` in the
first place.

## Mechanical proof this works for a never-hardcoded identity (mandate section 13)

`future_strategy_fixture.py` is the working, runnable proof — reuse its shape, not its content, when
onboarding a real strategy:

```python
from ai_trader.new_brain_live.strategy_platform.future_strategy_fixture import (
    FutureValidatedStrategyPositiveEdge, catalog_entry_for_future_strategy,
)

strategy = FutureValidatedStrategyPositiveEdge()          # id="FIXTURE_FUTURE_VALIDATED_STRATEGY_POSITIVE"
entry = catalog_entry_for_future_strategy(strategy)        # status=VALIDATED, real fingerprints
catalog = StrategyCatalog(entries=(entry,))
engine = RealEVDecisionEngine(catalog=catalog, market_state=market_state, cost_model=cost_model)

hypothesis = strategy.evaluate(StrategyEvaluationInput(market_state=market_state, tower_context=None, config={}))
decision = engine.decide(hypothesis)   # -> EVDecision(decision="TRADE_DECISION", reason_codes=("REAL_EV_VALIDATED_EDGE",))
```

`ve_brain` has never heard of `FIXTURE_FUTURE_VALIDATED_STRATEGY_POSITIVE` — it reaches a real
`TRADE_DECISION` purely because it is `VALIDATED` in `catalog` and carries a genuinely positive-EV
`expected_edge`. `real_ev_engine.py`'s own code contains zero references to this or any other specific
`strategy_id` (mechanically verified, `test_no_strategy_id_branch_exists_in_real_ev_engine_source`). A
real future strategy reaches `TRADE_DECISION` through **exactly** this same path, with **zero** change to
`real_ev_engine.py`, `pipeline.py`, `router.py`, the Risk Engine, or the Execution Adapter.

## What does NOT change, still, per the onboarding contract

Per the onboarding contract's own "what does NOT need to change" section, onboarding a strategy — now
including reaching a real `TRADE_DECISION` — never touches: `new_brain_bridge`'s N1–N6 chain,
`market_state.py`, `strategy_platform.router`, `strategy_platform.risk_execution_adapter`,
`strategy_platform.shadow_ledger`, or `ve_brain.n6`/`_canonical_catalog`. This is structurally true, not a
promise: none of those modules import anything from `real_ev_engine.py`, only the reverse.

## Still explicitly out of scope (mandate section 22 — unchanged by this handoff)

- Which strategy is `VALIDATED` first, and when — a Statistician/Red-Team/CEO decision, not an
  engineering one.
- The conflict-arbitration policy when two `VALIDATED` strategies co-signal on the same `MarketState`
  (`pipeline.py`'s `POLICY_PENDING_VALIDATED_STRATEGY_PORTFOLIO` still applies unchanged — this mandate
  did not touch it, and the fixture proofs deliberately used single-strategy catalogs to avoid conflating
  the two concerns).
- Enabling `BrokerOrderSubmissionGate` — remains `enabled=False`, structurally, everywhere.
- Any live or demo order.
