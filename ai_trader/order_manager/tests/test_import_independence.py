"""Static import-boundary verification. Order Manager is allowed to reuse `execution_engine`'s
build/validate/submit/track/reconcile machinery (unlike `risk_manager_live`, which forbids it) -- but it
must NEVER import the MT5-specific submodules (`adapters.mt5_gateway`/`mt5_adapter`/`mt5_types`), only
`adapters.base`/`adapters.connection` (Phase 1's venue-agnostic foundation). CEO rule 9: only the MT5
Broker Adapter itself may import `MetaTrader5`."""

from __future__ import annotations

import ast
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parents[1]

_FORBIDDEN_MODULE_PREFIXES = (
    "ai_trader.simulation", "ai_trader.learning_feedback", "ai_trader.shadow_evidence",
    "ai_trader.decision_intelligence", "ai_trader.decision_intelligence_v2", "ai_trader.decision_comparison",
    "ai_trader.recognition_engine", "ai_trader.context_memory", "ai_trader.portfolio_architect",
    "ai_trader.strategy_health", "ai_trader.market_scanner",
)

_FORBIDDEN_MT5_SUBMODULE_PREFIXES = (
    "ai_trader.execution_engine.adapters.mt5_gateway",
    "ai_trader.execution_engine.adapters.mt5_adapter",
    "ai_trader.execution_engine.adapters.mt5_types",
)

_ALLOWED_AI_TRADER_PREFIXES = (
    "ai_trader.order_manager", "ai_trader.risk_manager_live", "ai_trader.risk_manager",
    "ai_trader.execution_engine", "ai_trader.signal_engine",
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


def test_no_metatrader5_import_anywhere() -> None:
    for source_path in _production_source_files():
        assert "MetaTrader5" not in source_path.read_text(encoding="utf-8"), (
            f"{source_path.name} references MetaTrader5 -- only ai_trader/execution_engine/adapters/"
            "mt5_gateway.py may do this (CEO rule 9)"
        )


def test_no_mt5_specific_submodule_import() -> None:
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        imported = _imported_module_names(source_path)
        hits = {
            name for name in imported
            if any(name == prefix or name.startswith(prefix + ".") for prefix in _FORBIDDEN_MT5_SUBMODULE_PREFIXES)
        }
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"MT5-specific submodule imports found (Phase 3 is dry-run only): {violations}"


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


def test_no_harness_reference() -> None:
    for source_path in _production_source_files():
        assert "harness" not in source_path.read_text(encoding="utf-8").lower()
