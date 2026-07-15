"""Integration test against the REAL Strategy Library (``knowledge/strategies/``).

Documents the known gap (``STRATEGY_INTERFACE_v1.md`` §7) and its ongoing, explicit, CEO-gated
migration (Phase 6.8, ``STRATEGY_RUNTIME_INTEGRATION_GAP.md``): most real ``strategy.json`` files are
still "v0 seed" shape and do NOT validate against ``strategy_contract.v1.schema.json`` — migrating
them is a separate task, not part of Strategy Manager implementation. This test asserts the Manager's
fail-safe design handles that reality correctly: every not-yet-migrated real strategy is discovered
and quarantined as ``INVALID`` with a diagnostic reason, and the Manager stays queryable regardless.
This test's own docstring used to describe itself as a tripwire against "0 strategies load" going
unnoticed; each Wave B checkpoint updates these counts again as more strategies migrate -- expected,
not a regression, verified live against the real library rather than assumed each time. As of Wave
B's completion (Checkpoints 1-9, all 43 runtime-eligible strategies migrated), all 43 schema-validate
and load; of those, some are ALSO fully COMPATIBLE under this fixture's minimal ``FakeScanner``
feature declaration (whose own ``required_data`` needs only the handful of features this fixture
declares, e.g. ``m_atr``), while the rest remain INCOMPATIBLE under this fixture for the same reason
S1 originally was (missing declared fields like ``pdl``/``prev_sess_high``/``rmax20``) -- the real
``MarketScanner`` declares every feature, full compatibility proven by the Simulation Harness
integration tests. This is the FINAL count -- no further strategy is expected to move from `failed`
(still-v0 INVALID) to `loaded` (schema-valid) under the current Strategy Library, since every
runtime-eligible strategy is now migrated.
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

        # ALL 43 runtime-eligible strategies are migrated (Wave B COMPLETE, Checkpoints 1-9) and pass
        # SCHEMA validation (now in `loaded`). `loaded`/`failed` are not mutually exclusive by design
        # (manager.py `_build_load_report`): a schema-valid entry that fails the separate
        # COMPATIBILITY check (against the scanner's declared `get_provided_features()`) appears in
        # both. `FakeScanner()` here is a deliberately minimal test double declaring only a handful of
        # M15 features (including `m_atr`, but NOT `pdl`/`prev_sess_high`/`rmax20`/etc.) -- so some of
        # the 43 are fully COMPATIBLE even under this fixture, while the rest are schema-valid but
        # INCOMPATIBLE, not a real problem, just this particular fixture's own limited feature
        # declaration (the real `MarketScanner` declares every feature -- full compatibility proven
        # by the Simulation Harness integration tests).
        assert set(report.loaded) == {
            "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10", "S11", "S12", "S13", "S14",
            "S15", "S16", "S17", "S18", "S19", "S20", "S21", "S22", "S23", "S24", "S25", "S26", "S27",
            "S28", "S29", "S30", "S31", "S38", "S39", "S40", "S41", "S42", "S43", "S44", "S45", "S46",
            "S48", "S50", "S51",
        }
        assert len(report.failed) == 36  # 8 still-v0 INVALID (S32-S37, S47, S49) + schema-valid-but-INCOMPATIBLE
        s1_failure = next(f for f in report.failed if f.id == "S1")
        assert "pdl" in " ".join(s1_failure.reasons)
        assert report.duplicates == ()

        # Still not ACTIVE: compatibility alone is not ACTIVATABLE -- this Manager's own default
        # config auto-admits nothing (ManagerConfig()'s conservative default, by design).
        assert mgr.active_strategies() == []
        assert mgr.required_context().contributor_ids == ()

        # DEGRADED (not FAILED): several strategies are healthy-but-inactive under this fixture, so
        # the Manager is no longer "every entry unusable" -- but it stays fully queryable regardless.
        assert mgr.health().overall is ManagerOverallHealth.DEGRADED
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
