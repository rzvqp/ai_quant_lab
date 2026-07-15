# Simulation Framework v1 — Frozen Implementation Choices

**Frozen BEFORE any code was written and BEFORE any run was ever executed, per explicit CEO directive
("Do not tune these choices after seeing profitability results. Freeze them before performance
inspection.").** This document resolves `SIMULATION_HANDOFF.md` §15 items 1-9 (renumbered 1-8 below
per the CEO approval message's own numbering). Each choice is a documented IMPLEMENTATION CHOICE, the
same class of gap-fill every prior module's own `config.py`/`types.py` used (conservative, disclosed,
never silently invented).

---

## 1. Execution Simulator ↔ `BrokerAdapter` Protocol mapping

**Decision:** the Execution Simulator implements `ai_trader.execution_engine.broker_adapter.BrokerAdapter`
**unmodified** — `capabilities()`, `submit_order(order)`, `cancel_order(client_order_id)`,
`query_status(client_order_id)`, `query_open_orders()` — exactly the five methods, exactly the pull-based
semantics the Execution Engine's `pipeline.py`/`reconciler.py` already call (verified by reading both
files directly: `pipeline._validate_and_submit` calls `submit_order` then one immediate `query_status`;
`reconciler.reconcile_all_open` calls `query_status` per open ledger record).

**Additionally**, the Execution Simulator exposes one simulation-only method **not** part of the
`BrokerAdapter` Protocol: `advance_bar(as_of, bars: Mapping[str, Bar]) -> tuple[Fill, ...]`. The
Simulation Harness calls this once per replayed bar, **after** every symbol's decisions have been
submitted for that bar (matching `SIMULATION_SEQUENCE.md` §2's own ordering: all `EE.execute()` calls,
then one `EXSIM.match(...)` step). `advance_bar` matches every currently-WORKING order whose
`submitted_as_of < as_of` (strictly earlier bar) against the just-arrived bar — an order submitted
**during** the bar that produced it is never matched against that same bar (no lookahead, per
`EXECUTION_SIMULATOR.md` §3: "never the signal bar"). This gives exactly the documented "next bar open"
semantics for MARKET orders (submitted at bar N, first eligible at bar N+1's `advance_bar` call, using
bar N+1's open) and is the natural, spec-consistent reading `SIMULATION_HANDOFF.md` §3 itself proposed.

## 2. Portfolio-state ownership

**Decision:** reuse `ai_trader.risk_manager.types.PortfolioState` **verbatim** as the wire-contract type
Risk Manager and Execution Engine consume — the same choice Execution Engine's own `types.py` already
made for the identical gap (documented there as IMPLEMENTATION CHOICE #1). No third parallel type is
invented.

The Portfolio Simulator's own internal state is a richer `SimAccount` dataclass (balance vs equity,
floating/closed PnL, used/free margin, margin_level, leverage, gross/net exposure per-symbol/direction/
strategy/correlation-group, pending-order count, daily/weekly realized+unrealized PnL, equity HWM,
drawdown, full trade ledger) — everything `PORTFOLIO_SIMULATOR.md` §2 requires that `PortfolioState`
does not carry. `SimAccount.to_portfolio_state(as_of) -> PortfolioState` is a **pure projection**,
recomputed fresh every bar; it never mutates `SimAccount` and never diverges from it (no cached/stale
duplicate field).

## 3. Partial-fill liquidity proxy

**Decision:** v1's documented default is **full-fill for every order** — `EXECUTION_SIMULATOR.md` §5's
own words: "fill up to the bar's available liquidity proxy, **or full-fill for liquid instruments
(default)**." No real liquidity/volume-participation model exists for XAUUSD in this repo's data (the
Replay Data Source has volume but no venue depth), so inventing a numeric liquidity proxy would be an
unfounded fabrication. `FillModelConfig.partial_fill_policy` is a closed enum: `FULL_FILL` (default) or
`FIXED_FRACTION` (fills `min(order_qty, order_qty * partial_fill_fraction)` from a config knob,
deterministic, for callers who want to exercise the partial-fill code path in tests). `FULL_FILL` never
partially fills; `PARTIALLY_FILLED` states are only reachable under `FIXED_FRACTION` in v1.

