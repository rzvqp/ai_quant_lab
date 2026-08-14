# Reproducible install of the ISOLATED ve_tower venv. Never touches the AI Trader main venv (venv/).
#
# What this does, in order:
#   1. Ensures a Python >=3.12 interpreter exists (via the official `py install` manager -- signature
#      verified against python.org's own index; installs 3.12.10 if no 3.12+ interpreter is present).
#   2. Creates the venv at $TowerVenvPath (default: sibling to this repo, OUTSIDE it).
#   3. Installs numpy/pandas from requirements.lock with --require-hashes (fails closed on any hash
#      mismatch -- this is the SHA-256-verified, reproducible dependency install the mandate requires).
#   4. Non-editable installs the ve-tower-worker package itself (`pip install --no-deps .` against
#      tower_worker/, this script's own parent directory) -- builds a real wheel and installs it into the
#      venv's site-packages, so the installed entrypoint never points back at this repo on disk.
#
# Does NOT install ve_tower itself -- see README.md for that step, gated on TOWER_HANDOFF_PASS.

param(
    [string]$TowerVenvPath = "C:\Users\MEDION GAMING\ve_tower_venv"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TowerWorkerRoot = Split-Path -Parent $ScriptDir

Write-Host "=== Step 1: ensure Python >=3.12 is installed ==="
$existing312 = py -0p 2>&1 | Select-String -Pattern "3\.1[2-9]|3\.[2-9][0-9]"
if (-not $existing312) {
    Write-Host "No Python >=3.12 found -- installing 3.12 via the official install manager."
    py install 3.12 -y
} else {
    Write-Host "Found existing Python >=3.12: $existing312"
}

Write-Host "=== Step 2: create/recreate the isolated tower venv at $TowerVenvPath ==="
if (Test-Path $TowerVenvPath) {
    Write-Host "Existing venv found at $TowerVenvPath -- leaving it in place (use rollback_tower_env.ps1 first for a clean rebuild)."
} else {
    & "$env:LOCALAPPDATA\Python\pythoncore-3.12-64\python.exe" -m venv $TowerVenvPath
}

$TowerPython = Join-Path $TowerVenvPath "Scripts\python.exe"

Write-Host "=== Step 3: install pinned, hash-verified dependencies ==="
& $TowerPython -m pip install --upgrade pip -q
& $TowerPython -m pip install --require-hashes -r (Join-Path $ScriptDir "requirements.lock")

Write-Host "=== Step 4: non-editable install of ve-tower-worker itself ==="
Push-Location $TowerWorkerRoot
& $TowerPython -m pip install --no-deps .
Pop-Location

Write-Host "=== Done. Verify with: & '$TowerVenvPath\Scripts\pip.exe' freeze ==="
Write-Host "ve_tower itself is NOT installed -- see README.md for the post-TOWER_HANDOFF_PASS procedure."
