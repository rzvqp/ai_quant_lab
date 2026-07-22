#requires -Version 5.1
<#
.SYNOPSIS
    Self-executing test suite for the Alpha Automation orchestration system. No external test
    framework required.

.DESCRIPTION
    Windows ships Pester 3.4.0, which is old enough (pre-`Should -Be` syntax, no modern mocking)
    that depending on it would make these tests fragile across machines and harder to read than a
    small purpose-built harness. This script IS that harness: Test-Case/Assert-That below, plus a
    `fake_claude.cmd` (scripts\tests\) standing in for the real Claude Code CLI so the whole
    pipeline -- process invocation, stdin/stdout capture, marker parsing, checkpoint-hash
    comparison, locking, log rotation -- can be exercised deterministically and for $0.

    Every scenario runs inside a throwaway sandbox directory (a full copy of scripts\, a generated
    config, and minimal prompt/state files) under the OS temp directory, created fresh and removed
    after each Test-Case. The real project's prompts/research_log/config are NEVER touched by this
    suite.

.PARAMETER KeepSandboxes
    Do not delete sandbox directories after each test (for debugging a failure).
#>
[CmdletBinding()]
param([switch]$KeepSandboxes)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$RepoScriptsDir = Split-Path $PSScriptRoot -Parent
$RepoRoot = Split-Path $RepoScriptsDir -Parent
$FakeClaudeCmd = Join-Path $PSScriptRoot 'fake_claude.cmd'
$FakeClaudeImpl = Join-Path $PSScriptRoot 'fake_claude_impl.ps1'
$PwshExe = Join-Path $PSHOME 'powershell.exe'

if (-not (Test-Path -LiteralPath $FakeClaudeCmd)) { throw "fake_claude.cmd not found next to this test script." }

$script:PassCount = 0
$script:FailCount = 0
$script:FailedNames = New-Object System.Collections.Generic.List[string]

function Assert-That {
    param([Parameter(Mandatory)][bool]$Condition, [Parameter(Mandatory)][string]$Message)
    if (-not $Condition) { throw "Assertion failed: $Message" }
}

function Test-Case {
    param([Parameter(Mandatory)][string]$Name, [Parameter(Mandatory)][scriptblock]$Body)
    Write-Host "`n--- $Name ---"
    try {
        & $Body
        $script:PassCount++
        Write-Host "[PASS] $Name" -ForegroundColor Green
    } catch {
        $script:FailCount++
        $script:FailedNames.Add($Name)
        Write-Host "[FAIL] $Name" -ForegroundColor Red
        Write-Host "       $($_.Exception.Message)" -ForegroundColor Red
    }
}

# ---------------------------------------------------------------------------
# Sandbox helpers
# ---------------------------------------------------------------------------

