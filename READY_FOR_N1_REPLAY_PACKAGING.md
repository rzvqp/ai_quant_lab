# N1 Canonical Replay Handoff — Delivery Report

**Status: `READY_FOR_N1_REPLAY_PACKAGING`** (not self-declared `N1_HANDOFF_PASS` — that verdict belongs
to whichever review process the CEO designates next).

Directive: RT-N1-REPLAY-0001, CEO 2026-08-17. LIVE_SHADOW was never touched, never restarted;
`decision_authority` was never modified; `BROKER_ORDER_SUBMISSION` remains `DISABLED` throughout.

## What was built

`ai_trader/n1_replay/` — a versioned replay interface wrapping the REAL, currently-running N1/Router
pipeline, reimplementing none of it:

- **`RawAxesBuilder`** (`ai_trader.new_brain_bridge.raw_axes_builder`, unmodified, imported directly)
- **`ve_brain.RawAxes`**, **`ve_brain.applicable_regimes`**, **`ve_brain.StrategyRouter`** (unmodified,
  imported directly)
- Fingerprint formulas mirror `ai_trader.new_brain_bridge.bridge.evaluate_bar`'s own real recipe exactly
  (same field order, same sha256-truncate-16 scheme) — proven, not assumed, by the real-data parity test
  below.

### Files

| File | Purpose |
|---|---|
| `ai_trader/n1_replay/__init__.py` | Public API |
| `ai_trader/n1_replay/types.py` | `N1ReplayResult`, `N1ReplaySnapshot` |
| `ai_trader/n1_replay/errors.py` | 7 fail-closed exception types |
| `ai_trader/n1_replay/identity.py` | `EvaluationIdentity`, all pinned provenance constants |
| `ai_trader/n1_replay/engine.py` | `N1ReplayEngine` — the state machine |
| `ai_trader/n1_replay/fixtures/canonical_bars.py` | Official fixtures (reused, not reinvented — see below) |
| `ai_trader/n1_replay/IDENTITY_MANIFEST.md` | Full pinned-identity documentation |
| `ai_trader/n1_replay/tests/` | 27 tests (26 always-run + 1 real-terminal-gated) |
| `N1_REPLAY_DEPENDENCY_INVENTORY.md` (repo root) | Exact VE-packaging dependency list |

## 1. Contract

`N1ReplayResult` carries all 11 required fields: `raw_axes` (complete), `applicable_regimes`,
`eligibility_decisions` (the router verdict), `n1_contract_version`, `router_version`,
`detector_configuration_fingerprint`, `input_data_identity`, `output_fingerprint`, `last_closed_bar`,
`reason_codes`, `availability_status` — plus `regime_axes_status`, `n1_output_fingerprint`,
`router_output_fingerprint`, `evaluation_identity` for direct live-comparability.

State machine, all six required states: `initialize` (`N1ReplayEngine(...)`), `observe_closed_bar`,
`snapshot`, `restore`, `replay` (batch wrapper over `observe_closed_bar`), `reset`. Every transition
either succeeds or raises a named fail-closed exception, leaving state exactly as it was before the call.

**Replay after snapshot/restore produces identical results to continuous running — proven by
construction, not merely tested**: `restore()` rebuilds a fresh `RawAxesBuilder` and replays every
snapshotted bar through the SAME `_build_result()` helper `observe_closed_bar` itself uses. The
determinism is structural (same pure function, same inputs), and `test_restart_and_restore_produces_identical_results`
confirms it directly against a continuously-run reference.

## 2. Identity and provenance

