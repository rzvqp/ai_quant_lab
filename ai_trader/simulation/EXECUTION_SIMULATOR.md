# Execution Simulator v1 — the virtual Broker Adapter (design)

The Execution Simulator is the simulation-only stand-in for the venue. It **implements the exact Broker Adapter
contract** the Execution Engine (Phase 5.6) talks to, but instead of a real broker it fills `OrderRequest`s
deterministically against historical bars. Swapping it for a real Broker Adapter is the ONLY change to go live.
Design only — no code, no broker.

---

## 1. Purpose & contract
- Consume `OrderRequest`s from the Execution Engine via the `broker_adapter_contract_version` (Phase 5.6) and
  return the SAME events a real broker would: acknowledgements, fills (full/partial), rejects, cancels, expiries.
- Deterministic: given `(OrderRequest, the relevant historical bars, cost/fill/slippage models, seed)`, the fill
  outcome is identical every run.
- It performs **virtual** execution only — no venue, no network, no MetaTrader.

## 2. Inputs & outputs
**Inputs:** `OrderRequest` (Phase 5.6 `ORDER_SCHEMA.json`); the historical bar(s) at/after the order's `as_of`
(from the Replay Data Source, lookahead-safe); the run's `cost_model` / `fill_model` / `slippage_model` / seed.
**Outputs:** `OrderStatus` transitions + `Fill` events (price, qty, fee, timestamp) — exactly the Broker Adapter
event stream the Execution Engine's Lifecycle Tracker consumes.

## 3. Fill model (deterministic, lookahead-safe)
Orders are matched only against bars whose `available_at ≤` the order's activation time — never the signal bar
(no lookahead). Conventions mirror the frozen research engine so simulated results are comparable to the Strategy
Library metrics:
| order type | fill rule (deterministic) |
|---|---|
| **Market** | fills at the **next bar open** ± spread (direction-adjusted) ± slippage; the reference matches the engine's entry-at-next-open |
| **Limit** | fills only if the bar's range **touches** `limit_price` (buy: low ≤ limit; sell: high ≥ limit), at `limit_price`; else remains working |
| **Stop** | triggers when the bar's range crosses `stop_price`; then fills as a market order at the trigger ± slippage |
| **Stop-Limit** | on stop trigger becomes a limit at `limit_price` (touch rule) |
| **Bracket** | parent fills as above; on fill, the protective stop + target become an OCO pair; intrabar priority = **stop before target** (conservative, matches the research engine) when a bar spans both |
| **OCO** | a fill on one leg cancels the other, deterministically |
- **Intrabar assumption:** when a single bar could hit both a stop and a target, the **stop is assumed hit first**
  (worst-case, engine-parity). This is a fixed, documented rule — never random.
- **Entry timing:** `next_open` by default (engine-parity); configurable in `fill_model` but pinned per run.

## 4. Spread, commission, slippage
- **Spread:** applied on entry and exit per the `cost_model.spread_model` (fixed ticks or a per-symbol schedule).
  Buys fill at ask, sells at bid (deterministic from the mid + half-spread).
- **Commission:** charged per fill per `cost_model.commission_model` (per-lot or per-notional), deducted from the
  account by the Portfolio Simulator.
- **Slippage:** per `slippage_model`:
  - `fixed` — a constant tick adjustment (deterministic).
  - `atr_fraction` — a fraction of ATR at the fill bar (deterministic from the bar).
  - `seeded_random` — drawn from a PRNG seeded by `hash(run_seed, client_order_id, as_of)` → reproducible and
    order-independent (NOT wall-clock or global RNG). Bounded by `max_slippage` from the order constraints.
- The default v1 cost model mirrors the research engine (spread 1 tick + slippage 1 tick per side) so the
  simulator reproduces the Strategy Library's cost assumptions.

## 5. Partial fills
- Deterministic partial-fill policy (`fill_model.partial_fill_policy`): e.g. fill up to the bar's available
  liquidity proxy, or full-fill for liquid instruments (default). When partial, emit a `PARTIALLY_FILLED` status +
  a `Fill` for the filled quantity; the remainder is handled per the order's TIF (IOC/FOK cancel; GTC/DAY keep) —
  exactly as the Execution Engine expects from a broker.
- Every partial `Fill` is reported so the Portfolio Simulator updates position truth incrementally.

## 6. Time-in-force & expiry
- **IOC:** fill what the current bar allows; cancel the remainder.
- **FOK:** fill fully on the current bar or cancel entirely.
- **GTC:** remain working across bars until filled/cancelled.
- **DAY:** expire at the simulated session/day boundary if unfilled.
- `valid_until` from the order constraints is honored deterministically against the replay clock.

## 7. Order lifecycle emission (Broker Adapter contract)
The simulator drives the same lifecycle the Execution Engine tracks: `SUBMITTED → ACKNOWLEDGED →
(PARTIALLY_FILLED)* → FILLED | CANCELLED | REJECTED | EXPIRED`. Rejects are deterministic (e.g. limit never
touched within TIF → `EXPIRED`; market closed in the replay calendar → `REJECTED(MARKET_CLOSED)`). Acks are
immediate in sim (no latency) unless a `latency_model` is configured (deterministic, seeded).

## 8. Determinism guarantees
- Fill price, quantity, fees, and timing are pure functions of `(OrderRequest, bars, cost/fill/slippage models,
  seed)`. No wall-clock, no global RNG.
- Processing order within a bar is fixed (by the Execution Engine's submission order, itself from the Scoring
  Engine's deterministic rank), so multi-order bars are reproducible.
- The intrabar stop-before-target rule and next-open entry are fixed conventions, versioned by `fill_model_version`.

## 9. Live parity (the swap)
The Execution Simulator and a real Broker Adapter implement the SAME contract. Going live replaces this module
with the real adapter; the Execution Engine, and everything upstream, is unchanged. The simulator's fill/cost
conventions are the modeled expectation of live fills — the closer the model, the more faithful the proof
(conformance to the research engine's conventions is the v1 baseline; richer microstructure models are future,
versioned, and optional).
