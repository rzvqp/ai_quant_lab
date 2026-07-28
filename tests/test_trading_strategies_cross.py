"""INDEPENDENT cross-verification of trading_strategies.py (136fadc), per CROSS_VERIFICATION_SPEC.
External suite, synthetic in-memory matrices, cases derived from the RATIFIED definition -- NOT reusing
VE's tests, NOT sharing implementation assumptions. Pure software audit: no .load(), no XAUUSD data,
no P&L, no simulation. mypy --strict clean.

Coverage:
  1. Anti-E010 barrier at the SOURCE (_emit, through which ALL nine families route): window fields,
     measurement clamp, fail-closed on out-of-range entry / ineligible spike.  Plus per-family
     mutation-invariance (mutating measurement-window bars leaves prior signals unchanged) for every
     family that fires on synthetic structure.
  2. S10 substitution (BOS-as-displacement): structural trigger, magnitude decoupled from volatility.
  3. S17 D7 rule: single consumption at first wick touch, no re-arm; faithful reuse of the daily rule.
  4. Inertness: exactly nine detect_s*, S15 absent, net_R defined-but-not-called.
"""
from __future__ import annotations

import inspect
import re
from typing import Callable

import numpy as np
import pytest

import trading_strategies as TS
from institutional_levels import LevelKind
from market_structure import Block
from trading_strategies import StrategySignal, _emit

Floats = list[float]


