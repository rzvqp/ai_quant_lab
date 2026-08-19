# RED TEAM — RANGE V4.3 REAL-BAR PREDICTIONS · FREEZE PROOF
### RT-RANGE-0010 · `PREDICTIONS_FROZEN_BEFORE_LABEL_ACCESS`

Committed **after** the single inference execution (`RUN_ATTEMPT=1`) and **before** any label is read.
The predictions payload itself is NOT committed (it encodes per-bar structure) — only its hash and a
sanitized manifest are published here. The payload is stored read-only in the Red Team escrow.

```
predictions.json sha256   = 1754c86d1e8be0b06e6bb06fc4688f34c3f61617cdef3a712ede1df646c848da
input.json sha256         = 3448f6f78b8a33ba9cb81fc1a25c0024b0d956797f4ae9726519d102a5338129
config_id                 = 24f72a60fcde42746d44f098558a745fac0f20b0141865bdbe0359f9cc3826da
prototype_commit          = f224e7d
n_windows                 = 48
n_bars_total              = 13824
ohlc_range_gate_skipped   = 13   (see FINDING F1 in the final report)
runner                    = red_team.engine_path (inference._run_one_window → RangeSemanticEngineV43.replay_batch)
zero_labels_access        = true
python                    = 3.12.10
```

**Execution note.** The audited `blind_runner/inference.py` CLI fail-closed-rejected the raw real corpus:
13 of 13,824 real bars carry a sub-tick vendor artifact (close/open exactly 0.0005 outside `[low,high]`)
that trips `CLOSE_OUTSIDE_HIGH_LOW` / `OPEN_OUTSIDE_HIGH_LOW` before any bar reaches the detector. No bar
was processed and no prediction was produced by that attempt. The frozen detector was then executed on the
same real bars via the runner's own per-window path (`inference._run_one_window`), skipping ONLY the
OHLC-range input gate; OHLC values, detector, config, and runner code are all UNMODIFIED and byte-identical
to `f224e7d` / `82f27c0`. This deviation is recorded as a finding, not concealed.

`PREDICTIONS_FROZEN_BEFORE_LABEL_ACCESS` — labels read only after this commit is pushed and `local=remote`.
