"""Teste pentru confirmarea zonei pe M5 (nivelul 4, v2.0 CEAS W=3). Sintetic; fără MT5. CONTRACT LevelOutput:
UNDETERMINED măsurat = Ok; fail-closed = Unavailable. Plus granița hit+W/hit+W+1 (perturbare) și starea
contradictorie INEXPRIMABILĂ prin TIP. (`status: str` s-a șters — statusul e CONSTRUCTORUL.)
"""

from __future__ import annotations

import os
import sys

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from level_output import Ok, Unavailable  # noqa: E402
from zone_confirmation import (  # noqa: E402
    P33_PERSISTENCE, P33_PROGRESS, P67_PERSISTENCE, P67_PROGRESS, W_DEFAULT, ZoneConfirmation,
    ZoneConfirmationResult, classify_zone_confirmation,
)

LV = 100.0
W = 10                           # fereastră mică pentru sintetic (logica e W-agnostică; W_DEFAULT=3 e ceasul real)


def _bars(rows: list[tuple[float, float, float]]) -> tuple[list[float], list[float], list[float], list[float]]:
    h = [r[0] for r in rows]; l = [r[1] for r in rows]; c = [r[2] for r in rows]
    return h, l, c, [1.0] * len(rows)                            # ATR=1 ⇒ progres = distanță brută


def _pre_hit_up() -> list[tuple[float, float, float]]:
    return [(99.0, 98.0, 98.5), (100.5, 99.0, 100.2)]           # idx0 pre (fără penetrare), idx1 HIT (sus)


def _pre_hit_down() -> list[tuple[float, float, float]]:
    return [(102.0, 101.0, 101.5), (101.0, 99.5, 99.8)]         # idx0 pre, idx1 HIT (jos: low<=100)


_POST = [(200.0, 50.0, 150.0)] * 3                              # bare DUPĂ fereastră (idx>hit+W) — irelevante


def _ok(out: object) -> ZoneConfirmationResult:
    assert isinstance(out, Ok)                                  # contractul: măsurat ⇒ Ok
    assert out.valid_until == out.as_of + 1 and out.schema_hash and len(out.schema_hash) == 16
    return out.value


# ───────────────────────────── cele patru clase + NEDETERMINAT (toate Ok — măsurate) ─────────────────────────────
def test_acceptance_bullish() -> None:
    win = [(101, 100, 100.8), (102, 100.5, 101.5), (107, 101, 106), (104, 101, 103.5), (103, 100.5, 102.5),
           (102, 100.2, 101.2), (101.5, 100.1, 101), (101, 100, 100.6), (100.9, 100, 100.4), (100.8, 100, 100.3)]
    h, l, c, a = _bars(_pre_hit_up() + win + _POST)
    r = _ok(classify_zone_confirmation(h, l, c, LV, side=1, w=W, atr=a))
    assert r.confirmation is ZoneConfirmation.ACCEPTANCE_BULLISH   # persistență 1,0≥0,667 ȘI progres 7≥0,838
    assert r.persistence == 1.0 and r.progress_atr >= P67_PROGRESS


def test_absorption_proxy_bullish() -> None:
    win = [(99.5, 98, 99)] * 10                                  # penetrarea în SUS absorbită: revine sub nivel
    h, l, c, a = _bars(_pre_hit_up() + win + _POST)
    r = _ok(classify_zone_confirmation(h, l, c, LV, side=1, w=W, atr=a))
    assert r.confirmation is ZoneConfirmation.ABSORPTION_PROXY_BULLISH   # persistență 0≤0,0 ȘI progres 0≤0,224
    assert r.persistence == 0.0


def test_acceptance_bearish() -> None:
    win = [(100, 99, 99.2), (99.5, 98, 98.5), (99, 93, 94), (98, 96, 96.5), (97, 95, 95.5),
           (98, 96, 97), (99, 97, 98), (99.5, 98, 98.8), (100, 99, 99.4), (100, 99.5, 99.6)]
    h, l, c, a = _bars(_pre_hit_down() + win + _POST)
    r = _ok(classify_zone_confirmation(h, l, c, LV, side=-1, w=W, atr=a))
    assert r.confirmation is ZoneConfirmation.ACCEPTANCE_BEARISH   # închideri sub nivel + progres 7≥0,838
    assert r.progress_atr >= P67_PROGRESS