# ─────────────────────────── shared synthetic structure ───────────────────────────
def rich_path() -> dict[str, object]:
    """A deterministic path with swings/breaks/sweep/FVG/levels that fires several families."""
    cps = [(0, 100.0), (6, 90.0), (12, 112.0), (18, 101.0), (24, 124.0), (30, 113.0), (36, 136.0),
           (42, 125.0), (48, 148.0), (54, 120.0), (60, 150.0), (66, 118.0), (72, 108.0)]
    n = cps[-1][0] + 8
    mid = np.interp(np.arange(n), [c[0] for c in cps], [c[1] for c in cps])
    high = mid.copy(); low = mid.copy(); open_ = mid.copy(); close = mid.copy()
    for i in range(2, n - 2):
        seg = mid[i - 2:i + 3]
        if mid[i] == seg.max() and mid[i] > mid[i - 1] and mid[i] > mid[i + 1]:
            high[i] = mid[i] + 3.0
        if mid[i] == seg.min() and mid[i] < mid[i - 1] and mid[i] < mid[i + 1]:
            low[i] = mid[i] - 3.0
    low[66] = 115.0; close[66] = 122.0; high[66] = 123.0; open_[66] = 121.0     # sweep
    high[24] = 127.0; low[26] = 129.0; open_[26] = 130.0; close[26] = 131.0     # FVG gap up
    return dict(open_=open_.tolist(), high=high.tolist(), low=low.tolist(), close=close.tolist(),
                blocks=[Block(0, n)], day_index=(np.arange(n) // 24).tolist(),
                week_index=(np.arange(n) // 120).tolist(), n=n)


def _runner(fam: str) -> Callable[[dict[str, object]], list[StrategySignal]]:
    def go(d: dict[str, object]) -> list[StrategySignal]:
        o = d["open_"]; h = d["high"]; l = d["low"]; c = d["close"]; bl = d["blocks"]
        di = d["day_index"]; wi = d["week_index"]
        assert isinstance(o, list) and isinstance(h, list) and isinstance(l, list) and isinstance(c, list)
        assert isinstance(bl, list) and isinstance(di, list) and isinstance(wi, list)
        if fam == "S1":
            return TS.detect_s1(o, h, l, c, bl)
        if fam == "S2":
            return TS.detect_s2(o, h, l, c, bl)
        if fam == "S3":
            return TS.detect_s3(o, h, l, c, bl)
        if fam == "S7":
            return TS.detect_s7(o, h, l, c, bl)
        if fam == "S10":
            return TS.detect_s10(o, h, l, c, bl)
        if fam == "S11":
            return TS.detect_s11(o, h, l, c, bl)
        if fam == "S13":
            return TS.detect_s13(o, h, l, c, bl)
        if fam == "S16":
            return TS.detect_s16(o, h, l, c, di, bl)
        return TS.detect_s17(o, h, l, c, di, wi, bl)
    return go


FIRING = ["S1", "S2", "S10", "S11", "S13", "S16"]   # families that fire on rich_path() (empirically)


# ─────────────────────────── 1a. anti-E010 barrier at the source (_emit) ───────────────────────────
def test_emit_window_fields() -> None:
    s = _emit("X", trigger_idx=40, entry_idx=41, direction=1, spike_price=3.0, horizon=20, n=100)
    assert s is not None
    assert s.selection_end == s.entry_idx == 41           # selection ends exactly AT entry
    assert s.measurement_start == 41                       # measurement starts AT entry
    assert s.measurement_end == min(41 + 20, 100) == 61
    # validity/selection interior [.., entry) and measurement interior (entry, end) never overlap.
    assert set(range(0, s.selection_end)).isdisjoint(set(range(s.measurement_start + 1, s.measurement_end)))


def test_emit_measurement_clamped_to_n() -> None:
    s = _emit("X", 90, 95, 1, 3.0, 20, 100)
    assert s is not None and s.measurement_end == 100      # never reads past n


def test_emit_failclosed_entry_out_of_range() -> None:
    assert _emit("X", 99, 100, 1, 3.0, 20, 100) is None    # entry >= n
    assert _emit("X", -2, -1, 1, 3.0, 20, 100) is None     # entry < 0


def test_emit_eligibility_skip_is_fail_closed() -> None:
    assert _emit("X", 40, 41, 1, 1.00, 20, 100) is None    # 10.0 pips < 10.1 -> SKIP
    assert _emit("X", 40, 41, 1, 6.50, 20, 100) is None    # 65.0 pips >= 65.0 -> SKIP
    assert _emit("X", 40, 41, 1, 1.01, 20, 100) is not None # 10.1 pips -> accept (half-open [10.1,65))


# ─────────────────────────── 1b. per-family mutation invariance ───────────────────────────
@pytest.mark.parametrize("fam", FIRING)
def test_measurement_bars_do_not_feed_selection(fam: str) -> None:
    """For each signal at entry e, mutate ALL bars strictly after e and confirm the signal is reproduced
    bit-identically -- proving selection is a pure function of bars <= entry_idx (anti-E010)."""
    d = rich_path()
    run = _runner(fam)
    sigs = run(d)
    assert sigs, f"{fam} produced no signals on rich_path() (fixture issue, not a module claim)"
    for s in sigs:
        d2 = {k: (list(v) if isinstance(v, list) else v) for k, v in d.items()}
        e = s.entry_idx
        for key in ("open_", "high", "low", "close"):
            arr = d2[key]
            assert isinstance(arr, list)
            for j in range(e + 1, len(arr)):
                arr[j] = 999999.0 if key == "high" else -999999.0 if key == "low" else 1.0
        sigs2 = run(d2)
        # StrategySignal is a frozen dataclass: `s in sigs2` is exact field-wise equality. Reproduced
        # bit-identically after every future bar is garbled -> its selection read only bars <= entry.
        # (S13 may emit several signals at the same entry -- different FVGs -- so match the exact signal.)
        assert s in sigs2, f"{fam}: signal at entry {e} NOT reproduced under future mutation -> selection read the future (E010)"


def test_s17_measurement_bars_do_not_feed_selection() -> None:
    """S17 fires only on a crafted weekly-level touch; give it its own mutation-invariance check."""
    d = _weekly_touch_fixture(n_touches=1)
    run = _runner("S17")
    sigs = run(d)
    assert sigs, "S17 fixture produced no signal"
    for s in sigs:
        d2 = {k: (list(v) if isinstance(v, list) else v) for k, v in d.items()}
        e = s.entry_idx
        for key in ("open_", "high", "low", "close"):
            arr = d2[key]
            assert isinstance(arr, list)
            for j in range(e + 1, len(arr)):
                arr[j] = 999999.0 if key == "high" else -999999.0 if key == "low" else 1.0
        assert s in run(d2), f"S17: signal at entry {e} NOT reproduced under future mutation (E010)"


# ─────────────────────────── 2. S10 substitution (BOS-as-displacement) ───────────────────────────
def test_s10_trigger_is_structural_not_volatility() -> None:
    """S10 emits on a body-BOS (structure). Its magnitude gate is the ABSOLUTE spike [10.1,65) pips, not
    an ATR/volatility-relative displacement -> magnitude is DECOUPLED from volatility (declared)."""
    src = inspect.getsource(TS.detect_s10)
    assert "detect_breaks" in src and "ATR" not in src.upper().replace("ATR-", "")  # no ATR magnitude gate
    d = rich_path(); s10 = _runner("S10")(d)
    assert s10, "S10 did not fire"
    # every S10 spike is an absolute price distance to the BOS level, filtered by the shared pip band:
    for s in s10:
        assert 10.1 <= s.spike_pips < 65.0


# ─────────────────────────── 3. S17 D7: single consumption, no re-arm; faithful reuse ───────────────────────────
def _weekly_touch_fixture(n_touches: int) -> dict[str, object]:
    """One COMPLETE prior-week WEEKLY_HIGH (>=5 distinct days), then `n_touches` wick touches of it in the
    following week. D7 => exactly one consumption (first touch), regardless of how many touches follow."""
    bars_per_day = 6
    day_index: list[int] = []
    week_index: list[int] = []
    high: Floats = []; low: Floats = []; open_: Floats = []; close: Floats = []
    # week 0: 5 days, the max high is 110.0 on day 2 -> weekly high
    for day in range(5):
        for b in range(bars_per_day):
            base = 100.0 + (10.0 if (day == 2 and b == 3) else 1.0 * b)
            high.append(base); low.append(base - 1.0); open_.append(base - 0.5); close.append(base - 0.2)
            day_index.append(day); week_index.append(0)
    wk_high = max(high)   # 110.0
    # week 1: 5 days; put n_touches bars whose high reaches wk_high (touch), spread out, with an eligible
    # spike (open ~ wk_high - 3.0 => 30 pips). Non-touch bars stay well below.
    for day in range(5, 10):
        for b in range(bars_per_day):
            idx_in_week = (day - 5) * bars_per_day + b
            touch = idx_in_week in [3 + 2 * t for t in range(n_touches)]
            if touch:
                high.append(wk_high + 0.5); low.append(wk_high - 5.0)
                open_.append(wk_high - 3.0); close.append(wk_high - 2.0)   # spike 30 pips, eligible
            else:
                high.append(95.0); low.append(94.0); open_.append(94.5); close.append(94.7)
            day_index.append(day); week_index.append(1)
    n = len(high)
    return dict(open_=open_, high=high, low=low, close=close, blocks=[Block(0, n)],
                day_index=day_index, week_index=week_index, n=n)


def test_s17_single_consumption_first_touch() -> None:
    d1 = _weekly_touch_fixture(n_touches=1)
    d4 = _weekly_touch_fixture(n_touches=4)
    run = _runner("S17")
    s1 = run(d1); s4 = run(d4)
    assert len(s1) == 1, f"S17 with 1 touch -> expected 1 signal, got {len(s1)}"
    # THE anti-re-arm check (market_structure.py symptom was 1 event -> 4 signals): 4 touches still 1 signal
    assert len(s4) == 1, f"S17 re-armed on secondary touches -> {len(s4)} signals (expected 1)"
    assert s1[0].entry_idx == s4[0].entry_idx, "S17 consumed a different (not the first) touch"


def test_s17_reuses_daily_D7_rule_faithfully() -> None:
    """S17's inline weekly D7 loop must implement the SAME rule as institutional_levels.detect_level_touches
    (first wick touch, consume once via break, window bounded by the period index). Verified structurally
    against the daily reference's source."""
    import institutional_levels as IL
    daily = inspect.getsource(IL.detect_level_touches)
    weekly = inspect.getsource(TS.detect_s17)
    # both: scan available_idx..block.end, break when leaving the period, wick-touch condition, break on touch
    assert "range(lv.available_idx, block.end)" in daily and "range(lv.available_idx, block.end)" in weekly
    assert "high[j] >= " in daily and "high[j] >= lv.price" in weekly     # high-side wick touch
    assert "break" in daily and weekly.count("break") >= 2                # leave-period break + consume break


# ─────────────────────────── 4. inertness / formalization coverage ───────────────────────────
def test_exactly_nine_detect_functions() -> None:
    got = {name for name, _ in inspect.getmembers(TS, inspect.isfunction) if re.fullmatch(r"detect_s\d+", name)}
    assert got == {"detect_s1", "detect_s2", "detect_s3", "detect_s7", "detect_s10",
                   "detect_s11", "detect_s13", "detect_s16", "detect_s17"}, got


def test_s15_not_implemented() -> None:
    assert not hasattr(TS, "detect_s15")
    assert "S15" in TS.UNFORMALIZED_FAMILIES and "GOL" in TS.UNFORMALIZED_FAMILIES["S15"].upper()


def test_net_R_defined_but_not_called_in_any_detector() -> None:
    assert callable(TS.net_R)                                    # signature exists
    for name, fn in inspect.getmembers(TS, inspect.isfunction):
        if name.startswith("detect_s"):
            assert "net_R(" not in inspect.getsource(fn), f"{name} calls net_R -> module not inert"
