"""Încărcare TRANZACȚIONALĂ (remediere TOWER_HANDOFF_CONDITIONAL): o tentativă eșuată nu lasă module parțial
încărcate, restaurează exact starea preexistentă (module host cu ACEEAȘI identitate), și NU maschează excepția
originală. Coliziune la prima/a doua/mijloc/ultima poziție + eroare în exec + concurență + retry."""

from __future__ import annotations

import os
import sys
import threading
import types

import pytest

_PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PKG not in sys.path:
    sys.path.insert(0, _PKG)

import ve_tower  # noqa: E402
import ve_tower._bootstrap as b  # noqa: E402


def _mk(d: str, name: str, body: str) -> None:
    with open(os.path.join(d, name + ".py"), "w", encoding="utf-8") as f:
        f.write(body)


def _cleanup(*names: str) -> None:
    for n in names:
        sys.modules.pop(n, None)


def _seq(d: str) -> tuple[str, ...]:
    _mk(d, "vtp_a", "va = 1\n"); _mk(d, "vtp_b", "vb = 1\n"); _mk(d, "vtp_c", "vc = 1\n")
    return ("vtp_a", "vtp_b", "vtp_c")


# ═══ coliziune la fiecare poziție ═══
def test_collision_at_first(tmp_path: object) -> None:
    d = str(tmp_path); order = _seq(d)
    foreign = types.ModuleType("vtp_a")
    try:
        sys.modules["vtp_a"] = foreign
        with pytest.raises(b.TowerLoadCollisionError):
            b._load_sequence(order, d)
        assert sys.modules["vtp_a"] is foreign               # host neatins
        assert "vtp_b" not in sys.modules and "vtp_c" not in sys.modules
    finally:
        _cleanup(*order)


def test_collision_at_second_red_team_case(tmp_path: object) -> None:
    d = str(tmp_path); order = _seq(d)
    foreign = types.ModuleType("vtp_b")
    try:
        sys.modules["vtp_b"] = foreign
        with pytest.raises(b.TowerLoadCollisionError):
            b._load_sequence(order, d)
        assert "vtp_a" not in sys.modules                    # INTRODUS de tentativă ⇒ RETRAS (defectul Red Team)
        assert sys.modules["vtp_b"] is foreign               # host cu ACEEAȘI identitate
        assert "vtp_c" not in sys.modules
    finally:
        _cleanup(*order)


def test_collision_at_middle(tmp_path: object) -> None:
    d = str(tmp_path)
    for n in ("m0", "m1", "m2", "m3", "m4"):
        _mk(d, "vtp_" + n, "x = 1\n")
    order = tuple("vtp_" + n for n in ("m0", "m1", "m2", "m3", "m4"))
    foreign = types.ModuleType("vtp_m2")
    try:
        sys.modules["vtp_m2"] = foreign
        with pytest.raises(b.TowerLoadCollisionError):
            b._load_sequence(order, d)
        assert "vtp_m0" not in sys.modules and "vtp_m1" not in sys.modules   # rollback
        assert sys.modules["vtp_m2"] is foreign
        assert "vtp_m3" not in sys.modules and "vtp_m4" not in sys.modules
    finally:
        _cleanup(*order)


def test_collision_at_last(tmp_path: object) -> None:
    d = str(tmp_path); order = _seq(d)
    foreign = types.ModuleType("vtp_c")
    try:
        sys.modules["vtp_c"] = foreign
        with pytest.raises(b.TowerLoadCollisionError):
            b._load_sequence(order, d)
        assert "vtp_a" not in sys.modules and "vtp_b" not in sys.modules      # ambele retrase
        assert sys.modules["vtp_c"] is foreign
    finally:
        _cleanup(*order)


