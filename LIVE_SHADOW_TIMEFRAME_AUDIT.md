# LIVE_SHADOW_TIMEFRAME_AUDIT

**Read-only audit. LIVE_SHADOW was not modified, not restarted, not touched.** Every claim below is
backed by a code citation and/or real, currently-persisted telemetry from the running process
(`ai_trader/new_brain_live/entrypoint.py`, task-managed since `LIVE_SHADOW_PERSISTENT_SERVICE_ACTIVE`).
Telemetry snapshot taken at audit time: 64 entries, all real, all from this deployment's actual history
(spans the original PID `6232` process through the current task-managed process).

## Summary verdict up front

The master clock is exclusively M15 — confirmed. But the audit surfaced something more serious than a
single-clock limitation: **`bridge.TowerDependencies.now` is a frozen, never-refreshed timestamp,
captured once at process startup and reused for every tower-chain bar-fetch for the rest of that
process's life.** Combined with the ~4.8-day eligibility ramp (see Q5/Q7), this means the tower chain
(N2/N3/N4) has **never once succeeded** in this deployment's history and, as currently coded, **cannot
ever succeed** for a long-running process — by the time any strategy becomes eligible to reach it, the
frozen `now` guarantees every node is already past its own `DATA_STALE` threshold. This is disclosed in
full under Q2-Q4 and factored into the dual-clock design's own requirements.

---

## 1. What timeframe does N1/`RawAxesBuilder` and the Router actually consume?

**M15, exclusively, hardcoded.** `ai_trader/new_brain_live/entrypoint.py:149`:
```python
outcomes = safe_evaluate_bar(bar, timeframe="M15", axes_builder=self._axes_builder, tower=self._tower)
```
`bar` itself only ever arrives from the ONE `LiveBarFeed` this process constructs
(`entrypoint.py:301-304`, `build_loop`):
```python
feed = LiveBarFeed(gateway, symbol, MT5_TIMEFRAME_M15, BAR_SECONDS_M15, state_store=state_store, ...)
```
Confirmed there is no second `LiveBarFeed(` call anywhere in `ai_trader/new_brain_live/` — grep returns
exactly one hit. `RawAxesBuilder` (N1) accumulates and reads ONLY the bars this single M15 feed hands it;
the Router (`ve_brain.StrategyRouter`) consumes N1's own `RawAxes` output, so it inherits the same M15
cadence — it has no independent timeframe of its own.

## 2/3/4. Do N2/N3/N4 receive real closed H1/M15/M5 bars?

**Real bars, yes — but frozen in time, not continuously refreshed. This is the central finding.**

`bridge.py:_query_tower_chain` (line 233) fetches the chain's H1/M15/M5 windows via:
```python
h1_bars, m15_bars, m5_bars = fetch_tower_chain_bar_windows(
    tower.gateway, symbol=symbol, now=tower.now, broker_offset_seconds=tower.broker_offset_seconds, ...)
```
`tower.now` comes from `TowerDependencies`, a **frozen (`@dataclass(frozen=True)`) object built exactly
ONCE per process lifetime**, in `entrypoint.py:build_loop` (called once, from `main()`, at process start):
```python
tower = TowerDependencies(client=tower_client, gateway=gateway, now=int(time.time()))
```
`now` is a plain `int` field — never updated, never re-read from the clock again for the rest of that
process's life. Every tower-chain bar fetch, for every bar this process EVER evaluates, is anchored to
`int(time.time())` **at process startup**. The H1/M15/M5 windows `ve_tower` receives therefore never
advance past whatever was "real and closed" the moment the process began.

