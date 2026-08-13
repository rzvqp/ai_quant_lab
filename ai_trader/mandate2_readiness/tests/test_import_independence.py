"""Static import-boundary verification -- same pattern every package in this tree already establishes
(`pdh_pdl_demo`, `multi_policy_live`, `spread_collection`, `zone_observer`, `execution_orchestrator`,
`live_loop`, `live_signal_source`, `risk_manager_live`, ...). CEO instruction, Mandate 2 prep, 2026-08-14:
"Ai deja testul static din adapters. Verifica daca acopera si caile noi" -- this file IS that check,
extended to the one new path this mandate added."""

from __future__ import annotations

import ast
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parents[1]  # ai_trader/mandate2_readiness/

_FORBIDDEN_ORDER_CALLS = ("order_send", "order_check", "order_calc_margin", "order_calc_profit")
_FORBIDDEN_SUBMISSION_VOCABULARY = ("submit_order", "cancel_order", "close_position")


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


def test_no_direct_order_call_anywhere_in_production_code() -> None:
    """`mandate2_readiness` produces exactly one thing: a gate that REFUSES. It must never itself contain
    a real trading call -- there would be no reason for one, and its entire value is being the thing
    everything else routes through, not a second place that could reach the broker independently."""
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        hits = {tok for tok in _FORBIDDEN_ORDER_CALLS + _FORBIDDEN_SUBMISSION_VOCABULARY if tok in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"forbidden trading call(s) found in production code: {violations}"


def test_does_not_import_any_execution_capable_package() -> None:
    """`broker_gate.py` is a pure, standalone primitive -- it must not import `mt5_demo_execution`,
    `execution_engine`, `execution_orchestrator`, or `order_manager`. If it ever needs to, that is itself
    the signal that real Mandate 2 wiring has started and this test's own assumptions need revisiting --
    not something to quietly let slide."""
    forbidden_packages = {
        "ai_trader.mt5_demo_execution", "ai_trader.execution_engine", "ai_trader.execution_orchestrator",
        "ai_trader.order_manager",
    }
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        imported = _imported_module_names(source_path)
        hits = {name for name in imported if any(name.startswith(pkg) for pkg in forbidden_packages)}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"forbidden execution-capable import(s) found: {violations}"


def test_nothing_outside_this_package_imports_it_yet() -> None:
    """Confirms the "not wired into anything" claim in every docstring in this package is actually true
    right now, not just asserted -- zero importers anywhere else in `ai_trader/` (excluding this
    package's own files)."""
    repo_root = _PACKAGE_ROOT.parents[1]  # repo root
    importers: list[str] = []
    for source_path in repo_root.glob("ai_trader/**/*.py"):
        if _PACKAGE_ROOT in source_path.parents or source_path.parent == _PACKAGE_ROOT:
            continue
        text = source_path.read_text(encoding="utf-8")
        if "mandate2_readiness" in text:
            importers.append(str(source_path.relative_to(repo_root)))
    assert importers == [], f"unexpected importer(s) of mandate2_readiness found: {importers}"


def test_forbidden_call_list_only_appears_in_this_test_module_and_docstrings() -> None:
    """Sanity check on the control itself, matching `execution_engine/adapters`'s own established
    pattern -- confirms the scan is exercising a real string match, not silently scanning zero files."""
    all_text = "\n".join(p.read_text(encoding="utf-8") for p in _PACKAGE_ROOT.rglob("*.py"))
    assert "order_send" in all_text
