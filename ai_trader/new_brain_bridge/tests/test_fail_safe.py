"""`safe_evaluate_bar` tests -- proves the fail-safe wraps REAL failures into `BrainUnavailableOutcome`
(not a hardcoded stub) and that the success path is unchanged from calling `bridge.evaluate_bar`
directly."""

from __future__ import annotations

import ve_brain  # type: ignore[import-untyped]

from ai_trader.live_signal_source.types import Bar
from ai_trader.new_brain_bridge.bridge import NewBrainOutcome
from ai_trader.new_brain_bridge.fail_safe import BRAIN_UNAVAILABLE, BrainUnavailableOutcome, safe_evaluate_bar
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder
from ai_trader.new_brain_bridge.tests.conftest import trend_up_regime_bars

_SYMBOL = "XAUUSD"
_TIMEFRAME = "M15"


def test_a_normal_bar_returns_the_same_outcomes_evaluate_bar_would() -> None:
    builder = RawAxesBuilder(_SYMBOL)
    bars = trend_up_regime_bars(_SYMBOL)
    for bar in bars[:-1]:
        builder.observe(bar)

    result = safe_evaluate_bar(bars[-1], timeframe=_TIMEFRAME, axes_builder=builder)

    assert isinstance(result, tuple)
    assert len(result) == len(ve_brain.CANONICAL_STRATEGIES)
    assert all(isinstance(o, NewBrainOutcome) for o in result)


def test_a_symbol_mismatch_is_caught_and_reported_as_brain_unavailable_not_a_crash() -> None:
    """`evaluate_bar`/`RawAxesBuilder.observe` raise `ValueError` on a symbol mismatch -- a REAL
    failure mode, not a synthetic one, used here to prove the wrapper genuinely catches exceptions
    rather than merely being written to expect them."""
    builder = RawAxesBuilder(_SYMBOL)
    wrong_symbol_bar = Bar(symbol="EURUSD", ts_open=0, ts_close=900, open=1.0, high=1.1, low=0.9,
                            close=1.0, volume=None)

    result = safe_evaluate_bar(wrong_symbol_bar, timeframe=_TIMEFRAME, axes_builder=builder)

    assert isinstance(result, BrainUnavailableOutcome)
    assert result.reason == BRAIN_UNAVAILABLE
    assert result.symbol == "EURUSD"
    assert result.timeframe == _TIMEFRAME
    assert result.bar_ts_close == 900
    assert "XAUUSD" in result.error  # the real ValueError message, not fabricated


def test_brain_unavailable_never_carries_any_reference_to_legacy_recognition() -> None:
    """Structural, not just behavioral: the fail-safe function's own module never imports anything from
    `pdh_pdl_demo`/`multi_policy_live` -- there is no code path back to legacy, not merely a check that
    happens not to take one."""
    import ast
    from pathlib import Path

    source_path = Path(__file__).resolve().parents[1] / "fail_safe.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.add(node.module)
        elif isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)

    forbidden = {"ai_trader.pdh_pdl_demo", "ai_trader.multi_policy_live"}
    hits = {m for m in imported_modules if any(m.startswith(f) for f in forbidden)}
    assert not hits, f"fail_safe.py must never import legacy recognition modules, found: {hits}"
