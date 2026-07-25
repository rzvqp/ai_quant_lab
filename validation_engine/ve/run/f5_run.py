"""Bundle-uri F5 marcate — CALIBRATION vs OFFICIAL. Reutilizează infrastructura F3.

Fiecare bundle poartă în manifest `mode` (CALIBRATION | OFFICIAL) și `official`
(bool), astfel încât un rezultat de calibrare să nu poată fi confundat cu unul oficial.
"""

from __future__ import annotations

import json
from pathlib import Path

from .. import paths
from ..audit import checksums, ledger, repo_integrity
from ..calibration.reproduce_obs0012 import reproduce
from ..manifest import environment
from .matched_null_official import official_run

ENGINE_VERSION = "ve-0.5.0-F5"


def _write(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def _bundle(result: dict, mode: str, official: bool, run_id: str, timestamp: str,
            runs_dir: Path, ledger_jsonl: Path | None, ledger_md: Path | None) -> Path:
    runs_dir.mkdir(parents=True, exist_ok=True)
    before = repo_integrity.snapshot()
    bundle = runs_dir / f"{run_id}__matched_null__{mode.lower()}"
    bundle.mkdir(parents=True, exist_ok=False)

    _write(bundle / "RESULT.json", result)
    _write(bundle / "environment.json", environment.capture())
    after = repo_integrity.snapshot()
    integ = repo_integrity.compare(before, after)

    _write(bundle / "MANIFEST.json", {
        "run_id": run_id, "engine_version": ENGINE_VERSION,
        "mode": mode, "official": official,
        "method": "matched_null@v1", "method_calibration_status": "UNVALIDATED",
        "phase": "F5",
        "warning": ("CALIBRATION — NON-OFFICIAL: reproducere a implementării istorice Alpha "
                    "(obs0012). NU este rezultat de protocol." if not official else
                    "OFFICIAL — rezultat in-sample cu parametrii DC-0004; metoda UNVALIDATED "
                    "până la F6, deci provizoriu."),
        "sealed_window_touched": result.get("sealed_window_touched"),
        "max_ts_read": result.get("max_ts_read"),
        "execution": {"methods_executed": 1, "method": "matched_null@v1"},
        "environment": environment.capture(),
        "repo_integrity": {"external_writes": integ["external_writes"],
                           "hash_before": integ["hash_before"], "hash_after": integ["hash_after"]},
        "replay_command": f"python -m ve verify --run {bundle}",
    })
    checksums.write_checksums(bundle)
    ledger.append({
        "run_id": run_id, "finished_at": timestamp, "mode": mode, "official": official,
        "status": "EXECUTED", "external_writes": integ["external_writes"],
        "sealed_window_touched": result.get("sealed_window_touched"),
        "bundle_sha256": checksums.bundle_sha256(bundle), "bundle_dir": str(bundle),
    }, jsonl=ledger_jsonl, md=ledger_md)
    return bundle


def calibration_bundle(*, runs_dir=None, run_id="VE-F5-CAL", timestamp="1970-01-01T00:00:00Z",
                       ledger_jsonl=None, ledger_md=None):
    return _bundle(reproduce(), "CALIBRATION", False, run_id, timestamp,
                   runs_dir or paths.RUNS_DIR, ledger_jsonl, ledger_md)


def official_bundle(*, runs_dir=None, run_id="VE-F5-OFF", timestamp="1970-01-01T00:00:00Z",
                    ledger_jsonl=None, ledger_md=None):
    return _bundle(official_run(), "OFFICIAL", True, run_id, timestamp,
                   runs_dir or paths.RUNS_DIR, ledger_jsonl, ledger_md)
