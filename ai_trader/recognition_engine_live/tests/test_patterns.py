from __future__ import annotations

from ai_trader.recognition_engine import ContextDimension
from ai_trader.recognition_engine_live.patterns import AUTHORIZED_PATTERNS, pattern_for_id


def test_catalog_has_one_entry_per_dimension() -> None:
    assert len(AUTHORIZED_PATTERNS) == len(list(ContextDimension))


def test_catalog_pattern_ids_are_unique() -> None:
    ids = [p.pattern_id for p in AUTHORIZED_PATTERNS]
    assert len(ids) == len(set(ids))


def test_pattern_for_id_returns_none_for_unknown_id() -> None:
    assert pattern_for_id("NOT-A-REAL-PATTERN") is None


def test_pattern_for_id_returns_the_matching_entry() -> None:
    pattern = pattern_for_id("REC-SESSION-STRATEGY")
    assert pattern is not None
    assert pattern.dimension is ContextDimension.SESSION
