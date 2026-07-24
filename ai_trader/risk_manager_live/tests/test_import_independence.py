"""Static import-boundary verification (CEO rule 9: only MT5 Broker Adapter may import `MetaTrader5`;
CEO rule 8: no module may bypass Risk Manager or Portfolio Manager -- this package cannot itself bypass
anything since IT IS the risk-authorization layer, but it must never depend on modules downstream of it
either)."""

from __future__ import annotations

import ast
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parents[1]

_FORBIDDEN_MODULE_PREFIXES = (
    "ai_trader.execution_engine", "ai_trader.simulation", "ai_trader.learning_feedback",
    "ai_trader.shadow_evidence", "ai_trader.decision_intelligence", "ai_trader.decision_intelligence_v2",
    "ai_trader.decision_comparison", "ai_trader.recognition_engine", "ai_trader.context_memory",
    "ai_trader.portfolio_architect", "ai_trader.strategy_health",
)

_ALLOWED_AI_TRADER_PREFIXES = (
    "ai_trader.risk_manager_live", "ai_trader.risk_manager", "ai_trader.scoring_engine",
    "ai_trader.signal_engine", "ai_trader.market_scanner",
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


def test_no_order_submission_vocabulary() -> None:
    """This is a RISK AUTHORIZATION layer -- it must never itself submit/modify/cancel an order (that
    is Order Manager's job, Phase 3, and Broker Adapter's job, Phase 1/10)."""
    forbidden = ("submit_order", "order_send", "order_check", "cancel_order", "close_position")
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        hits = {tok for tok in forbidden if tok in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"order-submission vocabulary found: {violations}"
