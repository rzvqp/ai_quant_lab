"""Gărzi de fundație pentru ve_tower: integritatea modulelor vendate (anti-tampering), INDEPENDENȚA de
market_intelligence/ai_trader, fail-closed la coliziune de nume, și că turnul RATIFICAT rulează (N3 hartă reală,
N4 confirmare, cascada N1/N2 fail-closed). Contractele versionate N3/N4 se testează separat, peste această fundație."""

from __future__ import annotations

import hashlib
import os
import sys

import pytest

_PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PKG not in sys.path:
    sys.path.insert(0, _PKG)

import ve_tower  # noqa: E402
from ve_tower.version import VENDORED_CONTENT_SHA256, VENDORED_SOURCE_COMMITS  # noqa: E402

_TOWER_DIR = os.path.join(_PKG, "ve_tower", "_tower")
_MODS = tuple(VENDORED_CONTENT_SHA256.keys())


def test_vendored_modules_content_integrity() -> None:
    # fiecare modul vendat are exact sha256-ul înregistrat (detectează orice modificare post-vendare)
    for m in _MODS:
        data = open(os.path.join(_TOWER_DIR, m + ".py"), "rb").read()
        assert hashlib.sha256(data).hexdigest() == VENDORED_CONTENT_SHA256[m], f"{m}.py modificat vs sha256 înregistrat"


def test_all_13_modules_present_with_source_commits() -> None:
    assert set(_MODS) == set(VENDORED_SOURCE_COMMITS)
    assert len(_MODS) == 13
    for m in _MODS:
        assert os.path.exists(os.path.join(_TOWER_DIR, m + ".py"))
        assert len(VENDORED_SOURCE_COMMITS[m]) == 40   # commit-sursă complet


def test_no_market_intelligence_or_ai_trader_import() -> None:
    # INDEPENDENȚĂ: niciun modul vendat nu importă market_intelligence / ai_trader (nici reactivare, nici duplicare)
    for m in _MODS:
        src = open(os.path.join(_TOWER_DIR, m + ".py"), encoding="utf-8").read()
        assert "market_intelligence" not in src, f"{m}.py atinge market_intelligence"
        assert "ai_trader" not in src, f"{m}.py atinge ai_trader"


def test_collision_is_fail_closed() -> None:
    # un modul STRĂIN sub un nume al turnului ⇒ eroare EXPLICITĂ, nu shadowing tăcut
    import types
    from ve_tower._bootstrap import TowerLoadCollisionError, _MARK
    ve_tower.ensure_tower_loaded()
    foreign = types.ModuleType("zone_map")            # NU poartă marcajul _MARK
    saved = sys.modules.get("zone_map")
    try:
        sys.modules["zone_map"] = foreign
        # forțează o reîncărcare: resetează flag-ul intern
        import ve_tower._bootstrap as b
        b._loaded = False
        with pytest.raises(TowerLoadCollisionError):
            b.ensure_tower_loaded()
    finally:
        if saved is not None:
            sys.modules["zone_map"] = saved
        assert getattr(saved, _MARK, False)           # al nostru rămâne marcat
        b._loaded = True


def test_tower_produces_real_map_and_confirmation() -> None:
    ve_tower.ensure_tower_loaded()
    zm = ve_tower.tower_module("zone_map")
    zc = ve_tower.tower_module("zone_confirmation")
    lo = ve_tower.tower_module("level_output")
    n = 40
    o = []; h = []; l = []; c = []; t = []
    for j in range(n):
        base = 100.0 + (1.0 if (j // 5) % 2 else -1.0)
        o.append(base); h.append(base + 1.5); l.append(base - 1.5); c.append(base + 0.3); t.append(1_600_000_000 + j * 900)
    r3 = zm.build_zone_map(h, l, c, o, t, atr=[5.0] * n, regime_available=True, bias_available=True)
    assert lo.is_available(r3)                          # N3 produce o hartă REALĂ din bare închise
    assert r3.value.zones and r3.value.zones[0].composition   # niveluri cu PROVENIENȚĂ (compoziție de familii)
    r4 = zc.classify_zone_confirmation([100 + (0 if i < 3 else 2) for i in range(9)],
                                       [99 + (0 if i < 3 else 2) for i in range(9)],
                                       [99.5 + (0 if i < 3 else 2) for i in range(9)], 100.0, +1, w=3, atr=[1.0] * 9)
    assert lo.is_available(r4)                          # N4 confirmă folosind doar informația disponibilă


def test_cascade_and_bad_input_fail_closed() -> None:
    ve_tower.ensure_tower_loaded()
    zm = ve_tower.tower_module("zone_map")
    zc = ve_tower.tower_module("zone_confirmation")
    n = 40
    o = [100.0] * n; h = [101.0] * n; l = [99.0] * n; c = [100.0] * n; t = [1_600_000_000 + j * 900 for j in range(n)]
    r3 = zm.build_zone_map(h, l, c, o, t, atr=[5.0] * n, regime_available=False, bias_available=True)
    assert getattr(r3, "reason", None) == "cascade_level1_or_level2_unavailable"   # N1/N2 indisponibil ⇒ Unavailable
    r4 = zc.classify_zone_confirmation([1.0, 2.0], [0.5, 1.5], [1.0, 2.0], 1.5, 0, w=3)   # side invalid
    assert getattr(r4, "reason", None) == "invalid_side"
