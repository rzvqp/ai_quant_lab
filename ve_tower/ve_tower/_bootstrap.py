"""Încărcătorul TURNULUI vendat — rezolvă importurile inter-modul BARE ale modulelor ratificate FĂRĂ a le rescrie o
singură linie (byte-identitate la git blob păstrată) și cu încărcare TRANZACȚIONALĂ.

Garanții (verificate de teste):
- **tranzacțional**: o tentativă eșuată (coliziune la ORICE poziție SAU eroare în `exec_module`) retrage TOATE modulele
  pe care le-a INTRODUS ea — zero module parțial încărcate. Restaurează exact starea preexistentă.
- **proprietate**: ce era în `sys.modules` ÎNAINTE de tentativă NU e al tower-ului — nu se șterge, nu se modifică; doar
  ce a introdus tentativa curentă se retrage. Modulele host își păstrează identitatea (același obiect) înainte și după.
- **excepția originală se păstrează**: cleanup-ul (pop-uri care nu aruncă) nu maschează eroarea/reason code inițial.
- **concurență**: lock (double-checked) — un fir încarcă, celelalte așteaptă determinist; fără dublă încărcare.
- **retry curat**: după un eșec, `_loaded` rămâne False și o nouă tentativă pornește pe o stare curată.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import threading
from types import ModuleType

_TOWER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_tower")

_LOAD_ORDER: tuple[str, ...] = (
    "level_output", "market_state", "market_structure", "imbalance_mechanics", "liquidity_mechanics",
    "institutional_levels", "session_levels", "order_block_void", "order_flow",
    "regime_classifier", "bias_h1", "zone_map", "zone_confirmation",
)

_MARK = "__ve_tower_vendored__"
_lock = threading.Lock()
_loaded = False


class TowerLoadCollisionError(RuntimeError):
    """Un nume de modul al turnului e ocupat în sys.modules de un modul STRĂIN — incompatibilitate explicită."""


def _load_one(name: str, path: str, introduced: list[str]) -> None:
    """Încarcă UN modul sub numele său bare. Coliziune cu modul STRĂIN ⇒ eroare (fără să-l atingă). Un modul ABSENT e
    înregistrat (marcat, ÎNAINTE de exec) și adăugat în `introduced` — retragerea e responsabilitatea tranzacției."""
    existing = sys.modules.get(name)
    if existing is not None:
        if getattr(existing, _MARK, False):
            return                                   # deja al nostru (din tentativa curentă) — nu reînregistra
        raise TowerLoadCollisionError(
            f"modulul {name!r} e deja în sys.modules și NU e vendat de ve_tower — coliziune de nume; "
            f"ve_tower refuză să facă shadowing tăcut (fail-closed)")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:          # pragma: no cover
        raise TowerLoadCollisionError(f"nu pot încărca modulul vendat {name!r} din {path!r}")
    module: ModuleType = importlib.util.module_from_spec(spec)
    setattr(module, _MARK, True)
    sys.modules[name] = module                       # înregistrează ÎNAINTE de exec (cross-importuri din cache)
    introduced.append(name)                          # urmărit DE LA înregistrare — retras dacă exec eșuează
    spec.loader.exec_module(module)


def _rollback(introduced: list[str]) -> None:
    """Retrage EXACT modulele introduse de tentativă (LIFO). `pop(..., None)` nu aruncă ⇒ nu maschează excepția
    originală. NU atinge module preexistente (nu sunt în `introduced`)."""
    for name in reversed(introduced):
        sys.modules.pop(name, None)


def _load_sequence(order: tuple[str, ...], tower_dir: str) -> tuple[str, ...]:
    """Tranzacție: încarcă `order` din `tower_dir`. La ORICE eroare, retrage tot ce a introdus și RE-RIDICĂ excepția
    originală (cu reason code-ul ei). Succes ⇒ întoarce numele introduse."""
    introduced: list[str] = []
    try:
        for name in order:
            _load_one(name, os.path.join(tower_dir, name + ".py"), introduced)
    except BaseException:
        _rollback(introduced)                        # cleanup COMPLET; nu aruncă ⇒ excepția originală se propagă
        raise
    return tuple(introduced)


def _load_module(name: str, path: str) -> ModuleType:
    """Încărcare tranzacțională a UNUI modul (folosită de teste). Eșec ⇒ cleanup complet, excepția originală re-ridicată."""
    introduced: list[str] = []
    try:
        _load_one(name, path, introduced)
    except BaseException:
        _rollback(introduced)
        raise
    return sys.modules[name]


def ensure_tower_loaded() -> None:
    """Încarcă cele 13 module vendate sub numele lor bare (idempotent, thread-safe, TRANZACȚIONAL)."""
    global _loaded
    if _loaded:
        return
    with _lock:
        if _loaded:
            return
        _load_sequence(_LOAD_ORDER, _TOWER_DIR)      # eșec ⇒ rollback complet + excepția originală; _loaded rămâne False
        _loaded = True


def tower_module(name: str) -> ModuleType:
    """Întoarce un modul vendat al turnului (după `ensure_tower_loaded`)."""
    ensure_tower_loaded()
    return sys.modules[name]
