# READY_FOR_LIVE_SHADOW_REVIEW_CANDIDATE_V2_CORRELATED

**Directive**: RT-TOWER-0010, `TOWER_CHAIN_ATR_PASS` (Red Team commit `68c6b59`), resuming RT-TOWER-0008 from checkpoint `ee92c8c`.
**Prior blocker**: `INTEGRATION_BLOCKED_TOWER_CHAIN_ATR_UNAVAILABLE` (closed by this delivery).
**Base checkpoint**: `ee92c8c472dab67598020ba90bad2dd73d2bba58`

## 1 — Final artifact install

```
package      ve_tower 0.5.2
wheel        ve_tower-0.5.2-py3-none-any.whl
SHA-256      1abcd60d6e541468a38e68a8b57e4200178585df37b489ff59b0ac99693c28d8  (verified 3 ways:
             own recompute from wheel bytes, release/SHA256SUMS.txt, HANDOFF_MANIFEST-0.5.2.json)
size         86775 bytes
build        b0cf2ea   ("ve_tower 0.5.2: correct N3 ATR provenance value, RT-TOWER-0009")
state        60bf71b   ("ve_tower: physical 0.5.2 wheel + sidecar manifest (N3 ATR provenance fix)")
                        -- the sidecar's OWN authoritative state_delivery_commit field
stamp        f7876ae   ("ve_tower: stamp 0.5.2 manifest state_delivery_commit 60bf71b")
                        -- documentary only, per the same three-commit discipline established for 0.5.0;
                           NOT used as state_delivery_commit even though the chat message called it "delivery"
entrypoint   run_tower_chain
```

**Before**: main venv snapshot recorded (`main_venv_snapshot_before_0.5.2.txt`) -- `ve_tower`/`ve_tower_worker` absent, confirmed via `pip show` (both "not found").
**Install**: clean `pip uninstall` of the prior 0.5.0 distribution, then `pip install --no-deps <verified wheel>` into the tower venv only -- non-editable (`ve_tower.__file__` resolves to `site-packages`). Worker package reinstalled the same way from the final source tree, non-editable.
**After**: `ve_tower 0.5.2` present in the tower venv only; main venv re-confirmed clean (`pip show ve-tower ve-tower-worker` -> both "not found").
**Pin**: `verify_pin(real_handshake_identity) == ()` -- zero mismatches, against a genuine, non-stub `EstablishedSession` from the real worker.
**Rollback**: demonstrated live -- uninstalled 0.5.2, installed the committed 0.5.0 wheel, real handshake against it was **correctly refused**: `HandshakeFailure(reason='HANDSHAKE_IDENTITY_MISMATCH', detail="ve_tower_package_version: expected='0.5.2' actual='0.5.0'")`. 0.5.2 then reinstalled and reverified before continuing.

## 2 — Pin / handshake, exact match

`ai_trader/new_brain_bridge/tower_identity_pin.py` updated (all 15 exact-match fields, +1 new):

```
EXPECTED_VE_TOWER_PACKAGE_VERSION      = "0.5.2"
EXPECTED_PACKAGE_BUILD_COMMIT          = "b0cf2ea"
EXPECTED_STATE_DELIVERY_COMMIT         = "60bf71b"
EXPECTED_WHEEL_SHA256                  = "1abcd60d6e541468a38e68a8b57e4200178585df37b489ff59b0ac99693c28d8"
EXPECTED_VENDORED_SOURCE_IDENTITY      = "sha256:4c0deecb...c647a69e1c"   (unchanged since 0.5.0 -- no re-vendoring)
EXPECTED_N2/N3/N4_CONTRACT_VERSION     = unchanged from 0.5.0
EXPECTED_CHAIN_*_VERSION               = unchanged from 0.5.0
EXPECTED_PRODUCTION_ENTRYPOINT         = "run_tower_chain"
EXPECTED_ATR_SOURCE_COMMIT             = "a80d8a085dfc26e3042beb512a10aa5c5c1ccb62"   -- NEW, RT-TOWER-0010
EXPECTED_WORKER_PACKAGE_VERSION        = "0.3.0"
EXPECTED_PROTOCOL_VERSION              = "3.0"
```

`EXPECTED_ATR_SOURCE_COMMIT` pins the vendored `market_state` module's own source commit (identical to `vendored_source_commits.market_state` in the sidecar -- confirming ATR is threaded from the SAME already-vendored, byte-identical module, not a new one). `WorkerIdentity` (both protocol.py copies), `InstallManifest`, `artifact_identity.py`, the artifact-identity test stub, and `sidecar_verification.py`'s `VerifiedSidecar`/`cross_check_against_existing_pin` all extended with `atr_source_commit`. Any `None`/mismatch on any of the 15 fields -> `HANDSHAKE_IDENTITY_MISMATCH` -> `TOWER_WORKER_STARTUP_FAILED` / `NO_TRADE` / `TOWER_UNAVAILABLE`, unchanged fail-closed behavior. Session HMAC unchanged (`tower_launcher.py`).

