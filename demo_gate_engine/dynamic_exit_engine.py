"""Extensie de EXIT DINAMIC pentru motorul DEMO — exit = eveniment, nu preț fix (ex. CAND-0002).

O condiție de ieșire din contractul înghețat (nu logică nouă): pentru politicile al căror exit e un EVENIMENT
forward (prima expansiune OPUSĂ după intrare → ieșire la open[k+1]), nu un nivel de preț. Reutilizează IDENTIC
podeaua S2, ierarhia worst-case S1 și fereastra S3 din `pdh_pdl_demo_engine` (înghețat, NEATINS) — doar „ținta"
devine un semnal per-bară în loc de un preț. Ierarhia rămâne STOP > TIME-STOP > EXIT-eveniment.

`time_stop_idx` (RT-CODE-A-0005 D2): UN singur înțeles — ultima bară de scanare, force-close la close-ul ei.
Caller-ul decide ce reprezintă (granița de bloc, orizont de N bare etc.); motorul îl tratează UNIFORM. Nu mai
poartă două înțelesuri sub același nume (fostul `day_end_idx`, care aici însemna „granița de bloc" iar în
`pdh_pdl` „granița de zi").

`expansion_dir[j]` ∈ {+1 (expansiune bullish), −1 (expansiune bearish), 0 (fără)}. Exit OPUS la bara j dacă
`expansion_dir[j] == -direction`. Nu decide nimic ce contractul nu acoperă: stopul (worst-case), ordinea de
coliziune (convenția S1 deja ratificată) și termenul-limită sunt toate în contract.

RT-CODE-A-0005 — aceleași corecții ca `pdh_pdl_demo_engine`:
  D1  S1 pe bara de INTRARE la TOATE tranzacțiile (nu doar cele podite): breach intrabar al stopului executabil
      pe bara de intrare = stop-out REAL după intrare (open = primul tick).
  R1  cele TREI condiții INVALID: (1) gap prin stopul podit la intrare; (2) risc zero/negativ; (3) fill ambiguu
      nerezolvabil (open dincolo de stopul executabil) — fail-closed, normal pre-emptat de garda structurală.
  R2  precondiție F3: `0 <= entry_idx <= time_stop_idx <= n-1`, fail-closed.
GARD 2 neatins; fără MT5; fără date reale.
"""

from __future__ import annotations

from typing import Sequence

from pdh_pdl_demo_engine import DemoSignal, DemoTradeResult, ExitReason, min_executable_risk


def simulate_demo_trade_dynamic(
    sig: DemoSignal,
    open_: Sequence[float], high: Sequence[float], low: Sequence[float], close: Sequence[float],
    expansion_dir: Sequence[int], tick_size: float,
) -> DemoTradeResult:
    """Ca `simulate_demo_trade`, dar exit = prima bară OPUSĂ (`expansion_dir[j]==-direction`) → open[j+1].
    `sig.target_price` e ignorat (exitul e dinamic). `time_stop_idx` = termenul-limită (caller)."""
    n = len(close)
    if not (0 <= sig.entry_idx <= sig.time_stop_idx <= n - 1):    # PRECONDIȚIE F3 (R2), fail-closed
        raise ValueError(
            f"F3: 0 <= entry_idx({sig.entry_idx}) <= time_stop_idx({sig.time_stop_idx}) <= n-1({n - 1}) încălcat.")

    d = sig.direction
    ei = sig.entry_idx
    entry = float(open_[ei])
    strategy_stop_distance = abs(entry - sig.strategy_stop_price)
    min_exec = min_executable_risk(sig.effective_spread, tick_size, sig.atr)
    executable_stop_distance = max(strategy_stop_distance, min_exec)
    floored = strategy_stop_distance < min_exec
    exec_stop_price = entry - d * executable_stop_distance
    scan_start = ei + 1
    scan_end = sig.time_stop_idx

    def _mk(traded: bool, reason: ExitReason, xi: int | None, xp: float | None, order: str) -> DemoTradeResult:
        net_R: float | None = None
        net_d: float | None = None
        if xp is not None and traded and executable_stop_distance > 0:
            net_R = (d * (xp - entry) - sig.cost) / executable_stop_distance
            net_d = net_R * executable_stop_distance
        return DemoTradeResult(
            traded=traded, exit_reason=reason.value, exit_idx=xi, exit_price=xp, net_R=net_R, net_dollars=net_d,
            entry_idx=ei, entry_price=entry, direction=d, time_stop_idx=sig.time_stop_idx, intrabar_ordering=order,
            effective_spread=sig.effective_spread, strategy_stop_distance=strategy_stop_distance,
            min_executable_risk=min_exec, executable_stop_distance=executable_stop_distance, floored=floored,
            executable_stop_price=exec_stop_price, target_scan_start=scan_start, target_scan_end=scan_end)

    if executable_stop_distance <= 0:                            # (2) risc zero/negativ
        return _mk(True, ExitReason.INVALID_EXECUTION, None, None, "zero_or_negative_risk")
    if (d > 0 and entry <= sig.strategy_stop_price) or (d < 0 and entry >= sig.strategy_stop_price):
        return _mk(False, ExitReason.NO_TRADE, None, None, "no_trade_entry_beyond_structural_stop")
    if (d > 0 and entry <= exec_stop_price) or (d < 0 and entry >= exec_stop_price):   # (3) fill ambiguu, fail-closed
        return _mk(True, ExitReason.INVALID_EXECUTION, ei, exec_stop_price, "ambiguous_same_bar_fill")

    # ── S1 pe bara de INTRARE (D1) — la TOATE tranzacțiile ──
    entry_bar_hitS = (low[ei] <= exec_stop_price) if d > 0 else (high[ei] >= exec_stop_price)
    if entry_bar_hitS:
        if floored:                                             # (1) gap prin stopul PODIT la intrare
            return _mk(True, ExitReason.INVALID_EXECUTION, ei, exec_stop_price, "gap_through_floored_stop_at_entry")
        return _mk(True, ExitReason.STOP, ei, exec_stop_price, "stop_at_entry_bar")   # D1: stop REAL, nepodit

    for j in range(scan_start, scan_end + 1):
        hitS = (low[j] <= exec_stop_price) if d > 0 else (high[j] >= exec_stop_price)
        opposing = expansion_dir[j] == -d
        boundary = (j == scan_end)
        if hitS:
            order = ("stop_over_opposing" if opposing else "stop_over_time_stop" if boundary else "stop")
            return _mk(True, ExitReason.STOP, j, exec_stop_price, order)
        if boundary:                                # termenul-limită → time-stop (peste exit-eveniment, S1)
            order = "time_stop_over_opposing" if opposing else "time_stop"
            return _mk(True, ExitReason.TIME_STOP, j, float(close[j]), order)
        if opposing:                                # prima expansiune opusă → ieșire la open[j+1]
            return _mk(True, ExitReason.TARGET, j + 1, float(open_[j + 1]), "opposing_expansion")

    return _mk(True, ExitReason.TIME_STOP, scan_end, float(close[scan_end]), "time_stop")


def simulate_demo_trades_dynamic(
    signals: Sequence[DemoSignal],
    open_: Sequence[float], high: Sequence[float], low: Sequence[float], close: Sequence[float],
    expansion_dir: Sequence[int], tick_size: float,
) -> list[DemoTradeResult]:
    return [simulate_demo_trade_dynamic(s, open_, high, low, close, expansion_dir, tick_size) for s in signals]