Separately, `as_of` — the value `ve_tower`'s own staleness gate compares against — **is** correctly
refreshed every bar (`bridge.py:460`, `as_of=bar.ts_close`, inside `_get_chain_result`). So the request
sent to `ve_tower` carries a genuinely advancing `as_of` alongside bar data that does NOT advance. The
installed `ve_tower` package's own gate (`ve_tower/n2.py:72`, `n3.py:64`, `n4.py:72`, all identical):
```python
if req.max_staleness_s is not None and (req.as_of - req.time[-1]) > req.max_staleness_s:
    return _unavailable(req, efp, ReasonCode.DATA_STALE)
```
With the defaults `bridge.py` sets (`TowerDependencies.m5_max_staleness_s=300*2=600`,
`m15_max_staleness_s=900*2=1800`, `h1_max_staleness_s=3600*2=7200`), this means: within roughly **10
minutes of process start**, N4 (M5) permanently fails `DATA_STALE` for the rest of that process's
lifetime; within **30 minutes**, N3 (M15) does too; within **2 hours**, N2 (H1) does too. None of these
recover until the next process restart re-freezes `tower.now` at a new, temporarily-fresh value.

**Direct confirmation from real telemetry**: queried every `NodeTrace.node_name` across all 64 persisted
telemetry entries in the actual running deployment. Result: `{'N1': 64, 'Router': 64}` — **zero** N2,
N3, N4, CostModel, or N6 traces exist anywhere in this deployment's real history. The tower chain has
never been reached even once, which is why this bug has not yet visibly manifested as a `DATA_STALE`
reason code — see Q7 for why.

## 5. Is N4 evaluated on every M5 close, or only once per M15 close?

**Only once per M15 close** — and only as a byproduct of the M15-triggered tower-chain call, never as an
independently-triggered event. There is no code path anywhere in `new_brain_live`/`new_brain_bridge`
that reacts to an M5 bar closing on its own. The tower chain is invoked at most once per `(bar, side)`
inside a single M15-triggered `evaluate_bar` call (`bridge.py`'s own `_get_chain_result` memoization,
"ONE chain call per distinct `side` actually needed this bar").

## 6. How many M5 bars are skipped as independent events between two M15 runs?

**2 out of every 3.** An M15 bar spans exactly 3 M5 bars (900s / 300s). `fetch_tower_chain_bar_windows`
fetches an M5 *window* (up to 300 bars of history, per `TowerDependencies.m5_count=300`), so the two
earlier M5 sub-bars within a given M15 window ARE present as passive historical context inside that
window's array — but neither one is ever independently evaluated as "the current bar" for a decision.
Only the M5 sub-bar whose own close time coincides with the M15 boundary is ever treated as the
"as-of" bar. (This is a distinct question from the `tower.now` freeze above — even if that bug were
fixed today, this 2-out-of-3 skip would remain a separate, structural consequence of M15 being the only
trigger.)

## 7. Does the chain stop before N4 when the Router says UNCERTAIN_REGIME?

**Yes — confirmed both by code and by 100% of real telemetry.** `bridge.py`'s per-strategy loop
(`evaluate_bar`, ~line 469):
```python
if not eligibility.eligible:
    outcomes.append(NewBrainOutcome(..., decision=None, provenance=None))
    continue
```
A strategy the Router marks ineligible never reaches the `if tower is not None: chain_result =
_get_chain_result(...)` branch at all — no N2/N3/N4 call is ever made for it. Separately, even an
ELIGIBLE strategy is blocked one gate earlier if ATR/entry-price history or the cost model is
unavailable (`if atr is None or entry_price is None or cost_components is None: ... continue`).

