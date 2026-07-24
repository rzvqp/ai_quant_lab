"""Static import-boundary verification. Context Engine must never depend on any order/execution/risk/
portfolio package -- it sits BEFORE Risk Manager in the live pipeline (Market Data -> Context Engine ->
Recognition Engine -> Confidence Engine -> Trade Proposal -> Risk Manager -> ...) and cannot submit an
order even in principle (CEO: "no orders, no final confidence")."""

from __future__ import annotations

import ast
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parents[1]

_FORBIDDEN_MODULE_PREFIXES = (
    "ai_trader.execution_engine", "ai_trader.order_manager", "ai_trader.risk_manager",
    "ai_trader.risk_manager_live", "ai_trader.portfolio_manager_live", "ai_trader.portfolio_architect",
    "ai_trader.simulation", "ai_trader.telegram_notifier", "ai_trader.learning_feedback",
    "ai_trader.shadow_evidence", "ai_trader.decision_intelligence", "ai_trader.decision_intelligence_v2",
    "ai_trader.decision_comparison", "ai_trader.strategy_health",
)

_ALLOWED_AI_TRADER_PREFIXES = (
    "ai_trader.context_engine", "ai_trader.context_memory", "ai_trader.market_intelligence",
    "ai_trader.edge_intelligence", "ai_trader.market_scanner", "ai_trader.strategy_runtime",
    "ai_trader.signal_engine",
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
    assert not violations, f"forbidden downstream-trading-domain imports found: {violations}"


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


def test_no_order_submission_vocabulary() -> None:
    forbidden = ("submit_order", "order_send", "order_check", "cancel_order", "close_position")
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        hits = {tok for tok in forbidden if tok in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"order-submission vocabulary found: {violations}"


def test_no_confidence_field_named_final() -> None:
    """CEO: "no final confidence" -- a static tripwire against ever adding a field/variable literally
    named to suggest a final trading confidence score."""
    forbidden = ("final_confidence", "trading_confidence")
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        hits = {tok for tok in forbidden if tok in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"final-confidence vocabulary found: {violations}"
