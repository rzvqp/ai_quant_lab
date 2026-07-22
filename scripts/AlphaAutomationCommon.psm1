#requires -Version 5.1
<#
Shared helpers for the Alpha Automation orchestration scripts
(run_alpha_automation.ps1, stop_alpha_automation.ps1, tests/Test-AlphaAutomation.ps1).

Kept in one module so config validation, path-safety checks, locking, and logging behave
IDENTICALLY across the run/stop/test scripts instead of drifting between three copies.
#>

Set-StrictMode -Version Latest

$script:RequiredConfigKeys = @(
    'project_path', 'allowed_working_directory', 'claude_command',
    'prompt_file', 'state_file', 'log_file', 'stop_file', 'lock_file', 'pid_file',
    'session_id_file', 'output_directory', 'checkpoint_backup_directory',
    'session_mode', 'output_format', 'permission_mode', 'dangerously_skip_permissions',
    'max_cycles', 'delay_seconds', 'retry_delay_seconds', 'max_consecutive_failures',
    'max_consecutive_missing_marker', 'max_consecutive_no_progress', 'max_runtime_minutes',
    'log_max_size_mb', 'dry_run', 'backup_state_before_cycle', 'require_continue_marker',
    'stop_on_missing_state', 'stop_on_missing_prompt'
)

$script:ValidSessionModes    = @('new', 'resume_id', 'continue')
$script:ValidOutputFormats   = @('text', 'json', 'stream-json')
$script:ValidPermissionModes = @('acceptEdits', 'auto', 'bypassPermissions', 'manual', 'dontAsk', 'plan')

$script:Markers = @{
    Continue = 'ALPHA_CONTINUE_REQUIRED'
    Complete = 'ALPHA_MISSION_COMPLETE'
    Blocker  = 'ALPHA_IRRECOVERABLE_BLOCKER'
}

