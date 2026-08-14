"""Gărzi de fundație: BYTE-IDENTITATE la git-blob a modulelor vendate (verificabilă independent cu
`git rev-parse <commit>:code/<mod>.py`), independența de market_intelligence/ai_trader, și că turnul rulează.
(Robustețea încărcătorului — tranzacționalitate/coliziune/concurență — e în `test_bootstrap.py`.)"""

from __future__ import annotations

import os
import sys

_PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PKG not in sys.path:
    sys.path.insert(0, _PKG)

import ve_tower  # noqa: E402
from ve_tower import VENDORED_BLOB_SHA1, VENDORED_SOURCE_COMMITS, git_blob_sha1  # noqa: E402

_TOWER_DIR = os.path.join(_PKG, "ve_tower", "_tower")
_MODS = tuple(VENDORED_BLOB_SHA1.keys())


def test_vendored_modules_are_git_blob_identical() -> None:
    # bytes IDENTICE cu blob-ul git (nu „content-identical după normalizare EOL"). Red Team verifică independent
    # git_blob_sha1(bytes) == VENDORED_BLOB_SHA1[m] == `git rev-parse <source_commit>:code/<m>.py`.
    for m in _MODS:
        data = open(os.path.join(_TOWER_DIR, m + ".py"), "rb").read()
        assert git_blob_sha1(data) == VENDORED_BLOB_SHA1[m], f"{m}.py NU e byte-identic cu blob-ul git"


def test_all_13_modules_present_with_source_commits_and_blobs() -> None:
    assert set(_MODS) == set(VENDORED_SOURCE_COMMITS)
    assert len(_MODS) == 13
    for m in _MODS:
        assert os.path.exists(os.path.join(_TOWER_DIR, m + ".py"))
        assert len(VENDORED_SOURCE_COMMITS[m]) == 40 and len(VENDORED_BLOB_SHA1[m]) == 40


def test_no_market_intelligence_or_ai_trader_import() -> None:
    for m in _MODS:
        src = open(os.path.join(_TOWER_DIR, m + ".py"), encoding="utf-8").read()
        assert "market_intelligence" not in src and "ai_trader" not in src, f"{m}.py atinge un stack interzis"


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
    assert lo.is_available(r3) and r3.value.zones and r3.value.zones[0].composition
    r4 = zc.classify_zone_confirmation([100 + (0 if i < 3 else 2) for i in range(9)],
                                       [99 + (0 if i < 3 else 2) for i in range(9)],
                                       [99.5 + (0 if i < 3 else 2) for i in range(9)], 100.0, +1, w=3, atr=[1.0] * 9)
    assert lo.is_available(r4)
