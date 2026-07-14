# Execution Engine — Phase 6.6 Implementation Handoff

**Purpose:** everything the next Claude session needs to begin implementing the Execution Engine
immediately, with zero context loss. **Documentation only — no implementation code was written to
produce this document.** Written 2026-07-15 at the close of the Risk Manager (Phase 6.5) session, HEAD
commit `7c225d1` on `ai-trader-implementation`.

**Before writing any code:** get explicit CEO approval for Phase 6.6 (see `NEXT_SESSION.md` §9/§11 —
this is a standing, non-negotiable gate). This document prepares you to start immediately once that
approval is granted; it does not itself constitute approval.

---

## 1. Architecture summary

The Execution Engine is the sixth module of the AI Trader: it turns an **approved** `RiskDecision`
(`decision=ALLOW`) into a validated, idempotent `OrderRequest`, submits it via an abstract Broker
Adapter, and manages its lifecycle to exactly one terminal state. It **re-decides nothing** — no
signals, no scoring, no risk, no learning. It is a deterministic order-construction + lifecycle-
management module; only the (future) venue's responses are non-deterministic, and every response is
always reconciled to a definite state.

Full frozen spec, all in `ai_trader/execution_engine/` (Phase 5.6, CEO-approved, do not redesign):

| file | what it defines |
|---|---|
| `README.md` | overview, responsibilities, boundaries, pipeline position, package contents |
| `EXECUTION_ENGINE_ARCHITECTURE.md` | full architecture: inputs/outputs, internal components, pipeline, data flow, validation rules (§8), failure modes, startup/shutdown, performance model, versioning, interaction matrix |
| `ORDER_LIFECYCLE.md` | the 11 order states + transitions, supported order types (Market/Limit/Stop/Stop-Limit/OCO/Bracket), time-in-force (IOC/FOK/GTC/DAY), the default RiskDecision→order-type mapping policy |
| `ORDER_SCHEMA.json` | JSON Schema (Draft 2020-12) for `OrderRequest` — the exact shape to build |
| `EXECUTION_API.md` | the public API surface (definition only): `execute`, `build_order`, `validate_order`, `cancel`, `status`, `reconcile`, `report`, `emergency_flatten`, `statistics`, `health`, `versions` |
| `EXECUTION_SEQUENCE.md` | 11 operational sequences: startup, single order, bracket, partial fill, cancel, rejection, broker-unavailable/timeout/network-fault, emergency flatten, duplicate/restart safety, shutdown, end-to-end condensed |
| `EXECUTION_STATE_MACHINE.md` | (A) engine lifecycle (IDLE→RECONCILING→READY⇄DEGRADED→EMERGENCY_FLATTEN, DRAINING→STOPPED) and (B) per-order state machine (mirrors ORDER_LIFECYCLE.md) |
| `EXECUTION_FAILURE_POLICY.md` | the fail-safe catalog: broker unavailable, timeout, network fault, rejection, partial fill, cancel, duplicate, validation failure, internal error, portfolio-unavailable, emergency flatten — plus bounded retry policy |

Read all 8 in full before writing code, exactly as done for every prior module.

---

## 2. Dependencies — what's available vs. what's still missing

### 2a. Available and ready to consume

- **Risk Manager** (`ai_trader/risk_manager/`) — READY, Phase 6.5. `RiskManager.evaluate()` returns a
  `RiskDecisionBatch` of `RiskDecision` objects; `RiskManager.allow_trade()` returns a single
  `RiskDecision`. Only `decision=ALLOW` decisions are actioned by the Execution Engine (DENY is a no-op
  per the architecture). See §3 below for the exact `RiskDecision` shape.
- **Scoring Engine, Signal Engine, Strategy Manager, Market Scanner** — all READY, all upstream of Risk
  Manager, all explicitly **forbidden** dependencies for the Execution Engine (interaction matrix,
  `EXECUTION_ENGINE_ARCHITECTURE.md` §13). Do not import from them.
- **`ORDER_SCHEMA.json`** — the complete, frozen output schema. Ready to drive `fastjsonschema`
  compilation exactly like every prior module's hot-path validation.

