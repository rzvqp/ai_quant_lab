"""JSON Schema validation for :meth:`~ai_trader.strategy_manager.registry.StrategyRegistry.snapshot`
output, against ``STRATEGY_REGISTRY_SCHEMA.json`` (checked in alongside this module, unlike the
Strategy Execution Contract schema which lives under ``knowledge/interface/``). Same engine choice
as :mod:`ai_trader.strategy_manager.schema_validation` for consistency; see that module's docstring
for the ``jsonschema``-once / ``fastjsonschema``-compiled-once rationale.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

import fastjsonschema  # type: ignore[import-untyped]
from jsonschema.validators import Draft202012Validator

from ai_trader.strategy_manager.exceptions import SchemaLoadError

_SCHEMA_PATH = Path(__file__).resolve().parent / "STRATEGY_REGISTRY_SCHEMA.json"


@lru_cache(maxsize=1)
def _load_schema() -> dict[str, Any]:
    try:
        with _SCHEMA_PATH.open("r", encoding="utf-8") as fh:
            loaded: dict[str, Any] = json.load(fh)
            return loaded
    except OSError as exc:
        raise SchemaLoadError(f"could not read {_SCHEMA_PATH}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SchemaLoadError(f"{_SCHEMA_PATH} is not valid JSON: {exc}") from exc


@lru_cache(maxsize=1)
def _compiled_validator() -> Callable[[dict[str, Any]], None]:
    schema = _load_schema()
    Draft202012Validator.check_schema(schema)
    try:
        compiled: Callable[[dict[str, Any]], None] = fastjsonschema.compile(schema)
    except fastjsonschema.JsonSchemaDefinitionException as exc:
        raise SchemaLoadError(f"schema failed to compile: {exc}") from exc
    return compiled


def validate_registry_snapshot(data: dict[str, Any]) -> list[str]:
    """Validate ``data`` against ``STRATEGY_REGISTRY_SCHEMA.json``. Returns a list of error
    messages (empty if valid)."""
    validate = _compiled_validator()
    try:
        validate(data)
    except fastjsonschema.JsonSchemaException as exc:
        return [str(exc)]
    return []
