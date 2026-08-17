# N1 incremental replay — benchmark report (0.1.1)

Target (mandate): a canonical N1 replay of up to **355,696 bars** must complete **under 4 hours** on the same machine.
0.1.0's `RawAxesBuilder.observe` is O(n²)+ (re-runs all detectors over the full growing history each bar), which put a
full 355,696-bar replay at **~20+ days** — the blocker Alpha reported (`531c7bb`). 0.1.1's incremental engine removes it.

## Method

`tools/benchmark_incremental.py`, run in the ve_brain-equipped venv with the `ai_trader` repo absent, undisturbed
(no concurrent CPU load). The real XAUUSD M15 dataset is **SEALED** (access forbidden), so the *performance* benchmark
uses a **deterministic synthetic** OHLC series of the **same bar count**, with periodic regime changes so the
swing/break/expansion/compression paths are genuinely exercised (not a degenerate flat series). **Semantic** parity is
proven separately and exhaustively on the official fixtures + adversarial sequences (`N1_INCREMENTAL_PARITY.md`,
`tests/test_incremental.py`), byte-identical to 0.1.0 — so this run measures only speed/memory/scaling, never
correctness. Metrics: wall (`perf_counter`), CPU (`process_time`), peak working set (Win32 `PeakWorkingSetSize`),
bars/sec, ledger size (canonical JSON serialization), and bounded snapshot+restore overhead.

## Results

| bars | wall (s) | CPU (s) | bars/sec | µs/bar | peak RSS (MB) | ledger JSON (MB) | snapshot (ms) | restore (ms) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 20,000 | 56.01 | 55.70 | 357.1 | 2800.7 | 91.0 | 11.2 | 0.68 | 0.37 |
| 100,000 | 280.01 | 277.80 | 357.1 | 2800.1 | 311.5 | 56.2 | 3.01 | 1.69 |
| **355,696** | **1016.73** | **1007.63** | **349.8** | **2858.4** | **1014.3** | **201.1** | **9.22** | **5.54** |

## Verdict

- **Full 355,696-bar replay: 1016.7 s ≈ 16.9 minutes** — **well under the 4-hour target** (≈ 0.07× of it), and a
  ~1,700× improvement over 0.1.0's ~20+ day projection.
- **Scaling is linear (O(n))**: from 20k→355,696 the bar count grows 17.78× and wall grows 18.15× → **linear index
  1.021** (≈ 1.0). bars/sec is flat (~350–357) across all sizes; µs/bar is constant (~2.80–2.86 ms). The per-bar cost is
  the bounded ≤460-window `expansion`/`compression` (called on the UNMODIFIED ratified functions — the exact reason the
  bounded axes are byte-identical) plus O(1) incremental swing/break work. No O(n) growth per bar.
- **Snapshot/restore is bounded, not O(n)**: at 355,696 bars snapshot is 9.2 ms and restore 5.5 ms — it carries only the
  460-buffer + live swing/break state, never re-observing history (contrast 0.1.0's `restore`, which re-runs all bars).
- **Memory** grows linearly with the retained ledger + observed bars (~1.0 GB at 355,696; ledger JSON ≈ 201 MB,
  ≈ 593 B/record). The per-bar detector *working set* is bounded by the 460-buffer; the O(n) footprint is the ledger the
  355 hypotheses consume, which is the intended read-only artifact.

## Reproduce

```
python tools/benchmark_incremental.py 20000 100000 355696 --out results.json
```

Raw JSON of this run is retained by the harness. No PASS is self-declared; submitted for Red Team revalidation as
`READY_FOR_N1_INCREMENTAL_REVALIDATION`.
