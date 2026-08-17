"""AST guard for `ai_trader/new_brain_live/` -- CEO authorization 2026-08-17, sections 3-5: this package
may NEVER submit an order, NEVER call `run_n2`/`run_n3`/`run_n4` directly, NEVER call `set_authority`
(it only ever READS `current_authority`), and NEVER construct `BrokerOrderSubmissionGate(enabled=True)`
anywhere outside a test. Mirrors `tower_worker/tests/test_decision_ast_guard.py`'s own exact-string-match
discipline (not a naive substring search, which would false-positive on this package's own explanatory
docstrings)."""

from __future__ import annotations

import ast
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parents[1]
_FORBIDDEN_NAMES = {"run_n2", "run_n3", "run_n4", "order_send", "set_authority"}


def _source_files() -> list[Path]:
    return sorted(p for p in _PACKAGE_ROOT.glob("*.py") if p.name != "__init__.py")


def _referenced_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            names.add(node.module)
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            names.add(node.value)
    return names


def test_no_source_file_references_forbidden_names() -> None:
    violations: dict[str, set[str]] = {}
    for path in _source_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        hits = _referenced_names(tree) & _FORBIDDEN_NAMES
        if hits:
            violations[path.name] = hits
    assert not violations, f"forbidden reference(s) found: {violations}"


def test_broker_order_submission_gate_never_constructed_with_enabled_true() -> None:
    for path in _source_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.keyword) and node.arg == "enabled":
                assert not (isinstance(node.value, ast.Constant) and node.value.value is True), (
                    f"{path.name}: found enabled=True"
                )


def test_no_source_file_imports_order_capable_packages() -> None:
    """Same convention `mandate2_readiness`'s own static import-independence guard already establishes --
    this package's source (not its tests) must never import anything that could submit a real order."""
    forbidden_modules = {
        "ai_trader.execution_orchestrator", "ai_trader.order_manager", "ai_trader.mt5_demo_execution",
        "ai_trader.execution_engine.ledger",
    }
    violations: dict[str, set[str]] = {}
    for path in _source_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module is not None:
                imported.add(node.module)
            elif isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
        hits = {m for m in imported if any(m == f or m.startswith(f + ".") for f in forbidden_modules)}
        if hits:
            violations[path.name] = hits
    assert not violations, f"order-capable import(s) found: {violations}"
