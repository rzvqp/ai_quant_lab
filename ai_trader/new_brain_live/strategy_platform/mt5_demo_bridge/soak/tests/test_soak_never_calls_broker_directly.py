"""Structural (AST-based) proof, same discipline as `mt5_demo_bridge/tests/test_broker_calls_confined_
to_sanctioned_sites.py`: no module under `soak/` ever calls `order_send`/`order_check`/`order_calc_
profit`/`order_calc_margin` directly. `soak_loop.py` reaches the broker only through `demo_execution_
adapter.execute()` (already proven sanctioned); `trade_lifecycle.py` is read-only observation
(`positions_get`/`history_deals_get`), never a broker mutation of any kind."""

from __future__ import annotations

import ast
from pathlib import Path

_PACKAGE_DIR = Path(__file__).resolve().parent.parent
_FORBIDDEN_CALL_NAMES = frozenset({"order_send", "order_check", "order_calc_margin", "order_calc_profit"})


def _production_source_files() -> list[Path]:
    return [p for p in _PACKAGE_DIR.rglob("*.py") if "tests" not in p.parts and "__pycache__" not in p.parts]


def _called_names(source: str) -> set[str]:
    tree = ast.parse(source)
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name):
            names.add(func.id)
        elif isinstance(func, ast.Attribute):
            names.add(func.attr)
    return names


def test_no_soak_module_calls_a_broker_function_directly() -> None:
    violations: dict[str, set[str]] = {}
    for path in _production_source_files():
        hits = _called_names(path.read_text(encoding="utf-8")) & _FORBIDDEN_CALL_NAMES
        if hits:
            violations[path.name] = hits
    assert not violations, f"direct broker call found under soak/: {violations}"
