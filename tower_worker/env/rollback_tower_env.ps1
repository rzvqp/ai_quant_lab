# Rollback for the ISOLATED ve_tower venv. Trivial by construction: the venv is a fully separate
# directory tree, never referenced from the AI Trader main venv or repo, so rollback is deleting it --
# there is no shared state to unwind, no package in the main venv to restore, nothing to reconcile.
#
# Does NOT uninstall the Python 3.12 interpreter itself (a separate, lower-blast-radius asset that other
# tooling could reasonably depend on later) -- only the venv this script's sibling installer created.

param(
    [string]$TowerVenvPath = "C:\Users\MEDION GAMING\ve_tower_venv"
)

$ErrorActionPreference = "Stop"

if (Test-Path $TowerVenvPath) {
    Write-Host "Removing $TowerVenvPath ..."
    Remove-Item -Recurse -Force -Confirm:$false $TowerVenvPath
    Write-Host "Done. The AI Trader main venv was never touched by this venv's existence or removal."
} else {
    Write-Host "$TowerVenvPath does not exist -- nothing to roll back."
}
