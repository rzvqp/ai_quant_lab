# RED TEAM — PHASE-2 FINAL VERIFICATION · READY_FOR_LIVE_SHADOW_REVIEW_CANDIDATE_V2_FINAL
### RT-MANDATE2-0002 · **MANDATE_2_REVIEW_CONDITIONAL**
**Date:** 2026-08-16 · **Auditor:** Red Team · **Target:** AI Trader delivery — report `c7f87a3`, corrected code `a98a0a4`, branch `ai-trader-implementation`. **Verified at `a98a0a4`/`c7f87a3` (not prior versions).** No engine modified; no real data traded; nothing changed outside `red_team/`.

# VERDICT — **MANDATE_2_REVIEW_CONDITIONAL**
The delivery is materially sound on six of the seven review areas (delivery integrity, worker/tower isolation, cost-model wiring, authority-switch mechanism, broker-gate blocking, and the benign nature of the 2 skips / 4 warnings all PASS). It is held to **CONDITIONAL by the single decisive requirement (Area 2): there is no single correlated chain.** The evidence glues **three separate, non-correlated proofs**, and the "fully-approved candidate → broker BLOCKED" proof is **constructed exclusively in test** — precisely the two things the CEO's rule maps to CONDITIONAL and explicitly forbade for the approved-candidate proof. This is **not FAIL**: no decision component is bypassed in the *production* path; the bypasses live in the evidence tooling, not in `bridge.evaluate_bar`.

Governing CEO rule applied verbatim: *"Orice lipire a unor probe separate fără identitate comună: MANDATE_2_REVIEW_CONDITIONAL. Orice bypass reproductibil al unei componente de decizie: MANDATE_2_REVIEW_FAIL."* → the first clause applies; the second does not.

---

## AREA 2 (DECISIVE) — the single correlated chain is NOT demonstrated
`demonstrate_candidate_v2_full_path.py` @ `a98a0a4` is **three disjoint proofs with three unrelated identity sets**:

| # | Part | What it does | Identity | Chain coverage |
|---|------|--------------|----------|----------------|
| 1 | `part1_real_live_path` | 250 real MT5 bars → `RawAxesBuilder`(N1) → `evaluate_bar` → trend_pullback → **UNCERTAIN_REGIME** | real MT5 `market_event_id` | Router **stops before the tower**; N3/N4/EV/N6/Risk/broker **never reached** |
| 1b | `part1b_direct_tower_probe_on_live_data` | **bypasses the Router**; hand-builds a `TowerRequest`, calls `tower_client.request_n3_n4` → 37 N3 levels | **FABRICATED**: `event_fingerprint=""`, `data_identity="candidate-v2-direct-probe-data-identity"`, `node_input_fingerprint="candidate-v2-direct-probe-node-input"`, `n1={"fingerprint":"candidate-v2-direct-probe-n1"}`, `strategy_id="candidate-v2-direct-probe"` | tower only; unrelated to Part 1 |
| 2 | `part2_fully_approved_candidate_blocked_at_broker` | **constructs** `EventIdentity`/`DecisionResponse`/`DecisionProvenance`/`NewBrainOutcome` directly, injects at `submit_new_brain_candidate` → real Risk → `attempt_shadow_execution` → broker gate **BLOCKED** | **FABRICATED**: `trace_id="candidate-v2-demo-trace"`, `market_event_id="candidate-v2-demo-event"`, `configuration_fingerprint="candidate-v2-demo-cfg"`; `decision="SHADOW_TRADE_CANDIDATE"` | **bypasses N1→N2→IPC→N3→N4→Router→Eligibility→EV→N6**; unrelated to Parts 1 & 1b |

