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


def _validate_bar_dict(raw: Any, window_id: str, idx: int) -> InputBar:
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
    if not (ohlc["low"] <= ohlc["open"] <= ohlc["high"]):
        raise InputValidationError("OPEN_OUTSIDE_HIGH_LOW",
                                   f"{window_id}[{idx}]: open={ohlc['open']} în afara [{ohlc['low']},{ohlc['high']}]")
    if not (ohlc["low"] <= ohlc["close"] <= ohlc["high"]):
        raise InputValidationError("CLOSE_OUTSIDE_HIGH_LOW",
                                   f"{window_id}[{idx}]: close={ohlc['close']} în afara [{ohlc['low']},{ohlc['high']}]")
    volume = raw.get("volume")
    if volume is not None:
        if not isinstance(volume, (int, float)) or isinstance(volume, bool) or not math.isfinite(float(volume)):
            raise InputValidationError("NON_FINITE_VALUE", f"{window_id}[{idx}]: volume non-finit")
        volume = float(volume)
    is_backfilled = bool(raw.get("is_backfilled", False))
    return InputBar(ts_open=ts_open, ts_close=ts_close, open=ohlc["open"], high=ohlc["high"],
                    low=ohlc["low"], close=ohlc["close"], volume=volume, is_backfilled=is_backfilled)


def validate_and_normalize_window(raw: Any) -> InputWindow:
    """Validează fail-closed o singură fereastră (dict brut din JSON) și o normalizează la
    `InputWindow`. Ordinea verificărilor urmează exact lista mandatului §5."""
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
    raw_bars = raw["bars"]
    if not isinstance(raw_bars, list) or len(raw_bars) == 0:
        raise InputValidationError("EMPTY_WINDOW", f"{window_id}: fereastră fără bare")
    bars = [_validate_bar_dict(b, window_id, i) for i, b in enumerate(raw_bars)]

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

    return InputWindow(window_id=window_id, symbol=symbol, timeframe=timeframe,
                       bar_interval_seconds=bar_interval_seconds, bars=tuple(bars))


def validate_and_normalize_input(raw: Any) -> tuple[InputWindow, ...]:
    """Validează inputul complet (mai multe ferestre). Refuză ID-uri de fereastră duplicate."""
    if not isinstance(raw, dict) or "windows" not in raw:
        raise InputValidationError("CORRUPT_FILE", "inputul trebuie să fie {\"windows\": [...]}")
    raw_windows = raw["windows"]
    if not isinstance(raw_windows, list) or len(raw_windows) == 0:
        raise InputValidationError("PARTIAL_DATA", "\"windows\" lipsă sau goală")
    windows = []
    seen_ids: set[str] = set()
    for rw in raw_windows:
        w = validate_and_normalize_window(rw)
        if w.window_id in seen_ids:
            raise InputValidationError("DUPLICATE_WINDOW_ID", f"window_id duplicat: {w.window_id}")
        seen_ids.add(w.window_id)
        windows.append(w)
    return tuple(windows)
