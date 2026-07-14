# Market Scanner — Operational Sequences (design)

How the Market Scanner behaves over time. Sequences only — no implementation. Symbols: `MS`=Market Scanner,
`ADP`=Data Source Adapter, `ORCH`=AI Trader orchestrator, `LOADER`=Strategy Loader, `SIGENG`=Signal Engine.

Legend for HTF sync: an HTF bar is usable only when `available_at (= ts_close) ≤ as_of`.

---

## 1. Startup & warmup

```
ORCH → MS.configure(symbols[], data_source=live|replay|lab_parity)
LOADER → MS.register_requirements(union of strategies' required_context())
         MS → CompatibilityReport (satisfiable? missing fields/timeframes)
         LOADER quarantines any strategy whose required field MS cannot provide
ADP  → MS.ingest_bar(...) × N        # backfill historical bars per (symbol, timeframe)
MS   → builds rolling windows; computes features as history accrues
loop until MS.warmup_status(symbol).satisfied for all symbols:
         contexts emitted in this phase carry sufficiency=INSUFFICIENT (null features)
warmup satisfied → normal operation begins
```
No strategy is evaluated during warmup: `sufficiency=INSUFFICIENT` ⇒ the Signal Engine skips it (strategy returns
`NEED_CONTEXT`).

## 2. Live per-bar cycle (the heartbeat)

```
ADP  → MS.ingest_tick(tick)              # forming base bar updates; optional quote block
... at base-bar (M15) close ...
ADP  → MS.ingest_bar(closed base bar, complete=true)
ADP  → MS.advance_clock(as_of = base bar ts_close)
         MS returns the (symbol,timeframe) bars that closed at/before as_of
MS   internally, per symbol:
         • append closed bar; update session (bar_in_session, dev high/low, OR), calendar flags
         • Timeframe Sync: for each HTF, select last bar with available_at ≤ as_of
         • Feature Provider: recompute the declared feature namespace at as_of
         • Data Quality: gaps, completeness, staleness, warmup
         • Sufficiency: overall + missing fields/timeframes
ORCH → MS.scan(as_of) → MarketContextBatch { symbol → MarketContext }   (schema-validated)
ORCH → hands each MarketContext to SIGENG (which calls the strategies)
```
The scanner's job ends when it emits the validated batch. It never learns whether a signal resulted.

## 3. Cross-timeframe close (HTF just closed on this base bar)

```
as_of = base bar close that coincides with an H1/H4/D1 close
MS: the newly-closed HTF bar has available_at = its ts_close ≤ as_of  → it IS included this cycle
    (consistent with "available at close"; no lookahead because the bar is closed)
    HTF features (e.g. h4_trend_up) update on THIS cycle
next base bars until the next HTF close: HTF window is unchanged (last closed HTF bar reused)
```
This reproduces the research engine's `merge_asof`-on-availability behaviour exactly (parity §10 of the
architecture).

## 4. Missing-data / gap handling

```
ADP delivers bars with a hole on the grid (e.g. feed outage)
MS.ingest_bar detects the skipped grid slot(s):
    • record data_quality.by_timeframe[tf].gaps += { from_ts, to_ts, bars_missing, cause }
    • DO NOT fabricate/forward-fill OHLC
    • features that need the missing bars → null; warmup_satisfied may flip false
build_context still runs:
    • data_quality.overall = DEGRADED (or STALE if the feed is silent past threshold)
    • sufficiency = PARTIAL/INSUFFICIENT with missing_fields/missing_timeframes listed
SIGENG: strategies needing the missing fields return NEED_CONTEXT and are skipped;
        strategies whose required fields are all present still evaluate normally
when the feed recovers and backfills the gap:
    • MS fills the real bars, recomputes features, clears the gap; sufficiency recovers
```

## 5. Weekend / holiday boundary

```
Friday base close → MS marks session/day/week boundaries
Sunday/Monday open bar arrives:
    • calendar.is_weekend_gap = true; the `gap` feature = open − prior_session_close (legitimate, not missing)
    • is_new_week / is_new_day set; session block (blk) resets at NY-17:00 anchor
holidays: ADP simply delivers no bars; MS marks is_holiday, keeps windows intact (no fabricated bars)
```
Calendar strategies (S18/S29/S31) and gap strategies (S19/S47) receive the correct flags without special-casing.

## 6. Multi-symbol scan

```
ORCH → MS.scan(as_of, symbols?=all)
MS: for each symbol independently:
        build_context(symbol, as_of) using THAT symbol's windows/session/calendar
        (a symbol whose last base close < as_of carries its own as_of, flagged)
MS → MarketContextBatch { S_A: ctx_A, S_B: ctx_B, ... }
ORCH → routes each symbol's context to the strategies scoped to that symbol
```
Symbols are fully isolated; one symbol's gap/staleness never affects another's context.

## 7. Replay & conformance

```
mode = REPLAY:  ORCH steps MS.advance_clock(as_of) over historical timestamps; identical sync/feature logic as LIVE
                → deterministic, reproducible contexts (replay parity)
mode = LAB_PARITY: ADP reads the exact market CSVs used in research
                → run the (future) conformance test: assert MS features == frozen engine feature frame within
                  tolerance on the shared window (owed at build; not executed here; reads NO research artifacts)
```

## 8. Failure & fail-safe sequence

```
context fails schema validation           → MS does NOT emit it; cycle flagged in health(); ORCH skips the symbol
feed stale beyond threshold               → data_quality.overall = STALE; health().state degraded; ORCH may pause
required feature missing at load          → LOADER quarantines the strategy (never evaluated) — not a runtime error
late tick for a closed bar                → dropped, counted in data_quality.late_dropped
```
Every abnormal condition resolves to an explicit flag and a skip — never a fabricated or malformed context.

## 9. End-to-end (one heartbeat, condensed)
```
tick/bar in → ingest → advance_clock(as_of) → per symbol {session, calendar, TF-sync, features, quality,
sufficiency} → scan(as_of) → validate → MarketContextBatch → Signal Engine.  (Scanner stops here.)
```
