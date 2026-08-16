"""`shadow_cost_model.py` tests — CEO decision 2026-08-16 ("Costurile pe care le monitorizezi si le
calculezi in shadow devin sursa canonica"). Proves: (1) the published numbers trace to the exact
git-committed report this module claims, not to memory or invention; (2) known fixtures Red Team can
re-derive by hand; (3) fail-closed on every unavailable component, never a silent zero; (4) the manifest's
own fields are internally consistent and reproducible across calls; (5) the published cost fields are
directly consumable by `ve_brain.DecisionRequest` without adaptation, so this division, the evaluator, and
Alpha all read the same numbers under the same field names."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import ve_brain  # type: ignore[import-untyped]

from ai_trader.mandate2_readiness import shadow_cost_model as scm

_REPO_ROOT = Path(__file__).resolve().parents[3]


def _git_hash_object(relative_path: str) -> str:
    result = subprocess.run(
        ["git", "hash-object", relative_path], cwd=_REPO_ROOT, capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def test_source_report_blob_hash_matches_the_live_committed_file() -> None:
    """The single most important trust check: this module's claimed provenance
    (`SOURCE_REPORT_BLOB_SHA1`) must match the ACTUAL current content of the file it cites, computed
    fresh via `git hash-object` -- not merely asserted equal to itself. If the report is ever edited,
    this test fails LOUDLY rather than letting `shadow_cost_model.py` silently drift from its own
    citation."""
    actual = _git_hash_object(scm.SOURCE_REPORT_PATH)
    assert actual == scm.SOURCE_REPORT_BLOB_SHA1, (
        f"{scm.SOURCE_REPORT_PATH} has changed since commit {scm.SOURCE_REPORT_COMMIT} -- "
        f"shadow_cost_model.py's own citation is now stale and must be re-derived, not assumed"
    )


def test_slippage_mechanism_blob_hash_matches_the_live_committed_file() -> None:
    actual = _git_hash_object(scm.SLIPPAGE_MECHANISM_SOURCE_PATH)
    assert actual == scm.SLIPPAGE_MECHANISM_BLOB_SHA1


def test_base_provisional_matches_the_ratified_report_table_exactly() -> None:
    """Fixture with a KNOWN result, hand-verifiable against
    `AI_TRADER_MANDATE8_STEP1_COST_CALIBRATION_REPORT.md` section 3's own table."""
    assert scm.BASE_PROVISIONAL.full_spread_price == 0.05
    assert scm.BASE_PROVISIONAL.entry_slippage_price == 0.00
    assert scm.BASE_PROVISIONAL.exit_slippage_price == 0.00
    assert scm.BASE_PROVISIONAL.round_trip_total == pytest.approx(0.05)


def test_stress_provisional_matches_the_ratified_report_table_exactly() -> None:
    assert scm.STRESS_PROVISIONAL.full_spread_price == 0.08
    assert scm.STRESS_PROVISIONAL.entry_slippage_price == 0.08
    assert scm.STRESS_PROVISIONAL.exit_slippage_price == 0.08
    assert scm.STRESS_PROVISIONAL.round_trip_total == pytest.approx(0.24)


def test_full_spread_entry_exit_accessors_match_the_tier_constants() -> None:
    assert scm.full_spread_price(tier="BASE") == scm.BASE_PROVISIONAL.full_spread_price
    assert scm.entry_slippage_price(tier="BASE") == scm.BASE_PROVISIONAL.entry_slippage_price
    assert scm.exit_slippage_price(tier="BASE") == scm.BASE_PROVISIONAL.exit_slippage_price
    assert scm.full_spread_price(tier="STRESS") == scm.STRESS_PROVISIONAL.full_spread_price
    assert scm.round_trip_cost(tier="STRESS") == pytest.approx(0.24)


def test_unknown_tier_fails_closed() -> None:
    with pytest.raises(scm.CostModelUnavailableError):
        scm.full_spread_price(tier="MEDIAN")  # not a published tier -- must refuse, not guess


def test_real_measured_slippage_always_fails_closed_today() -> None:
    """Zero NU e fallback -- confirmed: this must raise for BOTH legs, never return 0.0."""
    with pytest.raises(scm.CostModelUnavailableError):
        scm.real_measured_slippage(leg="entry")
    with pytest.raises(scm.CostModelUnavailableError):
        scm.real_measured_slippage(leg="exit")
    with pytest.raises(scm.CostModelUnavailableError):
        scm.real_measured_slippage(leg="unknown-leg")


def test_spread_distribution_clean_matches_the_ratified_report_table() -> None:
    d = scm.SPREAD_DISTRIBUTION_CLEAN
    assert d["n"] == 175
    assert d["median_p50"] == pytest.approx(0.0700)
    assert d["p90"] == pytest.approx(0.1240)
    assert d["mean"] == pytest.approx(0.0809)


