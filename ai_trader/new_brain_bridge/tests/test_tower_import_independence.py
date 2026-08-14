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


def test_tower_client_and_protocol_import_none_of_the_forbidden_modules() -> None:
    violations: dict[str, set[str]] = {}
    for filename in ("tower_client.py", "tower_protocol.py"):
        source_path = _NEW_BRAIN_BRIDGE_ROOT / filename
        imported = _imported_module_names(source_path)
        hits = {
            name for name in imported
            if any(name == prefix or name.startswith(prefix + ".") for prefix in _FORBIDDEN_IMPORTS_FOR_TOWER_MODULES)
        }
        if hits:
            violations[filename] = hits
    assert not violations, f"forbidden imports found: {violations}"


def test_bridge_py_does_not_yet_call_the_tower_client() -> None:
    """`bridge.py`'s hardcoded market_map_available=False/levels_available=False/confirmation_available=
    False stay exactly as they are until TOWER_HANDOFF_PASS -- this asserts the infrastructure built this
    segment has NOT been wired into the production evaluation path, matching the explicit CEO instruction
    not to do that yet."""
    bridge_source = (_NEW_BRAIN_BRIDGE_ROOT / "bridge.py").read_text(encoding="utf-8")
    assert "tower_client" not in bridge_source
    assert "TowerClient" not in bridge_source


def test_no_live_process_package_imports_the_tower_client_or_protocol() -> None:
    violations: dict[str, set[str]] = {}
    for relative_dir, _package_name in _PACKAGES_THAT_MUST_NOT_IMPORT_TOWER:
        package_dir = _REPO_ROOT / relative_dir
        for source_path in package_dir.glob("*.py"):
            imported = _imported_module_names(source_path)
            hits = {
                name for name in imported
                if "tower_client" in name or "tower_protocol" in name
            }
            if hits:
                violations[str(source_path.relative_to(_REPO_ROOT))] = hits
    assert not violations, f"a live-process package imports the tower client/protocol: {violations}"
