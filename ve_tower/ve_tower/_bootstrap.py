"""Încărcătorul TURNULUI vendat — rezolvă importurile inter-modul BARE ale modulelor ratificate FĂRĂ a le rescrie o
singură linie (byte-identitate la git blob păstrată) și FĂRĂ coliziuni globale tăcute.

Garanții (verificate de teste):
- **concurență**: `ensure_tower_loaded` e protejat de un lock (double-checked) — importul din mai multe fire e sigur.
- **eroare la jumătatea încărcării**: dacă exec-ul unui modul eșuează, modulul e ȘTERS din `sys.modules` (cleanup
  complet) — ZERO module parțial încărcate.
- **fără contaminare**: un nume deja ocupat de un modul STRĂIN ⇒ eroare EXPLICITĂ (fail-closed), nu shadowing tăcut.
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
    """Un nume de modul al turnului e deja ocupat în sys.modules de un modul STRĂIN — incompatibilitate explicită."""


def _load_module(name: str, path: str) -> ModuleType:
    """Încarcă UN modul sub numele său bare: coliziune străină ⇒ eroare; exec eșuat ⇒ cleanup COMPLET (pop), nu lăsa
    un modul parțial în sys.modules."""
    existing = sys.modules.get(name)
    if existing is not None:
        if getattr(existing, _MARK, False):
            return existing
        raise TowerLoadCollisionError(
            f"modulul {name!r} e deja în sys.modules și NU e vendat de ve_tower — coliziune de nume; "
            f"ve_tower refuză să facă shadowing tăcut (fail-closed)")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:               # pragma: no cover
        raise TowerLoadCollisionError(f"nu pot încărca modulul vendat {name!r} din {path!r}")
    module: ModuleType = importlib.util.module_from_spec(spec)
    setattr(module, _MARK, True)
    sys.modules[name] = module                            # înregistrează ÎNAINTE de exec (cross-importuri din cache)
    try:
        spec.loader.exec_module(module)
    except BaseException:                                 # exec eșuat ⇒ cleanup COMPLET
        sys.modules.pop(name, None)
        raise
    return module


def ensure_tower_loaded() -> None:
    """Încarcă cele 13 module vendate sub numele lor bare (idempotent, thread-safe)."""
    global _loaded
    if _loaded:
        return
    with _lock:
        if _loaded:
            return
        for name in _LOAD_ORDER:
            _load_module(name, os.path.join(_TOWER_DIR, name + ".py"))
        _loaded = True


def tower_module(name: str) -> ModuleType:
    """Întoarce un modul vendat al turnului (după `ensure_tower_loaded`)."""
    ensure_tower_loaded()
    return sys.modules[name]
