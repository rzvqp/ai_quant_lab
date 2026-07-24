"""Import-boundary verification for the new `adapters/` package, matching this project's own established
pattern (`decision_intelligence_v2/tests/test_import_independence.py`). Confirms: no forbidden package is
imported; `MetaTrader5` is imported ONLY by `mt5_gateway.py`; the pre-existing `BrokerAdapter` Protocol
and `ExecutionSimulator` are never imported for modification (read-only reference via `isinstance` checks
in tests is fine; production code here never imports `ExecutionSimulator` at all)."""

from __future__ import annotations

import ast
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parents[1]

_FORBIDDEN_MODULE_PREFIXES = (
    "ai_trader.learning_feedback", "ai_trader.shadow_evidence", "ai_trader.decision_intelligence",
    "ai_trader.decision_intelligence_v2", "ai_trader.decision_comparison", "ai_trader.risk_manager",
    "ai_trader.signal_engine", "ai_trader.scoring_engine", "ai_trader.portfolio_architect",
    "ai_trader.strategy_health", "ai_trader.recognition_engine", "ai_trader.context_memory",
    "ai_trader.simulation",
)

_ALLOWED_AI_TRADER_PREFIXES = (
    "ai_trader.execution_engine.adapters",
    "ai_trader.execution_engine.types",
    "ai_trader.execution_engine.exceptions",
    "ai_trader.execution_engine.broker_adapter",
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


def test_only_depends_on_allowed_ai_trader_packages() -> None:
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        imported = _imported_module_names(source_path)
        unexpected = {
            name for name in imported
            if name.startswith("ai_trader.")
            and not any(name == p or name.startswith(p + ".") for p in _ALLOWED_AI_TRADER_PREFIXES)
        }
        if unexpected:
            violations[source_path.name] = unexpected
    assert not violations, f"unexpected ai_trader dependency: {violations}"


def test_metatrader5_imported_only_by_mt5_gateway() -> None:
    violations = []
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        if "MetaTrader5" in text and source_path.name != "mt5_gateway.py":
            violations.append(source_path.name)
    assert not violations, f"MetaTrader5 referenced outside mt5_gateway.py: {violations}"


def test_execution_simulator_never_imported_by_this_package() -> None:
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        assert "execution_simulator" not in text.lower(), (
            f"{source_path.name} references execution_simulator -- ExecutionSimulator must remain "
            "completely untouched and unreferenced by this new package"
        )


def test_no_harness_reference_exists() -> None:
    for source_path in _production_source_files():
        assert "harness" not in source_path.read_text(encoding="utf-8").lower(), (
            f"{source_path.name} references 'harness' -- Execution Integration (a later, separately "
            "authorized step) is where any harness wiring would happen, not here"
        )
