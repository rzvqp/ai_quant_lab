"""Verificarea unui bundle existent — fără date, fără execuție.

Re-calculează checksums-urile și le compară cu CHECKSUMS.sha256; confirmă
coerența internă a manifestului. O alterare de un bit produce MISMATCH.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..audit import checksums

REQUIRED_FILES = ("MANIFEST.json", "PRE_MANIFEST.json", "CHECKSUMS.sha256")
REQUIRED_MANIFEST_FIELDS = (
    "run_id", "engine_version", "status", "repo_integrity", "environment", "replay_command",
)


def verify_bundle(bundle_dir: str | Path) -> dict:
    bundle = Path(bundle_dir)
    problems: list[str] = []

    if not bundle.is_dir():
        return {"status": "MISMATCH", "problems": [f"directorul nu există: {bundle}"]}

    for name in REQUIRED_FILES:
        if not (bundle / name).exists():
            problems.append(f"fișier obligatoriu absent: {name}")

    check = checksums.verify_checksums(bundle)

    manifest = None
    mpath = bundle / "MANIFEST.json"
    if mpath.exists():
        try:
            manifest = json.loads(mpath.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            problems.append(f"MANIFEST.json invalid: {exc}")
    if manifest is not None:
        for field in REQUIRED_MANIFEST_FIELDS:
            if field not in manifest:
                problems.append(f"câmp de manifest absent: {field}")
        ew = manifest.get("repo_integrity", {}).get("external_writes")
        if ew not in (0, None):
            problems.append(f"external_writes != 0 în manifest: {ew}")

    status = "EXACT" if (check["status"] == "EXACT" and not problems) else "MISMATCH"
    return {
        "status": status,
        "checksums": check,
        "problems": problems,
        "manifest_status": manifest.get("status") if manifest else None,
        "external_writes": manifest.get("repo_integrity", {}).get("external_writes") if manifest else None,
    }