function New-Sandbox {
    param([hashtable]$ConfigOverrides = @{})

    $root = Join-Path ([System.IO.Path]::GetTempPath()) ("alpha_automation_test_" + [Guid]::NewGuid().ToString('N').Substring(0,10))
    New-Item -ItemType Directory -Path $root | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $root 'scripts\tests') -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $root 'config') | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $root 'prompts') | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $root 'research_log\checkpoint_backups') -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $root 'research_log\cycle_output') -Force | Out-Null

    Copy-Item -LiteralPath (Join-Path $RepoScriptsDir 'run_alpha_automation.ps1') -Destination (Join-Path $root 'scripts\run_alpha_automation.ps1')
    Copy-Item -LiteralPath (Join-Path $RepoScriptsDir 'AlphaAutomationCommon.psm1') -Destination (Join-Path $root 'scripts\AlphaAutomationCommon.psm1')
    Copy-Item -LiteralPath $FakeClaudeCmd -Destination (Join-Path $root 'scripts\tests\fake_claude.cmd')
    Copy-Item -LiteralPath $FakeClaudeImpl -Destination (Join-Path $root 'scripts\tests\fake_claude_impl.ps1')

    Set-Content -LiteralPath (Join-Path $root 'prompts\ALPHA_AUTOMATION_CONTINUE.md') -Value "# Test prompt`nDo the thing." -Encoding UTF8
    Set-Content -LiteralPath (Join-Path $root 'research_log\ALPHA_AUTONOMOUS_STATE.md') -Value "# Test checkpoint`nline1`n" -Encoding UTF8

    $cfg = [ordered]@{
        schema_version                   = '1.0'
        project_path                      = $root
        allowed_working_directory         = $root
        claude_command                    = (Join-Path $root 'scripts\tests\fake_claude.cmd')
        mcp_config_path                   = $null
        prompt_file                       = 'prompts\ALPHA_AUTOMATION_CONTINUE.md'
        state_file                        = 'research_log\ALPHA_AUTONOMOUS_STATE.md'
        log_file                          = 'research_log\alpha_automation.log'
        stop_file                         = 'research_log\ALPHA_AUTOMATION.stop'
        lock_file                         = 'research_log\ALPHA_AUTOMATION.lock'
        pid_file                          = 'research_log\ALPHA_AUTOMATION.pid'
        session_id_file                   = 'research_log\ALPHA_AUTOMATION.session_id'
        output_directory                  = 'research_log\cycle_output'
        checkpoint_backup_directory       = 'research_log\checkpoint_backups'
        session_mode                      = 'new'
        output_format                     = 'json'
        permission_mode                   = 'acceptEdits'
        dangerously_skip_permissions      = $false
        model                             = $null
        effort                            = $null
        max_turns                         = $null
        max_budget_usd                    = $null
        max_cycles                        = 2
        delay_seconds                     = 0
        retry_delay_seconds               = 0
        max_consecutive_failures          = 2
        max_consecutive_missing_marker    = 1
        max_consecutive_no_progress       = 1
        max_runtime_minutes               = 60
        log_max_size_mb                   = 20
        dry_run                           = $false
        backup_state_before_cycle         = $true
        require_continue_marker           = $true
        stop_on_missing_state             = $true
        stop_on_missing_prompt            = $true
    }
    foreach ($key in $ConfigOverrides.Keys) { $cfg[$key] = $ConfigOverrides[$key] }

    ($cfg | ConvertTo-Json -Depth 5) | Set-Content -LiteralPath (Join-Path $root 'config\alpha_automation.json') -Encoding UTF8

    return $root
}

function Remove-Sandbox {
    param([string]$Root)
    if ($KeepSandboxes) { Write-Host "  (kept sandbox: $Root)"; return }
    Remove-Item -LiteralPath $Root -Recurse -Force -ErrorAction SilentlyContinue
}

function Invoke-RunScript {
    param([Parameter(Mandatory)][string]$SandboxRoot, [string[]]$ExtraArgs = @(), [int]$TimeoutMs = 30000)
    $scriptPath = Join-Path $SandboxRoot 'scripts\run_alpha_automation.ps1'
    $configPath = Join-Path $SandboxRoot 'config\alpha_automation.json'
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $PwshExe
    $argList = @('-NoProfile', '-NoLogo', '-ExecutionPolicy', 'Bypass', '-File', $scriptPath, '-ConfigPath', $configPath, '-NoDelay') + $ExtraArgs
    $psi.Arguments = ConvertTo-WindowsArgumentString -ArgumentList $argList
    $psi.WorkingDirectory = $SandboxRoot
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $psi
    [void]$proc.Start()
    $outTask = $proc.StandardOutput.ReadToEndAsync()
    $errTask = $proc.StandardError.ReadToEndAsync()
    $finished = $proc.WaitForExit($TimeoutMs)
    if (-not $finished) {
        try { $proc.Kill($true) } catch {}
        throw "run_alpha_automation.ps1 did not exit within ${TimeoutMs}ms (sandbox: $SandboxRoot)"
    }
    $stdout = $outTask.GetAwaiter().GetResult()
    $stderr = $errTask.GetAwaiter().GetResult()
    return @{ ExitCode = $proc.ExitCode; Stdout = $stdout; Stderr = $stderr; Process = $proc }
}

