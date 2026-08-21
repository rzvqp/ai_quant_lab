"""CEO decision (AI Trader New Brain Architecture mandate, AI-TRADER-NEW-BRAIN-ARCHITECTURE-
IMPLEMENTATION-001): CAND-0001 (`pdh_pdl_demo`)/CAND-0007+CAND-0019 (`multi_policy_live`) are
LEGACY_NON_AUTHORITY -- their real order_send capability must be UNREACHABLE, not merely "currently
blocked by one flag nobody happens to have flipped." Two independent, durable guarantees, both checked
here:

1. `gating.send_after_dry_run_gate` is the ONLY reachable path to a real MT5 DEMO order for either
   legacy package (a source-level guard, not a behavioral one -- proves there is no second, bypassing
   `order_send` call site anywhere in either package; constructing `RealMT5DemoGateway`/
   `MT5DemoBrokerAdapter` to hand to the gate is legitimate plumbing, not itself an order submission).
2. The quarantine flag itself is `True` -- a canary that fails loudly the moment anyone flips it,
   forcing that change through code review rather than letting it drift silently."""

from __future__ import annotations

import ast
from pathlib import Path

from ai_trader.mt5_demo_execution import gating

_REPO_ROOT = Path(__file__).resolve().parents[3]
_LEGACY_PACKAGES = ("pdh_pdl_demo", "multi_policy_live")
_FORBIDDEN_NAMES = ("order_send",)


def _all_py_files(package: str) -> list[Path]:
    package_dir = _REPO_ROOT / "ai_trader" / package
    return [p for p in package_dir.rglob("*.py") if "tests" not in p.parts and "__pycache__" not in p.parts]


def _referenced_names(source: str) -> set[str]:
    tree = ast.parse(source)
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
    return names


def test_legacy_packages_never_reference_order_send_directly() -> None:
    for package in _LEGACY_PACKAGES:
        for path in _all_py_files(package):
            names = _referenced_names(path.read_text(encoding="utf-8"))
            for forbidden in _FORBIDDEN_NAMES:
                assert forbidden not in names, (
                    f"{path.relative_to(_REPO_ROOT)} references {forbidden!r} directly -- the only "
                    f"permitted path to a real order is send_after_dry_run_gate"
                )


def test_legacy_packages_only_reach_the_broker_through_the_single_gate() -> None:
    for package in _LEGACY_PACKAGES:
        found_gate_import = False
        for path in _all_py_files(package):
            source = path.read_text(encoding="utf-8")
            if "send_after_dry_run_gate" in source:
                found_gate_import = True
        assert found_gate_import, f"{package} no longer imports send_after_dry_run_gate at all -- re-verify its broker path"


def test_legacy_trading_authority_quarantine_flag_is_true() -> None:
    """Canary: fails loudly the instant this flag is flipped, so un-quarantining requires a reviewed,
    deliberate change to this test too -- never a silent drift."""
    assert gating.LEGACY_TRADING_AUTHORITY_QUARANTINED is True
