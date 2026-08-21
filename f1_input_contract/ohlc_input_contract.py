"""CONTRACT DE INPUT OHLC — `ohlc_input_contract_v1`. Remediaza F1 (RT-RANGE-0010, `57a0cd4`).

Toleranta sub-tick DERIVATA, nu literal ascuns:

    min_tick                 = 0.01 USD     (XAUUSD, deja normativ in proiect)
    ohlc_validation_epsilon  = min_tick / 2 = 0.005 USD

NU modifica valorile OHLC. NU taie, NU rotunjeste, NU normalizeaza, NU rescrie, NU reordoneaza.
Valideaza si emite un eveniment de calitate; detectorul primeste valori IDENTICE cu sursa.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Iterable, Sequence

INPUT_CONTRACT_VERSION = "ohlc_input_contract_v1"

# `tick_size = 0.01` pentru XAUUSD e deja normativ in proiect: declarat in `SymbolMeta` pe patru
# subsisteme AI Trader (decision_comparison, decision_intelligence, decision_intelligence_v2,
# edge_intelligence) si ratificat independent de Red Team in RT-AUDIT-MEAS-0001, care a si CORECTAT
# o valoare gresita de 0.1. NU e o constanta introdusa pentru F1.
MIN_TICK: float = 0.01
OHLC_VALIDATION_EPSILON: float = MIN_TICK / 2.0        # DERIVAT, nu literal

# Eveniment de CALITATE A INPUTULUI — NU intra in cele 29 de reason codes semantice ale detectorului.
INPUT_QUALITY_EVENTS = ("INPUT_OHLC_SUBTICK_TOLERATED",)

# Erori fail-closed ale contractului de input (tot in afara setului semantic).
INPUT_ERRORS = ("HIGH_BELOW_LOW", "NON_FINITE_VALUE", "MISSING_FIELD", "NON_NUMERIC_VALUE",
                "CLOSE_OUTSIDE_HIGH_LOW", "OPEN_OUTSIDE_HIGH_LOW", "INVALID_MIN_TICK")

REQUIRED_FIELDS = ("open", "high", "low", "close")


class InputContractError(ValueError):
    """Refuz fail-closed al contractului de input."""

    def __init__(self, code: str, bar_index: int) -> None:
        super().__init__(f"{code} @ bara relativa {bar_index}")
        self.code = code
        self.bar_index = bar_index


@dataclass(frozen=True)
class InputQualityEvent:
    """Schema evenimentului. `bar_index` e RELATIV la fereastra, niciodata absolut."""
    kind: str
    bar_index: int
    field: str                 # "open" | "close"
    direction: str             # "above_high" | "below_low"
    magnitude: float           # abaterea, in USD
    epsilon: float
    contract_version: str = INPUT_CONTRACT_VERSION


def epsilon_for(min_tick: float = MIN_TICK) -> float:
    """Deriva toleranta. Refuza fail-closed un tick absent, zero sau negativ."""
    if min_tick is None or not isinstance(min_tick, (int, float)) or isinstance(min_tick, bool):
        raise InputContractError("INVALID_MIN_TICK", -1)
    if not math.isfinite(min_tick) or min_tick <= 0.0:
        raise InputContractError("INVALID_MIN_TICK", -1)
    return float(min_tick) / 2.0


def validate_bar(bar: Any, bar_index: int, *, min_tick: float = MIN_TICK) -> InputQualityEvent | None:
    """Valideaza O bara. Intoarce cel mult UN eveniment de toleranta; ridica la orice incalcare.

    Prioritate (fail-closed inaintea tolerantei): camp lipsa -> non-numeric -> non-finit ->
    `high >= low` -> abateri open/close fata de `[low - eps, high + eps]`.
    Un singur eveniment per bara: daca si open si close ar fi tolerate, se raporteaza abaterea
    cu magnitudinea cea mai mare (determinist, cu `close` inaintea lui `open` la egalitate).
    """
    eps = epsilon_for(min_tick)
    vals: dict[str, float] = {}
    for f in REQUIRED_FIELDS:
        if isinstance(bar, dict):
            if f not in bar:
                raise InputContractError("MISSING_FIELD", bar_index)
            v = bar[f]
        else:
            if not hasattr(bar, f):
                raise InputContractError("MISSING_FIELD", bar_index)
            v = getattr(bar, f)
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise InputContractError("NON_NUMERIC_VALUE", bar_index)
        v = float(v)
        if not math.isfinite(v):
            raise InputContractError("NON_FINITE_VALUE", bar_index)
        vals[f] = v

    hi, lo = vals["high"], vals["low"]
    if hi < lo:
        raise InputContractError("HIGH_BELOW_LOW", bar_index)

    best: InputQualityEvent | None = None
    for f, err in (("close", "CLOSE_OUTSIDE_HIGH_LOW"), ("open", "OPEN_OUTSIDE_HIGH_LOW")):
        v = vals[f]
        if lo <= v <= hi:
            continue
        # ★ Comparatia se face VALOARE fata de FRONTIERA DEPLASATA (`v <= hi + eps`), nu diferenta
        # fata de epsilon (`v - hi <= eps`). Cele doua nu sunt echivalente in float64: o valoare
        # construita exact ca `hi + eps` da o diferenta care depaseste `eps` cu cativa ULP, si o
        # comparatie pe diferenta ar respinge exact cazul de egalitate pe care contractul il declara
        # ADMIS. Forma de mai jos e exacta prin constructie si nu are nevoie de nicio marja inventata.
        if v > hi + eps or v < lo - eps:  # depasire STRICTA -> fail-closed
            raise InputContractError(err, bar_index)
        dev = (v - hi) if v > hi else (lo - v)
        ev = InputQualityEvent(kind="INPUT_OHLC_SUBTICK_TOLERATED", bar_index=bar_index, field=f,
                               direction="above_high" if v > hi else "below_low",
                               magnitude=dev, epsilon=eps)
        if best is None or ev.magnitude > best.magnitude:
            best = ev
    return best


def validate_window(bars: Sequence[Any] | Iterable[Any], *,
                    min_tick: float = MIN_TICK) -> list[InputQualityEvent]:
    """Valideaza o fereastra. NU modifica si NU reordoneaza barele; intoarce doar evenimentele.

    Determinist si invariant la fragmentare (`chunk invariance`): validarea unei bare nu depinde de
    nicio alta bara, deci concatenarea evenimentelor pe fragmente e identica cu validarea intregului.
    Restart/snapshot: contractul e FARA STARE, deci un restart nu poate schimba rezultatul.
    """
    return [ev for i, b in enumerate(bars)
            if (ev := validate_bar(b, i, min_tick=min_tick)) is not None]
