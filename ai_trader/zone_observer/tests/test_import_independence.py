"""Static import-boundary verification -- same pattern `spread_collection`/`structural_observer`
already established. This package is a pure OBSERVER: no order call, no cost/demo-gate engine
reference, and the vendored detector modules (both the git-submodule-pinned ones and the single
locally-vendored `session_levels.py`) are reached only through `vendor_bridge.py`."""

from __future__ import annotations

import ast
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parents[1]

_FORBIDDEN_ORDER_CALLS = ("order_send", "order_check", "order_calc_margin", "order_calc_profit")

_VENDORED_MODULE_NAMES = (
    "market_structure", "order_flow", "imbalance_mechanics", "institutional_levels",
    "order_block_void", "session_levels",
)

_DEMO_GATE_NAMES = ("pdh_pdl_demo_engine", "simulate_demo_trade", "simulate_demo_trades", "DemoSignal")


def _production_source_files() -> list[Path]:
    return sorted(_PACKAGE_ROOT.glob("*.py"))


def _imported_module_names(source_path: Path) -> set[str]:
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            names.add(node.module)
    return names


def test_no_order_call_anywhere() -> None:
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        hits = {tok for tok in _FORBIDDEN_ORDER_CALLS if tok in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"order call found -- this package must never send an order: {violations}"


def test_demo_gate_engine_never_referenced() -> None:
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        hits = {tok for tok in _DEMO_GATE_NAMES if tok in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"demo_gate_engine referenced -- this package must never touch it: {violations}"


def test_vendored_modules_are_imported_only_by_vendor_bridge() -> None:
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        if source_path.name == "vendor_bridge.py":
            continue
        imported = _imported_module_names(source_path)
        hits = {name for name in imported if name in _VENDORED_MODULE_NAMES}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"vendored module imported outside vendor_bridge.py: {violations}"


def test_mstrat_is_never_referenced() -> None:
    for source_path in _production_source_files():
        assert "mstrat" not in source_path.read_text(encoding="utf-8").lower(), (
            f"{source_path.name} references mstrat -- must remain unreferenced"
        )


def test_no_file_ever_constructs_a_non_null_livecandidate() -> None:
    violations: list[str] = []
    for source_path in _production_source_files():
        if "LiveCandidate(" in source_path.read_text(encoding="utf-8"):
            violations.append(source_path.name)
    assert not violations, f"LiveCandidate constructed -- this package is a pure OBSERVER: {violations}"
