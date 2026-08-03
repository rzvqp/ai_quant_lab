"""DEMO gate-enforcement engine — CAND-0001 PDH-PDL v2.0 (DEMO_BASELINE).

Impune cele TREI garduri Red Team (criteriile Statistician `c6305d5`, manifest v2.7.34 `a11dde7`) cu câmpuri
de audit per tranzacție. Motor SEPARAT de `code/mstrat.py` (motorul de cercetare/backtest, NEATINS). Funcție
PURĂ de bare + spread OBSERVAT; fără MT5, fără trimitere de ordine, fără date reale. NU proiectez metoda de risc
(SL=extrema barei de atingere, țintă=nivelul opus, time-stop=închiderea zilei, sizing=1R — a lui Alpha,
înghețată `1558397`). Impun DOAR gardurile + auditul.

GARDURI:
  S1  ierarhie worst-case STOP > TIME-STOP > TARGET la toate TREI coliziunile intrabar. Time-stop-ul e al ZILEI
      (`day_end_idx` = ultima bară a zilei de intrare), nu un timeout pe bare. Pe bara-graniță, STOP primează;
      dacă bara-graniță atinge ținta dar NU stopul → TIME-STOP (ieșire la close), nu ținta (presupunerea
      optimistă interzisă de Red Team). Audit: `intrabar_ordering`.
  S2  `min_executable_risk = max(2×effective_spread, 5×tick_size, 0,10×ATR)`; `executable_stop_distance =
      max(strategy_stop_distance, min_executable_risk)`; sizing 1R pe distanța CORECTATĂ. `effective_spread` =
      spread REAL observat (nu modelat). Audit: `strategy_stop_distance` (NU se suprascrie), `min_executable_risk`,
      `executable_stop_distance`, `floored`.
  S3  ținta scanată STRICT de la `entry_idx+1`; o atingere anterioară în zi e irelevantă. Audit: fereastra de
      scanare (`target_scan_start`/`target_scan_end`).

INVALID_EXECUTION rămâne ÎNGUST (convenția MIN_STOP_FLOOR_PREREG): gap prin stopul PODIT la intrare (doar
tranzacții podite, ca regimul ATR ne-podit să rămână neschimbat) SAU risc zero/negativ după podire. NU
coliziunile obișnuite. Garda de intrare a politicii (nu se intră dacă next-open e dincolo de țintă / de stopul
structural) → NO_TRADE, separat.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

# Constante pre-înregistrate (docs/MIN_STOP_FLOOR_PREREG.md) — NU re-derivate aici.
K_SPREAD: float = 2.0
K_TICK: float = 5.0
K_ATR: float = 0.10


class ExitReason(Enum):
    STOP = "stop"
    TARGET = "target"
    TIME_STOP = "time_stop"
    INVALID_EXECUTION = "invalid_execution"
    NO_TRADE = "no_trade"


@dataclass(frozen=True)
class DemoSignal:
    """Un semnal deja validat de Part A (declanșator) — motorul impune gardurile Part B."""
    entry_idx: int              # = touch_idx + 1 (next-open), a lui Alpha
    direction: int              # +1 long (PDL), -1 short (PDH)
    strategy_stop_price: float  # extrema barei de atingere (politică, înghețată)
    target_price: float         # nivelul opus al zilei anterioare (politică, înghețată)
    atr: float                  # ATR la bara declanșator (pentru 0,10×ATR)
    effective_spread: float     # spread REAL observat la intrare (DEMO), unități de preț
    cost: float                 # cost round-trip OBSERVAT (spread+slippage), unități de preț
    day_end_idx: int            # ultima bară a zilei de intrare (granița `day_index`) → bara de time-stop


@dataclass(frozen=True)
class DemoTradeResult:
    # rezultat
    traded: bool
    exit_reason: str
    exit_idx: int | None
    exit_price: float | None
    net_R: float | None
    net_dollars: float | None
    # intrare
    entry_idx: int
    entry_price: float
    direction: int
    day_end_idx: int
    # S1 audit
    intrabar_ordering: str
    # S2 audit (strategy_stop_distance NU se suprascrie)
    effective_spread: float
    strategy_stop_distance: float
    min_executable_risk: float
    executable_stop_distance: float
    floored: bool
    executable_stop_price: float
    # S3 audit
    target_scan_start: int
    target_scan_end: int


def min_executable_risk(effective_spread: float, tick_size: float, atr: float) -> float:
    """S2, formula pre-înregistrată, cifră cu cifră."""
    return max(K_SPREAD * effective_spread, K_TICK * tick_size, K_ATR * atr)


def simulate_demo_trade(
    sig: DemoSignal,
    open_: Sequence[float], high: Sequence[float], low: Sequence[float], close: Sequence[float],
    tick_size: float,
) -> DemoTradeResult:
    """Rezultatul UNEI tranzacții sub cele trei garduri, cu TOATE câmpurile de audit. Bare + spread observat.

    `effective_spread` din semnal e valoarea OBSERVATĂ (DEMO) — S2 o folosește direct în podea, nu o constantă.
    """
    d = sig.direction
    ei = sig.entry_idx
    entry = float(open_[ei])

    # ── S2: podea + sizing (strategy_stop_distance PĂSTRAT, NU suprascris) ──
    strategy_stop_distance = abs(entry - sig.strategy_stop_price)
    min_exec = min_executable_risk(sig.effective_spread, tick_size, sig.atr)
    executable_stop_distance = max(strategy_stop_distance, min_exec)
    floored = strategy_stop_distance < min_exec
    exec_stop_price = entry - d * executable_stop_distance
    scan_start = ei + 1                         # S3
    scan_end = sig.day_end_idx

    def _mk(traded: bool, reason: ExitReason, xi: int | None, xp: float | None, order: str) -> DemoTradeResult:
        net_R: float | None = None
        net_d: float | None = None
        if xp is not None and traded and executable_stop_distance > 0:
            net_R = (d * (xp - entry) - sig.cost) / executable_stop_distance
            net_d = net_R * executable_stop_distance     # $ pe distanța PODITĂ (S2), sizing 1R
        return DemoTradeResult(
            traded=traded, exit_reason=reason.value, exit_idx=xi, exit_price=xp,
            net_R=net_R, net_dollars=net_d, entry_idx=ei, entry_price=entry, direction=d,
            day_end_idx=sig.day_end_idx, intrabar_ordering=order, effective_spread=sig.effective_spread,
            strategy_stop_distance=strategy_stop_distance, min_executable_risk=min_exec,
            executable_stop_distance=executable_stop_distance, floored=floored,
            executable_stop_price=exec_stop_price, target_scan_start=scan_start, target_scan_end=scan_end)

    # risc zero/negativ după podire → INVALID (îngust)
    if executable_stop_distance <= 0:
        return _mk(True, ExitReason.INVALID_EXECUTION, None, None, "zero_or_negative_risk")

    # gardă de intrare a politicii (Part B): next-open deja dincolo de țintă / de stopul STRUCTURAL → NU se intră
    if (d > 0 and entry >= sig.target_price) or (d < 0 and entry <= sig.target_price):
        return _mk(False, ExitReason.NO_TRADE, None, None, "no_trade_entry_beyond_target")
    if (d > 0 and entry <= sig.strategy_stop_price) or (d < 0 and entry >= sig.strategy_stop_price):
        return _mk(False, ExitReason.NO_TRADE, None, None, "no_trade_entry_beyond_structural_stop")

    # INVALID îngust: gap prin stopul PODIT chiar pe bara de intrare (DOAR tranzacții podite)
    entry_bar_breaches_floored = (low[ei] <= exec_stop_price) if d > 0 else (high[ei] >= exec_stop_price)
    if floored and entry_bar_breaches_floored:
        return _mk(True, ExitReason.INVALID_EXECUTION, ei, exec_stop_price, "gap_through_floored_stop_at_entry")

    # ── S1 + S3: scanare STRICT de la entry_idx+1 până la granița ZILEI ──
    for j in range(scan_start, scan_end + 1):
        hitS = (low[j] <= exec_stop_price) if d > 0 else (high[j] >= exec_stop_price)
        hitT = (high[j] >= sig.target_price) if d > 0 else (low[j] <= sig.target_price)
        boundary = (j == scan_end)
        # ierarhie worst-case: STOP > TIME-STOP > TARGET
        if hitS:
            order = ("stop_over_target_time_stop" if (hitT and boundary)
                     else "stop_over_target" if hitT
                     else "stop_over_time_stop" if boundary
                     else "stop")
            return _mk(True, ExitReason.STOP, j, exec_stop_price, order)
        if boundary:
            order = "time_stop_over_target" if hitT else "time_stop"
            return _mk(True, ExitReason.TIME_STOP, j, float(close[j]), order)   # ieșire la close-ul zilei
        if hitT:
            return _mk(True, ExitReason.TARGET, j, sig.target_price, "target")

    # ziua se termină pe/înainte de bara de intrare (entry pe ultima bară a zilei) → time-stop la close
    return _mk(True, ExitReason.TIME_STOP, scan_end, float(close[scan_end]), "time_stop")


def simulate_demo_trades(
    signals: Sequence[DemoSignal],
    open_: Sequence[float], high: Sequence[float], low: Sequence[float], close: Sequence[float],
    tick_size: float,
) -> list[DemoTradeResult]:
    """Batch peste semnale — fiecare tranzacție emite TOATE câmpurile de audit."""
    return [simulate_demo_trade(s, open_, high, low, close, tick_size) for s in signals]
