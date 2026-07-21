"""Capability gate -- the single enforcement point for what Alpha may do on TradingView.

Every TradingView action Alpha (or the dossier builder, or an Alpha follow-up request) attempts
is classified here BEFORE it reaches the Node bridge. Default-deny: any verb not explicitly
allowed is refused. Classes:

  READ      -- non-mutating observation (chart/indicator/Pine/screenshot reads)
  NAVIGATE  -- changes the chart view/state (symbol/timeframe/replay/visible-range/tabs)
  MUTATE    -- adds/removes/configures research objects (indicators, drawings, Pine authoring)
  GATED     -- powerful mutation that may write to the TradingView account (Pine compile/save);
               allowed only when config.tv_pine_apply is True (kept off by default in v1)
  DENY      -- strictly prohibited (trades, broker, alerts, Strategy-Tester/backtest evidence)

MUTATE/GATED/NAVIGATE actions are all logged and linked to the investigation by the client;
the classification here only decides allow/deny and whether the action is "mutating" (for the
provenance log).
"""

from __future__ import annotations

from typing import Dict

READ = "READ"
NAVIGATE = "NAVIGATE"
MUTATE = "MUTATE"
GATED = "GATED"
DENY = "DENY"

# Authoritative verb -> class registry. The Node bridge dispatches these same verb names to
# tradingview-mcp core functions; a test asserts the bridge's verb set matches this registry.
VERB_CLASS: Dict[str, str] = {
    # --- READ (observation) ---
    "get_state": READ,
    "get_ohlcv": READ,
    "get_quote": READ,
    "get_study_values": READ,
    "get_indicator": READ,
    "get_pine_lines": READ,
    "get_pine_labels": READ,
    "get_pine_tables": READ,
    "get_pine_boxes": READ,
    "get_visible_range": READ,
    "get_depth": READ,
    "list_drawings": READ,
    "replay_status": READ,
    "symbol_info": READ,
    "symbol_search": READ,
    "tab_list": READ,
    "capture_screenshot": READ,
    "pine_get_source": READ,
    "pine_get_errors": READ,
    "pine_analyze": READ,      # offline static analysis, no chart/cloud effect
    "pine_check": READ,        # REST validation, no chart/cloud effect
    # --- NAVIGATE (view/state changes) ---
    "set_symbol": NAVIGATE,
    "set_timeframe": NAVIGATE,
    "set_type": NAVIGATE,
    "set_visible_range": NAVIGATE,
    "scroll_to_date": NAVIGATE,
    "replay_start": NAVIGATE,
    "replay_step": NAVIGATE,
    "replay_stop": NAVIGATE,
    "replay_autoplay": NAVIGATE,
    "tab_new": NAVIGATE,
    "tab_switch": NAVIGATE,
    "tab_close": NAVIGATE,
    # --- MUTATE (research objects / Pine authoring, no cloud write) ---
    "add_indicator": MUTATE,
    "remove_indicator": MUTATE,
    "set_indicator_inputs": MUTATE,
    "toggle_indicator": MUTATE,
    "draw_shape": MUTATE,
    "remove_drawing": MUTATE,
    "clear_drawings": MUTATE,
    "pine_set_source": MUTATE,   # inject into editor only (no compile, no save)
    "pine_new": MUTATE,
    "pine_open": MUTATE,
    # --- GATED (may write to the TradingView account) ---
    "pine_compile": GATED,
    "pine_smart_compile": GATED,
    "pine_save": GATED,
}

# Explicitly prohibited -- these are hard errors regardless of any flag.
DENY_VERBS = {
    "replay_trade",          # placing/simulating trades
    "alert_create",          # alert functions
    "alert_delete",
    "alert_list",
    "get_strategy_results",  # Strategy Tester profitability -- never edge evidence
    "get_trades",            # Strategy Tester / broker trade list
    "get_equity",            # Strategy Tester equity curve
    "watchlist_add",         # unrelated to research
    "layout_save",           # persistent account layout write unrelated to research logging
}


class CapabilityDenied(PermissionError):
    def __init__(self, verb: str, reason: str):
        self.verb = verb
        self.reason = reason
        super().__init__(f"capability denied for {verb!r}: {reason}")


def classify(verb: str) -> str:
    """Return the capability class for a verb (DENY if unknown or explicitly denied)."""
    if verb in DENY_VERBS:
        return DENY
    return VERB_CLASS.get(verb, DENY)


def is_mutating(verb: str) -> bool:
    return classify(verb) in (MUTATE, GATED)


def check(verb: str, *, pine_apply: bool = False) -> str:
    """Authorize a verb. Returns its class or raises CapabilityDenied."""
    cls = classify(verb)
    if cls == DENY:
        if verb in DENY_VERBS:
            raise CapabilityDenied(verb, "prohibited action (trades/broker/alerts/strategy-tester)")
        raise CapabilityDenied(verb, "unknown verb (default-deny)")
    if cls == GATED and not pine_apply:
        raise CapabilityDenied(
            verb, "Pine compile/save may write to the TradingView account; enable config.tv_pine_apply to allow")
    return cls


def allowed_verbs(pine_apply: bool = False) -> list:
    """The verbs Alpha may currently use (for advertising the action menu to Alpha)."""
    out = [v for v, c in VERB_CLASS.items() if c != GATED]
    if pine_apply:
        out += [v for v, c in VERB_CLASS.items() if c == GATED]
    return sorted(out)
