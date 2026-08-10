"""Teste pentru harta operațională M15 (nivelul 3). Un test per convenție + non-lookahead (perturbare) + fail-closed.

Nucleul (contor NEPONDERAT, prag de confluență totală, mulțime vidă, dezvăluire de redundanță) se testează pe
helper-ul pur `_assemble`; cablarea primitivelor + cauzalitatea + fail-closed pe `build_zone_map`.
"""

from __future__ import annotations

import os
import sys

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from zone_map import (  # noqa: E402
    BAND_ATR_MULT, FEATURE_NAMES, REDUNDANT_WITH, THRESHOLD_K, Status, ZoneMap, _assemble, build_zone_map,
)

_ALL_AVAIL = {nm: Status.AVAILABLE.value for nm in FEATURE_NAMES}


# ───────────────────────────── NUCLEUL: contor NEPONDERAT + prag de confluență totală ─────────────────────────────
def test_total_confluence_emits_one_zone() -> None:
    present = {"pdh_pdl": True, "fvg": True, "liquidity": True, "discount": True}
    zm = _assemble(present, _ALL_AVAIL, "discount", reference=100.0, as_of=50)
    assert len(zm.zones) == 1 and zm.zones[0].k == 4 and zm.counter_k == 4
    assert set(zm.zones[0].features) == set(FEATURE_NAMES) and zm.ranked_by_k == (4,)
    assert zm.status == Status.AVAILABLE.value and zm.threshold_k == THRESHOLD_K


def test_below_threshold_is_empty_set_not_error() -> None:
    present = {"pdh_pdl": True, "fvg": True, "liquidity": True, "discount": False}
    zm = _assemble(present, _ALL_AVAIL, "premium", reference=100.0, as_of=50)
    assert zm.zones == () and zm.counter_k == 3                  # mulțime VIDĂ = rezultat valid
    assert zm.status == Status.AVAILABLE.value and zm.reason == "empty_set_below_threshold"


def test_discount_unavailable_blocks_total_confluence() -> None:
    present = {"pdh_pdl": True, "fvg": True, "liquidity": True, "discount": False}
    status = {**_ALL_AVAIL, "discount": Status.UNAVAILABLE.value}   # Mid absent → UNAVAILABLE, NU FALSE
    zm = _assemble(present, status, None, reference=100.0, as_of=50)
    assert zm.zones == () and zm.counter_k == 3                  # nu poate atinge confluența totală fără discount
    assert zm.status == Status.AVAILABLE.value                   # mulțime vidă = rezultat valid, NU eroare


def test_counter_is_unweighted_pure_count() -> None:
    for combo, exp in ((("pdh_pdl", "fvg", "liquidity", "discount"), 4),
                       (("pdh_pdl", "liquidity"), 2), (("fvg",), 1), ((), 0)):
        present = {nm: (nm in combo) for nm in FEATURE_NAMES}
        zm = _assemble(present, _ALL_AVAIL, None, 100.0, 10)
        assert zm.counter_k == exp                              # k = numărul de trăsături, fără ponderi


def test_redundant_with_disclosed_two_tier() -> None:
    present = {nm: True for nm in FEATURE_NAMES}
    zm = _assemble(present, _ALL_AVAIL, "discount", 100.0, 10)
    red = set(zm.zones[0].redundant_with)
    assert "CAND-0028" in red and "CAND-0001" in red            # discount↔0028, pdh_pdl↔0001 (dezvăluit)
    assert red == {c for nm in FEATURE_NAMES for c in REDUNDANT_WITH[nm]}


def test_does_not_emit_confidence() -> None:
    zm = _assemble({nm: True for nm in FEATURE_NAMES}, _ALL_AVAIL, "discount", 100.0, 10)
    for attr in ("confidence", "score", "weights", "probability"):
        assert not hasattr(zm, attr) and attr not in ZoneMap.__dataclass_fields__


# ───────────────────────────── cablare: non-lookahead prin perturbare ─────────────────────────────
def _bars(n: int) -> tuple[list[float], list[float], list[float], list[int]]:
    h: list[float] = []; l: list[float] = []; c: list[float] = []; t: list[int] = []
    base = 100.0
    for j in range(n):
        base += 1.0 if (j // 5) % 2 == 0 else -1.0              # zigzag pentru swing-uri/FVG
        h.append(base + 1.5); l.append(base - 1.5); c.append(base + 0.3)
        t.append(1_600_000_000 + j * 900)                      # M15 = 900s
    return h, l, c, t


def test_non_lookahead_perturbing_current_bar_does_not_change_map() -> None:
    h, l, c, t = _bars(40)
    atr = [5.0] * 40
    zm1 = build_zone_map(h, l, c, t, atr=atr)
    m = len(c) - 1
    h2, l2, c2 = list(h), list(l), list(c)
    h2[m] = 9999.0; l2[m] = 0.001; c2[m] = 9999.0              # bara CURENTĂ (i) — NU trebuie citită (ref=close[i-1])
    zm2 = build_zone_map(h2, l2, c2, t, atr=atr)
    assert zm1 == zm2                                           # descriptorul la i citește doar bare <= i-1


# ───────────────────────────── fail-closed ─────────────────────────────
def test_fail_closed_incomplete_window() -> None:
    zm = build_zone_map([100.0], [99.0], [99.5], [1_600_000_000], atr=[5.0])
    assert zm.status == Status.UNAVAILABLE.value and zm.reason == "incomplete_window"
    assert zm.zones == () and zm.counter_k is None


def test_fail_closed_cascade_when_level1_or_level2_unavailable() -> None:
    h, l, c, t = _bars(20); atr = [5.0] * 20
    zr = build_zone_map(h, l, c, t, atr=atr, regime_available=False)
    zb = build_zone_map(h, l, c, t, atr=atr, bias_available=False)
    assert zr.reason == "cascade_level1_or_level2_unavailable" and zr.status == Status.UNAVAILABLE.value
    assert zb.reason == "cascade_level1_or_level2_unavailable"


def test_fail_closed_atr_unavailable() -> None:
    h, l, c, t = _bars(20); atr = [5.0] * 20; atr[len(c) - 2] = float("nan")   # ATR nefinit la i-1
    zm = build_zone_map(h, l, c, t, atr=atr)
    assert zm.status == Status.UNAVAILABLE.value and zm.reason == "atr_unavailable"


def test_build_runs_and_is_wellformed() -> None:
    h, l, c, t = _bars(60); atr = [5.0] * 60
    zm = build_zone_map(h, l, c, t, atr=atr)
    assert isinstance(zm, ZoneMap) and zm.threshold_k == 4
    assert zm.counter_k is None or (0 <= zm.counter_k <= 4)     # contor în {0..4}
    assert len(zm.zones) == len(zm.ranked_by_k)                 # coerență listă


# ───────────────────────────── constante ─────────────────────────────
def test_constants_and_schema() -> None:
    assert THRESHOLD_K == 4 and BAND_ATR_MULT == 1.0            # confluență TOTALĂ; bandă 1×ATR (JOINT în schema_hash)
    assert len(FEATURE_NAMES) == 4
    zm = _assemble({nm: True for nm in FEATURE_NAMES}, _ALL_AVAIL, "discount", 100.0, 10)
    assert zm.schema_hash and len(zm.schema_hash) == 16 and zm.band_atr == 1.0
