# Market Scanner — Architecture (design)

The Market Scanner turns a raw, venue-specific market feed into a standardized, versioned, lookahead-safe
`MarketContext` for every tracked symbol at every evaluation instant. It is a pure observer/normalizer: no
decisions, no scoring, no orders. Design only — no code here.

---

## 1. Component map

```
                 ┌──────────────────────────── MARKET SCANNER ────────────────────────────┐
 raw feed  ─────▶│  Data Source Adapter  (pluggable: live | replay | lab-parity)          │
 (broker /       │        │ normalized RawBar / RawTick / CalendarEvent                    │
  historical)    │        ▼                                                                │
                 │  Ingestion & Clock        ── canonical timestamps, ordering, dedupe     │
                 │        │                                                                │
                 │        ▼                                                                │
                 │  Per-Symbol State                                                        │
                 │    ├─ Bar Store         (rolling windows per timeframe)                  │
                 │    ├─ Timeframe Sync     (HTF derivation + lookahead-safe availability)  │
                 │    ├─ Session Engine     (NY-17:00 anchoring, session tags, OR, dev H/L) │
                 │    ├─ Calendar Engine    (weekend/holiday/DST, day/week/month boundaries)│
                 │    ├─ Feature Provider   (standardized declared feature namespace v1)    │
                 │    └─ Data Quality       (gaps, completeness, staleness, sufficiency)    │
                 │        │                                                                │
                 │        ▼                                                                │
                 │  Context Builder  ── assembles + validates MarketContext (schema)        │
                 └────────────────────────────────┬───────────────────────────────────────┘
                                                  ▼
                                    MarketContext  →  Signal Engine
```

The Data Source Adapter is the ONLY component that touches a venue. Everything above it is venue-agnostic and
deterministic given `(ingested data, clock)`.

---

## 2. What data it receives (inputs)

The scanner is fed through the **Data Source Adapter**, which normalizes any venue into three input types:
1. **RawBar** — `{symbol, timeframe, ts_open, ts_close, open, high, low, close, volume, complete}`. `complete=false`
   marks a still-forming bar. Bars arrive per (symbol, timeframe) the venue provides; missing HTFs are derived.
2. **RawTick / Quote** (optional) — `{symbol, ts, bid, ask, last?, volume?}`. Used for the optional `quote` block
   and to close/append the forming base bar in live mode. Strategies in the current Library are bar-based; ticks
   are optional context.
3. **CalendarEvent** (optional) — `{ts, kind, symbol?, impact}` for the economic/holiday calendar.

Plus static **reference data** loaded at configure time: **SymbolMeta** `{symbol, tick_size, point_value,
price_precision, trading_hours, session_anchor}` and the **SessionCalendar** (session definitions, holidays, DST).

The scanner receives **no** research artifacts and no strategy internals — only market/reference data.

## 3. Timeframes it tracks

- The scanner tracks the **union of timeframes required by all loaded strategies**, obtained from the Strategy
  Loader's aggregation of each strategy's `required_context()` (`semantics.required_data`). For the current
  Library that union is **base M15 + context H1, H4, D1** (and a derived **W1** for weekly-level strategies).
- One timeframe is designated the **base heartbeat** (M15): a base-bar close is the evaluation trigger.
- Higher timeframes are **derived from the base feed by resampling** when the venue does not supply them, OR
  ingested directly and reconciled. Either way the scanner owns a single canonical version of each HTF bar.
- Each (symbol, timeframe) keeps a **rolling window** sized to `max(lookback_bars)` across all strategies needing
  it, plus a warmup margin for feature computation.

## 4. How it normalizes data

1. **Time base:** all timestamps are **UTC epoch seconds**. Bars are keyed by `ts_open`; `ts_close = ts_open +
   tf_seconds`. No local time anywhere in the context.
2. **Canonical bar grid:** bars are snapped to the canonical grid for the timeframe (e.g. M15 boundaries). Ticks
   are aggregated into the forming base bar; the bar is emitted `complete=true` at its close.
3. **Session/day anchoring:** day and session blocks are anchored to the **lab convention (NY 17:00)** so that
   PDH/PDL, opening ranges, and "previous session" match how strategies were researched. Session tags use the
   frozen UTC-hour mapping (`<8 asia, <13 london, <21 ny, else late`). *(Parity requirement — see §10.)*
4. **Price normalization:** prices are kept in instrument units (not normalized away); `tick_size`/`point_value`
   from SymbolMeta are exposed so downstream sizing is exact. Rounding to `price_precision` only for display.
