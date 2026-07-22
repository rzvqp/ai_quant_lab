#requires -Version 5.1
<#
.SYNOPSIS
    Controlled stop for the Alpha Automation loop.

.DESCRIPTION
    Default behavior (no switches): creates the configured stop file. The running loop checks for
    it before every cycle and during its inter-cycle delay, and exits cleanly (exit code 0, reason
    'stop_file') within at most ~1 second of the check. This script then waits up to -WaitSeconds
    for the PID in the pid file to actually disappear, and reports whether it did.

    This script does NOT delete an existing lock/pid file that still belongs to a live process --
    only a loop that has actually exited (or -Force) may have those cleaned up.

.PARAMETER ConfigPath
    Path to alpha_automation.json. Defaults to ..\config\alpha_automation.json relative to this
    script's own location.

.PARAMETER WaitSeconds
    How long to wait after creating the stop file for the loop's PID to disappear before reporting
    "still running". Default 15.

.PARAMETER Force
    Escape hatch: if the loop has not stopped on its own within -WaitSeconds, forcibly terminate
    the process via Stop-Process, then clean up the lock/pid files. Off by default -- this is a
    hard kill, not a controlled stop, and can leave a cycle's Claude subprocess or checkpoint write
    in an inconsistent state.

.PARAMETER ClearStopFileAfter
    Remove the stop file once the loop has confirmed stopped, so the NEXT run doesn't immediately
    see a stale stop file and refuse to start. Default: on (pass -ClearStopFileAfter:$false to keep it).
#>
[CmdletBinding()]
param(
    [string]$ConfigPath,
    [int]$WaitSeconds = 15,
    [switch]$Force,
    [bool]$ClearStopFileAfter = $true
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
$stopFile = $cfg.Resolved_stop_file
$pidFile = $cfg.Resolved_pid_file
$lockFile = $cfg.Resolved_lock_file

$wasRunning = Test-AlphaLockHeldByLiveProcess -PidPath $pidFile

if (-not (Test-Path -LiteralPath (Split-Path $stopFile -Parent))) {
    New-Item -ItemType Directory -Path (Split-Path $stopFile -Parent) -Force | Out-Null
}
Set-Content -LiteralPath $stopFile -Value "Stop requested at $((Get-Date).ToUniversalTime().ToString('o')) by stop_alpha_automation.ps1 (PID $PID)." -Encoding UTF8
Write-Host "Stop file created: $stopFile"

if (-not $wasRunning) {
    Write-Host "No live process found in pid file ($pidFile). Nothing appears to be running; stop file left in place so a not-yet-started loop won't launch until it is cleared."
    exit 0
}

$targetPid = (Get-Content -LiteralPath $pidFile -Raw).Trim()
Write-Host "Loop appears to be running (PID $targetPid). Waiting up to $WaitSeconds second(s) for a controlled exit..."

$stopped = $false
for ($i = 0; $i -lt $WaitSeconds; $i++) {
    Start-Sleep -Seconds 1
    if (-not (Test-AlphaLockHeldByLiveProcess -PidPath $pidFile)) { $stopped = $true; break }
}

if ($stopped) {
    Write-Host "Loop stopped on its own within $($i + 1)s."
    if ($ClearStopFileAfter) {
        Remove-Item -LiteralPath $stopFile -Force -ErrorAction SilentlyContinue
        Write-Host "Stop file cleared."
    }
    exit 0
}

Write-Host "Loop did NOT stop within $WaitSeconds second(s)."
if (-not $Force) {
    Write-Host "Not forcing termination (no -Force given). The stop file remains in place; the loop should still notice it at its next check. Re-run with -Force to hard-kill PID $targetPid if it is truly stuck." -ForegroundColor Yellow
    exit 1
}

Write-Host "Forcing termination of PID $targetPid (-Force given)." -ForegroundColor Yellow
try {
    Stop-Process -Id ([int]$targetPid) -Force -ErrorAction Stop
    Write-Host "Process $targetPid terminated."
} catch {
    Write-Host "Could not terminate PID ${targetPid}: $($_.Exception.Message)" -ForegroundColor Red
}
Remove-Item -LiteralPath $lockFile -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $pidFile -Force -ErrorAction SilentlyContinue
if ($ClearStopFileAfter) { Remove-Item -LiteralPath $stopFile -Force -ErrorAction SilentlyContinue }
Write-Host "Lock/pid files cleaned up after forced stop. NOTE: a forced stop means the in-flight cycle's checkpoint update may be incomplete -- check research_log\ALPHA_AUTONOMOUS_STATE.md and the checkpoint backup directory before trusting its state."
exit 0