def test_absorption_proxy_bearish() -> None:
    win = [(102, 100.5, 101)] * 10                              # penetrarea în JOS absorbită: revine peste nivel
    h, l, c, a = _bars(_pre_hit_down() + win + _POST)
    r = _ok(classify_zone_confirmation(h, l, c, LV, side=-1, w=W, atr=a))
    assert r.confirmation is ZoneConfirmation.ABSORPTION_PROXY_BEARISH
    assert r.persistence == 0.0


def test_undetermined_is_ok_measured_neutral() -> None:
    win = [(100.5, 100, 100.3)] * 10                            # persistență 1,0 DAR progres 0,5<0,838 → nici, nici
    h, l, c, a = _bars(_pre_hit_up() + win + _POST)
    out = classify_zone_confirmation(h, l, c, LV, side=1, w=W, atr=a)
    r = _ok(out)                                               # 0 MĂSURAT = Ok, NU Unavailable
    assert r.confirmation is ZoneConfirmation.UNDETERMINED
    assert r.persistence == 1.0 and r.progress_atr < P67_PROGRESS


# ───────────────────────────── efortul e SATURAT — nu e prag ─────────────────────────────
def test_encounters_saturated_does_not_drive_classification() -> None:
    # 9/10 bare penetrează (encounters mare) DAR închideri straddle (persistență 0,5) + progres 3 → NEDETERMINAT
    win = [(103, 100, 100.5), (103, 100, 99.5), (103, 100, 100.5), (103, 100, 99.5), (103, 100, 100.5),
           (103, 100, 99.5), (103, 100, 100.5), (103, 100, 99.5), (103, 100, 100.5), (99, 98, 98.5)]
    h, l, c, a = _bars(_pre_hit_up() + win + _POST)
    r = _ok(classify_zone_confirmation(h, l, c, LV, side=1, w=W, atr=a))
    assert r.encounters >= 8                                    # EFORT mare
    assert r.confirmation is ZoneConfirmation.UNDETERMINED       # persistență 0,5 ∈ (0, 0,667) → nici, nici


# ───────────────────────────── GRANIȚA DE TIMP: hit+W / hit+W+1, prin perturbare ─────────────────────────────
def test_time_boundary_and_no_lookahead_by_perturbation() -> None:
    win = [(101, 100, 100.8), (102, 100.5, 101.5), (107, 101, 106), (104, 101, 103.5), (103, 100.5, 102.5),
           (102, 100.2, 101.2), (101.5, 100.1, 101), (101, 100, 100.6), (100.9, 100, 100.4), (100.8, 100, 100.3)]
    rows = _pre_hit_up() + win
    post_a = [(200.0, 50.0, 150.0)] * 5                          # viitor EXTREM într-un sens
    post_b = [(100.001, 99.999, 100.0)] * 5                     # viitor EXTREM în alt sens
    ha, la, ca, aa = _bars(rows + post_a)
    hb, lb, cb, ab = _bars(rows + post_b)
    ra = _ok(classify_zone_confirmation(ha, la, ca, LV, side=1, w=W, atr=aa))
    rb = _ok(classify_zone_confirmation(hb, lb, cb, LV, side=1, w=W, atr=ab))
    assert ra.window_end_idx == ra.hit_idx + W                   # fereastra se închide la hit+W
    assert ra.descriptor_available_idx == ra.hit_idx + W + 1     # intrarea abia la hit+W+1
    # barele > hit+W NU pot schimba descriptorul (altfel = condiționare pe rezultat)
    assert ra.confirmation is rb.confirmation
    assert (ra.persistence, ra.progress_atr, ra.encounters) == (rb.persistence, rb.progress_atr, rb.encounters)


