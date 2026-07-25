"""Static safety-boundary verification for MT5 Demo Execution (Phase 10). This package legitimately
extends the MT5 adapter (that is its whole purpose), so the checks here are narrower and more targeted
than every prior phase's "depend on nothing" style test: no literal `MetaTrader5` import of its own (it
reuses the parent's already-set `self._mt5` reference instead), no `cancel_order` implementation, no
algo-trading-activation capability, no LIVE-account bypass."""

from __future__ import annotations

import ast
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parents[1]


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


def test_no_literal_metatrader5_import_in_this_package() -> None:
    """This package never opens a second entry point into the library -- it only calls the ALREADY-SET
    `self._mt5` attribute the parent's own, unmodified `__init__` establishes."""
    for source_path in _production_source_files():
        assert "import MetaTrader5" not in source_path.read_text(encoding="utf-8"), (
            f"{source_path.name} imports MetaTrader5 directly -- only "
            "ai_trader/execution_engine/adapters/mt5_gateway.py may do this (CEO rule 9); this package "
            "must only ever call the inherited self._mt5 reference"
        )


def test_no_forbidden_imports() -> None:
    forbidden_prefixes = (
        "ai_trader.order_manager.dry_run_adapter",  # a real adapter must never be confused with the dry-run one
    )
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        imported = _imported_module_names(source_path)
        hits = {
            name for name in imported
            if any(name == prefix or name.startswith(prefix + ".") for prefix in forbidden_prefixes)
        }
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"forbidden imports found: {violations}"


def test_no_cancel_order_implementation() -> None:
    adapter_text = (_PACKAGE_ROOT / "adapter.py").read_text(encoding="utf-8")
    assert "def cancel_order" not in adapter_text


def test_no_algo_trading_activation_capability() -> None:
    """No file in this package ever WRITES a terminal/account setting -- grep for common
    activation-sounding tokens that would indicate an attempt to flip AlgoTrading on programmatically
    (no such MT5 API call exists in the gateway Protocol at all, so this is a static tripwire, not a
    functional gap)."""
    forbidden = ("enable_algo_trading", "set_trade_allowed", "activate_trading")
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        hits = {tok for tok in forbidden if tok in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"algo-trading-activation vocabulary found: {violations}"


def test_do_connect_is_never_overridden() -> None:
    """`MT5DemoBrokerAdapter` must never override `_do_connect` -- every existing DEMO/server safety
    refusal from the already-approved parent class applies unchanged."""
    adapter_text = (_PACKAGE_ROOT / "adapter.py").read_text(encoding="utf-8")
    assert "_do_connect" not in adapter_text
