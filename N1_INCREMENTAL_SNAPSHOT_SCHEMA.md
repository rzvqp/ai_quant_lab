# N1 incremental snapshot — schema (`n1-incremental-snapshot-v1`)

`N1IncrementalReplayEngine.snapshot()` returns an `N1IncrementalSnapshot` that carries **only bounded state** — not the
full bar history. `restore()` is therefore **O(HISTORY_HORIZON)**, not O(n): it does not re-observe the past. This is the
difference from the vendored 0.1.0 `restore`, which rebuilds a `RawAxesBuilder` by re-observing every stored bar
(O(n²) over the run — the defect 0.1.1 removes). Measured snapshot+restore at 355,696 bars: **< 1 ms each.**

## `N1IncrementalSnapshot`

| field | type | meaning |
|---|---|---|
| `identity_fingerprint` | str | `EvaluationIdentity.fingerprint()` — restore into an engine with a different identity raises `IncompatibleSnapshotError` (fail-closed). |
| `snapshot_schema_version` | str | `n1-incremental-snapshot-v1`. |
| `history_horizon` | int | `460`; must match the target engine's horizon or restore refuses. |
| `history_horizon_version` | str | `n1-history-horizon-v1`; must match. |
| `bars_observed` | int | cursor — number of bars seen so far (source of truth for `bars_observed` after restore). |
| `builder_state` | dict | bounded incremental state of `IncrementalRawAxesBuilder` (below). |
| `last_bar_parts` | tuple \| None | the last observed bar's fields (needed only for the ordering/duplicate guards); None if no bar seen. |
| `last_result` | `N1ReplayResult` \| None | the last decision (so a conflicting-duplicate re-observe returns the cached result exactly as in 0.1.0). |

## `builder_state` (from `IncrementalRawAxesBuilder.snapshot_state`)

Bounded — its size does not grow with the run length beyond the 460-bar buffers and the set of currently-unconsumed
swings:

| key | content | bound |
|---|---|---|
| `horizon`, `n` | horizon and bars observed | scalar |
| `bo`, `bh`, `bl`, `bc` | rolling OHLC buffers feeding the unmodified `expansion`/`compression` | ≤ 460 each |
| `wh`, `wl` | fractal detection window | 2k+1 = 5 each |
| `last_high`, `last_low` | last labeled swing of each kind (`label_structure` state) | 1 each |
| `stack` | 4 label stacks (HH/LL/HL/LH) of **unconsumed confirmed** swings | ≤ number of live unconsumed swings |
| `consumed` | idx of swings already broken | grows with breaks (small in practice) |
| `pending` | swing detected at the previous bar (confirmed_idx = n−1), not yet stacked | 0 or 1 |
| `latest_break_kind` | the persistent latest break (`bos_bull`/…/None) that drives `structure`/`direction` | scalar |

A swing is stored as `[idx, price, kind, label]`. Restore rebuilds the deques with the correct `maxlen`, so subsequent
`observe` calls behave exactly as if the snapshot boundary had never occurred.

## Guarantees (verified in `tests/test_incremental.py`)

- **restart-invariance**: snapshot at any cut, restore into a fresh engine, continue → identical per-bar
  `output_fingerprint` (`test_chunk_size_invariance_via_snapshot` across five chunkings).
- **swing/break boundary**: snapshot taken with an unconsumed old swing live but the break not yet fired survives the
  restart and the break fires identically (`test_snapshot_restart_between_swing_and_break`).
- **fail-closed identity**: a snapshot from a different `(symbol, timeframe, interval, …)` identity, or a mismatched
  horizon, is rejected (`test_restore_rejects_foreign_snapshot_identity`).
- **bounded cost**: restore does not scan history — snapshot 0.8 ms / restore 0.4 ms at 20k, still < 1 ms at 355,696.
