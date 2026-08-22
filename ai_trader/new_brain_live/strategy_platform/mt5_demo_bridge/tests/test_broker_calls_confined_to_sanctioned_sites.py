"""Structural (AST-based) proof that `mt5_demo_bridge`'s own broker-facing calls (`order_send`,
`order_check`, `order_calc_profit`, `order_calc_margin`) are confined to exactly the sanctioned wrapper
site (`gateway_ext.py`'s two passthrough methods) plus `risk_sizer.py`'s single, legitimate
`gateway.order_calc_profit(...)` call -- never scattered into `reconciliation.py`, `preflight.py`,
`order_identity.py`, `execution_mode.py`, `mt5_execution_ledger.py`, or `live_runtime_loop.py`, all of
which must reach the broker only indirectly, through `demo_execution_adapter.execute()`'s own use of the
already-sanctioned, already-tested `MT5DemoBrokerAdapter.submit_order()` -- never a raw `order_send`/
`order_check` call of their own. Same AST-not-substring discipline as
`strategy_platform/tests/test_strategies_never_reach_broker.py`'s own precedent (that test excludes this
package entirely and defers to this one instead)."""

from __future__ import annotations

import ast
from pathlib import Path

_PACKAGE_DIR = Path(__file__).resolve().parent.parent
_FORBIDDEN_CALL_NAMES = frozenset({"order_send", "order_check", "order_calc_margin", "order_calc_profit"})

_ALLOWED_FILES_FOR_ORDER_SEND_CHECK = frozenset({"gateway_ext.py"})
_ALLOWED_FILES_FOR_ORDER_CALC_PROFIT = frozenset({"gateway_ext.py", "risk_sizer.py"})


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


def test_order_send_and_order_check_confined_to_gateway_ext() -> None:
    violations: dict[str, set[str]] = {}
    for path in _production_source_files():
        if path.name in _ALLOWED_FILES_FOR_ORDER_SEND_CHECK:
            continue
        hits = _called_names(path.read_text(encoding="utf-8")) & {"order_send", "order_check", "order_calc_margin"}
        if hits:
            violations[path.name] = hits
    assert not violations, f"order_send/order_check/order_calc_margin called outside gateway_ext.py: {violations}"


def test_order_calc_profit_confined_to_gateway_ext_and_risk_sizer() -> None:
    violations: dict[str, set[str]] = {}
    for path in _production_source_files():
        if path.name in _ALLOWED_FILES_FOR_ORDER_CALC_PROFIT:
            continue
        hits = _called_names(path.read_text(encoding="utf-8")) & {"order_calc_profit"}
        if hits:
            violations[path.name] = hits
    assert not violations, f"order_calc_profit called outside gateway_ext.py/risk_sizer.py: {violations}"


def test_demo_execution_adapter_only_reaches_broker_via_the_sanctioned_adapter_submit_order() -> None:
    """`demo_execution_adapter.py` itself must never call a forbidden name directly -- its only path to
    the broker is `adapter.submit_order(order)`, the already-tested `MT5DemoBrokerAdapter` method."""
    path = _PACKAGE_DIR / "demo_execution_adapter.py"
    hits = _called_names(path.read_text(encoding="utf-8")) & _FORBIDDEN_CALL_NAMES
    assert not hits, f"demo_execution_adapter.py must never call a broker function directly, found: {hits}"


def test_reconciliation_and_preflight_never_call_a_forbidden_name() -> None:
    for name in ("reconciliation.py", "preflight.py", "order_identity.py", "execution_mode.py", "mt5_execution_ledger.py", "live_runtime_loop.py"):
        path = _PACKAGE_DIR / name
        hits = _called_names(path.read_text(encoding="utf-8")) & _FORBIDDEN_CALL_NAMES
        assert not hits, f"{name} must never call a broker function directly, found: {hits}"
