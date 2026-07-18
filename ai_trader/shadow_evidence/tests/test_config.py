"""Unit tests for :mod:`ai_trader.shadow_evidence.config` -- Phase 6.10 Implementation Checkpoint 3's
``all_registered_strategies()`` helper.
"""

from __future__ import annotations

from ai_trader.shadow_evidence.config import ShadowConfig, all_registered_strategies


def test_all_registered_strategies_returns_the_real_production_set() -> None:
    ids = all_registered_strategies()
    # The exact, already-known-and-documented set (PROJECT_STATE_v2.md §2): S1-S31, S38-S46, S48,
    # S50, S51 -- S32-S37 NOT_IMPLEMENTED, S47/S49 technically invalid, none hand-picked here.
    assert len(ids) == 43
    assert "S32" not in ids and "S37" not in ids  # NOT_IMPLEMENTED range excluded
    assert "S47" not in ids and "S49" not in ids  # technically invalid, excluded
    assert "S1" in ids and "S51" in ids


def test_all_registered_strategies_is_safe_to_call_before_any_harness_runs() -> None:
    # A fresh call in a process that has never constructed a SimulationHarness must still see the
    # real, full set -- never an accidentally-empty one from a lazy import that hasn't fired yet.
    ids = all_registered_strategies()
    assert len(ids) > 0


def test_all_registered_strategies_feeds_a_valid_shadow_config() -> None:
    config = ShadowConfig(enabled=True, shadow_strategies=tuple(sorted(all_registered_strategies())))
    assert config.active_strategy_ids() == all_registered_strategies()
