# Alpha Automation — PowerShell Orchestration Loop

Relaunches Claude Code non-interactively, cycle after cycle, so Alpha's research can continue
across many invocations without a human typing "continue" after every response. The orchestrator
itself has no research logic — it only manages the loop, the process invocation, and the
checkpoint-integrity guarantees. All research behavior lives in
[`prompts/ALPHA_AUTOMATION_CONTINUE.md`](../prompts/ALPHA_AUTOMATION_CONTINUE.md) and in whatever
Alpha (Claude) does inside each invocation.

This is a different mechanism from the existing `alpha_automation/` Python package (which drives a
`codex exec`-backed batch loop, see [`alpha_automation/README.md`](../alpha_automation/README.md)).
That system is untouched by this one. This system is specifically: "keep relaunching **Claude
Code** for Alpha until a stop condition is met."

## What it does

Each cycle:

1. Loads and validates `config/alpha_automation.json`.
2. Checks the stop file, elapsed runtime, and cycle count.
3. Confirms `prompts/ALPHA_AUTOMATION_CONTINUE.md` and `research_log/ALPHA_AUTONOMOUS_STATE.md`
   exist (fails closed if not).
4. Backs up the checkpoint.
5. Builds a prompt (persistent instructions + current checkpoint + cycle metadata) and pipes it to
   `claude -p` via stdin.
6. Captures stdout, stderr, exit code, and duration; writes them to
   `research_log/cycle_output/`.
7. Reads the **last line** of Claude's output for one of three markers:
   `ALPHA_CONTINUE_REQUIRED`, `ALPHA_MISSION_COMPLETE`, `ALPHA_IRRECOVERABLE_BLOCKER`.
8. Verifies the checkpoint file's hash actually changed. If Alpha said "continue" but did not
   rewrite the checkpoint, the orchestrator does **not** assume progress — it stops (fail-closed).