def test_spread_distribution_by_session_matches_the_ratified_report_table() -> None:
    assert scm.SPREAD_DISTRIBUTION_BY_SESSION["ny"]["n"] == 83
    assert scm.SPREAD_DISTRIBUTION_BY_SESSION["ny"]["median_p50"] == pytest.approx(0.0800)
    assert scm.SPREAD_DISTRIBUTION_BY_SESSION["asia"]["n"] == 38
    assert scm.SPREAD_DISTRIBUTION_BY_SESSION["london"]["n"] == 33
    assert scm.SPREAD_DISTRIBUTION_BY_SESSION["late"]["n"] == 21
    assert sum(s["n"] for s in scm.SPREAD_DISTRIBUTION_BY_SESSION.values()) == 175  # accounts for every clean observation


def test_bridge_py_cost_literal_mismatch_is_real_and_disclosed() -> None:
    """This is the genuine discrepancy this canonicalization effort found -- confirmed here as a
    standing fact, not silently resolved. If a future commit makes bridge.py match BASE_PROVISIONAL (or
    a new ratified standard), this test's own assertion direction is the signal to update it -- NEVER
    flip it without also updating shadow_cost_model.py's own docstring explaining why."""
    assert scm.BRIDGE_PY_COST_LITERAL_MISMATCH is True
    assert scm._BRIDGE_PY_COST_LITERAL.full_spread_price == 0.10  # noqa: SLF001 -- test-only introspection
    assert scm._BRIDGE_PY_COST_LITERAL.round_trip_total == pytest.approx(0.20)  # noqa: SLF001


def test_content_hash_is_deterministic_across_calls() -> None:
    assert scm.content_hash() == scm.content_hash()
    assert len(scm.content_hash()) == 64  # sha256 hex digest


def test_configuration_fingerprint_is_deterministic_and_truncated() -> None:
    assert scm.configuration_fingerprint() == scm.configuration_fingerprint()
    assert len(scm.configuration_fingerprint()) == 16


def test_data_identity_carries_the_real_git_anchored_provenance() -> None:
    di = scm.data_identity()
    assert di["symbol"] == "XAUUSD"
    assert di["n_clean_observations"] == 175
    assert di["source_report_commit"] == "351f789"
    assert di["source_report_blob_sha1"] == scm.SOURCE_REPORT_BLOB_SHA1


def test_manifest_is_a_single_complete_object_with_every_required_field() -> None:
    m = scm.manifest()
    required_top_level = {
        "shadow_cost_model_version", "broker_server", "symbol", "units", "entry_order_type",
        "exit_order_type", "monitored_calendar_days", "base_provisional", "stress_provisional",
        "formula", "spread_distribution_clean", "spread_distribution_by_session",
        "slippage_distribution", "data_source", "source_report_path", "source_report_commit",
        "source_report_blob_sha1", "data_identity", "configuration_fingerprint", "content_hash",
        "bridge_py_cost_literal_mismatch",
    }
    assert required_top_level.issubset(m.keys())
    assert m["shadow_cost_model_version"] == "v1"
    assert m["slippage_distribution"] == "COST_MODEL_UNAVAILABLE -- zero real observations"
    assert m["bridge_py_cost_literal_mismatch"] is True


def test_manifest_is_deterministic_across_calls() -> None:
    assert scm.manifest() == scm.manifest()


def test_published_cost_fields_are_directly_consumable_by_ve_brain_decision_request() -> None:
    """The literal proof that 'evaluatorul si Alpha produc acelasi cost': `ve_brain.DecisionRequest`'s
    own three cost fields accept this module's published values with NO adaptation, wrapper, or unit
    conversion -- same field names, same semantics (full bid-ask spread, per-leg slippage, price units)."""
    canon = next(c for c in ve_brain.CANONICAL_STRATEGIES if c.strategy_id == "trend_pullback")
    request = ve_brain.DecisionRequest(
        contract_id=ve_brain.INPUT_CONTRACT_ID,
        strategy_id=canon.strategy_id, strategy_version=canon.strategy_version,
        validation_status=canon.validation_status, strategy_family=canon.strategy_family,
        strategy_policy_fingerprint=ve_brain.strategy_policy_fingerprint(canon),
        market_event_id="shadow-cost-model-fixture-event", regime_fingerprint="fp",
        market_state_ref="ref", regime_label="TREND_UP", bias_direction="LONG",
        market_map_available=False, levels_available=False, confirmation_available=False,
        entry_price=2000.0, stop_price=1990.0, target_kind="rr", target_param=2.0, holding_window=10,
        atr=10.0, probability_inputs=None,
        full_spread_price=scm.full_spread_price(tier="BASE"),
        entry_slippage_price=scm.entry_slippage_price(tier="BASE"),
        exit_slippage_price=scm.exit_slippage_price(tier="BASE"),
        symbol=scm.SYMBOL, timeframe="M15", block_start=0, block_end=900,
        segment_id="shadow-cost-model-fixture", manifest_hash="shadow-cost-model-fixture-manifest",
        n1_contract_version=ve_brain.N1_CONTRACT_VERSION,
        raw_axis_schema_version=ve_brain.RAW_AXIS_SCHEMA_VERSION, router_version=ve_brain.ROUTER_VERSION,
        eligibility_policy_version="eligibility-v1",
        measurement_contract_version=ve_brain.MEASUREMENT_CONTRACT_VERSION,
        configuration_fingerprint="shadow-cost-model-fixture-cfg",
    )
    assert request.full_spread_price == 0.05
    assert request.entry_slippage_price == 0.00
    assert request.exit_slippage_price == 0.00
