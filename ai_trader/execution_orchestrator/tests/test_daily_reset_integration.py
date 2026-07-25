"""Demo Readiness precondition #11, at the orchestrator level: a `PortfolioDailyState` from a PRIOR
UTC day must not be used stale -- if it is, a trade count already at yesterday's limit would wrongly
deny today's first candidate. `orchestrate()` must reset it to today's fresh state before Portfolio
Manager ever sees it."""

from __future__ import annotations

from pathlib import Path

from ai_trader.execution_orchestrator.engine import orchestrate
from ai_trader.execution_orchestrator.tests._fixtures import make_candidate, make_daily_state, make_deps, make_market_context
from ai_trader.execution_orchestrator.types import OrchestratorConfig

_DAY_SECONDS = 86_400
_TODAY = 1_700_000_000 - (1_700_000_000 % _DAY_SECONDS) + 3600  # aligned, one hour into a UTC day
_YESTERDAY = _TODAY - _DAY_SECONDS


def _no_recognition_config() -> OrchestratorConfig:
    return OrchestratorConfig(recognition_pattern_id=None)


def test_stale_daily_state_from_a_prior_day_is_reset_before_use(tmp_path: Path) -> None:
    stale_daily_state = make_daily_state(as_of=_YESTERDAY, trades_opened_today=20)  # == default max_trades_per_day
    deps = make_deps(tmp_path, daily_state=stale_daily_state)

    result = orchestrate(
        make_candidate(as_of=_TODAY), make_market_context(as_of=_TODAY), deps, config=_no_recognition_config(),
    )

    # If the stale state (trades_opened_today=20) had been used as-is, Portfolio Manager's own
    # DAILY_TRADE_COUNT check (20 < 20 is False) would have denied this -- proving the reset actually
    # ran, not just that the happy path coincidentally still works.
    assert result.approved is True
    assert result.daily_state_after is not None
    assert result.daily_state_after.as_of == _TODAY
    assert result.daily_state_after.trades_opened_today == 0


def test_same_day_daily_state_is_not_reset(tmp_path: Path) -> None:
    same_day_state = make_daily_state(as_of=_TODAY - 1800, trades_opened_today=3)  # 30 min earlier, same UTC day
    deps = make_deps(tmp_path, daily_state=same_day_state)

    result = orchestrate(
        make_candidate(as_of=_TODAY), make_market_context(as_of=_TODAY), deps, config=_no_recognition_config(),
    )

    assert result.daily_state_after is not None
    assert result.daily_state_after.trades_opened_today == 3  # unchanged -- not reset, still the same day
