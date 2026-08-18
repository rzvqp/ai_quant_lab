# RED TEAM — N1 INCREMENTAL HYDRATION INTEGRATION REVIEW
### RT-N1-0003 · **N1_INCREMENTAL_HYDRATION_INTEGRATION_PASS**
**Date:** 2026-08-18 · **Auditor:** Red Team · **Target:** `ai_quant_lab-research-main` @ `9f0c13c` (branch `ai-trader-implementation`) — AI Trader's isolated integration of `ve_n1_replay 0.1.1` (SHA `2cff7e7b…`, delivery `e118c33`, RT-N1-0002 `N1_INCREMENTAL_PASS` @ `6230ee5`), on top of Commit A `7905236` (request-scoped time) + Commit B `6b45ee1` (M5 dual-clock). **LIVE_SHADOW audit was read-only; no deployment, restart, or cutover; no VE engine or AI Trader code modified.** Nothing changed outside `red_team/`.

# VERDICT — **N1_INCREMENTAL_HYDRATION_INTEGRATION_PASS**
The integration runs the incremental artefact as a genuinely isolated subprocess (never imported into the main venv), verifies its pin two ways, is fail-closed on every snapshot/worker failure, preserves unbounded structural memory across restart, and never touches the broker/decision path. All 8 integration tests pass against the **real** artefact, mypy is clean, and the change is purely additive. **This PASS authorizes ONLY the full AI Trader regression and the cutover report/plan — not deployment, restart, Scheduled-Task changes, `set_authority`, broker activation, or `order_send`.**

---

## §1 — Delivery integrity · PASS
`9f0c13c` exists, is HEAD of `ai-trader-implementation`, and **local == remote** (`9f0c13c5e295…`). It descends from A+B+C. **The change is purely additive** — 9 new files under `ai_trader/new_brain_live/n1_incremental/` (+1105, `git diff --name-status` shows only `A` entries; no existing file modified), so it cannot regress existing runtime or tests. No uncommitted runtime code (the 4 dirty entries are untracked logs/scratch dirs). The live runtime does not consume the new files (§10).

## §2 — Artefact isolation · PASS
**Isolation, not installation.** `import ve_n1_replay` in the main AI Trader venv → `ModuleNotFoundError` (it is not installed there), so its vendored `ai_trader.n1_replay` **cannot collide** with the repo's real `ai_trader.n1_replay` (which the main process does import). It runs only in `C:/Users/MEDION GAMING/.alpha_n1_venv` (`ve_n1_replay 0.1.1` + `ve_brain 0.1.3` + numpy), launched by `client.py` via **`subprocess.run` per call, JSON over stdin/stdout** — never an in-process import; the client reconstructs `ve_brain.RawAxes`/`EligibilityDecision` with the **main** venv's ve_brain. **Pin verified two ways** (`artifact_pin.verify_pin()` → `ok=True`): pip's `direct_url.json` recorded `sha256=2cff7e7b…` AND an independent re-hash of the physical wheel both equal the pinned SHA; `PINNED_DELIVERY_COMMIT=e118c33`, `PINNED_RT_PASS_COMMIT=6230ee5`, `PINNED_VERSION=0.1.1`. The isolated venv's ve_brain (0.1.3) and detector identities match the pin.

