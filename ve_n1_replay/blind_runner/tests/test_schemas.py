"""Teste de validare input -- mandat §11 iteme 2-3 (input valid + fiecare input invalid)."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dev_fixtures import make_dev_input  # noqa: E402
from schemas import InputValidationError, validate_and_normalize_input  # noqa: E402


def _valid_input() -> dict:
    return make_dev_input(n_windows=1, bars_per_window=10)


def test_valid_input_passes() -> None:
    windows = validate_and_normalize_input(_valid_input())
    assert len(windows) == 1
    assert len(windows[0].bars) == 10


@pytest.mark.parametrize("mutate,expected_code", [
    (lambda d: d["windows"][0]["bars"][0].pop("ts_close"), "MISSING_FIELD"),
    (lambda d: d["windows"][0]["bars"][0].pop("open"), "MISSING_FIELD"),
    (lambda d: d["windows"][0]["bars"][0].__setitem__("close", float("nan")), "NON_FINITE_VALUE"),
    (lambda d: d["windows"][0]["bars"][0].__setitem__("high", d["windows"][0]["bars"][0]["low"] - 1), "HIGH_LESS_THAN_LOW"),
    (lambda d: d["windows"][0]["bars"][0].__setitem__("open", d["windows"][0]["bars"][0]["high"] + 100), "OPEN_OUTSIDE_HIGH_LOW"),
    (lambda d: d["windows"][0]["bars"][0].__setitem__("close", d["windows"][0]["bars"][0]["low"] - 100), "CLOSE_OUTSIDE_HIGH_LOW"),
    (lambda d: d["windows"][0].__setitem__("bars", []), "EMPTY_WINDOW"),
    (lambda d: d["windows"][0].__setitem__("bar_interval_seconds", 0), "WRONG_TIMEFRAME"),
    (lambda d: d["windows"][0].__setitem__("bar_interval_seconds", "900"), "WRONG_TIMEFRAME"),
    (lambda d: d["windows"][0].__setitem__("window_id", ""), "MALFORMED_WINDOW_ID"),
])
def test_each_invalid_input_refused_fail_closed(mutate, expected_code) -> None:
    d = copy.deepcopy(_valid_input())
    mutate(d)
    with pytest.raises(InputValidationError) as exc_info:
        validate_and_normalize_input(d)
    assert exc_info.value.code == expected_code


def test_duplicate_bar_refused() -> None:
    d = copy.deepcopy(_valid_input())
    d["windows"][0]["bars"][1] = dict(d["windows"][0]["bars"][0])
    with pytest.raises(InputValidationError) as exc_info:
        validate_and_normalize_input(d)
    assert exc_info.value.code == "DUPLICATE_BAR"


def test_bad_temporal_order_refused() -> None:
    d = copy.deepcopy(_valid_input())
    bars = d["windows"][0]["bars"]
    bars[0], bars[1] = bars[1], bars[0]
    with pytest.raises(InputValidationError) as exc_info:
        validate_and_normalize_input(d)
    assert exc_info.value.code == "BAD_TEMPORAL_ORDER"


def test_duplicate_window_id_refused() -> None:
    d = make_dev_input(n_windows=2, bars_per_window=5)
    d["windows"][1]["window_id"] = d["windows"][0]["window_id"]
    with pytest.raises(InputValidationError) as exc_info:
        validate_and_normalize_input(d)
    assert exc_info.value.code == "DUPLICATE_WINDOW_ID"


def test_corrupt_file_shape_refused() -> None:
    with pytest.raises(InputValidationError) as exc_info:
        validate_and_normalize_input({"not_windows": []})
    assert exc_info.value.code == "CORRUPT_FILE"


def test_partial_data_missing_windows_key_content() -> None:
    with pytest.raises(InputValidationError) as exc_info:
        validate_and_normalize_input({"windows": []})
    assert exc_info.value.code == "PARTIAL_DATA"


def test_partial_data_missing_window_field() -> None:
    d = _valid_input()
    del d["windows"][0]["symbol"]
    with pytest.raises(InputValidationError) as exc_info:
        validate_and_normalize_input(d)
    assert exc_info.value.code == "PARTIAL_DATA"
