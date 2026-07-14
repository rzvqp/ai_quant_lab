"""JSON Schema validation for Strategy Execution Contracts.

Loads ``knowledge/interface/strategy_contract.v1.schema.json`` — the single frozen source of truth
(never copied into this package) — once and exposes :func:`validate_contract`. Mirrors
:mod:`ai_trader.market_scanner.schema_validation`'s engine choice exactly: the schema is checked
once at startup for structural well-formedness via :mod:`jsonschema`
(``Draft202012Validator.check_schema``), then compiled once into a plain Python function via
:mod:`fastjsonschema` for the actual per-contract validation calls. Unlike the Market Scanner's
per-bar hot path, ``load_library()`` validates each contract once per (re)load — not a
performance-critical loop — but the compiled validator is used anyway for consistency and because
it is strictly faster with identical pass/fail semantics, not because of a measured bottleneck here.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

import fastjsonschema  # type: ignore[import-untyped]  # no stubs published for this library
from jsonschema.validators import Draft202012Validator

from ai_trader.strategy_manager.exceptions import SchemaLoadError

#: The Strategy Interface v1 contract schema is the frozen source of truth checked in under
#: ``knowledge/interface/`` (NOT under this package) — see ``STRATEGY_INTERFACE_v1.md``.
#: ``ai_trader/strategy_manager/schema_validation.py`` -> parents[2] = repo root.
_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2] / "knowledge" / "interface" / "strategy_contract.v1.schema.json"
)


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


def validate_contract(data: dict[str, Any]) -> list[str]:
    """Validate ``data`` against ``strategy_contract.v1.schema.json``.

    Args:
        data: the candidate contract as a plain JSON-deserialized dict.

    Returns:
        A list of human-readable error messages (empty if ``data`` is valid). Fails fast on the
        first violation, matching the Loader's own "quarantine, never coerce" needs — the caller
        only needs to know "valid or not, with a diagnostic reason" (architecture §4: "A failure
        lists the offending path(s)").
    """
    validate = _compiled_validator()
    try:
        validate(data)
    except fastjsonschema.JsonSchemaException as exc:
        return [str(exc)]
    return []


def schema_dict() -> dict[str, Any]:
    """Return the loaded schema (read-only use — callers must not mutate it)."""
    return _load_schema()
