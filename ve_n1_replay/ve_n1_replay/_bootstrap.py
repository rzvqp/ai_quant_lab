"""Încărcătorul IZOLAT al closure-ului N1 replay — încarcă modulele vendate BYTE-IDENTIC (ai_trader @21ae632 +
detectorii @61cbd58c) FĂRĂ să rescrie o linie, sub numele lor reale, TRANZACȚIONAL și FAIL-CLOSED la coliziune.

Consumatorul (Alpha) rulează într-un VENV SEPARAT: fără repo-ul ai_trader, fără ve_tower. Acolo numele reale
(`ai_trader.*`, `market_structure`, …) sunt libere ⇒ izolare completă. Dacă un nume e DEJA ocupat de un modul STRĂIN
(ex. `market_structure` al lui ve_tower — alt blob/semantică), încărcarea REFUZĂ fail-closed cu ZERO reziduuri —
NICIODATĂ nu substituie silențios. Rollback tranzacțional retrage EXACT ce a introdus, păstrează excepția originală,
permite retry curat, e sigur la două importuri concurente. NU atinge module host preexistente.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import threading
from types import ModuleType

_HERE = os.path.dirname(os.path.abspath(__file__))
_AI_DIR = os.path.join(_HERE, "_ai")          # ai_trader/... @21ae632
_DET_DIR = os.path.join(_HERE, "_det")        # detectorii @61cbd58c (nume bare)

_MARK = "__ve_n1_replay_vendored__"
_lock = threading.Lock()
_loaded = False

# pachetele-namespace ce trebuie să existe ca să se rezolve `from ai_trader.x.y import ...`
_NAMESPACE_PACKAGES: tuple[str, ...] = (
    "ai_trader", "ai_trader.n1_replay", "ai_trader.live_signal_source",
    "ai_trader.signal_engine", "ai_trader.market_scanner", "ai_trader.strategy_manager",
    "ai_trader.mandate2_readiness", "ai_trader.new_brain_bridge", "ai_trader.structural_observer",
)
# pachete cu __init__.py de CONȚINUT (nu doar container): se exec în modulul-pachet DUPĂ ce se încarcă frunzele
_PACKAGE_INITS: tuple[str, ...] = ("ai_trader.n1_replay",)
# detectorii @61cbd58c, nume BARE, ordine de dependențe (market_structure/market_state/order_block_void întâi)
_DETECTOR_ORDER: tuple[str, ...] = (
    "market_structure", "market_state", "order_block_void", "imbalance_mechanics", "order_flow",
)
# modulele ai_trader runtime, ordine TOPOLOGICĂ (canonical_bars e test-only, exclus din runtime)
_AITRADER_ORDER: tuple[str, ...] = (
    "ai_trader.market_scanner.exceptions", "ai_trader.market_scanner.types", "ai_trader.strategy_manager.contract",
    "ai_trader.signal_engine.types", "ai_trader.live_signal_source.types", "ai_trader.n1_replay.errors",
    "ai_trader.mandate2_readiness.wheel_verification", "ai_trader.n1_replay.identity", "ai_trader.n1_replay.types",
    "ai_trader.structural_observer.vendor_bridge", "ai_trader.new_brain_bridge.raw_axes_builder",
    "ai_trader.n1_replay.engine",
)


class N1ReplayLoadCollisionError(RuntimeError):
    """Un nume necesar e ocupat de un modul STRĂIN (ex. detector ve_tower) — incompatibilitate explicită, fail-closed."""


def _ai_path(name: str) -> str:
    return os.path.join(_AI_DIR, name.replace(".", os.sep) + ".py")


def _check_free(name: str) -> None:
    existing = sys.modules.get(name)
    if existing is not None and not getattr(existing, _MARK, False):
        raise N1ReplayLoadCollisionError(
            f"numele {name!r} e ocupat de un modul STRĂIN (nevendat de ve_n1_replay) — ve_n1_replay refuză să facă "
            f"shadowing/substituție silențioasă (fail-closed). Rulează într-un venv separat, fără ve_tower/ai_trader.")


def _register_namespace(name: str, introduced: list[str]) -> None:
    if sys.modules.get(name) is not None:
        _check_free(name)
        return
    pkg = ModuleType(name)
    real_dir = os.path.join(_AI_DIR, name.replace(".", os.sep))
    pkg.__path__ = [real_dir] if os.path.isdir(real_dir) else []
    setattr(pkg, _MARK, True)
    sys.modules[name] = pkg
    introduced.append(name)


def _exec_package_init(name: str) -> None:
    """Exec-ă __init__.py de conținut ÎN modulul-pachet deja înregistrat (păstrează __path__), FĂRĂ a-l rescrie."""
    pkg = sys.modules[name]
    path = os.path.join(_AI_DIR, name.replace(".", os.sep), "__init__.py")
    with open(path, "rb") as f:
        code = compile(f.read(), path, "exec")
    exec(code, pkg.__dict__)


def _load_file(name: str, path: str, introduced: list[str]) -> None:
    if sys.modules.get(name) is not None:
        _check_free(name)
        if getattr(sys.modules[name], _MARK, False):
            return
    _check_free(name)
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:                     # pragma: no cover
        raise N1ReplayLoadCollisionError(f"nu pot încărca modulul vendat {name!r} din {path!r}")
    module: ModuleType = importlib.util.module_from_spec(spec)
    setattr(module, _MARK, True)
    sys.modules[name] = module
    introduced.append(name)
    spec.loader.exec_module(module)


def _rollback(introduced: list[str]) -> None:
    for name in reversed(introduced):
        sys.modules.pop(name, None)


def ensure_loaded() -> None:
    """Încarcă closure-ul izolat (idempotent, thread-safe, tranzacțional). Coliziune/eroare ⇒ rollback complet."""
    global _loaded
    if _loaded:
        return
    with _lock:
        if _loaded:
            return
        introduced: list[str] = []
        try:
            for ns in _NAMESPACE_PACKAGES:
                _register_namespace(ns, introduced)
            for det in _DETECTOR_ORDER:
                _load_file(det, os.path.join(_DET_DIR, det + ".py"), introduced)
            for mod in _AITRADER_ORDER:
                _load_file(mod, _ai_path(mod), introduced)
            for pkg in _PACKAGE_INITS:
                _exec_package_init(pkg)          # umple pachetul cu __init__.py real (după frunze)
        except BaseException:
            _rollback(introduced)                              # cleanup COMPLET; pop nu aruncă ⇒ excepția originală
            raise
        _loaded = True


def vendored_module(name: str) -> ModuleType:
    ensure_loaded()
    return sys.modules[name]
