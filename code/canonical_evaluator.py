"""EVALUATORUL CANONIC UNIC (STAT-CANONICAL-EVALUATOR-CONTRACT-v1.0-DRAFT — NOT RATIFIED). UN SINGUR evaluator,
importat de toate motoarele (_screen, mstrat, demo_gate_engine); ele îl CONSUMĂ, nu-și păstrează propria logică.
Rezolvă divergențele care făceau aceeași tranzacție să iasă diferit la motoare diferite.

REGULILE (D-1 și D-2 aprobate de CEO):
  R1  tick_size = 0,01 USD. SURSĂ UNICĂ (`TICK_SIZE`), importată. Increment de PREȚ, nu costul unui tick.
  R2  semnal pe bara ÎNCHISĂ i → intrare la `open[i+1]`. Retroactiv interzis.
  R3  minimum_stop_distance = max(2×spread_price, 0,05 USD, 0,10×ATR). Toți trei termenii în USD de preț, FĂRĂ
      înmulțire cu tick_size. D-2: dacă requested_stop_distance < minimum → SEMNALUL SE RESPINGE înainte de deschidere
      (NU se extinde — extinderea ar modifica tacit riscul/R:R/logica/populația reală). Respins ⇒ registrul de
      SEMNALE, fără P&L fictiv.
  R4  D-1: total_cost_price = spread_price + entry_slippage_price + exit_slippage_price (toate USD). Spread-ul NU se
      dublează; slippage-ul se aplică SEPARAT fiecărei execuții. BASE 0,05 / STRESS 0,24, ambele PROVISIONAL —
      NOT EMPIRICALLY CALIBRATED. TOATE strategiile raportează în AMBELE scenarii.
  R5  intrare la open; SL și TP verificate INCLUSIV pe bara de intrare; la coliziune intrabar SL PRIMEAZĂ; costurile
      se aplică indiferent de motivul ieșirii. (Punctul doi = defectul D1: 4.160 pierderi raportate drept câștiguri.)
  R6  max_holding_bars = bare EVALUATE, INCLUSIV bara de intrare (bara de intrare = bara 1). La H=10: barele 1..10,
      time-exit la close-ul barei 10 ⇒ interval [ei, ei+H-1].
  R7  time-exit executabil LIVE. Granița unui bloc/chunk/fișier/segment NU e semnal de piață: tranzacțiile rămase
      deschise la acea graniță se raportează SEPARAT (still_open_at_end), NU time-exit la graniță.
  R11 fiecare rezultat poartă configurația completă (`config_id` imuabil). Două rezultate se compară DOAR dacă toate
      dimensiunile coincid; altfel NON-COMPARABLE.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Sequence

# ── R1: sursă UNICĂ pentru tick_size (increment de preț, USD). Zero TICK local în motoare. ──
TICK_SIZE: float = 0.01

CODE_VERSION: str = "canonical-evaluator-v1.0-DRAFT"
REASON_STOP_BELOW_MINIMUM: str = "STOP_BELOW_MINIMUM"


# ── R4: scenarii de cost, în USD de preț. PROVISIONAL — NOT EMPIRICALLY CALIBRATED. ──
@dataclass(frozen=True)
class CostScenario:
    name: str
    spread_price: float
    entry_slippage_price: float
    exit_slippage_price: float
    calibrated: bool = False           # PROVISIONAL ⇒ False (nu e calibrat empiric)

    @property
    def total_cost_price(self) -> float:
        # spread-ul NU se dublează; slippage aplicat SEPARAT fiecărei execuții (intrare + ieșire)
        return self.spread_price + self.entry_slippage_price + self.exit_slippage_price


BASE_PROVISIONAL = CostScenario("BASE_PROVISIONAL", 0.05, 0.00, 0.00)       # total 0,05
STRESS_PROVISIONAL = CostScenario("STRESS_PROVISIONAL", 0.08, 0.08, 0.08)   # total 0,24
DEFAULT_SCENARIOS: tuple[CostScenario, ...] = (BASE_PROVISIONAL, STRESS_PROVISIONAL)


@dataclass(frozen=True)
class Signal:
    """Ce furnizează fiecare motor. Intrarea se derivă din `signal_bar` (R2), NU se dă direct — retroactiv interzis.
    `spread_price`/`atr` sunt CONTEXTUL de la `signal_bar` (cauzal) pentru podeaua R3."""
    strategy_id: str
    signal_id: str
    signal_bar: int                    # bara ÎNCHISĂ i (R2) — intrarea va fi open[i+1]
    direction: int                     # +1 long / −1 short
    requested_stop_price: float        # stopul INTENȚIONAT al strategiei (NU se extinde — R3/D-2)
    target_kind: str                   # 'rr' | 'price' | 'none'
    target_param: float | None         # R:R (dacă 'rr') sau prețul țintă (dacă 'price')
    max_holding_bars: int              # R6, inclusiv bara de intrare (≥1)
    spread_price: float                # spread de context la semnal (pentru podeaua R3, executabilitate)
    atr: float                         # ATR la semnal (pentru podeaua R3)
    timestamp: int


@dataclass(frozen=True)
class MinimumStop:
    minimum_stop_distance: float
    dominant_component: str            # '2x_spread' | 'floor_0.05usd' | '0.10x_atr'


def minimum_stop_distance(spread_price: float, atr: float) -> MinimumStop:
    """R3: max(2×spread, 0,05 USD, 0,10×ATR). Toți termenii în USD. Raportează componenta DOMINANTĂ."""
    terms = {"2x_spread": 2.0 * spread_price, "floor_0.05usd": 0.05, "0.10x_atr": 0.10 * atr}
    dom = max(terms, key=lambda k: terms[k])
    return MinimumStop(terms[dom], dom)


@dataclass(frozen=True)
class Rejection:
    """R3/D-2: semnal respins ÎNAINTE de deschidere. Rămâne în registrul de SEMNALE, fără P&L fictiv."""
    strategy_id: str
    signal_id: str
    timestamp: int
    requested_stop_distance: float
    minimum_stop_distance: float
    spread_used: float
    atr_used: float
    dominant_component: str
    reason_code: str = REASON_STOP_BELOW_MINIMUM


@dataclass(frozen=True)
class ScenarioResult:
    scenario: str
    net_R: float
    gross_move_price: float
    total_cost_price: float


@dataclass(frozen=True)
class NoEntry:
    """Semnal fără open[i+1] disponibil (granița datasetului la intrare). Registrul de SEMNALE, nu tranzacție."""
    strategy_id: str
    signal_id: str
    timestamp: int
    reason_code: str = "NO_NEXT_OPEN_DATASET_END"


@dataclass(frozen=True)
class ExecutedTrade:
    strategy_id: str
    signal_id: str
    entry_bar: int                     # i+1 (R2)
    entry_price: float
    direction: int
    requested_stop_price: float
    risk_price: float                  # |entry − requested_stop| (NEEXTINS — R3/D-2)
    exit_bar: int
    exit_price: float
    exit_reason: str                   # 'stop' | 'target' | 'time' | 'still_open_at_end'
    still_open_at_end: bool            # R7: rămasă deschisă la granița tradeabilă → raportată SEPARAT
    results: tuple[ScenarioResult, ...]  # R4: BASE + STRESS
    config_id: str                     # R11


EvalOutcome = ExecutedTrade | Rejection | NoEntry


def _config_id(scenarios: Sequence[CostScenario]) -> str:
    payload = {
        "R1_tick_size": TICK_SIZE, "R2_entry": "open[i+1]",
        "R3_min_stop": "max(2xspread,0.05usd,0.10xatr)_REJECT_not_extend",
        "R4_cost": "spread+entry_slip+exit_slip",
        "R4_scenarios": [[s.name, s.spread_price, s.entry_slippage_price, s.exit_slippage_price] for s in scenarios],
        "R5_sl_primacy": True, "R5_check_entry_bar": True, "R5_cost_regardless_of_exit": True,
        "R6_holding": "inclusive_entry_bar_is_1_[ei,ei+H-1]",
        "R7_boundary": "still_open_reported_separately_not_time_exit",
        "code_version": CODE_VERSION,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def _finite(x: float) -> bool:
    return x == x and x not in (float("inf"), float("-inf"))


def evaluate_signal(
    sig: Signal, open_: Sequence[float], high: Sequence[float], low: Sequence[float], close: Sequence[float],
    *, scenarios: Sequence[CostScenario] = DEFAULT_SCENARIOS, block_end: int | None = None,
) -> EvalOutcome:
    """Evaluează UN semnal sub contract. Întoarce ExecutedTrade | Rejection | NoEntry. PUR, cauzal.
    `block_end` = ultima bară a blocului tradeabil (R7); implicit ultima bară a seriei."""
    n = len(close)
    be = (n - 1) if block_end is None else min(block_end, n - 1)
    cfg = _config_id(scenarios)
    ei = sig.signal_bar + 1                                     # R2: intrare la open[i+1]

    # R2/R7: fără bara următoare (sau dincolo de blocul tradeabil) ⇒ NU se intră (granița datasetului)
    if ei > be:
        return NoEntry(sig.strategy_id, sig.signal_id, sig.timestamp)

    entry = float(open_[ei])
    if not (_finite(entry) and _finite(sig.requested_stop_price) and _finite(sig.atr) and sig.atr > 0.0):
        return NoEntry(sig.strategy_id, sig.signal_id, sig.timestamp)   # context invalid → nu se intră
    dirn = 1 if sig.direction > 0 else -1
    requested_stop_distance = abs(entry - sig.requested_stop_price)

    # ── R3/D-2: RESPINGE dacă stopul cerut e sub minim (NU extinde) ──
    ms = minimum_stop_distance(sig.spread_price, sig.atr)
    if requested_stop_distance < ms.minimum_stop_distance:
        return Rejection(
            strategy_id=sig.strategy_id, signal_id=sig.signal_id, timestamp=sig.timestamp,
            requested_stop_distance=requested_stop_distance, minimum_stop_distance=ms.minimum_stop_distance,
            spread_used=sig.spread_price, atr_used=sig.atr, dominant_component=ms.dominant_component)

    risk = requested_stop_distance                             # NEEXTINS
    stop_price = sig.requested_stop_price
    if sig.target_kind == "rr" and sig.target_param is not None:
        tgt: float | None = entry + dirn * sig.target_param * risk
    elif sig.target_kind == "price" and sig.target_param is not None:
        tgt = sig.target_param
    else:
        tgt = None

    # ── R6: barele 1..H inclusiv (bara de intrare = bara 1) ⇒ [ei, ei+H-1] ──
    last_hold = ei + sig.max_holding_bars - 1

    # ── R5: scanează de la BARA DE INTRARE; SL PRIMEAZĂ la coliziune ──
    exit_bar = -1; exit_price = float("nan"); exit_reason = ""
    scan_last = min(last_hold, be)                             # nu scana dincolo de blocul tradeabil
    for j in range(ei, scan_last + 1):
        if dirn > 0:
            hit_stop = low[j] <= stop_price
            hit_tgt = tgt is not None and _finite(tgt) and high[j] >= tgt
        else:
            hit_stop = high[j] >= stop_price
            hit_tgt = tgt is not None and _finite(tgt) and low[j] <= tgt
        if hit_stop:                                           # SL PRIMEAZĂ (verificat înaintea TP)
            exit_bar, exit_price, exit_reason = j, stop_price, "stop"; break
        if hit_tgt and tgt is not None:
            exit_bar, exit_price, exit_reason = j, tgt, "target"; break

    still_open = False
    if exit_reason == "":
        if last_hold > be:
            # R7: fereastra de holding depășește blocul tradeabil ⇒ RĂMASĂ DESCHISĂ (raportat separat), NU time-exit
            still_open = True
            exit_bar, exit_price, exit_reason = be, float(close[be]), "still_open_at_end"
        else:
            # R6: time-exit la close-ul barei H
            exit_bar, exit_price, exit_reason = last_hold, float(close[last_hold]), "time"

    # ── R4/R5: R per scenariu; costurile se aplică INDIFERENT de motivul ieșirii ──
    results = tuple(
        ScenarioResult(sc.name, (dirn * (exit_price - entry) - sc.total_cost_price) / risk,
                       dirn * (exit_price - entry), sc.total_cost_price)
        for sc in scenarios)

    return ExecutedTrade(
        strategy_id=sig.strategy_id, signal_id=sig.signal_id, entry_bar=ei, entry_price=entry, direction=dirn,
        requested_stop_price=stop_price, risk_price=risk, exit_bar=exit_bar, exit_price=exit_price,
        exit_reason=exit_reason, still_open_at_end=still_open, results=results, config_id=cfg)


# ────────────────────────── raportarea per strategie (câmpurile obligatorii) ──────────────────────────
@dataclass(frozen=True)
class StrategyReport:
    strategy_id: str
    config_id: str
    total_signals: int
    eligible_trades: int               # executate cu ieșire reală (exclude respinse, no-entry, still-open)
    rejected: int
    rejected_pct: float
    rejection_reasons: tuple[tuple[str, int], ...]
    no_entry: int
    still_open_at_end: int             # R7, raportate SEPARAT
    base_mean_R: float | None          # performanță EXCLUSIV pe tranzacțiile executabile
    stress_mean_R: float | None
    base_minus_stress: float | None    # diferența explicită


def _mean(xs: list[float]) -> float | None:
    return (sum(xs) / len(xs)) if xs else None


def evaluate_strategy(
    strategy_id: str, signals: Sequence[Signal],
    open_: Sequence[float], high: Sequence[float], low: Sequence[float], close: Sequence[float],
    *, scenarios: Sequence[CostScenario] = DEFAULT_SCENARIOS, block_end: int | None = None,
) -> tuple[StrategyReport, list[EvalOutcome]]:
    """Rulează toate semnalele unei strategii prin evaluatorul canonic și agregă câmpurile obligatorii."""
    outcomes: list[EvalOutcome] = [
        evaluate_signal(s, open_, high, low, close, scenarios=scenarios, block_end=block_end) for s in signals]
    cfg = _config_id(scenarios)
    execd = [o for o in outcomes if isinstance(o, ExecutedTrade)]
    eligible = [o for o in execd if not o.still_open_at_end]    # executabile = ieșire reală
    still_open = [o for o in execd if o.still_open_at_end]
    rejs = [o for o in outcomes if isinstance(o, Rejection)]
    noent = [o for o in outcomes if isinstance(o, NoEntry)]

    reasons: dict[str, int] = {}
    for r in rejs:
        reasons[r.reason_code] = reasons.get(r.reason_code, 0) + 1

    def _scn(o: ExecutedTrade, name: str) -> float:
        return next(r.net_R for r in o.results if r.scenario == name)

    base = [_scn(o, BASE_PROVISIONAL.name) for o in eligible]
    stress = [_scn(o, STRESS_PROVISIONAL.name) for o in eligible]
    bm, sm = _mean(base), _mean(stress)
    total = len(signals)
    report = StrategyReport(
        strategy_id=strategy_id, config_id=cfg, total_signals=total,
        eligible_trades=len(eligible), rejected=len(rejs),
        rejected_pct=(100.0 * len(rejs) / total) if total else 0.0,
        rejection_reasons=tuple(sorted(reasons.items())), no_entry=len(noent),
        still_open_at_end=len(still_open),
        base_mean_R=bm, stress_mean_R=sm,
        base_minus_stress=(bm - sm) if (bm is not None and sm is not None) else None)
    return report, outcomes
