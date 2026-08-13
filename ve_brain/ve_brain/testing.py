"""ENTRYPOINT EXCLUSIV DE TEST — fault-injection asupra catalogului canonic al lui N6.

NU importa acest modul din codul de PRODUCȚIE (AI Trader). Nu e re-exportat de `ve_brain` (nu e în `__all__` de
nivel superior) și fiecare funcție e blocată până la un `unlock_for_tests(TOKEN)` explicit — deci un import accidental
nu poate muta nimic. Producția consumă `ve_brain` (API sigilat) și nu are motiv să atingă acest modul.

Motivul separării (verdict Red Team, a 6-a suprafață): API-ul de definire arbitrară a catalogului + resetarea +
marcarea de indisponibilitate NU pot sta pe suprafața de producție, altfel consumatorul redefinește conținutul
catalogului canonic. Aici sunt izolate, gate-uite și reversibile spre catalogul de producție.
"""

from __future__ import annotations

from . import n6
from ._canonical_catalog import build_sealed_catalog
from ._canonical_catalog import CANONICAL_CATALOG_HASH, CANONICAL_CATALOG_VERSION
from .regime_routing import SealedRegistry, StrategyContract

_UNLOCK_TOKEN = "VE-BRAIN-TEST-ONLY"
_unlocked = False


def unlock_for_tests(token: str) -> None:
    """Deblochează hook-urile de test. Token greșit ⇒ RuntimeError (nu se poate folosi accidental)."""
    global _unlocked
    if token != _UNLOCK_TOKEN:
        raise RuntimeError("ve_brain.testing: token invalid — hook-urile de test rămân blocate")
    _unlocked = True


def _require_unlocked() -> None:
    if not _unlocked:
        raise RuntimeError("ve_brain.testing e BLOCAT — apelează unlock_for_tests(TOKEN) întâi (test-only)")


def install_sealed_catalog(strategies: tuple[StrategyContract, ...], catalog_version: str) -> None:
    """Instalează un catalog SIGILAT de test + aliniază versiunea/amprenta aprobată (calea validă rulează normal)."""
    _require_unlocked()
    reg = SealedRegistry.build(strategies, catalog_version)
    n6._SEALED_CATALOG = reg
    n6._APPROVED_CATALOG_VERSION = reg.catalog_version
    n6._APPROVED_CATALOG_HASH = reg.content_hash


def install_unsealed_catalog(strategies: tuple[StrategyContract, ...], catalog_version: str) -> None:
    """Fault: catalog NESIGILAT → N6 trebuie să refuze (CATALOG_NOT_SEALED)."""
    _require_unlocked()
    n6._SEALED_CATALOG = SealedRegistry.unsealed(strategies, catalog_version)
    n6._APPROVED_CATALOG_VERSION = catalog_version
    n6._APPROVED_CATALOG_HASH = n6._SEALED_CATALOG.content_hash


def force_version_mismatch(expected_version: str) -> None:
    """Fault: versiunea aprobată nu se potrivește cu cea a catalogului → N6 refuză (CATALOG_VERSION_MISMATCH)."""
    _require_unlocked()
    n6._APPROVED_CATALOG_VERSION = expected_version


def restore_production_catalog() -> None:
    """Revine la catalogul de PRODUCȚIE încorporat (idempotent, folosit între teste)."""
    _require_unlocked()
    n6._SEALED_CATALOG = build_sealed_catalog()
    n6._APPROVED_CATALOG_VERSION = CANONICAL_CATALOG_VERSION
    n6._APPROVED_CATALOG_HASH = CANONICAL_CATALOG_HASH
