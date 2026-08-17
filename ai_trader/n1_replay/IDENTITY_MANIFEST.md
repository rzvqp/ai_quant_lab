# N1 Replay — Identity Manifest

Every value below is a real, currently-verified constant or git blob hash — none are typed literals
invented for this document; each is read at runtime from `ai_trader.n1_replay.identity` (which itself
reads from `ve_brain`, `ai_trader.mandate2_readiness.wheel_verification`, and `git hash-object` on the
three source files it pins).

## Wrapped runtime

| Field | Value |
|---|---|
| `WRAPPED_RUNTIME_COMMIT` | `eb97a80` (full: `eb97a804172a6b275311c351f080dac421d6dbb5`) |
| Zero commits touched `raw_axes_builder.py`/`bridge.py`/`vendor_bridge.py` between `eb97a80` and this package's own delivery commit | confirmed via `git log --oneline eb97a80..HEAD -- <3 paths>` → empty |
| `RAW_AXES_BUILDER_BLOB_SHA1` | `d071c8cbd993cb9377b70af6b61e353d4c101966` |
| `BRIDGE_PY_BLOB_SHA1` | `b4a301371e7c2f174064dc2d50129912f3d82a52` |
| `VENDOR_BRIDGE_BLOB_SHA1` | `bb53680c2180a23366b9aa5a08130b4410ea6683` |

## `ve_brain` artifact

| Field | Value |
|---|---|
| `VE_BRAIN_VERSION` | `0.1.3` |
| `VE_BRAIN_WHEEL_SHA256` | `edd208ad6c2c943b17a11759ece1fdf5ab2a7025779b191764c383ecce987d11` |
| `DETECTOR_SOURCE_COMMIT` (`ve_brain.version.SOURCE_COMMIT`) | `dc28e4a` (`ai_quant_lab-wp5b`, branch `discovery-mk-matrix-v1`) |
| `N1_CONTRACT_VERSION` | `n1-additive-raw-axes-v1` |
| `ROUTER_VERSION` | `router-v1` |
| `RAW_AXIS_SCHEMA_VERSION` | `raw-axis-v1` |

## Vendored detector source (transitive, via `vendor_bridge.py`)

| Field | Value |
|---|---|
| Git submodule | `vendor/alpha_automation_detectors` |
| Tracks | `ai_quant_lab-alpha-automation`, branch `discovery-mk-matrix-v1` |
| Pinned commit | `61cbd58c3d5da19001b125b65d669ddad54a14c4` |
| Modules consumed | `market_structure.py` (`Block`, `detect_swings`, `label_structure`, `detect_breaks`), `market_state.py` (`expansion`, `compression`, `atr14`) |

## This package's own schema

| Field | Value |
|---|---|
| `N1_REPLAY_SCHEMA_VERSION` | `n1-replay-contract-v1` |
| `N1ReplayResult`/`N1ReplaySnapshot`/`EvaluationIdentity` field shapes | `ai_trader/n1_replay/types.py`, `ai_trader/n1_replay/identity.py` |

## Composite identity

`EvaluationIdentity.fingerprint()` = sha256 (first 16 hex chars) of, in order: `implementation_commit`
(caller-supplied, this package's own delivery commit), `wrapped_runtime_commit`, `ve_brain_version`,
`ve_brain_wheel_sha256`, `detector_source_commit`, `detector_configuration_fingerprint` (itself a hash
of the three blob SHA-1s above), `n1_contract_version`, `router_version`, `raw_axis_schema_version`,
`n1_replay_schema_version`, `symbol`, `timeframe`, `bar_interval_seconds`.

**Any relevant change updates this fingerprint** — `N1ReplayEngine.restore()` refuses a snapshot whose
identity fingerprint does not exactly match the target engine's own (`IncompatibleSnapshotError`,
proven by 3 dedicated single-field-mismatch tests: N1 contract version, Router version, detector
configuration fingerprint — `ai_trader/n1_replay/tests/test_engine.py`).
