"""Trasabilitatea codului: commit git + arbore curat (arhitectură §10 pct. 4).

Modul `official` cere arbore git curat. `audit`/`rehearse` permit arbore murdar,
dar înregistrează starea. Git nu citește date de piață; rularea lui e permisă.
Dacă git lipsește, se înregistrează 'unknown' (fail-soft pe metadate, nu pe integritate).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from .. import paths


def _git(args: list[str]) -> str | None:
    try:
        out = subprocess.run(
            ["git", *args], cwd=str(paths.LAB_ROOT),
            capture_output=True, text=True, timeout=15,
        )
        if out.returncode != 0:
            return None
        return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def capture() -> dict:
    commit = _git(["rev-parse", "HEAD"])
    status = _git(["status", "--porcelain"])
    tree_clean = (status == "") if status is not None else None
    return {
        "git_commit": commit or "unknown",
        "tree_clean": tree_clean,
        "root": str(Path(paths.LAB_ROOT)),
    }
