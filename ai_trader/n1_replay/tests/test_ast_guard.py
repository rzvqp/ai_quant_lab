"""AST guard for `ai_trader/n1_replay/` -- CEO directive 2026-08-17: this package may NEVER import
`ve_tower` (N1/Router are `ve_brain`-only), NEVER call `order_send`, and NEVER call `set_authority`
(only `ai_trader.new_brain_bridge.authority.set_authority` exists in this codebase, and this package
does not even import `ai_trader.new_brain_bridge` at all -- it depends on exactly one thing from that
package, `RawAxesBuilder`). Mirrors `ai_trader/new_brain_live/tests/test_ast_guard.py`'s own
exact-string-match discipline."""

from __future__ import annotations

import ast
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parents[1]
_FORBIDDEN_NAMES = {"order_send", "set_authority", "ve_tower"}


def _source_files() -> list[Path]:
    return sorted(p for p in _PACKAGE_ROOT.rglob("*.py") if "tests" not in p.parts)


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
            violations[str(path.relative_to(_PACKAGE_ROOT))] = hits
    assert not violations, f"forbidden reference(s) found: {violations}"


def test_no_source_file_imports_ai_trader_live_process_packages() -> None:
    """This package depends on exactly `ai_trader.live_signal_source.types.Bar`,
    `ai_trader.new_brain_bridge.raw_axes_builder.RawAxesBuilder`, and
    `ai_trader.mandate2_readiness.wheel_verification` -- never `new_brain_live` (the live process
    itself), never `execution_orchestrator`/`order_manager`/any broker-capable package, and never
    `risk_manager_live`/`mt5_pnl_source` (account/position state has no place in a pure N1 replay)."""
    forbidden_modules = {
        "ai_trader.new_brain_live", "ai_trader.execution_orchestrator", "ai_trader.order_manager",
        "ai_trader.mt5_demo_execution", "ai_trader.execution_engine.ledger",
        "ai_trader.risk_manager_live", "ai_trader.mt5_pnl_source",
        "ai_trader.mandate2_readiness.broker_gate",
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
            violations[str(path.relative_to(_PACKAGE_ROOT))] = hits
    assert not violations, f"forbidden import(s) found: {violations}"


def test_main_venv_still_has_no_ve_tower_importable() -> None:
    """Regression proof, not merely a static guard: the main venv genuinely cannot import `ve_tower` --
    `n1_replay` has no tower dependency, so this must remain true regardless of what this package does."""
    try:
        import ve_tower  # type: ignore[import-not-found]  # noqa: F401
    except ModuleNotFoundError:
        return
    raise AssertionError("ve_tower is importable in the main venv -- isolation violation")
