"""Schema exactă a inputului și outputului pt. rularea detectorului V4.3 înghețat (`f224e7d`) pe
bare reale. Derivată din API-ul real al prototipului (`ve_n1_replay._ai.ai_trader.live_signal_source.
types.Bar` -- tipul REAL pe care `RangeSemanticEngineV43.observe_closed_bar`/`replay_batch` îl
consumă -- nu un tip inventat). Nicio valoare implicită ascunsă: fiecare câmp obligatoriu al
`Bar`-ului real e obligatoriu și aici.

`Bar` real (câmpurile pe care le folosim -- `symbol` e purtat la nivel de fereastră, nu per-bară,
ca să nu se repete inutil; `volume`/`is_backfilled` sunt opționale, exact ca-n tipul real):
    ts_open: int, ts_close: int, open: float, high: float, low: float, close: float,
    volume: float | None, is_backfilled: bool = False
"""
from __future__ import annotations

import dataclasses as dc
import math
from typing import Any


class InputValidationError(Exception):
    """Fail-closed, cu `code` distinct per tip de defect (mandat §5) -- niciodată o singură
    excepție generică ce ascunde CE anume a eșuat."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        super().__init__(f"{code}: {detail}")


# ═══════════════════════════ F1 -- toleranță OHLC sub-tick (RT-RANGE-0011, `8d71fce`) ═══════════════════════════
# Remediază F1 (RT-RANGE-0010 `57a0cd4`): CLI-ul audiat respingea fail-closed 13/13.824 bare reale --
# close-ul OANDA XAUUSD M15 sub-tick depășea [low,high] cu exact 0,0005 USD (artefact de rotunjire mixtă
# de precizie a vendorului -- high la 3 zecimale, close la 4 -- NU o eroare de extracție/date). Portat din
# oracolul deja verificat INDEPENDENT de două ori (Statistician `870d3f8`/fingerprint `662b3bca…`, 27/28
# teste + mypy strict; Red Team `RT-RANGE-0011`/`8d71fce`, reprodus independent din corpusul canonic:
# 13/13.824, toate pe close, 9 peste high/4 sub low, magnitudine unică 0,0005) -- NU o implementare nouă,
# independentă, ci exact aceeași regulă, integrată în validatorul acestui runner.
INPUT_CONTRACT_VERSION = "ohlc_input_contract_v1"

# `min_tick` NU e un literal ascuns -- vine din metadata simbolului (mandat §4.1: "trebuie derivată din
# metadata simbolului"). `0.01` pt. XAUUSD e deja normativ în proiect: declarat în `SymbolMeta` pe patru
# subsisteme AI Trader și ratificat independent de Red Team în `RT-AUDIT-MEAS-0001` (care a corectat o
# valoare greșită de 0.1 acolo) -- nu o constantă inventată pt. ca cele 13 bare să treacă. Simbol
# necunoscut -> fail-closed (`UNKNOWN_SYMBOL_MIN_TICK`), nu un tick implicit ghicit.
SYMBOL_MIN_TICK: dict[str, float] = {"XAUUSD": 0.01}

INPUT_OHLC_SUBTICK_TOLERATED = "INPUT_OHLC_SUBTICK_TOLERATED"


class UnknownSymbolMinTickError(InputValidationError):
    def __init__(self, symbol: str) -> None:
        super().__init__("UNKNOWN_SYMBOL_MIN_TICK", f"niciun min_tick normativ pt. simbolul {symbol!r}")


def epsilon_for(min_tick: float) -> float:
    """Deriva toleranța (mandat §4.1: `epsilon = min_tick / 2`). Refuză fail-closed un tick absent,
    zero, negativ sau non-finit -- nu un implicit tăcut."""
    if min_tick is None or isinstance(min_tick, bool) or not isinstance(min_tick, (int, float)):
        raise InputValidationError("INVALID_MIN_TICK", f"min_tick invalid: {min_tick!r}")
    min_tick = float(min_tick)
    if not math.isfinite(min_tick) or min_tick <= 0.0:
        raise InputValidationError("INVALID_MIN_TICK", f"min_tick invalid: {min_tick!r}")
    return min_tick / 2.0


@dc.dataclass(frozen=True, slots=True)
class InputQualityEvent:
    """Eveniment de INFRASTRUCTURĂ/calitatea datelor -- NU un reason code semantic RANGE (mandat §4.4,
    verificat mecanic: `tests/test_f1_ohlc_tolerance.py::test_quality_event_outside_29_reason_codes`).
    `bar_index` e RELATIV la fereastră, niciodată absolut (mandat §6, aceeași convenție ca restul
    output-ului acestui runner) -- nu ts_close real, care nu are voie în output-ul pt. evaluare."""
    kind: str
    symbol: str
    window_id: str
    bar_index: int
    field: str                 # "open" | "close"
    direction: str              # "above_high" | "below_low"
    boundary: float             # valoarea high/low față de care s-a măsurat abaterea
    original_value: float       # valoarea originală, NEmodificată
    min_tick: float
    epsilon: float
    validator_version: str = INPUT_CONTRACT_VERSION


@dc.dataclass(frozen=True, slots=True)
class InputBar:
    ts_open: int
    ts_close: int
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None
    is_backfilled: bool = False


@dc.dataclass(frozen=True, slots=True)
class InputWindow:
    window_id: str
    symbol: str
    timeframe: str
    bar_interval_seconds: int
    bars: tuple[InputBar, ...]


_REQUIRED_BAR_FIELDS = ("ts_open", "ts_close", "open", "high", "low", "close")
_REQUIRED_WINDOW_FIELDS = ("window_id", "symbol", "timeframe", "bar_interval_seconds", "bars")


def _validate_bar_dict(raw: Any, window_id: str, idx: int, symbol: str,
                       min_tick: float) -> tuple[InputBar, InputQualityEvent | None]:
    if not isinstance(raw, dict):
        raise InputValidationError("MALFORMED_BAR", f"{window_id}[{idx}]: bara nu e un obiect")
    for f in _REQUIRED_BAR_FIELDS:
        if f not in raw or raw[f] is None:
            raise InputValidationError("MISSING_FIELD", f"{window_id}[{idx}]: câmp lipsă '{f}'")
    ts_open, ts_close = raw["ts_open"], raw["ts_close"]
    if not isinstance(ts_open, int) or not isinstance(ts_close, int):
        raise InputValidationError("MISSING_TIMESTAMP", f"{window_id}[{idx}]: ts_open/ts_close nu sunt int")
    ohlc = {}
    for f in ("open", "high", "low", "close"):
        v = raw[f]
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            raise InputValidationError("MISSING_OHLC", f"{window_id}[{idx}]: '{f}' lipsă sau non-numeric")
        v = float(v)
        if not math.isfinite(v):
            raise InputValidationError("NON_FINITE_VALUE", f"{window_id}[{idx}]: '{f}'={v} non-finit")
        ohlc[f] = v
    if ohlc["high"] < ohlc["low"]:
        raise InputValidationError("HIGH_LESS_THAN_LOW",
                                   f"{window_id}[{idx}]: high={ohlc['high']} < low={ohlc['low']}")

    # F1 (§4.1/§4.2 mandat): comparație VALOARE-vs-frontieră-DEPLASATĂ (`v > hi+eps`/`v < lo-eps` ->
    # respinge), NU diferență-vs-epsilon (`v - hi <= eps`) -- cele două NU sunt echivalente în float64:
    # o valoare construită EXACT ca `hi + eps` dă o diferență ce depășește `eps` cu câțiva ULP, deci o
    # comparație pe diferență ar respinge exact cazul de egalitate pe care contractul îl declară ADMIS.
    # Forma de mai jos e exactă prin construcție, fără nicio marjă inventată (bug propriu găsit chiar de
    # Statistician prin testele proprii, v. istoricul `870d3f8` -- corectat aici de la prima implementare).
    eps = epsilon_for(min_tick)
    best_event: InputQualityEvent | None = None
    for field, err_code in (("open", "OPEN_OUTSIDE_HIGH_LOW"), ("close", "CLOSE_OUTSIDE_HIGH_LOW")):
        v = ohlc[field]
        if ohlc["low"] <= v <= ohlc["high"]:
            continue
        if v > ohlc["high"] + eps or v < ohlc["low"] - eps:
            raise InputValidationError(
                err_code, f"{window_id}[{idx}]: {field}={v} în afara [{ohlc['low']},{ohlc['high']}] "
                         f"±epsilon={eps}")
        direction = "above_high" if v > ohlc["high"] else "below_low"
        boundary_v = ohlc["high"] if direction == "above_high" else ohlc["low"]
        magnitude = abs(v - boundary_v)
        ev = InputQualityEvent(kind=INPUT_OHLC_SUBTICK_TOLERATED, symbol=symbol, window_id=window_id,
                               bar_index=idx, field=field, direction=direction, boundary=boundary_v,
                               original_value=v, min_tick=min_tick, epsilon=eps)
        # un singur eveniment per bară -- magnitudinea cea mai mare câștigă (close înaintea lui open la
        # egalitate, prin ordinea buclei de mai sus, identic oracolului deja auditat)
        if best_event is None or magnitude > abs(best_event.original_value - best_event.boundary):
            best_event = ev

    volume = raw.get("volume")
    if volume is not None:
        if not isinstance(volume, (int, float)) or isinstance(volume, bool) or not math.isfinite(float(volume)):
            raise InputValidationError("NON_FINITE_VALUE", f"{window_id}[{idx}]: volume non-finit")
        volume = float(volume)
    is_backfilled = bool(raw.get("is_backfilled", False))
    bar = InputBar(ts_open=ts_open, ts_close=ts_close, open=ohlc["open"], high=ohlc["high"],
                   low=ohlc["low"], close=ohlc["close"], volume=volume, is_backfilled=is_backfilled)
    return bar, best_event


def validate_and_normalize_window(raw: Any) -> tuple[InputWindow, tuple[InputQualityEvent, ...]]:
    """Validează fail-closed o singură fereastră (dict brut din JSON) și o normalizează la
    `InputWindow`. Ordinea verificărilor urmează exact lista mandatului §5. Întoarce și evenimentele
    de calitate F1 (cel mult unul per bară) -- STATELESS: nicio bară nu influențează validarea altei
    bare, deci concatenarea pe fragmente == validarea întregii ferestre (mandat §10, chunk invariance)."""
    if not isinstance(raw, dict):
        raise InputValidationError("CORRUPT_FILE", "fereastra nu e un obiect JSON")
    for f in _REQUIRED_WINDOW_FIELDS:
        if f not in raw:
            raise InputValidationError("PARTIAL_DATA", f"câmp de fereastră lipsă: '{f}'")
    window_id = raw["window_id"]
    if not isinstance(window_id, str) or not window_id:
        raise InputValidationError("MALFORMED_WINDOW_ID", "window_id lipsă sau gol")
    symbol, timeframe = raw["symbol"], raw["timeframe"]
    bar_interval_seconds = raw["bar_interval_seconds"]
    if not isinstance(symbol, str) or not symbol:
        raise InputValidationError("WRONG_TIMEFRAME", "symbol lipsă/invalid")
    if not isinstance(timeframe, str) or not timeframe:
        raise InputValidationError("WRONG_TIMEFRAME", "timeframe lipsă/invalid")
    if not isinstance(bar_interval_seconds, int) or bar_interval_seconds <= 0:
        raise InputValidationError("WRONG_TIMEFRAME", f"bar_interval_seconds invalid: {bar_interval_seconds!r}")
    if symbol not in SYMBOL_MIN_TICK:
        raise UnknownSymbolMinTickError(symbol)
    min_tick = SYMBOL_MIN_TICK[symbol]
    raw_bars = raw["bars"]
    if not isinstance(raw_bars, list) or len(raw_bars) == 0:
        raise InputValidationError("EMPTY_WINDOW", f"{window_id}: fereastră fără bare")
    bars: list[InputBar] = []
    quality_events: list[InputQualityEvent] = []
    for i, b in enumerate(raw_bars):
        bar, ev = _validate_bar_dict(b, window_id, i, symbol, min_tick)
        bars.append(bar)
        if ev is not None:
            quality_events.append(ev)

    seen_ts: set[int] = set()
    prev_ts: int | None = None
    for i, b in enumerate(bars):
        if b.ts_close in seen_ts:
            raise InputValidationError("DUPLICATE_BAR", f"{window_id}[{i}]: ts_close={b.ts_close} duplicat")
        seen_ts.add(b.ts_close)
        if prev_ts is not None and b.ts_close <= prev_ts:
            raise InputValidationError("BAD_TEMPORAL_ORDER",
                                       f"{window_id}[{i}]: ts_close={b.ts_close} nu e strict crescător "
                                       f"față de bara anterioară ({prev_ts})")
        prev_ts = b.ts_close

    window = InputWindow(window_id=window_id, symbol=symbol, timeframe=timeframe,
                         bar_interval_seconds=bar_interval_seconds, bars=tuple(bars))
    return window, tuple(quality_events)


def validate_and_normalize_input(
    raw: Any
) -> tuple[tuple[InputWindow, ...], tuple[InputQualityEvent, ...]]:
    """Validează inputul complet (mai multe ferestre). Refuză ID-uri de fereastră duplicate."""
    if not isinstance(raw, dict) or "windows" not in raw:
        raise InputValidationError("CORRUPT_FILE", "inputul trebuie să fie {\"windows\": [...]}")
    raw_windows = raw["windows"]
    if not isinstance(raw_windows, list) or len(raw_windows) == 0:
        raise InputValidationError("PARTIAL_DATA", "\"windows\" lipsă sau goală")
    windows = []
    all_events: list[InputQualityEvent] = []
    seen_ids: set[str] = set()
    for rw in raw_windows:
        w, evs = validate_and_normalize_window(rw)
        if w.window_id in seen_ids:
            raise InputValidationError("DUPLICATE_WINDOW_ID", f"window_id duplicat: {w.window_id}")
        seen_ids.add(w.window_id)
        windows.append(w)
        all_events.extend(evs)
    return tuple(windows), tuple(all_events)
