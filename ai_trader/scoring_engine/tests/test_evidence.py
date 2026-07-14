"""Tests for :mod:`ai_trader.scoring_engine.evidence`."""

from __future__ import annotations

from ai_trader.scoring_engine.evidence import BoundEvidence, EvidenceCache, bind_evidence
from ai_trader.scoring_engine.tests.fixtures.fake_strategy_manager import FakeStrategyManager
from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_manager.tests.fixtures.contracts import make_contract_dict
from ai_trader.strategy_manager.types import Lifecycle, NotFound as SMNotFound, StrategyView


class TestBoundEvidence:
    def test_found_is_true_only_when_both_present(self) -> None:
        assert BoundEvidence(None, None).found is False
        contract = parse_contract(make_contract_dict())
        assert BoundEvidence(Lifecycle.CANDIDATE, None).found is False
        assert BoundEvidence(None, contract).found is False
        assert BoundEvidence(Lifecycle.CANDIDATE, contract).found is True


class TestBindEvidence:
    def test_none_manager_is_evidence_missing(self) -> None:
        result = bind_evidence("S1", None, {})
        assert result.found is False

    def test_unknown_strategy_is_evidence_missing(self) -> None:
        mgr = FakeStrategyManager()
        result = bind_evidence("S1", mgr, {})
        assert result.found is False

    def test_known_strategy_returns_lifecycle_and_contract(self) -> None:
        mgr = FakeStrategyManager()
        contract = parse_contract(make_contract_dict(id="S1"))
        mgr.register("S1", contract, lifecycle=Lifecycle.VALIDATED)
        result = bind_evidence("S1", mgr, {})
        assert result.lifecycle is Lifecycle.VALIDATED
        assert result.contract is contract

    def test_result_is_cached_and_manager_called_once(self) -> None:
        mgr = FakeStrategyManager()
        contract = parse_contract(make_contract_dict(id="S1"))
        mgr.register("S1", contract)
        cache: EvidenceCache = {}
        first = bind_evidence("S1", mgr, cache)
        second = bind_evidence("S1", mgr, cache)
        assert first is second
        assert mgr.calls.count("find_strategy:S1") == 1
        assert mgr.calls.count("get_contract:S1") == 1

    def test_manager_raising_is_treated_as_evidence_missing_not_propagated(self) -> None:
        def _raise(strategy_id: str) -> "StrategyView | SMNotFound":
            raise RuntimeError("boom")

        mgr = FakeStrategyManager(find_strategy_fn=_raise)
        result = bind_evidence("S1", mgr, {})
        assert result.found is False

    def test_partial_lookup_mismatch_is_evidence_missing(self) -> None:
        """A strategy known to find_strategy() but not get_contract() (or vice versa) must not
        produce a half-populated BoundEvidence -- found requires BOTH."""
        mgr = FakeStrategyManager()
        contract = parse_contract(make_contract_dict(id="S1"))
        mgr.contracts["S1"] = contract  # only get_contract knows it; find_strategy does not
        result = bind_evidence("S1", mgr, {})
        assert result.lifecycle is None
        assert result.contract is contract
        assert result.found is False
