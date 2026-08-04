"""Static import-boundary verification -- same pattern `pdh_pdl_demo`/`multi_policy_live` already
established. This package is even more restricted than those: it must NEVER reference an order call or
the demo_gate_engine at all (CEO: "Fara ordine, fara cost")."""

from __future__ import annotations

import ast
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parents[1]

_FORBIDDEN_ORDER_CALLS = ("order_send", "order_check", "order_calc_margin", "order_calc_profit")

_VENDORED_MODULE_NAMES = ("market_structure", "market_state", "institutional_levels")

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
    """Stronger than `pdh_pdl_demo`'s own equivalent test: this package doesn't even bridge
    `demo_gate_engine` (see `vendor_bridge.py`'s own docstring) -- "fara cost" means no cost engine
    call of any kind, not even the post-hoc audit call CAND-0001/CAND-0007/CAND-0019 make."""
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
