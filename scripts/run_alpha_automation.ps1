#requires -Version 5.1
<#
.SYNOPSIS
    Alpha Automation orchestration loop -- relaunches Claude Code non-interactively for the
    Alpha research division, cycle after cycle, until a stop condition is met.

.DESCRIPTION
    See docs/ALPHA_AUTOMATION.md for the full contract. In short: each cycle reads
    prompts/ALPHA_AUTOMATION_CONTINUE.md + research_log/ALPHA_AUTONOMOUS_STATE.md, feeds them to
    `claude -p` via stdin, captures stdout/stderr/exit code, checks the last line of output for
    one of three markers (ALPHA_CONTINUE_REQUIRED / ALPHA_MISSION_COMPLETE /
    ALPHA_IRRECOVERABLE_BLOCKER), verifies the checkpoint file actually changed, and either loops,
    stops cleanly, or stops with an error -- never assuming progress it cannot verify on disk.

.PARAMETER ConfigPath
    Path to alpha_automation.json. Defaults to ..\config\alpha_automation.json relative to this
    script's own location.

.PARAMETER DryRun
    Force dry-run regardless of the config file's dry_run value: builds every prompt/argument and
    logs what WOULD be run, but never invokes Claude and never touches the checkpoint.

.PARAMETER MaxCycles
    Override config max_cycles for this invocation only.

.PARAMETER Once
    Convenience for -MaxCycles 1.

.PARAMETER ClaudeCommandOverride
    Override config claude_command for this invocation only. Used by the test suite to point at a
    fake/simulated claude executable instead of the real one.

.PARAMETER NoDelay
    Collapse inter-cycle and retry delays to near-zero. Used by the test suite; never use for a
    real research run (it exists purely to make automated tests fast).

.EXIT CODES
    0 clean stop (mission complete / stop file / max cycles / max runtime reached)
    1 invalid configuration
    2 required prompt/state file missing (fail-closed)
    3 ALPHA_IRRECOVERABLE_BLOCKER reported by Alpha
    4 output marker missing/invalid beyond the configured grace
    5 max consecutive process/exit-code failures exceeded
    6 checkpoint not updated after a cycle that declared progress (fail-closed)
    7 another instance already holds the lock
    8 script is not running from the project directory named in its own config (safety check)
