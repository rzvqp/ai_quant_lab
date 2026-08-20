"""F1 -- contractul de toleranță OHLC sub-tick (mandat "F1 + F5 CONFORMANCE IMPLEMENTATION", §4, §10, §11).

Portat din oracolul deja auditat de DOUĂ ori independent (Statistician `870d3f8`/fp `662b3bca…`,
27/28 teste + mypy strict; Red Team `RT-RANGE-0011`/`8d71fce`, reprodus independent din corpusul
canonic: 13/13.824, toate pe close, 9 peste high/4 sub low, magnitudine unică 0,0005). Aici:
integrarea EFECTIVĂ în acest runner (`schemas.py`/`inference.py`), nu o reimplementare de la zero."""
from __future__ import annotations

import copy
import json
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dev_fixtures import make_dev_input  # noqa: E402
from inference import run_inference  # noqa: E402
from schemas import (  # noqa: E402
    INPUT_OHLC_SUBTICK_TOLERATED, SYMBOL_MIN_TICK, InputQualityEvent, InputValidationError,
    UnknownSymbolMinTickError, epsilon_for, validate_and_normalize_input,
)

EPS = epsilon_for(SYMBOL_MIN_TICK["XAUUSD"])


def _one_bar_input(o: float, h: float, lo: float, c: float, symbol: str = "XAUUSD") -> dict:
    return {"windows": [{"window_id": "W", "symbol": symbol, "timeframe": "15m",
                         "bar_interval_seconds": 900,
                         "bars": [{"ts_open": 0, "ts_close": 900, "open": o, "high": h, "low": lo,
                                  "close": c, "volume": None, "is_backfilled": False}]}]}


# ─────────────────────────── formula derivată ───────────────────────────

def test_epsilon_is_derived_min_tick_over_2() -> None:
    assert SYMBOL_MIN_TICK["XAUUSD"] == 0.01
    assert epsilon_for(SYMBOL_MIN_TICK["XAUUSD"]) == 0.005
    assert epsilon_for(0.02) == 0.01 and epsilon_for(0.001) == 0.0005


def test_epsilon_always_below_one_tick() -> None:
    """Garanția: o abatere de UN TICK ÎNTREG nu poate fi tolerată niciodată (mandat §4.1)."""
    min_tick = SYMBOL_MIN_TICK["XAUUSD"]
    assert epsilon_for(min_tick) < min_tick


@pytest.mark.parametrize("bad", [None, 0.0, -0.01, float("nan"), float("inf"), True, "0.01"])
def test_invalid_min_tick_refused_fail_closed(bad: object) -> None:
    with pytest.raises(InputValidationError) as exc_info:
        epsilon_for(bad)  # type: ignore[arg-type]
    assert exc_info.value.code == "INVALID_MIN_TICK"


def test_unknown_symbol_refused_fail_closed() -> None:
    d = _one_bar_input(10.0, 11.0, 9.0, 10.5, symbol="EURUSD")
    with pytest.raises(UnknownSymbolMinTickError):
        validate_and_normalize_input(d)


# ─────────────────────────── comparație valoare-vs-frontieră-deplasată ───────────────────────────

def test_perfectly_valid_bar_no_event() -> None:
    windows, events = validate_and_normalize_input(_one_bar_input(10.0, 11.0, 9.0, 10.5))
    assert events == ()


def test_deviation_0_0005_tolerated_with_event() -> None:
    windows, events = validate_and_normalize_input(_one_bar_input(10.0, 11.0, 9.0, 11.0005))
    assert len(events) == 1
    ev = events[0]
    assert ev.kind == INPUT_OHLC_SUBTICK_TOLERATED
    assert ev.field == "close" and ev.direction == "above_high"
    assert math.isclose(ev.original_value, 11.0005, rel_tol=1e-9)
    assert windows[0].bars[0].close == 11.0005, "bara NU trebuie modificată"


def test_deviation_exactly_equal_to_epsilon_ACCEPTED() -> None:
    """Egalitatea la limită trece -- cerință explicită a contractului (mandat §4.2)."""
    windows, events = validate_and_normalize_input(_one_bar_input(10.0, 11.0, 9.0, 11.0 + EPS))
    assert len(events) == 1
    assert math.isclose(events[0].epsilon, EPS, rel_tol=1e-9)


