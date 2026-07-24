# Broker Adapter — Design (Step 1 of the CEO's new execution-first ordering)

**Status**: DESIGN ONLY, per explicit CEO instruction (2026-07-24). No code was written, no
`ai_trader/` file touched. Written to disk, deliberately left uncommitted, pending CEO review — same
treatment every prior design document in this session received before its own acceptance.

**Standing-directive conflict, disclosed up front, not silently resolved**: `PROJECT_STATE_v2.md:129`
records a standing CEO directive — "**Simulation-first**: the AI Trader must prove robust historical
profitability in simulation before any Broker Adapter/MT5/live execution work begins" — and
`NEXT_SESSION_FLOW_B.md`/`EXECUTION_ENGINE_HANDOFF.md`/`EXECUTION_ENGINE_VALIDATION_REPORT.md` all
independently repeat variants of "do not self-authorize Broker Adapter/MT5 without explicit new CEO
approval." No session artifact declares "robust historical profitability proven" as a closed milestone —
Wave D's own historical result (§3, `PROJECT_STATE_v2.md`) is the closest existing evidence, but was never
formally ratified as clearing this specific gate. The CEO's most recent, explicit instruction
("Broker Adapter (implementare peste Protocol-ul existent)... Începe cu proiectarea Broker Adapter")
supersedes the standing note for THIS design step — proceeding on that basis, disclosed rather than
silently overridden, per this project's own established practice of surfacing exactly this kind of
conflict.

---

## 1. Scope of THIS step, vs. the two steps after it

The CEO's own new ordering separates three things that are easy to conflate:

1. **Broker Adapter (this document)** — a concrete, venue-agnostic adapter ARCHITECTURE that satisfies
   the already-existing `BrokerAdapter` `Protocol` (`ai_trader/execution_engine/broker_adapter.py`,
   unmodified), plus a safe, testable **reference implementation** that requires no live venue connection
   at all. No MT5 code. No credentials. No network I/O to a real broker.
2. **Execution Integration** (next, separately authorized) — wiring a Broker Adapter instance into the
   AI Trader's own live-run orchestration (whatever eventually plays the role `SimulationHarness` plays
   for backtests) so orders actually flow through it.
3. **MT5 Live Integration** (after that) — a concrete `BrokerAdapter` implementation that actually talks
   to MT5, "connectivity and communication, no autonomous trading" per the CEO's own words — i.e., the
   FIRST time real credentials/network I/O to a real venue exist in this codebase.

This document is scoped to (1) only.

## 2. What already exists (verified this session, not assumed)

