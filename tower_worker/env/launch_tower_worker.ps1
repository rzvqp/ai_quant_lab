# Isolated launch for the ve_tower worker -- CEO mandate section 2. Every bullet point implemented
# explicitly, not left to defaults:
#
#   "interpreterul venv-ului dedicat"        -> $TowerPython, never the AI Trader main venv's python.exe
#   "mod izolat -- python -I"                -> -I passed explicitly
#   "PYTHONPATH ignorat sau golit"           -> -I already makes the interpreter ignore PYTHONPATH, but we
#                                                ALSO clear the env var itself before spawning -- defense in
#                                                depth, the same "don't rely on a single check" discipline
#                                                startup_audit.py's own docstring uses.
#   "working directory IN AFARA repo-ului"   -> $RunDir, a sibling of the tower venv, never inside the repo
#   "entrypoint INSTALAT in venv, nu script
#    importat accidental din repo"           -> `-m ve_tower_worker.cli` resolves the module from the
#                                                TOWER VENV'S OWN site-packages (installed there by
#                                                install_tower_env.ps1's non-editable `pip install .`) --
#                                                under -I, sys.path for `-m` resolution is limited to the
#                                                venv's site-packages and the stdlib, never PYTHONPATH,
#                                                never a repo-relative path. This is a stronger guarantee
#                                                than invoking the pip-generated .exe launcher shim, which
#                                                does not accept interpreter flags like -I.
#   "audit sys.path la pornire"              -> performed by the module itself, first thing in
#                                                `ve_tower_worker.cli.main()` -- see startup_audit.py.
#
# On any startup-audit failure, `cli.main()` prints "TOWER_WORKER_STARTUP_FAILED: ..." to stderr and exits
# 1 -- this script propagates that exit code unchanged so a calling process (or the client's own health
# check) sees the failure.

param(
    [string]$TowerVenvPath = "C:\Users\MEDION GAMING\ve_tower_venv",
    [string]$RunDir = "C:\Users\MEDION GAMING\ve_tower_venv\run",
    [string]$BindHost = "127.0.0.1",
    [int]$Port = 8765
)

$ErrorActionPreference = "Stop"
$TowerPython = Join-Path $TowerVenvPath "Scripts\python.exe"

if (-not (Test-Path $TowerPython)) {
    Write-Error "Tower venv python not found at $TowerPython -- run install_tower_env.ps1 first."
    exit 1
}
if (-not (Test-Path $RunDir)) {
    New-Item -ItemType Directory -Force -Path $RunDir | Out-Null
}

# Clear PYTHONPATH explicitly (defense in depth alongside -I's own PYTHONPATH-ignoring behavior).
$env:PYTHONPATH = $null

Push-Location $RunDir
try {
    & $TowerPython -I -m ve_tower_worker.cli --host $BindHost --port $Port
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
