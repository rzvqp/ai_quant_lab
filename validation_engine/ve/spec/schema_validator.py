"""Etapa 1 — validarea formei, față de SPEC_SCHEMA_v1.0.json.

Verifică structura: secțiuni prezente, tipuri, `const`, `enum`, `pattern`,
`additionalProperties`. NU verifică vocabularul (ID-uri de metode, parametri
obligatorii ai unei metode, domenii) — acelea aparțin etapei 2, față de registru.

Maparea codurilor:
  - cuvântul-cheie `required` din schemă  -> E1 (câmp obligatoriu absent)
  - orice altă încălcare                  -> E2 (formă ambiguă sau invalidă)
"""

from __future__ import annotations

import functools
import json
import re

from jsonschema import Draft202012Validator

from .. import paths
from ..errors import VEError

_MISSING = re.compile(r"^'([^']+)' is a required property$")


@functools.lru_cache(maxsize=1)
def load_schema() -> dict:
    with open(paths.SPEC_SCHEMA_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


@functools.lru_cache(maxsize=1)
def _validator() -> Draft202012Validator:
    schema = load_schema()
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _path_of(err) -> str:
    parts = ["/"] if not err.absolute_path else []
    trail = "/".join(str(p) for p in err.absolute_path)
    return trail if trail else (parts[0] if parts else "/")


def validate_shape(spec: dict) -> list[VEError]:
    """Întoarce lista completă de erori de formă (nu se oprește la prima)."""
    errors: list[VEError] = []
    for err in sorted(_validator().iter_errors(spec), key=lambda e: list(e.absolute_path)):
        base = _path_of(err)
        m = _MISSING.match(err.message)
        if err.validator == "required" and m:
            missing = m.group(1)
            field_path = f"{base}/{missing}" if base != "/" else missing
            errors.append(
                VEError(
                    code="E1",
                    field_path=field_path,
                    reason="Câmp obligatoriu absent din specificație.",
                    registry_info=_context_hint(err),
                )
            )
        else:
            errors.append(
                VEError(
                    code="E2",
                    field_path=base,
                    reason=_reason_for(err),
                    registry_info=_context_hint(err),
                )
            )
    return errors


def _reason_for(err) -> str:
    v = err.validator
    if v == "additionalProperties":
        return (
            "Câmp necunoscut în specificație. Schema nu admite câmpuri "
            f"suplimentare la acest nivel ({err.message})."
        )
    if v == "const":
        return f"Valoare neadmisă: singura valoare acceptată este {err.validator_value!r}."
    if v == "enum":
        return f"Valoare în afara mulțimii admise {err.validator_value!r}."
    if v == "type":
        return f"Tip greșit: se cere {err.validator_value!r}."
    if v == "pattern":
        return f"Formatul nu respectă tiparul cerut {err.validator_value!r}."
    if v in {"minItems", "minimum", "maximum", "minLength"}:
        return f"Restricția {v}={err.validator_value!r} nu este respectată."
    return err.message


def _context_hint(err) -> str:
    """Informație factuală despre ce admite schema în acel punct. Fără recomandări."""
    sch = err.schema if isinstance(err.schema, dict) else {}
    bits = []
    if "const" in sch:
        bits.append(f"valoare unică admisă: {sch['const']!r}")
    if "enum" in sch:
        bits.append("valori admise: " + ", ".join(repr(x) for x in sch["enum"]))
    if err.validator == "required" and "properties" in sch:
        bits.append("câmpuri definite aici: " + ", ".join(sorted(sch["properties"])))
    if err.validator == "additionalProperties" and "properties" in sch:
        bits.append("câmpuri admise aici: " + ", ".join(sorted(sch["properties"])))
    return " · ".join(bits)
