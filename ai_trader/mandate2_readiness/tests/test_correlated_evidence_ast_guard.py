"""AST guard for `demonstrate_candidate_v2_correlated.py` (repo root) -- RT-TOWER-0008 section 7 / RT-
TOWER-0010 section 4's own explicit prohibition list for the single correlated-run evidence script:

    "Fara: obiecte terminale construite manual, candidat aprobat injectat, DecisionResponse construit
    manual, EventIdentity terminal construit manual, N2/N3/N4 response injectat, fingerprint sintetic,
    default LONG, direct run_n2/run_n3/run_n4."

Mirrors `tower_worker/tests/test_decision_ast_guard.py`'s own AST-walk discipline (exact-string `ast.
Constant` matches too, not a naive substring search, so the script's own explanatory docstring naming these
concepts is never mistaken for a violation)."""

from __future__ import annotations

import ast
from pathlib import Path

_SCRIPT_PATH = Path(__file__).resolve().parents[3] / "demonstrate_candidate_v2_correlated.py"

_FORBIDDEN_CONSTRUCTOR_NAMES = {
    "EventIdentity", "DecisionResponse", "DecisionProvenance", "N2Response", "N3Response", "N4Response",
}
_FORBIDDEN_DIRECT_API_NAMES = {"run_n2", "run_n3", "run_n4"}
_FORBIDDEN_AUTHORITY_NAMES = {"set_authority"}


def _tree() -> ast.AST:
    assert _SCRIPT_PATH.is_file(), f"evidence script not found at {_SCRIPT_PATH}"
    return ast.parse(_SCRIPT_PATH.read_text(encoding="utf-8"), filename=str(_SCRIPT_PATH))


def _referenced_names(tree: ast.AST) -> set[str]:
    """Every name this module's AST references as an attribute access, bare name, import, or CALL target
    -- plus exact-string constants, to catch `getattr(x, "run_n3")`-style evasion. Deliberately NOT a
    substring search over the raw source (which would false-positive on this file's own explanatory
    docstring, exactly like `tower_worker/tests/test_decision_ast_guard.py`'s own reasoning)."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            names.add(node.module)
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            names.add(node.value)
    return names


def test_never_constructs_a_terminal_object_by_hand() -> None:
    referenced = _referenced_names(_tree())
    hits = referenced & _FORBIDDEN_CONSTRUCTOR_NAMES
    assert not hits, f"evidence script references forbidden manual-construction names: {hits}"


def test_never_references_the_unbound_direct_tower_api() -> None:
    referenced = _referenced_names(_tree())
    hits = referenced & _FORBIDDEN_DIRECT_API_NAMES
    assert not hits, f"evidence script references run_n2/run_n3/run_n4 directly: {hits}"


def test_never_calls_set_authority() -> None:
    referenced = _referenced_names(_tree())
    hits = referenced & _FORBIDDEN_AUTHORITY_NAMES
    assert not hits, f"evidence script references set_authority: {hits}"


def test_never_references_order_send() -> None:
    """AST-based, not a substring search over the raw source -- this module's own explanatory docstring
    legitimately names `order_send` in prose to explain why it is forbidden."""
    referenced = _referenced_names(_tree())
    assert "order_send" not in referenced


def test_never_defaults_bias_direction_to_long() -> None:
    """No `bias_direction="LONG"`-shaped keyword call anywhere -- `side` must come from the real
    `evaluate_bar` call path (`StrategyContract.allowed_directions[0]`), never a script-level default."""
    tree = _tree()
    for node in ast.walk(tree):
        if isinstance(node, ast.keyword) and node.arg == "bias_direction":
            assert not (isinstance(node.value, ast.Constant) and node.value.value == "LONG"), (
                "found a bias_direction=\"LONG\" keyword argument in the evidence script"
            )


def test_the_only_ve_tower_call_reachable_is_via_bridge_evaluate_bar() -> None:
    """Confirms the script never imports `ve_tower` at all -- every tower interaction is mediated through
    `bridge.evaluate_bar` -> `TowerClient.request_chain` -> the isolated worker's own `run_tower_chain`,
    never a same-process `import ve_tower`."""
    tree = _tree()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert not any(alias.name == "ve_tower" for alias in node.names)
        if isinstance(node, ast.ImportFrom):
            assert node.module != "ve_tower"