## 4. Latency model

**Decision:** v1 default is **no latency** — `EXECUTION_SIMULATOR.md` §7: "Acks are immediate in sim (no
latency) unless a `latency_model` is configured." `submit_order` always acknowledges synchronously
within the same bar it was called. `SimulationContext.fill_model.latency_model` is accepted as a field
(schema compatibility) but only `None`/`"none"` is implemented in v1; any other value is rejected at
`configure()` with a clear `ConfigError` rather than silently ignored. A seeded, non-zero latency model
is out of scope for v1 (explicit, disclosed, matches `SIMULATION_HANDOFF.md` §15 item 4's own suggested
default).

## 5. Margin model defaults

**Decision:** conservative, documented placeholders (never tuned against results):
`initial_margin_pct = 0.01` (100:1 nominal leverage cap per position), `maintenance_margin_pct = 0.005`
(half of initial — a margin call triggers once equity has fallen to half the required opening margin),
`leverage_max = 100.0`. These mirror Risk Manager's own `RISK_POLICY.md` §0 "conservative placeholder
for design review, not tuned values" precedent. **Fail-safe:** if `required_margin > free_margin` at
fill time, the fill is rejected back deterministically (`REJECTED(INSUFFICIENT_MARGIN)`) — no position
is ever opened past the configured margin ceiling, even though the Risk Manager's own upstream exposure/
leverage limits are expected to prevent this in the normal case (`PORTFOLIO_SIMULATOR.md` §4).

## 6. Liquidation ordering

**Decision:** deterministic rule, evaluated inside `ACCOUNT` (`SIMULATION_STATE_MACHINE.md` §B) every
bar after mark-to-market: while `margin_level < maintenance_margin_pct` and open positions remain, close
**the position with the most negative floating PnL first** (ties broken by symbol id, ascending) —
"worst loser first" reduces risk fastest, the same worst-case/conservative bias as the stop-before-target
intrabar rule. Each closure books realized PnL and re-evaluates `margin_level` before deciding whether to
close another. `SimulationContext`'s `halt_on_liquidation: bool` (default `True`, the conservative
default) decides whether a liquidation event drives the run to `FAILED` or lets it continue with reduced
equity; every liquidation is logged as a risk event regardless.

## 7. Conformance test (research engine vs. simulator)

**Decision:** `test_conformance_vs_research_engine.py` builds a small, fixed set of historical bars and
orders and asserts the Execution Simulator's fills match the **documented conventions of the frozen
research engine** (`code/mstrat.py` — read-only, never imported into production `ai_trader` code, only
its documented conventions are asserted against): entry at next-bar open, cost = 1 tick spread + 1 tick
slippage per side (the "default v1 cost model" `EXECUTION_SIMULATOR.md` §4 itself names as mirroring the
research engine), and stop-before-target when a single bar spans both. The check is **exact** (0 tick
tolerance) because both conventions are, by construction, the same fixed rule — a real numeric drift
would indicate a genuine implementation bug, not a modeling difference to tolerate.

## 8. Artifact persistence

**Decision:** JSON Lines + JSON under `results/simulation_runs/<run_id>/`:
`trade_history.jsonl` (one JSON object per closed trade, append-only), `execution_log.jsonl` (one JSON
object per order-lifecycle event), `equity_curve.jsonl` (one `{as_of, equity, balance, drawdown_pct}`
point per bar), `report.json` (the full `SimulationReport`, `SIMULATION_SCHEMA.json`-shaped), and
`manifest.json` (sha256 checksum + byte size of every file above, plus `run_id`/`generated_at`). Every
write is atomic: content is written to `<name>.tmp` in the same directory, then `os.replace()`d onto the
final name — a crash mid-write can never leave a corrupt, partially-written artifact at the canonical
path. `report.artifacts.*_ref` fields store the relative paths (`"trade_history.jsonl"`, etc.), never the
inlined data (matching `SIMULATION_SCHEMA.json`'s own `artifacts` shape).
