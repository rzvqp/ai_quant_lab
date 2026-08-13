"""Modulul 6 — market_state.py: Compression / Expansion / Sessions (MK, Mandat 5.8).

Primitive PURE. NU citește prețuri, NU apelează `load()`, NU rulează backtest. Inerte. mypy --strict.

Parametri RATIFICAȚI (Statistician v2.6.1 `2fb948f`, doc `3c64848`):

  EXPANSION — reutilizat VERBATIM din E010 (`e010_breaker_block_snatch.py`, `code/mtf.py:17`):
     bară de deplasare i ⇔ `range[i]=high[i]-low[i] > 1.5×ATR14[i-1]` (ATR-ul barei PRECEDENTE, ca bara să
     nu-și infleze propriul reper) ȘI corp direcțional puternic `|close[i]-open[i]| >= 0.5×range[i]`.
     ATR14 = `tr.rolling(14).mean()`, `tr=max(h-l, |h-c₋₁|, |l-c₋₁|)` (identic mtf.py/_common.py). Respinse:
     2,5×ATR (nederivat) și REACTION_THRESHOLD=1,0 (măsoară reacția FORWARD, altă categorie).

  COMPRESSION — fereastră RULANTĂ STRICT CAUZALĂ de 460 de bare, percentila 10:
     măsura = log-range Parkinson per bară `ln(high/low)` (metrica OFICIALĂ E000, primară). Bara i e
     „compresată" ⇔ `measure[i] <= P10(measure pe [i-459, i])` — fereastra = bara curentă + 459 anterioare,
     NICIODATĂ bare viitoare. Lungimea 460 = media empirică de săptămână, DERIVATĂ la Mandatele 3.18/3.19
     (`derive_week_index`), reutilizată verbatim. Nivelul 10 = default declarat al spec-ului („disclosed,
     not tuned"), nu re-derivat. Fereastra rezolvă riscul de LOOKAHEAD (o percentilă pe tot istoricul ar
     clasifica o bară din 2013 cu date din 2021 — confirmat risc real).

     ⚠ RISC DECLARAT (consemnat, nu ascuns — cerut explicit de Statistician): Compression e SINGURA
     primitivă (împreună cu criteriul de formare OB) genuin NEANCORATĂ — nicio familie SMC_S* nu o cere.
     Definiție în ABSTRACT, acceptată provizoriu (poziția CTO: bibliotecă completă înainte de simulare).
     Fereastra derivată reduce, dar NU elimină, riscul de „zece variante plauzibile" (granularitatea măsurii,
     nivelul percentilei, `<=` vs `<`) — rămâne o alegere de definiție, nu o ancorare la un consumator.

  SESSIONS — patru, VERBATIM din `code/mtf.py:38`
     `np.select([hh<8, hh<13, hh<21], ['asia','london','ny'], default='late')`, hh = ora UTC.
     NICIO a cincea sesiune. „Cash" NU există (nu se mapează pe un instrument XAUUSD ~24/5).
"""

from __future__ import annotations

import datetime as _dt
from typing import Sequence

import numpy as np

DISP_MULT = 1.5           # E010 PRIMARY_DISP
BODY_FRAC = 0.5           # E010 BODY_FRAC
ATR_WINDOW = 14           # ATR14
COMPRESSION_WINDOW = 460  # media empirică de săptămână (Mandat 3.18/3.19), derivată
COMPRESSION_PCTL = 10.0   # default declarat al spec-ului


def atr14(high: Sequence[float], low: Sequence[float], close: Sequence[float]) -> list[float]:
    """ATR14 verbatim (mtf.py:17 / _common.py:162): `tr=max(h-l,|h-c₋₁|,|l-c₋₁|)`, `rolling(14).mean()`.
    NaN pentru primele 14 bare (c₋₁ lipsă la i=0 → tr[0]=NaN → prima valoare validă la index 14)."""
    h = np.asarray(high, dtype=float); lo = np.asarray(low, dtype=float); c = np.asarray(close, dtype=float)
    prev_c = np.concatenate(([np.nan], c[:-1]))
    tr = np.maximum(h - lo, np.maximum(np.abs(h - prev_c), np.abs(lo - prev_c)))
    out = np.full(len(tr), np.nan)
    for i in range(ATR_WINDOW - 1, len(tr)):
        window = tr[i - ATR_WINDOW + 1:i + 1]
        if np.isnan(window).any():
            continue
        out[i] = float(window.mean())
    return [float(x) for x in out]


def expansion(
    open_: Sequence[float], high: Sequence[float], low: Sequence[float], close: Sequence[float],
) -> list[bool]:
    """Bare de deplasare E010: `range > 1.5×ATR14[i-1]` ȘI `|close-open| >= 0.5×range`. False unde
    ATR14[i-1] lipsește sau ≤0 (identic cu `continue`-ul din e010_breaker_block_snatch.py)."""
    o = np.asarray(open_, dtype=float); h = np.asarray(high, dtype=float)
    lo = np.asarray(low, dtype=float); c = np.asarray(close, dtype=float)
    atr = atr14(high, low, close)
    rng = h - lo
    out: list[bool] = [False] * len(c)
    for i in range(1, len(c)):
        prior_atr = atr[i - 1]                       # ATR-ul barei PRECEDENTE
        if not np.isfinite(prior_atr) or prior_atr <= 0:
            continue
        if rng[i] <= DISP_MULT * prior_atr:
            continue
        if abs(c[i] - o[i]) < BODY_FRAC * rng[i]:
            continue
        out[i] = True
    return out


def compression(
    high: Sequence[float], low: Sequence[float],
    window: int = COMPRESSION_WINDOW, pctl: float = COMPRESSION_PCTL,
) -> tuple[list[bool], list[bool]]:
    """Compresie strict cauzală. Returnează (`is_compressed`, `is_valid`) per bară.
    `is_compressed[i]` = `ln(high[i]/low[i]) <= P{pctl}` calculată pe fereastra RETROSPECTIVĂ `[i-window+1, i]`.
    `is_valid[i]` = False până când există o fereastră trailing COMPLETĂ (i >= window-1) — bara nu poate fi
    clasificată fără fereastra completă. ZERO lookahead: nicio bară `> i` nu intră în clasificarea lui i."""
    h = np.asarray(high, dtype=float); lo = np.asarray(low, dtype=float)
    measure = np.log(h / lo)                          # log-range Parkinson per bară (E000)
    n = len(measure)
    is_compressed: list[bool] = [False] * n
    is_valid: list[bool] = [False] * n
    for i in range(window - 1, n):
        w = measure[i - window + 1:i + 1]             # trailing, INCLUSIV bara curentă; niciodată viitor
        threshold = float(np.percentile(w, pctl))
        is_valid[i] = True
        is_compressed[i] = bool(measure[i] <= threshold)
    return is_compressed, is_valid


def session_of(epoch: int) -> str:
    """Sesiunea unei bare (mtf.py:38 verbatim): asia hh<8, london hh<13, ny hh<21, late. hh = ora UTC."""
    hh = _dt.datetime.fromtimestamp(int(epoch), tz=_dt.timezone.utc).hour
    if hh < 8:
        return "asia"
    if hh < 13:
        return "london"
    if hh < 21:
        return "ny"
    return "late"


def sessions(time: Sequence[int]) -> list[str]:
    """Etichetele de sesiune pentru un vector de epoci. Patru etichete, nicio a cincea."""
    return [session_of(int(t)) for t in time]
