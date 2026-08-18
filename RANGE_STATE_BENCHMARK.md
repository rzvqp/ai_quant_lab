# RANGE_STATE replay — benchmark report (ve_n1_replay 0.2.0)

Target (mandate §8): the additive RANGE_STATE producer must keep the replay bounded and complete up to **355,696 bars**
well under 4 hours. `RangeStateReplayEngine` runs the byte-identical N1 incremental engine **plus** the range producer +
event state machine per bar.

## Method

`tools/benchmark_range.py`, ve_brain venv, `ai_trader` repo absent, undisturbed. Real XAUUSD M15 is SEALED (forbidden),
so a **deterministic synthetic** series of the same bar count is used, shaped as oscillating ranges with periodic
breakouts so every RANGE/event path (RANGE_MID guard, rejections, candidate→accepted/failed, retest, sweep, invalidation)
is exercised. Correctness is proven separately and exhaustively (`RANGE_STATE_CONTRACT.md`, `tests/test_range_state.py`,
34 tests); this run measures only speed/memory/scaling. Metrics: wall (`perf_counter`), CPU (`process_time`), peak
working set (Win32), bars/sec, event/guard counts, bounded snapshot+restore.

## Results

| bars | wall (s) | CPU (s) | bars/sec | µs/bar | peak RSS (MB) | events | n_guards | snapshot (s) | restore (s) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 20,000 | 105.44 | 104.70 | 189.7 | 5271.8 | 68.4 | 19,925 | 19,425 | 0.0018 | 0.0021 |
| 100,000 | 530.45 | 527.70 | 188.5 | 5304.5 | 199.1 | 99,925 | 97,425 | 0.134 | 0.0086 |
| **355,696** | **1882.43** | **1870.58** | **189.0** | **5292.2** | **610.8** | **355,621** | **346,729** | **0.049** | **0.048** |

## Verdict

- **Full 355,696-bar RANGE replay: 1882.4 s ≈ 31.4 minutes** — **well under the 4-hour target** (≈ 0.13× of it).
- **Scaling is linear (O(n))**: 20k→355,696 grows the bars 17.78× and the wall 17.85× → **linear index 1.004** (≈ 1.0).
  bars/sec is flat (~189) and µs/bar constant (~5.3 ms) across all sizes. The ~5.3 ms/bar decomposes into N1's bounded
  ≤460-window exp/comp (~2.9 ms, the byte-identity cost) plus the range producer's bounded work over the active
  confirmed-swing set (touch counting / boundary extension, ≤ range_window). No O(n) growth per bar.
- **Snapshot/restore is bounded** (carries the 460-buffer + range state, not history): ≤ 0.13 s even at 355,696 bars.
- **Memory** grows linearly with the retained ledger + observed bars (~0.6 GB at 355,696).
- On this synthetic series the machine emits a RANGE_MID SAFETY_GUARD on most in-range bars (`n_guards` = 346,729),
  confirming F7 fires as an explicit, counted state — the guard is present in the audit, not inferred from absence.

## Reproduce

```
python tools/benchmark_range.py 20000 100000 355696 --out results.json
```

No PASS is self-declared; submitted for Red Team revalidation as `READY_FOR_RANGE_STATE_HANDOFF_REVALIDATION`.