### 2b. NOT available — must be resolved before/during implementation

- **Portfolio Manager module does not exist.** `EXECUTION_ENGINE_ARCHITECTURE.md` names it as a
  required dependency (read `PortfolioState`; report fills to it) but **no `ai_trader/portfolio_manager/`
  directory, schema, or implementation exists anywhere in this repository, and none is scheduled.**
  This is the single most important open item for Phase 6.6. Two options, both legitimate
  "IMPLEMENTATION CHOICE" gap-fills in the established pattern (see `RISK_MANAGER_VALIDATION_REPORT.md`
  §2 for the precedent):
  1. **Reuse `ai_trader.risk_manager.types.PortfolioState`** (and `OpenPosition`/`ClosedPosition`) —
     Risk Manager IS an allowed direct dependency for the Execution Engine per the interaction matrix,
     so importing its already-published types is not a boundary violation. The shape already covers
     equity, open positions, and the computed properties (`portfolio_risk_pct`, `leverage`, `drawdown_pct`)
     that a "read PortfolioState" consumer would want.
  2. **Design a new, Execution-Engine-owned `PortfolioState`-equivalent type**, analogous to how Risk
     Manager designed its own `RiskContext`/`SymbolRiskSnapshot` when no upstream schema existed.
  Recommendation for the next session to consider (not a decision made here): option 1 is simpler and
  avoids a second parallel definition of the same concept drifting out of sync, but creates a
  Risk-Manager-shaped dependency that the frozen architecture doc's own interaction matrix does
  technically allow but did not originally anticipate (it says "Portfolio Manager", not "Risk Manager's
  PortfolioState type"). **Raise this explicitly with the CEO or document the choice clearly as
  IMPLEMENTATION CHOICE #1 in the eventual `EXECUTION_ENGINE_VALIDATION_REPORT.md`** — do not silently
  pick one without a paper trail, matching every prior module's discipline.
- **Broker Adapter is abstract-only.** No real venue integration exists or should be built in Phase 6.6.
  `BrokerCapabilities` (supported order types/TIF, tick_size, lot_step, min/max qty, market_status) is a
  **declared capability set** per the architecture, not a live connection. Build against a fake/test
  double implementing this contract (analogous to how Risk Manager was tested against a real
  `OpportunityScore` fixture-builder rather than a live Scoring Engine process).
- **No real strategy signals yet.** Every real strategy's `StrategySignal` is currently `INVALID`/
  `CORRUPTED_OUTPUT` (Signal Engine's `StrategyRuntimeHandle.api` has no real `detect`/`generate_signal`
  logic — see `NEXT_SESSION.md` §8 item 1). This means every real `RiskDecision` flowing through the
  live pipeline today is `DENY`, never `ALLOW`. **The Execution Engine's own test suite must exercise
  the ALLOW path using hand-built/fixture `RiskDecision` objects** (constructed directly, matching the
  precedent set by every prior module's `tests/fixtures/`), not by trying to coax a real ALLOW out of
  the live upstream chain — that path is fail-safe-INVALID by design today and is out of scope to fix.

---

## 3. Expected inputs (exact shapes, from already-published code/schema)

### `RiskDecision` (from `ai_trader.risk_manager.types`, already implemented — import directly)
```python
@dataclass(frozen=True, slots=True)
class RiskDecision:
    risk_schema_version: str
    risk_engine_version: str
    risk_policy_version: str
    decision_id: str
    score_id: str
    signal_id: str
    strategy_id: str            # pattern ^S\d+$
    symbol: str
    timestamp: int
    as_of: int
    engine_state: EngineState   # READY / SUSPENDED / EMERGENCY_STOP
    decision: Decision          # ALLOW / DENY
    direction: Direction        # LONG / SHORT / NONE
    applied_rules: tuple[AppliedRule, ...]
    refs: RiskRefs
    denied_reasons: tuple[DeniedReason, ...] = ()
    sizing: Sizing | None = None        # present only for ALLOW
    constraints: Constraints | None = None  # present only for ALLOW
    portfolio_impact: PortfolioImpact | None = None
```
`Sizing`: `method` (SizingMethod.FIXED_FRACTIONAL), `risk_per_trade_pct`, `risk_R`, `size_units`,
`min_size`, `max_size`, plus optional `quality_factor`, `risk_budget_currency`, `stop_distance`,
`size_lots`, `notional`, `leverage`, `partial_exit_plan`. **`size_units` is the field
`ORDER_SCHEMA.json#/properties/quantity` maps from.**

`Constraints`: `entry`, `stop`, `target` (all `float | None`), `max_hold_bars`, `valid_until`,
`max_slippage`, `allowed_session`, `reduce_only`. **These map directly to `OrderRequest`'s
`limit_price`/`stop_price`/`bracket.{take_profit,stop_loss}`/`constraints.{max_slippage,valid_until,
allowed_session,max_hold_bars,reduce_only}`.**

`RiskDecisionBatch`: `as_of`, `decisions: tuple[RiskDecision, ...]`, `counts_by_decision`,
`engine_state`, `generated_at` — what `RiskManager.evaluate()` returns; the Execution Engine will
process a batch's ALLOW decisions in the same fixed order Risk Manager itself uses (ascending `rank`
carried implicitly by decision order in the batch).

### `BrokerCapabilities` (abstract — does not exist as code yet; must be designed in Phase 6.6)
Named in `EXECUTION_ENGINE_ARCHITECTURE.md` §3 as: supported order types + TIF, `tick_size`, `lot_step`,
min/max quantity, market hours/status, supported contingent orders (OCO/bracket). `ORDER_SCHEMA.json`'s
`broker_capabilities_ref` object shows the exact fields expected to be echoed onto a built order
(`tick_size`, `lot_step`, `min_qty`, `max_qty`, `contract_version`). Design this as a frozen dataclass +
a fake/test-double instance, matching how `RiskConfig`/`ScoringConfig`/etc. were built for every prior
module.

---

## 4. Expected outputs (exact shape, from `ORDER_SCHEMA.json`)

`OrderRequest` — full required fields: `order_schema_version` (const `"1.0.0"`), `execution_engine_version`,
`order_request_id`, `client_order_id` (idempotency key, derived from `decision_id`), `decision_id`,
`strategy_id`, `symbol`, `timestamp`, `as_of` (MUST equal the `RiskDecision.as_of`), `side` (BUY/SELL),
`direction` (LONG/SHORT), `intent` (OPEN/CLOSE/REDUCE/SCALE_IN/SCALE_OUT), `order_type`
(MARKET/LIMIT/STOP/STOP_LIMIT/OCO/BRACKET), `time_in_force` (IOC/FOK/GTC/DAY), `quantity` (>0),
`constraints` (object: `max_slippage`, `reduce_only`, `post_only` required; `valid_until`,
`allowed_session`, `max_hold_bars` optional), `refs` (object: `risk_schema_version`,
`risk_policy_version` required; `account` optional). Conditional requirements (`allOf` in the schema):
LIMIT needs `limit_price`; STOP needs `stop_price`; STOP_LIMIT needs both; BRACKET needs the `bracket`
object; OCO needs `oco_link`; OPEN/SCALE_IN intents require `side` to agree with `direction`
(LONG⇒BUY, SHORT⇒SELL).

Other emitted types (`EXECUTION_API.md` §0, no schema file yet — design as dataclasses like every
module's own `types.py`):
```
OrderStatus     { order_request_id, client_order_id, state, filled_qty, remaining_qty, avg_price, reasons[] }
ExecutionResult { order_request_id, terminal_state, filled_qty, avg_price, fees, reasons[] }
ExecutionReport { as_of, results: ExecutionResult[], fills[], counts_by_state }
ValidationResult{ valid, reasons[] }
Statistics      { orders_total, by_state, fills, rejects, failures, avg_submit_ms }
EngineHealth    { overall, state, degraded_reasons[], broker_available, supported_versions }
```

---

## 5. Pipeline position

```
Risk Manager → [Execution Engine] → Broker Adapter (future) → venue
   RiskDecision(ALLOW)     OrderRequest / lifecycle / ExecutionResult
        ▲                                    │ fills/status
PortfolioState (Portfolio Manager*, read) ◀──┘ ExecutionReport (fills reported to Portfolio Manager*)
```
*Portfolio Manager does not exist yet — see §2b.

Allowed direct dependencies (interaction matrix, `EXECUTION_ENGINE_ARCHITECTURE.md` §13): **Risk
Manager, Portfolio Manager (or its stand-in per §2b), Broker Adapter (abstract, future)**. Forbidden,
always: Research Lab, Knowledge Base, Strategy Library, Market Scanner, Signal Engine, Scoring Engine,
Learning Engine.

---

## 6. Internal component breakdown (from `EXECUTION_ENGINE_ARCHITECTURE.md` §5 — suggested module split)

Following the same one-file-per-component pattern used by every prior module (e.g. Risk Manager's
`filters.py`/`limits.py`/`guards.py`/`sizing.py`/`constraints.py`/`pipeline.py`/`assembler.py`/
`validator.py`/`engine.py`):

| architecture component | suggested module |
|---|---|
| Intake (accept ALLOW; ignore DENY; bind PortfolioState) | folded into `engine.py`, mirrors Risk Manager's own Global-State-Gate-then-dispatch pattern |
| Order Builder (decision+constraints → OrderRequest; idempotent `client_order_id`; order type/TIF selection) | `builder.py` |
| Order Validator (tick/lot/qty/price/slippage/time/market/direction/duplicate — §8 of the architecture doc) | `validator.py` |
| Order Router / Queue (submit to Broker Adapter; rate limits; idempotency) | `router.py` |
| Lifecycle Tracker (ACK/fills/partials/cancel/reject/expire) | `lifecycle.py` |
| Reconciler (query broker on uncertainty; resolve unknown states before any resend) | `reconciler.py` |
| Order Ledger (own record of live/terminal orders) | part of `engine.py`'s state, or `ledger.py` if it grows large |
| Result/Reporter (ExecutionResult + ExecutionReport → Portfolio Manager) | `reporter.py` |
| Value types (mirrors `ORDER_SCHEMA.json` + the API's own summary types) | `types.py` |
| Config / errors | `config.py`, `exceptions.py` |
| Schema loading + compiled validation | `schema_validation.py` (fastjsonschema pattern, §2a) |
| Public API facade + lifecycle/statistics/health | `engine.py` (`ExecutionEngine`) |
| Broker Adapter abstract contract + a fake/test double | `broker_adapter.py` (protocol/ABC) + `tests/fixtures/fake_broker.py` |

This is a suggested starting decomposition based on the architecture's own component diagram, not a
frozen requirement — adjust as the implementation reveals better boundaries, exactly as every prior
module did.

---

## 7. Implementation order (suggested, mirrors every prior module's own successful sequence)

1. `types.py` — mirror `ORDER_SCHEMA.json` + the API's summary types exactly.
2. `config.py`, `exceptions.py` — config objects for retry bounds, rate limits, reconciliation timeouts
   (all undocumented numeric placeholders per `NEXT_SESSION.md` §8 item 4 — treat as IMPLEMENTATION
   CHOICE, document explicitly).
3. `schema_validation.py` — `fastjsonschema` compiled validator for `OrderRequest`, from the start.
4. **Resolve the Portfolio Manager gap** (§2b) before writing `builder.py` — this blocks the Order
   Builder's "position-limit consistency" check (`EXECUTION_ENGINE_ARCHITECTURE.md` §8).
5. `broker_adapter.py` — the abstract contract (Protocol/ABC) + a fake/test-double implementation for
   tests, matching the fixture-based-real-object-testing pattern established by every prior module's
   integration tests.
6. `builder.py` — Order Builder: decision → `OrderRequest`, idempotent `client_order_id = f(decision_id)`,
   order type/TIF mapping (`ORDER_LIFECYCLE.md` §6 default policy — pin down the "entry ≈ current
   market" threshold as a documented config constant).
7. `validator.py` (order mechanics) — the §8 checks table, in the order the architecture lists them.
8. `router.py`, `lifecycle.py`, `reconciler.py`, `reporter.py` — the rest of the pipeline, per
   `EXECUTION_SEQUENCE.md`'s sequences (single order, bracket, partial fill, cancel, reject,
   broker-unavailable/timeout/network, emergency flatten, startup/shutdown reconciliation).
9. `engine.py` (`ExecutionEngine`) — the public facade wiring everything together, with the engine
   lifecycle state machine (`EXECUTION_STATE_MACHINE.md` §A: IDLE→RECONCILING→READY⇄DEGRADED→
   EMERGENCY_FLATTEN, DRAINING→STOPPED). **Apply the Risk Manager lesson explicitly here**: `execute()`,
   `cancel()`, `reconcile()`, and `emergency_flatten()` are FOUR entry points that can each mutate the
   Order Ledger — design one shared internal helper for state mutation + validation from the start (see
   `NEXT_SESSION.md` §6, the "sibling-entry-point inconsistency" lesson) rather than retrofitting it
   after an adversarial review finds the gap, as happened with Risk Manager.
10. Unit tests per module, then `test_engine_integration.py` against real `RiskDecision` objects built
    via a `RiskManager` (real Risk Manager, real Scoring Engine, fixture Signal Engine handle) —
    matching the "real upstream, fixture-driven" integration-test pattern of every prior module.

---

## 8. Validation strategy (mandatory, identical process to every prior module — do not skip steps)

1. Implement source modules.
2. Write unit tests per module + one integration test file against real upstream types.
3. Run `pytest`, `mypy --strict`, `coverage` until: all green, mypy clean on source (excluding tests is
   acceptable per the established per-module scoping — see `NEXT_SESSION.md` §4), coverage ≥95%.
4. **Independent adversarial code review — mandatory, not optional** (`NEXT_SESSION.md` §6/§9). Spawn a
   fresh-eyes subagent with NO memory of writing the code. It must read all 8 frozen spec docs in full,
   then every source file, hunting specifically for:
   - order-mechanics/formula deviations from `EXECUTION_ENGINE_ARCHITECTURE.md` §8's validation table
   - fail-safe violations against `EXECUTION_FAILURE_POLICY.md`'s catalog (§2 of that doc)
   - idempotency violations (does every entry point actually derive/check `client_order_id` correctly?)
   - determinism violations (construction/validation must be deterministic; only outcomes may vary)
   - **sibling-entry-point inconsistency** (§6/§9 of `NEXT_SESSION.md` — the newest, most likely-to-recur
     class of bug: does `execute()`, `cancel()`, `reconcile()`, and `emergency_flatten()` all route
     through the same validated/exception-safe path?)
   - state-machine correctness (engine lifecycle AND per-order lifecycle, both tables in
     `EXECUTION_STATE_MACHINE.md`)
   - reconciliation correctness (never a blind resend; every ambiguous state resolved before action)
5. Fix every genuine issue found, with a dedicated regression test per fix (name tests descriptively,
   e.g. `test_a_reconcile_call_never_creates_a_duplicate_order`, matching the naming convention used in
   every prior module's own regression tests).
6. Rerun the full validation suite until clean again.
7. Rerun the FULL `ai_trader/` suite (currently 967 tests) to confirm zero regressions in any prior
   module.
8. Write `EXECUTION_ENGINE_VALIDATION_REPORT.md` at the repo root, following the exact template used by
   all five prior reports (what was built → design decisions marked IMPLEMENTATION CHOICE → adversarial
   review findings + fixes table → final numbers → protected-invariants confirmation → verdict).
9. Update `NEXT_SESSION.md` and `CHANGELOG.md`.
10. Commit only once the module reaches production quality and reaches a READY verdict.
11. **Stop.** Do not self-authorize Simulation Framework, Learning Engine, Broker Adapter, or MT5
    integration — wait for explicit new CEO approval, exactly as done at the end of every phase so far.

---

## 9. Testing strategy specifics

- **Idempotency tests are the highest-value new test class for this module** (no prior module has a
  concept exactly like `client_order_id` retries) — write explicit tests proving that calling `execute()`
  twice with the same `decision_id`, or a simulated process restart followed by `RECONCILING`, never
  produces two orders.
- **Reconciliation-under-ambiguity tests** — simulate a broker timeout/unknown-ack and prove the engine
  queries status before any resend, for every ambiguous scenario in `EXECUTION_FAILURE_POLICY.md` §2.
- **State-machine coverage** — both the engine lifecycle (7 states) and the per-order lifecycle (11
  states) need explicit transition tests, matching the transition tables in `EXECUTION_STATE_MACHINE.md`.
- **Fail-safe coverage** — every row of `EXECUTION_FAILURE_POLICY.md`'s failure catalog (§2, 12 rows)
  should have at least one direct test.
- **Determinism tests** — identical `(RiskDecision, PortfolioState, BrokerCapabilities, ExecConfig)` must
  produce byte-identical `OrderRequest` + `ValidationResult`, exactly like every prior module's own
  `TestDeterminism` class.
- **Use a fake Broker Adapter fixture**, not a real venue — build it once, reuse it across all lifecycle/
  reconciliation/failure tests, matching the `fake_strategy.py`/`fake_opportunity.py` fixture pattern
  already established in `signal_engine/tests/fixtures/` and `risk_manager/tests/fixtures/`.

---

## 10. Non-negotiable rules specific to this module

- **Never generate signals, evaluate strategies, or score.**
- **Never manage portfolio risk or re-size** — it executes the Risk Manager's `sizing.size_units`
  exactly; any "position-limit" check it runs is a defensive consistency guard, never a risk re-decision
  (`EXECUTION_ENGINE_ARCHITECTURE.md` §8, explicit).
- **Never learn or adapt.**
- **Never read Research Lab / Knowledge Base / Strategy Library / Market Scanner / Signal Engine /
  Scoring Engine / Learning Engine.**
- **Never contact a venue except through the abstract Broker Adapter contract** — no real broker/MT5
  integration in this phase, full stop.
- **Never blind-resend under ambiguity** — reconcile first, always (the module's own core fail-safe
  principle, §1 of `EXECUTION_FAILURE_POLICY.md`).
- **Every order reaches exactly one terminal state** — never abandon an order in an unknown state.
- **`emergency_flatten` is commanded by the Risk Manager, never self-initiated** — the Execution Engine
  executes the flatten; it does not decide to flatten.
- Every standing rule in `NEXT_SESSION.md` §9 applies unchanged (no shortcuts, no fake benchmarks, no
  fabricated statistics, no hidden redesign, documentation-before-implementation already satisfied,
  mandatory adversarial review, stop-and-wait-for-CEO-approval between phases).

---

## 11. Quick-reference: everything this document depends on, verified present at handoff time

```
ai_trader/execution_engine/{README,EXECUTION_ENGINE_ARCHITECTURE,ORDER_LIFECYCLE,EXECUTION_API,
                            EXECUTION_SEQUENCE,EXECUTION_STATE_MACHINE,EXECUTION_FAILURE_POLICY}.md
ai_trader/execution_engine/ORDER_SCHEMA.json
ai_trader/risk_manager/types.py          (RiskDecision, Sizing, Constraints, RiskRefs, RiskDecisionBatch,
                                           PortfolioState, OpenPosition, ClosedPosition, EngineState, Decision)
ai_trader/risk_manager/engine.py         (RiskManager — evaluate(), allow_trade() produce the inputs)
RISK_MANAGER_VALIDATION_REPORT.md        (the immediately-prior module's report — read for the exact
                                           process/quality bar and the "sibling-entry-point" lesson in full)
NEXT_SESSION.md                          (project-wide status, git state, rules — read first)
```
No `ai_trader/execution_engine/*.py` exists yet. No `ai_trader/portfolio_manager/` exists. No Broker
Adapter code exists. All are legitimately, explicitly out of scope until this session's work begins.
