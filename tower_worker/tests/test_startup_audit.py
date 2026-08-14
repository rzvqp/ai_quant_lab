from __future__ import annotations

import sys
from pathlib import Path

from ve_tower_worker.startup_audit import (
    AI_TRADER_REPO_MARKER,
    CONFIRMED_HOST_MODULE_NAMES,
    TowerWorkerStartupFailed,
    cwd_is_outside_repo,
    enforce_startup_audit,
    run_startup_audit,
)


def test_clean_environment_passes() -> None:
    # Synthetic, controlled input -- NOT the real ambient sys.path, which under a test runner (pytest's
    # own rootdir insertion) may legitimately include this very repo's own path. That is a fact about how
    # the test was invoked, not a contamination this worker introduced -- see run_startup_audit's own
    # docstring. The real production call site (cli.main -> enforce_startup_audit(), no arguments) uses
    # the genuine ambient sys.path/sys.modules, exercised separately by the real subprocess launches in
    # test_tower_isolation.py (main repo, section 5).
    result = run_startup_audit(
        sys_path=["C:\\Python312\\Lib", "C:\\ve_tower_venv\\Lib\\site-packages"],
        loaded_modules={"sys", "os", "json"},
    )
    assert result.passed
    assert result.contaminated_sys_path_entries == ()
    assert result.preloaded_host_names == ()


def test_confirmed_host_names_are_exactly_the_nine_named_by_the_ceo() -> None:
    assert CONFIRMED_HOST_MODULE_NAMES == (
        "market_state", "market_structure", "order_flow", "institutional_levels",
        "imbalance_mechanics", "interactions", "pdh_pdl_demo_engine", "session_levels",
        "order_block_void",
    )


def test_repo_path_on_sys_path_is_detected() -> None:
    poisoned = f"C:\\Users\\Someone\\{AI_TRADER_REPO_MARKER}\\vendor\\alpha_automation_detectors\\code"
    sys.path.insert(0, poisoned)
    try:
        result = run_startup_audit()
        assert not result.passed
        assert poisoned in result.contaminated_sys_path_entries
    finally:
        sys.path.remove(poisoned)


def test_preloaded_host_name_is_detected() -> None:
    sys.modules["market_state"] = sys.modules[__name__]  # any real module object works as a stand-in
    try:
        result = run_startup_audit()
        assert not result.passed
        assert "market_state" in result.preloaded_host_names
    finally:
        del sys.modules["market_state"]


def test_enforce_raises_with_both_reasons_when_both_present() -> None:
    poisoned = f"C:\\{AI_TRADER_REPO_MARKER}\\vendor"
    sys.path.insert(0, poisoned)
    sys.modules["order_flow"] = sys.modules[__name__]
    try:
        try:
            enforce_startup_audit()
            raise AssertionError("expected TowerWorkerStartupFailed")
        except TowerWorkerStartupFailed as exc:
            assert "TOWER_WORKER_STARTUP_FAILED" in str(exc)
            assert poisoned in str(exc)
            assert "order_flow" in str(exc)
    finally:
        sys.path.remove(poisoned)
        del sys.modules["order_flow"]


def test_enforce_does_not_raise_on_clean_environment() -> None:
    enforce_startup_audit(
        sys_path=["C:\\Python312\\Lib", "C:\\ve_tower_venv\\Lib\\site-packages"],
        loaded_modules={"sys", "os", "json"},
    )  # must not raise


def test_cwd_is_outside_repo_true_for_unrelated_path(tmp_path: Path) -> None:
    assert cwd_is_outside_repo(tmp_path)


def test_cwd_is_outside_repo_false_for_repo_path() -> None:
    fake_repo_path = Path(f"C:/Users/Someone/{AI_TRADER_REPO_MARKER}/ai_trader")
    assert not cwd_is_outside_repo(fake_repo_path)
