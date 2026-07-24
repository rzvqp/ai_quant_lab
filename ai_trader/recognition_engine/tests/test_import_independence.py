"""Static import-boundary verification -- Recognition Engine Phase 1A
(`RECOGNITION_ENGINE_PHASE1_DESIGN.md` §4/§10, CEO decisions 2-8). Confirms Recognition Engine never
imports Learning Feedback, Shadow Evidence, Decision Intelligence (v1 or v2), Risk Manager, Execution
Engine, Signal Engine, Scoring Engine, or Portfolio Architect; never writes to Context Memory's own
repository; never references `harness`; and contains no BUY/SELL/order/execution vocabulary of any kind
-- the same static-verification pattern `decision_intelligence_v2/tests/test_import_independence.py`
already established.
"""

from __future__ import annotations

import ast
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parents[1]

_FORBIDDEN_MODULE_PREFIXES = (
    "ai_trader.learning_feedback",
    "ai_trader.shadow_evidence",
    "ai_trader.decision_intelligence",
    "ai_trader.decision_intelligence_v2",
    "ai_trader.decision_comparison",
    "ai_trader.risk_manager",
    "ai_trader.execution_engine",
    "ai_trader.signal_engine",
    "ai_trader.scoring_engine",
    "ai_trader.portfolio_architect",
    "ai_trader.strategy_health",
)

#: Recognition Engine Phase 1A's ONLY legitimate dependency is Context Memory's own public read API --
#: not even Edge Intelligence/Market Intelligence, since Phase 1A reads exclusively from already-captured
#: PositionOutcome/Observation records, never a live snapshot.
_ALLOWED_AI_TRADER_PREFIXES = (
    "ai_trader.recognition_engine",
    "ai_trader.context_memory",
)

_REPOSITORY_WRITE_METHODS = (
    "append_context_snapshot", "append_context_snapshots", "append_observation", "append_observations",
    "append_outcome", "append_outcomes", "append_operational_metadata", "append_operational_metadatas",
    "append_interim_realization", "append_position_outcome",
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


def test_no_harness_reference_exists() -> None:
    for source_path in _production_source_files():
        assert "harness" not in source_path.read_text(encoding="utf-8").lower(), (
            f"{source_path.name} references 'harness'"
        )


def test_never_writes_to_context_memory_repository() -> None:
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        hits = {method for method in _REPOSITORY_WRITE_METHODS if method in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"context_memory repository write call found: {violations}"


def test_no_buy_sell_order_or_execution_vocabulary_in_source() -> None:
    forbidden_tokens = (
        "submit_order", "place_order", "send_order", "\"BUY\"", "\"SELL\"", "'BUY'", "'SELL'",
        "\"LONG\"", "\"SHORT\"", "'LONG'", "'SHORT'", "stop_loss", "take_profit", "lot_size",
        "entry_price", "confidence_to_trade",
    )
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        hits = {tok for tok in forbidden_tokens if tok in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"trading/execution vocabulary found: {violations}"


def test_no_recognitionverdict_style_classification_label_in_source() -> None:
    # Phase 1A's own explicit output-contract limit: descriptive statistics only, never a
    # FAVORABLE/UNFAVORABLE/NEUTRAL-style classification VERDICT (that belongs to a future,
    # not-yet-authorized phase, RECOGNITION_ENGINE_DESIGN.md's own original recognize()/RecognitionVerdict
    # design -- deliberately NOT what Phase 1A implements).
    # Deliberately NOT the bare word "verdict" -- this package's own docstrings legitimately discuss why
    # no verdict exists, in prose; that discussion must not trip this check.
    forbidden_tokens = ("RecognitionVerdict", "RECOGNIZED_FAVORABLE", "RECOGNIZED_UNFAVORABLE")
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        hits = {tok for tok in forbidden_tokens if tok in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"classification-verdict vocabulary found (out of Phase 1A scope): {violations}"