## §3 — Snapshot fail-closed (DECISIVE) · PASS
Verified by driving the **real** worker via `N1IncrementalClient`:
- **Valid, same-identity restore** → `restore_rejected_reason=None`, and restore-then-continue is **byte-identical** to the never-restarted run.
- **Identity mismatch** (a client with a different `implementation_commit` restoring another's snapshot) → **`IncompatibleSnapshotError: snapshot identity '…' != engine '…'`** (explicit refusal).
- **Corrupt blob** → **`UnpicklableSnapshot: Invalid base64…`** (explicit refusal).
- **After a refused restore the worker does NOT continue as valid:** the worker returns a well-formed-but-incomplete-history result with `restore_rejected_reason` set, and **both consumers reject it** — `hydrate_n1_incremental` sets `prior=None` and rebuilds cold from `_DEFAULT_COLD_START_BAR_COUNT=6000` bars ("Fail-closed rebuild, not a silent accept"); `IncrementalContextRefreshLoop.tick` **leaves the context store untouched** ("never fabricates a context on a rejected response" → stale/missing context → NO_TRADE). The rejected-restore result is empirically ≠ the true final, so it can never be mistaken for a valid context.

## §4 — Unbounded structural memory · PASS
Through the real subprocess, on a history with a break followed by **5,300 calm bars** (break age 5,300 > 5,000): the continuous run's final reading is **`structure=strong`, `direction=up`, `applicable_regimes={TREND_UP, COMPRESSION}` — not `UNCERTAIN`**; and snapshot(after break+300)→restore→continue produces the **identical** final structure/direction/regimes/fingerprints as the continuous run. The >5,000-bar-old trend is retained across restart, exactly closing the 0.1.0/C blocker.

## §5 — Cold start & zero lookahead · PASS
Hydration/refresh fetch bars only via `LiveBarFeed` (**closed bars only, `ts_close ≤ now`**); the worker calls `observe_closed_bar(bar, as_of=bar.ts_close)` — judging each bar by its own close, correct for closed bars — and enforces **staleness** via `assert_not_stale(now=wall_clock_now)` → `StaleStateError`→rejected. Future exclusion is therefore feed-enforced upstream, and the **M5-level `CONTEXT_FROM_FUTURE`** guard rejects a context whose `market_timestamp > M5.ts_close` (integration test: all journal entries `CONTEXT_FROM_FUTURE`, **`worker.connection_count == 0`** — a from-the-future context never reaches the tower); a too-old context → `CONTEXT_STALE`. (My raw-worker future-bar probe was returned as processed because the worker judges by `ts_close`, not wall clock — that layer is the feed's job, not the worker's; not a defect.)

## §6 — Request-scoped time · PASS
`N1IncrementalClient.observe` sends `wall_clock_now` **fresh on every call** (from the caller's own `wall_clock` callable), never a value cached at client construction — the same request-scoped discipline as `TowerDependencies.wall_clock_provider`. The worker never persists an engine across calls (fresh subprocess per invocation). `test_request_scoped_time_not_frozen` passes.

## §7 — Dual clock M15/M5 · PASS
The incremental context-refresh loop uses its **own** M15 watermark, separate from the M5 decision loop's watermark; three M5 between two M15 closes are processed once each; a second tick with no new bar produces zero new evaluations. `test_dedup_and_watermark_continuity_across_ticks` passes, and the live journal shows **zero duplicate `(market_event_id, strategy_id)` pairs**.

## §8 — Failure matrix · PASS
`N1IncrementalClient` converts every failure into `N1IncrementalWorkerError`, which the consumers catch as fail-closed: subprocess dead (`returncode != 0`), timeout (`TimeoutExpired`), invalid/incomplete JSON (`JSONDecodeError`), and worker-internal error all → `N1IncrementalWorkerError` → context untouched → NO_TRADE. Corrupt snapshot → `UnpicklableSnapshot`; identity/artefact/contract/router/detector mismatch → `IncompatibleSnapshotError`; missing history → `NO_CLOSED_BARS_AVAILABLE`; NaN/Inf → `NonFiniteAxesInputError`; stale → `StaleStateError`. Worker restart is inherent (a fresh subprocess with no persistent state per call). **No legacy fallback, no fabricated context/values anywhere** — all paths resolve to NO_TRADE/UNAVAILABLE.

## §9 — Tests, mypy, baseline · PASS
**8 integration tests pass against the real artefact** (via subprocess, ~22 s) — covering the mandatory scenarios: >5,300-bar survival, cold-start = continuous (chunked), CONTEXT_FROM_FUTURE, request-scoped time, dedup/watermark continuity, identity-mismatch-leaves-store-untouched, no-broker/decision-references, and artefact-pin. mypy `--strict` clean on the whole `n1_incremental` package; no broker/`order_send`/`set_authority`/execution/risk imports. Since the commit is **purely additive** (no existing file modified), it cannot introduce a regression in any existing test; the single pre-existing suite item (unrelated) fails identically with or without `9f0c13c`. **The full 6-hour regression was not run** (authorized only after this PASS).

## §10 — LIVE_SHADOW · PASS (read-only)
The live process was not stopped/restarted and the Scheduled Task was not modified. `AITraderLiveShadow` is Running; the live process (PID 22592/25992) **started 2026-08-17 23:12:37, when HEAD was `255eee6`** (before A and long before `9f0c13c`) — so the active runtime is the **old** version, not `9f0c13c`. `decision_authority=1.0` → **NEW_BRAIN**; broker gate DISABLED; **152 shadow records all `LIVE_SHADOW_NO_TRADE`, `order_send=0`, none reached the broker**; zero orders/positions. After the market reopened: a **fresh heartbeat** (pid 25992, recent UTC ts), **new M15 bars** (19→38 distinct), the watermark advanced, **journal continuity with zero duplicate `(event, strategy)` pairs**.

---

## AUTHORIZATION (on PASS)
Authorized **only**: (1) the full AI Trader regression; (2) preparation of the Red Team report and the cutover plan. **NOT authorized:** deployment, LIVE_SHADOW restart, Scheduled-Task modification, `set_authority`, broker activation, `order_send`. **LIVE_SHADOW continues on the old runtime untouched; broker DISABLED; authority NEW_BRAIN; CAND-T05 frozen.** Red Team modified no VE engine or AI Trader code, ran no real orders, disturbed no live process, and changed nothing outside `red_team/`.
