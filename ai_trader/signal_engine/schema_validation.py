"""JSON Schema validation for ``StrategySignal``/``Explanation`` objects.

Loads ``SIGNAL_SCHEMA.json`` and ``SIGNAL_EXPLANATION_SCHEMA.json`` (checked in alongside this
module) once and exposes :func:`validate_signal_dict`/:func:`validate_explanation_dict`. Same engine
choice as :mod:`ai_trader.market_scanner.schema_validation` /
:mod:`ai_trader.strategy_manager.schema_validation` for consistency: :mod:`jsonschema` checks the
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

from ai_trader.signal_engine.exceptions import SchemaLoadError

_PACKAGE_DIR = Path(__file__).resolve().parent
_SIGNAL_SCHEMA_PATH = _PACKAGE_DIR / "SIGNAL_SCHEMA.json"
_EXPLANATION_SCHEMA_PATH = _PACKAGE_DIR / "SIGNAL_EXPLANATION_SCHEMA.json"


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
def _signal_validator() -> Callable[[dict[str, Any]], None]:
    return _compile_schema(_SIGNAL_SCHEMA_PATH)


@lru_cache(maxsize=1)
def _explanation_validator() -> Callable[[dict[str, Any]], None]:
    return _compile_schema(_EXPLANATION_SCHEMA_PATH)


def validate_signal_dict(data: dict[str, Any]) -> list[str]:
    """Validate ``data`` against ``SIGNAL_SCHEMA.json``. Returns error messages (empty if valid)."""
    validate = _signal_validator()
    try:
        validate(data)
    except fastjsonschema.JsonSchemaException as exc:
        return [str(exc)]
    return []


def validate_explanation_dict(data: dict[str, Any]) -> list[str]:
    """Validate ``data`` against ``SIGNAL_EXPLANATION_SCHEMA.json``. Returns error messages (empty
    if valid)."""
    validate = _explanation_validator()
    try:
        validate(data)
    except fastjsonschema.JsonSchemaException as exc:
        return [str(exc)]
    return []
