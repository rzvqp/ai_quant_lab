"""Startup self-audit for the isolated tower worker (CEO mandate, 2026-08-14: "TOWER WORKER IZOLAT...
audit sys.path la pornire... cele noua nume host NU trebuie sa fie preincarcate").

The AI Trader repository's own `vendor_bridge.py` files (structural_observer, pdh_pdl_demo,
multi_policy_live, spread_collection, zone_observer) each insert a vendored, flat-script code directory
at `sys.path[0]` and import bare top-level module names from it -- confirmed by direct process inspection
(`AI_TRADER_VE_TOWER_RUNTIME_INVENTORY.md`) to already be live, at position 0, in 4-5 of the 5 running
processes today. If `ve_tower`'s own bootstrap imports a bare module sharing one of those names, which
implementation wins depends on import order and sys.path position -- a silent, undetectable substitution.

This module is the worker's OWN defense: run first, before any other import in this package (including
`protocol`/`server`), and refuse to start rather than risk running with the wrong module shadowing
another. Two independent checks, both must pass:

1. **No AI Trader repository path anywhere in `sys.path`.** The launch procedure (isolated venv, `-I`,
   cleared `PYTHONPATH`, a CWD outside the repo, an installed console-script entrypoint rather than a
   repo-imported script) should make this structurally impossible already -- this is defense in depth,
   not the sole defense, catching a misconfigured launch rather than replacing a correct one.
2. **None of the nine confirmed host module names already sit in `sys.modules`.** Since this worker
   always runs as its own OS process (never a thread, never `exec()`d in-process), `sys.modules` here is
   never shared with the AI Trader process by construction -- checking for these nine names guards
   against a DIFFERENT contamination path: this worker's own future code (or `ve_tower` itself, once
   installed) accidentally importing something on `sys.path` that happens to resolve to one of these
   names from an unexpected source, e.g. a stray file in the worker's own CWD.
"""

from __future__ import annotations

import sys
from collections.abc import Container
from dataclasses import dataclass
from pathlib import Path

CONFIRMED_HOST_MODULE_NAMES: tuple[str, ...] = (
    "market_state",
    "market_structure",
    "order_flow",
    "institutional_levels",
    "imbalance_mechanics",
    "interactions",
    "pdh_pdl_demo_engine",
    "session_levels",
    "order_block_void",
)
"""The nine bare names independently confirmed, by direct process inspection, to already be loaded at
sys.path position 0 in the AI Trader repo's own live processes -- see
`AI_TRADER_VE_TOWER_RUNTIME_INVENTORY.md` section 8. NOT claimed exhaustive against VE's own internal
13-name list (never supplied) -- this is the confirmed subset, not the complete one."""

AI_TRADER_REPO_MARKER = "ai_quant_lab-research-main"
"""Substring match against the AI Trader repository's own directory name. A substring check (not an exact
path equality) deliberately errs toward over-refusing rather than under-refusing: a false positive costs a
`TOWER_WORKER_STARTUP_FAILED` the CEO can investigate; a false negative would let a contaminated launch
through silently."""


class TowerWorkerStartupFailed(Exception):
    """Raised when the startup audit finds contamination. Reason string is `TOWER_WORKER_STARTUP_FAILED`
    plus the specific finding -- never a generic message, so a failed launch is diagnosable from its own
    exception text alone."""


@dataclass(frozen=True, slots=True)
class StartupAuditResult:
    passed: bool
    contaminated_sys_path_entries: tuple[str, ...]
    preloaded_host_names: tuple[str, ...]


def run_startup_audit(
    *, sys_path: list[str] | None = None, loaded_modules: Container[str] | None = None,
) -> StartupAuditResult:
    """Never raises -- returns a result the caller (`cli.main`) decides how to act on.

    `sys_path`/`loaded_modules` are injectable (default to the real, ambient `sys.path`/`sys.modules` when
    omitted, which is what `cli.main`'s production call site relies on) so tests can exercise the pure
    detection logic against a deliberately controlled, synthetic environment -- the real ambient `sys.path`
    during a test run is itself shaped by however the test runner was invoked (e.g. pytest's own rootdir
    insertion), which is a fact about the test harness, not about this worker's own startup contamination."""
    path_source = sys.path if sys_path is None else sys_path
    modules_source = sys.modules if loaded_modules is None else loaded_modules
    contaminated = tuple(p for p in path_source if AI_TRADER_REPO_MARKER in p)
    preloaded = tuple(name for name in CONFIRMED_HOST_MODULE_NAMES if name in modules_source)
    return StartupAuditResult(
        passed=not contaminated and not preloaded,
        contaminated_sys_path_entries=contaminated,
        preloaded_host_names=preloaded,
    )


def enforce_startup_audit(
    *, sys_path: list[str] | None = None, loaded_modules: Container[str] | None = None,
) -> None:
    """Raises `TowerWorkerStartupFailed` on any contamination. Called first thing in `cli.main` (with no
    arguments -- the real ambient environment), before `protocol`/`server` are even imported."""
    result = run_startup_audit(sys_path=sys_path, loaded_modules=loaded_modules)
    if result.passed:
        return
    reasons = []
    if result.contaminated_sys_path_entries:
        reasons.append(
            "AI Trader repo path present in sys.path: "
            + ", ".join(result.contaminated_sys_path_entries)
        )
    if result.preloaded_host_names:
        reasons.append(
            "confirmed host module name(s) already in sys.modules: "
            + ", ".join(result.preloaded_host_names)
        )
    raise TowerWorkerStartupFailed("TOWER_WORKER_STARTUP_FAILED: " + "; ".join(reasons))


def cwd_is_outside_repo(cwd: Path) -> bool:
    """Structural check the launch script itself should also honor (CWD outside the AI Trader repo) --
    exposed here as a pure function so both the launcher and the isolation tests can call the exact same
    logic rather than duplicating the string match."""
    return AI_TRADER_REPO_MARKER not in str(cwd.resolve())
