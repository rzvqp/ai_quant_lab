"""Teste pentru nivelurile de sesiune (MK-04 sesiuni, v2.7.39). Date sintetice; oglindesc PDH/PDL.

Acoperă: primitiva A (expiră) vs B (persistă), atingere High/Low prin depășire, Mid prin CONȚINERE (obiect
diferit, fără direcție), reset D3_bis, fără lookahead, acumularea măsurată (precondiția dură a lui B).
"""

from __future__ import annotations

import os
import sys

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from market_structure import Block  # noqa: E402
from session_levels import (  # noqa: E402
    SessionLevel, SessionLevelKind, compute_persistent_session_levels, compute_prior_session_levels,
    count_active_persistent_levels, detect_session_level_touches, detect_session_mid_touches,
)

# 3 sesiuni × 3 bare (session_index monoton, etichete distincte)
_SIDX = [0, 0, 0, 1, 1, 1, 2, 2, 2]
_SLAB = ["asia", "asia", "asia", "london", "london", "london", "ny", "ny", "ny"]
_HIGH = [10.0, 12.0, 11.0, 20.0, 20.0, 20.0, 30.0, 30.0, 30.0]   # sesiuni: H=12/20/30
_LOW = [5.0, 4.0, 6.0, 15.0, 15.0, 15.0, 25.0, 25.0, 25.0]        # L=4/15/25 ; Mid=8/17.5/27.5


def _lv(price: float, kind: SessionLevelKind, avail: int, expiry: int) -> SessionLevel:
    return SessionLevel(price, kind, source_session_start=avail - 1, available_idx=avail,
                        expiry_idx=expiry, block_index=0, session_label="asia")


# ── primitiva A (expiră) ──
def test_prior_session_levels_emit_HLM_first_session_unclassified() -> None:
    lv = compute_prior_session_levels(_HIGH, _LOW, _SIDX, _SLAB, [Block(0, 9)])
    src0 = [x for x in lv if x.source_session_start == 0]        # sesiunea 0 = sursă pt. sesiunea 1
    assert len(src0) == 3                                        # H/L/Mid
    prices = {x.kind: x.price for x in src0}
    assert prices[SessionLevelKind.SESSION_HIGH] == 12.0 and prices[SessionLevelKind.SESSION_LOW] == 4.0
    assert prices[SessionLevelKind.SESSION_MID] == 8.0
    assert all(x.available_idx == 3 and x.expiry_idx == 5 for x in src0)   # activ DOAR pe sesiunea 1 (expiră)
    assert not any(x.source_session_start == 6 for x in lv)      # sesiunea 2 (bara 6) nu e sursă în A
    assert not any(x.available_idx == 0 for x in lv)             # D3_bis: prima sesiune nu emite


def test_prior_no_lookahead_level_uses_only_completed_session() -> None:
    lv = compute_prior_session_levels(_HIGH, _LOW, _SIDX, _SLAB, [Block(0, 9)])
    src0 = [x for x in lv if x.source_session_start == 0]
    assert all(x.available_idx > 2 for x in src0)                # disponibil ABIA după închiderea sesiunii 0 (bara 2)
    hi2 = list(_HIGH); hi2[3] = 999.0; hi2[6] = 999.0            # mutarea barelor VIITOARE
    lv2 = compute_prior_session_levels(hi2, _LOW, _SIDX, _SLAB, [Block(0, 9)])
    src0b = [x for x in lv2 if x.source_session_start == 0]
    assert {(x.kind, x.price) for x in src0} == {(x.kind, x.price) for x in src0b}   # neschimbate


