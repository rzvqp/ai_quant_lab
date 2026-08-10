"""Teste pentru harta M15 RE-ANCORATĂ (nivelul 3, v2.0). Contract LevelOutput, re-ancorare pe grup, ordonare
cauzală, non-lookahead, fail-closed. (Vechiul contor-per-bară @11ae360 e înlocuit — vezi SPEC1 404b6c8.)
"""

from __future__ import annotations

import os
import sys
from typing import Sequence

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from level_output import Ok, Unavailable  # noqa: E402
from zone_map import BAND_ATR_MULT, SORT_KEY, ZoneMap, _cluster, _Instance, Family, build_zone_map  # noqa: E402


def _bars(n: int) -> tuple[list[float], list[float], list[float], list[float], list[int]]:
    o: list[float] = []; h: list[float] = []; l: list[float] = []; c: list[float] = []; t: list[int] = []
    base = 100.0
    for j in range(n):
        base += 1.0 if (j // 5) % 2 == 0 else -1.0
        o.append(base); h.append(base + 1.5); l.append(base - 1.5); c.append(base + 0.3)
        t.append(1_600_000_000 + j * 900)
    return o, h, l, c, t


# ───────────────────────────── re-ancorarea: grupare geometrică ─────────────────────────────
def test_cluster_single_linkage_by_band() -> None:
    insts = [_Instance(Family.LEVEL, 100.0, 1), _Instance(Family.FVG, 100.2, 2),   # <=0.25 apart → un grup
             _Instance(Family.POOL, 105.0, 3)]                                      # departe → grup separat
    groups = _cluster(insts, band=0.25)
    assert len(groups) == 2 and len(groups[0]) == 2 and len(groups[1]) == 1


def test_anchor_is_group_mean_not_price() -> None:
    insts = [_Instance(Family.LEVEL, 100.0, 1), _Instance(Family.OB, 100.2, 2)]
    groups = _cluster(insts, band=0.5)
    assert len(groups) == 1 and abs(sum(x.price for x in groups[0]) / 2 - 100.1) < 1e-9   # ancora = media grupului


# ───────────────────────────── contract LevelOutput + fail-closed ─────────────────────────────
def test_returns_leveloutput_ok_on_valid_bars() -> None:
    o, h, l, c, t = _bars(60)
    out = build_zone_map(h, l, c, o, t, atr=[5.0] * 60)
    assert isinstance(out, Ok) and isinstance(out.value, ZoneMap)
    assert out.value.band_atr == BAND_ATR_MULT and out.value.sort_key == SORT_KEY
    assert out.valid_until == out.as_of + 1 and out.schema_hash                    # cadență + schema


def test_zonemap_has_no_status_field() -> None:
    assert "status" not in ZoneMap.__dataclass_fields__                            # statusul = CONSTRUCTORUL, nu câmp


def test_fail_closed_returns_unavailable_constructor() -> None:
    o, h, l, c, t = _bars(20)
    assert isinstance(build_zone_map([1.0], [1.0], [1.0], [1.0], [1], atr=[5.0]), Unavailable)   # n<2
    r = build_zone_map(h, l, c, o, t, atr=[5.0] * 20, regime_available=False)
    assert isinstance(r, Unavailable) and r.reason == "cascade_level1_or_level2_unavailable"
    atr_bad = [5.0] * 20; atr_bad[18] = float("nan")
    assert isinstance(build_zone_map(h, l, c, o, t, atr=atr_bad), Unavailable)     # ATR nefinit → Unavailable


def test_empty_set_is_ok_not_unavailable() -> None:
    # bare fără nicio instanță în bandă → Ok(ZoneMap(zones=())), un REZULTAT, nu Unavailable
    n = 40
    flat = [100.0] * n
    out = build_zone_map(flat, flat, flat, flat, [1_600_000_000 + j * 900 for j in range(n)], atr=[5.0] * n)
    assert isinstance(out, Ok)                                                     # mulțime vidă = rezultat valid


# ───────────────────────────── ordonare cauzală + ranking ─────────────────────────────
def test_zones_ranked_by_declared_key() -> None:
    o, h, l, c, t = _bars(80)
    out = build_zone_map(h, l, c, o, t, atr=[5.0] * 80)
    assert isinstance(out, Ok)
    zones = out.value.zones
    ranks = [z.relative_rank for z in zones]
    assert ranks == list(range(1, len(zones) + 1))                                # relative_rank 1..N
    # cheia (distance_atr ASC, age_bars DESC, k DESC) e monotonă pe distanță
    dists = [z.distance_atr for z in zones]
    assert dists == sorted(dists)                                                  # proximitatea prima (acționabilitate)
    for z in zones:
        assert z.k == len({f for f, _cnt in z.composition})                       # k = familii DISTINCTE (descriptor)


# ───────────────────────────── non-lookahead prin perturbare ─────────────────────────────
def test_non_lookahead_perturbing_current_bar() -> None:
    o, h, l, c, t = _bars(60); atr = [5.0] * 60
    z1 = build_zone_map(h, l, c, o, t, atr=atr)
    m = len(c) - 1
    o2, h2, l2, c2 = list(o), list(h), list(l), list(c)
    o2[m] = 9999.0; h2[m] = 9999.0; l2[m] = 0.001; c2[m] = 9999.0                 # bara curentă (i) NU se citește
    z2 = build_zone_map(h2, l2, c2, o2, t, atr=atr)
    assert z1 == z2                                                                # ref=close[i-1], instanțe <= i-1
