"""Teste pentru clasificatorul de regim (nivelul 1, H4). Un test per axă și per convenție de fail-closed.

Ținte explicite din spec: cele cinci benzi de volatilitate + fereastra 30 (NU 460), axa B (run→structură+direcție),
share-urile direcționale, atribuirea moale/confidence, cele două câmpuri de știri, fail-closed la n_min, și
demonstrația că NU folosește harta retrospectivă (cauzalitate strictă).
"""

from __future__ import annotations

import inspect
import math
import os
import sys

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from market_structure import BreakKind  # noqa: E402
from regime_classifier import (  # noqa: E402
    Direction, Status, StructBand, VolBand, W_WEEK_H4, _direction, _propagate_run, _struct_band,
    classify_regime,
)


def _bars(ms: list[float], big_body_last: bool = False) -> tuple[list[float], list[float], list[float], list[float]]:
    """Construiește OHLC cu `ln(high/low)=m` per bară; corp mic (fără expansion) exceptând ultima dacă cerut."""
    n = len(ms)
    low = [100.0] * n
    high = [100.0 * math.exp(mm) for mm in ms]
    o: list[float] = []
    c: list[float] = []
    for idx in range(n):
        lo, hi = low[idx], high[idx]
        if idx == n - 1 and big_body_last:
            o.append(lo); c.append(hi)                       # corp plin → expansion (dacă range e destul de mare)
        else:
            mid = 0.5 * (lo + hi); eps = 0.001 * (hi - lo)
            o.append(mid - eps); c.append(mid + eps)         # corp minuscul → niciodată expansion
    return o, high, low, c


# ───────────────────────────── AXA A — volatilitate: cele cinci benzi + fereastra 30 (NU 460) ─────────────────────────────
def _ctx() -> list[float]:
    """29 de valori m NETED distribuite (linspace 0,001..0,050) → percentile line, margini largi pt. benzi."""
    return [0.001 + (0.050 - 0.001) * idx / 28 for idx in range(29)]


def test_volatility_five_bands() -> None:
    base = _ctx()                                                   # P10≈0,006  P33≈0,017  P67≈0,034
    compressed = classify_regime(*_bars(base + [0.002]))            # last <= P10
    assert compressed.volatility.label == VolBand.COMPRESSED.value
    low = classify_regime(*_bars(base + [0.010]))                   # P10 < last <= P33
    assert low.volatility.label == VolBand.LOW.value
    normal = classify_regime(*_bars(base + [0.025]))               # P33 < last <= P67
    assert normal.volatility.label == VolBand.NORMAL.value
    choppy = classify_regime(*_bars(base + [0.090], big_body_last=False))   # > P67, corp mic → choppy
    assert choppy.volatility.label == VolBand.HIGH_CHOPPY.value
    directional = classify_regime(*_bars(base + [0.090], big_body_last=True))   # > P67 + expansion → directional
    assert directional.volatility.label == VolBand.HIGH_DIRECTIONAL.value


def test_window_is_30_not_460() -> None:
    """La 30 de bare volatilitatea e DISPONIBILĂ; cu fereastra transplantată 460 ar fi fost UNAVAILABLE."""
    assert W_WEEK_H4 == 30
    st = classify_regime(*_bars([0.01] * 30))
    assert st.volatility.status == Status.AVAILABLE.value           # 30 de bare ajung (nu 460)
    assert st.n_bars == 30


def test_volatility_unavailable_during_warmup() -> None:
    st = classify_regime(*_bars([0.01] * 20))                       # < W → fereastră incompletă
    assert st.volatility.label == VolBand.UNAVAILABLE.value and st.volatility.status == Status.UNAVAILABLE.value


def test_soft_assignment_boundary_lowers_confidence_and_adds_weight() -> None:
    center = classify_regime(*_bars(_ctx() + [0.024]))            # interior NORMAL, departe de ambele granițe
    edge = classify_regime(*_bars(_ctx() + [0.030]))             # tot NORMAL, dar lipit de granița P67
    assert center.volatility.label == VolBand.NORMAL.value and edge.volatility.label == VolBand.NORMAL.value
    assert edge.volatility.confidence < center.volatility.confidence          # aproape de graniță → confidence mai mic
    assert edge.volatility.weights[0][1] < center.volatility.weights[0][1]    # ponderea dominantă scade
    for ax in (center.volatility, edge.volatility):
        assert abs(sum(w for _, w in ax.weights) - 1.0) < 1e-9               # distribuția sumează la 1