function Start-RunScriptAsync {
    <# For concurrency tests: returns the live Process object without waiting. #>
    param([Parameter(Mandatory)][string]$SandboxRoot, [string[]]$ExtraArgs = @())
    $scriptPath = Join-Path $SandboxRoot 'scripts\run_alpha_automation.ps1'
    $configPath = Join-Path $SandboxRoot 'config\alpha_automation.json'
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $PwshExe
    $argList = @('-NoProfile', '-NoLogo', '-ExecutionPolicy', 'Bypass', '-File', $scriptPath, '-ConfigPath', $configPath, '-NoDelay') + $ExtraArgs
    $psi.Arguments = ConvertTo-WindowsArgumentString -ArgumentList $argList
    $psi.WorkingDirectory = $SandboxRoot
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $psi
    [void]$proc.Start()
    return $proc
}

Import-Module (Join-Path $RepoScriptsDir 'AlphaAutomationCommon.psm1') -Force

# ===========================================================================
# 1. Config validation
# ===========================================================================

Test-Case "config valid" {
    $root = New-Sandbox
    try {
        $r = Import-AlphaConfig -ConfigPath (Join-Path $root 'config\alpha_automation.json')
        Assert-That $r.Valid "expected a freshly generated sandbox config to be valid: $($r.Errors -join '; ')"
    } finally { Remove-Sandbox $root }
}

Test-Case "config invalid - missing required key" {
    $root = New-Sandbox
    try {
        $configPath = Join-Path $root 'config\alpha_automation.json'
        $obj = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
        $obj.PSObject.Properties.Remove('max_cycles')
        ($obj | ConvertTo-Json -Depth 5) | Set-Content -LiteralPath $configPath -Encoding UTF8
        $r = Import-AlphaConfig -ConfigPath $configPath
        Assert-That (-not $r.Valid) "expected config missing max_cycles to be invalid"
        Assert-That (($r.Errors -join ' ') -match 'max_cycles') "expected error message to mention max_cycles, got: $($r.Errors -join '; ')"
    } finally { Remove-Sandbox $root }
}

Test-Case "config invalid - malformed JSON" {
    $root = New-Sandbox
    try {
        $configPath = Join-Path $root 'config\alpha_automation.json'
        Set-Content -LiteralPath $configPath -Value '{ this is not json ' -Encoding UTF8
        $r = Import-AlphaConfig -ConfigPath $configPath
        Assert-That (-not $r.Valid) "expected malformed JSON to be invalid"
    } finally { Remove-Sandbox $root }
}

Test-Case "config invalid - path escapes project root" {
    $root = New-Sandbox -ConfigOverrides @{ state_file = '..\..\outside.md' }
    try {
        $r = Import-AlphaConfig -ConfigPath (Join-Path $root 'config\alpha_automation.json')
        Assert-That (-not $r.Valid) "expected state_file escaping project root to be rejected"
        Assert-That (($r.Errors -join ' ') -match 'outside allowed_working_directory') "expected a path-escape error, got: $($r.Errors -join '; ')"
    } finally { Remove-Sandbox $root }
}

# ===========================================================================
# 2. Missing files / stop file / locking / wrong-project guard
# ===========================================================================

Test-Case "prompt file missing -> exit 2, fail closed" {
    $root = New-Sandbox
    try {
        Remove-Item -LiteralPath (Join-Path $root 'prompts\ALPHA_AUTOMATION_CONTINUE.md') -Force
        $r = Invoke-RunScript -SandboxRoot $root
        Assert-That ($r.ExitCode -eq 2) "expected exit code 2, got $($r.ExitCode). stderr: $($r.Stderr)"
    } finally { Remove-Sandbox $root }
}

Test-Case "state file missing -> exit 2, fail closed" {
    $root = New-Sandbox
    try {
        Remove-Item -LiteralPath (Join-Path $root 'research_log\ALPHA_AUTONOMOUS_STATE.md') -Force
        $r = Invoke-RunScript -SandboxRoot $root
        Assert-That ($r.ExitCode -eq 2) "expected exit code 2, got $($r.ExitCode)"
    } finally { Remove-Sandbox $root }
}

