"""Static import-boundary verification -- Phase 7 Checkpoint 14. Confirms Decision Intelligence v2
never imports Signal Engine, Scoring Engine, Risk Manager, Execution Engine, or Shadow Evidence (the
same independence requirement v1 already satisfies, CEO Checkpoint 14's own rule), and never writes to
Context Memory's own repository (consumes it strictly as a read-only evidence source)."""

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
)

#: Everything this package IS allowed to depend on -- v2 legitimately builds on v1's own decision
#: logic, Context Memory's public API, and the same intelligence-layer inputs v1 already consumes.
_ALLOWED_AI_TRADER_PREFIXES = (
    "ai_trader.decision_intelligence_v2",
    "ai_trader.decision_intelligence",
    "ai_trader.context_memory",
    "ai_trader.market_intelligence",
    "ai_trader.edge_intelligence",
    "ai_trader.strategy_runtime",
    "ai_trader.strategy_manager",
)

#: Context Memory's own write API -- if any of these appear as a plain identifier anywhere in this
#: package's source, something is writing to the repository, which this integration must never do.
_REPOSITORY_WRITE_METHODS = ("append_context_snapshot", "append_observation", "append_outcome", "append_context_snapshots", "append_observations", "append_outcomes")


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
            if name.startswith("ai_trader.") and not any(name == p or name.startswith(p + ".") for p in _ALLOWED_AI_TRADER_PREFIXES)
        }
        if unexpected:
            violations[source_path.name] = unexpected
    assert not violations, f"unexpected ai_trader dependency: {violations}"


def test_no_harness_wiring_reference_exists() -> None:
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        assert "harness" not in text.lower(), f"{source_path.name} references 'harness'"


def test_never_writes_to_context_memory_repository() -> None:
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        hits = {method for method in _REPOSITORY_WRITE_METHODS if method in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"context_memory repository write call found: {violations}"


def test_no_buy_sell_order_or_execution_vocabulary_in_source() -> None:
    # A cheap, disclosed proxy for "this layer never generates a trade action" -- these tokens have no
    # legitimate reason to appear in a package whose only output is a recommendation string/report.
    forbidden_tokens = ("submit_order", "place_order", "send_order", "\"BUY\"", "\"SELL\"", "'BUY'", "'SELL'")
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        hits = {tok for tok in forbidden_tokens if tok in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"execution/order vocabulary found: {violations}"
