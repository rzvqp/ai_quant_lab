"""Orchestrarea validării: etapa 1 (formă) apoi etapa 2 (vocabular).

Etapa 2 NU rulează dacă etapa 1 a eșuat: pe o structură invalidă, verificarea
vocabularului ar produce erori derivate, care ar îngreuna clarificarea în loc să
o ajute.

Întreaga validare rulează sub garda de acces la date, în regim de INTERDICȚIE:
o încercare de a deschide un fișier de date în timpul validării ridică excepție
și abandonează operațiunea. Garanția „zero accesări de date la E1-E3" este astfel
structurală, nu doar testată.
"""

from __future__ import annotations

from pathlib import Path

from ..audit import access_audit
from ..errors import SpecHalt, ValidationResult
from . import registry_validator, schema_validator
from .loader import load_spec


def _run(spec: dict, spec_sha256: str | None, record) -> ValidationResult:
    shape_errors = schema_validator.validate_shape(spec)
    if shape_errors:
        return ValidationResult(
            status="HALTED", errors=shape_errors, spec_sha256=spec_sha256, stage_reached=1,
        )

    vocab_errors = registry_validator.validate_vocabulary(spec)
    if vocab_errors:
        return ValidationResult(
            status="HALTED", errors=vocab_errors, spec_sha256=spec_sha256, stage_reached=2,
        )

    return ValidationResult(status="PASSED", errors=[], spec_sha256=spec_sha256, stage_reached=2)


def _finish(result: ValidationResult, record) -> ValidationResult:
    result.files_opened = list(record.opened)
    result.data_accesses = list(record.data_accesses)
    return result


def validate_spec_object(spec: dict, spec_sha256: str | None = None) -> ValidationResult:
    """Validează o specificație deja încărcată în memorie."""
    with access_audit.recording(forbid_data=True) as record:
        result = _run(spec, spec_sha256, record)
    return _finish(result, record)


def validate_spec_file(path: str | Path) -> ValidationResult:
    """Încarcă și validează o specificație de pe disc."""
    with access_audit.recording(forbid_data=True) as record:
        try:
            spec, digest = load_spec(path)
        except SpecHalt as halt:
            result = ValidationResult(
                status="HALTED", errors=halt.errors, spec_sha256=None, stage_reached=0,
            )
            return _finish(result, record)
        result = _run(spec, digest, record)
    return _finish(result, record)