## 3 — Code finalized from checkpoint `ee92c8c`

Kept unchanged: chain protocol v3, worker exclusive to `run_tower_chain`, the AST guard against direct `run_n2`/`run_n3`/`run_n4`, `bridge.py`'s chain rewrite, N2/N3/N4/chain identity propagation, `regime_axes_status`'s `"available"`/`"unavailable"` correction, `test_e2e_readiness.py`'s migration.

Updated strictly for the 0.5.0 -> 0.5.2 diff: the pin (above), the tower venv's own install manifest (rewritten for 0.5.2, `installed_by="RT-TOWER-0010-remediation"`), the one-time wheel-install pin (`verify_tower_wheel.py`), the worker's runtime identity (via reinstall), the handshake (via the new `atr_source_commit` field), and every test asserting a hardcoded `"0.5.0"`/`b128d8b`/`26470f5` value against the live pin (either bumped to the 0.5.2 values or switched to reading `tower_identity_pin.EXPECTED_*` dynamically so this class of staleness can't recur). `ve_tower` itself was never rewritten by this division -- VE shipped the fix (0.5.1 first made N4 reachable, 0.5.2 corrected a wrong ATR-provenance VALUE that shipped with 0.5.1); `ve_brain` was never touched.

## 4 — The single correlated run

`demonstrate_candidate_v2_correlated.py` (repo root, evidence tooling, same convention as the prior CANDIDATE_V2 script). One execution, real installed components throughout:

closed bars -> `RawAxesBuilder` (N1) -> real `StrategyRouter.eligible` -> real IPC v3 -> the isolated worker -> `ve_tower.run_tower_chain` -> real N2 -> real N3 -> real N4 -> `ve_brain.decide_n6`'s own real `DecisionResponse` -> the official ratified cost model -> EV -> N6 -> real `submit_new_brain_candidate` (Risk Manager) -> real `attempt_shadow_execution` (Execution Adapter) -> `BrokerOrderSubmissionGate` -- **BLOCKED**.

**Bar-data provenance, disclosed**: live MT5 was tried first and honestly captured (`mt5_live_probe_result` in the evidence JSON) -- at execution time, real XAUUSD was in `UNCERTAIN_REGIME`/`TRUE_RANGE_NOT_IDENTIFIABLE` for every catalog strategy, so no real cycle reached N6 approval. Per the CEO's own explicit second option, this run instead uses `new_brain_bridge.tests.conftest.trend_up_regime_bars` -- the SAME versioned, git-tracked canonical fixture this repository's own real-artifact test suite already uses -- for the bar series N1 observes; the tower's own H1/M15/M5 windows are derived from that identical bar shape, anchored to one consistent `as_of`, never independently invented. The genuinely live MT5 connection is still used, separately, for the broker-evidence proof (below) -- a real system fact no fixture can substitute for.

**Zero manual construction**: `test_correlated_evidence_ast_guard.py` (new, 6 tests) AST-walks the evidence script and proves it never references `EventIdentity`/`DecisionResponse`/`DecisionProvenance`/`N2Response`/`N3Response`/`N4Response` as constructors, never references `run_n2`/`run_n3`/`run_n4`, never calls `set_authority`, never references `order_send`, never hardcodes `bias_direction="LONG"`, and never imports `ve_tower` directly (the only tower interaction is through `bridge.evaluate_bar` -> `TowerClient.request_chain` -> the isolated worker).

**The one permitted VALUE fixture**: `probability_inputs`, monkeypatched at `bridge_module.load_probability_inputs` exactly the way `test_probability_source.py` already established and proved safe -- labeled `TEST_ONLY_CANONICAL_FIXTURE` in the evidence output, never a production value, never demonstrating economic edge (200/150 outcome counts, the same illustrative numbers already disclosed elsewhere in this repo).

**Result**: `trend_pullback` reached a real `TRADE` decision (`TRADE_VALIDATED_EDGE`, `expected_value_net=1.159...`); `trend_shadow` independently reached `SHADOW_TRADE_CANDIDATE`; `range_fade`/`trend_experimental` refused for their own real reasons (`TRUE_RANGE_NOT_IDENTIFIABLE`, `NO_ELIGIBLE_STRATEGY`) -- proving the chain result is genuinely per-strategy, not a single forced outcome.

## 5 — Single correlated identity (from `CANDIDATE_V2_CORRELATED_EVIDENCE.json`)

```
market_event_id            XAUUSD:M15:430200
trace_id                   44ab1b6187f77690
configuration_fingerprint  3d8a8b6cd277a09b
worker_session_id          ed489567e1b64588adedf36b9be0e9e4
worker_identity_fingerprint 337660b500c913ce6e620153502ca6549dedc02f305e3985505e408c334703bb
tower_version               0.5.2
chain_binding_version       tower-chain-binding-v1
chain_fingerprint            112749852f7a1f8782fb4bbcf8477d044095ccc053b69a1c490ab8da775d2eee
chain_status / terminal     ok_chain / ok_chain
strategy_id                 trend_pullback   (side=1, provenance: StrategyContract.allowed_directions[0])
cost_model_fingerprint      860e208812d61406
n6_engine_version            ev-core@bdd15e5+ev-adapter-v1
```

Per-node identity -- shared `event_fingerprint=997d40de3e8aa57f` across N2/N3/N4 (the correlation key), DISTINCT `data_identity`/`node_input_fingerprint` per timeframe (never forced equal):

| node | contract | code version | data_identity timeframe/bar_count |
|---|---|---|---|
| N2 | tower-n2-request-v1 | STAT-LEVEL2-BIAS-H1-SPEC-v1.0 | H1 / 119 bars |
| N3 | tower-n3-request-v2 | level3-v2.0-reanchored | M15 / 150 bars |
| N4 | tower-n4-request-v2 | level4-v2.0-w3 | M5 / 150 bars |

N3 ATR provenance: `atr14(M15)[i-1]`. N4 ATR provenance: `atr14(M15)[i]` / `M15_band_1xATR`. Both per the sidecar's own `atr_source` field, both now genuinely non-`None` in the real response (the exact defect closed).

## 6 — Broker evidence (same run)

```
approved_upstream   = True
risk_approved        = True   (reason_codes: [])
reached_broker_gate  = True
broker_blocked       = True   (reason: "BrokerOrderSubmissionGate: order submission is DISABLED --
                                Mandate 2 integration not yet ratified by Red Team -- default-closed")
gate_enabled         = False  (the only reachable default -- never constructed enabled=True anywhere
                                outside this module's OWN fault-injection tests)
order_send_calls     = 0
orders_created        = 0
positions_created     = 0
balance_before/after = 1800.34 / 1800.34   (real MT5 demo account, read via RealMT5Gateway, unchanged)
equity_before/after  = 1800.34 / 1800.34   (unchanged)
```

`BROKER_ORDER_SUBMISSION` remains DISABLED throughout -- confirmed both by the gate's own `enabled=False` and by the account state genuinely not moving.

## 7 — Tests and validation

**Targeted (310/310 passing)**:
- 265 -- `ai_trader/new_brain_bridge/` + `ai_trader/mandate2_readiness/` (main venv), including the 6 new correlated-evidence AST-guard tests, the 4 new pin tests for `atr_source_commit`, and the renamed/added sidecar-verification tests for the 0.5.0-historical / 0.5.2-current split.
- 45 -- `tower_worker/tests/` (isolated tower venv), including the version-literal bump in `test_decision.py`.

**mypy --strict**: clean on `bridge.py`, `tower_client.py`, `tower_protocol.py`, `tower_bar_source.py`, `tower_identity_pin.py`, `event_identity.py`, both new mandate2_readiness test files, and all 11 `tower_worker/src` modules (isolated venv's own mypy).

**Full regression** (`venv\Scripts\python.exe -m pytest ai_trader/ -q`, main venv, never system Python):

```
passed:    3407
failed:    0
skipped:   2
warnings:  4   (pre-existing RuntimeWarning in vendor/alpha_automation_detectors/market_state.py,
                divide-by-zero in structural_observer's own tests -- unrelated to this segment,
                not touched here)
duration:  21347.47s  (5:55:47)
EXIT_CODE: 0
```

Not restarted mid-run, per instruction; ran to completion once, cleanly.

**Rollback/isolation**: proven live in section 1. Main-venv-unchanged: proven via `pip show ve-tower ve-tower-worker` on the main venv both before and after this segment's work -- "not found" both times.

## 8 — Operational safety (unchanged)

- `LIVE_SHADOW`: not started.
- `set_authority()`: never called (structurally proven by the AST guard, not just asserted).
- `BROKER_ORDER_SUBMISSION`: remains `DISABLED` -- `broker_gate.py` untouched this segment.
- `ve_brain` / `ve_tower` internals: untouched.
- Legacy / `market_intelligence` fallback: not reactivated.
- Alpha: `ALPHA_BLOCKED_CANONICAL_N1_HANDOFF`, unmodified. `CAND-T05`: frozen, unmodified.

## 9 — Delivery contents

- Code commit: pin/handshake/manifest/ATR-provenance updates, the single correlated-run script, its AST guard, all touched tests, the wheel-verification pin bump.
- This report.
- `CANDIDATE_V2_CORRELATED_EVIDENCE.json` -- the single-run evidence JSON.
- `main_venv_snapshot_before_0.5.2.txt` / `tower_venv_snapshot_before_0.5.2.txt` -- before-state proof.
- `full_regression_output_rt_tower_0010.txt` -- full regression transcript.

## Status

**READY_FOR_LIVE_SHADOW_REVIEW_CANDIDATE_V2_CORRELATED**

Awaiting Red Team's final delta verification for `PASS_FOR_LIVE_SHADOW`. `LIVE_SHADOW` not started, `set_authority()` never called, broker disabled, Alpha frozen, per standing instruction.