9. Loops, stops cleanly, or stops with a specific non-zero exit code — see [Exit codes](#exit-codes).

## Prerequisites

- Windows PowerShell 5.1 (built in; this system does **not** require PowerShell 7/pwsh).
- A working `claude` (Claude Code) install. This machine does not have `claude` on `PATH` — it
  only has the build bundled with Claude Desktop. Confirm what you have:

  ```powershell
  # If claude is on PATH:
  claude --version
  claude --help

  # If not (this machine's case), find the bundled exe via the env var Claude Code itself sets:
  echo $env:CLAUDE_CODE_EXECPATH
  & $env:CLAUDE_CODE_EXECPATH --version
  ```

  `config/alpha_automation.json`'s `claude_command` is currently pinned to the exact path this was
  built and tested against (`...\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude-code\2.1.217\claude.exe`).
  If Claude Desktop updates, that path's version segment (`2.1.217`) will change — re-run the
  `echo $env:CLAUDE_CODE_EXECPATH` check above and update `claude_command` accordingly. **Never
  assume CLI flags** — re-run `--help` against whatever binary you actually point at, since flags
  have changed between versions before (this system was built against a version with no
  `--max-turns` flag, for example — see below).
- TradingView Desktop running with CDP enabled on port 9222, if Alpha needs live chart/replay
  access this cycle (Phase 2.5 TVRE). The orchestrator does not start it for you — Alpha's own
  first step should call `tv_health_check` / `tv_launch` as needed.

## Files

| File | Purpose |
|---|---|
| `config/alpha_automation.json` | All tunables. No secrets or environment-specific values are hardcoded in the scripts. |
| `prompts/ALPHA_AUTOMATION_CONTINUE.md` | Persistent instructions sent every cycle. |
| `research_log/ALPHA_AUTONOMOUS_STATE.md` | The checkpoint. Alpha rewrites it completely every cycle. |
| `research_log/alpha_automation.log` | Orchestrator's own log (one line per event; rotates past `log_max_size_mb`). |
| `research_log/cycle_output/` | Raw stdout/stderr per cycle, plus dry-run artifacts. |
| `research_log/checkpoint_backups/` | One checkpoint backup per cycle, taken before invoking Claude. |
| `research_log/ALPHA_AUTOMATION.stop` | Presence of this file stops the loop before the next cycle. |
| `research_log/ALPHA_AUTOMATION.lock` / `.pid` | Single-instance lock + PID, removed on clean exit. |
| `scripts/run_alpha_automation.ps1` | The loop. |
| `scripts/stop_alpha_automation.ps1` | Controlled stop. |
| `scripts/AlphaAutomationCommon.psm1` | Shared config/lock/log/marker helpers used by both scripts and the tests. |
| `scripts/tests/Test-AlphaAutomation.ps1` | Self-executing test suite (see [Testing](#testing)). |

## Configuring the project

Open `config/alpha_automation.json`. Everything is documented inline via `_comment_*` keys. The
fields you are most likely to change:

- `max_cycles`, `delay_seconds`, `max_runtime_minutes` — how big a run you're authorizing.
- `dry_run` — **defaults to `true`**. You must explicitly set it to `false` (or pass `-DryRun:$false`
  is not a thing — just edit the config, or omit `-DryRun` and ensure config says `false`) to spend
  real API cost.
- `session_mode` — `"new"` (default, safest), `"resume_id"`, or `"continue"`. See the comment in
  the config file; `"continue"` risks resuming a manual session you have open in the same
  directory and is not recommended.
- `permission_mode` / `dangerously_skip_permissions` — `dangerously_skip_permissions` defaults to
  `false` and the script will refuse to silently enable it; you must explicitly set it to `true` in
  the config if you want that behavior, and the script logs a `WARN` every time it does so.
- `mcp_config_path` — points at the sibling `tradingview-mcp` repo's `.mcp.json` so Alpha has chart
  access. This is a read-only cross-repo reference; it does not modify that repo.

Config validation is strict: unknown-but-required keys missing, wrong types, or any path that
resolves outside `allowed_working_directory` all cause a hard failure with a specific message
(exit code 1) before anything is invoked.

## Running it

All commands assume you are in `C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation`.

### Dry run (no API calls, no checkpoint changes) — always do this first

```powershell
.\scripts\run_alpha_automation.ps1 -DryRun -MaxCycles 3
```

Inspect `research_log\alpha_automation.log` and `research_log\cycle_output\*.dryrun.txt` afterward
— the `.dryrun.txt` files show you the exact combined prompt+checkpoint text that *would* have been
piped to Claude, and the log shows the exact command line that *would* have run.

### One real cycle

```powershell
.\scripts\run_alpha_automation.ps1 -Once
```

Check the outcome before doing more:

```powershell
Get-Content .\research_log\alpha_automation.log -Tail 20
Get-Content .\research_log\ALPHA_AUTONOMOUS_STATE.md | Select-Object -First 40
```

### A bounded multi-cycle run

```powershell
.\scripts\run_alpha_automation.ps1 -MaxCycles 5
```

Or edit `max_cycles` / `max_runtime_minutes` in the config and just run:

```powershell
.\scripts\run_alpha_automation.ps1
```

The script refuses to run with `max_cycles` unset/zero, and defaults to a 4-hour runtime cap
(`max_runtime_minutes: 240`) even if you forget to set one.

## Stopping it

```powershell
.\scripts\stop_alpha_automation.ps1
```

This creates the stop file and waits (default 15s) for the loop to notice and exit on its own —
the loop checks for the stop file before every cycle and at every second of its inter-cycle delay,
so a clean stop is normally seconds away, not a full `delay_seconds` away. If it's still running
after the wait:

```powershell
.\scripts\stop_alpha_automation.ps1 -Force   # hard kill escape hatch, off by default
```

`-Force` is a last resort: it means whatever cycle was in flight may not have finished writing its
checkpoint. Check `research_log\ALPHA_AUTONOMOUS_STATE.md` and the most recent file in
`research_log\checkpoint_backups\` before trusting state after a forced stop.

You can also just create the stop file yourself for the exact same effect:

```powershell
New-Item -ItemType File .\research_log\ALPHA_AUTOMATION.stop -Force
```

## Recovering from errors

| Symptom | What happened | What to do |
|---|---|---|
| Exit 1 | Config invalid, or unhandled script error | Read the printed errors / log; fix the config. |
| Exit 2 | Prompt or checkpoint file missing | Restore the file from git or from `research_log\checkpoint_backups\`. |
| Exit 3 | Alpha reported `ALPHA_IRRECOVERABLE_BLOCKER` | Read the cause in the log (it prints the last lines of Alpha's output) — usually TradingView Desktop unreachable or a data-source problem. Fix the underlying issue, then restart. |
| Exit 4 | Marker missing/malformed past the configured grace | Check the last cycle's `.stdout.log` in `cycle_output\` — Claude likely did not end its message with a bare marker line as instructed. |
| Exit 5 | `claude` process itself failed repeatedly (non-zero exit) | Check `.stderr.log` for the failing cycles — likely a CLI/auth/permission problem unrelated to research content. |
| Exit 6 | Checkpoint didn't change after a declared "continue" | The orchestrator refused to assume progress. If the checkpoint file was also found empty/corrupted, it was already auto-restored from the most recent backup before this exit — verify with `git diff research_log/ALPHA_AUTONOMOUS_STATE.md` or by comparing against `research_log\checkpoint_backups\`. |
| Exit 7 | Another instance holds the lock | Either it's genuinely still running (`Get-Content research_log\ALPHA_AUTOMATION.pid` then `Get-Process -Id <that>`), or it crashed without cleaning up. If confirmed dead, remove `research_log\ALPHA_AUTOMATION.lock` and `.pid` manually. |
| Exit 8 | Script copied into/run from the wrong project | `config.project_path` must equal this script's own parent directory. Fix the config, or move the script back. |

### Restoring the checkpoint manually

Every cycle's pre-run checkpoint snapshot lives in `research_log\checkpoint_backups\`, named
`ALPHA_AUTONOMOUS_STATE.<cycle_id>.md`. To roll back to a specific point:

```powershell
Copy-Item .\research_log\checkpoint_backups\ALPHA_AUTONOMOUS_STATE.<cycle_id>.md `
          .\research_log\ALPHA_AUTONOMOUS_STATE.md -Force
```

Since `research_log/` is a normal git-tracked directory, `git log -- research_log/ALPHA_AUTONOMOUS_STATE.md`
and `git diff`/`git checkout` also work as an independent recovery path.

### Verifying Alpha actually progressed (not just "said" it did)

The orchestrator already does this for you mechanically (SHA-256 hash comparison, every cycle,
logged) and will not silently continue past a cycle where it didn't. To check yourself:

```powershell
git log --oneline -- research_log/  # did new OBS files / journal entries actually get committed?
git diff HEAD~1 -- research_log/ALPHA_AUTONOMOUS_STATE.md
```

A `ALPHA_CONTINUE_REQUIRED` marker with an unchanged checkpoint is treated as a failure (exit 6),
not a success — see the design note in [`prompts/ALPHA_AUTOMATION_CONTINUE.md`](../prompts/ALPHA_AUTOMATION_CONTINUE.md).

### Avoiding resuming the wrong session

Default `session_mode` is `"new"`: every cycle is a completely independent `claude -p` invocation
with no `-c`/`-r`/`--resume` flag at all. The on-disk checkpoint is the only thing carried forward.
This means it is **impossible** to accidentally resume a manual, unrelated Claude Code session in
this directory, because no session is ever resumed.

If you switch `session_mode` to `"resume_id"`, the orchestrator captures the `session_id` returned
by cycle 1 and reuses it explicitly for later cycles — still unambiguous (a specific ID, not "most
recent"). Only `session_mode: "continue"` (uses `-c`, "continue the most recent conversation in
this directory") carries real ambiguity risk, and it is not the default; the script logs a `WARN`
every time it's used.

## Testing

```powershell
.\scripts\tests\Test-AlphaAutomation.ps1
```

24 scenarios, no external dependencies, ~15-20 seconds, $0 cost (uses `scripts\tests\fake_claude.cmd`,
a simulated `claude` executable controlled entirely via environment variables — never point
production config at it). Covers: config validation (valid/invalid JSON/missing keys/path escape),
missing prompt/state files, stop file, single-instance locking (including two real concurrent
processes), the wrong-project guard, both `claude` process exit-code paths, all three markers plus
missing-marker with and without grace, checkpoint-changed/unchanged/corrupted-and-restored, max
cycles, max runtime, log rotation, dry-run non-invocation, and the lock/pid cleanup contract that
also protects against Ctrl+C (PowerShell runs `finally` blocks on pipeline-stop, which is what a
Ctrl+C raises — this suite verifies that contract directly rather than trying to script a literal
OS-level Ctrl+C signal into an unattended test run; see [Limitations](#risks--limitations)).

Windows ships Pester 3.4.0 (very old, incompatible assertion syntax with modern Pester). Rather
than fight that version or ask to install a newer one globally, this suite is a small self-
contained harness (`Test-Case`/`Assert-That`) — see the file's header comment for the reasoning.

## Risks & limitations

- **Cost**: every non-dry-run cycle is a real `claude -p` invocation. `max_cycles`,
  `max_runtime_minutes`, and `max_budget_usd` (if you set a per-cycle budget) are your cost
  controls. There is no cumulative cost cap across cycles in this version — `max_budget_usd` in the
  config is passed straight through as `--max-budget-usd` and is a **per-cycle** limit, not a
  per-run total.
- **No per-cycle timeout.** If a single `claude -p` invocation hangs, the loop waits indefinitely
  for it (only `max_runtime_minutes` is checked *between* cycles, not during one). This was not in
  the original spec's requirements list; if you need it, add a `WaitForExit(timeoutMs)` +
  `Kill($true)` around the process invocation in `run_alpha_automation.ps1`.
- **`--max-turns` is not supported** by the installed CLI (2.1.217; confirmed via `--help`). The
  config key exists for forward compatibility and is ignored with a one-time log warning if set.
- **`acceptEdits` permission mode plus non-interactive `-p`**: any tool call that isn't covered by
  your allow-listed permissions and isn't an edit will not get an interactive prompt to approve it
  (there is no TTY) — expect it to be denied rather than to hang, but this was not exhaustively
  verified against a real paid invocation as part of this build (see [Pilot](#pilot-results)
  below). If Alpha's research needs Bash/MCP tool calls beyond simple file edits, pre-approve them
  in this project's Claude Code settings, or explicitly opt into
  `dangerously_skip_permissions: true` after evaluating that risk yourself.
- **Ctrl+C is not tested end-to-end as an OS signal** — see the Testing section above. The
  underlying mechanism (try/finally around the whole loop; PowerShell runs `finally` on
  pipeline-stop) is standard and is tested directly, but nobody has sent this script a literal
  Ctrl+C during a real run as part of this build.
- **`session_mode: "resume_id"` and `"continue"`** are implemented and unit-testable in isolation,
  but have not been exercised against the real `claude` CLI (only against the fake one), since
  doing so costs real API calls. Prefer `"new"` (the default) until you've explicitly verified the
  others against a real invocation yourself.

## Pilot results

See the session that built this system for the dry-run pilot output. A real 1-cycle pilot against
the actual `claude.exe` was intentionally **not** run automatically as part of this build, because
it would spend real API budget and start genuine Alpha research without your review of this
document first. To run it yourself once you've read the above:

```powershell
# 1. Set dry_run to false in config\alpha_automation.json, then:
.\scripts\run_alpha_automation.ps1 -Once
```
