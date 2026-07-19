"""Static import-boundary verification -- Checkpoint 9 §L/§P. Scans every production source file under
``ai_trader/context_memory/`` (excluding this ``tests/`` package itself) and asserts no forbidden package
is ever imported. A static source scan, not a live ``sys.modules`` check, deliberately -- a live check run
inside a shared pytest session can produce false negatives/positives depending on what OTHER test files
already imported earlier in the same session; a source-level scan has no such contamination risk and
matches the same grep-based adversarial-review convention every prior checkpoint's own report used.
"""

from __future__ import annotations

import ast
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parents[1]

_FORBIDDEN_MODULE_PREFIXES = (
    "ai_trader.signal_engine",
    "ai_trader.scoring_engine",
    "ai_trader.risk_manager",
    "ai_trader.execution_engine",
    "ai_trader.shadow_evidence",
    "ai_trader.decision_intelligence",
    "ai_trader.market_intelligence",
    "ai_trader.edge_intelligence",
    "ai_trader.strategy_manager",
    "ai_trader.strategy_runtime",
    "ai_trader.strategy_health",
    "ai_trader.simulation",
    "ai_trader.market_scanner",
)


def _production_source_files() -> list[Path]:
    # Non-recursive glob over the package's own top-level directory -- naturally excludes tests/ (a
    # subdirectory) without needing an explicit exclusion rule.
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


def test_no_forbidden_imports_in_any_production_module() -> None:
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        imported = _imported_module_names(source_path)
        hits = {
            name for name in imported
            if any(name == prefix or name.startswith(prefix + ".") for prefix in _FORBIDDEN_MODULE_PREFIXES)
        }
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"forbidden imports found: {violations}"


def test_package_only_depends_on_standard_library_and_itself() -> None:
    allowed_prefixes = ("ai_trader.context_memory",)
    stdlib_or_self_violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        imported = _imported_module_names(source_path)
        third_party = {
            name for name in imported
            if name.startswith("ai_trader.") and not any(name.startswith(p) for p in allowed_prefixes)
        }
        if third_party:
            stdlib_or_self_violations[source_path.name] = third_party
    assert not stdlib_or_self_violations, f"unexpected ai_trader dependency: {stdlib_or_self_violations}"


def test_no_harness_wiring_reference_exists() -> None:
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        assert "harness" not in text.lower(), f"{source_path.name} references 'harness'"
