"""Teste sintetice pentru trading_strategies.py — familiile SMC_S* ca mașini de stare (Mandat 5.9).

Array-uri în memorie, fără CSV, fără .load(). Pentru fiecare familie: semnalele se activează corect,
eligibilitatea filtrează, fără suprapuneri distructive (același entry + direcții opuse). Și testul
anti-lookahead: mutarea barelor din fereastra de MĂSURARE nu schimbă niciun semnal (selecția ≤ entry_idx).
"""

import os
import sys
from typing import Callable, Sequence

import numpy as np

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from market_structure import Block  # noqa: E402
from institutional_levels import derive_week_index  # noqa: E402
import trading_strategies as TS  # noqa: E402

Detector = Callable[..., list[TS.StrategySignal]]


def _zz(pivots: list[tuple[int, float, str]], n: int, w: float = 0.2):
    idxs = [p[0] for p in pivots]; prices = [p[1] for p in pivots]
    base = np.interp(range(n), idxs, prices)
    return ([float(x) for x in base], (base + w).tolist(), (base - w).tolist(), [float(x) for x in base])


# ── serii verificate ────────────────────────────────────────────────────────────────────────────
def _trend_series():  # BOS_BULL @16, @24; CHOCH_BEAR @27,@28 → alimentează S2/S7/S10/S11
    n = 32
    piv = [(2, 100.0, "L"), (5, 103.0, "H"), (8, 101.0, "L"), (11, 104.0, "H"), (14, 102.0, "L"),
           (17, 105.5, "H"), (20, 103.0, "L"), (24, 106.0, "H"), (28, 101.0, "L")]
    o, h, l, c = _zz(piv, n)
    return o, h, l, c, [Block(0, n)], n


def _sweep_series():  # sweep al unui pool ABOVE @16 → S1
    n = 20
    piv = [(2, 100.0, "L"), (5, 105.0, "H"), (8, 101.0, "L"), (11, 104.0, "H"), (14, 101.5, "L")]
    o, h, l, c = _zz(piv, n)
    o[16], h[16], l[16], c[16] = 103.0, 107.0, 102.5, 103.0     # fitil peste pool, close înapoi sub
    return o, h, l, c, [Block(0, n)], n


def _retest_series():  # BOS_BULL @16 apoi retest cu bară largă de respingere @19 → S3
    n = 26
    piv = [(2, 100.0, "L"), (5, 103.0, "H"), (8, 101.0, "L"), (11, 104.0, "H"), (14, 102.0, "L"), (17, 105.5, "H")]
    o, h, l, c = _zz(piv, n)
    o[19], h[19], l[19], c[19] = 105.5, 106.6, 104.1, 106.4
    o[20], h[20], l[20], c[20] = 106.5, 107.0, 106.2, 106.8
    for i in range(21, n):
        o[i] = h[i] = l[i] = c[i] = 106.8
    return o, h, l, c, [Block(0, n)], n


def _pdh_series():  # day0 PDH=105 disponibil @10, atins @14 în day1 → S16 short
    n = 20
    day = [0] * 10 + [1] * 10
    base = [100, 101, 102, 103, 104, 103, 102, 101, 100.5, 101,
            102, 103, 104, 103.5, 104.8, 102.5, 103, 102.5, 103, 102.5]
    o = [float(x) for x in base]; c = [float(x) for x in base]
    h = [b + 0.3 for b in base]; l = [b - 0.3 for b in base]
    h[4], l[4], l[0] = 105.0, 104.5, 99.7
    h[14], l[14], o[14], c[14] = 105.1, 102.2, 103.0, 102.5     # fitil la PDH, close reject
    o[15], c[15], h[15], l[15] = 102.8, 102.8, 103.1, 102.5
    return o, h, l, c, [Block(0, n)], n, day


def _weekly_series(week0_days: int = 5):  # week0 (N zile) HIGH=110 atins în week1
    day_ord: list[int] = []
    for d in range(week0_days):
        day_ord += [d] * 5
    day_ord += [7] * 8                                          # gol de weekend → week1
    n = len(day_ord)
    wk = derive_week_index(day_ord)
    base = [100 + (i % 5) for i in range(5 * week0_days)] + [108, 109, 108, 109, 108, 109, 108, 109]
    o = [float(x) for x in base]; c = [float(x) for x in base]
    h = [b + 0.3 for b in base]; l = [b - 0.3 for b in base]
    hi_bar = 12 if week0_days >= 3 else 2
    h[hi_bar], l[hi_bar], l[2] = 110.0, 109.5, 99.0            # week0 HIGH=110
    w1 = 5 * week0_days + 2                                     # o bară în week1
    h[w1], l[w1], o[w1], c[w1] = 110.1, 107.8, 108.5, 108.0    # fitil la weekly high, reject
    o[w1 + 1], c[w1 + 1], h[w1 + 1], l[w1 + 1] = 108.2, 108.2, 108.5, 108.0
    return o, h, l, c, [Block(0, n)], n, day_ord, wk


