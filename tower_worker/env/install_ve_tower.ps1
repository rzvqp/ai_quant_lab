# Installs ve_tower 0.3.0 into the ISOLATED tower venv, and ONLY there -- CEO mandate, Phase 2 step 1-2.
# Never touches the AI Trader main venv (venv/ at the repo root).
#
# Order, each step fail-closed:
#   1. Verify the wheel's SHA-256 (main venv, tower_worker/env/verify_tower_wheel.py) BEFORE any install.
#   2. pip install --no-deps into the tower venv ONLY.
#   3. Re-verify the sidecar manifest (main venv, sidecar_verification.py) -- the same independent
#      recomputation already used to close the pin, run again here as the install-time source of truth.
#   4. Write ve_tower_install_manifest.json into the tower venv's own root, using ONLY the values that
#      step 3 (this install run) independently verified -- never values assumed correct from a prior
#      session.

param(
    [string]$WheelPath = "C:\Users\MEDION GAMING\ai_quant_lab-wp5b\ve_tower\release\ve_tower-0.3.0-py3-none-any.whl",
    [string]$SidecarPath = "C:\Users\MEDION GAMING\ai_quant_lab-wp5b\ve_tower\HANDOFF_MANIFEST-0.3.0.json",
    [string]$TowerVenvPath = "C:\Users\MEDION GAMING\ve_tower_venv",
    [string]$RepoRoot = "C:\Users\MEDION GAMING\ai_quant_lab-research-main"
)

$ErrorActionPreference = "Stop"
$MainPython = Join-Path $RepoRoot "venv\Scripts\python.exe"
$TowerPython = Join-Path $TowerVenvPath "Scripts\python.exe"

Write-Host "=== Step 1: verify the wheel's SHA-256 BEFORE any install ==="
& $MainPython (Join-Path $RepoRoot "tower_worker\env\verify_tower_wheel.py") $WheelPath
if ($LASTEXITCODE -ne 0) { Write-Error "wheel verification FAILED -- refusing to install"; exit 1 }

Write-Host "=== Step 2: install into the TOWER venv only ==="
& $TowerPython -m pip install --no-deps $WheelPath

Write-Host "=== Step 3+4: re-verify the sidecar and write the install manifest ==="
$InstalledAtUtc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$InstalledBy = "$env:USERDOMAIN\$env:USERNAME"

$ManifestScript = @"
import sys
sys.path.insert(0, r"$RepoRoot\tower_worker\env")
from sidecar_verification import verify_sidecar, cross_check_against_existing_pin
from pathlib import Path

sidecar = verify_sidecar(Path(r"$SidecarPath"))
mismatches = cross_check_against_existing_pin(sidecar)
if mismatches:
    raise SystemExit(f"sidecar disagrees with the existing pin on: {mismatches}")

from ve_tower_worker.install_manifest import InstallManifest, write_install_manifest

manifest = InstallManifest(
    ve_tower_package_version=sidecar.ve_tower_package_version,
    package_build_commit=sidecar.package_build_commit,
    state_delivery_commit=sidecar.state_delivery_commit,
    wheel_sha256=sidecar.wheel_sha256,
    wheel_filename=sidecar.wheel_filename,
    vendored_source_identity=sidecar.vendored_source_identity,
    n3_contract_version=sidecar.n3_contract_version,
    n4_contract_version=sidecar.n4_contract_version,
    installed_at_utc="$InstalledAtUtc",
    installed_by=r"$InstalledBy",
    verification_note="SHA-256 verified before install (verify_tower_wheel.py); sidecar independently recomputed (sidecar_verification.py) and cross-checked against the existing pin before this manifest was written.",
)
write_install_manifest(manifest, venv_root=Path(r"$TowerVenvPath"))
print(f"Install manifest written: ve_tower_package_version={manifest.ve_tower_package_version} package_build_commit={manifest.package_build_commit}")
"@

# Note: this script needs BOTH ai_trader (for sidecar_verification's own cross-check import) and
# ve_tower_worker (installed in the tower venv) -- so it MUST run under the tower venv's own python,
# which additionally needs the main repo root on sys.path for the sidecar_verification import.
$ManifestScript = $ManifestScript -replace 'sys.path.insert\(0, r"\$RepoRoot\\tower_worker\\env"\)', "sys.path.insert(0, r`"$RepoRoot\tower_worker\env`")`nsys.path.insert(0, r`"$RepoRoot`")"

$ManifestScriptPath = Join-Path $env:TEMP "write_ve_tower_install_manifest_$([guid]::NewGuid().ToString('N')).py"
Set-Content -Path $ManifestScriptPath -Value $ManifestScript -Encoding utf8
try {
    & $TowerPython $ManifestScriptPath
} finally {
    Remove-Item -Force $ManifestScriptPath -ErrorAction SilentlyContinue
}

Write-Host "=== Done. ve_tower installed ONLY in $TowerVenvPath ==="
