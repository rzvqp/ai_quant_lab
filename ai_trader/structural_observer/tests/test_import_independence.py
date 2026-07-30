"""Static import-boundary verification -- same 5-check pattern as every prior live package's own
precedent (`live_loop`, `execution_engine/adapters`, `context_memory`, `recognition_engine`). This
package's only non-`ai_trader` dependency is the vendored, git-submodule-pinned detector code at
`vendor/alpha_automation_detectors/code/` -- reached exclusively through `vendor_bridge.py`'s `sys.path`
insertion, never imported directly by any other module here. No execution-capable path exists: this
package only ever calls `journal.record(...)`, never touches risk/order/execution machinery."""

from __future__ import annotations

import ast
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parents[1]

_FORBIDDEN_MODULE_PREFIXES = (
    "ai_trader.execution_engine.broker_adapter",
    "ai_trader.execution_engine.pipeline",
    "ai_trader.order_manager",
    "ai_trader.mt5_demo_execution",
    "ai_trader.execution_orchestrator",
    "ai_trader.simulation",
    "ai_trader.learning_feedback",
    "ai_trader.shadow_evidence",
    "ai_trader.risk_manager",
    "ai_trader.risk_manager_live",
    "ai_trader.signal_engine",
    "ai_trader.scoring_engine",
    "ai_trader.decision_intelligence",
    "ai_trader.decision_intelligence_v2",
    "ai_trader.portfolio_architect",
    "ai_trader.portfolio_manager_live",
    "ai_trader.strategy_health",
    "ai_trader.recognition_engine",
    "ai_trader.recognition_engine_live",
    "ai_trader.context_memory",
)

_ALLOWED_AI_TRADER_PREFIXES = (
    "ai_trader.structural_observer",
    "ai_trader.live_signal_source.types",
    "ai_trader.persistent_state",
)

# The vendored detector modules are plain, non-namespaced scripts (`market_structure`, not
# `ai_trader.market_structure`) reached only via `vendor_bridge.py`'s `sys.path` insertion.
_VENDORED_MODULE_NAMES = (
    "market_structure", "imbalance_mechanics", "market_state", "order_flow", "order_block_void",
    "liquidity_mechanics", "institutional_levels", "interactions", "resample_ny", "gapfind",
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


def test_no_forbidden_imports_in_any_production_module() -> None:
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        imported = _imported_module_names(source_path)
        hits = {
            name for name in imported
            if any(name == prefix or name.startswith(prefix + ".") for prefix in _FORBIDDEN_MODULE_PREFIXES)
        }
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"forbidden imports found: {violations}"


def test_only_depends_on_allowed_ai_trader_packages() -> None:
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        imported = _imported_module_names(source_path)
        unexpected = {
            name for name in imported
            if name.startswith("ai_trader.")
            and not any(name == p or name.startswith(p + ".") for p in _ALLOWED_AI_TRADER_PREFIXES)
        }
        if unexpected:
            violations[source_path.name] = unexpected
    assert not violations, f"unexpected ai_trader dependency: {violations}"


def test_vendored_detector_modules_are_imported_only_by_vendor_bridge() -> None:
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        if source_path.name == "vendor_bridge.py":
            continue
        imported = _imported_module_names(source_path)
        hits = {name for name in imported if name in _VENDORED_MODULE_NAMES}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"vendored detector module imported outside vendor_bridge.py: {violations}"


def test_no_order_or_execution_vocabulary() -> None:
    """`vendor_bridge.py`'s own docstring mentions `MetaTrader5` by name (comparing its `type: ignore`
    convention to `RealMT5Gateway`'s) -- that is documentation, not a dependency, so it is checked
    separately below via an actual `import` statement, not raw substring presence."""
    forbidden = (
        "order_send", "order_check", "submit_order", "cancel_order", "close_position",
        "BrokerAdapter", "DryRunBrokerAdapter", "MT5DemoBrokerAdapter",
    )
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        hits = {tok for tok in forbidden if tok in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"order/execution vocabulary found: {violations}"


def test_metatrader5_is_never_actually_imported() -> None:
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        imported = _imported_module_names(source_path)
        hits = {name for name in imported if name == "MetaTrader5" or name.startswith("MetaTrader5.")}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"MetaTrader5 actually imported (not just mentioned): {violations}"


def test_candidate_signal_and_trade_proposal_are_never_imported() -> None:
    """`observing_rule.py` legitimately DISCUSSES `RecognitionRule` in prose/type-conformance (it
    implements that Protocol -- the whole point of the class) and `CandidateSignal` by name (comparing
    itself to the producer's own design in its docstring) -- neither is a real dependency, so this checks
    actual imports, not raw text presence."""
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        imported = _imported_module_names(source_path)
        hits = {
            name for name in imported
            if "CandidateSignal" in name or "TradeProposal" in name
        }
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"execution-signal type actually imported: {violations}"


def test_no_file_ever_constructs_a_non_null_livecandidate() -> None:
    """The one place a `LiveCandidate(` constructor call would legitimately appear is a REAL recognition
    rule -- this package ships none. `evaluate()` methods here must return `None` unconditionally."""
    violations: list[str] = []
    for source_path in _production_source_files():
        if "LiveCandidate(" in source_path.read_text(encoding="utf-8"):
            violations.append(source_path.name)
    assert not violations, f"LiveCandidate constructed -- this package is a pure OBSERVER: {violations}"
