"""Încărcătorul TURNULUI vendat — rezolvă importurile inter-modul BARE (`from level_output import ...`,
`from market_state import ...`) ale modulelor ratificate FĂRĂ a le rescrie o singură linie (byte-identitate păstrată)
și FĂRĂ coliziuni globale tăcute.

Modulele din `_tower/` sunt copii BYTE-IDENTICE ale modulelor ratificate din `code/` (comiturile-sursă în `version.py`).
Ele se importă reciproc prin nume BARE (cod de cercetare cu module plate). Le înregistrăm în `sys.modules` sub numele
lor bare, în ordinea dependențelor, marcate cu `__ve_tower_vendored__`. Dacă un nume bare e DEJA în `sys.modules` și NU
e al nostru ⇒ eroare EXPLICITĂ (incompatibilitate, fail-closed) — niciodată shadowing tăcut al modulelor gazdei.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from types import ModuleType

_TOWER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_tower")

# ordinea dependențelor (dependența înainte de consumator) — cross-importurile bare se rezolvă din cache
_LOAD_ORDER: tuple[str, ...] = (
    "level_output", "market_state", "market_structure", "imbalance_mechanics", "liquidity_mechanics",
    "institutional_levels", "session_levels", "order_block_void", "order_flow",
    "regime_classifier", "bias_h1", "zone_map", "zone_confirmation",
)

_MARK = "__ve_tower_vendored__"
_loaded = False


class TowerLoadCollisionError(RuntimeError):
    """Un nume de modul al turnului e deja ocupat în sys.modules de un modul STRĂIN — incompatibilitate explicită."""


def ensure_tower_loaded() -> None:
    """Încarcă cele 13 module vendate sub numele lor bare (idempotent). Coliziune cu modul străin ⇒ eroare explicită."""
    global _loaded
    if _loaded:
        return
    for name in _LOAD_ORDER:
        existing = sys.modules.get(name)
        if existing is not None:
            if getattr(existing, _MARK, False):
                continue                                   # deja al nostru
            raise TowerLoadCollisionError(
                f"modulul {name!r} e deja în sys.modules și NU e vendat de ve_tower — coliziune de nume; "
                f"ve_tower refuză să facă shadowing tăcut (fail-closed)")
        path = os.path.join(_TOWER_DIR, name + ".py")
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:            # pragma: no cover
            raise TowerLoadCollisionError(f"nu pot încărca modulul vendat {name!r} din {path!r}")
        module: ModuleType = importlib.util.module_from_spec(spec)
        setattr(module, _MARK, True)
        sys.modules[name] = module                         # înregistrează ÎNAINTE de exec (cross-importuri din cache)
        try:
            spec.loader.exec_module(module)
        except BaseException:                              # pragma: no cover — nu lăsa un modul pe jumătate încărcat
            sys.modules.pop(name, None)
            raise
    _loaded = True


def tower_module(name: str) -> ModuleType:
    """Întoarce un modul vendat al turnului (după `ensure_tower_loaded`)."""
    ensure_tower_loaded()
    return sys.modules[name]
