"""EVALUATORUL CANONIC UNIC (STAT-CANONICAL-CONTRACT-v1.0, manifest v2.7.66, doc 9fc8b67 — NOT RATIFIED).
UN SINGUR evaluator importat de toate motoarele; ele îl CONSUMĂ. Rezolvă divergențele care făceau aceeași
tranzacție să iasă diferit la motoare diferite.

REGULI (R1-R7, R11) + corecțiile v2.7.66:
  R1  tick_size = 0,01 USD, sursă unică (increment de preț).
  R2  semnal pe bara ÎNCHISĂ i → intrare open[i+1].
  R3  min_executable_risk = max(K_SPREAD×spread_HALF, K_TICK×tick, K_ATR×atr); K_SPREAD=2, K_TICK=5, K_ATR=0,10.
      §1: spread_price e bid-ask COMPLET; podeaua ia o JUMĂTATE ⇒ 2×(full/2)=full. Factorul 2 nu dispare, se
      ANULEAZĂ cu conversia. `SpreadFull`/`SpreadHalf` sunt NewType DISTINCTE — eroarea de unitate e NESCRIIBILĂ.
      Semantica: REJECT-NOT-WIDEN. Respins ⇒ NUMĂRAT și raportat (niciodată `continue` tăcut), fără P&L.
  R4  cost = spread_price + entry_slip + exit_slip (spread O DATĂ). BASE 0,05 / STRESS 0,24, PROVISIONAL.
  R5  SL+TP inclusiv pe bara de intrare; SL PRIMEAZĂ la coliziune; cost indiferent de motiv.
  R6  max_holding inclusiv, bara de intrare = bara 1 ⇒ [ei, ei+H-1].
  R7  time-exit executabil LIVE; over-orizont la granița blocului = still_open, raportat SEPARAT.
  R11 §3: `run_hash = sha256(config_hash ‖ sha256(data_identity))` — acoperă ȘI DATELE (simbol/timeframe/split/
      manifest/n_blocks/holdout), nu doar costul. `compare()` RIDICĂ NonComparableError (nu comentează).

  §5 GEOMETRIE STRICTĂ la open (AMENDAMENT CEO A2 — prevalează asupra variantei asimetrice, care NU e aprobată),
     aplicată ÎNAINTE de orice evaluare de ieșire. LONG: stop < entry < target; SHORT: target < entry < stop.
     `risc = dirn·(entry−stop) <= 0  OR  recompensă = dirn·(target−entry) <= 0` ⇒ INVALID_EXECUTION.
     Acoperă: gap prin stop, gap prin target, open EXACT pe stop, open EXACT pe target. Fără tranzacție, fără P&L,
     NUMĂRAT. (Varianta asimetrică — reward≤0 → ieșire-la-intrare — a fost RETRASĂ de A2.)

  §7 MEAS-10: `StrategyReport` poartă câmpurile de CONCENTRARE (best_trade_share, trimmed_top1, sum_R, ...) — altfel
     garda fat-tail a CEO (R10) e NECALCULABILĂ din ieșirea oficială („o cerință necalculabilă e un text, nu o cerință").
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import NewType, Sequence

from level_output import LevelOutput, Ok, Unavailable

# ── R1 + §1 unități ──
TICK_SIZE: float = 0.01
K_SPREAD: float = 2.0                # pe JUMĂTATE de spread (dus-întors)
K_TICK: float = 5.0
K_ATR: float = 0.10
CODE_VERSION: str = "canonical-evaluator-v2.7.66-A2"   # A2: geometrie strictă (reward≤0 → INVALID) ⇒ NON-COMPARABIL cu asimetricul
REASON_STOP_BELOW_MINIMUM: str = "STOP_BELOW_MINIMUM"
REASON_INVALID_EXECUTION: str = "INVALID_EXECUTION"

SpreadFull = NewType("SpreadFull", float)    # ask − bid (bid-ask COMPLET)
SpreadHalf = NewType("SpreadHalf", float)    # (ask − bid) / 2


def half_of(s: SpreadFull) -> SpreadHalf:
    """Conversia scrisă O SINGURĂ DATĂ. mypy --strict respinge un SpreadFull acolo unde se cere SpreadHalf."""
    return SpreadHalf(float(s) / 2.0)


# ── R4: scenarii de cost (spread_price = FULL, folosit O DATĂ). PROVISIONAL — NOT EMPIRICALLY CALIBRATED. ──
@dataclass(frozen=True)
class CostScenario:
    name: str
    spread_price: SpreadFull
    entry_slippage_price: float
    exit_slippage_price: float
    calibrated: bool = False

    @property
    def total_cost_price(self) -> float:
        return float(self.spread_price) + self.entry_slippage_price + self.exit_slippage_price


BASE_PROVISIONAL = CostScenario("BASE_PROVISIONAL", SpreadFull(0.05), 0.00, 0.00)       # total 0,05 · R3 0,05
STRESS_PROVISIONAL = CostScenario("STRESS_PROVISIONAL", SpreadFull(0.08), 0.08, 0.08)   # total 0,24 · R3 0,08
DEFAULT_SCENARIOS: tuple[CostScenario, ...] = (BASE_PROVISIONAL, STRESS_PROVISIONAL)


@dataclass(frozen=True)
class Signal:
    strategy_id: str
    signal_id: str
    signal_bar: int
    direction: int
    requested_stop_price: float
    target_kind: str                   # 'rr' | 'price' | 'none'
    target_param: float | None
    max_holding_bars: int
    spread_price: SpreadFull           # bid-ask COMPLET de context (podeaua R3 ia jumătatea)
    atr: float
    timestamp: int


@dataclass(frozen=True)
class MinimumStop:
    minimum_stop_distance: float
    dominant_component: str            # 'spread' | 'tick_floor' | 'atr'


def minimum_stop_distance(spread_half: SpreadHalf, atr: float) -> MinimumStop:
    """R3 (§2): max(K_SPREAD×spread_HALF, K_TICK×tick, K_ATR×atr). K_SPREAD×half = 2×(full/2) = full."""
    terms = {"spread": K_SPREAD * float(spread_half), "tick_floor": K_TICK * TICK_SIZE, "atr": K_ATR * atr}
    dom = max(terms, key=lambda k: terms[k])
    return MinimumStop(terms[dom], dom)


# ── ieșiri posibile ──
@dataclass(frozen=True)
class Rejection:
    """R3/D-2: respins ÎNAINTE de deschidere (stop sub podea). NUMĂRAT, fără P&L fictiv."""
    strategy_id: str
    signal_id: str
    timestamp: int
    requested_stop_distance: float
    minimum_stop_distance: float
    spread_used: SpreadFull
    atr_used: float
    dominant_component: str
    reason_code: str = REASON_STOP_BELOW_MINIMUM


@dataclass(frozen=True)
class InvalidExecution:
    """GEOMETRIE STRICTĂ la open (AMENDAMENT CEO A2, prevalează asupra variantei asimetrice). LONG: stop < entry <
    target; SHORT: target < entry < stop. Orice încălcare (gap prin stop, gap prin target, open EXACT pe stop sau pe
    target) ⇒ INVALID_EXECUTION: fără tranzacție, fără P&L, NUMĂRAT. `risc ≤ 0 OR recompensă ≤ 0`."""
    strategy_id: str
    signal_id: str
    timestamp: int
    entry_price: float
    stop_price: float
    directional_risk: float                    # dirn·(entry−stop); ≤ 0 = gap/open pe stop
    violation: str                             # 'risk_nonpositive' | 'reward_nonpositive'
    directional_reward: float | None = None    # dirn·(target−entry); ≤ 0 = gap/open pe target
    reason_code: str = REASON_INVALID_EXECUTION


@dataclass(frozen=True)
class NoEntry:
    strategy_id: str
    signal_id: str
    timestamp: int
    reason_code: str = "NO_NEXT_OPEN_DATASET_END"


@dataclass(frozen=True)
class ScenarioResult:
    scenario: str
    net_R: float
    gross_move_price: float
    total_cost_price: float


@dataclass(frozen=True)
class ExecutedTrade:
    strategy_id: str
    signal_id: str
    entry_bar: int
    entry_price: float
    direction: int
    requested_stop_price: float
    risk_price: float
    exit_bar: int
    exit_price: float
    exit_reason: str                   # 'stop'|'target'|'time'|'still_open_at_end'|'gap_through_target'
    still_open_at_end: bool
    results: tuple[ScenarioResult, ...]
    run_hash: str                      # R11 (§3)


EvalOutcome = ExecutedTrade | Rejection | InvalidExecution | NoEntry


# ── R11 (§3): run_hash pe două niveluri, acoperind ȘI datele. compare() RIDICĂ. ──
@dataclass(frozen=True)
class RunContext:
    """Identitatea DATELOR (§3). Fără ea, două rulări pe INSTRUMENTE DIFERITE ar împărți un hash."""
    symbol: str = "UNSPECIFIED"
    timeframe: str = "UNSPECIFIED"
    split_id: str = "UNSPECIFIED"
    block_manifest_hash: str = "UNSPECIFIED"
    n_blocks: int = 0
    holdout_cutoff: str = "UNSPECIFIED"


_DEFAULT_RUN = RunContext()


class NonComparableError(ValueError):
    """R11: comparația trebuie să fie IMPOSIBILĂ, nu descurajată."""


def _config_hash(scenarios: Sequence[CostScenario]) -> str:
    payload = {
        "scenarios": [[s.name, float(s.spread_price), s.entry_slippage_price, s.exit_slippage_price,
                       s.total_cost_price, "PROVISIONAL — NOT EMPIRICALLY CALIBRATED" if not s.calibrated else "CALIBRATED"]
                      for s in scenarios],
        "K_SPREAD": K_SPREAD, "K_TICK": K_TICK, "K_ATR": K_ATR, "tick_size": TICK_SIZE,
        "code_version": CODE_VERSION,   # fixează semantica regulilor R1-R7 + gap-guard
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def _data_identity_hash(run: RunContext) -> str:
    payload = {"symbol": run.symbol, "timeframe": run.timeframe, "split_id": run.split_id,
               "block_manifest_hash": run.block_manifest_hash, "n_blocks": run.n_blocks,
               "holdout_cutoff": run.holdout_cutoff}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def run_hash(scenarios: Sequence[CostScenario], run: RunContext) -> str:
    """§3: run_hash = sha256(config_hash ‖ sha256(data_identity))."""
    ch = _config_hash(scenarios)
    dih = _data_identity_hash(run)
    return hashlib.sha256((ch + dih).encode("utf-8")).hexdigest()[:16]


def compare(a_run_hash: str, b_run_hash: str) -> None:
    """§3: REFUZĂ, nu comentează. Ridică `NonComparableError` dacă run_hash-urile diferă."""
    if a_run_hash != b_run_hash:
        raise NonComparableError(f"NON_COMPARABLE: run_hash {a_run_hash} != {b_run_hash}")


def require_comparable(*run_hashes: str) -> None:
    """Impune comparația-pe-potrivire pe orice cale (ridică dacă vreo pereche diferă)."""
    uniq = list(dict.fromkeys(run_hashes))
    for i in range(1, len(uniq)):
        compare(uniq[0], uniq[i])


def _finite(x: float) -> bool:
    return x == x and x not in (float("inf"), float("-inf"))


def evaluate_signal(
    sig: Signal, open_: Sequence[float], high: Sequence[float], low: Sequence[float], close: Sequence[float],
    *, scenarios: Sequence[CostScenario] = DEFAULT_SCENARIOS, block_end: int | None = None,
    run: RunContext = _DEFAULT_RUN,
) -> EvalOutcome:
    """Evaluează UN semnal sub contract. Întoarce ExecutedTrade | Rejection | InvalidExecution | NoEntry. PUR, cauzal."""
    n = len(close)
    be = (n - 1) if block_end is None else min(block_end, n - 1)
    rh = run_hash(scenarios, run)
    ei = sig.signal_bar + 1                                     # R2

    if ei > be:
        return NoEntry(sig.strategy_id, sig.signal_id, sig.timestamp)
    entry = float(open_[ei])
    if not (_finite(entry) and _finite(sig.requested_stop_price) and _finite(sig.atr) and sig.atr > 0.0):
        return NoEntry(sig.strategy_id, sig.signal_id, sig.timestamp)
    dirn = 1 if sig.direction > 0 else -1
    stop_price = sig.requested_stop_price

    # ── GEOMETRIE STRICTĂ la open (AMENDAMENT CEO A2): risc ≤ 0 (gap/open pe stop) → INVALID_EXECUTION ──
    directional_risk = dirn * (entry - stop_price)
    if directional_risk <= 0.0:
        return InvalidExecution(sig.strategy_id, sig.signal_id, sig.timestamp, entry, stop_price,
                                directional_risk, "risk_nonpositive")

    risk = directional_risk                                    # = |entry − stop|, strict pozitiv aici

    if sig.target_kind == "rr" and sig.target_param is not None:
        tgt: float | None = entry + dirn * sig.target_param * risk
    elif sig.target_kind == "price" and sig.target_param is not None:
        tgt = sig.target_param
    else:
        tgt = None

    # ── GEOMETRIE STRICTĂ (A2): recompensă ≤ 0 (gap/open pe target) → INVALID_EXECUTION (NU ieșire-la-intrare) ──
    if tgt is not None and _finite(tgt):
        directional_reward = dirn * (tgt - entry)
        if directional_reward <= 0.0:
            return InvalidExecution(sig.strategy_id, sig.signal_id, sig.timestamp, entry, stop_price,
                                    directional_risk, "reward_nonpositive", directional_reward)

    # ── R3/D-2: RESPINGE dacă stopul cerut e sub podea (spread pe JUMĂTATE) ──
    ms = minimum_stop_distance(half_of(sig.spread_price), sig.atr)
    if risk < ms.minimum_stop_distance:
        return Rejection(sig.strategy_id, sig.signal_id, sig.timestamp, risk, ms.minimum_stop_distance,
                         sig.spread_price, sig.atr, ms.dominant_component)

    # ── R6: [ei, ei+H-1] ──
    last_hold = ei + sig.max_holding_bars - 1
    # ── R5: scanează de la BARA DE INTRARE; SL PRIMEAZĂ ──
    exit_bar = -1; exit_price = float("nan"); exit_reason = ""
    scan_last = min(last_hold, be)
    for j in range(ei, scan_last + 1):
        if dirn > 0:
            hit_stop = low[j] <= stop_price
            hit_tgt = tgt is not None and _finite(tgt) and high[j] >= tgt
        else:
            hit_stop = high[j] >= stop_price
            hit_tgt = tgt is not None and _finite(tgt) and low[j] <= tgt
        if hit_stop:
            exit_bar, exit_price, exit_reason = j, stop_price, "stop"; break
        if hit_tgt and tgt is not None:
            exit_bar, exit_price, exit_reason = j, tgt, "target"; break

    still_open = False
    if exit_reason == "":
        if last_hold > be:
            still_open = True
            exit_bar, exit_price, exit_reason = be, float(close[be]), "still_open_at_end"
        else:
            exit_bar, exit_price, exit_reason = last_hold, float(close[last_hold]), "time"

    results = tuple(
        ScenarioResult(sc.name, (dirn * (exit_price - entry) - sc.total_cost_price) / risk,
                       dirn * (exit_price - entry), sc.total_cost_price)
        for sc in scenarios)
    return ExecutedTrade(sig.strategy_id, sig.signal_id, ei, entry, dirn, stop_price, risk, exit_bar, exit_price,
                         exit_reason, still_open, results, rh)


# ────────────────────────── MEAS-10: concentrare + raportarea per strategie ──────────────────────────
@dataclass(frozen=True)
class Concentration:
    """§7: câmpurile R10 pe ieșirea OFICIALĂ (altfel garda fat-tail e necalculabilă). Tăiere: (R DESC, entry ASC),
    ceil-min-1; STRES ADVERSARIAL, nu estimator."""
    best_trade_share: LevelOutput[float]   # Unavailable('net_non_positive') dacă sum_R ≤ 0
    trimmed_top1_avg_R: float
    n_trimmed: int
    trimmed_fraction: float
    sum_R: float
    wo1_still_positive: bool


def _concentration(pairs: list[tuple[float, int]]) -> Concentration | None:
    """pairs = (net_R, entry_bar). None dacă populația e vidă."""
    if not pairs:
        return None
    rs = [r for r, _ in pairs]
    n = len(rs)
    sum_R = sum(rs)
    best: LevelOutput[float] = (Ok(max(rs) / sum_R, as_of=0, valid_until=1, schema_hash="concentration")
                                if sum_R > 0.0 else Unavailable(reason="net_non_positive", as_of=0))
    k = max(1, math.ceil(0.01 * n))                            # D-3 ceil-min-1
    order = sorted(range(n), key=lambda i: (-pairs[i][0], pairs[i][1]))   # (R DESC, entry ASC)
    removed = set(order[:k])
    kept = [rs[i] for i in range(n) if i not in removed]
    trimmed_avg = (sum(kept) / len(kept)) if kept else 0.0
    return Concentration(best, trimmed_avg, k, k / n, sum_R, trimmed_avg > 0.0)


@dataclass(frozen=True)
class StrategyReport:
    strategy_id: str
    run_hash: str
    total_signals: int
    eligible_trades: int
    rejected: int
    rejected_pct: float
    rejection_reasons: tuple[tuple[str, int], ...]
    invalid_executions: int            # §5(a) MEAS-9: gap prin stop, NUMĂRAT, exclus din randamente
    no_entry: int
    still_open_at_end: int
    base_mean_R: float | None
    stress_mean_R: float | None
    base_minus_stress: float | None
    base_concentration: Concentration | None    # §7 MEAS-10
    stress_concentration: Concentration | None


def _mean(xs: list[float]) -> float | None:
    return (sum(xs) / len(xs)) if xs else None


def evaluate_strategy(
    strategy_id: str, signals: Sequence[Signal],
    open_: Sequence[float], high: Sequence[float], low: Sequence[float], close: Sequence[float],
    *, scenarios: Sequence[CostScenario] = DEFAULT_SCENARIOS, block_end: int | None = None,
    run: RunContext = _DEFAULT_RUN,
) -> tuple[StrategyReport, list[EvalOutcome]]:
    outcomes: list[EvalOutcome] = [
        evaluate_signal(s, open_, high, low, close, scenarios=scenarios, block_end=block_end, run=run)
        for s in signals]
    rh = run_hash(scenarios, run)
    execd = [o for o in outcomes if isinstance(o, ExecutedTrade)]
    eligible = [o for o in execd if not o.still_open_at_end]
    still_open = [o for o in execd if o.still_open_at_end]
    rejs = [o for o in outcomes if isinstance(o, Rejection)]
    invalids = [o for o in outcomes if isinstance(o, InvalidExecution)]
    noent = [o for o in outcomes if isinstance(o, NoEntry)]

    reasons: dict[str, int] = {}
    for r in rejs:
        reasons[r.reason_code] = reasons.get(r.reason_code, 0) + 1

    def _scn(o: ExecutedTrade, name: str) -> float:
        return next(r.net_R for r in o.results if r.scenario == name)

    base_pairs = [(_scn(o, BASE_PROVISIONAL.name), o.entry_bar) for o in eligible]
    stress_pairs = [(_scn(o, STRESS_PROVISIONAL.name), o.entry_bar) for o in eligible]
    base = [r for r, _ in base_pairs]; stress = [r for r, _ in stress_pairs]
    bm, sm = _mean(base), _mean(stress)
    total = len(signals)
    report = StrategyReport(
        strategy_id=strategy_id, run_hash=rh, total_signals=total, eligible_trades=len(eligible),
        rejected=len(rejs), rejected_pct=(100.0 * len(rejs) / total) if total else 0.0,
        rejection_reasons=tuple(sorted(reasons.items())), invalid_executions=len(invalids),
        no_entry=len(noent), still_open_at_end=len(still_open),
        base_mean_R=bm, stress_mean_R=sm,
        base_minus_stress=(bm - sm) if (bm is not None and sm is not None) else None,
        base_concentration=_concentration(base_pairs), stress_concentration=_concentration(stress_pairs))
    return report, outcomes