Test-Case "stop file present -> immediate controlled stop, exit 0" {
    $root = New-Sandbox
    try {
        Set-Content -LiteralPath (Join-Path $root 'research_log\ALPHA_AUTOMATION.stop') -Value 'stop' -Encoding UTF8
        $env:FAKE_CLAUDE_CALL_LOG = Join-Path $root 'research_log\call.log'
        $r = Invoke-RunScript -SandboxRoot $root
        Assert-That ($r.ExitCode -eq 0) "expected exit code 0, got $($r.ExitCode)"
        Assert-That (-not (Test-Path (Join-Path $root 'research_log\call.log'))) "claude should never have been invoked when stop file was already present"
    } finally { Remove-Item Env:\FAKE_CLAUDE_CALL_LOG -ErrorAction SilentlyContinue; Remove-Sandbox $root }
}

Test-Case "lock already held -> exit 7, second instance refuses" {
    $root = New-Sandbox
    $lockStream = $null
    try {
        $lockPath = Join-Path $root 'research_log\ALPHA_AUTOMATION.lock'
        $pidPath = Join-Path $root 'research_log\ALPHA_AUTOMATION.pid'
        $lockStream = Lock-AlphaAutomation -LockPath $lockPath -PidPath $pidPath
        Assert-That ($null -ne $lockStream) "test setup failed: could not acquire lock itself"
        $r = Invoke-RunScript -SandboxRoot $root
        Assert-That ($r.ExitCode -eq 7) "expected exit code 7 when lock already held, got $($r.ExitCode)"
    } finally {
        if ($lockStream) { Unlock-AlphaAutomation -LockStream $lockStream -LockPath (Join-Path $root 'research_log\ALPHA_AUTOMATION.lock') -PidPath (Join-Path $root 'research_log\ALPHA_AUTOMATION.pid') }
        Remove-Sandbox $root
    }
}

Test-Case "two real concurrent instances -> second refuses while first runs" {
    $root = New-Sandbox -ConfigOverrides @{ max_cycles = 1 }
    $env:FAKE_CLAUDE_SLEEP_MS = '3000'
    $env:FAKE_CLAUDE_MARKER = 'COMPLETE'
    try {
        $first = Start-RunScriptAsync -SandboxRoot $root
        Start-Sleep -Milliseconds 800
        $second = Invoke-RunScript -SandboxRoot $root -TimeoutMs 10000
        Assert-That ($second.ExitCode -eq 7) "expected the second concurrent instance to exit 7, got $($second.ExitCode)"
        $finished = $first.WaitForExit(15000)
        Assert-That $finished "first instance should have finished within 15s"
        Assert-That ($first.ExitCode -eq 0) "expected first instance to finish with exit 0 (COMPLETE), got $($first.ExitCode)"
    } finally {
        Remove-Item Env:\FAKE_CLAUDE_SLEEP_MS, Env:\FAKE_CLAUDE_MARKER -ErrorAction SilentlyContinue
        Remove-Sandbox $root
    }
}

Test-Case "wrong project -> exit 8 when config.project_path does not match script location" {
    $root = New-Sandbox
    try {
        $configPath = Join-Path $root 'config\alpha_automation.json'
        $obj = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
        $decoyRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("alpha_decoy_" + [Guid]::NewGuid().ToString('N').Substring(0,8))
        New-Item -ItemType Directory -Path $decoyRoot | Out-Null
        $obj.project_path = $decoyRoot
        $obj.allowed_working_directory = $decoyRoot
        ($obj | ConvertTo-Json -Depth 5) | Set-Content -LiteralPath $configPath -Encoding UTF8
        try {
            $r = Invoke-RunScript -SandboxRoot $root
            Assert-That ($r.ExitCode -eq 8) "expected exit code 8 for project_path/script-location mismatch, got $($r.ExitCode). stderr: $($r.Stderr)"
        } finally { Remove-Item -LiteralPath $decoyRoot -Recurse -Force -ErrorAction SilentlyContinue }
    } finally { Remove-Sandbox $root }
}

# ===========================================================================
# 3. Claude process exit codes
# ===========================================================================

