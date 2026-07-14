"""Synthetic, schema-conformant Strategy Execution Contract builders for tests.

The real Strategy Library's ``strategy.json`` files are "v0 seed" shape and do NOT validate against
``strategy_contract.v1.schema.json`` (see ``STRATEGY_INTERFACE_v1.md`` §7 — a known, documented,
separate-CEO-gated-migration gap, not a Strategy Manager defect). Unit/integration tests therefore
exercise the Manager's logic against synthetic fixtures that DO conform to the frozen v1 schema —
the correct testing strategy for code whose job is precisely "validate against the schema" (testing
against inputs the schema was designed to accept AND reject). A dedicated integration test
separately runs against the REAL Library and asserts the documented fail-safe quarantine outcome.
"""

from __future__ import annotations

from typing import Any


def make_contract_dict(
    id: str = "S1",
    name: str = "Test Strategy",
    slug: str | None = None,
    version: str = "1.0.0",
    klass: str = "test",
    status: str = "IMPLEMENTED",
    maturity: str = "EXPLORATORY",
    current_health: str = "OK",
    last_review: str = "2026-07-01",
    priority: int | None = None,
    interface_version: str = "1.0.0",
    required_data: list[dict[str, Any]] | None = None,
    dependencies: list[str] | None = None,
    walk_forward_status: str = "NOT_RUN",
    matched_null_status: str = "NOT_RUN",
    global_fdr_status: str = "NOT_RUN",
    holdout_status: str = "SEALED",
    target: dict[str, Any] | None = None,
    market_regime_applicable: list[str] | None = None,
    market_regime_avoid: list[str] | None = None,
) -> dict[str, Any]:
    """Build a full, schema-valid contract dict, with the common test-relevant fields exposed as
    keyword overrides. Every field not exposed here is a fixed, valid placeholder value."""
    num = "".join(ch for ch in id if ch.isdigit()) or "1"
    if slug is None:
        slug = f"S{int(num):02d}_test_strategy"
    if required_data is None:
        required_data = [{"timeframe": "M15", "fields": ["m_atr", "m_rsi"], "lookback_bars": 20, "htf": None}]

    return {
        "interface_version": interface_version,
        "identity": {"id": id, "name": name, "slug": slug, "version": version, "class": klass},
        "lifecycle": {
            "status": status, "maturity": maturity, "current_health": current_health,
            "last_review": last_review, "priority": priority,
        },
        "semantics": {
            "mechanism": "test mechanism", "signal_reason": "test reason",
            "market_regime": {
                "applicable": market_regime_applicable if market_regime_applicable is not None else ["ANY"],
                "avoid": market_regime_avoid if market_regime_avoid is not None else [],
            },
            "required_data": required_data,
            "required_confirmations": [],
            "dependencies": dependencies,
        },
        "execution": {
            "timeframe": "M15", "sessions": "all", "long_short": "BOTH",
            "entry": {"description": "test entry"}, "exit": {"description": "test exit"},
            "stop": {"description": "test stop"}, "target": target,
            "risk_model": {"model": "1R", "risk_definition": "test", "stop_floor": "test", "costs": "test"},
            "position_sizing": {}, "capital_limit": None, "max_concurrent_positions": 1,
            "expected_frequency": {"trades_per_year": 100.0, "basis": "test"},
            "cooldown": {"bars": 0, "scope": "PER_STRATEGY"},
            "invalid_conditions": ["test invalid condition"],
        },
        "evidence": {
            "confidence": {"level": "LOW", "rationale": "test", "score": None},
            "historical_metrics": {"segment": "research"},
            "oos_metrics": {"segment": "validation"},
            "walk_forward_status": walk_forward_status,
            "matched_null_status": {
                "status": matched_null_status, "scope": "NONE", "note": "test", "p": None, "adjusted_p": None,
            },
            "global_fdr_status": global_fdr_status,
            "validation_status": "EXPLORATORY",
            "known_limitations": [],
        },
        "provenance": {
            "engine": "test", "generated_from": "test", "holdout_status": holdout_status, "source_ref": None,
        },
    }


#: A contract with every validation-ladder gate satisfied -- reaches PROMOTED.
PROMOTED_GATE_OVERRIDES: dict[str, Any] = {
    "maturity": "PROMOTED",
    "walk_forward_status": "PASS",
    "matched_null_status": "PASS",
    "global_fdr_status": "PASS",
    "holdout_status": "OPENED",
}

#: A contract with the matched-null/walk-forward gate satisfied but not global-FDR/holdout -- reaches VALIDATED.
VALIDATED_GATE_OVERRIDES: dict[str, Any] = {
    "maturity": "VALIDATED",
    "walk_forward_status": "PASS",
    "matched_null_status": "PASS",
}