# ───────────────────────────── starea contradictorie INEXPRIMABILĂ prin TIP ─────────────────────────────
def test_contradiction_is_inexpressible_by_type() -> None:
    h, l, c, a = _bars(_pre_hit_up() + [(101, 100, 100.5)] * 10 + _POST)
    r = _ok(classify_zone_confirmation(h, l, c, LV, side=1, w=W, atr=a))
    assert isinstance(r.confirmation, ZoneConfirmation)          # O SINGURĂ variabilă ordinală
    for flag in ("absorption", "acceptance", "is_absorption", "is_acceptance"):
        assert not hasattr(r, flag)
        assert flag not in ZoneConfirmationResult.__dataclass_fields__
    assert len(set(ZoneConfirmation)) == 5 and r.confirmation in set(ZoneConfirmation)


# ───────────────────────────── fail-closed → Unavailable (n-am-putut-măsura), NU Ok ─────────────────────────────
def test_fail_closed_incomplete_window_is_unavailable() -> None:
    h, l, c, a = _bars(_pre_hit_up() + [(101, 100, 100.5)] * 2)  # doar 4 bare, W=10 → hit+W depășește seria
    out = classify_zone_confirmation(h, l, c, LV, side=1, w=W, atr=a)
    assert isinstance(out, Unavailable) and out.reason == "incomplete_window"


def test_fail_closed_no_penetration_is_unavailable() -> None:
    h, l, c, a = _bars([(99, 98, 98.5)] * 20)                    # niciun high≥100 → nu intră în populație
    out = classify_zone_confirmation(h, l, c, LV, side=1, w=W, atr=a)
    assert isinstance(out, Unavailable) and out.reason == "no_penetration"


def test_fail_closed_atr_unavailable_is_unavailable() -> None:
    rows = _pre_hit_up() + [(101, 100, 100.5)] * 10 + _POST
    h, l, c, _a = _bars(rows)
    atr_bad = [1.0] * len(rows); atr_bad[1] = float("nan")       # ATR nefinit la HIT
    out = classify_zone_confirmation(h, l, c, LV, side=1, w=W, atr=atr_bad)
    assert isinstance(out, Unavailable) and out.reason == "atr_unavailable"


def test_fail_closed_zone_unavailable_cascades() -> None:
    h, l, c, a = _bars(_pre_hit_up() + [(101, 100, 100.5)] * 10 + _POST)
    out = classify_zone_confirmation(h, l, c, float("nan"), side=1, w=W, atr=a)   # zona N3 absentă
    assert isinstance(out, Unavailable) and out.reason == "zone_unavailable"


def test_fail_closed_invalid_side_is_unavailable() -> None:
    h, l, c, a = _bars(_pre_hit_up() + [(101, 100, 100.5)] * 10 + _POST)
    out = classify_zone_confirmation(h, l, c, LV, side=0, w=W, atr=a)
    assert isinstance(out, Unavailable) and out.reason == "invalid_side"


# ───────────────────────────── constante: W=3 (ceasul), terțile RE-DERIVATE la W=3 ─────────────────────────────
def test_constants_clock_is_w3_and_tertiles_rederived() -> None:
    assert W_DEFAULT == 3                                        # 15 min = o bară M15; cel mai scurt ceas ratificat
    assert (P33_PROGRESS, P67_PROGRESS) == (0.2240, 0.8378)      # terțile pe progres @ W=3 (măsurate, ocupanță egală)
    assert (P33_PERSISTENCE, P67_PERSISTENCE) == (0.0000, 0.6667)   # persistence ∈ {0,⅓,⅔,1} la W=3


def test_no_status_field_status_is_constructor() -> None:
    assert "status" not in ZoneConfirmationResult.__dataclass_fields__   # statusul = Ok/Unavailable, nu câmp
    assert "reason" not in ZoneConfirmationResult.__dataclass_fields__   # reason trăiește pe Unavailable
    assert "schema_hash" not in ZoneConfirmationResult.__dataclass_fields__   # schema_hash trăiește pe Ok


def test_tick_volume_structurally_excluded() -> None:
    import inspect
    params = set(inspect.signature(classify_zone_confirmation).parameters)
    assert not any("vol" in p.lower() for p in params)          # funcția ia DOAR OHLC — volumul nu poate intra
