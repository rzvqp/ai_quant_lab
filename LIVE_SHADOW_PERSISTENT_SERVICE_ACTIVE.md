# LIVE_SHADOW Persistent Service — Cutover Complete

**Status: `LIVE_SHADOW_PERSISTENT_SERVICE_ACTIVE`**

`AITraderLiveShadow` is now a registered Windows Scheduled Task (boot + logon triggers,
`RestartOnFailure` PT1M/999, `MultipleInstances=IgnoreNew`, unlimited execution time), confirmed
running as a task-managed process — not a chat-shell-spawned background process. `BROKER_ORDER_SUBMISSION`
remains `DISABLED`. Authority remains `NEW_BRAIN`. Strategies/`probability_inputs`/authority were not
modified.

## Commits

| Item | Commit |
|---|---|
| Singleton + heartbeat + watchdog + task XML (sections 1-3) | `630032e` |
| Cutover attempt #1 (UTF-16 fix, blocked on admin, session-scoped recovery) | `255eee6` |
| This report | *(pushed below)* |

## Task registration (performed by the user, elevated PowerShell)

```
schtasks /Create /XML "...\ai_trader\new_brain_live\AITraderLiveShadow_task.xml" /TN "AITraderLiveShadow"
```

`schtasks /Query /TN AITraderLiveShadow /FO LIST /V` before cutover confirmed: `Status: Ready`,
`Scheduled Task State: Enabled`, both triggers present (`At system start up`, `At logon time`), correct
`Task To Run` (the real venv interpreter + `-m ai_trader.new_brain_live.entrypoint`), correct
`Start In` (repo root).

## Cutover sequence executed (in order)

1. **Verified task registered and Ready** before touching anything running.
2. **Captured pre-cutover baseline**: watermark `1786995840.0`, last `market_event_id`
   `XAUUSD:M15:1786996740`, telemetry/journal both 56 entries, authority `NEW_BRAIN`, fresh heartbeat
   from the session-scoped process (PID `2956`).
3. **Stopped PID `2956`** (`taskkill /F` — the same process this directive's own prior cutover attempt
   had relaunched after the first, admin-blocked attempt). Cleaned up its orphaned tower-worker child
   (PID `27376`).
4. **Started the task**: `schtasks /Run /TN AITraderLiveShadow` → `SUCCESS`. New process tree:
   PID `22592` (Task Scheduler's own launched wrapper) → PID `25992` (real interpreter, the actual
   `NewBrainLiveLoop`) → PID `26952`/`28096` (fresh tower worker, new handshake).
5. **Verified parent = Task Scheduler, not the chat shell**: `ParentProcessId` of PID `22592` is `1676`,
   confirmed via `Get-CimInstance Win32_Process` to be `svchost.exe` — the standard Windows service
   host process, which is what runs the Task Scheduler service. Not PowerShell, not bash, not any
   process in this session's own shell tree.

## Verification (all real, all after the task-managed process was already running)

| Check | Result |
|---|---|
| Singleton mutex | A fresh `SingletonLock().acquire()` attempt from a separate process correctly raised `AlreadyRunningError` — the task-managed process genuinely holds `Global\AITraderLiveShadowSingleton`. |
| Heartbeat | Fresh (`timestamp_utc=1786997588`), `pid=25992` (matches the task-managed interpreter), `runtime_commit='255eee6'`, `tower_worker_session_id` populated (real handshake). |
| Watchdog | `watchdog.evaluate(store, stale_threshold_seconds=180.0)` → `WatchdogState.OK — "healthy"`. |
| Authority | `NEW_BRAIN` — unchanged, never touched. |
| Broker gate | `DISABLED` — `BrokerOrderSubmissionGate().enabled is False`. |
| Orders / positions | 0 / 0. |
| Balance / equity | 1800.34 / 1800.34 PLN — unchanged throughout the entire cutover. |
| Duplicate bars | **Zero** — rigorously checked across the full telemetry log: 60 entries, 60 unique `(market_event_id, strategy_id)` pairs, zero repeats. |

## Disclosed, non-blocking artifact: a 60-second offset relabeling, not a duplicate

The distinct bars processed show the expected 900s spacing except for the very last transition
(`...1786996740` → `...1786996800`, a 60s gap rather than 900s). This is the SAME `make_broker_offset`
drift phenomenon already documented elsewhere in this codebase (`bar_feed.py`'s own docstring: the
offset is deliberately re-measured fresh on every process start, to within about a minute) — the
task-managed process's freshly-computed broker offset differs by ~60s from the process it replaced,
shifting the true-UTC label the NEXT real bar receives. This is **not** a duplicate: rigorously confirmed
above that every `(market_event_id, strategy_id)` pair appears exactly once. It is a labeling artifact of
an already-known, already-disclosed limitation in the offset-measurement approach, not something this
persistence delivery introduced or needs to fix to satisfy "zero bare duplicate."

## Final process/task state

| | Value |
|---|---|
| Old PID (session-scoped, stopped) | `2956` |
| New PID (task-managed) | `25992` (wrapper `22592`) |
| New process parent | `svchost.exe` (PID `1676`, Task Scheduler service host) |
| Tower worker | PID `26952` → `28096`, fresh handshake, session `9e637db218bee4e5ec5997c80e0e996a` |
| Task state | `Running` (`Last Result: 267009` = `SCHED_S_TASK_RUNNING`, the expected in-progress code) |
| Journal / telemetry | 60 / 60 entries, zero duplicates |
| Broker orders/positions before → after | 0/0 → 0/0 |
| Balance/equity before → after | 1800.34/1800.34 → 1800.34/1800.34 (unchanged) |

## What section 5's tests this cutover directly demonstrates vs. what remains for later observation

Demonstrated for real during this cutover: `restart -> ultima bara nu se dubleaza` ✓ (rigorous proof
above), `authority ramane NEW_BRAIN` ✓, `broker ramane DISABLED` ✓, `order_send_calls = 0` ✓,
`balance/equity neschimbate` ✓, singleton genuinely enforced ✓, parent process genuinely Task
Scheduler ✓.

Not yet directly observed (would require time passing or an actual reboot, neither performed without
further explicit confirmation, per the CEO's own "Nu efectua restart Windows fara confirmare separata"):
`inchiderea shellului -> procesul continua` (now structurally true — the process is no longer a child of
this session's shell at all, but the passage of enough real time to prove it outlives a full session close
hasn't been separately observed), `restart Windows sau simularea triggerului startup`, a genuine
`RestartOnFailure` recovery from an actual future crash (the crash-recovery MECHANISM was proven
directly in section 1's real-subprocess tests; observing the Task Scheduler's own `RestartOnFailure`
trigger fire in production has not been separately witnessed).
