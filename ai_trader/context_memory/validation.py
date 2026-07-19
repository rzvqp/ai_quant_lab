"""Validation helpers and the timestamp policy -- Phase 7 Checkpoint 9.

Every Context Memory contract validates itself at construction time (in its own ``__post_init__``);
this module holds the shared, reusable checks so each contract's own validation reads as a short,
literal list of rules rather than duplicated boilerplate. Nothing here is exported as a long-term public
contract beyond :class:`ContextMemoryValidationError` and :func:`as_of_from_datetime` -- see
``__init__.py`` for the exact public surface.

**Timestamp policy (Checkpoint 9 §D, a required, disclosed design decision)**: every timestamp Context
Memory stores is a plain ``int`` -- unix epoch seconds, UTC-implicit by definition (unix time has no
timezone ambiguity), matching the ``as_of: int`` convention already used uniformly across
``MarketIntelligenceSnapshot``, ``EdgeIntelligenceSnapshot``, ``DecisionReport``, and every Shadow
Evidence record. A Python ``datetime`` is never accepted directly as a contract field -- it is timezone-
AMBIGUOUS by construction (a naive ``datetime`` carries no timezone at all; an aware one could be in any
zone) in a way a plain unix-epoch ``int`` structurally cannot be. :func:`as_of_from_datetime` is the one
sanctioned conversion path: it REJECTS a naive ``datetime`` outright (no implicit UTC assumption) and
REQUIRES an explicitly timezone-aware ``datetime`` before converting to a canonical unix-epoch ``int``.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone


class ContextMemoryValidationError(ValueError):
    """Raised whenever a Context Memory contract is constructed from invalid or ambiguous data. One
    exception type, not a large hierarchy -- Checkpoint 9's own "smallest foundational slice" scope; a
    caller distinguishes failure reasons from the message, not the exception subtype, until a real
    consumer needs otherwise."""


def require_non_empty_str(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContextMemoryValidationError(f"{field_name} must be a non-empty string, got {value!r}")
    return value


def require_positive_int(value: object, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ContextMemoryValidationError(f"{field_name} must be an int, got {value!r}")
    if value <= 0:
        raise ContextMemoryValidationError(f"{field_name} must be > 0, got {value!r}")
    return value


def require_finite_float_or_none(value: object, field_name: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContextMemoryValidationError(f"{field_name} must be a float or None, got {value!r}")
    result = float(value)
    if not math.isfinite(result):
        raise ContextMemoryValidationError(f"{field_name} must be finite, got {result!r}")
    return result


def require_unit_interval_or_none(value: object, field_name: str) -> float | None:
    result = require_finite_float_or_none(value, field_name)
    if result is not None and not (0.0 <= result <= 1.0):
        raise ContextMemoryValidationError(f"{field_name} must be within [0.0, 1.0], got {result!r}")
    return result


def as_of_from_datetime(dt: datetime) -> int:
    """The one sanctioned ``datetime`` -> unix-epoch-seconds conversion (see module docstring for the
    full policy). Rejects a naive ``datetime`` (``tzinfo is None``) -- never assumes UTC on its behalf."""
    if dt.tzinfo is None:
        raise ContextMemoryValidationError(
            "naive datetime is not accepted -- pass a timezone-aware datetime "
            "(e.g. dt.replace(tzinfo=timezone.utc) only if UTC is genuinely known, "
            "never assumed silently)"
        )
    return int(dt.astimezone(timezone.utc).timestamp())
