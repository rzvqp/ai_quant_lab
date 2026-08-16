# AI Trader — Mandate 2, Phase 2 — READY_FOR_LIVE_SHADOW_REVIEW_CANDIDATE_V2

**Date**: 2026-08-16 · branch `ai-trader-implementation`, remote `trader`
(`https://github.com/rzvqp/ai_quant_lab-research-main.git`) · **Status**: `ve_tower` 0.3.0 genuinely
installed and wired end-to-end; `LIVE_SHADOW` **not started**, `set_authority()` **never called**,
`BROKER_ORDER_SUBMISSION` **remains DISABLED**. Stops here for Red Team verification, per the CEO's own
instruction ("oprește-te acolo pentru verificarea Red Team").

---

## 1. Artifact pins (unchanged since `TOWER_METADATA_PASS`, re-verified this segment)

`ve_tower` 0.3.0: `package_build_commit=6daf2aa`, `state_delivery_commit=0207ffa`, `wheel_sha256=
0c2581c068f3bd7d0c5beff1358af0aa906485d69ed74bf66c8a6d8d0c0120d2` (77,088 bytes), `vendored_source_identity
=sha256:4c0deecbec7afc74b1fc7f61898ad10e54b63d3b7c5cad63b80ee8c647a69e1c`, `n3_contract_version=
tower-n3-request-v2`, `n4_contract_version=tower-n4-request-v2`. `ve-tower-worker` 0.2.0: `worker_delivery_
commit=7747c4b4fbdf71e0e435d5957ad2fa38d0e2f80f`, `protocol_version=2.0`. All nine fields verified via
`tower_identity_pin.verify_pin()` against the REAL installed distribution — zero mismatches (task 272).

**Install location, re-confirmed**: `ve_tower` installed EXCLUSIVELY in `C:\Users\MEDION GAMING\
ve_tower_venv` (Python 3.12.10). Main AI Trader venv's `pip freeze` re-diffed against the pre-Phase-2
snapshot — the only delta is `ve_brain` (already installed in an earlier, separate mandate); `ve_tower` is
confirmed absent (`pip show ve_tower` → "not found") in the main venv, unchanged throughout this entire
segment.

## 2. Full real-data path — demonstrated (task 276)

Script: `demonstrate_candidate_v2_full_path.py` (repo root — deliberately outside `mandate2_readiness/`,
whose own static import-independence guard forbids that package's production files from importing
execution-capable modules at all; this script's read-only `RealMT5Gateway` use is real evidence tooling,
not part of that boundary). Raw output: `CANDIDATE_V2_FULL_PATH_EVIDENCE.json`. Run against the live demo
terminal (`DEMO_020`, FusionMarkets-Demo) and the real, freshly-spawned tower worker — no stubs anywhere.

**Part 1 — the real live path, honest result.** Real M15 history (250 closed bars) → `RawAxesBuilder` (N1)
→ `ve_brain.StrategyRouter`: today's real regime for `trend_pullback` resolved `UNCERTAIN_REGIME` at the
Router — a true, disclosed fact about current market structure (no confirmed trend), not a defect; the
tower is never queried for a strategy the Router already excluded (lazy-query design, task 275).

**Part 1b — direct tower probe, isolated from Router eligibility.** The SAME real M15/M5 windows sent
straight to the real worker over real IPC: `ve_tower.run_n3` returned `market_map_available=true,
levels_available=true` (**37 real zones**), `ve_tower.run_n4` returned `confirmation_available=true`,
`reason_codes=["ok_market_map","ok_confirmation"]`, `tower_version="0.3.0"`. This is the literal proof of
"IPC → worker izolat → N3/N4 reale" against TODAY's live data, independent of whether any one strategy
happened to route there.

