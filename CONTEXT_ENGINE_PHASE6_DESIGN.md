# Phase 6 — Context Engine — Design

**CEO scope**: no orders, no final confidence; all calculations as-of timestamped, no look-ahead;
returns a versioned, serializable `MarketContextSnapshot` with provenance, data quality, a stale-data
flag, and a reason trace; reuse only official existing contracts, disable (don't invent) missing
authorized definitions.

## 1. Investigation finding: the building blocks already exist -- this is a thin wrapper

`ai_trader/market_intelligence/` (already built, an earlier checkpoint of this same project) is a pure,
stateless engine: `build_market_intelligence(context: MarketContext) -> MarketIntelligenceSnapshot`
(`engine.py:36`), computing trend/momentum/structure/volatility/liquidity/expansion/session/multi-
timeframe-agreement/confidence, entirely from the passed-in `MarketContext` dict, with zero wall-clock
reads (confirmed by grep) and its own module docstring disclaiming any order/scoring/risk touch. Its own
`ContextConfidence` (`confidence.py`) is already a disclosed, three-component composite -- by name and
shape exactly the kind of thing CEO says Context Engine must not itself invent; it is REUSED verbatim,
embedded whole inside the new snapshot, never recomputed or renamed into a "final" score (that
remains Phase 8's job). `ai_trader/edge_intelligence/evaluate_edges(context, library_path)` is also
already wired to `market_intelligence` and produces per-strategy evidence with mandatory, concrete
explanation strings -- reused, optionally, when a strategy library path is supplied.

`context_memory.contracts.SchemaVersion` (`namespace`, `version`, both caller-supplied, never inferred)
is the project's own established versioning convention, with existing instances for `market_intelligence`
and `edge_intelligence` already defined there -- reused verbatim rather than inventing a new scheme.

`ai_trader.strategy_runtime.context_access.data_quality_level(context)` is the existing, reused helper
for extracting the market context's own data-quality string (source: `context["data_quality"]["level"]`,
default `"OK"` when absent -- an inherited, disclosed default, not a new fail-open behavior introduced
here). `market_scanner.types.DataQualityLevel` (`OK/DEGRADED/STALE/INSUFFICIENT`) is the existing enum
reused to type it.

## 2. Genuinely missing, per CEO's own "disable, don't invent" instruction

No upstream module (`market_intelligence`, `edge_intelligence`, `market_scanner`, `context_memory`)
carries a generic **provenance** or **reason-trace** concept on a live snapshot. Per the CEO's explicit
instruction, these are added as new, disclosed fields with an honest scope:

- **`calculation_trace`**: NOT fabricated -- this is Context Engine's OWN processing trace of its own
  wrapping steps (market intelligence built?, edge intelligence built?, data quality resolved, stale
  check), the same `CalculationTraceStep` pattern already established in Phases 2/4. It is not a
  fabricated explanation of upstream analyzer internals.
- **`provenance`**: carries the REAL, already-existing `SchemaVersion` instances for
  `market_intelligence`/`edge_intelligence` (official existing contracts, reused verbatim) plus one
  explicitly-disabled field, `data_source_lineage_id: None`, documented as "no authorized data-source
  identity/lineage-tracking contract exists anywhere upstream today -- deliberately left disabled, not
  fabricated," satisfying "disable (don't invent)" literally rather than inventing a fake lineage id.

## 3. Public entry point

```python
def build_context_snapshot(
    context: MarketContext, strategy_library_path: str | None = None,
) -> MarketContextSnapshot: ...
```

Fail-closed: any exception building `market_intelligence`/`edge_intelligence` is caught (never
propagated -- this is a read-only, side-effect-free query, no pipeline it could safely block anyway) and
recorded in `calculation_trace`; the corresponding snapshot field becomes `None` and `data_quality`
resolves to `INSUFFICIENT`.

## 4. Safety boundary

No import of `execution_engine`/`order_manager`/`risk_manager`/`risk_manager_live`/
`portfolio_manager_live`/`simulation` anywhere in this package (verified by a dedicated static test) --
Context Engine cannot submit an order even in principle, and never computes anything presented as a
final trading confidence (only carries `market_intelligence`'s own disclosed `ContextConfidence` through
unmodified, embedded, clearly not renamed to "final").
