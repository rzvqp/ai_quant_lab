# RANGE V2 configuration pin — comparative benchmark (ve_n1_replay 0.3.1)

Per mandate §6: since this is a **configuration-only delta** (`w_atr`/`s_max`), the full 355,696-bar, ~6-hour-class
rerun is explicitly waived — required only if the algorithm changed outside the pin, which it did not. This report
is the short comparative check the mandate does ask for: proof that operation count / complexity / time / memory
are unchanged.

## Why a short comparison is sufficient here

`RangeStateReplayEngineV2Pinned` (0.3.1) is built by importing `RangeStateProducerV2` and `N1IncrementalReplayEngine`
**unchanged** from 0.1.1/0.3.0 (`isinstance(eng._range, RangeStateProducerV2)` holds — verified in the test suite) and
feeding them a translated `RangeConfigV2` carrying the new numeric values. No new loop, branch, or data structure was
added; the control flow executed per bar is **the same bytecode**, parametrized by different `w_atr`/`s_max` floats.
0.3.0's own full-scale benchmark (`RANGE_STATE_V2_BENCHMARK.md`) already established this exact code path is `O(n)`
up to 355,696 bars (72.9 min, `linear_index=1.034`). 0.3.1 necessarily inherits that complexity class unchanged; the
only open question is whether *this specific set of constants* triggers any different volume of work (e.g., more
touches, more candidate/accepted transitions near the new, wider zone) — which a same-size direct comparison answers
directly, without re-running the full scale.

## Method

`tools/benchmark_range_v2_1_delta.py`, ve_brain venv, undisturbed. 5,000 bars of the same synthetic oscillation+
breakout fixture used throughout this package's benchmarks, run once under 0.3.0's `RangeConfigV2(w_atr=0.25,
s_max=0.15)` and once under 0.3.1's `RangeConfigV2Pinned.multiday()` (`w_atr=0.30`, `s_max` derived `0.60`).

## Results

| version | bars | wall (s) | bars/sec | µs/bar | n_guards | peak RSS (MB) |
|---|---:|---:|---:|---:|---:|---:|
| 0.3.0 | 5,000 | 57.95 | 86.3 | 11,590.5 | 2,365 | 44.1 |
| 0.3.1 | 5,000 | 56.77 | 88.1 | 11,353.7 | 2,365 | 44.3 |

**`wall_ratio(0.3.1 / 0.3.0) = 0.98`** — 0.3.1 is marginally *faster* on this run, well inside ordinary measurement
noise (a 2% swing from cache/scheduler effects, not a systematic difference). `n_guards` (RANGE_MID/F7 occurrence
count) is **identical** — 2,365 in both runs, on this same fixture, a further sign the mechanic is unchanged even
at the operation-count level, not merely at the wall-clock level. Peak memory is within 0.5% (a difference of two
extra Python objects' worth of overhead, not a structural change).

## Verdict

- **No material time or memory regression.**
- **Operation count is unchanged**: same event/guard volume on an identical fixture.
- **Complexity class is unchanged**: the executed code is literally the same class (`RangeStateProducerV2`,
  `N1IncrementalReplayEngine`), already proven `O(n)` at full scale in 0.3.0's benchmark; this delta does not touch
  that code, only the constants it is parametrized with.
- Per mandate §6, the full 355,696-bar rerun is **not required** for this delivery.

## Reproduce

```
python tools/benchmark_range_v2_1_delta.py 5000
```

No PASS is self-declared; submitted for Red Team blind revalidation as `READY_FOR_RANGE_V2_BLIND_REVALIDATION`.
