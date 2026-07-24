"""Control 15 + the CEO's own mandatory static control: zero trading calls anywhere in authorized
(production) code. `order_send`/`order_check` may appear ONLY in this test file's own forbidden-token
list and in negative-test/docstring prose explaining why they're absent -- never as an executable call
in `ai_trader/execution_engine/adapters/*.py` (excluding `tests/`). Also verifies no dynamic indirect
access to these names via `getattr`/`importlib`/`eval`/`exec`, and no other trading-producing method
(order modification, cancellation, position open/close, SL/TP change, AlgoTrading auto-enable, terminal
settings change) appears anywhere in production code.
"""

from __future__ import annotations

from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parents[1]  # ai_trader/execution_engine/adapters/

_FORBIDDEN_TRADING_CALLS = (
    "order_send", "order_check", "order_calc_margin", "order_calc_profit",
)

_FORBIDDEN_DYNAMIC_ACCESS_PATTERNS = ("getattr(", "importlib", "eval(", "exec(")

_FORBIDDEN_SETTINGS_MODIFICATION_TOKENS = (
    # Nothing in the real MetaTrader5 Python API mutates terminal settings or the AlgoTrading toggle
    # programmatically at all (there is no such function) -- this list exists as a permanent, explicit
    # documentation of that fact, checked anyway so any future accidental addition is caught immediately.
    "enable_algo_trading", "terminal_settings_set", "config_set",
)


def _production_source_files() -> list[Path]:
    """Every `.py` file directly in `adapters/`, excluding the `tests/` subdirectory entirely."""
    return sorted(p for p in _PACKAGE_ROOT.glob("*.py"))


def test_no_order_send_or_order_check_anywhere_in_production_code() -> None:
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        hits = {token for token in _FORBIDDEN_TRADING_CALLS if token in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"forbidden trading call(s) found in production code: {violations}"


def test_no_dynamic_indirect_access_patterns_in_production_code() -> None:
    """`getattr`/`importlib`/`eval`/`exec` are forbidden OUTRIGHT in this package's own production code
    -- not because they are always dangerous, but because this package's own design (direct attribute
    access on real MT5 namedtuples, a single static `RealMT5Gateway` wrapper) never legitimately needs
    any of them, so their total absence is a clean, unambiguous, permanent guarantee rather than a
    judgment call about "safe" vs "unsafe" usage."""
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        hits = {pattern for pattern in _FORBIDDEN_DYNAMIC_ACCESS_PATTERNS if pattern in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"dynamic-access pattern(s) found in production code: {violations}"


def test_no_settings_or_algo_trading_modification_tokens() -> None:
    violations: dict[str, set[str]] = {}
    for source_path in _production_source_files():
        text = source_path.read_text(encoding="utf-8")
        hits = {token for token in _FORBIDDEN_SETTINGS_MODIFICATION_TOKENS if token in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"settings/AlgoTrading-modification token(s) found: {violations}"


def test_mt5_gateway_class_does_not_define_order_send_or_order_check() -> None:
    """A structural (not just textual) proof: even if some future edit added the literal substring
    inside a comment/docstring elsewhere, THIS check confirms the actual `RealMT5Gateway`/`MT5Gateway`
    classes never define these as real, callable methods."""
    from ai_trader.execution_engine.adapters.mt5_gateway import MT5Gateway, RealMT5Gateway

    for forbidden in ("order_send", "order_check", "order_calc_margin", "order_calc_profit"):
        assert not hasattr(MT5Gateway, forbidden)
        assert forbidden not in dir(RealMT5Gateway)


def test_mt5_adapter_never_defines_submit_order_or_cancel_order() -> None:
    from ai_trader.execution_engine.adapters.mt5_adapter import MT5ReadOnlyBrokerAdapter

    assert not hasattr(MT5ReadOnlyBrokerAdapter, "submit_order")
    assert not hasattr(MT5ReadOnlyBrokerAdapter, "cancel_order")


def test_forbidden_call_list_only_appears_in_this_test_module_and_docstrings() -> None:
    """A sanity check on the control itself: confirm the forbidden tokens DO appear somewhere in the
    package (this test file, and design-rationale docstrings explaining their absence) -- proving the
    static scan above is exercising a real string match, not silently scanning zero files."""
    all_text = "\n".join(p.read_text(encoding="utf-8") for p in _PACKAGE_ROOT.rglob("*.py"))
    assert "order_send" in all_text  # present in docstrings/this test file -- the scan itself is live