Test-Case "claude exit code 0, marker CONTINUE, checkpoint touched -> cycle succeeds" {
    $root = New-Sandbox -ConfigOverrides @{ max_cycles = 1 }
    $stateFile = Join-Path $root 'research_log\ALPHA_AUTONOMOUS_STATE.md'
    $env:FAKE_CLAUDE_MARKER = 'CONTINUE'
    $env:FAKE_CLAUDE_TOUCH_STATE = '1'
    $env:FAKE_CLAUDE_STATE_FILE = $stateFile
    try {
        $r = Invoke-RunScript -SandboxRoot $root
        Assert-That ($r.ExitCode -eq 0) "expected exit 0 (max_cycles=1 reached cleanly), got $($r.ExitCode)"
        $log = Get-Content -LiteralPath (Join-Path $root 'research_log\alpha_automation.log') -Raw
        Assert-That ($log -match 'exit_code=0') "expected log to record the claude process's own exit_code=0"
    } finally {
        Remove-Item Env:\FAKE_CLAUDE_MARKER, Env:\FAKE_CLAUDE_TOUCH_STATE, Env:\FAKE_CLAUDE_STATE_FILE -ErrorAction SilentlyContinue
        Remove-Sandbox $root
    }
}

Test-Case "claude exit code non-zero repeatedly -> max_consecutive_failures -> exit 5" {
    $root = New-Sandbox -ConfigOverrides @{ max_cycles = 5; max_consecutive_failures = 2 }
    $env:FAKE_CLAUDE_EXIT_CODE = '17'
    try {
        $r = Invoke-RunScript -SandboxRoot $root
        Assert-That ($r.ExitCode -eq 5) "expected exit 5 (max_consecutive_failures), got $($r.ExitCode)"
        $log = Get-Content -LiteralPath (Join-Path $root 'research_log\alpha_automation.log') -Raw
        Assert-That ($log -match 'max_consecutive_failures reached') "expected log to explain why it stopped"
    } finally {
        Remove-Item Env:\FAKE_CLAUDE_EXIT_CODE -ErrorAction SilentlyContinue
        Remove-Sandbox $root
    }
}

# ===========================================================================
# 4. Markers
# ===========================================================================

Test-Case "marker COMPLETE -> exit 0 even with cycles remaining" {
    $root = New-Sandbox -ConfigOverrides @{ max_cycles = 5 }
    $env:FAKE_CLAUDE_MARKER = 'COMPLETE'
    try {
        $r = Invoke-RunScript -SandboxRoot $root
        Assert-That ($r.ExitCode -eq 0) "expected exit 0 on ALPHA_MISSION_COMPLETE, got $($r.ExitCode)"
        $log = Get-Content -LiteralPath (Join-Path $root 'research_log\alpha_automation.log') -Raw
        Assert-That ($log -match 'ALPHA_MISSION_COMPLETE received') "expected the log to note mission complete"
        $outputs = @(Get-ChildItem (Join-Path $root 'research_log\cycle_output') -Filter '*.stdout.log')
        Assert-That ($outputs.Count -eq 1) "expected exactly 1 cycle to have run before stopping, found $($outputs.Count)"
    } finally { Remove-Item Env:\FAKE_CLAUDE_MARKER -ErrorAction SilentlyContinue; Remove-Sandbox $root }
}

Test-Case "marker BLOCKER -> exit 3" {
    $root = New-Sandbox -ConfigOverrides @{ max_cycles = 5 }
    $env:FAKE_CLAUDE_MARKER = 'BLOCKER'
    try {
        $r = Invoke-RunScript -SandboxRoot $root
        Assert-That ($r.ExitCode -eq 3) "expected exit 3 on ALPHA_IRRECOVERABLE_BLOCKER, got $($r.ExitCode)"
    } finally { Remove-Item Env:\FAKE_CLAUDE_MARKER -ErrorAction SilentlyContinue; Remove-Sandbox $root }
}

