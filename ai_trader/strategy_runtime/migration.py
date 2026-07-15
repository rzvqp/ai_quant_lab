"""v0 (Research Lab export) -> Strategy Interface v1 contract migration.

**Design decision** (documented, not accidental): the boilerplate/metrics/provenance portion of a v1
contract IS mechanically derivable from every v0 ``strategy.json`` (they share one uniform shape,
confirmed across all 43 runtime-eligible strategies -- see ``STRATEGY_RUNTIME_INTEGRATION_GAP.md``).
The SEMANTIC portion -- exactly which ``required_data`` fields/timeframes a strategy reads, its
``required_confirmations`` as a clean code list, and its ``entry``/``exit``/``stop`` ``RuleSpec``
text -- is NOT mechanically derivable from v0's free-text prose without risking exactly the
"invent missing semantics" failure mode the CEO explicitly forbade. So :func:`build_v1_contract_dict`
takes those as EXPLICIT, per-strategy arguments (supplied by whoever writes that strategy's own
runtime evaluator, since the evaluator code is the authoritative source of what it actually reads) and
fills everything else from the v0 document automatically.
"""

from __future__ import annotations

from typing import Any

INTERFACE_VERSION = "1.0.0"
ENGINE_PROVENANCE = "mstrat.py v2 (FROZEN)"


def _confidence_from_v0(v0: dict[str, Any]) -> dict[str, Any]:
    """v0's own ``confidence`` field is free text (e.g. "VERY LOW -- research-worthy in-sample but
    non-positive out-of-sample"). Map its LEADING descriptor onto the closed v1 vocabulary
    conservatively (never upgrades what the Research Lab itself already called low-confidence)."""
    text = str(v0.get("confidence", "")).upper()
    if text.startswith("VERY LOW"):
        level = "VERY_LOW"
    elif text.startswith("LOW"):
        level = "LOW"
    elif text.startswith("MEDIUM"):
        level = "MEDIUM"
    elif text.startswith("HIGH"):
        level = "HIGH"
    elif text.startswith("NEGATIVE") or "no confirmed alpha" in text.lower():
        level = "NEGATIVE" if text.startswith("NEGATIVE") else "VERY_LOW"
    else:
        level = "NONE"
    return {"level": level, "rationale": str(v0.get("confidence", ""))}


def _metrics_from_v0(perf: dict[str, Any] | None, historical: dict[str, Any] | None, segment: str) -> dict[str, Any]:
    src = historical if historical is not None else (perf or {})
    return {
        "segment": segment,
        "n": src.get("n"),
        "expectancy_R": src.get("expectancy_R"),
        "profit_factor": src.get("profit_factor"),
        "drawdown_R": src.get("drawdown_R"),
        "win_rate": src.get("win_rate"),
        "pos_months": src.get("pos_months"),
        "months": src.get("months"),
        "top1_share": src.get("top1_share"),
    }


def _matched_null_from_v0(v0: dict[str, Any]) -> dict[str, Any]:
    """v0's ``monte_carlo`` field is free text describing a matched-null pilot/wave result. Extract
    the ``p=`` value textually when present; otherwise honestly report NOT_RUN/INCONCLUSIVE rather
    than fabricate a number."""
    text = str(v0.get("monte_carlo", ""))
    p_value: float | None = None
    marker = "p="
    idx = text.find(marker)
    if idx != -1:
        rest = text[idx + len(marker):]
        digits = ""
        for ch in rest:
            if ch.isdigit() or ch == ".":
                digits += ch
            else:
                break
        try:
            p_value = float(digits) if digits else None
        except ValueError:
            p_value = None
    status = "INCONCLUSIVE" if "NO DIFFERENCE" in text or "no confirmed alpha" in text.lower() else (
        "PASS" if p_value is not None and p_value < 0.05 else ("FAIL" if p_value is not None else "NOT_RUN")
    )
    scope = "WAVE1" if "Wave-1" in text or "Wave 1" in text else ("PILOT" if "pilot" in text.lower() else "NONE")
    return {"status": status, "scope": scope, "note": text, "p": p_value, "adjusted_p": None}


