# LIVE_SHADOW_AUTHORIZATION_RECORD — v1

**This record authorizes LIVE_SHADOW only. It is NOT and must never be interpreted as
LIVE_ORDER_AUTHORIZATION, DEMO_ORDER_AUTHORIZATION, or authorization to unblock the broker
gate.** `BROKER_ORDER_SUBMISSION` remains structurally `DISABLED` throughout the entire
scope this record covers.

| Field | Value |
|---|---|
| `record_version` | 1 |
| `authorization_type` | `CEO_EXPLICIT` |
| `mode` | `LIVE_SHADOW` |
| `authorized_at_utc` | `2026-08-17T18:41:30Z` |
| `authorizing_directive` | "AUTORIZARE CEO — PORNEȘTE LIVE_SHADOW / AUTORIZEZ PORNIREA LIVE_SHADOW", received 2026-08-17 |
| `red_team_verdict` | `RT-MANDATE2-0003` |
| `red_team_commit` | `b05cbcb` |
| `ai_trader_code_commit` | `6e5a333` (RT-TOWER-0010 code: ve_tower 0.5.2 pin/handshake + single correlated run) |
| `ai_trader_report_commit` | `bf9243d` (`READY_FOR_LIVE_SHADOW_REVIEW_CANDIDATE_V2_CORRELATED.md`) |
| `activation_code_commit` | `eb97a80` — see disclosure below |

## Authorization basis and an explicit disclosure

`RT-MANDATE2-0003`/`b05cbcb` reviewed and passed the artifacts at `6e5a333`/`bf9243d`: the
`ve_tower` 0.5.2 ATR-provenance fix, the identity pin, and the single correlated evidence run
(`CANDIDATE_V2_CORRELATED_EVIDENCE.json`). **It did not review `ai_trader/new_brain_live/`**,
because that package did not exist yet — no continuous consumer of `new_brain_bridge` existed
anywhere in this codebase before this authorization. It was built afterward, by AI Trader
alone, specifically to carry out this directive (commit `eb97a80`, pushed and hash-verified
against `trader`/`ai-trader-implementation`).

`eb97a80` is pure orchestration around already-reviewed components (`evaluate_bar` via
`fail_safe.safe_evaluate_bar`, `risk_gate.submit_new_brain_candidate`,
`execution_shadow.attempt_shadow_execution`, `authority.current_authority`) — it introduces no
new decision logic, no new N2/N3/N4 call, no new cost model, and no order-capable import
(enforced by `ai_trader/new_brain_live/tests/test_ast_guard.py`, 3 tests). It carries its own
23 unit tests (fakes only, no real terminal) plus `mypy --strict` clean, run and verified
before this record was written. It has **not** been through Red Team's own adversarial review
process. This gap is disclosed here rather than silently assumed covered by `RT-MANDATE2-0003`.

## Ve_brain pin

| Field | Value |
|---|---|
| `ve_brain_package_version` | `0.1.3` |
| `ve_brain_source_commit` | `dc28e4a` (`ai_quant_lab-wp5b`, branch `discovery-mk-matrix-v1`) |
| `canonical_catalog_hash` | `37b95393df85dc2b` |
| `measurement_contract_version` | `canonical-evaluator-v2.7.66-A2` |
| `measurement_contract_status` | `v1.0-DRAFT — NOT RATIFIED` |
| `output_contract_id` | `ve.decision_response.v1` |
| `engine_version` | `ev-core@bdd15e5+ev-adapter-v1` |
| `broker_order_submission (ve_brain's own copy)` | `"DISABLED"` |
| `installed_wheel_sha256` | `edd208ad6c2c943b17a11759ece1fdf5ab2a7025779b191764c383ecce987d11` |

## Ve_tower pin (`ai_trader/new_brain_bridge/tower_identity_pin.py`, 15/15 fields, zero mismatches at install time)

| Field | Value |
|---|---|
| `ve_tower_package_version` | `0.5.2` |
| `package_build_commit` | `b0cf2ea` |
| `state_delivery_commit` | `60bf71b` |
| `wheel_sha256` | `1abcd60d6e541468a38e68a8b57e4200178585df37b489ff59b0ac99693c28d8` |
| `vendored_source_identity` | `sha256:4c0deecbec7afc74b1fc7f61898ad10e54b63d3b7c5cad63b80ee8c647a69e1c` |
| `atr_source_commit` | `a80d8a085dfc26e3042beb512a10aa5c5c1ccb62` |
| `n2/n3/n4/chain contract versions` | `tower-n2-request-v1` / `tower-n3-request-v2` / `tower-n4-request-v2` / `tower-chain-request-v1` / `tower-chain-response-v1` / `tower-chain-binding-v1` |
| `production_entrypoint` | `run_tower_chain` |
| `worker_package_version` | `0.3.0` |
| `protocol_version` | `3.0` |
| `installed_manifest_path` | `C:\Users\MEDION GAMING\ve_tower_venv\ve_tower_install_manifest.json` (all 15 fields match pin exactly) |

