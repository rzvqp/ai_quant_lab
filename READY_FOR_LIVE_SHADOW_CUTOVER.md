# LIVE_SHADOW Persistence — Sections 1-3 Delivery Report

**Status: `READY_FOR_LIVE_SHADOW_CUTOVER`** (not `LIVE_SHADOW_PERSISTENT_SERVICE_ACTIVE` — the cutover
itself, section 4, has deliberately NOT been executed yet; see "What was NOT done" below).

LIVE_SHADOW (PID `6232`) is unchanged throughout this entire delivery: same process, same start time
(`2026-08-17 21:47:09`), authority still `NEW_BRAIN`, telemetry grew (48 → 56 entries during this work),
`BROKER_ORDER_SUBMISSION` never touched.

## 1. Singleton (`ai_trader/new_brain_live/singleton.py`)

A real Windows named mutex (`kernel32.CreateMutexW` via `ctypes`, no new dependency) — not a PID file.
`SingletonLock.acquire()` raises `AlreadyRunningError` immediately (never blocks) if another holder
exists; `main()` acquires it BEFORE any MT5/tower I/O, so a second launch exits cleanly
(`ALREADY_RUNNING`, exit code 0) without ever touching the terminal or spawning a second tower worker.

Because it is a real OS kernel object, not a file, "mutex eliberat după crash/exit" is structural:
Windows closes every handle a process holds — mutex included — the instant that process terminates for
ANY reason. There is no stale-mutex state to recover from.

A supplementary `ProcessIdentityRecord` + `verify_process_identity()` exists purely for
diagnostic/watchdog use — real-time, re-queried command-line verification via `Get-CimInstance
Win32_Process`, never a cached/trusted value. Never the sole enforcement mechanism (the mutex is).

**Tests** (`tests/test_singleton.py`, 7 tests, all against REAL subprocesses — not simulated):
- `test_two_simultaneous_launches_only_one_active` — a real second process holds the mutex; a third
  attempt genuinely raises `AlreadyRunningError`.
- `test_pid_stale_recovery_after_clean_exit` — a real subprocess exits cleanly; a fresh acquire
  immediately afterward succeeds.
- `test_crash_mutex_recoverable` — a real subprocess is `taskkill /F`'d (genuine crash, not a clean
  exit); a fresh acquire immediately afterward succeeds.
- `test_foreign_process_with_matching_pid_but_wrong_command_line_is_not_treated_as_ours` — the CURRENT
  test process's own real PID, checked against markers it doesn't have, correctly returns `False`.
- Plus: nonexistent-PID handling, JSON round-trip, command-line-query-for-dead-PID.

## 2. Windows Scheduled Task (`ai_trader/new_brain_live/AITraderLiveShadow_task.xml`)

Task name `AITraderLiveShadow`. XML well-formedness verified (`xml.etree.ElementTree.parse`) — **NOT
yet registered with `schtasks /Create`** (see cutover section below).

