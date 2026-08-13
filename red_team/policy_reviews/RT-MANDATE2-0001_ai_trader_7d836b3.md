# RED TEAM — MANDATE 2 RUNTIME REVIEW · AI Trader `7d836b3` (code HEAD `8866876`)
### RT-MANDATE2-0001 · real decision-path audit, not just the written tests
**Date:** 2026-08-14 · **Auditor:** Red Team · **Target:** AI Trader Mandate-2 integration; report commit `7d836b3`, real code at `8866876` (branch `ai-trader-implementation`). Accepted status: `READY_FOR_LIVE_SHADOW_REVIEW_CANDIDATE` (LIVE_SHADOW not approved; MANDATE_2_PASS not accepted). **No engine modified; no real data; traced the actual runtime code, not fixtures.**

# VERDICT — **MANDATE_2_REVIEW_CONDITIONAL · INTEGRATION_BLOCKED**
PASS_FOR_LIVE_SHADOW is **not** granted. **Point 2 is the decisive blocker (as the CEO anticipated):** the N1→N6 integration is **incomplete** — `market_map_available`, `levels_available`, and `confirmation_available` (N3/N4 **tower** outputs) are **permanently hardcoded `False`** in the bridge because the level-tower (N3) and N4-confirmation are **not wired** into `ai_trader`. Per the CEO's pre-registered rule ("if market_map/levels/confirmation must be produced by the tower but are permanently False, the N1-N6 integration is INCOMPLETE and the verdict is INTEGRATION_BLOCKED"), this blocks LIVE_SHADOW. AI Trader **did not invent** the missing data (it fail-closes to NO_TRADE, correctly) — so this is a clean, remediable integration gap, not a corruption; hence CONDITIONAL, not FAIL. Two further items are also unclosed (§5 full suite has no verdict; §4 the 5 skipped tests). The safety machinery (broker gate, authority switch, legacy demotion) is built correctly and inactive.

---

## THE DECISIVE MATRIX (point 2) — the four missing inputs
Verified at source (`new_brain_bridge/bridge.py:161`, the ONLY place these are set — grep-confirmed no path sets them `True`):

| missing input | canonical producer | node | in the artifact? | wired in AI Trader? | action |
|---|---|---|---|---|---|
| `market_map_available` | zone map | **N3** | tower (wp5b) | **NO — hardcoded `False`** | **INTEGRATION_BLOCKED** — wire N3 |
| `levels_available` | level tower | **N3** | tower (wp5b) | **NO — hardcoded `False`** | **INTEGRATION_BLOCKED** — wire N3 |
| `confirmation_available` | M5 zone confirmation | **N4** | tower (wp5b) | **NO — hardcoded `False`** | **INTEGRATION_BLOCKED** — wire N4 |
| `probability_inputs` | ratified per-regime outcome-count table (Alpha/Statistician) | EV input to N6 | interface `load_probability_inputs` exists; returns `None` | strategy-dependent, not yet ratified | **OK (conditional)** — deterministic NO_TRADE until a ratified table plugs in |