5. **Feature namespace:** the scanner computes a **fixed, versioned feature dictionary** (v1) that mirrors the
   research engine's lookahead-safe features under the SAME names (e.g. `m_atr, m_ema20, m_ema50, m_rsi, m_sma,
   m_std, m_volrank, m_trend_up, session, blk, rmax20/rmin20/rmax50/rmin50, sess_high/sess_low, pdh/pdl,
   or_high/or_low, bar_in_sess, prev_sess_high/low/close, vwap, pd_open/close/mid, pw_high/pw_low, gap,
   fvg_bull/fvg_bear, disp, bull_close/bear_close, roc3, atr_ma, compress, h4_/h1_/d1_ trend_up/volrank/rsi`).
   Strategies reference these names in `required_data.fields`; the scanner provides exactly those. The scanner
   computes ONLY this standardized namespace — never strategy-specific logic. The namespace is versioned
   (`feature_dictionary_version`) independently of the context schema.
6. **Determinism:** given the same ingested bars and clock, feature values are identical every run (required for
   replay and parity).

## 5. How it manages multiple symbols

- The scanner holds **independent Per-Symbol State** (bar stores, session/calendar state, feature caches) keyed
  by symbol. Symbols never share windows.
- `MarketContext` is **per (symbol, as_of)**. A single scan cycle may produce a **`MarketContextBatch`** — a map
  `{symbol → MarketContext}` — for all tracked symbols at the same `as_of`.
- Strategies are **per-symbol evaluators**; the Signal Engine hands each strategy the context for the symbol it
  applies to (declared in the contract or by the Strategy Manager). The scanner does not decide which strategy
  runs on which symbol — it only supplies contexts.
- Symbols may advance on different venue clocks; the scanner aligns each symbol's context to its own last closed
  base bar and records `as_of` per symbol (a batch may carry slightly different `as_of` per symbol, each flagged).

## 6. How it manages sessions

- **Session Engine** tags each base bar with `session ∈ {asia, london, ny, late}` and maintains a **session block
  id (`blk`)** anchored at NY-17:00 (the research convention) that resets daily.
- Per bar it exposes: `session`, `bar_in_session` (cumulative count within the block), `session_open_ts`,
  developing `session_high`/`session_low`, and the **opening range** (`or_high`/`or_low` from the first 4 base
  bars of the block, available only after the OR forms).
- Previous-session values (`prev_sess_high/low/close`) become available at the new session's start (lookahead-safe
  — a completed block only).
- Session boundaries also drive `is_new_session` in the clock block, so session-open strategies (S5/S6/S30) fire
  correctly.

## 7. How it manages the calendar

- **Calendar Engine** exposes, per context: `date`, `dow` (0–6), `dom`, `is_new_day`, `is_new_week`,
  `is_month_boundary`, `is_holiday`, `is_weekend_gap`, and the DST offset in effect.
- **Weekly anchoring** matches the research weekly resample (for `pw_high/pw_low` and W1 context); month/day
  boundaries support calendar strategies (S18/S29/S31) exactly as researched.
- **Weekend/holiday handling:** the Friday-close → Sunday/Monday-open gap is a **legitimate event**, not missing
  data — flagged `is_weekend_gap=true` and reflected in the `gap` feature (for S19/S47), never fabricated.
- **Economic events** (optional): if a calendar feed is configured, upcoming high-impact events within a window
  are exposed as `calendar.event_flags` (advisory; the scanner does not act on them).

## 8. How it handles missing data

Policy: **never invent prices; always disclose.**
- **Gap detection:** on ingest, a missing expected bar on the grid is recorded as a **gap** in
  `data_quality.gaps[]` with `{timeframe, from_ts, to_ts, bars_missing, cause?}`. OHLC is **never forward-filled**.
- **Forming/partial bars:** the current bar is `complete=false` until its close; strategies see only completed
  bars for signals (the base heartbeat fires on close). `data_quality.last_bar_complete` states this.
- **Out-of-order / late ticks:** the Ingestion layer orders by timestamp and dedupes; a late tick inside the
  forming bar updates it; a late tick for a closed bar is dropped and logged (`data_quality.late_dropped`).
- **Warmup not met:** if a required rolling window is not yet full (feature warmup / lookback), the affected
  fields are `null` and `data_quality.warmup_satisfied=false`; `sufficiency` for any strategy needing them is
  `INSUFFICIENT`.
- **Stale feed:** `data_quality.staleness_ms` = now − last bar close; beyond a configured threshold the context
  is marked `STALE` (the scanner reports it; the Strategy Manager/health decides what to do).
- **Sufficiency object:** the context carries an explicit per-requirement `sufficiency` so the Signal Engine can
  skip a strategy cleanly (strategy returns `NEED_CONTEXT`) rather than evaluating on incomplete data.

## 9. How it synchronizes across timeframes

This is the correctness core. All timeframes advance off **one canonical clock**, and HTF context is **lookahead-
safe by availability**:
- An HTF bar becomes **available only at its close**: `available_at = htf_bar.ts_close`. A lower timeframe may use
  an HTF bar only when `available_at ≤ as_of` (equivalently, consumed at the next lower-TF bar open). This mirrors
  the research engine's `merge_asof` on availability (next-bar-start) and prevents any lookahead.
- On each **base-bar close (`as_of`)**, the Timeframe Sync selects, per HTF, the **last bar whose `available_at ≤
  as_of`**, and exposes it plus its `available_at`. If an HTF bar closed exactly on this base bar, it is included
  (its close ≤ as_of) — consistent with "available at close".
- Windows are kept **monotonic and aligned**: base index increments by one per heartbeat; HTF windows advance
  only when an HTF bar closes. The context records, per timeframe, the window and each bar's `complete`/
  `available_at`.
- **Replay vs live** use the identical rule (the clock source differs, the sync logic does not), guaranteeing
  replay parity.

## 10. Parity & conformance (first-class requirement)

Because the Strategy Library metrics assume the research conventions, the scanner's output must be **behaviourally
equivalent** to the frozen engine's feature frame:
- Same bar grid, same NY-17:00 session/`blk` anchoring, same lookahead-safe HTF availability, same feature
  definitions and names (§4.5), same weekly/day/month boundaries.
- **Conformance test (owed at build time, not here):** run the scanner over the historical CSVs the research used
  (via the **lab-parity adapter**) and assert the produced features match the frozen engine's feature frame
  within tolerance on the shared window. This document specifies the requirement; it does not implement or run it,
  and it does not read or modify the engine.
- The scanner **references** the research conventions as its target; it never imports Lab code at runtime (the
  separation law). The lab-parity adapter reads only market CSVs, never research artifacts.

## 11. Data Source Adapters (pluggable)
| adapter | use | clock |
|---|---|---|
| **live** | broker/venue websocket/REST | wall clock |
| **replay** | historical bars streamed in order | simulated clock (as_of steps) |
| **lab-parity** | the exact market CSVs used in research | simulated clock (for the conformance test) |

All adapters emit the same normalized `RawBar/RawTick/CalendarEvent`, so the scanner core is identical across
them. Swapping adapters changes the source, never the `MarketContext` shape.

## 12. Versioning policy
Three independent version lines, all semver, all recorded in every `MarketContext`:
- **`context_schema_version`** — the shape of `MarketContext` (`MARKET_CONTEXT_SCHEMA.json`). MAJOR = breaking
  field change; MINOR = additive optional field / new enum value; PATCH = clarification.
- **`feature_dictionary_version`** — the standardized feature namespace (§4.5). MAJOR = a feature's definition or
  name changes (breaks strategies referencing it); MINOR = new feature added; PATCH = doc/tolerance fix.
- **`scanner_version`** — the module implementation (set at build; irrelevant to consumers except for audit).

The context also echoes the `interface_version` it is built to serve, so the Strategy Loader can check the whole
chain (scanner ↔ contract) is compatible.

## 13. Compatibility policy
- **Consumer (Signal Engine / strategies) rule:** a strategy's `required_data.fields` must all exist in the
  scanner's `feature_dictionary_version` at a compatible MAJOR. The Strategy Loader computes this at load and
  **quarantines** any strategy whose required field is missing/incompatible (it is not evaluated), rather than
  producing a partial context silently.
- **Producer (scanner) rule:** within a feature-dictionary MAJOR, a feature's name and definition never change;
  new features are additive. Renames/removals only at the next MAJOR, after a deprecation window.
- **Unknown fields:** consumers ignore unknown OPTIONAL context fields (forward-compatible).
- **Validation on emit:** every `MarketContext` is validated against `MARKET_CONTEXT_SCHEMA.json` before it
  leaves the scanner; an invalid context is not emitted (fail-safe: the cycle is skipped and flagged, never a
  malformed context downstream).

## 14. Non-goals (hard boundaries)
- No signals, no scoring, no ranking, no conflict resolution, no sizing, no orders, no portfolio state.
- No reading of Research-Lab artifacts (engine, parquets, KB/KG/experiments) at runtime.
- No strategy-specific computation — only the standardized feature namespace.
- No fabrication of prices or bars under any missing-data condition.
