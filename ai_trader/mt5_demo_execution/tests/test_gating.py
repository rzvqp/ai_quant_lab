from __future__ import annotations

from pathlib import Path

import pytest

from ai_trader.execution_engine.ledger import OrderLedger
from ai_trader.execution_orchestrator.tests._fixtures import make_candidate, make_deps, make_market_context
from ai_trader.execution_orchestrator.types import OrchestratorConfig, OrchestratorDependencies
from ai_trader.mt5_demo_execution import gating
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


def test_demo_blocked_by_legacy_quarantine_even_when_dry_run_and_guards_pass(tmp_path: Path) -> None:
    """CEO decision (AI Trader New Brain Architecture mandate): CAND-0001/0007/0019 are
    LEGACY_NON_AUTHORITY -- the DEMO leg must be unreachable even on the otherwise-happy path (dry run
    passes, safety guards pass). This is the production default (`gating.LEGACY_TRADING_AUTHORITY_
    QUARANTINED` is a hardcoded `True`, not patched here)."""
    assert gating.LEGACY_TRADING_AUTHORITY_QUARANTINED is True
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
    assert outcome.dry_run_result.approved is True  # the no-real-order leg still runs, for audit/testability
    assert outcome.demo_result is None
    assert outcome.sent is False
    assert "LEGACY_TRADING_AUTHORITY_QUARANTINED" in outcome.reason_codes
    assert demo_gateway.order_send_calls == []


def test_demo_still_blocked_when_caller_passes_emergency_stop_true(tmp_path: Path) -> None:
    """`emergency_stop=True` independently denies the DRY_RUN leg itself (a separate, pre-existing
    kill-switch parameter threaded through `orchestrate`) -- so this scenario never even reaches the
    quarantine check, and the reason code is `DRY_RUN_DID_NOT_PASS` rather than
    `LEGACY_TRADING_AUTHORITY_QUARANTINED`. Kept as its own test because it proves a caller cannot use
    `emergency_stop` to reach or bypass the quarantine check either way -- two independent layers both
    deny, never one enabling what the other blocks."""
    dry_run_deps = make_deps(tmp_path / "dry")
    demo_gateway = FakeMT5DemoGateway(tick_time=AS_OF)
    demo_adapter = MT5DemoBrokerAdapter(gateway=demo_gateway, config=MT5DemoConfig(max_order_volume=1.0))
    demo_adapter.connect()
    demo_deps = _make_demo_deps(tmp_path, demo_adapter)

    candidate = make_candidate()
    safety_report = verify_safety_guards(demo_adapter, MT5DemoConfig(max_order_volume=1.0), symbol="XAUUSD", clock=lambda: AS_OF)

    outcome = send_after_dry_run_gate(
        candidate, make_market_context(), dry_run_deps, demo_deps, demo_adapter, safety_report,
        emergency_stop=True, config=_no_recognition_config(),
    )
    assert outcome.demo_result is None
    assert outcome.sent is False
    assert demo_gateway.order_send_calls == []


def test_demo_would_still_send_if_explicitly_unquarantined(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The underlying mechanism (dry-run-then-demo, separate ledgers) is otherwise unchanged -- proven
    here by explicitly monkeypatching the quarantine flag OFF, exactly what a future, reviewed,
    CEO-authorized un-quarantine code change would flip. This is NOT the production default (see the
    two tests above for that) -- it exists so a future un-quarantine change has a test already proving
    the mechanism still works, and so ledger-separation remains verified independent of the quarantine
    question."""
    monkeypatch.setattr(gating, "LEGACY_TRADING_AUTHORITY_QUARANTINED", False)
    dry_run_deps = make_deps(tmp_path / "dry")
    demo_gateway = FakeMT5DemoGateway(tick_time=AS_OF)
    demo_adapter = MT5DemoBrokerAdapter(gateway=demo_gateway, config=MT5DemoConfig(max_order_volume=1.0))
    demo_adapter.connect()
    demo_deps = _make_demo_deps(tmp_path, demo_adapter)
    assert dry_run_deps.ledger is not demo_deps.ledger

    candidate = make_candidate()
    safety_report = verify_safety_guards(demo_adapter, MT5DemoConfig(max_order_volume=1.0), symbol="XAUUSD", clock=lambda: AS_OF)
    outcome = send_after_dry_run_gate(
        candidate, make_market_context(), dry_run_deps, demo_deps, demo_adapter, safety_report,
        config=_no_recognition_config(),
    )

    assert outcome.sent is True
    assert len(demo_gateway.order_send_calls) == 1
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