# ═══ eroare în exec_module ═══
def test_exec_failure_rolls_back_all_introduced(tmp_path: object) -> None:
    d = str(tmp_path)
    _mk(d, "vtp_a", "va = 1\n"); _mk(d, "vtp_boom", "raise RuntimeError('BOOM-ORIG')\n"); _mk(d, "vtp_c", "vc = 1\n")
    order = ("vtp_a", "vtp_boom", "vtp_c")
    try:
        with pytest.raises(RuntimeError, match="BOOM-ORIG"):         # excepția ORIGINALĂ, nu una de cleanup
            b._load_sequence(order, d)
        assert "vtp_a" not in sys.modules                            # introdus ⇒ retras
        assert "vtp_boom" not in sys.modules                         # parțial (register-before-exec) ⇒ retras
        assert "vtp_c" not in sys.modules                            # neatins vreodată
    finally:
        _cleanup(*order)


def test_zero_new_modules_after_failure(tmp_path: object) -> None:
    d = str(tmp_path); order = _seq(d)
    before = set(sys.modules)
    sys.modules["vtp_b"] = types.ModuleType("vtp_b")
    try:
        with pytest.raises(b.TowerLoadCollisionError):
            b._load_sequence(order, d)
        # singurul nume nou e cel preexistent pe care l-am pus NOI (foreign) — restul zero
        assert set(sys.modules) - before == {"vtp_b"}
    finally:
        _cleanup(*order)


# ═══ retry pe încărcătorul REAL — exact cazul Red Team (coliziune la market_state) ═══
def test_real_loader_transactional_then_retry_succeeds() -> None:
    saved = {n: sys.modules.get(n) for n in b._LOAD_ORDER}
    foreign_ms = types.ModuleType("market_state")
    try:
        with b._lock:                                               # stare curată
            for n in b._LOAD_ORDER:
                sys.modules.pop(n, None)
            b._loaded = False
        sys.modules["market_state"] = foreign_ms                   # coliziune la AL DOILEA modul
        with pytest.raises(b.TowerLoadCollisionError):
            b.ensure_tower_loaded()
        assert "level_output" not in sys.modules                   # DEFECTUL Red Team: acum e RETRAS
        assert sys.modules["market_state"] is foreign_ms           # host neatins
        assert b._loaded is False                                   # stare curată pentru retry
        # elimină coliziunea și reîncearcă → REUȘEȘTE
        sys.modules.pop("market_state", None)
        b.ensure_tower_loaded()
        assert all(n in sys.modules and getattr(sys.modules[n], b._MARK, False) for n in b._LOAD_ORDER)
    finally:
        with b._lock:
            for n in b._LOAD_ORDER:
                sys.modules.pop(n, None)
            for n, mod in saved.items():
                if mod is not None:
                    sys.modules[n] = mod
            b._loaded = False
        b.ensure_tower_loaded()                                    # restaurează pentru celelalte teste


def test_concurrent_import_is_deterministic() -> None:
    with b._lock:
        for n in b._LOAD_ORDER:
            sys.modules.pop(n, None)
        b._loaded = False
    errors: list[BaseException] = []
    barrier = threading.Barrier(8)

    def worker() -> None:
        try:
            barrier.wait()
            b.ensure_tower_loaded()
        except BaseException as e:                                 # noqa: BLE001
            errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors, errors
    assert b._loaded is True
    assert all(n in sys.modules and getattr(sys.modules[n], b._MARK, False) for n in b._LOAD_ORDER)


def test_mid_load_error_single_module_cleanup(tmp_path: object) -> None:
    d = str(tmp_path)
    _mk(d, "vtp_broken", "raise ImportError('boom mid-load')\n")
    try:
        with pytest.raises(ImportError, match="boom mid-load"):
            b._load_module("vtp_broken", os.path.join(d, "vtp_broken.py"))
        assert "vtp_broken" not in sys.modules
    finally:
        _cleanup("vtp_broken")


def test_after_removing_collision_load_succeeds(tmp_path: object) -> None:
    d = str(tmp_path); order = _seq(d)
    foreign = types.ModuleType("vtp_b")
    try:
        sys.modules["vtp_b"] = foreign
        with pytest.raises(b.TowerLoadCollisionError):
            b._load_sequence(order, d)
        sys.modules.pop("vtp_b", None)                             # elimină coliziunea
        introduced = b._load_sequence(order, d)                    # acum REUȘEȘTE
        assert introduced == order and all(n in sys.modules for n in order)
    finally:
        _cleanup(*order)
