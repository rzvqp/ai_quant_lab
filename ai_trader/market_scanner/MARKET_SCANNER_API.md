# Market Scanner — API (definition only)

The Market Scanner's own module API, called by the AI Trader orchestrator and the Data Source Adapter. **It is
NOT called by strategies** — strategies never see the scanner; they receive a `MarketContext` from the Signal
Engine. Definition and semantics only — no implementation.

- **api_version:** `1.0.0` · **produces:** `MarketContext` (`MARKET_CONTEXT_SCHEMA.json`).
- **Purity:** context assembly is a deterministic function of `(ingested data, clock, configuration)`. The scanner
  is stateful only in the mechanical sense (rolling windows, session/calendar state); no randomness, no decisions.
- **No side effects beyond its own state:** the API never scores, signals, sizes, or orders, and never reads
  Research-Lab artifacts.

---

## 0. Types (summary; full shapes in the schemas)
```
SymbolMeta         { symbol, tick_size, point_value, price_precision, session_anchor, trading_hours? }
RawBar             { symbol, timeframe, ts_open, ts_close, open, high, low, close, volume, complete }
RawTick            { symbol, ts, bid?, ask?, last?, volume? }
CalendarEvent      { ts, kind?, impact, symbol? }
Requirements       # aggregated from strategies' required_context()
    timeframes[]           union of needed timeframes
    fields_by_timeframe    map tf -> required feature names
    lookback_by_timeframe  map tf -> max lookback bars
    symbols[]              symbols in scope
MarketContext      # the deliverable (schema)
MarketContextBatch { as_of, contexts: map<symbol, MarketContext> }
ScannerHealth      { state, feeds[], sync_ok, gaps_open, staleness_ms_by_symbol, notes }
```

---

## 1. Configuration & registration

### `configure(symbols: SymbolMeta[], data_source: AdapterConfig) -> void`
Initializes per-symbol state, selects the Data Source Adapter (live | replay | lab_parity), and loads reference
data (SymbolMeta, SessionCalendar). Idempotent; must be called before ingestion.

### `register_requirements(req: Requirements) -> CompatibilityReport`
Receives the union of strategy `required_context()` requirements (assembled by the Strategy Loader) and configures
which timeframes/features/lookbacks to maintain. Returns a `CompatibilityReport { satisfiable: bool,
missing_fields[], missing_timeframes[], feature_dictionary_version }` so the Loader can quarantine any strategy
whose required field the scanner cannot provide (§13 of the architecture). Does NOT evaluate strategies.

### `get_provided_features() -> { feature_dictionary_version, fields_by_timeframe }`
Declares exactly what the scanner provides, for the Loader's compatibility check.

---

## 2. Ingestion (from the Data Source Adapter)

### `ingest_bar(bar: RawBar) -> void`
Normalizes and appends a bar to the correct (symbol, timeframe) window; snaps to the canonical grid; updates
completeness; records gaps if the grid skipped. A `complete=false` bar updates the forming bar in place.

### `ingest_tick(tick: RawTick) -> void`  *(optional feed)*
Updates the forming base bar and the optional `quote` block. Late ticks for closed bars are dropped and counted.

### `ingest_calendar(evt: CalendarEvent) -> void`  *(optional feed)*
Adds an economic/holiday event to the Calendar Engine; surfaced later as `calendar.event_flags`.

### `advance_clock(as_of: int) -> list<SymbolTimeframeClose>`  *(replay/live tick)*
Moves the canonical clock to `as_of` and returns the set of (symbol, timeframe) bars that closed at/before it.
This is what triggers context building. In live mode the adapter calls this on real bar closes; in replay the
orchestrator steps it.

---

## 3. Context production (the core output)

### `build_context(symbol: str, as_of: int) -> MarketContext`
Assembles the standardized `MarketContext` for one symbol at `as_of`: selects lookahead-safe windows per
timeframe (only bars with `available_at ≤ as_of`), tags session/calendar, computes the declared feature namespace,
fills `data_quality` and `sufficiency`, and **validates against `MARKET_CONTEXT_SCHEMA.json`**. If validation
fails, it raises internally and returns nothing usable for that symbol (the cycle is flagged, never a malformed
context downstream). Deterministic.

### `scan(as_of: int, symbols?: str[]) -> MarketContextBatch`
Builds contexts for all tracked symbols (or a subset) at `as_of` and returns them as a batch. This is the normal
per-heartbeat entry point the orchestrator calls after `advance_clock`.

### `context_for(symbol, as_of)  ==  build_context`  *(alias for single-symbol callers)*

---

## 4. Introspection & health

### `warmup_status(symbol: str) -> { satisfied: bool, by_timeframe: map<tf,bool>, bars_needed }`
Whether every rolling window/feature has enough history to be non-null. Until satisfied, contexts are emitted with
`sufficiency=INSUFFICIENT` / null features.

### `health() -> ScannerHealth`
Operational status of the scanner itself: feed connectivity, staleness per symbol, open gaps, and cross-timeframe
sync status. Consumed by the AI Trader's Performance Monitor / Strategy Manager. Reports only; takes no action.

### `versions() -> { context_schema_version, feature_dictionary_version, scanner_version, interface_version }`
Echoes the version lines (§12 architecture) for the Loader's end-to-end compatibility check.

---

## 5. Contract of use (invariants the caller can rely on)
1. **Lookahead-safe:** no `MarketContext` ever contains an HTF bar or feature whose `available_at > as_of`.
2. **Deterministic:** identical ingested data + `as_of` ⇒ identical `MarketContext` (replay parity).
3. **Honest:** missing/warming data ⇒ null features + `data_quality`/`sufficiency` flags, never fabricated prices.
4. **Validated:** every emitted context conforms to `MARKET_CONTEXT_SCHEMA.json`.
5. **Bounded scope:** the API exposes only observation/normalization. There is no method to score, signal, size,
   or order, and none to read Lab artifacts — by design.

## 6. What the API deliberately does NOT provide
- No `generate_signal`, `score`, `rank`, `size`, or `submit_order` — those live in downstream modules.
- No access to strategy internals or Research-Lab data.
- No mutation hook for strategies or contracts.
