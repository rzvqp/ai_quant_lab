# RED TEAM — MB3-001→024 PREDICTIONS FREEZE PROOF
### RT-RANGE-MB3-001 · `MB3_PREDICTIONS_FROZEN_BEFORE_LABEL_ACCESS`

Committed after Env A inference (`RUN_ATTEMPT=1`) and **before any label access**. The predictions payload
is not committed (only its hash + a sanitized, label-free manifest); it is stored read-only in the Red Team
escrow. Env B (scoring) is created only after this commit is pushed and `local=remote` confirmed.

```
batch                     = MB3-001 … MB3-024   (MB3-025..048 NOT processed, remain sealed)
predictions.json sha256   = 26a7d46179a85000354b5de3412872ab09fa4d1529a32bf7bd707dbe81e233ba
n_windows                 = 24
n_bars_total              = 6912   (8×96 + 8×288 + 8×480)
detector prototype_commit = f224e7d+F1   (ratified F1-only build bc6b9dc)
config_id                 = 24f72a60fcde42746d44f098558a745fac0f20b0141865bdbe0359f9cc3826da
implementation_fingerprint= f1-only-f5-deferred-2026-08-20
f1_bars_tolerated         = 10   (sub-tick OHLC, tolerated by the ratified F1 validator; OHLC unmodified)
```

**F1 / OHLC handling (mandate §4).** The ratified F1-only build's input validator (RT-RANGE-0013 PASS)
tolerated **10** sub-tick bars (close marginally outside `[low,high]` within `epsilon = min_tick/2 = 0.005`),
emitting `INPUT_OHLC_SUBTICK_TOLERATED` quality events on a separate channel. **No OHLC value was modified, no
gate was widened, the detector was not changed.** This is the already-ratified execution path, not an ad-hoc
fix — so no `MB3_EXECUTION_BLOCKED_F1`.

**Env A isolation (dynamic).** Inference read **no** label/scorer file (labels/fixtures/scoring removed from
the Env A tree); no subprocess, no socket. Input built from the corpus + the sealed window payload's canonical
indices only (contains no MACRO/level/CHANNEL/TREND/timestamp fields — verified).

`MB3_PREDICTIONS_FROZEN_BEFORE_LABEL_ACCESS` — labels are read only after this commit is pushed and verified.
