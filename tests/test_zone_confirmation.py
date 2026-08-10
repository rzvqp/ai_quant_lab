"""Teste pentru confirmarea zonei pe M5 (nivelul 4). Sintetic; fără MT5. Un test per convenție, PLUS:
demonstrația granței hit+W / hit+W+1 (perturbare) și că starea contradictorie e INEXPRIMABILĂ prin TIP.
"""

from __future__ import annotations

import math
import os
import sys

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from zone_confirmation import (  # noqa: E402
    P33_PERSISTENCE, P33_PROGRESS, P67_PERSISTENCE, P67_PROGRESS, Status, W_DEFAULT, ZoneConfirmation,
    ZoneConfirmationResult, classify_zone_confirmation,
)

LV = 100.0
W = 10                           # fereastră mică pentru sintetic (logica e W-agnostică; W_DEFAULT=60 testat separat)


def _bars(rows: list[tuple[float, float, float]]) -> tuple[list[float], list[float], list[float], list[float]]:
    h = [r[0] for r in rows]; l = [r[1] for r in rows]; c = [r[2] for r in rows]
    return h, l, c, [1.0] * len(rows)                            # ATR=1 ⇒ progres = distanță brută


def _pre_hit_up() -> list[tuple[float, float, float]]:
    return [(99.0, 98.0, 98.5), (100.5, 99.0, 100.2)]           # idx0 pre (fără penetrare), idx1 HIT (sus)


def _pre_hit_down() -> list[tuple[float, float, float]]:
    return [(102.0, 101.0, 101.5), (101.0, 99.5, 99.8)]         # idx0 pre, idx1 HIT (jos: low<=100)


_POST = [(200.0, 50.0, 150.0)] * 3                              # bare DUPĂ fereastră (idx>hit+W) — irelevante


# ───────────────────────────── cele patru clase + NEDETERMINAT ─────────────────────────────
def test_acceptance_bullish() -> None:
    win = [(101, 100, 100.8), (102, 100.5, 101.5), (107, 101, 106), (104, 101, 103.5), (103, 100.5, 102.5),
           (102, 100.2, 101.2), (101.5, 100.1, 101), (101, 100, 100.6), (100.9, 100, 100.4), (100.8, 100, 100.3)]
    h, l, c, a = _bars(_pre_hit_up() + win + _POST)
    r = classify_zone_confirmation(h, l, c, LV, side=1, w=W, atr=a)
    assert r.confirmation is ZoneConfirmation.ACCEPTANCE_BULLISH   # persistență 1,0≥0,80 ȘI progres 7≥5,99
    assert r.persistence == 1.0 and r.progress_atr is not None and r.progress_atr >= P67_PROGRESS


def test_absorption_proxy_bullish() -> None:
    win = [(99.5, 98, 99)] * 10                                  # penetrarea în SUS absorbită: revine sub nivel
    h, l, c, a = _bars(_pre_hit_up() + win + _POST)
    r = classify_zone_confirmation(h, l, c, LV, side=1, w=W, atr=a)
    assert r.confirmation is ZoneConfirmation.ABSORPTION_PROXY_BULLISH   # persistență 0≤0,22 ȘI progres 0≤2,53
    assert r.persistence == 0.0


def test_acceptance_bearish() -> None:
    win = [(100, 99, 99.2), (99.5, 98, 98.5), (99, 93, 94), (98, 96, 96.5), (97, 95, 95.5),
           (98, 96, 97), (99, 97, 98), (99.5, 98, 98.8), (100, 99, 99.4), (100, 99.5, 99.6)]
    h, l, c, a = _bars(_pre_hit_down() + win + _POST)
    r = classify_zone_confirmation(h, l, c, LV, side=-1, w=W, atr=a)
    assert r.confirmation is ZoneConfirmation.ACCEPTANCE_BEARISH   # închideri sub nivel + progres 7≥5,99
    assert r.progress_atr is not None and r.progress_atr >= P67_PROGRESS


def test_absorption_proxy_bearish() -> None:
    win = [(102, 100.5, 101)] * 10                              # penetrarea în JOS absorbită: revine peste nivel
    h, l, c, a = _bars(_pre_hit_down() + win + _POST)
    r = classify_zone_confirmation(h, l, c, LV, side=-1, w=W, atr=a)
    assert r.confirmation is ZoneConfirmation.ABSORPTION_PROXY_BEARISH
    assert r.persistence == 0.0


def test_undetermined_mixed_axes() -> None:
    win = [(100.5, 100, 100.3)] * 10                            # persistență 1,0 DAR progres 0,5<5,99 → nici, nici
    h, l, c, a = _bars(_pre_hit_up() + win + _POST)
    r = classify_zone_confirmation(h, l, c, LV, side=1, w=W, atr=a)
    assert r.confirmation is ZoneConfirmation.UNDETERMINED
    assert r.persistence == 1.0 and r.progress_atr is not None and r.progress_atr < P67_PROGRESS


# ───────────────────────────── efortul e SATURAT — nu e prag ─────────────────────────────
def test_encounters_saturated_does_not_drive_classification() -> None:
    # 9/10 bare penetrează (encounters mare) DAR închideri straddle (persistență 0,5) + progres 3<5,99 → NEDETERMINAT
    win = [(103, 100, 100.5), (103, 100, 99.5), (103, 100, 100.5), (103, 100, 99.5), (103, 100, 100.5),
           (103, 100, 99.5), (103, 100, 100.5), (103, 100, 99.5), (103, 100, 100.5), (99, 98, 98.5)]
    h, l, c, a = _bars(_pre_hit_up() + win + _POST)
    r = classify_zone_confirmation(h, l, c, LV, side=1, w=W, atr=a)
    assert r.encounters is not None and r.encounters >= 8        # EFORT mare
    assert r.confirmation is ZoneConfirmation.UNDETERMINED        # dar NU decide clasificarea


