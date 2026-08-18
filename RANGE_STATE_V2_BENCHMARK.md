# RANGE_STATE SPEC V2 — benchmark report (ve_n1_replay 0.3.0)

Demonstrates that the semantic fix (median anchor + zone + causal touch accumulation + bounded trailing-window
regression + internal descriptor builder) does **not** reintroduce O(n²) behavior. Every added structure is bounded:
the confirmed-swing deque (`range_window`), the regression window (`d_min_bars`), and the internal
`IncrementalRawAxesBuilder` instance (`HISTORY_HORIZON`) — so per-bar cost stays bounded and total replay cost stays
`O(n)`.

## Method

`tools/benchmark_range_v2.py`, ve_brain venv, `ai_trader` repo absent, undisturbed. Deterministic synthetic OHLC
(real XAUUSD M15 is SEALED/forbidden), shaped with oscillation + periodic breakouts so touch/candidate/accepted/
retest/sweep/internal-descriptor paths are all exercised. `RangeConfigV2.multiday()` (`d_min_bars=96`, the primary
duration class). Metrics: wall (`perf_counter`), CPU (`process_time`), peak working set (Win32), bars/sec, isolated
`observe_closed_bar` cost (measured separately from `replay_batch` over the first 2,000 bars, to isolate per-call
overhead from ledger-construction overhead), bounded snapshot+restore.

## Results

| bars | wall (s) | CPU (s) | bars/sec | µs/bar (batch) | µs/bar (observe) | peak RSS (MB) | events | n_guards | snapshot (s) | restore (s) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 20,000 | 237.95 | 236.09 | 84.0 | 11,897.7 | 10,117.8 | 68.5 | 14,486 | 9,490 | 0.0021 | 0.0078 |
| 100,000 | 1,200.06 | 1,191.59 | 83.3 | 12,000.6 | 10,084.7 | 198.8 | 72,486 | 47,490 | 0.0177 | 0.0228 |
| **355,696** | **4,375.22** | **4,344.28** | **81.3** | **12,300.4** | **9,496.4** | **601.0** | **257,865** | **168,945** | **0.0656** | **0.1086** |

## Verdict

- **Full 355,696-bar RANGE V2 replay: 4,375.2 s ≈ 72.9 minutes** — **under the 4-hour target** (≈ 0.30× of it).
- **Scaling is linear (O(n))**: bars grow 17.78× (20k→355,696), wall grows 18.39× → **`linear_index = 1.034`** (≈ 1.0).
  bars/sec stays flat (81–84) and µs/bar stays essentially constant (~11.9–12.3 ms) across two orders of magnitude —
  no per-bar cost growth as the replay lengthens, confirming no O(n²) reintroduction.
- **Cost breakdown vs 0.2.0** (which measured ~5.3 ms/bar at the same scale): V2's ~12.3 ms/bar is **≈2.3×** 0.2.0's
  cost — attributable to three *bounded* additions, not unbounded growth: (a) the internal `IncrementalRawAxesBuilder`
  instance running a full second bounded-detector pass per bar for `structure_events_inside` (the same ~460-bar-window
  cost 0.1.1 already pays, paid twice); (b) the trailing `d_min_bars=96` OLS slope recomputed per bar (`O(96)`, a sort
  is not required here since it's a linear pass, but it is a real 96-term accumulation every bar); (c) the median
  computation over the active confirmed-swing set (a sort, bounded by `range_window`). All three are bounded constants
  independent of total replay length `n` — hence linear scaling holds despite the higher constant factor.
- **Snapshot/restore stays bounded**: 66–109 ms even at 355,696 bars (vs 0.2.0's ~9–48 ms) — the increase is the extra
  state now carried (the internal builder's own bounded snapshot, the closes deque) but remains independent of `n`.
- **Memory** grows linearly with the retained ledger (~601 MB at 355,696, comparable to 0.2.0's ~611 MB — the ledger
  is the dominant term, not the per-bar working state).

## Reproduce

```
python tools/benchmark_range_v2.py 20000 100000 355696 --out results.json
```

No PASS is self-declared; submitted for Red Team blind semantic revalidation as
`READY_FOR_RANGE_SEMANTIC_REVALIDATION`.
