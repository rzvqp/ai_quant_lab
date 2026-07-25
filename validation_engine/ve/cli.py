"""Interfața de linie de comandă — faza F2.

Sunt disponibile doar `validate` și `capabilities`. Subcomenzile `rehearse`,
`run` și `verify` NU există încă: execuția protocoalelor aparține fazelor F5+.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import clarification, paths
from .spec import registry_validator
from .spec.validate import validate_spec_file

EXIT_PASSED = 0
EXIT_HALTED = 2
EXIT_ENGINE_ERROR = 3


def _cmd_validate(args) -> int:
    result = validate_spec_file(args.spec)
    spec_id = None
    try:
        spec_id = json.loads(Path(args.spec).read_text(encoding="utf-8")).get("spec_id")
    except Exception:
        pass

    print(f"specificație : {args.spec}")
    print(f"hash         : {result.spec_sha256}")
    print(f"etapă atinsă : {result.stage_reached}")
    print(f"status       : {result.status}")
    print(f"fișiere deschise în timpul validării : {len(result.files_opened)}")
    print(f"accesări de date                     : {len(result.data_accesses)}")

    if result.halted:
        print(f"\ncauze ({len(result.errors)}):")
        for err in result.errors:
            print(f"  {err}")
        out_dir = Path(args.out) if args.out else paths.CLARIFICATIONS_DIR
        out_dir.mkdir(parents=True, exist_ok=True)
        target = out_dir / "CLARIFICATION_REQUEST.md"
        target.write_text(clarification.render(result, spec_id=spec_id), encoding="utf-8")
        print(f"\ncerere de clarificare: {target}")
        return EXIT_HALTED

    print("\nSpecificația a trecut validarea de formă și de vocabular.")
    return EXIT_PASSED


def _cmd_run(args) -> int:
    """Rulare de AUDIT (F3): validează + sigilează metadatele. NU execută, NU atinge date."""
    from .run.runner import audit_run

    result = audit_run(args.spec, run_id=args.run_id)
    print(f"run_id       : {result.run_id}")
    print(f"bundle       : {result.bundle_dir}")
    print(f"status       : {result.status}")
    print(f"spec hash    : {result.spec_sha256}")
    print(f"accesări date: {len(result.data_accesses)}")
    print(f"external_writes: {result.external_writes}")
    print(f"manifest     : {result.manifest_path}")
    return EXIT_PASSED if result.external_writes == 0 else EXIT_ENGINE_ERROR


def _cmd_materialize(args) -> int:
    """Materializare (F4): date + populație + variabile. NU execută metode, NU atinge holdout."""
    from .run.materializer import materialize_run

    r = materialize_run(args.spec, run_id=args.run_id)
    print(f"run_id       : {r.run_id}")
    print(f"bundle       : {r.bundle_dir}")
    print(f"status       : {r.status}")
    if r.halt_reason:
        print(f"halt         : {r.halt_reason}")
    print(f"evenimente   : {r.n_events}")
    print(f"holdout atins: {r.sealed_window_touched}")
    print(f"external_writes: {r.external_writes}")
    return EXIT_PASSED if (r.status == "MATERIALIZED" and not r.sealed_window_touched) else EXIT_HALTED


def _cmd_verify(args) -> int:
    from .verify.replay import verify_bundle

    rep = verify_bundle(args.run)
    print(f"bundle : {args.run}")
    print(f"verify : {rep['status']}")
    if rep.get("checksums"):
        print(f"fișiere verificate : {rep['checksums'].get('files_checked')}")
    print(f"external_writes    : {rep.get('external_writes')}")
    for p in rep.get("problems", []):
        print(f"  problemă: {p}")
    for m in rep.get("checksums", {}).get("mismatches", []):
        print(f"  checksum: {m}")
    return EXIT_PASSED if rep["status"] == "EXACT" else EXIT_HALTED


def _cmd_capabilities(args) -> int:
    reg = registry_validator.load_registry()
    ok, bad = registry_validator.registry_domains_are_parseable()
    print(f"registru      : {reg['registry_id']} (v{reg['registry_version']})")
    print(f"status        : {reg['status']}")
    print(f"gramatică     : {'toate domeniile parsabile' if ok else 'DESCRIPTORI NEACOPERIȚI: ' + '; '.join(bad)}")
    for section in ("data_sources", "variable_primitives", "population_predicates",
                    "statistics", "test_methods", "correction_methods"):
        print(f"  {section:24} {len(reg[section]):3}")
    validated = [
        k for s in ("test_methods", "correction_methods")
        for k, v in reg[s].items() if v.get("calibration_status") == "VALIDATED"
    ]
    print(f"metode executabile (VALIDATED): {len(validated)}")
    return EXIT_PASSED


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ve", description="Validation Engine (faza F2)")
    sub = p.add_subparsers(dest="command", required=True)

    v = sub.add_parser("validate", help="validează o specificație (formă + vocabular)")
    v.add_argument("spec", help="calea către specificația .json")
    v.add_argument("--out", help="directorul în care se scrie cererea de clarificare")
    v.set_defaults(func=_cmd_validate)

    r = sub.add_parser("run", help="rulare de audit (F3): manifest + bundle, fără date, fără execuție")
    r.add_argument("spec", help="calea către specificația .json")
    r.add_argument("--run-id", dest="run_id", default=None, help="run_id explicit (implicit: derivat)")
    r.set_defaults(func=_cmd_run)

    m = sub.add_parser("materialize", help="materializare (F4): date + populație + variabile, fără execuție")
    m.add_argument("spec", help="calea către specificația .json")
    m.add_argument("--run-id", dest="run_id", default=None)
    m.set_defaults(func=_cmd_materialize)

    vf = sub.add_parser("verify", help="verifică integritatea unui bundle de rulare")
    vf.add_argument("--run", required=True, help="directorul bundle-ului")
    vf.set_defaults(func=_cmd_verify)

    c = sub.add_parser("capabilities", help="rezumatul registrului de capabilități")
    c.set_defaults(func=_cmd_capabilities)
    return p


def _force_utf8_console() -> None:
    """Consola Windows implicită (cp1252) nu poate scrie diacriticele din rapoarte.

    Ieșirea nu are voie să provoace oprirea motorului, deci fluxurile sunt
    reconfigurate pe UTF-8 înainte de orice afișare.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass


def main(argv: list[str] | None = None) -> int:
    _force_utf8_console()
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:  # defect de motor, nu defect de specificație
        print(f"EROARE DE MOTOR: {exc.__class__.__name__}: {exc}", file=sys.stderr)
        return EXIT_ENGINE_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