function ConvertTo-WindowsArgumentString {
    <#
    Builds a single Windows command-line string from an argument array, using the same escaping
    rules .NET's ProcessStartInfo.ArgumentList applies internally (which match CommandLineToArgvW /
    standard argv parsing). Needed because Windows PowerShell 5.1 runs on .NET Framework, which
    only exposes ProcessStartInfo.Arguments (a single pre-escaped string) -- the ArgumentList
    collection property is .NET Core/.NET 5+ only and does not exist here.
    #>
    param([Parameter(Mandatory)][AllowEmptyCollection()][string[]]$ArgumentList)
    $sb = New-Object System.Text.StringBuilder
    foreach ($argument in $ArgumentList) {
        if ($sb.Length -ne 0) { [void]$sb.Append(' ') }
        if ($argument.Length -ne 0 -and ($argument -notmatch '[\s"]')) {
            [void]$sb.Append($argument)
            continue
        }
        [void]$sb.Append('"')
        $idx = 0
        while ($idx -lt $argument.Length) {
            $c = $argument[$idx]; $idx++
            if ($c -eq '\') {
                $numBackslash = 1
                while ($idx -lt $argument.Length -and $argument[$idx] -eq '\') { $numBackslash++; $idx++ }
                if ($idx -eq $argument.Length) {
                    [void]$sb.Append('\', ($numBackslash * 2))
                } elseif ($argument[$idx] -eq '"') {
                    [void]$sb.Append('\', ($numBackslash * 2 + 1))
                    [void]$sb.Append('"')
                    $idx++
                } else {
                    [void]$sb.Append('\', $numBackslash)
                }
            } elseif ($c -eq '"') {
                [void]$sb.Append('\')
                [void]$sb.Append('"')
            } else {
                [void]$sb.Append($c)
            }
        }
        [void]$sb.Append('"')
    }
    return $sb.ToString()
}

function ConvertTo-AbsolutePath {
    param([Parameter(Mandatory)][string]$Base, [Parameter(Mandatory)][string]$PathValue)
    if ([System.IO.Path]::IsPathRooted($PathValue)) {
        return [System.IO.Path]::GetFullPath($PathValue)
    }
    return [System.IO.Path]::GetFullPath((Join-Path -Path $Base -ChildPath $PathValue))
}

function Test-PathInsideRoot {
    param([Parameter(Mandatory)][string]$Path, [Parameter(Mandatory)][string]$Root)
    $normalizedRoot = [System.IO.Path]::GetFullPath($Root).TrimEnd('\', '/')
    $normalizedPath = [System.IO.Path]::GetFullPath($Path).TrimEnd('\', '/')
    return ($normalizedPath -eq $normalizedRoot) -or
           $normalizedPath.StartsWith($normalizedRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)
}

function Import-AlphaConfig {
    <#
    Loads, validates, and resolves the alpha_automation.json config.
    Returns @{ Valid = [bool]; Errors = [string[]]; Config = [pscustomobject] }
    Config (when Valid) has Resolved* absolute-path properties added.
    #>
    param([Parameter(Mandatory)][string]$ConfigPath)

    $errors = New-Object System.Collections.Generic.List[string]

    if (-not (Test-Path -LiteralPath $ConfigPath -PathType Leaf)) {
        $errors.Add("Config file not found: $ConfigPath")
        return @{ Valid = $false; Errors = $errors.ToArray(); Config = $null }
    }

    $raw = Get-Content -LiteralPath $ConfigPath -Raw -Encoding UTF8 -ErrorAction Stop
    try {
        $cfg = $raw | ConvertFrom-Json -ErrorAction Stop
    } catch {
        $errors.Add("Config is not valid JSON: $($_.Exception.Message)")
        return @{ Valid = $false; Errors = $errors.ToArray(); Config = $null }
    }

    foreach ($key in $script:RequiredConfigKeys) {
        if (-not (Get-Member -InputObject $cfg -Name $key -MemberType NoteProperty)) {
            $errors.Add("Missing required config key: $key")
        }
    }
    if ($errors.Count -gt 0) {
        return @{ Valid = $false; Errors = $errors.ToArray(); Config = $null }
    }

    if (-not (Test-Path -LiteralPath $cfg.project_path -PathType Container)) {
        $errors.Add("project_path does not exist or is not a directory: $($cfg.project_path)")
    }
    if ($cfg.session_mode -notin $script:ValidSessionModes) {
        $errors.Add("session_mode must be one of: $($script:ValidSessionModes -join ', ') (got '$($cfg.session_mode)')")
    }
    if ($cfg.output_format -notin $script:ValidOutputFormats) {
        $errors.Add("output_format must be one of: $($script:ValidOutputFormats -join ', ') (got '$($cfg.output_format)')")
    }
    if ($cfg.permission_mode -notin $script:ValidPermissionModes) {
        $errors.Add("permission_mode must be one of: $($script:ValidPermissionModes -join ', ') (got '$($cfg.permission_mode)')")
    }
    foreach ($intKey in @('max_cycles', 'delay_seconds', 'retry_delay_seconds', 'max_consecutive_failures',
                          'max_consecutive_missing_marker', 'max_consecutive_no_progress', 'max_runtime_minutes',
                          'log_max_size_mb')) {
        $val = $cfg.$intKey
        if (-not ($val -is [int] -or $val -is [long] -or $val -is [double] -or $val -is [decimal]) -or [double]$val -lt 0) {
            $errors.Add("$intKey must be a non-negative number (got '$val')")
        }
    }
    if ($cfg.max_cycles -eq 0) {
        $errors.Add("max_cycles must be at least 1 (0 would never run a cycle; use the stop file to halt, not max_cycles=0)")
    }
    foreach ($boolKey in @('dangerously_skip_permissions', 'dry_run', 'backup_state_before_cycle',
                           'require_continue_marker', 'stop_on_missing_state', 'stop_on_missing_prompt')) {
        if ($cfg.$boolKey -isnot [bool]) {
            $errors.Add("$boolKey must be a boolean (got '$($cfg.$boolKey)')")
        }
    }

    if ($errors.Count -gt 0) {
        return @{ Valid = $false; Errors = $errors.ToArray(); Config = $null }
    }

    $root = [System.IO.Path]::GetFullPath($cfg.project_path)
    $allowedRoot = [System.IO.Path]::GetFullPath($cfg.allowed_working_directory)
    if (-not (Test-PathInsideRoot -Path $root -Root $allowedRoot)) {
        $errors.Add("project_path ('$root') is not inside allowed_working_directory ('$allowedRoot')")
        return @{ Valid = $false; Errors = $errors.ToArray(); Config = $null }
    }

    $pathKeys = @('prompt_file', 'state_file', 'log_file', 'stop_file', 'lock_file', 'pid_file',
                  'session_id_file', 'output_directory', 'checkpoint_backup_directory')
    $resolved = @{}
    foreach ($key in $pathKeys) {
        $abs = ConvertTo-AbsolutePath -Base $root -PathValue $cfg.$key
        if (-not (Test-PathInsideRoot -Path $abs -Root $allowedRoot)) {
            $errors.Add("$key resolves outside allowed_working_directory: $abs")
            continue
        }
        $resolved[$key] = $abs
    }
    if ($errors.Count -gt 0) {
        return @{ Valid = $false; Errors = $errors.ToArray(); Config = $null }
    }

    # mcp_config_path is an intentional, documented cross-repo reference (TradingView MCP server
    # config) and is NOT required to be inside allowed_working_directory. Only check it exists if set.
    if ((Get-Member -InputObject $cfg -Name 'mcp_config_path' -MemberType NoteProperty) -and $cfg.mcp_config_path) {
        if (-not (Test-Path -LiteralPath $cfg.mcp_config_path -PathType Leaf)) {
            $errors.Add("mcp_config_path is set but the file does not exist: $($cfg.mcp_config_path)")
        }
    }

    if ($errors.Count -gt 0) {
        return @{ Valid = $false; Errors = $errors.ToArray(); Config = $null }
    }

    foreach ($key in $resolved.Keys) {
        $propName = 'Resolved_' + $key
        Add-Member -InputObject $cfg -MemberType NoteProperty -Name $propName -Value $resolved[$key] -Force
    }
    Add-Member -InputObject $cfg -MemberType NoteProperty -Name 'Resolved_project_path' -Value $root -Force
    Add-Member -InputObject $cfg -MemberType NoteProperty -Name 'Resolved_allowed_working_directory' -Value $allowedRoot -Force

    return @{ Valid = $true; Errors = @(); Config = $cfg }
}

function New-AtomicFile {
    <# Writes $Content to $Path via write-to-temp + Move-Item, so readers never see a partial file. #>
    param([Parameter(Mandatory)][string]$Path, [Parameter(Mandatory)][string]$Content)
    $dir = Split-Path -Path $Path -Parent
    if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    $tmp = "$Path.tmp-$([System.Guid]::NewGuid().ToString('N'))"
    Set-Content -LiteralPath $tmp -Value $Content -Encoding UTF8 -NoNewline
    Move-Item -LiteralPath $tmp -Destination $Path -Force
}

function Get-FileHashSafe {
    param([Parameter(Mandatory)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
}

function Lock-AlphaAutomation {
    <#
    Acquires an exclusive lock via an exclusively-opened FileStream (atomic at the OS level --
    not a Test-Path-then-write race). Returns the FileStream on success, or $null if another
    instance already holds it. Caller must keep the handle alive for the run and call
    Unlock-AlphaAutomation in a finally block.
    #>
    param([Parameter(Mandatory)][string]$LockPath, [Parameter(Mandatory)][string]$PidPath)
    try {
        $dir = Split-Path -Path $LockPath -Parent
        if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
        $stream = [System.IO.File]::Open($LockPath, [System.IO.FileMode]::OpenOrCreate, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
    } catch [System.IO.IOException] {
        return $null
    }
    $pidBytes = [System.Text.Encoding]::UTF8.GetBytes("$PID`n")
    $stream.SetLength(0)
    $stream.Write($pidBytes, 0, $pidBytes.Length)
    $stream.Flush()
    New-AtomicFile -Path $PidPath -Content "$PID"
    return $stream
}

function Unlock-AlphaAutomation {
    param($LockStream, [Parameter(Mandatory)][string]$LockPath, [Parameter(Mandatory)][string]$PidPath)
    if ($null -ne $LockStream) {
        try { $LockStream.Close() } catch {}
        try { $LockStream.Dispose() } catch {}
    }
    Remove-Item -LiteralPath $LockPath -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $PidPath -Force -ErrorAction SilentlyContinue
}

function Test-AlphaLockHeldByLiveProcess {
    <# Best-effort check for stop_alpha_automation.ps1: is the PID in pid_file actually running? #>
    param([Parameter(Mandatory)][string]$PidPath)
    if (-not (Test-Path -LiteralPath $PidPath -PathType Leaf)) { return $false }
    $content = (Get-Content -LiteralPath $PidPath -Raw -ErrorAction SilentlyContinue)
    if (-not $content) { return $false }
    $procId = 0
    if (-not [int]::TryParse($content.Trim(), [ref]$procId)) { return $false }
    return $null -ne (Get-Process -Id $procId -ErrorAction SilentlyContinue)
}

function Invoke-AlphaLogRotation {
    param([Parameter(Mandatory)][string]$LogPath, [Parameter(Mandatory)][double]$MaxSizeMb)
    if (-not (Test-Path -LiteralPath $LogPath -PathType Leaf)) { return }
    $sizeMb = (Get-Item -LiteralPath $LogPath).Length / 1MB
    if ($sizeMb -le $MaxSizeMb) { return }
    $rotated = "$LogPath.1"
    Remove-Item -LiteralPath $rotated -Force -ErrorAction SilentlyContinue
    Move-Item -LiteralPath $LogPath -Destination $rotated -Force
}

function Write-AlphaLog {
    param(
        [Parameter(Mandatory)][string]$LogPath,
        [Parameter(Mandatory)][ValidateSet('DEBUG','INFO','WARN','ERROR','CRITICAL')][string]$Level,
        [Parameter(Mandatory)][string]$Message,
        [double]$MaxSizeMb = 20
    )
    Invoke-AlphaLogRotation -LogPath $LogPath -MaxSizeMb $MaxSizeMb
    $dir = Split-Path -Path $LogPath -Parent
    if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    $line = "[{0:yyyy-MM-ddTHH:mm:ss.fffZ}] [{1}] {2}" -f (Get-Date).ToUniversalTime(), $Level, $Message
    Add-Content -LiteralPath $LogPath -Value $line -Encoding UTF8
    Write-Host $line
}

function Get-AlphaLastMarker {
    <#
    Extracts one of the three known markers from Claude's output. Looks at the LAST non-empty
    line only -- a marker that appears mid-output but not as the final line does not count
    (matches the persistent prompt's explicit contract).
    #>
    param([Parameter(Mandatory)][AllowEmptyString()][string]$Text)
    $lines = $Text -split "`r?`n" | Where-Object { $_.Trim().Length -gt 0 }
    if ($lines.Count -eq 0) { return $null }
    $last = $lines[-1].Trim()
    foreach ($marker in $script:Markers.Values) {
        if ($last -eq $marker) { return $marker }
    }
    return $null
}

function Get-AlphaResultText {
    <#
    Given raw stdout from `claude -p`, extracts the text to scan for a marker, honoring
    output_format. For json/stream-json, parses and pulls the `.result` field (falling back to
    common alternates); for text, returns the raw string unchanged.
    #>
    param([Parameter(Mandatory)][AllowEmptyString()][string]$RawStdout, [Parameter(Mandatory)][string]$OutputFormat)

    if ($OutputFormat -eq 'text') { return $RawStdout }

    if ($OutputFormat -eq 'json') {
        try {
            $obj = $RawStdout | ConvertFrom-Json -ErrorAction Stop
        } catch {
            return $RawStdout
        }
        foreach ($field in @('result', 'message', 'output', 'text')) {
            if (Get-Member -InputObject $obj -Name $field -MemberType NoteProperty -ErrorAction SilentlyContinue) {
                $val = $obj.$field
                if ($val -is [string]) { return $val }
            }
        }
        return $RawStdout
    }

    # stream-json: newline-delimited JSON events; concatenate any text/result fields we find.
    $sb = New-Object System.Text.StringBuilder
    foreach ($line in ($RawStdout -split "`r?`n")) {
        if (-not $line.Trim()) { continue }
        try {
            $evt = $line | ConvertFrom-Json -ErrorAction Stop
        } catch { continue }
        foreach ($field in @('result', 'text')) {
            if ((Get-Member -InputObject $evt -Name $field -MemberType NoteProperty -ErrorAction SilentlyContinue) -and ($evt.$field -is [string])) {
                [void]$sb.AppendLine($evt.$field)
            }
        }
    }
    return $sb.ToString()
}

function Get-AlphaSessionIdFromOutput {
    param([Parameter(Mandatory)][AllowEmptyString()][string]$RawStdout, [Parameter(Mandatory)][string]$OutputFormat)
    if ($OutputFormat -eq 'text') { return $null }
    try {
        if ($OutputFormat -eq 'json') {
            $obj = $RawStdout | ConvertFrom-Json -ErrorAction Stop
            if (Get-Member -InputObject $obj -Name 'session_id' -MemberType NoteProperty -ErrorAction SilentlyContinue) {
                return $obj.session_id
            }
        } else {
            foreach ($line in ($RawStdout -split "`r?`n")) {
                if (-not $line.Trim()) { continue }
                $evt = $line | ConvertFrom-Json -ErrorAction SilentlyContinue
                if ($evt -and (Get-Member -InputObject $evt -Name 'session_id' -MemberType NoteProperty -ErrorAction SilentlyContinue)) {
                    return $evt.session_id
                }
            }
        }
    } catch {}
    return $null
}

Export-ModuleMember -Function `
    Import-AlphaConfig, New-AtomicFile, Get-FileHashSafe, ConvertTo-AbsolutePath, Test-PathInsideRoot, `
    Lock-AlphaAutomation, Unlock-AlphaAutomation, Test-AlphaLockHeldByLiveProcess, `
    Write-AlphaLog, Invoke-AlphaLogRotation, Get-AlphaLastMarker, Get-AlphaResultText, Get-AlphaSessionIdFromOutput, `
    ConvertTo-WindowsArgumentString `
    -Variable Markers