**No single `market_event_id` / `trace_id` / `event_fingerprint` / `data_identity` / `node_input_fingerprint` / worker `session_id` / `configuration_fingerprint` spans all three.** That is exactly *"lipirea unor probe separate fără identitate comună."* And Part 2's approved candidate is built by hand ("the same established pattern, test 8/16/17"), violating the CEO's explicit requirement: *"dovada candidatului complet aprobat trebuie să traverseze aceleași componente instalate și aceeași cale de producție/replay, nu ocoliri construite exclusiv în test."*

### Why CONDITIONAL, not FAIL — the *production* path is intact
The bypasses are confined to the **evidence script**. In production, `ai_trader/new_brain_bridge/bridge.py::evaluate_bar` @ `a98a0a4` genuinely traverses every decision component:
- **N1** via `RawAxesBuilder`; **Router** `router.eligible(...)`;
- **isolated worker** `tower.client.request_n3_n4(request)` (real IPC). The worker (`tower_worker/.../decision.py`) **ignores the client's placeholder identity fields** and feeds the **real bars** to `ve_tower.run_n3`/`run_n4` with `source_identity=f"tower-client:{symbol}:M15"` — so **ve_tower's own data-substitution protection is intact** (RT-TOWER-0002 defense not bypassed);
- **cost model** consumed fail-closed (Area 4); **EV**, **N6**, **Risk Manager**, **Execution Adapter**, **broker gate** all executed.

No reproducible bypass of a decision component exists in the production path → the FAIL clause does not fire.

### Supporting finding (production identity is thin — a real gap, but not itself FAIL)
Even the production bridge does **not preserve-and-verify the CEO-enumerated rich identities** end-to-end:
- The IPC `TowerRequest` is sent with `event_fingerprint=""`, `data_identity=_fp(market_event_id,"data-identity")`, `node_input_fingerprint=_fp(market_event_id,"node-input")` — **placeholders**, not the real bar-bound identities.
- The worker computes the **real** `ve_tower` `event_fingerprint`/`data_identity`/`node_input_fingerprint` and returns them, but the bridge **does not propagate them downstream**: the `Tower` `NodeTrace.input_fingerprint = _fp(market_event_id,"tower")`, `trace_id = _fp(market_event_id, strategy_id, strategy_version)`, `configuration_fingerprint = _fp(trace_id, VE_BRAIN_VERSION)`. The worker `session_id`/`worker_identity_fingerprint` are verified at the client handshake but **not threaded into the candidate provenance**.
- Net: the production correlation spine is **`market_event_id` + a derived `trace_id` only**; the tower's real `event_fingerprint`/`data_identity`/`node_input_fingerprint`/`session_id` are not carried into the candidate/N6/Risk provenance. This is a provenance-correlation gap, not a decision bypass → reinforces CONDITIONAL.

---

## AREAS THAT PASS

**Area 1 — Delivery integrity: PASS.** `a98a0a4` (`Wire bridge.py exclusively to AI_TRADER_SHADOW_COST_MODEL_v1…`, 2026-08-16 19:05:10 +0300) and `c7f87a3` both exist; `a98a0a4` **== remote `trader/ai-trader-implementation` HEAD** (local==remote). Report ↔ code consistent. **2 skips** = `MT5_REAL_DEMO_ORDER_TEST` / `MT5_REAL_TERMINAL_TEST` (operator-gated real-order tests) — **correctly left OFF for LIVE_SHADOW with the broker blocked; irrelevant to the shadow path.** **4 warnings** = pre-existing divide-by-zero in `vendor/alpha_automation_detectors/code/market_state.py:92`, unrelated to Mandate-2. *Limitation:* I did **not** independently re-run the 4h20m regression (15594.95s); I verified structure (test files exist, fail-closed logic present, exit-0/3393-passed claim internally consistent), not a full re-run.

