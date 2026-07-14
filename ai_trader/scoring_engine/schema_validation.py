"""JSON Schema validation for ``OpportunityScore`` objects.

Loads ``SCORING_SCHEMA.json`` (checked in alongside this module) once and exposes
:func:`validate_score_dict`. Same engine choice as
:mod:`ai_trader.signal_engine.schema_validation` for consistency: :mod:`jsonschema` checks the
schema's own well-formedness once at startup, :mod:`fastjsonschema` compiles it once into a plain
Python function used for every actual validation call.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

import fastjsonschema  # type: ignore[import-untyped]
from jsonschema.validators import Draft202012Validator

from ai_trader.scoring_engine.exceptions import SchemaLoadError

_PACKAGE_DIR = Path(__file__).resolve().parent
_SCORING_SCHEMA_PATH = _PACKAGE_DIR / "SCORING_SCHEMA.json"


def _load_schema(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as fh:
            loaded: dict[str, Any] = json.load(fh)
            return loaded
    except OSError as exc:
        raise SchemaLoadError(f"could not read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SchemaLoadError(f"{path} is not valid JSON: {exc}") from exc


def _compile_schema(path: Path) -> Callable[[dict[str, Any]], None]:
    schema = _load_schema(path)
    Draft202012Validator.check_schema(schema)
    try:
        compiled: Callable[[dict[str, Any]], None] = fastjsonschema.compile(schema)
    except fastjsonschema.JsonSchemaDefinitionException as exc:
        raise SchemaLoadError(f"schema {path} failed to compile: {exc}") from exc
    return compiled


@lru_cache(maxsize=1)
def _score_validator() -> Callable[[dict[str, Any]], None]:
    return _compile_schema(_SCORING_SCHEMA_PATH)


def validate_score_dict(data: dict[str, Any]) -> list[str]:
    """Validate ``data`` against ``SCORING_SCHEMA.json``. Returns error messages (empty if valid)."""
    validate = _score_validator()
    try:
        validate(data)
    except fastjsonschema.JsonSchemaException as exc:
        return [str(exc)]
    return []