| Requirement | XML element |
|---|---|
| Real venv interpreter, no alias, no system Python | `<Command>C:\Users\MEDION GAMING\ai_quant_lab-research-main\venv\Scripts\python.exe</Command>` |
| Correct module, no accidental import from another repo | `<Arguments>-m ai_trader.new_brain_live.entrypoint</Arguments>` |
| Trigger at Windows startup | `<BootTrigger><Enabled>true</Enabled></BootTrigger>` |
| Trigger at user logon | `<LogonTrigger>` bound to the real user SID |
| StartWhenAvailable | `<StartWhenAvailable>true</StartWhenAvailable>` |
| RestartOnFailure, ≤1 min | `<RestartOnFailure><Interval>PT1M</Interval><Count>999</Count></RestartOnFailure>` |
| MultipleInstances=IgnoreNew | `<MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>` (belt-and-suspenders with the mutex — the mutex is the real enforcement, this just stops Task Scheduler from even trying) |
| Unlimited execution time | `<ExecutionTimeLimit>PT0S</ExecutionTimeLimit>` |
| Ignore battery/idle | `DisallowStartIfOnBatteries=false`, `StopIfGoingOnBatteries=false`, `RunOnlyIfIdle=false` |
| Correct working directory | `<WorkingDirectory>C:\Users\MEDION GAMING\ai_quant_lab-research-main</WorkingDirectory>` |
| stdout/stderr persistent | handled by `entrypoint.py` itself (unchanged — still prints to whatever the task's own redirected output is; no separate log-rotation mechanism was added in this delivery — flagged below as a gap) |

**Broker gate verified DISABLED before every start**: unchanged — `main()`'s own preflight sequence
(MT5 init → tower handshake → `build_loop`, all before `run_forever`) never constructs
`BrokerOrderSubmissionGate(enabled=True)` anywhere, structurally (AST-guard-proven), independent of how
the process is launched.

## 3. Heartbeat + Watchdog

**Heartbeat** (`heartbeat.py`): `LiveShadowHeartbeat` — all 13 CEO-named fields present. Written once
per `tick()` (every ~30s), OVERWRITTEN (not appended — `SqliteStateStore.set_text`/`get_text`, new
additive methods on the shared store, 5 new tests, `kv_text_state` table separate from the existing
`REAL`-only `kv_state`). A heartbeat write failure is caught and swallowed — it can never crash the live
loop.

**Watchdog** (`watchdog.py`, a SEPARATE process/module — never imports anything order-capable, confirmed
by this package's own existing AST guard): `evaluate()` checks, in fail-closed order: heartbeat presence
→ freshness → real PID identity re-verification → MT5 connectivity → tower session → authority ==
`NEW_BRAIN` → broker gate == `DISABLED`. `check_and_notify_on_transition()` alerts ONLY when the
evaluated state differs from the last-persisted alert state — **proven directly**
(`test_no_notification_on_repeated_ok_state`: 5 checks of a healthy system produce exactly 1
notification, not 5). The 8 named triggers all map to real transitions: `STARTUP` (first-ever OK),
`RESTART` (recovered from a bad state), `CRASH` (transition into not-running), `HEARTBEAT_STALE`,
`MT5_UNAVAILABLE`, `TOWER_UNAVAILABLE`, `AUTHORITY_MISMATCH`, `BROKER_GATE_MISMATCH`.

`restart_preconditions_met()` implements the 5 named preconditions as one pure, independently-tested
function — fails closed on unknown (`None`) order/position counts, never treats "couldn't verify" as
"assume zero." **Deliberately not wired to auto-execute `schtasks /Run`** — there is no Scheduled Task
to restart yet; wiring an unused restart trigger before the task exists would be dead code, not a real
capability.

## Tests + validation

```
pytest ai_trader/new_brain_live/ -q          -> 53 passed
mypy --strict ai_trader/new_brain_live/      -> Success, 16 source files
pytest ai_trader/persistent_state/ -q        -> 20 passed (5 new set_text/get_text tests)
pytest ai_trader/new_brain_bridge/tests/test_tower_client.py -q -> 17 passed (new .session property)
```

No decision logic was modified — everything here is additive (new files, new optional constructor
parameters defaulting to `None`/unused, two new small public accessors). The pre-existing 23
`new_brain_live` tests and the RT-N1-REPLAY-0001 delivery's own tests are unaffected and still pass.

## What was NOT done (deliberately — pausing for explicit confirmation before proceeding)

Section 4 (controlled cutover) and section 5's Windows-restart-trigger test were **not executed**:

- The Scheduled Task was **not registered** (`schtasks /Create` never run).
- PID `6232` was **not stopped**.
- No cutover (watermark capture → stop old process → start Task → verify parent/authority/gate/no-
  duplicate/journal-continuation/MT5+tower handshake) was performed.
- No Windows restart or logon-trigger simulation was performed (the CEO's own instruction: "Nu efectua
  restart Windows fără confirmare separată").
- stdout/stderr log rotation for the Task's own output was not built in this delivery — flagged as an
  open item for the cutover step, not silently skipped.

This is deliberate, not an oversight: registering a task that autostarts on every boot/logon indefinitely
and then stopping the currently-running live process are both meaningfully more consequential, harder-to-
casually-reverse actions than anything built so far in this delivery. Confirming with the user in plain
terms before taking them, separate from the roleplay directive itself, before proceeding to section 4.
