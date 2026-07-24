from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_trader.order_manager.journal import (
    ConflictingDuplicateAuditEventError,
    JournalCorruptionError,
    OrderAuditEvent,
    OrderManagerAuditJournal,
    compute_audit_event_id,
)


def _event(**overrides: object) -> OrderAuditEvent:
    kwargs: dict[str, object] = {
        "stage": "ORDER_BUILT", "client_order_id": "CID-1", "correlation_id": "CORR-1", "as_of": 1_700_000_000,
        "detail": {"quantity": 0.2},
    }
    kwargs.update(overrides)
    return OrderAuditEvent(**kwargs)  # type: ignore[arg-type]


def test_append_returns_a_deterministic_content_hash_id(tmp_path: Path) -> None:
    journal = OrderManagerAuditJournal(tmp_path / "journal.jsonl")
    event = _event()
    event_id = journal.append(event)
    assert event_id == compute_audit_event_id(event.canonical_payload())


def test_append_is_idempotent_for_the_identical_event(tmp_path: Path) -> None:
    journal = OrderManagerAuditJournal(tmp_path / "journal.jsonl")
    event = _event()
    first_id = journal.append(event)
    second_id = journal.append(event)
    assert first_id == second_id
    assert len(journal) == 1


def test_append_persists_across_a_fresh_instance(tmp_path: Path) -> None:
    path = tmp_path / "journal.jsonl"
    journal_a = OrderManagerAuditJournal(path)
    event_id = journal_a.append(_event())
    journal_b = OrderManagerAuditJournal(path)
    assert journal_b.get(event_id) is not None
    assert len(journal_b) == 1


def test_two_distinct_events_get_distinct_sequences(tmp_path: Path) -> None:
    journal = OrderManagerAuditJournal(tmp_path / "journal.jsonl")
    journal.append(_event(stage="ORDER_BUILT"))
    journal.append(_event(stage="ORDER_STATE_ACKNOWLEDGED"))
    assert len(journal) == 2


def test_events_for_order_filters_by_client_order_id(tmp_path: Path) -> None:
    journal = OrderManagerAuditJournal(tmp_path / "journal.jsonl")
    journal.append(_event(client_order_id="CID-1", stage="A"))
    journal.append(_event(client_order_id="CID-1", stage="B"))
    journal.append(_event(client_order_id="CID-2", stage="A"))
    assert len(journal.events_for_order("CID-1")) == 2
    assert len(journal.events_for_order("CID-2")) == 1


def test_corrupted_line_raises_on_load(tmp_path: Path) -> None:
    path = tmp_path / "journal.jsonl"
    journal = OrderManagerAuditJournal(path)
    journal.append(_event())
    lines = path.read_text(encoding="utf-8").splitlines()
    envelope = json.loads(lines[0])
    envelope["payload"]["detail"]["quantity"] = 999.0  # tamper without recomputing event_id
    path.write_text(json.dumps(envelope) + "\n", encoding="utf-8")
    with pytest.raises(JournalCorruptionError):
        OrderManagerAuditJournal(path)


def test_fsync_flag_present_file_is_flushed_immediately(tmp_path: Path) -> None:
    path = tmp_path / "journal.jsonl"
    journal = OrderManagerAuditJournal(path)
    journal.append(_event())
    assert path.exists()
    assert len(path.read_text(encoding="utf-8").splitlines()) == 1


def test_conflicting_duplicate_id_with_different_payload_raises(tmp_path: Path) -> None:
    """A defensive guard for an adversarial/corrupted in-memory state (a real hash collision is
    astronomically unlikely with sha256) -- simulated directly via the in-memory index rather than
    relying on an actual collision, matching this project's own precedent for testing defensive-only
    code paths."""
    journal = OrderManagerAuditJournal(tmp_path / "journal.jsonl")
    event = _event()
    event_id = journal.append(event)
    journal._by_id[event_id] = {**event.canonical_payload(), "detail": {"quantity": 999.0}}
    with pytest.raises(ConflictingDuplicateAuditEventError):
        journal.append(event)
