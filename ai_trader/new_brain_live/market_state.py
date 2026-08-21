"""The canonical `MarketState` contract (AI Trader New Brain Architecture mandate
AI-TRADER-NEW-BRAIN-ARCHITECTURE-IMPLEMENTATION-001, section 6).

**No new class was created.** `dual_clock.upstream_context.CachedUpstreamContext` -- built from the
real N1/Router chain (`build_context`), produced once per M15 close, already IS the complete, causal,
authoritative reading strategies need: frozen (immutable), fully typed, carrying its own identity
(`context_id`). Per the mandate's own section 29 ("do not reorganize gratuitously if a canonical
structure already exists") and section 6 ("derive the exact schema from the authoritative N1-N6
contracts, do not invent fields"), this module re-exports it under the generic `MarketState` name the
rest of the platform (Catalog/Router/Strategy/EV) imports from, rather than duplicating or wrapping it.

**Field-by-field provenance** (every field traces to a specific N1-N6 contract; nothing here is invented):

| field | source | mandate category |
|---|---|---|
| `context_id` | `_compute_context_id` (sha256 of every other field) | source/fingerprint identity |
| `symbol`, `timeframe` | the M15 bar this context was computed from | instrument / timeframe |
| `market_event_id` | `f"{symbol}:{timeframe}:{ts_close}"` | source/fingerprint identity |
| `market_timestamp` | the M15 bar's own `ts_close` | timestamp |
| `n1_output_fp` | N1's own `_fp(is_compressed, is_displacement, direction, structure)` | source/fingerprint identity |
| `regime_axes_status` | N1's own axis-availability tuple (compressed/displacement/direction/structure) | confidence/reason metadata |
| `router_bias_direction`, `confidence` | Router's own inputs, passed through unmodified | directional context |
| `axes.is_compressed` | N1 | volatility/range context (compression is N1's own proxy for range) |
| `axes.is_displacement` | N1 | displacement context |
| `axes.direction` | N1 | directional context |
| `axes.structure` | N1 | market structure |
| `axes.volatility_state` | N1 | volatility context |
| `eligibility_decisions` | Router's own `StrategyRouter.eligible(...)` output | confidence/reason metadata (per-strategy reason codes) |
| `atr`, `entry_price` | `RawAxesBuilder.atr14()` / `.last_close` | levels/execution-adjacent context |

**Deliberately absent** (the mandate's own example category list names these; N1-N6's authoritative
output does not produce them at the MarketState layer, so no field is invented for them):
- **price levels** -- N3 ("market map") is evaluated PER M5 EVENT via `query_tower_chain`, not cached
  per-M15-context; a strategy that needs levels reaches them through the Router/Tower chain the same way
  `M5DecisionLoop` already does, not through `MarketState` itself.
- **session/time-of-day context** -- no N1-N6 contract currently produces this; adding it here would be
  exactly the "invent fields merely for convenience" the mandate forbids.
- **range context as a first-class field** -- `axes.is_compressed` is N1's own existing proxy; a
  dedicated "range" field does not exist in any ratified N1 contract (V4.4's RANGE research remains
  frozen, out of scope for this mandate, and not reachable from `RawAxes` today)."""

from __future__ import annotations

from ai_trader.new_brain_live.dual_clock.upstream_context import CachedUpstreamContext

MARKET_STATE_SCHEMA_VERSION = "market-state-v1"

MarketState = CachedUpstreamContext
"""Type alias, not a subclass -- every existing `CachedUpstreamContext` producer/consumer
(`build_context`, `UpstreamContextStore`, `M5DecisionLoop`, `hydrate_n1_incremental`,
`IncrementalContextRefreshLoop`) already IS a MarketState producer/consumer, with zero code changes
required anywhere in `dual_clock`/`n1_incremental`."""


def market_state_identity(state: MarketState) -> str:
    """The one, stable, documented way the rest of the platform (Catalog/Router/Strategy/EV/Shadow
    Ledger) should reference a MarketState's own identity -- `context_id` is already a real, computed
    fingerprint (`_compute_context_id`, sha256 over every field); this is a thin, named wrapper so
    callers never need to know that detail lives in `dual_clock.upstream_context`."""
    return state.context_id