def build_v1_contract_dict(
    v0: dict[str, Any], *, last_review: str,
    required_data: list[dict[str, Any]], required_confirmations: list[str],
    market_regime_applicable: list[str], market_regime_avoid: list[str],
    entry: dict[str, Any], exit_: dict[str, Any], stop: dict[str, Any], target: dict[str, Any] | None = None,
    max_concurrent_positions: int = 1,
) -> dict[str, Any]:
    """Build a schema-shaped (not yet validated -- the caller runs it through
    ``strategy_manager.schema_validation`` exactly like any other contract) v1 dict from a v0 spec +
    the strategy-specific semantic arguments its own evaluator author must supply."""
    perf = v0.get("performance") or {}
    historical = perf.get("historical")

    return {
        "interface_version": INTERFACE_VERSION,
        "identity": {
            "id": v0["id"], "name": v0["name"], "slug": v0["slug"], "version": "1.0.0",
            "class": v0["klass"],
        },
        "lifecycle": {
            "status": "IMPLEMENTED", "maturity": "EXPLORATORY", "current_health": "OK",
            "last_review": last_review,
        },
        "semantics": {
            "mechanism": v0["mechanism"],
            "signal_reason": v0.get("entry_rules", v0["mechanism"]),
            "market_regime": {"applicable": market_regime_applicable, "avoid": market_regime_avoid},
            "required_data": required_data,
            "required_confirmations": required_confirmations,
        },
        "execution": {
            "timeframe": "M15",
            "sessions": v0.get("sessions", "All sessions"),
            "long_short": str(v0.get("long_short", "both")).upper() if str(v0.get("long_short", "both")).upper() in ("LONG", "SHORT") else "BOTH",
            "entry": entry, "exit": exit_, "stop": stop,
            **({"target": target} if target is not None else {}),
            "risk_model": {
                "model": (v0.get("position_sizing") or {}).get("model", "risk-normalised (1R per trade)"),
                "risk_definition": (v0.get("position_sizing") or {}).get("risk_definition", "risk = |entry - executable_stop|"),
                "stop_floor": (v0.get("position_sizing") or {}).get("stop_floor", "max(2*spread_ticks*tick, 5*tick, 0.10*ATR)"),
                "costs": (v0.get("position_sizing") or {}).get("costs", "(spread 1 + slippage 1) ticks/side"),
            },
            "position_sizing": v0.get("position_sizing") or {},
            "max_concurrent_positions": max_concurrent_positions,
            "expected_frequency": {"trades_per_year": None, "basis": "not computed from v0 spec"},
            "cooldown": {"bars": 0, "scope": "PER_STRATEGY"},
            "invalid_conditions": v0.get("invalid_conditions") or [],
        },
        "evidence": {
            "confidence": _confidence_from_v0(v0),
            "historical_metrics": _metrics_from_v0(perf, historical, segment="historical"),
            "oos_metrics": _metrics_from_v0(perf, None, segment="oos") | {"expectancy_R": perf.get("oos_expectancy_R")},
            "walk_forward_status": "NOT_RUN" if "NOT RUN" in str(v0.get("walk_forward", "")).upper() else "INCONCLUSIVE",
            "matched_null_status": _matched_null_from_v0(v0),
            "global_fdr_status": "NOT_RUN",
            "validation_status": v0.get("validation_status", "EXPLORATORY"),
            "known_limitations": [str(v0.get("confidence", "")), str(v0.get("monte_carlo", ""))],
        },
        "provenance": {
            "engine": (v0.get("provenance") or {}).get("engine", ENGINE_PROVENANCE),
            "generated_from": (v0.get("provenance") or {}).get("generated_from", "frozen research; NO re-backtest, NO optimisation, NO engine change"),
            "holdout_status": "SEALED",
            "source_ref": v0.get("slug"),
        },
    }
