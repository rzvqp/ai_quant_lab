# Market Scanner — Phase 5.1 (design)

The **Market Scanner** is the first module of the AI Trader. It **observes the market and produces a standardized,
versioned `MarketContext`** that is sufficient to evaluate **any** strategy in the Strategy Library — without any
strategy ever touching the broker feed.

**This package is documentation and schema only.** No executable code, no backtest, no research, no changes to the
Research Lab / Strategy Library / Strategy Interface / engine / S1–S51 / Wave 1 / holdout / matched-null.

## What it is — and is NOT

| the Market Scanner DOES | the Market Scanner does NOT |
|---|---|
| ingest raw market data through a pluggable Data Source Adapter | make decisions |
| normalize it to a canonical bar grid + session/calendar model | score or rank anything |
| maintain rolling windows per (symbol, timeframe) | generate signals |
| derive lookahead-safe higher-timeframe context | place, size, or manage orders |
| compute the **declared, standardized feature namespace** strategies need | know anything about strategy internals |
| detect gaps / missing data and flag data quality | fabricate prices or fill OHLC gaps |
| emit a validated `MarketContext` per (symbol, as_of) | read Research-Lab artifacts |

It is a **pure observer/normalizer**: deterministic given (inputs, clock), stateful only in the sense of holding
rolling windows and session/calendar state. Decisions, scoring, and execution belong to downstream modules.

## Why it exists (the sufficiency contract)
Strategies declare, via the Strategy API `required_context()`, exactly which timeframes, fields, and lookback
they need. The Market Scanner's job is to **satisfy the union of all loaded strategies' requirements** so that the
Signal Engine can call `generate_signal(context)` on every strategy with a single standardized object. If the
`MarketContext` cannot satisfy a strategy's requirement (warmup not met, data gap), it says so explicitly
(`sufficiency = INSUFFICIENT`) and that strategy returns `NEED_CONTEXT` — nothing is guessed.

## Parity requirement (critical)
The Strategy Library's metrics were produced under the frozen research conventions (M15 grid, **NY-17:00
session anchoring**, lookahead-safe HTF availability, a specific feature namespace). For a strategy to behave live
the way it was researched, the Market Scanner's `MarketContext` — bar grid, session tags, HTF availability, and
the declared features — **must be behaviourally equivalent to the frozen engine's feature frame**. This is a
first-class requirement (`MARKET_SCANNER_ARCHITECTURE.md §10 Parity & Conformance`); a conformance check is owed
at build time. This document does not modify or copy the engine — it references its conventions as the target.

## Package contents
| file | purpose |
|---|---|
| `MARKET_SCANNER_README.md` | this overview |
| `MARKET_SCANNER_ARCHITECTURE.md` | inputs, timeframes, normalization, multi-symbol, sessions, calendar, missing-data, cross-TF sync, adapters, parity, versioning/compatibility |
| `MARKET_CONTEXT_SCHEMA.json` | JSON Schema (Draft 2020-12) for the `MarketContext` object — required/optional fields |
| `MARKET_SCANNER_API.md` | the scanner module's own API (configure/ingest/build_context/scan/health…) — definition only |
| `MARKET_SCANNER_SEQUENCE.md` | operational sequences: warmup, live tick, replay, gap handling, multi-symbol, cross-TF close |

## Position in the pipeline
```
[market data] → Market Scanner → MarketContext → Strategy Loader/Manager → Signal Engine → …
```
The Market Scanner sits at the head of the AI Trader pipeline (`ai_trader/README.md`). It hands `MarketContext`
to the Signal Engine; it has no knowledge of, and no dependency on, anything downstream.

## Status
DESIGN (Phase 5.1). Deliverables complete for review. Next step (gated): implement the scanner against these
documents + a parity conformance test versus the frozen research feature frame.