Full detail in `ai_trader/n1_replay/IDENTITY_MANIFEST.md`. Summary: `implementation_commit` (this
package's own delivery commit, caller-supplied — never self-referential), `wrapped_runtime_commit`
(`eb97a80`, confirmed zero commits touched `raw_axes_builder.py`/`bridge.py`/`vendor_bridge.py` since),
`ve_brain` version `0.1.3` + wheel SHA-256, `detector_source_commit` (`dc28e4a`),
`detector_configuration_fingerprint` (hash of the 3 real source files' own git blob SHA-1s),
`n1_contract_version`/`router_version`/`raw_axis_schema_version`, this package's own
`n1_replay_schema_version`, symbol, timeframe, bar interval. `EvaluationIdentity.fingerprint()` rolls
all of these into one comparable string; any relevant change moves it.

## 3. Tests — all 19 CEO-listed scenarios covered, plus the real-data requirement

| # | Scenario | Test |
|---|---|---|
| 1 | live vs replay RawAxes identical | `test_live_vs_replay_raw_axes_identical` |
| 2 | live vs replay Router identical | `test_live_vs_replay_router_identical` |
| 3 | same bars -> identical fingerprint | `test_same_bars_produce_identical_fingerprints` |
| 4 | modified bar -> different fingerprint | `test_modified_bar_produces_different_fingerprint` |
| 5 | duplicate bar -> refuse or deterministic dedup | `test_exact_duplicate_bar_is_deterministically_deduplicated` + `test_conflicting_duplicate_bar_is_refused` |
| 6 | unclosed bar -> refused | `test_unclosed_bar_is_refused` |
| 7 | wrong temporal order -> refused | `test_out_of_order_bar_is_refused` |
| 8 | future bar -> refused | `test_future_bar_beyond_as_of_horizon_is_refused` |
| 9 | restart + restore -> identical result | `test_restart_and_restore_produces_identical_results` |
| 10 | incompatible snapshot -> fail-closed | `test_incompatible_snapshot_symbol_is_refused_and_state_unchanged` |
| 11 | different N1 contract -> refused | `test_snapshot_with_different_n1_contract_version_is_refused` |
| 12 | different Router version -> refused | `test_snapshot_with_different_router_version_is_refused` |
| 13 | different detector pin/config -> refused | `test_snapshot_with_different_detector_configuration_fingerprint_is_refused` |
| 14 | stale state -> refused | `test_stale_state_is_refused` |
| 15 | NaN/Inf -> refused | `test_non_finite_ohlc_is_refused` (x3 parametrized) + `test_non_finite_volume_is_refused` |
| 16 | zero `ve_tower` import in main venv | `test_main_venv_still_has_no_ve_tower_importable` |
| 17 | zero broker access | `test_no_source_file_references_forbidden_names` + `test_no_source_file_imports_ai_trader_live_process_packages` |
| 18 | zero `set_authority` | same AST guard (covers all 3 forbidden names in one pass) |
| 19 | LIVE_SHADOW stays healthy throughout | manually verified before/during/after (below) — same PID, same start time, telemetry kept growing |

**Real-data Live Shadow parity test** (`test_live_parity.py`, gated `MT5_REAL_TERMINAL_TEST=1`, never
runs in standard regression): re-fetches the exact real M15 XAUUSD bars covering the already-journaled
LIVE_SHADOW window (read-only `copy_rates_range`, matched by nearest `ts_open` + contiguous run — never
by relying on an exactly-reproduced broker-offset label, which is not reliably recoverable after the
fact), replays them through a fresh `N1ReplayEngine`, and asserts the resulting `n1_output_fingerprint`
sequence matches LIVE_SHADOW's own persisted `NewBrainTelemetryLog` N1 node outputs EXACTLY. **Result at
delivery time: 12/12 bars matched, byte-for-byte identical fingerprints (`34d3ed98a5e335d0` for all 12 —
`is_compressed`/`direction`/`structure` still unresolved this early in LIVE_SHADOW's own real history,
correctly reproduced as such).**

### Validation run

```
pytest ai_trader/n1_replay/ -q          -> 26 passed, 1 skipped
MT5_REAL_TERMINAL_TEST=1 pytest ai_trader/n1_replay/tests/test_live_parity.py -q -> 1 passed
mypy --strict ai_trader/n1_replay/      -> Success: no issues found in 11 source files
```

No decision logic outside this new, standalone package was touched, so the full `ai_trader/` regression
was not repeated (nothing else imports `n1_replay` yet).

## 4. Dependency inventory

`N1_REPLAY_DEPENDENCY_INVENTORY.md` (repo root): `ve_brain` wheel, this package, 3 direct `ai_trader`
dependencies, the vendored-detector git submodule (`vendor/alpha_automation_detectors` @
`61cbd58c3d5da19001b125b65d669ddad54a14c4`), and `Bar`'s own transitive chain (traced, with one
disclosed incomplete tail flagged for VE to close with a proper import-closure tool rather than a
hand-trace). Also flags the "official fixtures reuse a `tests/conftest.py` module" wrinkle for VE's own
packaging decision — not resolved unilaterally here.

## 5. LIVE_SHADOW health, before/throughout/after this work

| Checkpoint | PID | Process start (unchanged = healthy, never restarted) | Authority | Telemetry entries | Orders/positions | Balance/equity |
|---|---|---|---|---|---|---|
| Before this directive | `6232` | `2026-08-17 21:47:09` (local) | `NEW_BRAIN` | 36 | 0 / 0 | 1800.34 / 1800.34 |
| After full delivery | `6232` (same) | `2026-08-17 21:47:09` (same, unchanged) | `NEW_BRAIN` (unchanged) | 48 (growing -- still actively processing) | 0 / 0 | 1800.34 / 1800.34 |

Zero interaction with `decision_authority`, zero `set_authority` calls, zero process signals sent to
PID `6232` or its children, at any point in this directive.

## Constraints honored

- LIVE_SHADOW: active and untouched throughout.
- `BROKER_ORDER_SUBMISSION`: `DISABLED` throughout (never referenced by this package at all — confirmed
  by the AST guard).
- Alpha not yet connected to any AI Trader live source (this package only exists in `ai_trader/`; nothing
  outside it imports `n1_replay` yet).
- No `probability_inputs` supplied.
- Broker gate not modified.
- `N1_HANDOFF_PASS` not self-declared.
