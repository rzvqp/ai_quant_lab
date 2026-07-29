"""Static import-boundary verification -- same 5-check pattern as every prior live package's own
precedent. The loop orchestrates `live_signal_source`/`risk_manager_live`/`persistent_state`, so its
allow-list is broader than any single one of them, but the execution-capable forbidden list is
unchanged: no order-submission path exists anywhere in this mandate."""

from __future__ import annotations

import ast
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parents[1]

_FORBIDDEN_MODULE_PREFIXES = (
    "ai_trader.execution_engine.broker_adapter",
    "ai_trader.execution_engine.pipeline",
    "ai_trader.order_manager",
    "ai_trader.mt5_demo_execution",
    "ai_trader.execution_orchestrator",
    "ai_trader.simulation",
    "ai_trader.learning_feedback",
    "ai_trader.shadow_evidence",
)

_ALLOWED_AI_TRADER_PREFIXES = (
    "ai_trader.live_loop",
    "ai_trader.live_signal_source",
    "ai_trader.persistent_state",
    "ai_trader.risk_manager_live",
    "ai_trader.risk_manager",
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
        assert "MetaTrader5" not in source_path.read_text(encoding="utf-8")


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
    assert not violations, f"forbidden imports found (execution-capable modules): {violations}"


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
    forbidden = ("order_send", "order_check", "submit_order", "cancel_order", "close_position")
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        hits = {tok for tok in forbidden if tok in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"order-submission vocabulary found: {violations}"


def test_never_references_an_execution_capable_adapter_type() -> None:
    forbidden = ("BrokerAdapter", "DryRunBrokerAdapter", "MT5DemoBrokerAdapter")
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        hits = {tok for tok in forbidden if tok in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"execution-capable adapter type referenced: {violations}"
