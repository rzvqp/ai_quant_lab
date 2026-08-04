"""CLASIFICATORUL DE REGIM — nivelul 1, pe H4 (STAT-LEVEL1-REGIME-H4-SPEC-v1.0, 7a9013d, manifest v2.7.49).

Funcție PURĂ pe barele H4 până la momentul deciziei (clasifică bara CURENTĂ = ultima). Fără MT5, fără date reale.
Construită STRICT după spec — NU reconstitui din mesaj. **Spec-ul REVIZUIEȘTE încadrarea în „nouă stări":**

  Cele nouă „stări" sunt AXE (măsurat, nu presupus):
    AXA A — VOLATILITATE (o variabilă, măsura Parkinson E000 `ln(h/l)`, fereastra CAUZALĂ [i-29,i]):
            COMPRESSED (<=P10) | LOW (P10..P33) | NORMAL (P33..P67) | HIGH_CHOPPY | HIGH_DIRECTIONAL(=expansion)
            → compresia e DECILA INFERIOARĂ a volatilității; expansiunea e 99,5% în banda HIGH ⇒ NU sunt axe separate.
    AXA B — STRUCTURĂ + DIRECȚIE (din `detect_breaks` ratificat, cascadă v2.7.38): `run` = nr. de BOS consecutive
            de același semn de la ultimul CHoCH opus, CU SEMN. Persistență: RANGE(|run|=1) | WEAK(2-3) | STRONG(>=4).
            Direcția = SEMNUL lui run (nu EMA/ADX — ar fi a treia definiție de structură, RESPINSĂ de spec).
    AXA C — ȘTIRI: value(bool) + status(AVAILABLE/UNAVAILABLE), două câmpuri.

**Divergență semnalată (spec vs mesaj), pentru CEO/Red Team:** mesajul rezumă DIRECTION ca „din EMA pe bare
închise"; spec-ul autoritar o derivă din SEMNUL run-ului BOS (axa B), tocmai ca să NU introducă a treia definiție
de direcție/structură (motivul pentru care ADX a fost respins). Urmez spec-ul („nu reconstitui din acest mesaj").

DECIZII CHEIE (din spec):
  · `COMPRESSION_WINDOW=460` e un TRANSPLANT DE UNITATE pe H4 (= trimestru, nu săptămână) → RE-DERIVAT la W=30
    (media empirică de săptămână H4 = 29,84). Eroarea era INDETECTABILĂ în aval (o percentilă dă ~aceeași rată la
    orice fereastră) → se prinde la specificație sau deloc.
  · Pragul puternic/slab NU e derivabil (run-urile sunt geometrice = fără memorie) → ALEGERE, ancorată pe ocupanță
    egală: RANGE(|run|=1) 31,7% | WEAK(2-3) 30,2% | STRONG(>=4) 37,9%. RANGE = INSTABILITATE (direcție proaspăt
    răsturnată), NU absența structurii (99,88% din bare au run nenul).
  · „Trend Long: 82%" NU e o previziune → `trend_long_share`/`trend_short_share`, etichetate `share`, pe [i-29,i].
  · CONFIDENCE nu e câmp/poartă separat: e FRAGILITATEA de frontieră (distanța normalizată până la granița benzii);
    atribuire MOALE care propagă incertitudinea la nivelul 6 (interval mai lat ⇒ EV_LCB cade). Nicio poartă la nivel 1.
  · Contracția ierarhică (nivelul 6) NU se aplică aici: nivelul 1 CLASIFICĂ determinist (produce cheia), nu estimează.

FAIL-CLOSED:
  · sub `n_min`, DIRECȚIA = NEUTRAL (nu o presupunere direcțională); la fel RANGE(|run|=1) = neutral (instabil).
  · VOLATILITATEA sub fereastra completă (i < W-1) = UNAVAILABLE (warmup), nu o bandă presupusă.
  · ȘTIRILE: value=FALSE + status=UNAVAILABLE (NU se confundă cu „verificat și curat"). AMBIGUU ≠ INDISPONIBIL.

INTERZIS: harta retrospectivă bear/bull/corecție (închideri lunare pe TOT istoricul = lookahead maxim). Totul aici
e cauzal: ferestre [i-W+1, i], run din break-uri cu idx<=i. Programul de știri (calendar) e cauzal; REZULTATUL nu.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Sequence

import numpy as np

from market_state import expansion
from market_structure import Block, BreakKind, detect_breaks, detect_swings, label_structure

# Constante DERIVATE / ALESE (marcate). NU se transplantează 460.
W_WEEK_H4: int = 30              # DERIVAT: media empirică de săptămână H4 = 29,84 (NU 460 = trimestru)
PCTL_COMPRESSED: float = 10.0    # P10 = default declarat al spec-ului (reutilizat, ca `compression`)
PCTL_LOW: float = 33.0           # ALEGERE (terțilă, ocupanță egală maximizează celula minimă)
PCTL_HIGH: float = 67.0          # ALEGERE (terțilă)
RUN_WEAK_MIN: int = 2            # ALEGERE ancorată pe ocupanță egală: WEAK = |run| in {2,3}
RUN_STRONG_MIN: int = 4          # STRONG = |run| >= 4
K_SWING_DEFAULT: int = 2         # k pentru detect_swings (default de laborator)
N_MIN_DEFAULT: int = 30          # sub acesta, DIRECȚIA = neutral (fail-closed)


class VolBand(Enum):
    COMPRESSED = "compressed"
    LOW = "low"
    NORMAL = "normal"
    HIGH_CHOPPY = "high_choppy"
    HIGH_DIRECTIONAL = "high_directional"
    UNAVAILABLE = "unavailable"


class StructBand(Enum):
    NONE = "none"                # fără structură (warmup / niciun break) — 0,1% din bare
    RANGE = "range"              # |run| == 1 — direcție proaspăt răsturnată, INSTABILĂ
    WEAK = "weak"                # |run| in {2,3}
    STRONG = "strong"            # |run| >= 4


class Direction(Enum):
    DOWN = "down"                # DOWN_STRONG
    WEAK_DOWN = "weak_down"      # DOWN_WEAK
    NEUTRAL = "neutral"          # RANGE / fără structură / sub n_min (fail-closed)
    WEAK_UP = "weak_up"          # UP_WEAK
    UP = "up"                    # UP_STRONG


class Status(Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class Axis:
    """O axă: eticheta + distribuția MOALE (probabilități de bandă sub fragilitate) + confidence + status."""
    label: str
    weights: tuple[tuple[str, float], ...]     # distribuție moale (etichetă→pondere), sumează ~1 când e disponibilă
    confidence: float                          # [0,1]; 0 pe o graniță (ambiguu), 1 adânc în bandă
    status: str                                # AVAILABLE / UNAVAILABLE


@dataclass(frozen=True)
class RegimeState:
    volatility: Axis
    structure: Axis
    direction: Axis
    news: Axis
    trend_long_share: float | None             # SHARE descriptiv pe [i-29,i], NU o probabilitate/previziune
    trend_short_share: float | None
    run: int | None                            # run cu semn la bara curentă
    as_of_index: int
    n_bars: int


NewsFn = Callable[[int], tuple[bool, Status]]


def _propagate_run(events: Sequence[tuple[int, BreakKind]], n: int) -> list[int]:
    """Propagă `run` cu semn bară cu bară dintr-un flux de break-uri (idx crescător). Convenția: CHoCH răstoarnă
    (reset la ±1); BOS de același semn incrementează magnitudinea; BOS opus (rar) resetează la ±1. Fără structură
    (înainte de primul break) → 0. Cauzal prin construcție: run[i] folosește DOAR evenimente cu idx<=i."""
    series = [0] * n
    run = 0
    bi = 0
    ev = sorted(events, key=lambda e: e[0])
    for i in range(n):
        while bi < len(ev) and ev[bi][0] == i:
            kind = ev[bi][1]
            bi += 1
            if kind is BreakKind.CHOCH_BULL:
                run = 1
            elif kind is BreakKind.CHOCH_BEAR:
                run = -1
            elif kind is BreakKind.BOS_BULL:
                run = run + 1 if run > 0 else 1
            elif kind is BreakKind.BOS_BEAR:
                run = run - 1 if run < 0 else -1
        series[i] = run
    return series


def _run_series(close: Sequence[float], high: Sequence[float], low: Sequence[float], n: int, k: int) -> list[int]:
    """`run` cu semn din fluxul `detect_breaks` ratificat (cascadă v2.7.38), propagat cauzal (idx<=i)."""
    blk = [Block(0, n)]
    swings = label_structure(detect_swings(high, low, blk, k))
    breaks = detect_breaks(close, swings, blk)
    return _propagate_run([(b.idx, b.kind) for b in breaks], n)


def _struct_band(run_abs: int) -> StructBand:
    if run_abs == 0:
        return StructBand.NONE
    if run_abs == 1:
        return StructBand.RANGE
    if run_abs < RUN_STRONG_MIN:                              # {2,3}
        return StructBand.WEAK
    return StructBand.STRONG


def _direction(run: int, enough: bool) -> Direction:
    if not enough or run == 0 or abs(run) == 1:              # sub n_min / fără structură / RANGE(instabil) → neutral
        return Direction.NEUTRAL
    if run > 0:
        return Direction.WEAK_UP if abs(run) < RUN_STRONG_MIN else Direction.UP
    return Direction.WEAK_DOWN if abs(run) < RUN_STRONG_MIN else Direction.DOWN


def _volatility_axis(m: np.ndarray, i: int, is_expansion: bool) -> Axis:
    """Banda de volatilitate a barei i cu atribuire MOALE. Fereastra CAUZALĂ [i-W+1, i] (inclusiv i, zero lookahead)."""
    if i < W_WEEK_H4 - 1:                                     # fereastră trailing incompletă → fail-closed
        return Axis(VolBand.UNAVAILABLE.value, (), 0.0, Status.UNAVAILABLE.value)
    w = m[i - W_WEEK_H4 + 1:i + 1]
    pcts = np.percentile(w, [PCTL_COMPRESSED, PCTL_LOW, PCTL_HIGH])
    p10, p33, p67 = float(pcts[0]), float(pcts[1]), float(pcts[2])
    mi = float(m[i])
    bounds = [p10, p33, p67]                                  # 3 granițe între 4 benzi de bază
    base_vals: list[str] = [VolBand.COMPRESSED.value, VolBand.LOW.value, VolBand.NORMAL.value]  # banda 3 = HIGH_*
    kband = 0
    while kband < 3 and mi > bounds[kband]:
        kband += 1

    def _lbl(idx: int) -> str:                                # banda HIGH se subdivizează prin corp direcțional
        if idx == 3:
            return str((VolBand.HIGH_DIRECTIONAL if is_expansion else VolBand.HIGH_CHOPPY).value)
        return base_vals[idx]

    label_band = _lbl(kband)
    scale = 0.5 * (p67 - p10)                                 # normalizator uniform (jumătate din spread-ul central)
    lower_b = bounds[kband - 1] if kband > 0 else None
    upper_b = bounds[kband] if kband < 3 else None
    cand: list[tuple[float, int]] = []                       # (distanță, index vecin)
    if lower_b is not None:
        cand.append((mi - lower_b, kband - 1))
    if upper_b is not None:
        cand.append((upper_b - mi, kband + 1))
    nearest_d, nb_idx = min(cand, key=lambda t: t[0]) if cand else (scale, kband)
    conf = 1.0 if scale <= 0.0 else max(0.0, min(1.0, nearest_d / scale))
    w_nb = 0.5 * (1.0 - conf)                                 # atribuire moale către vecinul de frontieră
    w_band = 1.0 - w_nb

    weights = [(label_band, w_band)]
    if w_nb > 0.0:
        weights.append((_lbl(nb_idx), w_nb))
    return Axis(label_band, tuple(weights), conf, Status.AVAILABLE.value)


def classify_regime(
    open_: Sequence[float], high: Sequence[float], low: Sequence[float], close: Sequence[float],
    *, k: int = K_SWING_DEFAULT, n_min: int = N_MIN_DEFAULT, news_fn: NewsFn | None = None,
) -> RegimeState:
    """Clasifică bara CURENTĂ (ultima) din barele H4 de până la ea. Cele patru axe, cu ponderi/intervale. PURĂ, cauzală."""
    n = len(close)
    i = n - 1
    if n == 0:
        na = Axis(VolBand.UNAVAILABLE.value, (), 0.0, Status.UNAVAILABLE.value)
        return RegimeState(na, na, na, na, None, None, None, as_of_index=-1, n_bars=0)

    # ── AXA A: volatilitate ──
    h = np.asarray(high, dtype=float)
    lo = np.asarray(low, dtype=float)
    m = np.log(h / lo)                                        # Parkinson E000 per bară
    exp_series = expansion(open_, high, low, close)
    vol = _volatility_axis(m, i, bool(exp_series[i]))

    # ── AXA B: structură + direcție (din run) ──
    run_series = _run_series(close, high, low, n, k)
    run_i = run_series[i]
    sband = _struct_band(abs(run_i))
    enough = n >= n_min
    direction = _direction(run_i, enough)
    struct_status = Status.AVAILABLE.value if sband is not StructBand.NONE else Status.UNAVAILABLE.value
    structure = Axis(sband.value, ((sband.value, 1.0),), 1.0 if sband is not StructBand.NONE else 0.0, struct_status)

    # confidence direcțional = decisivitatea ferestrei (cât de unilateral e recentul); interval prin share-uri
    if enough and i >= W_WEEK_H4 - 1:
        wnd = run_series[i - W_WEEK_H4 + 1:i + 1]
        long_share = float(np.mean([1.0 if r > 0 else 0.0 for r in wnd]))
        short_share = float(np.mean([1.0 if r < 0 else 0.0 for r in wnd]))
        dir_conf = abs(long_share - short_share)
        dir_status = Status.AVAILABLE.value
    else:
        long_share = short_share = None                      # type: ignore[assignment]
        dir_conf = 0.0
        dir_status = Status.UNAVAILABLE.value if not enough else Status.AVAILABLE.value
    direction_axis = Axis(direction.value, ((direction.value, 1.0),),
                          dir_conf if direction is not Direction.NEUTRAL else 0.0, dir_status)

    # ── AXA C: știri (două câmpuri; value=FALSE + status=UNAVAILABLE până la calendar) ──
    if news_fn is None:
        news_val, news_status = False, Status.UNAVAILABLE
    else:
        news_val, news_status = news_fn(i)
    news_label = "news_dominated" if news_val else "normal"
    news = Axis(news_label, ((news_label, 1.0),),
                1.0 if news_status is Status.AVAILABLE else 0.0, news_status.value)

    return RegimeState(
        volatility=vol, structure=structure, direction=direction_axis, news=news,
        trend_long_share=long_share, trend_short_share=short_share, run=run_i,
        as_of_index=i, n_bars=n)