**Part 2 — a fully-approved candidate reaches the broker gate and is blocked.** Since live conditions
cannot be forced to produce a `SHADOW_TRADE_CANDIDATE` on demand (the one remaining, disclosed gap:
`probability_inputs` is still always `None`), this reuses the SAME established, CEO-sanctioned pattern
already ratified for exactly this property (`test_e2e_readiness.py`'s tests 8/16/17): a real
`ve_brain.DecisionResponse` shaped as `SHADOW_TRADE_CANDIDATE` with a real `DecisionProvenance`, run
through the REAL, unmodified `submit_new_brain_candidate` → `risk_manager_live.evaluate_trade_proposal`.

| Checkpoint | Result |
|---|---|
| Risk Manager approval | `approved=true`, zero denial reason codes |
| Reached `BrokerOrderSubmissionGate.authorize()` | `reached_broker_gate=true` |
| Gate result | `blocked=true` — `"order submission is DISABLED — Mandate 2 integration not yet ratified by Red Team — default-closed"` |
| `gate.enabled` | `false` (the only reachable default; never constructed `True` anywhere in this script) |
| `order_send` calls | **zero** — not imported, not called, anywhere in this file |
| Broker positions, before → after | `0 → 0` |
| Broker orders, before → after | `0 → 0` |
| Account balance/equity, before → after | `1800.34 → 1800.34` (unchanged) |

## 3. Tests 04, 05, 09, 20b — closed for real (task 277)

All four previously `BLOCKED_ON_TOWER_HANDOFF` tests are now real, passing, against the genuinely
installed artifact (skip cleanly if the isolated tower venv is absent, matching this repo's own
established convention):

- **Test 04** — spawns the real worker, sends a KNOWN true-UTC last-bar timestamp, confirms N3's own
  `data_identity.last_closed_bar_time` in the real response equals that value UNCHANGED across the whole
  round trip (fetch → wire serialize → IPC → `ve_tower.build_data_identity` → wire deserialize), and that
  `day_boundary_start_utc` (the same true-UTC anchor `pdh_pdl_demo`'s own live day-index already uses)
  applied to it matches the independently expected boundary.
- **Test 05** — `tower_bar_source.detect_gaps` (new, reuses `bar_feed.py`'s own `classify_gap`) correctly
  classifies a real, hand-built discontinuity in the M15/M5 window about to be sent to the tower, and
  produces no false positive on a clean window; `bridge.py`'s own `_query_tower` surfaces any detected gap
  on the Tower `NodeTrace`'s `reason_codes` unconditionally (a single, auditable call site).
- **Test 09** — spawns the real worker, sends bars that are genuinely stale relative to `as_of` with a
  tight `max_staleness_s` (new wire field, threaded through to `ve_tower.N3Request`/`N4Request`'s own real
  `DATA_STALE` gate): the real artifact refuses with `market_map_available=false` and a real
  stale-shaped reason code — a stale snapshot never reaches N6 mislabeled as available.
- **Test 20b** — `ve_tower.run_n3`/`run_n4` are themselves designed to never raise, so "N3 raises" cannot
  be triggered without corrupting the real artifact (forbidden). The real, reachable failure modes are
  proven two ways: (1) `tower_worker/tests/test_server_roundtrip.py`'s new
  `test_decision_fn_raising_an_unexpected_exception_degrades_and_the_server_keeps_serving` — dependency
  injection proves ANY unexpected exception from the worker's own request-handling code degrades to
  `NODE_FAILURE_DEGRADED_TO_UNAVAILABLE` (a new, added fail-closed wrapper in `server.py`) rather than
  crashing the whole persistent process; (2) `test_e2e_readiness.py`'s own test 20b spawns the REAL
  production worker (`real_decision`, no fault injected), sends a normal request, a genuinely malformed
  one (rejected, not crashed), then a second normal request — proving the SAME real worker process
  answers correctly afterward.

**`ai_trader/mandate2_readiness/tests/test_e2e_readiness.py` — 26 passed, 0 skipped** (25 canonical
numbers; test 20b is the amendment's own named sub-test of 20, not a 26th canonical number).
**25/25 canonical end-to-end tests are real.**

## 4. Regression

**Scoped (full blast radius of this Phase 2 segment — `mandate2_readiness` + `new_brain_bridge` +
`pdh_pdl_demo` + `multi_policy_live`)**: `350 passed, 0 failed, 0 skipped, 23 warnings, 28.24s`. All 23
warnings are pre-existing `ResourceWarning`s from unrelated test fixtures (unclosed sqlite/file handles in
`test_tower_isolation.py`/`pdh_pdl_demo` fixtures, present before this segment) — none newly introduced.

**Isolated tower venv (`tower_worker/`)**: `41 passed`, `mypy --strict` clean across 15 source files.

**Main venv, scoped to everything touched (`new_brain_bridge` + `mandate2_readiness`)**: `mypy --strict`
clean across 35 + 17 files respectively.

**Whole-repo `mypy --strict`**: 227 pre-existing errors, ALL in `ai_trader/strategy_runtime/` and
`ai_trader/simulation/` test files — zero relation to anything touched this segment (confirmed by path);
matches this repo's own established "validation-scope rule" (mypy strict is scoped per package, not
whole-repo, precisely because of pre-existing issues outside any given mandate's touched scope).

**Whole-repo `pytest ai_trader/`**: STARTED in background at session time, confirmed still running — the
prior mandate segment's own full-suite baseline (`AI_TRADER_MANDATE2_READY_FOR_LIVE_SHADOW_REVIEW.md`,
section 9) measured `3268 passed, 0 failed, 6 skipped, 4 warnings in 15006.15s (4h10m)` for this same
suite; this run has not yet reached that wall-clock mark. **Not reported as complete because it is not
complete** — no number is fabricated here. Will be reported in a follow-up once it finishes; the scoped
regression above already covers 100% of this segment's actual code changes.

## 5. Constraints held throughout (verified, not merely asserted)

- `LIVE_SHADOW`: never started.
- `set_authority()`: never called — confirmed by the SAME static grep this repo's own tests already run
  (`test_no_live_process_package_imports_the_tower_client_or_protocol`, still passing).
- `BROKER_ORDER_SUBMISSION`: DISABLED — `BrokerOrderSubmissionGate()`'s only reachable default; every
  construction site in this segment's own new code (`demonstrate_candidate_v2_full_path.py`) uses the
  bare default, never `enabled=True`.
- `ve_brain`/`ve_tower` internals: never modified — every change this segment touched is in `ai_trader`'s
  own repo (`bridge.py`, `tower_bar_source.py`, `tower_protocol.py`, `test_e2e_readiness.py`) or in
  `tower_worker`, this repo's OWN isolated-worker package (`decision.py`, `protocol.py`, `server.py`) —
  never the vendored `ve_tower`/`ve_brain` packages themselves.
- Legacy/`market_intelligence` fallback: none added — `new_brain_bridge`'s own
  `test_21_zero_broker_calls_for_any_shadow_trade_candidate_however_confident_static_analysis` and the
  import-independence tests still pass unchanged.
- Worker process/venv isolation: unchanged — `ve_tower_worker` still only ever installed in
  `ve_tower_venv`; every real-subprocess test spawns it via `TowerWorkerLauncher`, never in-process.
- MT5 terminal: read-only throughout — `RealMT5Gateway`'s own Protocol declares no order-submitting
  method at all (structural, not behavioral); `order_send` is never imported anywhere in this segment's
  new code.

## 6. Rollback procedure (unchanged mechanism, re-confirmed)

1. Stop any running tower worker process (`TowerWorkerLauncher.stop()` / kill the PID).
2. `pip uninstall ve_tower ve-tower-worker` inside `ve_tower_venv` ONLY — never touches the main venv,
   which has never had either package installed.
3. Revert `bridge.py`'s `evaluate_bar` callers to omit `tower=` (already the default everywhere in
   production — no live entrypoint constructs a `TowerDependencies` yet, so no code change is needed to
   roll back the RUNTIME effect; only the `tower_worker/`/`new_brain_bridge` source changes themselves
   would need `git revert` if the code itself must be removed).
4. `git revert` this commit and `d2f9fbb` (Phase 2 steps 1-5) in sequence if a full source rollback is
   required — both are self-contained, additive commits touching no shared state outside `new_brain_bridge
   `/`tower_worker`/`mandate2_readiness/tests`.
5. No persisted state to clean up: `TowerClient`'s cache is in-memory only; no database schema changed.

## 7. Commits

| Commit | Content |
|---|---|
| `d2f9fbb` | Phase 2 steps 1-5: install `ve_tower` 0.3.0, wire real N3/N4 into the tower worker and `bridge.py` |
| *(this commit)* | Phase 2 steps 6-10: `max_staleness_s` wire field, gap detection, server fail-closed hardening, full real-data path demonstration, tests 04/05/09/20b closed, CANDIDATE_V2 report |

Pushed to `trader` (`https://github.com/rzvqp/ai_quant_lab-research-main.git`), branch
`ai-trader-implementation`; local/remote HEAD hash verified identical after push (see Telegram
notification for the exact hash).

---

**Stops here.** Awaiting Red Team verification per the CEO's own instruction. Not requesting an
intermediate checkpoint; the whole-repo regression will be reported in a follow-up once it completes.