- `ai_trader/execution_engine/broker_adapter.py`: `BrokerAdapter` is a `@runtime_checkable Protocol`
  with exactly 5 methods, all synchronous, all documented as **non-raising** ("failures are reported via
  the return value... never via an exception"): `capabilities() -> BrokerCapabilities`,
  `submit_order(order: OrderRequest) -> BrokerAck`, `cancel_order(client_order_id: str) -> BrokerAck`,
  `query_status(client_order_id: str) -> BrokerOrderState | None`,
  `query_open_orders() -> tuple[BrokerOrderState, ...]`. **Pull-based by explicit design** — "the
  Reconciler always QUERIES; nothing here pushes events into the engine."
- **This Protocol is already real, load-bearing plumbing, not dead scaffolding**:
  `ExecutionEngine.configure(adapter: BrokerAdapter)` (`engine.py:73`) stores it and calls
  `adapter.capabilities()`; `reconciler.py` calls `query_status`/`query_open_orders`/`cancel_order`
  throughout its own reconciliation logic; `pipeline.py` calls `submit_order`.
- **`ai_trader.simulation.execution_simulator.ExecutionSimulator` already implements this exact Protocol,
  unmodified** — its own module docstring calls itself "the virtual Broker Adapter." This is the single
  most important existing precedent: proof the Protocol is sufficient for a real implementer, and a
  concrete model for how one is structured (order bookkeeping, state mapping, deterministic processing).
- **`OrderState`** (`execution_engine/types.py`, 11 members: `CREATED, VALIDATED, QUEUED, SUBMITTED,
  ACKNOWLEDGED, PARTIALLY_FILLED, FILLED, CANCELLED, REJECTED, EXPIRED, FAILED`) is the single, already-
  frozen order-lifecycle vocabulary. `BrokerOrderState.state` should always be reported in terms of this
  enum — a real adapter reports only the in-flight/terminal subset a real broker would ever confirm
  (never the engine-internal pre-submit states `CREATED`/`VALIDATED`/`QUEUED`), exactly matching
  `ExecutionSimulator`'s own already-established convention.
- **The Protocol has ZERO connectivity/session-lifecycle concept** — no `connect()`, no `disconnect()`,
  no health/heartbeat method, no reconnect hook. This is a genuine, confirmed gap (not merely suspected)
  — `EXECUTION_SEQUENCE.md`'s own sequence never shows a connection step, because the Simulator never
  needed one. **Any real adapter needs this and the existing Protocol must not be modified to add it**
  (breaking `ExecutionSimulator`'s own "implements `BrokerAdapter` unmodified" guarantee, and every
  existing test double/consumer that only knows the 5-method shape).

## 3. Architecture: additive connectivity layer + a venue-agnostic base

**Principle: the existing `BrokerAdapter` Protocol is never modified.** A second, new, separate
interface captures what it doesn't — connection lifecycle — and a real adapter implements BOTH:

```
BrokerAdapter (Protocol, UNCHANGED)          BrokerConnectionLifecycle (Protocol, NEW, additive)
  capabilities()                               connect() -> ConnectionResult
  submit_order(order)                          disconnect() -> None
  cancel_order(client_order_id)                is_connected() -> bool
  query_status(client_order_id)                last_heartbeat_as_of() -> int | None
  query_open_orders()

                    \                                /
                     \                              /
                      RealBrokerAdapterBase (new, abstract)
                      -- implements BOTH protocols
                      -- owns: connection state, retry/idempotency bookkeeping,
                         credential handling, logging hooks
                      -- delegates venue-specific wire protocol to a subclass
                              |
                              |  (step 3, NOT this document)
                              v
                      MT5BrokerAdapter(RealBrokerAdapterBase)
```

`BrokerConnectionLifecycle` being a SEPARATE Protocol (not folded into `BrokerAdapter` itself) means:
- `ExecutionEngine.configure()`'s own existing type hint (`adapter: BrokerAdapter`) needs no change.
- Whatever future caller manages connection lifecycle (Execution Integration's own responsibility, step
  2, not designed here) can check `isinstance(adapter, BrokerConnectionLifecycle)` opt-in, never a hard
  requirement on every `BrokerAdapter`-typed value (`ExecutionSimulator` itself should NOT need to grow
  a fake `connect()`/`disconnect()` pair it doesn't need — it stays exactly as-is, unmodified).

**`RealBrokerAdapterBase`** (abstract, new): the shared, venue-agnostic machinery every real
implementation needs, that `ExecutionSimulator` never needed because it has no network boundary:
- **Idempotent `submit_order`**: a real network call can time out with the order actually having gone
  through on the venue's own side. `client_order_id` (already a field on `OrderRequest`, unmodified) is
  the idempotency key — `RealBrokerAdapterBase` must track "have I already attempted this
  `client_order_id`" and, on a retried/duplicate submission, query the venue instead of blindly
  resubmitting, never risking a double-fill from client-side retry logic. This is a NEW concern the
  Protocol itself is silent on (its own docstring only says "non-blocking," not "idempotent") — flagged
  here as an explicit design requirement for step 1, not deferred to step 3.
- **Retry/backoff policy for transient failures** (network blip, venue rate-limit) — explicit, versioned,
  bounded (never infinite retry), reported via `BrokerAck.accepted=False` + a disclosed `reason` string on
  exhaustion, matching the Protocol's own "report failures via return value, never exception" contract.
- **Credential handling** — read from an external secret store/environment variable at construction time,
  NEVER hardcoded, NEVER logged, NEVER included in any `BrokerAck`/`BrokerOrderState`/exception message.
  This step defines the INTERFACE for credential injection (a constructor parameter accepting an opaque
  credentials object/loader callback); it does not itself implement a live credential store, since no
  live venue exists yet to authenticate against.
- **Reconnection**: `is_connected()` false → `submit_order`/`cancel_order` must return a disclosed,
  non-raising rejection (`BrokerAck(accepted=False, reason="NOT_CONNECTED")`), never attempt a call over a
  dead connection, never raise. Reconnection ITSELF (the retry loop, backoff schedule) is owned by
  `BrokerConnectionLifecycle.connect()`, callable by whatever component manages the adapter's own
  lifecycle (Execution Integration, step 2 — not decided here).
- **Clock/timestamp handling**: a real venue's own fill timestamps are wall-clock, not simulated-bar
  timestamps (`ExecutionSimulator`'s own `as_of` is a replay-clock tick, `SimFillEvent.as_of` in bar-time)
  — `RealBrokerAdapterBase` must record real UTC epoch timestamps for every state transition, disclosed
  explicitly as a different provenance from simulation's own `as_of` semantics, never silently conflated.

## 4. Reference implementation for THIS step: `NullBrokerAdapter`

To have something concrete, buildable, and testable in Step 1 without any live venue, this design
proposes ONE reference implementation: `NullBrokerAdapter(RealBrokerAdapterBase)` — a safe, in-memory,
zero-network adapter that exercises every piece of `RealBrokerAdapterBase`'s own new machinery (idempotency
tracking, retry/backoff paths under an injectable simulated-failure mode, connection state transitions,
credential-object plumbing) WITHOUT connecting to anything real:

- `connect()` always succeeds after a configurable simulated delay (proves the connection-lifecycle
  contract works end-to-end).
- `submit_order` accepts every syntactically valid `OrderRequest` and immediately marks it
  `ACKNOWLEDGED` (never fills it — filling requires a real or simulated market, out of scope; this is a
  connectivity/plumbing adapter, not a second execution simulator — `ExecutionSimulator` already owns
  that role).
- Deliberately injectable failure modes (a constructor flag to force disconnected/rejected/duplicate-
  submission scenarios) exist SPECIFICALLY so the negative-control-style tests below can exercise
  `RealBrokerAdapterBase`'s own retry/idempotency logic deterministically, mirroring this project's own
  established "synthetic fixture over waiting for a real failure" testing discipline
  (Recognition Engine Phase 1A's own negative controls, Shadow Evidence's own synthetic multi-strategy
  tests).

`NullBrokerAdapter` is NOT a second `ExecutionSimulator` and is not meant to replace it for backtesting —
it exists solely to validate `RealBrokerAdapterBase`'s own connectivity/idempotency/retry machinery before
`MT5BrokerAdapter` (step 3) has to carry that burden for the first time against a real venue.

## 5. Testing strategy for this step

- **Protocol conformance**: `NullBrokerAdapter`/`RealBrokerAdapterBase` must pass the exact same
  Protocol-shape tests `ExecutionSimulator` already does (5-method signature match, non-raising under
  every tested condition) — reusing `tests/fixtures/fake_broker.py`'s own existing test patterns as a
  template where applicable, not reinventing them.
- **Idempotency test**: submit the same `client_order_id` twice (simulating a client-side retry after a
  false-timeout) and confirm exactly one logical order results, never two.
- **Disconnected-state test**: force `is_connected() == False` and confirm every `BrokerAdapter` method
  returns a disclosed rejection, never raises, never attempts I/O.
- **Retry-exhaustion test**: force every simulated attempt to fail and confirm the adapter gives up after
  its own configured bound, reports `accepted=False` with a disclosed reason, never hangs, never retries
  forever.
- **No-live-network test** (a static/structural control, matching this project's own established
  import-independence pattern): grep-based test confirming zero references to `socket`, `requests`,
  `aiohttp`, `MetaTrader5`, or any networking import anywhere in this step's own new code — this step is
  provably offline.

## 6. Explicit non-goals for this step

- No MT5 code, no MT5 Python package dependency, no live credentials of any kind.
- No wiring into `SimulationHarness` or any live-run orchestrator (Execution Integration's own job, step
  2, separately authorized).
- No autonomous trading of any kind, live or otherwise.
- No modification of `BrokerAdapter`, `ExecutionSimulator`, `OrderState`, `BrokerOrderState`, `BrokerAck`,
  `BrokerCapabilities`, or any other existing `execution_engine`/`simulation` contract.
- No Risk Integration, no Position Manager, no Monitoring/Logging/Health Checks/Recovery/Telegram/
  Dashboard — all explicitly later steps in the CEO's own new ordering.

## 7. Risks

1. **Idempotency is a genuinely new correctness requirement `ExecutionSimulator` never had to solve** —
   a real network boundary makes "did my order actually go through" a real, not hypothetical, question.
   Mitigated by designing it into `RealBrokerAdapterBase` at this step, before MT5 specifics complicate
   it further.
2. **Credential handling, even though not exercised with real secrets yet, must be architecturally
   correct from the start** — retrofitting secure credential handling after MT5 wiring exists would be
   far riskier than designing the injection point now, before any real secret ever touches this code.
3. **The standing "simulation-first" gate is being explicitly superseded, not cleared** (§ conflict
   disclosure above) — this is the CEO's own call to make, disclosed rather than silently acted on; not a
   reason to withhold this design, but worth the CEO's own explicit acknowledgment.
4. **Connection-lifecycle design decisions made now will shape step 3's own MT5 implementation** — if
   `BrokerConnectionLifecycle`'s own shape turns out wrong for MT5's actual connection model (session
   tokens, terminal-process-based connectivity, etc.), step 3 may need to revise it; disclosed as a
   forward-looking risk, not resolved here since MT5's own specific connection model is out of this
   step's scope.

## 8. Maturity verdict

**READY FOR IMPLEMENTATION** at this step's own narrow scope (`RealBrokerAdapterBase` +
`BrokerConnectionLifecycle` Protocol + `NullBrokerAdapter` reference implementation + the 5 test
categories above) — every element reuses existing, already-validated contracts
(`BrokerAdapter`/`OrderState`/`BrokerAck`/`BrokerOrderState`/`OrderRequest`, all unmodified); the one
genuinely new design surface (idempotency, retry, connection lifecycle) is scoped narrowly and validated
against a safe, offline reference implementation before any real venue is involved; no frozen module is
touched; no live capital exposure is possible at this step by construction (no network code exists yet).

**Await CEO approval before implementation begins. No code has been written. No repository change has
been made.**
