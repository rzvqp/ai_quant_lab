"""Static import-boundary verification for the tower client (CEO mandate section 4/5, 2026-08-14): "zero
fallback la market_intelligence, zero fallback la legacy, zero acces la broker" and "oprirea worker-ului NU
afecteaza cele cinci procese". A static AST scan (not a live `sys.modules` check), mirroring the same
convention already established across the repo (e.g. `context_memory/tests/test_import_independence.py`,
`mandate2_readiness/tests/test_import_independence.py`) -- immune to whatever else a shared pytest session
happens to have already imported."""

from __future__ import annotations

import ast
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_NEW_BRAIN_BRIDGE_ROOT = Path(__file__).resolve().parents[1]

_FORBIDDEN_IMPORTS_FOR_TOWER_MODULES = (
    "ai_trader.market_intelligence",
    "ai_trader.pdh_pdl_demo",
    "ai_trader.multi_policy_live",
    "ai_trader.new_brain_bridge.risk_gate",
    "ai_trader.new_brain_bridge.execution_shadow",
    "ai_trader.mandate2_readiness.broker_gate",
)
"""tower_client.py/tower_protocol.py must import NONE of these -- structurally, not by convention, so a
worker failure can never route into legacy recognition, a decision, or a broker call from THIS module."""

_PACKAGES_THAT_MUST_NOT_IMPORT_TOWER = (
    ("ai_trader/pdh_pdl_demo", "ai_trader.pdh_pdl_demo"),
    ("ai_trader/multi_policy_live", "ai_trader.multi_policy_live"),
    ("ai_trader/market_intelligence", "ai_trader.market_intelligence"),
)
"""None of the 5 live processes' own packages may import the tower client/protocol -- proving "stopping
the worker cannot affect the 5 processes" structurally: there is no code path between them today."""


def _imported_module_names(source_path: Path) -> set[str]:
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            names.add(node.module)
    return names


_TOWER_MODULE_FILENAMES = (
    "tower_client.py", "tower_protocol.py", "tower_launcher.py", "tower_cache.py", "tower_identity_pin.py",
)


def test_tower_client_and_protocol_import_none_of_the_forbidden_modules() -> None:
    violations: dict[str, set[str]] = {}
    for filename in _TOWER_MODULE_FILENAMES:
        source_path = _NEW_BRAIN_BRIDGE_ROOT / filename
        imported = _imported_module_names(source_path)
        hits = {
            name for name in imported
            if any(name == prefix or name.startswith(prefix + ".") for prefix in _FORBIDDEN_IMPORTS_FOR_TOWER_MODULES)
        }
        if hits:
            violations[filename] = hits
    assert not violations, f"forbidden imports found: {violations}"


def test_bridge_py_calls_the_tower_client_only_when_explicitly_supplied() -> None:
    """2026-08-14, CEO Phase 2 step 5 (`STAGED_INSTALL_AUTHORIZED`): `bridge.py` now DOES import
    `tower_client` -- the prior version of this test asserted the OPPOSITE, correct for the period before
    `ve_tower` was genuinely installed and verified. What must still hold, and what this asserts instead:
    the tower call is OPT-IN via `evaluate_bar`'s own `tower: TowerDependencies | None = None` parameter
    -- default `None` byte-for-byte reproduces the pre-Phase-2 `market_map_available=False,
    levels_available=False, confirmation_available=False` behavior (see `test_bridge.py`'s own
    `test_a_real_feed_event_reaches_n6_and_is_no_trade_missing_level_input`, which calls `evaluate_bar`
    with no `tower=` argument and still asserts `MISSING_LEVEL_INPUT`) -- never unconditionally active."""
    bridge_source = (_NEW_BRAIN_BRIDGE_ROOT / "bridge.py").read_text(encoding="utf-8")
    assert "tower_client" in bridge_source
    assert "TowerClient" in bridge_source
    assert "tower: TowerDependencies | None = None" in bridge_source


def test_no_live_process_package_imports_the_tower_client_or_protocol() -> None:
    violations: dict[str, set[str]] = {}
    for relative_dir, _package_name in _PACKAGES_THAT_MUST_NOT_IMPORT_TOWER:
        package_dir = _REPO_ROOT / relative_dir
        for source_path in package_dir.glob("*.py"):
            imported = _imported_module_names(source_path)
            hits = {
                name for name in imported
                if any(marker in name for marker in ("tower_client", "tower_protocol", "tower_launcher", "tower_cache", "tower_identity_pin"))
            }
            if hits:
                violations[str(source_path.relative_to(_REPO_ROOT))] = hits
    assert not violations, f"a live-process package imports the tower client/protocol: {violations}"
