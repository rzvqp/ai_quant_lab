"""Teste sintetice pentru OBDZ-001 (obdz001.py) — mașina de stare a ipotezei compuse. Array-uri în memorie."""

import os
import sys

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

import obdz001 as OB  # noqa: E402


def _series(n: int = 70):
    """Două OB bullish (A@14, B@39) cu zone care se suprapun, bias up, OB_B mitigat prima dată @50."""
    o = [100.0] * n; h = [100.5] * n; l = [99.5] * n; c = [100.0] * n
    for i in range(1, 15):
        c[i] = 100.0 + (0.15 if i % 2 else -0.15)
    o[14], c[14], h[14], l[14] = 100.0, 99.0, 100.3, 98.8         # OB A: bearish
    o[15], c[15], h[15], l[15] = 98.9, 101.5, 101.7, 98.7         # impuls A → OB bullish, corp [99,100]
    for j in range(16, 39):
        o[j] = h[j] = l[j] = c[j] = 101.5
    o[38], c[38], h[38], l[38] = 101.5, 100.3, 101.6, 100.2
    o[39], c[39], h[39], l[39] = 100.1, 99.2, 100.4, 99.0          # OB B: bearish
    o[40], c[40], h[40], l[40] = 99.0, 101.6, 101.8, 98.9          # impuls B → OB bullish, corp [99.2,100.1]
    for j in range(41, 50):
        o[j] = h[j] = l[j] = c[j] = 102.0
    o[50], c[50], h[50], l[50] = 101.5, 100.2, 101.6, 99.5         # prima mitigare OB_B @50
    for j in range(51, n):
        o[j] = h[j] = l[j] = c[j] = 102.5
    atr = [1.5] * n; h1 = [1.0] * n; h4 = [1.0] * n; day = [0] * n
    return o, h, l, c, atr, h1, h4, day, n


def _sig(series):
    o, h, l, c, atr, h1, h4, day, n = series
    return OB.detect_obdz001_signals(o, h, l, c, atr, h1, h4, day, n)


def test_signal_detected_with_correct_levels():
    o, h, l, c, atr, h1, h4, day, n = _series()
    sigs = _sig((o, h, l, c, atr, h1, h4, day, n))
    assert len(sigs) == 1
    s = sigs[0]
    assert s.trigger_idx == 50 and s.entry_idx == 51 and s.direction == 1
    ep = o[51]                                                    # 102.5
    assert abs(s.sl_price - (ep - 0.7 * 1.5)) < 1e-9              # 0,7×ATR
    assert abs(s.tp1_price - (ep + 1.4 * 1.5)) < 1e-9            # 1,4×ATR
    assert abs(s.tp2_price - (ep + 2.1 * 1.5)) < 1e-9            # 2,1×ATR
    assert s.measurement_start == s.entry_idx and s.measurement_end == min(51 + 20, n - 1)


def test_evaluate_tp2():
    o, h, l, c, atr, h1, h4, day, n = _series()
    s = _sig((o, h, l, c, atr, h1, h4, day, n))[0]
    for j in range(52, 60):                                       # urcă spre TP1 apoi TP2, deasupra breakeven
        o[j] = h[j] = l[j] = c[j] = 103.0
    h[55] = s.tp1_price + 0.1                                     # TP1
    h[58] = s.tp2_price + 0.1                                     # TP2
    r = OB.evaluate_obdz001(s, h, l, c)
    assert r.exit_reason == "tp1_then_tp2" and abs(r.R_leg1 - 2.0) < 1e-9 and abs(r.R_leg2 - 3.0) < 1e-9


def test_evaluate_stop():
    o, h, l, c, atr, h1, h4, day, n = _series()
    s = _sig((o, h, l, c, atr, h1, h4, day, n))[0]
    l[53] = s.sl_price - 0.1                                      # SL înainte de TP1
    r = OB.evaluate_obdz001(s, h, l, c)
    assert r.exit_reason == "stopped_full" and r.R_leg1 == -1.0


def test_bias_mismatch_no_signal():
    o, h, l, c, atr, h1, h4, day, n = _series()
    h1 = [0.0] * n; h4 = [0.0] * n                                # bias down, OB bullish → mismatch
    assert OB.detect_obdz001_signals(o, h, l, c, atr, h1, h4, day, n) == []


def test_no_cross_candle_demandzone_no_signal():
    # eliminăm OB A (bara 14 nu mai e opusă impulsului) → doar OB B; DemandZone_A == propria zonă → exclus
    o, h, l, c, atr, h1, h4, day, n = _series()
    o[14], c[14] = 99.0, 100.0                                    # bara 14 acum bullish → fără OB A
    assert OB.detect_obdz001_signals(o, h, l, c, atr, h1, h4, day, n) == []


def test_atr_floor_excludes():
    o, h, l, c, atr, h1, h4, day, n = _series()
    atr = [0.5] * n                                              # sub podeaua 0,857
    assert OB.detect_obdz001_signals(o, h, l, c, atr, h1, h4, day, n) == []


def test_no_lookahead():
    """Mutarea barelor din fereastra de MĂSURARE (> entry_idx) nu schimbă niciun semnal (selecție ≤ entry_idx)."""
    o, h, l, c, atr, h1, h4, day, n = _series()
    base = _sig((o, h, l, c, atr, h1, h4, day, n))
    key = lambda ss: [(s.trigger_idx, s.entry_idx, s.direction, round(s.sl_price, 6), round(s.tp1_price, 6)) for s in ss]
    before = key(base)
    e = base[0].entry_idx
    for i in range(e + 1, n):                                     # mutăm agresiv fereastra de măsurare
        o[i], h[i], l[i], c[i] = 500.0, 600.0, 50.0, 55.0
    after = key(OB.detect_obdz001_signals(o, h, l, c, atr, h1, h4, day, n))
    assert before == after
