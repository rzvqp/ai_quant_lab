"""Static import-boundary verification -- same pattern `pdh_pdl_demo`'s own package established.
Confirms: no direct `order_send`/`order_check` call exists anywhere in this package (every real send
routes through the EXISTING, already-gated `mt5_demo_execution.gating.send_after_dry_run_gate`); the
frozen `demo_gate_engine`/detector primitives are reached ONLY via `vendor_bridge.py`; `code/mstrat.py`
is never referenced."""

from __future__ import annotations

import ast
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parents[1]

_FORBIDDEN_ORDER_CALLS = ("order_send", "order_check", "order_calc_margin", "order_calc_profit")

_VENDORED_MODULE_NAMES = (
    "market_structure", "market_state", "institutional_levels", "imbalance_mechanics", "order_flow",
    "order_block_void", "interactions", "pdh_pdl_demo_engine",
)


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


def test_no_direct_order_send_or_order_check_call() -> None:
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        hits = {tok for tok in _FORBIDDEN_ORDER_CALLS if tok in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"direct order call found -- must route through send_after_dry_run_gate: {violations}"


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
            f"{source_path.name} references mstrat -- code/mstrat.py must remain completely untouched "
            "and unreferenced by this package"
        )


def test_demo_gate_engine_is_never_reimplemented() -> None:
    forbidden_definitions = ("def simulate_demo_trade", "def min_executable_risk", "class DemoSignal", "class DemoTradeResult")
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        if source_path.name == "vendor_bridge.py":
            continue
        text = source_path.read_text(encoding="utf-8")
        hits = {tok for tok in forbidden_definitions if tok in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"demo_gate_engine's own types/functions redefined outside the vendor bridge: {violations}"


def test_pdh_pdl_demo_orchestration_class_never_imported() -> None:
    """This package must reuse `pdh_pdl_demo`'s TYPES only (verbatim, unmodified) -- it must never
    import CAND-0001's own `PdhPdlOrchestrator` class itself (checked via AST, not a raw text scan, so
    this test survives a docstring that merely DISCUSSES the class by name, as this package's own
    `orchestration.py` module docstring does when explaining why a NEW class was written instead)."""
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
        hits: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                hits.update(alias.name for alias in node.names if alias.name == "PdhPdlOrchestrator")
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"CAND-0001's own orchestrator class imported: {violations}"
