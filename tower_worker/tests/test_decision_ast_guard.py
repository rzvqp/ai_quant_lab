"""AST guard -- RT-TOWER-0008 remediation (2026-08-17, CEO section 9): "Adauga gardieni AST pentru: zero
run_n2/run_n3/run_n4 direct in production worker." Statically scans `decision.py`'s own source for any
reference to the three unbound direct APIs (`ve_tower.UNBOUND_DIRECT_API`) -- a call, an attribute access,
an import -- and fails if found. This is enforced structurally (parse the source, walk the AST), not by
grepping for a string, so it cannot be defeated by whitespace/aliasing tricks that a naive text search
would miss."""

from __future__ import annotations

import ast
from pathlib import Path

_DECISION_SOURCE_PATH = Path(__file__).resolve().parents[1] / "src" / "ve_tower_worker" / "decision.py"
_FORBIDDEN_NAMES = frozenset({"run_n2", "run_n3", "run_n4"})


def _referenced_names(tree: ast.AST) -> set[str]:
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr in _FORBIDDEN_NAMES:
            found.add(node.attr)
        elif isinstance(node, ast.Name) and node.id in _FORBIDDEN_NAMES:
            found.add(node.id)
        elif isinstance(node, ast.ImportFrom) and node.module == "ve_tower":
            for alias in node.names:
                if alias.name in _FORBIDDEN_NAMES:
                    found.add(alias.name)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value in _FORBIDDEN_NAMES:
            # Catches an evasion the two checks above can't: getattr(ve_tower, "run_n3")/hasattr/
            # import_module-by-string. Exact-string-equality only (not substring) so this never flags
            # this module's own prose docstrings, which legitimately name run_n2/run_n3/run_n4 to explain
            # why they're forbidden -- those are longer sentences, never a bare "run_n3" string constant.
            found.add(node.value)
    return found


def test_decision_module_never_references_unbound_direct_api() -> None:
    source = _DECISION_SOURCE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(_DECISION_SOURCE_PATH))
    referenced = _referenced_names(tree)
    assert not referenced, (
        f"decision.py references forbidden direct API(s) {sorted(referenced)} -- production worker code "
        f"must call ONLY ve_tower.run_tower_chain (see ve_tower.PRODUCTION_ENTRYPOINT / "
        f"ve_tower.UNBOUND_DIRECT_API)"
    )


def test_decision_module_calls_run_tower_chain() -> None:
    """The positive half of the same guard: not just "doesn't call the forbidden three" but "does call
    the one permitted entrypoint" -- a decision.py that called NEITHER would vacuously pass the test
    above."""
    source = _DECISION_SOURCE_PATH.read_text(encoding="utf-8")
    assert "run_tower_chain" in source