def _fvg_series():  # FVG bullish (formed_idx 5, gap [100.5,102.5], ce 101.5) + atingere CE-50 @11 → S13
    n = 22
    o = [99.0, 99.5, 100.0, 100.2, 100.3, 101.3, 103.0, 103.5, 103.6, 103.5, 103.4, 102.0, 103.6, 104.0] + [104.0] * 8
    h = [99.3, 99.8, 100.3, 100.5, 100.5, 101.6, 103.3, 103.8, 103.9, 103.8, 103.7, 102.3, 103.9, 104.3] + [104.3] * 8
    l = [98.7, 99.2, 99.7, 99.9, 100.1, 101.0, 102.5, 103.2, 103.3, 103.2, 103.1, 101.4, 103.3, 103.7] + [103.7] * 8
    c = [99.0, 99.5, 100.0, 100.2, 100.3, 101.3, 103.0, 103.5, 103.6, 103.5, 103.4, 103.5, 103.6, 104.0] + [104.0] * 8
    return o, h, l, c, [Block(0, n)], n


# ── activare per familie ────────────────────────────────────────────────────────────────────────
def test_s1_sweep_reversal_activates():
    o, h, l, c, B, n = _sweep_series()
    sig = TS.detect_s1(o, h, l, c, B)
    assert len(sig) >= 1
    s = sig[0]
    assert s.direction == -1 and s.family == "S1"
    assert TS.ELIG_LO <= s.spike_pips < TS.ELIG_HI
    assert s.entry_idx == s.trigger_idx + 1
    assert s.measurement_end == min(s.entry_idx + TS.HORIZON_GROUP_A, n)


def test_s2_failed_breakout_fade_activates():
    o, h, l, c, B, n = _trend_series()
    sig = TS.detect_s2(o, h, l, c, B)
    assert len(sig) >= 1
    assert all(s.direction == -1 and s.family == "S2" for s in sig)   # fade după BOS_BULL


def test_s3_breakout_retest_activates():
    o, h, l, c, B, n = _retest_series()
    sig = TS.detect_s3(o, h, l, c, B)
    assert len(sig) == 1
    assert sig[0].direction == +1 and sig[0].family == "S3"


def test_s7_trend_pullback_activates():
    o, h, l, c, B, n = _trend_series()
    sig = TS.detect_s7(o, h, l, c, B)
    assert len(sig) >= 1 and all(s.direction == +1 and s.family == "S7" for s in sig)


def test_s10_displacement_continuation_activates():
    o, h, l, c, B, n = _trend_series()
    sig = TS.detect_s10(o, h, l, c, B)
    assert len(sig) >= 1 and all(s.family == "S10" for s in sig)
    assert any(s.direction == +1 for s in sig)


def test_s11_structure_break_reversal_activates():
    o, h, l, c, B, n = _trend_series()
    sig = TS.detect_s11(o, h, l, c, B)
    assert len(sig) >= 1 and all(s.direction == -1 and s.family == "S11" for s in sig)


def test_s13_imbalance_fill_activates():
    o, h, l, c, B, n = _fvg_series()
    sig = TS.detect_s13(o, h, l, c, B)
    assert len(sig) >= 1 and all(s.family == "S13" for s in sig)
    longs = [s for s in sig if s.direction == +1]
    assert longs and all(TS.ELIG_LO <= s.spike_pips < TS.ELIG_HI for s in sig)   # bullish FVG → long
    assert all(s.measurement_end == min(s.entry_idx + TS.HORIZON_GROUP_A, n) for s in sig)


def test_s16_prior_day_levels_activates():
    o, h, l, c, B, n, day = _pdh_series()
    sig = TS.detect_s16(o, h, l, c, day, B)
    assert len(sig) == 1
    s = sig[0]
    assert s.direction == -1 and s.family == "S16"             # respingere PDH → short
    assert TS.ELIG_LO <= s.spike_pips < TS.ELIG_HI
    assert s.measurement_end == min(s.entry_idx + TS.HORIZON_GROUP_C_DAY, n)


def test_s17_weekly_levels_activates_complete_only():
    o, h, l, c, B, n, day, wk = _weekly_series(week0_days=5)
    sig = TS.detect_s17(o, h, l, c, day, wk, B)
    assert len(sig) == 1
    s = sig[0]
    assert s.direction == -1 and s.family == "S17"
    assert s.measurement_end == min(s.entry_idx + TS.HORIZON_GROUP_C_WEEK, n)