Test-Case "marker missing, zero grace -> exit 4 immediately" {
    $root = New-Sandbox -ConfigOverrides @{ max_cycles = 5; max_consecutive_missing_marker = 0 }
    $env:FAKE_CLAUDE_MARKER = 'NONE'
    try {
        $r = Invoke-RunScript -SandboxRoot $root
        Assert-That ($r.ExitCode -eq 4) "expected exit 4 on missing marker, got $($r.ExitCode)"
        $outputs = @(Get-ChildItem (Join-Path $root 'research_log\cycle_output') -Filter '*.stdout.log')
        Assert-That ($outputs.Count -eq 1) "expected the loop to stop after exactly 1 cycle with zero grace, found $($outputs.Count)"
    } finally { Remove-Item Env:\FAKE_CLAUDE_MARKER -ErrorAction SilentlyContinue; Remove-Sandbox $root }
}

Test-Case "marker missing with grace period -> stops after grace exhausted, not immediately" {
    $root = New-Sandbox -ConfigOverrides @{ max_cycles = 5; max_consecutive_missing_marker = 2 }
    $env:FAKE_CLAUDE_MARKER = 'NONE'
    try {
        $r = Invoke-RunScript -SandboxRoot $root
        Assert-That ($r.ExitCode -eq 4) "expected eventual exit 4 once grace is exhausted, got $($r.ExitCode)"
        $outputs = @(Get-ChildItem (Join-Path $root 'research_log\cycle_output') -Filter '*.stdout.log')
        Assert-That ($outputs.Count -eq 2) "expected exactly 2 cycles to run (the configured grace), found $($outputs.Count)"
    } finally { Remove-Item Env:\FAKE_CLAUDE_MARKER -ErrorAction SilentlyContinue; Remove-Sandbox $root }
}

# ===========================================================================
# 5. Checkpoint progress verification
# ===========================================================================

Test-Case "checkpoint updated after CONTINUE -> hash changes, loop proceeds" {
    $root = New-Sandbox -ConfigOverrides @{ max_cycles = 2 }
    $stateFile = Join-Path $root 'research_log\ALPHA_AUTONOMOUS_STATE.md'
    $hashBefore = (Get-FileHash -LiteralPath $stateFile -Algorithm SHA256).Hash
    $env:FAKE_CLAUDE_MARKER = 'CONTINUE'
    $env:FAKE_CLAUDE_TOUCH_STATE = '1'
    $env:FAKE_CLAUDE_STATE_FILE = $stateFile
    try {
        $r = Invoke-RunScript -SandboxRoot $root
        Assert-That ($r.ExitCode -eq 0) "expected clean exit 0 (max_cycles reached), got $($r.ExitCode)"
        $hashAfter = (Get-FileHash -LiteralPath $stateFile -Algorithm SHA256).Hash
        Assert-That ($hashBefore -ne $hashAfter) "expected the checkpoint file hash to change across cycles"
        $outputs = @(Get-ChildItem (Join-Path $root 'research_log\cycle_output') -Filter '*.stdout.log')
        Assert-That ($outputs.Count -eq 2) "expected both configured cycles to run, found $($outputs.Count)"
    } finally {
        Remove-Item Env:\FAKE_CLAUDE_MARKER, Env:\FAKE_CLAUDE_TOUCH_STATE, Env:\FAKE_CLAUDE_STATE_FILE -ErrorAction SilentlyContinue
        Remove-Sandbox $root
    }
}

Test-Case "checkpoint NOT updated after CONTINUE -> fail-closed, exit 6" {
    $root = New-Sandbox -ConfigOverrides @{ max_cycles = 5; max_consecutive_no_progress = 1 }
    $env:FAKE_CLAUDE_MARKER = 'CONTINUE'
    # deliberately do NOT set FAKE_CLAUDE_TOUCH_STATE, so the checkpoint never changes
    try {
        $r = Invoke-RunScript -SandboxRoot $root
        Assert-That ($r.ExitCode -eq 6) "expected exit 6 (no-progress fail-closed), got $($r.ExitCode)"
        $log = Get-Content -LiteralPath (Join-Path $root 'research_log\alpha_automation.log') -Raw
        Assert-That ($log -match 'did not change') "expected log to explain the checkpoint did not change"
    } finally { Remove-Item Env:\FAKE_CLAUDE_MARKER -ErrorAction SilentlyContinue; Remove-Sandbox $root }
}