#>
[CmdletBinding()]
param(
    [string]$ConfigPath,
    [switch]$DryRun,
    [int]$MaxCycles = -1,
    [switch]$Once,
    [string]$ClaudeCommandOverride,
    [switch]$NoDelay
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

Import-Module (Join-Path $PSScriptRoot 'AlphaAutomationCommon.psm1') -Force

if (-not $ConfigPath) {
    $ConfigPath = Join-Path $PSScriptRoot '..\config\alpha_automation.json'
}
$ConfigPath = [System.IO.Path]::GetFullPath($ConfigPath)

$loaded = Import-AlphaConfig -ConfigPath $ConfigPath
if (-not $loaded.Valid) {
    Write-Host "Configuration is invalid:" -ForegroundColor Red
    foreach ($e in $loaded.Errors) { Write-Host "  - $e" -ForegroundColor Red }
    exit 1
}
$cfg = $loaded.Config

# --- Safety check: this script must be running from inside the project it is configured for.
$scriptProjectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
if ($scriptProjectRoot.TrimEnd('\','/') -ne $cfg.Resolved_project_path.TrimEnd('\','/')) {
    Write-Host "Refusing to run: this script lives under '$scriptProjectRoot' but the config's project_path is '$($cfg.Resolved_project_path)'. Copying this script into another project without updating config, or vice versa, is exactly the 'wrong project' scenario this check exists to catch." -ForegroundColor Red
    exit 8
}

if ($MaxCycles -ge 0) { $cfg.max_cycles = $MaxCycles }
if ($Once) { $cfg.max_cycles = 1 }
if ($DryRun) { $cfg.dry_run = $true }
if ($ClaudeCommandOverride) { $cfg.claude_command = $ClaudeCommandOverride }

$logFile   = $cfg.Resolved_log_file
$stateFile = $cfg.Resolved_state_file
$promptFile = $cfg.Resolved_prompt_file
$stopFile  = $cfg.Resolved_stop_file
$lockFile  = $cfg.Resolved_lock_file
$pidFile   = $cfg.Resolved_pid_file
$sessionIdFile = $cfg.Resolved_session_id_file
$outputDir = $cfg.Resolved_output_directory
$backupDir = $cfg.Resolved_checkpoint_backup_directory

foreach ($d in @($outputDir, $backupDir, (Split-Path $logFile -Parent), (Split-Path $lockFile -Parent))) {
    if (-not (Test-Path -LiteralPath $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
}

function Log { param($Level, $Message) Write-AlphaLog -LogPath $logFile -Level $Level -Message $Message -MaxSizeMb $cfg.log_max_size_mb }

if (-not $cfg.claude_command -or -not (Test-Path -LiteralPath $cfg.claude_command -PathType Leaf)) {
    Log 'ERROR' "claude_command does not exist or is not set: '$($cfg.claude_command)'"
    exit 1
}
if ($cfg.dangerously_skip_permissions -eq $true) {
    Log 'WARN' "dangerously_skip_permissions is TRUE in config -- this run will pass --dangerously-skip-permissions to Claude. This was explicitly enabled by the config, not defaulted."
}
if (Get-Member -InputObject $cfg -Name 'max_turns' -MemberType NoteProperty) {
    if ($null -ne $cfg.max_turns) {
        Log 'WARN' "config max_turns=$($cfg.max_turns) is set but the installed claude CLI (checked via --help) has no --max-turns flag; this key is ignored."
    }
}

$lockStream = Lock-AlphaAutomation -LockPath $lockFile -PidPath $pidFile
if ($null -eq $lockStream) {
    Log 'ERROR' "Another instance appears to hold the lock ($lockFile). Refusing to start a second instance. If you are certain no other instance is running, check research_log\ALPHA_AUTOMATION.pid and remove the lock manually."
    exit 7
}

Log 'INFO' "=== Alpha Automation loop starting === config=$ConfigPath dry_run=$($cfg.dry_run) max_cycles=$($cfg.max_cycles) session_mode=$($cfg.session_mode) pid=$PID"

$cleanupAction = {
    Unlock-AlphaAutomation -LockStream $lockStream -LockPath $lockFile -PidPath $pidFile
}
Register-EngineEvent -SourceIdentifier ([System.Management.Automation.PsEngineEvent]::Exiting) -Action $cleanupAction | Out-Null

$exitCode = 0
try {
    $startTime = Get-Date
    $cycle = 0
    $consecutiveFailures = 0
    $consecutiveMissingMarker = 0
    $consecutiveNoProgress = 0
    $stopReason = $null

    while ($cycle -lt $cfg.max_cycles) {
        $cycle++
        $cycleId = "{0:yyyyMMddTHHmmssZ}-c{1}" -f (Get-Date).ToUniversalTime(), $cycle
        $runId = $cycleId

        if (Test-Path -LiteralPath $stopFile -PathType Leaf) {
            Log 'INFO' "Stop file present ($stopFile). Stopping controlled before cycle $cycle."
            $stopReason = 'stop_file'
            break
        }

        $elapsedMinutes = ((Get-Date) - $startTime).TotalMinutes
        if ($elapsedMinutes -ge $cfg.max_runtime_minutes) {
            Log 'INFO' "max_runtime_minutes ($($cfg.max_runtime_minutes)) reached ($([math]::Round($elapsedMinutes,1)) min elapsed). Stopping controlled."
            $stopReason = 'max_runtime'
            break
        }

        if (-not (Test-Path -LiteralPath $promptFile -PathType Leaf)) {
            Log 'CRITICAL' "Prompt file missing: $promptFile"
            if ($cfg.stop_on_missing_prompt) { $exitCode = 2; $stopReason = 'missing_prompt'; break }
            else { Log 'WARN' "stop_on_missing_prompt=false; skipping this cycle slot without invoking Claude."; Start-Sleep -Seconds 1; continue }
        }
        if (-not (Test-Path -LiteralPath $stateFile -PathType Leaf)) {
            Log 'CRITICAL' "State/checkpoint file missing: $stateFile"
            if ($cfg.stop_on_missing_state) { $exitCode = 2; $stopReason = 'missing_state'; break }
            else { Log 'WARN' "stop_on_missing_state=false; skipping this cycle slot without invoking Claude."; Start-Sleep -Seconds 1; continue }
        }

        $backupPath = $null
        if ($cfg.backup_state_before_cycle) {
            $backupPath = Join-Path $backupDir ("ALPHA_AUTONOMOUS_STATE.{0}.md" -f $cycleId)
            Copy-Item -LiteralPath $stateFile -Destination $backupPath -Force
            Log 'INFO' "Checkpoint backed up to $backupPath"
        }
        $preHash = Get-FileHashSafe -Path $stateFile

        $promptBody = Get-Content -LiteralPath $promptFile -Raw -Encoding UTF8
        $stateBody = Get-Content -LiteralPath $stateFile -Raw -Encoding UTF8
        $header = @"
<!-- AUTOMATION CYCLE METADATA (injected by run_alpha_automation.ps1) -->
cycle: $cycle
run_id: $runId
timestamp_utc: $((Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ'))
instruction: Continue the actual research now. Do not just report status. Follow the rules below,
then rewrite the checkpoint and end with exactly one marker as the last line.
<!-- END METADATA -->

$promptBody

---
# Current checkpoint (research_log/ALPHA_AUTONOMOUS_STATE.md) as of this cycle's start

$stateBody
"@

        $args = @('-p', '--output-format', $cfg.output_format, '--permission-mode', $cfg.permission_mode)
        if ($cfg.dangerously_skip_permissions -eq $true) { $args += '--dangerously-skip-permissions' }
        if ($cfg.model) { $args += @('--model', $cfg.model) }
        if ($cfg.effort) { $args += @('--effort', $cfg.effort) }
        if ($cfg.max_budget_usd) { $args += @('--max-budget-usd', "$($cfg.max_budget_usd)") }
        if ((Get-Member -InputObject $cfg -Name 'mcp_config_path' -MemberType NoteProperty) -and $cfg.mcp_config_path) {
            $args += @('--mcp-config', $cfg.mcp_config_path)
        }
        $storedSessionId = $null
        if (Test-Path -LiteralPath $sessionIdFile -PathType Leaf) {
            $storedSessionId = (Get-Content -LiteralPath $sessionIdFile -Raw -ErrorAction SilentlyContinue)
            if ($storedSessionId) { $storedSessionId = $storedSessionId.Trim() }
        }
        switch ($cfg.session_mode) {
            'resume_id' {
                if ($storedSessionId) { $args += @('--resume', $storedSessionId) }
                else { Log 'INFO' "session_mode=resume_id but no stored session id yet; this cycle starts a new session (id will be captured for next cycle)." }
            }
            'continue' {
                $args += '-c'
                Log 'WARN' "session_mode=continue uses -c (most recent conversation in this directory). Make sure no manual Claude Code sessions run in this project."
            }
            default {} # 'new': no session flags
        }

        if ($cfg.dry_run) {
            Log 'INFO' "[DRY RUN] cycle=$cycle would invoke: `"$($cfg.claude_command)`" $($args -join ' ') (stdin length $($header.Length) chars)"
            $dryOutPath = Join-Path $outputDir "cycle_$cycleId.dryrun.txt"
            Set-Content -LiteralPath $dryOutPath -Value $header -Encoding UTF8
            if (-not $NoDelay) { Start-Sleep -Seconds $cfg.delay_seconds } else { Start-Sleep -Milliseconds 50 }
            continue
        }

        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = $cfg.claude_command
        $psi.Arguments = ConvertTo-WindowsArgumentString -ArgumentList $args
        $psi.WorkingDirectory = $cfg.Resolved_project_path
        $psi.RedirectStandardInput = $true
        $psi.RedirectStandardOutput = $true
        $psi.RedirectStandardError = $true
        $psi.UseShellExecute = $false
        $psi.StandardOutputEncoding = [System.Text.Encoding]::UTF8
        $psi.StandardErrorEncoding = [System.Text.Encoding]::UTF8

        $cycleStart = Get-Date
        $proc = New-Object System.Diagnostics.Process
        $proc.StartInfo = $psi
        Log 'INFO' "Cycle $cycle starting: run_id=$runId args=[$($args -join ' ')]"
        [void]$proc.Start()
        # .NET Framework's Process.StandardInput StreamWriter has no configurable encoding (unlike
        # StandardOutput/ErrorEncoding above -- ProcessStartInfo has no StandardInputEncoding
        # property on this runtime). Writing through it would silently re-encode the prompt via the
        # system's default codepage and corrupt non-ASCII characters. Write raw UTF-8 bytes directly
        # to the underlying stream instead, bypassing that default entirely.
        $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
        $headerBytes = $utf8NoBom.GetBytes($header)
        $proc.StandardInput.BaseStream.Write($headerBytes, 0, $headerBytes.Length)
        $proc.StandardInput.BaseStream.Flush()
        $proc.StandardInput.Close()
        $stdoutTask = $proc.StandardOutput.ReadToEndAsync()
        $stderrTask = $proc.StandardError.ReadToEndAsync()
        $proc.WaitForExit()
        $stdout = $stdoutTask.GetAwaiter().GetResult()
        $stderr = $stderrTask.GetAwaiter().GetResult()
        $procExitCode = $proc.ExitCode
        $cycleEnd = Get-Date
        $durationSec = [math]::Round(($cycleEnd - $cycleStart).TotalSeconds, 1)

        $stdoutPath = Join-Path $outputDir "cycle_$cycleId.stdout.log"
        $stderrPath = Join-Path $outputDir "cycle_$cycleId.stderr.log"
        Set-Content -LiteralPath $stdoutPath -Value $stdout -Encoding UTF8
        Set-Content -LiteralPath $stderrPath -Value $stderr -Encoding UTF8

        Log 'INFO' "Cycle $cycle finished: exit_code=$procExitCode duration_s=$durationSec stdout=$stdoutPath stderr=$stderrPath"

        if ($procExitCode -ne 0) {
            $consecutiveFailures++
            $stderrTailLines = $stderr -split "`r?`n" | Select-Object -Last 5
            $stderrTail = $stderrTailLines -join ' | '
            Log 'ERROR' "Claude process exited non-zero ($procExitCode), consecutive_failures=$consecutiveFailures/$($cfg.max_consecutive_failures). stderr tail: $stderrTail"
            if ($consecutiveFailures -ge $cfg.max_consecutive_failures) {
                Log 'CRITICAL' "max_consecutive_failures reached. Stopping."
                $exitCode = 5; $stopReason = 'max_consecutive_failures'; break
            }
            if (-not $NoDelay) { Start-Sleep -Seconds $cfg.retry_delay_seconds } else { Start-Sleep -Milliseconds 50 }
            continue
        }
        $consecutiveFailures = 0

        $resultText = Get-AlphaResultText -RawStdout $stdout -OutputFormat $cfg.output_format
        $marker = Get-AlphaLastMarker -Text $resultText
        $postHash = Get-FileHashSafe -Path $stateFile
        $checkpointChanged = ($preHash -ne $postHash)

        # A wiped/truncated checkpoint also changes the hash (to "empty"), so this corruption check
        # must run independently of -- and before -- the "did it change" progress check below.
        # Checked via decoded text length, not raw byte length: Set-Content -Encoding UTF8 still
        # writes a 3-byte BOM for an empty string, so a byte-length check alone would miss it.
        $stateTextForCorruptionCheck = if (Test-Path -LiteralPath $stateFile -PathType Leaf) { Get-Content -LiteralPath $stateFile -Raw -Encoding UTF8 -ErrorAction SilentlyContinue } else { $null }
        $stateIsCorrupted = (-not (Test-Path -LiteralPath $stateFile -PathType Leaf)) -or ([string]::IsNullOrWhiteSpace($stateTextForCorruptionCheck))
        if ($stateIsCorrupted -and $backupPath -and (Test-Path -LiteralPath $backupPath)) {
            Copy-Item -LiteralPath $backupPath -Destination $stateFile -Force
            Log 'CRITICAL' "Checkpoint file was missing/empty after cycle $cycle -- restored from backup $backupPath. Treating this cycle as no-progress regardless of marker."
            $postHash = Get-FileHashSafe -Path $stateFile
            $checkpointChanged = ($preHash -ne $postHash)
        }

        $newSessionId = Get-AlphaSessionIdFromOutput -RawStdout $stdout -OutputFormat $cfg.output_format
        if ($newSessionId -and $cfg.session_mode -eq 'resume_id') {
            New-AtomicFile -Path $sessionIdFile -Content $newSessionId
            Log 'INFO' "Captured session_id for resume_id mode: $newSessionId"
        }

        if ($null -eq $marker) {
            $consecutiveMissingMarker++
            $tail = ($resultText -split "`r?`n" | Where-Object { $_.Trim() } | Select-Object -Last 3) -join ' | '
            Log 'WARN' "No recognized marker as the last line of output (consecutive_missing=$consecutiveMissingMarker). Tail: $tail"
            if ($cfg.require_continue_marker -and $consecutiveMissingMarker -ge 1 -and $cfg.max_consecutive_missing_marker -le 0) {
                Log 'CRITICAL' "require_continue_marker=true and max_consecutive_missing_marker<=0: stopping immediately on missing marker (fail-closed, not looping aggressively)."
                $exitCode = 4; $stopReason = 'missing_marker'; break
            }
            if ($consecutiveMissingMarker -ge $cfg.max_consecutive_missing_marker) {
                Log 'CRITICAL' "max_consecutive_missing_marker reached. Stopping (fail-closed)."
                $exitCode = 4; $stopReason = 'missing_marker'; break
            }
            if (-not $NoDelay) { Start-Sleep -Seconds $cfg.delay_seconds } else { Start-Sleep -Milliseconds 50 }
            continue
        }
        $consecutiveMissingMarker = 0

        if ($marker -eq $script:Markers.Blocker) {
            $tail = ($resultText -split "`r?`n" | Where-Object { $_.Trim() } | Select-Object -Last 15) -join "`n"
            Log 'CRITICAL' "ALPHA_IRRECOVERABLE_BLOCKER reported. Cause (last lines of output):`n$tail"
            $exitCode = 3; $stopReason = 'irrecoverable_blocker'; break
        }

        if ($marker -eq $script:Markers.Complete) {
            if (-not $checkpointChanged) {
                Log 'WARN' "ALPHA_MISSION_COMPLETE received but checkpoint hash did not change -- Alpha may not have rewritten the checkpoint as required. Stopping anyway (mission-complete is unconditional per spec), but flag this for human review."
            }
            Log 'INFO' "ALPHA_MISSION_COMPLETE received. Stopping controlled."
            $exitCode = 0; $stopReason = 'mission_complete'; break
        }

        # marker must be Continue at this point
        if (-not $checkpointChanged) {
            $consecutiveNoProgress++
            Log 'ERROR' "ALPHA_CONTINUE_REQUIRED received but the checkpoint file did not change (hash identical, after any corruption restore above). Not assuming progress. consecutive_no_progress=$consecutiveNoProgress/$($cfg.max_consecutive_no_progress)."
            if ($consecutiveNoProgress -ge $cfg.max_consecutive_no_progress) {
                Log 'CRITICAL' "max_consecutive_no_progress reached. Stopping (fail-closed: will not assume progress that isn't on disk)."
                $exitCode = 6; $stopReason = 'no_progress'; break
            }
            if (-not $NoDelay) { Start-Sleep -Seconds $cfg.retry_delay_seconds } else { Start-Sleep -Milliseconds 50 }
            continue
        }
        $consecutiveNoProgress = 0
        Log 'INFO' "Cycle ${cycle}: ALPHA_CONTINUE_REQUIRED, checkpoint updated. Proceeding to next cycle after $($cfg.delay_seconds)s."

        if (Test-Path -LiteralPath $stopFile -PathType Leaf) {
            Log 'INFO' "Stop file appeared during cycle $cycle. Stopping controlled before delay."
            $stopReason = 'stop_file'
            break
        }
        if (-not $NoDelay) {
            $waited = 0
            while ($waited -lt $cfg.delay_seconds) {
                if (Test-Path -LiteralPath $stopFile -PathType Leaf) { break }
                Start-Sleep -Seconds ([Math]::Min(1, $cfg.delay_seconds - $waited))
                $waited++
            }
        } else {
            Start-Sleep -Milliseconds 50
        }
    }

    if (-not $stopReason) {
        Log 'INFO' "max_cycles ($($cfg.max_cycles)) reached without a terminal marker. Stopping controlled."
        $stopReason = 'max_cycles'
    }
    Log 'INFO' "=== Alpha Automation loop ended === reason=$stopReason exit_code=$exitCode cycles_run=$cycle"
}
catch {
    Log 'CRITICAL' "Unhandled error in orchestration loop: $($_.Exception.Message)`n$($_.ScriptStackTrace)"
    $exitCode = 1
}
finally {
    Unlock-AlphaAutomation -LockStream $lockStream -LockPath $lockFile -PidPath $pidFile
    Log 'INFO' "Lock released, PID file removed."
}

exit $exitCode
