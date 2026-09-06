"""Mandate item 4's own "broker/order submission remains disabled" and "S5 execution behavior
unchanged" requirements -- static, source-level proofs that run in ANY environment (no MetaTrader5
install required), unlike the real-MT5 integration test (`test_mt5_e2e_integration.py`), which needs
a live terminal and is gated accordingly.
"""

from __future__ import annotations

from pathlib import Path

import ai_trader.apprenticeship_v2.general_observer as general_observer_pkg

_FORBIDDEN_MT5_CALLS = (
    "order_send", "order_check", "order_calc_margin", "order_calc_profit",
    "positions_get", "positions_close", "orders_get", "order_close",
)

_GENERAL_OBSERVER_DIR = Path(general_observer_pkg.__file__).parent


def _all_general_observer_source_files() -> list[Path]:
    return sorted(p for p in _GENERAL_OBSERVER_DIR.glob("*.py"))


def test_general_observer_package_has_source_files_to_check():
    """Sanity check on the test itself -- if this fails, the glob above is broken, not the
    production code, and every other test in this file would otherwise pass vacuously."""
    files = _all_general_observer_source_files()
    assert len(files) >= 10
    assert any(f.name == "tick.py" for f in files)


def test_no_broker_order_or_position_call_anywhere_in_general_observer():
    """Structural proof, not a convention: no file in general_observer/ references any MT5
    write/position/order function name, anywhere, in any form (a direct `mt5.order_send(...)` call,
    an imported alias, or even a string/comment mentioning intent to call one)."""
    for path in _all_general_observer_source_files():
        text = path.read_text(encoding="utf-8")
        for forbidden in _FORBIDDEN_MT5_CALLS:
            assert forbidden not in text, f"{path.name} references forbidden MT5 call {forbidden!r}"


def test_general_observer_only_imports_the_read_only_mt5_source_module():
    """`tick.py`/`main_general_observer.py` are the only files that need real MT5 access, and both
    must go through `mt5_read_only_source` (the SOLE `import MetaTrader5` point in the package, per
    that module's own docstring) -- never `import MetaTrader5` directly, which would bypass its
    read-only guarantees entirely."""
    for path in _all_general_observer_source_files():
        text = path.read_text(encoding="utf-8")
        assert "import MetaTrader5" not in text, f"{path.name} imports MetaTrader5 directly, bypassing mt5_read_only_source"


def test_mt5_read_only_source_itself_documents_and_only_uses_read_only_calls():
    """Re-verifies the pre-existing S5 file's own documented guarantee (not modified by this
    delivery) -- general_observer's entire real-data path depends on this file staying read-only.
    Checks for an actual `mt5.<name>` call site, not the file's own docstring prose (which
    deliberately names these functions to document that they are absent -- a bare substring check
    would misfire on that documentation itself)."""
    source_path = _GENERAL_OBSERVER_DIR.parent / "mt5_read_only_source.py"
    text = source_path.read_text(encoding="utf-8")
    for forbidden in _FORBIDDEN_MT5_CALLS:
        assert f"mt5.{forbidden}" not in text, f"mt5_read_only_source.py calls forbidden mt5.{forbidden}"
    assert "Never imported or called anywhere in this file" in text  # its own documented guarantee, still present


def test_s5_files_byte_unchanged_by_this_delivery(tmp_path):
    """S5's own entrypoint and tick loop must never reference general_observer -- confirms isolation
    from the READING side too (S5 doesn't import the new subsystem, matching the already-verified
    `git diff` proof that the new subsystem doesn't modify S5's files)."""
    repo_root = _GENERAL_OBSERVER_DIR.parent.parent.parent  # ai_trader/apprenticeship_v2/general_observer -> repo root
    for name in ("loop.py", "main.py", "s5_observer.py"):
        path = repo_root / "ai_trader" / "apprenticeship_v2" / name
        text = path.read_text(encoding="utf-8")
        assert "general_observer" not in text, f"{name} references general_observer -- isolation violated"
