"""Tests for :mod:`ai_trader.strategy_manager.loader`."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.loader import discover, draft_registry_entry, load_all, load_one
from ai_trader.strategy_manager.tests.fixtures.contracts import make_contract_dict
from ai_trader.strategy_manager.types import CompatibilityResult, Health, Lifecycle


def _write_contract(tmp_path: Path, folder: str, data: dict | str) -> Path:
    d = tmp_path / folder
    d.mkdir(parents=True, exist_ok=True)
    f = d / "strategy.json"
    if isinstance(data, str):
        f.write_text(data, encoding="utf-8")
    else:
        f.write_text(json.dumps(data), encoding="utf-8")
    return f


class TestDiscover:
    def test_empty_directory(self, tmp_path: Path) -> None:
        assert discover(tmp_path) == ()

    def test_missing_directory(self, tmp_path: Path) -> None:
        assert discover(tmp_path / "does_not_exist") == ()

    def test_finds_files_sorted(self, tmp_path: Path) -> None:
        _write_contract(tmp_path, "S02_b", make_contract_dict(id="S2"))
        _write_contract(tmp_path, "S01_a", make_contract_dict(id="S1"))
        _write_contract(tmp_path, "S10_c", make_contract_dict(id="S10"))
        paths = discover(tmp_path)
        assert [p.parent.name for p in paths] == ["S01_a", "S02_b", "S10_c"]

    def test_ignores_non_strategy_json_files(self, tmp_path: Path) -> None:
        (tmp_path / "S01_a").mkdir()
        (tmp_path / "S01_a" / "README.md").write_text("hi")
        assert discover(tmp_path) == ()


class TestLoadOne:
    def test_valid_contract(self, tmp_path: Path) -> None:
        path = _write_contract(tmp_path, "S01_a", make_contract_dict(id="S1"))
        outcome = load_one(path)
        assert outcome.ok
        assert outcome.health is Health.LOADED
        assert outcome.id == "S1"
        assert outcome.slug == "S01_test_strategy"
        assert outcome.contract is not None
        assert outcome.contract_ref.content_hash is not None
        assert outcome.reasons == ()

    def test_missing_file(self, tmp_path: Path) -> None:
        outcome = load_one(tmp_path / "S01_a" / "strategy.json")
        assert not outcome.ok
        assert outcome.health is Health.CORRUPTED
        assert "could not read" in outcome.reasons[0]

    def test_invalid_json(self, tmp_path: Path) -> None:
        path = _write_contract(tmp_path, "S01_a", "{not valid json")
        outcome = load_one(path)
        assert not outcome.ok
        assert outcome.health is Health.CORRUPTED
        assert "invalid JSON" in outcome.reasons[0]

    def test_non_object_root(self, tmp_path: Path) -> None:
        path = _write_contract(tmp_path, "S01_a", "[1, 2, 3]")
        outcome = load_one(path)
        assert not outcome.ok
        assert outcome.health is Health.CORRUPTED
        assert "must be a JSON object" in outcome.reasons[0]

    def test_invalid_utf8(self, tmp_path: Path) -> None:
        d = tmp_path / "S01_a"
        d.mkdir()
        (d / "strategy.json").write_bytes(b"\xff\xfe\x00\x01not utf8")
        outcome = load_one(d / "strategy.json")
        assert not outcome.ok
        assert outcome.health is Health.CORRUPTED

    def test_schema_invalid_missing_fields(self, tmp_path: Path) -> None:
        path = _write_contract(tmp_path, "S01_a", {"interface_version": "1.0.0"})
        outcome = load_one(path)
        assert not outcome.ok
        assert outcome.health is Health.INVALID
        assert outcome.reasons != ()

    def test_schema_invalid_still_extracts_partial_id(self, tmp_path: Path) -> None:
        data = make_contract_dict(id="S9")
        del data["evidence"]  # make it schema-invalid while keeping identity intact
        path = _write_contract(tmp_path, "S09_a", data)
        outcome = load_one(path)
        assert not outcome.ok
        assert outcome.health is Health.INVALID
        assert outcome.id == "S9"
        assert outcome.contract_ref.identity_version == "1.0.0"
        assert outcome.contract_ref.interface_version == "1.0.0"

    def test_content_hash_deterministic(self, tmp_path: Path) -> None:
        data = make_contract_dict(id="S1")
        path_a = _write_contract(tmp_path, "S01_a", data)
        path_b = _write_contract(tmp_path, "S01_b", data)
        assert load_one(path_a).contract_ref.content_hash == load_one(path_b).contract_ref.content_hash

    def test_content_hash_changes_with_content(self, tmp_path: Path) -> None:
        path_a = _write_contract(tmp_path, "S01_a", make_contract_dict(id="S1", name="A"))
        path_b = _write_contract(tmp_path, "S01_b", make_contract_dict(id="S1", name="B"))
        assert load_one(path_a).contract_ref.content_hash != load_one(path_b).contract_ref.content_hash


class TestLoadAll:
    def test_loads_all_and_is_best_effort(self, tmp_path: Path) -> None:
        _write_contract(tmp_path, "S01_a", make_contract_dict(id="S1"))
        _write_contract(tmp_path, "S02_b", "{bad json")
        _write_contract(tmp_path, "S03_c", make_contract_dict(id="S3"))
        outcomes = load_all(tmp_path)
        assert len(outcomes) == 3
        assert [o.ok for o in outcomes] == [True, False, True]


class TestDraftRegistryEntry:
    def test_valid_outcome(self, tmp_path: Path) -> None:
        path = _write_contract(tmp_path, "S01_a", make_contract_dict(id="S1"))
        outcome = load_one(path)
        compat = CompatibilityResult(True, True, True, True, True)
        entry = draft_registry_entry(outcome, compat, Lifecycle.EXPERIMENTAL)
        assert entry.id == "S1"
        assert entry.loaded is True
        assert entry.last_review == "2026-07-01"
        assert entry.errors == []

    def test_corrupted_outcome_gets_folder_based_fallback_id(self, tmp_path: Path) -> None:
        path = _write_contract(tmp_path, "S05_broken", "{bad")
        outcome = load_one(path)
        compat = CompatibilityResult(False, False, False, False, False)
        entry = draft_registry_entry(outcome, compat, Lifecycle.INVALID)
        assert entry.id == "S05"  # extracted verbatim from the folder name, still satisfies ^S\d+$
        assert entry.loaded is False
        assert entry.errors != []

    def test_pathological_folder_name_falls_back_to_s0(self, tmp_path: Path) -> None:
        path = _write_contract(tmp_path, "not_a_strategy_folder", "{bad")
        outcome = load_one(path)
        compat = CompatibilityResult(False, False, False, False, False)
        entry = draft_registry_entry(outcome, compat, Lifecycle.INVALID)
        assert entry.id == "S0"
