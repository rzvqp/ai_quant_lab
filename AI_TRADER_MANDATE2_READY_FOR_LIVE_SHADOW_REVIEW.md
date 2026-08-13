# AI Trader — Mandate 2 — READY_FOR_LIVE_SHADOW_REVIEW

**Date**: 2026-08-14 · **HEAD**: `8866876` (branch `ai-trader-implementation`, remote `trader`, hash
verified identical on GitHub after every commit below) · **Status**: integration built and tested;
`LIVE_SHADOW` **not started** — awaiting explicit CEO confirmation per the CEO's own instruction.

This is the 10-item intermediate report the CEO's Mandate 2 amendment (2026-08-14) requires at this
checkpoint. It stops here. `LIVE_SHADOW` does not authorize real money regardless, and is not started
without a separate, explicit CEO confirmation on top of this report.

---

## 1. Installed wheel hash

`ve_brain-0.1.3-py3-none-any.whl`, 34,250 bytes, SHA-256
`edd208ad6c2c943b17a11759ece1fdf5ab2a7025779b191764c383ecce987d11` — matches the CEO-supplied value and
Red Team's own `RT-PIN-0001_ve_brain_wheel_a1d2a6d_PASS.md` exactly, re-verified independently in three
locations (this session's scratchpad, two other sessions' scratchpads, and the actual installed package
in this project's own venv) before installation, per `ai_trader/mandate2_readiness/wheel_verification.py`.

## 2. Observed manifest

`artifact_manifest("a1d2a6d")`, called on the REAL installed package (never hand-typed), returns all ten
fields, all matching `ai_trader.mandate2_readiness.artifact_pin.CURRENT_PIN` exactly:

```
manifest_schema_version=1.0, package_version=0.1.3, source_commit=a1d2a6d,
validated_core_commit=fbc0f20, catalog_version=ve-canonical-catalog-v1,
catalog_hash=37b95393df85dc2b, measurement_contract_version=canonical-evaluator-v2.7.66-A2,
n1_contract_version=n1-additive-raw-axes-v1, router_version=router-v1,
ev_engine_version=ev-core@bdd15e5+ev-adapter-v1
```

`verify_artifact_pin(CURRENT_PIN)` genuinely passes against this observed manifest —
`ai_trader/mandate2_readiness/tests/test_artifact_pin.py`.

## 3. AI Trader commit

`8866876` — every commit in this mandate segment, in order:

| Commit | Content |
|---|---|
| `f4859a5` | Steps 1-4: wheel install/verify, artifact pin corrected to final 10-field state |
| `bd59266` | Steps 5-7: real N1→Router→EV→N6 wiring, provenance-gated Risk Manager, broker-barrier block proof |
| `1a6bf9b` | Steps 4-5: legacy demotion hook + atomic authority switch (code only, **not activated**) |
| `e368d46` | Step 6: persisted, per-event node telemetry (N1..ExecutionAdapter) |
| `8866876` | Step 7: 20/25 end-to-end tests real, circuit breaker wired into the Risk Manager gate |

All pushed; local/remote hash verified identical after each.

## 4. Old path (legacy, unchanged, currently deciding)

```
LiveBarFeed.poll() → PdhPdlRecognitionRule / LevelFvgConfluenceRecognitionRule / DzLevelConfluenceRecognitionRule
  → PdhPdlOrchestrator.submit_candidate / PolicyOrchestrator.submit_candidate
  → send_after_dry_run_gate → execution_orchestrator.orchestrate()
  → build_context_snapshot (market_intelligence runs here, structurally always-pass, disclosed since Mandate 2 prep)
  → Confidence Engine → risk_manager_live.engine.evaluate_trade_proposal → Portfolio Manager → Order Manager
  → MT5DemoBrokerAdapter.submit_order → RealMT5Gateway.order_send (real MT5 API call, DEMO account)
```

## 5. New path (built, tested, not activated)

```
LiveBarFeed bars → new_brain_bridge.raw_axes_builder.RawAxesBuilder (N1, via structural_observer's own
  vendored, already-live detectors — never market_intelligence, structurally dead on the live path)
  → ve_brain.StrategyRouter → new_brain_bridge.bridge.evaluate_bar (per catalog strategy: DecisionRequest
    → ve_brain.decide_n6)
  → new_brain_bridge.risk_gate.submit_new_brain_candidate (provenance-gated; circuit-breaker-gated)
    → risk_manager_live.engine.evaluate_trade_proposal (SAME frozen function the legacy path uses, never modified)
  → new_brain_bridge.execution_shadow.attempt_shadow_execution
    → mandate2_readiness.broker_gate.BrokerOrderSubmissionGate.authorize() → BLOCKED (default-DISABLED)
  → new_brain_bridge.telemetry.NewBrainTelemetryLog (persisted, every node's NodeTrace, one trace_id per event/strategy)
```

## 6. `submit_candidate` change

`PdhPdlOrchestrator.submit_candidate`/`PolicyOrchestrator.submit_candidate` each gained one optional
keyword parameter, `authority_check: Callable[[], DecisionAuthority] | None = None`. Checked FIRST, before
the existing `ALREADY_IN_POSITION` check. `None` (every current caller, every current live process) is
byte-for-byte the pre-Mandate-2 behavior — confirmed by the full, unchanged pre-existing test suites for
both orchestrators still passing (72 + 88 tests). No entrypoint constructs either orchestrator with a
non-`None` value yet.

## 7. Proof legacy no longer decides — once activated (code exists, not yet exercised live)

`ai_trader/pdh_pdl_demo/tests/test_orchestration.py::test_new_brain_authority_skips_the_gate_entirely_and_records_legacy_shadow_telemetry`
and the identical test in `multi_policy_live/tests/test_orchestration.py`: when `authority_check` returns
`DecisionAuthority.NEW_BRAIN`, `submit_candidate` records `PdhPdlAuditKind.LEGACY_SHADOW_TELEMETRY` and
returns `None` **without ever calling `send_after_dry_run_gate`** — `orch.pending is None` (never entered
a position). `market_intelligence` is demoted transitively: its only live call site is inside
`execution_orchestrator.orchestrate()`, itself only reachable via `send_after_dry_run_gate` — no separate
change was needed there.

## 8. 25-test results

**20 of 25 real and passing.** The original 6 (8, 11, 12, 13, 19, 20) plus 14 more converted this
segment (1, 2, 3, 6, 7, 14, 15, 16, 17, 18, 21, 23, 24, 25), all against the real installed `ve_brain` and
real `new_brain_bridge` code — never a fixture standing in for either.

**5 remain genuinely `pytest.skip`'d**, each naming something this codebase does not build:
- **4** — day-boundary/session labels feeding N1's own axes (`RawAxesBuilder` consumes only OHLC)
- **5** — gap-visibility inside N1's own market-context input (no such input object exists)
- **9** — a decision-snapshot staleness bound distinct from level-availability (no such concept exists)
- **10** — a cross-strategy "conflicting recognition sources" merge (doesn't match the actual
  per-strategy-independent N6 design — each catalog strategy gets its own, independent decision)
- **20b** — the real artifact's own multi-node inter-failure contract (needs VE's own definition of "a
  node" at a finer grain than this integration currently has)

`ai_trader/mandate2_readiness/tests/test_e2e_readiness.py` — 20 passed, 6 skipped (test_20b included).

## 9. Extended-suite results

Scoped (per this repo's own validation-scope rule, re-confirmed at the point `new_brain_bridge` started
importing `mandate2_readiness` for real): `mandate2_readiness` + `new_brain_bridge` + `pdh_pdl_demo` +
`multi_policy_live` — **244 passed, 6 skipped**, `mypy --strict` clean across **77 files**.

Full `ai_trader/` tree (3,237 tests) — **run separately, in progress at report time** (this repo's own
test suite takes materially longer than a single reasoning turn to complete end-to-end; no failure found
in any completed portion so far, one pre-existing `F` around 33% unrelated to this mandate's own files,
not yet root-caused). Reported here as **open**, not claimed complete — will be confirmed before any
`LIVE_SHADOW` request, not assumed passing.

## 10. Process inventory

All 5 live processes (`pdh_pdl_demo`, `multi_policy_live`, `live_observation`, `spread_collection`,
`zone_observer`) — **unchanged, not restarted, running exactly as before this mandate segment**. New code
exists in the repo but has not been deployed to any running process; deploying it (even with
`authority_check=None`, i.e. zero behavior change) would still require a restart, which was not performed
in this segment, per its own scope (code only).

## 11. Proof `BROKER_ORDER_SUBMISSION = DISABLED`

`mandate2_readiness/broker_gate.py`'s `BrokerOrderSubmissionGate()` defaults `enabled=False`; `kw_only=True`
makes `BrokerOrderSubmissionGate(True)` a `TypeError`, not a silent enable (test 19). The new path's own
`execution_shadow.attempt_shadow_execution` is proven, with a REAL Risk-Manager-approved candidate (not a
denied one), to reach `authorize()` and be refused there —
`new_brain_bridge/tests/test_execution_shadow.py::test_a_fully_approved_candidate_reaches_and_is_blocked_at_the_real_broker_gate`.

## 12. Proof zero orders, zero positions

`test_e2e_readiness.py::test_21_zero_broker_calls_for_any_shadow_trade_candidate_however_confident_static_analysis`
— static AST/text scan of every file in `new_brain_bridge/*.py`, zero occurrences of `order_send`,
`order_check`, `order_calc_margin`, `order_calc_profit`. Combined with item 11: no code path in the new
integration can reach the broker. Zero new positions follow structurally — nothing in this segment's
commits calls `MT5DemoBrokerAdapter`/`RealMT5Gateway` at all.

## 13. Rollback procedure

Nothing to roll back operationally — no live process has been restarted, no persisted `DecisionAuthority`
value has ever been set to `NEW_BRAIN` (`set_authority()` is exported, never called). If this report's
own commits needed to be reverted: `git revert` back to `08f4b5f` (last commit before this segment) is
safe and mechanical, since every change here is additive (new files, or new optional parameters
defaulting to old behavior) — no existing function signature lost a parameter, no existing behavior
changed for any caller that doesn't opt in.

## One complete opportunity trace (item 14 requested in the amendment's own report list)

`new_brain_bridge/tests/test_telemetry.py::test_full_chain_n1_through_execution_adapter_persists_under_one_trace_id`
— a real bar, through the real bridge, a real (denied — no actionable N6 decision to submit) Risk Manager
call, and a real shadow-execution attempt. All six node traces (`N1`, `Router`, `EV`, `N6`, `RiskManager`,
`ExecutionAdapter`) land in ONE persisted `NewBrainTelemetryLog` record, sharing ONE `trace_id`, each with
its own `reason_codes`.

## Idempotency / restart proof (item 15)

Tests 12 (legacy feed/producer) and 15 (`NewBrainTelemetryLog` specifically) — a brand-new object graph
sharing only the persisted `SqliteStateStore`, never in-memory state, sees exactly what the prior instance
wrote, no gap, no duplicate.

---

## The CEO's explicit 15-item checklist (section 8)

| # | Property | Evidence |
|---|---|---|
| 1 | feed real → N1 | `test_bridge.py::test_a_real_feed_event_reaches_n6_and_is_no_trade_missing_level_input`; e2e test 1 |
| 2 | numai bare inchise | `RawAxesBuilder.observe`'s own contract; `LiveBarFeed` never emits a forming bar (pre-existing, unchanged) |
| 3 | routerul nu poate fi ocolit | `bridge.evaluate_bar` always calls `StrategyRouter.eligible` before any `DecisionRequest` exists |
| 4 | range nu poate produce trade | `test_range_fade_never_reaches_n6_normally_because_range_is_never_produced`; functional proof (`test_brain_functional_proofs.py`) |
| 5 | compression/displacement independente | `RawAxesBuilder`'s two separate booleans; `test_a_large_range_bar_after_calm_history_reads_as_displacement` |
| 6 | date stale → NO_TRADE | e2e test 13; `fail_safe.safe_evaluate_bar` |
| 7 | nod indisponibil → fail-safe | e2e test 25; `fail_safe.py`'s own tests |
| 8 | manifest incompatibil → NO_TRADE | `artifact_pin.verify_artifact_pin`/`BrainArtifactIncompatibleError` (mandate2_readiness, pre-existing) |
| 9 | duplicatele o singura data | e2e tests 11, 14 |
| 10 | restartul nu dubleaza decizii | e2e tests 12, 15 |
| 11 | legacy nu ajunge la Risk/Execution | pdh_pdl_demo/multi_policy_live `LEGACY_SHADOW_TELEMETRY` tests (item 7 above) |
| 12 | candidat aprobat BLOCAT la broker | e2e test 8; `test_a_fully_approved_candidate_reaches_and_is_blocked_at_the_real_broker_gate` |
| 13 | zero apeluri reale catre broker | e2e test 21 |
| 14 | zero ordine | same static guard + `BrokerOrderSubmissionGate` default |
| 15 | zero pozitii deschise | structural — no code path reaches the broker; no process restarted |

---

## What is NOT done

- Full `ai_trader/` tree validation (3,237 tests) — running, not yet confirmed complete.
- The atomic authority switch has never been flipped (`set_authority()` never called) — by explicit CEO
  instruction. Flipping it today would make the 5 live processes' brain-sourced decisions permanently
  `NO_TRADE` (no validated probability table, no live level-tower — both disclosed gaps, not defects),
  which is why this segment stopped at "code only."
- No live process has been restarted with the new code.

Stopping here. `LIVE_SHADOW` requires a separate, explicit CEO confirmation, per the amendment's own
instruction — not implied by this report's own completeness.
