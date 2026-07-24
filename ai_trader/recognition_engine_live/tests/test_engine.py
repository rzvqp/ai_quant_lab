from __future__ import annotations

from pathlib import Path

from ai_trader.context_memory.enums import OutcomeKind
from ai_trader.recognition_engine.types import Sufficiency
from ai_trader.recognition_engine_live.engine import recognize
from ai_trader.recognition_engine_live.tests._fixtures import build_repository, make_candidate, make_mi_snapshot


def test_unauthorized_pattern_id_is_rejected(tmp_path: Path) -> None:
    repo = build_repository(tmp_path, [])
    result = recognize(make_candidate(pattern_id="NOT-REAL"), make_mi_snapshot(), repo)
    assert result.pattern_authorized is False
    assert "UNAUTHORIZED_PATTERN" in result.reason_codes
    assert result.statistics is None


def test_no_historical_bucket_match_when_repository_empty(tmp_path: Path) -> None:
    repo = build_repository(tmp_path, [])
    result = recognize(make_candidate(), make_mi_snapshot(session_name="LONDON"), repo)
    assert result.pattern_authorized is True
    assert result.statistics is None
    assert "NO_HISTORICAL_BUCKET_MATCH" in result.reason_codes


def test_matching_bucket_returns_real_statistics(tmp_path: Path) -> None:
    records = [
        {"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": 5.0,
         "snapshot_overrides": {"session_state": "LONDON"}},
        {"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": -3.0,
         "snapshot_overrides": {"session_state": "LONDON"}},
    ]
    repo = build_repository(tmp_path, records)
    result = recognize(make_candidate(strategy_id="S1"), make_mi_snapshot(session_name="LONDON"), repo)
    assert result.statistics is not None
    assert result.statistics.n == 2
    assert result.context_bucket_value == "LONDON"


def test_insufficient_evidence_below_min_25(tmp_path: Path) -> None:
    records = [
        {"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": 1.0,
         "snapshot_overrides": {"session_state": "LONDON"}}
        for _ in range(3)
    ]
    repo = build_repository(tmp_path, records)
    result = recognize(make_candidate(strategy_id="S1"), make_mi_snapshot(session_name="LONDON"), repo)
    assert result.sufficiency is Sufficiency.INSUFFICIENT_EVIDENCE
    assert "INSUFFICIENT_EVIDENCE" in result.reason_codes


def test_different_session_bucket_never_matches(tmp_path: Path) -> None:
    records = [
        {"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": 5.0,
         "snapshot_overrides": {"session_state": "NY"}},
    ]
    repo = build_repository(tmp_path, records)
    result = recognize(make_candidate(strategy_id="S1"), make_mi_snapshot(session_name="LONDON"), repo)
    assert result.statistics is None
    assert "NO_HISTORICAL_BUCKET_MATCH" in result.reason_codes


def test_strategy_isolation_never_blends_across_strategies(tmp_path: Path) -> None:
    records = [
        {"strategy_id": "S2", "outcome_kind": OutcomeKind.STRATEGY, "result": 5.0,
         "snapshot_overrides": {"session_state": "LONDON"}},
    ]
    repo = build_repository(tmp_path, records)
    result = recognize(make_candidate(strategy_id="S1"), make_mi_snapshot(session_name="LONDON"), repo)
    assert result.statistics is None


def test_result_never_carries_a_trade_decision_field() -> None:
    """Static-shape check: the result's own field names never suggest a trade decision."""
    from ai_trader.recognition_engine_live.types import RecognitionResult

    field_names = set(RecognitionResult.__dataclass_fields__)
    assert "approved" not in field_names
    assert "should_trade" not in field_names
    assert "direction" not in field_names


def test_calculation_trace_never_empty(tmp_path: Path) -> None:
    repo = build_repository(tmp_path, [])
    result = recognize(make_candidate(), make_mi_snapshot(), repo)
    assert len(result.calculation_trace) >= 1
