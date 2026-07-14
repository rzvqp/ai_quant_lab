# Strategy API v1 — runtime query interface (definition only)

The runtime API is the ONLY behavioural channel between the AI Trader and a strategy. It complements the static
Execution Contract (`STRATEGY_INTERFACE_v1.md`): the contract says what a strategy IS; the API answers what it
SAYS RIGHT NOW, given market context the Trader supplies. **This document defines signatures and semantics only —
no implementation.** Response shapes are normatively specified in `runtime_responses.v1.schema.json`.

- **api_version:** `1.0.0` (tracks `interface_version`).
- **Purity:** every method is a deterministic function of `(contract, context, trader_state)`. A strategy holds
  NO internal state, fetches NO data, and places NO orders. All state (positions, cooldown clocks, kill switches)
  lives in the AI Trader and is passed in.
- **Encapsulation:** the Trader learns nothing about internals. It calls methods and reads typed responses.
- **No side effects:** methods never mutate anything; they return values.

---

## 0. Common inputs

```
Context           # supplied by the AI Trader, shaped by required_context()
  as_of           timestamp of the bar/tick being evaluated
  bars            map<timeframe, OHLCV window>   # exactly the required_data windows, no more
  session         current session tag
  regime          detected market regime (Regime enum) — the Trader's classification
  account         { equity, risk_budget_R }      # for sizing translation only
TraderState       # owned by the Trader, passed in for stateful queries
  open_positions  list of this strategy's open positions (ids, direction, entry, age_bars)
  last_signal_at  timestamp of the strategy's last emitted signal (for cooldown)
  kill_switch     bool (operator/monitor override)
```

A strategy MUST declare, via `required_context()`, exactly which `bars`/fields it needs; the Trader MUST provide
those and MAY withhold everything else. If the Context is insufficient, the method returns a `NEED_CONTEXT`
outcome rather than guessing.

---

## 1. Methods

### `required_context() -> ContextRequirement`
Pure function of the contract (mirrors `semantics.required_data`). Tells the Trader exactly what data windows and
fields to assemble before any evaluation. Deterministic, cheap, cacheable.
- **returns** `ContextRequirement { timeframes[], fields_by_timeframe, lookback_bars_by_timeframe, htf[], warmup_bars }`.

### `detect(context) -> DetectResult`
"Are you active, and is a setup forming right now?" Cheap gate that decides whether a full signal evaluation is
worth running this bar. Does NOT commit to a trade.
- **returns** `DetectResult { active: bool, setup_forming: bool, reason, insufficient_context: bool }`.
- `active=false` when `lifecycle.status ∈ {INVALID, DISABLED, NOT_IMPLEMENTED}` or the session/regime is out of
  scope. `insufficient_context=true` ⇒ the Trader must supply more per `required_context()`.

### `generate_signal(context) -> Signal`
"Do you have a signal, long or short, with entry/stop/target and why?" The core method.
- **returns** `Signal` (see schema): `{ present, direction, entry, stop, target, risk_R, confidence, strength,
  reason, regime, required_confirmations_met, valid_until, invalidations[] }`.
- If `present=false`, `direction=NONE` and the price fields are `null`; `reason` still explains why not.
- `entry/stop/target` are prices; `risk_R` is 1.0 by construction of the sizing model (the stop defines 1R).
- The strategy proposes; it never sizes in currency or sends orders (that is the Risk Manager / Execution Planner).

### `get_score(context) -> Score`
"How strong/reliable is this signal?" A normalised score the Confidence Engine can compare ACROSS strategies.
- **returns** `Score { value: 0..1, components{ setup_quality, confirmation, regime_fit, maturity_prior,
  health_penalty }, basis }`.
- `value` blends live setup quality with the static `evidence.confidence` prior and `current_health`. A strategy
  with `maturity=EXPLORATORY` and negative OOS carries a low `maturity_prior`, capping its score — the interface
  refuses to let an unvalidated strategy look confident.

### `can_trade(context, trader_state) -> Gate`
"Are you allowed to signal at all right now?" Enforces cooldown, session/regime scope, invalid conditions, health
and kill-switch — independent of whether a setup exists.
- **returns** `Gate { allowed: bool, reasons[] }`. `allowed=false` if in cooldown, out of session/regime,
  `current_health ∈ {DISABLED, INVALID}`, `status` non-tradable, or any `execution.invalid_conditions` holds.

### `can_open_position(context, trader_state) -> Gate`
"Given open positions, may you open ANOTHER one now?" Enforces `max_concurrent_positions` and per-direction
overlap on top of `can_trade`.
- **returns** `Gate { allowed: bool, reasons[], slots_remaining }`. `allowed=false` if open positions ≥
  `max_concurrent_positions` or an overlapping same-direction position is still live.

### `explain_signal(context) -> Explanation`
"Why this signal?" Fills `semantics.signal_reason` with the concrete evaluated facts, for the Explainability
Engine and audit logs. Human + structured.
- **returns** `Explanation { headline, mechanism, triggered_conditions[], confirmations[], regime, counterfactual,
  contract_ref{ id, version } }`. Contains NO research internals — only evaluated contract facts.

### `health(context?, trader_state?) -> HealthReport`
"What is your current operational health?" Distinct from maturity (research confidence). Reflects data
availability, staleness, recent live drift (if the Trader feeds performance back), cooldown, and kill-switch.
- **returns** `HealthReport { state: Health, checks{ data_ok, not_stale, within_scope, not_killed,
  live_drift_ok }, last_review, notes }`. `state=INVALID` for invalid strategies; `STALE` if `last_review` is old
  or context is missing; `DEGRADED` if live drift breaches a threshold the Monitor set.

---

## 2. Call sequence (per bar, per strategy) — reference flow
```
required_context()                     # once at load (cacheable)
 └─ Trader assembles Context
health(...)            → if INVALID/DISABLED: skip strategy
can_trade(...)         → if not allowed:      skip (cooldown/scope/invalid)
detect(context)        → if not setup_forming: skip (cheap gate)
generate_signal(context) → Signal.present ?   continue : skip
get_score(context)     → Score.value          (for ranking across strategies)
can_open_position(...)  → if allowed:          hand (Signal, Score) to the Portfolio/Risk layer
explain_signal(context) → attach Explanation to the audit trail
```
The Trader orchestrates; strategies only answer. Ordering is the Trader's choice, but `can_trade`/`health` gates
MUST be honoured before a signal is acted on.

## 3. Error & degradation semantics
- **Insufficient context:** methods return an explicit `insufficient_context`/`NEED_CONTEXT` outcome; never throw
  a domain guess. The Trader re-supplies context or skips.
- **Contract invalid at load:** the Trader quarantines the strategy (`current_health=INVALID`); its API returns
  inactive/`allowed=false` for everything.
- **Determinism:** identical `(contract, context, trader_state)` ⇒ identical responses (required for replay,
  audit, and the Learning Engine).
- **No throws across the boundary for expected conditions:** out-of-scope, cooldown, no-setup, missing data are
  all NORMAL responses, not errors.

## 4. What the API deliberately does NOT expose
- No access to the engine, parquets, knowledge graph, or research reports (the separation law).
- No order placement, no position accounting, no capital allocation — those belong to the Trader's Risk Manager,
  Portfolio Manager and Execution Planner.
- No self-mutation, no learning inside the strategy — adaptation happens in the Trader's Learning Engine, which
  may only feed back through new contract versions (a research-gated act), never by writing to a live strategy.
