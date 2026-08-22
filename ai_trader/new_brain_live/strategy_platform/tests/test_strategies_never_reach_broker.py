"""Structural (AST/source-level) proof, not merely a convention: no `strategy_platform` module ever
CALLS a broker-facing function -- mirrors the SAME `_FORBIDDEN_ORDER_CALLS` pattern already established
across `pdh_pdl_demo`/`multi_policy_live`/`new_brain_live`/`execution_engine`, extended here to
`strategy_platform`.

**AST-based, not substring-based** (deliberately, after a real false-positive: a naive `"order_send" in
text` check matched this package's own `soak/harness.py`'s `order_send_calls_total` FIELD NAME, which
merely records a count and never calls anything). Only an actual function/method CALL whose name exactly
equals a forbidden token counts as a violation -- an identifier that happens to CONTAIN one as a
substring (a field name, a variable, a comment) does not.

**`mt5_demo_bridge/` is deliberately EXCLUDED from this scan** (mandate `AI-TRADER-S5-MT5-DEMO-EXECUTION-
001`): that subpackage is the new, explicitly CEO-authorized, DEMO-account-only broker-integration
surface this mandate exists to build -- the invariant this test enforces for the REST of
`strategy_platform` (only ever reach the broker through the already-gated `risk_execution_adapter.py`,
which stays `BROKER_ORDER_SUBMISSION_DISABLED` forever) is intentionally different for that one
subpackage. `mt5_demo_bridge` has its OWN, separate, equally strict AST guard
(`mt5_demo_bridge/tests/test_broker_calls_confined_to_sanctioned_sites.py`) proving broker calls inside
IT are confined to exactly the two sanctioned wrapper sites, never scattered elsewhere -- the same
discipline this test applies to the rest of the package, just scoped to its own new boundary."""

from __future__ import annotations

import ast
from pathlib import Path

_PACKAGE_DIR = Path(__file__).resolve().parents[1]
_FORBIDDEN_CALL_NAMES = frozenset({"order_send", "order_check", "order_calc_margin", "order_calc_profit", "set_authority"})


def _production_source_files() -> list[Path]:
    return [
        p for p in _PACKAGE_DIR.rglob("*.py")
        if "tests" not in p.parts and "__pycache__" not in p.parts and "mt5_demo_bridge" not in p.parts
    ]


def _called_names(source: str) -> set[str]:
    tree = ast.parse(source)
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name):
            names.add(func.id)
        elif isinstance(func, ast.Attribute):
            names.add(func.attr)
    return names


def test_no_strategy_platform_module_calls_a_broker_function_directly() -> None:
    violations: dict[str, set[str]] = {}
    for path in _production_source_files():
        called = _called_names(path.read_text(encoding="utf-8"))
        hits = called & _FORBIDDEN_CALL_NAMES
        if hits:
            violations[path.name] = hits
    assert not violations, (
        f"direct broker call found -- strategy_platform must only ever reach the broker "
        f"through risk_execution_adapter.py's own use of the existing, gated Execution Adapter: {violations}"
    )


def test_mock_strategies_are_all_marked_mock_test_only_by_convention() -> None:
    """Every mock strategy's own `strategy_id` starts with `MOCK_` -- impossible to confuse with an
    Alpha strategy id, which this codebase's own convention (`g0037_...`, `s1_...`, `CAND-000x`) never
    produces."""
    from ai_trader.new_brain_live.strategy_platform.mock_strategies import (
        MockAlwaysNoTrade,
        MockConflictA,
        MockConflictB,
        MockLongOnFixedFixture,
        MockShortOnFixedFixture,
    )

    for strategy in (MockAlwaysNoTrade(), MockLongOnFixedFixture(), MockShortOnFixedFixture(), MockConflictA(), MockConflictB()):
        assert strategy.strategy_id.startswith("MOCK_")
