"""Rularea de AUDIT (F3) — produce bundle + manifest + checksums + ledger, FĂRĂ
să execute nicio metodă statistică și FĂRĂ să atingă date de piață.

Fluxul (subset F3 al arhitecturii §4):
  0. Intake       — primește specificația, calculează spec_sha256, alocă run_id
  1-3. Validare   — formă + vocabular (F2), sub garda de acces la date
  5. PRE-MANIFEST — scris înainte de orice altă operație (write-once)
  11. Manifest    — final: mediu, cod, semințe derivate, integritate repo
  +. Checksums, ledger append-only

Execuția testelor (faza 8) și stratul de date NU sunt implementate aici — aparțin
fazelor F4/F5+. O rulare de audit este, prin construcție, o „rulare goală": nu
deschide nicio sursă de date. Garda de acces o dovedește mecanic.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .. import paths
from ..audit import access_audit, checksums, ledger, repo_integrity
from ..manifest import code_snapshot, environment
from ..rng import streams
from ..spec.loader import load_spec
from ..spec.validate import validate_spec_object

ENGINE_VERSION = "ve-0.3.0-F3"


@dataclass
class RunResult:
    run_id: str
    bundle_dir: Path
    status: str            # COMPLETED | HALTED | ERROR
    spec_sha256: str | None
    data_accesses: list
    external_writes: int
    manifest_path: Path


def _write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def audit_run(
    spec_path: str | Path,
    *,
    runs_dir: Path | None = None,
    run_id: str | None = None,
    timestamp: str = "1970-01-01T00:00:00Z",
    mode: str = "audit",
    ledger_jsonl: Path | None = None,
    ledger_md: Path | None = None,
) -> RunResult:
    """Execută o rulare de audit. `timestamp`/`run_id` sunt injectabile (determinism în teste)."""
    runs_dir = runs_dir or paths.RUNS_DIR
    runs_dir.mkdir(parents=True, exist_ok=True)

    # Integritate: instantaneu ÎNAINTE (exclude runs/, deci bundle-ul nu contează).
    before = repo_integrity.snapshot()

    # --- Fazele 0-3 sub garda de acces la date (interdicție) --------------------
    with access_audit.recording(forbid_data=True) as record:
        try:
            spec, spec_sha = load_spec(spec_path)
            loaded_ok = True
        except Exception:  # SpecHalt sau eroare de citire a specificației
            spec, spec_sha, loaded_ok = None, None, False
        if loaded_ok:
            result = validate_spec_object(spec, spec_sha256=spec_sha)
        else:
            result = None

    candidate_id = (spec or {}).get("candidate", {}).get("id") if spec else None
    freeze_hash = (spec or {}).get("candidate", {}).get("freeze_hash") if spec else None

    rid = run_id or f"VE-RUN-{timestamp.replace(':', '').replace('-', '')}-{(spec_sha or '0'*8)[:8]}"
    bundle_dir = runs_dir / f"{rid}__{candidate_id or 'unknown'}__{mode}"
    bundle_dir.mkdir(parents=True, exist_ok=False)  # write-once: nu suprascrie
    (bundle_dir / "logs").mkdir()

    status = "COMPLETED" if (result and result.status == "PASSED") else "HALTED"

    # --- Faza 5: PRE-MANIFEST (înainte de orice altceva în bundle) -------------
    pre_manifest = {
        "run_id": rid, "engine_version": ENGINE_VERSION, "mode": mode,
        "phase": "F3-audit (no execution, no data)",
        "spec": {"path": str(spec_path), "sha256": spec_sha,
                 "candidate_id": candidate_id, "freeze_hash": freeze_hash},
        "started_at": timestamp,
        "note": "Rulare de audit: validează și sigilează metadatele. NU execută metode. NU atinge date.",
    }
    _write_json(bundle_dir / "PRE_MANIFEST.json", pre_manifest)

    # copie bit-identică a specificației (dacă a putut fi încărcată)
    if spec is not None:
        _write_json(bundle_dir / "SPEC_RECEIVED.json", spec)

    # rezultatul validării
    validation = {
        "status": result.status if result else "LOAD_FAILED",
        "stage_reached": result.stage_reached if result else 0,
        "codes": result.codes if result else [],
        "errors": [
            {"code": e.code, "field_path": e.field_path, "reason": e.reason}
            for e in (result.errors if result else [])
        ],
        "files_opened_during_validation": len(result.files_opened) if result else 0,
        "data_accesses": result.data_accesses if result else [],
    }
    _write_json(bundle_dir / "VALIDATION.json", validation)

    # semințe derivate — DOAR dacă validarea a trecut (spec bine-formată); pur hashing
    seeds = None
    if result and result.status == "PASSED":
        test_ids = [t.get("test_id") for t in spec.get("tests", [])]
        seeds = streams.derive_seeds(spec_sha, test_ids)
        _write_json(bundle_dir / "seeds.json", seeds)

    _write_json(bundle_dir / "environment.json", environment.capture())

    (bundle_dir / "logs" / "run.log").write_text(
        f"[{timestamp}] {rid} mode={mode} status={status} "
        f"data_accesses={len(validation['data_accesses'])}\n",
        encoding="utf-8",
    )

    # --- Integritate: instantaneu DUPĂ, comparație --------------------------------
    after = repo_integrity.snapshot()
    integrity = repo_integrity.compare(before, after)

    # --- Faza 11: MANIFEST final -------------------------------------------------
    manifest = {
        "run_id": rid, "engine_version": ENGINE_VERSION, "mode": mode,
        "status": status,
        "phase": "F3-audit",
        "capability_registry_version": (spec or {}).get("capability_registry_version"),
        "code": code_snapshot.capture(),
        "spec": {"sha256": spec_sha, "candidate_id": candidate_id, "freeze_hash": freeze_hash},
        "validation": {"status": validation["status"], "codes": validation["codes"]},
        "data": {
            "policy": "F3 audit run does not open data files; hashes are taken from the "
                      "specification's declared values, not computed. File-level verification is F4.",
            "declared_inputs": [
                {"source_id": d.get("source_id"), "declared_sha256": d.get("sha256")}
                for d in (spec or {}).get("data", [])
            ],
            "sealed_resources_touched": [],
            "data_accesses": len(validation["data_accesses"]),
        },
        "seeds": seeds,
        "execution": {
            "started_at": timestamp, "finished_at": timestamp,
            "methods_executed": 0,
            "note": "Nicio metodă executată (F3). Execuția aparține F5+.",
        },
        "environment": environment.capture(),
        "repo_integrity": {
            "hash_before": integrity["hash_before"],
            "hash_after": integrity["hash_after"],
            "external_writes": integrity["external_writes"],
        },
        "replay_command": f"python -m ve verify --run {bundle_dir}",
    }
    manifest_path = bundle_dir / "MANIFEST.json"
    _write_json(manifest_path, manifest)

    # --- Checksums peste tot bundle-ul (ultimul fișier scris) --------------------
    checksums.write_checksums(bundle_dir)
    bundle_hash = checksums.bundle_sha256(bundle_dir)

    # --- Ledger append-only ------------------------------------------------------
    ledger.append({
        "run_id": rid, "finished_at": timestamp, "candidate_id": candidate_id,
        "spec_sha256": spec_sha, "status": status,
        "data_accesses": len(validation["data_accesses"]),
        "external_writes": integrity["external_writes"],
        "bundle_sha256": bundle_hash, "bundle_dir": str(bundle_dir),
    }, jsonl=ledger_jsonl, md=ledger_md)

    return RunResult(
        run_id=rid, bundle_dir=bundle_dir, status=status, spec_sha256=spec_sha,
        data_accesses=validation["data_accesses"], external_writes=integrity["external_writes"],
        manifest_path=manifest_path,
    )
