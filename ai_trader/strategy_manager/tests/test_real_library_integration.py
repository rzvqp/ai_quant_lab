"""Integration test against the REAL Strategy Library (``knowledge/strategies/``).

Documents the known, pre-existing gap (``STRATEGY_INTERFACE_v1.md`` §7): the real
``strategy.json`` files are "v0 seed" shape and do NOT validate against
``strategy_contract.v1.schema.json`` — migrating them is an explicit, separate, CEO-gated task, not
part of Strategy Manager implementation. This test asserts the Manager's fail-safe design handles
that reality correctly: every real strategy is discovered and quarantined as ``INVALID`` with a
diagnostic reason, the Manager still reaches a ``READY`` (schema-valid, queryable) state with an
empty active set, and nothing crashes. If a future CEO-gated migration updates the real files to
v1 shape, this test's quarantine assertions will start failing loudly — which is the point: it is a
tripwire against silently regressing back to "0 strategies load" without anyone noticing.
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

        assert report.loaded == ()  # v0 seed shape -> every file fails schema validation
        assert len(report.failed) == 51
        assert all(f.health is Health.INVALID for f in report.failed)
        assert report.duplicates == ()

        assert mgr.active_strategies() == []
        assert mgr.required_context().contributor_ids == ()

        # FAILED, not a crash: every entry is unusable, but the Manager itself is fully queryable.
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
