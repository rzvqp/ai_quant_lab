"""Integration tests for :class:`ai_trader.strategy_manager.manager.StrategyManager` — full
lifecycle walks and multi-strategy scenarios against a synthetic (schema-conformant) Library."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from ai_trader.strategy_manager.config import ManagerConfig
from ai_trader.strategy_manager.manager import StrategyManager
from ai_trader.strategy_manager.tests.fixtures.contracts import (
    PROMOTED_GATE_OVERRIDES,
    VALIDATED_GATE_OVERRIDES,
    make_contract_dict,
)
from ai_trader.strategy_manager.tests.fixtures.fake_scanner import FakeScanner
from ai_trader.strategy_manager.types import Health, Lifecycle

AS_OF = int(datetime(2026, 7, 10, tzinfo=UTC).timestamp())


def _write(tmp_path: Path, folder: str, data: dict) -> None:
    d = tmp_path / folder
    d.mkdir(parents=True, exist_ok=True)
    (d / "strategy.json").write_text(json.dumps(data), encoding="utf-8")


def _manager(tmp_path: Path, scanner: FakeScanner | None = None, **config_kwargs) -> tuple[StrategyManager, FakeScanner]:
    scanner = scanner or FakeScanner()
    mgr = StrategyManager(ManagerConfig(library_path=tmp_path, **config_kwargs))
    mgr.configure(scanner)
    return mgr, scanner


class TestMultiStrategyAggregation:
    def test_union_dedup_and_max_lookback_across_three_strategies(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1", required_data=[
            {"timeframe": "M15", "fields": ["m_atr"], "lookback_bars": 10, "htf": None},
        ]))
        _write(tmp_path, "S02_b", make_contract_dict(id="S2", required_data=[
            {"timeframe": "M15", "fields": ["m_atr", "m_rsi"], "lookback_bars": 30, "htf": None},
        ]))
        _write(tmp_path, "S03_c", make_contract_dict(id="S3", required_data=[
            {"timeframe": "H1", "fields": ["h1_trend_up"], "lookback_bars": 5, "htf": None},
        ]))
        mgr, scanner = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        for sid in ("S1", "S2", "S3"):
            assert mgr.activate(sid).ok

        agg = mgr.required_context()
        assert agg.timeframes == frozenset({"M15", "H1"})
        assert agg.required_fields_by_timeframe["M15"] == frozenset({"m_atr", "m_rsi"})  # deduped union
        assert agg.lookback_by_timeframe["M15"] == 30  # max wins
        assert agg.contributor_ids == ("S1", "S2", "S3")

        last_req = scanner.registered_requirements[-1]
        assert last_req.timeframes == frozenset({"M15", "H1"})
        assert last_req.lookback_by_timeframe["M15"] == 30

    def test_deactivating_one_strategy_shrinks_the_aggregate(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1", required_data=[
            {"timeframe": "M15", "fields": ["m_atr"], "lookback_bars": 10, "htf": None},
        ]))
        _write(tmp_path, "S02_b", make_contract_dict(id="S2", required_data=[
            {"timeframe": "H4", "fields": ["h4_trend_up"], "lookback_bars": 5, "htf": None},
        ]))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        mgr.activate("S1")
        mgr.activate("S2")
        assert mgr.required_context().timeframes == frozenset({"M15", "H4"})
        mgr.deactivate("S2")
        assert mgr.required_context().timeframes == frozenset({"M15"})
        assert mgr.required_context().contributor_ids == ("S1",)


class TestDependencyChain:
    def test_missing_dependency_blocks_health_then_recovers(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        _write(tmp_path, "S02_b", make_contract_dict(id="S2", dependencies=["S1"]))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        # S1 not yet active -> S2's declared dependency is unsatisfied.
        assert mgr.find_strategy("S2").health is Health.MISSING_DEPENDENCY

        mgr.activate("S1")  # activate() itself now runs a full refine_health pass on success
        assert mgr.find_strategy("S2").health is Health.LOADED

    def test_missing_dependency_actually_blocks_activation_not_just_health(self, tmp_path: Path) -> None:
        # health=MISSING_DEPENDENCY alone must not be the only signal -- activate() has to actually
        # refuse, or an unsatisfied dependency would still reach the Signal Engine.
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        _write(tmp_path, "S02_b", make_contract_dict(id="S2", dependencies=["S1"]))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)

        result = mgr.activate("S2")
        assert result.ok is False
        assert "missing/inactive dependencies" in result.reason
        assert mgr.find_strategy("S2").active is False
        assert mgr.active_strategies() == []

        mgr.activate("S1")
        result = mgr.activate("S2")  # now satisfied
        assert result.ok is True
        assert {h.id for h in mgr.active_strategies()} == {"S1", "S2"}

    def test_deactivating_a_dependency_re_flags_dependents_immediately(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        _write(tmp_path, "S02_b", make_contract_dict(id="S2", dependencies=["S1"]))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        mgr.activate("S1")
        mgr.activate("S2")
        assert mgr.find_strategy("S2").health is Health.LOADED

        mgr.deactivate("S1")  # S2 stays active (deactivate() doesn't force-retract dependents)...
        # ...but its health must immediately reflect the now-broken dependency, without a full reload.
        assert mgr.find_strategy("S2").health is Health.MISSING_DEPENDENCY

    def test_unknown_dependency_id_also_blocks(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1", dependencies=["S999"]))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        assert mgr.find_strategy("S1").health is Health.MISSING_DEPENDENCY


class TestValidationLadderGates:
    def test_admits_directly_to_validated_when_gates_pass(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1", **VALIDATED_GATE_OVERRIDES))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        result = mgr.activate("S1")
        assert result.ok
        assert result.to_state is Lifecycle.VALIDATED

    def test_admits_directly_to_promoted_when_all_gates_pass(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1", **PROMOTED_GATE_OVERRIDES))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        result = mgr.activate("S1")
        assert result.ok
        assert result.to_state is Lifecycle.PROMOTED

    def test_holds_at_candidate_when_validated_gate_not_satisfied(self, tmp_path: Path) -> None:
        # Reflects reality lab-wide today: no strategy has walk-forward/matched-null PASS yet.
        _write(tmp_path, "S01_a", make_contract_dict(id="S1", maturity="VALIDATED"))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        result = mgr.activate("S1")
        assert result.ok
        assert result.to_state is Lifecycle.CANDIDATE
        assert "gate is not satisfied" in result.reason

    def test_holdout_sealed_always_blocks_promoted(self, tmp_path: Path) -> None:
        # Project-wide invariant: holdout stays SEALED. A contract cannot reach PROMOTED while
        # provenance.holdout_status=SEALED, no matter what else passes.
        overrides = dict(PROMOTED_GATE_OVERRIDES)
        overrides["holdout_status"] = "SEALED"
        _write(tmp_path, "S01_a", make_contract_dict(id="S1", **overrides))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        result = mgr.activate("S1")
        assert result.to_state is Lifecycle.VALIDATED  # held below PROMOTED


class TestFullLifecycleWalk:
    def test_load_activate_reload_disable_enable_retire(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1", maturity="EXPLORATORY"))
        mgr, scanner = _manager(tmp_path)

        report = mgr.load_library(as_of=AS_OF)
        assert report.loaded == ("S1",)
        assert mgr.find_strategy("S1").lifecycle is Lifecycle.EXPERIMENTAL

        act = mgr.activate("S1")
        assert act.to_state is Lifecycle.EXPLORATORY
        assert len(mgr.active_strategies()) == 1

        _write(tmp_path, "S01_a", make_contract_dict(id="S1", maturity="CANDIDATE"))
        mgr.reload(as_of=AS_OF + 1, strategy_id="S1")
        assert mgr.find_strategy("S1").lifecycle is Lifecycle.CANDIDATE
        assert mgr.find_strategy("S1").active is True

        dis = mgr.disable("S1", reason="operator kill-switch drill")
        assert dis.to_state is Lifecycle.DISABLED
        assert mgr.active_strategies() == []

        en = mgr.enable("S1")
        assert en.to_state is Lifecycle.CANDIDATE  # restored to its pre-disable tier
        assert len(mgr.active_strategies()) == 1

        ret = mgr.retire("S1", reason="superseded by S2 research")
        assert ret.to_state is Lifecycle.RETIRED
        assert mgr.active_strategies() == []
        assert mgr.activate("S1").ok is False  # terminal

        final_snapshot_errors = mgr.validate_snapshot_against_schema()
        assert final_snapshot_errors == []


class TestDisableSurvivesReload:
    def test_kill_switch_not_cleared_by_a_routine_reload(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1", maturity="CANDIDATE"))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        mgr.activate("S1")
        assert mgr.find_strategy("S1").lifecycle is Lifecycle.CANDIDATE

        mgr.disable("S1", reason="drawdown breach")
        assert mgr.find_strategy("S1").lifecycle is Lifecycle.DISABLED
        assert mgr.find_strategy("S1").health is Health.DISABLED

        # An unrelated evidence-field update republishes the contract -- this must NOT reactivate it.
        _write(tmp_path, "S01_a", make_contract_dict(id="S1", maturity="CANDIDATE", name="Updated Name"))
        mgr.reload(as_of=AS_OF + 1, strategy_id="S1")
        assert mgr.find_strategy("S1").lifecycle is Lifecycle.DISABLED
        assert mgr.find_strategy("S1").health is Health.DISABLED
        assert mgr.find_strategy("S1").name == "Updated Name"  # contract data still refreshed
        assert mgr.active_strategies() == []

        # enable() still restores to the correct pre-disable tier afterward.
        en = mgr.enable("S1")
        assert en.ok
        assert en.to_state is Lifecycle.CANDIDATE

    def test_whole_library_reload_also_preserves_disabled(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        mgr, _ = _manager(tmp_path)
        mgr.load_library(as_of=AS_OF)
        mgr.activate("S1")
        mgr.disable("S1", reason="test")
        _write(tmp_path, "S01_a", make_contract_dict(id="S1", name="Changed"))
        mgr.reload(as_of=AS_OF + 1)  # whole-library reload, not single-id
        assert mgr.find_strategy("S1").lifecycle is Lifecycle.DISABLED


class TestAutoAdmitOnReload:
    def test_auto_admit_applies_to_an_existing_experimental_strategy_on_reload(self, tmp_path: Path) -> None:
        # A strategy loaded before auto-admission would have applied (or never eligible until a
        # later contract update) must still get admitted once a qualifying reload happens -- not
        # only brand-new strategies discovered during that same reload.
        _write(tmp_path, "S01_a", make_contract_dict(id="S1", maturity="CANDIDATE"))
        mgr, _ = _manager(tmp_path, auto_admit_min_maturity="EXPLORATORY")
        mgr.load_library(as_of=AS_OF)
        assert mgr.find_strategy("S1").active is True  # admitted at initial load already

        # Deliberately withdraw admission, simulating a strategy that rests at EXPERIMENTAL...
        mgr.deactivate("S1")
        assert mgr.find_strategy("S1").active is False
        assert mgr.find_strategy("S1").lifecycle is Lifecycle.EXPERIMENTAL

        # ...then an unrelated content change triggers a reload. Auto-admit must re-fire.
        _write(tmp_path, "S01_a", make_contract_dict(id="S1", maturity="CANDIDATE", name="v2"))
        mgr.reload(as_of=AS_OF + 1, strategy_id="S1")
        assert mgr.find_strategy("S1").active is True
        assert mgr.find_strategy("S1").lifecycle is Lifecycle.CANDIDATE


class TestBestEffortLoad:
    def test_one_bad_file_never_aborts_the_others(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        d = tmp_path / "S02_broken"
        d.mkdir()
        (d / "strategy.json").write_text("{not json", encoding="utf-8")
        _write(tmp_path, "S03_c", make_contract_dict(id="S3"))

        mgr, _ = _manager(tmp_path)
        report = mgr.load_library(as_of=AS_OF)
        assert set(report.loaded) == {"S1", "S3"}
        assert len(report.failed) == 1
        assert report.failed[0].health is Health.CORRUPTED


class TestDeterminism:
    def test_same_library_loaded_twice_is_identical(self, tmp_path: Path) -> None:
        _write(tmp_path, "S01_a", make_contract_dict(id="S1"))
        _write(tmp_path, "S02_b", make_contract_dict(id="S2", dependencies=["S1"]))
        mgr, _ = _manager(tmp_path)

        mgr.load_library(as_of=AS_OF)
        mgr.activate("S1")
        snap1 = mgr.snapshot()

        mgr.load_library(as_of=AS_OF)  # full reset + reload
        mgr.activate("S1")
        snap2 = mgr.snapshot()

        assert snap1 == snap2
