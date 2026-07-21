"""Minimal, dependency-free JSON-Schema validator (subset of Draft 2020-12).

We author both the schemas and the validator, so we only implement the keywords we use:
type, required, properties, additionalProperties (bool), enum, const, items, minItems,
maxItems, minLength, maxLength, minimum, maximum, pattern, anyOf, nullable via type lists.

This avoids adding `jsonschema` as an external dependency (CEO directive: avoid unnecessary
external dependencies). If richer schema features are ever needed, this can be swapped for
the real library without changing call sites -- `validate()` returns a list of error strings
and `is_valid()` returns a bool.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, List

_SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"

_TYPE_CHECKS = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


def _check_type(value: Any, type_spec, path: str, errors: List[str]) -> bool:
    types = type_spec if isinstance(type_spec, list) else [type_spec]
    if any(_TYPE_CHECKS[t](value) for t in types):
        return True
    errors.append(f"{path}: expected type {type_spec}, got {type(value).__name__}")
    return False


def _validate(value: Any, schema: dict, path: str, errors: List[str]) -> None:
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}, got {value!r}")

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} not in enum {schema['enum']}")

    if "anyOf" in schema:
        branch_errs = []
        for i, sub in enumerate(schema["anyOf"]):
            e: List[str] = []
            _validate(value, sub, f"{path}#anyOf[{i}]", e)
            if not e:
                break
            branch_errs.extend(e)
        else:
            errors.append(f"{path}: did not match anyOf ({'; '.join(branch_errs)})")

    if "type" in schema:
        if not _check_type(value, schema["type"], path, errors):
            return  # further keyword checks assume the type held

    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path}: shorter than minLength {schema['minLength']}")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(f"{path}: longer than maxLength {schema['maxLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{path}: does not match pattern {schema['pattern']!r}")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: below minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: above maximum {schema['maximum']}")

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}: fewer than minItems {schema['minItems']}")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{path}: more than maxItems {schema['maxItems']}")
        if "items" in schema:
            for i, item in enumerate(value):
                _validate(item, schema["items"], f"{path}[{i}]", errors)

    if isinstance(value, dict):
        props = schema.get("properties", {})
        for req in schema.get("required", []):
            if req not in value:
                errors.append(f"{path}: missing required property {req!r}")
        for k, v in value.items():
            if k in props:
                _validate(v, props[k], f"{path}.{k}", errors)
            elif schema.get("additionalProperties", True) is False:
                errors.append(f"{path}: additional property {k!r} not allowed")


def validate(instance: Any, schema: dict) -> List[str]:
    """Return a list of validation error strings. Empty list == valid."""
    errors: List[str] = []
    _validate(instance, schema, "$", errors)
    return errors


def is_valid(instance: Any, schema: dict) -> bool:
    return not validate(instance, schema)


_CACHE: dict = {}


def load_schema(name: str) -> dict:
    """Load a schema by bare name (without .schema.json) from the package schemas/ dir."""
    if name in _CACHE:
        return _CACHE[name]
    path = _SCHEMA_DIR / f"{name}.schema.json"
    schema = json.loads(path.read_text(encoding="utf-8"))
    _CACHE[name] = schema
    return schema