**Area 3 — Worker/tower isolation: PASS.** `bridge.py` no longer imports `ve_tower` in the main process (verified: no `import ve_tower`); the three `False`s are now **real reads** from the tower response (`n3.get("market_map_available") is True`, etc.) with fail-closed `False` only on tower-absent/malformed (lines 164/202). Worker `server.py::_stamp_session` stamps `session_id`/`worker_identity_fingerprint` **unconditionally, re-derived from `identity_fn`, never from client input**, with HMAC over `challenge + canonical_identity + session_id`. Worker unavailable/malformed → honest `ok=False` + `TOWER_UNAVAILABLE`/`MALFORMED_TOWER_REQUEST`, zero fabricated zones.

**Area 4 — Cost model: PASS.** `bridge.py` consumes exclusively `resolve_cost_components(tier="BASE")` from `mandate2_readiness.shadow_cost_model`. Fail-closed: fingerprint ≠ `cost_model_configuration_fingerprint()` → `COST_MODEL_FINGERPRINT_MISMATCH`; resolution failure → `COST_MODEL_UNAVAILABLE` (degrades every strategy that bar). **No hardcoded cost numeric literals** in `bridge.py` (grep-clean). Guard/consumption tests present: `new_brain_bridge/tests/test_bridge_cost_model_wiring.py`, `mandate2_readiness/tests/test_shadow_cost_model.py`. Economic ratification not reopened.

**Area 5 — Authority switch: PASS (INACTIVE).** `set_authority` is exported and covered by `test_authority.py` (real `SqliteStateStore`), but **never called in any production or demo path** — the only non-test references are the docstrings stating exactly that. Atomic switch verified **without activation**; not invoked.

**Area 6 — Broker blocked: PASS (mechanism).** `BrokerOrderSubmissionGate` default `enabled=False`; a COMPLETE approved candidate yields `reached_broker_gate=True, blocked=True`; `enabled=True` is grep-able and constructed nowhere except explicitly. Part 2 reports positions=0, orders=0, balance unchanged (1800.34). **Caveat:** the candidate reaching the gate in the demo is the *fabricated* Part-2 candidate, so this proof inherits the Area-2 correlation caveat — the gate mechanism is real; the candidate that exercises it is not production-produced.

---

## CONDITION TO CLEAR → PASS_FOR_LIVE_SHADOW
Produce **one** run — via **replay** of a historical bar/date whose regime actually routes a strategy through the **installed** components — that traverses, with **one shared identity set**:

> MT5 closed bar → N1 → N2 → isolated IPC worker → N3 → N4 → StrategyRouter → EligibilityDecision → StrategyCandidate → EV → N6 → Risk Manager → Execution Adapter → **broker gate BLOCKED**

carrying a **single `market_event_id`** whose `trace_id`, `event_fingerprint`, `data_identity`, `node_input_fingerprint`, worker `session_id`+`worker_identity_fingerprint`, `configuration_fingerprint`, and artifact+contract versions are the **same real values preserved and verified at every node** — specifically, the tower's **real returned** `event_fingerprint`/`data_identity`/`node_input_fingerprint` **propagated into** the candidate and N6/Risk provenance, **not** re-derived `_fp(market_event_id, …)` placeholders. **No hand-constructed `DecisionResponse`/`EventIdentity`/`DecisionProvenance`.** If today's live market gives UNCERTAIN/NO_TRADE, replay a date whose regime yields a candidate — the CEO explicitly permits *"cale de producție/replay."* An auditable NO_TRADE at N3/N4 on live data is acceptable **only if the same run still traverses the same installed components under one identity**; the approved-candidate demonstration must not be a test-only construction.

---

## STANDING CONSTRAINTS (unchanged, reaffirmed)
LIVE_SHADOW **NOT started** and not to be started automatically — CEO grants that separately and explicitly. Authority **NOT activated** (`set_authority` stays uncalled). `BROKER_ORDER_SUBMISSION` stays **DISABLED**; no real orders. **Alpha stays `ALPHA_BLOCKED_CANONICAL_N1_HANDOFF`; CAND-T05 and all Alpha results frozen/diagnostic.** ve_tower remains isolated in the separate tower venv. Red Team modified no engine, ran no data on the market, changed nothing outside `red_team/`.
