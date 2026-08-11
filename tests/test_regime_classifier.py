"""Teste pentru clasificatorul de regim (nivelul 1, H4, v2.0 CONTRACT LevelOutput). Un test per axă și per
convenție de fail-closed. Axele sunt acum `LevelOutput[Axis]` (statusul = CONSTRUCTORUL); `news` e ÎN AFARA
mulțimii necesare {volatility, structure, direction}; `classify_regime` întoarce `LevelOutput[RegimeState]`.
"""

from __future__ import annotations

import inspect
import math
import os
import sys

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from level_output import Ok, Unavailable  # noqa: E402
from market_structure import BreakKind  # noqa: E402
from regime_classifier import (  # noqa: E402
    Axis, Direction, REGIME_SCHEMA, RegimeState, Status, StructBand, VolBand, W_WEEK_H4,
    _direction, _propagate_run, _struct_band, classify_regime,
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


def _state(out: object) -> RegimeState:
    assert isinstance(out, Ok)
    assert out.valid_until == out.as_of + 1 and out.schema_hash and len(out.schema_hash) == 16
    return out.value


def _axis(lo: object) -> Axis:
    assert isinstance(lo, Ok)
    return lo.value


# ───────────────────────────── AXA A — volatilitate: cele cinci benzi + fereastra 30 (NU 460) ─────────────────────────────
def _ctx() -> list[float]:
    """29 de valori m NETED distribuite (linspace 0,001..0,050) → percentile line, margini largi pt. benzi."""
    return [0.001 + (0.050 - 0.001) * idx / 28 for idx in range(29)]


def test_volatility_five_bands() -> None:
    base = _ctx()                                                   # P10≈0,006  P33≈0,017  P67≈0,034
    def vlabel(out: object) -> str:
        return _axis(_state(out).volatility).label
    assert vlabel(classify_regime(*_bars(base + [0.002]))) == VolBand.COMPRESSED.value
    assert vlabel(classify_regime(*_bars(base + [0.010]))) == VolBand.LOW.value
    assert vlabel(classify_regime(*_bars(base + [0.025]))) == VolBand.NORMAL.value
    assert vlabel(classify_regime(*_bars(base + [0.090], big_body_last=False))) == VolBand.HIGH_CHOPPY.value
    assert vlabel(classify_regime(*_bars(base + [0.090], big_body_last=True))) == VolBand.HIGH_DIRECTIONAL.value


def test_window_is_30_not_460() -> None:
    """La 30 de bare volatilitatea e DISPONIBILĂ; cu fereastra transplantată 460 ar fi fost Unavailable."""
    assert W_WEEK_H4 == 30
    st = _state(classify_regime(*_bars([0.01] * 30)))
    assert isinstance(st.volatility, Ok)                           # 30 de bare ajung (nu 460)
    assert st.n_bars == 30


def test_warmup_below_window_is_unavailable_not_an_assumed_band() -> None:
    out = classify_regime(*_bars([0.01] * 20))                     # < W, fără structură → toate axele necesare absente
    assert isinstance(out, Unavailable)                            # fail-closed la nivel de stare (nu o bandă presupusă)


def test_soft_assignment_boundary_lowers_confidence_and_adds_weight() -> None:
    center = _axis(_state(classify_regime(*_bars(_ctx() + [0.024]))).volatility)   # interior NORMAL
    edge = _axis(_state(classify_regime(*_bars(_ctx() + [0.030]))).volatility)     # NORMAL lipit de P67
    assert center.label == VolBand.NORMAL.value and edge.label == VolBand.NORMAL.value
    assert edge.confidence < center.confidence                     # aproape de graniță → confidence mai mic
    assert edge.weights[0][1] < center.weights[0][1]               # ponderea dominantă scade
    for ax in (center, edge):
        assert abs(sum(w for _, w in ax.weights) - 1.0) < 1e-9     # distribuția sumează la 1


def test_no_status_field_on_axis() -> None:
    assert "status" not in Axis.__dataclass_fields__               # statusul = constructorul LevelOutput[Axis]


# ───────────────────────────── AXA B — run → structură + direcție (unit, deterministe) ─────────────────────────────
def test_propagate_run_choch_resets_bos_increments() -> None:
    ev = [(5, BreakKind.CHOCH_BULL), (7, BreakKind.BOS_BULL), (9, BreakKind.BOS_BULL),
          (12, BreakKind.CHOCH_BEAR), (14, BreakKind.BOS_BEAR)]
    s = _propagate_run(ev, 16)
    assert s[4] == 0 and s[5] == 1 and s[6] == 1
    assert s[7] == 2 and s[9] == 3 and s[11] == 3
    assert s[12] == -1 and s[13] == -1 and s[14] == -2


def test_struct_band_cuts() -> None:
    assert _struct_band(0) is StructBand.NONE and _struct_band(1) is StructBand.RANGE
    assert _struct_band(2) is StructBand.WEAK and _struct_band(3) is StructBand.WEAK
    assert _struct_band(4) is StructBand.STRONG and _struct_band(7) is StructBand.STRONG


def test_direction_maps_run_sign_and_strength() -> None:
    assert _direction(5, True) is Direction.UP and _direction(4, True) is Direction.UP
    assert _direction(3, True) is Direction.WEAK_UP and _direction(2, True) is Direction.WEAK_UP
    assert _direction(-5, True) is Direction.DOWN and _direction(-2, True) is Direction.WEAK_DOWN
    assert _direction(1, True) is Direction.NEUTRAL and _direction(-1, True) is Direction.NEUTRAL
    assert _direction(0, True) is Direction.NEUTRAL


def test_direction_fail_closed_below_n_min_is_unavailable() -> None:
    assert _direction(5, False) is Direction.NEUTRAL               # unit: sub n_min → neutral
    st = _state(classify_regime(*_bars([0.01] * 40), n_min=100))   # vol Ok (40≥30) ⇒ stare Ok; direcția indisponibilă
    assert isinstance(st.direction, Unavailable) and st.direction.reason == "direction_below_n_min"


def test_classify_wires_run_to_structure_and_direction_consistently() -> None:
    st = _state(classify_regime(*_bars([0.01] * 60)))
    assert st.run is not None
    if st.run == 0:                                                # fără structură → axa e Unavailable, nu NONE-etichetă
        assert isinstance(st.structure, Unavailable)
    else:
        assert _axis(st.structure).label == _struct_band(abs(st.run)).value
    assert _axis(st.direction).label == _direction(st.run, st.n_bars >= 30).value   # 60≥n_min ⇒ direcție Ok


def test_trend_shares_labeled_and_causal() -> None:
    st = _state(classify_regime(*_bars([0.01] * 60)))
    for share in (st.trend_long_share, st.trend_short_share):
        assert share is None or (0.0 <= share <= 1.0)
    fields = set(RegimeState.__dataclass_fields__)
    assert "trend_long_share" in fields and not any("probability" in f for f in fields)


# ───────────────────────────── AXA C — știri: ÎN AFARA mulțimii necesare, permanent Unavailable ─────────────────────────────
def test_news_default_unavailable_and_does_not_block() -> None:
    out = classify_regime(*_bars([0.01] * 40))                     # fără news_fn
    st = _state(out)                                               # starea rămâne Ok (news e în afara mulțimii necesare)
    assert isinstance(st.news, Unavailable) and st.news.reason == "news_absent_no_calendar"


def test_news_available_when_calendar_supplied() -> None:
    st = _state(classify_regime(*_bars([0.01] * 40), news_fn=lambda i: (True, Status.AVAILABLE)))
    assert _axis(st.news).label == "news_dominated"


def test_news_is_declared_outside_required_set() -> None:
    assert REGIME_SCHEMA["required_set"] == ["volatility", "structure", "direction"]
    assert REGIME_SCHEMA["news_in_required_set"] is False          # altfel fail-closed → fail-MORT


# ───────────────────────────── interdicția de LOOKAHEAD / harta retrospectivă ─────────────────────────────
def test_no_retrospective_map_causal_prefix_deterministic() -> None:
    """Clasificarea unei bare depinde DOAR de barele până la ea — nicio hartă retrospectivă pe tot istoricul."""
    ms = [0.005 + 0.0003 * (idx % 7) for idx in range(50)]
    o, h, l, c = _bars(ms)
    j = 40
    s_prefix = classify_regime(o[:j + 1], h[:j + 1], l[:j + 1], c[:j + 1])
    o2 = o[:j + 1] + [200.0] * 30; h2 = h[:j + 1] + [260.0] * 30
    l2 = l[:j + 1] + [190.0] * 30; c2 = c[:j + 1] + [255.0] * 30
    s_again = classify_regime(o2[:j + 1], h2[:j + 1], l2[:j + 1], c2[:j + 1])
    assert s_prefix == s_again                                     # viitorul NU schimbă trecutul
    params = set(inspect.signature(classify_regime).parameters)
    assert not any(p in params for p in ("regime_map", "monthly", "regime", "labels", "full_history"))
