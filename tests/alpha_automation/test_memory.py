import json

from alpha_automation.memory import ResearchMemory


def _record(task_id, outcome, pass_no=0, qnorm=None, tf="H1"):
    return {
        "task_id": task_id,
        "run_id": "R-TEST",
        "pass": pass_no,
        "perspective": {"perspective_id": "P0000", "lens": "time",
                        "analytical_style": "descriptive_scan", "framing": "neutral_observation"},
        "task": {"question_norm": qnorm or f"q {task_id}", "edge_ref": "E001"},
        "window": {"timeframe": tf, "start": "2024-01-01T00:00:00+00:00",
                   "end": "2024-02-01T00:00:00+00:00"},
        "data_provenance": {"data_source": "csv_fallback"},
        "response": {"finding_type": outcome},
        "outcome": outcome,
        "ts": "2026-07-21T00:00:00+00:00",
    }


def test_records_persist_and_route_by_type(tmp_path):
    m = ResearchMemory(tmp_path / "mem")
    m.record_investigation(_record("INV-000001", "NEGATIVE"))
    m.record_investigation(_record("INV-000002", "TENTATIVE"))
    m.record_investigation(_record("INV-000003", "CANDIDATE_PROPOSED"))

    stats = m.stats()
    assert stats["investigations"] == 3
    assert stats["negatives"] == 1
    assert stats["tentative"] == 1
    assert stats["candidates_proposed"] == 1


def test_negative_is_not_a_candidate(tmp_path):
    m = ResearchMemory(tmp_path / "mem")
    m.record_investigation(_record("INV-000001", "NEGATIVE"))
    # A negative result must never land in the candidates ledger.
    assert m.stats()["candidates_proposed"] == 0
    cand_path = (tmp_path / "mem" / "candidates_proposed.jsonl")
    assert not cand_path.exists() or cand_path.read_text().strip() == ""


def test_asked_and_reviewed_indexes(tmp_path):
    m = ResearchMemory(tmp_path / "mem")
    m.record_investigation(_record("INV-000001", "NEGATIVE", qnorm="the ny session question"))
    assert "the ny session question" in m.asked_question_norms()
    assert len(m.reviewed_windows("H1")) == 1
    assert len(m.reviewed_windows("M15")) == 0


def test_restart_rebuilds_indexes(tmp_path):
    d = tmp_path / "mem"
    m1 = ResearchMemory(d)
    m1.record_investigation(_record("INV-000001", "NEGATIVE", qnorm="q1"))
    m1.record_investigation(_record("INV-000002", "TENTATIVE", qnorm="q2"))

    # New instance over the same dir == restart recovery.
    m2 = ResearchMemory(d)
    assert m2.stats()["investigations"] == 2
    assert m2.asked_question_norms() == {"q1", "q2"}
    assert m2.has_task("INV-000001")
    assert len(m2.recent_stances(10)) == 2


def test_invalid_record_rejected(tmp_path):
    m = ResearchMemory(tmp_path / "mem")
    bad = _record("BADID", "NEGATIVE")  # task_id violates INV-###### pattern
    try:
        m.record_investigation(bad)
        assert False, "expected ValueError"
    except ValueError:
        pass
