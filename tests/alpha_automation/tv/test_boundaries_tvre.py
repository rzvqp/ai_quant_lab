from alpha_automation import boundaries


def test_strategy_tester_language_rejected():
    assert boundaries.forbidden_language("the Strategy Tester shows a positive result")
    assert boundaries.forbidden_language("backtest results confirm the edge")


def test_optimization_language_rejected():
    assert boundaries.forbidden_language("optimize the parameters for better returns")
    assert boundaries.forbidden_language("this is the best-performing parameter set")
    assert boundaries.forbidden_language("we curve-fit the length")


def test_descriptive_language_allowed():
    assert not boundaries.forbidden_language(
        "price swept the prior high, then formed a lower high across the sampled window")
