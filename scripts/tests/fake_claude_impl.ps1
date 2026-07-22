#requires -Version 5.1
<#
Simulated `claude -p` process for tests. Reads and discards stdin (the real CLI reads the prompt
from stdin the same way), then behaves according to environment variables set by the test
harness. Never used outside scripts\tests\Test-AlphaAutomation.ps1.
#>
Set-StrictMode -Version Latest

$stdin = [Console]::In.ReadToEnd()

if ($env:FAKE_CLAUDE_CALL_LOG) {
    Add-Content -LiteralPath $env:FAKE_CLAUDE_CALL_LOG -Value "call at $((Get-Date).ToUniversalTime().ToString('o')), stdin_len=$($stdin.Length)" -Encoding UTF8
}

if ($env:FAKE_CLAUDE_SLEEP_MS) {
    Start-Sleep -Milliseconds ([int]$env:FAKE_CLAUDE_SLEEP_MS)
}

$exitCode = 0
if ($env:FAKE_CLAUDE_EXIT_CODE) { $exitCode = [int]$env:FAKE_CLAUDE_EXIT_CODE }

if ($exitCode -ne 0) {
    [Console]::Error.WriteLine("fake_claude: simulated non-zero exit ($exitCode)")
    exit $exitCode
}

if ($env:FAKE_CLAUDE_WIPE_STATE -eq '1' -and $env:FAKE_CLAUDE_STATE_FILE) {
    Set-Content -LiteralPath $env:FAKE_CLAUDE_STATE_FILE -Value '' -NoNewline -Encoding UTF8
}
elseif ($env:FAKE_CLAUDE_TOUCH_STATE -eq '1' -and $env:FAKE_CLAUDE_STATE_FILE) {
    Add-Content -LiteralPath $env:FAKE_CLAUDE_STATE_FILE -Value "`n<!-- fake-claude touched this checkpoint at $((Get-Date).ToUniversalTime().ToString('o')) -->" -Encoding UTF8
}

$marker = if ($env:FAKE_CLAUDE_MARKER) { $env:FAKE_CLAUDE_MARKER } else { 'CONTINUE' }
$markerText = switch ($marker) {
    'CONTINUE' { 'ALPHA_CONTINUE_REQUIRED' }
    'COMPLETE' { 'ALPHA_MISSION_COMPLETE' }
    'BLOCKER'  { 'ALPHA_IRRECOVERABLE_BLOCKER' }
    'NONE'     { '' }
    default    { $marker }
}

$resultBody = "Simulated Alpha cycle output.`nStdin length received: $($stdin.Length)"
if ($markerText) { $resultBody += "`n$markerText" }

$obj = [ordered]@{
    type       = 'result'
    subtype    = 'success'
    is_error   = $false
    result     = $resultBody
    session_id = ('fake-session-' + [Guid]::NewGuid().ToString('N').Substring(0, 8))
}
Write-Output ($obj | ConvertTo-Json -Compress)
exit 0