**Consequence (confirmed from `decide_n6`'s own order):** every real event that survives eligibility+catalog reaches step 4 and returns **NO_TRADE / MISSING_LEVEL_INPUT** (gap 2 fires before the EV/probability stage ever would). The new brain **cannot produce any shadow decision today** other than NO_TRADE-MISSING_LEVEL_INPUT. Starting LIVE_SHADOW now would shadow the *plumbing*, not the brain's *decisions*.

**Why this is INTEGRATION_BLOCKED and not an acceptable gap:** `market_map`/`levels`/`confirmation` are **tower** outputs owed for **every** event, independent of strategy ratification — they must come from N3/N4. They are permanently `False`. That is exactly the CEO's blocking condition. (Contrast `probability_inputs`, which is legitimately strategy-dependent — §Point 3.)

## POINT 3 — `probability_inputs`: acceptable, all four conditions met
`new_brain_bridge/probability_source.py::load_probability_inputs` → always `None`, honestly disclosed. Verified:
1. **Interface exists** — `load_probability_inputs(strategy_id, strategy_version) -> ProbabilityInputs | None`, keyed at the granularity a real table would use. ✅
2. **Absence → deterministic NO_TRADE** — `None` → `decide_n6` step 5 → `MISSING_PROBABILITY_INPUTS` (or an earlier NO_TRADE; today gap 2 fires first). ✅
3. **A future ratified table plugs in without re-architecting** — it is "an explicit, separate, reviewable change to this one function"; the bridge/DecisionRequest/decide_n6 path and call-shape do not change. ✅ (single plug point)
4. **Source is the ratified evaluator/statistics, not locally invented** — the docstring forbids AI Trader estimating outcome stats itself (Alpha/Statistician territory); it fail-closes to `None` rather than fabricating. ✅
**So `probability_inputs` being absent is acceptable per the CEO's rule** — it is NOT the blocker. The blocker is the tower inputs (gap 2).

## POINT 1 — the real path (built, exercised in tests with real code, NOT running live)
`bridge.evaluate_bar`: real bar → `RawAxesBuilder.observe` (N1, OHLC+ATR14 only, no invented detectors) → `ve_brain.StrategyRouter.eligible` → per-strategy `DecisionRequest` → `ve_brain.decide_n6` → `risk_gate.submit_new_brain_candidate` (provenance+circuit-breaker gated) → `risk_manager_live.evaluate_trade_proposal` (the SAME frozen function legacy uses) → `execution_shadow.attempt_shadow_execution` → `BrokerOrderSubmissionGate.authorize()` → **BLOCKED**. The chain is real code (not fixtures), but it runs in **tests only** — no live process has been restarted; on the live processes today, **legacy still decides** (§Point 6). So "a real-feed event traverses the chain" is demonstrated in tests, not in a running process.

## POINT 6 — authority switch: mechanism sound, doubly inactive, safe
`authority.py`: `DecisionAuthority{LEGACY,NEW_BRAIN}` persisted in `SqliteStateStore`, re-read fresh every call, **default LEGACY**. `set_authority()` is the only flip — **exported, never called** anywhere. Additionally, `submit_candidate`'s `authority_check` param defaults to `None` and **no entrypoint passes a non-None value** — so even if the persisted value flipped, legacy would still not check it. **Double-inactive.** Mechanism (verified via the orchestrator tests): when `authority_check` returns `NEW_BRAIN`, `submit_candidate` records `LEGACY_SHADOW_TELEMETRY` and returns `None` **without calling `send_after_dry_run_gate`** → legacy cannot reach Risk Manager/Execution; `market_intelligence` is demoted transitively (only reachable past that gate). Atomicity across the two OS processes = a **coordinated restart** after the persisted flip (matches the codebase's existing cross-process pattern). **Not activated** (CEO: build, don't switch). Caveat to verify at activation: the "no fallback to legacy / brain-down → NO_TRADE/BRAIN_UNAVAILABLE" path lives in `fail_safe.py` and must be exercised on the real switched path before LIVE_SHADOW — not exercisable while inactive.

## POINT 7 — broker barrier: blocked, genuinely called, zero orders
`execution_shadow.attempt_shadow_execution`: a **Risk-Manager-APPROVED** candidate reaches `gate.authorize()` and is refused (`BrokerOrderSubmissionDisabledError` → `reached_broker_gate=True, blocked=True`). The gate is genuinely called (the fault-injection test constructs `enabled=True` to prove `authorize()` is really invoked, not hardcoded); the production default is `enabled=False`, and `kw_only` makes `BrokerOrderSubmissionGate(True)` a `TypeError`. No `order_send`/`order_check`/etc. anywhere in `new_brain_bridge` (static scan). ✅ **Broker stays blocked; zero orders, zero positions structurally.**

## POINT 4 — the 5 skipped tests (owner + effect on the real path)
| test | reason | missing component | owner | effect on real path | closure |
|---|---|---|---|---|---|
| 4 | day-boundary/session labels feeding N1 | session-label input to `RawAxesBuilder` | **N1/tower spec (VE/wp5b)** | none (N1 uses OHLC only) | define whether N1's axes need session labels |
| 5 | gap-visibility in N1 market-context input | no such input object | **N1/tower spec (VE)** | none | define the gap input if N1 requires it |
| 9 | decision-snapshot staleness bound ≠ level-availability | no such concept | **ve_brain contract (VE)** | none | VE defines a staleness bound or confirms none |
| 10 | cross-strategy "conflicting recognition" merge | doesn't match per-strategy-independent N6 | **design mismatch (test is for a non-existent design)** | none — likely **irrelevant to shadow** | drop or re-spec the test |
| 20b | multi-node inter-failure contract | finer "node" definition | **VE (artifact)** | none today | VE defines node-failure granularity |
**None of the 5 gates a trade** (the real path is already blocked at gap 2). But per the CEO, they are **not AI Trader's to invent**; owners are VE / the tower spec. They are "not closed," and only #10 is plausibly "irrelevant to shadow." So §4 is **not satisfied** ("closed or proven irrelevant") — most need an owner ruling.

## POINT 5 — the full 3,237 suite: NO VERDICT
The report states the full `ai_trader/` suite is "run separately, in progress," with "one pre-existing `F` around 33% ... not yet root-caused," reported as **open**. Per the CEO ("'runs for a long time' is not a verdict"), this is **unsatisfied**: the complete suite has **no final result**, and there is an **un-diagnosed failure**. The scoped suite (`mandate2_readiness`+`new_brain_bridge`+`pdh_pdl_demo`+`multi_policy_live`) = 244 passed / 6 skipped, mypy-strict clean on 77 files — real, but not the full tree. **Required before PASS:** finalize the 3,237 with a verdict, or diagnose the blockage exactly (test, process, stack, reproducible cause) — and root-cause the ~33% `F`.

## WHAT IS SOUND (so the CONDITIONAL is precise)
Real (non-fixture) N1→N6 wiring; N1 from OHLC only (no invented detectors); `probability_inputs` fail-closed and correctly deferred (§3); the authority switch mechanism (safe, default-LEGACY, doubly-inactive, LEGACY_SHADOW_TELEMETRY demotion); the broker barrier (approved candidate blocked, gate genuinely called, zero orders); no live process restarted; every gap **disclosed, not papered over**. AI Trader invented nothing — it fail-closes, which is correct.

## VERDICT — **MANDATE_2_REVIEW_CONDITIONAL · INTEGRATION_BLOCKED**
PASS_FOR_LIVE_SHADOW requires all of: runtime path demonstrated · the 5 tests closed or proven shadow-irrelevant · full suite with a verdict · N2-N4 absence clarified · authority switch safe+atomic · legacy cannot decide · broker blocked. **Blocked by:** (a) **INTEGRATION_BLOCKED** — N3/N4 tower not wired, `market_map`/`levels`/`confirmation` permanently `False` (decisive); (b) the 3,237 suite has no verdict + an un-diagnosed failure; (c) the 5 skipped tests are un-owned/not-closed. The switch, broker, and legacy-demotion machinery are sound but **not activated**. **LIVE_SHADOW must not start.** Alpha remains PAUSED; CAND-T05 frozen.

## HANDOFF → CEO / AI Trader / (wp5b tower owner)
1. **Blocking (INTEGRATION_BLOCKED):** wire the **real N3 (zone map + levels)** and **N4 (confirmation)** tower outputs into `bridge.evaluate_bar` so `market_map_available`/`levels_available`/`confirmation_available` come from the tower, not hardcoded `False`. This is a wp5b-tower deliverable into `ai_trader` — AI Trader must not stub it. Until then the brain shadows only NO_TRADE/MISSING_LEVEL_INPUT.
2. **Blocking:** finalize the 3,237 suite with a verdict (or exact reproducible diagnosis) and root-cause the ~33% `F`.
3. **Owner rulings** on the 5 skipped tests (mostly VE / tower spec); confirm #10 is shadow-irrelevant or re-spec it.
4. **At activation** (later): exercise `fail_safe` on the switched path (brain-down → NO_TRADE/BRAIN_UNAVAILABLE, no legacy fallback), and re-run the broker-blocked proof on the live switched path.
5. `probability_inputs` may stay `None` until a ratified table exists — its four conditions are met; it is **not** a blocker.

Red Team modified no engine, ran no data on the market, changed nothing outside `red_team/`.
