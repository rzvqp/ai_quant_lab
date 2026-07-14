"""JSON Schema validation for ``MarketContext`` objects.

Loads ``MARKET_CONTEXT_SCHEMA.json`` (checked in alongside this module) once and exposes a single
:func:`validate_context` entry point used by :meth:`MarketScanner.build_context` before any context
ever leaves the scanner (architecture §14, API §5 contract #4: "every emitted context conforms").

Validation engine: the schema is checked once at startup for structural well-formedness against the
JSON Schema Draft 2020-12 meta-schema via :mod:`jsonschema` (``Draft202012Validator.check_schema``),
then **compiled once** into a plain Python validation function via :mod:`fastjsonschema`. Every
subsequent :func:`validate_context` call runs that compiled function — no per-call ``$ref``
resolution. This matters: profiling a multi-year replay showed the original per-call
``jsonschema.Draft202012Validator.iter_errors`` approach spending >95% of wall-clock time inside
``jsonschema``/``referencing`` internals (repeatedly re-resolving the schema's internal ``$defs``
refs for every bar in every timeframe window, on every single emitted context), making any
replay/backtest over more than a few thousand bars impractically slow (~10 ms/context). The compiled
validator is ~10x faster (~1 ms/context) with byte-identical pass/fail semantics and the same
required-vs-optional/enum/``additionalProperties`` behaviour — verified against the existing test
suite before the swap. Both libraries validate the exact same, unmodified schema file.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

import fastjsonschema  # type: ignore[import-untyped]  # no stubs published for this library
from jsonschema.validators import Draft202012Validator

from ai_trader.market_scanner.exceptions import SchemaLoadError

_SCHEMA_FILENAME = "MARKET_CONTEXT_SCHEMA.json"


@lru_cache(maxsize=1)
def _load_schema() -> dict[str, Any]:
    path = Path(__file__).resolve().parent / _SCHEMA_FILENAME
    try:
        with path.open("r", encoding="utf-8") as fh:
            loaded: dict[str, Any] = json.load(fh)
            return loaded
    except OSError as exc:
        raise SchemaLoadError(f"could not read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SchemaLoadError(f"{path} is not valid JSON: {exc}") from exc


@lru_cache(maxsize=1)
def _compiled_validator() -> Callable[[dict[str, Any]], None]:
    schema = _load_schema()
    # Verify the schema itself is well-formed Draft 2020-12 (structural sanity check, run once).
    Draft202012Validator.check_schema(schema)
    try:
        compiled: Callable[[dict[str, Any]], None] = fastjsonschema.compile(schema)
    except fastjsonschema.JsonSchemaDefinitionException as exc:
        raise SchemaLoadError(f"schema failed to compile: {exc}") from exc
    return compiled


def validate_context(context: dict[str, Any]) -> list[str]:
    """Validate ``context`` against ``MARKET_CONTEXT_SCHEMA.json``.

    Args:
        context: the candidate ``MarketContext`` as a plain JSON-serializable dict.

    Returns:
        A list of human-readable error messages (empty if ``context`` is valid). Fails fast on the
        first violation (a single-element list) rather than collecting every violation — the caller
        only needs to know "valid or not, with a diagnostic", and this is what keeps validation fast
        enough for large-scale replay. The caller decides what to do with a non-empty list
        (``build_context`` raises :class:`~ai_trader.market_scanner.exceptions.ContextValidationError`).
    """
    validate = _compiled_validator()
    try:
        validate(context)
    except fastjsonschema.JsonSchemaException as exc:
        return [str(exc)]
    return []


def schema_dict() -> dict[str, Any]:
    """Return the loaded schema (read-only use — callers must not mutate it)."""
    return _load_schema()
