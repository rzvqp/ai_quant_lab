"""Tests for the v0 -> v1 migration mapper, and that S1's OWN already-migrated file on disk stays
schema-valid (a tripwire against silent drift)."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_manager.schema_validation import validate_contract
from ai_trader.strategy_runtime.migration import build_v1_contract_dict

V0_FIXTURE = {
    "id": "S99", "name": "Test Strategy", "slug": "S99_test", "klass": "Test",
    "status": "IMPLEMENTED", "sessions": "All sessions", "long_short": "long",
    "mechanism": "A test mechanism.", "entry_rules": "Enter on X.", "exit_rules": "Exit on Y.",
    "stop_loss_rules": "2 ticks past Z.",
    "position_sizing": {"model": "risk-normalised", "risk_definition": "risk = |entry-stop|",
                         "stop_floor": "max(...)", "costs": "1 tick/side"},
    "invalid_conditions": ["ATR non-finite"],
    "performance": {"historical": {"n": 100, "expectancy_R": 0.05, "profit_factor": 1.1}, "oos_expectancy_R": -0.02},
    "monte_carlo": "Wave-1 pilot p=0.031 -- DIAGNOSTIC only.",
    "walk_forward": "NOT RUN.",
    "validation_status": "EXPLORATORY", "confidence": "VERY LOW -- no confirmed alpha",
    "provenance": {"engine": "mstrat.py v2 (FROZEN)", "generated_from": "frozen research"},
}


def build_test_contract() -> dict:  # type: ignore[type-arg]
    return build_v1_contract_dict(
        V0_FIXTURE, last_review="2026-07-15",
        required_data=[{"timeframe": "M15", "fields": ["m_atr"], "lookback_bars": 20}],
        required_confirmations=["TEST_CONFIRM"],
        market_regime_applicable=["ANY"], market_regime_avoid=[],
        entry={"description": "Enter on X."}, exit_={"description": "Exit on Y."},
        stop={"description": "2 ticks past Z."},
    )


def test_migrated_dict_passes_schema_validation() -> None:
    v1 = build_test_contract()
    errors = validate_contract(v1)
    assert errors == [], errors


def test_migrated_dict_parses_into_a_typed_contract() -> None:
    v1 = build_test_contract()
    contract = parse_contract(v1)
    assert contract.identity.id == "S99"
    assert contract.lifecycle.status.value == "IMPLEMENTED"
    assert contract.lifecycle.maturity.value == "EXPLORATORY"
    assert contract.evidence.historical_metrics.expectancy_R == 0.05
    assert contract.evidence.oos_metrics.expectancy_R == -0.02
    assert contract.provenance.holdout_status.value == "SEALED"


def test_confidence_mapping_never_upgrades_low_confidence() -> None:
    v1 = build_test_contract()
    assert v1["evidence"]["confidence"]["level"] == "VERY_LOW"


def test_confidence_mapping_covers_every_tier() -> None:
    from ai_trader.strategy_runtime.migration import _confidence_from_v0
    assert _confidence_from_v0({"confidence": "LOW -- weak"})["level"] == "LOW"
    assert _confidence_from_v0({"confidence": "MEDIUM -- ok"})["level"] == "MEDIUM"
    assert _confidence_from_v0({"confidence": "HIGH -- strong"})["level"] == "HIGH"
    assert _confidence_from_v0({"confidence": "NEGATIVE -- harmful"})["level"] == "NEGATIVE"
    assert _confidence_from_v0({"confidence": "unrecognized text"})["level"] == "NONE"


def test_matched_null_pass_and_fail_status() -> None:
    from ai_trader.strategy_runtime.migration import _matched_null_from_v0
    assert _matched_null_from_v0({"monte_carlo": "pilot run p=0.01"})["status"] == "PASS"
    assert _matched_null_from_v0({"monte_carlo": "pilot run p=0.5"})["status"] == "FAIL"


def test_matched_null_extracts_p_value_honestly() -> None:
    v1 = build_test_contract()
    mn = v1["evidence"]["matched_null_status"]
    assert mn["p"] == 0.031
    assert mn["scope"] == "WAVE1"


def test_matched_null_never_fabricates_p_when_absent() -> None:
    v0 = dict(V0_FIXTURE)
    v0["monte_carlo"] = "No matched-null run yet."
    v1 = build_v1_contract_dict(
        v0, last_review="2026-07-15",
        required_data=[{"timeframe": "M15", "fields": ["m_atr"], "lookback_bars": 20}],
        required_confirmations=[], market_regime_applicable=["ANY"], market_regime_avoid=[],
        entry={"description": "x"}, exit_={"description": "y"}, stop={"description": "z"},
    )
    assert v1["evidence"]["matched_null_status"]["p"] is None
    assert v1["evidence"]["matched_null_status"]["status"] == "NOT_RUN"


class TestS1FileOnDisk:
    """A tripwire: S1's real, already-migrated ``strategy.json`` must stay schema-valid. If this
    ever fails, someone edited the file by hand without re-validating."""

    def test_s1_strategy_json_is_schema_valid_v1(self) -> None:
        path = Path(__file__).resolve().parents[3] / "knowledge" / "strategies" / "S01_confirmed_liquidity_sweep_reversal" / "strategy.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        errors = validate_contract(data)
        assert errors == [], errors
        assert data["identity"]["id"] == "S1"


#: Phase 6.8 Checkpoint 2 -- Wave B batches B1 (session/calendar) + B2 (liquidity/sweep).
CHECKPOINT_2_FOLDERS_BY_ID = {
    "S6": "S06_session_transition", "S16": "S16_previous_day_levels", "S17": "S17_weekly_levels",
    "S18": "S18_time_of_day_edge", "S19": "S19_session_gap", "S24": "S24_overnight_variance_session_carry",
    "S29": "S29_day_of_week_effect", "S30": "S30_kill_zone_time_window",
    "S31": "S31_month_end_month_start_effect", "S2": "S02_failed_breakout_fade",
    "S11": "S11_structure_break_reversal_choch", "S12": "S12_range_rotation",
    "S21": "S21_equal_highs_lows_liquidity_pool_raid", "S22": "S22_round_number_magnet_rejection",
}


class TestCheckpoint2FilesOnDisk:
    """The same tripwire as ``TestS1FileOnDisk``, extended to every strategy migrated in Checkpoint 2
    -- every v1 ``strategy.json`` stays schema-valid, and the original v0 export is preserved
    unchanged alongside it (never deleted)."""

    def test_every_checkpoint_2_strategy_json_is_schema_valid_v1(self) -> None:
        root = Path(__file__).resolve().parents[3] / "knowledge" / "strategies"
        for strategy_id, folder in CHECKPOINT_2_FOLDERS_BY_ID.items():
            data = json.loads((root / folder / "strategy.json").read_text(encoding="utf-8"))
            errors = validate_contract(data)
            assert errors == [], f"{folder}: {errors}"
            assert data["identity"]["id"] == strategy_id

    def test_every_checkpoint_2_v0_file_is_preserved(self) -> None:
        root = Path(__file__).resolve().parents[3] / "knowledge" / "strategies"
        for folder in CHECKPOINT_2_FOLDERS_BY_ID.values():
            v0_path = root / folder / "strategy.v0.json"
            assert v0_path.exists(), f"{folder}: original v0 export missing"
            v0 = json.loads(v0_path.read_text(encoding="utf-8"))
            assert "interface_version" not in v0  # the v0 shape, never migrated in place
