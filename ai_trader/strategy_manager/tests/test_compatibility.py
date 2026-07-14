"""Tests for :mod:`ai_trader.strategy_manager.compatibility`."""

from __future__ import annotations

from dataclasses import dataclass

from ai_trader.strategy_manager.compatibility import check
from ai_trader.strategy_manager.config import SupportedVersions
from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_manager.tests.fixtures.contracts import make_contract_dict


@dataclass(frozen=True)
class _Features:
    feature_dictionary_version: str
    fields_by_timeframe: dict[str, frozenset[str]]


DEFAULT_FEATURES = _Features("1.0.0", {"M15": frozenset({"m_atr", "m_rsi"}), "H1": frozenset({"h1_trend_up"})})
SUPPORTED = SupportedVersions()


class TestCheck:
    def test_fully_compatible(self) -> None:
        contract = parse_contract(make_contract_dict())
        result = check(contract, DEFAULT_FEATURES, SUPPORTED)
        assert result.compatible
        assert result.interface_ok
        assert result.runtime_ok
        assert result.context_ok
        assert result.reasons == []

    def test_interface_major_mismatch(self) -> None:
        contract = parse_contract(make_contract_dict())
        result = check(contract, DEFAULT_FEATURES, SupportedVersions(interface_major=2))
        assert not result.compatible
        assert not result.interface_ok
        assert not result.runtime_ok  # runtime tracks interface MAJOR
        assert any("MAJOR" in r for r in result.reasons)

    def test_no_scanner_handshake_is_incompatible(self) -> None:
        contract = parse_contract(make_contract_dict())
        result = check(contract, None, SUPPORTED)
        assert not result.compatible
        assert not result.context_ok
        assert any("handshake" in r for r in result.reasons)

    def test_missing_timeframe(self) -> None:
        contract = parse_contract(make_contract_dict(required_data=[
            {"timeframe": "D1", "fields": ["d1_trend_up"], "lookback_bars": 5, "htf": None},
        ]))
        result = check(contract, DEFAULT_FEATURES, SUPPORTED)
        assert not result.compatible
        assert not result.context_ok
        assert "missing_timeframe:D1" in result.reasons

    def test_missing_field(self) -> None:
        contract = parse_contract(make_contract_dict(required_data=[
            {"timeframe": "M15", "fields": ["m_atr", "nonexistent_field"], "lookback_bars": 5, "htf": None},
        ]))
        result = check(contract, DEFAULT_FEATURES, SUPPORTED)
        assert not result.compatible
        assert "missing_field:M15.nonexistent_field" in result.reasons

    def test_feature_dictionary_major_mismatch(self) -> None:
        contract = parse_contract(make_contract_dict())
        stale_features = _Features("2.0.0", DEFAULT_FEATURES.fields_by_timeframe)
        result = check(contract, stale_features, SUPPORTED)
        assert not result.compatible
        assert not result.context_ok
        assert any("feature_dictionary_version" in r for r in result.reasons)

    def test_deprecated_field_flagged_but_not_rejected(self) -> None:
        contract = parse_contract(make_contract_dict(target={"description": "deprecated usage"}))
        result = check(contract, DEFAULT_FEATURES, SUPPORTED, deprecated_field_paths=frozenset({"execution.target"}))
        assert result.compatible  # deprecated = accept + warn, not reject
        assert result.deprecated_fields == ["execution.target"]

    def test_non_deprecated_field_absent_from_deprecated_list(self) -> None:
        contract = parse_contract(make_contract_dict())  # target=None
        result = check(contract, DEFAULT_FEATURES, SUPPORTED, deprecated_field_paths=frozenset({"execution.target"}))
        assert result.deprecated_fields == []

    def test_deprecated_path_traversal_through_none_intermediate(self) -> None:
        # execution.target is None -> "execution.target.description" must short-circuit False
        # instead of raising AttributeError when traversing past a None intermediate.
        contract = parse_contract(make_contract_dict())  # target=None
        result = check(
            contract, DEFAULT_FEATURES, SUPPORTED,
            deprecated_field_paths=frozenset({"execution.target.description"}),
        )
        assert result.deprecated_fields == []

    def test_multiple_required_data_entries_all_checked(self) -> None:
        contract = parse_contract(make_contract_dict(required_data=[
            {"timeframe": "M15", "fields": ["m_atr"], "lookback_bars": 5, "htf": None},
            {"timeframe": "H1", "fields": ["h1_trend_up"], "lookback_bars": 5, "htf": None},
        ]))
        result = check(contract, DEFAULT_FEATURES, SUPPORTED)
        assert result.context_ok

    def test_schema_valid_always_true(self) -> None:
        """check() is only ever called on already schema-validated contracts; the result always
        carries schema_valid=True to remain self-describing."""
        contract = parse_contract(make_contract_dict())
        result = check(contract, DEFAULT_FEATURES, SUPPORTED)
        assert result.schema_valid is True
