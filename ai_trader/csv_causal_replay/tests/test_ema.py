"""Mandate section 14: "indicator no-lookahead" -- proves `causal_ema` is a strict left-to-right
fold, not merely documented as one.
"""

from __future__ import annotations

import csv

from ai_trader.csv_causal_replay.ema import EMA_PERIOD, causal_ema, sub_ema_streak
from ai_trader.csv_causal_replay.tests.conftest import SEALED_FIXTURE_PATH


def test_ema_seed_is_sma_of_first_period_values():
    values = [10.0] * 50 + [20.0]
    ema = causal_ema(values, period=50)
    assert ema[48] is None
    assert ema[49] == 10.0  # SMA of fifty 10.0s


def test_changing_a_later_value_never_changes_an_earlier_ema():
    """The adversarial no-lookahead check: `causal_ema(values)[i]` must be identical whether or not
    `values[i+1:]` is later mutated to something wildly different."""
    base = [1900.0 + (i % 7) - 3 for i in range(200)]
    ema_a = causal_ema(base, period=50)

    tampered = list(base)
    tampered[150:] = [9_999_999.0] * (len(tampered) - 150)  # a "future" value nothing should see
    ema_b = causal_ema(tampered, period=50)

    for i in range(150):
        assert ema_a[i] == ema_b[i], f"EMA at index {i} changed after mutating only index >= 150 -- LOOKAHEAD LEAK"


def test_sub_ema_streak_is_zero_when_last_close_is_above_ema():
    values = [100.0] * 60  # flat series: close == EMA exactly, "below" is strictly less-than -> 0
    assert sub_ema_streak(values, period=50) == 0


def test_sub_ema_streak_counts_only_the_trailing_run():
    # 60 bars flat at 100 (EMA settles at 100), then a run below, then one bar back above, then below again.
    values = [100.0] * 60 + [90.0, 89.0, 88.0, 101.0, 95.0, 94.0]
    streak = sub_ema_streak(values, period=50)
    assert streak == 2  # only the trailing two (94, 95) count -- the 101 bar reset the streak


def test_real_fixture_bar_378_is_below_its_own_causal_ema50():
    """Measured against the real sealed fixture -- see ema.py's own docstring for the full,
    disclosed comparison against AI_TRADER_Q4_M15_LOG.md's reported 38-bar streak (this module
    computes 44; the DIRECTION matches, the exact streak length does not, and that divergence is
    reported, not hidden)."""
    closes = []
    with SEALED_FIXTURE_PATH.open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        next(reader)
        for row in reader:
            closes.append(float(row[4]))
    ema = causal_ema(closes, EMA_PERIOD)
    assert closes[-1] == 1880.434  # bar 378's close, sanity-pinning this test to the right row
    assert ema[-1] is not None
    assert closes[-1] < ema[-1]
    streak = sub_ema_streak(closes, EMA_PERIOD)
    assert streak == 44  # measured fact about this implementation -- see ema.py docstring for the disclosed gap vs the log's 38
