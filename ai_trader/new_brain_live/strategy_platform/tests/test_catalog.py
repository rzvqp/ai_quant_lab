"""`StrategyCatalog`/`CatalogEntry` -- validation, duplicate rejection, empty-catalog identity."""

from __future__ import annotations

import pytest

from ai_trader.new_brain_live.strategy_platform.catalog import EMPTY_CATALOG, CatalogEntry, StrategyCatalog, StrategyStatus
from ai_trader.new_brain_live.strategy_platform.mock_strategies import MockLongOnFixedFixture
from ai_trader.new_brain_live.strategy_platform.tests._fixtures import catalog_entry_for


def test_empty_catalog_has_zero_enabled_entries() -> None:
    assert EMPTY_CATALOG.enabled_entries() == ()
    assert EMPTY_CATALOG.lookup("anything", "v1") is None


def test_duplicate_strategy_id_version_pair_rejected() -> None:
    entry = catalog_entry_for(MockLongOnFixedFixture())
    with pytest.raises(ValueError, match="duplicate"):
        StrategyCatalog(entries=(entry, entry))


def test_validated_status_requires_validation_provenance() -> None:
    with pytest.raises(ValueError, match="VALIDATED"):
        CatalogEntry(
            strategy_id="X", strategy_version="v1", status=StrategyStatus.VALIDATED, enabled=True,
            allowed_instruments=("XAUUSD",), allowed_directions=("LONG",), context_eligibility=None,
            implementation_fingerprint="fp", config_fingerprint="fp", validation_provenance=None,
            risk_contract_reference="risk-v1", rollback_identity="rb-v1", strategy=MockLongOnFixedFixture(),
        )


def test_disabled_entry_excluded_from_enabled_entries() -> None:
    entry = catalog_entry_for(MockLongOnFixedFixture(), enabled=False)
    catalog = StrategyCatalog(entries=(entry,))
    assert catalog.enabled_entries() == ()
    assert catalog.lookup(entry.strategy_id, entry.strategy_version) is entry


def test_only_validated_status_is_production_eligible() -> None:
    from ai_trader.new_brain_live.strategy_platform.catalog import PRODUCTION_ELIGIBLE_STATUSES

    assert PRODUCTION_ELIGIBLE_STATUSES == frozenset({StrategyStatus.VALIDATED})
    for status in StrategyStatus:
        if status is not StrategyStatus.VALIDATED:
            assert status not in PRODUCTION_ELIGIBLE_STATUSES
