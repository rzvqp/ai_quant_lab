"""Static import-boundary verification. The Execution Orchestrator legitimately depends on every
trading-domain package (that is its whole job, unlike every prior phase's own narrow allow-list) --
but it must NEVER import the MT5 terminal API directly, or any MT5-specific submodule
(`adapters.mt5_gateway`/`mt5_adapter`/`mt5_types`), only the venue-agnostic `DryRunBrokerAdapter` (CEO
rule 9: only the MT5 Broker Adapter itself may import `MetaTrader5`)."""

from __future__ import annotations

import ast
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parents[1]

_FORBIDDEN_MT5_SUBMODULE_PREFIXES = (
    "ai_trader.execution_engine.adapters.mt5_gateway",
    "ai_trader.execution_engine.adapters.mt5_adapter",
    "ai_trader.execution_engine.adapters.mt5_types",
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
    assert not violations, f"MT5-specific submodule imports found: {violations}"


def test_no_direct_order_send_or_low_level_broker_call() -> None:
    """The orchestrator must only ever reach the broker through `order_manager.process_approved_intent`
    -- never call `submit_order`/`order_send` itself directly."""
    forbidden = ("order_send", "order_check", ".submit_order(")
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        hits = {tok for tok in forbidden if tok in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"direct low-level broker calls found (must route through order_manager only): {violations}"


def test_live_mode_enum_member_exists_but_is_never_referenced_as_default() -> None:
    """`ExecutionMode.LIVE` must exist (so it can be explicitly requested and then refused), but no
    production default parameter may ever default TO live mode."""
    engine_text = (_PACKAGE_ROOT / "engine.py").read_text(encoding="utf-8")
    assert "mode: ExecutionMode = ExecutionMode.DRY_RUN" in engine_text
    assert "= ExecutionMode.LIVE" not in engine_text
