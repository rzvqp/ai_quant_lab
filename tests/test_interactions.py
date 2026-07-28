"""Teste sintetice pentru Modulul 7 (interactions.py) — locator generic de confluență.

Array-uri în memorie, fără CSV. Acoperă masca din indici, dilatarea (toleranță, cauzalitate), confluența
la aceeași bară, apartenența preț↔zonă și intersecția matricială preț↔multiple zone. Zero logică de trade.
"""

import os
import sys

import pytest

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from interactions import (  # noqa: E402
    confluence, dilate, price_in_any_zone, price_in_zone, to_mask,
)


def test_to_mask_ignores_out_of_range():
    assert to_mask([1, 3, 99, -2], 5) == [False, True, False, True, False]


def test_confluence_same_bar_and():
    a = [True, True, False, True]
    b = [False, True, False, True]
    c = [True, True, True, True]
    assert confluence([a, b, c]) == [1, 3]


def test_confluence_empty_masks():
    assert confluence([]) == []


def test_confluence_length_mismatch_raises():
    with pytest.raises(ValueError):
        confluence([[True, False], [True]])


def test_dilate_causal_default():
    # after=0 → doar înapoi (strict cauzal)
    m = [False, False, True, False, False]
    assert dilate(m, before=1) == [False, True, True, False, False]


def test_dilate_symmetric_when_after_set():
    m = [False, False, True, False, False]
    assert dilate(m, before=1, after=1) == [False, True, True, True, False]


def test_dilate_negative_raises():
    with pytest.raises(ValueError):
        dilate([True], before=-1)


def test_windowed_confluence_via_dilate_composition():
    # confluență într-o toleranță = confluence(dilate(...)) — nicio convenție băgată în locator
    a = to_mask([2], 6)          # condiție la bara 2
    b = to_mask([4], 6)          # condiție la bara 4
    # fără toleranță: nicio co-ocurență
    assert confluence([a, b]) == []
    # cu toleranță simetrică de 2 bare, se ating la bara 3 (și în jur)
    res = confluence([dilate(a, 2, 2), dilate(b, 2, 2)])
    assert 3 in res


def test_price_in_zone_inclusive_and_normalized():
    price = [99.0, 100.0, 101.0, 102.0, 103.0]
    assert price_in_zone(price, 100.0, 102.0) == [False, True, True, True, False]
    # ordine inversată → același rezultat
    assert price_in_zone(price, 102.0, 100.0) == [False, True, True, True, False]


def test_price_in_any_zone_matrix_intersection():
    price = [99.0, 100.5, 105.0, 110.5]
    zones = [(100.0, 101.0), (110.0, 111.0)]
    assert price_in_any_zone(price, zones) == [False, True, False, True]
    assert price_in_any_zone(price, []) == [False, False, False, False]
