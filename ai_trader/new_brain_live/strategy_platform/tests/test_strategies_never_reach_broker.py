"""Structural (AST/source-level) proof, not merely a convention: `mock_strategies.py` and the generic
`Strategy` protocol never reference anything broker-capable -- mirrors the SAME `_FORBIDDEN_ORDER_CALLS`
pattern already established across `pdh_pdl_demo`/`multi_policy_live`/`new_brain_live`/`execution_
engine`, extended here to `strategy_platform`."""

from __future__ import annotations

from pathlib import Path

_PACKAGE_DIR = Path(__file__).resolve().parents[1]
_FORBIDDEN_TOKENS = ("order_send", "order_check", "order_calc_margin", "order_calc_profit", "set_authority")


def _production_source_files() -> list[Path]:
    return [p for p in _PACKAGE_DIR.rglob("*.py") if "tests" not in p.parts and "__pycache__" not in p.parts]


def test_no_strategy_platform_module_references_broker_calls_directly() -> None:
    violations: dict[str, set[str]] = {}
    for path in _production_source_files():
        text = path.read_text(encoding="utf-8")
        hits = {tok for tok in _FORBIDDEN_TOKENS if tok in text}
        if hits:
            violations[path.name] = hits
    assert not violations, (
        f"direct broker call reference found -- strategy_platform must only ever reach the broker "
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
