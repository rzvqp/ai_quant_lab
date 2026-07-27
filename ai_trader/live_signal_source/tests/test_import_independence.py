"""Static import-boundary verification (CEO instruction, 2026-07-26: "producatorul nu primeste
niciodata adaptorul de executie, impus static") -- same 5-check pattern as `mt5_pnl_source`'s/
`mt5_account_bridge`'s own precedent.

Notably stricter than either precedent on one point: `ai_trader.execution_orchestrator` is forbidden
in its ENTIRETY, including `.types` -- `execution_orchestrator/types.py` itself imports
`ai_trader.execution_engine.broker_adapter.BrokerAdapter` at module level, so even importing its pure
`CandidateSignal` type would transitively reach an execution-capable module. `types.py`'s own docstring
explains this is exactly why `LiveCandidate` is this package's own, independently-owned type instead."""

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
    "ai_trader.live_signal_source",
    "ai_trader.execution_engine.adapters.mt5_gateway",
    "ai_trader.signal_engine.types",
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
            "mt5_gateway.py may do this (CEO rule 9); this package must extend it, never re-import it"
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
    """This package only observes bars and proposes candidates -- it must never itself submit/modify/
    cancel an order."""
    forbidden = ("order_send", "order_check", "submit_order", "cancel_order", "close_position")
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        hits = {tok for tok in forbidden if tok in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"order-submission vocabulary found: {violations}"


def test_never_references_an_execution_capable_adapter_type() -> None:
    """Never `BrokerAdapter`/`DryRunBrokerAdapter`/`MT5DemoBrokerAdapter` -- only the read-only
    `MT5Gateway` Protocol this package reads bars from directly."""
    forbidden = ("BrokerAdapter", "DryRunBrokerAdapter", "MT5DemoBrokerAdapter")
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        hits = {tok for tok in forbidden if tok in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"execution-capable adapter type referenced: {violations}"