Test-Case "checkpoint wiped/corrupted -> restored from backup" {
    $root = New-Sandbox -ConfigOverrides @{ max_cycles = 5; max_consecutive_no_progress = 1; backup_state_before_cycle = $true }
    $stateFile = Join-Path $root 'research_log\ALPHA_AUTONOMOUS_STATE.md'
    $originalContent = Get-Content -LiteralPath $stateFile -Raw
    $env:FAKE_CLAUDE_MARKER = 'CONTINUE'
    $env:FAKE_CLAUDE_WIPE_STATE = '1'
    $env:FAKE_CLAUDE_STATE_FILE = $stateFile
    try {
        $r = Invoke-RunScript -SandboxRoot $root
        Assert-That ($r.ExitCode -eq 6) "expected exit 6 (still fail-closed even after restore), got $($r.ExitCode)"
        Assert-That ((Get-Item -LiteralPath $stateFile).Length -gt 0) "expected the checkpoint to be non-empty after restore"
        $restoredContent = Get-Content -LiteralPath $stateFile -Raw
        Assert-That ($restoredContent -eq $originalContent) "expected restored content to match the pre-cycle backup exactly"
        $log = Get-Content -LiteralPath (Join-Path $root 'research_log\alpha_automation.log') -Raw
        Assert-That ($log -match 'restored from backup') "expected log to record the restore action"
    } finally {
        Remove-Item Env:\FAKE_CLAUDE_MARKER, Env:\FAKE_CLAUDE_WIPE_STATE, Env:\FAKE_CLAUDE_STATE_FILE -ErrorAction SilentlyContinue
        Remove-Sandbox $root
    }
}

# ===========================================================================
# 6. Limits: cycles, runtime, log rotation, dry-run
# ===========================================================================

Test-Case "max_cycles enforced -> exactly N cycles run, then clean exit 0" {
    $root = New-Sandbox -ConfigOverrides @{ max_cycles = 3 }
    $stateFile = Join-Path $root 'research_log\ALPHA_AUTONOMOUS_STATE.md'
    $env:FAKE_CLAUDE_MARKER = 'CONTINUE'
    $env:FAKE_CLAUDE_TOUCH_STATE = '1'
    $env:FAKE_CLAUDE_STATE_FILE = $stateFile
    try {
        $r = Invoke-RunScript -SandboxRoot $root
        Assert-That ($r.ExitCode -eq 0) "expected exit 0, got $($r.ExitCode)"
        $outputs = @(Get-ChildItem (Join-Path $root 'research_log\cycle_output') -Filter '*.stdout.log')
        Assert-That ($outputs.Count -eq 3) "expected exactly 3 cycles, found $($outputs.Count)"
        $log = Get-Content -LiteralPath (Join-Path $root 'research_log\alpha_automation.log') -Raw
        Assert-That ($log -match 'reason=max_cycles') "expected stop reason max_cycles in the log"
    } finally {
        Remove-Item Env:\FAKE_CLAUDE_MARKER, Env:\FAKE_CLAUDE_TOUCH_STATE, Env:\FAKE_CLAUDE_STATE_FILE -ErrorAction SilentlyContinue
        Remove-Sandbox $root
    }
}

Test-Case "max_runtime_minutes=0 -> stops before any cycle runs" {
    $root = New-Sandbox -ConfigOverrides @{ max_cycles = 5; max_runtime_minutes = 0 }
    $env:FAKE_CLAUDE_CALL_LOG = Join-Path $root 'research_log\call.log'
    try {
        $r = Invoke-RunScript -SandboxRoot $root
        Assert-That ($r.ExitCode -eq 0) "expected clean exit 0, got $($r.ExitCode)"
        Assert-That (-not (Test-Path (Join-Path $root 'research_log\call.log'))) "expected zero cycles to run when max_runtime_minutes=0"
        $log = Get-Content -LiteralPath (Join-Path $root 'research_log\alpha_automation.log') -Raw
        Assert-That ($log -match 'reason=max_runtime') "expected stop reason max_runtime in the log"
    } finally { Remove-Item Env:\FAKE_CLAUDE_CALL_LOG -ErrorAction SilentlyContinue; Remove-Sandbox $root }
}