# ── primitiva B (persistă) + precondiția de acumulare ──
def test_persistent_levels_accumulate_and_expiry_is_block_end() -> None:
    lv = compute_persistent_session_levels(_HIGH, _LOW, _SIDX, _SLAB, [Block(0, 9)])
    # sesiunea 0 disponibilă de la 3, sesiunea 1 de la 6; ambele persistă la sfârșitul blocului (8)
    src0 = [x for x in lv if x.source_session_start == 0]
    assert src0 and all(x.available_idx == 3 and x.expiry_idx == 8 for x in src0)   # PERSISTĂ (nu expiră la 5)
    assert any(x.source_session_start == 3 and x.available_idx == 6 for x in lv)   # sesiunea 1 începe la bara 3
    active = count_active_persistent_levels(lv, [], 9)           # fără atingeri → acumulare pură
    assert active[4] == 3 and active[7] == 6                     # sesiunea 1 adaugă 3 → ACUMULARE măsurată


def test_prior_expires_but_persistent_does_not() -> None:
    a = compute_prior_session_levels(_HIGH, _LOW, _SIDX, _SLAB, [Block(0, 9)])
    b = compute_persistent_session_levels(_HIGH, _LOW, _SIDX, _SLAB, [Block(0, 9)])
    a0 = next(x for x in a if x.source_session_start == 0)
    b0 = next(x for x in b if x.source_session_start == 0)
    assert a0.expiry_idx == 5 and b0.expiry_idx == 8            # A expiră după sesiunea următoare; B persistă


# ── atingeri High/Low (depășire) ──
def test_high_low_touch_by_exceedance_d7_once_mid_excluded() -> None:
    n = 8
    high = [70.0] * n; low = [60.0] * n                         # bază: High=100/Low=50 NEatinse
    high[4] = 101.0; high[5] = 101.0                            # High=100 depășit la 4 (și 5)
    low[6] = 49.0                                                # Low=50 depășit la 6
    levels = [_lv(100.0, SessionLevelKind.SESSION_HIGH, 2, 7), _lv(50.0, SessionLevelKind.SESSION_LOW, 2, 7),
              _lv(75.0, SessionLevelKind.SESSION_MID, 2, 7)]
    tk = detect_session_level_touches(high, low, levels)
    kinds = {t.level.kind: t.touch_idx for t in tk}
    assert kinds[SessionLevelKind.SESSION_HIGH] == 4            # prima depășire (D7: o singură atingere)
    assert kinds[SessionLevelKind.SESSION_LOW] == 6
    assert SessionLevelKind.SESSION_MID not in kinds           # Mid EXCLUS din detectorul de depășire
    assert sum(1 for t in tk if t.level.kind is SessionLevelKind.SESSION_HIGH) == 1


# ── atingere Mid (conținere, fără direcție) ──
def test_mid_touch_by_containment_not_exceedance() -> None:
    n = 8
    high = [70.0] * n; low = [60.0] * n                         # Mid=75 NEconținut (75>70) la barele de bază
    high[4] = 80.0; low[4] = 70.0                               # bara 4 conține 75 (70<=75<=80)
    mid = [_lv(75.0, SessionLevelKind.SESSION_MID, 2, 7)]
    tk = detect_session_mid_touches(high, low, mid)
    assert len(tk) == 1 and tk[0].touch_idx == 4               # conținere la 4
    # detectorul de DEPĂȘIRE nu tratează Mid; iar Mid nu poartă direcție (SessionLevelTouch nu are side)
    assert detect_session_level_touches(high, low, mid) == []
    assert not hasattr(tk[0], "side") and not hasattr(tk[0], "direction")


def test_mid_containment_fires_where_exceedance_of_edges_would_not() -> None:
    """O bară strict în interior (nu depășește nicio extremă) tot atinge Mid prin conținere."""
    mid = [_lv(75.0, SessionLevelKind.SESSION_MID, 0, 3)]
    high = [76.0, 60.0, 60.0, 60.0]; low = [74.0, 50.0, 50.0, 50.0]   # bara 0: [74,76] conține 75
    tk = detect_session_mid_touches(high, low, mid)
    assert len(tk) == 1 and tk[0].touch_idx == 0
