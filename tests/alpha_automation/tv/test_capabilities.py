import pytest

from alpha_automation.tv import capabilities as caps


def test_classification():
    assert caps.classify("get_state") == caps.READ
    assert caps.classify("set_symbol") == caps.NAVIGATE
    assert caps.classify("add_indicator") == caps.MUTATE
    assert caps.classify("pine_compile") == caps.GATED
    assert caps.classify("replay_trade") == caps.DENY
    assert caps.classify("totally_unknown_verb") == caps.DENY  # default-deny


def test_prohibited_actions_denied():
    for verb in ("replay_trade", "alert_create", "alert_delete", "get_strategy_results",
                 "get_trades", "get_equity", "watchlist_add"):
        with pytest.raises(caps.CapabilityDenied):
            caps.check(verb)


def test_unknown_verb_denied():
    with pytest.raises(caps.CapabilityDenied):
        caps.check("do_something_weird")


def test_gated_requires_flag():
    with pytest.raises(caps.CapabilityDenied):
        caps.check("pine_compile", pine_apply=False)
    assert caps.check("pine_compile", pine_apply=True) == caps.GATED


def test_read_and_navigate_allowed():
    assert caps.check("get_ohlcv") == caps.READ
    assert caps.check("replay_start") == caps.NAVIGATE
    assert caps.check("add_indicator") == caps.MUTATE


def test_is_mutating():
    assert caps.is_mutating("add_indicator")
    assert caps.is_mutating("pine_save")
    assert not caps.is_mutating("get_state")
    assert not caps.is_mutating("set_symbol")  # navigation is not "mutating" for provenance


def test_allowed_verbs_excludes_gated_by_default():
    default = caps.allowed_verbs(pine_apply=False)
    assert "get_state" in default and "add_indicator" in default
    assert "pine_compile" not in default
    assert "replay_trade" not in default
    withpine = caps.allowed_verbs(pine_apply=True)
    assert "pine_compile" in withpine
