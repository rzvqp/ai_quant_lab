"""New reason codes Order Manager's own build stage can produce -- additive, never colliding with the
existing, frozen `execution_engine.validator`/`execution_engine.pipeline` vocabulary (those modules'
own reason strings are reused verbatim, unmodified, when they fire)."""

from __future__ import annotations

INSTRUMENT_SYMBOL_MISMATCH = "INSTRUMENT_SYMBOL_MISMATCH"
INVALID_DIRECTION = "INVALID_DIRECTION"
PRICE_NORMALIZATION_FAILED = "PRICE_NORMALIZATION_FAILED"
BUILD_FAILED = "BUILD_FAILED"
