"""JSON Schema validation for ``MarketContext`` objects.

Loads ``MARKET_CONTEXT_SCHEMA.json`` (checked in alongside this module) once and exposes a single
:func:`validate_context` entry point used by :meth:`MarketScanner.build_context` before any context
ever leaves the scanner (architecture §14, API §5 contract #4: "every emitted context conforms").
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import jsonschema
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
def _validator() -> Draft202012Validator:
    schema = _load_schema()
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def validate_context(context: dict[str, Any]) -> list[str]:
    """Validate ``context`` against ``MARKET_CONTEXT_SCHEMA.json``.

    Args:
        context: the candidate ``MarketContext`` as a plain JSON-serializable dict.

    Returns:
        A list of human-readable error messages (empty if ``context`` is valid). The caller
        decides what to do with a non-empty list (``build_context`` raises
        :class:`~ai_trader.market_scanner.exceptions.ContextValidationError`).
    """
    validator = _validator()
    errors = sorted(validator.iter_errors(context), key=lambda e: list(e.path))
    return [f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}" for e in errors]


def schema_dict() -> dict[str, Any]:
    """Return the loaded schema (read-only use — callers must not mutate it)."""
    return _load_schema()