Real evidence: all 64 telemetry entries show `Router` reason codes `UNCERTAIN_REGIME` (48) or
`TRUE_RANGE_NOT_IDENTIFIABLE` (16, `range_fade`-specific) — every single real event this deployment has
ever processed was refused at the Router, before the tower chain was ever called. This also explains why
the `tower.now`-freeze defect (Q2-4) has not yet produced a visible symptom: the code path that would
expose it has never executed. `is_compressed` requires a 460-bar compression window (per
`new_brain_bridge/tests/conftest.py`'s own documented threshold) — at one M15 bar every 900s, that's
≈4.8 days of continuous uptime before ANY axis can fully resolve out of `UNCERTAIN`. By that point,
`tower.now` (frozen at whichever process start most recently reset it) will already be many hours-to-days
stale relative to `as_of` — meaning the very first time a strategy ever becomes eligible, the tower chain
will immediately answer `DATA_STALE` on all three nodes, never a genuine N2/N3/N4 result, under the
current (unfixed) implementation.

## 8. Maximum latency between an M5 bar closing and its evaluation?

Two different answers depending on which M5 sub-bar:

- **The 1-in-3 M5 sub-bar aligned with the M15 boundary**: as designed, near-zero — it's fetched as part
  of the same M15-triggered cycle that processes it, bounded by `POLL_INTERVAL_SECONDS=30`. In practice,
  ≈0-30s after that bar's own close.
- **The other 2-in-3 M5 sub-bars**: **never evaluated as their own event, ever** — infinite latency by
  construction (they only ever appear as historical context inside a later M15-triggered window, never
  as the "as-of" bar of an actual N4 call).
- **In practice, today, for ALL THREE**: also infinite, because of the `tower.now` freeze (Q2-4) — no M5
  bar of any kind has ever actually reached a real N4 evaluation in this deployment's history (zero N4
  `NodeTrace`s exist).

---

# Dual-Clock Design (proposal only — no code changed)

Confirmed premise: the master (and only) clock triggering ANY evaluation in the live process is M15.
Below is a design for a second, independent M5-triggered path for N4/EV/N6, while N1/N2/N3 stay on their
own natural cadence (M15 for N1/N3, H1 for N2) and are cached, not recomputed on every M5 tick.

## Components

**1. `CachedUpstreamContext`** (new, small, immutable record) — the cached, identified snapshot of
"everything M4 needs that isn't M5 itself":
```
CachedUpstreamContext:
    context_id: str                    # fingerprint over every field below — this IS the "identified" part
    n1_axes: ve_brain.RawAxes
    n1_market_event_id: str            # the M15 bar this axes reading came from
    n1_as_of: int                      # that M15 bar's ts_close
    eligibility_decisions: tuple[ve_brain.EligibilityDecision, ...]
    n2_result: ...                     # bias, from the LAST successful H1-driven N2 call
    n2_as_of: int                      # the H1 bar N2 last answered on
    n3_result: ...                     # map/levels, from the LAST successful M15-driven N3 call
    n3_as_of: int                      # the M15 bar N3 last answered on
    cached_at: int                     # wall-clock time this snapshot was produced (for staleness math)
```
Produced by the EXISTING M15-triggered path (unchanged: N1 -> Router -> N2 -> N3, still all M15/H1-paced,
still exactly as today) and written to a new, small, OVERWRITE-latest store entry (same
`SqliteStateStore.set_text`/`get_text` pattern this delivery's own heartbeat already established — no
new persistence mechanism). Never appended/history-tracked; only the latest matters for M5 triggering.

**2. A second, independent M5-triggered loop** (`M5EvaluationLoop`, new, alongside — not replacing —
the existing M15 loop):
- Its OWN `LiveBarFeed(gateway, symbol, MT5_TIMEFRAME_M5, BAR_SECONDS_M5, state_store=state_store,
  broker_offset=...)`, using a SEPARATE watermark key (`live_signal_source.bar_feed:{symbol}:5`, already
  distinct by construction since `LiveBarFeed`'s own watermark key is `f"...:{symbol}:{mt5_timeframe}"`
  and `mt5_timeframe` differs — 5 vs 15 — so this is free, no new dedup key needed beyond what
  `LiveBarFeed` already provides per-timeframe).
- On every newly-closed M5 bar: read the latest `CachedUpstreamContext`, run ONLY N4 (real M5 bar, `as_of
  = <this M5 bar's own ts_close, freshly computed, never frozen>`) against it, then EV/N6 using the
  cached N1/N2/N3 results plus this fresh N4 result.
