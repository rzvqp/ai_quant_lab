"""Hash canonic: determinism, sensibilitate la un singur element, REFUZ NaN/Inf, distincție de tip, normalizare."""

from __future__ import annotations

import math
import os
import sys

import pytest

_PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PKG not in sys.path:
    sys.path.insert(0, _PKG)

from ve_tower import canonical_hash, git_blob_sha1  # noqa: E402
from ve_tower.canonical import NonFiniteValueError  # noqa: E402


def test_same_input_same_hash() -> None:
    a = {"time": [1, 2, 3], "close": [1.0, 2.0, 3.0], "s": "x"}
    b = {"s": "x", "close": [1.0, 2.0, 3.0], "time": [1, 2, 3]}    # altă ordine de chei
    assert canonical_hash(a) == canonical_hash(b)                  # ordinea cheilor NU contează


def test_single_element_change_changes_hash() -> None:
    base = {"h": [1.0, 2.0, 3.0], "t": [10, 20, 30]}
    assert canonical_hash(base) != canonical_hash({"h": [1.0, 2.0, 3.0000001], "t": [10, 20, 30]})   # un OHLC
    assert canonical_hash(base) != canonical_hash({"h": [1.0, 2.0, 3.0], "t": [10, 20, 31]})         # un timestamp


def test_nan_inf_refused() -> None:
    for bad in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(NonFiniteValueError):
            canonical_hash({"v": [1.0, bad]})


def test_types_are_distinct() -> None:
    # 1 (int), 1.0 (float), True (bool) NU trebuie să coincidă
    assert canonical_hash(1) != canonical_hash(1.0) != canonical_hash(True) != canonical_hash(1)
    assert canonical_hash(None) != canonical_hash("null")


def test_float_representation_is_exact_and_platform_independent() -> None:
    # reprezentare IEEE-754 exactă: 0.1+0.2 != 0.3 la nivel de biți
    assert canonical_hash(0.1 + 0.2) != canonical_hash(0.3)
    assert math.isfinite(0.1 + 0.2)


def test_git_blob_sha1_matches_git_semantics() -> None:
    # blob-ul unui șir gol are hash-ul cunoscut al lui git
    assert git_blob_sha1(b"") == "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"
    assert git_blob_sha1(b"hello\n") == "ce013625030ba8dba906f756967f9e9ca394464a"
