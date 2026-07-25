from __future__ import annotations

from pathlib import Path

import pytest

from ai_trader.execution_engine.ledger import OrderLedger
from ai_trader.execution_orchestrator.tests._fixtures import make_candidate, make_deps, make_market_context
from ai_trader.execution_orchestrator.types import OrchestratorConfig, OrchestratorDependencies
from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.gating import send_after_dry_run_gate
from ai_trader.mt5_demo_execution.safety import verify_safety_guards
from ai_trader.mt5_demo_execution.tests._fixtures import AS_OF, FakeMT5DemoGateway
from ai_trader.mt5_demo_execution.types import MT5DemoConfig
from ai_trader.order_manager.journal import OrderManagerAuditJournal


def _no_recognition_config() -> OrchestratorConfig:
    return OrchestratorConfig(recognition_pattern_id=None)


def _make_demo_deps(tmp_path: Path, demo_adapter: MT5DemoBrokerAdapter) -> OrchestratorDependencies:
    return make_deps(
        tmp_path / "demo", ledger=OrderLedger(),
        order_journal=OrderManagerAuditJournal(tmp_path / "demo" / "journal.jsonl"), adapter=demo_adapter,
    )


def test_demo_never_attempted_when_dry_run_fails(tmp_path: Path) -> None:
    dry_run_deps = make_deps(tmp_path / "dry")
    demo_gateway = FakeMT5DemoGateway(tick_time=AS_OF)
    demo_adapter = MT5DemoBrokerAdapter(gateway=demo_gateway)
    demo_adapter.connect()
    demo_deps = _make_demo_deps(tmp_path, demo_adapter)

    candidate = make_candidate(as_of=AS_OF + 999_999)  # deliberately stale vs market_context's own as_of -> STALE_CANDIDATE denial
    safety_report = verify_safety_guards(demo_adapter, MT5DemoConfig(), symbol="XAUUSD", clock=lambda: AS_OF)

    outcome = send_after_dry_run_gate(
        candidate, make_market_context(), dry_run_deps, demo_deps, demo_adapter, safety_report,
        config=_no_recognition_config(),
    )
    assert outcome.sent is False
    assert outcome.demo_result is None
    assert "DRY_RUN_DID_NOT_PASS" in outcome.reason_codes
    assert demo_gateway.order_send_calls == []


def test_demo_never_attempted_when_safety_guards_fail(tmp_path: Path) -> None:
    dry_run_deps = make_deps(tmp_path / "dry")
    demo_gateway = FakeMT5DemoGateway(algo_trading_enabled=False, tick_time=AS_OF)
    demo_adapter = MT5DemoBrokerAdapter(gateway=demo_gateway)
    demo_adapter.connect()
    demo_deps = _make_demo_deps(tmp_path, demo_adapter)

    candidate = make_candidate()
    safety_report = verify_safety_guards(demo_adapter, MT5DemoConfig(), symbol="XAUUSD", clock=lambda: AS_OF)
    assert safety_report.all_passed is False

    outcome = send_after_dry_run_gate(
        candidate, make_market_context(), dry_run_deps, demo_deps, demo_adapter, safety_report,
        config=_no_recognition_config(),
    )
    assert outcome.dry_run_result.approved is True  # dry run itself succeeds fine
    assert outcome.demo_result is None
    assert "SAFETY_GUARDS_FAILED" in outcome.reason_codes
    assert demo_gateway.order_send_calls == []


def test_demo_sent_after_dry_run_passes_and_guards_pass(tmp_path: Path) -> None:
    dry_run_deps = make_deps(tmp_path / "dry")
    demo_gateway = FakeMT5DemoGateway(tick_time=AS_OF)
    demo_adapter = MT5DemoBrokerAdapter(gateway=demo_gateway, config=MT5DemoConfig(max_order_volume=1.0))
    demo_adapter.connect()
    demo_deps = _make_demo_deps(tmp_path, demo_adapter)

    candidate = make_candidate()
    safety_report = verify_safety_guards(demo_adapter, MT5DemoConfig(max_order_volume=1.0), symbol="XAUUSD", clock=lambda: AS_OF)
    assert safety_report.all_passed is True

    outcome = send_after_dry_run_gate(
        candidate, make_market_context(), dry_run_deps, demo_deps, demo_adapter, safety_report,
        config=_no_recognition_config(),
    )
    assert outcome.dry_run_result.approved is True
    assert outcome.demo_result is not None
    assert outcome.sent is True
    assert outcome.demo_result.order_result is not None
    assert outcome.demo_result.order_result.dry_run is False
    assert len(demo_gateway.order_send_calls) == 1


def test_dry_run_and_demo_use_separate_ledgers(tmp_path: Path) -> None:
    dry_run_deps = make_deps(tmp_path / "dry")
    demo_gateway = FakeMT5DemoGateway(tick_time=AS_OF)
    demo_adapter = MT5DemoBrokerAdapter(gateway=demo_gateway, config=MT5DemoConfig(max_order_volume=1.0))
    demo_adapter.connect()
    demo_deps = _make_demo_deps(tmp_path, demo_adapter)
    assert dry_run_deps.ledger is not demo_deps.ledger

    candidate = make_candidate()
    safety_report = verify_safety_guards(demo_adapter, MT5DemoConfig(max_order_volume=1.0), symbol="XAUUSD", clock=lambda: AS_OF)
    send_after_dry_run_gate(candidate, make_market_context(), dry_run_deps, demo_deps, demo_adapter, safety_report, config=_no_recognition_config())

    assert len(dry_run_deps.ledger) == 1
    assert len(demo_deps.ledger) == 1  # a SEPARATE ledger entry, not a duplicate-guard no-op


def test_mismatched_demo_adapter_object_raises(tmp_path: Path) -> None:
    dry_run_deps = make_deps(tmp_path / "dry")
    demo_gateway = FakeMT5DemoGateway(tick_time=AS_OF)
    demo_adapter = MT5DemoBrokerAdapter(gateway=demo_gateway)
    demo_adapter.connect()
    other_demo_adapter = MT5DemoBrokerAdapter(gateway=FakeMT5DemoGateway(tick_time=AS_OF))
    other_demo_adapter.connect()
    demo_deps = _make_demo_deps(tmp_path, other_demo_adapter)  # deliberately a DIFFERENT object

    candidate = make_candidate()
    safety_report = verify_safety_guards(demo_adapter, MT5DemoConfig(), symbol="XAUUSD", clock=lambda: AS_OF)

    with pytest.raises(ValueError):
        send_after_dry_run_gate(
            candidate, make_market_context(), dry_run_deps, demo_deps, demo_adapter, safety_report,
            config=_no_recognition_config(),
        )