# ───────────────────────────── GRANIȚA DE TIMP: hit+W / hit+W+1, prin perturbare ─────────────────────────────
def test_time_boundary_and_no_lookahead_by_perturbation() -> None:
    win = [(101, 100, 100.8), (102, 100.5, 101.5), (107, 101, 106), (104, 101, 103.5), (103, 100.5, 102.5),
           (102, 100.2, 101.2), (101.5, 100.1, 101), (101, 100, 100.6), (100.9, 100, 100.4), (100.8, 100, 100.3)]
    rows = _pre_hit_up() + win
    post_a = [(200.0, 50.0, 150.0)] * 5                          # viitor EXTREM într-un sens
    post_b = [(100.001, 99.999, 100.0)] * 5                     # viitor EXTREM în alt sens
    ha, la, ca, aa = _bars(rows + post_a)
    hb, lb, cb, ab = _bars(rows + post_b)
    ra = classify_zone_confirmation(ha, la, ca, LV, side=1, w=W, atr=aa)
    rb = classify_zone_confirmation(hb, lb, cb, LV, side=1, w=W, atr=ab)
    assert ra.hit_idx is not None
    assert ra.window_end_idx == ra.hit_idx + W                   # fereastra se închide la hit+W
    assert ra.descriptor_available_idx == ra.hit_idx + W + 1     # intrarea abia la hit+W+1
    # barele > hit+W NU pot schimba descriptorul (altfel = condiționare pe rezultat)
    assert ra.confirmation is rb.confirmation
    assert (ra.persistence, ra.progress_atr, ra.encounters) == (rb.persistence, rb.progress_atr, rb.encounters)


# ───────────────────────────── starea contradictorie INEXPRIMABILĂ prin TIP ─────────────────────────────
def test_contradiction_is_inexpressible_by_type() -> None:
    h, l, c, a = _bars(_pre_hit_up() + [(101, 100, 100.5)] * 10 + _POST)
    r = classify_zone_confirmation(h, l, c, LV, side=1, w=W, atr=a)
    assert isinstance(r.confirmation, ZoneConfirmation)          # O SINGURĂ variabilă ordinală
    # NU există steaguri separate absorbție/acceptare care ar permite starea contradictorie
    for flag in ("absorption", "acceptance", "is_absorption", "is_acceptance"):
        assert not hasattr(r, flag)
        assert flag not in ZoneConfirmationResult.__dataclass_fields__
    # cele două stări exclusive sunt valori distincte ale ACELUIAȘI tip — nu pot coexista
    assert len(set(ZoneConfirmation)) == 5 and r.confirmation in set(ZoneConfirmation)


# ───────────────────────────── fail-closed → UNDETERMINED ─────────────────────────────
def test_fail_closed_incomplete_window() -> None:
    h, l, c, a = _bars(_pre_hit_up() + [(101, 100, 100.5)] * 2)  # doar 4 bare, W=10 → hit+W depășește seria
    r = classify_zone_confirmation(h, l, c, LV, side=1, w=W, atr=a)
    assert r.confirmation is ZoneConfirmation.UNDETERMINED and r.reason == "incomplete_window"
    assert r.status == Status.UNAVAILABLE.value


def test_fail_closed_no_penetration_not_in_population() -> None:
    h, l, c, a = _bars([(99, 98, 98.5)] * 20)                    # niciun high≥100 → nicio penetrare
    r = classify_zone_confirmation(h, l, c, LV, side=1, w=W, atr=a)
    assert r.confirmation is ZoneConfirmation.UNDETERMINED and r.reason == "no_penetration"


def test_fail_closed_atr_unavailable() -> None:
    rows = _pre_hit_up() + [(101, 100, 100.5)] * 10 + _POST
    h, l, c, _a = _bars(rows)
    atr_bad = [1.0] * len(rows); atr_bad[1] = float("nan")       # ATR nefinit la HIT
    r = classify_zone_confirmation(h, l, c, LV, side=1, w=W, atr=atr_bad)
    assert r.confirmation is ZoneConfirmation.UNDETERMINED and r.reason == "atr_unavailable"


def test_fail_closed_zone_unavailable_cascades() -> None:
    h, l, c, a = _bars(_pre_hit_up() + [(101, 100, 100.5)] * 10 + _POST)
    r = classify_zone_confirmation(h, l, c, float("nan"), side=1, w=W, atr=a)   # zona nivelului 3 absentă
    assert r.confirmation is ZoneConfirmation.UNDETERMINED and r.reason == "zone_unavailable"


# ───────────────────────────── constante: W=60 (calendaristic), praguri = terțile declarate ─────────────────────────────
def test_constants_are_declared_choices_and_W_is_calendar() -> None:
    assert W_DEFAULT == 60                                       # 5h în unități M5, NU 20 bare transplantate
    assert (P33_PROGRESS, P67_PROGRESS) == (2.53, 5.99)          # terțile pe progres (alegeri, ancoră ocupanță egală)
    assert (P33_PERSISTENCE, P67_PERSISTENCE) == (0.22, 0.80)
    hh, ll, cc, aa = _bars(_pre_hit_up() + [(101, 100, 100.5)] * 10 + _POST)
    r = classify_zone_confirmation(hh, ll, cc, LV, side=1, w=W, atr=aa)
    assert r.schema_hash and len(r.schema_hash) == 16           # schema pre-înregistrată (audit)


def test_tick_volume_structurally_excluded() -> None:
    import inspect
    params = set(inspect.signature(classify_zone_confirmation).parameters)
    assert not any("vol" in p.lower() for p in params)          # funcția ia DOAR OHLC — volumul nu poate intra