def test_s17_excludes_partial_weekly():
    # week0 are doar 3 zile → PARTIAL → exclus din populația primară, chiar dacă e atins
    o, h, l, c, B, n, day, wk = _weekly_series(week0_days=3)
    assert TS.detect_s17(o, h, l, c, day, wk, B) == []


def test_eligibility_filter_skips_out_of_band():
    # spike prea mic: pool foarte aproape de intrare → skip
    n = 20
    piv = [(2, 100.0, "L"), (5, 100.3, "H"), (8, 100.0, "L"), (11, 100.2, "H"), (14, 100.0, "L")]
    o, h, l, c = _zz(piv, n)
    o[16], h[16], l[16], c[16] = 100.25, 100.35, 100.2, 100.25   # sweep minuscul → spike ~ 1 pip
    assert TS.detect_s1(o, h, l, c, [Block(0, n)]) == []


# ── anti-lookahead: mutarea ferestrei de măsurare NU schimbă semnalele ─────────────────────────────
def _assert_no_lookahead(fn: Detector, series) -> None:
    o, h, l, c, B, n = series
    base = fn(o, h, l, c, B)
    assert base, "seria trebuie să producă cel puțin un semnal"
    s = base[0]
    key = lambda sig: [(x.trigger_idx, x.entry_idx, x.direction, round(x.spike_pips, 4))
                       for x in sig if x.entry_idx <= s.entry_idx]
    before = key(base)
    # mutăm agresiv barele din fereastra de MĂSURARE a primului semnal (strict > entry_idx)
    o2, h2, l2, c2 = list(o), list(h), list(l), list(c)
    for i in range(s.entry_idx + 1, min(s.measurement_end, n)):
        o2[i], h2[i], l2[i], c2[i] = 500.0, 600.0, 50.0, 55.0
    after = key(fn(o2, h2, l2, c2, B))
    assert before == after


def test_no_lookahead_all():
    _assert_no_lookahead(TS.detect_s1, _sweep_series())
    _assert_no_lookahead(TS.detect_s3, _retest_series())
    _assert_no_lookahead(TS.detect_s13, _fvg_series())
    for fn in (TS.detect_s2, TS.detect_s7, TS.detect_s10, TS.detect_s11):
        _assert_no_lookahead(fn, _trend_series())
    # S16/S17 poartă day_index/week_index (fixe); le împachetăm pentru același helper
    o, h, l, c, B, n, day = _pdh_series()
    _assert_no_lookahead(lambda o_, h_, l_, c_, B_: TS.detect_s16(o_, h_, l_, c_, day, B_),
                         (o, h, l, c, B, n))
    o, h, l, c, B, n, day, wk = _weekly_series(5)
    _assert_no_lookahead(lambda o_, h_, l_, c_, B_: TS.detect_s17(o_, h_, l_, c_, day, wk, B_),
                         (o, h, l, c, B, n))


def test_no_destructive_overlap():
    # niciun semnal cu ACELAȘI entry și direcții OPUSE în cadrul aceleiași familii
    o16, h16, l16, c16, B16, n16, day16 = _pdh_series()
    o17, h17, l17, c17, B17, n17, day17, wk17 = _weekly_series(5)
    cases: list[list[TS.StrategySignal]] = [
        TS.detect_s2(*_trend_series()[:5]), TS.detect_s7(*_trend_series()[:5]),
        TS.detect_s10(*_trend_series()[:5]), TS.detect_s11(*_trend_series()[:5]),
        TS.detect_s1(*_sweep_series()[:5]), TS.detect_s3(*_retest_series()[:5]),
        TS.detect_s13(*_fvg_series()[:5]),
        TS.detect_s16(o16, h16, l16, c16, day16, B16),
        TS.detect_s17(o17, h17, l17, c17, day17, wk17, B17),
    ]
    for sig in cases:
        by_entry: dict[int, set[int]] = {}
        for s in sig:
            by_entry.setdefault(s.entry_idx, set()).add(s.direction)
        assert all(len(dirs) == 1 for dirs in by_entry.values())


def test_s15_and_gaps_not_implemented():
    assert "S15" in TS.UNFORMALIZED_FAMILIES
    assert "GENUIN GOL" in TS.UNFORMALIZED_FAMILIES["S15"]
    assert not hasattr(TS, "detect_s15")


def test_net_R_signature_exists_but_is_not_price_free():
    # net_R e o SEMNĂTURĂ; produce un număr doar cu prețuri furnizate explicit (Corecția 3)
    o, h, l, c, B, n = _sweep_series()
    s = TS.detect_s1(o, h, l, c, B)[0]
    r = TS.net_R(s, entry_price=100.0, exit_price=101.0)
    assert isinstance(r, float)