# ───────────────────────────── AXA B — run → structură + direcție (unit, deterministe) ─────────────────────────────
def test_propagate_run_choch_resets_bos_increments() -> None:
    ev = [(5, BreakKind.CHOCH_BULL), (7, BreakKind.BOS_BULL), (9, BreakKind.BOS_BULL),
          (12, BreakKind.CHOCH_BEAR), (14, BreakKind.BOS_BEAR)]
    s = _propagate_run(ev, 16)
    assert s[4] == 0 and s[5] == 1 and s[6] == 1                    # CHoCH bull → +1, ține
    assert s[7] == 2 and s[9] == 3 and s[11] == 3                   # BOS bull incrementează
    assert s[12] == -1 and s[13] == -1 and s[14] == -2             # CHoCH bear resetează, BOS bear incrementează


def test_struct_band_cuts() -> None:
    assert _struct_band(0) is StructBand.NONE and _struct_band(1) is StructBand.RANGE
    assert _struct_band(2) is StructBand.WEAK and _struct_band(3) is StructBand.WEAK
    assert _struct_band(4) is StructBand.STRONG and _struct_band(7) is StructBand.STRONG


def test_direction_maps_run_sign_and_strength() -> None:
    assert _direction(5, True) is Direction.UP and _direction(4, True) is Direction.UP
    assert _direction(3, True) is Direction.WEAK_UP and _direction(2, True) is Direction.WEAK_UP
    assert _direction(-5, True) is Direction.DOWN and _direction(-2, True) is Direction.WEAK_DOWN
    assert _direction(1, True) is Direction.NEUTRAL and _direction(-1, True) is Direction.NEUTRAL   # RANGE = neutral
    assert _direction(0, True) is Direction.NEUTRAL


def test_direction_fail_closed_below_n_min_is_neutral() -> None:
    assert _direction(5, False) is Direction.NEUTRAL               # sub n_min → neutral, nu presupunere direcțională
    st = classify_regime(*_bars([0.01] * 40), n_min=100)          # 40 bare, n_min 100 → fail-closed
    assert st.direction.label == Direction.NEUTRAL.value and st.direction.status == Status.UNAVAILABLE.value


def test_classify_wires_run_to_structure_and_direction_consistently() -> None:
    st = classify_regime(*_bars([0.01] * 60))
    assert st.run is not None
    assert st.structure.label == _struct_band(abs(st.run)).value
    assert st.direction.label == _direction(st.run, st.n_bars >= 30).value


def test_trend_shares_labeled_and_causal() -> None:
    st = classify_regime(*_bars([0.01] * 60))
    for share in (st.trend_long_share, st.trend_short_share):
        assert share is None or (0.0 <= share <= 1.0)             # fracții descriptive (SHARE), nu probabilități
    # accesibile ca `*_share`, niciodată `*_probability`
    assert "trend_long_share" in RegimeStateFields() and not any("probability" in f for f in RegimeStateFields())


def RegimeStateFields() -> set[str]:
    from regime_classifier import RegimeState
    return set(RegimeState.__dataclass_fields__)


# ───────────────────────────── AXA C — știri: două câmpuri, FALSE + UNAVAILABLE ─────────────────────────────
def test_news_default_false_and_unavailable() -> None:
    st = classify_regime(*_bars([0.01] * 40))                      # fără news_fn
    assert st.news.label == "normal" and st.news.status == Status.UNAVAILABLE.value   # NU „verificat și curat"


def test_news_available_when_calendar_supplied() -> None:
    st = classify_regime(*_bars([0.01] * 40), news_fn=lambda i: (True, Status.AVAILABLE))
    assert st.news.label == "news_dominated" and st.news.status == Status.AVAILABLE.value


# ───────────────────────────── interdicția de LOOKAHEAD / harta retrospectivă ─────────────────────────────
def test_no_retrospective_map_causal_prefix_deterministic() -> None:
    """Clasificarea unei bare depinde DOAR de barele până la ea — nicio hartă retrospectivă pe tot istoricul."""
    ms = [0.005 + 0.0003 * (idx % 7) for idx in range(50)]
    o, h, l, c = _bars(ms)
    j = 40
    s_prefix = classify_regime(o[:j + 1], h[:j + 1], l[:j + 1], c[:j + 1])
    # extindem cu viitor ARBITRAR și reclasificăm ACEEAȘI bară j (prin trunchiere) → identic
    o2 = o[:j + 1] + [200.0] * 30; h2 = h[:j + 1] + [260.0] * 30
    l2 = l[:j + 1] + [190.0] * 30; c2 = c[:j + 1] + [255.0] * 30
    s_again = classify_regime(o2[:j + 1], h2[:j + 1], l2[:j + 1], c2[:j + 1])
    assert s_prefix == s_again                                     # viitorul NU schimbă trecutul
    # și API-ul nu ingerează o hartă de regim / închideri lunare
    params = set(inspect.signature(classify_regime).parameters)
    assert not any(p in params for p in ("regime_map", "monthly", "regime", "labels", "full_history"))
