"""Teste sintetice pentru Modulul 6 (market_state.py) — Compression / Expansion / Sessions.

Array-uri în memorie, fără CSV, fără .load(). Acoperă ATR14 verbatim, criteriul E010 de expansiune,
sesiunile mtf.py:38, și — cerut explicit — ABSENȚA LOOKAHEAD-ului la compresie (o bară nu poate fi
clasificată folosind date de după ea).
"""

import math
import os
import sys

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from market_state import (  # noqa: E402
    ATR_WINDOW, atr14, compression, expansion, session_of, sessions,
)


def test_atr14_warmup_nan_then_matches_rolling_mean():
    n = 20
    high = [10.0 + i * 0.1 for i in range(n)]
    low = [9.0 + i * 0.1 for i in range(n)]
    close = [9.5 + i * 0.1 for i in range(n)]
    a = atr14(high, low, close)
    assert all(math.isnan(a[i]) for i in range(ATR_WINDOW))       # NaN până la index 14
    assert not math.isnan(a[ATR_WINDOW])                           # prima valoare validă la 14
    # true range constant (h-l=1, gaps mici) → ATR ≈ 1.0
    assert abs(a[ATR_WINDOW] - 1.0) < 0.2


def test_expansion_matches_e010_criterion():
    # 15 bare mici (range≈1) ca să existe ATR14, apoi o bară de deplasare puternică
    n = 17
    open_ = [100.0] * n
    high = [101.0] * n
    low = [100.0] * n
    close = [100.5] * n
    i = 16
    high[i], low[i], open_[i], close[i] = 110.0, 100.0, 100.0, 109.0   # range=10 >> 1.5×ATR(≈1); body=9>=0.5×10
    ex = expansion(open_, high, low, close)
    assert ex[i] is True
    assert sum(ex) == 1                                             # doar bara de deplasare


def test_expansion_rejects_weak_body():
    n = 17
    open_ = [100.0] * n
    high = [101.0] * n
    low = [100.0] * n
    close = [100.5] * n
    i = 16
    high[i], low[i], open_[i], close[i] = 110.0, 100.0, 105.0, 105.2  # range=10 dar body=0.2 < 0.5×10
    assert expansion(open_, high, low, close)[i] is False


def test_compression_flags_low_range_bar():
    # fereastră mică pt. test; 30 bare normale, una foarte îngustă la final
    n = 30
    high = [101.0] * n
    low = [100.0] * n
    high[29], low[29] = 100.05, 100.0                              # log-range foarte mic
    comp, valid = compression(high, low, window=20, pctl=10.0)
    assert valid[29] is True and comp[29] is True
    assert valid[0] is False and comp[0] is False                 # warmup: fără fereastră completă


def test_compression_no_lookahead():
    """O bară nu poate fi clasificată folosind date de DUPĂ ea (cerut explicit)."""
    n = 60
    high = [101.0 + (i % 5) * 0.2 for i in range(n)]
    low = [100.0] * n
    comp_base, valid_base = compression(high, low, window=20, pctl=10.0)
    target = 30
    base_flag = comp_base[target]
    # mutăm agresiv toate barele de DUPĂ target
    for i in range(target + 1, n):
        high[i], low[i] = 500.0, 100.0
    comp_mut, valid_mut = compression(high, low, window=20, pctl=10.0)
    assert valid_mut[target] == valid_base[target]
    assert comp_mut[target] == base_flag                          # clasificarea lui `target` neschimbată


def test_compression_window_is_causal_vs_full_history():
    # demonstrează că fereastra rulantă diferă de percentila pe tot istoricul (motivul anti-lookahead)
    n = 40
    high = [100.5] * 20 + [200.0] * 20        # a doua jumătate foarte volatilă
    low = [100.0] * n
    comp, valid = compression(high, low, window=10, pctl=10.0)
    # o bară din prima jumătate (îngustă) e clasificată doar față de vecinii ei trailing, nu față de spike-urile viitoare
    assert valid[15] is True                   # are fereastră completă (bare 6..15)


def test_sessions_four_labels_no_fifth():
    base = 1_700_000_000  # o zi oarecare, UTC
    # construim epoci la ore UTC cunoscute
    def at_hour(h: int) -> int:
        day = base - (base % 86400)
        return day + h * 3600
    assert session_of(at_hour(3)) == "asia"
    assert session_of(at_hour(10)) == "london"
    assert session_of(at_hour(15)) == "ny"
    assert session_of(at_hour(23)) == "late"
    labels = set(sessions([at_hour(h) for h in range(24)]))
    assert labels == {"asia", "london", "ny", "late"}             # exact patru, nicio a cincea
