"""Orchestratorul F4 — materializare: validare → date → populație → variabile →
eligibilitate → bundle. NU execută metode statistice. NU atinge holdout-ul.

Materializarea continuă chiar dacă metodele sunt `UNVALIDATED` (nu le rulează), dar
se oprește fail-closed la orice altă eroare (structură, vocabular, hash, fereastră
sigilată, leakage, anomalie de date). Extinde bundle-ul F3.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .. import paths
from ..audit import access_audit, checksums, ledger, repo_integrity
from ..data import calendar, sealing
from ..data.access_journal import AccessJournal
from ..data.integrity import DataIntegrityError
from ..data.sources import DataLoadError, load_open_window
from ..manifest import code_snapshot, environment
from ..population import builder, eligibility
from ..spec.loader import load_spec
from ..spec.validate import validate_spec_object
from ..variables import materialize as var_mat

ENGINE_VERSION = "ve-0.4.0-F4"
_ISO_EPOCH = {"2023-01-01T00:00:00Z": 1672531200}


@dataclass
class MaterializeResult:
    run_id: str
    bundle_dir: Path
    status: str            # MATERIALIZED | HALTED
    halt_reason: str | None
    n_events: int | None
    sealed_window_touched: bool
    external_writes: int


def _iso_to_epoch(iso: str) -> int:
    import datetime
    return int(datetime.datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ")
               .replace(tzinfo=datetime.timezone.utc).timestamp())


def _only_calibration_gate(result) -> bool:
    if result is None:
        return False
    if result.status == "PASSED":
        return True
    for e in result.errors:
        is_calib = (e.code == "E3" and "/method" in e.field_path
                    and ("calibrare" in e.reason or "statusul" in e.reason))
        if not is_calib:
            return False
    return True


def _write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def materialize_run(
    spec_path,
    *,
    runs_dir: Path | None = None,
    run_id: str | None = None,
    timestamp: str = "1970-01-01T00:00:00Z",
    ledger_jsonl: Path | None = None,
    ledger_md: Path | None = None,
) -> MaterializeResult:
    runs_dir = runs_dir or paths.RUNS_DIR
    runs_dir.mkdir(parents=True, exist_ok=True)
    before = repo_integrity.snapshot()

    journal = AccessJournal()
    halt_reason = None
    population = variables_summary = family = None
    n_events = None

    # --- validare (F2) + încărcare + materializare, sub garda de acces (înregistrare) ---
    with access_audit.recording(forbid_data=False) as record:
        try:
            spec, spec_sha = load_spec(spec_path)
            result = validate_spec_object(spec, spec_sha256=spec_sha)
        except Exception as exc:
            spec, spec_sha, result = None, None, None
            halt_reason = f"spec load/validate: {exc}"

        proceed = spec is not None and _only_calibration_gate(result)
        if spec is not None and not proceed:
            halt_reason = halt_reason or "validare oprită (erori în afara porții de calibrare)"

        if proceed:
            try:
                base_src = spec["population"]["source_id"]
                declared = {d["source_id"]: d["sha256"] for d in spec["data"]}
                win = spec["population"]["window"]
                win_start = _iso_to_epoch(win["start"])
                win_end = _iso_to_epoch(win["end"])
                # F4 nu deschide holdout-ul: o fereastră de populație care atinge granița
                # sigilată se oprește aici, indiferent de autorizare (protocolul e F8).
                sealing.assert_open_window(win_end, win["bounds"])

                # încarcă FIECARE sursă pe fereastra ei deschisă (start date → graniță)
                frames = {}
                for sid, sha in declared.items():
                    series = load_open_window(
                        sid, sha, 0, sealing.boundary_epoch() - 1, "[)", journal,
                    )
                    frames[sid] = var_mat.series_to_frame(series)

                base = frames[base_src]
                aux = {k: v for k, v in frames.items() if k != base_src}

                values, variables_summary = var_mat.materialize(
                    spec["variables"], base, aux, base_source_id=base_src)

                # restrânge candidații la fereastra de populație
                in_window = (base["time"] >= win_start) & (base["time"] < win_end)
                base_win = base[in_window]
                # re-aliniază valorile la sub-set
                values_win = {k: v[in_window] for k, v in values.items()}

                population = builder.build(spec["population"], values_win, base_win)
                n_events = population["n_after_cooldown"]
                # min_n la nivel de populație: sub prag → oprire (E6), nu interpretare
                min_n = int(spec["population"].get("min_n", 1))
                if n_events < min_n:
                    raise DataLoadError(
                        f"populația are {n_events} evenimente, sub min_n={min_n} "
                        "(oprire E6 — VE nu rulează pe un eșantion sub prag)")
                family = eligibility.realized_family(
                    spec.get("multiple_testing", {}), spec.get("tests", []),
                    population["event_indices"], values_win, base_win,
                )
            except (DataIntegrityError, DataLoadError, sealing.HoldoutAccessError) as exc:
                proceed = False
                halt_reason = f"{type(exc).__name__}: {exc}"
            except Exception as exc:  # defect de materializare
                proceed = False
                halt_reason = f"materializare: {type(exc).__name__}: {exc}"

    status = "MATERIALIZED" if (proceed and halt_reason is None) else "HALTED"
    candidate_id = (spec or {}).get("candidate", {}).get("id") if spec else None
    rid = run_id or f"VE-RUN-{timestamp.replace(':', '').replace('-', '')}-{(spec_sha or '0'*8)[:8]}"
    bundle_dir = runs_dir / f"{rid}__{candidate_id or 'unknown'}__materialize"
    bundle_dir.mkdir(parents=True, exist_ok=False)
    (bundle_dir / "logs").mkdir()

    # --- PRE-MANIFEST ---
    _write_json(bundle_dir / "PRE_MANIFEST.json", {
        "run_id": rid, "engine_version": ENGINE_VERSION, "mode": "materialize",
        "phase": "F4 (data layer + population + variables; NO method execution)",
        "spec": {"path": str(spec_path), "sha256": spec_sha, "candidate_id": candidate_id},
        "started_at": timestamp,
        "note": "Materializare: încarcă DOAR fereastra deschisă, construiește populația și "
                "variabilele. NU execută metode. NU atinge holdout-ul.",
    })
    if spec is not None:
        _write_json(bundle_dir / "SPEC_RECEIVED.json", spec)
    _write_json(bundle_dir / "VALIDATION.json", {
        "status": result.status if result else "LOAD_FAILED",
        "codes": result.codes if result else [],
        "materialization_proceeded": status == "MATERIALIZED",
        "halt_reason": halt_reason,
        "data_accesses_raw": len(record.data_accesses),
    })
    _write_json(bundle_dir / "ACCESS_JOURNAL.json", journal.to_dict())
    if population is not None:
        _write_json(bundle_dir / "POPULATION.json", population)
    if family is not None:
        _write_json(bundle_dir / "REALIZED_FAMILY.json", family)
    if variables_summary is not None:
        _write_json(bundle_dir / "MATERIALIZATION.json", variables_summary)
    _write_json(bundle_dir / "environment.json", environment.capture())

    max_ts = journal.max_ts_by_source()
    sealed_touched = journal.sealed_window_touched()
    (bundle_dir / "logs" / "run.log").write_text(
        f"[{timestamp}] {rid} status={status} n_events={n_events} "
        f"sealed_touched={sealed_touched} halt={halt_reason}\n", encoding="utf-8")

    after = repo_integrity.snapshot()
    integrity = repo_integrity.compare(before, after)

    # --- MANIFEST ---
    _write_json(bundle_dir / "MANIFEST.json", {
        "run_id": rid, "engine_version": ENGINE_VERSION, "mode": "materialize",
        "status": status, "phase": "F4",
        "halt_reason": halt_reason,
        "capability_registry_version": (spec or {}).get("capability_registry_version"),
        "code": code_snapshot.capture(),
        "spec": {"sha256": spec_sha, "candidate_id": candidate_id},
        "data": {
            "computed_hashes_verified": status == "MATERIALIZED" or "hash" in (halt_reason or ""),
            "max_ts_read_by_source": max_ts,
            "sealed_boundary_epoch": sealing.boundary_epoch(),
            "sealed_window_touched": sealed_touched,
            "data_accesses_raw": len(record.data_accesses),
        },
        "population": None if population is None else {
            "n_events": population["n_after_cooldown"],
            "n_candidates": population["n_candidates"],
        },
        "realized_family": None if family is None else {
            "m_realized": family["m_realized"], "eligible_cells": family["eligible_cells"],
        },
        "execution": {"methods_executed": 0, "note": "Nicio metodă executată (F4). Execuția e F5."},
        "environment": environment.capture(),
        "repo_integrity": {
            "hash_before": integrity["hash_before"], "hash_after": integrity["hash_after"],
            "external_writes": integrity["external_writes"],
        },
        "replay_command": f"python -m ve verify --run {bundle_dir}",
    })

    checksums.write_checksums(bundle_dir)
    bundle_hash = checksums.bundle_sha256(bundle_dir)

    ledger.append({
        "run_id": rid, "finished_at": timestamp, "candidate_id": candidate_id,
        "spec_sha256": spec_sha, "status": status,
        "data_accesses": len(record.data_accesses),
        "external_writes": integrity["external_writes"],
        "sealed_window_touched": sealed_touched,
        "bundle_sha256": bundle_hash, "bundle_dir": str(bundle_dir),
    }, jsonl=ledger_jsonl, md=ledger_md)

    return MaterializeResult(
        run_id=rid, bundle_dir=bundle_dir, status=status, halt_reason=halt_reason,
        n_events=n_events, sealed_window_touched=sealed_touched,
        external_writes=integrity["external_writes"],
    )
