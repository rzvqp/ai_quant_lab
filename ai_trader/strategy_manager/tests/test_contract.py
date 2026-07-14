"""Tests for :mod:`ai_trader.strategy_manager.contract`."""

from __future__ import annotations

from ai_trader.strategy_manager.contract import (
    ContractStatus,
    HoldoutStatus,
    Maturity,
    Regime,
    TestStatus as GateStatus,
    maturity_rank,
    parse_contract,
)
from ai_trader.strategy_manager.tests.fixtures.contracts import make_contract_dict


class TestMaturityRank:
    def test_ladder_is_strictly_increasing(self) -> None:
        ranks = [maturity_rank(m) for m in (Maturity.EXPLORATORY, Maturity.CANDIDATE, Maturity.VALIDATED, Maturity.PROMOTED)]
        assert ranks == sorted(ranks)
        assert len(set(ranks)) == 4

    def test_retired_ranks_below_exploratory(self) -> None:
        assert maturity_rank(Maturity.RETIRED) < maturity_rank(Maturity.EXPLORATORY)


class TestParseContract:
    def test_round_trips_basic_fields(self) -> None:
        data = make_contract_dict(id="S7", name="Seven", maturity="CANDIDATE")
        contract = parse_contract(data)
        assert contract.identity.id == "S7"
        assert contract.identity.name == "Seven"
        assert contract.lifecycle.maturity is Maturity.CANDIDATE
        assert contract.lifecycle.status is ContractStatus.IMPLEMENTED
        assert contract.provenance.holdout_status is HoldoutStatus.SEALED

    def test_required_data_parsed(self) -> None:
        data = make_contract_dict(required_data=[
            {"timeframe": "M15", "fields": ["m_atr"], "lookback_bars": 10, "htf": ["H1"]},
            {"timeframe": "H1", "fields": ["h1_trend_up"], "lookback_bars": 5, "htf": None},
        ])
        contract = parse_contract(data)
        assert len(contract.semantics.required_data) == 2
        first = contract.semantics.required_data[0]
        assert first.timeframe == "M15"
        assert first.fields == ("m_atr",)
        assert first.lookback_bars == 10
        assert first.htf == ("H1",)
        assert contract.semantics.required_data[1].htf is None

    def test_dependencies_none_by_default(self) -> None:
        contract = parse_contract(make_contract_dict())
        assert contract.semantics.dependencies is None

    def test_dependencies_tuple_when_present(self) -> None:
        contract = parse_contract(make_contract_dict(dependencies=["S1", "S2"]))
        assert contract.semantics.dependencies == ("S1", "S2")

    def test_target_none_by_default(self) -> None:
        contract = parse_contract(make_contract_dict())
        assert contract.execution.target is None

    def test_target_parsed_when_present(self) -> None:
        contract = parse_contract(make_contract_dict(target={"description": "test target", "trigger": "x"}))
        assert contract.execution.target is not None
        assert contract.execution.target.description == "test target"
        assert contract.execution.target.trigger == "x"

    def test_market_regime_enums(self) -> None:
        contract = parse_contract(make_contract_dict(
            market_regime_applicable=["TREND_UP", "HIGH_VOL"], market_regime_avoid=["RANGE"],
        ))
        assert contract.semantics.market_regime.applicable == (Regime.TREND_UP, Regime.HIGH_VOL)
        assert contract.semantics.market_regime.avoid == (Regime.RANGE,)

    def test_matched_null_and_gate_statuses(self) -> None:
        contract = parse_contract(make_contract_dict(
            walk_forward_status="PASS", matched_null_status="PASS", global_fdr_status="FAIL",
        ))
        assert contract.evidence.walk_forward_status is GateStatus.PASS
        assert contract.evidence.matched_null_status.status is GateStatus.PASS
        assert contract.evidence.global_fdr_status is GateStatus.FAIL

    def test_holdout_opened(self) -> None:
        contract = parse_contract(make_contract_dict(holdout_status="OPENED"))
        assert contract.provenance.holdout_status is HoldoutStatus.OPENED

    def test_priority_optional(self) -> None:
        assert parse_contract(make_contract_dict()).lifecycle.priority is None
        assert parse_contract(make_contract_dict(priority=50)).lifecycle.priority == 50
