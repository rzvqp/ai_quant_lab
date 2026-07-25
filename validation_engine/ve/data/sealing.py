"""Registrul de ferestre sigilate + granița oficială (F4).

Granița sigilată `2025-10-23T09:15:00Z` (epoch 1761210900) este comună tuturor
timeframe-urilor (ratificată provizoriu, P4). F4 NU deschide niciodată holdout-ul:
orice fereastră care se suprapune peste graniță este refuzată. Protocolul de
holdout (token, rehearsal, consum unic) aparține F8.
"""

from __future__ import annotations

from .. import paths
from ..spec import registry_validator

SEALED_BOUNDARY_ISO = "2025-10-23T09:15:00Z"
SEALED_BOUNDARY_EPOCH = 1761210900


class HoldoutAccessError(RuntimeError):
    """F4 nu are voie să atingă fereastra sigilată."""


def boundary_epoch() -> int:
    return SEALED_BOUNDARY_EPOCH


def window_overlaps_sealed(end_iso: str, bounds: str, end_epoch: int) -> bool:
    """True dacă fereastra [.., end] atinge sau depășește granița sigilată."""
    if end_epoch > SEALED_BOUNDARY_EPOCH:
        return True
    if end_epoch == SEALED_BOUNDARY_EPOCH and bounds.endswith("]"):
        return True
    return False


def assert_open_window(end_epoch: int, bounds: str) -> None:
    """Oprește fail-closed dacă fereastra atinge holdout-ul."""
    if end_epoch > SEALED_BOUNDARY_EPOCH or (end_epoch == SEALED_BOUNDARY_EPOCH and bounds.endswith("]")):
        raise HoldoutAccessError(
            f"Fereastra atinge granița sigilată {SEALED_BOUNDARY_ISO}; F4 nu deschide "
            "holdout-ul. Protocolul de holdout este F8."
        )
