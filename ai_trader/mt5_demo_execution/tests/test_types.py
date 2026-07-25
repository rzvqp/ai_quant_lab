from __future__ import annotations

import pytest

from ai_trader.mt5_demo_execution.types import MT5DemoConfig, MT5OrderCheckResult, MT5OrderSendResult, SafetyGuardReport


def test_config_rejects_zero_max_volume() -> None:
    with pytest.raises(ValueError):
        MT5DemoConfig(max_order_volume=0.0)


def test_config_default_max_volume_is_the_broker_minimum() -> None:
    assert MT5DemoConfig().max_order_volume == 0.01


def test_order_check_result_ok_only_for_retcode_zero() -> None:
    assert MT5OrderCheckResult(retcode=0, comment="Done").ok is True
    assert MT5OrderCheckResult(retcode=10004, comment="Requote").ok is False


def test_order_send_result_ok_only_for_retcode_10009() -> None:
    assert MT5OrderSendResult(retcode=10009, comment="Done").ok is True
    assert MT5OrderSendResult(retcode=10013, comment="Invalid request").ok is False


def test_safety_guard_report_all_passed_requires_every_guard() -> None:
    passing = SafetyGuardReport(
        connected=True, account_is_demo=True, algo_trading_enabled=True, server_matches_expected=True,
        max_volume_configured=True, market_open=True,
    )
    assert passing.all_passed is True


def test_safety_guard_report_market_open_none_fails_closed() -> None:
    report = SafetyGuardReport(
        connected=True, account_is_demo=True, algo_trading_enabled=True, server_matches_expected=True,
        max_volume_configured=True, market_open=None,
    )
    assert report.all_passed is False


def test_safety_guard_report_single_failed_guard_fails_the_whole_report() -> None:
    report = SafetyGuardReport(
        connected=True, account_is_demo=True, algo_trading_enabled=False, server_matches_expected=True,
        max_volume_configured=True, market_open=True,
    )
    assert report.all_passed is False
