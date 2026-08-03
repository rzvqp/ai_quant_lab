"""Static import-boundary verification -- same pattern as `live_loop`'s own precedent, extended with one
more allowed prefix (`ai_trader.structural_observer`) and the concrete `execution_engine.adapters` module
this package needs to reach `RealMT5Gateway`. `MT5Gateway`/`RealMT5Gateway` declare zero order-capable
methods by construction (`mt5_gateway.py`'s own module docstring) -- importing the concrete class here is
not an execution-capable coupling."""

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
    "ai_trader.signal_engine",
    "ai_trader.scoring_engine",
    "ai_trader.decision_intelligence",
    "ai_trader.decision_intelligence_v2",
    "ai_trader.portfolio_architect",
    "ai_trader.portfolio_manager_live",
    "ai_trader.strategy_health",
    "ai_trader.recognition_engine",
    "ai_trader.recognition_engine_live",
    "ai_trader.context_memory",
)

_ALLOWED_AI_TRADER_PREFIXES = (
    "ai_trader.live_observation",
    "ai_trader.live_signal_source",
    "ai_trader.live_loop",
    "ai_trader.persistent_state",
    "ai_trader.risk_manager_live",
    "ai_trader.risk_manager",
    "ai_trader.structural_observer",
    "ai_trader.execution_engine.adapters.mt5_gateway",
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


def test_no_order_or_execution_vocabulary() -> None:
    forbidden = (
        "order_send", "order_check", "order_calc_margin", "order_calc_profit",
        "submit_order", "cancel_order", "close_position",
        "BrokerAdapter", "DryRunBrokerAdapter", "MT5DemoBrokerAdapter",
    )
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        hits = {tok for tok in forbidden if tok in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"order/execution vocabulary found: {violations}"


def test_only_null_recognition_rule_family_is_used() -> None:
    """Guards against a future edit silently swapping in a real strategy: the only `RecognitionRule`
    implementation this package may construct is `ObservingNullRecognitionRule` (or, transitively,
    `NullRecognitionRule` it wraps) -- never anything with "strategy" or a bespoke rule name in it."""
    forbidden = ("Strategy(", "RealRecognitionRule", "LiveRecognitionRule")
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        hits = {tok for tok in forbidden if tok in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"non-null recognition rule vocabulary found: {violations}"
