"""Integration test against the REAL Strategy Library (``knowledge/strategies/``).

Documents the known gap (``STRATEGY_INTERFACE_v1.md`` §7) and its ongoing, explicit, CEO-gated
migration (Phase 6.8, ``STRATEGY_RUNTIME_INTEGRATION_GAP.md``): most real ``strategy.json`` files are
still "v0 seed" shape and do NOT validate against ``strategy_contract.v1.schema.json`` — migrating
them is a separate task, not part of Strategy Manager implementation. This test asserts the Manager's
fail-safe design handles that reality correctly: every not-yet-migrated real strategy is discovered
and quarantined as ``INVALID`` with a diagnostic reason, and the Manager stays queryable regardless.
This test's own docstring used to describe itself as a tripwire against "0 strategies load" going
unnoticed; as of the Phase 6.8 reference slice, S1 IS migrated and loads successfully -- the counts
below were updated to match, exactly the "tripwire fires, get updated deliberately" scenario the
original docstring anticipated. As more strategies migrate (Phase 6.8 Wave B), these counts will need
updating again -- expected, not a regression.
"""

from __future__ import annotations

from datetime import UTC, datetime

from ai_trader.strategy_manager.config import DEFAULT_LIBRARY_PATH, ManagerConfig
from ai_trader.strategy_manager.manager import StrategyManager
from ai_trader.strategy_manager.tests.fixtures.fake_scanner import FakeScanner
from ai_trader.strategy_manager.types import Health, ManagerOverallHealth

AS_OF = int(datetime(2026, 7, 14, tzinfo=UTC).timestamp())


class TestRealStrategyLibrary:
    def test_library_directory_exists_and_has_51_folders(self) -> None:
        assert DEFAULT_LIBRARY_PATH.is_dir()
        contract_files = list(DEFAULT_LIBRARY_PATH.glob("*/strategy.json"))
        assert len(contract_files) == 51

    def test_load_library_is_fail_safe_and_ready(self) -> None:
        mgr = StrategyManager(ManagerConfig())  # default library_path -> the real Library
        mgr.configure(FakeScanner())
        report = mgr.load_library(as_of=AS_OF)

        # S1 is migrated (Phase 6.8 reference slice) and passes SCHEMA validation (now in `loaded`).
        # It still appears in `failed` too here -- `loaded`/`failed` are not mutually exclusive by
        # design (manager.py `_build_load_report`): a schema-valid entry that fails the separate
        # COMPATIBILITY check (against the scanner's declared `get_provided_features()`) appears in
        # both. `FakeScanner()` here is a deliberately minimal test double that does not declare
        # `pdl`/`m_atr` as provided M15 features (unlike the real `MarketScanner`, which does -- S1
        # loads AND is fully compatible against the real scanner, proven by the Simulation Harness
        # integration tests) -- so under this fixture S1 is schema-valid but INCOMPATIBLE, not a real
        # problem, just this particular fixture's own limited feature declaration.
        assert report.loaded == ("S1",)
        assert len(report.failed) == 51
        s1_failure = next(f for f in report.failed if f.id == "S1")
        assert "pdl" in " ".join(s1_failure.reasons)
        assert report.duplicates == ()

        # Still not ACTIVE: INCOMPATIBLE (under this fixture) is never ACTIVATABLE.
        assert mgr.active_strategies() == []
        assert mgr.required_context().contributor_ids == ()

        # FAILED, not a crash: every entry is still unusable UNDER THIS FIXTURE (50 INVALID + 1
        # INCOMPATIBLE), but the Manager itself is fully queryable.
        assert mgr.health().overall is ManagerOverallHealth.FAILED
        assert mgr.statistics().total == 51
        assert len(mgr.list_strategies()) == 51

    def test_every_real_entry_reports_a_diagnostic_reason(self) -> None:
        mgr = StrategyManager(ManagerConfig())
        mgr.configure(FakeScanner())
        report = mgr.load_library(as_of=AS_OF)
        for failure in report.failed:
            assert failure.reasons, f"{failure.id} has no diagnostic reason recorded"

    def test_snapshot_is_schema_valid_even_though_every_strategy_is_quarantined(self) -> None:
        mgr = StrategyManager(ManagerConfig())
        mgr.configure(FakeScanner())
        mgr.load_library(as_of=AS_OF)
        errors = mgr.validate_snapshot_against_schema()
        assert errors == [], errors

    def test_ids_derived_from_folder_names_are_schema_conformant(self) -> None:
        mgr = StrategyManager(ManagerConfig())
        mgr.configure(FakeScanner())
        mgr.load_library(as_of=AS_OF)
        views = mgr.list_strategies()
        ids = sorted(int("".join(c for c in v.id if c.isdigit())) for v in views)
        assert ids == list(range(1, 52))

    def test_no_scanner_handshake_still_reaches_ready(self) -> None:
        """Even with a scanner whose handshake fails, load_library() must not raise -- the real
        Library's own schema-validity failure would dominate the quarantine reason anyway, but the
        Manager's fail-safe contract holds regardless of which check fails first."""
        mgr = StrategyManager(ManagerConfig())
        mgr.configure(FakeScanner(raise_on_handshake=True))
        report = mgr.load_library(as_of=AS_OF)
        assert len(report.failed) == 51
        assert mgr.health().overall is ManagerOverallHealth.FAILED