## Cost model

| Field | Value |
|---|---|
| `module` | `ai_trader/mandate2_readiness/shadow_cost_model.py` |
| `version` | `v1` |
| `calibration_status` | `RATIFIED` |
| `content_hash()` | `1341f228bb627e8bd33dc38822e2cc834efddd322a70f10561a120c4789f0111` |
| `configuration_fingerprint()` | `b7bb9a9aed17a1c8` |
| `source_report_commit` | `351f789` |
| `BASE_RATIFIED` | `full_spread_price=0.05, entry_slippage_price=0.00, exit_slippage_price=0.00` |
| `STRESS_RATIFIED` | `full_spread_price=0.08, entry_slippage_price=0.08, exit_slippage_price=0.08` |

Note on the per-event `configuration_fingerprint` field carried on `EventIdentity`/telemetry:
that value is NOT this static system fingerprint — `bridge.py` computes it fresh per event as
`_fp(trace_id, ve_brain.VE_BRAIN_VERSION)`. The static identity of this authorized
configuration is the set of pins above, not a single rolled-up hash.

## Broker gate state

| Field | Value |
|---|---|
| `gate.enabled` (default, `BrokerOrderSubmissionGate()`) | `False` |
| `BROKER_ORDER_SUBMISSION` (`ve_brain`) | `"DISABLED"` |
| `ai_trader/new_brain_live/entrypoint.py` gate construction | zero-arg default only, never `enabled=True` (AST-guard-proven) |
| `order_send` reachability from this package | zero — not imported, not referenced (AST-guard-proven) |

## Decision authority mechanism

| Field | Value |
|---|---|
| `state_store_key` | `"new_brain_bridge.decision_authority"` |
| `default_value` | `LEGACY` (any account with no persisted value) |
| `switch_function` | `ai_trader.new_brain_bridge.authority.set_authority(state_store, DecisionAuthority.NEW_BRAIN)` — first invocation in this codebase's history, performed under this record |
| `read_function` | `ai_trader.new_brain_bridge.authority.current_authority(state_store)` |
| `state_store_path_for_this_activation` | `ai_trader/new_brain_live_state/xauusd_m15.db` (`entrypoint.DEFAULT_DB_PATH`) |
| `legacy_demotion` | `pdh_pdl_demo` / `multi_policy_live` / `market_intelligence` become `LEGACY_SHADOW_TELEMETRY` on any process that reads `current_authority` and finds it not `NEW_BRAIN`; `new_brain_live` never falls back the other direction |

## Expiration / review condition

This authorization remains valid only while ALL of the following continue to hold. Any one
failing requires the running process to reach `NO_TRADE`/`BRAIN_UNAVAILABLE` or
`NO_TRADE`/`TOWER_UNAVAILABLE` (never a fallback to legacy authority) and requires a fresh CEO
authorization before any restart:

- `BROKER_ORDER_SUBMISSION` remains `DISABLED` and `gate.enabled` remains `False`.
- No code under `ai_trader/new_brain_live/`, `ai_trader/new_brain_bridge/`, or the pinned
  `ve_tower`/`ve_brain` artifacts is modified without a new authorization record.
- The pins above (ve_brain `0.1.3`, ve_tower `0.5.2`/`b0cf2ea`/`60bf71b`) remain unchanged.
- Zero orders, zero positions are ever created by this process.
- Review trigger: 7 days from `authorized_at_utc`, OR any `EMERGENCY_SHADOW_STOP`, OR any
  unexplained balance/equity delta, whichever comes first.

## Rollback procedure

1. Send `SIGTERM` (or `SIGINT`) to the `new_brain_live` process PID — `NewBrainLiveLoop.
   run_forever`'s installed signal handler sets `stop_requested`, finishes the in-flight tick,
   and closes the state store cleanly; no new bars are processed after that point.
2. Confirm process exit (PID no longer present).
3. Optionally revert authority: `set_authority(SqliteStateStore(DEFAULT_DB_PATH),
   DecisionAuthority.LEGACY)` — NOT required for safety (the process is stopped either way;
   `pdh_pdl_demo`/`multi_policy_live` do not reclaim authority automatically per section 3's
   own "never reclaim" rule even if this step is skipped).
4. All journal/telemetry data in `ai_trader/new_brain_live_state/xauusd_m15.db` is preserved,
   never deleted, regardless of rollback reason.
5. No broker-side action is ever required, since no order/position was ever created.

---
Prepared by AI Trader division, `ai_quant_lab-research-main`, branch `ai-trader-implementation`.