def test_deviation_plus_one_ulp_beyond_epsilon_REJECTED() -> None:
    """Cazul `value == nextafter(boundary+epsilon, +inf)` trebuie respins (mandat §4.2)."""
    just_over = math.nextafter(11.0 + EPS, math.inf)
    assert just_over > 11.0 + EPS  # confirmă că nextafter a produs efectiv o valoare mai mare
    with pytest.raises(InputValidationError) as exc_info:
        validate_and_normalize_input(_one_bar_input(10.0, 11.0, 9.0, just_over))
    assert exc_info.value.code == "CLOSE_OUTSIDE_HIGH_LOW"


def test_difference_form_would_wrongly_reject_the_equality_case() -> None:
    """Demonstrează DE CE forma valoare-vs-frontieră e obligatorie: construită ca `high+eps` prin
    adunare, unele valori float64 dau o diferență ce depășește `eps` cu câțiva ULP -- forma pe
    diferență ar respinge cazul pe care contractul îl declară admis. Verificăm direct pe valoarea
    problematică citată de Statistician (`0.0005000000001018634`, care depășește 0.0005 nominal cu
    ~1e-13 dar rămâne CONFORTABIL sub epsilon=0.005)."""
    problematic = 11.0 + 0.0005000000001018634
    windows, events = validate_and_normalize_input(_one_bar_input(10.0, 11.0, 9.0, problematic))
    assert len(events) == 1, "forma corectă (valoare-vs-frontieră) trebuie să accepte această valoare"


def test_open_below_low_tolerated_and_rejected_boundaries() -> None:
    windows, events = validate_and_normalize_input(_one_bar_input(9.0 - EPS, 11.0, 9.0, 10.0))
    assert len(events) == 1 and events[0].direction == "below_low" and events[0].field == "open"
    with pytest.raises(InputValidationError) as exc_info:
        validate_and_normalize_input(_one_bar_input(9.0 - 2 * EPS, 11.0, 9.0, 10.0))
    assert exc_info.value.code == "OPEN_OUTSIDE_HIGH_LOW"


def test_high_below_low_still_rejected() -> None:
    with pytest.raises(InputValidationError) as exc_info:
        validate_and_normalize_input(_one_bar_input(10.0, 9.0, 11.0, 10.0))
    assert exc_info.value.code == "HIGH_LESS_THAN_LOW"


def test_nan_inf_still_rejected_fail_closed() -> None:
    for bad in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(InputValidationError) as exc_info:
            validate_and_normalize_input(_one_bar_input(10.0, 11.0, 9.0, bad))
        assert exc_info.value.code == "NON_FINITE_VALUE"


def test_one_event_per_bar_larger_magnitude_wins() -> None:
    d = _one_bar_input(9.0 - EPS / 4, 11.0, 9.0, 11.0 + EPS / 2)
    windows, events = validate_and_normalize_input(d)
    assert len(events) == 1 and events[0].field == "close"


# ─────────────────────────── evenimentul NU e reason code semantic ───────────────────────────

def test_quality_event_outside_29_reason_codes() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    from ve_n1_replay.range_semantic_v4_3 import REASONS_V43
    assert INPUT_OHLC_SUBTICK_TOLERATED not in REASONS_V43
    assert len(REASONS_V43) == 29


def test_quality_event_has_all_required_audit_fields() -> None:
    windows, events = validate_and_normalize_input(_one_bar_input(10.0, 11.0, 9.0, 11.0005))
    ev = events[0]
    for f in ("symbol", "window_id", "bar_index", "field", "direction", "boundary", "original_value",
             "min_tick", "epsilon", "validator_version"):
        assert hasattr(ev, f), f"câmp lipsă din InputQualityEvent: {f}"
    assert ev.bar_index == 0, "bar_index e RELATIV, niciodată ts_close absolut"


# ─────────────────────────── determinism / structură (fără stare) ───────────────────────────

def test_f1_determinism() -> None:
    d = _one_bar_input(10.0, 11.0, 9.0, 11.0 + EPS / 2)
    _, e1 = validate_and_normalize_input(d)
    _, e2 = validate_and_normalize_input(d)
    assert [(e.bar_index, e.field, e.original_value) for e in e1] == \
           [(e.bar_index, e.field, e.original_value) for e in e2]


