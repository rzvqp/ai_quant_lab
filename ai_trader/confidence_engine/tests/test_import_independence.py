"""Static import-boundary verification. Confidence Engine must never construct or submit anything --
CEO: "never automatically executable". Forbids every execution/order/risk/portfolio package, and the old
scoring-engine ORCHESTRATION modules (`scoring_engine.engine`/`aggregator`/`pipeline` are never imported
-- only the plain `scoring_engine.types.Quality` enum, a values-only, zero-coupling reuse)."""

from __future__ import annotations

import ast
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parents[1]

_FORBIDDEN_MODULE_PREFIXES = (
    "ai_trader.execution_engine", "ai_trader.order_manager", "ai_trader.risk_manager",
    "ai_trader.risk_manager_live", "ai_trader.portfolio_manager_live", "ai_trader.portfolio_architect",
    "ai_trader.simulation", "ai_trader.telegram_notifier", "ai_trader.decision_intelligence",
    "ai_trader.decision_intelligence_v2", "ai_trader.decision_comparison", "ai_trader.learning_feedback",
    "ai_trader.shadow_evidence", "ai_trader.strategy_health", "ai_trader.strategy_manager",
    "ai_trader.signal_engine",
)

_FORBIDDEN_SCORING_ENGINE_SUBMODULES = (
    "ai_trader.scoring_engine.engine", "ai_trader.scoring_engine.aggregator", "ai_trader.scoring_engine.pipeline",
    "ai_trader.scoring_engine.evidence", "ai_trader.scoring_engine.assembler", "ai_trader.scoring_engine.ranker",
    "ai_trader.scoring_engine.validator", "ai_trader.scoring_engine.conflict",
)

_ALLOWED_AI_TRADER_PREFIXES = (
    "ai_trader.confidence_engine", "ai_trader.context_engine", "ai_trader.recognition_engine_live",
    "ai_trader.recognition_engine", "ai_trader.market_intelligence", "ai_trader.edge_intelligence",
    "ai_trader.context_memory", "ai_trader.market_scanner", "ai_trader.scoring_engine",
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


def test_no_scoring_engine_orchestration_submodules() -> None:
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        imported = _imported_module_names(source_path)
        hits = {
            name for name in imported
            if any(name == prefix or name.startswith(prefix + ".") for prefix in _FORBIDDEN_SCORING_ENGINE_SUBMODULES)
        }
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"scoring_engine orchestration modules imported (only .types is allowed): {violations}"


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


def test_no_order_submission_or_trade_decision_vocabulary() -> None:
    forbidden = ("submit_order", "order_send", "order_check", "cancel_order", "close_position", "should_trade")
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        hits = {tok for tok in forbidden if tok in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"order-submission/trade-decision vocabulary found: {violations}"


def test_no_harness_reference() -> None:
    for source_path in _production_source_files():
        assert "harness" not in source_path.read_text(encoding="utf-8").lower()
