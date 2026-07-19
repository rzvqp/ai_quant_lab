"""Unit tests for :mod:`ai_trader.edge_intelligence.contracts`."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.edge_intelligence.contracts import load_strategy_contracts
from ai_trader.strategy_manager.tests.fixtures.contracts import make_contract_dict


def _write_strategy(tmp_path: Path, folder: str, data: dict) -> None:
    strategy_dir = tmp_path / folder
    strategy_dir.mkdir()
    (strategy_dir / "strategy.json").write_text(json.dumps(data), encoding="utf-8")


def test_loads_only_valid_contracts_keyed_by_id(tmp_path: Path) -> None:
    _write_strategy(tmp_path, "S1_test", make_contract_dict(id="S1"))
    _write_strategy(tmp_path, "SX_broken", {"not": "a valid contract"})

    contracts = load_strategy_contracts(tmp_path)

    assert set(contracts) == {"S1"}
    assert contracts["S1"].identity.id == "S1"


def test_empty_library_returns_empty_dict(tmp_path: Path) -> None:
    assert load_strategy_contracts(tmp_path) == {}


def test_is_deterministic(tmp_path: Path) -> None:
    _write_strategy(tmp_path, "S1_test", make_contract_dict(id="S1"))
    first = load_strategy_contracts(tmp_path)
    second = load_strategy_contracts(tmp_path)
    assert set(first) == set(second) == {"S1"}