- **Fixes the `tower.now` freeze as a byproduct**: since N4's own bar-fetch `now` would be computed fresh
  at EACH M5 trigger (not reused from a process-start-frozen field), this design eliminates the root
  cause found in Q2-4 rather than inheriting it. (This fix would need to happen regardless of the
  dual-clock work — the tower chain does not function today without it — but the dual-clock rebuild is
  the natural place to do it, since it already requires threading a fresh `now` through per M5 tick.)

## Requirement-by-requirement

- **N1/N2/N3 context cached and identified**: `CachedUpstreamContext.context_id` (a `_fp(...)`-style hash
  over every field that could change the decision, same convention already used throughout this
  codebase). Every M5-triggered N4/EV/N6 evaluation records WHICH `context_id` it used — full provenance,
  auditable after the fact, never implicit.
- **Trigger at every closed M5 for N4/EV/N6**: the new `M5EvaluationLoop`'s own `LiveBarFeed.poll()` is
  the trigger — mirrors the existing M15 loop's own structure exactly, just parameterized to M5 and
  scoped to N4/EV/N6 only (never re-runs N1/Router/N2/N3).
- **Zero lookahead**: the M5 loop only ever reads the MOST RECENTLY CACHED upstream context — never
  "waits for" or special-cases a not-yet-closed M15/H1 bar. If the M15 loop hasn't produced a context yet
  covering the current moment (e.g. very first minutes after a restart), there IS no cached context and
  the M5 loop degrades to `NO_TRADE` (next bullet) rather than inventing one. Concretely: `n1_as_of`/
  `n2_as_of`/`n3_as_of` are all bar close times strictly ≤ the M5 bar's own `ts_close` being evaluated,
  by construction (the cache can only ever hold already-computed, already-closed-bar results).
- **Stale context -> NO_TRADE**: `M5EvaluationLoop` checks `current_m5_bar.ts_close - cached_context.
  n3_as_of` (M15/N3 is the tightest-coupled upstream dependency for N4) against an explicit threshold
  (natural default: `2 * BAR_SECONDS_M15 = 1800s`, mirroring the existing `m15_max_staleness_s` convention
  already established in `TowerDependencies`) — exceeding it produces `NO_TRADE` /
  `UPSTREAM_CONTEXT_STALE`, structurally identical in shape to the existing `N2_UNAVAILABLE`/
  `N3_UNAVAILABLE` fail-closed reason codes this codebase already uses. Never silently reuses ancient
  context past that threshold.
- **Dedup per M5 `market_event_id`**: `market_event_id = f"{symbol}:M5:{bar.ts_close}"` (identical
  convention to the existing M15 `market_event_id` construction, `bridge.py`'s own `f"{bar.symbol}:
  {timeframe}:{bar.ts_close}"`), watermarked by the M5 loop's own dedicated `LiveBarFeed` instance exactly
  as `LiveBarFeed.poll()` already deduplicates the M15 stream today (`ts_open <= last_emitted_ts_open ->
  skip`) — no new dedup mechanism needs inventing, only a second instance of the existing one, keyed to
  M5.
- **Broker gate stays DISABLED**: unchanged, structural, not a parameter of this design at all — the new
  M5 loop would reuse the EXACT SAME `execution_shadow.attempt_shadow_execution(risk_decision, gate=...)`
  call with the EXACT SAME default (`enabled=False`) `BrokerOrderSubmissionGate` the M15 loop already
  uses. No new code path would ever construct a gate with `enabled=True` — enforceable the same way the
  existing AST guards already prove it for `new_brain_live`.

## What this design does NOT do (scope discipline)

Does not touch `LIVE_SHADOW` (design only, per instruction). Does not change N1's own M15 cadence (N1 is
inherently a swing/structure detector over M15 history — re-running it on M5 would be a different,
unrequested redesign). Does not change probability_inputs, strategies, or authority. Does not
independently propose a fix for the `tower.now` freeze as a standalone patch — it is described here only
because the dual-clock rebuild is the point where it would naturally get fixed; a targeted one-line fix
to `TowerDependencies`/its construction site is a smaller, separable piece of work if the freeze needs
addressing before the fuller dual-clock build.