Test-Case "log rotation kicks in past log_max_size_mb" {
    $root = New-Sandbox -ConfigOverrides @{ max_cycles = 3; log_max_size_mb = 0.0005 }
    $stateFile = Join-Path $root 'research_log\ALPHA_AUTONOMOUS_STATE.md'
    $env:FAKE_CLAUDE_MARKER = 'CONTINUE'
    $env:FAKE_CLAUDE_TOUCH_STATE = '1'
    $env:FAKE_CLAUDE_STATE_FILE = $stateFile
    try {
        $r = Invoke-RunScript -SandboxRoot $root
        Assert-That ($r.ExitCode -eq 0) "expected exit 0, got $($r.ExitCode)"
        $rotated = Join-Path $root 'research_log\alpha_automation.log.1'
        Assert-That (Test-Path -LiteralPath $rotated) "expected a rotated .log.1 file to exist given a tiny log_max_size_mb"
    } finally {
        Remove-Item Env:\FAKE_CLAUDE_MARKER, Env:\FAKE_CLAUDE_TOUCH_STATE, Env:\FAKE_CLAUDE_STATE_FILE -ErrorAction SilentlyContinue
        Remove-Sandbox $root
    }
}

Test-Case "dry-run never invokes claude" {
    $root = New-Sandbox -ConfigOverrides @{ max_cycles = 3; dry_run = $true }
    $env:FAKE_CLAUDE_CALL_LOG = Join-Path $root 'research_log\call.log'
    try {
        $r = Invoke-RunScript -SandboxRoot $root
        Assert-That ($r.ExitCode -eq 0) "expected exit 0, got $($r.ExitCode)"
        Assert-That (-not (Test-Path (Join-Path $root 'research_log\call.log'))) "dry-run must never actually invoke claude"
        $dryFiles = @(Get-ChildItem (Join-Path $root 'research_log\cycle_output') -Filter '*.dryrun.txt')
        Assert-That ($dryFiles.Count -eq 3) "expected 3 dry-run artifact files (one per configured cycle), found $($dryFiles.Count)"
    } finally { Remove-Item Env:\FAKE_CLAUDE_CALL_LOG -ErrorAction SilentlyContinue; Remove-Sandbox $root }
}

# ===========================================================================
# 7. Lock/PID cleanup contract (the same finally-block structure that handles Ctrl+C)
# ===========================================================================

Test-Case "lock+pid cleanup happens via finally even when the try block throws" {
    $root = New-Sandbox
    $lockPath = Join-Path $root 'research_log\ALPHA_AUTOMATION.lock'
    $pidPath = Join-Path $root 'research_log\ALPHA_AUTOMATION.pid'
    $lockStream = Lock-AlphaAutomation -LockPath $lockPath -PidPath $pidPath
    Assert-That ($null -ne $lockStream) "test setup failed acquiring lock"
    Assert-That (Test-Path -LiteralPath $lockPath) "lock file should exist while held"
    Assert-That (Test-Path -LiteralPath $pidPath) "pid file should exist while held"
    try {
        try {
            throw "simulated abrupt termination mid-cycle"
        } finally {
            Unlock-AlphaAutomation -LockStream $lockStream -LockPath $lockPath -PidPath $pidPath
        }
    } catch {
        # expected: we threw on purpose to exercise the finally block
    }
    Assert-That (-not (Test-Path -LiteralPath $lockPath)) "lock file should be removed after the finally block runs, exactly as it is on Ctrl+C in the real script (PowerShell runs finally blocks on pipeline-stop)"
    Assert-That (-not (Test-Path -LiteralPath $pidPath)) "pid file should be removed after the finally block runs"
    Remove-Sandbox $root
}

# ===========================================================================
# Summary
# ===========================================================================

Write-Host "`n==================================================================="
Write-Host "RESULTS: $script:PassCount passed, $script:FailCount failed" -ForegroundColor $(if ($script:FailCount -eq 0) { 'Green' } else { 'Red' })
if ($script:FailCount -gt 0) {
    Write-Host "Failed tests:"
    $script:FailedNames | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
}
Write-Host "==================================================================="

if ($script:FailCount -gt 0) { exit 1 } else { exit 0 }