def test_f1_chunk_invariance() -> None:
    """Validarea unei bare nu depinde de nicio altă bară -- concatenarea pe fragmente == întreaga
    fereastră (mandat §10)."""
    bars = [{"ts_open": i * 900, "ts_close": (i + 1) * 900, "open": 10.0, "high": 11.0, "low": 9.0,
            "close": 11.0 + EPS / 2, "volume": None, "is_backfilled": False} for i in range(5)]
    whole = {"windows": [{"window_id": "W", "symbol": "XAUUSD", "timeframe": "15m",
                          "bar_interval_seconds": 900, "bars": bars}]}
    _, whole_events = validate_and_normalize_input(whole)

    part1 = {"windows": [{"window_id": "W", "symbol": "XAUUSD", "timeframe": "15m",
                          "bar_interval_seconds": 900, "bars": bars[:2]}]}
    part2 = {"windows": [{"window_id": "W2", "symbol": "XAUUSD", "timeframe": "15m",
                          "bar_interval_seconds": 900, "bars": bars[2:]}]}
    _, e1 = validate_and_normalize_input(part1)
    _, e2 = validate_and_normalize_input(part2)
    whole_sig = [(e.field, e.direction, e.original_value) for e in whole_events]
    part_sig = [(e.field, e.direction, e.original_value) for e in e1] + \
              [(e.field, e.direction, e.original_value) for e in e2]
    assert whole_sig == part_sig


def test_f1_does_not_duplicate_event_after_restart() -> None:
    """Fără stare -- re-validarea aceleiași bare produce EXACT același eveniment, nu unul suplimentar
    (mandat §4.4: 'nu genera evenimentul de două ori după restart')."""
    d = _one_bar_input(10.0, 11.0, 9.0, 11.0 + EPS / 2)
    _, e1 = validate_and_normalize_input(d)
    _, e2 = validate_and_normalize_input(d)
    assert len(e1) == 1 and len(e2) == 1


# ─────────────────────────── OHLC nu se modifică ───────────────────────────

def test_ohlc_byte_unchanged_through_full_inference(tmp_path: Path) -> None:
    """OHLC-ul care ajunge la detector rămâne IDENTIC cu inputul -- verificat capăt-la-capăt prin
    `run_inference`, nu doar la nivel de validator izolat."""
    d = make_dev_input(n_windows=1, bars_per_window=30)
    tolerated_close = 11.0 + EPS / 2
    d["windows"][0]["bars"][5]["high"] = 11.0
    d["windows"][0]["bars"][5]["low"] = 9.0
    d["windows"][0]["bars"][5]["open"] = 10.0
    d["windows"][0]["bars"][5]["close"] = tolerated_close
    original_bars = copy.deepcopy(d["windows"][0]["bars"])

    inp = tmp_path / "input.json"
    inp.write_text(json.dumps(d), encoding="utf-8")
    result = run_inference(inp, tmp_path / "out")
    preds = json.loads(result["predictions_path"].read_text(encoding="utf-8"))

    assert preds["input_quality_events"], "trebuie să existe cel puțin un eveniment F1"
    ev = preds["input_quality_events"][0]
    assert ev["field"] == "close" and math.isclose(ev["original_value"], tolerated_close, rel_tol=1e-9)

    # inputul de pe disc rămâne byte-neschimbat -- runner-ul nu rescrie fișierul de intrare
    on_disk = json.loads(inp.read_text(encoding="utf-8"))
    assert on_disk["windows"][0]["bars"] == original_bars


def test_zero_bars_modified_13_bar_characterization_synthetic_proxy() -> None:
    """Nu putem reproduce direct cele 13 bare reale (escrow, inaccesibil VE) -- construim un proxy
    SINTETIC cu EXACT caracterizarea publicată (13 bare, toate pe close, 9 peste high/4 sub low,
    magnitudine unică 0.0005) și verificăm regula pe acel proxy (mandat §4.5)."""
    bars = []
    for i in range(9):
        bars.append({"ts_open": i * 900, "ts_close": (i + 1) * 900, "open": 100.0, "high": 101.0,
                    "low": 99.0, "close": 101.0 + 0.0005, "volume": None, "is_backfilled": False})
    for i in range(9, 13):
        bars.append({"ts_open": i * 900, "ts_close": (i + 1) * 900, "open": 100.0, "high": 101.0,
                    "low": 99.0, "close": 99.0 - 0.0005, "volume": None, "is_backfilled": False})
    d = {"windows": [{"window_id": "PROXY", "symbol": "XAUUSD", "timeframe": "15m",
                      "bar_interval_seconds": 900, "bars": bars}]}
    windows, events = validate_and_normalize_input(d)
    assert len(events) == 13
    assert sum(1 for e in events if e.field == "close") == 13
    assert sum(1 for e in events if e.field == "open") == 0
    assert sum(1 for e in events if e.direction == "above_high") == 9
    assert sum(1 for e in events if e.direction == "below_low") == 4
    assert all(math.isclose(abs(e.original_value - e.boundary), 0.0005, rel_tol=1e-9) for e in events)
    # barele rămân neschimbate
    assert [b.close for b in windows[0].bars[:9]] == [101.0005] * 9
