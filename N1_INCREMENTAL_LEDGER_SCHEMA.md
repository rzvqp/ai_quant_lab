# N1 incremental ledger — schema (`n1-incremental-ledger-v1`)

The canonical N1 ledger is produced **once** by a single O(n) forward pass (`N1IncrementalReplayEngine.replay_batch`)
and is then **read-only** for all 355 hypotheses. It is defined in `ve_n1_replay/ve_n1_replay/incremental.py`.

## Header (`N1IncrementalLedger`)

| field | type | meaning |
|---|---|---|
| `ledger_key` | str (16 hex) | fail-closed cache key — see below. Any identity change ⇒ new key ⇒ recompute. |
| `evaluation_identity_fingerprint` | str (16 hex) | `EvaluationIdentity.fingerprint()` — identical scheme to 0.1.0 (impl commit, wrapped runtime, ve_brain version+wheel SHA, detector source commit, detector config fingerprint, N1 contract, Router version, raw-axis schema, replay schema, symbol, timeframe, bar interval). |
| `history_horizon` | int | `460` — the bounded-axis horizon (COMPRESSION_WINDOW), derived in `N1_INCREMENTAL_HORIZON.md`. |
| `history_horizon_version` | str | `n1-history-horizon-v1`. |
| `ledger_schema_version` | str | `n1-incremental-ledger-v1`. |
| `ve_n1_replay_version` | str | `0.1.1`. |
| `data_identity` | str (16 hex) | `bars_content_hash` over the ordered OHLCV+time of every input bar — changes iff any bar's content changes, not merely its count. |
| `bar_count` | int | number of records. |
| `last_closed_bar_id` | str | `input_data_identity` of the last bar (`symbol:timeframe:ts_close`). |
| `records` | tuple[record] | one per closed bar, in order. |

## Record (`N1IncrementalLedgerRecord`, frozen)

| field | type | meaning |
|---|---|---|
| `bar_index` | int | 0-based position in the pass. |
| `ts_open`, `ts_close` | int | bar timestamps. |
| `is_compressed` | bool \| None | RawAxes — None until the 460-bar compression window is valid. |
| `is_displacement` | bool | RawAxes. |
| `direction` | str \| None | RawAxes (`up`/`down`/`weak_up`/`weak_down`/None). |
| `structure` | str \| None | RawAxes (`strong`/`weak`/None). |
| `availability_status` | str | `FULL`/`PARTIAL`/`UNAVAILABLE` (from 0.1.0 `_build_result`). |
| `regime_axes_status` | tuple[str] | per-axis `available`/`unavailable`. |
| `applicable_regimes` | tuple[str] | sorted `ve_brain.applicable_regimes(axes)` values. |
| `reason_codes` | tuple[str] | sorted router reason codes. |
| `input_data_identity` | str | `symbol:timeframe:ts_close` (the 0.1.0 market-event id). |
| `n1_output_fingerprint` | str | 0.1.0 N1 output fingerprint (`_fp` over the 4 axes). |
| `router_output_fingerprint` | str | 0.1.0 router output fingerprint. |
| `output_fingerprint` | str | `_fp(n1_output_fp, router_output_fp)` — the byte-comparable identity of the bar's decision. |
| `latest_break_kind` | str \| None | intermediate-state audit: `bos_bull`/`bos_bear`/`choch_bull`/`choch_bear`/None — the break that produced `structure`/`direction`. |

`as_dict()` on a record and `header()` on the ledger yield JSON-serializable primitives.

## `ledger_key` — fail-closed cache identity

```
ledger_key = _fp(
    evaluation_identity_fingerprint,   # 0.1.0 identity: dataset symbol/tf/interval, ve_brain wheel SHA,
                                       #   detector-config fingerprint, N1 contract, Router version, impl commit
    HISTORY_HORIZON_VERSION, str(HISTORY_HORIZON),   # incremental/horizon contract
    LEDGER_SCHEMA_VERSION, VE_N1_REPLAY_VERSION,      # ledger schema + wheel version
    data_identity,                     # content hash of the actual bars
    str(bar_count), last_closed_bar_id,
)
```

Every input the mandate names — dataset identity, ve_n1_replay wheel version, ve_brain wheel SHA (inside the evaluation
identity), detector fingerprint, N1 contract, Router version, horizon/incremental contract, last closed bar — is folded
in. A cached ledger whose stored `ledger_key` differs from a freshly computed one for the same request **must not** be
reused: the mismatch means an identity changed, so N1 is recomputed (fail-closed). Verified by
`test_ledger_key_invalidates_on_data_change` and `test_ledger_key_invalidates_on_horizon_change`.
